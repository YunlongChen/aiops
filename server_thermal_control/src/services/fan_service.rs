// use crate::controllers::control_controller::FanCurve;
use crate::controllers::fan_controller::FanQueryParams;
use crate::models::{
    config::MonitoringConfig,
    error::{AppError, AppResult},
    fan::*,
};
use crate::services::ipmi_service::IpmiService;
use crate::utils::{
    ipmi::IpmiClient,
    math::{MathUtils, PidController},
    time::TimeUtils,
};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

/// 风扇服务
///
/// 负责风扇控制、监控和管理
#[derive(Clone)]
pub struct FanService {
    /// IPMI客户端
    ipmi_service: Arc<IpmiService>,
    /// 风扇配置
    fan_configs: Arc<RwLock<HashMap<String, FanConfig>>>,
    /// 风扇历史数据
    fan_history: Arc<RwLock<HashMap<String, Vec<FanReading>>>>,
    /// 控制配置
    control_config: Arc<RwLock<MonitoringConfig>>,
    /// PID控制器
    pid_controllers: Arc<RwLock<HashMap<String, PidController>>>,
    /// 数学工具
    math_utils: (),
    /// 自动控制状态
    auto_control_enabled: Arc<RwLock<bool>>,
}

impl FanService {
    /// 创建新的风扇服务
    ///
    /// # 参数
    /// * `ipmi_client` - IPMI客户端
    /// * `control_config` - 风扇控制配置
    pub fn new(ipmi_service: Arc<IpmiService>, control_config: MonitoringConfig) -> Self {
        Self {
            ipmi_service,
            fan_configs: Arc::new(RwLock::new(HashMap::new())),
            fan_history: Arc::new(RwLock::new(HashMap::new())),
            control_config: Arc::new(RwLock::new(control_config)),
            pid_controllers: Arc::new(RwLock::new(HashMap::new())),
            math_utils: (),
            auto_control_enabled: Arc::new(RwLock::new(false)),
        }
    }

    /// 获取当前风扇状态
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID，None表示获取所有风扇
    pub async fn get_current_fan_status(&self, fan_id: Option<&str>) -> AppResult<Vec<FanReading>> {
        let fans = self.ipmi_service.get_all_fan_status().await?;
        let mut readings = Vec::new();

        for (id, fan_data) in fans {
            // 如果指定了风扇ID，只返回匹配的风扇
            if let Some(target_id) = fan_id {
                if id != target_id {
                    continue;
                }
            }

            let config = self.get_fan_config(&id).await;
            let status = self.determine_fan_status(&fan_data, config.as_ref());

            let reading = FanReading::new(
                id.clone(),
                fan_data.speed_rpm.unwrap_or(0),
                fan_data.speed_percent.unwrap_or(0.0),
                status,
            );

            readings.push(reading);
        }

        // 更新历史数据
        self.update_fan_history(&readings).await;

        Ok(readings)
    }

    /// 设置风扇转速
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `speed_percent` - 转速百分比 (0-100)
    pub async fn set_fan_speed(&self, fan_id: &str, speed_percent: f64) -> AppResult<()> {
        // 验证转速范围
        if !(0.0..=100.0).contains(&speed_percent) {
            return Err(AppError::validation_error(
                "speed_percent",
                "转速百分比必须在0-100之间",
            ));
        }

        // 检查风扇配置
        let config = self.get_fan_config(fan_id).await;
        if let Some(ref cfg) = config {
            if speed_percent < cfg.min_speed_percent {
                return Err(AppError::validation_error(
                    "speed_percent",
                    &format!("转速不能低于最小值 {}%", cfg.min_speed_percent),
                ));
            }
            if speed_percent > cfg.max_speed_percent {
                return Err(AppError::validation_error(
                    "speed_percent",
                    &format!("转速不能高于最大值 {}%", cfg.max_speed_percent),
                ));
            }
        }

        // 设置风扇转速
        self.ipmi_service
            .set_fan_speed(fan_id, speed_percent as u8)
            .await?;

        // 记录操作
        log::info!("设置风扇 {} 转速为 {}%", fan_id, speed_percent);

        Ok(())
    }

    /// 设置所有风扇转速
    ///
    /// # 参数
    /// * `speed_percent` - 转速百分比 (0-100)
    pub async fn set_all_fans_speed(&self, speed_percent: f64) -> AppResult<()> {
        let fans = self.get_current_fan_status(None).await?;

        for fan in fans {
            if let Err(e) = self.set_fan_speed(&fan.fan_id, speed_percent).await {
                log::warn!("设置风扇 {} 转速失败: {}", fan.fan_id, e);
            }
        }

        Ok(())
    }

