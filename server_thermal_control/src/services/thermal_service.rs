use crate::models::api::ExportFormat;
use crate::models::sensor::TemperatureSensor;
use crate::models::thermal::*;
use crate::models::*;
use crate::models::{AppError, AppResult};
use crate::services::ipmi_service::IpmiService;
use crate::utils::math::*;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

/// 温度服务
///
/// 负责温度数据的收集、处理和分析
#[derive(Clone)]
pub struct ThermalService {
    /// IPMI服务
    ipmi_service: Arc<IpmiService>,
    /// 温度阈值配置
    thresholds: Arc<RwLock<HashMap<String, TemperatureThreshold>>>,
    /// 温度历史数据
    temperature_history: Arc<RwLock<HashMap<String, Vec<TemperatureReading>>>>,
    /// 监控配置
    monitoring_config: Arc<RwLock<MonitoringConfig>>,
    /// 数学工具
    math_utils: (),
}

impl ThermalService {
    /// 创建新的温度服务
    ///
    /// # 参数
    /// * `ipmi_service` - IPMI服务
    /// * `monitoring_config` - 监控配置
    pub fn new(ipmi_service: Arc<IpmiService>, monitoring_config: MonitoringConfig) -> Self {
        Self {
            ipmi_service,
            thresholds: Arc::new(RwLock::new(HashMap::new())),
            temperature_history: Arc::new(RwLock::new(HashMap::new())),
            monitoring_config: Arc::new(RwLock::new(monitoring_config)),
            math_utils: (),
        }
    }

    /// 获取当前温度读数
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    pub async fn get_current_temperature(&self, sensor_id: &str) -> AppResult<TemperatureReading> {
        match self.ipmi_service.get_temperature_by_sensor(sensor_id) {
            Ok(Some(sensor_data)) => {
                let threshold = self.get_threshold(sensor_id).await;
                let status: TemperatureStatus = if let Some(ref th) = threshold {
                    th.get_status(sensor_data.temperature)
                } else {
                    // 默认阈值判断
                    if sensor_data.temperature > 80.0 {
                        TemperatureStatus::Critical
                    } else if sensor_data.temperature > 70.0 {
                        TemperatureStatus::Warning
                    } else {
                        TemperatureStatus::Normal
                    }
                };

                let reading = TemperatureReading {
                    id: sensor_data.id,
                    sensor_id: sensor_data.sensor_id,
                    sensor_name: "".to_string(),
                    temperature: sensor_data.temperature,
                    status: sensor_data.status,
                    timestamp: sensor_data.timestamp,
                    server_id: "".to_string(),
                };

                // 更新历史数据
                self.update_single_temperature_history(&reading).await;

                Ok(reading)
            }
            Ok(None) => Err(AppError::NotFoundError(
                format!("传感器 {} 未找到", sensor_id),
                sensor_id.into(),
            )),
            Err(e) => Err(AppError::External(format!("获取温度数据失败: {}", e))),
        }
    }

    /// 获取所有当前温度读数
    pub async fn get_all_current_temperatures(&self) -> AppResult<Vec<TemperatureReading>> {
        match self.ipmi_service.get_temperature_sensors().await {
            Ok(sensors) => {
                let mut readings = Vec::new();

                for sensor_data in sensors {
                    let threshold = self.get_threshold(&sensor_data.sensor_id).await;
                    let status = if let Some(ref th) = threshold {
                        th.get_status(sensor_data.temperature)
                    } else {
                        // 默认阈值判断
                        if sensor_data.temperature > 80.0 {
                            TemperatureStatus::Critical
                        } else if sensor_data.temperature > 70.0 {
                            TemperatureStatus::Warning
                        } else {
                            TemperatureStatus::Normal
                        }
                    };

                    let reading = TemperatureReading {
                        id: sensor_data.id,
                        sensor_id: sensor_data.sensor_id,
                        temperature: sensor_data.temperature,
                        unit: sensor_data.unit,
                        location: sensor_data.location,
                        status: sensor_data.status,
                        timestamp: sensor_data.timestamp,
                    };

                    readings.push(reading);
                }

                // 更新历史数据
                self.update_temperature_history(&readings).await;

                Ok(readings)
            }
            Err(e) => Err(AppError::External(format!("获取温度数据失败: {}", e))),
        }
    }

