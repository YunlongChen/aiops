use crate::models::{
    alert::*, error::{AppError, AppResult}, fan::FanReading, sensor::SensorReading, thermal::TemperatureReading, Alert
};
use crate::controllers::alert_controller::{AlertType, AlertFilter};
use crate::utils::{
    time::TimeUtils,
    logger::LoggerManager,
    validation::ValidationUtils,
};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::{RwLock, Mutex};
use tokio::time::{interval, Duration};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use tracing::{info, warn, error, debug};

/// 告警服务
/// 
/// 负责系统告警、通知和事件管理
#[derive(Clone)]
pub struct AlertService {
    /// 告警配置
    config: Arc<RwLock<AlertConfig>>,
    /// 活跃告警
    active_alerts: Arc<RwLock<HashMap<String, Alert>>>,
    /// 告警历史
    alert_history: Arc<RwLock<Vec<Alert>>>,
    /// 告警规则
    alert_rules: Arc<RwLock<HashMap<String, AlertRule>>>,
    /// 通知渠道
    notification_channels: Arc<RwLock<HashMap<String, NotificationChannel>>>,
    /// 告警统计
    alert_stats: Arc<RwLock<AlertStatistics>>,
    /// 任务句柄
    task_handles: Arc<Mutex<Vec<tokio::task::JoinHandle<()>>>>,
    /// 时间工具
    time_utils: TimeUtils,
}

impl AlertService {
    /// 创建新的告警服务
    pub fn new() -> Self {
        Self {
            config: Arc::new(RwLock::new(AlertConfig::default())),
            active_alerts: Arc::new(RwLock::new(HashMap::new())),
            alert_history: Arc::new(RwLock::new(Vec::new())),
            alert_rules: Arc::new(RwLock::new(HashMap::new())),
            notification_channels: Arc::new(RwLock::new(HashMap::new())),
            alert_stats: Arc::new(RwLock::new(AlertStatistics::default())),
            task_handles: Arc::new(Mutex::new(Vec::new())),
            time_utils: TimeUtils,
        }
    }

    /// 启动告警服务
    pub async fn start(&self) -> AppResult<()> {
        info!("启动告警服务");

        // 初始化默认告警规则
        self.initialize_default_rules().await?;

        // 启动告警检查任务
        self.start_alert_monitoring().await?;

        // 启动告警清理任务
        self.start_alert_cleanup().await?;

        info!("告警服务启动完成");
        Ok(())
    }

    /// 停止告警服务
    pub async fn stop(&self) -> AppResult<()> {
        info!("停止告警服务");

        // 停止所有任务
        let mut handles = self.task_handles.lock().await;
        for handle in handles.drain(..) {
            handle.abort();
        }

        info!("告警服务已停止");
        Ok(())
    }

    /// 创建告警
    /// 
    /// # 参数
    /// * `alert_type` - 告警类型
    /// * `severity` - 告警严重程度
    /// * `source` - 告警源
    /// * `message` - 告警消息
    /// * `details` - 告警详情
    pub async fn create_alert(
        &self,
        alert_type: AlertType,
        severity: AlertSeverity,
        source: String,
        message: String,
        details: Option<HashMap<String, String>>,
    ) -> AppResult<String> {
        let alert_id = uuid::Uuid::new_v4();
        
        let alert = Alert {
            id: alert_id.clone(),
            alert_type,
            severity,
            source,
            message,
            status: AlertStatus::Active,
            created_at: Utc::now(),
            updated_at: Utc::now(),
            acknowledged_at: None,
            acknowledged_by: None,
            resolved_at: None,
            title: todo!(),
            source_id: todo!(),
            acknowledged: todo!(),
        };

        info!("创建告警: {} - {} - {}", alert_id, alert.alert_type, alert.message);

        // 添加到活跃告警
        {
            let mut active_alerts = self.active_alerts.write().await;
            active_alerts.insert(alert_id.clone(), alert.clone());
        }

        // 添加到历史记录
        {
            let mut history = self.alert_history.write().await;
            history.push(alert.clone());
            
            // 限制历史记录数量
            if history.len() > 10000 {
                history.drain(0..1000);
            }
        }

        // 更新统计信息
        self.update_alert_statistics(&alert, true).await;

        // 发送通知
        self.send_alert_notification(&alert).await?;

        debug!("告警创建完成: {}", alert_id);
        Ok(alert_id)
    }

