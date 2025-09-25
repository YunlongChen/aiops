use actix_web::{web, HttpResponse, Result};
use chrono::Utc;
use serde_json::json;
use crate::{models, AppState};

/// 获取所有风扇数据
/// 
/// 从IPMI服务获取真实的风扇状态和转速数据
pub async fn list_fan_data(data: web::Data<AppState>) -> Result<HttpResponse> {
    match data.ipmi_service.get_fan_data().await {
        Ok(fans) => {
            let fan_data: Vec<_> = fans.into_iter().map(|fan| {
                json!({
                    "id": uuid::Uuid::new_v4().to_string(),
                    "fan_id": fan.name,
                    "rpm": fan.rpm,
                    "speed_percent": fan.speed_percent,
                    "status": fan.status,
                    "location": fan.name,
                    "timestamp": Utc::now().to_rfc3339()
                })
            }).collect();

            Ok(HttpResponse::Ok().json(models::ApiResponse::success(
                json!({
                    "data": fan_data,
                    "total": fan_data.len(),
                    "limit": 100,
                    "offset": 0
                }),
                "Fan data retrieved successfully"
            )))
        }
        Err(e) => {
            Ok(HttpResponse::InternalServerError().json(models::ApiResponse::error(
                &format!("Failed to retrieve fan data: {}", e)
            )))
        }
    }
}

/// 设置风扇转速
/// 
/// 注意：IPMI通常不支持直接设置风扇转速，这里返回模拟响应
pub async fn set_fan_speed(
    path: web::Path<String>,
    _body: web::Json<serde_json::Value>,
    _data: web::Data<AppState>
) -> Result<HttpResponse> {
    let fan_id = path.into_inner();
    
    // IPMI通常不支持直接设置风扇转速，这里返回一个提示信息
    Ok(HttpResponse::Ok().json(models::ApiResponse::success(
        json!({
            "fan_id": fan_id,
            "message": "Fan speed control via IPMI is typically not supported. Consider using system-level fan control utilities.",
            "timestamp": Utc::now().to_rfc3339()
        }),
        "Fan speed control request processed"
    )))
}