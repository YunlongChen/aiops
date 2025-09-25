use crate::models::{
    config::LoggingConfig,
    error::{AppError, AppResult},
};
use std::fs;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;
use tracing::level_filters::LevelFilter;
use tracing::{debug, error, info, warn};
use tracing::{subscriber::set_global_default, Level};
use tracing_subscriber::filter::Builder;
use tracing_subscriber::{
    filter::EnvFilter,
    fmt::{self, time::ChronoUtc},
    layer::SubscriberExt,
    util::SubscriberInitExt,
    Layer,
};

/// 日志级别枚举
///
/// 定义不同的日志级别
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum LogLevel {
    /// 调试级别
    Debug,
    /// 信息级别
    Info,
    /// 警告级别
    Warn,
    /// 错误级别
    Error,
}

impl From<LogLevel> for Level {
    fn from(level: LogLevel) -> Self {
        match level {
            LogLevel::Debug => Level::DEBUG,
            LogLevel::Info => Level::INFO,
            LogLevel::Warn => Level::WARN,
            LogLevel::Error => Level::ERROR,
        }
    }
}

impl std::fmt::Display for LogLevel {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LogLevel::Debug => write!(f, "debug"),
            LogLevel::Info => write!(f, "info"),
            LogLevel::Warn => write!(f, "warn"),
            LogLevel::Error => write!(f, "error"),
        }
    }
}

/// 初始化日志系统
///
/// 使用默认配置初始化日志记录器
pub fn init_logger() -> AppResult<()> {
    let config = LoggingConfig::default();
    let manager = LoggerManager::new(config);
    manager.init()
}

/// 日志管理器
///
/// 提供日志初始化、配置和管理功能
pub struct LoggerManager {
    config: LoggingConfig,
}

impl LoggerManager {
    /// 创建新的日志管理器
    ///
    /// # 参数
    /// * `config` - 日志配置
    pub fn new(config: LoggingConfig) -> Self {
        Self { config }
    }

    /// 初始化日志系统
    ///
    /// 根据配置初始化日志记录器
    pub fn init(&self) -> AppResult<()> {
        let file_path = &self.config.file_path.unwrap();

        // 创建日志目录
        if let Some(parent) = Path::new(file_path).parent() {
            fs::create_dir_all(parent)
                .map_err(|e| AppError::file_system_error(format!("创建日志目录失败: {}", e)))?;
        }

        // 设置环境过滤器
        let env_filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| {
            EnvFilter::new(format!("{}={}", env!("CARGO_PKG_NAME"), self.config.level))
        });

        // 创建格式化层
        let fmt_layer = fmt::layer()
            .with_timer(ChronoUtc::rfc_3339())
            .with_target(true)
            .with_thread_ids(true)
            .with_thread_names(true)
            .with_file(true)
            .with_line_number(true);

        // 根据配置决定输出目标
        let subscriber = tracing_subscriber::registry().with(env_filter);

        if self.config.console_output {
            // 控制台输出
            let console_layer = fmt_layer.with_ansi(true).with_writer(std::io::stdout);

            if self.config.file_output {
                let file_path = self.config.file_path.unwrap();

                // 同时输出到控制台和文件
                let file = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(Path::new(&file_path))
                    .map_err(|e| AppError::file_system_error(format!("打开日志文件失败: {}", e)))?;

                let file_layer = fmt_layer.with_ansi(false).with_writer(file);

                subscriber.with(console_layer).with(file_layer).init();
            } else {
                // 仅控制台输出
                subscriber.with(console_layer).init();
            }
        } else if self.config.file_output {
            let file_path = self.config.file_path.unwrap().clone();

            // 仅文件输出
            let file = OpenOptions::new()
                .create(true)
                .append(true)
                .open(Path::new(file_path))
                .map_err(|e| AppError::file_system_error(format!("打开日志文件失败: {}", e)))?;

            let file_layer = fmt_layer.with_ansi(false).with_writer(file);

            subscriber.with(file_layer).init();
        } else {
            return Err(AppError::config_error("必须启用控制台或文件输出"));
        }

        info!("日志系统初始化完成");
        debug!("日志配置: {:?}", self.config);