    /// 确认告警
    /// 
    /// # 参数
    /// * `alert_id` - 告警ID
    /// * `acknowledged_by` - 确认人
    pub async fn acknowledge_alert(&self, alert_id: &str, acknowledged_by: String) -> AppResult<()> {
        info!("确认告警: {} by {}", alert_id, acknowledged_by);

        let mut active_alerts = self.active_alerts.write().await;
        
        if let Some(alert) = active_alerts.get_mut(alert_id) {
            alert.status = AlertStatus::Acknowledged;
            alert.acknowledged_at = Some(Utc::now());
            alert.acknowledged_by = Some(acknowledged_by);
            alert.updated_at = Utc::now();

            // 更新历史记录
            self.update_alert_in_history(alert).await;

            info!("告警确认完成: {}", alert_id);
            Ok(())
        } else {
            Err(AppError::NotFoundError(format!("告警不存在: {}", alert_id)))
        }
    }

    /// 解决告警
    /// 
    /// # 参数
    /// * `alert_id` - 告警ID
    /// * `resolved_by` - 解决人
    pub async fn resolve_alert(&self, alert_id: &str, resolved_by: String) -> AppResult<()> {
        info!("解决告警: {} by {}", alert_id, resolved_by);

        let mut active_alerts = self.active_alerts.write().await;
        
        if let Some(alert) = active_alerts.remove(alert_id) {
            let mut resolved_alert = alert;
            resolved_alert.status = AlertStatus::Resolved;
            resolved_alert.resolved_at = Some(Utc::now());
            resolved_alert.resolved_by = Some(resolved_by);
            resolved_alert.updated_at = Utc::now();

            // 更新历史记录
            self.update_alert_in_history(&resolved_alert).await;

            // 更新统计信息
            self.update_alert_statistics(&resolved_alert, false).await;

            info!("告警解决完成: {}", alert_id);
            Ok(())
        } else {
            Err(AppError::NotFound(format!("告警不存在: {}", alert_id)))
        }
    }

    /// 获取活跃告警
    pub async fn get_active_alerts(&self) -> Vec<Alert> {
        let active_alerts = self.active_alerts.read().await;
        active_alerts.values().cloned().collect()
    }

    /// 获取告警历史
    /// 
    /// # 参数
    /// * `filter` - 过滤条件
    pub async fn get_alert_history(&self, filter: Option<AlertFilter>) -> Vec<Alert> {
        let history = self.alert_history.read().await;
        
        if let Some(filter) = filter {
            history.iter()
                .filter(|alert| self.matches_filter(alert, &filter))
                .cloned()
                .collect()
        } else {
            history.clone()
        }
    }

    /// 获取告警统计
    pub async fn get_alert_statistics(&self) -> AlertStatistics {
        self.alert_stats.read().await.clone()
    }

    /// 添加告警规则
    /// 
    /// # 参数
    /// * `rule` - 告警规则
    pub async fn add_alert_rule(&self, rule: AlertRule) -> AppResult<()> {
        info!("添加告警规则: {}", rule.name);

        // 验证规则
        rule.validate()?;

        let mut rules = self.alert_rules.write().await;
        rules.insert(rule.id.clone(), rule);

        info!("告警规则添加完成");
        Ok(())
    }

    /// 移除告警规则
    /// 
    /// # 参数
    /// * `rule_id` - 规则ID
    pub async fn remove_alert_rule(&self, rule_id: &str) -> AppResult<()> {
        info!("移除告警规则: {}", rule_id);

        let mut rules = self.alert_rules.write().await;
        if rules.remove(rule_id).is_some() {
            info!("告警规则移除完成: {}", rule_id);
            Ok(())
        } else {
            Err(AppError::NotFound(format!("告警规则不存在: {}", rule_id)))
        }
    }

