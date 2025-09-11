//! 应用程序配置模块
//! 
//! 管理Web服务的配置参数，包括数据库连接、端口设置等

use serde::{Deserialize, Serialize};
use std::env;

/// 应用程序配置结构
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    /// 服务监听端口
    pub port: u16,
    /// 数据库连接URL
    pub database_url: String,
    /// 日志级别
    pub log_level: String,
    /// 测试脚本目录
    pub test_scripts_dir: String,
    /// 结果存储目录
    pub results_dir: String,
    /// 最大并发测试数
    pub max_concurrent_tests: usize,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            port: 8888,
            database_url: "sqlite:./data/aiops_tests.db".to_string(),
            log_level: "info".to_string(),
            test_scripts_dir: "../".to_string(),
            results_dir: "./results".to_string(),
            max_concurrent_tests: 5,
        }
    }
}

impl AppConfig {
    /// 从环境变量加载配置
    pub fn load() -> anyhow::Result<Self> {
        let mut config = Self::default();

        // 从环境变量读取配置
        if let Ok(port) = env::var("AIOPS_PORT") {
            config.port = port.parse().unwrap_or(config.port);
        }

        if let Ok(db_url) = env::var("AIOPS_DATABASE_URL") {
            config.database_url = db_url;
        }

        if let Ok(log_level) = env::var("AIOPS_LOG_LEVEL") {
            config.log_level = log_level;
        }

        if let Ok(scripts_dir) = env::var("AIOPS_SCRIPTS_DIR") {
            config.test_scripts_dir = scripts_dir;
        }

        if let Ok(results_dir) = env::var("AIOPS_RESULTS_DIR") {
            config.results_dir = results_dir;
        }

        if let Ok(max_concurrent) = env::var("AIOPS_MAX_CONCURRENT") {
            config.max_concurrent_tests = max_concurrent.parse().unwrap_or(config.max_concurrent_tests);
        }

        Ok(config)
    }

    /// 验证配置有效性
    pub fn validate(&self) -> anyhow::Result<()> {
        if self.port == 0 {
            anyhow::bail!("端口不能为0");
        }

        if self.database_url.is_empty() {
            anyhow::bail!("数据库URL不能为空");
        }

        if self.max_concurrent_tests == 0 {
            anyhow::bail!("最大并发测试数不能为0");
        }

        Ok(())
    }
}