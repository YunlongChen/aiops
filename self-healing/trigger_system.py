#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
触发器系统模块
用于监听各种告警源并触发相应的自愈动作

主要功能:
- 监听Alertmanager Webhook
- 监听Prometheus告警
- 监听ELK告警
- 监听系统指标
- 触发自愈执行器
- 管理告警状态
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

import aiohttp
import yaml
from aiohttp import web, ClientSession
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus指标
alert_received_total = Counter('trigger_alerts_received_total', 'Total alerts received', ['source', 'severity'])
alert_processed_total = Counter('trigger_alerts_processed_total', 'Total alerts processed', ['source', 'action', 'status'])
alert_processing_duration = Histogram('trigger_alert_processing_duration_seconds', 'Alert processing duration')
active_alerts_gauge = Gauge('trigger_active_alerts', 'Number of active alerts', ['severity'])
trigger_system_health = Gauge('trigger_system_health', 'Trigger system health status')

class AlertSeverity(Enum):
    """告警严重程度枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AlertStatus(Enum):
    """告警状态枚举"""
    FIRING = "firing"
    RESOLVED = "resolved"
    PENDING = "pending"
    SUPPRESSED = "suppressed"

class TriggerAction(Enum):
    """触发动作类型枚举"""
    RESTART_SERVICE = "restart_service"
    CLEAR_CACHE = "clear_cache"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    CLEANUP_DISK = "cleanup_disk"
    KILL_PROCESS = "kill_process"
    NOTIFY_ADMIN = "notify_admin"
    CUSTOM_SCRIPT = "custom_script"

@dataclass
class Alert:
    """告警数据模型"""
    id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    message: str
    labels: Dict[str, str]
    annotations: Dict[str, str]
    starts_at: datetime
    ends_at: Optional[datetime] = None
    fingerprint: Optional[str] = None
    generator_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['severity'] = self.severity.value
        data['status'] = self.status.value
        data['starts_at'] = self.starts_at.isoformat()
        if self.ends_at:
            data['ends_at'] = self.ends_at.isoformat()
        return data
    
    @classmethod
    def from_alertmanager(cls, alert_data: Dict[str, Any]) -> 'Alert':
        """从Alertmanager数据创建Alert对象"""
        return cls(
            id=alert_data.get('fingerprint', ''),
            name=alert_data.get('labels', {}).get('alertname', 'Unknown'),
            severity=AlertSeverity(alert_data.get('labels', {}).get('severity', 'medium')),
            status=AlertStatus(alert_data.get('status', 'firing')),
            source='alertmanager',
            message=alert_data.get('annotations', {}).get('summary', ''),
            labels=alert_data.get('labels', {}),
            annotations=alert_data.get('annotations', {}),
            starts_at=datetime.fromisoformat(alert_data.get('startsAt', '').replace('Z', '+00:00')),
            ends_at=datetime.fromisoformat(alert_data.get('endsAt', '').replace('Z', '+00:00')) if alert_data.get('endsAt') else None,
            fingerprint=alert_data.get('fingerprint'),
            generator_url=alert_data.get('generatorURL')
        )
    
    @classmethod
    def from_prometheus(cls, alert_data: Dict[str, Any]) -> 'Alert':
        """从Prometheus数据创建Alert对象"""
        return cls(
            id=alert_data.get('fingerprint', ''),
            name=alert_data.get('metric', {}).get('__name__', 'Unknown'),
            severity=AlertSeverity(alert_data.get('labels', {}).get('severity', 'medium')),
            status=AlertStatus.FIRING,
            source='prometheus',
            message=f"Metric {alert_data.get('metric', {}).get('__name__')} value: {alert_data.get('value', [None, 'N/A'])[1]}",
            labels=alert_data.get('labels', {}),
            annotations={},
            starts_at=datetime.now(),
            fingerprint=alert_data.get('fingerprint')
        )

@dataclass
class TriggerRule:
    """触发规则数据模型"""
    id: str
    name: str
    pattern: str
    severity_threshold: AlertSeverity
    action: TriggerAction
    cooldown_seconds: int
    enabled: bool
    conditions: Dict[str, Any]
    parameters: Dict[str, Any]
    max_executions: int = 5
    execution_count: int = 0
    last_execution: Optional[datetime] = None
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        if not self.enabled:
            return False
        
        if self.execution_count >= self.max_executions:
            return False
        
        if self.last_execution:
            cooldown_end = self.last_execution + timedelta(seconds=self.cooldown_seconds)
            if datetime.now() < cooldown_end:
                return False
        
        return True
    
    def matches_alert(self, alert: Alert) -> bool:
        """检查告警是否匹配规则"""
        # 检查严重程度
        severity_levels = {
            AlertSeverity.INFO: 0,
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4
        }
        
        if severity_levels[alert.severity] < severity_levels[self.severity_threshold]:
            return False
        
        # 检查模式匹配
        import re
        if not re.search(self.pattern, alert.name, re.IGNORECASE):
            return False
        
        # 检查条件
        for key, expected_value in self.conditions.items():
            if key in alert.labels:
                if alert.labels[key] != expected_value:
                    return False
            elif key in alert.annotations:
                if alert.annotations[key] != expected_value:
                    return False
        
        return True

class AlertStore:
    """告警存储管理器"""
    
    def __init__(self, max_alerts: int = 10000):
        self.alerts: Dict[str, Alert] = {}
        self.max_alerts = max_alerts
        self._lock = asyncio.Lock()
    
    async def add_alert(self, alert: Alert) -> None:
        """添加告警"""
        async with self._lock:
            self.alerts[alert.id] = alert
            
            # 清理过期告警
            if len(self.alerts) > self.max_alerts:
                # 删除最旧的告警
                oldest_alerts = sorted(
                    self.alerts.items(),
                    key=lambda x: x[1].starts_at
                )[:len(self.alerts) - self.max_alerts + 100]
                
                for alert_id, _ in oldest_alerts:
                    del self.alerts[alert_id]
    
    async def get_alert(self, alert_id: str) -> Optional[Alert]:
        """获取告警"""
        async with self._lock:
            return self.alerts.get(alert_id)
    
    async def get_active_alerts(self) -> List[Alert]:
        """获取活跃告警"""
        async with self._lock:
            return [
                alert for alert in self.alerts.values()
                if alert.status == AlertStatus.FIRING
            ]
    
    async def resolve_alert(self, alert_id: str) -> None:
        """解决告警"""
        async with self._lock:
            if alert_id in self.alerts:
                self.alerts[alert_id].status = AlertStatus.RESOLVED
                self.alerts[alert_id].ends_at = datetime.now()
    
    async def get_alerts_by_severity(self, severity: AlertSeverity) -> List[Alert]:
        """按严重程度获取告警"""
        async with self._lock:
            return [
                alert for alert in self.alerts.values()
                if alert.severity == severity and alert.status == AlertStatus.FIRING
            ]

class TriggerSystem:
    """触发器系统主类"""
    
    def __init__(self, config_path: str = "config/trigger-system.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.alert_store = AlertStore(max_alerts=self.config.get('max_alerts', 10000))
        self.rules: Dict[str, TriggerRule] = {}
        self.webhooks: Dict[str, Callable] = {}
        self.running = False
        self.app = web.Application()
        self.session: Optional[ClientSession] = None
        
        # 设置路由
        self._setup_routes()
        
        # 加载规则
        self._load_rules()
        
        logger.info(f"触发器系统初始化完成，加载了 {len(self.rules)} 个规则")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning(f"配置文件 {self.config_path} 不存在，使用默认配置")
            return {
                'server': {
                    'host': '0.0.0.0',
                    'port': 8080
                },
                'alertmanager': {
                    'webhook_path': '/webhook/alertmanager'
                },
                'prometheus': {
                    'url': 'http://localhost:9090',
                    'query_interval': 30
                },
                'elasticsearch': {
                    'url': 'http://localhost:9200',
                    'index_pattern': 'alerts-*'
                },
                'self_healing': {
                    'executor_url': 'http://localhost:8081'
                }
            }
    
    def _load_rules(self) -> None:
        """加载触发规则"""
        rules_dir = Path("rules")
        if not rules_dir.exists():
            logger.warning("规则目录不存在")
            return
        
        for rule_file in rules_dir.glob("*.yaml"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rules_data = yaml.safe_load(f)
                
                for rule_data in rules_data.get('rules', []):
                    rule = TriggerRule(
                        id=rule_data['id'],
                        name=rule_data['name'],
                        pattern=rule_data['pattern'],
                        severity_threshold=AlertSeverity(rule_data['severity_threshold']),
                        action=TriggerAction(rule_data['action']),
                        cooldown_seconds=rule_data.get('cooldown_seconds', 300),
                        enabled=rule_data.get('enabled', True),
                        conditions=rule_data.get('conditions', {}),
                        parameters=rule_data.get('parameters', {}),
                        max_executions=rule_data.get('max_executions', 5)
                    )
                    self.rules[rule.id] = rule
                    logger.info(f"加载规则: {rule.name}")
            
            except Exception as e:
                logger.error(f"加载规则文件 {rule_file} 失败: {e}")
    
    def _setup_routes(self) -> None:
        """设置Web路由"""
        self.app.router.add_post('/webhook/alertmanager', self._handle_alertmanager_webhook)
        self.app.router.add_post('/webhook/prometheus', self._handle_prometheus_webhook)
        self.app.router.add_post('/webhook/elasticsearch', self._handle_elasticsearch_webhook)
        self.app.router.add_get('/health', self._handle_health_check)
        self.app.router.add_get('/alerts', self._handle_get_alerts)
        self.app.router.add_get('/rules', self._handle_get_rules)
        self.app.router.add_post('/rules/{rule_id}/enable', self._handle_enable_rule)
        self.app.router.add_post('/rules/{rule_id}/disable', self._handle_disable_rule)
    
    async def _handle_alertmanager_webhook(self, request: web.Request) -> web.Response:
        """处理Alertmanager Webhook"""
        try:
            data = await request.json()
            alerts_data = data.get('alerts', [])
            
            for alert_data in alerts_data:
                alert = Alert.from_alertmanager(alert_data)
                await self._process_alert(alert)
                
                # 更新指标
                alert_received_total.labels(
                    source='alertmanager',
                    severity=alert.severity.value
                ).inc()
            
            return web.json_response({'status': 'success', 'processed': len(alerts_data)})
        
        except Exception as e:
            logger.error(f"处理Alertmanager webhook失败: {e}")
            return web.json_response({'status': 'error', 'message': str(e)}, status=500)
    
    async def _handle_prometheus_webhook(self, request: web.Request) -> web.Response:
        """处理Prometheus Webhook"""
        try:
            data = await request.json()
            
            # 处理Prometheus查询结果
            if 'data' in data and 'result' in data['data']:
                for result in data['data']['result']:
                    alert = Alert.from_prometheus(result)
                    await self._process_alert(alert)
                    
                    alert_received_total.labels(
                        source='prometheus',
                        severity=alert.severity.value
                    ).inc()
            
            return web.json_response({'status': 'success'})
        
        except Exception as e:
            logger.error(f"处理Prometheus webhook失败: {e}")
            return web.json_response({'status': 'error', 'message': str(e)}, status=500)
    
    async def _handle_elasticsearch_webhook(self, request: web.Request) -> web.Response:
        """处理Elasticsearch Webhook"""
        try:
            data = await request.json()
            
            # 处理Elasticsearch告警
            alert = Alert(
                id=data.get('_id', ''),
                name=data.get('_source', {}).get('rule_name', 'Elasticsearch Alert'),
                severity=AlertSeverity(data.get('_source', {}).get('severity', 'medium')),
                status=AlertStatus.FIRING,
                source='elasticsearch',
                message=data.get('_source', {}).get('message', ''),
                labels=data.get('_source', {}).get('labels', {}),
                annotations=data.get('_source', {}).get('annotations', {}),
                starts_at=datetime.now()
            )
            
            await self._process_alert(alert)
            
            alert_received_total.labels(
                source='elasticsearch',
                severity=alert.severity.value
            ).inc()
            
            return web.json_response({'status': 'success'})
        
        except Exception as e:
            logger.error(f"处理Elasticsearch webhook失败: {e}")
            return web.json_response({'status': 'error', 'message': str(e)}, status=500)
    
    async def _handle_health_check(self, request: web.Request) -> web.Response:
        """健康检查"""
        active_alerts = await self.alert_store.get_active_alerts()
        
        health_data = {
            'status': 'healthy' if self.running else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'active_alerts': len(active_alerts),
            'total_rules': len(self.rules),
            'enabled_rules': len([r for r in self.rules.values() if r.enabled])
        }
        
        # 更新健康指标
        trigger_system_health.set(1 if self.running else 0)
        
        return web.json_response(health_data)
    
    async def _handle_get_alerts(self, request: web.Request) -> web.Response:
        """获取告警列表"""
        try:
            severity = request.query.get('severity')
            status = request.query.get('status')
            limit = int(request.query.get('limit', 100))
            
            alerts = await self.alert_store.get_active_alerts()
            
            # 过滤
            if severity:
                alerts = [a for a in alerts if a.severity.value == severity]
            if status:
                alerts = [a for a in alerts if a.status.value == status]
            
            # 限制数量
            alerts = alerts[:limit]
            
            return web.json_response({
                'alerts': [alert.to_dict() for alert in alerts],
                'total': len(alerts)
            })
        
        except Exception as e:
            logger.error(f"获取告警列表失败: {e}")
            return web.json_response({'status': 'error', 'message': str(e)}, status=500)
    
    async def _handle_get_rules(self, request: web.Request) -> web.Response:
        """获取规则列表"""
        try:
            rules_data = []
            for rule in self.rules.values():
                rule_dict = asdict(rule)
                rule_dict['severity_threshold'] = rule.severity_threshold.value
                rule_dict['action'] = rule.action.value
                if rule.last_execution:
                    rule_dict['last_execution'] = rule.last_execution.isoformat()
                rules_data.append(rule_dict)
            
            return web.json_response({
                'rules': rules_data,
                'total': len(rules_data)
            })
        
        except Exception as e:
            logger.error(f"获取规则列表失败: {e}")
            return web.json_response({'status': 'error', 'message': str(e)}, status=500)
    
    async def _handle_enable_rule(self, request: web.Request) -> web.Response:
        """启用规则"""
        rule_id = request.match_info['rule_id']
        
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            logger.info(f"规则 {rule_id} 已启用")
            return web.json_response({'status': 'success', 'message': f'Rule {rule_id} enabled'})
        else:
            return web.json_response({'status': 'error', 'message': 'Rule not found'}, status=404)
    
    async def _handle_disable_rule(self, request: web.Request) -> web.Response:
        """禁用规则"""
        rule_id = request.match_info['rule_id']
        
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            logger.info(f"规则 {rule_id} 已禁用")
            return web.json_response({'status': 'success', 'message': f'Rule {rule_id} disabled'})
        else:
            return web.json_response({'status': 'error', 'message': 'Rule not found'}, status=404)
    
    async def _process_alert(self, alert: Alert) -> None:
        """处理告警"""
        start_time = time.time()
        
        try:
            # 存储告警
            await self.alert_store.add_alert(alert)
            
            logger.info(f"处理告警: {alert.name} (严重程度: {alert.severity.value})")
            
            # 匹配规则并执行动作
            matched_rules = []
            for rule in self.rules.values():
                if rule.matches_alert(alert) and rule.can_execute():
                    matched_rules.append(rule)
            
            if matched_rules:
                logger.info(f"告警 {alert.name} 匹配到 {len(matched_rules)} 个规则")
                
                for rule in matched_rules:
                    try:
                        await self._execute_action(rule, alert)
                        
                        # 更新规则执行状态
                        rule.execution_count += 1
                        rule.last_execution = datetime.now()
                        
                        alert_processed_total.labels(
                            source=alert.source,
                            action=rule.action.value,
                            status='success'
                        ).inc()
                        
                        logger.info(f"规则 {rule.name} 执行成功")
                    
                    except Exception as e:
                        logger.error(f"规则 {rule.name} 执行失败: {e}")
                        alert_processed_total.labels(
                            source=alert.source,
                            action=rule.action.value,
                            status='failed'
                        ).inc()
            else:
                logger.debug(f"告警 {alert.name} 未匹配到任何规则")
            
            # 更新活跃告警指标
            for severity in AlertSeverity:
                count = len(await self.alert_store.get_alerts_by_severity(severity))
                active_alerts_gauge.labels(severity=severity.value).set(count)
        
        except Exception as e:
            logger.error(f"处理告警失败: {e}")
        
        finally:
            # 记录处理时间
            processing_time = time.time() - start_time
            alert_processing_duration.observe(processing_time)
    
    async def _execute_action(self, rule: TriggerRule, alert: Alert) -> None:
        """执行触发动作"""
        executor_url = self.config.get('self_healing', {}).get('executor_url', 'http://localhost:8081')
        
        # 构建执行请求
        action_data = {
            'rule_id': rule.id,
            'rule_name': rule.name,
            'action': rule.action.value,
            'alert': alert.to_dict(),
            'parameters': rule.parameters,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if not self.session:
                self.session = ClientSession()
            
            async with self.session.post(
                f"{executor_url}/execute",
                json=action_data,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"动作执行成功: {result}")
                else:
                    error_text = await response.text()
                    logger.error(f"动作执行失败: HTTP {response.status} - {error_text}")
                    raise Exception(f"HTTP {response.status}: {error_text}")
        
        except Exception as e:
            logger.error(f"执行动作失败: {e}")
            raise
    
    async def start_prometheus_monitoring(self) -> None:
        """启动Prometheus监控"""
        prometheus_config = self.config.get('prometheus', {})
        if not prometheus_config.get('url'):
            logger.warning("未配置Prometheus URL，跳过监控")
            return
        
        query_interval = prometheus_config.get('query_interval', 30)
        
        while self.running:
            try:
                # 这里可以添加主动查询Prometheus的逻辑
                # 例如查询特定指标并生成告警
                await asyncio.sleep(query_interval)
            
            except Exception as e:
                logger.error(f"Prometheus监控错误: {e}")
                await asyncio.sleep(query_interval)
    
    async def start_elasticsearch_monitoring(self) -> None:
        """启动Elasticsearch监控"""
        es_config = self.config.get('elasticsearch', {})
        if not es_config.get('url'):
            logger.warning("未配置Elasticsearch URL，跳过监控")
            return
        
        # 这里可以添加监控Elasticsearch告警索引的逻辑
        logger.info("Elasticsearch监控已启动")
    
    async def start(self) -> None:
        """启动触发器系统"""
        self.running = True
        
        # 启动Prometheus指标服务器（如果启用）
        metrics_config = self.config.get('metrics', {})
        if metrics_config.get('enabled', True):
            metrics_port = metrics_config.get('port', 9090)
            start_http_server(metrics_port)
            logger.info(f"Prometheus指标服务器启动在端口 {metrics_port}")
        else:
            logger.info("Prometheus指标服务器已禁用")
        
        # 启动监控任务
        asyncio.create_task(self.start_prometheus_monitoring())
        asyncio.create_task(self.start_elasticsearch_monitoring())
        
        # 启动Web服务器（如果启用）
        server_config = self.config.get('server', {})
        if server_config.get('enabled', True):
            host = server_config.get('host', '0.0.0.0')
            port = server_config.get('port', 8080)
            
            runner = web.AppRunner(self.app)
            await runner.setup()
            
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            logger.info(f"触发器系统Web服务器启动在 {host}:{port}")
        else:
            logger.info("触发器系统Web服务器已禁用")
        
        # 保持运行
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭...")
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """停止触发器系统"""
        self.running = False
        
        if self.session:
            await self.session.close()
        
        logger.info("触发器系统已停止")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='自愈触发器系统')
    parser.add_argument('--config', '-c', default='config/trigger-system.yaml',
                       help='配置文件路径')
    parser.add_argument('--log-level', default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    
    args = parser.parse_args()
    
    # 设置日志级别
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # 创建并启动触发器系统
    trigger_system = TriggerSystem(args.config)
    
    try:
        asyncio.run(trigger_system.start())
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        raise

if __name__ == '__main__':
    main()