    /// 获取所有告警规则
    pub async fn get_alert_rules(&self) -> Vec<AlertRule> {
        let rules = self.alert_rules.read().await;
        rules.values().cloned().collect()
    }

    /// 添加通知渠道
    /// 
    /// # 参数
    /// * `channel` - 通知渠道
    pub async fn add_notification_channel(&self, channel: NotificationChannel) -> AppResult<()> {
        info!("添加通知渠道: {} ({})", channel.name, channel.channel_type);

        // 验证渠道配置
        channel.validate()?;

        let mut channels = self.notification_channels.write().await;
        channels.insert(channel.id.clone(), channel);

        info!("通知渠道添加完成");
        Ok(())
    }

    /// 移除通知渠道
    /// 
    /// # 参数
    /// * `channel_id` - 渠道ID
    pub async fn remove_notification_channel(&self, channel_id: &str) -> AppResult<()> {
        info!("移除通知渠道: {}", channel_id);

        let mut channels = self.notification_channels.write().await;
        if channels.remove(channel_id).is_some() {
            info!("通知渠道移除完成: {}", channel_id);
            Ok(())
        } else {
            Err(AppError::NotFound(format!("通知渠道不存在: {}", channel_id)))
        }
    }

    /// 获取所有通知渠道
    pub async fn get_notification_channels(&self) -> Vec<NotificationChannel> {
        let channels = self.notification_channels.read().await;
        channels.values().cloned().collect()
    }

    /// 测试通知渠道
    /// 
    /// # 参数
    /// * `channel_id` - 渠道ID
    pub async fn test_notification_channel(&self, channel_id: &str) -> AppResult<()> {
        info!("测试通知渠道: {}", channel_id);

        let channels = self.notification_channels.read().await;
        if let Some(channel) = channels.get(channel_id) {
            // 创建测试告警
            let test_alert = Alert {
                id: "test".to_string(),
                alert_type: AlertType::System,
                severity: AlertSeverity::Info,
                source: "test".to_string(),
                message: "通知渠道测试消息".to_string(),
                details: HashMap::new(),
                status: AlertStatus::Active,
                created_at: Utc::now(),
                updated_at: Utc::now(),
                acknowledged_at: None,
                acknowledged_by: None,
                resolved_at: None,
                resolved_by: None,
                escalation_level: 0,
                notification_sent: false,
            };

            // 发送测试通知
            self.send_notification_to_channel(channel, &test_alert).await?;

            info!("通知渠道测试完成: {}", channel_id);
            Ok(())
        } else {
            Err(AppError::NotFound(format!("通知渠道不存在: {}", channel_id)))
        }
    }

    /// 检查温度告警
    /// 
    /// # 参数
    /// * `temperature_reading` - 温度读数
    pub async fn check_temperature_alert(&self, temperature_reading: &TemperatureReading) -> AppResult<()> {
        let rules = self.alert_rules.read().await;
        
        for rule in rules.values() {
            if rule.rule_type == AlertRuleType::Temperature && rule.enabled {
                if self.evaluate_temperature_rule(rule, temperature_reading).await? {
                    // 创建温度告警
                    let severity = self.determine_temperature_severity(temperature_reading.temperature, rule);
                    let mut details = HashMap::new();
                    details.insert("sensor_id".to_string(), temperature_reading.sensor_id.clone());
                    details.insert("temperature".to_string(), temperature_reading.temperature.to_string());
                    details.insert("threshold".to_string(), rule.threshold.to_string());

                    self.create_alert(
                        AlertType::Temperature,
                        severity,
                        temperature_reading.sensor_id.clone(),
                        format!("温度异常: {:.1}°C (阈值: {:.1}°C)", 
                               temperature_reading.temperature, rule.threshold),
                        Some(details),
                    ).await?;
                }
            }
        }

        Ok(())
    }

