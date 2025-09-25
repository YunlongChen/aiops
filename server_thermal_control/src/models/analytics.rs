use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 数据分析结果
/// 
/// 存储温度和风扇控制的分析结果
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct AnalyticsResult {
    /// 分析结果唯一标识符
    pub id: Uuid,
    /// 服务器标识符
    pub server_id: String,
    /// 分析类型
    pub analysis_type: AnalysisType,
    /// 分析时间范围开始
    pub time_range_start: DateTime<Utc>,
    /// 分析时间范围结束
    pub time_range_end: DateTime<Utc>,
    /// 分析结果数据
    pub result_data: serde_json::Value,
    /// 分析摘要
    pub summary: String,
    /// 建议操作
    pub recommendations: Vec<String>,
    /// 置信度评分（0-100）
    pub confidence_score: f32,
    /// 创建时间
    pub created_at: DateTime<Utc>,
}

/// 分析类型枚举
/// 
/// 定义不同类型的数据分析
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AnalysisType {
    /// 温度趋势分析
    TemperatureTrend,
    /// 风扇效率分析
    FanEfficiency,
    /// 能耗分析
    PowerConsumption,
    /// 性能优化分析
    PerformanceOptimization,
    /// 异常检测分析
    AnomalyDetection,
    /// 预测性维护分析
    PredictiveMaintenance,
}

/// 温度趋势分析结果
/// 
/// 温度数据的趋势分析结果
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TemperatureTrendAnalysis {
    /// 平均温度
    pub average_temperature: f32,
    /// 最高温度
    pub max_temperature: f32,
    /// 最低温度
    pub min_temperature: f32,
    /// 温度标准差
    pub temperature_std_dev: f32,
    /// 温度变化趋势
    pub trend_direction: TrendDirection,
    /// 趋势强度（-1到1）
    pub trend_strength: f32,
    /// 温度峰值次数
    pub peak_count: u32,
    /// 温度异常次数
    pub anomaly_count: u32,
    /// 预测未来温度
    pub predicted_temperatures: Vec<TemperaturePrediction>,
}

/// 趋势方向枚举
/// 
/// 定义数据的趋势方向
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum TrendDirection {
    /// 上升趋势
    Increasing,
    /// 下降趋势
    Decreasing,
    /// 稳定趋势
    Stable,
    /// 波动趋势
    Fluctuating,
}

/// 温度预测结果
/// 
/// 基于历史数据的温度预测
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TemperaturePrediction {
    /// 预测时间
    pub timestamp: DateTime<Utc>,
    /// 预测温度值
    pub predicted_value: f32,
    /// 预测置信区间下限
    pub confidence_lower: f32,
    /// 预测置信区间上限
    pub confidence_upper: f32,
    /// 预测准确度
    pub accuracy: f32,
}

/// 风扇效率分析结果
/// 
/// 风扇运行效率的分析结果
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FanEfficiencyAnalysis {
    /// 平均风扇转速
    pub average_fan_speed: f32,
    /// 风扇利用率
    pub fan_utilization: f32,
    /// 温度控制效果评分
    pub temperature_control_score: f32,
    /// 能耗效率评分
    pub energy_efficiency_score: f32,
    /// 噪音水平评估
    pub noise_level_assessment: NoiseLevel,
    /// 最优转速建议
    pub optimal_speed_recommendations: Vec<OptimalSpeedPoint>,
    /// 风扇性能退化指标
    pub performance_degradation: f32,
}

/// 噪音水平枚举
/// 
/// 定义风扇噪音的等级
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum NoiseLevel {
    /// 静音
    Silent,
    /// 低噪音
    Low,
    /// 中等噪音
    Medium,
    /// 高噪音
    High,
    /// 极高噪音
    VeryHigh,
}

/// 最优转速点
/// 
/// 在特定温度下的最优风扇转速建议
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct OptimalSpeedPoint {
    /// 目标温度
    pub target_temperature: f32,
    /// 建议转速百分比
    pub recommended_speed_percent: f32,
    /// 预期温度控制效果
    pub expected_temperature_control: f32,
    /// 预期能耗
    pub expected_power_consumption: f32,
    /// 预期噪音水平
    pub expected_noise_level: NoiseLevel,
}

/// 异常检测结果
/// 
/// 系统异常检测的分析结果
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AnomalyDetectionResult {
    /// 检测到的异常列表
    pub anomalies: Vec<DetectedAnomaly>,
    /// 异常检测算法
    pub detection_algorithm: String,
    /// 检测敏感度
    pub sensitivity: f32,
    /// 误报率估计
    pub false_positive_rate: f32,
    /// 系统健康评分
    pub system_health_score: f32,
}

/// 检测到的异常
/// 
/// 单个异常事件的详细信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct DetectedAnomaly {
    /// 异常唯一标识符
    pub id: Uuid,
    /// 异常类型
    pub anomaly_type: AnomalyType,
    /// 异常发生时间
    pub timestamp: DateTime<Utc>,
    /// 异常严重程度
    pub severity: AnomalySeverity,
    /// 异常描述
    pub description: String,
    /// 相关指标值
    pub metric_values: serde_json::Value,
    /// 异常评分
    pub anomaly_score: f32,
    /// 是否已处理
    pub is_resolved: bool,
    /// 处理建议
    pub resolution_suggestions: Vec<String>,
}

