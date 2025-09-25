use actix_web::{HttpResponse, ResponseError};
use serde::{Deserialize, Serialize};
use thiserror::Error;
use utoipa::ToSchema;

/// 应用程序错误类型
///
/// 定义应用程序中可能出现的各种错误类型
#[derive(Error, Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AppError {
    /// 数据库错误
    #[error("数据库错误: {message}")]
    DatabaseError { message: String },

    /// IPMI工具错误
    #[error("IPMI工具错误: {message}")]
    IpmiError { message: String },

    /// 配置错误
    #[error("配置错误: {message}")]
    ConfigError { message: String },

    /// 验证错误
    #[error("验证错误: {field}: {message}")]
    ValidationError { field: String, message: String },

    /// 认证错误
    #[error("认证错误: {message}")]
    AuthenticationError { message: String },

    /// 授权错误
    #[error("授权错误: {message}")]
    AuthorizationError { message: String },

    /// 资源未找到错误
    #[error("资源未找到: {resource}: {id}")]
    NotFoundError { resource: String, id: String },

    /// 资源冲突错误
    #[error("资源冲突: {message}")]
    ConflictError { message: String },

    /// 外部服务错误
    #[error("外部服务错误: {service}: {message}")]
    ExternalServiceError { service: String, message: String },

    /// 网络错误
    #[error("网络错误: {message}")]
    NetworkError { message: String },

    /// 超时错误
    #[error("操作超时: {operation}")]
    TimeoutError { operation: String },

    /// 解析错误
    #[error("解析错误: {message}")]
    ParseError { message: String },

    /// 序列化错误
    #[error("序列化错误: {message}")]
    SerializationError { message: String },

    /// 文件系统错误
    #[error("文件系统错误: {message}")]
    FileSystemError { message: String },

    /// 权限错误
    #[error("权限错误: {message}")]
    PermissionError { message: String },

    /// 内部服务器错误
    #[error("内部服务器错误: {message}")]
    InternalServerError { message: String },

    /// 服务不可用错误
    #[error("服务不可用: {service}")]
    ServiceUnavailableError { service: String },

    /// 请求过于频繁错误
    #[error("请求过于频繁: {message}")]
    RateLimitError { message: String },

    /// 业务逻辑错误
    #[error("业务逻辑错误: {message}")]
    BusinessLogicError { message: String },
}

/// 错误响应结构
///
/// 标准化的API错误响应格式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ErrorResponse {
    /// 错误代码
    pub error_code: String,
    /// 错误消息
    pub message: String,
    /// 详细错误信息
    pub details: Option<serde_json::Value>,
    /// 请求ID（用于追踪）
    pub request_id: Option<String>,
    /// 时间戳
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// 验证错误详情
///
/// 字段验证错误的详细信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ValidationErrorDetail {
    /// 字段名称
    pub field: String,
    /// 错误消息
    pub message: String,
    /// 拒绝的值
    pub rejected_value: Option<serde_json::Value>,
}

/// 错误上下文
///
/// 错误发生时的上下文信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ErrorContext {
    /// 操作名称
    pub operation: String,
    /// 服务器ID
    pub server_id: Option<String>,
    /// 用户ID
    pub user_id: Option<String>,
    /// 请求路径
    pub request_path: Option<String>,
    /// 请求方法
    pub request_method: Option<String>,
    /// 额外的上下文数据
    pub additional_data: Option<serde_json::Value>,
}

impl AppError {
    /// 创建数据库错误
    ///
    /// # 参数
    /// * `message` - 错误消息
    pub fn database_error(message: impl Into<String>) -> Self {
        Self::DatabaseError {
            message: message.into(),
        }
    }

    /// io异常
    ///
    /// # 参数
    /// * `message` - 错误消息
    pub fn file_system_error(message: impl Into<String>) -> Self {
        Self::DatabaseError {
            message: message.into(),
        }
    }

    /// 创建IPMI错误
    ///
    /// # 参数
    /// * `message` - 错误消息
    pub fn ipmi_error(message: impl Into<String>) -> Self {
        Self::IpmiError {
            message: message.into(),
        }
    }

    /// 创建配置错误
    ///
    /// # 参数
    /// * `message` - 错误消息
    pub fn config_error(message: impl Into<String>) -> Self {
        Self::ConfigError {
            message: message.into(),
        }
    }

    /// 创建验证错误
    ///
    /// # 参数
    /// * `field` - 字段名称
    /// * `message` - 错误消息
    pub fn validation_error(field: impl Into<String>, message: impl Into<String>) -> Self {
        Self::ValidationError {
            field: field.into(),
            message: message.into(),
        }
    }

    /// 创建资源未找到错误
    ///
    /// # 参数
    /// * `resource` - 资源类型
    /// * `id` - 资源ID
    pub fn not_found_error(resource: impl Into<String>, id: impl Into<String>) -> Self {
        Self::NotFoundError {
            resource: resource.into(),
            id: id.into(),
        }
    }

    /// 创建内部服务器错误
    ///
    /// # 参数
    /// * `message` - 错误消息
    pub fn internal_server_error(message: impl Into<String>) -> Self {
        Self::InternalServerError {
            message: message.into(),
        }
    }

    /// 网络错误
    ///
    /// # 参数
    /// * `message` - 错误消息
    pub fn network_error(message: impl Into<String>) -> Self {
        Self::NetworkError {
            message: message.into(),
        }
    }

    /// 序列化错误
    ///
    /// # 参数
    /// * `message` - 错误消息
    pub fn serialization_error(message: impl Into<String>) -> Self {
        Self::ParseError {
            message: message.into(),
        }
    }

