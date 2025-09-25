use crate::controllers::sensor_controller::{SensorHistoryParams, SensorTrendParams};
use crate::models::{
    config::MonitoringConfig,
    error::{AppError, AppResult},
    sensor::*,
};
use crate::services::ipmi_service::IpmiService;
use crate::utils::{ipmi::IpmiClient, math::MathUtils, time::TimeUtils};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

/// 传感器服务
///
/// 负责传感器数据的收集、处理和管理
#[derive(Clone)]
pub struct SensorService {
    /// IPMI客户端
    ipmi_service: Arc<IpmiService>,
    /// 传感器配置
    sensor_configs: Arc<RwLock<HashMap<String, SensorConfig>>>,
    /// 传感器历史数据
    sensor_history: Arc<RwLock<HashMap<String, Vec<SensorReading>>>>,
    /// 监控配置
    monitoring_config: Arc<RwLock<MonitoringConfig>>,
    /// 数学工具
    math_utils: MathUtils,
}

impl SensorService {
    /// 创建新的传感器服务
    ///
    /// # 参数
    /// * `ipmi_client` - IPMI客户端
    /// * `monitoring_config` - 监控配置
    pub fn new(ipmi_service: Arc<IpmiService>, monitoring_config: MonitoringConfig) -> Self {
        Self {
            ipmi_service,
            sensor_configs: Arc::new(RwLock::new(HashMap::new())),
            sensor_history: Arc::new(RwLock::new(HashMap::new())),
            monitoring_config: Arc::new(RwLock::new(monitoring_config)),
            math_utils: MathUtils,
        }
    }

    /// 获取所有传感器数据
    pub async fn get_all_sensors(&self) -> AppResult<Vec<SensorReading>> {
        let sensors = self.ipmi_service.get_fan_sensors().await?;
        let mut readings = Vec::new();

        for (id, sensor_data) in sensors {
            let config = self.get_sensor_config(&id).await;
            let sensor_type = self.determine_sensor_type(&sensor_data, config.as_ref());
            let status = self.determine_sensor_status(&sensor_data, config.as_ref());

            let reading = SensorReading::new(
                id.clone(),
                sensor_data.value,
                sensor_data.unit.unwrap_or("unknown".to_string()),
                sensor_type,
                status,
            );

            readings.push(reading);
        }

        // 更新历史数据
        self.update_sensor_history(&readings).await;

        Ok(readings)
    }

    /// 获取指定传感器数据
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    pub async fn get_sensor(&self, sensor_id: &str) -> AppResult<SensorReading> {
        let sensors = self.get_all_sensors().await?;

        sensors
            .into_iter()
            .find(|s| s.sensor_id == sensor_id)
            .ok_or_else(|| AppError::not_found(&format!("传感器 {} 不存在", sensor_id)))
    }

    /// 按类型获取传感器数据
    ///
    /// # 参数
    /// * `sensor_type` - 传感器类型
    pub async fn get_sensors_by_type(
        &self,
        sensor_type: &SensorType,
    ) -> AppResult<Vec<SensorReading>> {
        let all_sensors = self.get_all_sensors().await?;

        Ok(all_sensors
            .into_iter()
            .filter(|s| &s.sensor_type == sensor_type)
            .collect())
    }

