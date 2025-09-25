use crate::models::{
    error::{AppError, AppResult},
    config::*,
    api::{ApiResponse, PaginationParams},
};
use crate::services::{ConfigService, config_service::{ConfigExportFormat, ConfigTemplateType, ConfigValidationResult}};
use actix_web::{
    web::{Data, Path, Query, ServiceConfig},
    HttpResponse, Result as ActixResult,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tracing::{info, warn, error};

/// 配置控制器
/// 
/// 提供系统配置管理、持久化和热重载的HTTP API接口
#[derive(Clone)]
pub struct ConfigController {
    config_service: Arc<ConfigService>,
}

impl ConfigController {
    /// 创建新的配置控制器
    /// 
    /// # 参数
    /// * `config_service` - 配置服务
    pub fn new(config_service: Arc<ConfigService>) -> Self {
        Self { config_service }
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/config")
                .route("", actix_web::web::get().to(Self::get_config))
                .route("", actix_web::web::put().to(Self::update_config))
                .route("/reload", actix_web::web::post().to(Self::reload_config))
                .route("/reset", actix_web::web::post().to(Self::reset_config))
                .route("/server", actix_web::web::get().to(Self::get_server_config))
                .route("/server", actix_web::web::put().to(Self::update_server_config))
                .route("/database", actix_web::web::get().to(Self::get_database_config))
                .route("/database", actix_web::web::put().to(Self::update_database_config))
                .route("/ipmi", actix_web::web::get().to(Self::get_ipmi_config))
                .route("/ipmi", actix_web::web::put().to(Self::update_ipmi_config))
                .route("/monitoring", actix_web::web::get().to(Self::get_monitoring_config))
                .route("/monitoring", actix_web::web::put().to(Self::update_monitoring_config))
                .route("/alerts", actix_web::web::get().to(Self::get_alert_config))
                .route("/alerts", actix_web::web::put().to(Self::update_alert_config))
                .route("/logging", actix_web::web::get().to(Self::get_logging_config))
                .route("/logging", actix_web::web::put().to(Self::update_logging_config))
                .route("/export", actix_web::web::get().to(Self::export_config))
                .route("/import", actix_web::web::post().to(Self::import_config))
                .route("/history", actix_web::web::get().to(Self::get_config_history))
                .route("/history/{version}", actix_web::web::get().to(Self::get_config_version))
                .route("/rollback/{version}", actix_web::web::post().to(Self::rollback_config))
                .route("/validate", actix_web::web::post().to(Self::validate_config))
                .route("/templates", actix_web::web::get().to(Self::get_config_templates))
                .route("/templates/{template_type}", actix_web::web::get().to(Self::get_config_template))
                .route("/backup", actix_web::web::post().to(Self::backup_config))
                .route("/backups", actix_web::web::get().to(Self::list_config_backups))
                .route("/backups/{backup_id}", actix_web::web::get().to(Self::get_config_backup))
                .route("/backups/{backup_id}/restore", actix_web::web::post().to(Self::restore_config_backup))
                .route("/backups/{backup_id}", actix_web::web::delete().to(Self::delete_config_backup))
        );
    }

    /// 获取完整配置
    /// 
    /// GET /api/v1/config
    async fn get_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取完整配置");

        let config = service.get_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新完整配置
    /// 
    /// PUT /api/v1/config
    async fn update_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<AppConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新完整配置");

        service.update_config(config.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 重新加载配置
    /// 
    /// POST /api/v1/config/reload
    async fn reload_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("重新加载配置");

        let result = service.reload_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 重置配置为默认值
    /// 
    /// POST /api/v1/config/reset
    async fn reset_config(
        service: Data<ConfigService>,
        request: actix_web::web::Json<ResetConfigRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("重置配置为默认值");

        service.reset_to_default(request.backup_current.unwrap_or(true)).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取服务器配置
    /// 
    /// GET /api/v1/config/server
    async fn get_server_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取服务器配置");

        let config = service.get_server_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新服务器配置
    /// 
    /// PUT /api/v1/config/server
    async fn update_server_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<ServerConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新服务器配置");

        service.update_server_config(config.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取数据库配置
    /// 
    /// GET /api/v1/config/database
    async fn get_database_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取数据库配置");

        let config = service.get_database_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新数据库配置
    /// 
    /// PUT /api/v1/config/database
    async fn update_database_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<DatabaseConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新数据库配置");

        service.update_database_config(config.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取IPMI配置
    /// 
    /// GET /api/v1/config/ipmi
    async fn get_ipmi_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取IPMI配置");

        let config = service.get_ipmi_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新IPMI配置
    /// 
    /// PUT /api/v1/config/ipmi
    async fn update_ipmi_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<IpmiConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新IPMI配置");

        service.update_ipmi_config(config.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取监控配置
    /// 
    /// GET /api/v1/config/monitoring
    async fn get_monitoring_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取监控配置");

        let config = service.get_monitoring_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新监控配置
    /// 
    /// PUT /api/v1/config/monitoring
    async fn update_monitoring_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<MonitoringConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新监控配置");

        service.update_monitoring_config(config.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取告警配置
    /// 
    /// GET /api/v1/config/alerts
    async fn get_alert_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取告警配置");

        let config = service.get_alert_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新告警配置
    /// 
    /// PUT /api/v1/config/alert
    async fn update_alert_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<AlertingConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新告警配置");

        service.update_alert_config(config.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 获取日志配置
    /// 
    /// GET /api/v1/config/logging
    async fn get_logging_config(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取日志配置");

        let config = service.get_logging_config().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 更新日志配置
    /// 
    /// PUT /api/v1/config/logging
    async fn update_logging_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<LoggingConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("更新日志配置");

        service.update_logging_config(config.into_inner()).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }

    /// 导出配置
    /// 
    /// GET /api/v1/config/export
    async fn export_config(
        service: Data<ConfigService>,
        params: Query<ExportConfigParams>,
    ) -> ActixResult<HttpResponse> {
        info!("导出配置");

        let export_data = service.export_config(
            params.format.unwrap_or(ConfigExportFormat::Json),
            params.include_sensitive.unwrap_or(false),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(export_data)))
    }

    /// 导入配置
    /// 
    /// POST /api/v1/config/import
    async fn import_config(
        service: Data<ConfigService>,
        request: actix_web::web::Json<ImportConfigRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("导入配置");

        let request = request.into_inner();
        let result = service.import_config(
            request.data,
            request.format,
            request.merge_strategy.unwrap_or(ConfigMergeStrategy::Replace),
            request.validate_before_import.unwrap_or(true),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取配置变更历史
    /// 
    /// GET /api/v1/config/history
    async fn get_config_history(
        service: Data<ConfigService>,
        params: Query<ConfigHistoryParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取配置变更历史");

        let history = service.get_config_history(
            params.limit.unwrap_or(50),
            params.offset.unwrap_or(0),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(history)))
    }

    /// 获取指定版本的配置
    /// 
    /// GET /api/v1/config/history/:version
    async fn get_config_version(
        service: Data<ConfigService>,
        version: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("获取配置版本: {}", version);

        let config = service.get_config_version(&version).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(config)))
    }

    /// 回滚到指定版本
    /// 
    /// POST /api/v1/config/rollback/:version
    async fn rollback_config(
        service: Data<ConfigService>,
        version: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("回滚配置到版本: {}", version);

        let result = service.rollback_to_version(&version).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 验证配置
    /// 
    /// POST /api/v1/config/validate
    async fn validate_config(
        service: Data<ConfigService>,
        config: actix_web::web::Json<AppConfig>,
    ) -> ActixResult<HttpResponse> {
        info!("验证配置");

        let result = service.validate_config(&config).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 获取配置模板列表
    /// 
    /// GET /api/v1/config/templates
    async fn get_config_templates(
        service: Data<ConfigService>,
    ) -> ActixResult<HttpResponse> {
        info!("获取配置模板列表");

        let templates = service.get_available_templates().await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(templates)))
    }

    /// 获取指定类型的配置模板
    /// 
    /// GET /api/v1/config/templates/:template_type
    async fn get_config_template(
        service: Data<ConfigService>,
        template_type: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("获取配置模板: {}", template_type);

        let template_type = match template_type.as_str() {
            "development" => ConfigTemplateType::Development,
            "production" => ConfigTemplateType::Production,
            "testing" => ConfigTemplateType::Testing,
            "minimal" => ConfigTemplateType::Minimal,
            _ => return Err(actix_web::error::ErrorBadRequest("Invalid template type")),
        };

        let template = service.get_config_template(template_type).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(template)))
    }

    /// 备份当前配置
    /// 
    /// POST /api/v1/config/backup
    async fn backup_config(
        service: Data<ConfigService>,
        request: actix_web::web::Json<BackupConfigRequest>,
    ) -> ActixResult<HttpResponse> {
        info!("备份当前配置");

        let backup = service.create_config_backup(
            request.name.as_deref(),
            request.description.as_deref(),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(backup)))
    }

    /// 获取配置备份列表
    /// 
    /// GET /api/v1/config/backups
    async fn list_config_backups(
        service: Data<ConfigService>,
        params: Query<ListBackupsParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取配置备份列表");

        let backups = service.list_config_backups(
            params.limit.unwrap_or(20),
            params.offset.unwrap_or(0),
        ).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;

        Ok(HttpResponse::Ok().json(ApiResponse::success(backups)))
    }

    /// 获取指定配置备份
    /// 
    /// GET /api/v1/config/backups/:backup_id
    async fn get_config_backup(
        service: Data<ConfigService>,
        backup_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("获取配置备份: {}", backup_id);

        let backup = service.get_config_backup(&backup_id).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(backup)))
    }

    /// 恢复配置备份
    /// 
    /// POST /api/v1/config/backups/:backup_id/restore
    async fn restore_config_backup(
        service: Data<ConfigService>,
        backup_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("恢复配置备份: {}", backup_id);

        let result = service.restore_config_backup(&backup_id).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(result)))
    }

    /// 删除配置备份
    /// 
    /// DELETE /api/v1/config/backups/:backup_id
    async fn delete_config_backup(
        service: Data<ConfigService>,
        backup_id: Path<String>,
    ) -> ActixResult<HttpResponse> {
        info!("删除配置备份: {}", backup_id);

        service.delete_config_backup(&backup_id).await
            .map_err(|e| actix_web::error::ErrorInternalServerError(e))?;
        Ok(HttpResponse::Ok().json(ApiResponse::success(())))
    }
}

