use crate::models::api::ApiResponse;
use crate::{models, AppState};
use actix_web::{web, HttpResponse, Result};
use chrono::Utc;
use serde_json::json;

/// 获取所有温度数据
/// 
/// 从IPMI服务获取真实的温度传感器数据
pub async fn list_temperature_data(data: web::Data<AppState>) -> Result<HttpResponse> {
    match data.ipmi_service.get_temperature_sensors() {
        Ok(sensors) => {
            let temperature_data: Vec<_> = sensors.into_iter().map(|sensor| {
                json!({
                    "id": uuid::Uuid::new_v4().to_string(),
                    "sensor_id": sensor.sensor_id,
                    "temperature": sensor.temperature,
                    "unit": "°C",
                    "location": sensor.location,
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
            let response: ApiResponse<()> = ApiResponse::error(
                &format!("Failed to retrieve temperature data: {}", e)
            );
            Ok(HttpResponse::InternalServerError().json(response))
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

    match data.ipmi_service.get_temperature_sensors() {
        Ok(sensors) => {
            if let Some(sensor) = sensors.into_iter().find(|s| s.sensor_id == sensor_id) {
                let sensor_data = json!({
                    "id": uuid::Uuid::new_v4().to_string(),
                    "sensor_id": sensor.sensor_id,
                    "temperature": sensor.temperature,
                    "unit": "°C",
                    "location": sensor.location,
                    "status": sensor.status,
                    "timestamp": Utc::now().to_rfc3339(),
                    "history": []
                });

                Ok(HttpResponse::Ok().json(models::ApiResponse::success(
                    sensor_data,
                    &format!("Temperature data for sensor {} retrieved successfully", sensor_id)
                )))
            } else {
                let response: ApiResponse<()> = ApiResponse::error(
                    &format!("Sensor {} not found", sensor_id)
                );
                Ok(HttpResponse::NotFound().json(response))
            }
        }
        Err(e) => {
            let response: ApiResponse<()> = ApiResponse::error(
                &format!("Failed to retrieve temperature data: {}", e)
            );
            Ok(HttpResponse::InternalServerError().json(response))
        }
    }
}