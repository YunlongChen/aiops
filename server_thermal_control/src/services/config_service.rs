use crate::models::{
    config::*,
    error::{AppError, AppResult},
    alert::AlertConfig,
};
use crate::utils::{
    time::TimeUtils,
    validation::ValidationUtils,
    logger::LoggerManager,
};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tokio::fs;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json;
use tracing::{info, warn, error, debug};
use crate::config::AppConfig;

/// 配置服务
/// 
/// 负责系统配置的管理、持久化和热重载
#[derive(Clone)]
pub struct ConfigService {
    /// 应用配置
    app_config: Arc<RwLock<AppConfig>>,
    /// 配置文件路径
    config_file_path: String,
    /// 配置历史
    config_history: Arc<RwLock<Vec<ConfigChange>>>,
    /// 配置验证器
    validator: ValidationUtils,
    /// 时间工具
    time_utils: TimeUtils,
}

impl ConfigService {
    /// 创建新的配置服务
    /// 
    /// # 参数
    /// * `config_file_path` - 配置文件路径
    pub fn new(config_file_path: String) -> Self {
        Self {
            app_config: Arc::new(RwLock::new(AppConfig::default())),
            config_file_path,
            config_history: Arc::new(RwLock::new(Vec::new())),
            validator: ValidationUtils,
            time_utils: TimeUtils,
        }
    }

    /// 初始化配置服务
    pub async fn initialize(&self) -> AppResult<()> {
        info!("初始化配置服务");

        // 尝试加载配置文件
        if let Err(e) = self.load_config().await {
            warn!("加载配置文件失败: {}, 使用默认配置", e);
            
            // 使用默认配置并保存
            let default_config = AppConfig::default();
            self.save_config(&default_config).await?;
            
            {
                let mut config = self.app_config.write().await;
                *config = default_config;
            }
        }

        // 验证配置
        self.validate_current_config().await?;

        info!("配置服务初始化完成");
        Ok(())
    }

    /// 获取当前配置
    pub async fn get_config(&self) -> AppConfig {
        self.app_config.read().await.clone()
    }

    /// 获取服务器配置
    pub async fn get_server_config(&self) -> ServerConfig {
        let config = self.app_config.read().await;
        config.server.clone()
    }

    /// 获取数据库配置
    pub async fn get_database_config(&self) -> DatabaseConfig {
        let config = self.app_config.read().await;
        config.database.clone()
    }

    /// 获取IPMI配置
    pub async fn get_ipmi_config(&self) -> IpmiConfig {
        let config = self.app_config.read().await;
        config.ipmi.clone()
    }

    /// 获取监控配置
    pub async fn get_monitoring_config(&self) -> MonitoringConfig {
        let config = self.app_config.read().await;
        config.monitoring.clone()
    }

    /// 获取告警配置
    pub async fn get_alert_config(&self) -> AlertConfig {
        let config = self.app_config.read().await;
        config.alert.clone()
    }

    /// 获取日志配置
    pub async fn get_logging_config(&self) -> LoggingConfig {
        let config = self.app_config.read().await;
        config.logging.clone()
    }

    /// 更新完整配置
    /// 
    /// # 参数
    /// * `new_config` - 新的配置
    /// * `updated_by` - 更新者
    pub async fn update_config(&self, new_config: AppConfig, updated_by: String) -> AppResult<()> {
        info!("更新完整配置 by {}", updated_by);

        // 验证新配置
        self.validate_config(&new_config).await?;

        // 记录配置变更
        let old_config = self.app_config.read().await.clone();
        self.record_config_change(&old_config, &new_config, updated_by).await;

        // 保存配置到文件
        self.save_config(&new_config).await?;

        // 更新内存中的配置
        {
            let mut config = self.app_config.write().await;
            *config = new_config;
        }

        info!("配置更新完成");
        Ok(())
    }

    /// 更新服务器配置
    /// 
    /// # 参数
    /// * `server_config` - 服务器配置
    /// * `updated_by` - 更新者
    pub async fn update_server_config(&self, server_config: ServerConfig, updated_by: String) -> AppResult<()> {
        info!("更新服务器配置 by {}", updated_by);

        // 验证服务器配置
        server_config.validate()?;

        let old_config = self.app_config.read().await.clone();
        let mut new_config = old_config.clone();
        new_config.server = server_config;

        self.update_config(new_config, updated_by).await
    }

