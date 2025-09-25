use crate::models::{
    alert::AlertSeverity,
    api::{ApiResponse, ExportFormat, PaginationParams, TimeRangeParams},
    error::{AppError, AppResult},
    thermal::*,
};
use crate::services::ThermalService;
use crate::utils::time::{TimeUtils, TimeWindow};
use actix_web::{
    delete, get, post, put,
    web::{Data, Path, Query, ServiceConfig},
    HttpResponse, Result as ActixResult,
};
use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{error, info, warn};

/// 温度控制器
///
/// 提供温度数据的HTTP API接口
#[derive(Clone)]
pub struct ThermalController {
    thermal_service: Arc<ThermalService>,
}

impl ThermalController {
    /// 创建新的温度控制器
    ///
    /// # 参数
    /// * `thermal_service` - 温度服务
    pub fn new(thermal_service: Arc<ThermalService>) -> Self {
        Self { thermal_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/temperatures")
                .route("", actix_web::web::get().to(Self::get_current_temperatures))
                .route(
                    "/history",
                    actix_web::web::get().to(Self::get_temperature_history),
                )
                .route(
                    "/statistics",
                    actix_web::web::get().to(Self::get_temperature_statistics),
                )
                .route(
                    "/trends",
                    actix_web::web::get().to(Self::get_temperature_trends),
                )
                .route(
                    "/sensors",
                    actix_web::web::get().to(Self::get_temperature_sensors),
                )
                .route(
                    "/export",
                    actix_web::web::get().to(Self::export_temperature_data),
                )
                .route(
                    "/thresholds",
                    actix_web::web::get().to(Self::get_temperature_thresholds),
                )
                .route(
                    "/thresholds",
                    actix_web::web::post().to(Self::set_temperature_threshold),
                )
                .route(
                    "/thresholds/{sensor_id}",
                    actix_web::web::put().to(Self::update_temperature_threshold),
                )
                .route(
                    "/thresholds/{sensor_id}",
                    actix_web::web::delete().to(Self::delete_temperature_threshold),
                )
                .route(
                    "/alerts",
                    actix_web::web::get().to(Self::get_temperature_alerts),
                )
                .route(
                    "/cleanup",
                    actix_web::web::post().to(Self::cleanup_expired_data),
                ),
        );
    }