        Ok(())
    }

    /// 轮转日志文件
    ///
    /// 当日志文件过大时进行轮转
    pub fn rotate_log_file(&self) -> AppResult<()> {
        let log_path = Path::new(&self.config.file_path.unwrap());

        if !log_path.exists() {
            return Ok(());
        }

        let metadata = fs::metadata(log_path)
            .map_err(|e| AppError::file_system_error(format!("获取日志文件信息失败: {}", e)))?;

        // 检查文件大小（假设最大10MB）
        const MAX_LOG_SIZE: u64 = 10 * 1024 * 1024;

        if metadata.len() > MAX_LOG_SIZE {
            let backup_path = format!(
                "{}.{}",
                self.config.file_path.unwrap(),
                chrono::Utc::now().format("%Y%m%d_%H%M%S")
            );

            fs::rename(log_path, &backup_path)
                .map_err(|e| AppError::file_system_error(format!("轮转日志文件失败: {}", e)))?;

            info!(
                "日志文件已轮转: {} -> {}",
                self.config.file_path, backup_path
            );
        }
        Ok(())
    }

    /// 清理旧日志文件
    ///
    /// 删除超过保留期限的日志文件
    pub fn cleanup_old_logs(&self, retention_days: u32) -> AppResult<()> {
        let log_dir = Path::new(&self.config.file_path.unwrap())
            .parent()
            .ok_or_else(|| AppError::file_system_error("无法获取日志目录"))?;

        let cutoff_time = chrono::Utc::now() - chrono::Duration::days(retention_days as i64);

        let entries = fs::read_dir(log_dir)
            .map_err(|e| AppError::file_system_error(format!("读取日志目录失败: {}", e)))?;

        let mut deleted_count = 0;

        for entry in entries {
            let entry =
                entry.map_err(|e| AppError::file_system_error(format!("读取目录项失败: {}", e)))?;

            let path = entry.path();

            // 只处理日志文件
            if let Some(file_name) = path.file_name().and_then(|n| n.to_str()) {
                if file_name.starts_with("thermal_control") && file_name.ends_with(".log") {
                    let metadata = fs::metadata(&path).map_err(|e| {
                        AppError::file_system_error(format!("获取文件信息失败: {}", e))
                    })?;

                    if let Ok(modified_time) = metadata.modified() {
                        let modified_datetime =
                            chrono::DateTime::<chrono::Utc>::from(modified_time);

                        if modified_datetime < cutoff_time {
                            fs::remove_file(&path).map_err(|e| {
                                AppError::file_system_error(format!("删除日志文件失败: {}", e))
                            })?;

                            deleted_count += 1;
                            debug!("已删除旧日志文件: {:?}", path);
                        }
                    }
                }
            }
        }

        if deleted_count > 0 {
            info!("已清理 {} 个旧日志文件", deleted_count);
        }

        Ok(())
    }

    /// 获取日志统计信息
    ///
    /// 返回日志文件的统计信息
    pub fn get_log_stats(&self) -> AppResult<LogStats> {
        let log_path = Path::new(&self.config.file_path.unwrap());

        if !log_path.exists() {
            return Ok(LogStats::default());
        }

        let metadata = fs::metadata(log_path)
            .map_err(|e| AppError::file_system_error(format!("获取日志文件信息失败: {}", e)))?;

        let content = fs::read_to_string(log_path)
            .map_err(|e| AppError::file_system_error(format!("读取日志文件失败: {}", e)))?;

        let line_count = content.lines().count();
        let error_count = content.matches("ERROR").count();
        let warn_count = content.matches("WARN").count();
        let info_count = content.matches("INFO").count();
        let debug_count = content.matches("DEBUG").count();

        Ok(LogStats {
            file_size: metadata.len(),
            line_count,
            error_count,
            warn_count,
            info_count,
            debug_count,
            last_modified: metadata
                .modified()
                .ok()
                .map(|t| chrono::DateTime::<chrono::Utc>::from(t)),
        })
    }
}

/// 日志统计信息
#[derive(Debug, Clone)]
pub struct LogStats {
    /// 文件大小（字节）
    pub file_size: u64,
    /// 行数
    pub line_count: usize,
    /// 错误日志数量
    pub error_count: usize,
    /// 警告日志数量
    pub warn_count: usize,
    /// 信息日志数量
    pub info_count: usize,
    /// 调试日志数量
    pub debug_count: usize,
    /// 最后修改时间
    pub last_modified: Option<chrono::DateTime<chrono::Utc>>,
}

impl Default for LogStats {
    fn default() -> Self {
        Self {
            file_size: 0,
            line_count: 0,
            error_count: 0,
            warn_count: 0,
            info_count: 0,
            debug_count: 0,
            last_modified: None,
        }
    }
}

