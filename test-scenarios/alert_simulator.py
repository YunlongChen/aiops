#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
告警系统模拟器

该模块模拟告警系统的各种功能，包括告警规则、阈值检测、告警通知等。
支持多种告警类型和通知渠道的模拟。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid


class AlertSeverity(Enum):
    """告警严重级别枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(Enum):
    """告警状态枚举"""
    FIRING = "firing"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ACKNOWLEDGED = "acknowledged"


class NotificationChannel(Enum):
    """通知渠道枚举"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    PAGERDUTY = "pagerduty"
    DINGTALK = "dingtalk"


class MetricType(Enum):
    """指标类型枚举"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    DISK_USAGE = "disk_usage"
    NETWORK_USAGE = "network_usage"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"


@dataclass
class AlertRule:
    """告警规则数据类"""
    id: str
    name: str
    description: str
    metric_type: MetricType
    condition: str  # >, <, >=, <=, ==, !=
    threshold: float
    duration_seconds: int  # 持续时间
    severity: AlertSeverity
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    notification_channels: List[NotificationChannel] = field(default_factory=list)
    

@dataclass
class Alert:
    """告警数据类"""
    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    description: str
    source: str  # 告警来源（主机名、服务名等）
    metric_name: str
    metric_value: float
    threshold: float
    condition: str
    fired_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)


@dataclass
class NotificationRecord:
    """通知记录数据类"""
    id: str
    alert_id: str
    channel: NotificationChannel
    recipient: str
    subject: str
    content: str
    sent_at: datetime
    success: bool
    error_message: Optional[str] = None
    retry_count: int = 0


class AlertSimulator:
    """告警系统模拟器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化告警模拟器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._get_default_config()
        self.alert_rules = self._load_alert_rules()
        self.active_alerts = {}  # alert_id -> Alert
        self.alert_history = []  # 历史告警记录
        self.notification_records = []  # 通知记录
        self.running = False
        self.simulation_threads = []
        self.logger = self._setup_logger()
        
        # 模拟数据源
        self.metric_sources = self._generate_metric_sources()
        
        # 通知回调函数
        self.notification_callbacks = {}
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "evaluation": {
                "interval_seconds": 15,
                "max_alerts_per_rule": 10,
                "alert_timeout_hours": 24
            },
            "notification": {
                "retry_attempts": 3,
                "retry_delay_seconds": 60,
                "rate_limit_per_minute": 10,
                "group_wait_seconds": 30,
                "group_interval_seconds": 300,
                "repeat_interval_hours": 4
            },
            "channels": {
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.example.com",
                    "from_address": "alerts@example.com",
                    "recipients": ["admin@example.com", "ops@example.com"]
                },
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/services/...",
                    "channel": "#alerts",
                    "username": "AlertBot"
                },
                "webhook": {
                    "enabled": True,
                    "url": "http://localhost:8080/webhook/alerts",
                    "timeout_seconds": 10
                }
            },
            "simulation": {
                "enable_random_alerts": True,
                "random_alert_probability": 0.1,
                "enable_alert_storms": True,
                "storm_probability": 0.02,
                "auto_resolve_probability": 0.3,
                "auto_resolve_delay_minutes": [5, 30]
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("AlertSimulator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """加载告警规则"""
        rules = [
            # CPU相关告警
            AlertRule(
                id="cpu_high",
                name="High CPU Usage",
                description="CPU usage is above threshold",
                metric_type=MetricType.CPU_USAGE,
                condition=">",
                threshold=80.0,
                duration_seconds=300,
                severity=AlertSeverity.HIGH,
                tags={"team": "infrastructure", "service": "system"},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            AlertRule(
                id="cpu_critical",
                name="Critical CPU Usage",
                description="CPU usage is critically high",
                metric_type=MetricType.CPU_USAGE,
                condition=">",
                threshold=95.0,
                duration_seconds=60,
                severity=AlertSeverity.CRITICAL,
                tags={"team": "infrastructure", "service": "system"},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PAGERDUTY]
            ),
            
            # 内存相关告警
            AlertRule(
                id="memory_high",
                name="High Memory Usage",
                description="Memory usage is above threshold",
                metric_type=MetricType.MEMORY_USAGE,
                condition=">",
                threshold=85.0,
                duration_seconds=300,
                severity=AlertSeverity.MEDIUM,
                tags={"team": "infrastructure", "service": "system"},
                notification_channels=[NotificationChannel.EMAIL]
            ),
            AlertRule(
                id="memory_critical",
                name="Critical Memory Usage",
                description="Memory usage is critically high",
                metric_type=MetricType.MEMORY_USAGE,
                condition=">",
                threshold=95.0,
                duration_seconds=120,
                severity=AlertSeverity.CRITICAL,
                tags={"team": "infrastructure", "service": "system"},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.PAGERDUTY]
            ),
            
            # 磁盘相关告警
            AlertRule(
                id="disk_high",
                name="High Disk Usage",
                description="Disk usage is above threshold",
                metric_type=MetricType.DISK_USAGE,
                condition=">",
                threshold=90.0,
                duration_seconds=600,
                severity=AlertSeverity.HIGH,
                tags={"team": "infrastructure", "service": "storage"},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            
            # 应用相关告警
            AlertRule(
                id="response_time_high",
                name="High Response Time",
                description="Application response time is too high",
                metric_type=MetricType.RESPONSE_TIME,
                condition=">",
                threshold=2000.0,  # 2秒
                duration_seconds=180,
                severity=AlertSeverity.MEDIUM,
                tags={"team": "application", "service": "web"},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK]
            ),
            AlertRule(
                id="error_rate_high",
                name="High Error Rate",
                description="Application error rate is above threshold",
                metric_type=MetricType.ERROR_RATE,
                condition=">",
                threshold=5.0,  # 5%
                duration_seconds=120,
                severity=AlertSeverity.HIGH,
                tags={"team": "application", "service": "web"},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK, NotificationChannel.PAGERDUTY]
            ),
            
            # 可用性告警
            AlertRule(
                id="service_down",
                name="Service Unavailable",
                description="Service is not responding",
                metric_type=MetricType.AVAILABILITY,
                condition="<",
                threshold=1.0,  # 服务不可用
                duration_seconds=60,
                severity=AlertSeverity.CRITICAL,
                tags={"team": "sre", "service": "all"},
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.PAGERDUTY]
            )
        ]
        
        return rules
    
    def _generate_metric_sources(self) -> List[Dict]:
        """生成指标数据源"""
        return [
            {"name": "web-01", "type": "server", "service": "nginx"},
            {"name": "web-02", "type": "server", "service": "nginx"},
            {"name": "db-01", "type": "server", "service": "mysql"},
            {"name": "app-01", "type": "server", "service": "application"},
            {"name": "cache-01", "type": "server", "service": "redis"},
            {"name": "lb-01", "type": "server", "service": "haproxy"},
            {"name": "api-service", "type": "application", "service": "api"},
            {"name": "web-service", "type": "application", "service": "web"},
            {"name": "payment-service", "type": "application", "service": "payment"}
        ]
    
    def start_simulation(self):
        """启动告警模拟"""
        self.running = True
        
        # 启动告警评估线程
        evaluation_thread = threading.Thread(
            target=self._alert_evaluation_loop,
            name="AlertEvaluation"
        )
        evaluation_thread.daemon = True
        evaluation_thread.start()
        self.simulation_threads.append(evaluation_thread)
        
        # 启动通知处理线程
        notification_thread = threading.Thread(
            target=self._notification_loop,
            name="NotificationHandler"
        )
        notification_thread.daemon = True
        notification_thread.start()
        self.simulation_threads.append(notification_thread)
        
        # 启动自动解决线程
        auto_resolve_thread = threading.Thread(
            target=self._auto_resolve_loop,
            name="AutoResolve"
        )
        auto_resolve_thread.daemon = True
        auto_resolve_thread.start()
        self.simulation_threads.append(auto_resolve_thread)
        
        self.logger.info("Alert simulation started")
    
    def stop_simulation(self):
        """停止告警模拟"""
        self.running = False
        
        # 等待所有线程结束
        for thread in self.simulation_threads:
            thread.join(timeout=5)
        
        self.simulation_threads.clear()
        self.logger.info("Alert simulation stopped")
    
    def _alert_evaluation_loop(self):
        """告警评估循环"""
        interval = self.config["evaluation"]["interval_seconds"]
        
        while self.running:
            try:
                # 评估所有启用的告警规则
                for rule in self.alert_rules:
                    if rule.enabled:
                        self._evaluate_rule(rule)
                
                # 模拟随机告警
                if self.config["simulation"]["enable_random_alerts"]:
                    self._generate_random_alerts()
                
                # 模拟告警风暴
                if self.config["simulation"]["enable_alert_storms"]:
                    self._generate_alert_storm()
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in alert evaluation: {e}")
                time.sleep(interval)
    
    def _notification_loop(self):
        """通知处理循环"""
        while self.running:
            try:
                # 处理待发送的通知
                self._process_pending_notifications()
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                self.logger.error(f"Error in notification processing: {e}")
                time.sleep(5)
    
    def _auto_resolve_loop(self):
        """自动解决告警循环"""
        while self.running:
            try:
                # 自动解决一些告警
                if self.config["simulation"]["auto_resolve_probability"] > 0:
                    self._auto_resolve_alerts()
                
                time.sleep(30)  # 每30秒检查一次
                
            except Exception as e:
                self.logger.error(f"Error in auto resolve: {e}")
                time.sleep(30)
    
    def _evaluate_rule(self, rule: AlertRule):
        """评估告警规则"""
        # 模拟获取指标值
        for source in self.metric_sources:
            metric_value = self._simulate_metric_value(rule.metric_type, source)
            
            # 检查是否满足告警条件
            if self._check_condition(metric_value, rule.condition, rule.threshold):
                # 检查是否已经有相同的告警
                alert_key = f"{rule.id}_{source['name']}"
                
                if alert_key not in self.active_alerts:
                    # 创建新告警
                    alert = self._create_alert(rule, source, metric_value)
                    self.active_alerts[alert_key] = alert
                    self.alert_history.append(alert)
                    
                    self.logger.info(f"Alert fired: {alert.rule_name} on {alert.source}")
                    
                    # 发送通知
                    self._schedule_notifications(alert)
                else:
                    # 更新现有告警的指标值
                    existing_alert = self.active_alerts[alert_key]
                    existing_alert.metric_value = metric_value
            else:
                # 检查是否需要解决告警
                alert_key = f"{rule.id}_{source['name']}"
                if alert_key in self.active_alerts:
                    alert = self.active_alerts[alert_key]
                    self._resolve_alert(alert)
    
    def _simulate_metric_value(self, metric_type: MetricType, source: Dict) -> float:
        """模拟指标值"""
        # 根据指标类型和数据源生成模拟值
        base_values = {
            MetricType.CPU_USAGE: 45.0,
            MetricType.MEMORY_USAGE: 60.0,
            MetricType.DISK_USAGE: 70.0,
            MetricType.NETWORK_USAGE: 30.0,
            MetricType.RESPONSE_TIME: 500.0,
            MetricType.ERROR_RATE: 1.0,
            MetricType.THROUGHPUT: 100.0,
            MetricType.AVAILABILITY: 1.0
        }
        
        base_value = base_values.get(metric_type, 50.0)
        
        # 根据服务类型调整基础值
        if source["service"] == "mysql" and metric_type == MetricType.CPU_USAGE:
            base_value *= 1.5  # 数据库CPU使用率通常更高
        elif source["service"] == "redis" and metric_type == MetricType.MEMORY_USAGE:
            base_value *= 1.3  # Redis内存使用率更高
        
        # 添加随机变化
        variation = random.uniform(0.7, 1.4)
        value = base_value * variation
        
        # 模拟异常情况
        if random.random() < 0.1:  # 10%概率出现异常值
            if metric_type in [MetricType.CPU_USAGE, MetricType.MEMORY_USAGE, MetricType.DISK_USAGE]:
                value = random.uniform(85, 98)  # 高使用率
            elif metric_type == MetricType.RESPONSE_TIME:
                value = random.uniform(3000, 10000)  # 高响应时间
            elif metric_type == MetricType.ERROR_RATE:
                value = random.uniform(8, 25)  # 高错误率
            elif metric_type == MetricType.AVAILABILITY:
                value = 0.0  # 服务不可用
        
        return round(value, 2)
    
    def _check_condition(self, value: float, condition: str, threshold: float) -> bool:
        """检查告警条件"""
        if condition == ">":
            return value > threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<":
            return value < threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return abs(value - threshold) < 0.001
        elif condition == "!=":
            return abs(value - threshold) >= 0.001
        else:
            return False
    
    def _create_alert(self, rule: AlertRule, source: Dict, metric_value: float) -> Alert:
        """创建告警"""
        alert_id = str(uuid.uuid4())
        
        # 生成告警消息
        message = f"{rule.name}: {source['name']} {rule.metric_type.value} is {metric_value} (threshold: {rule.threshold})"
        
        # 生成描述
        description = f"{rule.description}. Current value: {metric_value}, Threshold: {rule.threshold}"
        
        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.FIRING,
            message=message,
            description=description,
            source=source["name"],
            metric_name=rule.metric_type.value,
            metric_value=metric_value,
            threshold=rule.threshold,
            condition=rule.condition,
            fired_at=datetime.now(),
            tags=rule.tags.copy(),
            annotations={
                "service": source["service"],
                "type": source["type"],
                "runbook": f"https://runbooks.example.com/{rule.id}",
                "dashboard": f"https://grafana.example.com/d/{source['name']}"
            }
        )
        
        return alert
    
    def _resolve_alert(self, alert: Alert):
        """解决告警"""
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now()
        
        # 从活跃告警中移除
        alert_key = f"{alert.rule_id}_{alert.source}"
        if alert_key in self.active_alerts:
            del self.active_alerts[alert_key]
        
        self.logger.info(f"Alert resolved: {alert.rule_name} on {alert.source}")
        
        # 发送解决通知
        self._schedule_resolution_notifications(alert)
    
    def _schedule_notifications(self, alert: Alert):
        """安排通知发送"""
        rule = next((r for r in self.alert_rules if r.id == alert.rule_id), None)
        if not rule:
            return
        
        for channel in rule.notification_channels:
            self._send_notification(alert, channel, "alert")
    
    def _schedule_resolution_notifications(self, alert: Alert):
        """安排解决通知发送"""
        rule = next((r for r in self.alert_rules if r.id == alert.rule_id), None)
        if not rule:
            return
        
        for channel in rule.notification_channels:
            self._send_notification(alert, channel, "resolution")
    
    def _send_notification(self, alert: Alert, channel: NotificationChannel, notification_type: str):
        """发送通知"""
        notification_id = str(uuid.uuid4())
        
        # 生成通知内容
        if notification_type == "alert":
            subject = f"🚨 {alert.severity.value.upper()}: {alert.rule_name}"
            content = self._generate_alert_content(alert)
        else:  # resolution
            subject = f"✅ RESOLVED: {alert.rule_name}"
            content = self._generate_resolution_content(alert)
        
        # 获取收件人
        recipients = self._get_recipients(channel)
        
        for recipient in recipients:
            # 模拟发送
            success = self._simulate_send(channel, recipient, subject, content)
            
            # 记录通知
            record = NotificationRecord(
                id=notification_id,
                alert_id=alert.id,
                channel=channel,
                recipient=recipient,
                subject=subject,
                content=content,
                sent_at=datetime.now(),
                success=success,
                error_message=None if success else "Simulated delivery failure"
            )
            
            self.notification_records.append(record)
            
            if success:
                self.logger.info(f"Notification sent via {channel.value} to {recipient}")
            else:
                self.logger.warning(f"Notification failed via {channel.value} to {recipient}")
    
    def _generate_alert_content(self, alert: Alert) -> str:
        """生成告警通知内容"""
        content = f"""
🚨 Alert: {alert.rule_name}

Severity: {alert.severity.value.upper()}
Source: {alert.source}
Metric: {alert.metric_name}
Current Value: {alert.metric_value}
Threshold: {alert.condition} {alert.threshold}
Fired At: {alert.fired_at.strftime('%Y-%m-%d %H:%M:%S')}

Description: {alert.description}

Tags: {', '.join([f'{k}={v}' for k, v in alert.tags.items()])}

Runbook: {alert.annotations.get('runbook', 'N/A')}
Dashboard: {alert.annotations.get('dashboard', 'N/A')}
        """.strip()
        
        return content
    
    def _generate_resolution_content(self, alert: Alert) -> str:
        """生成解决通知内容"""
        duration = ""
        if alert.resolved_at and alert.fired_at:
            duration_seconds = (alert.resolved_at - alert.fired_at).total_seconds()
            duration = f"Duration: {int(duration_seconds // 60)}m {int(duration_seconds % 60)}s"
        
        content = f"""
✅ Alert Resolved: {alert.rule_name}

Source: {alert.source}
Metric: {alert.metric_name}
Fired At: {alert.fired_at.strftime('%Y-%m-%d %H:%M:%S')}
Resolved At: {alert.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if alert.resolved_at else 'N/A'}
{duration}

The alert condition is no longer met.
        """.strip()
        
        return content
    
    def _get_recipients(self, channel: NotificationChannel) -> List[str]:
        """获取通知收件人"""
        channel_config = self.config["channels"].get(channel.value, {})
        
        if channel == NotificationChannel.EMAIL:
            return channel_config.get("recipients", ["admin@example.com"])
        elif channel == NotificationChannel.SMS:
            return ["+1234567890", "+0987654321"]
        elif channel == NotificationChannel.SLACK:
            return [channel_config.get("channel", "#alerts")]
        elif channel == NotificationChannel.WEBHOOK:
            return [channel_config.get("url", "http://localhost:8080/webhook")]
        elif channel == NotificationChannel.PAGERDUTY:
            return ["integration-key-123"]
        elif channel == NotificationChannel.DINGTALK:
            return ["dingtalk-webhook-url"]
        else:
            return ["default-recipient"]
    
    def _simulate_send(self, channel: NotificationChannel, recipient: str, subject: str, content: str) -> bool:
        """模拟发送通知"""
        # 模拟发送成功率
        success_rates = {
            NotificationChannel.EMAIL: 0.95,
            NotificationChannel.SMS: 0.90,
            NotificationChannel.SLACK: 0.98,
            NotificationChannel.WEBHOOK: 0.85,
            NotificationChannel.PAGERDUTY: 0.99,
            NotificationChannel.DINGTALK: 0.92
        }
        
        success_rate = success_rates.get(channel, 0.90)
        return random.random() < success_rate
    
    def _process_pending_notifications(self):
        """处理待发送的通知"""
        # 这里可以实现通知重试、限流等逻辑
        # 当前只是模拟，实际实现会更复杂
        pass
    
    def _generate_random_alerts(self):
        """生成随机告警"""
        probability = self.config["simulation"]["random_alert_probability"]
        
        if random.random() < probability:
            # 随机选择一个规则和数据源
            rule = random.choice(self.alert_rules)
            source = random.choice(self.metric_sources)
            
            # 生成满足告警条件的指标值
            if rule.condition == ">":
                metric_value = rule.threshold + random.uniform(1, 20)
            elif rule.condition == "<":
                metric_value = rule.threshold - random.uniform(0.1, 1)
            else:
                metric_value = rule.threshold
            
            # 创建告警
            alert_key = f"{rule.id}_{source['name']}"
            if alert_key not in self.active_alerts:
                alert = self._create_alert(rule, source, metric_value)
                self.active_alerts[alert_key] = alert
                self.alert_history.append(alert)
                
                self.logger.info(f"Random alert generated: {alert.rule_name} on {alert.source}")
                self._schedule_notifications(alert)
    
    def _generate_alert_storm(self):
        """生成告警风暴"""
        probability = self.config["simulation"]["storm_probability"]
        
        if random.random() < probability:
            self.logger.warning("Alert storm detected! Generating multiple alerts...")
            
            # 生成多个告警
            storm_size = random.randint(5, 15)
            for _ in range(storm_size):
                rule = random.choice(self.alert_rules)
                source = random.choice(self.metric_sources)
                
                # 生成告警条件值
                if rule.condition == ">":
                    metric_value = rule.threshold + random.uniform(10, 50)
                else:
                    metric_value = rule.threshold - random.uniform(0.5, 2)
                
                alert_key = f"{rule.id}_{source['name']}_storm_{random.randint(1000, 9999)}"
                alert = self._create_alert(rule, source, metric_value)
                alert.tags["storm"] = "true"
                
                self.active_alerts[alert_key] = alert
                self.alert_history.append(alert)
                self._schedule_notifications(alert)
    
    def _auto_resolve_alerts(self):
        """自动解决一些告警"""
        probability = self.config["simulation"]["auto_resolve_probability"]
        
        # 获取可以自动解决的告警
        resolvable_alerts = []
        for alert in self.active_alerts.values():
            if alert.status == AlertStatus.FIRING:
                # 检查告警持续时间
                duration_minutes = (datetime.now() - alert.fired_at).total_seconds() / 60
                min_duration, max_duration = self.config["simulation"]["auto_resolve_delay_minutes"]
                
                if min_duration <= duration_minutes <= max_duration:
                    resolvable_alerts.append(alert)
        
        # 随机解决一些告警
        for alert in resolvable_alerts:
            if random.random() < probability:
                self._resolve_alert(alert)
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """确认告警"""
        # 在活跃告警中查找
        for alert in self.active_alerts.values():
            if alert.id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                alert.acknowledged_by = acknowledged_by
                
                self.logger.info(f"Alert acknowledged: {alert.rule_name} by {acknowledged_by}")
                return True
        
        return False
    
    def suppress_alert(self, alert_id: str) -> bool:
        """抑制告警"""
        for alert in self.active_alerts.values():
            if alert.id == alert_id:
                alert.status = AlertStatus.SUPPRESSED
                self.logger.info(f"Alert suppressed: {alert.rule_name}")
                return True
        
        return False
    
    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """获取活跃告警"""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda x: x.fired_at, reverse=True)
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [a for a in self.alert_history if a.fired_at >= cutoff_time]
    
    def get_notification_records(self, hours: int = 24) -> List[NotificationRecord]:
        """获取通知记录"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [n for n in self.notification_records if n.sent_at >= cutoff_time]
    
    def export_alerts_to_json(self, filename: str):
        """导出告警到JSON文件"""
        data = {
            "active_alerts": [],
            "alert_history": [],
            "notification_records": [],
            "exported_at": datetime.now().isoformat()
        }
        
        # 转换活跃告警
        for alert in self.active_alerts.values():
            data["active_alerts"].append(self._alert_to_dict(alert))
        
        # 转换历史告警
        for alert in self.alert_history:
            data["alert_history"].append(self._alert_to_dict(alert))
        
        # 转换通知记录
        for record in self.notification_records:
            data["notification_records"].append({
                "id": record.id,
                "alert_id": record.alert_id,
                "channel": record.channel.value,
                "recipient": record.recipient,
                "subject": record.subject,
                "content": record.content,
                "sent_at": record.sent_at.isoformat(),
                "success": record.success,
                "error_message": record.error_message,
                "retry_count": record.retry_count
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Alerts exported to {filename}")
    
    def _alert_to_dict(self, alert: Alert) -> Dict:
        """将告警对象转换为字典"""
        return {
            "id": alert.id,
            "rule_id": alert.rule_id,
            "rule_name": alert.rule_name,
            "severity": alert.severity.value,
            "status": alert.status.value,
            "message": alert.message,
            "description": alert.description,
            "source": alert.source,
            "metric_name": alert.metric_name,
            "metric_value": alert.metric_value,
            "threshold": alert.threshold,
            "condition": alert.condition,
            "fired_at": alert.fired_at.isoformat(),
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "acknowledged_at": alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
            "acknowledged_by": alert.acknowledged_by,
            "tags": alert.tags,
            "annotations": alert.annotations
        }
    
    def generate_alert_report(self) -> Dict[str, Any]:
        """生成告警报告"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        
        # 统计活跃告警
        active_alerts = list(self.active_alerts.values())
        active_by_severity = {}
        for severity in AlertSeverity:
            active_by_severity[severity.value] = len([a for a in active_alerts if a.severity == severity])
        
        # 统计24小时内的告警
        recent_alerts = [a for a in self.alert_history if a.fired_at >= last_24h]
        total_alerts_24h = len(recent_alerts)
        resolved_alerts_24h = len([a for a in recent_alerts if a.status == AlertStatus.RESOLVED])
        
        # 统计通知
        recent_notifications = [n for n in self.notification_records if n.sent_at >= last_24h]
        total_notifications = len(recent_notifications)
        successful_notifications = len([n for n in recent_notifications if n.success])
        
        # 按渠道统计通知
        notifications_by_channel = {}
        for channel in NotificationChannel:
            channel_notifications = [n for n in recent_notifications if n.channel == channel]
            notifications_by_channel[channel.value] = {
                "total": len(channel_notifications),
                "successful": len([n for n in channel_notifications if n.success])
            }
        
        # 最频繁的告警规则
        rule_counts = {}
        for alert in recent_alerts:
            rule_counts[alert.rule_name] = rule_counts.get(alert.rule_name, 0) + 1
        
        top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "summary": {
                "active_alerts": len(active_alerts),
                "alerts_last_24h": total_alerts_24h,
                "resolved_last_24h": resolved_alerts_24h,
                "resolution_rate": resolved_alerts_24h / total_alerts_24h if total_alerts_24h > 0 else 0,
                "notifications_sent": total_notifications,
                "notification_success_rate": successful_notifications / total_notifications if total_notifications > 0 else 0
            },
            "active_alerts_by_severity": active_by_severity,
            "notifications_by_channel": notifications_by_channel,
            "top_alert_rules": dict(top_rules),
            "generated_at": now.isoformat()
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Alert System Simulator")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--duration", type=int, default=300, help="Simulation duration in seconds")
    parser.add_argument("--export", help="Export alerts to JSON file")
    parser.add_argument("--report", help="Generate alert report file")
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    
    # 创建模拟器
    simulator = AlertSimulator(config)
    
    try:
        # 启动模拟
        simulator.start_simulation()
        
        print(f"Alert simulation running for {args.duration} seconds...")
        print("Press Ctrl+C to stop early")
        
        time.sleep(args.duration)
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    finally:
        simulator.stop_simulation()
        
        # 导出数据
        if args.export:
            simulator.export_alerts_to_json(args.export)
        
        # 生成报告
        if args.report:
            report = simulator.generate_alert_report()
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Alert report saved to {args.report}")
        
        # 显示简要统计
        report = simulator.generate_alert_report()
        print("\n=== Alert Simulation Summary ===")
        print(f"Active alerts: {report['summary']['active_alerts']}")
        print(f"Alerts in last 24h: {report['summary']['alerts_last_24h']}")
        print(f"Resolution rate: {report['summary']['resolution_rate']:.2%}")
        print(f"Notifications sent: {report['summary']['notifications_sent']}")
        print(f"Notification success rate: {report['summary']['notification_success_rate']:.2%}")


if __name__ == "__main__":
    main()