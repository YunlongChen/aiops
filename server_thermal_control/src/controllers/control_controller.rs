use crate::models::{
    api::{ApiResponse, PaginationParams, TimeRangeParams},
    control::*,
    error::{AppError, AppResult},
};
use crate::services::ControlService;
use actix_web::{
    delete, get, post, put,
    web::{Data, Path, Query, ServiceConfig},
    HttpResponse, Result as ActixResult,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{error, info, warn};

/// 控制控制器
///
/// 提供智能温度控制和风扇调节的HTTP API接口
#[derive(Clone)]
pub struct ControlController {
    control_service: Arc<ControlService>,
}

impl ControlController {
    /// 创建新的控制控制器
    ///
    /// # 参数
    /// * `control_service` - 控制服务
    pub fn new(control_service: Arc<ControlService>) -> Self {
        Self { control_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/control")
                .route(
                    "/start",
                    actix_web::web::post().to(Self::start_auto_control),
                )
                .route("/stop", actix_web::web::post().to(Self::stop_auto_control))
                .route(
                    "/status",
                    actix_web::web::get().to(Self::get_control_status),
                )
                .route(
                    "/config",
                    actix_web::web::get().to(Self::get_control_config),
                )
                .route(
                    "/config",
                    actix_web::web::put().to(Self::update_control_config),
                )
                .route(
                    "/fan/{fan_id}/speed",
                    actix_web::web::post().to(Self::set_fan_speed),
                )
                .route(
                    "/strategy",
                    actix_web::web::post().to(Self::apply_control_strategy),
                )
                .route(
                    "/emergency/cooling",
                    actix_web::web::post().to(Self::emergency_cooling),
                )
                .route(
                    "/emergency/exit",
                    actix_web::web::post().to(Self::exit_emergency_mode),
                )
                .route(
                    "/history",
                    actix_web::web::get().to(Self::get_control_history),
                )
                .route(
                    "/performance",
                    actix_web::web::get().to(Self::get_control_performance),
                )
                .route(
                    "/optimize",
                    actix_web::web::post().to(Self::optimize_control_parameters),
                )
                .route(
                    "/parameters",
                    actix_web::web::get().to(Self::get_control_parameters),
                ),
        );
    }

    /// 启动自动控制
    ///
    /// POST /api/v1/control/start
    async fn start_auto_control(
        service: Data<ControlService>,
        request: actix_web::web::Json<StartControlRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("启动自动控制");

        let result = service
            .start_auto_control(request.into_inner())
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 停止自动控制
    ///
    /// POST /api/v1/control/stop
    async fn stop_auto_control(service: Data<ControlService>) -> ActixResult<HttpResponse> {
        info!("停止自动控制");

        let result = service
            .stop_auto_control()
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取控制状态
    ///
    /// GET /api/v1/control/status
    async fn get_control_status(service: Data<ControlService>) -> ActixResult<HttpResponse> {
        info!("获取控制状态");

        let status = service
            .get_control_status()
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(status)))
    }

    /// 获取控制配置
    ///
    /// GET /api/v1/control/config
    async fn get_control_config(service: Data<ControlService>) -> ActixResult<HttpResponse> {
        info!("获取控制配置");

        let config = service
            .get_control_config()
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新控制配置
    ///
    /// PUT /api/v1/control/config
    async fn update_control_config(
        service: Data<ControlService>,
        config: actix_web::web::Json<ControlConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新控制配置");

        service
            .update_control_config(config.into_inner())
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 设置风扇转速
    ///
    /// POST /api/v1/control/fan/:fan_id/speed
    async fn set_fan_speed(
        service: Data<ControlService>,
        fan_id: Path<String>,
        request: actix_web::web::Json<SetFanSpeedRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("设置风扇转速: {}", fan_id);

        let result = service
            .set_fan_speed(&fan_id, request.into_inner())
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 应用控制策略
    ///
    /// POST /api/v1/control/strategy
    async fn apply_control_strategy(
        service: Data<ControlService>,
        strategy: actix_web::web::Json<ControlStrategy>,
    ) -> ActixResult<HttpResponse> {
        info!("应用控制策略");

        let result = service
            .apply_control_strategy(strategy.into_inner())
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 紧急冷却
    ///
    /// POST /api/v1/control/emergency/cooling
    async fn emergency_cooling(
        service: Data<ControlService>,
        request: actix_web::web::Json<EmergencyCoolingRequest>,
    ) -> ActixResult<HttpResponse> {
        warn!("启动紧急冷却");

        let result = service
            .emergency_cooling(request.into_inner())
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 退出紧急模式
    ///
    /// POST /api/v1/control/emergency/exit
    async fn exit_emergency_mode(service: Data<ControlService>) -> ActixResult<HttpResponse> {
        info!("退出紧急模式");

        let result = service
            .exit_emergency_mode()
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取控制历史
    ///
    /// GET /api/v1/control/history
    async fn get_control_history(
        service: Data<ControlService>,
        params: Query<ControlHistoryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取控制历史");

        let history = service
            .get_control_history(
                params.limit.unwrap_or(100),
                params.offset.unwrap_or(0),
                params.start_time,
                params.end_time,
            )
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(history)))
    }

    /// 获取控制性能指标
    ///
    /// GET /api/v1/control/performance
    async fn get_control_performance(
        service: Data<ControlService>,
        params: Query<TimeRangeParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取控制性能指标");

        let performance = service
            .get_control_performance(params.start_time, params.end_time)
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(performance)))
    }

    /// 优化控制参数
    ///
    /// POST /api/v1/control/optimize
    async fn optimize_control_parameters(
        service: Data<ControlService>,
        request: actix_web::web::Json<OptimizeParametersRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("优化控制参数");

        let result = service
            .optimize_control_parameters(request.into_inner())
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取控制参数
    ///
    /// GET /api/v1/control/parameters
    async fn get_control_parameters(service: Data<ControlService>) -> ActixResult<HttpResponse> {
        info!("获取控制参数");

        let parameters = service
            .get_control_parameters()
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(parameters)))
    }

    /// 应用优化后的参数
    ///
    /// PUT /api/v1/control/parameters
    async fn apply_optimized_parameters(
        service: Data<ControlService>,
        parameters: actix_web::web::Json<ControlParameters>,
    ) -> ActixResult<HttpResponse> {
        info!("应用优化后的参数");

        service
            .apply_optimized_parameters(parameters.into_inner())
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取控制分析
    ///
    /// GET /api/v1/control/analysis
    async fn get_control_analysis(
        service: Data<ControlService>,
        params: Query<ControlAnalysisParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取控制分析");

        let analysis = service
            .get_control_analysis(
                params.time_window_hours.unwrap_or(24),
                params.include_predictions.unwrap_or(false),
            )
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(analysis)))
    }

    /// 获取控制预设列表
    ///
    /// GET /api/v1/control/presets
    async fn get_control_presets(service: Data<ControlService>) -> ActixResult<HttpResponse> {
        info!("获取控制预设列表");

        let presets = service
            .get_control_presets()
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(presets)))
    }

    /// 创建控制预设
    ///
    /// POST /api/v1/control/presets
    async fn create_control_preset(
        service: Data<ControlService>,
        preset: actix_web::web::Json<CreatePresetRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("创建控制预设: {}", preset.name);

        let created_preset = service
            .create_control_preset(
                preset.name.clone(),
                preset.description.clone(),
                preset.config.clone(),
            )
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(created_preset)))
    }

    /// 获取指定控制预设
    ///
    /// GET /api/v1/control/presets/:preset_id
    async fn get_control_preset(
        service: Data<ControlService>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let preset_id = path.into_inner();
        info!("获取控制预设: {}", preset_id);

        let preset = service
            .get_control_preset(&preset_id)
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(preset)))
    }

    /// 更新控制预设
    ///
    /// PUT /api/v1/control/presets/:preset_id
    async fn update_control_preset(
        service: Data<ControlService>,
        path: Path<String>,
        preset: actix_web::web::Json<UpdatePresetRequest>,
    ) -> ActixResult<HttpResponse> {
        let preset_id = path.into_inner();
        info!("更新控制预设: {}", preset_id);

        service
            .update_control_preset(
                &preset_id,
                preset.name.clone(),
                preset.description.clone(),
                preset.config.clone(),
            )
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 删除控制预设
    ///
    /// DELETE /api/v1/control/presets/:preset_id
    async fn delete_control_preset(
        service: Data<ControlService>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let preset_id = path.into_inner();
        info!("删除控制预设: {}", preset_id);

        service
            .delete_control_preset(&preset_id)
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 应用控制预设
    ///
    /// POST /api/v1/control/presets/:preset_id/apply
    async fn apply_control_preset(
        service: Data<ControlService>,
        path: Path<String>,
    ) -> ActixResult<HttpResponse> {
        let preset_id = path.into_inner();
        info!("应用控制预设: {}", preset_id);

        service
            .apply_control_preset(&preset_id)
            .await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }
}

// 请求和响应结构体

/// 启动控制请求
#[derive(Debug, Deserialize)]
pub struct StartControlRequest {
    /// 控制配置
    pub config: Option<ControlConfig>,
}

/// 设置风扇转速请求
#[derive(Debug, Deserialize)]
pub struct SetFanSpeedRequest {
    /// 转速（RPM）
    pub speed: u32,
}

/// 应用策略请求
#[derive(Debug, Deserialize)]
pub struct ApplyStrategyRequest {
    /// 控制策略
    pub strategy: ControlStrategy,
}

/// 紧急冷却请求
#[derive(Debug, Deserialize)]
pub struct EmergencyCoolingRequest {
    /// 原因
    pub reason: Option<String>,
    /// 最大风扇转速
    pub max_fan_speed: Option<u32>,
}

/// 控制历史参数
#[derive(Debug, Deserialize)]
pub struct ControlHistoryParams {
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 动作类型
    pub action_type: Option<Vec<String>>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 控制性能参数
#[derive(Debug, Deserialize)]
pub struct ControlPerformanceParams {
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
}

/// 优化参数请求
#[derive(Debug, Deserialize)]
pub struct OptimizeParametersRequest {
    /// 优化目标
    pub optimization_target: OptimizationTarget,
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
}

/// 控制分析参数
#[derive(Debug, Deserialize)]
pub struct ControlAnalysisParams {
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
    /// 是否包含预测
    pub include_predictions: Option<bool>,
}

/// 创建预设请求
#[derive(Debug, Deserialize)]
pub struct CreatePresetRequest {
    /// 预设名称
    pub name: String,
    /// 描述
    pub description: Option<String>,
    /// 控制配置
    pub config: ControlConfig,
}

/// 更新预设请求
#[derive(Debug, Deserialize)]
pub struct UpdatePresetRequest {
    /// 预设名称
    pub name: Option<String>,
    /// 描述
    pub description: Option<String>,
    /// 控制配置
    pub config: Option<ControlConfig>,
}

/// 优化目标
#[derive(Debug, Clone, Deserialize)]
pub enum OptimizationTarget {
    /// 温度稳定性
    TemperatureStability,
    /// 能效
    EnergyEfficiency,
    /// 噪音最小化
    NoiseMinimization,
    /// 响应速度
    ResponseSpeed,
}

/// 控制状态
#[derive(Debug, Serialize)]
pub struct ControlStatus {
    /// 是否启用自动控制
    pub auto_control_enabled: bool,
    /// 当前控制策略
    pub current_strategy: ControlStrategy,
    /// 是否处于紧急模式
    pub emergency_mode: bool,
    /// 启动时间
    pub started_at: Option<chrono::DateTime<chrono::Utc>>,
    /// 运行时长（秒）
    pub uptime_seconds: Option<u64>,
    /// 控制循环统计
    pub control_loop_stats: ControlLoopStats,
    /// 最后错误
    pub last_error: Option<String>,
}

/// 控制循环统计
#[derive(Debug, Serialize)]
pub struct ControlLoopStats {
    /// 总循环次数
    pub total_loops: u64,
    /// 成功循环次数
    pub successful_loops: u64,
    /// 失败循环次数
    pub failed_loops: u64,
    /// 平均循环时间（毫秒）
    pub avg_loop_time_ms: f64,
    /// 最后循环时间
    pub last_loop_at: Option<chrono::DateTime<chrono::Utc>>,
}

/// 控制历史条目
#[derive(Debug, Serialize)]
pub struct ControlHistoryEntry {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 动作类型
    pub action_type: String,
    /// 目标（风扇ID等）
    pub target: String,
    /// 动作详情
    pub action_details: serde_json::Value,
    /// 结果
    pub result: String,
    /// 原因
    pub reason: Option<String>,
}

/// 控制性能指标
#[derive(Debug, Serialize)]
pub struct ControlPerformanceMetrics {
    /// 时间窗口
    pub time_window_hours: u32,
    /// 温度控制效果
    pub temperature_control: TemperatureControlMetrics,
    /// 风扇控制效果
    pub fan_control: FanControlMetrics,
    /// 系统稳定性
    pub system_stability: SystemStabilityMetrics,
    /// 能效指标
    pub energy_efficiency: EnergyEfficiencyMetrics,
}

/// 温度控制指标
#[derive(Debug, Serialize)]
pub struct TemperatureControlMetrics {
    /// 平均温度偏差
    pub avg_temperature_deviation: f64,
    /// 最大温度偏差
    pub max_temperature_deviation: f64,
    /// 温度稳定性分数（0-100）
    pub stability_score: f64,
    /// 超温事件数
    pub overheat_events: usize,
}

/// 风扇控制指标
#[derive(Debug, Serialize)]
pub struct FanControlMetrics {
    /// 平均风扇利用率
    pub avg_fan_utilization: f64,
    /// 风扇调节频率
    pub fan_adjustment_frequency: f64,
    /// 风扇效率分数（0-100）
    pub efficiency_score: f64,
    /// 风扇故障次数
    pub fan_failures: usize,
}

/// 系统稳定性指标
#[derive(Debug, Serialize)]
pub struct SystemStabilityMetrics {
    /// 稳定性分数（0-100）
    pub stability_score: f64,
    /// 控制振荡次数
    pub oscillation_count: usize,
    /// 紧急模式触发次数
    pub emergency_triggers: usize,
    /// 平均响应时间（秒）
    pub avg_response_time_seconds: f64,
}

/// 能效指标
#[derive(Debug, Serialize)]
pub struct EnergyEfficiencyMetrics {
    /// 能效分数（0-100）
    pub efficiency_score: f64,
    /// 估算功耗（瓦特）
    pub estimated_power_consumption: f64,
    /// 功耗节省百分比
    pub power_savings_percent: f64,
    /// 冷却效率
    pub cooling_efficiency: f64,
}

/// 优化结果
#[derive(Debug, Serialize)]
pub struct OptimizationResult {
    /// 优化目标
    pub optimization_target: OptimizationTarget,
    /// 优化前参数
    pub original_parameters: ControlParameters,
    /// 优化后参数
    pub optimized_parameters: ControlParameters,
    /// 预期改进
    pub expected_improvements: ExpectedImprovements,
    /// 优化置信度
    pub confidence: f64,
    /// 优化时间
    pub optimized_at: chrono::DateTime<chrono::Utc>,
}

/// 预期改进
#[derive(Debug, Serialize)]
pub struct ExpectedImprovements {
    /// 温度稳定性改进百分比
    pub temperature_stability_improvement: f64,
    /// 能效改进百分比
    pub energy_efficiency_improvement: f64,
    /// 噪音减少百分比
    pub noise_reduction: f64,
    /// 响应速度改进百分比
    pub response_speed_improvement: f64,
}

/// 控制参数
#[derive(Debug, Serialize, Deserialize)]
pub struct ControlParameters {
    /// PID参数
    pub pid_parameters: PidParameters,
    /// 温度阈值
    pub temperature_thresholds: TemperatureThresholds,
    /// 风扇曲线
    pub fan_curves: std::collections::HashMap<String, FanCurve>,
    /// 控制间隔（毫秒）
    pub control_interval_ms: u64,
}

/// PID参数
#[derive(Debug, Serialize, Deserialize)]
pub struct PidParameters {
    /// 比例系数
    pub kp: f64,
    /// 积分系数
    pub ki: f64,
    /// 微分系数
    pub kd: f64,
    /// 输出限制
    pub output_limits: (f64, f64),
}

/// 温度阈值
#[derive(Debug, Serialize, Deserialize)]
pub struct TemperatureThresholds {
    /// 目标温度
    pub target_temperature: f64,
    /// 警告温度
    pub warning_temperature: f64,
    /// 临界温度
    pub critical_temperature: f64,
    /// 紧急温度
    pub emergency_temperature: f64,
}

/// 风扇曲线
#[derive(Debug, Serialize, Deserialize)]
pub struct FanCurve {
    /// 曲线点
    pub points: Vec<FanCurvePoint>,
    /// 最小转速
    pub min_speed: u32,
    /// 最大转速
    pub max_speed: u32,
}

/// 风扇曲线点
#[derive(Debug, Serialize, Deserialize)]
pub struct FanCurvePoint {
    /// 温度
    pub temperature: f64,
    /// 转速百分比（0-100）
    pub speed_percent: f64,
}

/// 控制分析
#[derive(Debug, Serialize)]
pub struct ControlAnalysis {
    /// 时间窗口
    pub time_window_hours: u32,
    /// 控制效果分析
    pub control_effectiveness: ControlEffectivenessAnalysis,
    /// 系统行为分析
    pub system_behavior: SystemBehaviorAnalysis,
    /// 优化建议
    pub optimization_suggestions: Vec<OptimizationSuggestion>,
    /// 预测（如果请求）
    pub predictions: Option<ControlPredictions>,
}

/// 控制效果分析
#[derive(Debug, Serialize)]
pub struct ControlEffectivenessAnalysis {
    /// 整体效果分数（0-100）
    pub overall_effectiveness: f64,
    /// 温度控制效果
    pub temperature_control_effectiveness: f64,
    /// 风扇控制效果
    pub fan_control_effectiveness: f64,
    /// 响应时间分析
    pub response_time_analysis: ResponseTimeAnalysis,
}

/// 响应时间分析
#[derive(Debug, Serialize)]
pub struct ResponseTimeAnalysis {
    /// 平均响应时间（秒）
    pub avg_response_time: f64,
    /// 最快响应时间（秒）
    pub fastest_response_time: f64,
    /// 最慢响应时间（秒）
    pub slowest_response_time: f64,
    /// 响应时间标准差
    pub response_time_std_dev: f64,
}

/// 系统行为分析
#[derive(Debug, Serialize)]
pub struct SystemBehaviorAnalysis {
    /// 稳定性分析
    pub stability_analysis: StabilityAnalysis,
    /// 振荡检测
    pub oscillation_detection: OscillationDetection,
    /// 异常行为检测
    pub anomaly_detection: Vec<BehaviorAnomaly>,
}

/// 稳定性分析
#[derive(Debug, Serialize)]
pub struct StabilityAnalysis {
    /// 稳定性分数（0-100）
    pub stability_score: f64,
    /// 稳定时间百分比
    pub stable_time_percent: f64,
    /// 不稳定事件数
    pub instability_events: usize,
    /// 平均稳定时间（分钟）
    pub avg_stable_duration_minutes: f64,
}

/// 振荡检测
#[derive(Debug, Serialize)]
pub struct OscillationDetection {
    /// 是否检测到振荡
    pub oscillation_detected: bool,
    /// 振荡频率（次/小时）
    pub oscillation_frequency: f64,
    /// 振荡幅度
    pub oscillation_amplitude: f64,
    /// 振荡持续时间（分钟）
    pub oscillation_duration_minutes: f64,
}

/// 行为异常
#[derive(Debug, Serialize)]
pub struct BehaviorAnomaly {
    /// 异常类型
    pub anomaly_type: String,
    /// 严重程度
    pub severity: String,
    /// 描述
    pub description: String,
    /// 发生时间
    pub occurred_at: chrono::DateTime<chrono::Utc>,
    /// 持续时间（分钟）
    pub duration_minutes: f64,
}

/// 优化建议
#[derive(Debug, Serialize)]
pub struct OptimizationSuggestion {
    /// 建议类型
    pub suggestion_type: String,
    /// 优先级
    pub priority: String,
    /// 描述
    pub description: String,
    /// 预期改进
    pub expected_improvement: f64,
    /// 实施难度
    pub implementation_difficulty: String,
}

/// 控制预测
#[derive(Debug, Serialize)]
pub struct ControlPredictions {
    /// 温度预测
    pub temperature_predictions: Vec<TemperaturePrediction>,
    /// 风扇转速预测
    pub fan_speed_predictions: Vec<FanSpeedPrediction>,
    /// 系统负载预测
    pub system_load_predictions: Vec<SystemLoadPrediction>,
    /// 预测置信度
    pub prediction_confidence: f64,
}

/// 温度预测
#[derive(Debug, Serialize)]
pub struct TemperaturePrediction {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 预测温度
    pub predicted_temperature: f64,
    /// 置信区间
    pub confidence_interval: (f64, f64),
}

/// 风扇转速预测
#[derive(Debug, Serialize)]
pub struct FanSpeedPrediction {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 风扇ID
    pub fan_id: String,
    /// 预测转速
    pub predicted_speed: u32,
    /// 置信区间
    pub confidence_interval: (u32, u32),
}

/// 系统负载预测
#[derive(Debug, Serialize)]
pub struct SystemLoadPrediction {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 预测负载百分比
    pub predicted_load_percent: f64,
    /// 置信区间
    pub confidence_interval: (f64, f64),
}

/// 控制预设
#[derive(Debug, Serialize, Deserialize)]
pub struct ControlPreset {
    /// 预设ID
    pub id: String,
    /// 名称
    pub name: String,
    /// 描述
    pub description: Option<String>,
    /// 控制配置
    pub config: ControlConfig,
    /// 创建时间
    pub created_at: chrono::DateTime<chrono::Utc>,
    /// 更新时间
    pub updated_at: chrono::DateTime<chrono::Utc>,
    /// 是否为系统预设
    pub is_system_preset: bool,
}

/// 控制动作
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ControlAction {
    /// 动作ID
    pub id: String,
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 动作类型
    pub action_type: ControlActionType,
    /// 目标组件
    pub target_component: String,
    /// 之前的值
    pub previous_value: f64,
    /// 新值
    pub new_value: f64,
    /// 原因
    pub reason: String,
    /// 是否成功
    pub success: bool,
    /// 错误信息
    pub error_message: Option<String>,
}

/// 控制动作类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ControlActionType {
    /// 手动风扇控制
    ManualFanControl,
    /// 紧急冷却
    EmergencyCooling,
    /// 参数优化
    ParameterOptimization,
    /// 自动控制
    AutomaticControl,
}

/// 控制优化结果
#[derive(Debug, Serialize, Deserialize)]
pub struct ControlOptimizationResult {
    /// 优化ID
    pub optimization_id: String,
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 原始参数
    pub original_parameters:
        std::collections::HashMap<String, std::collections::HashMap<String, f64>>,
    /// 优化后参数
    pub optimized_parameters:
        std::collections::HashMap<String, std::collections::HashMap<String, f64>>,
    /// 性能改进百分比
    pub performance_improvement: f64,
    /// 建议列表
    pub recommendations: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::MonitoringConfig;
    use crate::services::ipmi_service::{IpmiConfig, IpmiService};
    use crate::services::{
        ControlService, FanService, MonitoringService, SensorService, ThermalService,
    };
    use actix_web::{http::StatusCode, test, web, App};

    /// 测试控制控制器路由
    #[actix_web::test]
    async fn test_control_controller_routes() {
        let impi_service = Arc::new(IpmiService::new(IpmiConfig::default()));

        let thermal_service = Arc::new(
            ThermalService::new(
                impi_service,
                MonitoringConfig {
                    collection_interval: 0,
                    retention_days: 0,
                    enable_performance_monitoring: false,
                    enable_health_checks: false,
                    health_check_interval: 0,
                    metrics_export: Default::default(),
                },
            )
            .await
            .unwrap(),
        );

        let fan_service = Arc::new(
            FanService::new(impi_service, MonitoringConfig::default())
                .await
                .unwrap(),
        );
        let sensor_service = Arc::new(SensorService::new().await.unwrap());
        let monitoring_service = Arc::new(
            MonitoringService::new(
                thermal_service.clone(),
                fan_service.clone(),
                sensor_service.clone(),
                Arc::new(crate::services::AlertService::new().await.unwrap()),
            )
            .await
            .unwrap(),
        );
        let control_service = Arc::new(
            ControlService::new(
                thermal_service,
                fan_service,
                sensor_service,
                monitoring_service,
            )
            .await
            .unwrap(),
        );

        let app = test::init_service(
            App::new()
                .app_data(web::Data::new(control_service))
                .configure(ControlController::configure),
        )
        .await;

        // 测试获取控制状态
        let req = test::TestRequest::get().uri("/control/status").to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);

        // 测试获取控制参数
        let req = test::TestRequest::get()
            .uri("/control/parameters")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);
    }

    /// 测试设置风扇转速请求反序列化
    #[test]
    fn test_set_fan_speed_request_deserialization() {
        let json = r#"{"speed": 2000}"#;
        let request: SetFanSpeedRequest = serde_json::from_str(json).unwrap();

        assert_eq!(request.speed, 2000);
    }

    /// 测试优化目标反序列化
    #[test]
    fn test_optimization_target_deserialization() {
        let json = r#""TemperatureStability""#;
        let target: OptimizationTarget = serde_json::from_str(json).unwrap();

        matches!(target, OptimizationTarget::TemperatureStability);
    }
}