/// 异常类型枚举
/// 
/// 定义不同类型的系统异常
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AnomalyType {
    /// 温度异常
    TemperatureAnomaly,
    /// 风扇异常
    FanAnomaly,
    /// 传感器异常
    SensorAnomaly,
    /// 性能异常
    PerformanceAnomaly,
    /// 通信异常
    CommunicationAnomaly,
}

/// 异常严重程度枚举
/// 
/// 定义异常的严重程度级别
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AnomalySeverity {
    /// 低
    Low,
    /// 中等
    Medium,
    /// 高
    High,
    /// 严重
    Critical,
}

/// 性能指标
/// 
/// 系统性能相关的指标数据
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct PerformanceMetrics {
    /// 指标唯一标识符
    pub id: Uuid,
    /// 服务器标识符
    pub server_id: String,
    /// 指标类型
    pub metric_type: MetricType,
    /// 指标值
    pub value: f64,
    /// 指标单位
    pub unit: String,
    /// 测量时间
    pub timestamp: DateTime<Utc>,
    /// 指标标签
    pub labels: serde_json::Value,
    /// 创建时间
    pub created_at: DateTime<Utc>,
}

/// 指标类型枚举
/// 
/// 定义不同类型的性能指标
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum MetricType {
    /// CPU温度
    CpuTemperature,
    /// 内存温度
    MemoryTemperature,
    /// 硬盘温度
    DiskTemperature,
    /// 风扇转速
    FanSpeed,
    /// 功耗
    PowerConsumption,
    /// 系统负载
    SystemLoad,
    /// 网络延迟
    NetworkLatency,
    /// 响应时间
    ResponseTime,
}

/// 数据聚合结果
/// 
/// 时间序列数据的聚合统计结果
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct DataAggregation {
    /// 聚合时间窗口开始
    pub window_start: DateTime<Utc>,
    /// 聚合时间窗口结束
    pub window_end: DateTime<Utc>,
    /// 聚合类型
    pub aggregation_type: AggregationType,
    /// 数据点数量
    pub data_points: u32,
    /// 聚合结果
    pub aggregated_values: Vec<AggregatedValue>,
}

/// 聚合类型枚举
/// 
/// 定义不同的数据聚合方式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AggregationType {
    /// 平均值
    Average,
    /// 最大值
    Maximum,
    /// 最小值
    Minimum,
    /// 总和
    Sum,
    /// 计数
    Count,
    /// 百分位数
    Percentile,
}

/// 聚合值
/// 
/// 单个聚合计算的结果
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AggregatedValue {
    /// 指标名称
    pub metric_name: String,
    /// 聚合值
    pub value: f64,
    /// 值的单位
    pub unit: String,
    /// 聚合时间戳
    pub timestamp: DateTime<Utc>,
}

impl AnalyticsResult {
    /// 创建新的分析结果
    /// 
    /// # 参数
    /// * `server_id` - 服务器标识符
    /// * `analysis_type` - 分析类型
    /// * `time_range_start` - 分析时间范围开始
    /// * `time_range_end` - 分析时间范围结束
    /// * `result_data` - 分析结果数据
    /// * `summary` - 分析摘要
    /// * `recommendations` - 建议操作
    /// * `confidence_score` - 置信度评分
    pub fn new(
        server_id: String,
        analysis_type: AnalysisType,
        time_range_start: DateTime<Utc>,
        time_range_end: DateTime<Utc>,
        result_data: serde_json::Value,
        summary: String,
        recommendations: Vec<String>,
        confidence_score: f32,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            server_id,
            analysis_type,
            time_range_start,
            time_range_end,
            result_data,
            summary,
            recommendations,
            confidence_score,
            created_at: Utc::now(),
        }
    }
}

impl DetectedAnomaly {
    /// 创建新的异常检测结果
    /// 
    /// # 参数
    /// * `anomaly_type` - 异常类型
    /// * `timestamp` - 异常发生时间
    /// * `severity` - 异常严重程度
    /// * `description` - 异常描述
    /// * `metric_values` - 相关指标值
    /// * `anomaly_score` - 异常评分
    /// * `resolution_suggestions` - 处理建议
    pub fn new(
        anomaly_type: AnomalyType,
        timestamp: DateTime<Utc>,
        severity: AnomalySeverity,
        description: String,
        metric_values: serde_json::Value,
        anomaly_score: f32,
        resolution_suggestions: Vec<String>,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            anomaly_type,
            timestamp,
            severity,
            description,
            metric_values,
            anomaly_score,
            is_resolved: false,
            resolution_suggestions,
        }
    }
}

impl PerformanceMetrics {
    /// 创建新的性能指标记录
    /// 
    /// # 参数
    /// * `server_id` - 服务器标识符
    /// * `metric_type` - 指标类型
    /// * `value` - 指标值
    /// * `unit` - 指标单位
    /// * `timestamp` - 测量时间
    /// * `labels` - 指标标签
    pub fn new(
        server_id: String,
        metric_type: MetricType,
        value: f64,
        unit: String,
        timestamp: DateTime<Utc>,
        labels: serde_json::Value,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            server_id,
            metric_type,
            value,
            unit,
            timestamp,
            labels,
            created_at: Utc::now(),
        }
    }
}