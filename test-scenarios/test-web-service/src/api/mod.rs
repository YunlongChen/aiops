//! API路由模块
//! 
//! 定义所有REST API端点和路由配置

use axum::{
    routing::{get, post, put, delete},
    Router,
};

mod test_cases;
mod test_runs;
mod runtime_managers;
mod system;
mod users;
mod settings;

use crate::AppState;

/// 创建API路由
pub fn routes() -> Router<AppState> {
    Router::new()
        // 系统相关路由
        .route("/docs", get(system::api_docs))
        .route("/stats", get(system::system_stats))
        .route("/version", get(system::version_info))
        
        // 测试用例管理路由
        .route("/test-cases", get(test_cases::list_test_cases))
        .route("/test-cases", post(test_cases::create_test_case))
        .route("/test-cases/:id", get(test_cases::get_test_case))
        .route("/test-cases/:id", put(test_cases::update_test_case))
        .route("/test-cases/:id", delete(test_cases::delete_test_case))
        .route("/test-cases/:id/run", post(test_cases::run_test_case))
        
        // 测试运行记录路由
        .route("/test-runs", get(test_runs::list_test_runs))
        .route("/test-runs", post(test_runs::create_test_run))
        .route("/test-runs/:id", get(test_runs::get_test_run))
        .route("/test-runs/:id", put(test_runs::update_test_run))
        .route("/test-runs/:id/start", post(test_runs::start_test_run))
        .route("/test-runs/:id/stop", post(test_runs::stop_test_run))
        .route("/test-runs/:id/logs", get(test_runs::get_test_logs))
        .route("/test-runs/stats", get(test_runs::get_test_stats))
        
        // 运行时管理器路由
        .route("/runtime-managers", get(runtime_managers::list_managers))
        .route("/runtime-managers", post(runtime_managers::create_manager))
        .route("/runtime-managers/:id", get(runtime_managers::get_manager))
        .route("/runtime-managers/:id", put(runtime_managers::update_manager))
        .route("/runtime-managers/:id", delete(runtime_managers::delete_manager))
        .route("/runtime-managers/:id/heartbeat", post(runtime_managers::heartbeat))
        .route("/runtime-managers/:id/test", post(runtime_managers::test_connection))
        
        // 用户管理路由
        .route("/auth/login", post(users::login))
        .route("/auth/logout", post(users::logout))
        .route("/auth/refresh", post(users::refresh_token))
        .route("/auth/me", get(users::get_current_user))
        .route("/users", get(users::list_users))
        .route("/users", post(users::create_user))
        .route("/users/:id", get(users::get_user))
        .route("/users/:id", put(users::update_user))
        .route("/users/:id", delete(users::delete_user))
        .route("/users/change-password", post(users::change_password))
        .route("/users/:id/reset-password", post(users::reset_password))
        
        // 设置管理路由
        .route("/settings", get(settings::list_settings))
        .route("/settings/category/:category", get(settings::get_settings_by_category))
        .route("/settings/:key", get(settings::get_setting))
        .route("/settings/:key", put(settings::update_setting))
        .route("/settings/batch", put(settings::batch_update_settings))
        .route("/settings/:key/reset", post(settings::reset_setting))
        .route("/settings/config", get(settings::get_system_config))
        .route("/preferences", get(settings::get_user_preferences))
        .route("/preferences", put(settings::update_user_preference))
}