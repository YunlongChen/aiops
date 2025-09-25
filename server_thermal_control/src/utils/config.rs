use crate::models::{
    config::{AppConfig, DatabaseConfig, LoggingConfig, ServerConfig},
    error::{AppError, AppResult},
};
use config::{Config, ConfigError, Environment, File};
use serde::de::DeserializeOwned;
use serde::{Deserialize, Serialize};
use std::env;
use std::path::Path;
use std::sync::RwLock;
use tracing::{debug, info, warn};

/// 配置管理器
///
/// 提供配置文件加载、管理和热重载功能
pub struct ConfigManager {
    /// 当前配置
    config: RwLock<AppConfig>,
    /// 配置文件路径
    config_path: String,
}

impl ConfigManager {
    /// 创建新的配置管理器
    ///
    /// # 参数
    /// * `config_path` - 配置文件路径
    pub fn new(config_path: impl Into<String>) -> AppResult<Self> {
        let config_path = config_path.into();
        let config = load_config_from_file(&config_path)?;

        Ok(Self {
            config: RwLock::new(config),
            config_path,
        })
    }

    /// 获取配置的只读引用
    ///
    /// 返回当前配置的克隆
    pub fn get_config(&self) -> AppResult<AppConfig> {
        self.config
            .read()
            .map_err(|e| AppError::internal_server_error(format!("读取配置失败: {}", e)))
            .map(|config| config.clone())
    }

    /// 更新配置
    ///
    /// # 参数
    /// * `new_config` - 新的配置
    pub fn update_config(&self, new_config: AppConfig) -> AppResult<()> {
        let mut config = self
            .config
            .write()
            .map_err(|e| AppError::internal_server_error(format!("写入配置失败: {}", e)))?;

        *config = new_config;
        info!("配置已更新");

        Ok(())
    }

    /// 重新加载配置
    ///
    /// 从文件重新加载配置
    pub fn reload_config(&self) -> AppResult<()> {
        let new_config = load_config_from_file(&self.config_path)?;
        self.update_config(new_config)?;

        info!("配置已从文件重新加载: {}", self.config_path);
        Ok(())
    }

    /// 保存配置到文件
    ///
    /// # 参数
    /// * `path` - 保存路径（可选，默认使用原路径）
    pub fn save_config(&self, path: Option<&str>) -> AppResult<()> {
        let config = self.get_config()?;
        let save_path = path.unwrap_or(&self.config_path);

        save_config_to_file(&config, save_path)?;
        info!("配置已保存到文件: {}", save_path);

        Ok(())
    }

    /// 验证配置
    ///
    /// 验证当前配置的有效性
    pub fn validate_config(&self) -> AppResult<Vec<String>> {
        let config = self.get_config()?;
        let mut warnings = Vec::new();

        // 验证服务器配置
        if config.server.port == 0 {
            return Err(AppError::validation_error("server.port", "端口不能为0"));
        }

        if config.server.port < 1024 {
            warnings.push("使用小于1024的端口可能需要管理员权限".to_string());
        }

        // 验证数据库配置
        if config.database.url.is_empty() {
            return Err(AppError::validation_error(
                "database.url",
                "数据库URL不能为空",
            ));
        }

        if config.database.max_connections == 0 {
            return Err(AppError::validation_error(
                "database.max_connections",
                "最大连接数不能为0",
            ));
        }

        // 验证IPMI配置
        if config.ipmi.servers.is_empty() {
            warnings.push("未配置任何IPMI服务器".to_string());
        }

        for server in &config.ipmi.servers {
            if server.host.is_empty() {
                return Err(AppError::validation_error(
                    &format!("ipmi.servers[{}].host", server.id),
                    "服务器主机地址不能为空",
                ));
            }

            if server.username.is_empty() {
                return Err(AppError::validation_error(
                    &format!("ipmi.servers[{}].username", server.id),
                    "用户名不能为空",
                ));
            }

            if server.password.is_empty() {
                warnings.push(format!("服务器 {} 未设置密码", server.id));
            }
        }

        // 验证监控配置
        if config.monitoring.collection_interval == 0 {
            return Err(AppError::validation_error(
                "monitoring.collection_interval",
                "数据采集间隔不能为0",
            ));
        }

        if config.monitoring.retention_days == 0 {
            warnings.push("数据保留天数为0，历史数据将不会保存".to_string());
        }

        Ok(warnings)
    }

    /// 获取配置文件路径
    ///
    /// 返回当前配置文件的路径
    pub fn config_path(&self) -> &str {
        &self.config_path
    }
}

/// 从文件加载配置
///
/// # 参数
/// * `config_path` - 配置文件路径
pub fn load_config(config_path: &str) -> AppResult<AppConfig> {
    load_config_from_file(config_path)
}

/// 从文件加载配置的内部实现
///
/// # 参数
/// * `config_path` - 配置文件路径
fn load_config_from_file(config_path: &str) -> AppResult<AppConfig> {
    debug!("加载配置文件: {}", config_path);

    let mut builder = Config::builder();

    // 添加默认配置
    builder = builder.add_source(Config::try_from(&AppConfig::default())?);

    // 如果配置文件存在，则加载它
    if Path::new(config_path).exists() {
        let file_extension = Path::new(config_path)
            .extension()
            .and_then(|ext| ext.to_str())
            .unwrap_or("yaml");

        builder = builder.add_source(File::with_name(config_path).format(match file_extension {
            "toml" => config::FileFormat::Toml,
            "json" => config::FileFormat::Json,
            "yaml" | "yml" => config::FileFormat::Yaml,
            _ => config::FileFormat::Yaml,
        }));

        info!("已加载配置文件: {}", config_path);
    } else {
        warn!("配置文件不存在，使用默认配置: {}", config_path);
    }

    // 添加环境变量覆盖
    builder = builder.add_source(
        Environment::with_prefix("THERMAL_CONTROL")
            .separator("__")
            .try_parsing(true),
    );

    let config = builder
        .build()
        .map_err(|e| AppError::config_error(format!("构建配置失败: {}", e)))?;

    let app_config: AppConfig = config
        .try_deserialize()
        .map_err(|e| AppError::config_error(format!("反序列化配置失败: {}", e)))?;

    debug!("配置加载完成");
    Ok(app_config)
}

