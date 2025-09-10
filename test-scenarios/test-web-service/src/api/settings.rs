//! 系统设置管理API处理器
//! 
//! 实现系统配置、用户偏好设置和全局参数管理功能

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    response::Json,
};
use uuid::Uuid;
use serde_json::{json, Value};
use crate::{
    AppState,
    models::{ApiResponse, PaginationParams, PaginatedResponse}
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// 设置项结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Setting {
    pub id: String,
    pub key: String,
    pub value: Value,
    pub category: String,
    pub description: String,
    pub data_type: String, // string, number, boolean, json
    pub is_public: bool,
    pub is_readonly: bool,
    pub created_at: String,
    pub updated_at: String,
}

/// 设置更新请求
#[derive(Debug, Deserialize)]
pub struct UpdateSettingRequest {
    pub value: Value,
    pub description: Option<String>,
}

/// 批量设置更新请求
#[derive(Debug, Deserialize)]
pub struct BatchUpdateSettingsRequest {
    pub settings: HashMap<String, Value>,
}

/// 用户偏好设置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserPreference {
    pub id: String,
    pub user_id: String,
    pub key: String,
    pub value: Value,
    pub created_at: String,
    pub updated_at: String,
}

/// 用户偏好更新请求
#[derive(Debug, Deserialize)]
pub struct UpdateUserPreferenceRequest {
    pub key: String,
    pub value: Value,
}