    /// 检查风扇告警
    /// 
    /// # 参数
    /// * `fan_reading` - 风扇读数
    pub async fn check_fan_alert(&self, fan_reading: &FanReading) -> AppResult<()> {
        let rules = self.alert_rules.read().await;
        
        for rule in rules.values() {
            if rule.rule_type == AlertRuleType::Fan && rule.enabled {
                if self.evaluate_fan_rule(rule, fan_reading).await? {
                    // 创建风扇告警
                    let severity = self.determine_fan_severity(fan_reading, rule);
                    let mut details = HashMap::new();
                    details.insert("fan_id".to_string(), fan_reading.fan_id.clone());
                    details.insert("speed_rpm".to_string(), fan_reading.speed_rpm.to_string());
                    details.insert("speed_percent".to_string(), fan_reading.speed_percent.to_string());

                    self.create_alert(
                        AlertType::Fan,
                        severity,
                        fan_reading.fan_id.clone(),
                        format!("风扇异常: {} RPM ({:.1}%)", 
                               fan_reading.speed_rpm, fan_reading.speed_percent),
                        Some(details),
                    ).await?;
                }
            }
        }

        Ok(())
    }

    /// 检查传感器告警
    /// 
    /// # 参数
    /// * `sensor_reading` - 传感器读数
    pub async fn check_sensor_alert(&self, sensor_reading: &SensorReading) -> AppResult<()> {
        let rules = self.alert_rules.read().await;
        
        for rule in rules.values() {
            if rule.rule_type == AlertRuleType::Sensor && rule.enabled {
                if self.evaluate_sensor_rule(rule, sensor_reading).await? {
                    // 创建传感器告警
                    let severity = AlertSeverity::Warning; // 默认警告级别
                    let mut details = HashMap::new();
                    details.insert("sensor_id".to_string(), sensor_reading.sensor_id.clone());
                    details.insert("value".to_string(), sensor_reading.value.to_string());
                    details.insert("status".to_string(), format!("{:?}", sensor_reading.status));

                    self.create_alert(
                        AlertType::Sensor,
                        severity,
                        sensor_reading.sensor_id.clone(),
                        format!("传感器异常: {} = {:.2} {}", 
                               sensor_reading.sensor_id, sensor_reading.value, sensor_reading.unit),
                        Some(details),
                    ).await?;
                }
            }
        }

        Ok(())
    }

    /// 创建系统告警
    /// 
    /// # 参数
    /// * `message` - 告警消息
    /// * `severity` - 严重程度
    /// * `details` - 详细信息
    pub async fn create_system_alert(
        &self,
        message: String,
        severity: AlertSeverity,
        details: Option<HashMap<String, String>>,
    ) -> AppResult<String> {
        self.create_alert(
            AlertType::System,
            severity,
            "system".to_string(),
            message,
            details,
        ).await
    }

    // 私有方法

    /// 初始化默认告警规则
    async fn initialize_default_rules(&self) -> AppResult<()> {
        info!("初始化默认告警规则");

        let mut rules = self.alert_rules.write().await;

        // 高温告警规则
        let high_temp_rule = AlertRule {
            id: "high_temperature".to_string(),
            name: "高温告警".to_string(),
            description: "当温度超过阈值时触发告警".to_string(),
            rule_type: AlertRuleType::Temperature,
            condition: AlertCondition::GreaterThan,
            threshold: 80.0,
            duration: 60, // 持续60秒
            severity: AlertSeverity::Critical,
            enabled: true,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };
        rules.insert(high_temp_rule.id.clone(), high_temp_rule);

        // 风扇故障告警规则
        let fan_failure_rule = AlertRule {
            id: "fan_failure".to_string(),
            name: "风扇故障告警".to_string(),
            description: "当风扇转速异常时触发告警".to_string(),
            rule_type: AlertRuleType::Fan,
            condition: AlertCondition::LessThan,
            threshold: 500.0, // RPM
            duration: 30,
            severity: AlertSeverity::Critical,
            enabled: true,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };
        rules.insert(fan_failure_rule.id.clone(), fan_failure_rule);

        // 温度警告规则
        let temp_warning_rule = AlertRule {
            id: "temperature_warning".to_string(),
            name: "温度警告".to_string(),
            description: "当温度接近阈值时触发警告".to_string(),
            rule_type: AlertRuleType::Temperature,
            condition: AlertCondition::GreaterThan,
            threshold: 70.0,
            duration: 120,
            severity: AlertSeverity::Warning,
            enabled: true,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };
        rules.insert(temp_warning_rule.id.clone(), temp_warning_rule);

        info!("默认告警规则初始化完成，共创建 {} 个规则", rules.len());
        Ok(())
    }

