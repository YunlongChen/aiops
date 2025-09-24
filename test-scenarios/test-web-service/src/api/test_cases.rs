//! 测试用例API处理器
//! 
//! 实现测试用例的CRUD操作和运行功能

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
};
use uuid::Uuid;
use utoipa;
use crate::{
    AppState,
    models::{
        ApiResponse, PaginationParams, PaginatedResponse,
        test_case::{TestCase, CreateTestCaseRequest, UpdateTestCaseRequest, TestCaseQuery, RunTestCaseRequest},
        test_run::{TestRun, CreateTestRunRequest},
        TestStatus, RuntimeType
    }
};

/// 分页获取测试用例列表
#[utoipa::path(
    get,
    path = "/api/v1/test-cases",
    tag = "test-cases",
    params(TestCaseQuery),
    responses(
        (status = 200, description = "Test case list", body = PaginatedResponse<TestCase>),
        (status = 500, description = "Internal server error")
    )
)]
pub async fn list_test_cases(
    Query(params): Query<PaginationParams>,
    Query(query): Query<TestCaseQuery>,
    State(state): State<AppState>,
) -> Result<Json<PaginatedResponse<TestCase>>, StatusCode> {
    match TestCase::list(state.db.pool(), &params, &query).await {
        Ok((data, pagination)) => Ok(Json(PaginatedResponse {
            data,
            pagination,
        })),
        Err(e) => {
            tracing::error!("获取测试用例列表失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 创建新的测试用例
#[utoipa::path(
    post,
    path = "/api/v1/test-cases",
    tag = "test-cases",
    request_body = CreateTestCaseRequest,
    responses(
        (status = 201, description = "Test case created", body = ApiResponse<TestCase>),
        (status = 400, description = "Invalid request"),
        (status = 500, description = "Internal server error")
    )
)]
pub async fn create_test_case(
    State(state): State<AppState>,
    Json(request): Json<CreateTestCaseRequest>,
) -> Result<Json<ApiResponse<TestCase>>, StatusCode> {
    // 验证请求数据
    if let Err(e) = validate_create_request(&request) {
        return Ok(Json(ApiResponse::<TestCase>::error(e)));
    }

    match TestCase::create(state.db.pool(), request).await {
        Ok(test_case) => {
            tracing::info!("创建测试用例成功: {} ({})", test_case.name, test_case.id);
            Ok(Json(ApiResponse::success(test_case)))
        }
        Err(e) => {
            tracing::error!("创建测试用例失败: {}", e);
            match e.to_string().as_str() {
                s if s.contains("UNIQUE constraint failed") => {
                    Ok(Json(ApiResponse::<TestCase>::error("测试用例名称已存在".to_string())))
                }
                _ => Err(StatusCode::INTERNAL_SERVER_ERROR)
            }
        }
    }
}

/// 根据ID获取测试用例详情
#[utoipa::path(
    get,
    path = "/api/v1/test-cases/{id}",
    tag = "test-cases",
    params(
        ("id" = Uuid, Path, description = "Test case ID")
    ),
    responses(
        (status = 200, description = "Test case details", body = ApiResponse<TestCase>),
        (status = 404, description = "Test case not found"),
        (status = 500, description = "Internal server error")
    )
)]
pub async fn get_test_case(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<TestCase>>, StatusCode> {
    match TestCase::get_by_id(state.db.pool(), &id.to_string()).await {
        Ok(Some(test_case)) => Ok(Json(ApiResponse::success(test_case))),
        Ok(None) => Ok(Json(ApiResponse::<TestCase>::error("测试用例不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试用例失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 更新测试用例
#[utoipa::path(
    put,
    path = "/api/v1/test-cases/{id}",
    tag = "test-cases",
    params(
        ("id" = Uuid, Path, description = "Test case ID")
    ),
    request_body = UpdateTestCaseRequest,
    responses(
        (status = 200, description = "Test case updated", body = ApiResponse<TestCase>),
        (status = 404, description = "Test case not found"),
        (status = 400, description = "Invalid request"),
        (status = 500, description = "Internal server error")
    )
)]
pub async fn update_test_case(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
    Json(request): Json<UpdateTestCaseRequest>,
) -> Result<Json<ApiResponse<TestCase>>, StatusCode> {
    // 验证请求数据
    if let Err(e) = validate_update_request(&request) {
        return Ok(Json(ApiResponse::error(e)));
    }

    // 检查测试用例是否存在
    match TestCase::get_by_id(state.db.pool(), &id.to_string()).await {
        Ok(Some(_)) => {},
        Ok(None) => return Ok(Json(ApiResponse::error("测试用例不存在".to_string()))),
        Err(e) => {
            tracing::error!("检查测试用例存在性失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    }

    match TestCase::update(state.db.pool(), &id.to_string(), request).await {
        Ok(test_case) => {
            tracing::info!("更新测试用例成功: {} ({})", test_case.name, test_case.id);
            Ok(Json(ApiResponse::success(test_case)))
        }
        Err(e) => {
            tracing::error!("更新测试用例失败: {}", e);
            match e.to_string().as_str() {
                s if s.contains("UNIQUE constraint failed") => {
                    Ok(Json(ApiResponse::error("测试用例名称已存在".to_string())))
                }
                _ => Err(StatusCode::INTERNAL_SERVER_ERROR)
            }
        }
    }
}

/// 删除测试用例
#[utoipa::path(
    delete,
    path = "/api/v1/test-cases/{id}",
    tag = "test-cases",
    params(
        ("id" = Uuid, Path, description = "Test case ID")
    ),
    responses(
        (status = 200, description = "Test case deleted", body = ApiResponse<String>),
        (status = 404, description = "Test case not found"),
        (status = 500, description = "Internal server error")
    )
)]
pub async fn delete_test_case(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    // 检查是否有正在运行的测试
    match check_running_tests(&state, &id).await {
        Ok(true) => {
            return Ok(Json(ApiResponse::error("无法删除：该测试用例有正在运行的测试".to_string())));
        }
        Ok(false) => {},
        Err(e) => {
            tracing::error!("检查运行中测试失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    }

    match TestCase::delete(state.db.pool(), &id.to_string()).await {
        Ok(()) => {
            tracing::info!("删除测试用例成功: {}", id);
            Ok(Json(ApiResponse::success("测试用例删除成功".to_string())))
        }
        Err(e) => {
            tracing::error!("删除测试用例失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 运行测试用例
#[utoipa::path(
    post,
    path = "/api/v1/test-cases/{id}/run",
    tag = "test-cases",
    params(
        ("id" = Uuid, Path, description = "Test case ID")
    ),
    request_body = RunTestCaseRequest,
    responses(
        (status = 200, description = "Test case run started", body = ApiResponse<TestRun>),
        (status = 404, description = "Test case not found"),
        (status = 400, description = "Invalid request"),
        (status = 500, description = "Internal server error")
    )
)]
pub async fn run_test_case(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
    Json(request): Json<RunTestCaseRequest>,
) -> Result<Json<ApiResponse<TestRun>>, StatusCode> {
    // 检查测试用例是否存在
    let test_case = match TestCase::get_by_id(state.db.pool(), &id.to_string()).await {
        Ok(Some(test_case)) => test_case,
        Ok(None) => return Ok(Json(ApiResponse::error("测试用例不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试用例失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // 检查并发限制
    match check_concurrent_limit(&state).await {
        Ok(false) => {
            return Ok(Json(ApiResponse::error("已达到最大并发测试数量限制".to_string())));
        }
        Ok(true) => {},
        Err(e) => {
            tracing::error!("检查并发限制失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    }

    // 创建测试运行记录
    let create_run_request = CreateTestRunRequest {
        test_case_id: id.to_string(),
        metadata: request.metadata,
    };

    match TestRun::create(state.db.pool(), create_run_request).await {
        Ok(test_run) => {
            tracing::info!("创建测试运行记录成功: {} -> {}", test_case.name, test_run.id);
            
            // 异步启动测试执行
            let state_clone = state.clone();
            let test_run_id = match Uuid::parse_str(&test_run.id) {
                Ok(id) => id,
                Err(e) => {
                    tracing::error!("解析测试运行ID失败: {}", e);
                    return Err(StatusCode::INTERNAL_SERVER_ERROR);
                }
            };
            tokio::spawn(async move {
                if let Err(e) = execute_test_case(state_clone, test_run_id, test_case).await {
                    tracing::error!("执行测试用例失败: {}", e);
                }
            });

            Ok(Json(ApiResponse::success(test_run)))
        }
        Err(e) => {
            tracing::error!("创建测试运行记录失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 验证创建请求
fn validate_create_request(request: &CreateTestCaseRequest) -> Result<(), String> {
    if request.name.trim().is_empty() {
        return Err("测试用例名称不能为空".to_string());
    }
    
    if request.name.len() > 255 {
        return Err("测试用例名称长度不能超过255个字符".to_string());
    }

    if request.script_path.trim().is_empty() {
        return Err("脚本路径不能为空".to_string());
    }

    // 验证运行时类型
    match request.runtime_type {
        RuntimeType::Local | RuntimeType::Docker | RuntimeType::Kubernetes => {},
    }

    // 验证标签
    if let Some(ref tags) = request.tags {
        if tags.len() > 20 {
            return Err("标签数量不能超过20个".to_string());
        }
        for tag in tags {
            if tag.len() > 50 {
                return Err("单个标签长度不能超过50个字符".to_string());
            }
        }
    }

    Ok(())
}

/// 验证更新请求
fn validate_update_request(request: &UpdateTestCaseRequest) -> Result<(), String> {
    if let Some(ref name) = request.name {
        if name.trim().is_empty() {
            return Err("测试用例名称不能为空".to_string());
        }
        if name.len() > 255 {
            return Err("测试用例名称长度不能超过255个字符".to_string());
        }
    }

    if let Some(ref script_path) = request.script_path {
        if script_path.trim().is_empty() {
            return Err("脚本路径不能为空".to_string());
        }
    }

    // 验证标签
    if let Some(ref tags) = request.tags {
        if tags.len() > 20 {
            return Err("标签数量不能超过20个".to_string());
        }
        for tag in tags {
            if tag.len() > 50 {
                return Err("单个标签长度不能超过50个字符".to_string());
            }
        }
    }

    Ok(())
}

/// 检查是否有正在运行的测试
async fn check_running_tests(state: &AppState, test_case_id: &Uuid) -> anyhow::Result<bool> {
    let running_count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM test_runs WHERE test_case_id = ? AND status IN ('pending', 'running')"
    )
    .bind(test_case_id)
    .fetch_one(state.db.pool())
    .await?;

    Ok(running_count > 0)
}

/// 检查并发限制
async fn check_concurrent_limit(state: &AppState) -> anyhow::Result<bool> {
    let running_count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM test_runs WHERE status IN ('pending', 'running')"
    )
    .fetch_one(state.db.pool())
    .await?;

    Ok(running_count < state.config.max_concurrent_tests as i64)
}

/// 执行测试用例
async fn execute_test_case(
    state: AppState,
    test_run_id: Uuid,
    test_case: TestCase,
) -> anyhow::Result<()> {
    // 更新状态为运行中
    TestRun::update_status(state.db.pool(), &test_run_id, TestStatus::Running).await?;
    
    let start_time = chrono::Utc::now();
    
    // 根据运行时类型执行测试
    let runtime_type = test_case.get_runtime_type()?;
    let result = match runtime_type {
        RuntimeType::Local => execute_local_test(&test_case).await,
        RuntimeType::Docker => execute_docker_test(&test_case).await,
        RuntimeType::Kubernetes => execute_k8s_test(&test_case).await,
    };

    let end_time = chrono::Utc::now();
    let duration_ms = (end_time - start_time).num_milliseconds();

    // 更新测试运行结果
    match result {
        Ok((exit_code, stdout, stderr)) => {
            let status = if exit_code == 0 { TestStatus::Success } else { TestStatus::Failed };
            TestRun::update_result(
                state.db.pool(),
                &test_run_id,
                status,
                Some(start_time),
                Some(end_time),
                Some(duration_ms),
                Some(exit_code),
                Some(stdout),
                Some(stderr),
            ).await?;
            
            tracing::info!("测试执行完成: {} -> {} ({}ms)", test_case.name, 
                         if exit_code == 0 { "成功" } else { "失败" }, duration_ms);
        }
        Err(e) => {
            TestRun::update_result(
                state.db.pool(),
                &test_run_id,
                TestStatus::Failed,
                Some(start_time),
                Some(end_time),
                Some(duration_ms),
                Some(-1),
                None,
                Some(format!("执行错误: {}", e)),
            ).await?;
            
            tracing::error!("测试执行失败: {} -> {}", test_case.name, e);
        }
    }

    Ok(())
}

/// 执行本地测试
async fn execute_local_test(test_case: &TestCase) -> anyhow::Result<(i32, String, String)> {
    use tokio::process::Command;
    
    let mut cmd = Command::new("python");
    cmd.arg(&test_case.script_path);
    
    if let Some(ref config_path) = test_case.config_path {
        cmd.arg("--config").arg(config_path);
    }
    
    let output = cmd.output().await?;
    
    Ok((
        output.status.code().unwrap_or(-1),
        String::from_utf8_lossy(&output.stdout).to_string(),
        String::from_utf8_lossy(&output.stderr).to_string(),
    ))
}

/// 执行Docker测试
async fn execute_docker_test(test_case: &TestCase) -> anyhow::Result<(i32, String, String)> {
    // TODO: 实现Docker运行时支持
    tracing::warn!("Docker运行时支持尚未实现: {}", test_case.name);
    Err(anyhow::anyhow!("Docker运行时支持尚未实现"))
}

/// 执行Kubernetes测试
async fn execute_k8s_test(test_case: &TestCase) -> anyhow::Result<(i32, String, String)> {
    // TODO: 实现Kubernetes运行时支持
    tracing::warn!("Kubernetes运行时支持尚未实现: {}", test_case.name);
    Err(anyhow::anyhow!("Kubernetes运行时支持尚未实现"))
}