/// 保存配置到文件
///
/// # 参数
/// * `config` - 要保存的配置
/// * `path` - 保存路径
pub fn save_config_to_file(config: &AppConfig, path: &str) -> AppResult<()> {
    let file_extension = Path::new(path)
        .extension()
        .and_then(|ext| ext.to_str())
        .unwrap_or("yaml");

    let content = match file_extension {
        "toml" => toml::to_string_pretty(config)
            .map_err(|e| AppError::serialization_error(format!("TOML序列化失败: {}", e)))?,
        "json" => serde_json::to_string_pretty(config)
            .map_err(|e| AppError::serialization_error(format!("JSON序列化失败: {}", e)))?,
        // "yaml" | "yml" => serde_yaml::to_string(config)
        //     .map_err(|e| AppError::serialization_error(format!("YAML序列化失败: {}", e)))?,
        _ => {
            return Err(AppError::config_error(format!(
                "不支持的文件格式: {}",
                file_extension
            )))
        }
    };

    // 确保目录存在
    if let Some(parent) = Path::new(path).parent() {
        std::fs::create_dir_all(parent)
            .map_err(|e| AppError::file_system_error(format!("创建目录失败: {}", e)))?;
    }

    std::fs::write(path, content)
        .map_err(|e| AppError::file_system_error(format!("写入文件失败: {}", e)))?;

    debug!("配置已保存到: {}", path);
    Ok(())
}

/// 从环境变量加载配置
///
/// 从环境变量中加载特定的配置项
pub fn load_config_from_env<T: DeserializeOwned>(prefix: &str) -> AppResult<T> {
    let config = Config::builder()
        .add_source(Environment::with_prefix(prefix).separator("__"))
        .build()
        .map_err(|e| AppError::config_error(format!("从环境变量构建配置失败: {}", e)))?;

    config
        .try_deserialize()
        .map_err(|e| AppError::config_error(format!("从环境变量反序列化配置失败: {}", e)))
}

/// 合并配置
///
/// 将多个配置源合并为一个配置
///
/// # 参数
/// * `base_config` - 基础配置
/// * `override_config` - 覆盖配置
pub fn merge_configs(base_config: AppConfig, override_config: AppConfig) -> AppConfig {
    // 这里可以实现更复杂的合并逻辑
    // 目前简单地用override_config覆盖base_config
    override_config
}

/// 获取配置模板
///
/// 返回一个配置模板，用于生成示例配置文件
pub fn get_config_template() -> AppConfig {
    AppConfig::default()
}

/// 验证配置文件格式
///
/// # 参数
/// * `path` - 配置文件路径
pub fn validate_config_file_format(path: &str) -> AppResult<()> {
    if !Path::new(path).exists() {
        return Err(AppError::not_found_error("config_file", path));
    }

    let extension = Path::new(path)
        .extension()
        .and_then(|ext| ext.to_str())
        .ok_or_else(|| AppError::config_error("无法确定配置文件格式"))?;

    match extension {
        "yaml" | "yml" | "toml" | "json" => Ok(()),
        _ => Err(AppError::config_error(format!(
            "不支持的配置文件格式: {}",
            extension
        ))),
    }
}

/// 创建默认配置文件
///
/// # 参数
/// * `path` - 配置文件路径
pub fn create_default_config_file(path: &str) -> AppResult<()> {
    if Path::new(path).exists() {
        return Err(AppError::config_error("配置文件已存在"));
    }

    let default_config = AppConfig::default();
    save_config_to_file(&default_config, path)?;

    info!("已创建默认配置文件: {}", path);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;

    #[test]
    fn test_load_default_config() {
        let config = AppConfig::default();
        assert_eq!(config.server.host, "127.0.0.1");
        assert_eq!(config.server.port, 8080);
    }

    #[test]
    fn test_save_and_load_config() {
        let temp_file = NamedTempFile::new().unwrap();
        let config_path = temp_file.path().to_str().unwrap();

        let original_config = AppConfig::default();
        save_config_to_file(&original_config, config_path).unwrap();

        let loaded_config = load_config_from_file(config_path).unwrap();
        assert_eq!(loaded_config.server.host, original_config.server.host);
        assert_eq!(loaded_config.server.port, original_config.server.port);
    }

    #[test]
    fn test_config_manager() {
        let temp_file = NamedTempFile::new().unwrap();
        let config_path = temp_file.path().to_str().unwrap();

        // 创建默认配置文件
        create_default_config_file(config_path).unwrap();

        // 创建配置管理器
        let manager = ConfigManager::new(config_path).unwrap();

        // 验证配置
        let warnings = manager.validate_config().unwrap();
        assert!(!warnings.is_empty()); // 应该有一些警告

        // 获取配置
        let config = manager.get_config().unwrap();
        assert_eq!(config.server.port, 8080);
    }
}
