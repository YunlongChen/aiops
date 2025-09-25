use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 温度传感器
///
/// 专门用于温度监控的传感器结构
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TemperatureSensor {
    /// 传感器唯一标识符
    pub id: String,
    /// 传感器ID（来自IPMI）
    pub sensor_id: String,
    /// 传感器名称
    pub name: String,
    /// 传感器位置描述
    pub location: String,
    /// 传感器类型
    pub sensor_type: String,
    /// 传感器单位
    pub unit: String,
    /// 最小值
    pub min_value: Option<f64>,
    /// 最大值
    pub max_value: Option<f64>,
    /// 精度
    pub accuracy: Option<f64>,
    /// 传感器状态
    pub status: String,
    /// 最后读数
    pub last_reading: Option<f64>,
    /// 最后更新时间
    pub last_update: Option<DateTime<Utc>>,
}

/// 传感器信息
///
/// 存储服务器上所有传感器的基本信息
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct SensorInfo {
    /// 传感器唯一标识符
    pub id: Uuid,
    /// 传感器ID（来自IPMI）
    pub sensor_id: String,
    /// 传感器名称
    pub name: String,
    /// 传感器类型
    pub sensor_type: SensorType,
    /// 传感器单位
    pub unit: String,
    /// 传感器位置描述
    pub location: String,
    /// 是否启用监控
    pub enabled: bool,
    /// 最小值
    pub min_value: Option<f64>,
    /// 最大值
    pub max_value: Option<f64>,
    /// 精度（小数位数）
    pub precision: i32,
    /// 服务器标识符
    pub server_id: String,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 传感器读数
///
/// 存储从传感器读取的实时数据
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct SensorReading {
    /// 读数唯一标识符
    pub id: Uuid,
    /// 传感器标识符
    pub sensor_id: String,
    /// 读数值
    pub value: f64,
    /// 读数状态
    pub status: SensorStatus,
    /// 读数时间戳
    pub timestamp: DateTime<Utc>,
    /// 原始数据（IPMI输出）
    pub raw_data: Option<String>,
}

/// 传感器类型枚举
///
/// 定义不同类型的传感器
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum SensorType {
    /// 温度传感器
    Temperature,
    /// 风扇转速传感器
    Fan,
    /// 电压传感器
    Voltage,
    /// 电流传感器
    Current,
    /// 功率传感器
    Power,
    /// 湿度传感器
    Humidity,
    /// 其他类型传感器
    Other(String),
}

/// 传感器状态枚举
///
/// 定义传感器读数的状态
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum SensorStatus {
    /// 正常状态
    Ok,
    /// 警告状态
    Warning,
    /// 危险状态
    Critical,
    /// 传感器故障
    Error,
    /// 数据不可用
    NotAvailable,
}

/// 传感器配置
///
/// 存储传感器的配置参数
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct SensorConfig {
    /// 配置唯一标识符
    pub id: Uuid,
    /// 传感器标识符
    pub sensor_id: String,
    /// 采样间隔（秒）
    pub sampling_interval: i32,
    /// 数据保留天数
    pub retention_days: i32,
    /// 是否启用告警
    pub alert_enabled: bool,
    /// 告警阈值配置
    pub alert_thresholds: AlertThresholds,
    /// 数据平滑配置
    pub smoothing_config: SmoothingConfig,
    /// 校准配置
    pub calibration: Option<SensorCalibration>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 告警阈值配置
///
/// 定义传感器的告警阈值
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AlertThresholds {
    /// 低危险阈值
    pub critical_low: Option<f64>,
    /// 低警告阈值
    pub warning_low: Option<f64>,
    /// 高警告阈值
    pub warning_high: Option<f64>,
    /// 高危险阈值
    pub critical_high: Option<f64>,
}

impl Default for AlertThresholds {
    fn default() -> Self {
        AlertThresholds {
            critical_low: None,
            warning_low: None,
            warning_high: None,
            critical_high: None,
        }
    }
}

/// 数据平滑配置
///
/// 定义传感器数据的平滑处理参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SmoothingConfig {
    /// 是否启用平滑
    pub enabled: bool,
    /// 平滑算法类型
    pub algorithm: SmoothingAlgorithm,
    /// 窗口大小（数据点数量）
    pub window_size: i32,
    /// 平滑因子（0.0-1.0）
    pub smoothing_factor: f64,
}

/// 传感器校准配置
///
/// 定义传感器的校准参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SensorCalibration {
    /// 偏移量
    pub offset: f64,
    /// 缩放因子
    pub scale_factor: f64,
    /// 参考值
    pub reference_value: f64,
    /// 校准时间
    pub calibrated_at: DateTime<Utc>,
}

/// 平滑算法枚举
///
/// 定义不同的数据平滑算法
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum SmoothingAlgorithm {
    /// 移动平均
    MovingAverage,
    /// 指数平滑
    ExponentialSmoothing,
    /// 中位数滤波
    MedianFilter,
    /// 无平滑
    None,
}

