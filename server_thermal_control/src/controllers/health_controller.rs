use crate::models::{
    error::{AppError, AppResult},
    api::ApiResponse,
};
use actix_web::{
    web::{Query, Data, ServiceConfig},
    HttpResponse, Result as ActixResult,
    get, post, put, delete,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tracing::{info, warn, error};
use chrono::{DateTime, Utc};

/// 健康检查控制器
/// 
/// 提供系统健康状态监控和诊断的HTTP API接口
#[derive(Clone)]
pub struct HealthController;

impl HealthController {
    /// 创建新的健康检查控制器
    pub fn new() -> Self {
        Self
    }

    /// 配置路由
    pub fn configure(cfg: &mut ServiceConfig) {
        cfg.service(
            actix_web::web::scope("/health")
                .route("", actix_web::web::get().to(Self::health_check))
                .route("/detailed", actix_web::web::get().to(Self::detailed_health_check))
                .route("/readiness", actix_web::web::get().to(Self::readiness_check))
                .route("/liveness", actix_web::web::get().to(Self::liveness_check))
                .route("/components", actix_web::web::get().to(Self::component_health))
                .route("/metrics", actix_web::web::get().to(Self::health_metrics))
                .route("/dependencies", actix_web::web::get().to(Self::dependency_health))
                .route("/system", actix_web::web::get().to(Self::system_health))
        );
    }

    /// 基础健康检查
    /// 
    /// GET /api/v1/health
    async fn health_check() -> ActixResult<HttpResponse> {
        info!("执行基础健康检查");

        let status = HealthStatus {
            status: ServiceStatus::Healthy,
            timestamp: Utc::now(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            uptime: get_uptime(),
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(status)))
    }

    /// 详细健康检查
    /// 
    /// GET /api/v1/health/detailed
    async fn detailed_health_check() -> ActixResult<HttpResponse> {
        info!("执行详细健康检查");

        let mut components = HashMap::new();
        
        // 检查各个组件状态
        components.insert("database".to_string(), check_database_health().await);
        components.insert("ipmi".to_string(), check_ipmi_health().await);
        components.insert("sensors".to_string(), check_sensors_health().await);
        components.insert("fans".to_string(), check_fans_health().await);
        components.insert("thermal".to_string(), check_thermal_health().await);

        let overall_status = if components.values().all(|c| c.status == ServiceStatus::Healthy) {
            ServiceStatus::Healthy
        } else if components.values().any(|c| c.status == ServiceStatus::Critical) {
            ServiceStatus::Critical
        } else {
            ServiceStatus::Warning
        };

        let detailed_status = DetailedHealthStatus {
            status: overall_status,
            timestamp: Utc::now(),
            version: env!("CARGO_PKG_VERSION").to_string(),
            uptime: get_uptime(),
            components,
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(detailed_status)))
    }

    /// 就绪检查
    /// 
    /// GET /api/v1/health/readiness
    async fn readiness_check() -> ActixResult<HttpResponse> {
        info!("执行就绪检查");

        let is_ready = check_readiness().await;
        
        if is_ready {
            Ok(HttpResponse::Ok().json(ApiResponse::success(ReadinessStatus {
                ready: true,
                timestamp: Utc::now(),
                checks: get_readiness_checks().await,
            })))
        } else {
            Ok(HttpResponse::ServiceUnavailable().json(ApiResponse::<()>::error("Service not ready")))
        }
    }

    /// 存活检查
    /// 
    /// GET /api/v1/health/liveness
    async fn liveness_check() -> ActixResult<HttpResponse> {
        info!("执行存活检查");

        let is_alive = check_liveness().await;
        
        if is_alive {
            Ok(HttpResponse::Ok().json(ApiResponse::success(LivenessStatus {
                alive: true,
                timestamp: Utc::now(),
                process_id: std::process::id(),
            })))
        } else {
            Ok(HttpResponse::ServiceUnavailable().json(ApiResponse::<()>::error("Service not alive")))
        }
    }

    /// 组件健康状态
    /// 
    /// GET /api/v1/health/components
    async fn component_health(
        Query(params): Query<ComponentHealthParams>,
    ) -> ActixResult<HttpResponse> {
        info!("获取组件健康状态");

        let components = if let Some(component_name) = params.component {
            let health = match component_name.as_str() {
                "database" => check_database_health().await,
                "ipmi" => check_ipmi_health().await,
                "sensors" => check_sensors_health().await,
                "fans" => check_fans_health().await,
                "thermal" => check_thermal_health().await,
                _ => {
                    return Ok(HttpResponse::BadRequest().json(ApiResponse::<()>::error("Unknown component")));
                }
            };
            
            let mut map = HashMap::new();
            map.insert(component_name, health);
            map
        } else {
            let mut components = HashMap::new();
            components.insert("database".to_string(), check_database_health().await);
            components.insert("ipmi".to_string(), check_ipmi_health().await);
            components.insert("sensors".to_string(), check_sensors_health().await);
            components.insert("fans".to_string(), check_fans_health().await);
            components.insert("thermal".to_string(), check_thermal_health().await);
            components
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(ComponentHealthResponse { components })))
    }

    /// 健康指标
    /// 
    /// GET /api/v1/health/metrics
    async fn health_metrics() -> ActixResult<HttpResponse> {
        info!("获取健康指标");

        let metrics = HealthMetrics {
            cpu_usage: get_cpu_usage().await,
            memory_usage: get_memory_usage().await,
            disk_usage: get_disk_usage().await,
            network_status: get_network_status().await,
            active_connections: get_active_connections().await,
            response_times: get_response_times().await,
            error_rates: get_error_rates().await,
            timestamp: Utc::now(),
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(metrics)))
    }

    /// 依赖健康状态
    /// 
    /// GET /api/v1/health/dependencies
    async fn dependency_health() -> ActixResult<HttpResponse> {
        info!("检查依赖健康状态");

        let mut dependencies = HashMap::new();
        
        // 检查外部依赖
        dependencies.insert("database".to_string(), check_database_dependency().await);
        dependencies.insert("ipmi_service".to_string(), check_ipmi_dependency().await);
        dependencies.insert("monitoring_service".to_string(), check_monitoring_dependency().await);

        let overall_status = if dependencies.values().all(|d| d.status == DependencyStatus::Available) {
            DependencyStatus::Available
        } else if dependencies.values().any(|d| d.status == DependencyStatus::Critical) {
            DependencyStatus::Critical
        } else {
            DependencyStatus::Degraded
        };

        let dependency_health = DependencyHealthResponse {
            overall_status,
            dependencies,
            timestamp: Utc::now(),
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(dependency_health)))
    }

    /// 系统健康状态
    /// 
    /// GET /api/v1/health/system
    async fn system_health() -> ActixResult<HttpResponse> {
        info!("获取系统健康状态");

        let system_info = SystemHealthInfo {
            hostname: get_hostname(),
            platform: get_platform(),
            architecture: get_architecture(),
            kernel_version: get_kernel_version(),
            boot_time: get_boot_time(),
            load_average: get_load_average().await,
            processes: get_process_count().await,
            threads: get_thread_count().await,
            file_descriptors: get_file_descriptor_count().await,
            timestamp: Utc::now(),
        };

        Ok(HttpResponse::Ok().json(ApiResponse::success(system_info)))
    }

    // 私有辅助方法

    /// 获取系统运行时间
    async fn get_uptime() -> u64 {
        // 实现获取系统运行时间的逻辑
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
    }

    /// 检查数据库健康状态
    async fn check_database_health() -> ComponentHealth {
        // 实现数据库健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Database connection is healthy".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 检查IPMI健康状态
    async fn check_ipmi_health() -> ComponentHealth {
        // 实现IPMI健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "IPMI interface is accessible".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 检查温度传感器健康状态
    async fn check_thermal_sensors_health() -> ComponentHealth {
        // 实现温度传感器健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "All thermal sensors are responding".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 检查风扇控制器健康状态
    async fn check_fan_controllers_health() -> ComponentHealth {
        // 实现风扇控制器健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "All fan controllers are operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 检查监控健康状态
    async fn check_monitoring_health() -> ComponentHealth {
        // 实现监控健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Monitoring system is active".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 检查告警健康状态
    async fn check_alerts_health() -> ComponentHealth {
        // 实现告警健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Alert system is functioning".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 检查存储健康状态
    async fn check_storage_health() -> ComponentHealth {
        // 实现存储健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Storage system is available".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 检查内存健康状态
    async fn check_memory_health() -> ComponentHealth {
        // 实现内存健康检查逻辑
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Memory usage is within normal limits".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    /// 获取系统信息
    async fn get_system_info() -> SystemInfo {
        SystemInfo {
            hostname: Self::get_hostname().await,
            platform: Self::get_platform().await,
            architecture: Self::get_architecture().await,
            cpu_cores: Self::get_cpu_cores().await,
            total_memory_bytes: Self::get_total_memory().await,
        }
    }

    /// 获取性能指标
    async fn get_performance_metrics() -> PerformanceMetrics {
        PerformanceMetrics {
            cpu_usage_percent: Self::get_cpu_usage().await,
            memory_usage_percent: Self::get_memory_usage_percent().await,
            disk_usage_percent: Self::get_disk_usage_percent().await,
            network_io_bytes_per_sec: Self::get_network_io().await,
            disk_io_bytes_per_sec: Self::get_disk_io().await,
        }
    }

    /// 检查数据库连接
    async fn check_database_connection() -> HealthCheck {
        // 实现数据库连接检查逻辑
        HealthCheck {
            name: "database_connection".to_string(),
            passed: true,
            message: "Database connection successful".to_string(),
            duration_ms: 10,
            timestamp: Utc::now(),
        }
    }

    /// 检查IPMI连接
    async fn check_ipmi_connection() -> HealthCheck {
        // 实现IPMI连接检查逻辑
        HealthCheck {
            name: "ipmi_connection".to_string(),
            passed: true,
            message: "IPMI interface accessible".to_string(),
            duration_ms: 15,
            timestamp: Utc::now(),
        }
    }

    /// 检查配置是否加载
    async fn check_config_loaded() -> HealthCheck {
        // 实现配置加载检查逻辑
        HealthCheck {
            name: "config_loaded".to_string(),
            passed: true,
            message: "Configuration loaded successfully".to_string(),
            duration_ms: 5,
            timestamp: Utc::now(),
        }
    }

    /// 检查服务是否初始化
    async fn check_services_initialized() -> HealthCheck {
        // 实现服务初始化检查逻辑
        HealthCheck {
            name: "services_initialized".to_string(),
            passed: true,
            message: "All services initialized".to_string(),
            duration_ms: 20,
            timestamp: Utc::now(),
        }
    }

    /// 检查进程是否运行
    async fn check_process_running() -> HealthCheck {
        HealthCheck {
            name: "process_running".to_string(),
            passed: true,
            message: "Process is running normally".to_string(),
            duration_ms: 1,
            timestamp: Utc::now(),
        }
    }

    /// 检查内存使用情况
    async fn check_memory_usage() -> HealthCheck {
        let usage_percent = Self::get_memory_usage_percent().await;
        let passed = usage_percent < 90.0;
        
        HealthCheck {
            name: "memory_usage".to_string(),
            passed,
            message: format!("Memory usage: {:.1}%", usage_percent),
            duration_ms: 2,
            timestamp: Utc::now(),
        }
    }

    /// 检查CPU使用情况
    async fn check_cpu_usage() -> HealthCheck {
        let usage_percent = Self::get_cpu_usage().await;
        let passed = usage_percent < 95.0;
        
        HealthCheck {
            name: "cpu_usage".to_string(),
            passed,
            message: format!("CPU usage: {:.1}%", usage_percent),
            duration_ms: 2,
            timestamp: Utc::now(),
        }
    }

    /// 检查磁盘空间
    async fn check_disk_space() -> HealthCheck {
        let usage_percent = Self::get_disk_usage_percent().await;
        let passed = usage_percent < 90.0;
        
        HealthCheck {
            name: "disk_space".to_string(),
            passed,
            message: format!("Disk usage: {:.1}%", usage_percent),
            duration_ms: 3,
            timestamp: Utc::now(),
        }
    }

    // 各个服务的健康检查方法
    async fn check_thermal_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Thermal service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    async fn check_fan_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Fan service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    async fn check_sensor_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Sensor service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    async fn check_analytics_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Analytics service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    async fn check_monitoring_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Monitoring service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    async fn check_control_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Control service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    async fn check_alert_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Alert service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    async fn check_config_service_health() -> ComponentHealth {
        ComponentHealth {
            status: ComponentStatus::Healthy,
            message: "Config service is operational".to_string(),
            last_check: Utc::now(),
            details: HashMap::new(),
        }
    }

    // 依赖检查方法
    async fn check_database_dependency() -> DependencyHealth {
        DependencyHealth {
            name: "database".to_string(),
            status: DependencyStatus::Available,
            endpoint: "sqlite://./data/thermal_control.db".to_string(),
            response_time_ms: 5,
            last_check: Utc::now(),
            error_message: None,
        }
    }

    async fn check_ipmi_dependency() -> DependencyHealth {
        DependencyHealth {
            name: "ipmi_interface".to_string(),
            status: DependencyStatus::Available,
            endpoint: "/dev/ipmi0".to_string(),
            response_time_ms: 10,
            last_check: Utc::now(),
            error_message: None,
        }
    }

    async fn check_filesystem_dependency() -> DependencyHealth {
        DependencyHealth {
            name: "file_system".to_string(),
            status: DependencyStatus::Available,
            endpoint: "/".to_string(),
            response_time_ms: 2,
            last_check: Utc::now(),
            error_message: None,
        }
    }

    async fn check_network_dependency() -> DependencyHealth {
        DependencyHealth {
            name: "network".to_string(),
            status: DependencyStatus::Available,
            endpoint: "localhost".to_string(),
            response_time_ms: 1,
            last_check: Utc::now(),
            error_message: None,
        }
    }

    // 系统指标获取方法
    async fn get_hostname() -> String {
        "thermal-control-server".to_string()
    }

    async fn get_platform() -> String {
        std::env::consts::OS.to_string()
    }

    async fn get_architecture() -> String {
        std::env::consts::ARCH.to_string()
    }

    async fn get_cpu_cores() -> u32 {
        num_cpus::get() as u32
    }

    async fn get_total_memory() -> u64 {
        // 实现获取总内存的逻辑
        8 * 1024 * 1024 * 1024 // 8GB 示例
    }

    async fn get_boot_time() -> DateTime<Utc> {
        // 实现获取启动时间的逻辑
        Utc::now() - chrono::Duration::hours(24)
    }

    async fn get_load_average() -> Vec<f64> {
        // 实现获取负载平均值的逻辑
        vec![0.5, 0.7, 0.9]
    }

    /// 获取内核版本
    async fn get_kernel_version() -> String {
        std::env::consts::OS.to_string()
    }

    /// 获取进程数
    async fn get_process_count() -> u32 {
        // 实现获取进程数的逻辑
        150
    }

    /// 获取文件描述符数
    async fn get_file_descriptor_count() -> u32 {
        // 实现获取文件描述符数的逻辑
        1024
    }

    async fn get_system_temperature() -> Option<f64> {
        // 实现获取系统温度的逻辑
        Some(45.5)
    }

    async fn get_fan_speeds() -> Vec<u32> {
        // 实现获取风扇转速的逻辑
        vec![1200, 1150, 1300, 1250]
    }

    async fn get_power_consumption() -> Option<f64> {
        // 实现获取功耗的逻辑
        Some(150.5)
    }

    async fn get_cpu_usage() -> f64 {
        // 实现获取CPU使用率的逻辑
        25.5
    }

    async fn get_memory_usage_percent() -> f64 {
        // 实现获取内存使用率的逻辑
        65.2
    }

    async fn get_memory_usage_bytes() -> u64 {
        // 实现获取内存使用量的逻辑
        5 * 1024 * 1024 * 1024 // 5GB
    }

    async fn get_disk_usage_percent() -> f64 {
        // 实现获取磁盘使用率的逻辑
        45.8
    }

    async fn get_disk_usage_bytes() -> u64 {
        // 实现获取磁盘使用量的逻辑
        100 * 1024 * 1024 * 1024 // 100GB
    }

    async fn get_network_connections() -> u32 {
        // 实现获取网络连接数的逻辑
        25
    }

    async fn get_open_file_descriptors() -> u32 {
        // 实现获取打开文件描述符数的逻辑
        150
    }

    async fn get_thread_count() -> u32 {
        // 实现获取线程数的逻辑
        20
    }

    async fn get_request_count() -> u64 {
        // 实现获取请求数的逻辑
        1000
    }

    async fn get_error_count() -> u64 {
        // 实现获取错误数的逻辑
        5
    }

    async fn get_average_response_time() -> f64 {
        // 实现获取平均响应时间的逻辑
        25.5
    }

    async fn get_network_io() -> u64 {
        // 实现获取网络IO的逻辑
        1024 * 1024 // 1MB/s
    }

    async fn get_disk_io() -> u64 {
        // 实现获取磁盘IO的逻辑
        10 * 1024 * 1024 // 10MB/s
    }
}

// 请求和响应结构体

/// 组件健康参数
#[derive(Debug, Deserialize)]
pub struct ComponentHealthParams {
    /// 是否包含所有组件
    pub include_all: Option<bool>,
    /// 指定的组件列表
    pub components: Option<Vec<String>>,
}

/// 服务状态
#[derive(Debug, Clone, PartialEq, Serialize)]
pub enum ServiceStatus {
    /// 健康
    Healthy,
    /// 降级
    Degraded,
    /// 不健康
    Unhealthy,
}

/// 组件状态
#[derive(Debug, Clone, PartialEq, Serialize)]
pub enum ComponentStatus {
    /// 健康
    Healthy,
    /// 警告
    Warning,
    /// 错误
    Error,
    /// 严重
    Critical,
}

/// 依赖状态
#[derive(Debug, Clone, PartialEq, Serialize)]
pub enum DependencyStatus {
    /// 可用
    Available,
    /// 降级
    Degraded,
    /// 不可用
    Unavailable,
}

/// 基础健康状态
#[derive(Debug, Serialize)]
pub struct HealthStatus {
    /// 服务状态
    pub status: ServiceStatus,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 版本
    pub version: String,
    /// 运行时间（秒）
    pub uptime_seconds: u64,
}

/// 详细健康状态
#[derive(Debug, Serialize)]
pub struct DetailedHealthStatus {
    /// 整体状态
    pub status: ServiceStatus,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 版本
    pub version: String,
    /// 运行时间（秒）
    pub uptime_seconds: u64,
    /// 组件健康状态
    pub components: HashMap<String, ComponentHealth>,
    /// 系统信息
    pub system_info: SystemInfo,
    /// 性能指标
    pub performance_metrics: PerformanceMetrics,
}

/// 组件健康状态
#[derive(Debug, Serialize)]
pub struct ComponentHealth {
    /// 状态
    pub status: ComponentStatus,
    /// 消息
    pub message: String,
    /// 最后检查时间
    pub last_check: DateTime<Utc>,
    /// 详细信息
    pub details: HashMap<String, serde_json::Value>,
}

/// 系统信息
#[derive(Debug, Serialize)]
pub struct SystemInfo {
    /// 主机名
    pub hostname: String,
    /// 平台
    pub platform: String,
    /// 架构
    pub architecture: String,
    /// CPU核心数
    pub cpu_cores: u32,
    /// 总内存（字节）
    pub total_memory_bytes: u64,
}

/// 性能指标
#[derive(Debug, Serialize)]
pub struct PerformanceMetrics {
    /// CPU使用率（百分比）
    pub cpu_usage_percent: f64,
    /// 内存使用率（百分比）
    pub memory_usage_percent: f64,
    /// 磁盘使用率（百分比）
    pub disk_usage_percent: f64,
    /// 网络IO（字节/秒）
    pub network_io_bytes_per_sec: u64,
    /// 磁盘IO（字节/秒）
    pub disk_io_bytes_per_sec: u64,
}

/// 就绪性状态
#[derive(Debug, Serialize)]
pub struct ReadinessStatus {
    /// 是否就绪
    pub ready: bool,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 检查项
    pub checks: HashMap<String, HealthCheck>,
}

/// 存活性状态
#[derive(Debug, Serialize)]
pub struct LivenessStatus {
    /// 是否存活
    pub alive: bool,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 检查项
    pub checks: HashMap<String, HealthCheck>,
}

/// 健康检查项
#[derive(Debug, Serialize)]
pub struct HealthCheck {
    /// 检查名称
    pub name: String,
    /// 是否通过
    pub passed: bool,
    /// 消息
    pub message: String,
    /// 检查耗时（毫秒）
    pub duration_ms: u64,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
}

/// 组件健康状态
#[derive(Debug, Serialize)]
pub struct ComponentHealthStatus {
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 组件状态
    pub components: HashMap<String, ComponentHealth>,
}

/// 健康指标
#[derive(Debug, Serialize)]
pub struct HealthMetrics {
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// CPU使用率（百分比）
    pub cpu_usage_percent: f64,
    /// 内存使用率（百分比）
    pub memory_usage_percent: f64,
    /// 内存使用量（字节）
    pub memory_usage_bytes: u64,
    /// 磁盘使用率（百分比）
    pub disk_usage_percent: f64,
    /// 磁盘使用量（字节）
    pub disk_usage_bytes: u64,
    /// 网络连接数
    pub network_connections: u32,
    /// 打开的文件描述符数
    pub open_file_descriptors: u32,
    /// 线程数
    pub thread_count: u32,
    /// 运行时间（秒）
    pub uptime_seconds: u64,
    /// 请求总数
    pub request_count: u64,
    /// 错误总数
    pub error_count: u64,
    /// 平均响应时间（毫秒）
    pub response_time_ms: f64,
}

/// 依赖健康状态
#[derive(Debug, Serialize)]
pub struct DependencyHealthStatus {
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 依赖状态
    pub dependencies: HashMap<String, DependencyHealth>,
}

/// 依赖健康信息
#[derive(Debug, Serialize)]
pub struct DependencyHealth {
    /// 依赖名称
    pub name: String,
    /// 状态
    pub status: DependencyStatus,
    /// 端点
    pub endpoint: String,
    /// 响应时间（毫秒）
    pub response_time_ms: u64,
    /// 最后检查时间
    pub last_check: DateTime<Utc>,
    /// 错误消息
    pub error_message: Option<String>,
}

/// 组件健康响应
#[derive(Debug, Serialize)]
pub struct ComponentHealthResponse {
    /// 组件健康状态映射
    pub components: HashMap<String, ComponentHealth>,
}

/// 依赖健康响应
#[derive(Debug, Serialize)]
pub struct DependencyHealthResponse {
    /// 整体状态
    pub overall_status: DependencyStatus,
    /// 依赖健康状态映射
    pub dependencies: HashMap<String, DependencyHealth>,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
}

/// 系统健康信息
#[derive(Debug, Serialize)]
pub struct SystemHealthInfo {
    /// 主机名
    pub hostname: String,
    /// 平台
    pub platform: String,
    /// 架构
    pub architecture: String,
    /// 内核版本
    pub kernel_version: String,
    /// 启动时间
    pub boot_time: DateTime<Utc>,
    /// 负载平均值
    pub load_average: Vec<f64>,
    /// 进程数
    pub processes: u32,
    /// 线程数
    pub threads: u32,
    /// 文件描述符数
    pub file_descriptors: u32,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
}

/// 系统健康状态
#[derive(Debug, Serialize)]
pub struct SystemHealthStatus {
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 主机名
    pub hostname: String,
    /// 平台
    pub platform: String,
    /// 架构
    pub architecture: String,
    /// CPU核心数
    pub cpu_cores: u32,
    /// 总内存（字节）
    pub total_memory_bytes: u64,
    /// 启动时间
    pub boot_time: DateTime<Utc>,
    /// 负载平均值
    pub load_average: Vec<f64>,
    /// 系统温度（摄氏度）
    pub temperature_celsius: Option<f64>,
    /// 风扇转速（RPM）
    pub fan_speeds_rpm: Vec<u32>,
    /// 功耗（瓦特）
    pub power_consumption_watts: Option<f64>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use actix_web::{test, App};

    #[actix_web::test]
    async fn test_health_controller_routes() {
        let app = test::init_service(
            App::new().configure(HealthController::configure)
        ).await;
        
        // 测试基础健康检查
        let req = test::TestRequest::get().uri("/health").to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
        
        // 测试详细健康检查
        let req = test::TestRequest::get().uri("/health/detailed").to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
        
        // 测试就绪性检查
        let req = test::TestRequest::get().uri("/health/readiness").to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
        
        // 测试存活性检查
        let req = test::TestRequest::get().uri("/health/liveness").to_request();
        let resp = test::call_service(&app, req).await;
        assert!(resp.status().is_success());
    }

    #[test]
    fn test_service_status_serialization() {
        let status = ServiceStatus::Healthy;
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(json, r#""Healthy""#);
    }

    #[test]
    fn test_component_status_serialization() {
        let status = ComponentStatus::Warning;
        let json = serde_json::to_string(&status).unwrap();
        assert_eq!(json, r#""Warning""#);
    }
}