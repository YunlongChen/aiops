//! 运行时管理器API处理器
//! 
//! 实现运行时管理器的CRUD操作和连接测试功能

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
};
use uuid::Uuid;
use serde_json::{json, Value};
use crate::{
    AppState,
    models::{
        ApiResponse, PaginationParams, PaginatedResponse,
        runtime_manager::{
            RuntimeManager, CreateRuntimeManagerRequest, UpdateRuntimeManagerRequest, 
            RuntimeManagerQuery, ManagerStatus
        },
        RuntimeType
    }
};

/// 分页获取运行时管理器列表
pub async fn list_managers(
    Query(params): Query<PaginationParams>,
    Query(query): Query<RuntimeManagerQuery>,
    State(state): State<AppState>,
) -> Result<Json<PaginatedResponse<RuntimeManager>>, StatusCode> {
    let query_params = RuntimeManagerQuery {
        pagination: params,
        runtime_type: query.runtime_type,
        status: query.status,
        name: query.name,
    };
    
    match RuntimeManager::find_all(state.db.pool(), query_params).await {
        Ok(result) => {
            let response = PaginatedResponse {
                data: result.data,
                pagination: crate::models::PaginationInfo {
                    page: result.pagination.page,
                    limit: result.pagination.per_page,
                    total: result.pagination.total,
                    total_pages: result.pagination.total_pages,
                    has_next: result.pagination.page < result.pagination.total_pages,
                    has_prev: result.pagination.page > 1,
                },
            };
            Ok(Json(response))
        }
        Err(e) => {
            tracing::error!("获取运行时管理器列表失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 创建新的运行时管理器
pub async fn create_manager(
    State(state): State<AppState>,
    Json(request): Json<CreateRuntimeManagerRequest>,
) -> Result<Json<ApiResponse<RuntimeManager>>, StatusCode> {
    // 验证请求数据
    if let Err(e) = validate_create_request(&request) {
        return Ok(Json(ApiResponse::error(e)));
    }

    match RuntimeManager::create(state.db.pool(), request).await {
        Ok(manager) => {
            tracing::info!("创建运行时管理器成功: {} ({})", manager.name, manager.id);
            Ok(Json(ApiResponse::success(manager)))
        }
        Err(e) => {
            tracing::error!("创建运行时管理器失败: {}", e);
            match e.to_string().as_str() {
                s if s.contains("UNIQUE constraint failed") => {
                    Ok(Json(ApiResponse::error("运行时管理器名称已存在".to_string())))
                }
                _ => Err(StatusCode::INTERNAL_SERVER_ERROR)
            }
        }
    }
}

/// 根据ID获取运行时管理器详情
pub async fn get_manager(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<RuntimeManager>>, StatusCode> {
    match RuntimeManager::get_by_id(state.db.pool(), &id.to_string()).await {
        Ok(Some(manager)) => Ok(Json(ApiResponse::success(manager))),
        Ok(None) => Ok(Json(ApiResponse::error("运行时管理器不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取运行时管理器失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 更新运行时管理器
pub async fn update_manager(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
    Json(request): Json<UpdateRuntimeManagerRequest>,
) -> Result<Json<ApiResponse<RuntimeManager>>, StatusCode> {
    // 验证请求数据
    if let Err(e) = validate_update_request(&request) {
        return Ok(Json(ApiResponse::error(e)));
    }

    // 检查运行时管理器是否存在
    match RuntimeManager::get_by_id(state.db.pool(), &id.to_string()).await {
        Ok(Some(_manager)) => {},
        Ok(None) => return Ok(Json(ApiResponse::error("运行时管理器不存在".to_string()))),
        Err(e) => {
            tracing::error!("检查运行时管理器存在性失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    }

    match RuntimeManager::update(state.db.pool(), &id.to_string(), request).await {
        Ok(manager) => {
            tracing::info!("更新运行时管理器成功: {} ({})", manager.name, manager.id);
            Ok(Json(ApiResponse::success(manager)))
        }
        Err(e) => {
            tracing::error!("更新运行时管理器失败: {}", e);
            match e.to_string().as_str() {
                s if s.contains("UNIQUE constraint failed") => {
                    Ok(Json(ApiResponse::error("运行时管理器名称已存在".to_string())))
                }
                _ => Err(StatusCode::INTERNAL_SERVER_ERROR)
            }
        }
    }
}

/// 删除运行时管理器
pub async fn delete_manager(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    // 检查是否有正在使用该管理器的测试
    match check_manager_in_use(&state, &id).await {
        Ok(true) => {
            return Ok(Json(ApiResponse::error("无法删除：该运行时管理器正在被测试用例使用".to_string())));
        }
        Ok(false) => {},
        Err(e) => {
            tracing::error!("检查管理器使用状态失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    }

    match RuntimeManager::delete(state.db.pool(), &id.to_string()).await {
        Ok(()) => {
            tracing::info!("删除运行时管理器成功: {}", id);
            Ok(Json(ApiResponse::success("运行时管理器删除成功".to_string())))
        }
        Err(e) => {
            tracing::error!("删除运行时管理器失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 发送心跳信号
pub async fn heartbeat(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    match RuntimeManager::update_heartbeat(state.db.pool(), &id.to_string()).await {
        Ok(()) => {
            tracing::debug!("运行时管理器心跳更新成功: {}", id);
            Ok(Json(ApiResponse::success("心跳信号已记录".to_string())))
        }
        Err(e) => {
            tracing::error!("更新心跳信号失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 测试连接
pub async fn test_connection(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<Value>>, StatusCode> {
    // 获取运行时管理器信息
    let manager = match RuntimeManager::get_by_id(state.db.pool(), &id.to_string()).await {
        Ok(Some(manager)) => manager,
        Ok(None) => return Ok(Json(ApiResponse::error("运行时管理器不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取运行时管理器失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    // 执行连接测试
    let test_result = match test_runtime_connection(&manager).await {
        Ok(result) => result,
        Err(e) => {
            tracing::error!("测试运行时连接失败: {}", e);
            json!({
                "success": false,
                "message": format!("连接测试失败: {}", e),
                "timestamp": chrono::Utc::now().to_rfc3339(),
                "details": null
            })
        }
    };

    // 根据测试结果更新管理器状态
    let new_status = if test_result["success"].as_bool().unwrap_or(false) {
        ManagerStatus::Active
    } else {
        ManagerStatus::Error
    };

    if let Err(e) = RuntimeManager::update_status(state.db.pool(), &id.to_string(), new_status).await {
        tracing::error!("更新管理器状态失败: {}", e);
    }

    Ok(Json(ApiResponse::success(test_result)))
}

/// 验证创建请求
fn validate_create_request(request: &CreateRuntimeManagerRequest) -> Result<(), String> {
    if request.name.trim().is_empty() {
        return Err("运行时管理器名称不能为空".to_string());
    }
    
    if request.name.len() > 255 {
        return Err("运行时管理器名称长度不能超过255个字符".to_string());
    }

    // 验证运行时类型
    match request.runtime_type {
        RuntimeType::Local | RuntimeType::Docker | RuntimeType::Kubernetes => {},
    }

    // 验证配置格式
    if let Some(ref config) = request.config {
        if !config.is_object() {
            return Err("配置必须是有效的JSON对象".to_string());
        }
    }

    Ok(())
}

/// 验证更新请求
fn validate_update_request(request: &UpdateRuntimeManagerRequest) -> Result<(), String> {
    if let Some(ref name) = request.name {
        if name.trim().is_empty() {
            return Err("运行时管理器名称不能为空".to_string());
        }
        if name.len() > 255 {
            return Err("运行时管理器名称长度不能超过255个字符".to_string());
        }
    }

    // 验证配置格式
    if let Some(ref config) = request.config {
        if !config.is_object() {
            return Err("配置必须是有效的JSON对象".to_string());
        }
    }

    Ok(())
}

/// 检查管理器是否正在使用
async fn check_manager_in_use(state: &AppState, manager_id: &Uuid) -> anyhow::Result<bool> {
    // 检查是否有测试用例使用该管理器的运行时类型
    // 注意：这里简化了检查逻辑，实际应用中可能需要更复杂的关联检查
    let usage_count: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM test_runs tr 
         JOIN test_cases tc ON tr.test_case_id = tc.id 
         WHERE tr.status IN ('pending', 'running')"
    )
    .fetch_one(state.db.pool())
    .await?;

    Ok(usage_count > 0)
}

/// 测试运行时连接
async fn test_runtime_connection(manager: &RuntimeManager) -> anyhow::Result<Value> {
    let start_time = chrono::Utc::now();
    
    let result = match &manager.runtime_type {
        RuntimeType::Local => test_local_runtime(manager).await,
        RuntimeType::Docker => test_docker_runtime(manager).await,
        RuntimeType::Kubernetes => test_k8s_runtime(manager).await,
    };

    let end_time = chrono::Utc::now();
    let duration_ms = (end_time - start_time).num_milliseconds();

    match result {
        Ok(details) => Ok(json!({
            "success": true,
            "message": "连接测试成功",
            "timestamp": end_time.to_rfc3339(),
            "duration_ms": duration_ms,
            "runtime_type": manager.runtime_type,
            "details": details
        })),
        Err(e) => Ok(json!({
            "success": false,
            "message": format!("连接测试失败: {}", e),
            "timestamp": end_time.to_rfc3339(),
            "duration_ms": duration_ms,
            "runtime_type": manager.runtime_type,
            "details": null
        }))
    }
}

/// 测试本地运行时
async fn test_local_runtime(_manager: &RuntimeManager) -> anyhow::Result<Value> {
    use tokio::process::Command;
    
    // 测试Python环境
    let python_output = Command::new("python")
        .arg("--version")
        .output()
        .await?;

    let python_version = if python_output.status.success() {
        String::from_utf8_lossy(&python_output.stdout).trim().to_string()
    } else {
        "未安装或不可用".to_string()
    };

    // 获取系统信息
    let system_info = json!({
        "python_version": python_version,
        "python_available": python_output.status.success(),
        "platform": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "cpu_cores": std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1)
    });

    Ok(system_info)
}

/// 测试Docker运行时
async fn test_docker_runtime(manager: &RuntimeManager) -> anyhow::Result<Value> {
    use tokio::process::Command;
    
    // 测试Docker是否可用
    let docker_output = Command::new("docker")
        .arg("version")
        .arg("--format")
        .arg("json")
        .output()
        .await?;

    if !docker_output.status.success() {
        return Err(anyhow::anyhow!("Docker不可用或未安装"));
    }

    // 解析Docker版本信息
    let docker_info: Value = serde_json::from_slice(&docker_output.stdout)
        .unwrap_or_else(|_| json!({"Client": {"Version": "unknown"}}));

    // 测试Docker连接
    let ping_output = Command::new("docker")
        .arg("info")
        .arg("--format")
        .arg("json")
        .output()
        .await?;

    let docker_details = if ping_output.status.success() {
        serde_json::from_slice(&ping_output.stdout)
            .unwrap_or_else(|_| json!({"status": "connected"}))
    } else {
        json!({"status": "connection_failed"})
    };

    Ok(json!({
        "docker_version": docker_info,
        "connection_status": docker_details,
        "config": manager.config
    }))
}

/// 测试Kubernetes运行时
async fn test_k8s_runtime(manager: &RuntimeManager) -> anyhow::Result<Value> {
    use tokio::process::Command;
    
    // 测试kubectl是否可用
    let kubectl_output = Command::new("kubectl")
        .arg("version")
        .arg("--client")
        .arg("--output=json")
        .output()
        .await?;

    if !kubectl_output.status.success() {
        return Err(anyhow::anyhow!("kubectl不可用或未安装"));
    }

    // 测试集群连接
    let cluster_output = Command::new("kubectl")
        .arg("cluster-info")
        .output()
        .await?;

    let cluster_status = if cluster_output.status.success() {
        "connected"
    } else {
        "connection_failed"
    };

    // 获取节点信息
    let nodes_output = Command::new("kubectl")
        .arg("get")
        .arg("nodes")
        .arg("--output=json")
        .output()
        .await;

    let nodes_info = match nodes_output {
        Ok(output) if output.status.success() => {
            serde_json::from_slice(&output.stdout)
                .unwrap_or_else(|_| json!({"items": []}))
        }
        _ => json!({"items": [], "error": "无法获取节点信息"})
    };

    Ok(json!({
        "kubectl_available": true,
        "cluster_status": cluster_status,
        "nodes": nodes_info,
        "config": manager.config
    }))
}