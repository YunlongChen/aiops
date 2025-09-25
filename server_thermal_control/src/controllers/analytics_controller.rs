use crate::models::{
    error::{AppError, AppResult},
    analytics::*,
    api::{ApiResponse, PaginationParams, TimeRangeParams},
};
use crate::services::{AnalyticsService, analytics_service::OptimizationRecommendation};
use actix_web::{
    web::{Data, Path, Query, ServiceConfig},
    HttpResponse, Result as ActixResult,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{info, warn, error};

/// 分析控制器
/// 
/// 提供数据分析和趋势预测的HTTP API接口
#[derive(Clone)]
pub struct AnalyticsController {
    analytics_service: Arc<AnalyticsService>,
}

impl AnalyticsController {
    /// 创建新的分析控制器
    /// 
    /// # 参数
    /// * `analytics_service` - 分析服务
    pub fn new(analytics_service: Arc<AnalyticsService>) -> Self {
        Self { analytics_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/analytics")
                .route("/temperature/trends", actix_web::web::get().to(Self::analyze_temperature_trends))
                .route("/fan/efficiency", actix_web::web::get().to(Self::analyze_fan_efficiency))
                .route("/anomalies", actix_web::web::get().to(Self::detect_anomalies))
                .route("/performance", actix_web::web::get().to(Self::get_performance_metrics))
                .route("/aggregation", actix_web::web::get().to(Self::aggregate_data))
                .route("/recommendations", actix_web::web::get().to(Self::get_optimization_recommendations))
                .route("/predictions", actix_web::web::get().to(Self::get_predictions))
                .route("/reports", actix_web::web::get().to(Self::generate_reports))
                .route("/reports/{report_id}", actix_web::web::get().to(Self::get_report))
                .route("/reports/{report_id}", actix_web::web::delete().to(Self::delete_report))
                .route("/cache/clear", actix_web::web::post().to(Self::clear_cache))
                .route("/cache/status", actix_web::web::get().to(Self::get_cache_status))
                .route("/export", actix_web::web::get().to(Self::export_analytics_data))
        );
    }

    /// 分析温度趋势
    /// 
    /// GET /api/v1/analytics/temperature/trends
    async fn analyze_temperature_trends(
        service: Data<AnalyticsService>,
        Query(params): Query<TemperatureTrendParams>,
    ) -> ActixResult<HttpResponse> {
        info!("分析温度趋势");

        let analysis = service.analyze_temperature_trends(
            params.sensor_id.as_deref(),
            params.time_window_hours.unwrap_or(24),
            params.prediction_hours.unwrap_or(6),
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(analysis)))
    }

    /// 分析风扇效率
    /// 
    /// GET /api/v1/analytics/fan/efficiency
    async fn analyze_fan_efficiency(
        service: Data<AnalyticsService>,
        Query(params): Query<FanEfficiencyParams>,
    ) -> ActixResult<HttpResponse> {
        info!("分析风扇效率");

        let analysis = service.analyze_fan_efficiency(
            params.fan_id.as_deref(),
            params.time_window_hours.unwrap_or(24),
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(analysis)))
    }

    /// 检测异常
    /// 
    /// GET /api/v1/analytics/anomalies
    async fn detect_anomalies(
        service: Data<AnalyticsService>,
        Query(params): Query<AnomalyDetectionParams>,
    ) -> ActixResult<HttpResponse> {
        info!("检测系统异常");

        let result = service.detect_anomalies(
            params.time_window_hours.unwrap_or(24),
            params.sensitivity.unwrap_or(0.8),
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取性能指标
    /// 
    /// GET /api/v1/analytics/performance
    async fn get_performance_metrics(
        service: Data<AnalyticsService>,
        Query(params): Query<PerformanceMetricsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取性能指标");

        let metrics = service.get_performance_metrics(
            params.time_window_hours.unwrap_or(24),
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(metrics)))
    }

    /// 聚合数据
    /// 
    /// GET /api/v1/analytics/aggregation
    async fn aggregate_data(
        service: Data<AnalyticsService>,
        Query(params): Query<DataAggregationParams>,
    ) -> ActixResult<HttpResponse> {
        info!("聚合数据，类型: {:?}", params.aggregation_type);

        let data = service.aggregate_data(
            params.aggregation_type,
            params.start_time,
            params.end_time,
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(data)))
    }

    /// 获取优化建议
    /// 
    /// GET /api/v1/analytics/recommendations
    async fn get_optimization_recommendations(
        service: Data<AnalyticsService>,
        Query(params): Query<RecommendationParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取优化建议");

        let recommendations = service.get_optimization_recommendations(
            params.include_system_level.unwrap_or(true),
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(recommendations)))
    }

    /// 获取预测数据
    /// 
    /// GET /api/v1/analytics/predictions
    async fn get_predictions(
        service: Data<AnalyticsService>,
        Query(params): Query<PredictionParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取预测数据");

        let predictions = service.get_predictions(
            params.prediction_type,
            params.time_horizon_hours.unwrap_or(24),
            params.target_id.as_deref(),
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(predictions)))
    }

    /// 生成分析报告
    /// 
    /// GET /api/v1/analytics/reports
    async fn generate_reports(
        service: Data<AnalyticsService>,
        Query(params): Query<ReportGenerationParams>,
    ) -> ActixResult<HttpResponse> {
        info!("生成分析报告，类型: {:?}", params.report_type);

        let report = service.generate_report(
            params.report_type,
            params.start_time,
            params.end_time,
            params.include_recommendations.unwrap_or(true),
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(report)))
    }

    /// 获取指定报告
    /// 
    /// GET /api/v1/analytics/reports/:report_id
    async fn get_report(
        service: Data<AnalyticsService>,
        report_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("获取分析报告: {}", report_id);

        let report = service.get_report(&report_id).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(report)))
    }

    /// 删除报告
    /// 
    /// DELETE /api/v1/analytics/reports/:report_id
    async fn delete_report(
        service: Data<AnalyticsService>,
        report_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("删除分析报告: {}", report_id);

        service.delete_report(&report_id).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 清理缓存
    /// 
    /// POST /api/v1/analytics/cache/clear
    async fn clear_cache(
        service: Data<AnalyticsService>,
        Query(params): Query<CacheClearParams>,
    ) -> ActixResult<HttpResponse> {
        info!("清理分析缓存");

        let result = service.clear_cache(
            params.cache_type.as_deref(),
            params.older_than_hours,
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取缓存状态
    /// 
    /// GET /api/v1/analytics/cache/status
    async fn get_cache_status(
        service: Data<AnalyticsService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取缓存状态");

        let status = service.get_cache_status().await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(status)))
    }

    /// 导出分析数据
    /// 
    /// GET /api/v1/analytics/export
    async fn export_analytics_data(
        service: Data<AnalyticsService>,
        Query(params): Query<AnalyticsExportParams>,
    ) -> ActixResult<HttpResponse> {
        info!("导出分析数据，格式: {:?}", params.format);

        let data = service.export_analytics_data(
            params.data_type,
            params.start_time,
            params.end_time,
            params.format,
        ).await.map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(data)))
    }
}

