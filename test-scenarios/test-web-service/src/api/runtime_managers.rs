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
        tags: query.tags,
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

/// 获取平台信息和环境检测
pub async fn get_platform_info() -> Result<Json<ApiResponse<Value>>, StatusCode> {
    let platform_info = detect_platform_capabilities().await;
    Ok(Json(ApiResponse::success(platform_info)))
}

/// 获取运行时接入指引
pub async fn get_setup_guide(
    Path(runtime_type): Path<String>,
) -> Result<Json<ApiResponse<Value>>, StatusCode> {
    let guide = match runtime_type.as_str() {
        "docker" => get_docker_setup_guide().await,
        "kubernetes" => get_k8s_setup_guide().await,
        "local" => get_local_setup_guide().await,
        _ => return Ok(Json(ApiResponse::error("不支持的运行时类型".to_string()))),
    };
    
    Ok(Json(ApiResponse::success(guide)))
}

/// 运行时健康检查
pub async fn health_check(
    Path(id): Path<Uuid>,
    State(state): State<AppState>,
) -> Result<Json<ApiResponse<Value>>, StatusCode> {
    let manager = match RuntimeManager::get_by_id(state.db.pool(), &id.to_string()).await {
        Ok(Some(manager)) => manager,
        Ok(None) => return Ok(Json(ApiResponse::error("运行时管理器不存在".to_string()))),
        Err(e) => {
            tracing::error!("获取运行时管理器失败: {}", e);
            return Err(StatusCode::INTERNAL_SERVER_ERROR);
        }
    };

    let health_result = perform_health_check(&manager).await;
    Ok(Json(ApiResponse::success(health_result)))
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

/// 检测平台能力
async fn detect_platform_capabilities() -> Value {
    use tokio::process::Command;
    
    let mut capabilities = json!({
        "platform": std::env::consts::OS,
        "arch": std::env::consts::ARCH,
        "runtimes": {}
    });
    
    // 检测Docker
    let docker_available = Command::new("docker")
        .arg("--version")
        .output()
        .await
        .map(|output| output.status.success())
        .unwrap_or(false);
    
    if docker_available {
        let docker_info = Command::new("docker")
            .arg("version")
            .arg("--format")
            .arg("json")
            .output()
            .await
            .ok()
            .and_then(|output| {
                if output.status.success() {
                    serde_json::from_slice(&output.stdout).ok()
                } else {
                    None
                }
            })
            .unwrap_or_else(|| json!({"available": true}));
        
        capabilities["runtimes"]["docker"] = docker_info;
    } else {
        capabilities["runtimes"]["docker"] = json!({"available": false});
    }
    
    // 检测Kubernetes
    let kubectl_available = Command::new("kubectl")
        .arg("version")
        .arg("--client")
        .output()
        .await
        .map(|output| output.status.success())
        .unwrap_or(false);
    
    if kubectl_available {
        let k8s_info = Command::new("kubectl")
            .arg("version")
            .arg("--client")
            .arg("--output=json")
            .output()
            .await
            .ok()
            .and_then(|output| {
                if output.status.success() {
                    serde_json::from_slice(&output.stdout).ok()
                } else {
                    None
                }
            })
            .unwrap_or_else(|| json!({"available": true}));
        
        capabilities["runtimes"]["kubernetes"] = k8s_info;
    } else {
        capabilities["runtimes"]["kubernetes"] = json!({"available": false});
    }
    
    // 检测Python环境
    let python_available = Command::new("python")
        .arg("--version")
        .output()
        .await
        .map(|output| output.status.success())
        .unwrap_or(false);
    
    capabilities["runtimes"]["local"] = json!({
        "available": true,
        "python_available": python_available,
        "cpu_cores": std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1)
    });
    
    capabilities
}

/// 获取Docker设置指引
async fn get_docker_setup_guide() -> Value {
    json!({
        "title": "Docker运行时设置指引",
        "description": "配置Docker运行时环境以执行容器化测试",
        "prerequisites": [
            "Docker Engine 20.10+",
            "Docker Compose (可选)",
            "足够的磁盘空间用于镜像存储"
        ],
        "installation_steps": {
            "windows": [
                "下载并安装Docker Desktop for Windows",
                "启用WSL2后端（推荐）",
                "配置资源限制（内存、CPU）",
                "验证安装：docker --version"
            ],
            "linux": [
                "添加Docker官方GPG密钥",
                "添加Docker仓库到APT源",
                "安装docker-ce docker-ce-cli containerd.io",
                "启动Docker服务：sudo systemctl start docker",
                "添加用户到docker组：sudo usermod -aG docker $USER"
            ],
            "macos": [
                "下载并安装Docker Desktop for Mac",
                "配置资源限制",
                "验证安装：docker --version"
            ]
        },
        "configuration": {
            "endpoint": "unix:///var/run/docker.sock (Linux/Mac) 或 npipe://./pipe/docker_engine (Windows)",
            "registry": "可配置私有镜像仓库",
            "network": "默认使用bridge网络，可创建自定义网络"
        },
        "test_commands": [
            "docker --version",
            "docker info",
            "docker run hello-world"
        ],
        "troubleshooting": {
            "permission_denied": "确保用户在docker组中，或使用sudo",
            "connection_refused": "检查Docker守护进程是否运行",
            "out_of_space": "清理未使用的镜像和容器：docker system prune"
        }
    })
}