    /// 获取传感器历史数据
    ///
    /// # 参数
    /// * `query` - 查询参数
    pub async fn get_sensor_history(
        &self,
        query: &SensorHistoryParams,
    ) -> AppResult<Vec<SensorReading>> {
        let history = self.sensor_history.read().await;
        let mut results = Vec::new();

        for (sensor_id, readings) in history.iter() {
            // 传感器ID过滤
            if let Some(ref target_ids) = query.sensor_ids {
                if !target_ids.contains(sensor_id) {
                    continue;
                }
            }

            for reading in readings {
                // 时间范围过滤
                if let Some(start_time) = query.start_time {
                    if reading.timestamp < start_time {
                        continue;
                    }
                }

                if let Some(end_time) = query.end_time {
                    if reading.timestamp > end_time {
                        continue;
                    }
                }

                // 数值范围过滤
                if let Some(min_value) = query.min_value {
                    if reading.value < min_value {
                        continue;
                    }
                }

                if let Some(max_value) = query.max_value {
                    if reading.value > max_value {
                        continue;
                    }
                }

                // 类型过滤
                if let Some(ref sensor_type) = query.sensor_type {
                    if &reading.sensor_type != sensor_type {
                        continue;
                    }
                }

                // 状态过滤
                if let Some(ref status) = query.status {
                    if &reading.status != status {
                        continue;
                    }
                }

                results.push(reading.clone());
            }
        }

        // 排序
        results.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));

        // 限制结果数量
        if let Some(limit) = query.limit {
            results.truncate(limit);
        }

        Ok(results)
    }

    /// 获取传感器统计信息
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `duration_hours` - 统计时间范围（小时）
    pub async fn get_sensor_stats(
        &self,
        sensor_id: &str,
        duration_hours: u64,
    ) -> AppResult<SensorStats> {
        let end_time = Utc::now();
        let start_time = end_time - chrono::Duration::hours(duration_hours as i64);

        let query = SensorHistoryParams {
            sensor_id: Some(sensor_id.to_string()),
            start_time: Some(start_time),
            end_time: Some(end_time),
            min_value: None,
            max_value: None,
            sensor_type: None,
            status: None,
            limit: None,
        };

        let readings = self.get_sensor_history(&query).await?;

        if readings.is_empty() {
            return Err(AppError::not_found("指定时间范围内没有传感器数据"));
        }

        let values: Vec<f64> = readings.iter().map(|r| r.value).collect();

        let min_value = values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max_value = values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
        let avg_value = values.iter().sum::<f64>() / values.len() as f64;
        let std_dev = self.math_utils.calculate_standard_deviation(&values);

        // 计算各状态的数量
        let mut normal_count = 0;
        let mut warning_count = 0;
        let mut critical_count = 0;

        for reading in &readings {
            match reading.status {
                SensorStatus::Normal => normal_count += 1,
                SensorStatus::Warning => warning_count += 1,
                SensorStatus::Critical => critical_count += 1,
            }
        }

        Ok(SensorStats {
            sensor_id: sensor_id.to_string(),
            sensor_type: readings[0].sensor_type.clone(),
            min_value,
            max_value,
            avg_value,
            std_deviation: std_dev,
            sample_count: readings.len(),
            normal_count,
            warning_count,
            critical_count,
            start_time,
            end_time,
        })
    }

    /// 获取传感器趋势
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `duration_hours` - 分析时间范围（小时）
    pub async fn get_sensor_trend(
        &self,
        sensor_id: &str,
        duration_hours: u64,
    ) -> AppResult<SensorTrend> {
        let end_time = Utc::now();
        let start_time = end_time - chrono::Duration::hours(duration_hours as i64);

        let query = SensorHistoryParams {
            sensor_id: Some(sensor_id.to_string()),
            start_time: Some(start_time),
            end_time: Some(end_time),
            min_value: None,
            max_value: None,
            sensor_type: None,
            status: None,
            limit: None,
        };

        let readings = self.get_sensor_history(&query).await?;

        if readings.len() < 2 {
            return Err(AppError::validation_error(
                "data",
                "数据点不足，无法计算趋势",
            ));
        }

        // 准备线性回归数据
        let x_values: Vec<f64> = readings.iter().enumerate().map(|(i, _)| i as f64).collect();
        let y_values: Vec<f64> = readings.iter().map(|r| r.value).collect();

        let (slope, intercept, r_squared) = self.math_utils.linear_regression(&x_values, &y_values);

        // 计算变化率（每小时）
        let time_span_hours = duration_hours as f64;
        let change_rate = slope * (readings.len() as f64 / time_span_hours);

        // 预测未来值
        let future_points = 6; // 预测未来6个时间点
        let mut predictions = Vec::new();

        for i in 1..=future_points {
            let future_x = readings.len() as f64 + i as f64;
            let predicted_value = slope * future_x + intercept;
            let future_time = end_time + chrono::Duration::minutes(i * 10); // 假设每10分钟一个预测点

            predictions.push((future_time, predicted_value));
        }

        Ok(SensorTrend {
            sensor_id: sensor_id.to_string(),
            sensor_type: readings[0].sensor_type.clone(),
            slope,
            intercept,
            r_squared,
            change_rate,
            predictions,
            start_time,
            end_time,
        })
    }

    /// 设置传感器配置
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `config` - 传感器配置
    pub async fn set_sensor_config(
        &self,
        sensor_id: String,
        config: SensorConfig,
    ) -> AppResult<()> {
        let mut configs = self.sensor_configs.write().await;
        configs.insert(sensor_id, config);
        Ok(())
    }

    /// 获取传感器配置
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    pub async fn get_sensor_config(&self, sensor_id: &str) -> Option<SensorConfig> {
        let configs = self.sensor_configs.read().await;
        configs.get(sensor_id).cloned()
    }

    /// 获取所有传感器配置
    pub async fn get_all_sensor_configs(&self) -> HashMap<String, SensorConfig> {
        let configs = self.sensor_configs.read().await;
        configs.clone()
    }

    /// 删除传感器配置
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    pub async fn remove_sensor_config(&self, sensor_id: &str) -> AppResult<()> {
        let mut configs = self.sensor_configs.write().await;
        configs.remove(sensor_id);
        Ok(())
    }

    /// 获取传感器列表
    pub async fn get_sensor_list(&self) -> AppResult<Vec<SensorInfo>> {
        let sensors = self.ipmi_service.get_all_sensors().await?;
        let mut sensor_list = Vec::new();

        for (id, sensor_data) in sensors {
            let config = self.get_sensor_config(&id).await;
            let sensor_type = self.determine_sensor_type(&sensor_data, config.as_ref());

            let info = SensorInfo {
                sensor_id: id,
                name: config
                    .as_ref()
                    .map(|c| c.name.clone())
                    .unwrap_or_else(|| "未知传感器".to_string()),
                sensor_type,
                unit: sensor_data.unit.unwrap_or("unknown".to_string()),
                description: config.as_ref().and_then(|c| c.description.clone()),
                location: config.as_ref().and_then(|c| c.location.clone()),
                enabled: config.as_ref().map(|c| c.enabled).unwrap_or(true),
            };

            sensor_list.push(info);
        }

        Ok(sensor_list)
    }

    /// 校准传感器
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `calibration` - 校准参数
    pub async fn calibrate_sensor(
        &self,
        sensor_id: &str,
        calibration: SensorCalibration,
    ) -> AppResult<()> {
        let mut configs = self.sensor_configs.write().await;

        if let Some(config) = configs.get_mut(sensor_id) {
            config.calibration = Some(calibration);
        } else {
            return Err(AppError::not_found(&format!(
                "传感器配置 {} 不存在",
                sensor_id
            )));
        }

        log::info!("传感器 {} 校准完成", sensor_id);
        Ok(())
    }

    /// 检测传感器异常
    pub async fn detect_sensor_anomalies(&self) -> AppResult<Vec<SensorAnomaly>> {
        let all_sensors = self.get_all_sensors().await?;
        let mut anomalies = Vec::new();

        for sensor in all_sensors {
            // 检查传感器状态
            if matches!(
                sensor.status,
                SensorStatus::Warning | SensorStatus::Critical
            ) {
                let anomaly = SensorAnomaly {
                    id: uuid::Uuid::new_v4().to_string(),
                    sensor_id: sensor.sensor_id.clone(),
                    anomaly_type: match sensor.status {
                        SensorStatus::Warning => AnomalyType::Warning,
                        SensorStatus::Critical => AnomalyType::Critical,
                        _ => AnomalyType::Info,
                    },
                    description: format!(
                        "传感器 {} 状态异常: {:?}",
                        sensor.sensor_id, sensor.status
                    ),
                    value: sensor.value,
                    expected_range: None, // 可以从配置中获取
                    severity: match sensor.status {
                        SensorStatus::Warning => AnomalySeverity::Medium,
                        SensorStatus::Critical => AnomalySeverity::High,
                        _ => AnomalySeverity::Low,
                    },
                    timestamp: sensor.timestamp,
                    resolved: false,
                };

                anomalies.push(anomaly);
            }

            // 检查数值异常（基于历史数据）
            if let Ok(stats) = self.get_sensor_stats(&sensor.sensor_id, 24).await {
                let z_score = (sensor.value - stats.avg_value) / stats.std_deviation;

                if z_score.abs() > 3.0 {
                    // 3-sigma规则
                    let anomaly = SensorAnomaly {
                        id: uuid::Uuid::new_v4().to_string(),
                        sensor_id: sensor.sensor_id.clone(),
                        anomaly_type: AnomalyType::Statistical,
                        description: format!(
                            "传感器 {} 数值异常: {:.2} (Z-score: {:.2})",
                            sensor.sensor_id, sensor.value, z_score
                        ),
                        value: sensor.value,
                        expected_range: Some((
                            stats.avg_value - 2.0 * stats.std_deviation,
                            stats.avg_value + 2.0 * stats.std_deviation,
                        )),
                        severity: if z_score.abs() > 4.0 {
                            AnomalySeverity::High
                        } else {
                            AnomalySeverity::Medium
                        },
                        timestamp: sensor.timestamp,
                        resolved: false,
                    };

                    anomalies.push(anomaly);
                }
            }
        }

        Ok(anomalies)
    }

    /// 获取传感器健康状态
    pub async fn get_sensor_health(&self) -> AppResult<SensorHealthReport> {
        let all_sensors = self.get_all_sensors().await?;
        let anomalies = self.detect_sensor_anomalies().await?;

        let total_sensors = all_sensors.len();
        let healthy_sensors = all_sensors
            .iter()
            .filter(|s| matches!(s.status, SensorStatus::Normal))
            .count();
        let warning_sensors = all_sensors
            .iter()
            .filter(|s| matches!(s.status, SensorStatus::Warning))
            .count();
        let critical_sensors = all_sensors
            .iter()
            .filter(|s| matches!(s.status, SensorStatus::Critical))
            .count();

        let health_score = if total_sensors > 0 {
            (healthy_sensors as f64 / total_sensors as f64) * 100.0
        } else {
            0.0
        };

        Ok(SensorHealthReport {
            total_sensors,
            healthy_sensors,
            warning_sensors,
            critical_sensors,
            health_score,
            anomaly_count: anomalies.len(),
            last_updated: Utc::now(),
        })
    }

    /// 导出传感器数据
    ///
    /// # 参数
    /// * `query` - 查询参数
    /// * `format` - 导出格式
    pub async fn export_sensor_data(
        &self,
        query: &SensorHistoryParams,
        format: &str,
    ) -> AppResult<String> {
        let readings = self.get_sensor_history(query).await?;

        match format.to_lowercase().as_str() {
            "csv" => self.export_to_csv(&readings),
            "json" => self.export_to_json(&readings),
            _ => Err(AppError::validation_error("format", "不支持的导出格式")),
        }
    }

    /// 确定传感器类型
    ///
    /// # 参数
    /// * `sensor_data` - 传感器数据
    /// * `config` - 传感器配置
    fn determine_sensor_type(
        &self,
        sensor_data: &crate::utils::ipmi::SensorData,
        config: Option<&SensorConfig>,
    ) -> SensorType {
        // 优先使用配置中的类型
        if let Some(cfg) = config {
            return cfg.sensor_type.clone();
        }

        // 根据单位和名称推断类型
        if let Some(ref unit) = sensor_data.unit {
            match unit.to_lowercase().as_str() {
                "c" | "°c" | "celsius" => SensorType::Temperature,
                "rpm" => SensorType::Fan,
                "v" | "volts" => SensorType::Voltage,
                "a" | "amps" => SensorType::Current,
                "w" | "watts" => SensorType::Power,
                _ => SensorType::Other,
            }
        } else {
            SensorType::Other
        }
    }

    /// 确定传感器状态
    ///
    /// # 参数
    /// * `sensor_data` - 传感器数据
    /// * `config` - 传感器配置
    fn determine_sensor_status(
        &self,
        sensor_data: &crate::utils::ipmi::SensorData,
        config: Option<&SensorConfig>,
    ) -> SensorStatus {
        // 检查IPMI传感器状态
        if let Some(ref status) = sensor_data.status {
            match status.to_lowercase().as_str() {
                "ok" | "normal" => SensorStatus::Ok,
                "warning" | "warn" => SensorStatus::Warning,
                "critical" | "crit" | "error" => SensorStatus::Critical,
                _ => SensorStatus::Ok,
            }
        } else if let Some(cfg) = config {
            // 根据阈值判断状态
            if let Some(ref thresholds) = cfg.thresholds {
                if sensor_data.value >= thresholds.critical_high
                    || sensor_data.value <= thresholds.critical_low
                {
                    SensorStatus::Critical
                } else if sensor_data.value >= thresholds.warning_high
                    || sensor_data.value <= thresholds.warning_low
                {
                    SensorStatus::Warning
                } else {
                    SensorStatus::Normal
                }
            } else {
                SensorStatus::Normal
            }
        } else {
            SensorStatus::Normal
        }
    }

    /// 更新传感器历史数据
    ///
    /// # 参数
    /// * `readings` - 传感器读数列表
    async fn update_sensor_history(&self, readings: &[SensorReading]) {
        let mut history = self.sensor_history.write().await;
        let config = self.monitoring_config.read().await;

        for reading in readings {
            let sensor_history = history
                .entry(reading.sensor_id.clone())
                .or_insert_with(Vec::new);
            sensor_history.push(reading.clone());

            // 限制历史数据数量
            let max_history = (config.retention_days * 24 * 60) as usize; // 转换为分钟数
            if sensor_history.len() > max_history {
                sensor_history.drain(0..sensor_history.len() - max_history);
            }
        }
    }

    /// 清理过期的历史数据
    pub async fn cleanup_expired_data(&self) -> AppResult<usize> {
        let mut history = self.sensor_history.write().await;
        let config = self.monitoring_config.read().await;
        let retention_hours = (config.retention_days * 24) as i64;
        let cutoff_time = Utc::now() - chrono::Duration::hours(retention_hours);

        let mut removed_count = 0;

        for (_, readings) in history.iter_mut() {
            let original_len = readings.len();
            readings.retain(|reading| reading.timestamp > cutoff_time);
            removed_count += original_len - readings.len();
        }

        Ok(removed_count)
    }

    /// 导出为CSV格式
    ///
    /// # 参数
    /// * `readings` - 传感器读数列表
    fn export_to_csv(&self, readings: &[SensorReading]) -> AppResult<String> {
        let mut csv = String::from("timestamp,sensor_id,value,unit,sensor_type,status\n");

        for reading in readings {
            csv.push_str(&format!(
                "{},{},{},{},{:?},{:?}\n",
                reading.timestamp.format("%Y-%m-%d %H:%M:%S"),
                reading.sensor_id,
                reading.value,
                reading.unit,
                reading.sensor_type,
                reading.status
            ));
        }

        Ok(csv)
    }

    /// 导出为JSON格式
    ///
    /// # 参数
    /// * `readings` - 传感器读数列表
    fn export_to_json(&self, readings: &[SensorReading]) -> AppResult<String> {
        serde_json::to_string_pretty(readings)
            .map_err(|e| AppError::serialization_error(format!("JSON序列化失败: {}", e)))
    }
}

