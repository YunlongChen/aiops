//! 错误处理中间件
//! 
//! 提供统一的错误处理和日志记录功能

use axum::{
    extract::Request,
    http::StatusCode,
    middleware::Next,
    response::{IntoResponse, Response},
    Json,
};
use serde_json::json;
use tracing::{error, warn, info};

/// 错误处理中间件
/// 
/// 捕获HTTP请求处理过程中的错误，并记录相应的日志
pub async fn error_handler_middleware(request: Request, next: Next) -> Response {
    let method = request.method().clone();
    let uri = request.uri().clone();
    let path = uri.path();
    
    // 记录请求信息
    info!(
        method = %method,
        path = %path,
        "处理HTTP请求"
    );

    let response = next.run(request).await;
    let status = response.status();

    // 根据状态码记录不同级别的日志
    match status {
        StatusCode::NOT_FOUND => {
            warn!(
                method = %method,
                path = %path,
                status = %status,
                "请求的资源未找到 (404)"
            );
        }
        StatusCode::INTERNAL_SERVER_ERROR => {
            error!(
                method = %method,
                path = %path,
                status = %status,
                "服务器内部错误 (500)"
            );
        }
        StatusCode::BAD_REQUEST => {
            warn!(
                method = %method,
                path = %path,
                status = %status,
                "请求参数错误 (400)"
            );
        }
        StatusCode::UNAUTHORIZED => {
            warn!(
                method = %method,
                path = %path,
                status = %status,
                "未授权访问 (401)"
            );
        }
        StatusCode::FORBIDDEN => {
            warn!(
                method = %method,
                path = %path,
                status = %status,
                "访问被禁止 (403)"
            );
        }
        status if status.is_client_error() => {
            warn!(
                method = %method,
                path = %path,
                status = %status,
                "客户端请求错误"
            );
        }
        status if status.is_server_error() => {
            error!(
                method = %method,
                path = %path,
                status = %status,
                "服务器错误"
            );
        }
        status if status.is_success() => {
            info!(
                method = %method,
                path = %path,
                status = %status,
                "请求处理成功"
            );
        }
        _ => {
            info!(
                method = %method,
                path = %path,
                status = %status,
                "请求处理完成"
            );
        }
    }

    response
}

/// 全局错误处理器
/// 
/// 处理应用程序中未捕获的错误
pub async fn global_error_handler(err: Box<dyn std::error::Error + Send + Sync>) -> impl IntoResponse {
    error!(
        error = %err,
        "全局错误处理器捕获到未处理的错误"
    );

    let error_response = json!({
        "success": false,
        "message": "服务器内部错误",
        "error": "Internal Server Error",
        "timestamp": chrono::Utc::now().to_rfc3339()
    });

    (StatusCode::INTERNAL_SERVER_ERROR, Json(error_response))
}