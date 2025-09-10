//! 系统API处理器
//! 
//! 提供系统信息、统计数据和API文档

use axum::{
    extract::State,
    http::StatusCode,
    response::Json,
};
use serde_json::{json, Value};
use crate::{AppState, models::ApiResponse};

/// API文档端点
pub async fn api_docs() -> Result<Json<Value>, StatusCode> {
    let docs = json!({
        "title": "AIOps测试管理API",
        "version": "v1",
        "description": "基于Rust Axum的AIOps测试用例管理和运行服务API",
        "base_url": "/api/v1",
        "endpoints": {
            "system": {
                "GET /docs": "获取API文档",
                "GET /stats": "获取系统统计信息",
                "GET /version": "获取版本信息"
            },
            "test_cases": {
                "GET /test-cases": "分页获取测试用例列表",
                "POST /test-cases": "创建新的测试用例",
                "GET /test-cases/{id}": "根据ID获取测试用例详情",
                "PUT /test-cases/{id}": "更新测试用例",
                "DELETE /test-cases/{id}": "删除测试用例",
                "POST /test-cases/{id}/run": "运行指定的测试用例"
            },
            "test_runs": {
                "GET /test-runs": "分页获取测试运行记录",
                "POST /test-runs": "创建新的测试运行记录",
                "GET /test-runs/{id}": "根据ID获取测试运行详情",
                "PUT /test-runs/{id}": "更新测试运行记录",
                "POST /test-runs/{id}/start": "开始测试运行",
                "POST /test-runs/{id}/stop": "停止测试运行",
                "GET /test-runs/{id}/logs": "获取测试运行日志",
                "GET /test-runs/stats": "获取测试运行统计信息"
            },
            "runtime_managers": {
                "GET /runtime-managers": "分页获取运行时管理器列表",
                "POST /runtime-managers": "创建新的运行时管理器",
                "GET /runtime-managers/{id}": "根据ID获取运行时管理器详情",
                "PUT /runtime-managers/{id}": "更新运行时管理器",
                "DELETE /runtime-managers/{id}": "删除运行时管理器",
                "POST /runtime-managers/{id}/heartbeat": "发送心跳信号",
                "POST /runtime-managers/{id}/test": "测试连接"
            }
        },
        "data_models": {
            "TestCase": {
                "id": "string (UUID)",
                "name": "string",
                "description": "string (optional)",
                "script_path": "string",
                "config_path": "string (optional)",
                "runtime_type": "enum: local|docker|kubernetes",
                "tags": "array of strings (optional)",
                "created_at": "datetime",
                "updated_at": "datetime"
            },
            "TestRun": {
                "id": "string (UUID)",
                "test_case_id": "string (UUID)",
                "status": "enum: pending|running|success|failed|cancelled|timeout",
                "start_time": "datetime (optional)",
                "end_time": "datetime (optional)",
                "duration_ms": "integer (optional)",
                "exit_code": "integer (optional)",
                "stdout": "string (optional)",
                "stderr": "string (optional)",
                "metadata": "json (optional)",
                "created_at": "datetime"
            },
            "RuntimeManager": {
                "id": "string (UUID)",
                "name": "string",
                "runtime_type": "enum: local|docker|kubernetes",
                "config": "json (optional)",
                "status": "enum: active|inactive|error|maintenance",
                "last_heartbeat": "datetime (optional)",
                "created_at": "datetime",
                "updated_at": "datetime"
            }
        },
        "response_format": {
            "success_response": {
                "success": true,
                "data": "<response_data>",
                "message": null,
                "timestamp": "datetime"
            },
            "error_response": {
                "success": false,
                "data": null,
                "message": "error_message",
                "timestamp": "datetime"
            },
            "paginated_response": {
                "data": "array of items",
                "pagination": {
                    "page": "integer",
                    "limit": "integer",
                    "total": "integer",
                    "total_pages": "integer",
                    "has_next": "boolean",
                    "has_prev": "boolean"
                }
            }
        },
        "examples": {
            "create_test_case": {
                "name": "CPU负载测试",
                "description": "测试系统在高CPU负载下的表现",
                "script_path": "stress_tester.py",
                "config_path": "configs/cpu_stress.json",
                "runtime_type": "local",
                "tags": ["performance", "cpu", "stress"]
            },
            "run_test_case": {
                "metadata": {
                    "environment": "production",
                    "user": "admin",
                    "priority": "high"
                }
            }
        }
    });

    Ok(Json(docs))
}