    /// 更新数据库配置
    /// 
    /// # 参数
    /// * `database_config` - 数据库配置
    /// * `updated_by` - 更新者
    pub async fn update_database_config(&self, database_config: DatabaseConfig, updated_by: String) -> AppResult<()> {
        info!("更新数据库配置 by {}", updated_by);

        // 验证数据库配置
        database_config.validate()?;

        let old_config = self.app_config.read().await.clone();
        let mut new_config = old_config.clone();
        new_config.database = database_config;

        self.update_config(new_config, updated_by).await
    }

    /// 更新IPMI配置
    /// 
    /// # 参数
    /// * `ipmi_config` - IPMI配置
    /// * `updated_by` - 更新者
    pub async fn update_ipmi_config(&self, ipmi_config: IpmiConfig, updated_by: String) -> AppResult<()> {
        info!("更新IPMI配置 by {}", updated_by);

        // 验证IPMI配置
        ipmi_config.validate()?;

        let old_config = self.app_config.read().await.clone();
        let mut new_config = old_config.clone();
        new_config.ipmi = ipmi_config;

        self.update_config(new_config, updated_by).await
    }

    /// 更新监控配置
    /// 
    /// # 参数
    /// * `monitoring_config` - 监控配置
    /// * `updated_by` - 更新者
    pub async fn update_monitoring_config(&self, monitoring_config: MonitoringConfig, updated_by: String) -> AppResult<()> {
        info!("更新监控配置 by {}", updated_by);

        // 验证监控配置
        monitoring_config.validate()?;

        let old_config = self.app_config.read().await.clone();
        let mut new_config = old_config.clone();
        new_config.monitoring = monitoring_config;

        self.update_config(new_config, updated_by).await
    }

    /// 更新告警配置
    /// 
    /// # 参数
    /// * `alert_config` - 告警配置
    /// * `updated_by` - 更新者
    pub async fn update_alert_config(&self, alert_config: AlertConfig, updated_by: String) -> AppResult<()> {
        info!("更新告警配置 by {}", updated_by);

        // 验证告警配置
        alert_config.validate()?;

        let old_config = self.app_config.read().await.clone();
        let mut new_config = old_config.clone();
        new_config.alert = alert_config;

        self.update_config(new_config, updated_by).await
    }

    /// 更新日志配置
    /// 
    /// # 参数
    /// * `logging_config` - 日志配置
    /// * `updated_by` - 更新者
    pub async fn update_logging_config(&self, logging_config: LoggingConfig, updated_by: String) -> AppResult<()> {
        info!("更新日志配置 by {}", updated_by);

        // 验证日志配置
        logging_config.validate()?;

        let old_config = self.app_config.read().await.clone();
        let mut new_config = old_config.clone();
        new_config.logging = logging_config;

        self.update_config(new_config, updated_by).await
    }

    /// 重置配置为默认值
    /// 
    /// # 参数
    /// * `reset_by` - 重置者
    pub async fn reset_to_default(&self, reset_by: String) -> AppResult<()> {
        info!("重置配置为默认值 by {}", reset_by);

        let default_config = AppConfig::default();
        self.update_config(default_config, reset_by).await
    }

    /// 导出配置
    /// 
    /// # 参数
    /// * `format` - 导出格式
    pub async fn export_config(&self, format: ConfigExportFormat) -> AppResult<String> {
        info!("导出配置，格式: {:?}", format);

        let config = self.app_config.read().await;

        match format {
            ConfigExportFormat::Json => {
                serde_json::to_string_pretty(&*config)
                    .map_err(|e| AppError::SerializationError(e.to_string()))
            },
            ConfigExportFormat::Yaml => {
                serde_yaml::to_string(&*config)
                    .map_err(|e| AppError::SerializationError(e.to_string()))
            },
            ConfigExportFormat::Toml => {
                toml::to_string_pretty(&*config)
                    .map_err(|e| AppError::SerializationError(e.to_string()))
            },
        }
    }

    /// 导入配置
    /// 
    /// # 参数
    /// * `config_data` - 配置数据
    /// * `format` - 配置格式
    /// * `imported_by` - 导入者
    pub async fn import_config(
        &self,
        config_data: String,
        format: ConfigExportFormat,
        imported_by: String,
    ) -> AppResult<()> {
        info!("导入配置，格式: {:?} by {}", format, imported_by);

        let new_config: AppConfig = match format {
            ConfigExportFormat::Json => {
                serde_json::from_str(&config_data)
                    .map_err(|e| AppError::DeserializationError(e.to_string()))?
            },
            ConfigExportFormat::Yaml => {
                serde_yaml::from_str(&config_data)
                    .map_err(|e| AppError::DeserializationError(e.to_string()))?
            },
            ConfigExportFormat::Toml => {
                toml::from_str(&config_data)
                    .map_err(|e| AppError::DeserializationError(e.to_string()))?
            },
        };

        self.update_config(new_config, imported_by).await
    }

