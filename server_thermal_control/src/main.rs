use actix_cors::Cors;
use actix_web::{middleware::Logger, web, App, HttpResponse, HttpServer, Result};
use std::sync::Arc;
use tracing::{error, info};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

mod config;
mod controllers;
mod handlers;
mod middleware;
mod models;
mod services;
mod utils;

use crate::services::ipmi_service::IpmiConfig;
use config::AppConfig;
use services::ipmi_service::IpmiService;

/// 应用程序状态
#[derive(Clone)]
pub struct AppState {
    pub config: Arc<AppConfig>,
    pub ipmi_service: Arc<IpmiService>,
}

/// 配置CORS中间件
///
/// # Arguments
/// * `config` - 应用配置
///
/// # Returns
/// * `Cors` - 配置好的CORS中间件
fn configure_cors(config: &AppConfig) -> Cors {
    let mut cors = Cors::default()
        .allowed_methods(vec!["GET", "POST", "PUT", "DELETE", "OPTIONS"])
        .allowed_headers(vec![
            actix_web::http::header::AUTHORIZATION,
            actix_web::http::header::ACCEPT,
            actix_web::http::header::CONTENT_TYPE,
        ])
        .max_age(3600);

    if config.server.cors_origins.is_empty() {
        cors = cors.allow_any_origin();
    } else {
        for origin in &config.server.cors_origins {
            cors = cors.allowed_origin(origin);
        }
    }

    cors
}

/// 根路径处理器
///
/// # Returns
/// * `Result<HttpResponse>` - HTTP响应
async fn root() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "name": "Server Thermal Control System",
        "version": env!("CARGO_PKG_VERSION"),
        "status": "running"
    })))
}

/// 版本信息处理器
///
/// # Returns
/// * `Result<HttpResponse>` - HTTP响应
async fn version() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "version": env!("CARGO_PKG_VERSION"),
        "build_time": chrono::Utc::now().to_rfc3339()
    })))
}

/// API信息处理器
///
/// # Returns
/// * `Result<HttpResponse>` - HTTP响应
async fn api_info() -> Result<HttpResponse> {
    Ok(HttpResponse::Ok().json(serde_json::json!({
        "api_version": "v1",
        "endpoints": [
            "/health",
            "/api/v1/temperature",
            "/api/v1/fans",
            "/api/v1/alerts"
        ]
    })))
}

/// 初始化日志系统
///
/// # Arguments
/// * `config` - 应用配置
fn init_logging(config: &AppConfig) {
    let env_filter = tracing_subscriber::EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| format!("{}={}", env!("CARGO_PKG_NAME"), config.logging.level).into());

    tracing_subscriber::registry()
        .with(env_filter)
        .with(tracing_subscriber::fmt::layer())
        .init();
}