/// 系统统计信息端点
pub async fn system_stats(State(state): State<AppState>) -> Result<Json<ApiResponse<Value>>, StatusCode> {
    match get_system_stats(&state).await {
        Ok(stats) => Ok(Json(ApiResponse::success(stats))),
        Err(e) => {
            tracing::error!("获取系统统计信息失败: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

/// 版本信息端点
pub async fn version_info() -> Result<Json<ApiResponse<Value>>, StatusCode> {
    let version_info = json!({
        "service_name": "aiops-web-service",
        "version": env!("CARGO_PKG_VERSION"),
        "build_date": option_env!("VERGEN_BUILD_DATE").unwrap_or("unknown"),
        "git_commit": option_env!("VERGEN_GIT_SHA").unwrap_or("unknown"),
        "rust_version": option_env!("VERGEN_RUSTC_SEMVER").unwrap_or("unknown"),
        "features": [
            "axum web framework",
            "sqlite database",
            "multi-runtime support",
            "real-time monitoring",
            "rest api"
        ],
        "api_version": "v1",
        "documentation": "/api/v1/docs"
    });

    Ok(Json(ApiResponse::success(version_info)))
}

/// 获取系统统计信息
async fn get_system_stats(state: &AppState) -> anyhow::Result<Value> {
    // 获取数据库统计信息
    let db_stats = state.db.get_stats().await?;
    
    // 获取测试运行统计信息
    let test_stats = crate::models::TestRun::get_stats(state.db.pool()).await?;
    
    // 系统信息
    let system_info = json!({
        "uptime": chrono::Utc::now().to_rfc3339(),
        "memory_usage": get_memory_usage(),
        "cpu_usage": get_cpu_usage(),
        "disk_usage": get_disk_usage()
    });

    let stats = json!({
        "database": {
            "test_cases_count": db_stats.test_cases_count,
            "test_runs_count": db_stats.test_runs_count,
            "active_managers_count": db_stats.active_managers_count,
            "health": state.db.health_check().await.unwrap_or(false)
        },
        "test_execution": {
            "total_runs": test_stats.total_runs,
            "success_runs": test_stats.success_runs,
            "failed_runs": test_stats.failed_runs,
            "running_runs": test_stats.running_runs,
            "pending_runs": test_stats.pending_runs,
            "success_rate": format!("{:.2}%", test_stats.success_rate),
            "average_duration_ms": test_stats.average_duration_ms
        },
        "system": system_info,
        "service": {
            "name": "AIOps测试管理服务",
            "version": env!("CARGO_PKG_VERSION"),
            "status": "running",
            "port": state.config.port,
            "max_concurrent_tests": state.config.max_concurrent_tests
        }
    });

    Ok(stats)
}

/// 获取内存使用情况（简化版本）
fn get_memory_usage() -> Value {
    // 在实际应用中，可以使用sysinfo等库获取真实的系统信息
    json!({
        "used_mb": "N/A",
        "total_mb": "N/A",
        "usage_percent": "N/A"
    })
}

/// 获取CPU使用情况（简化版本）
fn get_cpu_usage() -> Value {
    json!({
        "usage_percent": "N/A",
        "cores": std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1)
    })
}

/// 获取磁盘使用情况（简化版本）
fn get_disk_usage() -> Value {
    json!({
        "used_gb": "N/A",
        "total_gb": "N/A",
        "usage_percent": "N/A"
    })
}