    /// 获取风扇历史数据
    ///
    /// # 参数
    /// * `query` - 查询参数
    pub async fn get_fan_history(&self, query: &FanQueryParams) -> AppResult<Vec<FanReading>> {
        let history = self.fan_history.read().await;
        let mut results = Vec::new();

        for (fan_id, readings) in history.iter() {
            // 风扇ID过滤
            if let Some(ref target_ids) = query.fan_ids {
                if !target_ids.contains(fan_id) {
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

                // 转速范围过滤
                if let Some(min_speed) = query.min_speed_percent {
                    if reading.speed_percent < min_speed {
                        continue;
                    }
                }

                if let Some(max_speed) = query.max_speed_percent {
                    if reading.speed_percent > max_speed {
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

    /// 获取风扇统计信息
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `duration_hours` - 统计时间范围（小时）
    pub async fn get_fan_stats(&self, fan_id: &str, duration_hours: u64) -> AppResult<FanStats> {
        let end_time = Utc::now();
        let start_time = end_time - chrono::Duration::hours(duration_hours as i64);

        let query = FanQueryParams {
            fan_ids: Some(vec![fan_id.to_string()]),
            start_time: Some(start_time),
            end_time: Some(end_time),
            min_speed_percent: None,
            max_speed_percent: None,
            status: None,
            limit: None,
        };

        let readings = self.get_fan_history(&query).await?;

        if readings.is_empty() {
            return Err(AppError::not_found("指定时间范围内没有风扇数据"));
        }

        let speed_values: Vec<f64> = readings.iter().map(|r| r.speed_percent).collect();
        let rpm_values: Vec<u32> = readings.iter().map(|r| r.speed_rpm).collect();

        let min_speed = speed_values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let max_speed = speed_values
            .iter()
            .fold(f64::NEG_INFINITY, |a, &b| a.max(b));
        let avg_speed = speed_values.iter().sum::<f64>() / speed_values.len() as f64;

        let min_rpm = *rpm_values.iter().min().unwrap_or(&0);
        let max_rpm = *rpm_values.iter().max().unwrap_or(&0);
        let avg_rpm = rpm_values.iter().sum::<u32>() as f64 / rpm_values.len() as f64;

        // 计算各状态的数量
        let mut normal_count = 0;
        let mut warning_count = 0;
        let mut error_count = 0;

        for reading in &readings {
            match reading.status {
                FanStatus::Normal => normal_count += 1,
                FanStatus::Warning => warning_count += 1,
                FanStatus::Error => error_count += 1,
            }
        }

        Ok(FanStats {
            fan_id: fan_id.to_string(),
            min_speed_percent: min_speed,
            max_speed_percent: max_speed,
            avg_speed_percent: avg_speed,
            min_rpm,
            max_rpm,
            avg_rpm: avg_rpm as u32,
            sample_count: readings.len(),
            normal_count,
            warning_count,
            error_count,
            start_time,
            end_time,
        })
    }

    /// 启用自动控制
    ///
    /// # 参数
    /// * `target_temperature` - 目标温度
    pub async fn enable_auto_control(&self, target_temperature: f64) -> AppResult<()> {
        let mut enabled = self.auto_control_enabled.write().await;
        *enabled = true;

        // 初始化PID控制器
        let mut controllers = self.pid_controllers.write().await;
        let config = self.control_config.read().await;

        let fans = self.get_current_fan_status(None).await?;
        for fan in fans {
            let pid = PidController::new(
                config.pid_kp.unwrap_or(1.0),
                config.pid_ki.unwrap_or(0.1),
                config.pid_kd.unwrap_or(0.05),
                target_temperature,
            );
            controllers.insert(fan.fan_id, pid);
        }

        log::info!("启用自动风扇控制，目标温度: {}°C", target_temperature);
        Ok(())
    }

    /// 禁用自动控制
    pub async fn disable_auto_control(&self) -> AppResult<()> {
        let mut enabled = self.auto_control_enabled.write().await;
        *enabled = false;

        log::info!("禁用自动风扇控制");
        Ok(())
    }

    /// 检查自动控制状态
    pub async fn is_auto_control_enabled(&self) -> bool {
        *self.auto_control_enabled.read().await
    }

    /// 执行自动控制逻辑
    ///
    /// # 参数
    /// * `current_temperature` - 当前温度
    pub async fn execute_auto_control(&self, current_temperature: f64) -> AppResult<()> {
        if !self.is_auto_control_enabled().await {
            return Ok(());
        }

        let mut controllers = self.pid_controllers.write().await;
        let config = self.control_config.read().await;

        for (fan_id, controller) in controllers.iter_mut() {
            let output = controller.update(current_temperature);

            // 将PID输出转换为风扇转速百分比
            let fan_config = self.get_fan_config(fan_id).await;
            let (min_speed, max_speed) = if let Some(ref cfg) = fan_config {
                (cfg.min_speed_percent, cfg.max_speed_percent)
            } else {
                (
                    config.min_fan_speed.unwrap_or(20.0),
                    config.max_fan_speed.unwrap_or(100.0),
                )
            };

            let speed_percent = (min_speed + (max_speed - min_speed) * (output / 100.0))
                .max(min_speed)
                .min(max_speed);

            if let Err(e) = self.set_fan_speed(fan_id, speed_percent).await {
                log::warn!("自动控制设置风扇 {} 转速失败: {}", fan_id, e);
            } else {
                log::debug!("自动控制: 风扇 {} 转速设置为 {:.1}%", fan_id, speed_percent);
            }
        }

        Ok(())
    }

    /// 设置风扇配置
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    /// * `config` - 风扇配置
    pub async fn set_fan_config(&self, fan_id: String, config: FanConfig) -> AppResult<()> {
        let mut configs = self.fan_configs.write().await;
        configs.insert(fan_id, config);
        Ok(())
    }

    /// 获取风扇配置
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    pub async fn get_fan_config(&self, fan_id: &str) -> Option<FanConfig> {
        let configs = self.fan_configs.read().await;
        configs.get(fan_id).cloned()
    }

    /// 获取所有风扇配置
    pub async fn get_all_fan_configs(&self) -> HashMap<String, FanConfig> {
        let configs = self.fan_configs.read().await;
        configs.clone()
    }

    /// 删除风扇配置
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    pub async fn remove_fan_config(&self, fan_id: &str) -> AppResult<()> {
        let mut configs = self.fan_configs.write().await;
        configs.remove(fan_id);
        Ok(())
    }

    /// 获取风扇列表
    pub async fn get_fan_list(&self) -> AppResult<Vec<String>> {
        let fans = self.ipmi_service.get_all_fan_status().await?;
        Ok(fans.keys().cloned().collect())
    }

    /// 测试风扇
    ///
    /// # 参数
    /// * `fan_id` - 风扇ID
    pub async fn test_fan(&self, fan_id: &str) -> AppResult<FanTestResult> {
        let initial_reading = self.get_current_fan_status(Some(fan_id)).await?;
        if initial_reading.is_empty() {
            return Err(AppError::not_found(&format!("风扇 {} 不存在", fan_id)));
        }

        let initial_speed = initial_reading[0].speed_percent;
        let mut test_results = Vec::new();

        // 测试不同转速
        let test_speeds = vec![30.0, 50.0, 70.0, 90.0];

        for &test_speed in &test_speeds {
            // 设置测试转速
            self.set_fan_speed(fan_id, test_speed).await?;

            // 等待稳定
            tokio::time::sleep(tokio::time::Duration::from_secs(3)).await;

            // 读取实际转速
            let reading = self.get_current_fan_status(Some(fan_id)).await?;
            if !reading.is_empty() {
                let actual_speed = reading[0].speed_percent;
                let speed_diff = (actual_speed - test_speed).abs();

                test_results.push(FanSpeedTest {
                    target_speed: test_speed,
                    actual_speed,
                    speed_difference: speed_diff,
                    response_time_ms: 3000, // 简化处理
                });
            }
        }

        // 恢复初始转速
        self.set_fan_speed(fan_id, initial_speed).await?;

        // 分析测试结果
        let avg_error = test_results.iter().map(|t| t.speed_difference).sum::<f64>()
            / test_results.len() as f64;

        let test_passed = avg_error < 5.0; // 平均误差小于5%认为测试通过

        Ok(FanTestResult {
            fan_id: fan_id.to_string(),
            test_passed,
            average_error: avg_error,
            speed_tests: test_results,
            timestamp: Utc::now(),
        })
    }

    /// 优化风扇曲线
    ///
    /// # 参数
    /// * `temperature_readings` - 温度读数历史
    pub async fn optimize_fan_curve(&self, temperature_readings: &[f64]) -> AppResult<FanCurve> {
        if temperature_readings.len() < 10 {
            return Err(AppError::validation_error(
                "temperature_readings",
                "温度数据不足，无法优化风扇曲线",
            ));
        }

        let min_temp = temperature_readings
            .iter()
            .fold(f64::INFINITY, |a, &b| a.min(b));
        let max_temp = temperature_readings
            .iter()
            .fold(f64::NEG_INFINITY, |a, &b| a.max(b));

        // 创建优化的风扇曲线点
        let mut curve_points = Vec::new();

        // 基础曲线点
        curve_points.push(FanCurvePoint {
            temperature: min_temp,
            fan_speed_percent: 20.0,
        });
        curve_points.push(FanCurvePoint {
            temperature: min_temp + (max_temp - min_temp) * 0.3,
            fan_speed_percent: 30.0,
        });
        curve_points.push(FanCurvePoint {
            temperature: min_temp + (max_temp - min_temp) * 0.6,
            fan_speed_percent: 50.0,
        });
        curve_points.push(FanCurvePoint {
            temperature: min_temp + (max_temp - min_temp) * 0.8,
            fan_speed_percent: 75.0,
        });
        curve_points.push(FanCurvePoint {
            temperature: max_temp,
            fan_speed_percent: 100.0,
        });

        Ok(FanCurve {
            name: "优化曲线".to_string(),
            description: Some("基于历史温度数据优化的风扇曲线".to_string()),
            points: curve_points,
            hysteresis: 2.0, // 2度滞后
            created_at: Utc::now(),
        })
    }

    /// 应用风扇曲线
    ///
    /// # 参数
    /// * `curve` - 风扇曲线
    /// * `current_temperature` - 当前温度
    pub async fn apply_fan_curve(
        &self,
        curve: &FanCurve,
        current_temperature: f64,
    ) -> AppResult<()> {
        let target_speed = self.calculate_fan_speed_from_curve(curve, current_temperature);
        self.set_all_fans_speed(target_speed).await?;

        log::info!(
            "应用风扇曲线: 温度 {}°C -> 风扇转速 {}%",
            current_temperature,
            target_speed
        );
        Ok(())
    }

    /// 从风扇曲线计算目标转速
    ///
    /// # 参数
    /// * `curve` - 风扇曲线
    /// * `temperature` - 当前温度
    fn calculate_fan_speed_from_curve(&self, curve: &FanCurve, temperature: f64) -> f64 {
        let points = &curve.points;

        if points.is_empty() {
            return 50.0; // 默认转速
        }

        // 如果温度低于最低点
        if temperature <= points[0].temperature {
            return points[0].fan_speed_percent;
        }

        // 如果温度高于最高点
        if temperature >= points[points.len() - 1].temperature {
            return points[points.len() - 1].fan_speed_percent;
        }

        // 线性插值
        for i in 0..points.len() - 1 {
            let p1 = &points[i];
            let p2 = &points[i + 1];

            if temperature >= p1.temperature && temperature <= p2.temperature {
                let ratio = (temperature - p1.temperature) / (p2.temperature - p1.temperature);
                return p1.fan_speed_percent
                    + ratio * (p2.fan_speed_percent - p1.fan_speed_percent);
            }
        }

        50.0 // 默认转速
    }

    /// 确定风扇状态
    ///
    /// # 参数
    /// * `fan_data` - 风扇数据
    /// * `config` - 风扇配置
    fn determine_fan_status(
        &self,
        fan_data: &crate::utils::ipmi::SensorData,
        config: Option<&FanConfig>,
    ) -> FanStatus {
        // 检查风扇是否运行
        if let Some(speed_rpm) = fan_data.speed_rpm {
            if speed_rpm == 0 {
                return FanStatus::Error;
            }
        }

        // 检查转速是否在正常范围内
        if let Some(speed_percent) = fan_data.speed_percent {
            if let Some(cfg) = config {
                if speed_percent < cfg.min_speed_percent || speed_percent > cfg.max_speed_percent {
                    return FanStatus::Warning;
                }
            }
        }

        FanStatus::Normal
    }

    /// 更新风扇历史数据
    ///
    /// # 参数
    /// * `readings` - 风扇读数列表
    async fn update_fan_history(&self, readings: &[FanReading]) {
        let mut history = self.fan_history.write().await;
        let config = self.control_config.read().await;

        for reading in readings {
            let fan_history = history
                .entry(reading.fan_id.clone())
                .or_insert_with(Vec::new);
            fan_history.push(reading.clone());

            // 限制历史数据数量
            let max_history = config.data_retention_hours.unwrap_or(24) * 60; // 假设每分钟一个数据点
            if fan_history.len() > max_history {
                fan_history.drain(0..fan_history.len() - max_history);
            }
        }
    }

    /// 清理过期的历史数据
    pub async fn cleanup_expired_data(&self) -> AppResult<usize> {
        let mut history = self.fan_history.write().await;
        let config = self.control_config.read().await;
        let retention_hours = config.data_retention_hours.unwrap_or(24);
        let cutoff_time = Utc::now() - chrono::Duration::hours(retention_hours as i64);

        let mut removed_count = 0;

        for (_, readings) in history.iter_mut() {
            let original_len = readings.len();
            readings.retain(|reading| reading.timestamp > cutoff_time);
            removed_count += original_len - readings.len();
        }

        Ok(removed_count)
    }
}

/// 风扇测试结果
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FanTestResult {
    /// 风扇ID
    pub fan_id: String,
    /// 测试是否通过
    pub test_passed: bool,
    /// 平均误差
    pub average_error: f64,
    /// 转速测试结果
    pub speed_tests: Vec<FanSpeedTest>,
    /// 测试时间
    pub timestamp: DateTime<Utc>,
}

/// 风扇转速测试
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FanSpeedTest {
    /// 目标转速
    pub target_speed: f64,
    /// 实际转速
    pub actual_speed: f64,
    /// 转速差异
    pub speed_difference: f64,
    /// 响应时间（毫秒）
    pub response_time_ms: u64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::config::IpmiConfig;

    #[tokio::test]
    async fn test_fan_service_creation() {
        let ipmi_config = IpmiConfig {
            host: "192.168.3.48".to_string(),
            username: "test".to_string(),
            password: "test".to_string(),
            interface: Some("lanplus".to_string()),
            port: Some(623),
            timeout: Some(5),
        };

        let ipmi_client = Arc::new(IpmiClient::new(ipmi_config));
        let control_config = FanControlConfig {
            enabled: true,
            mode: Some("auto".to_string()),
            target_temperature: Some(65.0),
            min_fan_speed: Some(20.0),
            max_fan_speed: Some(100.0),
            pid_kp: Some(1.0),
            pid_ki: Some(0.1),
            pid_kd: Some(0.05),
            update_interval_seconds: Some(30),
            data_retention_hours: Some(24),
        };

        let fan_service = FanService::new(ipmi_client, control_config);

        // 测试设置和获取风扇配置
        let config = FanConfig {
            name: "CPU风扇".to_string(),
            description: Some("CPU散热风扇".to_string()),
            min_speed_percent: 20.0,
            max_speed_percent: 100.0,
            critical_speed_percent: Some(90.0),
            sensor_association: Some("CPU1".to_string()),
        };

        fan_service
            .set_fan_config("FAN1".to_string(), config.clone())
            .await
            .unwrap();

        let retrieved_config = fan_service.get_fan_config("FAN1").await;
        assert!(retrieved_config.is_some());
        assert_eq!(retrieved_config.unwrap().name, "CPU风扇");
    }

    #[test]
    fn test_fan_curve_calculation() {
        let fan_service = FanService::new(
            Arc::new(IpmiClient::new(crate::models::config::IpmiConfig {
                host: "test".to_string(),
                username: "test".to_string(),
                password: "test".to_string(),
                interface: None,
                port: None,
                timeout: None,
            })),
            FanControlConfig {
                enabled: true,
                mode: None,
                target_temperature: None,
                min_fan_speed: None,
                max_fan_speed: None,
                pid_kp: None,
                pid_ki: None,
                pid_kd: None,
                update_interval_seconds: None,
                data_retention_hours: None,
            },
        );

        let curve = FanCurve {
            name: "测试曲线".to_string(),
            description: None,
            points: vec![
                FanCurvePoint {
                    temperature: 40.0,
                    fan_speed_percent: 20.0,
                },
                FanCurvePoint {
                    temperature: 60.0,
                    fan_speed_percent: 50.0,
                },
                FanCurvePoint {
                    temperature: 80.0,
                    fan_speed_percent: 100.0,
                },
            ],
            hysteresis: 2.0,
            created_at: Utc::now(),
        };

        // 测试线性插值
        let speed = fan_service.calculate_fan_speed_from_curve(&curve, 50.0);
        assert!((speed - 35.0).abs() < 0.1); // 50度应该对应35%转速

        // 测试边界值
        let speed_low = fan_service.calculate_fan_speed_from_curve(&curve, 30.0);
        assert_eq!(speed_low, 20.0); // 低于最低温度

        let speed_high = fan_service.calculate_fan_speed_from_curve(&curve, 90.0);
        assert_eq!(speed_high, 100.0); // 高于最高温度
    }
}
