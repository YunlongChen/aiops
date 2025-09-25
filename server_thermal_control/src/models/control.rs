use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 控制配置
/// 
/// 定义系统控制的各项配置参数
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct ControlConfig {
    /// 配置唯一标识符
    pub id: Uuid,
    /// 配置名称
    pub name: String,
    /// 控制模式
    pub control_mode: ControlMode,
    /// 是否启用自动控制
    pub auto_control_enabled: bool,
    /// 控制参数
    pub parameters: ControlParameters,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 控制模式枚举
/// 
/// 定义不同的控制模式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum ControlMode {
    /// 手动控制
    Manual,
    /// 自动控制
    Auto,
    /// PID控制
    Pid,
    /// 智能控制
    Smart,
}

/// 控制参数
/// 
/// 定义控制算法的参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ControlParameters {
    /// 目标温度
    pub target_temperature: f64,
    /// 温度容差
    pub temperature_tolerance: f64,
    /// PID参数
    pub pid_params: Option<PidParameters>,
    /// 最大风扇转速
    pub max_fan_speed: i32,
    /// 最小风扇转速
    pub min_fan_speed: i32,
}

/// PID控制参数
/// 
/// 定义PID控制器的参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct PidParameters {
    /// 比例系数
    pub kp: f64,
    /// 积分系数
    pub ki: f64,
    /// 微分系数
    pub kd: f64,
    /// 积分限制
    pub integral_limit: f64,
}

/// 控制策略
/// 
/// 定义控制策略的配置
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct ControlStrategy {
    /// 策略唯一标识符
    pub id: Uuid,
    /// 策略名称
    pub name: String,
    /// 策略描述
    pub description: String,
    /// 策略类型
    pub strategy_type: StrategyType,
    /// 策略规则
    pub rules: Vec<ControlRule>,
    /// 优先级
    pub priority: i32,
    /// 是否启用
    pub enabled: bool,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 策略类型枚举
/// 
/// 定义不同类型的控制策略
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum StrategyType {
    /// 温度控制策略
    Temperature,
    /// 负载控制策略
    Load,
    /// 节能策略
    PowerSaving,
    /// 性能策略
    Performance,
}

/// 控制规则
/// 
/// 定义具体的控制规则
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ControlRule {
    /// 规则名称
    pub name: String,
    /// 条件
    pub condition: RuleCondition,
    /// 动作
    pub action: RuleAction,
    /// 是否启用
    pub enabled: bool,
}

/// 规则条件
/// 
/// 定义规则触发的条件
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct RuleCondition {
    /// 监控指标
    pub metric: String,
    /// 比较操作符
    pub operator: String,
    /// 阈值
    pub threshold: f64,
    /// 持续时间（秒）
    pub duration_seconds: i32,
}

/// 规则动作
/// 
/// 定义规则触发后的动作
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct RuleAction {
    /// 动作类型
    pub action_type: ActionType,
    /// 动作参数
    pub parameters: serde_json::Value,
}

/// 动作类型枚举
/// 
/// 定义不同类型的控制动作
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum ActionType {
    /// 设置风扇转速
    SetFanSpeed,
    /// 发送警报
    SendAlert,
    /// 执行脚本
    ExecuteScript,
    /// 紧急关机
    EmergencyShutdown,
}

/// 控制历史记录
/// 
/// 记录控制操作的历史
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct ControlHistory {
    /// 记录唯一标识符
    pub id: Uuid,
    /// 策略标识符
    pub strategy_id: Option<Uuid>,
    /// 控制动作
    pub action: String,
    /// 动作参数
    pub parameters: serde_json::Value,
    /// 执行结果
    pub result: String,
    /// 执行时间
    pub executed_at: DateTime<Utc>,
    /// 执行者
    pub executor: String,
}

impl ControlConfig {
    /// 创建新的控制配置
    /// 
    /// # 参数
    /// * `name` - 配置名称
    /// * `control_mode` - 控制模式
    /// * `parameters` - 控制参数
    pub fn new(
        name: String,
        control_mode: ControlMode,
        parameters: ControlParameters,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name,
            control_mode,
            auto_control_enabled: true,
            parameters,
            created_at: now,
            updated_at: now,
        }
    }

    /// 启用自动控制
    pub fn enable_auto_control(&mut self) {
        self.auto_control_enabled = true;
        self.updated_at = Utc::now();
    }

    /// 禁用自动控制
    pub fn disable_auto_control(&mut self) {
        self.auto_control_enabled = false;
        self.updated_at = Utc::now();
    }
}

impl ControlStrategy {
    /// 创建新的控制策略
    /// 
    /// # 参数
    /// * `name` - 策略名称
    /// * `description` - 策略描述
    /// * `strategy_type` - 策略类型
    /// * `rules` - 控制规则列表
    pub fn new(
        name: String,
        description: String,
        strategy_type: StrategyType,
        rules: Vec<ControlRule>,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name,
            description,
            strategy_type,
            rules,
            priority: 1,
            enabled: true,
            created_at: now,
            updated_at: now,
        }
    }
}