/// 传感器统计数据
///
/// 用于API响应的传感器统计信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SensorStats {
    /// 传感器标识符
    pub sensor_id: String,
    /// 传感器名称
    pub sensor_name: String,
    /// 平均值
    pub average: f64,
    /// 最小值
    pub minimum: f64,
    /// 最大值
    pub maximum: f64,
    /// 当前值
    pub current: f64,
    /// 标准差
    pub standard_deviation: f64,
    /// 统计时间范围（分钟）
    pub time_range_minutes: i32,
    /// 数据点数量
    pub data_points: i32,
    /// 最后更新时间
    pub last_updated: DateTime<Utc>,
}

/// 传感器趋势分析结果
///
/// 包含传感器数据的趋势分析信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SensorTrend {
    /// 传感器ID
    pub sensor_id: String,
    /// 传感器类型
    pub sensor_type: SensorType,
    /// 趋势斜率
    pub slope: f64,
    /// 截距
    pub intercept: f64,
    /// 相关系数的平方（R²）
    pub r_squared: f64,
    /// 变化率（每小时）
    pub change_rate: f64,
    /// 预测值列表（时间，预测值）
    pub predictions: Vec<(DateTime<Utc>, f64)>,
    /// 分析开始时间
    pub start_time: DateTime<Utc>,
    /// 分析结束时间
    pub end_time: DateTime<Utc>,
}

/// 传感器健康状态
///
/// 评估传感器的整体健康状况
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SensorHealth {
    /// 传感器标识符
    pub sensor_id: String,
    /// 健康评分（0-100）
    pub health_score: f64,
    /// 健康状态
    pub health_status: HealthStatus,
    /// 数据质量评分（0-100）
    pub data_quality_score: f64,
    /// 连续性评分（0-100）
    pub continuity_score: f64,
    /// 准确性评分（0-100）
    pub accuracy_score: f64,
    /// 最后检查时间
    pub last_check: DateTime<Utc>,
    /// 健康报告
    pub health_report: Vec<HealthIssue>,
}

/// 健康状态枚举
///
/// 定义传感器的健康状态级别
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum HealthStatus {
    /// 健康
    Healthy,
    /// 良好
    Good,
    /// 一般
    Fair,
    /// 差
    Poor,
    /// 故障
    Failed,
}

/// 健康问题
///
/// 描述传感器存在的具体健康问题
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct HealthIssue {
    /// 问题类型
    pub issue_type: IssueType,
    /// 问题描述
    pub description: String,
    /// 严重程度
    pub severity: IssueSeverity,
    /// 发现时间
    pub detected_at: DateTime<Utc>,
}

/// 问题类型枚举
///
/// 定义不同类型的传感器问题
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum IssueType {
    /// 数据缺失
    DataMissing,
    /// 数据异常
    DataAnomalous,
    /// 读取错误
    ReadError,
    /// 连接问题
    ConnectionIssue,
    /// 校准问题
    CalibrationIssue,
}

/// 问题严重程度枚举
///
/// 定义问题的严重程度级别
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum IssueSeverity {
    /// 信息
    Info,
    /// 警告
    Warning,
    /// 错误
    Error,
    /// 严重
    Critical,
}

impl SensorInfo {
    /// 创建新的传感器信息
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `name` - 传感器名称
    /// * `sensor_type` - 传感器类型
    /// * `unit` - 传感器单位
    /// * `location` - 传感器位置
    /// * `server_id` - 服务器标识符
    pub fn new(
        sensor_id: String,
        name: String,
        sensor_type: SensorType,
        unit: String,
        location: String,
        server_id: String,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            sensor_id,
            name,
            sensor_type,
            unit,
            location,
            enabled: true,
            min_value: None,
            max_value: None,
            precision: 2,
            server_id,
            created_at: now,
            updated_at: now,
        }
    }
}

impl SensorReading {
    /// 创建新的传感器读数
    ///
    /// # 参数
    /// * `sensor_id` - 传感器标识符
    /// * `value` - 读数值
    /// * `thresholds` - 告警阈值配置
    /// * `raw_data` - 原始数据
    pub fn new(
        sensor_id: String,
        value: f64,
        thresholds: &AlertThresholds,
        raw_data: Option<String>,
    ) -> Self {
        let status = Self::determine_status(value, thresholds);

        Self {
            id: Uuid::new_v4(),
            sensor_id,
            value,
            status,
            timestamp: Utc::now(),
            raw_data,
        }
    }

    /// 根据读数值和阈值确定传感器状态
    ///
    /// # 参数
    /// * `value` - 读数值
    /// * `thresholds` - 告警阈值配置
    fn determine_status(value: f64, thresholds: &AlertThresholds) -> SensorStatus {
        if let Some(critical_high) = thresholds.critical_high {
            if value >= critical_high {
                return SensorStatus::Critical;
            }
        }

        if let Some(critical_low) = thresholds.critical_low {
            if value <= critical_low {
                return SensorStatus::Critical;
            }
        }

        if let Some(warning_high) = thresholds.warning_high {
            if value >= warning_high {
                return SensorStatus::Warning;
            }
        }

        if let Some(warning_low) = thresholds.warning_low {
            if value <= warning_low {
                return SensorStatus::Warning;
            }
        }

        SensorStatus::Ok
    }
}
