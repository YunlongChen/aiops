use crate::models::{
    error::{AppError, AppResult},
    sensor::*,
    api::{ApiResponse, PaginationParams, TimeRangeParams},
};
use crate::services::SensorService;
use actix_web::{
    web::{Path, Query, Data, ServiceConfig},
    HttpResponse, Result as ActixResult,
    get, post, put, delete,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{info, warn, error};

/// 传感器控制器
/// 
/// 提供传感器数据管理的HTTP API接口
#[derive(Clone)]
pub struct SensorController {
    sensor_service: Arc<SensorService>,
}

impl SensorController {
    /// 创建新的传感器控制器
    /// 
    /// # 参数
    /// * `sensor_service` - 传感器服务
    pub fn new(sensor_service: Arc<SensorService>) -> Self {
        Self { sensor_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/sensors")
                .route("", actix_web::web::get().to(Self::get_all_sensors))
                .route("/{sensor_id}", actix_web::web::get().to(Self::get_sensor_data))
                .route("/type/{sensor_type}", actix_web::web::get().to(Self::get_sensors_by_type))
                .route("/history", actix_web::web::get().to(Self::get_sensor_history))
                .route("/statistics", actix_web::web::get().to(Self::get_sensor_statistics))
                .route("/trends", actix_web::web::get().to(Self::get_sensor_trends))
                .route("/list", actix_web::web::get().to(Self::get_sensor_list))
                .route("/{sensor_id}/calibrate", actix_web::web::post().to(Self::calibrate_sensor))
                .route("/anomalies", actix_web::web::get().to(Self::detect_sensor_anomalies))
                .route("/health", actix_web::web::get().to(Self::get_sensor_health))
                .route("/export", actix_web::web::get().to(Self::export_sensor_data))
                .route("/configurations", actix_web::web::get().to(Self::get_sensor_configurations))
                .route("/configurations", actix_web::web::post().to(Self::set_sensor_configuration))
                .route("/configurations/{sensor_id}", actix_web::web::put().to(Self::update_sensor_configuration))
                .route("/configurations/{sensor_id}", actix_web::web::delete().to(Self::delete_sensor_configuration))
        );
    }

    /// 获取所有传感器数据
    /// 
    /// GET /api/v1/sensors
    async fn get_all_sensors(
        service: Data<SensorService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取所有传感器数据");

        match service.get_all_sensor_data().await {
            Ok(sensors) => Ok(HttpResponse::Ok().json(ApiResponse::success(sensors))),
            Err(e) => {
                error!("获取传感器数据失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器数据失败")))
            }
        }
    }

    /// 获取指定传感器数据
    /// 
    /// GET /api/v1/sensors/{sensor_id}
    async fn get_sensor_data(
        service: Data<SensorService>,
        sensor_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("获取传感器数据: {}", sensor_id);

        match service.get_sensor_data(&sensor_id).await {
            Ok(sensor_data) => Ok(HttpResponse::Ok().json(ApiResponse::success(sensor_data))),
            Err(e) => {
                error!("获取传感器数据失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器数据失败")))
            }
        }
    }

    /// 按类型获取传感器数据
    /// 
    /// GET /api/v1/sensors/type/{sensor_type}
    async fn get_sensors_by_type(
        service: Data<SensorService>,
        sensor_type: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("按类型获取传感器数据: {}", sensor_type);

        match service.get_sensors_by_type(&sensor_type).await {
            Ok(sensors) => Ok(HttpResponse::Ok().json(ApiResponse::success(sensors))),
            Err(e) => {
                error!("按类型获取传感器数据失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("按类型获取传感器数据失败")))
            }
        }
    }

    /// 获取传感器历史数据
    /// 
    /// GET /api/v1/sensors/history
    async fn get_sensor_history(
        service: Data<SensorService>,
        params: Query<SensorHistoryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取传感器历史数据");

        match service.get_sensor_history(
            params.sensor_id.as_deref(),
            params.sensor_type.as_deref(),
            params.start_time,
            params.end_time,
            params.limit,
        ).await {
            Ok(history) => Ok(HttpResponse::Ok().json(ApiResponse::success(history))),
            Err(e) => {
                error!("获取传感器历史数据失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器历史数据失败")))
            }
        }
    }

    /// 获取传感器统计信息
    /// 
    /// GET /api/v1/sensors/statistics
    async fn get_sensor_statistics(
        service: Data<SensorService>,
        params: Query<SensorStatsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取传感器统计信息");

        match service.get_sensor_statistics(
            params.sensor_id.as_deref(),
            params.sensor_type.as_deref(),
            params.start_time,
            params.end_time,
        ).await {
            Ok(stats) => Ok(HttpResponse::Ok().json(ApiResponse::success(stats))),
            Err(e) => {
                error!("获取传感器统计信息失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器统计信息失败")))
            }
        }
    }

    /// 获取传感器趋势分析
    /// 
    /// GET /api/v1/sensors/trends
    async fn get_sensor_trends(
        service: Data<SensorService>,
        params: Query<SensorTrendParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取传感器趋势分析");

        match service.get_sensor_trend(
            &params.sensor_id,
            params.start_time,
            params.end_time,
        ).await {
            Ok(trend) => Ok(HttpResponse::Ok().json(ApiResponse::success(trend))),
            Err(e) => {
                error!("获取传感器趋势分析失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器趋势分析失败")))
            }
        }
    }

    /// 获取传感器列表
    /// 
    /// GET /api/v1/sensors/list
    async fn get_sensor_list(
        service: Data<SensorService>,
        params: Query<SensorListParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取传感器列表");

        match service.get_sensor_list(
            params.sensor_type.as_deref(),
            params.status.as_deref(),
        ).await {
            Ok(sensors) => Ok(HttpResponse::Ok().json(ApiResponse::success(sensors))),
            Err(e) => {
                error!("获取传感器列表失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器列表失败")))
            }
        }
    }

    /// 校准传感器
    /// 
    /// POST /api/v1/sensors/{sensor_id}/calibrate
    async fn calibrate_sensor(
        service: Data<SensorService>,
        sensor_id: Path<String>,
        request: actix_web::web::Json<CalibrateSensorRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("校准传感器: {}", sensor_id);

        match service.calibrate_sensor(&sensor_id, request.calibration_value).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("校准传感器失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("校准传感器失败")))
            }
        }
    }

    /// 检测传感器异常
    /// 
    /// GET /api/v1/sensors/anomalies
    async fn detect_sensor_anomalies(
        service: Data<SensorService>,
        params: Query<AnomalyDetectionParams>,
    ) -> ActixResult<HttpResponse> {
        info!("检测传感器异常");

        match service.detect_anomalies(
            params.sensor_id.as_deref(),
            params.threshold,
            params.time_window,
        ).await {
            Ok(anomalies) => Ok(HttpResponse::Ok().json(ApiResponse::success(anomalies))),
            Err(e) => {
                error!("检测传感器异常失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("检测传感器异常失败")))
            }
        }
    }

    /// 获取传感器健康状态
    /// 
    /// GET /api/v1/sensors/health
    async fn get_sensor_health(
        service: Data<SensorService>,
        params: Query<SensorHealthParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取传感器健康状态");

        match service.get_sensor_health(params.sensor_id.as_deref()).await {
            Ok(health) => Ok(HttpResponse::Ok().json(ApiResponse::success(health))),
            Err(e) => {
                error!("获取传感器健康状态失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器健康状态失败")))
            }
        }
    }

    /// 导出传感器数据
    /// 
    /// GET /api/v1/sensors/export
    async fn export_sensor_data(
        service: Data<SensorService>,
        params: Query<SensorExportParams>,
    ) -> ActixResult<HttpResponse> {
        info!("导出传感器数据，格式: {:?}", params.format);

        match service.export_sensor_data(
            params.sensor_id.as_deref(),
            params.sensor_type.as_deref(),
            params.start_time,
            params.end_time,
            params.format,
        ).await {
            Ok(data) => Ok(HttpResponse::Ok().json(ApiResponse::success(data))),
            Err(e) => {
                error!("导出传感器数据失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("导出传感器数据失败")))
            }
        }
    }

    /// 获取传感器配置
    /// 
    /// GET /api/v1/sensors/configurations
    async fn get_sensor_configurations(
        service: Data<SensorService>,
        params: Query<SensorConfigQueryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取传感器配置");

        let result = if let Some(sensor_id) = &params.sensor_id {
            service.get_sensor_configuration(sensor_id).await.map(|c| vec![c])
        } else {
            service.get_all_sensor_configurations().await
        };

        match result {
            Ok(configs) => Ok(HttpResponse::Ok().json(ApiResponse::success(configs))),
            Err(e) => {
                error!("获取传感器配置失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("获取传感器配置失败")))
            }
        }
    }

    /// 设置传感器配置
    /// 
    /// POST /api/v1/sensors/configurations
    async fn set_sensor_configuration(
        service: Data<SensorService>,
        request: actix_web::web::Json<SetSensorConfigurationRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("设置传感器配置: {}", request.sensor_id);

        match service.set_sensor_configuration(
            &request.sensor_id,
            &request.configuration,
        ).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("设置传感器配置失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("设置传感器配置失败")))
            }
        }
    }

    /// 更新传感器配置
    /// 
    /// PUT /api/v1/sensors/configurations/{sensor_id}
    async fn update_sensor_configuration(
        service: Data<SensorService>,
        sensor_id: Path<String>,
        request: actix_web::web::Json<UpdateSensorConfigRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("更新传感器配置: {}", sensor_id);

        match service.set_sensor_configuration(
            &sensor_id,
            &request.configuration,
        ).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("更新传感器配置失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("更新传感器配置失败")))
            }
        }
    }

    /// 删除传感器配置
    /// 
    /// DELETE /api/v1/sensors/configurations/{sensor_id}
    async fn delete_sensor_configuration(
        service: Data<SensorService>,
        sensor_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("删除传感器配置: {}", sensor_id);

        match service.delete_sensor_configuration(&sensor_id).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("删除传感器配置失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error("删除传感器配置失败")))
            }
        }
    }
}