    /// 获取错误代码
    ///
    /// 返回错误的标准化代码
    pub fn error_code(&self) -> &'static str {
        match self {
            AppError::DatabaseError { .. } => "DATABASE_ERROR",
            AppError::IpmiError { .. } => "IPMI_ERROR",
            AppError::ConfigError { .. } => "CONFIG_ERROR",
            AppError::ValidationError { .. } => "VALIDATION_ERROR",
            AppError::AuthenticationError { .. } => "AUTHENTICATION_ERROR",
            AppError::AuthorizationError { .. } => "AUTHORIZATION_ERROR",
            AppError::NotFoundError { .. } => "NOT_FOUND",
            AppError::ConflictError { .. } => "CONFLICT",
            AppError::ExternalServiceError { .. } => "EXTERNAL_SERVICE_ERROR",
            AppError::NetworkError { .. } => "NETWORK_ERROR",
            AppError::TimeoutError { .. } => "TIMEOUT_ERROR",
            AppError::ParseError { .. } => "PARSE_ERROR",
            AppError::SerializationError { .. } => "SERIALIZATION_ERROR",
            AppError::FileSystemError { .. } => "FILESYSTEM_ERROR",
            AppError::PermissionError { .. } => "PERMISSION_ERROR",
            AppError::InternalServerError { .. } => "INTERNAL_SERVER_ERROR",
            AppError::ServiceUnavailableError { .. } => "SERVICE_UNAVAILABLE",
            AppError::RateLimitError { .. } => "RATE_LIMIT_EXCEEDED",
            AppError::BusinessLogicError { .. } => "BUSINESS_LOGIC_ERROR",
        }
    }

    /// 获取HTTP状态码
    ///
    /// 返回对应的HTTP状态码
    pub fn status_code(&self) -> u16 {
        match self {
            AppError::ValidationError { .. } => 400,
            AppError::AuthenticationError { .. } => 401,
            AppError::AuthorizationError { .. } => 403,
            AppError::NotFoundError { .. } => 404,
            AppError::ConflictError { .. } => 409,
            AppError::RateLimitError { .. } => 429,
            AppError::InternalServerError { .. } => 500,
            AppError::ServiceUnavailableError { .. } => 503,
            AppError::TimeoutError { .. } => 504,
            _ => 500,
        }
    }

    /// 转换为错误响应
    ///
    /// # 参数
    /// * `request_id` - 请求ID
    pub fn to_error_response(&self, request_id: Option<String>) -> ErrorResponse {
        ErrorResponse {
            error_code: self.error_code().to_string(),
            message: self.to_string(),
            details: None,
            request_id,
            timestamp: chrono::Utc::now(),
        }
    }
}

impl ResponseError for AppError {
    fn error_response(&self) -> HttpResponse {
        let error_response = self.to_error_response(None);

        match self.status_code() {
            400 => HttpResponse::BadRequest().json(error_response),
            401 => HttpResponse::Unauthorized().json(error_response),
            403 => HttpResponse::Forbidden().json(error_response),
            404 => HttpResponse::NotFound().json(error_response),
            409 => HttpResponse::Conflict().json(error_response),
            429 => HttpResponse::TooManyRequests().json(error_response),
            503 => HttpResponse::ServiceUnavailable().json(error_response),
            504 => HttpResponse::GatewayTimeout().json(error_response),
            _ => HttpResponse::InternalServerError().json(error_response),
        }
    }
}

// 从其他错误类型转换为AppError
impl From<sqlx::Error> for AppError {
    fn from(err: sqlx::Error) -> Self {
        AppError::DatabaseError {
            message: err.to_string(),
        }
    }
}

impl From<serde_json::Error> for AppError {
    fn from(err: serde_json::Error) -> Self {
        AppError::SerializationError {
            message: err.to_string(),
        }
    }
}

impl From<std::io::Error> for AppError {
    fn from(err: std::io::Error) -> Self {
        AppError::FileSystemError {
            message: err.to_string(),
        }
    }
}

impl From<reqwest::Error> for AppError {
    fn from(err: reqwest::Error) -> Self {
        AppError::NetworkError {
            message: err.to_string(),
        }
    }
}

impl From<config::ConfigError> for AppError {
    fn from(err: config::ConfigError) -> Self {
        AppError::ConfigError {
            message: err.to_string(),
        }
    }
}

impl From<chrono::ParseError> for AppError {
    fn from(err: chrono::ParseError) -> Self {
        AppError::ParseError {
            message: err.to_string(),
        }
    }
}

impl From<uuid::Error> for AppError {
    fn from(err: uuid::Error) -> Self {
        AppError::ParseError {
            message: format!("UUID解析错误: {}", err),
        }
    }
}

/// 应用程序结果类型
///
/// 标准化的结果类型，用于错误处理
pub type AppResult<T> = Result<T, AppError>;

/// 创建验证错误的宏
///
/// 简化验证错误的创建
#[macro_export]
macro_rules! validation_error {
    ($field:expr, $message:expr) => {
        AppError::validation_error($field, $message)
    };
}

/// 创建未找到错误的宏
///
/// 简化未找到错误的创建
#[macro_export]
macro_rules! not_found_error {
    ($resource:expr, $id:expr) => {
        AppError::not_found_error($resource, $id)
    };
}

/// 创建内部服务器错误的宏
///
/// 简化内部服务器错误的创建
#[macro_export]
macro_rules! internal_error {
    ($message:expr) => {
        AppError::internal_server_error($message)
    };
}
