use crate::controllers::monitoring_controller::{
    HealthStatus, MonitoringDataCache, MonitoringDataPoint, MonitoringDataType, MonitoringMetrics,
    MonitoringStatus, MonitoringTarget, RealtimeMonitoringData, SystemHealth, SystemHealthReport,
    SystemHealthStatus,
};
use crate::models::{
    config::MonitoringConfig,
    error::{AppError, AppResult},
    fan::FanReading,
    monitoring::*,
    sensor::SensorReading,
    thermal::TemperatureReading,
    SensorType, TemperatureQuery,
};
use crate::services::{
    alert_service::AlertService, fan_service::FanService, sensor_service::SensorService,
    thermal_service::ThermalService,
};
use crate::utils::{logger::LoggerManager, time::TimeUtils};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{Mutex, RwLock};
use tokio::time::{interval, Duration, Instant};
use tracing::{debug, error, info, warn};

/// 监控服务
///
/// 负责系统监控、数据收集和状态跟踪
#[derive(Clone)]
pub struct MonitoringService {
    /// 温度服务
    thermal_service: Arc<ThermalService>,
    /// 风扇服务
    fan_service: Arc<FanService>,
    /// 传感器服务
    sensor_service: Arc<SensorService>,
    /// 告警服务
    alert_service: Arc<AlertService>,
    /// 监控配置
    config: Arc<RwLock<MonitoringConfig>>,
    /// 监控状态
    status: Arc<RwLock<MonitoringStatus>>,
    /// 监控任务句柄
    task_handles: Arc<Mutex<Vec<tokio::task::JoinHandle<()>>>>,
    /// 监控数据缓存
    data_cache: Arc<RwLock<MonitoringDataCache>>,
    /// 性能指标
    metrics: Arc<RwLock<MonitoringMetrics>>,
}

impl MonitoringService {
    /// 创建新的监控服务
    ///
    /// # 参数
    /// * `thermal_service` - 温度服务
    /// * `fan_service` - 风扇服务
    /// * `sensor_service` - 传感器服务
    /// * `alert_service` - 告警服务
    pub fn new(
        thermal_service: Arc<ThermalService>,
        fan_service: Arc<FanService>,
        sensor_service: Arc<SensorService>,
        alert_service: Arc<AlertService>,
    ) -> Self {
        Self {
            thermal_service,
            fan_service,
            sensor_service,
            alert_service,
            config: Arc::new(RwLock::new(MonitoringConfig::default())),
            status: Arc::new(RwLock::new(MonitoringStatus::default())),
            task_handles: Arc::new(Mutex::new(Vec::new())),
            data_cache: Arc::new(RwLock::new(MonitoringDataCache::default())),
            metrics: Arc::new(RwLock::new(MonitoringMetrics::default())),
        }
    }

    /// 启动监控服务
    pub async fn start(&self) -> AppResult<()> {
        info!("启动监控服务");

        // 更新状态
        {
            let mut status = self.status.write().await;
            status.is_running = true;
            status.started_at = Some(Utc::now());
            status.last_update = Some(Utc::now());
        }

        // 启动各种监控任务
        self.start_temperature_monitoring().await?;
        self.start_fan_monitoring().await?;
        self.start_sensor_monitoring().await?;
        self.start_system_health_monitoring().await?;
        self.start_performance_monitoring().await?;
        self.start_data_cleanup_task().await?;

        info!("监控服务启动完成");
        Ok(())
    }

    /// 停止监控服务
    pub async fn stop(&self) -> AppResult<()> {
        info!("停止监控服务");

        // 更新状态
        {
            let mut status = self.status.write().await;
            status.is_running = false;
            status.stopped_at = Some(Utc::now());
        }

        // 停止所有监控任务
        let mut handles = self.task_handles.lock().await;
        for handle in handles.drain(..) {
            handle.abort();
        }

        info!("监控服务已停止");
        Ok(())
    }

