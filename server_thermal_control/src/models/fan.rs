use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 风扇状态记录
///
/// 存储风扇的当前状态和转速信息
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct FanStatus {
    /// 记录唯一标识符
    pub id: Uuid,
    /// 风扇标识符
    pub fan_id: String,
    /// 风扇名称
    pub fan_name: String,
    /// 当前转速（RPM）
    pub current_rpm: f32,
    /// 目标转速（RPM）
    pub target_rpm: f32,
    /// 转速百分比（0-100）
    pub speed_percentage: f64,
    /// 风扇状态
    pub status: FanOperationStatus,
    /// 记录时间戳
    pub timestamp: DateTime<Utc>,
    /// 服务器标识符
    pub server_id: String,
}

/// 风扇控制命令
///
/// 用于发送风扇控制指令
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FanControlCommand {
    /// 风扇标识符
    pub fan_id: String,
    /// 控制类型
    pub control_type: FanControlType,
    /// 目标值（转速或百分比）
    pub target_value: f64,
    /// 命令优先级
    pub priority: CommandPriority,
    /// 执行延迟（秒）
    pub delay_seconds: Option<i32>,
}

/// 风扇控制策略
///
/// 定义自动风扇控制的策略配置
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct FanControlStrategy {
    /// 策略唯一标识符
    pub id: Uuid,
    /// 策略名称
    pub name: String,
    /// 策略描述
    pub description: String,
    /// 目标温度范围
    pub target_temperature_range: TemperatureRange,
    /// 风扇曲线配置
    pub fan_curve: Vec<FanCurvePoint>,
    /// 是否启用
    pub enabled: bool,
    /// 优先级
    pub priority: i32,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 风扇操作状态枚举
///
/// 定义风扇的不同操作状态
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum FanOperationStatus {
    /// 正常运行
    Normal,
    /// 高速运行
    HighSpeed,
    /// 低速运行
    LowSpeed,
    /// 故障状态
    Error,
    /// 离线状态
    Offline,
}

/// 风扇控制类型枚举
///
/// 定义不同的风扇控制方式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum FanControlType {
    /// 按转速控制（RPM）
    Rpm,
    /// 按百分比控制（0-100%）
    Percentage,
    /// 自动控制
    Auto,
    /// 手动控制
    Manual,
}

/// 命令优先级枚举
///
/// 定义控制命令的优先级
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum CommandPriority {
    /// 低优先级
    Low,
    /// 正常优先级
    Normal,
    /// 高优先级
    High,
    /// 紧急优先级
    Emergency,
}

/// 温度范围结构
///
/// 定义温度的最小值和最大值范围
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TemperatureRange {
    /// 最低温度
    pub min: f64,
    /// 最高温度
    pub max: f64,
}

/// 风扇曲线点
///
/// 定义温度与风扇转速的对应关系点
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FanCurvePoint {
    /// 温度值
    pub temperature: f64,
    /// 对应的风扇转速百分比
    pub fan_speed_percentage: f64,
}

/// 风扇统计信息
///
/// 用于分析和报告风扇性能数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FanStats {
    /// 风扇标识符
    pub fan_id: String,
    /// 平均转速
    pub average_rpm: f64,
    /// 最小转速
    pub min_rpm: i32,
    /// 最大转速
    pub max_rpm: i32,
    /// 运行时间（小时）
    pub runtime_hours: f64,
    /// 转速变化次数
    pub speed_changes: i32,
    /// 时间范围（小时）
    pub time_range_hours: i32,
}

/// 风扇性能统计
///
/// 详细的风扇性能分析数据
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FanPerformanceStats {
    /// 风扇标识符
    pub fan_id: String,
    /// 平均转速
    pub average_rpm: f64,
    /// 最低转速
    pub min_rpm: i32,
    /// 最高转速
    pub max_rpm: i32,
    /// 运行时间（小时）
    pub runtime_hours: f64,
    /// 转速变化次数
    pub speed_changes: i32,
    /// 统计时间范围
    pub time_range_hours: i32,
}

/// 风扇控制历史记录
///
/// 记录风扇控制命令的执行历史
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct FanControlHistory {
    /// 记录唯一标识符
    pub id: Uuid,
    /// 风扇标识符
    pub fan_id: String,
    /// 控制命令
    pub command: String,
    /// 执行前转速
    pub previous_rpm: i32,
    /// 执行后转速
    pub new_rpm: i32,
    /// 执行结果
    pub result: CommandResult,
    /// 执行时间
    pub executed_at: DateTime<Utc>,
    /// 执行者（系统/用户）
    pub executor: String,
}