    /// 获取配置变更历史
    /// 
    /// # 参数
    /// * `limit` - 返回记录数限制
    pub async fn get_config_history(&self, limit: Option<usize>) -> Vec<ConfigChange> {
        let history = self.config_history.read().await;
        let limit = limit.unwrap_or(100);
        
        history.iter()
            .rev()
            .take(limit)
            .cloned()
            .collect()
    }

    /// 回滚到指定版本
    /// 
    /// # 参数
    /// * `change_id` - 变更ID
    /// * `rollback_by` - 回滚者
    pub async fn rollback_to_version(&self, change_id: &str, rollback_by: String) -> AppResult<()> {
        info!("回滚配置到版本: {} by {}", change_id, rollback_by);

        let history = self.config_history.read().await;
        
        if let Some(change) = history.iter().find(|c| c.id == change_id) {
            let rollback_config = change.old_config.clone();
            drop(history); // 释放读锁
            
            self.update_config(rollback_config, rollback_by).await?;
            
            info!("配置回滚完成");
            Ok(())
        } else {
            Err(AppError::NotFound(format!("配置变更记录不存在: {}", change_id)))
        }
    }

    /// 验证配置文件
    /// 
    /// # 参数
    /// * `config_data` - 配置数据
    /// * `format` - 配置格式
    pub async fn validate_config_file(
        &self,
        config_data: String,
        format: ConfigExportFormat,
    ) -> AppResult<ConfigValidationResult> {
        info!("验证配置文件，格式: {:?}", format);

        let mut result = ConfigValidationResult {
            is_valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
        };

        // 尝试解析配置
        let config: AppConfig = match format {
            ConfigExportFormat::Json => {
                match serde_json::from_str(&config_data) {
                    Ok(config) => config,
                    Err(e) => {
                        result.is_valid = false;
                        result.errors.push(format!("JSON解析错误: {}", e));
                        return Ok(result);
                    }
                }
            },
            ConfigExportFormat::Yaml => {
                match serde_yaml::from_str(&config_data) {
                    Ok(config) => config,
                    Err(e) => {
                        result.is_valid = false;
                        result.errors.push(format!("YAML解析错误: {}", e));
                        return Ok(result);
                    }
                }
            },
            ConfigExportFormat::Toml => {
                match toml::from_str(&config_data) {
                    Ok(config) => config,
                    Err(e) => {
                        result.is_valid = false;
                        result.errors.push(format!("TOML解析错误: {}", e));
                        return Ok(result);
                    }
                }
            },
        };

        // 验证配置内容
        if let Err(e) = self.validate_config(&config).await {
            result.is_valid = false;
            result.errors.push(e.to_string());
        }

        // 添加警告信息
        self.add_config_warnings(&config, &mut result).await;

        info!("配置验证完成，有效: {}", result.is_valid);
        Ok(result)
    }

    /// 获取配置模板
    /// 
    /// # 参数
    /// * `template_type` - 模板类型
    pub async fn get_config_template(&self, template_type: ConfigTemplateType) -> AppResult<String> {
        info!("获取配置模板: {:?}", template_type);

        let template_config = match template_type {
            ConfigTemplateType::Development => self.create_development_template(),
            ConfigTemplateType::Production => self.create_production_template(),
            ConfigTemplateType::Testing => self.create_testing_template(),
            ConfigTemplateType::Minimal => self.create_minimal_template(),
        };

        serde_json::to_string_pretty(&template_config)
            .map_err(|e| AppError::SerializationError(e.to_string()))
    }

    /// 热重载配置
    pub async fn reload_config(&self) -> AppResult<()> {
        info!("热重载配置");

        // 重新加载配置文件
        self.load_config().await?;

        // 验证新配置
        self.validate_current_config().await?;

        info!("配置热重载完成");
        Ok(())
    }

    // 私有方法

