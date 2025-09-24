//! 测试运行API处理器
//! 
//! 实现测试运行记录的管理和监控功能

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
};
use uuid::Uuid;
use serde_json::{json, Value};
use utoipa;
use crate::{
    AppState,
    models::{
        ApiResponse, PaginationParams, PaginatedResponse,
        test_run::{TestRun, CreateTestRunRequest, UpdateTestRunRequest, TestRunQuery, TestRunStats},
        TestStatus
    }
};

/// 分页获取测试运行记录列表
#[utoipa::path(
    get,
    path = "/test-runs",
    tag = "test-runs",
    params(TestRunQuery),
    responses(
        (status = 200, description = "Test run list", body = PaginatedResponse<TestRun>),
        (status = 500, description = "Internal server error")
    )
)]
pub async fn list_test_runs(
    Query(params): Query<PaginationParams>,
    Query(query): Query<TestRunQuery>,
    State(state): State<AppState>,
) -> Result<Json<PaginatedResponse<TestRun>>, StatusCode> {
    match TestRun::list(state.db.pool(), &params, &query).await {
        Ok((test_runs, pagination)) => {
            let response = PaginatedResponse {
                data: test_runs,
                pagination,
            };
            Ok(Json(response))
        },
        Err(e) => {
            tracing::error!("获取测试运行记录列表失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 创建新的测试运行记录
#[utoipa::path(
    post,
    path = "/test-runs",
    tag = "test-runs",
    request_body = CreateTestRunRequest,
    responses(
        (status = 200, description = "Created successfully", body = ApiResponse<TestRun>),
        (status = 400, description = "Invalid request parameters", body = ApiResponse<String>)
    )
)]
pub async fn create_test_run(
    State(state): State<AppState>,
    Json(request): Json<CreateTestRunRequest>,
) -> Result<Json<ApiResponse<TestRun>>, StatusCode> {
    // 验证测试用例是否存在
    match crate::models::test_case::TestCase::get_by_id(state.db.pool(), &request.test_case_id).await {
        Ok(Some(_)) => {},
        Ok(None) => return Ok(Json(ApiResponse::error("测试用例不存在".to_string()))),
        Err(e) => {
            tracing::error!("验证测试用例存在性失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    }

    match TestRun::create(state.db.pool(), request).await {
        Ok(test_run) => {
            tracing::info!("创建测试运行记录成功: {}", test_run.id);
            Ok(Json(ApiResponse::success(test_run)))
        }
        Err(e) => {
            tracing::error!("创建测试运行记录失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 根据ID获取测试运行详情
#[utoipa::path(
    get,
    path = "/test-runs/{id}",
    tag = "test-runs",
    params(
        ("id" = Uuid, Path, description = "Test run record ID")
    ),
    responses(
        (status = 200, description = "Test run details", body = ApiResponse<TestRun>),
        (status = 404, description = "Test run record not found", body = ApiResponse<String>)
    )
)]
pub async fn get_test_run(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<TestRun>>, StatusCode> {
    match TestRun::get_by_id(state.db.pool(), &id).await {
        Ok(Some(test_run)) => Ok(Json(ApiResponse::success(test_run))),
        Ok(None) => Ok(Json(ApiResponse::error("测试运行记录不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试运行记录失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 更新测试运行记录
#[utoipa::path(
    put,
    path = "/test-runs/{id}",
    tag = "test-runs",
    params(
        ("id" = Uuid, Path, description = "Test run record ID")
    ),
    request_body = UpdateTestRunRequest,
    responses(
        (status = 200, description = "Updated successfully", body = ApiResponse<TestRun>),
        (status = 404, description = "Test run record not found", body = ApiResponse<String>),
        (status = 400, description = "Invalid request parameters", body = ApiResponse<String>)
    )
)]
pub async fn update_test_run(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
    Json(request): Json<UpdateTestRunRequest>,
) -> Result<Json<ApiResponse<TestRun>>, StatusCode> {
    // 检查测试运行记录是否存在
    match TestRun::get_by_id(state.db.pool(), &id).await {
        Ok(Some(_)) => {},
        Ok(None) => return Ok(Json(ApiResponse::error("测试运行记录不存在".to_string()))),
        Err(e) => {
            tracing::error!("检查测试运行记录存在性失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    }

    match TestRun::update(state.db.pool(), &id.to_string(), request).await {
        Ok(test_run) => {
            tracing::info!("更新测试运行记录成功: {}", test_run.id);
            Ok(Json(ApiResponse::success(test_run)))
        }
        Err(e) => {
            tracing::error!("更新测试运行记录失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 开始测试运行
#[utoipa::path(
    post,
    path = "/test-runs/{id}/start",
    tag = "test-runs",
    params(
        ("id" = Uuid, Path, description = "Test run record ID")
    ),
    responses(
        (status = 200, description = "Started successfully", body = ApiResponse<String>),
        (status = 400, description = "Test is already running or status does not allow start", body = ApiResponse<String>),
        (status = 404, description = "Test run record not found", body = ApiResponse<String>)
    )
)]
pub async fn start_test_run(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    // 获取测试运行记录
    let test_run = match TestRun::get_by_id(state.db.pool(), &id).await {
        Ok(Some(test_run)) => test_run,
        Ok(None) => return Ok(Json(ApiResponse::error("测试运行记录不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试运行记录失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // 检查状态是否允许启动
    if test_run.get_test_status().unwrap_or(TestStatus::Failed) != TestStatus::Pending {
        return Ok(Json(ApiResponse::error(format!(
            "测试运行状态为 {:?}，无法启动", test_run.status
        ))));
    }

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

    // 获取测试用例信息
    let test_case = match crate::models::test_case::TestCase::get_by_id(
        state.db.pool(), 
        &test_run.test_case_id
    ).await {
        Ok(Some(test_case)) => test_case,
        Ok(None) => return Ok(Json(ApiResponse::error("关联的测试用例不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试用例失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // 异步启动测试执行
    let state_clone = state.clone();
    tokio::spawn(async move {
        if let Err(e) = execute_test_run(state_clone, id, test_case).await {
            tracing::error!("执行测试运行失败: {}", e);
        }
    });

    tracing::info!("测试运行启动成功: {}", id);
    Ok(Json(ApiResponse::success("测试运行已启动".to_string())))
}

/// 停止测试运行
#[utoipa::path(
    post,
    path = "/test-runs/{id}/stop",
    tag = "test-runs",
    params(
        ("id" = Uuid, Path, description = "Test run record ID")
    ),
    responses(
        (status = 200, description = "Stopped successfully", body = ApiResponse<String>),
        (status = 400, description = "Test is not running or status does not allow stop", body = ApiResponse<String>),
        (status = 404, description = "Test run record not found", body = ApiResponse<String>)
    )
)]
pub async fn stop_test_run(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    // 获取测试运行记录
    let test_run = match TestRun::get_by_id(state.db.pool(), &id).await {
        Ok(Some(test_run)) => test_run,
        Ok(None) => return Ok(Json(ApiResponse::error("测试运行记录不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试运行记录失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // 检查状态是否允许停止
    let status = match test_run.get_test_status() {
        Ok(status) => status,
        Err(_) => return Err(StatusCode::INTERNAL_SERVER_ERROR),
    };
    match status {
        TestStatus::Running | TestStatus::Pending => {},
        _ => {
            return Ok(Json(ApiResponse::error(format!(
                "测试运行状态为 {:?}，无法停止", status
            ))));
        }
    }

    // 更新状态为已取消
    match TestRun::update_status(state.db.pool(), &id, TestStatus::Cancelled).await {
        Ok(_) => {
            tracing::info!("测试运行停止成功: {}", id);
            Ok(Json(ApiResponse::success("测试运行已停止".to_string())))
        }
        Err(e) => {
            tracing::error!("停止测试运行失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 获取测试运行日志
#[utoipa::path(
    get,
    path = "/test-runs/{id}/logs",
    tag = "test-runs",
    params(
        ("id" = Uuid, Path, description = "Test run record ID")
    ),
    responses(
        (status = 200, description = "Test run logs", body = ApiResponse<String>),
        (status = 404, description = "Test run record not found", body = ApiResponse<String>)
    )
)]
pub async fn get_test_logs(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<Value>>, StatusCode> {
    match TestRun::get_by_id(state.db.pool(), &id).await {
        Ok(Some(test_run)) => {
            let logs = json!({
                "test_run_id": test_run.id,
                "status": test_run.status,
                "start_time": test_run.start_time,
                "end_time": test_run.end_time,
                "duration_ms": test_run.duration_ms,
                "exit_code": test_run.exit_code,
                "stdout": test_run.stdout.unwrap_or_default(),
                "stderr": test_run.stderr.unwrap_or_default(),
                "metadata": test_run.metadata
            });
            Ok(Json(ApiResponse::<Value>::success(logs)))
        }
        Ok(None) => Ok(Json(ApiResponse::<Value>::error("测试运行记录不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试运行日志失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 获取测试运行统计信息
#[utoipa::path(
    get,
    path = "/test-runs/stats",
    tag = "test-runs",
    responses(
        (status = 200, description = "Test run statistics", body = ApiResponse<TestRunStats>)
    )
)]
pub async fn get_test_stats(
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<TestRunStats>>, StatusCode> {
    match TestRun::get_stats(state.db.pool()).await {
        Ok(stats) => Ok(Json(ApiResponse::success(stats))),
        Err(e) => {
            tracing::error!("获取测试运行统计信息失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
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

/// 执行测试运行
async fn execute_test_run(
    state: AppState,
    test_run_id: Uuid,
    test_case: crate::models::test_case::TestCase,
) -> anyhow::Result<()> {
    use crate::models::{RuntimeType, TestStatus};
    
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
            
            tracing::info!("测试运行完成: {} -> {} ({}ms)", test_run_id, 
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
            
            tracing::error!("测试运行失败: {} -> {}", test_run_id, e);
        }
    }

    Ok(())
}

/// 执行本地测试
async fn execute_local_test(
    test_case: &crate::models::test_case::TestCase
) -> anyhow::Result<(i32, String, String)> {
    use tokio::process::Command;
    
    let mut cmd = Command::new("python");
    cmd.arg(&test_case.script_path);
    
    if let Some(ref config_path) = test_case.config_path {
        cmd.arg("--config").arg(config_path);
    }
    
    // 设置超时时间（30分钟）
    let timeout = std::time::Duration::from_secs(30 * 60);
    
    match tokio::time::timeout(timeout, cmd.output()).await {
        Ok(Ok(output)) => {
            Ok((
                output.status.code().unwrap_or(-1),
                String::from_utf8_lossy(&output.stdout).to_string(),
                String::from_utf8_lossy(&output.stderr).to_string(),
            ))
        }
        Ok(Err(e)) => Err(anyhow::anyhow!("命令执行失败: {}", e)),
        Err(_) => Err(anyhow::anyhow!("测试执行超时")),
    }
}

/// 执行Docker测试
async fn execute_docker_test(
    test_case: &crate::models::test_case::TestCase
) -> anyhow::Result<(i32, String, String)> {
    // TODO: 实现Docker运行时支持
    tracing::warn!("Docker运行时支持尚未实现: {}", test_case.name);
    Err(anyhow::anyhow!("Docker运行时支持尚未实现"))
}

/// 执行Kubernetes测试
async fn execute_k8s_test(
    test_case: &crate::models::test_case::TestCase
) -> anyhow::Result<(i32, String, String)> {
    // TODO: 实现Kubernetes运行时支持
    tracing::warn!("Kubernetes运行时支持尚未实现: {}", test_case.name);
    Err(anyhow::anyhow!("Kubernetes运行时支持尚未实现"))
}

/// 删除测试运行记录
#[utoipa::path(
    delete,
    path = "/test-runs/{id}",
    tag = "test-runs",
    params(
        ("id" = Uuid, Path, description = "Test run record ID")
    ),
    responses(
        (status = 200, description = "Deleted successfully", body = ApiResponse<String>),
        (status = 404, description = "Test run record not found", body = ApiResponse<String>)
    )
)]
pub async fn delete_test_run(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    match TestRun::get_by_id(state.db.pool(), &id).await {
        Ok(Some(test_run)) => {
            let logs = json!({
                "test_run_id": test_run.id,
                "status": test_run.status,
                "start_time": test_run.start_time,
                "end_time": test_run.end_time,
                "duration_ms": test_run.duration_ms,
                "exit_code": test_run.exit_code,
                "stdout": test_run.stdout.unwrap_or_default(),
                "stderr": test_run.stderr.unwrap_or_default(),
                "metadata": test_run.metadata
            });
            Ok(Json(ApiResponse::success(logs.to_string())))
        }
        Ok(None) => Ok(Json(ApiResponse::error("测试运行记录不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取测试运行日志失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}