    /// 获取当前温度读数
    ///
    /// GET /api/v1/temperatures
    async fn get_current_temperatures(
        service: Data<ThermalService>,
        params: Query<TemperatureQueryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取当前温度读数");

        let temperatures = if let Some(sensor_ids) = params.sensor_ids.clone() {
            let mut results = Vec::new();
            for sensor_id in sensor_ids {
                if let Ok(temp) = service.get_current_temperature(&sensor_id).await {
                    results.push(temp);
                }
            }
            results
        } else {
            match service.get_all_current_temperatures().await {
                Ok(temps) => temps,
                Err(e) => {
                    error!("获取温度数据失败: {}", e);
                    return Ok(HttpResponse::InternalServerError()
                        .json(ApiResponse::<()>::error("获取温度数据失败")));
                }
            }
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(temperatures)))
    }

    /// 获取温度历史数据
    ///
    /// GET /api/v1/temperatures/history
    async fn get_temperature_history(
        service: Data<ThermalService>,
        params: Query<TemperatureHistoryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取温度历史数据");

        match service
            .get_temperature_history(&TemperatureQuery {
                server_id: None,
                sensor_id: params.sensor_id,
                start_time: params.start_time,
                end_time: params.end_time,
                page: None,
                limit: params.limit,
            })
            .await
        {
            Ok(history) => Ok(HttpResponse::Ok().json(ApiResponse::success(history))),
            Err(e) => {
                error!("获取温度历史数据失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("获取温度历史数据失败")))
            }
        }
    }

    /// 获取温度统计信息
    ///
    /// GET /api/v1/temperatures/statistics
    async fn get_temperature_statistics(
        service: Data<ThermalService>,
        params: Query<TemperatureStatsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取温度统计信息");

        match service
            .get_temperature_statistics(
                params.sensor_id.as_deref(),
                params.start_time,
                params.end_time,
            )
            .await
        {
            Ok(stats) => Ok(HttpResponse::Ok().json(ApiResponse::success(stats))),
            Err(e) => {
                error!("获取温度统计信息失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("获取温度统计信息失败")))
            }
        }
    }

    /// 获取温度趋势分析
    ///
    /// GET /api/v1/temperatures/trends
    async fn get_temperature_trends(
        service: Data<ThermalService>,
        params: Query<TemperatureTrendParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取温度趋势分析");

        let duration = TimeUtils::try_duration_seconds_of_from_now(
            params.start_time,
            params.end_time,
            Utc::now(),
        );
        match duration {
            Ok(duration) => match service
                .get_temperature_trend(&params.sensor_id, duration as u64)
                .await
            {
                Ok(trend) => Ok(HttpResponse::Ok().json(ApiResponse::success(trend))),
                Err(e) => {
                    error!("获取温度趋势分析失败: {}", e);
                    Ok(HttpResponse::InternalServerError()
                        .json(ApiResponse::<()>::error("获取温度趋势分析失败")))
                }
            },
            Err(e) => {
                error!("获取温度趋势分析失败:获取时间间隔异常: {}", e);
                Ok(
                    HttpResponse::InternalServerError().json(ApiResponse::<()>::error(
                        "获取温度趋势分析失败:获取时间间隔异常",
                    )),
                )
            }
        }
    }

    /// 获取温度传感器列表
    ///
    /// GET /api/v1/temperatures/sensors
    async fn get_temperature_sensors(service: Data<ThermalService>) -> ActixResult<HttpResponse> {
        info!("获取温度传感器列表");

        match service.get_temperature_sensors().await {
            Ok(sensors) => Ok(HttpResponse::Ok().json(ApiResponse::success(sensors))),
            Err(e) => {
                error!("获取温度传感器列表失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("获取温度传感器列表失败")))
            }
        }
    }

    /// 导出温度数据
    ///
    /// GET /api/v1/temperatures/export
    async fn export_temperature_data(
        service: Data<ThermalService>,
        params: Query<TemperatureExportParams>,
    ) -> ActixResult<HttpResponse> {
        info!("导出温度数据，格式: {:?}", params.format);

        match service
            .export_temperature_data(
                params.sensor_id.as_deref(),
                params.start_time,
                params.end_time,
                params.format,
            )
            .await
        {
            Ok(data) => Ok(HttpResponse::Ok().json(ApiResponse::success(data))),
            Err(e) => {
                error!("导出温度数据失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("导出温度数据失败")))
            }
        }
    }

    /// 获取温度阈值配置
    ///
    /// GET /api/v1/temperatures/thresholds
    async fn get_temperature_thresholds(
        service: Data<ThermalService>,
        params: Query<ThresholdQueryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取温度阈值配置");

        let result = if let Some(sensor_id) = &params.sensor_id {
            service
                .get_temperature_threshold(sensor_id)
                .await
                .map(|t| vec![t])
        } else {
            service.get_all_temperature_thresholds().await
        };

        match result {
            Ok(thresholds) => Ok(HttpResponse::Ok().json(ApiResponse::success(thresholds))),
            Err(e) => {
                error!("获取温度阈值配置失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("获取温度阈值配置失败")))
            }
        }
    }

    /// 设置温度阈值
    ///
    /// POST /api/v1/temperatures/thresholds
    async fn set_temperature_threshold(
        service: Data<ThermalService>,
        request: actix_web::web::Json<SetTemperatureThresholdRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("设置温度阈值: {}", request.sensor_id);

        match service
            .set_temperature_threshold(TemperatureThreshold {
                id: Default::default(),
                component_type: "".to_string(),
                sensor_id: request.sensor_id.clone(),
                normal_max: 0.0,
                warning_max: request.warning_temp,
                critical_max: 0.0,
                created_at: Default::default(),
                updated_at: Default::default(),
            })
            .await
        {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("设置温度阈值失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("设置温度阈值失败")))
            }
        }
    }

    /// 更新温度阈值
    ///
    /// PUT /api/v1/temperatures/thresholds/{sensor_id}
    async fn update_temperature_threshold(
        service: Data<ThermalService>,
        sensor_id: Path<String>,
        request: actix_web::web::Json<UpdateTemperatureThresholdRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("更新温度阈值: {}", sensor_id);

        match service
            .set_temperature_threshold(&sensor_id, request.warning_temp, request.critical_temp)
            .await
        {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("更新温度阈值失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("更新温度阈值失败")))
            }
        }
    }

    /// 删除温度阈值
    ///
    /// DELETE /api/v1/temperatures/thresholds/{sensor_id}
    async fn delete_temperature_threshold(
        service: Data<ThermalService>,
        sensor_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("删除温度阈值: {}", sensor_id);

        match service.delete_temperature_threshold(&sensor_id).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("删除温度阈值失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("删除温度阈值失败")))
            }
        }
    }

    /// 获取温度告警
    ///
    /// GET /api/v1/temperatures/alerts
    async fn get_temperature_alerts(
        service: Data<ThermalService>,
        params: Query<AlertQueryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取温度告警");

        match service
            .check_temperature_alerts(params.sensor_id.as_deref(), params.severity)
            .await
        {
            Ok(alerts) => Ok(HttpResponse::Ok().json(ApiResponse::success(alerts))),
            Err(e) => {
                error!("获取温度告警失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("获取温度告警失败")))
            }
        }
    }

    /// 清理过期数据
    ///
    /// POST /api/v1/temperatures/cleanup
    async fn cleanup_expired_data(
        service: Data<ThermalService>,
        request: actix_web::web::Json<CleanupRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("清理过期温度数据，保留天数: {}", request.retention_days);

        match service.cleanup_expired_data(request.retention_days).await {
            Ok(result) => Ok(HttpResponse::Ok().json(ApiResponse::success(result))),
            Err(e) => {
                error!("清理过期数据失败: {}", e);
                Ok(HttpResponse::InternalServerError()
                    .json(ApiResponse::<()>::error("清理过期数据失败")))
            }
        }
    }
}

// 请求和响应结构体

/// 温度查询参数
#[derive(Debug, Deserialize)]
pub struct TemperatureQueryParams {
    /// 传感器ID列表
    pub sensor_ids: Option<Vec<String>>,
}

/// 温度历史查询参数
#[derive(Debug, Deserialize)]
pub struct TemperatureHistoryParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 开始时间
    pub start_time: Option<DateTime<Utc>>,
    /// 结束时间
    pub end_time: Option<DateTime<Utc>>,
    /// 最低温度
    pub min_temperature: Option<f64>,
    /// 最高温度
    pub max_temperature: Option<f64>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 温度统计查询参数
#[derive(Debug, Deserialize)]
pub struct TemperatureStatsParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 开始时间
    pub start_time: Option<DateTime<Utc>>,
    /// 结束时间
    pub end_time: Option<DateTime<Utc>>,
}

/// 温度趋势查询参数
#[derive(Debug, Deserialize)]
pub struct TemperatureTrendParams {
    /// 传感器ID
    pub sensor_id: String,
    /// 开始时间
    pub start_time: Option<DateTime<Utc>>,
    /// 结束时间
    pub end_time: Option<DateTime<Utc>>,
}

/// 温度导出参数
#[derive(Debug, Deserialize)]
pub struct TemperatureExportParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 开始时间
    pub start_time: Option<DateTime<Utc>>,
    /// 结束时间
    pub end_time: Option<DateTime<Utc>>,
    /// 导出格式
    pub format: ExportFormat,
}

/// 阈值查询参数
#[derive(Debug, Deserialize)]
pub struct ThresholdQueryParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
}

/// 告警查询参数
#[derive(Debug, Deserialize)]
pub struct AlertQueryParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 严重程度
    pub severity: Option<AlertSeverity>,
}

