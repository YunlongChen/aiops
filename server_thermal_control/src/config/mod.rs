use serde::{Deserialize, Serialize};
use std::env;

/// 应用程序配置结构体
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub server: ServerConfig,
    pub database: DatabaseConfig,
    pub redis: RedisConfig,
    pub ipmi: IpmiConfig,
    pub monitoring: MonitoringConfig,
    pub control: ControlConfig,
    pub alert: AlertConfig,
    pub logging: LoggingConfig,
    pub analytics: AnalyticsConfig,
    pub cache: CacheConfig,
    pub security: SecurityConfig,
    pub performance: PerformanceConfig,
}

/// 服务器配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServerConfig {
    pub host: String,
    pub port: u16,
    pub workers: Option<usize>,
    pub keep_alive: u64,
    pub client_timeout: u64,
    pub client_shutdown: u64,
    pub cors_origins: Vec<String>,
}

/// 数据库配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
    pub min_connections: u32,
    pub connect_timeout: u64,
    pub idle_timeout: u64,
}

/// Redis配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RedisConfig {
    pub url: String,
    pub max_connections: u32,
    pub connect_timeout: u64,
    pub command_timeout: u64,
}

/// IPMI配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IpmiConfig {
    pub host: String,
    pub username: String,
    pub password: String,
    pub interface: String,
    pub timeout: u64,
    pub retries: u32,
}

/// 监控配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MonitoringConfig {
    pub enabled: bool,
    pub interval: u64,
    pub retention_days: u32,
    pub alert_threshold_temp: f64,
    pub alert_threshold_fan: u32,
}

/// 控制配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ControlConfig {
    pub enabled: bool,
    pub mode: String,
    pub temp_target: f64,
    pub temp_hysteresis: f64,
    pub fan_min_speed: u32,
    pub fan_max_speed: u32,
    pub update_interval: u64,
}

/// 告警配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AlertConfig {
    pub enabled: bool,
    pub email: EmailConfig,
    pub webhook: WebhookConfig,
}

/// 邮件配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EmailConfig {
    pub enabled: bool,
    pub smtp_host: String,
    pub smtp_port: u16,
    pub username: String,
    pub password: String,
    pub from: String,
    pub to: String,
}

/// Webhook配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WebhookConfig {
    pub enabled: bool,
    pub url: String,
}

/// 日志配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoggingConfig {
    pub level: String,
    pub format: String,
    pub file_enabled: bool,
    pub file_path: String,
    pub file_max_size: String,
    pub file_max_files: u32,
}

/// 分析配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalyticsConfig {
    pub enabled: bool,
    pub interval: u64,
    pub history_days: u32,
    pub prediction_enabled: bool,
    pub ml_model_path: String,
}

/// 缓存配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CacheConfig {
    pub ttl: u64,
    pub max_size: usize,
    pub enabled: bool,
}

/// 安全配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub jwt_secret: String,
    pub jwt_expiration: u64,
    pub api_key: String,
    pub cors_origins: Vec<String>,
    pub rate_limit_requests: u32,
    pub rate_limit_window: u64,
}

/// 性能配置
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceConfig {
    pub worker_threads: usize,
    pub max_request_size: String,
    pub request_timeout: u64,
    pub keep_alive_timeout: u64,
    pub graceful_shutdown_timeout: u64,
}

