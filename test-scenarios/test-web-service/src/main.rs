//! AIOps测试管理Web服务
//! 
//! 基于Rust Axum框架的高性能Web服务，用于管理和运行AIOps测试用例
//! 支持多种运行时环境（Docker、Kubernetes、本地）

use axum::{
    extract::State,
    http::StatusCode,
    response::Json,
    routing::get,
    Router,
};
use serde_json::{json, Value};
use std::{net::SocketAddr, sync::Arc};
use tokio::net::TcpListener;
use tower::ServiceBuilder;
use tower_http::{
    cors::CorsLayer,
    services::ServeDir,
    trace::TraceLayer,
};
use tracing::{info, warn};
use tracing_subscriber;
use utoipa;

mod api;
mod config;
mod database;
mod docs;
mod execution;
mod handlers;
mod models;
mod services;

use config::AppConfig;
use database::Database;

/// 应用程序状态
#[derive(Clone)]
pub struct AppState {
    pub db: Arc<Database>,
    pub config: Arc<AppConfig>,
}

/// 健康检查端点
#[utoipa::path(
    get,
    path = "/health",
    tag = "system",
    summary = "健康检查",
    description = "检查服务健康状态",
    responses(
        (status = 200, description = "服务健康", body = Value),
        (status = 500, description = "服务异常")
    )
)]
async fn health_check() -> Result<Json<Value>, StatusCode> {
    Ok(Json(json!({
        "status": "healthy",
        "timestamp": chrono::Utc::now(),
        "service": "aiops-web-service"
    })))
}

/// 服务信息端点
async fn service_info(State(_state): State<AppState>) -> Result<Json<Value>, StatusCode> {
    Ok(Json(json!({
        "name": "AIOps测试管理服务",
        "version": env!("CARGO_PKG_VERSION"),
        "description": "基于Rust Axum的AIOps测试用例管理和运行服务",
        "features": [
            "测试用例管理",
            "多运行时支持",
            "实时结果监控",
            "配置文件管理",
            "API接口"
        ],
        "database_status": "connected",
        "uptime": chrono::Utc::now().to_rfc3339()
    })))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // 初始化日志
    tracing_subscriber::fmt()
        .with_target(false)
        .compact()
        .init();

    info!("启动AIOps测试管理Web服务...");

    // 加载配置
    let config = Arc::new(AppConfig::load()?);
    info!("配置加载完成: 端口 {}", config.port);

    // 初始化数据库
    let db = Arc::new(Database::new(&config.database_url).await?);
    info!("数据库连接成功");

    // 创建应用状态
    let app_state = AppState {
        db: db.clone(),
        config: config.clone(),
    };

    // 创建应用路由
    let app = Router::new()
        .route("/health", get(health_check))
        .nest("/api/v1", api::routes())
        .nest_service("/static", ServeDir::new("static"))
        .merge(docs::create_swagger_ui())
        .route("/api-docs/openapi.json", get(|| async {
            Json(docs::get_openapi_json())
        }))
        .layer(
            ServiceBuilder::new()
                .layer(TraceLayer::new_for_http())
                .layer(CorsLayer::permissive())
        )
        .with_state(app_state);

    // 启动服务器
    let addr = format!("127.0.0.1:{}", config.port);
    let listener = TcpListener::bind(&addr).await?;
    
    info!("🚀 AIOps Web服务已启动: http://{}", addr);
    info!("📖 API文档: http://{}/api/v1/docs", addr);
    info!("💚 健康检查: http://{}/health", addr);

    axum::serve(listener, app).await?;

    Ok(())
}
