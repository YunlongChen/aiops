use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use utoipa::ToSchema;
use uuid::Uuid;

/// API响应结构
/// 
/// 标准的API响应格式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ApiResponse<T> {
    /// 是否成功
    pub success: bool,
    /// 响应数据
    pub data: Option<T>,
    /// 错误信息
    pub error: Option<String>,
    /// 响应消息
    pub message: Option<String>,
    /// 响应时间戳
    pub timestamp: DateTime<Utc>,
}

/// 分页响应结构
/// 
/// 用于分页查询的响应格式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct PaginatedResponse<T> {
    /// 数据列表
    pub items: Vec<T>,
    /// 总数量
    pub total: i64,
    /// 当前页码
    pub page: i32,
    /// 每页大小
    pub page_size: i32,
    /// 总页数
    pub total_pages: i32,
}

/// 分页查询参数
/// 
/// 用于分页查询的请求参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct PaginationParams {
    /// 页码（从1开始）
    #[serde(default = "default_page")]
    pub page: i32,
    /// 每页大小
    #[serde(default = "default_page_size")]
    pub page_size: i32,
}

/// 排序参数
/// 
/// 用于排序的请求参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct SortParams {
    /// 排序字段
    pub field: String,
    /// 排序方向
    pub direction: SortDirection,
}

/// 排序方向枚举
/// 
/// 定义排序的方向
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum SortDirection {
    /// 升序
    Asc,
    /// 降序
    Desc,
}

/// 过滤参数
/// 
/// 用于数据过滤的请求参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FilterParams {
    /// 过滤条件
    pub filters: Vec<FilterCondition>,
}

/// 过滤条件
/// 
/// 单个过滤条件
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct FilterCondition {
    /// 字段名
    pub field: String,
    /// 操作符
    pub operator: FilterOperator,
    /// 值
    pub value: serde_json::Value,
}

/// 过滤操作符枚举
/// 
/// 定义过滤操作的类型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum FilterOperator {
    /// 等于
    Eq,
    /// 不等于
    Ne,
    /// 大于
    Gt,
    /// 大于等于
    Gte,
    /// 小于
    Lt,
    /// 小于等于
    Lte,
    /// 包含
    Contains,
    /// 不包含
    NotContains,
    /// 在列表中
    In,
    /// 不在列表中
    NotIn,
}

/// 时间范围参数
/// 
/// 用于时间范围查询的请求参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TimeRangeParams {
    /// 开始时间
    pub start_time: Option<DateTime<Utc>>,
    /// 结束时间
    pub end_time: Option<DateTime<Utc>>,
    /// 时间范围类型（如：1h, 1d, 1w等）
    pub range: Option<String>,
}

/// 健康检查响应
/// 
/// 系统健康状态检查的响应
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct HealthCheckResponse {
    /// 服务状态
    pub status: ServiceStatus,
    /// 版本信息
    pub version: String,
    /// 启动时间
    pub uptime: String,
    /// 数据库连接状态
    pub database: ComponentStatus,
    /// Redis连接状态
    pub redis: ComponentStatus,
    /// IPMI连接状态
    pub ipmi: ComponentStatus,
    /// 检查时间
    pub timestamp: DateTime<Utc>,
}

/// 服务状态枚举
/// 
/// 定义服务的运行状态
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum ServiceStatus {
    /// 健康
    Healthy,
    /// 降级
    Degraded,
    /// 不健康
    Unhealthy,
}

/// 组件状态
/// 
/// 单个组件的状态信息
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ComponentStatus {
    /// 状态
    pub status: ServiceStatus,
    /// 响应时间（毫秒）
    pub response_time_ms: Option<i64>,
    /// 错误信息
    pub error: Option<String>,
}

/// 批量操作请求
/// 
/// 用于批量操作的请求结构
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct BatchRequest<T> {
    /// 操作类型
    pub operation: BatchOperation,
    /// 数据列表
    pub items: Vec<T>,
}

/// 批量操作类型枚举
/// 
/// 定义批量操作的类型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum BatchOperation {
    /// 创建
    Create,
    /// 更新
    Update,
    /// 删除
    Delete,
}

/// 批量操作响应
/// 
/// 批量操作的响应结果
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct BatchResponse {
    /// 成功数量
    pub success_count: i32,
    /// 失败数量
    pub failure_count: i32,
    /// 错误详情
    pub errors: Vec<BatchError>,
}