/// 获取Kubernetes设置指引
async fn get_k8s_setup_guide() -> Value {
    json!({
        "title": "Kubernetes运行时设置指引",
        "description": "配置Kubernetes集群以执行云原生测试",
        "prerequisites": [
            "kubectl命令行工具",
            "有效的kubeconfig文件",
            "集群访问权限"
        ],
        "installation_steps": {
            "kubectl": [
                "下载kubectl二进制文件",
                "添加到系统PATH",
                "验证安装：kubectl version --client"
            ],
            "kubeconfig": [
                "从集群管理员获取kubeconfig文件",
                "放置在~/.kube/config位置",
                "或设置KUBECONFIG环境变量"
            ]
        },
        "cluster_types": {
            "minikube": "本地开发集群，适合测试",
            "kind": "Docker中的Kubernetes，轻量级",
            "k3s": "轻量级Kubernetes发行版",
            "managed": "云服务商托管集群（EKS、GKE、AKS）"
        },
        "configuration": {
            "context": "使用kubectl config use-context切换集群",
            "namespace": "建议为测试创建专用命名空间",
            "rbac": "确保有足够权限创建Pod、Service等资源"
        },
        "test_commands": [
            "kubectl version",
            "kubectl cluster-info",
            "kubectl get nodes",
            "kubectl get namespaces"
        ],
        "troubleshooting": {
            "connection_refused": "检查kubeconfig和网络连接",
            "forbidden": "检查RBAC权限设置",
            "context_not_found": "使用kubectl config get-contexts查看可用上下文"
        }
    })
}

/// 获取本地运行时设置指引
async fn get_local_setup_guide() -> Value {
    json!({
        "title": "本地运行时设置指引",
        "description": "配置本地环境以执行脚本和程序",
        "prerequisites": [
            "操作系统支持的脚本解释器",
            "必要的运行时环境（Python、Node.js等）",
            "足够的系统资源"
        ],
        "supported_languages": {
            "python": {
                "versions": ["3.8+"],
                "installation": "从python.org下载或使用包管理器",
                "verification": "python --version"
            },
            "nodejs": {
                "versions": ["16+"],
                "installation": "从nodejs.org下载或使用nvm",
                "verification": "node --version"
            },
            "bash": {
                "platforms": ["Linux", "macOS", "Windows (WSL/Git Bash)"],
                "verification": "bash --version"
            },
            "powershell": {
                "platforms": ["Windows", "Linux", "macOS"],
                "verification": "pwsh --version"
            }
        },
        "configuration": {
            "working_directory": "设置测试脚本的工作目录",
            "environment_variables": "配置必要的环境变量",
            "permissions": "确保脚本有执行权限"
        },
        "security_considerations": [
            "避免执行不受信任的脚本",
            "使用受限的用户权限",
            "定期更新运行时环境"
        ],
        "troubleshooting": {
            "command_not_found": "检查程序是否安装并在PATH中",
            "permission_denied": "检查文件执行权限",
            "module_not_found": "安装缺失的依赖包"
        }
    })
}

/// 执行健康检查
async fn perform_health_check(manager: &RuntimeManager) -> Value {
    let start_time = chrono::Utc::now();
    
    let mut health_status = json!({
        "manager_id": manager.id,
        "manager_name": manager.name,
        "runtime_type": manager.runtime_type,
        "timestamp": start_time.to_rfc3339(),
        "checks": {}
    });
    
    // 基础连接检查
    let connection_result = test_runtime_connection(manager).await;
    health_status["checks"]["connection"] = match connection_result {
        Ok(result) => result,
        Err(e) => json!({
            "success": false,
            "message": format!("连接检查失败: {}", e)
        })
    };
    
    // 资源检查
    let resource_result = check_runtime_resources(manager).await;
    health_status["checks"]["resources"] = resource_result;
    
    // 权限检查
    let permission_result = check_runtime_permissions(manager).await;
    health_status["checks"]["permissions"] = permission_result;
    
    // 计算总体健康状态
    let all_checks_passed = health_status["checks"]
        .as_object()
        .unwrap()
        .values()
        .all(|check| check["success"].as_bool().unwrap_or(false));
    
    health_status["overall_status"] = if all_checks_passed {
        json!("healthy")
    } else {
        json!("unhealthy")
    };
    
    let end_time = chrono::Utc::now();
    health_status["duration_ms"] = json!((end_time - start_time).num_milliseconds());
    
    health_status
}

/// 检查运行时资源
async fn check_runtime_resources(manager: &RuntimeManager) -> Value {
    match &manager.runtime_type {
        RuntimeType::Local => check_local_resources().await,
        RuntimeType::Docker => check_docker_resources().await,
        RuntimeType::Kubernetes => check_k8s_resources().await,
    }
}

