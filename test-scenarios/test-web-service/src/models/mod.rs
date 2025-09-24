//! 数据模型模块
//! 
//! 定义AIOps测试管理系统的核心数据结构

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use utoipa::{ToSchema, IntoParams};

// 子模块
pub mod test_case;
pub mod test_run;
pub mod runtime_manager;
pub mod test_script;

pub use test_case::*;
pub use test_run::*;
pub use runtime_manager::*;
pub use test_script::*;

/// 运行时类型枚举
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, ToSchema)]
#[serde(rename_all = "lowercase")]
pub enum RuntimeType {
    /// 本地运行时
    Local,
    /// Docker容器运行时
    Docker,
    /// Kubernetes集群运行时
    Kubernetes,
}

impl std::fmt::Display for RuntimeType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RuntimeType::Local => write!(f, "local"),
            RuntimeType::Docker => write!(f, "docker"),
            RuntimeType::Kubernetes => write!(f, "kubernetes"),
        }
    }
}

impl std::str::FromStr for RuntimeType {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s.to_lowercase().as_str() {
            "local" => Ok(RuntimeType::Local),
            "docker" => Ok(RuntimeType::Docker),
            "kubernetes" | "k8s" => Ok(RuntimeType::Kubernetes),
            _ => anyhow::bail!("未知的运行时类型: {}", s),
        }
    }
}

/// 测试状态枚举
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, ToSchema)]
#[serde(rename_all = "lowercase")]
pub enum TestStatus {
    /// 等待中
    Pending,
    /// 运行中
    Running,
    /// 成功完成
    Success,
    /// 失败
    Failed,
    /// 已取消
    Cancelled,
    /// 超时
    Timeout,
}

impl std::fmt::Display for TestStatus {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            TestStatus::Pending => write!(f, "pending"),
            TestStatus::Running => write!(f, "running"),
            TestStatus::Success => write!(f, "success"),
            TestStatus::Failed => write!(f, "failed"),
            TestStatus::Cancelled => write!(f, "cancelled"),
            TestStatus::Timeout => write!(f, "timeout"),
        }
    }
}

/// 分页请求参数
#[derive(Debug, Deserialize, ToSchema, IntoParams)]
pub struct PaginationParams {
    #[serde(default = "default_page", deserialize_with = "deserialize_string_to_u32")]
    /// 页码，从1开始
    pub page: u32,
    #[serde(default = "default_limit", deserialize_with = "deserialize_string_to_u32")]
    /// 每页数量，最大100
    pub limit: u32,
}

/// 将字符串反序列化为u32
fn deserialize_string_to_u32<'de, D>(deserializer: D) -> Result<u32, D::Error>
where
    D: serde::Deserializer<'de>,
{
    use serde::de::{self, Visitor};
    use std::fmt;

    struct StringToU32Visitor;

    impl<'de> Visitor<'de> for StringToU32Visitor {
        type Value = u32;

        fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
            formatter.write_str("a string or number that can be converted to u32")
        }

        fn visit_i64<E>(self, value: i64) -> Result<u32, E>
        where
            E: de::Error,
        {
            if value >= 0 && value <= u32::MAX as i64 {
                Ok(value as u32)
            } else {
                Err(de::Error::custom(format!("u32 out of range: {}", value)))
            }
        }

        fn visit_u64<E>(self, value: u64) -> Result<u32, E>
        where
            E: de::Error,
        {
            if value <= u32::MAX as u64 {
                Ok(value as u32)
            } else {
                Err(de::Error::custom(format!("u32 out of range: {}", value)))
            }
        }

        fn visit_str<E>(self, value: &str) -> Result<u32, E>
        where
            E: de::Error,
        {
            value.parse().map_err(de::Error::custom)
        }
    }

    deserializer.deserialize_any(StringToU32Visitor)
}

fn default_page() -> u32 {
    1
}

fn default_limit() -> u32 {
    20
}

impl PaginationParams {
    pub fn offset(&self) -> u32 {
        (self.page - 1) * self.limit
    }

    pub fn validate(&self) -> anyhow::Result<()> {
        if self.page == 0 {
            anyhow::bail!("页码不能为0");
        }
        if self.limit == 0 || self.limit > 100 {
            anyhow::bail!("每页数量必须在1-100之间");
        }
        Ok(())
    }
}

/// 分页响应数据
#[derive(Debug, Serialize, ToSchema)]
pub struct PaginatedResponse<T> {
    /// 数据列表
    pub data: Vec<T>,
    /// 分页信息
    pub pagination: PaginationInfo,
}

/// 分页信息
#[derive(Debug, Serialize, ToSchema)]
pub struct PaginationInfo {
    /// 当前页码
    pub page: u32,
    /// 每页数量
    pub limit: u32,
    /// 总记录数
    pub total: u64,
    /// 总页数
    pub total_pages: u32,
    /// 是否有下一页
    pub has_next: bool,
    /// 是否有上一页
    pub has_prev: bool,
}

impl PaginationInfo {
    pub fn new(page: u32, limit: u32, total: u64) -> Self {
        let total_pages = ((total as f64) / (limit as f64)).ceil() as u32;
        Self {
            page,
            limit,
            total,
            total_pages,
            has_next: page < total_pages,
            has_prev: page > 1,
        }
    }
}

/// API响应结构
#[derive(Debug, Serialize, ToSchema)]
pub struct ApiResponse<T> {
    /// 请求是否成功
    pub success: bool,
    /// 响应数据
    pub data: Option<T>,
    /// 错误消息
    pub message: Option<String>,
    /// 响应时间戳
    pub timestamp: DateTime<Utc>,
}

impl<T> ApiResponse<T> {
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            message: None,
            timestamp: Utc::now(),
        }
    }

    pub fn error(message: String) -> Self {
        Self {
            success: false,
            data: None,
            message: Some(message),
            timestamp: Utc::now(),
        }
    }
}