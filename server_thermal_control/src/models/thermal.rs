use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 温度数据记录
///
/// 存储从服务器传感器读取的温度数据
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct TemperatureReading {
    /// 记录唯一标识符
    pub id: Uuid,
    /// 传感器标识符
    pub sensor_id: String,
    /// 传感器名称
    pub sensor_name: String,
    /// 温度值（摄氏度）
    pub temperature: f64,
    /// 温度状态（正常/警告/危险）
    pub status: TemperatureStatus,
    /// 记录时间戳
    pub timestamp: DateTime<Utc>,
    /// 服务器标识符
    pub server_id: String,
}

/// 温度状态枚举
///
/// 定义温度的不同状态级别
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum TemperatureStatus {
    /// 正常温度范围
    Normal,
    /// 警告温度范围
    Warning,
    /// 危险温度范围
    Critical,
    /// 传感器故障
    Error,
}

/// 温度阈值配置
///
/// 定义不同组件的温度阈值
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct TemperatureThreshold {
    /// 配置唯一标识符
    pub id: Uuid,
    /// 组件类型（CPU、内存、硬盘等）
    pub component_type: String,
    /// 传感器标识符
    pub sensor_id: String,
    /// 正常温度上限
    pub normal_max: f64,
    /// 警告温度上限
    pub warning_max: f64,
    /// 危险温度上限
    pub critical_max: f64,
    /// 配置创建时间
    pub created_at: DateTime<Utc>,
    /// 配置更新时间
    pub updated_at: DateTime<Utc>,
}

impl Default for TemperatureThreshold {
    fn default() -> Self {
        TemperatureThreshold {
            id: Default::default(),
            component_type: "".to_string(),
            sensor_id: "".to_string(),
            normal_max: 0.0,
            warning_max: 0.0,
            critical_max: 0.0,
            created_at: Default::default(),
            updated_at: Default::default(),
        }
    }
}

/// 温度统计数据
///
/// 用于API响应的温度统计信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TemperatureStats {
    /// 平均温度
    pub average: f64,
    /// 最低温度
    pub minimum: f64,
    /// 最高温度
    pub maximum: f64,
    /// 当前温度
    pub current: f64,
    /// 统计时间范围（分钟）
    pub time_range_minutes: i32,
    /// 数据点数量
    pub data_points: i32,
}

/// 温度趋势数据
///
/// 用于图表显示的温度趋势信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TemperatureTrend {
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 温度值
    pub temperature: f64,
    /// 传感器标识符
    pub sensor_id: String,
}

/// 温度查询参数
///
/// 用于API查询的参数结构
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TemperatureQuery {
    /// 服务器ID（可选）
    pub server_id: Option<String>,
    /// 传感器ID（可选）
    pub sensor_id: Option<String>,
    /// 开始时间（可选）
    pub start_time: Option<DateTime<Utc>>,
    /// 结束时间（可选）
    pub end_time: Option<DateTime<Utc>>,
    /// 页码
    pub page: Option<usize>,
    /// 每页数量
    pub limit: Option<usize>,
}

impl Default for TemperatureQuery {
    fn default() -> Self {
        Self {
            server_id: None,
            sensor_id: None,
            start_time: None,
            end_time: None,
            page: Some(1),
            limit: Some(50),
        }
    }
}

impl TemperatureReading {
    /// 创建新的温度记录
    ///
    /// # 参数
    /// * `sensor_id` - 传感器标识符
    /// * `sensor_name` - 传感器名称
    /// * `temperature` - 温度值
    /// * `server_id` - 服务器标识符
    /// * `threshold` - 温度阈值配置
    pub fn new(
        sensor_id: String,
        sensor_name: String,
        temperature: f64,
        server_id: String,
        threshold: &TemperatureThreshold,
    ) -> Self {
        let status = Self::determine_status(temperature, threshold);

        Self {
            id: Uuid::new_v4(),
            sensor_id,
            sensor_name,
            temperature,
            status,
            timestamp: Utc::now(),
            server_id,
        }
    }

    /// 根据温度值和阈值确定温度状态
    ///
    /// # 参数
    /// * `temperature` - 温度值
    /// * `threshold` - 温度阈值配置
    fn determine_status(temperature: f64, threshold: &TemperatureThreshold) -> TemperatureStatus {
        if temperature >= threshold.critical_max {
            TemperatureStatus::Critical
        } else if temperature >= threshold.warning_max {
            TemperatureStatus::Warning
        } else if temperature <= threshold.normal_max {
            TemperatureStatus::Normal
        } else {
            TemperatureStatus::Normal
        }
    }
}

impl TemperatureThreshold {
    /// 创建新的温度阈值配置
    ///
    /// # 参数
    /// * `component_type` - 组件类型
    /// * `sensor_id` - 传感器标识符
    /// * `normal_max` - 正常温度上限
    /// * `warning_max` - 警告温度上限
    /// * `critical_max` - 危险温度上限
    pub fn new(
        component_type: String,
        sensor_id: String,
        normal_max: f64,
        warning_max: f64,
        critical_max: f64,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            component_type,
            sensor_id,
            normal_max,
            warning_max,
            critical_max,
            created_at: now,
            updated_at: now,
        }
    }
}