/// 批量操作错误
/// 
/// 批量操作中的单个错误
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct BatchError {
    /// 索引
    pub index: i32,
    /// 错误信息
    pub error: String,
}

/// 导出请求
/// 
/// 数据导出的请求参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct ExportRequest {
    /// 导出格式
    pub format: ExportFormat,
    /// 过滤条件
    pub filters: Option<FilterParams>,
    /// 字段列表
    pub fields: Option<Vec<String>>,
    /// 时间范围
    pub time_range: Option<TimeRange>,
}

/// 导出格式枚举
/// 
/// 定义支持的导出格式
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum ExportFormat {
    /// CSV格式
    Csv,
    /// JSON格式
    Json,
    /// Excel格式
    Excel,
}

/// 时间范围
/// 
/// 定义时间查询范围
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct TimeRange {
    /// 开始时间
    pub start: DateTime<Utc>,
    /// 结束时间
    pub end: DateTime<Utc>,
}

/// 统计查询请求
/// 
/// 用于统计数据查询的请求参数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct StatisticsRequest {
    /// 统计类型
    pub stat_type: StatisticsType,
    /// 时间范围
    pub time_range: TimeRange,
    /// 分组字段
    pub group_by: Option<Vec<String>>,
    /// 聚合函数
    pub aggregations: Vec<AggregationFunction>,
}

/// 统计类型枚举
/// 
/// 定义统计数据的类型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum StatisticsType {
    /// 风扇统计
    Fan,
    /// 温度统计
    Temperature,
    /// 警报统计
    Alert,
    /// 系统统计
    System,
}

/// 聚合函数
/// 
/// 定义数据聚合的函数
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub struct AggregationFunction {
    /// 字段名
    pub field: String,
    /// 函数类型
    pub function: AggregationType,
}

/// 聚合类型枚举
/// 
/// 定义聚合函数的类型
#[derive(Debug, Clone, Serialize, Deserialize, ToSchema)]
pub enum AggregationType {
    /// 计数
    Count,
    /// 求和
    Sum,
    /// 平均值
    Avg,
    /// 最小值
    Min,
    /// 最大值
    Max,
}

// 默认值函数
fn default_page() -> i32 {
    1
}

fn default_page_size() -> i32 {
    20
}

impl<T> ApiResponse<T> {
    /// 创建成功响应
    /// 
    /// # 参数
    /// * `data` - 响应数据
    pub fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            message: None,
            timestamp: Utc::now(),
        }
    }

    /// 创建成功响应（带消息）
    /// 
    /// # 参数
    /// * `data` - 响应数据
    /// * `message` - 响应消息
    pub fn success_with_message(data: T, message: String) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            message: Some(message),
            timestamp: Utc::now(),
        }
    }

    /// 创建错误响应
    /// 
    /// # 参数
    /// * `error` - 错误信息
    pub fn error(error: String) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(error),
            message: None,
            timestamp: Utc::now(),
        }
    }

        /// 创建错误响应
    /// 
    /// # 参数
    /// * `error` - 错误信息
    pub fn error(error: &str) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(error.to_string()),
            message: None,
            timestamp: Utc::now(),
        }
    }
}

impl<T> PaginatedResponse<T> {
    /// 创建分页响应
    /// 
    /// # 参数
    /// * `items` - 数据列表
    /// * `total` - 总数量
    /// * `page` - 当前页码
    /// * `page_size` - 每页大小
    pub fn new(items: Vec<T>, total: i64, page: i32, page_size: i32) -> Self {
        let total_pages = ((total as f64) / (page_size as f64)).ceil() as i32;
        Self {
            items,
            total,
            page,
            page_size,
            total_pages,
        }
    }
}

impl Default for PaginationParams {
    fn default() -> Self {
        Self {
            page: default_page(),
            page_size: default_page_size(),
        }
    }
}

impl ComponentStatus {
    /// 创建健康状态
    /// 
    /// # 参数
    /// * `response_time_ms` - 响应时间
    pub fn healthy(response_time_ms: i64) -> Self {
        Self {
            status: ServiceStatus::Healthy,
            response_time_ms: Some(response_time_ms),
            error: None,
        }
    }

    /// 创建不健康状态
    /// 
    /// # 参数
    /// * `error` - 错误信息
    pub fn unhealthy(error: String) -> Self {
        Self {
            status: ServiceStatus::Unhealthy,
            response_time_ms: None,
            error: Some(error),
        }
    }
}