// 请求和响应结构体

/// 重置配置请求
#[derive(Debug, Deserialize)]
pub struct ResetConfigRequest {
    /// 是否备份当前配置
    pub backup_current: Option<bool>,
}

/// 导出配置参数
#[derive(Debug, Deserialize)]
pub struct ExportConfigParams {
    /// 导出格式
    pub format: Option<ConfigExportFormat>,
    /// 是否包含敏感信息
    pub include_sensitive: Option<bool>,
}

/// 导入配置请求
#[derive(Debug, Deserialize)]
pub struct ImportConfigRequest {
    /// 配置数据（base64编码）
    pub data: String,
    /// 数据格式
    pub format: ConfigExportFormat,
    /// 合并策略
    pub merge_strategy: Option<ConfigMergeStrategy>,
    /// 导入前是否验证
    pub validate_before_import: Option<bool>,
}

/// 配置历史参数
#[derive(Debug, Deserialize)]
pub struct ConfigHistoryParams {
    /// 返回记录数限制
    pub limit: Option<usize>,
    /// 偏移量
    pub offset: Option<usize>,
}

/// 备份配置请求
#[derive(Debug, Deserialize)]
pub struct BackupConfigRequest {
    /// 备份名称
    pub name: Option<String>,
    /// 备份描述
    pub description: Option<String>,
}

