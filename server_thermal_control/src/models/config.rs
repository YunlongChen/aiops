use crate::models::AppResult;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use utoipa::ToSchema;
use uuid::Uuid;

/// 应用程序配置
///
/// 存储应用程序的全局配置信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AppConfig {
    /// 服务器配置
    pub server: ServerConfig,
    /// 数据库配置
    pub database: DatabaseConfig,
    /// IPMI配置
    pub ipmi: IpmiConfig,
    /// 日志配置
    pub logging: LoggingConfig,
    /// 监控配置
    pub monitoring: MonitoringConfig,
    /// 告警配置
    pub alerting: AlertingConfig,
}

/// 服务器配置
///
/// HTTP服务器相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ServerConfig {
    /// 监听地址
    pub host: String,
    /// 监听端口
    pub port: u16,
    /// 工作线程数
    pub workers: Option<usize>,
    /// 请求超时时间（秒）
    pub timeout: u64,
    /// 是否启用CORS
    pub enable_cors: bool,
    /// 允许的源域名
    pub cors_origins: Vec<String>,
}

/// 数据库配置
///
/// 数据库连接和操作相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct DatabaseConfig {
    /// 数据库URL
    pub url: String,
    /// 最大连接数
    pub max_connections: u32,
    /// 连接超时时间（秒）
    pub connection_timeout: u64,
    /// 是否启用自动迁移
    pub auto_migrate: bool,
}

/// IPMI配置
///
/// IPMI工具和服务器连接相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct IpmiConfig {
    /// 目标服务器列表
    pub servers: Vec<ServerTarget>,
    /// IPMI工具路径
    pub ipmitool_path: String,
    /// 默认超时时间（秒）
    pub default_timeout: u64,
    /// 重试次数
    pub retry_count: u32,
    /// 重试间隔（秒）
    pub retry_interval: u64,
}

/// 服务器目标配置
///
/// 单个服务器的IPMI连接配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ServerTarget {
    /// 服务器标识符
    pub id: String,
    /// 服务器名称
    pub name: String,
    /// IPMI主机地址
    pub host: String,
    /// IPMI端口
    pub port: u16,
    /// 用户名
    pub username: String,
    /// 密码
    pub password: String,
    /// 接口类型（lan、lanplus等）
    pub interface: String,
    /// 是否启用
    pub enabled: bool,
}

/// 日志配置
///
/// 日志记录相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct LoggingConfig {
    /// 日志级别
    pub level: String,
    /// 日志格式
    pub format: LogFormat,
    /// 日志输出目标
    pub targets: Vec<LogTarget>,
    /// 日志文件路径
    pub file_path: Option<String>,
    /// 日志文件最大大小（MB）
    pub max_file_size: Option<u64>,
    /// 保留的日志文件数量
    pub max_files: Option<u32>,
    /// 打开控制台输出
    pub console_output: bool,
    // 打开文件输出
    pub file_output: bool,
}

impl Default for LoggingConfig {
    fn default() -> Self {
        todo!()
    }
}

/// 日志格式枚举
///
/// 定义不同的日志输出格式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum LogFormat {
    /// JSON格式
    Json,
    /// 纯文本格式
    Text,
    /// 紧凑格式
    Compact,
}

/// 日志输出目标枚举
///
/// 定义日志的输出目标
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum LogTarget {
    /// 控制台输出
    Console,
    /// 文件输出
    File,
    /// 系统日志
    Syslog,
}

/// 监控配置
///
/// 系统监控相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct MonitoringConfig {
    /// 数据采集间隔（秒）
    pub collection_interval: u64,
    /// 数据保留天数
    pub retention_days: u32,
    /// 是否启用性能监控
    pub enable_performance_monitoring: bool,
    /// 是否启用健康检查
    pub enable_health_checks: bool,
    /// 健康检查间隔（秒）
    pub health_check_interval: u64,
    /// 指标导出配置
    pub metrics_export: MetricsExportConfig,
}

impl Default for MonitoringConfig {
    fn default() -> Self {
        MonitoringConfig {
            collection_interval: 5,
            retention_days: 15,
            enable_performance_monitoring: false,
            enable_health_checks: true,
            health_check_interval: 60,
            metrics_export: MetricsExportConfig::default(),
        }
    }
}

impl MonitoringConfig {
    pub fn validate(&self) -> AppResult<()> {
        todo!()
    }
}

/// 指标导出配置
///
/// 监控指标导出相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct MetricsExportConfig {
    /// 是否启用Prometheus导出
    pub enable_prometheus: bool,
    /// Prometheus导出端口
    pub prometheus_port: Option<u16>,
    /// 是否启用InfluxDB导出
    pub enable_influxdb: bool,
    /// InfluxDB连接配置
    pub influxdb_config: Option<InfluxDbConfig>,
}