// 请求和响应结构体

/// 温度趋势分析参数
#[derive(Debug, Deserialize)]
pub struct TemperatureTrendParams {
    /// 传感器ID
    pub sensor_id: Option<String>,
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
    /// 预测时长（小时）
    pub prediction_hours: Option<u32>,
}

/// 风扇效率分析参数
#[derive(Debug, Deserialize)]
pub struct FanEfficiencyParams {
    /// 风扇ID
    pub fan_id: Option<String>,
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
}

/// 异常检测参数
#[derive(Debug, Deserialize)]
pub struct AnomalyDetectionParams {
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
    /// 敏感度（0.0-1.0）
    pub sensitivity: Option<f64>,
}

/// 性能指标参数
#[derive(Debug, Deserialize)]
pub struct PerformanceMetricsParams {
    /// 时间窗口（小时）
    pub time_window_hours: Option<u32>,
}

/// 数据聚合参数
#[derive(Debug, Deserialize)]
pub struct DataAggregationParams {
    /// 聚合类型
    pub aggregation_type: AggregationType,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
}

/// 建议参数
#[derive(Debug, Deserialize)]
pub struct RecommendationParams {
    /// 是否包含系统级建议
    pub include_system_level: Option<bool>,
}

/// 预测参数
#[derive(Debug, Deserialize)]
pub struct PredictionParams {
    /// 预测类型
    pub prediction_type: PredictionType,
    /// 时间范围（小时）
    pub time_horizon_hours: Option<u32>,
    /// 目标ID
    pub target_id: Option<String>,
}