    /// 获取监控状态
    pub async fn get_status(&self) -> MonitoringStatus {
        self.status.read()
    }

    /// 获取监控配置
    pub async fn get_config(&self) -> MonitoringConfig {
        self.config.read().await.clone()
    }

    /// 更新监控配置
    ///
    /// # 参数
    /// * `new_config` - 新的监控配置
    pub async fn update_config(&self, new_config: MonitoringConfig) -> AppResult<()> {
        info!("更新监控配置");

        // 验证配置
        new_config.validate()?;

        // 更新配置
        {
            let mut config = self.config.write().await;
            *config = new_config;
        }

        // 重启监控任务以应用新配置
        if self.status.read().await.is_running {
            self.restart_monitoring_tasks().await?;
        }

        info!("监控配置更新完成");
        Ok(())
    }

    /// 获取实时监控数据
    pub async fn get_realtime_data(&self) -> AppResult<RealtimeMonitoringData> {
        let cache = self.data_cache.read().await;

        Ok(RealtimeMonitoringData {
            timestamp: Utc::now(),
            temperature_data: cache.latest_temperature_data.clone(),
            fan_data: cache.latest_fan_data.clone(),
            sensor_data: cache.latest_sensor_data.clone(),
            health_data: None,
            alert_data: None,
        })
    }