/// 传感器异常
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SensorAnomaly {
    /// 异常ID
    pub id: String,
    /// 传感器ID
    pub sensor_id: String,
    /// 异常类型
    pub anomaly_type: AnomalyType,
    /// 描述
    pub description: String,
    /// 当前值
    pub value: f64,
    /// 期望范围
    pub expected_range: Option<(f64, f64)>,
    /// 严重程度
    pub severity: AnomalySeverity,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 是否已解决
    pub resolved: bool,
}

/// 异常类型
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AnomalyType {
    /// 信息
    Info,
    /// 警告
    Warning,
    /// 严重
    Critical,
    /// 统计异常
    Statistical,
    /// 趋势异常
    Trend,
}

/// 异常严重程度
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AnomalySeverity {
    /// 低
    Low,
    /// 中
    Medium,
    /// 高
    High,
}

/// 传感器健康报告
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SensorHealthReport {
    /// 传感器总数
    pub total_sensors: usize,
    /// 健康传感器数量
    pub healthy_sensors: usize,
    /// 警告传感器数量
    pub warning_sensors: usize,
    /// 严重传感器数量
    pub critical_sensors: usize,
    /// 健康分数 (0-100)
    pub health_score: f64,
    /// 异常数量
    pub anomaly_count: usize,
    /// 最后更新时间
    pub last_updated: DateTime<Utc>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::config::IpmiConfig;

    #[tokio::test]
    async fn test_sensor_service_creation() {
        let ipmi_config = IpmiConfig {
            host: "192.168.3.48".to_string(),
            username: "test".to_string(),
            password: "test".to_string(),
            interface: Some("lanplus".to_string()),
            port: Some(623),
            timeout: Some(5),
        };

        let ipmi_client = Arc::new(IpmiClient::new(ipmi_config));
        let monitoring_config = MonitoringConfig {
            enabled: true,
            interval_seconds: Some(60),
            data_retention_hours: Some(24),
            alert_thresholds: None,
        };

        let sensor_service = SensorService::new(ipmi_client, monitoring_config);

        // 测试设置和获取传感器配置
        let config = SensorConfig {
            name: "CPU温度传感器".to_string(),
            description: Some("CPU核心温度监控".to_string()),
            sensor_type: SensorType::Temperature,
            enabled: true,
            location: Some("CPU1".to_string()),
            thresholds: Some(SensorThresholds {
                warning_low: 0.0,
                warning_high: 70.0,
                critical_low: -10.0,
                critical_high: 85.0,
            }),
            calibration: None,
        };

        sensor_service
            .set_sensor_config("CPU1_TEMP".to_string(), config.clone())
            .await
            .unwrap();

        let retrieved_config = sensor_service.get_sensor_config("CPU1_TEMP").await;
        assert!(retrieved_config.is_some());
        assert_eq!(retrieved_config.unwrap().name, "CPU温度传感器");
    }

    #[test]
    fn test_sensor_type_determination() {
        let sensor_service = SensorService::new(
            Arc::new(IpmiClient::new(crate::models::config::IpmiConfig {
                host: "test".to_string(),
                username: "test".to_string(),
                password: "test".to_string(),
                interface: None,
                port: None,
                timeout: None,
            })),
            MonitoringConfig {
                enabled: true,
                interval_seconds: None,
                data_retention_hours: None,
                alert_thresholds: None,
            },
        );

        let temp_sensor = crate::utils::ipmi::SensorData {
            value: 45.0,
            unit: Some("°C".to_string()),
            status: Some("ok".to_string()),
            speed_rpm: None,
            speed_percent: None,
        };

        let sensor_type = sensor_service.determine_sensor_type(&temp_sensor, None);
        assert_eq!(sensor_type, SensorType::Temperature);

        let fan_sensor = crate::utils::ipmi::SensorData {
            value: 1200.0,
            unit: Some("RPM".to_string()),
            status: Some("ok".to_string()),
            speed_rpm: Some(1200),
            speed_percent: Some(50.0),
        };

        let fan_type = sensor_service.determine_sensor_type(&fan_sensor, None);
        assert_eq!(fan_type, SensorType::Fan);
    }
}