/// 报告生成参数
#[derive(Debug, Deserialize)]
pub struct ReportGenerationParams {
    /// 报告类型
    pub report_type: ReportType,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 是否包含建议
    pub include_recommendations: Option<bool>,
}

/// 缓存清理参数
#[derive(Debug, Deserialize)]
pub struct CacheClearParams {
    /// 缓存类型
    pub cache_type: Option<String>,
    /// 清理多少小时前的缓存
    pub older_than_hours: Option<u32>,
}

/// 分析数据导出参数
#[derive(Debug, Deserialize)]
pub struct AnalyticsExportParams {
    /// 数据类型
    pub data_type: AnalyticsDataType,
    /// 开始时间
    pub start_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 结束时间
    pub end_time: Option<chrono::DateTime<chrono::Utc>>,
    /// 导出格式
    pub format: ExportFormat,
}

/// 聚合类型
#[derive(Debug, Clone, Deserialize)]
pub enum AggregationType {
    Hourly,
    Daily,
    Weekly,
}

/// 预测类型
#[derive(Debug, Clone, Deserialize)]
pub enum PredictionType {
    Temperature,
    FanSpeed,
    SystemLoad,
}

/// 报告类型
#[derive(Debug, Clone, Deserialize)]
pub enum ReportType {
    Daily,
    Weekly,
    Monthly,
    Custom,
}

/// 分析数据类型
#[derive(Debug, Clone, Deserialize)]
pub enum AnalyticsDataType {
    Trends,
    Anomalies,
    Performance,
    Recommendations,
}

/// 导出格式
#[derive(Debug, Clone, Deserialize)]
pub enum ExportFormat {
    Json,
    Csv,
    Pdf,
}

/// 缓存清理结果
#[derive(Debug, Serialize)]
pub struct CacheClearResult {
    /// 清理的条目数
    pub cleared_entries: usize,
    /// 释放的内存大小（字节）
    pub freed_memory_bytes: usize,
    /// 清理的缓存类型
    pub cache_types: Vec<String>,
}

/// 缓存状态
#[derive(Debug, Serialize)]
pub struct CacheStatus {
    /// 总缓存条目数
    pub total_entries: usize,
    /// 缓存大小（字节）
    pub cache_size_bytes: usize,
    /// 命中率
    pub hit_rate: f64,
    /// 各类型缓存状态
    pub cache_types: std::collections::HashMap<String, CacheTypeStatus>,
}

/// 缓存类型状态
#[derive(Debug, Serialize)]
pub struct CacheTypeStatus {
    /// 条目数
    pub entries: usize,
    /// 大小（字节）
    pub size_bytes: usize,
    /// 最后更新时间
    pub last_updated: chrono::DateTime<chrono::Utc>,
}

/// 预测结果
#[derive(Debug, Serialize)]
pub struct PredictionResult {
    /// 预测类型
    pub prediction_type: PredictionType,
    /// 目标ID
    pub target_id: Option<String>,
    /// 预测数据点
    pub predictions: Vec<PredictionPoint>,
    /// 置信度
    pub confidence: f64,
    /// 预测模型信息
    pub model_info: PredictionModelInfo,
}

/// 预测数据点
#[derive(Debug, Serialize)]
pub struct PredictionPoint {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 预测值
    pub value: f64,
    /// 置信区间下限
    pub confidence_lower: f64,
    /// 置信区间上限
    pub confidence_upper: f64,
}