/// 备份列表参数
#[derive(Debug, Deserialize)]
pub struct ListBackupsParams {
    /// 返回记录数限制
    pub limit: Option<usize>,
    /// 偏移量
    pub offset: Option<usize>,
}

/// 配置重新加载结果
#[derive(Debug, Serialize)]
pub struct ConfigReloadResult {
    /// 是否成功
    pub success: bool,
    /// 重新加载的配置项数量
    pub reloaded_items: usize,
    /// 变更的配置项
    pub changed_items: Vec<String>,
    /// 警告信息
    pub warnings: Vec<String>,
    /// 错误信息
    pub errors: Vec<String>,
    /// 重新加载时间
    pub reloaded_at: chrono::DateTime<chrono::Utc>,
}

/// 配置导出数据
#[derive(Debug, Serialize)]
pub struct ConfigExportData {
    /// 导出格式
    pub format: ConfigExportFormat,
    /// 导出数据（base64编码）
    pub data: String,
    /// 文件名
    pub filename: String,
    /// 是否包含敏感信息
    pub includes_sensitive: bool,
    /// 导出时间
    pub exported_at: chrono::DateTime<chrono::Utc>,
    /// 配置版本
    pub config_version: String,
}

/// 配置合并策略
#[derive(Debug, Clone, Deserialize)]
pub enum ConfigMergeStrategy {
    /// 替换整个配置
    Replace,
    /// 合并配置项
    Merge,
    /// 仅更新存在的配置项
    Update,
}