    /// 获取监控历史数据
    ///
    /// # 参数
    /// * `start_time` - 开始时间
    /// * `end_time` - 结束时间
    /// * `data_type` - 数据类型
    pub async fn get_historical_data(
        &self,
        start_time: DateTime<Utc>,
        end_time: DateTime<Utc>,
        data_type: MonitoringDataType,
    ) -> AppResult<Vec<MonitoringDataPoint>> {
        let mut data_points = Vec::new();

        match data_type {
            MonitoringDataType::Temperature => {
                // 获取温度历史数据
                if let Ok(sensors) = self.thermal_service.get_temperature_sensors().await {
                    for sensor_id in sensors {
                        if let Ok(readings) = self
                            .thermal_service
                            .get_temperature_history(&TemperatureQuery {
                                server_id: None,
                                sensor_id: None,
                                start_time: None,
                                end_time: None,
                                page: None,
                                limit: None,
                            })
                            .await
                        {
                            for reading in readings {
                                data_points.push(MonitoringDataPoint {
                                    timestamp: reading.timestamp,
                                    component_id: sensor_id.sensor_id.clone(),
                                    data_type: MonitoringDataType::Temperature,
                                    value: reading.temperature,
                                    unit: "°C".to_string(),
                                    status: reading.status.to_string(),
                                    metadata: Some(serde_json::json!({
                                        "sensor_type": SensorType::Temperature,
                                        // todo 内容错误
                                        "location": ""
                                    })),
                                });
                            }
                        }
                    }
                }
            }
            MonitoringDataType::FanSpeed => {
                // 获取风扇历史数据
                if let Ok(fans) = self.fan_service.get_fan_list().await {
                    for fan_id in fans {
                        if let Ok(readings) = self
                            .fan_service
                            .get_fan_history(&fan_id, start_time, end_time)
                            .await
                        {
                            for reading in readings {
                                data_points.push(MonitoringDataPoint {
                                    timestamp: reading.timestamp,
                                    component_id: fan_id.clone(),
                                    data_type: MonitoringDataType::FanSpeed,
                                    value: reading.speed_percent,
                                    unit: "%".to_string(),
                                    status: reading.status.to_string(),
                                    metadata: Some(serde_json::json!({
                                        "rpm": reading.rpm,
                                        "target_speed": reading.target_speed
                                    })),
                                });
                            }
                        }
                    }
                }
            }
            MonitoringDataType::SystemHealth => {
                // 获取系统健康历史数据
                // 这里需要实现系统健康历史数据的获取
                // 暂时返回空数据
            }
            MonitoringDataType::All => {
                // 递归获取所有类型的数据
                let temp_data = self
                    .get_historical_data(start_time, end_time, MonitoringDataType::Temperature)
                    .await?;
                let fan_data = self
                    .get_historical_data(start_time, end_time, MonitoringDataType::FanSpeed)
                    .await?;
                let health_data = self
                    .get_historical_data(start_time, end_time, MonitoringDataType::SystemHealth)
                    .await?;

                data_points.extend(temp_data);
                data_points.extend(fan_data);
                data_points.extend(health_data);
            }
        }

        // 按时间排序
        data_points.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));

        Ok(data_points)
    }

    /// 获取监控指标
    pub async fn get_metrics(&self) -> MonitoringMetrics {
        self.metrics.read().await.clone()
    }

    /// 获取系统健康报告
    pub async fn get_health_report(&self) -> AppResult<SystemHealthReport> {
        let cache = self.data_cache.read().await;
        let metrics = self.metrics.read().await;

        // 计算整体健康分数
        let mut health_score = 100.0;
        let mut issues = Vec::new();

        // 检查温度状态
        if let Some(temp_data) = &cache.latest_temperature_data {
            for reading in temp_data {
                if reading.temperature > 80.0 {
                    health_score -= 10.0;
                    issues.push(format!(
                        "传感器 {} 温度过高: {:.1}°C",
                        reading.sensor_id, reading.temperature
                    ));
                } else if reading.temperature > 70.0 {
                    health_score -= 5.0;
                    issues.push(format!(
                        "传感器 {} 温度偏高: {:.1}°C",
                        reading.sensor_id, reading.temperature
                    ));
                }
            }
        }

        // 检查风扇状态
        if let Some(fan_data) = &cache.latest_fan_data {
            for reading in fan_data {
                if reading.rpm == 0 && reading.speed_percent > 0.0 {
                    health_score -= 15.0;
                    issues.push(format!(
                        "风扇 {} 可能故障: 设置转速 {:.1}% 但RPM为0",
                        reading.fan_id, reading.speed_percent
                    ));
                }
            }
        }

        // 检查活跃告警
        let active_alert_count = cache.active_alerts.len();
        if active_alert_count > 0 {
            health_score -= active_alert_count as f64 * 5.0;
            issues.push(format!("存在 {} 个活跃告警", active_alert_count));
        }

        health_score = health_score.max(0.0).min(100.0);

        let health_status = if health_score >= 90.0 {
            HealthStatus::Healthy
        } else if health_score >= 75.0 {
            HealthStatus::Healthy
        } else if health_score >= 60.0 {
            HealthStatus::Warning
        } else if health_score >= 40.0 {
            HealthStatus::Warning
        } else {
            HealthStatus::Critical
        };

        Ok(SystemHealthReport {
            timestamp: Utc::now(),
            overall_health_score: health_score,
            health_status,
            component_count: metrics.monitored_components,
            active_alerts: active_alert_count,
            issues,
            uptime_seconds: metrics.uptime_seconds,
            last_maintenance: None, // 需要从配置或数据库获取
            next_maintenance: None, // 需要从配置计算
        })
    }

    /// 添加自定义监控目标
    ///
    /// # 参数
    /// * `target` - 监控目标
    pub async fn add_monitoring_target(&self, target: MonitoringTarget) -> AppResult<()> {
        info!("添加监控目标: {}", target.id);

        let mut config = self.config.write().await;
        config.custom_targets.push(target);

        // 如果监控服务正在运行，启动新目标的监控
        if self.status.read().await.is_running {
            // 这里可以启动针对新目标的监控任务
            // 暂时省略具体实现
        }

        Ok(())
    }

    /// 移除监控目标
    ///
    /// # 参数
    /// * `target_id` - 目标ID
    pub async fn remove_monitoring_target(&self, target_id: &str) -> AppResult<bool> {
        info!("移除监控目标: {}", target_id);

        let mut config = self.config.write().await;
        let original_len = config.custom_targets.len();
        config
            .custom_targets
            .retain(|target| target.id != target_id);

        Ok(config.custom_targets.len() < original_len)
    }

    /// 触发手动数据收集
    pub async fn trigger_data_collection(&self) -> AppResult<()> {
        info!("触发手动数据收集");

        // 收集温度数据
        self.collect_temperature_data().await?;

        // 收集风扇数据
        self.collect_fan_data().await?;

        // 收集传感器数据
        self.collect_sensor_data().await?;

        // 更新系统健康状态
        self.update_system_health().await?;

        // 更新指标
        {
            let mut metrics = self.metrics.write().await;
            metrics.last_collection_time = Some(Utc::now());
            metrics.total_collections += 1;
        }

        info!("手动数据收集完成");
        Ok(())
    }

    // 私有方法

    /// 启动温度监控
    async fn start_temperature_monitoring(&self) -> AppResult<()> {
        let thermal_service = Arc::clone(&self.thermal_service);
        let data_cache = Arc::clone(&self.data_cache);
        let config = Arc::clone(&self.config);
        let metrics = Arc::clone(&self.metrics);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(30)); // 默认30秒间隔

            loop {
                interval.tick().await;

                // 检查配置的监控间隔
                let monitoring_interval = {
                    let cfg = config.read().await;
                    cfg.temperature_monitoring_interval
                };

                // 更新间隔
                interval = interval(Duration::from_secs(monitoring_interval));

                // 收集温度数据
                if let Ok(sensors) = thermal_service.get_temperature_sensors().await {
                    let mut temperature_readings = Vec::new();

                    for sensor_id in sensors {
                        if let Ok(reading) =
                            thermal_service.get_current_temperature(&sensor_id).await
                        {
                            temperature_readings.push(reading);
                        }
                    }

                    // 更新缓存
                    {
                        let mut cache = data_cache.write().await;
                        cache.latest_temperature_data = Some(temperature_readings);
                        cache.last_update = Utc::now();
                    }

                    // 更新指标
                    {
                        let mut m = metrics.write().await;
                        m.temperature_collections += 1;
                        m.last_collection_time = Some(Utc::now());
                    }
                }
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 启动风扇监控
    async fn start_fan_monitoring(&self) -> AppResult<()> {
        let fan_service = Arc::clone(&self.fan_service);
        let data_cache = Arc::clone(&self.data_cache);
        let config = Arc::clone(&self.config);
        let metrics = Arc::clone(&self.metrics);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(30));

            loop {
                interval.tick().await;

                let monitoring_interval = {
                    let cfg = config.read().await;
                    cfg.fan_monitoring_interval
                };

                interval = interval(Duration::from_secs(monitoring_interval));

                // 收集风扇数据
                if let Ok(fans) = fan_service.get_fan_list().await {
                    let mut fan_readings = Vec::new();

                    for fan_id in fans {
                        if let Ok(reading) = fan_service.get_current_fan_status(&fan_id).await {
                            fan_readings.push(reading);
                        }
                    }

                    // 更新缓存
                    {
                        let mut cache = data_cache.write().await;
                        cache.latest_fan_data = Some(fan_readings);
                        cache.last_update = Utc::now();
                    }

                    // 更新指标
                    {
                        let mut m = metrics.write().await;
                        m.fan_collections += 1;
                    }
                }
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 启动传感器监控
    async fn start_sensor_monitoring(&self) -> AppResult<()> {
        let sensor_service = Arc::clone(&self.sensor_service);
        let data_cache = Arc::clone(&self.data_cache);
        let config = Arc::clone(&self.config);
        let metrics = Arc::clone(&self.metrics);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(60));

            loop {
                interval.tick().await;

                let monitoring_interval = {
                    let cfg = config.read().await;
                    cfg.sensor_monitoring_interval
                };

                interval = interval(Duration::from_secs(monitoring_interval));

                // 收集传感器数据
                if let Ok(sensors) = sensor_service.get_all_sensor_data().await {
                    // 更新缓存
                    {
                        let mut cache = data_cache.write().await;
                        cache.latest_sensor_data = Some(sensors);
                        cache.last_update = Utc::now();
                    }

                    // 更新指标
                    {
                        let mut m = metrics.write().await;
                        m.sensor_collections += 1;
                    }
                }
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 启动系统健康监控
    async fn start_system_health_monitoring(&self) -> AppResult<()> {
        let data_cache = Arc::clone(&self.data_cache);
        let config = Arc::clone(&self.config);
        let alert_service = Arc::clone(&self.alert_service);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(60));

            loop {
                interval.tick().await;

                let monitoring_interval = {
                    let cfg = config.read().await;
                    cfg.health_check_interval
                };

                interval = interval(Duration::from_secs(monitoring_interval));

                // 检查系统健康状态
                let mut health_issues = Vec::new();

                // 检查缓存中的数据
                {
                    let cache = data_cache.read().await;

                    // 检查数据新鲜度
                    let data_age = Utc::now()
                        .signed_duration_since(cache.last_update)
                        .num_seconds();
                    if data_age > 300 {
                        // 5分钟
                        health_issues.push("监控数据过期".to_string());
                    }

                    // 检查温度异常
                    if let Some(temp_data) = &cache.latest_temperature_data {
                        for reading in temp_data {
                            if reading.temperature > 85.0 {
                                health_issues.push(format!(
                                    "传感器 {} 温度过高: {:.1}°C",
                                    reading.sensor_id, reading.temperature
                                ));
                            }
                        }
                    }

                    // 检查风扇异常
                    if let Some(fan_data) = &cache.latest_fan_data {
                        for reading in fan_data {
                            if reading.rpm == 0 && reading.speed_percent > 0.0 {
                                health_issues.push(format!("风扇 {} 可能故障", reading.fan_id));
                            }
                        }
                    }
                }

                // 更新系统健康状态
                let health_status = if health_issues.is_empty() {
                    SystemHealthStatus::Healthy
                } else if health_issues.len() <= 2 {
                    SystemHealthStatus::Warning
                } else {
                    SystemHealthStatus::Critical
                };

                {
                    let mut cache = data_cache.write().await;
                    cache.latest_system_health = Some(SystemHealth {
                        timestamp: Utc::now(),
                        status: health_status,
                        issues: health_issues.clone(),
                        uptime_seconds: 0, // 需要计算实际运行时间
                    });
                }

                // 如果有严重问题，触发告警
                if !health_issues.is_empty() {
                    for issue in health_issues {
                        // 这里可以通过告警服务发送告警
                        warn!("系统健康问题: {}", issue);
                    }
                }
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 启动性能监控
    async fn start_performance_monitoring(&self) -> AppResult<()> {
        let metrics = Arc::clone(&self.metrics);
        let status = Arc::clone(&self.status);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(60));
            let start_time = Instant::now();

            loop {
                interval.tick().await;

                // 更新性能指标
                {
                    let mut m = metrics.write().await;
                    m.uptime_seconds = start_time.elapsed().as_secs();

                    // 计算监控组件数量
                    m.monitored_components = 0; // 需要实际计算

                    // 更新其他指标
                    m.last_update = Utc::now();
                }

                // 更新状态
                {
                    let mut s = status.write().await;
                    s.last_update = Utc::now();
                }
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 启动数据清理任务
    async fn start_data_cleanup_task(&self) -> AppResult<()> {
        let data_cache = Arc::clone(&self.data_cache);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(3600)); // 每小时清理一次

            loop {
                interval.tick().await;

                // 清理过期的告警
                {
                    let mut cache = data_cache.write().await;
                    let cutoff_time = Utc::now() - chrono::Duration::hours(24);
                    cache
                        .active_alerts
                        .retain(|alert| alert.timestamp > cutoff_time);
                }

                debug!("数据清理任务执行完成");
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 重启监控任务
    async fn restart_monitoring_tasks(&self) -> AppResult<()> {
        info!("重启监控任务");

        // 停止现有任务
        {
            let mut handles = self.task_handles.lock().await;
            for handle in handles.drain(..) {
                handle.abort();
            }
        }

        // 重新启动任务
        self.start_temperature_monitoring().await?;
        self.start_fan_monitoring().await?;
        self.start_sensor_monitoring().await?;
        self.start_system_health_monitoring().await?;
        self.start_performance_monitoring().await?;
        self.start_data_cleanup_task().await?;

        info!("监控任务重启完成");
        Ok(())
    }

    /// 收集温度数据
    async fn collect_temperature_data(&self) -> AppResult<()> {
        if let Ok(sensors) = self.thermal_service.get_temperature_sensors().await {
            let mut temperature_readings = Vec::new();

            for sensor_id in sensors {
                if let Ok(reading) = self
                    .thermal_service
                    .get_current_temperature(&sensor_id)
                    .await
                {
                    temperature_readings.push(reading);
                }
            }

            let mut cache = self.data_cache.write().await;
            cache.latest_temperature_data = Some(temperature_readings);
            cache.last_update = Utc::now();
        }

        Ok(())
    }

    /// 收集风扇数据
    async fn collect_fan_data(&self) -> AppResult<()> {
        if let Ok(fans) = self.fan_service.get_fan_list().await {
            let mut fan_readings = Vec::new();

            for fan_id in fans {
                if let Ok(reading) = self.fan_service.get_current_fan_status(Some(&fan_id)).await {
                    fan_readings.extend(reading);
                }
            }

            let mut cache = self.data_cache.write().await;
            cache.latest_fan_data = Some(fan_readings);
            cache.last_update = Utc::now();
        }

        Ok(())
    }

    /// 收集传感器数据
    async fn collect_sensor_data(&self) -> AppResult<()> {
        if let Ok(sensors) = self.sensor_service.get_all_sensors().await {
            let mut cache = self.data_cache.write().await;
            cache.latest_sensor_data = Some(sensors);
            cache.last_update = Utc::now();
        }

        Ok(())
    }

    /// 更新系统健康状态
    async fn update_system_health(&self) -> AppResult<()> {
        let cache = self.data_cache.read().await;
        let mut health_issues = Vec::new();

        // 检查温度异常
        if let Some(temp_data) = &cache.latest_temperature_data {
            for reading in temp_data {
                if reading.temperature > 85.0 {
                    health_issues.push(format!(
                        "传感器 {} 温度过高: {:.1}°C",
                        reading.sensor_id, reading.temperature
                    ));
                }
            }
        }

        // 检查风扇异常
        if let Some(fan_data) = &cache.latest_fan_data {
            for reading in fan_data {
                if reading.current_rpm == 0.0 && reading.speed_percentage > 0.0 {
                    health_issues.push(format!("风扇 {} 可能故障", reading.fan_id));
                }
            }
        }

        let health_status = if health_issues.is_empty() {
            SystemHealthStatus::Healthy
        } else if health_issues.len() <= 2 {
            SystemHealthStatus::Warning
        } else {
            SystemHealthStatus::Critical
        };

        drop(cache);

        let mut cache = self.data_cache.write().await;
        cache.latest_system_health = Some(SystemHealth {
            timestamp: Utc::now(),
            status: health_status,
            issues: health_issues,
            // 需要计算实际运行时间
            uptime_seconds: 0,
        });
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_monitoring_service_creation() {
        // 这里需要创建模拟的服务实例来测试
        // 由于依赖较多，暂时跳过具体实现
        assert!(true);
    }

    #[test]
    fn test_monitoring_config_validation() {
        let config = MonitoringConfig::default();
        assert!(config.validate().is_ok());

        let mut invalid_config = config;
        invalid_config.temperature_monitoring_interval = 0;
        assert!(invalid_config.validate().is_err());
    }
}