// 请求和响应结构体

/// 传感器健康状态查询参数
#[derive(Debug, Deserialize)]
pub struct SensorHealthParams {
    /// 传感器ID（可选）
    pub sensor_id: Option<String>,
}

/// 传感器列表查询参数
#[derive(Debug, Deserialize)]
pub struct SensorListParams {
    /// 传感器类型
    pub sensor_type: Option<String>,
    /// 传感器状态
    pub status: Option<String>,
}

/// 传感器历史查询参数
#[derive(Debug, Deserialize)]
pub struct SensorHistoryParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 最小值
    pub min_value: Option<f64>,
    /// 最大值
    pub max_value: Option<f64>,
    /// 传感器类型
    pub sensor_type: Option<SensorType>,
    /// 传感器状态
    pub status: Option<SensorStatus>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 传感器统计查询参数
#[derive(Debug, Deserialize)]
pub struct SensorStatsParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
}

/// 传感器趋势查询参数
#[derive(Debug, Deserialize)]
pub struct SensorTrendParams {
    /// 传感器ID
    pub sensor_id: String,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
}

/// 传感器导出参数
#[derive(Debug, Deserialize)]
pub struct SensorExportParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 导出格式
    pub format: ExportFormat,
}

/// 传感器配置查询参数
#[derive(Debug, Deserialize)]
pub struct SensorConfigQueryParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
}