impl Default for AppConfig {
    fn default() -> Self {
        Self {
            server: ServerConfig {
                host: "127.0.0.1".to_string(),
                port: 8080,
                workers: None,
                keep_alive: 75,
                client_timeout: 5000,
                client_shutdown: 5000,
                cors_origins: vec!["http://localhost:3000".to_string()],
            },
            database: DatabaseConfig {
                url: "postgresql://thermal_user:thermal_pass@localhost:5432/thermal_control".to_string(),
                max_connections: 10,
                min_connections: 1,
                connect_timeout: 30,
                idle_timeout: 600,
            },
            redis: RedisConfig {
                url: "redis://localhost:6379/0".to_string(),
                max_connections: 10,
                connect_timeout: 5,
                command_timeout: 5,
            },
            ipmi: IpmiConfig {
                host: "192.168.1.100".to_string(),
                username: "admin".to_string(),
                password: "admin123".to_string(),
                interface: "lanplus".to_string(),
                timeout: 10,
                retries: 3,
            },
            monitoring: MonitoringConfig {
                enabled: true,
                interval: 30,
                retention_days: 30,
                alert_threshold_temp: 80.0,
                alert_threshold_fan: 1000,
            },
            control: ControlConfig {
                enabled: true,
                mode: "auto".to_string(),
                temp_target: 65.0,
                temp_hysteresis: 5.0,
                fan_min_speed: 20,
                fan_max_speed: 100,
                update_interval: 10,
            },
            alert: AlertConfig {
                enabled: true,
                email: EmailConfig {
                    enabled: false,
                    smtp_host: "smtp.gmail.com".to_string(),
                    smtp_port: 587,
                    username: "your-email@gmail.com".to_string(),
                    password: "your-app-password".to_string(),
                    from: "thermal-control@example.com".to_string(),
                    to: "admin@example.com".to_string(),
                },
                webhook: WebhookConfig {
                    enabled: false,
                    url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL".to_string(),
                },
            },
            logging: LoggingConfig {
                level: "info".to_string(),
                format: "json".to_string(),
                file_enabled: true,
                file_path: "logs/thermal-control.log".to_string(),
                file_max_size: "10MB".to_string(),
                file_max_files: 5,
            },
            analytics: AnalyticsConfig {
                enabled: true,
                interval: 300,
                history_days: 7,
                prediction_enabled: true,
                ml_model_path: "models/thermal_prediction.onnx".to_string(),
            },
            cache: CacheConfig {
                ttl: 300,
                max_size: 1000,
                enabled: true,
            },
            security: SecurityConfig {
                jwt_secret: "your-super-secret-jwt-key-change-this-in-production".to_string(),
                jwt_expiration: 3600,
                api_key: "your-api-key-for-external-access".to_string(),
                cors_origins: vec!["http://localhost:3000".to_string(), "http://localhost:8080".to_string()],
                rate_limit_requests: 100,
                rate_limit_window: 60,
            },
            performance: PerformanceConfig {
                worker_threads: 4,
                max_request_size: "1MB".to_string(),
                request_timeout: 30,
                keep_alive_timeout: 5,
                graceful_shutdown_timeout: 30,
            },
        }
    }
}

impl AppConfig {
    /// 从环境变量和配置文件加载配置
    /// 加载应用配置
    /// 
    /// 优先级：环境变量 > 配置文件 > 默认值
    /// 
    /// # Returns
    /// * `Result<Self, Box<dyn std::error::Error>>` - 配置对象或错误
    pub async fn load() -> Result<Self, Box<dyn std::error::Error>> {
        let mut config = Self::default();
        
        // 尝试从配置文件加载
        let config_paths = vec![
            "config/app.toml",
            "./config/app.toml",
            "../config/app.toml",
        ];
        
        for path in config_paths {
            if std::path::Path::new(path).exists() {
                match std::fs::read_to_string(path) {
                    Ok(content) => {
                        match toml::from_str::<AppConfig>(&content) {
                            Ok(file_config) => {
                                config = file_config;
                                println!("Loaded configuration from: {}", path);
                                break;
                            }
                            Err(e) => {
                                eprintln!("Failed to parse config file {}: {}", path, e);
                            }
                        }
                    }
                    Err(e) => {
                        eprintln!("Failed to read config file {}: {}", path, e);
                    }
                }
            }
        }
        
        // 从环境变量覆盖配置
        if let Ok(host) = env::var("APP_HOST") {
            config.server.host = host;
        }
        
        if let Ok(port) = env::var("APP_PORT") {
            config.server.port = port.parse()?;
        }
        
        if let Ok(db_url) = env::var("DATABASE_URL") {
            config.database.url = db_url;
        }
        
        if let Ok(redis_url) = env::var("REDIS_URL") {
            config.redis.url = redis_url;
        }
        
        // 可以添加更多环境变量覆盖逻辑
        
        Ok(config)
    }
}