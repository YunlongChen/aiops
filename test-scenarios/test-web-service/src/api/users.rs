//! 用户管理API处理器
//! 
//! 实现用户认证、授权和用户信息管理功能

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

/// 用户信息结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: String,
    pub username: String,
    pub email: String,
    pub full_name: String,
    pub role: String,
    pub status: String,
    pub created_at: String,
    pub updated_at: String,
    pub last_login: Option<String>,
}

/// 登录请求
#[derive(Debug, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}

/// 登录响应
#[derive(Debug, Serialize)]
pub struct LoginResponse {
    pub token: String,
    pub refresh_token: String,
    pub user: User,
    pub expires_in: i64,
}

/// 注册请求
#[derive(Debug, Deserialize)]
pub struct RegisterRequest {
    pub username: String,
    pub email: String,
    pub password: String,
    pub full_name: String,
}

/// 更新用户请求
#[derive(Debug, Deserialize)]
pub struct UpdateUserRequest {
    pub email: Option<String>,
    pub full_name: Option<String>,
    pub role: Option<String>,
    pub status: Option<String>,
}

/// 修改密码请求
#[derive(Debug, Deserialize)]
pub struct ChangePasswordRequest {
    pub old_password: String,
    pub new_password: String,
}

/// 用户登录
pub async fn login(
    State(_state): State<AppState>,
    Json(request): Json<LoginRequest>,
) -> Result<Json<ApiResponse<LoginResponse>>, StatusCode> {
    // 模拟用户验证
    if request.username == "admin" && request.password == "admin123" {
        let user = User {
            id: Uuid::new_v4().to_string(),
            username: request.username,
            email: "admin@aiops.local".to_string(),
            full_name: "系统管理员".to_string(),
            role: "admin".to_string(),
            status: "active".to_string(),
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
            last_login: Some(chrono::Utc::now().to_rfc3339()),
        };
        
        let response = LoginResponse {
            token: "mock_jwt_token_12345".to_string(),
            refresh_token: "mock_refresh_token_67890".to_string(),
            user,
            expires_in: 3600, // 1小时
        };
        
        Ok(Json(ApiResponse::<LoginResponse>::success(response)))
    } else {
        Ok(Json(ApiResponse::<LoginResponse>::error("用户名或密码错误".to_string())))
    }
}

/// 用户登出
pub async fn logout(
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    Ok(Json(ApiResponse::<String>::success("登出成功".to_string())))
}

/// 刷新令牌
pub async fn refresh_token(
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<Value>>, StatusCode> {
    let response = json!({
        "token": "new_mock_jwt_token_54321",
        "expires_in": 3600
    });
    
    Ok(Json(ApiResponse::<Value>::success(response)))
}

/// 获取当前用户信息
pub async fn get_current_user(
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<User>>, StatusCode> {
    let user = User {
        id: Uuid::new_v4().to_string(),
        username: "admin".to_string(),
        email: "admin@aiops.local".to_string(),
        full_name: "系统管理员".to_string(),
        role: "admin".to_string(),
        status: "active".to_string(),
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
        last_login: Some(chrono::Utc::now().to_rfc3339()),
    };
    
    Ok(Json(ApiResponse::<User>::success(user)))
}

/// 获取用户列表
pub async fn list_users(
    Query(params): Query<PaginationParams>,
    State(_state): State<AppState>,
) -> Result<Json<PaginatedResponse<User>>, StatusCode> {
    let users = vec![
        User {
            id: Uuid::new_v4().to_string(),
            username: "admin".to_string(),
            email: "admin@aiops.local".to_string(),
            full_name: "系统管理员".to_string(),
            role: "admin".to_string(),
            status: "active".to_string(),
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
            last_login: Some(chrono::Utc::now().to_rfc3339()),
        },
        User {
            id: Uuid::new_v4().to_string(),
            username: "user1".to_string(),
            email: "user1@aiops.local".to_string(),
            full_name: "测试用户1".to_string(),
            role: "user".to_string(),
            status: "active".to_string(),
            created_at: chrono::Utc::now().to_rfc3339(),
            updated_at: chrono::Utc::now().to_rfc3339(),
            last_login: None,
        },
    ];
    
    let pagination = crate::models::PaginationInfo {
        page: params.page,
        limit: params.limit,
        total: users.len() as u64,
        total_pages: 1,
        has_next: false,
        has_prev: false,
    };
    
    Ok(Json(PaginatedResponse {
        data: users,
        pagination,
    }))
}

/// 创建用户
pub async fn create_user(
    State(_state): State<AppState>,
    Json(request): Json<RegisterRequest>,
) -> Result<Json<ApiResponse<User>>, StatusCode> {
    let user = User {
        id: Uuid::new_v4().to_string(),
        username: request.username,
        email: request.email,
        full_name: request.full_name,
        role: "user".to_string(),
        status: "active".to_string(),
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
        last_login: None,
    };
    
    tracing::info!("创建用户成功: {} ({})", user.username, user.id);
    Ok(Json(ApiResponse::<User>::success(user)))
}

/// 获取用户详情
pub async fn get_user(
    Path(id): Path<Uuid>,
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<User>>, StatusCode> {
    let user = User {
        id: id.to_string(),
        username: "user1".to_string(),
        email: "user1@aiops.local".to_string(),
        full_name: "测试用户1".to_string(),
        role: "user".to_string(),
        status: "active".to_string(),
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
        last_login: None,
    };
    
    Ok(Json(ApiResponse::<User>::success(user)))
}

/// 更新用户
pub async fn update_user(
    Path(id): Path<Uuid>,
    State(_state): State<AppState>,
    Json(request): Json<UpdateUserRequest>,
) -> Result<Json<ApiResponse<User>>, StatusCode> {
    let mut user = User {
        id: id.to_string(),
        username: "user1".to_string(),
        email: "user1@aiops.local".to_string(),
        full_name: "测试用户1".to_string(),
        role: "user".to_string(),
        status: "active".to_string(),
        created_at: chrono::Utc::now().to_rfc3339(),
        updated_at: chrono::Utc::now().to_rfc3339(),
        last_login: None,
    };
    
    if let Some(email) = request.email {
        user.email = email;
    }
    if let Some(full_name) = request.full_name {
        user.full_name = full_name;
    }
    if let Some(role) = request.role {
        user.role = role;
    }
    if let Some(status) = request.status {
        user.status = status;
    }
    
    user.updated_at = chrono::Utc::now().to_rfc3339();
    
    tracing::info!("更新用户成功: {} ({})", user.username, user.id);
    Ok(Json(ApiResponse::<User>::success(user)))
}

/// 删除用户
pub async fn delete_user(
    Path(id): Path<Uuid>,
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    tracing::info!("删除用户: {}", id);
    Ok(Json(ApiResponse::<String>::success("用户删除成功".to_string())))
}

/// 修改密码
pub async fn change_password(
    State(_state): State<AppState>,
    Json(request): Json<ChangePasswordRequest>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    // 模拟密码验证
    if request.old_password == "admin123" {
        tracing::info!("用户密码修改成功");
        Ok(Json(ApiResponse::<String>::success("密码修改成功".to_string())))
    } else {
        Ok(Json(ApiResponse::<String>::error("原密码错误".to_string())))
    }
}

/// 重置密码
pub async fn reset_password(
    Path(id): Path<Uuid>,
    State(_state): State<AppState>,
) -> Result<Json<ApiResponse<String>>, StatusCode> {
    let new_password = "temp123456";
    tracing::info!("重置用户密码: {}, 新密码: {}", id, new_password);
    Ok(Json(ApiResponse::<String>::success(format!("密码已重置为: {}", new_password))))
}