/// 异常检测参数
#[derive(Debug, Deserialize)]
pub struct AnomalyDetectionParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 异常阈值
    pub threshold: Option<f64>,
    /// 时间窗口（小时）
    pub time_window: Option<u32>,
}

/// 校准传感器请求
#[derive(Debug, Deserialize)]
pub struct CalibrateSensorRequest {
    /// 校准值
    pub calibration_value: f64,
}

/// 设置传感器配置请求
#[derive(Debug, Deserialize)]
pub struct SetSensorConfigurationRequest {
    /// 传感器ID
    pub sensor_id: String,
    /// 传感器配置
    pub configuration: SensorConfig,
}

/// 更新传感器配置请求
#[derive(Debug, Deserialize)]
pub struct UpdateSensorConfigRequest {
    /// 传感器配置
    pub configuration: SensorConfig,
}

/// 导出格式
#[derive(Debug, Clone, Deserialize)]
pub enum ExportFormat {
    Csv,
    Json,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::services::SensorService;
    use actix_web::{test, web, App, http::StatusCode};

    #[actix_web::test]
    async fn test_sensor_controller_routes() {
        let sensor_service = web::Data::new(SensorService::new().await.unwrap());
        
        let app = test::init_service(
            App::new()
                .app_data(sensor_service.clone())
                .service(
                    web::scope("/api/v1")
                        .configure(SensorController::configure)
                )
        ).await;
        
        // 测试获取所有传感器
        let req = test::TestRequest::get()
            .uri("/api/v1/sensors")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);
    }

    #[test]
    fn test_calibrate_sensor_request_deserialization() {
        let json = r#"{"calibration_value": 25.0}"#;
        let request: CalibrateSensorRequest = serde_json::from_str(json).unwrap();
        
        assert_eq!(request.calibration_value, 25.0);
    }

    #[test]
    fn test_sensor_history_params_deserialization() {
        let json = r#"{"sensor_id": "temp_01", "limit": 100}"#;
        let params: SensorHistoryParams = serde_json::from_str(json).unwrap();
        
        assert_eq!(params.sensor_id, Some("temp_01".to_string()));
        assert_eq!(params.limit, Some(100));
    }
}