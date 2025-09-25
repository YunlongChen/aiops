use crate::models::{
    error::{AppError, AppResult},
    fan::*,
    api::{ApiResponse, PaginationParams, TimeRangeParams},
};
use crate::services::FanService;
use actix_web::{
    web::{Path, Query, Data, ServiceConfig},
    HttpResponse, Result as ActixResult,
    get, post, put, delete,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{info, warn, error};

/// 风扇控制器
/// 
/// 提供风扇控制和监控的HTTP API接口
#[derive(Clone)]
pub struct FanController {
    fan_service: Arc<FanService>,
}

impl FanController {
    /// 创建新的风扇控制器
    /// 
    /// # 参数
    /// * `fan_service` - 风扇服务
    pub fn new(fan_service: Arc<FanService>) -> Self {
        Self { fan_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/fans")
                .route("", actix_web::web::get().to(Self::get_fan_status))
                .route("/{fan_id}", actix_web::web::get().to(Self::get_single_fan_status))
                .route("/{fan_id}/speed", actix_web::web::put().to(Self::set_fan_speed))
                .route("/speed", actix_web::web::put().to(Self::set_all_fan_speeds))
                .route("/history", actix_web::web::get().to(Self::get_fan_history))
                .route("/statistics", actix_web::web::get().to(Self::get_fan_statistics))
                .route("/list", actix_web::web::get().to(Self::get_fan_list))
                .route("/{fan_id}/test", actix_web::web::post().to(Self::test_fan))
                .route("/auto-control", actix_web::web::get().to(Self::get_auto_control_status))
                .route("/auto-control/enable", actix_web::web::post().to(Self::enable_auto_control))
                .route("/auto-control/disable", actix_web::web::post().to(Self::disable_auto_control))
                .route("/auto-control/execute", actix_web::web::post().to(Self::execute_auto_control))
                .route("/configurations", actix_web::web::get().to(Self::get_fan_configurations))
        );
    }

    /// 获取风扇状态
    /// 
    /// GET /api/v1/fans
    async fn get_fan_status(
        service: Data<Arc<FanService>>,
        Query(params): Query<FanQueryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取风扇状态");

        let fan_status = if let Some(fan_ids) = params.fan_ids {
            let mut results = Vec::new();
            for fan_id in fan_ids {
                if let Ok(status) = service.get_fan_status(&fan_id).await {
                    results.push(status);
                }
            }
            results
        } else {
            match service.get_all_fan_status().await {
                Ok(status) => status,
                Err(e) => {
                    error!("获取风扇状态失败: {}", e);
                    return Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())));
                }
            }
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(fan_status)))
    }

    /// 获取单个风扇状态
    /// 
    /// GET /api/v1/fans/:fan_id
    async fn get_single_fan_status(
        service: Data<Arc<FanService>>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let fan_id = path.into_inner();
        info!("获取风扇状态: {}", fan_id);

        match service.get_fan_status(&fan_id).await {
            Ok(status) => Ok(HttpResponse::Ok().json(ApiResponse::success(status))),
            Err(e) => {
                error!("获取风扇状态失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 设置风扇转速
    /// 
    /// PUT /api/v1/fans/:fan_id/speed
    async fn set_fan_speed(
        service: Data<Arc<FanService>>,
        path: Path<String>,
        actix_web::web::Json(request): actix_web::web::Json<SetFanSpeedRequest>,
    ) -> ActixResult<HttpResponse> {
        let fan_id = path.into_inner();
        info!("设置风扇速度: {} -> {}%", fan_id, request.speed_percent);

        match service.set_fan_speed(&fan_id, request.speed_percent).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("设置风扇转速失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 设置所有风扇转速
    /// 
    /// PUT /api/v1/fans/speed
    async fn set_all_fan_speeds(
        service: Data<Arc<FanService>>,
        actix_web::web::Json(request): actix_web::web::Json<SetAllFanSpeedsRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("设置所有风扇转速: {}%", request.speed_percent);

        match service.set_all_fan_speeds(request.speed_percent).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("设置所有风扇转速失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取风扇历史数据
    /// 
    /// GET /api/v1/fans/history
    async fn get_fan_history(
        service: Data<Arc<FanService>>,
        Query(params): Query<FanHistoryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取风扇历史数据");

        match service.get_fan_history(
            params.fan_id.as_deref(),
            params.start_time,
            params.end_time,
            params.limit,
        ).await {
            Ok(history) => Ok(HttpResponse::Ok().json(ApiResponse::success(history))),
            Err(e) => {
                error!("获取风扇历史数据失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取风扇统计信息
    /// 
    /// GET /api/v1/fans/statistics
    async fn get_fan_statistics(
        service: Data<Arc<FanService>>,
        Query(params): Query<FanStatsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取风扇统计信息");

        match service.get_fan_statistics(
            params.fan_id.as_deref(),
            params.start_time,
            params.end_time,
        ).await {
            Ok(stats) => Ok(HttpResponse::Ok().json(ApiResponse::success(stats))),
            Err(e) => {
                error!("获取风扇统计信息失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取风扇列表
    /// 
    /// GET /api/v1/fans/list
    async fn get_fan_list(
        service: Data<Arc<FanService>>,
    ) -> ActixResult<HttpResponse> {
        info!("获取风扇列表");

        match service.get_fan_list().await {
            Ok(fans) => Ok(HttpResponse::Ok().json(ApiResponse::success(fans))),
            Err(e) => {
                error!("获取风扇列表失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 测试风扇
    /// 
    /// POST /api/v1/fans/:fan_id/test
    async fn test_fan(
        service: Data<Arc<FanService>>,
        path: Path<String>,
        actix_web::web::Json(request): actix_web::web::Json<TestFanRequest>,
    ) -> ActixResult<HttpResponse> {
        let fan_id = path.into_inner();
        info!("测试风扇: {} 持续 {} 秒", fan_id, request.test_duration_seconds);

        match service.test_fan(&fan_id, request.test_duration_seconds).await {
            Ok(result) => Ok(HttpResponse::Ok().json(ApiResponse::success(result))),
            Err(e) => {
                error!("测试风扇失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取自动控制状态
    /// 
    /// GET /api/v1/fans/auto-control
    async fn get_auto_control_status(
        service: Data<Arc<FanService>>,
    ) -> ActixResult<HttpResponse> {
        info!("获取自动控制状态");

        match service.get_auto_control_status().await {
            Ok(status) => Ok(HttpResponse::Ok().json(ApiResponse::success(status))),
            Err(e) => {
                error!("获取自动控制状态失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 启用自动控制
    /// 
    /// POST /api/v1/fans/auto-control/enable
    async fn enable_auto_control(
        service: Data<Arc<FanService>>,
    ) -> ActixResult<HttpResponse> {
        info!("启用风扇自动控制");

        match service.enable_auto_control().await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("启用风扇自动控制失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 禁用自动控制
    /// 
    /// POST /api/v1/fans/auto-control/disable
    async fn disable_auto_control(
        service: Data<Arc<FanService>>,
    ) -> ActixResult<HttpResponse> {
        info!("禁用风扇自动控制");

        match service.disable_auto_control().await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("禁用风扇自动控制失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 执行自动控制
    /// 
    /// POST /api/v1/fans/auto-control/execute
    async fn execute_auto_control(
        service: Data<Arc<FanService>>,
    ) -> ActixResult<HttpResponse> {
        info!("执行风扇自动控制");

        match service.execute_auto_control().await {
            Ok(result) => Ok(HttpResponse::Ok().json(ApiResponse::success(result))),
            Err(e) => {
                error!("执行风扇自动控制失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 获取风扇配置
    /// 
    /// GET /api/v1/fans/configurations
    async fn get_fan_configurations(
        service: Data<Arc<FanService>>,
        Query(params): Query<FanConfigQueryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取风扇配置");

        let configurations = if let Some(fan_id) = params.fan_id {
            match service.get_fan_configuration(&fan_id).await {
                Ok(config) => vec![config],
                Err(e) => {
                    error!("获取风扇配置失败: {}", e);
                    return Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())));
                }
            }
        } else {
            match service.get_all_fan_configurations().await {
                Ok(configs) => configs,
                Err(e) => {
                    error!("获取所有风扇配置失败: {}", e);
                    return Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())));
                }
            }
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(configurations)))
    }

    /// 设置风扇配置
    /// 
    /// POST /api/v1/fans/configurations
    async fn set_fan_configuration(
        service: Data<Arc<FanService>>,
        actix_web::web::Json(request): actix_web::web::Json<SetFanConfigurationRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("设置风扇配置: {}", request.fan_id);

        match service.set_fan_configuration(&request.fan_id, request.configuration).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("设置风扇配置失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 更新风扇配置
    /// 
    /// PUT /api/v1/fans/configurations/:fan_id
    async fn update_fan_configuration(
        service: Data<Arc<FanService>>,
        path: Path<String>,
        config: actix_web::web::Json<FanConfig>,
    ) -> ActixResult<HttpResponse> {
        let fan_id = path.into_inner();
        info!("更新风扇配置: {}", fan_id);

        match service.set_fan_configuration(&fan_id, config.into_inner()).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("更新风扇配置失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 删除风扇配置
    /// 
    /// DELETE /api/v1/fans/configurations/:fan_id
    async fn delete_fan_configuration(
        service: Data<Arc<FanService>>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let fan_id = path.into_inner();
        info!("删除风扇配置: {}", fan_id);

        match service.delete_fan_configuration(&fan_id).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("删除风扇配置失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 优化风扇曲线
    /// 
    /// POST /api/v1/fans/curves/optimize
    async fn optimize_fan_curves(
        service: Data<Arc<FanService>>,
        actix_web::web::Json(request): actix_web::web::Json<OptimizeFanCurvesRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("优化风扇曲线");

        match service.optimize_fan_curves(request.target_temperature, request.max_noise_level).await {
            Ok(curves) => Ok(HttpResponse::Ok().json(ApiResponse::success(curves))),
            Err(e) => {
                error!("优化风扇曲线失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 应用风扇曲线
    /// 
    /// POST /api/v1/fans/curves/apply
    async fn apply_fan_curves(
        service: Data<Arc<FanService>>,
        actix_web::web::Json(request): actix_web::web::Json<ApplyFanCurvesRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("应用风扇曲线");

        match service.apply_fan_curves(request.curves).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => {
                error!("应用风扇曲线失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }

    /// 清理过期数据
    /// 
    /// POST /api/v1/fans/cleanup
    async fn cleanup_expired_data(
        service: Data<Arc<FanService>>,
        actix_web::web::Json(request): actix_web::web::Json<CleanupRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("清理过期风扇数据，保留天数: {}", request.retention_days);

        match service.cleanup_expired_history(request.retention_days).await {
            Ok(result) => Ok(HttpResponse::Ok().json(ApiResponse::success(CleanupResult {
                deleted_count: result,
                cleaned_fans: 0, // 这里需要根据实际实现调整
            }))),
            Err(e) => {
                error!("清理过期风扇数据失败: {}", e);
                Ok(HttpResponse::InternalServerError().json(ApiResponse::<()>::error(&e.to_string())))
            }
        }
    }
}

// 请求和响应结构体

/// 风扇查询参数
#[derive(Debug, Deserialize)]
pub struct FanQueryParams {
    /// 风扇ID列表
    pub fan_ids: Option<Vec<String>>,
}

/// 风扇历史查询参数
#[derive(Debug, Deserialize)]
pub struct FanHistoryParams {
    /// 风扇ID
    pub fan_id: Option<String>,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 风扇统计查询参数
#[derive(Debug, Deserialize)]
pub struct FanStatsParams {
    /// 风扇ID
    pub fan_id: Option<String>,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
}

/// 风扇配置查询参数
#[derive(Debug, Deserialize)]
pub struct FanConfigQueryParams {
    /// 风扇ID
    pub fan_id: Option<String>,
}

/// 设置风扇转速请求
#[derive(Debug, Deserialize)]
pub struct SetFanSpeedRequest {
    /// 转速百分比 (0-100)
    pub speed_percent: u8,
}

/// 设置所有风扇转速请求
#[derive(Debug, Deserialize)]
pub struct SetAllFanSpeedsRequest {
    /// 转速百分比 (0-100)
    pub speed_percent: u8,
}

/// 测试风扇请求
#[derive(Debug, Deserialize)]
pub struct TestFanRequest {
    /// 测试持续时间（秒）
    pub test_duration_seconds: u32,
}

/// 设置风扇配置请求
#[derive(Debug, Deserialize)]
pub struct SetFanConfigurationRequest {
    /// 风扇ID
    pub fan_id: String,
    /// 风扇配置
    pub configuration: FanConfig,
}

/// 优化风扇曲线请求
#[derive(Debug, Deserialize)]
pub struct OptimizeFanCurvesRequest {
    /// 目标温度
    pub target_temperature: f64,
    /// 最大噪音水平
    pub max_noise_level: f64,
}

/// 应用风扇曲线请求
#[derive(Debug, Deserialize)]
pub struct ApplyFanCurvesRequest {
    /// 风扇曲线列表
    pub curves: Vec<crate::controllers::control_controller::FanCurve>,
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
    /// 清理的风扇数
    pub cleaned_fans: usize,
}

/// 自动控制状态
#[derive(Debug, Serialize)]
pub struct AutoControlStatus {
    /// 是否启用
    pub enabled: bool,
    /// 最后执行时间
    pub last_execution: Option<chrono::DateTime<chrono::Utc>>,
    /// 控制模式
    pub control_mode: String,
}

/// 自动控制结果
#[derive(Debug, Serialize)]
pub struct AutoControlResult {
    /// 调整的风扇数量
    pub adjusted_fans: usize,
    /// 平均温度
    pub average_temperature: f64,
    /// 执行时间
    pub execution_time: chrono::DateTime<chrono::Utc>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::services::FanService;
    use actix_web::{test, App};
    use std::sync::Arc;

    #[actix_web::test]
    async fn test_fan_controller_routes() {
        let fan_service = Arc::new(FanService::new().await.unwrap());
        
        let app = test::init_service(
            App::new()
                .app_data(actix_web::web::Data::new(fan_service))
                .configure(FanController::configure)
        ).await;
        
        // 测试获取风扇状态
        let req = test::TestRequest::get()
            .uri("/fans")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
        
        // 测试获取风扇列表
        let req = test::TestRequest::get()
            .uri("/fans/list")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
    }

    #[test]
    fn test_set_fan_speed_request_deserialization() {
        let json = r#"{"speed_percent": 75}"#;
        let request: SetFanSpeedRequest = serde_json::from_str(json).unwrap();
        
        assert_eq!(request.speed_percent, 75);
    }

    #[test]
    fn test_optimize_fan_curves_request_deserialization() {
        let json = r#"{"target_temperature": 65.0, "max_noise_level": 40.0}"#;
        let request: OptimizeFanCurvesRequest = serde_json::from_str(json).unwrap();
        
        assert_eq!(request.target_temperature, 65.0);
        assert_eq!(request.max_noise_level, 40.0);
    }
}