    /// 加载配置文件
    async fn load_config(&self) -> AppResult<()> {
        debug!("加载配置文件: {}", self.config_file_path);

        let config_content = fs::read_to_string(&self.config_file_path).await
            .map_err(|e| AppError::FileError(format!("读取配置文件失败: {}", e)))?;

        let config: AppConfig = if self.config_file_path.ends_with(".json") {
            serde_json::from_str(&config_content)
                .map_err(|e| AppError::DeserializationError(e.to_string()))?
        } else if self.config_file_path.ends_with(".yaml") || self.config_file_path.ends_with(".yml") {
            serde_yaml::from_str(&config_content)
                .map_err(|e| AppError::DeserializationError(e.to_string()))?
        } else if self.config_file_path.ends_with(".toml") {
            toml::from_str(&config_content)
                .map_err(|e| AppError::DeserializationError(e.to_string()))?
        } else {
            return Err(AppError::InvalidInput("不支持的配置文件格式".to_string()));
        };

        {
            let mut app_config = self.app_config.write().await;
            *app_config = config;
        }

        debug!("配置文件加载完成");
        Ok(())
    }

    /// 保存配置到文件
    async fn save_config(&self, config: &AppConfig) -> AppResult<()> {
        debug!("保存配置到文件: {}", self.config_file_path);

        let config_content = if self.config_file_path.ends_with(".json") {
            serde_json::to_string_pretty(config)
                .map_err(|e| AppError::SerializationError(e.to_string()))?
        } else if self.config_file_path.ends_with(".yaml") || self.config_file_path.ends_with(".yml") {
            serde_yaml::to_string(config)
                .map_err(|e| AppError::SerializationError(e.to_string()))?
        } else if self.config_file_path.ends_with(".toml") {
            toml::to_string_pretty(config)
                .map_err(|e| AppError::SerializationError(e.to_string()))?
        } else {
            return Err(AppError::InvalidInput("不支持的配置文件格式".to_string()));
        };

        // 创建备份
        if let Err(e) = self.create_config_backup().await {
            warn!("创建配置备份失败: {}", e);
        }

        // 保存新配置
        fs::write(&self.config_file_path, config_content).await
            .map_err(|e| AppError::FileError(format!("保存配置文件失败: {}", e)))?;

        debug!("配置文件保存完成");
        Ok(())
    }

    /// 创建配置备份
    async fn create_config_backup(&self) -> AppResult<()> {
        let backup_path = format!("{}.backup.{}", 
                                 self.config_file_path, 
                                 self.time_utils.get_current_timestamp());

        if let Ok(content) = fs::read_to_string(&self.config_file_path).await {
            fs::write(&backup_path, content).await
                .map_err(|e| AppError::FileError(format!("创建配置备份失败: {}", e)))?;
            
            debug!("配置备份创建完成: {}", backup_path);
        }

        Ok(())
    }

    /// 验证当前配置
    async fn validate_current_config(&self) -> AppResult<()> {
        let config = self.app_config.read().await;
        self.validate_config(&config).await
    }

    /// 验证配置
    async fn validate_config(&self, config: &AppConfig) -> AppResult<()> {
        debug!("验证配置");

        // 验证各个子配置
        config.server.validate()?;
        config.database.validate()?;
        config.ipmi.validate()?;
        config.monitoring.validate()?;
        config.alert.validate()?;
        config.logging.validate()?;

        debug!("配置验证通过");
        Ok(())
    }

    /// 记录配置变更
    async fn record_config_change(&self, old_config: &AppConfig, new_config: &AppConfig, changed_by: String) {
        let change = ConfigChange {
            id: uuid::Uuid::new_v4().to_string(),
            timestamp: Utc::now(),
            changed_by,
            old_config: old_config.clone(),
            new_config: new_config.clone(),
            changes: self.calculate_config_diff(old_config, new_config),
        };

        let mut history = self.config_history.write().await;
        history.push(change);

        // 限制历史记录数量
        if history.len() > 100 {
            history.drain(0..10); // 删除最旧的10条记录
        }

        debug!("配置变更记录已保存");
    }

    /// 计算配置差异
    fn calculate_config_diff(&self, old_config: &AppConfig, new_config: &AppConfig) -> Vec<String> {
        let mut changes = Vec::new();

        // 简化的差异计算，实际实现中可以更详细
        if old_config.server != new_config.server {
            changes.push("服务器配置已更改".to_string());
        }
        if old_config.database != new_config.database {
            changes.push("数据库配置已更改".to_string());
        }
        if old_config.ipmi != new_config.ipmi {
            changes.push("IPMI配置已更改".to_string());
        }
        if old_config.monitoring != new_config.monitoring {
            changes.push("监控配置已更改".to_string());
        }
        if old_config.alert != new_config.alert {
            changes.push("告警配置已更改".to_string());
        }
        if old_config.logging != new_config.logging {
            changes.push("日志配置已更改".to_string());
        }

        changes
    }