/// 获取系统设置列表
pub async fn list_settings(
    Query(params): Query<PaginationParams>,
    State(_state): State<AppState>,
) -> Result<Json<PaginatedResponse<Setting>>, StatusCode> {
    let settings = vec![
        Setting {
            id: Uuid::new_v4().to_string(),
            key: "system.name".to_string(),
            value: json!("AIOps测试场景管理系统"),
            category: "system".to_string(),
            description: "系统名称".to_string(),
            data_type: "string".to_string(),
            is_public: true,
            is_readonly: false,
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
        Setting {
            id: Uuid::new_v4().to_string(),
            key: "system.version".to_string(),
            value: json!("1.0.0"),
            category: "system".to_string(),
            description: "系统版本".to_string(),
            data_type: "string".to_string(),
            is_public: true,
            is_readonly: true,
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
        Setting {
            id: Uuid::new_v4().to_string(),
            key: "test.timeout".to_string(),
            value: json!(300),
            category: "test".to_string(),
            description: "测试超时时间（秒）".to_string(),
            data_type: "number".to_string(),
            is_public: false,
            is_readonly: false,
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
        Setting {
            id: Uuid::new_v4().to_string(),
            key: "test.parallel_limit".to_string(),
            value: json!(5),
            category: "test".to_string(),
            description: "并行测试数量限制".to_string(),
            data_type: "number".to_string(),
            is_public: false,
            is_readonly: false,
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
        Setting {
            id: Uuid::new_v4().to_string(),
            key: "notification.email_enabled".to_string(),
            value: json!(true),
            category: "notification".to_string(),
            description: "启用邮件通知".to_string(),
            data_type: "boolean".to_string(),
            is_public: false,
            is_readonly: false,
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
    ];
    
    let pagination = crate::models::PaginationInfo {
        page: params.page.unwrap_or(1),
        limit: params.limit.unwrap_or(10),
        total: settings.len() as i64,
        total_pages: 1,
        has_next: false,
        has_prev: false,
    };
    
    Ok(Json(PaginatedResponse {
        data: settings,
        pagination,
    }))
}

/// 根据分类获取设置
pub async fn get_settings_by_category(
    Path(category): Path<String>,
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<Vec<Setting>>>, StatusCode> {
    let all_settings = vec![
        Setting {
            id: Uuid::new_v4().to_string(),
            key: "system.name".to_string(),
            value: json!("AIOps测试场景管理系统"),
            category: "system".to_string(),
            description: "系统名称".to_string(),
            data_type: "string".to_string(),
            is_public: true,
            is_readonly: false,
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
        Setting {
            id: Uuid::new_v4().to_string(),
            key: "test.timeout".to_string(),
            value: json!(300),
            category: "test".to_string(),
            description: "测试超时时间（秒）".to_string(),
            data_type: "number".to_string(),
            is_public: false,
            is_readonly: false,
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
    ];
    
    let filtered_settings: Vec<Setting> = all_settings
        .into_iter()
        .filter(|s| s.category == category)
        .collect();
    
    Ok(Json(ApiResponse::success(filtered_settings)))
}

/// 获取单个设置
pub async fn get_setting(
    Path(key): Path<String>,
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<Setting>>, StatusCode> {
    let setting = Setting {
        id: Uuid::new_v4().to_string(),
        key: key.clone(),
        value: match key.as_str() {
            "system.name" => json!("AIOps测试场景管理系统"),
            "system.version" => json!("1.0.0"),
            "test.timeout" => json!(300),
            "test.parallel_limit" => json!(5),
            "notification.email_enabled" => json!(true),
            _ => json!(null),
        },
        category: match key.as_str() {
            k if k.starts_with("system.") => "system".to_string(),
            k if k.starts_with("test.") => "test".to_string(),
            k if k.starts_with("notification.") => "notification".to_string(),
            _ => "other".to_string(),
        },
        description: format!("设置项: {}", key),
        data_type: "string".to_string(),
        is_public: true,
        is_readonly: false,
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
    };
    
    Ok(Json(ApiResponse::success(setting)))
}

/// 更新设置
pub async fn update_setting(
    Path(key): Path<String>,
    State(_state): State<AppState>,
    Json(request): Json<UpdateSettingRequest>,
) -> Result<Json<ApiResponse<Setting>>, StatusCode> {
    let setting = Setting {
        id: Uuid::new_v4().to_string(),
        key: key.clone(),
        value: request.value,
        category: match key.as_str() {
            k if k.starts_with("system.") => "system".to_string(),
            k if k.starts_with("test.") => "test".to_string(),
            k if k.starts_with("notification.") => "notification".to_string(),
            _ => "other".to_string(),
        },
        description: request.description.unwrap_or_else(|| format!("设置项: {}", key)),
        data_type: "string".to_string(),
        is_public: true,
        is_readonly: false,
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
    };
    
    tracing::info!("更新设置成功: {} = {:?}", key, setting.value);
    Ok(Json(ApiResponse::success(setting)))
}

/// 批量更新设置
pub async fn batch_update_settings(
    State(_state): State<AppState>,
    Json(request): Json<BatchUpdateSettingsRequest>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    let count = request.settings.len();
    
    for (key, value) in request.settings {
        tracing::info!("批量更新设置: {} = {:?}", key, value);
    }
    
    Ok(Json(ApiResponse::success(format!("成功更新 {} 个设置项", count))))
}

/// 重置设置为默认值
pub async fn reset_setting(
    Path(key): Path<String>,
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<Setting>>, StatusCode> {
    let default_value = match key.as_str() {
        "system.name" => json!("AIOps测试场景管理系统"),
        "system.version" => json!("1.0.0"),
        "test.timeout" => json!(300),
        "test.parallel_limit" => json!(5),
        "notification.email_enabled" => json!(true),
        _ => json!(null),
    };
    
    let setting = Setting {
        id: Uuid::new_v4().to_string(),
        key: key.clone(),
        value: default_value,
        category: match key.as_str() {
            k if k.starts_with("system.") => "system".to_string(),
            k if k.starts_with("test.") => "test".to_string(),
            k if k.starts_with("notification.") => "notification".to_string(),
            _ => "other".to_string(),
        },
        description: format!("设置项: {}", key),
        data_type: "string".to_string(),
        is_public: true,
        is_readonly: false,
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
    };
    
    tracing::info!("重置设置为默认值: {}", key);
    Ok(Json(ApiResponse::success(setting)))
}

/// 获取用户偏好设置
pub async fn get_user_preferences(
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<Vec<UserPreference>>>, StatusCode> {
    let preferences = vec![
        UserPreference {
            id: Uuid::new_v4().to_string(),
            user_id: "current_user_id".to_string(),
            key: "theme".to_string(),
            value: json!("dark"),
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
        UserPreference {
            id: Uuid::new_v4().to_string(),
            user_id: "current_user_id".to_string(),
            key: "language".to_string(),
            value: json!("zh-CN"),
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
        UserPreference {
            id: Uuid::new_v4().to_string(),
            user_id: "current_user_id".to_string(),
            key: "page_size".to_string(),
            value: json!(20),
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
        },
    ];
    
    Ok(Json(ApiResponse::success(preferences)))
}

/// 更新用户偏好设置
pub async fn update_user_preference(
    State(_state): State<AppState>,
    Json(request): Json<UpdateUserPreferenceRequest>,
) -> Result<Json<ApiResponse<UserPreference>>, StatusCode> {
    let preference = UserPreference {
        id: Uuid::new_v4().to_string(),
        user_id: "current_user_id".to_string(),
        key: request.key.clone(),
        value: request.value,
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
    };
    
    tracing::info!("更新用户偏好设置: {} = {:?}", request.key, preference.value);
    Ok(Json(ApiResponse::success(preference)))
}

/// 获取系统配置概览
pub async fn get_system_config(
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<Value>>, StatusCode> {
    let config = json!({
        "system": {
            "name": "AIOps测试场景管理系统",
            "version": "1.0.0",
            "environment": "development",
            "debug_mode": true
        },
        "test": {
            "timeout": 300,
            "parallel_limit": 5,
            "retry_count": 3,
            "supported_languages": ["python", "javascript", "bash", "powershell"]
        },
        "notification": {
            "email_enabled": true,
            "webhook_enabled": false,
            "slack_enabled": false
        },
        "security": {
            "jwt_expiry": 3600,
            "password_policy": {
                "min_length": 8,
                "require_uppercase": true,
                "require_lowercase": true,
                "require_numbers": true,
                "require_symbols": false
            }
        }
    });
    
    Ok(Json(ApiResponse::success(config)))
}