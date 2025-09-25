use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 监控配置
/// 
/// 定义系统监控的各项配置参数
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct MonitoringConfiguration {
    /// 配置唯一标识符
    pub id: Uuid,
    /// 配置名称
    pub name: String,
    /// 监控间隔（秒）
    pub interval_seconds: i32,
    /// 是否启用
    pub enabled: bool,
    /// 监控目标
    pub targets: Vec<MonitoringTarget>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 监控目标
/// 
/// 定义具体的监控对象
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct MonitoringTarget {
    /// 目标类型
    pub target_type: MonitoringTargetType,
    /// 目标标识符
    pub target_id: String,
    /// 监控指标
    pub metrics: Vec<String>,
    /// 阈值配置
    pub thresholds: Option<ThresholdConfig>,
}

/// 监控目标类型枚举
/// 
/// 定义不同类型的监控目标
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum MonitoringTargetType {
    /// 温度传感器
    Temperature,
    /// 风扇
    Fan,
    /// CPU
    Cpu,
    /// 内存
    Memory,
    /// 磁盘
    Disk,
    /// 网络
    Network,
}

/// 阈值配置
/// 
/// 定义监控指标的阈值设置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ThresholdConfig {
    /// 警告阈值
    pub warning: f64,
    /// 严重阈值
    pub critical: f64,
    /// 比较操作符
    pub operator: ComparisonOperator,
}

/// 比较操作符枚举
/// 
/// 定义阈值比较的操作符
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum ComparisonOperator {
    /// 大于
    GreaterThan,
    /// 小于
    LessThan,
    /// 等于
    Equal,
    /// 大于等于
    GreaterThanOrEqual,
    /// 小于等于
    LessThanOrEqual,
}

/// 监控数据点
/// 
/// 存储监控采集的数据点
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct MonitoringDataPoint {
    /// 数据点唯一标识符
    pub id: Uuid,
    /// 目标标识符
    pub target_id: String,
    /// 指标名称
    pub metric_name: String,
    /// 指标值
    pub value: f64,
    /// 单位
    pub unit: String,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 服务器标识符
    pub server_id: String,
}

impl MonitoringConfiguration {
    /// 创建新的监控配置
    /// 
    /// # 参数
    /// * `name` - 配置名称
    /// * `interval_seconds` - 监控间隔
    /// * `targets` - 监控目标列表
    pub fn new(
        name: String,
        interval_seconds: i32,
        targets: Vec<MonitoringTarget>,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name,
            interval_seconds,
            enabled: true,
            targets,
            created_at: now,
            updated_at: now,
        }
    }

    /// 启用监控配置
    pub fn enable(&mut self) {
        self.enabled = true;
        self.updated_at = Utc::now();
    }

    /// 禁用监控配置
    pub fn disable(&mut self) {
        self.enabled = false;
        self.updated_at = Utc::now();
    }
}

impl MonitoringDataPoint {
    /// 创建新的监控数据点
    /// 
    /// # 参数
    /// * `target_id` - 目标标识符
    /// * `metric_name` - 指标名称
    /// * `value` - 指标值
    /// * `unit` - 单位
    /// * `server_id` - 服务器标识符
    pub fn new(
        target_id: String,
        metric_name: String,
        value: f64,
        unit: String,
        server_id: String,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            target_id,
            metric_name,
            value,
            unit,
            timestamp: Utc::now(),
            server_id,
        }
    }
}