    /// 添加配置警告
    async fn add_config_warnings(&self, config: &AppConfig, result: &mut ConfigValidationResult) {
        // 检查服务器超时配置
        if config.server.timeout < 30 {
            result.warnings.push("服务器超时时间过短，建议至少30秒".to_string());
        }

        // 检查数据库连接池大小
        if config.database.max_connections > 100 {
            result.warnings.push("数据库连接池大小过大，可能影响性能".to_string());
        }

        // 检查监控间隔
        if config.monitoring.collection_interval < 5 {
            result.warnings.push("监控数据收集间隔过短，可能影响性能".to_string());
        }

        // 检查日志级别
        if config.logging.level == "debug" {
            result.warnings.push("日志级别设置为debug，可能产生大量日志".to_string());
        }
    }

    /// 创建开发环境模板
    fn create_development_template(&self) -> AppConfig {
        let mut config = AppConfig::default();
        config.server.timeout = 60;
        config.server.port = 8080;
        config.logging.level = "debug".to_string();
        config.monitoring.collection_interval = 10;
        config
    }

    /// 创建生产环境模板
    fn create_production_template(&self) -> AppConfig {
        let mut config = AppConfig::default();
        config.server.timeout = 120;
        config.server.port = 80;
        config.logging.level = "info".to_string();
        config.monitoring.collection_interval = 30;
        config.database.max_connections = 50;
        config
    }

    /// 创建测试环境模板
    fn create_testing_template(&self) -> AppConfig {
        let mut config = AppConfig::default();
        config.server.timeout = 30;
        config.server.port = 3000;
        config.logging.level = "warn".to_string();
        config.monitoring.collection_interval = 5;
        config.database.max_connections = 10;
        config
    }

    /// 创建最小配置模板
    fn create_minimal_template(&self) -> AppConfig {
        AppConfig::default()
    }
}

/// 配置导出格式
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConfigExportFormat {
    Json,
    Yaml,
    Toml,
}

/// 配置验证结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigValidationResult {
    /// 是否有效
    pub is_valid: bool,
    /// 错误信息
    pub errors: Vec<String>,
    /// 警告信息
    pub warnings: Vec<String>,
}

/// 配置模板类型
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ConfigTemplateType {
    Development,
    Production,
    Testing,
    Minimal,
}

/// 配置变更记录
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConfigChange {
    /// 变更ID
    pub id: String,
    /// 变更时间
    pub timestamp: DateTime<Utc>,
    /// 变更者
    pub changed_by: String,
    /// 旧配置
    pub old_config: AppConfig,
    /// 新配置
    pub new_config: AppConfig,
    /// 变更内容
    pub changes: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[tokio::test]
    async fn test_config_service_creation() {
        let temp_file = NamedTempFile::new().unwrap();
        let config_path = temp_file.path().to_string_lossy().to_string();
        
        let service = ConfigService::new(config_path);
        let config = service.get_config().await;
        
        assert_eq!(config.server.host, "0.0.0.0");
        assert_eq!(config.server.port, 8080);
    }

    #[tokio::test]
    async fn test_config_validation() {
        let temp_file = NamedTempFile::new().unwrap();
        let config_path = temp_file.path().to_string_lossy().to_string();
        
        let service = ConfigService::new(config_path);
        let config = AppConfig::default();
        
        let result = service.validate_config(&config).await;
        assert!(result.is_ok());
    }

    #[tokio::test]
    async fn test_config_export_import() {
        let temp_file = NamedTempFile::new().unwrap();
        let config_path = temp_file.path().to_string_lossy().to_string();
        
        let service = ConfigService::new(config_path);
        
        // 导出配置
        let exported = service.export_config(ConfigExportFormat::Json).await.unwrap();
        assert!(!exported.is_empty());
        
        // 导入配置
        let result = service.import_config(exported, ConfigExportFormat::Json, "test".to_string()).await;
        assert!(result.is_ok());
    }

    #[test]
    fn test_config_diff_calculation() {
        let temp_file = NamedTempFile::new().unwrap();
        let config_path = temp_file.path().to_string_lossy().to_string();
        
        let service = ConfigService::new(config_path);
        
        let mut old_config = AppConfig::default();
        let mut new_config = AppConfig::default();
        new_config.server.port = 9090;
        
        let changes = service.calculate_config_diff(&old_config, &new_config);
        assert_eq!(changes.len(), 1);
        assert_eq!(changes[0], "服务器配置已更改");
    }
}