/// 配置导入结果
#[derive(Debug, Serialize)]
pub struct ConfigImportResult {
    /// 是否成功
    pub success: bool,
    /// 导入的配置项数量
    pub imported_items: usize,
    /// 更新的配置项
    pub updated_items: Vec<String>,
    /// 新增的配置项
    pub added_items: Vec<String>,
    /// 验证结果
    pub validation_result: ConfigValidationResult,
    /// 导入时间
    pub imported_at: chrono::DateTime<chrono::Utc>,
    /// 备份ID（如果创建了备份）
    pub backup_id: Option<String>,
}

/// 配置回滚结果
#[derive(Debug, Serialize)]
pub struct ConfigRollbackResult {
    /// 是否成功
    pub success: bool,
    /// 回滚的版本
    pub rolled_back_version: String,
    /// 回滚前的版本
    pub previous_version: String,
    /// 变更的配置项
    pub changed_items: Vec<String>,
    /// 回滚时间
    pub rolled_back_at: chrono::DateTime<chrono::Utc>,
    /// 备份ID（回滚前的配置备份）
    pub backup_id: String,
}

/// 配置模板信息
#[derive(Debug, Serialize)]
pub struct ConfigTemplateInfo {
    /// 模板类型
    pub template_type: ConfigTemplateType,
    /// 模板名称
    pub name: String,
    /// 描述
    pub description: String,
    /// 适用场景
    pub use_cases: Vec<String>,
    /// 是否推荐
    pub recommended: bool,
}

/// 配置备份
#[derive(Debug, Serialize, Deserialize)]
pub struct ConfigBackup {
    /// 备份ID
    pub id: String,
    /// 备份名称
    pub name: Option<String>,
    /// 描述
    pub description: Option<String>,
    /// 配置数据
    pub config_data: AppConfig,
    /// 创建时间
    pub created_at: chrono::DateTime<chrono::Utc>,
    /// 配置版本
    pub config_version: String,
    /// 备份大小（字节）
    pub size_bytes: u64,
    /// 是否为自动备份
    pub is_auto_backup: bool,
}

/// 配置恢复结果
#[derive(Debug, Serialize)]
pub struct ConfigRestoreResult {
    /// 是否成功
    pub success: bool,
    /// 恢复的备份ID
    pub restored_backup_id: String,
    /// 恢复前的配置版本
    pub previous_version: String,
    /// 恢复后的配置版本
    pub restored_version: String,
    /// 变更的配置项
    pub changed_items: Vec<String>,
    /// 恢复时间
    pub restored_at: chrono::DateTime<chrono::Utc>,
    /// 验证结果
    pub validation_result: ConfigValidationResult,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::services::ConfigService;
    use actix_web::{test, web, App, http::StatusCode};

    #[actix_web::test]
    async fn test_config_controller_routes() {
        let config_service = web::Data::new(ConfigService::new().await.unwrap());
        
        let app = test::init_service(
            App::new()
                .app_data(config_service.clone())
                .service(
                    web::scope("/api/v1")
                        .configure(ConfigController::configure)
                )
        ).await;
        
        // 测试获取配置
        let req = test::TestRequest::get()
            .uri("/api/v1/config")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);
        
        // 测试获取配置模板
        let req = test::TestRequest::get()
            .uri("/api/v1/config/templates")
            .to_request();
        let resp = test::call_service(&app, req).await;
        assert_eq!(resp.status(), StatusCode::OK);
    }

    #[test]
    fn test_reset_config_request_deserialization() {
        let json = r#"{"backup_current": true}"#;
        let request: ResetConfigRequest = serde_json::from_str(json).unwrap();
        
        assert_eq!(request.backup_current, Some(true));
    }

    #[test]
    fn test_config_merge_strategy_deserialization() {
        let json = r#""Merge""#;
        let strategy: ConfigMergeStrategy = serde_json::from_str(json).unwrap();
        
        matches!(strategy, ConfigMergeStrategy::Merge);
    }
}