/// 优雅关闭信号处理
///
/// # Returns
/// * `Result<()>` - 操作结果
async fn shutdown_signal() -> std::io::Result<()> {
    #[cfg(unix)]
    {
        use tokio::signal::unix::{signal, SignalKind};
        let mut sigterm = signal(SignalKind::terminate())?;
        let mut sigint = signal(SignalKind::interrupt())?;

        tokio::select! {
            _ = sigterm.recv() => {
                info!("Received SIGTERM");
            }
            _ = sigint.recv() => {
                info!("Received SIGINT");
            }
        }
    }

    #[cfg(windows)]
    {
        use tokio::signal::windows;
        let mut ctrl_c = windows::ctrl_c()?;
        let mut ctrl_break = windows::ctrl_break()?;

        tokio::select! {
            _ = ctrl_c.recv() => {
                info!("Received Ctrl+C");
            }
            _ = ctrl_break.recv() => {
                info!("Received Ctrl+Break");
            }
        }
    }

    Ok(())
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // 加载环境变量
    dotenvy::dotenv().ok();

    // 加载配置
    let config = match AppConfig::load().await {
        Ok(config) => Arc::new(config),
        Err(e) => {
            eprintln!("Failed to load configuration: {}", e);
            std::process::exit(1);
        }
    };

    // 初始化日志
    init_logging(&config);

    info!(
        "Starting Server Thermal Control System v{}",
        env!("CARGO_PKG_VERSION")
    );
    info!(
        "Server will bind to {}:{}",
        config.server.host, config.server.port
    );

    // 创建IPMI服务
    let ipmi_service = Arc::new(IpmiService::new(IpmiConfig {
        host: config.ipmi.host.clone(),
        username: config.ipmi.username.clone(),
        password: config.ipmi.password.clone(),
        interface: config.ipmi.interface.clone(),
    }));

    // 测试IPMI连接
    match ipmi_service.test_connection() {
        Ok(_) => info!("IPMI connection test successful"),
        Err(e) => {
            error!("IPMI connection test failed: {}", e);
            // 可以选择继续运行或退出
        }
    }

    // 创建应用状态
    let app_state = AppState {
        config: Arc::clone(&config),
        ipmi_service,
    };

    // 获取服务器配置
    let host = config.server.host.clone();
    let port = config.server.port;
    let workers = config.server.workers.unwrap_or_else(|| num_cpus::get());

    // 启动HTTP服务器
    let server = HttpServer::new(move || {
        let cors = configure_cors(&config);
        App::new()
            .app_data(web::Data::new(app_state.clone()))
            .wrap(cors)
            .wrap(Logger::default())
            .route("/", web::get().to(root))
            .route("/version", web::get().to(version))
            .route("/api", web::get().to(api_info))
            .service(
                web::scope("/api/v1")
                    .route("/health", web::get().to(handlers::health_check))
                    .route("/system/info", web::get().to(handlers::system_info))
                    .route("/system/health", web::get().to(handlers::system_health))
                    .route(
                        "/stats/temperature",
                        web::get().to(handlers::temperature_stats),
                    )
                    .route("/stats/fan", web::get().to(handlers::fan_stats))
            )
            .service(
                web::scope("/temperature")
                    .route(
                        "",
                        web::get().to(handlers::temperature::list_temperature_data),
                    )
                    .route(
                        "/{sensor_id}",
                        web::get().to(handlers::temperature::get_sensor_temperature),
                    ),
            )
            .service(
                web::scope("/fans")
                    .route("", web::get().to(handlers::fan::list_fan_data))
                    .route(
                        "/{fan_id}/speed",
                        web::post().to(handlers::fan::set_fan_speed),
                    ),
            )
            .service(
                web::scope("/alerts")
                    .route("", web::get().to(handlers::alert::list_alerts))
                    .route(
                        "/{alert_id}/acknowledge",
                        web::post().to(handlers::alert::acknowledge_alert),
                    ),
            )
    })
    .workers(workers)
    .bind((host.as_str(), port))?;

    info!("Server started successfully with {} workers", workers);

    // 启动服务器并等待关闭信号
    let server_handle = server.run();

    tokio::select! {
        result = server_handle => {
            match result {
                Ok(_) => info!("Server stopped normally"),
                Err(e) => error!("Server error: {}", e),
            }
        }
        _ = shutdown_signal() => {
            info!("Shutdown signal received, stopping server...");
        }
    }

    info!("Server shutdown complete");
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::{test, App};

    #[actix_web::test]
    async fn test_root_endpoint() {
        let app = test::init_service(App::new().route("/", web::get().to(root))).await;

        let req = test::TestRequest::get().uri("/").to_request();
        let resp = test::call_service(&app, req).await;

        assert!(resp.status().is_success());
    }

    #[actix_web::test]
    async fn test_version_endpoint() {
        let app = test::init_service(App::new().route("/version", web::get().to(version))).await;

        let req = test::TestRequest::get().uri("/version").to_request();
        let resp = test::call_service(&app, req).await;

        assert!(resp.status().is_success());
    }

    #[actix_web::test]
    async fn test_api_info_endpoint() {
        let app = test::init_service(App::new().route("/api", web::get().to(api_info))).await;

        let req = test::TestRequest::get().uri("/api").to_request();
        let resp = test::call_service(&app, req).await;

        assert!(resp.status().is_success());
    }
}
