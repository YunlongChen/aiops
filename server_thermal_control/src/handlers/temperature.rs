use actix_web::{web, HttpResponse, Result};
use chrono::Utc;
use serde_json::json;
use crate::{models, AppState};

/// 获取所有温度数据
/// 
/// 从IPMI服务获取真实的温度传感器数据
pub async fn list_temperature_data(data: web::Data<AppState>) -> Result<HttpResponse> {
    match data.ipmi_service.get_temperature_sensors().await {
        Ok(sensors) => {
            let temperature_data: Vec<_> = sensors.into_iter().map(|sensor| {
                json!({
                    "id": uuid::Uuid::new_v4().to_string(),
                    "sensor_id": sensor.name,
                    "temperature": sensor.value,
                    "unit": "°C",
                    "location": sensor.name,
                    "status": sensor.status,
                    "timestamp": Utc::now().to_rfc3339()
                })
            }).collect();

            Ok(HttpResponse::Ok().json(models::ApiResponse::success(
                json!({
                    "data": temperature_data,
                    "total": temperature_data.len(),
                    "limit": 100,
                    "offset": 0
                }),
                "Temperature data retrieved successfully"
            )))
        }
        Err(e) => {
            Ok(HttpResponse::InternalServerError().json(models::ApiResponse::error(
                &format!("Failed to retrieve temperature data: {}", e)
            )))
        }
    }
}

/// 获取指定传感器温度
/// 
/// 根据传感器ID获取特定传感器的温度数据
pub async fn get_sensor_temperature(
    path: web::Path<String>,
    data: web::Data<AppState>
) -> Result<HttpResponse> {
    let sensor_id = path.into_inner();
    
    match data.ipmi_service.get_temperature_sensors().await {
        Ok(sensors) => {
            if let Some(sensor) = sensors.into_iter().find(|s| s.name == sensor_id) {
                let sensor_data = json!({
                    "id": uuid::Uuid::new_v4().to_string(),
                    "sensor_id": sensor.name,
                    "temperature": sensor.value,
                    "unit": "°C",
                    "location": sensor.name,
                    "status": sensor.status,
                    "timestamp": Utc::now().to_rfc3339(),
                    "history": []
                });

                Ok(HttpResponse::Ok().json(models::ApiResponse::success(
                    sensor_data,
                    &format!("Temperature data for sensor {} retrieved successfully", sensor_id)
                )))
            } else {
                Ok(HttpResponse::NotFound().json(models::ApiResponse::error(
                    &format!("Sensor {} not found", sensor_id)
                )))
            }
        }
        Err(e) => {
            Ok(HttpResponse::InternalServerError().json(models::ApiResponse::error(
                &format!("Failed to retrieve temperature data: {}", e)
            )))
        }
    }
}