    /// 获取温度历史数据
    ///
    /// # 参数
    /// * `query` - 查询参数
    pub async fn get_temperature_history(
        &self,
        query: &TemperatureQuery,
    ) -> AppResult<Vec<TemperatureReading>> {
        let history = self.temperature_history.read().await;
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

                // 温度范围过滤
                if let Some(min_temp) = query.min_temperature {
                    if reading.value < min_temp {
                        continue;
                    }
                }

                if let Some(max_temp) = query.max_temperature {
                    if reading.value > max_temp {
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

    /// 获取温度统计信息
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `duration_hours` - 统计时间范围（小时）
    pub async fn get_temperature_stats(
        &self,
        sensor_id: &str,
        duration_hours: u64,
    ) -> AppResult<TemperatureStats> {
        let end_time = Utc::now();
        let start_time = end_time - chrono::Duration::hours(duration_hours as i64);

        let query = TemperatureQuery {
            sensor_ids: Some(vec![sensor_id.to_string()]),
            start_time: Some(start_time),
            end_time: Some(end_time),
            min_temperature: None,
            max_temperature: None,
            status: None,
            limit: None,
        };

        let readings = self.get_temperature_history(&query).await?;

        if readings.is_empty() {
            return Err(AppError::not_found("指定时间范围内没有温度数据"));
        }

        let values: Vec<f64> = readings.iter().map(|r| r.value).collect();

        let min_temp = values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max_temp = values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
        let avg_temp = values.iter().sum::<f64>() / values.len() as f64;
        let std_dev = MathUtils::calculate_standard_deviation(&values)?;

        // 计算各状态的数量
        let mut normal_count = 0;
        let mut warning_count = 0;
        let mut critical_count = 0;

        for reading in &readings {
            match reading.status {
                TemperatureStatus::Normal => normal_count += 1,
                TemperatureStatus::Warning => warning_count += 1,
                TemperatureStatus::Critical => critical_count += 1,
                _ => {}
            }
        }

        Ok(TemperatureStats {
            sensor_id: sensor_id.to_string(),
            min_temperature: min_temp,
            max_temperature: max_temp,
            avg_temperature: avg_temp,
            std_deviation: std_dev,
            sample_count: readings.len(),
            normal_count,
            warning_count,
            critical_count,
            start_time,
            end_time,
        })
    }

    /// 获取温度趋势
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `duration_hours` - 分析时间范围（小时）
    pub async fn get_temperature_trend(
        &self,
        sensor_id: &str,
        duration_hours: u64,
    ) -> AppResult<TemperatureTrend> {
        let end_time = Utc::now();
        let start_time = end_time - chrono::Duration::hours(duration_hours as i64);

        let query = TemperatureQuery {
            sensor_ids: Some(vec![sensor_id.to_string()]),
            start_time: Some(start_time),
            end_time: Some(end_time),
            min_temperature: None,
            max_temperature: None,
            status: None,
            limit: None,
        };

        let readings = self.get_temperature_history(&query).await?;

        if readings.len() < 2 {
            return Err(AppError::validation_error(
                "data",
                "数据点不足，无法计算趋势",
            ));
        }

        // 准备线性回归数据
        let x_values: Vec<f64> = readings.iter().enumerate().map(|(i, _)| i as f64).collect();
        let y_values: Vec<f64> = readings.iter().map(|r| r.value).collect();

        let (slope, intercept, r_squared) = MathUtils::linear_regression(&x_values, &y_values)?;

        // 计算变化率（每小时）
        let time_span_hours = duration_hours as f64;
        let change_rate = slope * (readings.len() as f64 / time_span_hours);

        // 预测未来温度
        let future_points = 6; // 预测未来6个时间点
        let mut predictions = Vec::new();

        for i in 1..=future_points {
            let future_x = readings.len() as f64 + i as f64;
            let predicted_temp = slope * future_x + intercept;
            let future_time = end_time + chrono::Duration::minutes(i * 10); // 假设每10分钟一个预测点

            predictions.push((future_time, predicted_temp));
        }

        Ok(TemperatureTrend {
            sensor_id: sensor_id.to_string(),
            slope,
            intercept,
            r_squared,
            change_rate,
            predictions,
            start_time,
            end_time,
        })
    }

    /// 设置温度阈值
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    /// * `threshold` - 温度阈值配置
    pub async fn set_temperature_threshold(
        &self,
        sensor_id: String,
        threshold: TemperatureThreshold,
    ) -> AppResult<()> {
        let mut thresholds = self.thresholds.write().await;
        thresholds.insert(sensor_id, threshold);
        Ok(())
    }

    /// 获取温度阈值
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    pub async fn get_threshold(&self, sensor_id: &str) -> Option<TemperatureThreshold> {
        let thresholds = self.thresholds.read().await;
        thresholds.get(sensor_id).cloned()
    }

    /// 获取所有温度阈值
    pub async fn get_all_thresholds(&self) -> HashMap<String, TemperatureThreshold> {
        let thresholds = self.thresholds.read().await;
        thresholds.clone()
    }

    /// 删除温度阈值
    ///
    /// # 参数
    /// * `sensor_id` - 传感器ID
    pub async fn remove_temperature_threshold(&self, sensor_id: &str) -> AppResult<()> {
        let mut thresholds = self.thresholds.write().await;
        thresholds.remove(sensor_id);
        Ok(())
    }

    /// 检查温度告警
    pub async fn check_temperature_alerts(&self) -> AppResult<Vec<TemperatureAlert>> {
        let current_readings = self.get_current_temperature(None).await?;
        let mut alerts = Vec::new();

        for reading in current_readings {
            if matches!(
                reading.status,
                TemperatureStatus::Warning | TemperatureStatus::Critical
            ) {
                let severity = match reading.status {
                    TemperatureStatus::Warning => AlertSeverity::Warning,
                    TemperatureStatus::Critical => AlertSeverity::Critical,
                    _ => continue,
                };

                let alert = TemperatureAlert {
                    id: uuid::Uuid::new_v4().to_string(),
                    sensor_id: reading.sensor_id.clone(),
                    temperature: reading.value,
                    threshold_type: match reading.status {
                        TemperatureStatus::Warning => "warning".to_string(),
                        TemperatureStatus::Critical => "critical".to_string(),
                        _ => "unknown".to_string(),
                    },
                    severity,
                    message: format!(
                        "传感器 {} 温度异常: {:.1}°C (状态: {:?})",
                        reading.sensor_id, reading.value, reading.status
                    ),
                    timestamp: reading.timestamp,
                    acknowledged: false,
                };

                alerts.push(alert);
            }
        }

        Ok(alerts)
    }

    /// 更新温度历史数据
    ///
    /// # 参数
    /// * `readings` - 温度读数列表
    async fn update_temperature_history(&self, readings: &[TemperatureReading]) {
        let mut history = self.temperature_history.write().await;
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
        let mut history = self.temperature_history.write().await;
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

    /// 更新单个温度历史记录
    async fn update_single_temperature_history(&self, reading: &TemperatureReading) {
        let mut history = self.temperature_history.write().await;
        let sensor_history = history
            .entry(reading.sensor_id.clone())
            .or_insert_with(Vec::new);

        sensor_history.push(reading.clone());

        // 保持历史记录在合理范围内（最多1000条记录）
        if sensor_history.len() > 1000 {
            sensor_history.remove(0);
        }
    }

    /// 获取温度传感器列表
    pub async fn get_temperature_sensors(&self) -> AppResult<Vec<TemperatureSensor>> {
        match self.ipmi_service.get_temperature_sensors().await {
            Ok(sensors) => {
                let temperature_sensors: Vec<TemperatureSensor> = sensors
                    .into_iter()
                    .map(|s| TemperatureSensor {
                        id: s.id,
                        sensor_id: s.sensor_id,
                        name: s.location.clone(),
                        location: s.location,
                        sensor_type: "Temperature".to_string(),
                        unit: s.unit,
                        min_value: Some(0.0),
                        max_value: Some(100.0),
                        accuracy: Some(0.5),
                        status: s.status,
                        last_reading: Some(s.temperature),
                        last_update: Some(s.timestamp),
                    })
                    .collect();

                Ok(temperature_sensors)
            }
            Err(e) => Err(AppError::External(format!("获取温度传感器失败: {}", e))),
        }
    }

    /// 获取温度统计信息
    pub async fn get_temperature_statistics(
        &self,
        sensor_id: Option<&str>,
        start_time: Option<DateTime<Utc>>,
        end_time: Option<DateTime<Utc>>,
    ) -> AppResult<TemperatureStats> {
        let history = self.temperature_history.read().await;
        let mut all_readings = Vec::new();

        // 收集相关的温度读数
        for (id, readings) in history.iter() {
            if let Some(target_id) = sensor_id {
                if id != target_id {
                    continue;
                }
            }

            for reading in readings {
                // 时间过滤
                if let Some(start) = start_time {
                    if reading.timestamp < start {
                        continue;
                    }
                }
                if let Some(end) = end_time {
                    if reading.timestamp > end {
                        continue;
                    }
                }

                all_readings.push(reading.clone());
            }
        }

        if all_readings.is_empty() {
            return Ok(TemperatureStats {
                sensor_count: 0,
                total_readings: 0,
                average_temperature: 0.0,
                min_temperature: 0.0,
                max_temperature: 0.0,
                temperature_trend: "stable".to_string(),
                period_start: start_time.unwrap_or_else(Utc::now),
                period_end: end_time.unwrap_or_else(Utc::now),
            });
        }

        // 计算统计信息
        let temperatures: Vec<f64> = all_readings.iter().map(|r| r.temperature).collect();
        let average = temperatures.iter().sum::<f64>() / temperatures.len() as f64;
        let min_temp = temperatures.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max_temp = temperatures
            .iter()
            .fold(f64::NEG_INFINITY, |a, &b| a.max(b));

        // 简单的趋势分析
        let trend = if temperatures.len() > 1 {
            let first_half_avg = temperatures[..temperatures.len() / 2].iter().sum::<f64>()
                / (temperatures.len() / 2) as f64;
            let second_half_avg = temperatures[temperatures.len() / 2..].iter().sum::<f64>()
                / (temperatures.len() - temperatures.len() / 2) as f64;

            if second_half_avg > first_half_avg + 1.0 {
                "rising"
            } else if second_half_avg < first_half_avg - 1.0 {
                "falling"
            } else {
                "stable"
            }
        } else {
            "stable"
        };

        let unique_sensors: std::collections::HashSet<_> =
            all_readings.iter().map(|r| &r.sensor_id).collect();

        Ok(TemperatureStats {
            sensor_count: unique_sensors.len(),
            total_readings: all_readings.len(),
            average_temperature: average,
            min_temperature: min_temp,
            max_temperature: max_temp,
            temperature_trend: trend.to_string(),
            period_start: start_time.unwrap_or_else(|| {
                all_readings
                    .iter()
                    .map(|r| r.timestamp)
                    .min()
                    .unwrap_or_else(Utc::now)
            }),
            period_end: end_time.unwrap_or_else(|| {
                all_readings
                    .iter()
                    .map(|r| r.timestamp)
                    .max()
                    .unwrap_or_else(Utc::now)
            }),
        })
    }

    /// 导出温度数据
    pub async fn export_temperature_data(
        &self,
        sensor_id: Option<&str>,
        start_time: Option<DateTime<Utc>>,
        end_time: Option<DateTime<Utc>>,
        format: ExportFormat,
    ) -> AppResult<String> {
        let history = self.temperature_history.read().await;
        let mut export_data = Vec::new();

        // 收集数据
        for (id, readings) in history.iter() {
            if let Some(target_id) = sensor_id {
                if id != target_id {
                    continue;
                }
            }

            for reading in readings {
                if let Some(start) = start_time {
                    if reading.timestamp < start {
                        continue;
                    }
                }
                if let Some(end) = end_time {
                    if reading.timestamp > end {
                        continue;
                    }
                }

                export_data.push(reading.clone());
            }
        }

        // 按时间排序
        export_data.sort_by(|a, b| a.timestamp.cmp(&b.timestamp));

        // 根据格式导出
        match format {
            ExportFormat::Csv => {
                let mut csv =
                    String::from("timestamp,sensor_id,temperature,unit,location,status\n");
                for reading in export_data {
                    csv.push_str(&format!(
                        "{},{},{},{},{},{}\n",
                        reading.timestamp.format("%Y-%m-%d %H:%M:%S"),
                        reading.sensor_id,
                        reading.temperature,
                        reading.unit,
                        reading.location,
                        reading.status
                    ));
                }
                Ok(csv)
            }
            ExportFormat::Json => match serde_json::to_string_pretty(&export_data) {
                Ok(json) => Ok(json),
                Err(e) => Err(AppError::Serialization(format!("JSON序列化失败: {}", e))),
            },
        }
    }

    /// 导出为CSV格式
    ///
    /// # 参数
    /// * `readings` - 温度读数列表
    fn export_to_csv(&self, readings: &[TemperatureReading]) -> AppResult<String> {
        let mut csv = String::from("timestamp,sensor_id,value,unit,status\n");

        for reading in readings {
            csv.push_str(&format!(
                "{},{},{},{},{:?}\n",
                reading.timestamp.format("%Y-%m-%d %H:%M:%S"),
                reading.sensor_id,
                reading.value,
                reading.unit,
                reading.status
            ));
        }

        Ok(csv)
    }

    /// 导出为JSON格式
    ///
    /// # 参数
    /// * `readings` - 温度读数列表
    fn export_to_json(&self, readings: &[TemperatureReading]) -> AppResult<String> {
        serde_json::to_string_pretty(readings)
            .map_err(|e| AppError::serialization_error(format!("JSON序列化失败: {}", e)))
    }
}

/// 温度告警
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TemperatureAlert {
    /// 告警ID
    pub id: String,
    /// 传感器ID
    pub sensor_id: String,
    /// 温度值
    pub temperature: f64,
    /// 阈值类型
    pub threshold_type: String,
    /// 严重程度
    pub severity: AlertSeverity,
    /// 告警消息
    pub message: String,
    /// 时间戳
    pub timestamp: DateTime<Utc>,
    /// 是否已确认
    pub acknowledged: bool,
}

/// 告警严重程度
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AlertSeverity {
    /// 信息
    Info,
    /// 警告
    Warning,
    /// 严重
    Critical,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::config::IpmiConfig;

    #[tokio::test]
    async fn test_thermal_service_creation() {
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

        let thermal_service = ThermalService::new(ipmi_client, monitoring_config);

        // 测试设置和获取阈值
        let threshold = TemperatureThreshold::new(70.0, 80.0);
        thermal_service
            .set_temperature_threshold("CPU1".to_string(), threshold.clone())
            .await
            .unwrap();

        let retrieved_threshold = thermal_service.get_threshold("CPU1").await;
        assert!(retrieved_threshold.is_some());
        assert_eq!(retrieved_threshold.unwrap().warning_temp, 70.0);
    }

    #[tokio::test]
    async fn test_temperature_stats_calculation() {
        // 这里可以添加更多的单元测试
        // 由于需要实际的IPMI连接，这些测试可能需要模拟数据
    }
}