impl Default for MetricsExportConfig {
    fn default() -> Self {
        MetricsExportConfig {
            enable_prometheus: false,
            prometheus_port: None,
            enable_influxdb: false,
            influxdb_config: None,
        }
    }
}

/// InfluxDB配置
///
/// InfluxDB连接相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct InfluxDbConfig {
    /// InfluxDB URL
    pub url: String,
    /// 数据库名称
    pub database: String,
    /// 用户名
    pub username: Option<String>,
    /// 密码
    pub password: Option<String>,
    /// 批量写入大小
    pub batch_size: u32,
    /// 写入间隔（秒）
    pub write_interval: u64,
}

/// 告警配置
///
/// 告警系统相关配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AlertingConfig {
    /// 是否启用告警
    pub enabled: bool,
    /// 告警检查间隔（秒）
    pub check_interval: u64,
    /// 告警通知配置
    pub notifications: Vec<NotificationConfig>,
    /// 告警规则配置
    pub rules: Vec<AlertRule>,
}

/// 通知配置
///
/// 告警通知方式配置
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct NotificationConfig {
    /// 通知类型
    pub notification_type: NotificationType,
    /// 是否启用
    pub enabled: bool,
    /// 通知配置参数
    pub config: serde_json::Value,
}

/// 通知类型枚举
///
/// 定义不同的告警通知方式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum NotificationType {
    /// 邮件通知
    Email,
    /// 短信通知
    Sms,
    /// Webhook通知
    Webhook,
    /// Slack通知
    Slack,
    /// 钉钉通知
    DingTalk,
}

/// 告警规则
///
/// 定义告警触发的规则条件
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AlertRule {
    /// 规则名称
    pub name: String,
    /// 规则描述
    pub description: String,
    /// 监控指标
    pub metric: String,
    /// 比较操作符
    pub operator: ComparisonOperator,
    /// 阈值
    pub threshold: f64,
    /// 持续时间（秒）
    pub duration: u64,
    /// 告警级别
    pub severity: AlertSeverity,
    /// 是否启用
    pub enabled: bool,
}

/// 比较操作符枚举
///
/// 定义告警规则中的比较操作
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum ComparisonOperator {
    /// 大于
    GreaterThan,
    /// 大于等于
    GreaterThanOrEqual,
    /// 小于
    LessThan,
    /// 小于等于
    LessThanOrEqual,
    /// 等于
    Equal,
    /// 不等于
    NotEqual,
}

/// 告警严重程度枚举
///
/// 定义告警的严重程度级别
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

/// 系统设置
///
/// 存储系统运行时的设置信息
#[derive(Debug, Clone, Serialize, Deserialize, FromRow, ToSchema)]
pub struct SystemSettings {
    /// 设置唯一标识符
    pub id: Uuid,
    /// 设置键名
    pub key: String,
    /// 设置值
    pub value: String,
    /// 设置描述
    pub description: Option<String>,
    /// 设置类别
    pub category: String,
    /// 是否为系统设置
    pub is_system: bool,
    /// 创建时间
    pub created_at: DateTime<Utc>,
    /// 更新时间
    pub updated_at: DateTime<Utc>,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            server: ServerConfig {
                host: "127.0.0.1".to_string(),
                port: 8080,
                workers: None,
                timeout: 30,
                enable_cors: true,
                cors_origins: vec!["*".to_string()],
            },
            database: DatabaseConfig {
                url: "sqlite://thermal_control.db".to_string(),
                max_connections: 10,
                connection_timeout: 30,
                auto_migrate: true,
            },
            ipmi: IpmiConfig {
                servers: vec![],
                ipmitool_path: "ipmitool".to_string(),
                default_timeout: 10,
                retry_count: 3,
                retry_interval: 5,
            },
            logging: LoggingConfig::default(),
            monitoring: MonitoringConfig {
                collection_interval: 30,
                retention_days: 30,
                enable_performance_monitoring: true,
                enable_health_checks: true,
                health_check_interval: 60,
                metrics_export: MetricsExportConfig {
                    enable_prometheus: false,
                    prometheus_port: Some(9090),
                    enable_influxdb: false,
                    influxdb_config: None,
                },
            },
            alerting: AlertingConfig {
                enabled: true,
                check_interval: 60,
                notifications: vec![],
                rules: vec![],
            },
        }
    }
}

impl SystemSettings {
    /// 创建新的系统设置
    ///
    /// # 参数
    /// * `key` - 设置键名
    /// * `value` - 设置值
    /// * `description` - 设置描述
    /// * `category` - 设置类别
    /// * `is_system` - 是否为系统设置
    pub fn new(
        key: String,
        value: String,
        description: Option<String>,
        category: String,
        is_system: bool,
    ) -> Self {
        let now = Utc::now();
        Self {
            id: Uuid::new_v4(),
            key,
            value,
            description,
            category,
            is_system,
            created_at: now,
            updated_at: now,
        }
    }
}
