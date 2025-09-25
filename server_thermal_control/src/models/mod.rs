// 模块声明
pub mod analytics;
pub mod config;
pub mod error;
pub mod fan;
pub mod sensor;
pub mod thermal;
pub mod monitoring;
pub mod control;
pub mod alert;
pub mod api;

pub use analytics::*;
pub use config::*;
pub use error::*;
pub use fan::*;
pub use sensor::*;
pub use thermal::*;
pub use alert::AlertStatus;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

/// 温度数据模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct TemperatureData {
    pub id: Uuid,
    pub sensor_id: String,
    pub temperature: f64,
    pub unit: String,
    pub location: String,
    pub timestamp: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 风扇数据模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct FanData {
    pub id: Uuid,
    pub fan_id: String,
    pub speed_rpm: i32,
    pub speed_percent: i32,
    pub status: String,
    pub location: String,
    pub timestamp: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 传感器数据模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct SensorData {
    pub id: Uuid,
    pub sensor_id: String,
    pub sensor_type: String,
    pub value: f64,
    pub unit: String,
    pub status: String,
    pub location: String,
    pub timestamp: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 控制历史记录模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct ControlHistory {
    pub id: Uuid,
    pub action_type: String,
    pub target_id: String,
    pub old_value: Option<f64>,
    pub new_value: f64,
    pub reason: String,
    pub success: bool,
    pub error_message: Option<String>,
    pub timestamp: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

/// 告警模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Alert {
    pub id: Uuid,
    pub alert_type: String,
    pub severity: String,
    pub title: String,
    pub message: String,
    pub source: String,
    pub source_id: String,
    pub status: AlertStatus,
    pub acknowledged: bool,
    pub acknowledged_by: Option<String>,
    pub acknowledged_at: Option<DateTime<Utc>>,
    pub resolved_at: Option<DateTime<Utc>>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 配置模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct Configuration {
    pub id: Uuid,
    pub key: String,
    pub value: String,
    pub description: Option<String>,
    pub category: String,
    pub data_type: String,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// 监控指标模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct MonitoringMetric {
    pub id: Uuid,
    pub metric_name: String,
    pub metric_type: String,
    pub value: f64,
    pub unit: String,
    pub tags: Option<serde_json::Value>,
    pub timestamp: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

/// 分析结果模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AnalysisResult {
    pub id: Uuid,
    pub analysis_type: String,
    pub input_data: serde_json::Value,
    pub result_data: serde_json::Value,
    pub confidence: Option<f64>,
    pub recommendations: Option<String>,
    pub created_at: DateTime<Utc>,
}

/// 系统事件模型
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct SystemEvent {
    pub id: Uuid,
    pub event_type: String,
    pub event_level: String,
    pub title: String,
    pub description: String,
    pub source: String,
    pub metadata: Option<serde_json::Value>,
    pub created_at: DateTime<Utc>,
}

/// API响应包装器
#[derive(Debug, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub message: String,
    pub data: Option<T>,
    pub timestamp: DateTime<Utc>,
}

impl<T> ApiResponse<T> {
    /// 创建成功响应
    pub fn success(data: T, message: &str) -> Self {
        Self {
            success: true,
            message: message.to_string(),
            data: Some(data),
            timestamp: Utc::now(),
        }
    }
    
    /// 创建错误响应
    pub fn error(message: &str) -> Self {
        Self {
            success: false,
            message: message.to_string(),
            data: None,
            timestamp: Utc::now(),
        }
    }
}

/// 分页查询参数
#[derive(Debug, Deserialize)]
pub struct PaginationParams {
    pub page: Option<u32>,
    pub limit: Option<u32>,
    pub sort_by: Option<String>,
    pub sort_order: Option<String>,
}

impl Default for PaginationParams {
    fn default() -> Self {
        Self {
            page: Some(1),
            limit: Some(20),
            sort_by: Some("created_at".to_string()),
            sort_order: Some("desc".to_string()),
        }
    }
}

/// 分页响应
#[derive(Debug, Serialize)]
pub struct PaginatedResponse<T> {
    pub data: Vec<T>,
    pub total: u64,
    pub page: u32,
    pub limit: u32,
    pub total_pages: u32,
}

impl<T> PaginatedResponse<T> {
    /// 创建分页响应
    pub fn new(data: Vec<T>, total: u64, page: u32, limit: u32) -> Self {
        let total_pages = ((total as f64) / (limit as f64)).ceil() as u32;
        Self {
            data,
            total,
            page,
            limit,
            total_pages,
        }
    }
}

/// 温度统计数据
#[derive(Debug, Serialize, Deserialize)]
pub struct TemperatureStats {
    pub avg_temperature: f64,
    pub min_temperature: f64,
    pub max_temperature: f64,
    pub sensor_count: i64,
    pub timestamp: DateTime<Utc>,
}

/// 风扇读数
#[derive(Debug, Serialize, Deserialize)]
pub struct FanReading {
    pub id: i64,
    pub sensor_id: String,
    pub speed_rpm: f64,
    pub speed_percent: f64,
    pub timestamp: DateTime<Utc>,
}



/// 系统健康状态
#[derive(Debug, Serialize, Deserialize)]
pub struct SystemHealth {
    pub overall_status: String,
    pub temperature_status: String,
    pub fan_status: String,
    pub alert_count: i64,
    pub last_update: DateTime<Utc>,
}