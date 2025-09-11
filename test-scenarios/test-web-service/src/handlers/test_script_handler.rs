//! 测试脚本API处理器
//! 
//! 提供测试脚本的CRUD操作和执行功能的HTTP接口

use crate::database::Database;
use crate::execution::ScriptExecutor;
use crate::models::test_script::{
    CreateTestScriptRequest, RunTestScriptRequest, ScriptExecutionResult,
    TestScript, UpdateTestScriptRequest,
};
use crate::AppState;
use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;

/// 查询参数
#[derive(Debug, Deserialize)]
pub struct TestScriptQuery {
    /// 测试用例ID过滤
    pub test_case_id: Option<String>,
    /// 脚本语言过滤
    pub language: Option<String>,
    /// 页码
    pub page: Option<i32>,
    /// 每页数量
    pub page_size: Option<i32>,
}

/// 测试脚本响应
#[derive(Debug, Serialize)]
pub struct TestScriptResponse {
    pub scripts: Vec<TestScript>,
    pub total: i64,
    pub page: i32,
    pub page_size: i32,
}

/// 执行结果响应
#[derive(Debug, Serialize)]
pub struct ExecutionResponse {
    pub script_id: String,
    pub execution_result: ScriptExecutionResult,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

/// 批量执行请求
#[derive(Debug, Deserialize)]
pub struct BatchExecutionRequest {
    pub script_ids: Vec<String>,
    pub environment_vars: Option<HashMap<String, String>>,
    pub parallel: Option<bool>,
}

/// 批量执行响应
#[derive(Debug, Serialize)]
pub struct BatchExecutionResponse {
    pub results: Vec<ExecutionResponse>,
    pub total_scripts: usize,
    pub successful_executions: usize,
    pub failed_executions: usize,
    pub total_execution_time_ms: u64,
}

/// 创建测试脚本路由
pub fn create_test_script_routes() -> Router<AppState> {
    Router::new()
        .route("/test-scripts", get(list_test_scripts).post(create_test_script))
        .route("/test-scripts/:id", get(get_test_script).put(update_test_script).delete(delete_test_script))
        .route("/test-scripts/:id/execute", post(execute_test_script))
        .route("/test-scripts/batch-execute", post(batch_execute_test_scripts))
        .route("/test-scripts/languages", get(get_supported_languages))
        .route("/test-scripts/validate", post(validate_test_script))
}

/// 获取测试脚本列表
pub async fn list_test_scripts(
    State(state): State<AppState>,
    Query(query): Query<TestScriptQuery>,
) -> Result<Json<TestScriptResponse>, StatusCode> {
    let page = query.page.unwrap_or(1);
    let limit = query.page_size.unwrap_or(20).min(100); // 最大100条
    let offset = (page - 1) * limit;

    match TestScript::list(
        state.db.pool(),
        query.test_case_id.as_deref(),
        query.language.as_deref(),
        query.page,
        query.page_size,
    ).await {
        Ok(scripts) => {
            let total = scripts.len() as i64;
            Ok(Json(TestScriptResponse {
                 scripts,
                 total,
                 page: query.page.unwrap_or(1),
                 page_size: query.page_size.unwrap_or(20),
             }))
        }
        Err(e) => {
            eprintln!("获取测试脚本列表失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 获取单个测试脚本
pub async fn get_test_script(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<TestScript>, StatusCode> {
    match TestScript::get_by_id(state.db.pool(), &id).await {
        Ok(Some(script)) => Ok(Json(script)),
        Ok(None) => Err(StatusCode::NOT_FOUND),
        Err(e) => {
            eprintln!("获取测试脚本失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 创建测试脚本
pub async fn create_test_script(
    State(state): State<AppState>,
    Json(request): Json<CreateTestScriptRequest>,
) -> Result<Json<TestScript>, StatusCode> {
    // 验证请求数据
    if let Err(e) = validate_create_request(&request) {
        eprintln!("创建测试脚本请求验证失败: {}", e);
        return Err(StatusCode::BAD_REQUEST);
    }

    match TestScript::create(state.db.pool(), request).await {
        Ok(script) => Ok(Json(script)),
        Err(e) => {
            eprintln!("创建测试脚本失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 更新测试脚本
pub async fn update_test_script(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(request): Json<UpdateTestScriptRequest>,
) -> Result<Json<TestScript>, StatusCode> {
    match TestScript::update(state.db.pool(), &id, request).await {
        Ok(script) => Ok(Json(script)),
        Err(e) => {
            eprintln!("更新测试脚本失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 删除测试脚本
pub async fn delete_test_script(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<StatusCode, StatusCode> {
    match TestScript::delete(state.db.pool(), &id).await {
        Ok(()) => Ok(StatusCode::NO_CONTENT),
        Err(e) => {
            eprintln!("删除测试脚本失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 执行测试脚本
pub async fn execute_test_script(
    State(state): State<AppState>,
    Path(id): Path<String>,
    Json(request): Json<RunTestScriptRequest>,
) -> Result<Json<ExecutionResponse>, StatusCode> {
    // 获取测试脚本
    let script = match TestScript::get_by_id(state.db.pool(), &id).await {
        Ok(Some(script)) => script,
        Ok(None) => return Err(StatusCode::NOT_FOUND),
        Err(e) => {
            eprintln!("获取测试脚本失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // 合并环境变量
    let mut script = script;
    if let Some(env_vars) = request.environment_vars {
        let mut merged_env = script.get_environment_vars().unwrap_or_default();
        merged_env.extend(env_vars);
        script.environment_vars = Some(serde_json::to_string(&merged_env).unwrap());
    }

    // 创建执行器并执行脚本
    let executor = match ScriptExecutor::new() {
        Ok(executor) => executor,
        Err(e) => {
            eprintln!("创建脚本执行器失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    let execution_result = match executor.execute_script(&script).await {
        Ok(result) => result,
        Err(e) => {
            eprintln!("执行测试脚本失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    Ok(Json(ExecutionResponse {
        script_id: id,
        execution_result,
        timestamp: chrono::Utc::now(),
    }))
}

/// 批量执行测试脚本
pub async fn batch_execute_test_scripts(
    State(state): State<AppState>,
    Json(request): Json<BatchExecutionRequest>,
) -> Result<Json<BatchExecutionResponse>, StatusCode> {
    let start_time = std::time::Instant::now();
    let mut results = Vec::new();
    let mut successful_executions = 0;
    let mut failed_executions = 0;

    let parallel = request.parallel.unwrap_or(false);

    if parallel {
        // 并行执行
        let mut tasks = Vec::new();
        
        for script_id in &request.script_ids {
            let db_clone = state.db.clone();
            let script_id_clone = script_id.clone();
            let env_vars_clone = request.environment_vars.clone();
            
            let task = tokio::spawn(async move {
                execute_single_script(&db_clone, &script_id_clone, env_vars_clone).await
            });
            
            tasks.push(task);
        }

        // 等待所有任务完成
        for task in tasks {
            match task.await {
                Ok(Ok(execution_response)) => {
                    if execution_response.execution_result.exit_code == 0 {
                        successful_executions += 1;
                    } else {
                        failed_executions += 1;
                    }
                    results.push(execution_response);
                }
                Ok(Err(_)) | Err(_) => {
                    failed_executions += 1;
                }
            }
        }
    } else {
        // 串行执行
        for script_id in &request.script_ids {
            match execute_single_script(&state.db, script_id, request.environment_vars.clone()).await {
                Ok(execution_response) => {
                    if execution_response.execution_result.exit_code == 0 {
                        successful_executions += 1;
                    } else {
                        failed_executions += 1;
                    }
                    results.push(execution_response);
                }
                Err(_) => {
                    failed_executions += 1;
                }
            }
        }
    }

    let total_execution_time = start_time.elapsed();

    Ok(Json(BatchExecutionResponse {
        results,
        total_scripts: request.script_ids.len(),
        successful_executions,
        failed_executions,
        total_execution_time_ms: total_execution_time.as_millis() as u64,
    }))
}

/// 获取支持的编程语言列表
pub async fn get_supported_languages() -> Json<Vec<&'static str>> {
    Json(vec![
        "python",
        "javascript",
        "shell",
        "go",
        "rust",
        "java",
        "docker",
    ])
}

/// 验证测试脚本
pub async fn validate_test_script(
    Json(request): Json<CreateTestScriptRequest>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let validation_result = validate_create_request(&request);
    
    match validation_result {
        Ok(_) => {
            Ok(Json(serde_json::json!({
                "valid": true,
                "message": "测试脚本验证通过"
            })))
        }
        Err(e) => {
            Ok(Json(serde_json::json!({
                "valid": false,
                "message": e
            })))
        }
    }
}

/// 执行单个脚本的辅助函数
async fn execute_single_script(
    db: &Arc<Database>,
    script_id: &str,
    environment_vars: Option<HashMap<String, String>>,
) -> Result<ExecutionResponse, anyhow::Error> {
    // 获取测试脚本
    let mut script = TestScript::get_by_id(db.pool(), script_id).await?
        .ok_or_else(|| anyhow::anyhow!("测试脚本不存在: {}", script_id))?;

    // 合并环境变量
    if let Some(env_vars) = environment_vars {
        let mut merged_env = script.get_environment_vars().unwrap_or_default();
        merged_env.extend(env_vars);
        script.environment_vars = Some(serde_json::to_string(&merged_env)?);
    }

    // 创建执行器并执行脚本
    let executor = ScriptExecutor::new()?;
    let execution_result = executor.execute_script(&script).await?;

    Ok(ExecutionResponse {
        script_id: script_id.to_string(),
        execution_result,
        timestamp: chrono::Utc::now(),
    })
}

/// 验证创建请求
fn validate_create_request(request: &CreateTestScriptRequest) -> Result<(), String> {
    if request.name.trim().is_empty() {
        return Err("脚本名称不能为空".to_string());
    }

    if request.test_case_id.trim().is_empty() {
        return Err("测试用例ID不能为空".to_string());
    }

    if request.script_content.trim().is_empty() {
        return Err("脚本内容不能为空".to_string());
    }

    let supported_languages = vec![
        "python", "javascript", "shell", "go", "rust", "java", "docker"
    ];
    
    let language_str = request.language.to_string().to_lowercase();
    if !supported_languages.contains(&language_str.as_str()) {
        return Err(format!(
            "不支持的编程语言: {}，支持的语言: {}",
            request.language,
            supported_languages.join(", ")
        ));
    }

    // 验证输入参数格式
    if let Some(inputs) = &request.inputs {
        if inputs.is_empty() {
            return Err("输入参数不能为空".to_string());
        }
        for input in inputs {
            if input.name.is_empty() {
                return Err("输入参数名称不能为空".to_string());
            }
        }
    }

    // 验证预期输出格式
    if let Some(outputs) = &request.expected_outputs {
        for output in outputs {
            if output.output_type.is_empty() {
                return Err("预期输出类型不能为空".to_string());
            }
        }
    }

    // 验证环境变量格式
    if let Some(env_vars) = &request.environment_vars {
        for (key, value) in env_vars {
            if key.is_empty() {
                return Err("环境变量名称不能为空".to_string());
            }
        }
    }

    // 验证依赖格式
    if let Some(deps) = &request.dependencies {
        for dep in deps {
            if dep.is_empty() {
                return Err("依赖名称不能为空".to_string());
            }
        }
    }

    // 验证超时时间
    if let Some(timeout) = request.timeout_seconds {
        if timeout <= 0 || timeout > 3600 {
            return Err("超时时间必须在1-3600秒之间".to_string());
        }
    }

    // 验证重试次数
    if let Some(retry) = request.retry_count {
        if retry < 0 || retry > 10 {
            return Err("重试次数必须在0-10次之间".to_string());
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::test_script::CreateTestScriptRequest;
    use crate::models::ScriptLanguage;

    #[test]
    fn test_validate_create_request() {
        let valid_request = CreateTestScriptRequest {
            test_case_id: "test-case-1".to_string(),
            name: "测试脚本".to_string(),
            description: Some("测试描述".to_string()),
            language: ScriptLanguage::Python,
            script_content: "print('Hello, World!')".to_string(),
            inputs: None,
            expected_outputs: None,
            timeout_seconds: Some(30),
            retry_count: Some(1),
            environment_vars: None,
            dependencies: None,
            docker_image: None,
        };

        assert!(validate_create_request(&valid_request).is_ok());
    }
}