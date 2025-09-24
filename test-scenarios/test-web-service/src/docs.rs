//! API文档生成模块
//! 
//! 使用utoipa自动生成OpenAPI文档和Swagger UI

use utoipa::{OpenApi, ToSchema};
use utoipa_swagger_ui::SwaggerUi;

use crate::models::{
    ApiResponse, PaginatedResponse, PaginationInfo, PaginationParams,
    RuntimeType, TestStatus,
    test_case::{TestCase, CreateTestCaseRequest, UpdateTestCaseRequest, RunTestCaseRequest, TestCaseQuery},
    test_run::{TestRun, CreateTestRunRequest, UpdateTestRunRequest, TestRunQuery, TestRunStats},
};

/// API文档结构定义
#[derive(OpenApi)]
#[openapi(
    paths(
        // 系统健康检查
        crate::health_check,
        
        // 系统信息相关
        crate::api::system::get_info,
        crate::api::system::get_stats,
        crate::api::system::get_version,
        
        // 测试用例管理
        crate::api::test_cases::list_test_cases,
        crate::api::test_cases::create_test_case,
        crate::api::test_cases::get_test_case,
        crate::api::test_cases::update_test_case,
        crate::api::test_cases::delete_test_case,
        crate::api::test_cases::run_test_case,
        
        // 测试运行记录
        crate::api::test_runs::list_test_runs,
        crate::api::test_runs::create_test_run,
        crate::api::test_runs::get_test_run,
        crate::api::test_runs::update_test_run,
        crate::api::test_runs::start_test_run,
        crate::api::test_runs::stop_test_run,
        crate::api::test_runs::get_test_logs,
        crate::api::test_runs::get_test_stats,
        
        // 运行时管理器
        crate::api::runtime_managers::list_managers,
        crate::api::runtime_managers::create_manager,
        crate::api::runtime_managers::get_manager,
        crate::api::runtime_managers::update_manager,
        crate::api::runtime_managers::delete_manager,
        crate::api::runtime_managers::heartbeat,
        crate::api::runtime_managers::test_connection,
        crate::api::runtime_managers::get_platform_info,
        crate::api::runtime_managers::get_setup_guide,
        crate::api::runtime_managers::health_check,
        crate::api::runtime_managers::get_runtime_info,
        crate::api::runtime_managers::get_runtime_resources
    ),
    components(
        schemas(
            ApiResponse<String>,
            ApiResponse<TestCase>,
            ApiResponse<TestRun>,
            ApiResponse<TestRunStats>,
            PaginatedResponse<TestCase>,
            PaginatedResponse<TestRun>,
            PaginationInfo,
            PaginationParams,
            RuntimeType,
            TestStatus,
            TestCase,
            CreateTestCaseRequest,
            UpdateTestCaseRequest,
            RunTestCaseRequest,
            TestCaseQuery,
            TestRun,
            CreateTestRunRequest,
            UpdateTestRunRequest,
            TestRunQuery,
            TestRunStats,
        )
    ),
    tags(
        (name = "system", description = "系统相关API"),
        (name = "test-cases", description = "测试用例管理API"),
        (name = "test-runs", description = "测试运行记录API"),
    ),
    info(
        title = "AIOps测试管理系统API",
        version = "1.0.0",
        description = "AIOps测试管理系统的REST API文档",
        contact(
            name = "AIOps Team",
            email = "aiops@example.com"
        ),
        license(
            name = "MIT",
            url = "https://opensource.org/licenses/MIT"
        )
    ),
    servers(
        (url = "http://localhost:3000", description = "本地开发环境"),
        (url = "https://api.aiops.example.com", description = "生产环境")
    )
)]
pub struct ApiDoc;

/// 创建Swagger UI服务
pub fn create_swagger_ui() -> SwaggerUi {
    SwaggerUi::new("/swagger-ui")
        .url("/api-docs/openapi.json", ApiDoc::openapi())
}

/// 获取OpenAPI JSON文档
pub fn get_openapi_json() -> String {
    ApiDoc::openapi().to_pretty_json().unwrap_or_else(|_| "{}".to_string())
}