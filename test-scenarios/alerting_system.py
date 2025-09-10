#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
告警系统模拟器
模拟各种告警场景，包括告警生成、升级、抑制、恢复等
用于AIOps测试场景
"""

import argparse
import json
import random
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from enum import Enum
from dataclasses import dataclass, asdict

class AlertSeverity(Enum):
    """告警严重程度枚举"""
    INFO = "info"
    WARNING = "warning"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """告警状态枚举"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"

class AlertCategory(Enum):
    """告警分类枚举"""
    INFRASTRUCTURE = "infrastructure"
    APPLICATION = "application"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    CAPACITY = "capacity"

@dataclass
class Alert:
    """告警数据类"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    category: AlertCategory
    source: str
    metric_name: str
    current_value: float
    threshold_value: float
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    escalation_level: int = 0
    suppression_reason: Optional[str] = None
    tags: Dict[str, str] = None
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.context is None:
            self.context = {}

class AlertingSystem:
    """告警系统模拟器"""
    
    def __init__(self, duration: int = 300):
        """
        初始化告警系统
        
        Args:
            duration: 模拟运行时长(秒)
        """
        self.duration = duration
        self.start_time = datetime.now()
        self.alerts = []
        self.active_alerts = {}
        self.alert_history = []
        self.running = False
        
        # 告警规则配置
        self.alert_rules = {
            'cpu_high': {
                'metric': 'cpu_usage',
                'threshold': 80.0,
                'severity': AlertSeverity.WARNING,
                'category': AlertCategory.PERFORMANCE,
                'title': 'CPU使用率过高',
                'description': 'CPU使用率超过阈值',
                'escalation_threshold': 90.0,
                'escalation_severity': AlertSeverity.CRITICAL
            },
            'memory_high': {
                'metric': 'memory_usage',
                'threshold': 85.0,
                'severity': AlertSeverity.WARNING,
                'category': AlertCategory.PERFORMANCE,
                'title': '内存使用率过高',
                'description': '内存使用率超过阈值',
                'escalation_threshold': 95.0,
                'escalation_severity': AlertSeverity.CRITICAL
            },
            'disk_full': {
                'metric': 'disk_usage',
                'threshold': 90.0,
                'severity': AlertSeverity.MAJOR,
                'category': AlertCategory.CAPACITY,
                'title': '磁盘空间不足',
                'description': '磁盘使用率超过阈值',
                'escalation_threshold': 95.0,
                'escalation_severity': AlertSeverity.CRITICAL
            },
            'response_time_high': {
                'metric': 'response_time',
                'threshold': 1000.0,
                'severity': AlertSeverity.WARNING,
                'category': AlertCategory.PERFORMANCE,
                'title': '响应时间过长',
                'description': '应用响应时间超过阈值',
                'escalation_threshold': 3000.0,
                'escalation_severity': AlertSeverity.MAJOR
            },
            'error_rate_high': {
                'metric': 'error_rate',
                'threshold': 5.0,
                'severity': AlertSeverity.MINOR,
                'category': AlertCategory.AVAILABILITY,
                'title': '错误率过高',
                'description': '应用错误率超过阈值',
                'escalation_threshold': 10.0,
                'escalation_severity': AlertSeverity.MAJOR
            },
            'network_errors': {
                'metric': 'network_errors',
                'threshold': 100.0,
                'severity': AlertSeverity.WARNING,
                'category': AlertCategory.INFRASTRUCTURE,
                'title': '网络错误过多',
                'description': '网络错误数量超过阈值',
                'escalation_threshold': 500.0,
                'escalation_severity': AlertSeverity.MAJOR
            },
            'service_down': {
                'metric': 'service_availability',
                'threshold': 0.99,
                'severity': AlertSeverity.CRITICAL,
                'category': AlertCategory.AVAILABILITY,
                'title': '服务不可用',
                'description': '服务可用性低于阈值',
                'escalation_threshold': 0.95,
                'escalation_severity': AlertSeverity.CRITICAL
            }
        }
        
        # 告警抑制规则
        self.suppression_rules = [
            {
                'name': 'maintenance_window',
                'description': '维护窗口期间抑制告警',
                'conditions': {
                    'time_range': [(2, 4), (14, 16)],  # 凌晨2-4点，下午2-4点
                    'categories': [AlertCategory.PERFORMANCE, AlertCategory.AVAILABILITY]
                }
            },
            {
                'name': 'cascade_suppression',
                'description': '级联告警抑制',
                'conditions': {
                    'parent_alert': 'service_down',
                    'suppress_categories': [AlertCategory.PERFORMANCE]
                }
            }
        ]
        
        # 通知渠道配置
        self.notification_channels = {
            'email': {
                'enabled': True,
                'recipients': ['admin@company.com', 'ops@company.com'],
                'severity_filter': [AlertSeverity.MAJOR, AlertSeverity.CRITICAL]
            },
            'sms': {
                'enabled': True,
                'recipients': ['+1234567890', '+0987654321'],
                'severity_filter': [AlertSeverity.CRITICAL]
            },
            'slack': {
                'enabled': True,
                'channel': '#alerts',
                'severity_filter': [AlertSeverity.WARNING, AlertSeverity.MAJOR, AlertSeverity.CRITICAL]
            },
            'webhook': {
                'enabled': True,
                'url': 'https://hooks.company.com/alerts',
                'severity_filter': [AlertSeverity.MAJOR, AlertSeverity.CRITICAL]
            }
        }
    
    def generate_metrics(self) -> Dict[str, float]:
        """
        生成模拟指标数据
        
        Returns:
            指标数据字典
        """
        # 基础指标
        metrics = {
            'cpu_usage': random.uniform(20, 95),
            'memory_usage': random.uniform(30, 98),
            'disk_usage': random.uniform(40, 96),
            'response_time': random.uniform(50, 3500),
            'error_rate': random.uniform(0, 15),
            'network_errors': random.uniform(0, 800),
            'service_availability': random.uniform(0.90, 1.0)
        }
        
        # 添加时间相关的变化
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # 工作时间，负载更高
            metrics['cpu_usage'] *= random.uniform(1.2, 1.5)
            metrics['memory_usage'] *= random.uniform(1.1, 1.3)
            metrics['response_time'] *= random.uniform(1.3, 2.0)
            metrics['error_rate'] *= random.uniform(1.5, 2.5)
        
        # 确保值在合理范围内
        metrics['cpu_usage'] = min(100, metrics['cpu_usage'])
        metrics['memory_usage'] = min(100, metrics['memory_usage'])
        metrics['disk_usage'] = min(100, metrics['disk_usage'])
        metrics['service_availability'] = max(0, min(1, metrics['service_availability']))
        
        return metrics
    
    def check_alert_conditions(self, metrics: Dict[str, float]) -> List[str]:
        """
        检查告警条件
        
        Args:
            metrics: 指标数据
            
        Returns:
            触发的告警规则名称列表
        """
        triggered_rules = []
        
        for rule_name, rule in self.alert_rules.items():
            metric_name = rule['metric']
            threshold = rule['threshold']
            
            if metric_name in metrics:
                current_value = metrics[metric_name]
                
                # 检查是否超过阈值
                if metric_name == 'service_availability':
                    # 可用性指标：低于阈值触发告警
                    if current_value < threshold:
                        triggered_rules.append(rule_name)
                else:
                    # 其他指标：高于阈值触发告警
                    if current_value > threshold:
                        triggered_rules.append(rule_name)
        
        return triggered_rules
    
    def create_alert(self, rule_name: str, metrics: Dict[str, float]) -> Alert:
        """
        创建告警
        
        Args:
            rule_name: 告警规则名称
            metrics: 指标数据
            
        Returns:
            创建的告警对象
        """
        rule = self.alert_rules[rule_name]
        metric_name = rule['metric']
        current_value = metrics[metric_name]
        
        alert = Alert(
            id=str(uuid.uuid4()),
            title=rule['title'],
            description=f"{rule['description']}。当前值: {current_value:.2f}, 阈值: {rule['threshold']:.2f}",
            severity=rule['severity'],
            status=AlertStatus.ACTIVE,
            category=rule['category'],
            source=f"monitoring-system-{random.choice(['prod', 'staging', 'dev'])}",
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=rule['threshold'],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags={
                'environment': random.choice(['production', 'staging', 'development']),
                'service': random.choice(['web-app', 'api-server', 'database', 'cache']),
                'region': random.choice(['us-east-1', 'us-west-2', 'eu-west-1']),
                'team': random.choice(['backend', 'frontend', 'devops', 'sre'])
            },
            context={
                'rule_name': rule_name,
                'detection_time': datetime.now().isoformat(),
                'host': f"server-{random.randint(1, 100)}",
                'instance_id': f"i-{random.randint(100000, 999999)}"
            }
        )
        
        return alert
    
    def should_suppress_alert(self, alert: Alert) -> Tuple[bool, Optional[str]]:
        """
        检查是否应该抑制告警
        
        Args:
            alert: 告警对象
            
        Returns:
            (是否抑制, 抑制原因)
        """
        current_time = datetime.now()
        current_hour = current_time.hour
        
        for rule in self.suppression_rules:
            if rule['name'] == 'maintenance_window':
                conditions = rule['conditions']
                time_ranges = conditions['time_range']
                categories = conditions['categories']
                
                # 检查时间窗口
                in_maintenance_window = any(
                    start <= current_hour < end for start, end in time_ranges
                )
                
                # 检查告警分类
                if in_maintenance_window and alert.category in categories:
                    return True, f"维护窗口期间抑制 ({current_hour}:00)"
            
            elif rule['name'] == 'cascade_suppression':
                conditions = rule['conditions']
                parent_alert = conditions['parent_alert']
                suppress_categories = conditions['suppress_categories']
                
                # 检查是否存在父告警
                has_parent_alert = any(
                    active_alert.context.get('rule_name') == parent_alert
                    for active_alert in self.active_alerts.values()
                )
                
                if has_parent_alert and alert.category in suppress_categories:
                    return True, f"级联抑制 (父告警: {parent_alert})"
        
        return False, None
    
    def process_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        处理告警
        
        Args:
            alert: 告警对象
            
        Returns:
            处理结果字典
        """
        result = {
            'alert_id': alert.id,
            'action': 'created',
            'notifications_sent': [],
            'suppressed': False,
            'escalated': False
        }
        
        # 检查是否应该抑制
        should_suppress, suppression_reason = self.should_suppress_alert(alert)
        if should_suppress:
            alert.status = AlertStatus.SUPPRESSED
            alert.suppression_reason = suppression_reason
            result['suppressed'] = True
            result['suppression_reason'] = suppression_reason
            return result
        
        # 检查是否需要升级
        rule = self.alert_rules[alert.context['rule_name']]
        if 'escalation_threshold' in rule:
            escalation_threshold = rule['escalation_threshold']
            if alert.current_value > escalation_threshold:
                alert.severity = rule['escalation_severity']
                alert.escalation_level = 1
                result['escalated'] = True
        
        # 发送通知
        notifications = self.send_notifications(alert)
        result['notifications_sent'] = notifications
        
        # 模拟自动确认
        if random.random() < 0.3:  # 30%概率自动确认
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = random.choice(['system', 'auto-ack-bot', 'on-call-engineer'])
            result['action'] = 'acknowledged'
        
        return result
    
    def send_notifications(self, alert: Alert) -> List[str]:
        """
        发送告警通知
        
        Args:
            alert: 告警对象
            
        Returns:
            发送的通知渠道列表
        """
        sent_channels = []
        
        for channel_name, config in self.notification_channels.items():
            if not config['enabled']:
                continue
            
            # 检查严重程度过滤
            if alert.severity not in config['severity_filter']:
                continue
            
            # 模拟发送通知
            if random.random() < 0.9:  # 90%成功率
                sent_channels.append(channel_name)
        
        return sent_channels
    
    def resolve_alerts(self, metrics: Dict[str, float]) -> List[str]:
        """
        解决告警
        
        Args:
            metrics: 当前指标数据
            
        Returns:
            已解决的告警ID列表
        """
        resolved_alerts = []
        
        for alert_id, alert in list(self.active_alerts.items()):
            if alert.status == AlertStatus.RESOLVED:
                continue
            
            rule_name = alert.context['rule_name']
            rule = self.alert_rules[rule_name]
            metric_name = rule['metric']
            threshold = rule['threshold']
            
            if metric_name in metrics:
                current_value = metrics[metric_name]
                
                # 检查是否恢复正常
                is_resolved = False
                if metric_name == 'service_availability':
                    # 可用性指标：高于阈值+缓冲区认为恢复
                    if current_value > threshold + 0.01:
                        is_resolved = True
                else:
                    # 其他指标：低于阈值-缓冲区认为恢复
                    buffer = threshold * 0.1  # 10%缓冲区
                    if current_value < threshold - buffer:
                        is_resolved = True
                
                if is_resolved:
                    alert.status = AlertStatus.RESOLVED
                    alert.resolved_at = datetime.now()
                    alert.updated_at = datetime.now()
                    resolved_alerts.append(alert_id)
                    
                    # 从活跃告警中移除
                    del self.active_alerts[alert_id]
        
        return resolved_alerts
    
    def generate_alert_summary(self) -> Dict[str, Any]:
        """
        生成告警摘要
        
        Returns:
            告警摘要字典
        """
        active_count = len(self.active_alerts)
        total_count = len(self.alert_history)
        
        # 按严重程度统计
        severity_stats = {}
        for alert in self.active_alerts.values():
            severity = alert.severity.value
            severity_stats[severity] = severity_stats.get(severity, 0) + 1
        
        # 按分类统计
        category_stats = {}
        for alert in self.active_alerts.values():
            category = alert.category.value
            category_stats[category] = category_stats.get(category, 0) + 1
        
        # 按状态统计
        status_stats = {}
        for alert in self.active_alerts.values():
            status = alert.status.value
            status_stats[status] = status_stats.get(status, 0) + 1
        
        return {
            'active_alerts': active_count,
            'total_alerts': total_count,
            'severity_distribution': severity_stats,
            'category_distribution': category_stats,
            'status_distribution': status_stats,
            'suppressed_alerts': len([a for a in self.active_alerts.values() if a.status == AlertStatus.SUPPRESSED]),
            'escalated_alerts': len([a for a in self.active_alerts.values() if a.escalation_level > 0])
        }
    
    def run_alerting(self, export_file: str = None):
        """
        运行告警系统模拟
        
        Args:
            export_file: 导出文件路径
        """
        print(f"🚨 启动告警系统模拟器")
        print(f"模拟时长: {self.duration}秒")
        print(f"告警规则: {len(self.alert_rules)}个")
        print(f"抑制规则: {len(self.suppression_rules)}个")
        print(f"通知渠道: {len([c for c in self.notification_channels.values() if c['enabled']])}个")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.running = True
        end_time = self.start_time + timedelta(seconds=self.duration)
        
        try:
            while datetime.now() < end_time and self.running:
                # 生成指标数据
                metrics = self.generate_metrics()
                
                # 检查告警条件
                triggered_rules = self.check_alert_conditions(metrics)
                
                # 创建新告警
                new_alerts = []
                for rule_name in triggered_rules:
                    # 检查是否已存在相同的活跃告警
                    existing_alert = None
                    for alert in self.active_alerts.values():
                        if (alert.context.get('rule_name') == rule_name and 
                            alert.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]):
                            existing_alert = alert
                            break
                    
                    if not existing_alert:
                        alert = self.create_alert(rule_name, metrics)
                        result = self.process_alert(alert)
                        
                        self.active_alerts[alert.id] = alert
                        self.alert_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'alert': asdict(alert),
                            'processing_result': result
                        })
                        new_alerts.append(alert)
                
                # 解决告警
                resolved_alert_ids = self.resolve_alerts(metrics)
                
                # 显示实时信息
                summary = self.generate_alert_summary()
                
                status_info = []
                if new_alerts:
                    status_info.append(f"新增: {len(new_alerts)}")
                if resolved_alert_ids:
                    status_info.append(f"解决: {len(resolved_alert_ids)}")
                if summary['active_alerts'] > 0:
                    status_info.append(f"活跃: {summary['active_alerts']}")
                
                status_str = ", ".join(status_info) if status_info else "无变化"
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {status_str}")
                
                # 显示新告警详情
                for alert in new_alerts:
                    action = "抑制" if alert.status == AlertStatus.SUPPRESSED else "创建"
                    print(f"  ↳ {action}告警: {alert.title} ({alert.severity.value})")
                
                # 显示解决的告警
                for alert_id in resolved_alert_ids:
                    print(f"  ↳ 解决告警: {alert_id[:8]}...")
                
                time.sleep(30)  # 每30秒检查一次
                
        except KeyboardInterrupt:
            print("\n告警系统被用户中断")
            self.running = False
        
        final_summary = self.generate_alert_summary()
        
        print(f"\n✅ 告警系统模拟完成")
        print(f"总告警数: {final_summary['total_alerts']}")
        print(f"活跃告警: {final_summary['active_alerts']}")
        print(f"抑制告警: {final_summary['suppressed_alerts']}")
        print(f"升级告警: {final_summary['escalated_alerts']}")
        
        print("\n📊 严重程度分布:")
        for severity, count in final_summary['severity_distribution'].items():
            print(f"  {severity}: {count}")
        
        print("\n📂 分类分布:")
        for category, count in final_summary['category_distribution'].items():
            print(f"  {category}: {count}")
        
        # 导出数据
        if export_file:
            self.export_results(export_file)
    
    def export_results(self, filename: str):
        """
        导出告警结果到JSON文件
        
        Args:
            filename: 导出文件名
        """
        export_data = {
            'simulation_info': {
                'type': 'alerting_system',
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': self.duration,
                'total_alerts': len(self.alert_history)
            },
            'configuration': {
                'alert_rules': {k: {**v, 'severity': v['severity'].value, 'category': v['category'].value} 
                               for k, v in self.alert_rules.items()},
                'suppression_rules': self.suppression_rules,
                'notification_channels': self.notification_channels
            },
            'active_alerts': {
                alert_id: {
                    **asdict(alert),
                    'severity': alert.severity.value,
                    'status': alert.status.value,
                    'category': alert.category.value,
                    'created_at': alert.created_at.isoformat(),
                    'updated_at': alert.updated_at.isoformat(),
                    'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None,
                    'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None
                }
                for alert_id, alert in self.active_alerts.items()
            },
            'alert_history': self.alert_history,
            'summary': self.generate_alert_summary()
        }
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 告警系统数据已导出到: {filename}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='告警系统模拟器')
    parser.add_argument('--duration', type=int, default=300, help='模拟时长(秒)')
    parser.add_argument('--export', type=str, help='导出文件路径')
    
    args = parser.parse_args()
    
    alerting_system = AlertingSystem(duration=args.duration)
    alerting_system.run_alerting(export_file=args.export)

if __name__ == '__main__':
    main()