/// 设置温度阈值请求
#[derive(Debug, Deserialize)]
pub struct SetTemperatureThresholdRequest {
    /// 传感器ID
    pub sensor_id: String,
    /// 警告温度
    pub warning_temp: f64,
    /// 严重温度
    pub critical_temp: f64,
}

/// 更新温度阈值请求
#[derive(Debug, Deserialize)]
pub struct UpdateTemperatureThresholdRequest {
    /// 警告温度
    pub warning_temp: f64,
    /// 严重温度
    pub critical_temp: f64,
}

/// 清理请求
#[derive(Debug, Deserialize)]
pub struct CleanupRequest {
    /// 保留天数
    pub retention_days: u32,
}

/// 清理结果
#[derive(Debug, Serialize)]
pub struct CleanupResult {
    /// 删除的记录数
    pub deleted_count: usize,
    /// 清理的传感器数
    pub cleaned_sensors: usize,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::services::ThermalService;
    use actix_web::{http::StatusCode, test, App};

    #[actix_web::test]
    async fn test_thermal_controller_routes() {
        let thermal_service = Arc::new(ThermalService::new().await.unwrap());

        let app = test::init_service(
            App::new()
                .app_data(Data::new(thermal_service.clone()))
                .configure(ThermalController::configure),
        )
        .await;

        // 测试获取当前温度
        let req = test::TestRequest::get().uri("/temperatures").to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);

        // 测试获取传感器列表
        let req = test::TestRequest::get()
            .uri("/temperatures/sensors")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);
    }

    #[test]
    fn test_temperature_query_params_deserialization() {
        let json = r#"{"sensor_ids": ["sensor1", "sensor2"]}"#;
        let params: TemperatureQueryParams = serde_json::from_str(json).unwrap();

        assert!(params.sensor_ids.is_some());
        assert_eq!(params.sensor_ids.unwrap().len(), 2);
    }

    #[test]
    fn test_set_threshold_request_deserialization() {
        let json = r#"{"sensor_id": "temp1", "warning_temp": 70.0, "critical_temp": 85.0}"#;
        let request: SetTemperatureThresholdRequest = serde_json::from_str(json).unwrap();

        assert_eq!(request.sensor_id, "temp1");
        assert_eq!(request.warning_temp, 70.0);
        assert_eq!(request.critical_temp, 85.0);
    }
}
