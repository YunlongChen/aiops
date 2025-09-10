//! 数据模型模块
//! 
//! 定义AIOps测试管理系统的核心数据结构

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

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
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
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
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
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
#[derive(Debug, Deserialize)]
pub struct PaginationParams {
    #[serde(default = "default_page")]
    pub page: u32,
    #[serde(default = "default_limit")]
    pub limit: u32,
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

/// 分页响应结构
#[derive(Debug, Serialize)]
pub struct PaginatedResponse<T> {
    pub data: Vec<T>,
    pub pagination: PaginationInfo,
}

/// 分页信息
#[derive(Debug, Serialize)]
pub struct PaginationInfo {
    pub page: u32,
    pub limit: u32,
    pub total: u64,
    pub total_pages: u32,
    pub has_next: bool,
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
#[derive(Debug, Serialize)]
pub struct ApiResponse<T> {
    pub success: bool,
    pub data: Option<T>,
    pub message: Option<String>,
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