/// 初始化简单的日志记录器
///
/// 用于快速初始化基本的日志功能
pub fn init_simple_logger() -> AppResult<()> {
    // Builder::from_default_env()
    //     .filter_level(LevelFilter::INFO)
    //     .format_timestamp_secs()
    //     .init();
    //
    // info!("简单日志记录器已初始化");
    // Ok(())
    todo!()
}

/// 记录应用程序启动信息
///
/// 记录应用程序的基本信息和启动参数
pub fn log_startup_info() {
    info!("=== 服务器温度控制系统启动 ===");
    info!("版本: {}", env!("CARGO_PKG_VERSION"));
    info!(
        "构建时间: {}",
        std::env::var("VERGEN_BUILD_TIMESTAMP").unwrap_or_else(|_| "未知".to_string())
    );
    info!(
        "Git提交: {}",
        std::env::var("VERGEN_GIT_SHA").unwrap_or_else(|_| "未知".to_string())
    );
    info!(
        "Rust版本: {}",
        std::env::var("VERGEN_RUSTC_SEMVER").unwrap_or_else(|_| "未知".to_string())
    );
    info!(
        "目标平台: {}",
        std::env::var("VERGEN_CARGO_TARGET_TRIPLE").unwrap_or_else(|_| "未知".to_string())
    );
    info!("===================================");
}

/// 记录应用程序关闭信息
///
/// 记录应用程序的关闭信息
pub fn log_shutdown_info() {
    info!("=== 服务器温度控制系统关闭 ===");
    info!("感谢使用！");
    info!("===================================");
}

/// 创建结构化日志记录器
///
/// 创建一个带有额外上下文信息的日志记录器
pub struct StructuredLogger {
    component: String,
    context: std::collections::HashMap<String, String>,
}

impl StructuredLogger {
    /// 创建新的结构化日志记录器
    ///
    /// # 参数
    /// * `component` - 组件名称
    pub fn new(component: impl Into<String>) -> Self {
        Self {
            component: component.into(),
            context: std::collections::HashMap::new(),
        }
    }

    /// 添加上下文信息
    ///
    /// # 参数
    /// * `key` - 键
    /// * `value` - 值
    pub fn with_context(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.context.insert(key.into(), value.into());
        self
    }

    /// 记录信息日志
    ///
    /// # 参数
    /// * `message` - 日志消息
    pub fn info(&self, message: &str) {
        let context_str = self.format_context();
        info!("[{}] {} {}", self.component, message, context_str);
    }

    /// 记录警告日志
    ///
    /// # 参数
    /// * `message` - 日志消息
    pub fn warn(&self, message: &str) {
        let context_str = self.format_context();
        warn!("[{}] {} {}", self.component, message, context_str);
    }

    /// 记录错误日志
    ///
    /// # 参数
    /// * `message` - 日志消息
    pub fn error(&self, message: &str) {
        let context_str = self.format_context();
        error!("[{}] {} {}", self.component, message, context_str);
    }

    /// 记录调试日志
    ///
    /// # 参数
    /// * `message` - 日志消息
    pub fn debug(&self, message: &str) {
        let context_str = self.format_context();
        debug!("[{}] {} {}", self.component, message, context_str);
    }

    /// 格式化上下文信息
    fn format_context(&self) -> String {
        if self.context.is_empty() {
            String::new()
        } else {
            let context_pairs: Vec<String> = self
                .context
                .iter()
                .map(|(k, v)| format!("{}={}", k, v))
                .collect();
            format!("[{}]", context_pairs.join(" "))
        }
    }
}

/// 性能日志记录器
///
/// 用于记录性能相关的日志信息
pub struct PerformanceLogger {
    start_time: std::time::Instant,
    operation: String,
}

impl PerformanceLogger {
    /// 开始性能监控
    ///
    /// # 参数
    /// * `operation` - 操作名称
    pub fn start(operation: impl Into<String>) -> Self {
        let operation = operation.into();
        debug!("开始操作: {}", operation);

        Self {
            start_time: std::time::Instant::now(),
            operation,
        }
    }

    /// 结束性能监控并记录耗时
    pub fn finish(self) {
        let duration = self.start_time.elapsed();
        info!("操作完成: {} (耗时: {:?})", self.operation, duration);
    }

    /// 记录中间检查点
    ///
    /// # 参数
    /// * `checkpoint` - 检查点名称
    pub fn checkpoint(&self, checkpoint: &str) {
        let duration = self.start_time.elapsed();
        debug!(
            "检查点 [{}]: {} (已耗时: {:?})",
            self.operation, checkpoint, duration
        );
    }
}
