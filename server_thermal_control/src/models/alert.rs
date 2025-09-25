use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 警报配置
/// 
/// 定义警报系统的配置参数
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct AlertConfig {
    /// 配置唯一标识符
    pub id: Uuid,
    /// 配置名称
    pub name: String,
    /// 是否启用
    pub enabled: bool,
    /// 警报规则
    pub rules: Vec<AlertRule>,
    /// 通知渠道
    pub notification_channels: Vec<NotificationChannel>,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

/// 警报规则
/// 
/// 定义触发警报的规则
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AlertRule {
    /// 规则名称
    pub name: String,
    /// 规则描述
    pub description: String,
    /// 监控指标
    pub metric: String,
    /// 条件
    pub condition: AlertCondition,
    /// 严重级别
    pub severity: AlertSeverity,
    /// 是否启用
    pub enabled: bool,
}

/// 警报条件
/// 
/// 定义警报触发的条件
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AlertCondition {
    /// 比较操作符
    pub operator: String,
    /// 阈值
    pub threshold: f64,
    /// 持续时间（秒）
    pub duration_seconds: i32,
}

/// 警报严重级别枚举
/// 
/// 定义不同级别的警报严重程度
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AlertSeverity {
    /// 信息
    Info,
    /// 警告
    Warning,
    /// 错误
    Error,
    /// 严重
    Critical,
}

/// 通知渠道
/// 
/// 定义警报通知的渠道
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct NotificationChannel {
    /// 渠道类型
    pub channel_type: ChannelType,
    /// 渠道配置
    pub config: serde_json::Value,
    /// 是否启用
    pub enabled: bool,
}

/// 渠道类型枚举
/// 
/// 定义不同类型的通知渠道
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum ChannelType {
    /// 邮件
    Email,
    /// 短信
    Sms,
    /// Webhook
    Webhook,
    /// Slack
    Slack,
    /// 钉钉
    DingTalk,
}

/// 警报记录
/// 
/// 存储触发的警报记录
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct AlertRecord {
    /// 记录唯一标识符
    pub id: Uuid,
    /// 警报规则名称
    pub rule_name: String,
    /// 警报标题
    pub title: String,
    /// 警报描述
    pub description: String,
    /// 严重级别
    pub severity: AlertSeverity,
    /// 警报状态
    pub status: AlertStatus,
    /// 触发时间
    pub triggered_at: DateTime<Utc>,
    /// 确认时间
    pub acknowledged_at: Option<DateTime<Utc>>,
    /// 解决时间
    pub resolved_at: Option<DateTime<Utc>>,
    /// 确认者
    pub acknowledged_by: Option<String>,
    /// 解决者
    pub resolved_by: Option<String>,
    /// 服务器标识符
    pub server_id: String,
    /// 相关数据
    pub metadata: serde_json::Value,
}

/// 警报状态枚举
/// 
/// 定义警报的不同状态
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AlertStatus {
    /// 触发
    Triggered,
    /// 已确认
    Acknowledged,
    /// 已解决
    Resolved,
    /// 已忽略
    Ignored,
}

/// 通知记录
/// 
/// 记录发送的通知
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct NotificationRecord {
    /// 记录唯一标识符
    pub id: Uuid,
    /// 警报记录标识符
    pub alert_id: Uuid,
    /// 通知渠道类型
    pub channel_type: ChannelType,
    /// 接收者
    pub recipient: String,
    /// 通知内容
    pub content: String,
    /// 发送状态
    pub status: NotificationStatus,
    /// 发送时间
    pub sent_at: DateTime<Utc>,
    /// 错误信息
    pub error_message: Option<String>,
}

/// 通知状态枚举
/// 
/// 定义通知发送的状态
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum NotificationStatus {
    /// 待发送
    Pending,
    /// 发送中
    Sending,
    /// 发送成功
    Sent,
    /// 发送失败
    Failed,
}

/// 警报统计
/// 
/// 警报系统的统计信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AlertStatistics {
    /// 总警报数
    pub total_alerts: i64,
    /// 活跃警报数
    pub active_alerts: i64,
    /// 已确认警报数
    pub acknowledged_alerts: i64,
    /// 已解决警报数
    pub resolved_alerts: i64,
    /// 按严重级别分组的统计
    pub by_severity: std::collections::HashMap<String, i64>,
    /// 统计时间范围
    pub time_range: String,
}

impl AlertConfig {
    /// 创建新的警报配置
    /// 
    /// # 参数
    /// * `name` - 配置名称
    /// * `rules` - 警报规则列表
    /// * `notification_channels` - 通知渠道列表
    pub fn new(
        name: String,
        rules: Vec<AlertRule>,
        notification_channels: Vec<NotificationChannel>,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            name,
            enabled: true,
            rules,
            notification_channels,
            created_at: now,
            updated_at: now,
        }
    }

    /// 启用警报配置
    pub fn enable(&mut self) {
        self.enabled = true;
        self.updated_at = Utc::now();
    }

    /// 禁用警报配置
    pub fn disable(&mut self) {
        self.enabled = false;
        self.updated_at = Utc::now();
    }
}

impl AlertRecord {
    /// 创建新的警报记录
    /// 
    /// # 参数
    /// * `rule_name` - 规则名称
    /// * `title` - 警报标题
    /// * `description` - 警报描述
    /// * `severity` - 严重级别
    /// * `server_id` - 服务器标识符
    pub fn new(
        rule_name: String,
        title: String,
        description: String,
        severity: AlertSeverity,
        server_id: String,
    ) -> Self {
        Self {
            id: Uuid::new_v4(),
            rule_name,
            title,
            description,
            severity,
            status: AlertStatus::Triggered,
            triggered_at: Utc::now(),
            acknowledged_at: None,
            resolved_at: None,
            acknowledged_by: None,
            resolved_by: None,
            server_id,
            metadata: serde_json::Value::Null,
        }
    }

    /// 确认警报
    /// 
    /// # 参数
    /// * `acknowledged_by` - 确认者
    pub fn acknowledge(&mut self, acknowledged_by: String) {
        self.status = AlertStatus::Acknowledged;
        self.acknowledged_at = Some(Utc::now());
        self.acknowledged_by = Some(acknowledged_by);
    }

    /// 解决警报
    /// 
    /// # 参数
    /// * `resolved_by` - 解决者
    pub fn resolve(&mut self, resolved_by: String) {
        self.status = AlertStatus::Resolved;
        self.resolved_at = Some(Utc::now());
        self.resolved_by = Some(resolved_by);
    }
}