/// 检查本地资源
async fn check_local_resources() -> Value {
    use sysinfo::{System, Disks};
    
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let disks = Disks::new_with_refreshed_list();
    
    let total_memory = sys.total_memory();
    let available_memory = sys.available_memory();
    let memory_usage = ((total_memory - available_memory) as f64 / total_memory as f64) * 100.0;
    
    let cpu_usage = sys.cpus().iter().map(|cpu| cpu.cpu_usage()).sum::<f32>() / sys.cpus().len() as f32;
    
    let disk_info: Vec<_> = disks.list().iter().map(|disk| {
        json!({
            "name": disk.name().to_string_lossy(),
            "mount_point": disk.mount_point().to_string_lossy(),
            "total_space": disk.total_space(),
            "available_space": disk.available_space(),
            "usage_percent": ((disk.total_space() - disk.available_space()) as f64 / disk.total_space() as f64) * 100.0
        })
    }).collect();
    
    json!({
        "success": true,
        "memory": {
            "total_gb": total_memory as f64 / 1024.0 / 1024.0 / 1024.0,
            "available_gb": available_memory as f64 / 1024.0 / 1024.0 / 1024.0,
            "usage_percent": memory_usage
        },
        "cpu": {
            "cores": sys.cpus().len(),
            "usage_percent": cpu_usage
        },
        "disks": disk_info
    })
}

/// 检查Docker资源
async fn check_docker_resources() -> Value {
    use tokio::process::Command;
    
    let output = Command::new("docker")
        .arg("system")
        .arg("df")
        .arg("--format")
        .arg("json")
        .output()
        .await;
    
    match output {
        Ok(output) if output.status.success() => {
            match serde_json::from_slice::<Value>(&output.stdout) {
                Ok(data) => json!({
                    "success": true,
                    "docker_system": data
                }),
                Err(_) => json!({
                    "success": false,
                    "message": "无法解析Docker系统信息"
                })
            }
        },
        _ => json!({
            "success": false,
            "message": "无法获取Docker系统信息"
        })
    }
}

/// 检查Kubernetes资源
async fn check_k8s_resources() -> Value {
    use tokio::process::Command;
    
    let nodes_output = Command::new("kubectl")
        .arg("top")
        .arg("nodes")
        .arg("--no-headers")
        .output()
        .await;
    
    match nodes_output {
        Ok(output) if output.status.success() => {
            let nodes_info = String::from_utf8_lossy(&output.stdout);
            json!({
                "success": true,
                "nodes_resource_usage": nodes_info.trim()
            })
        },
        _ => json!({
            "success": false,
            "message": "无法获取Kubernetes节点资源信息"
        })
    }
}

/// 检查运行时权限
async fn check_runtime_permissions(manager: &RuntimeManager) -> Value {
    match &manager.runtime_type {
        RuntimeType::Local => check_local_permissions().await,
        RuntimeType::Docker => check_docker_permissions().await,
        RuntimeType::Kubernetes => check_k8s_permissions().await,
    }
}

/// 检查本地权限
async fn check_local_permissions() -> Value {
    use std::fs;
    
    // 检查当前目录的读写权限
    let current_dir = std::env::current_dir().unwrap_or_else(|_| std::path::PathBuf::from("."));
    
    let can_read = fs::metadata(&current_dir).is_ok();
    let can_write = fs::File::create(current_dir.join(".test_write")).is_ok();
    
    if can_write {
        let _ = fs::remove_file(current_dir.join(".test_write"));
    }
    
    json!({
        "success": can_read && can_write,
        "current_directory": current_dir.to_string_lossy(),
        "can_read": can_read,
        "can_write": can_write
    })
}

/// 检查Docker权限
async fn check_docker_permissions() -> Value {
    use tokio::process::Command;
    
    let output = Command::new("docker")
        .arg("ps")
        .output()
        .await;
    
    match output {
        Ok(output) if output.status.success() => json!({
            "success": true,
            "message": "Docker权限正常"
        }),
        Ok(output) => {
            let error_msg = String::from_utf8_lossy(&output.stderr);
            json!({
                "success": false,
                "message": format!("Docker权限不足: {}", error_msg)
            })
        },
        Err(e) => json!({
            "success": false,
            "message": format!("无法检查Docker权限: {}", e)
        })
    }
}

/// 检查Kubernetes权限
async fn check_k8s_permissions() -> Value {
    use tokio::process::Command;
    
    let output = Command::new("kubectl")
        .arg("auth")
        .arg("can-i")
        .arg("create")
        .arg("pods")
        .output()
        .await;
    
    match output {
        Ok(output) if output.status.success() => {
            let can_create_pods = String::from_utf8_lossy(&output.stdout).trim() == "yes";
            json!({
                "success": can_create_pods,
                "can_create_pods": can_create_pods,
                "message": if can_create_pods { "Kubernetes权限正常" } else { "无法创建Pod" }
            })
        },
        _ => json!({
            "success": false,
            "message": "无法检查Kubernetes权限"
        })
    }
}