    /// 启动告警监控
    async fn start_alert_monitoring(&self) -> AppResult<()> {
        let active_alerts = Arc::clone(&self.active_alerts);
        let alert_stats = Arc::clone(&self.alert_stats);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(30)); // 每30秒检查一次

            loop {
                interval.tick().await;

                // 检查告警升级
                let alerts = active_alerts.read().await;
                for alert in alerts.values() {
                    // 检查是否需要升级告警
                    if Self::should_escalate_alert(alert) {
                        debug!("告警需要升级: {}", alert.id);
                        // 这里可以实现告警升级逻辑
                    }
                }

                // 更新统计信息
                let mut stats = alert_stats.write().await;
                stats.active_alerts_count = alerts.len();
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 启动告警清理
    async fn start_alert_cleanup(&self) -> AppResult<()> {
        let alert_history = Arc::clone(&self.alert_history);
        let config = Arc::clone(&self.config);

        let handle = tokio::spawn(async move {
            let mut interval = interval(Duration::from_secs(3600)); // 每小时清理一次

            loop {
                interval.tick().await;

                let retention_days = {
                    let cfg = config.read().await;
                    cfg.alert_retention_days
                };

                // 清理过期的告警历史
                let cutoff_time = Utc::now() - chrono::Duration::days(retention_days as i64);
                let mut history = alert_history.write().await;
                let original_len = history.len();
                
                history.retain(|alert| alert.created_at > cutoff_time);
                
                let removed_count = original_len - history.len();
                if removed_count > 0 {
                    info!("清理过期告警历史: {} 条", removed_count);
                }
            }
        });

        self.task_handles.lock().await.push(handle);
        Ok(())
    }

    /// 发送告警通知
    async fn send_alert_notification(&self, alert: &Alert) -> AppResult<()> {
        let channels = self.notification_channels.read().await;
        
        for channel in channels.values() {
            if channel.enabled && self.should_send_to_channel(channel, alert) {
                if let Err(e) = self.send_notification_to_channel(channel, alert).await {
                    error!("发送通知失败 (渠道: {}): {}", channel.name, e);
                } else {
                    debug!("通知发送成功 (渠道: {})", channel.name);
                }
            }
        }

        Ok(())
    }

    /// 发送通知到指定渠道
    async fn send_notification_to_channel(&self, channel: &NotificationChannel, alert: &Alert) -> AppResult<()> {
        match channel.channel_type {
            ChannelType::Email => {
                self.send_email_notification(channel, alert).await
            },
            ChannelType::Webhook => {
                self.send_webhook_notification(channel, alert).await
            },
            ChannelType::Slack => {
                self.send_slack_notification(channel, alert).await
            },
            ChannelType::Sms => {
                self.send_sms_notification(channel, alert).await
            },
            ChannelType::DingTalk => {
                self.send_sms_notification(channel, alert).await
            },
        }
    }

    /// 发送邮件通知
    async fn send_email_notification(&self, channel: &NotificationChannel, alert: &Alert) -> AppResult<()> {
        // 简化实现，实际应该集成邮件发送服务
        info!("发送邮件通知: {} -> {}", alert.message, channel.config.get("email").unwrap_or(&"unknown".to_string()));
        Ok(())
    }

    /// 发送Webhook通知
    async fn send_webhook_notification(&self, channel: &NotificationChannel, alert: &Alert) -> AppResult<()> {
        // 简化实现，实际应该发送HTTP请求
        info!("发送Webhook通知: {} -> {}", alert.message, channel.config.get("url").unwrap_or(&"unknown".to_string()));
        Ok(())
    }

    /// 发送Slack通知
    async fn send_slack_notification(&self, channel: &NotificationChannel, alert: &Alert) -> AppResult<()> {
        // 简化实现，实际应该调用Slack API
        info!("发送Slack通知: {} -> {}", alert.message, channel.config.get("webhook_url").unwrap_or(&"unknown".to_string()));
        Ok(())
    }

    /// 发送短信通知
    async fn send_sms_notification(&self, channel: &NotificationChannel, alert: &Alert) -> AppResult<()> {
        // 简化实现，实际应该集成短信服务
        info!("发送短信通知: {} -> {}", alert.message, channel.config.get("phone").unwrap_or(&"unknown".to_string()));
        Ok(())
    }

    /// 判断是否应该发送到指定渠道
    fn should_send_to_channel(&self, channel: &NotificationChannel, alert: &Alert) -> bool {
        // 检查严重程度过滤
        if let Some(min_severity) = &channel.severity_filter {
            if !Self::severity_meets_threshold(&alert.severity, min_severity) {
                return false;
            }
        }

        // 检查告警类型过滤
        if let Some(alert_types) = &channel.alert_type_filter {
            if !alert_types.contains(&alert.alert_type) {
                return false;
            }
        }

        true
    }

    /// 检查严重程度是否满足阈值
    fn severity_meets_threshold(current: &AlertSeverity, threshold: &AlertSeverity) -> bool {
        let current_level = match current {
            AlertSeverity::Info => 1,
            AlertSeverity::Warning => 2,
            AlertSeverity::Critical => 3,
        };

        let threshold_level = match threshold {
            AlertSeverity::Info => 1,
            AlertSeverity::Warning => 2,
            AlertSeverity::Critical => 3,
        };

        current_level >= threshold_level
    }

    /// 判断是否应该升级告警
    fn should_escalate_alert(alert: &Alert) -> bool {
        // 简化的升级逻辑
        let duration_since_created = Utc::now().signed_duration_since(alert.created_at);
        
        match alert.severity {
            AlertSeverity::Critical => duration_since_created.num_minutes() > 15,
            AlertSeverity::Warning => duration_since_created.num_minutes() > 60,
            AlertSeverity::Info => false,
        }
    }

    /// 更新告警统计
    async fn update_alert_statistics(&self, alert: &Alert, is_new: bool) {
        let mut stats = self.alert_stats.write().await;
        
        if is_new {
            stats.total_alerts += 1;
            match alert.severity {
                AlertSeverity::Critical => stats.critical_alerts += 1,
                AlertSeverity::Warning => stats.warning_alerts += 1,
                AlertSeverity::Info => stats.info_alerts += 1,
            }
        } else {
            // 告警解决时的统计更新
            stats.resolved_alerts += 1;
        }

        stats.last_updated = Utc::now();
    }

    /// 更新历史记录中的告警
    async fn update_alert_in_history(&self, updated_alert: &Alert) {
        let mut history = self.alert_history.write().await;
        
        if let Some(alert) = history.iter_mut().find(|a| a.id == updated_alert.id) {
            *alert = updated_alert.clone();
        }
    }

    /// 检查过滤条件匹配
    fn matches_filter(&self, alert: &Alert, filter: &AlertFilter) -> bool {
        // 检查时间范围
        if let Some(start_time) = filter.start_time {
            if alert.created_at < start_time {
                return false;
            }
        }

        if let Some(end_time) = filter.end_time {
            if alert.created_at > end_time {
                return false;
            }
        }

        // 检查严重程度
        if let Some(severity) = &filter.severity {
            if &alert.severity != severity {
                return false;
            }
        }

        // 检查告警类型
        if let Some(alert_type) = &filter.alert_type {
            if &alert.alert_type != alert_type {
                return false;
            }
        }

        // 检查状态
        if let Some(status) = &filter.status {
            if &alert.status != status {
                return false;
            }
        }

        // 检查源
        if let Some(source) = &filter.source {
            if &alert.source != source {
                return false;
            }
        }

        true
    }

    /// 评估温度规则
    async fn evaluate_temperature_rule(&self, rule: &AlertRule, reading: &TemperatureReading) -> AppResult<bool> {
        match rule.condition {
            AlertCondition::GreaterThan => Ok(reading.temperature > rule.threshold),
            AlertCondition::LessThan => Ok(reading.temperature < rule.threshold),
            AlertCondition::Equals => Ok((reading.temperature - rule.threshold).abs() < 0.1),
        }
    }

    /// 评估风扇规则
    async fn evaluate_fan_rule(&self, rule: &AlertRule, reading: &FanReading) -> AppResult<bool> {
        let value = reading.speed_rpm as f64;
        match rule.condition {
            AlertCondition::GreaterThan => Ok(value > rule.threshold),
            AlertCondition::LessThan => Ok(value < rule.threshold),
            AlertCondition::Equals => Ok((value - rule.threshold).abs() < 1.0),
        }
    }

    /// 评估传感器规则
    async fn evaluate_sensor_rule(&self, rule: &AlertRule, reading: &SensorReading) -> AppResult<bool> {
        match rule.condition {
            AlertCondition::GreaterThan => Ok(reading.value > rule.threshold),
            AlertCondition::LessThan => Ok(reading.value < rule.threshold),
            AlertCondition::Equals => Ok((reading.value - rule.threshold).abs() < 0.01),
        }
    }

    /// 确定温度告警严重程度
    fn determine_temperature_severity(&self, temperature: f64, rule: &AlertRule) -> AlertSeverity {
        if temperature > rule.threshold + 10.0 {
            AlertSeverity::Critical
        } else if temperature > rule.threshold + 5.0 {
            AlertSeverity::Warning
        } else {
            AlertSeverity::Info
        }
    }

    /// 确定风扇告警严重程度
    fn determine_fan_severity(&self, reading: &FanReading, rule: &AlertRule) -> AlertSeverity {
        if reading.speed_rpm == 0 {
            AlertSeverity::Critical
        } else if reading.speed_rpm < rule.threshold as u32 {
            AlertSeverity::Warning
        } else {
            AlertSeverity::Info
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_create_alert() {
        let service = AlertService::new();
        
        let alert_id = service.create_alert(
            AlertType::Temperature,
            AlertSeverity::Warning,
            "test_sensor".to_string(),
            "测试告警".to_string(),
            None,
        ).await.unwrap();

        assert!(!alert_id.is_empty());

        let active_alerts = service.get_active_alerts().await;
        assert_eq!(active_alerts.len(), 1);
        assert_eq!(active_alerts[0].id, alert_id);
    }

    #[tokio::test]
    async fn test_acknowledge_alert() {
        let service = AlertService::new();
        
        let alert_id = service.create_alert(
            AlertType::System,
            AlertSeverity::Info,
            "test".to_string(),
            "测试告警".to_string(),
            None,
        ).await.unwrap();

        service.acknowledge_alert(&alert_id, "test_user".to_string()).await.unwrap();

        let active_alerts = service.get_active_alerts().await;
        assert_eq!(active_alerts[0].status, AlertStatus::Acknowledged);
        assert_eq!(active_alerts[0].acknowledged_by, Some("test_user".to_string()));
    }

    #[tokio::test]
    async fn test_resolve_alert() {
        let service = AlertService::new();
        
        let alert_id = service.create_alert(
            AlertType::Fan,
            AlertSeverity::Critical,
            "test_fan".to_string(),
            "风扇故障".to_string(),
            None,
        ).await.unwrap();

        service.resolve_alert(&alert_id, "test_user".to_string()).await.unwrap();

        let active_alerts = service.get_active_alerts().await;
        assert_eq!(active_alerts.len(), 0);

        let history = service.get_alert_history(None).await;
        assert_eq!(history.len(), 1);
        assert_eq!(history[0].status, AlertStatus::Resolved);
    }

    #[test]
    fn test_severity_threshold() {
        assert!(AlertService::severity_meets_threshold(&AlertSeverity::Critical, &AlertSeverity::Warning));
        assert!(AlertService::severity_meets_threshold(&AlertSeverity::Warning, &AlertSeverity::Info));
        assert!(!AlertService::severity_meets_threshold(&AlertSeverity::Info, &AlertSeverity::Warning));
    }
}