/// 命令执行结果枚举
///
/// 定义命令执行的结果状态
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum CommandResult {
    /// 执行成功
    Success,
    /// 执行失败
    Failed,
    /// 部分成功
    PartialSuccess,
    /// 超时
    Timeout,
}

impl FanStatus {
    /// 创建新的风扇状态记录
    ///
    /// # 参数
    /// * `fan_id` - 风扇标识符
    /// * `fan_name` - 风扇名称
    /// * `current_rpm` - 当前转速
    /// * `target_rpm` - 目标转速
    /// * `server_id` - 服务器标识符
    pub fn new(
        fan_id: String,
        fan_name: String,
        current_rpm: f32,
        target_rpm: f32,
        server_id: String,
    ) -> Self {
        let speed_percentage = Self::calculate_speed_percentage(current_rpm);
        let status = Self::determine_status(current_rpm, target_rpm);

        Self {
            id: Uuid::new_v4(),
            fan_id,
            fan_name,
            current_rpm,
            target_rpm,
            speed_percentage,
            status,
            timestamp: Utc::now(),
            server_id,
        }
    }

    /// 计算转速百分比
    ///
    /// # 参数
    /// * `rpm` - 当前转速
    fn calculate_speed_percentage(rpm: f32) -> f64 {
        // 假设最大转速为6000 RPM
        const MAX_RPM: f64 = 6000.0;
        (rpm as f64 / MAX_RPM * 100.0).min(100.0).max(0.0)
    }

    /// 根据当前转速和目标转速确定风扇状态
    ///
    /// # 参数
    /// * `current_rpm` - 当前转速
    /// * `target_rpm` - 目标转速
    fn determine_status(current_rpm: f32, target_rpm: f32) -> FanOperationStatus {
        if current_rpm <= 0f32 {
            FanOperationStatus::Offline
        } else if current_rpm > 4000f32 {
            FanOperationStatus::HighSpeed
        } else if current_rpm < 1000f32 {
            FanOperationStatus::LowSpeed
        } else {
            FanOperationStatus::Normal
        }
    }
}

/// 风扇读数
///
/// 存储风扇的实时读数信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FanReading {
    /// 记录ID
    pub id: i64,
    /// 传感器ID
    pub sensor_id: String,
    /// 转速（RPM）
    pub speed_rpm: f64,
    /// 转速百分比
    pub speed_percent: f64,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
}

/// 风扇配置
///
/// 定义风扇的配置参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FanConfig {
    /// 风扇ID
    pub fan_id: String,
    /// 风扇名称
    pub name: String,
    /// 最小转速
    pub min_rpm: i32,
    /// 最大转速
    pub max_rpm: i32,
    /// 默认转速百分比
    pub default_speed_percent: f64,
    /// 是否启用
    pub enabled: bool,
}

impl FanControlStrategy {
    /// 创建新的风扇控制策略
    ///
    /// # 参数
    /// * `name` - 策略名称
    /// * `description` - 策略描述
    /// * `temperature_range` - 目标温度范围
    /// * `fan_curve` - 风扇曲线配置
    pub fn new(
        name: String,
        description: String,
        temperature_range: TemperatureRange,
        fan_curve: Vec<FanCurvePoint>,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            name,
            description,
            target_temperature_range: temperature_range,
            fan_curve,
            enabled: true,
            priority: 1,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        }
    }

    /// 根据温度计算风扇转速
    ///
    /// # 参数
    /// * `temperature` - 当前温度
    ///
    /// # 返回值
    /// 计算得出的风扇转速百分比
    pub fn calculate_fan_speed(&self, temperature: f64) -> f64 {
        if self.fan_curve.is_empty() {
            return 50.0; // 默认50%转速
        }

        // 线性插值计算风扇转速
        for i in 0..self.fan_curve.len() - 1 {
            let current_point = &self.fan_curve[i];
            let next_point = &self.fan_curve[i + 1];

            if temperature >= current_point.temperature && temperature <= next_point.temperature {
                let temp_diff = next_point.temperature - current_point.temperature;
                let speed_diff =
                    next_point.fan_speed_percentage - current_point.fan_speed_percentage;
                let temp_ratio = (temperature - current_point.temperature) / temp_diff;

                return current_point.fan_speed_percentage + (speed_diff * temp_ratio);
            }
        }

        // 如果温度超出范围，返回边界值
        if temperature <= self.fan_curve[0].temperature {
            self.fan_curve[0].fan_speed_percentage
        } else {
            self.fan_curve.last().unwrap().fan_speed_percentage
        }
    }
}
