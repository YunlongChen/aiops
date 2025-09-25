use crate::models::{
    api::{ApiResponse, PaginationParams, TimeRangeParams},
    config::MonitoringConfig,
    error::{AppError, AppResult},
    monitoring::*,
};
use crate::services::MonitoringService;
use actix_web::{
    delete, get, post, put,
    web::{Data, Path, Query, ServiceConfig},
    HttpResponse, Result as ActixResult,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{error, info, warn};

/// 监控控制器
///
/// 提供系统监控和数据收集的HTTP API接口
#[derive(Clone)]
pub struct MonitoringController {
    monitoring_service: Arc<MonitoringService>,
}

impl MonitoringController {
    /// 创建新的监控控制器
    ///
    /// # 参数
    /// * `monitoring_service` - 监控服务
    pub fn new(monitoring_service: Arc<MonitoringService>) -> Self {
        Self { monitoring_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/monitoring")
                .route("/start", actix_web::web::post().to(Self::start_monitoring))
                .route("/stop", actix_web::web::post().to(Self::stop_monitoring))
                .route(
                    "/status",
                    actix_web::web::get().to(Self::get_monitoring_status),
                )
                .route(
                    "/config",
                    actix_web::web::get().to(Self::get_monitoring_config),
                )
                .route(
                    "/config",
                    actix_web::web::put().to(Self::update_monitoring_config),
                )
                .route(
                    "/data/realtime",
                    actix_web::web::get().to(Self::get_realtime_data),
                )
                .route(
                    "/data/history",
                    actix_web::web::get().to(Self::get_historical_data),
                )
                .route(
                    "/metrics",
                    actix_web::web::get().to(Self::get_monitoring_metrics),
                )
                .route("/health", actix_web::web::get().to(Self::get_system_health))
                .route(
                    "/targets",
                    actix_web::web::get().to(Self::get_monitoring_targets),
                )
                .route(
                    "/targets",
                    actix_web::web::post().to(Self::add_monitoring_target),
                )
                .route(
                    "/targets/{target_id}",
                    actix_web::web::delete().to(Self::remove_monitoring_target),
                )
                .route(
                    "/collect",
                    actix_web::web::post().to(Self::trigger_data_collection),
                ),
        );
    }

    /// 启动监控服务
    ///
    /// POST /api/v1/monitoring/start
    async fn start_monitoring(
        service: Data<Arc<MonitoringService>>,
        request: actix_web::web::Json<StartMonitoringRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("启动监控服务");

        if let Some(config) = request.config.clone() {
            if let Err(e) = service.update_monitoring_config(config).await {
                return Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e)));
            }
        }

        match service.start_monitoring().await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 停止监控服务
    ///
    /// POST /api/v1/monitoring/stop
    async fn stop_monitoring(service: Data<Arc<MonitoringService>>) -> ActixResult<HttpResponse> {
        info!("停止监控服务");

        match service.stop_monitoring().await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取监控状态
    ///
    /// GET /api/v1/monitoring/status
    async fn get_monitoring_status(
        service: Data<Arc<MonitoringService>>,
    ) -> ActixResult<HttpResponse> {
        info!("获取监控状态");

        match service.get_monitoring_status().await {
            Ok(status) => Ok(HttpResponse::Ok().json(ApiResponse::success(status))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取监控配置
    ///
    /// GET /api/v1/monitoring/config
    async fn get_monitoring_config(
        service: Data<Arc<MonitoringService>>,
    ) -> ActixResult<HttpResponse> {
        info!("获取监控配置");

        match service.get_monitoring_config().await {
            Ok(config) => Ok(HttpResponse::Ok().json(ApiResponse::success(config))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 更新监控配置
    ///
    /// PUT /api/v1/monitoring/config
    async fn update_monitoring_config(
        service: Data<Arc<MonitoringService>>,
        config: actix_web::web::Json<MonitoringConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新监控配置");

        match service.update_monitoring_config(config.into_inner()).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取实时监控数据
    ///
    /// GET /api/v1/monitoring/data/realtime
    async fn get_realtime_data(
        service: Data<Arc<MonitoringService>>,
        params: Query<RealtimeDataParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取实时监控数据");

        match service
            .get_realtime_data(
                params.include_temperature.unwrap_or(true),
                params.include_fan.unwrap_or(true),
                params.include_sensor.unwrap_or(true),
                params.include_health.unwrap_or(true),
                params.include_alerts.unwrap_or(true),
            )
            .await
        {
            Ok(data) => Ok(HttpResponse::Ok().json(ApiResponse::success(data))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取历史监控数据
    ///
    /// GET /api/v1/monitoring/data/history
    async fn get_historical_data(
        service: Data<Arc<MonitoringService>>,
        params: Query<HistoricalDataParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取历史监控数据");

        match service
            .get_historical_data(
                params.start_time,
                params.end_time,
                params.data_types.as_deref(),
                params.limit,
            )
            .await
        {
            Ok(data) => Ok(HttpResponse::Ok().json(ApiResponse::success(data))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取监控指标
    ///
    /// GET /api/v1/monitoring/metrics
    async fn get_monitoring_metrics(
        service: Data<Arc<MonitoringService>>,
        params: Query<MetricsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取监控指标");

        match service
            .get_monitoring_metrics(params.time_window_hours.unwrap_or(24))
            .await
        {
            Ok(metrics) => Ok(HttpResponse::Ok().json(ApiResponse::success(metrics))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取系统健康状态
    ///
    /// GET /api/v1/monitoring/health
    async fn get_system_health(service: Data<Arc<MonitoringService>>) -> ActixResult<HttpResponse> {
        info!("获取系统健康状态");

        match service.get_system_health().await {
            Ok(health) => Ok(HttpResponse::Ok().json(ApiResponse::success(health))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取监控目标
    ///
    /// GET /api/v1/monitoring/targets
    async fn get_monitoring_targets(
        service: Data<Arc<MonitoringService>>,
    ) -> ActixResult<HttpResponse> {
        info!("获取监控目标");

        match service.get_monitoring_targets().await {
            Ok(targets) => Ok(HttpResponse::Ok().json(ApiResponse::success(targets))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 添加监控目标
    ///
    /// POST /api/v1/monitoring/targets
    async fn add_monitoring_target(
        service: Data<Arc<MonitoringService>>,
        target: actix_web::web::Json<MonitoringTarget>,
    ) -> ActixResult<HttpResponse> {
        info!("添加监控目标: {}", target.id);

        match service.add_monitoring_target(target.into_inner()).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 移除监控目标
    ///
    /// DELETE /api/v1/monitoring/targets/:target_id
    async fn remove_monitoring_target(
        service: Data<Arc<MonitoringService>>,
        target_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("移除监控目标: {}", target_id);

        match service.remove_monitoring_target(&target_id).await {
            Ok(_) => Ok(HttpResponse::Ok().json(ApiResponse::success(()))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 触发数据收集
    ///
    /// POST /api/v1/monitoring/collect
    async fn trigger_data_collection(
        service: Data<Arc<MonitoringService>>,
        request: actix_web::web::Json<DataCollectionRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("触发数据收集");

        match service
            .trigger_data_collection(
                request.collection_types.as_deref(),
                request.force_collection.unwrap_or(false),
            )
            .await
        {
            Ok(result) => Ok(HttpResponse::Ok().json(ApiResponse::success(result))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取监控告警
    ///
    /// GET /api/v1/monitoring/alerts
    async fn get_monitoring_alerts(
        service: Data<Arc<MonitoringService>>,
        params: Query<MonitoringAlertsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取监控告警");

        match service
            .get_monitoring_alerts(
                params.severity.as_deref(),
                params.status.as_deref(),
                params.limit,
            )
            .await
        {
            Ok(alerts) => Ok(HttpResponse::Ok().json(ApiResponse::success(alerts))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 获取监控性能
    ///
    /// GET /api/v1/monitoring/performance
    async fn get_monitoring_performance(
        service: Data<Arc<MonitoringService>>,
        params: Query<PerformanceParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取监控性能");

        match service
            .get_monitoring_performance(params.time_window_hours.unwrap_or(24))
            .await
        {
            Ok(performance) => Ok(HttpResponse::Ok().json(ApiResponse::success(performance))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }

    /// 导出监控数据
    ///
    /// GET /api/v1/monitoring/export
    async fn export_monitoring_data(
        service: Data<Arc<MonitoringService>>,
        params: Query<MonitoringExportParams>,
    ) -> ActixResult<HttpResponse> {
        info!("导出监控数据，格式: {:?}", params.format);

        match service
            .export_monitoring_data(
                params.data_types.as_deref(),
                params.start_time,
                params.end_time,
                params.format,
            )
            .await
        {
            Ok(data) => Ok(HttpResponse::Ok().json(ApiResponse::success(data))),
            Err(e) => Ok(HttpResponse::InternalServerError().json(format!("Error: {}", e))),
        }
    }
}

// 请求和响应结构体

/// 启动监控请求
#[derive(Debug, Deserialize)]
pub struct StartMonitoringRequest {
    /// 监控配置
    pub config: Option<MonitoringConfig>,
}

/// 实时数据参数
#[derive(Debug, Deserialize)]
pub struct RealtimeDataParams {
    /// 包含温度数据
    pub include_temperature: Option<bool>,
    /// 包含风扇数据
    pub include_fan: Option<bool>,
    /// 包含传感器数据
    pub include_sensor: Option<bool>,
    /// 包含健康数据
    pub include_health: Option<bool>,
    /// 包含告警数据
    pub include_alerts: Option<bool>,
}

/// 历史数据参数
#[derive(Debug, Deserialize)]
pub struct HistoricalDataParams {
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 数据类型
    pub data_types: Option<Vec<String>>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 指标参数
#[derive(Debug, Deserialize)]
pub struct MetricsParams {
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
}

/// 数据收集请求
#[derive(Debug, Deserialize)]
pub struct DataCollectionRequest {
    /// 收集类型
    pub collection_types: Option<Vec<String>>,
    /// 强制收集
    pub force_collection: Option<bool>,
}

/// 监控告警参数
#[derive(Debug, Deserialize)]
pub struct MonitoringAlertsParams {
    /// 严重程度
    pub severity: Option<Vec<String>>,
    /// 状态
    pub status: Option<Vec<String>>,
    /// 返回记录数限制
    pub limit: Option<usize>,
}

/// 性能参数
#[derive(Debug, Deserialize)]
pub struct PerformanceParams {
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
}

/// 监控导出参数
#[derive(Debug, Deserialize)]
pub struct MonitoringExportParams {
    /// 数据类型
    pub data_types: Option<Vec<String>>,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 导出格式
    pub format: ExportFormat,
}

/// 监控数据缓存
///
/// 用于缓存最新的监控数据
#[derive(Debug, Clone, Default)]
pub struct MonitoringDataCache {
    /// 最新温度数据
    pub latest_temperature_data: Option<Vec<crate::models::thermal::TemperatureReading>>,
    /// 最新风扇数据
    pub latest_fan_data: Option<Vec<crate::models::fan::FanStatus>>,
    /// 最新传感器数据
    pub latest_sensor_data: Option<Vec<crate::models::SensorData>>,
    /// 最新系统健康数据
    pub latest_system_health: Option<SystemHealth>,
    /// 活跃告警
    pub active_alerts: Option<Vec<MonitoringAlert>>,
}

/// 系统健康状态
#[derive(Debug, Clone, Serialize)]
pub struct SystemHealth {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 健康状态
    pub status: SystemHealthStatus,
    /// 问题列表
    pub issues: Vec<String>,
    /// 运行时间（秒）
    pub uptime_seconds: u64,
}

/// 系统健康状态枚举
#[derive(Debug, Clone, Serialize)]
pub enum SystemHealthStatus {
    /// 健康
    Healthy,
    /// 警告
    Warning,
    /// 严重
    Critical,
}

/// 监控数据类型
#[derive(Debug, Clone)]
pub enum MonitoringDataType {
    /// 温度
    Temperature,
    /// 风扇转速
    FanSpeed,
    /// 系统健康
    SystemHealth,
    /// 全部
    All,
}

/// 监控数据点
#[derive(Debug, Clone)]
pub struct MonitoringDataPoint {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 组件ID
    pub component_id: String,
    /// 数据类型
    pub data_type: MonitoringDataType,
    /// 数值
    pub value: f64,
    /// 单位
    pub unit: String,
    /// 状态
    pub status: String,
    /// 元数据
    pub metadata: Option<serde_json::Value>,
}

/// 监控目标
#[derive(Debug, Clone)]
pub struct MonitoringTarget {
    /// 目标ID
    pub target_id: String,
    /// 目标类型
    pub target_type: String,
    /// 监控指标
    pub metrics: Vec<String>,
}

/// 导出格式
#[derive(Debug, Clone, Deserialize)]
pub enum ExportFormat {
    Json,
    Csv,
    Excel,
}

/// 监控状态
#[derive(Debug, Serialize)]
pub struct MonitoringStatus {
    /// 是否运行中
    pub is_running: bool,
    /// 启动时间
    pub started_at: Option<chrono::DateTime<chrono::Utc>>,
    /// 停止时间
    pub stopped_at: Option<chrono::DateTime<chrono::Utc>>,
    /// 上次更新时间
    pub last_update: Option<chrono::DateTime<chrono::Utc>>,
    /// 运行时长（秒）
    pub uptime_seconds: Option<u64>,
    /// 活跃监控目标数
    pub active_targets: usize,
    /// 数据收集统计
    pub collection_stats: CollectionStats,
    /// 最后错误
    pub last_error: Option<String>,
}

impl Default for MonitoringStatus {
    fn default() -> Self {
        MonitoringStatus {
            is_running: false,
            started_at: None,
            stopped_at: None,
            last_update: None,
            uptime_seconds: None,
            active_targets: 0,
            collection_stats: CollectionStats::default(),
            last_error: None,
        }
    }
}

/// 收集统计
#[derive(Debug, Serialize)]
pub struct CollectionStats {
    /// 总收集次数
    pub total_collections: u64,
    /// 成功收集次数
    pub successful_collections: u64,
    /// 失败收集次数
    pub failed_collections: u64,
    /// 最后收集时间
    pub last_collection_at: Option<chrono::DateTime<chrono::Utc>>,
    /// 平均收集时间（毫秒）
    pub avg_collection_time_ms: f64,
}

impl Default for CollectionStats {
    fn default() -> Self {
        CollectionStats {
            total_collections: 0,
            successful_collections: 0,
            failed_collections: 0,
            last_collection_at: None,
            avg_collection_time_ms: 0.0,
        }
    }
}

/// 实时监控数据
#[derive(Debug, Serialize)]
pub struct RealtimeMonitoringData {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 温度数据
    pub temperature_data: Option<Vec<crate::models::thermal::TemperatureReading>>,
    /// 风扇数据
    pub fan_data: Option<Vec<crate::models::fan::FanStatus>>,
    /// 传感器数据
    pub sensor_data: Option<Vec<crate::models::SensorData>>,
    /// 系统健康数据
    pub health_data: Option<SystemHealthData>,
    /// 告警数据
    pub alert_data: Option<Vec<MonitoringAlert>>,
}

/// 历史监控数据
#[derive(Debug, Serialize)]
pub struct HistoricalMonitoringData {
    /// 时间范围
    pub time_range: TimeRange,
    /// 数据点
    pub data_points: Vec<HistoricalDataPoint>,
    /// 总记录数
    pub total_records: usize,
    /// 数据类型
    pub data_types: Vec<String>,
}

/// 历史数据点
#[derive(Debug, Serialize)]
pub struct HistoricalDataPoint {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 数据类型
    pub data_type: String,
    /// 数据值
    pub data: serde_json::Value,
}

/// 监控指标
#[derive(Debug, Serialize)]
pub struct MonitoringMetrics {
    /// 时间窗口
    pub time_window_hours: u32,
    /// 数据收集指标
    pub collection_metrics: CollectionMetrics,
    /// 系统性能指标
    pub performance_metrics: SystemPerformanceMetrics,
    /// 告警指标
    pub alert_metrics: AlertMetrics,
}

impl Default for MonitoringMetrics {
    fn default() -> Self {
        MonitoringMetrics {
            time_window_hours: 0,
            collection_metrics: CollectionMetrics::default(),
            performance_metrics: SystemPerformanceMetrics::default(),
            alert_metrics: AlertMetrics::default(),
        }
    }
}

/// 收集指标
#[derive(Debug, Serialize)]
pub struct CollectionMetrics {
    /// 收集频率（次/小时）
    pub collection_frequency: f64,
    /// 成功率
    pub success_rate: f64,
    /// 平均响应时间（毫秒）
    pub avg_response_time_ms: f64,
    /// 数据量（字节）
    pub data_volume_bytes: u64,
}

impl Default for CollectionMetrics {
    fn default() -> Self {
        CollectionMetrics {
            collection_frequency: 0.0,
            success_rate: 0.0,
            avg_response_time_ms: 0.0,
            data_volume_bytes: 0,
        }
    }
}

/// 系统性能指标
#[derive(Debug, Serialize)]
pub struct SystemPerformanceMetrics {
    /// CPU使用率
    pub cpu_usage_percent: f64,
    /// 内存使用率
    pub memory_usage_percent: f64,
    /// 磁盘使用率
    pub disk_usage_percent: f64,
    /// 网络吞吐量（字节/秒）
    pub network_throughput_bps: u64,
}

impl Default for SystemPerformanceMetrics {
    fn default() -> Self {
        SystemPerformanceMetrics {
            cpu_usage_percent: 0.0,
            memory_usage_percent: 0.0,
            disk_usage_percent: 0.0,
            network_throughput_bps: 0,
        }
    }
}

/// 告警指标
#[derive(Debug, Serialize)]
pub struct AlertMetrics {
    /// 总告警数
    pub total_alerts: usize,
    /// 活跃告警数
    pub active_alerts: usize,
    /// 按严重程度分组的告警数
    pub alerts_by_severity: std::collections::HashMap<String, usize>,
    /// 告警频率（次/小时）
    pub alert_frequency: f64,
}

impl Default for AlertMetrics {
    fn default() -> Self {
        AlertMetrics {
            total_alerts: 0,
            active_alerts: 0,
            alerts_by_severity: Default::default(),
            alert_frequency: 0.0,
        }
    }
}

/// 系统健康报告
#[derive(Debug, Serialize)]
pub struct SystemHealthReport {
    /// 整体健康分数（0-100）
    pub overall_health_score: f64,
    /// 健康状态
    pub health_status: HealthStatus,
    /// 组件健康状态
    pub component_health: std::collections::HashMap<String, ComponentHealth>,
    /// 识别的问题
    pub identified_issues: Vec<HealthIssue>,
    /// 建议
    pub recommendations: Vec<String>,
    /// 生成时间
    pub generated_at: chrono::DateTime<chrono::Utc>,
}

/// 健康状态
#[derive(Debug, Serialize)]
pub enum HealthStatus {
    Healthy,
    Warning,
    Critical,
    Unknown,
}

/// 组件健康状态
#[derive(Debug, Serialize)]
pub struct ComponentHealth {
    /// 健康分数（0-100）
    pub health_score: f64,
    /// 状态
    pub status: HealthStatus,
    /// 最后检查时间
    pub last_checked: chrono::DateTime<chrono::Utc>,
    /// 详细信息
    pub details: String,
}

/// 健康问题
#[derive(Debug, Serialize)]
pub struct HealthIssue {
    /// 问题ID
    pub id: String,
    /// 严重程度
    pub severity: String,
    /// 组件
    pub component: String,
    /// 描述
    pub description: String,
    /// 发现时间
    pub discovered_at: chrono::DateTime<chrono::Utc>,
}

/// 系统健康数据
#[derive(Debug, Serialize)]
pub struct SystemHealthData {
    /// 健康分数
    pub health_score: f64,
    /// 状态
    pub status: HealthStatus,
    /// 最后更新时间
    pub last_updated: chrono::DateTime<chrono::Utc>,
}

/// 监控告警
#[derive(Debug, Serialize, Clone)]
pub struct MonitoringAlert {
    /// 告警ID
    pub id: String,
    /// 严重程度
    pub severity: String,
    /// 状态
    pub status: String,
    /// 消息
    pub message: String,
    /// 组件
    pub component: String,
    /// 创建时间
    pub created_at: chrono::DateTime<chrono::Utc>,
    /// 更新时间
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

/// 监控性能
#[derive(Debug, Serialize)]
pub struct MonitoringPerformance {
    /// 时间窗口
    pub time_window_hours: u32,
    /// 监控开销
    pub monitoring_overhead: MonitoringOverhead,
    /// 资源使用情况
    pub resource_usage: ResourceUsage,
    /// 性能趋势
    pub performance_trends: PerformanceTrends,
}

/// 监控开销
#[derive(Debug, Serialize)]
pub struct MonitoringOverhead {
    /// CPU开销百分比
    pub cpu_overhead_percent: f64,
    /// 内存开销（字节）
    pub memory_overhead_bytes: u64,
    /// 网络开销（字节/秒）
    pub network_overhead_bps: u64,
    /// 存储开销（字节）
    pub storage_overhead_bytes: u64,
}

/// 资源使用情况
#[derive(Debug, Serialize)]
pub struct ResourceUsage {
    /// 平均CPU使用率
    pub avg_cpu_usage: f64,
    /// 峰值CPU使用率
    pub peak_cpu_usage: f64,
    /// 平均内存使用量
    pub avg_memory_usage: u64,
    /// 峰值内存使用量
    pub peak_memory_usage: u64,
}

/// 性能趋势
#[derive(Debug, Serialize)]
pub struct PerformanceTrends {
    /// CPU使用趋势
    pub cpu_trend: TrendDirection,
    /// 内存使用趋势
    pub memory_trend: TrendDirection,
    /// 响应时间趋势
    pub response_time_trend: TrendDirection,
}

/// 趋势方向
#[derive(Debug, Serialize)]
pub enum TrendDirection {
    Increasing,
    Decreasing,
    Stable,
    Unknown,
}

/// 数据收集结果
#[derive(Debug, Serialize)]
pub struct DataCollectionResult {
    /// 收集的数据类型
    pub collected_types: Vec<String>,
    /// 收集的记录数
    pub records_collected: usize,
    /// 收集时间（毫秒）
    pub collection_time_ms: u64,
    /// 是否成功
    pub success: bool,
    /// 错误信息
    pub errors: Vec<String>,
}

/// 时间范围
#[derive(Debug, Serialize)]
pub struct TimeRange {
    /// 开始时间
    pub start: chrono::DateTime<chrono::Utc>,
    /// 结束时间
    pub end: chrono::DateTime<chrono::Utc>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::services::{
        AlertService, FanService, MonitoringService, SensorService, ThermalService,
    };
    use actix_test::TestServer;
    use actix_web::http::StatusCode;

    #[tokio::test]
    async fn test_monitoring_controller_routes() {
        let thermal_service = Arc::new(ThermalService::new().await.unwrap());
        let fan_service = Arc::new(FanService::new().await.unwrap());
        let sensor_service = Arc::new(SensorService::new().await.unwrap());
        let alert_service = Arc::new(AlertService::new().await.unwrap());
        let monitoring_service = Arc::new(
            MonitoringService::new(thermal_service, fan_service, sensor_service, alert_service)
                .await
                .unwrap(),
        );

        let controller = MonitoringController::new(monitoring_service.clone());

        let app = Router::new()
            .nest("/api/v1", controller.routes())
            .with_state(monitoring_service);

        let server = TestServer::new(app).unwrap();

        // 测试获取监控状态
        let response = server.get("/api/v1/monitoring/status").await;
        assert_eq!(response.status_code(), StatusCode::OK);

        // 测试获取系统健康状态
        let response = server.get("/api/v1/monitoring/health").await;
        assert_eq!(response.status_code(), StatusCode::OK);
    }

    #[test]
    fn test_realtime_data_params_deserialization() {
        let json = r#"{"include_temperature": true, "include_fan": false}"#;
        let params: RealtimeDataParams = serde_json::from_str(json).unwrap();

        assert_eq!(params.include_temperature, Some(true));
        assert_eq!(params.include_fan, Some(false));
    }

    #[test]
    fn test_export_format_deserialization() {
        let json = r#""Json""#;
        let format: ExportFormat = serde_json::from_str(json).unwrap();

        matches!(format, ExportFormat::Json);
    }
}
