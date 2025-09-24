//! 请求日志中间件
//! 
//! 记录HTTP请求的详细信息，包括请求时间、响应时间、用户代理等

use axum::{
    extract::Request,
    middleware::Next,
    response::Response,
};
use std::time::Instant;
use tracing::{info, warn};

/// 请求日志中间件
/// 
/// 记录每个HTTP请求的详细信息和处理时间
pub async fn request_logger_middleware(request: Request, next: Next) -> Response {
    let start_time = Instant::now();
    let method = request.method().clone();
    let uri = request.uri().clone();
    let path = uri.path();
    let query = uri.query().unwrap_or("");
    
    // 获取请求头信息
    let user_agent = request
        .headers()
        .get("user-agent")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("Unknown");
    
    let content_type = request
        .headers()
        .get("content-type")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("Unknown");

    // 记录请求开始
    info!(
        method = %method,
        path = %path,
        query = %query,
        user_agent = %user_agent,
        content_type = %content_type,
        "开始处理HTTP请求"
    );

    // 处理请求
    let response = next.run(request).await;
    
    // 计算处理时间
    let duration = start_time.elapsed();
    let status = response.status();
    
    // 记录请求完成信息
    if status.is_success() {
        info!(
            method = %method,
            path = %path,
            status = %status,
            duration_ms = duration.as_millis(),
            "HTTP请求处理完成"
        );
    } else if status.is_client_error() {
        warn!(
            method = %method,
            path = %path,
            status = %status,
            duration_ms = duration.as_millis(),
            "HTTP请求处理完成 - 客户端错误"
        );
    } else if status.is_server_error() {
        warn!(
            method = %method,
            path = %path,
            status = %status,
            duration_ms = duration.as_millis(),
            "HTTP请求处理完成 - 服务器错误"
        );
    } else {
        info!(
            method = %method,
            path = %path,
            status = %status,
            duration_ms = duration.as_millis(),
            "HTTP请求处理完成"
        );
    }

    response
}