/// 预测模型信息
#[derive(Debug, Serialize)]
pub struct PredictionModelInfo {
    /// 模型类型
    pub model_type: String,
    /// 训练数据点数
    pub training_points: usize,
    /// 模型准确度
    pub accuracy: f64,
    /// 最后训练时间
    pub last_trained: chrono::DateTime<chrono::Utc>,
}

/// 聚合数据
#[derive(Debug, Serialize)]
pub struct AggregatedData {
    /// 聚合类型
    pub aggregation_type: AggregationType,
    /// 时间范围
    pub time_range: TimeRange,
    /// 温度数据
    pub temperature_data: Vec<AggregatedTemperatureData>,
    /// 风扇数据
    pub fan_data: Vec<AggregatedFanData>,
}

/// 聚合温度数据
#[derive(Debug, Serialize)]
pub struct AggregatedTemperatureData {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 平均温度
    pub avg_temperature: f64,
    /// 最高温度
    pub max_temperature: f64,
    /// 最低温度
    pub min_temperature: f64,
    /// 传感器数量
    pub sensor_count: usize,
}

/// 聚合风扇数据
#[derive(Debug, Serialize)]
pub struct AggregatedFanData {
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
    /// 平均转速
    pub avg_speed: f64,
    /// 最高转速
    pub max_speed: f64,
    /// 最低转速
    pub min_speed: f64,
    /// 风扇数量
    pub fan_count: usize,
}

/// 时间范围
#[derive(Debug, Serialize)]
pub struct TimeRange {
    /// 开始时间
    pub start: chrono::DateTime<chrono::Utc>,
    /// 结束时间
    pub end: chrono::DateTime<chrono::Utc>,
}

/// 分析报告
#[derive(Debug, Serialize)]
pub struct AnalyticsReport {
    /// 报告ID
    pub id: String,
    /// 报告类型
    pub report_type: ReportType,
    /// 生成时间
    pub generated_at: chrono::DateTime<chrono::Utc>,
    /// 时间范围
    pub time_range: TimeRange,
    /// 执行摘要
    pub executive_summary: String,
    /// 温度分析
    pub temperature_analysis: Option<TemperatureTrendAnalysis>,
    /// 风扇分析
    pub fan_analysis: Option<FanEfficiencyAnalysis>,
    /// 异常检测结果
    pub anomaly_detection: Option<AnomalyDetectionResult>,
    /// 性能指标
    pub performance_metrics: Option<PerformanceMetrics>,
    /// 优化建议
    pub recommendations: Option<Vec<OptimizationRecommendation>>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::services::{AnalyticsService, ThermalService, FanService, SensorService};
    use actix_web::{test, App};

    #[actix_web::test]
    async fn test_analytics_controller_routes() {
        let thermal_service = Arc::new(ThermalService::new().await.unwrap());
        let fan_service = Arc::new(FanService::new().await.unwrap());
        let sensor_service = Arc::new(SensorService::new().await.unwrap());
        let analytics_service = Arc::new(
            AnalyticsService::new(thermal_service, fan_service, sensor_service)
                .await.unwrap()
        );
        
        let app = test::init_service(
            App::new()
                .app_data(Data::new(analytics_service.clone()))
                .configure(AnalyticsController::configure)
        ).await;
        
        // 测试获取性能指标
        let req = test::TestRequest::get()
            .uri("/analytics/performance")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
        
        // 测试获取缓存状态
        let req = test::TestRequest::get()
            .uri("/analytics/cache/status")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
    }

    #[test]
    fn test_temperature_trend_params_deserialization() {
        let json = r#"{"sensor_id": "temp1", "time_window_hours": 24, "prediction_hours": 6}"#;
        let params: TemperatureTrendParams = serde_json::from_str(json).unwrap();
        
        assert_eq!(params.sensor_id, Some("temp1".to_string()));
        assert_eq!(params.time_window_hours, Some(24));
        assert_eq!(params.prediction_hours, Some(6));
    }

    #[test]
    fn test_aggregation_type_deserialization() {
        let json = r#""Hourly""#;
        let agg_type: AggregationType = serde_json::from_str(json).unwrap();
        
        matches!(agg_type, AggregationType::Hourly);
    }
}