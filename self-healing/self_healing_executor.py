#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Healing Executor - 自愈执行器核心引擎

功能说明:
- 监听告警事件和系统异常
- 执行自动化修复策略
- 管理Ansible Playbook执行
- 记录自愈操作日志
- 提供自愈状态监控

作者: AIOps Team
创建时间: 2024-01-09
版本: 1.0.0
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

import aiohttp
import yaml
from pydantic import BaseModel, Field


class HealingStatus(Enum):
    """自愈状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class AlertSeverity(Enum):
    """告警严重级别"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class HealingAction(BaseModel):
    """自愈动作模型"""
    id: str = Field(..., description="动作ID")
    name: str = Field(..., description="动作名称")
    playbook: str = Field(..., description="Ansible Playbook路径")
    timeout: int = Field(default=300, description="超时时间(秒)")
    retry_count: int = Field(default=3, description="重试次数")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="执行条件")
    variables: Dict[str, Any] = Field(default_factory=dict, description="变量")


class HealingRule(BaseModel):
    """自愈规则模型"""
    id: str = Field(..., description="规则ID")
    name: str = Field(..., description="规则名称")
    description: str = Field(default="", description="规则描述")
    alert_pattern: str = Field(..., description="告警匹配模式")
    severity: AlertSeverity = Field(..., description="告警级别")
    actions: List[HealingAction] = Field(..., description="修复动作列表")
    cooldown: int = Field(default=300, description="冷却时间(秒)")
    enabled: bool = Field(default=True, description="是否启用")


class HealingRecord(BaseModel):
    """自愈记录模型"""
    id: str = Field(..., description="记录ID")
    rule_id: str = Field(..., description="规则ID")
    alert_data: Dict[str, Any] = Field(..., description="告警数据")
    status: HealingStatus = Field(..., description="执行状态")
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="执行时长(秒)")
    actions_executed: List[str] = Field(default_factory=list, description="已执行动作")
    error_message: Optional[str] = Field(None, description="错误信息")
    logs: List[str] = Field(default_factory=list, description="执行日志")


class SelfHealingExecutor:
    """自愈执行器主类"""
    
    def __init__(self, config_path: str = "config/self-healing.yaml"):
        """
        初始化自愈执行器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.rules: Dict[str, HealingRule] = {}
        self.records: Dict[str, HealingRecord] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.last_execution: Dict[str, datetime] = {}
        
        # 设置日志
        self._setup_logging()
        
        # 加载规则
        self._load_rules()
        
        self.logger.info("自愈执行器初始化完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            # 创建默认配置
            default_config = {
                "executor": {
                    "max_concurrent_tasks": 10,
                    "default_timeout": 300,
                    "log_level": "INFO",
                    "log_file": "/var/log/self-healing/executor.log"
                },
                "ansible": {
                    "playbook_dir": "playbooks",
                    "inventory": "inventory/hosts.yml",
                    "vault_password_file": ".vault_pass"
                },
                "alertmanager": {
                    "webhook_url": "http://localhost:9093/api/v1/alerts",
                    "listen_port": 8080,
                    "listen_host": "0.0.0.0"
                },
                "elasticsearch": {
                    "host": "localhost",
                    "port": 9200,
                    "index": "self-healing-logs"
                }
            }
            
            # 创建配置目录
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入默认配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
            
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_logging(self):
        """设置日志配置"""
        log_config = self.config.get('executor', {})
        log_level = getattr(logging, log_config.get('log_level', 'INFO'))
        log_file = log_config.get('log_file', '/var/log/self-healing/executor.log')
        
        # 创建日志目录
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # 设置日志器
        self.logger = logging.getLogger('SelfHealingExecutor')
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _load_rules(self):
        """加载自愈规则"""
        rules_dir = Path("rules")
        if not rules_dir.exists():
            rules_dir.mkdir(parents=True, exist_ok=True)
            self.logger.warning(f"规则目录不存在，已创建: {rules_dir}")
            return
        
        for rule_file in rules_dir.glob("*.yaml"):
            try:
                with open(rule_file, 'r', encoding='utf-8') as f:
                    rule_data = yaml.safe_load(f)
                
                rule = HealingRule(**rule_data)
                self.rules[rule.id] = rule
                self.logger.info(f"加载规则: {rule.name} ({rule.id})")
                
            except Exception as e:
                self.logger.error(f"加载规则文件失败 {rule_file}: {e}")
        
        self.logger.info(f"共加载 {len(self.rules)} 个自愈规则")
    
    async def process_alert(self, alert_data: Dict[str, Any]) -> Optional[str]:
        """
        处理告警事件
        
        Args:
            alert_data: 告警数据
            
        Returns:
            处理记录ID，如果没有匹配的规则则返回None
        """
        self.logger.info(f"收到告警: {alert_data.get('alertname', 'Unknown')}")
        
        # 查找匹配的规则
        matched_rule = self._find_matching_rule(alert_data)
        if not matched_rule:
            self.logger.warning(f"未找到匹配的自愈规则: {alert_data}")
            return None
        
        # 检查冷却时间
        if not self._check_cooldown(matched_rule.id):
            self.logger.info(f"规则 {matched_rule.name} 在冷却期内，跳过执行")
            return None
        
        # 创建执行记录
        record_id = f"{matched_rule.id}_{int(time.time())}"
        record = HealingRecord(
            id=record_id,
            rule_id=matched_rule.id,
            alert_data=alert_data,
            status=HealingStatus.PENDING,
            start_time=datetime.now()
        )
        
        self.records[record_id] = record
        
        # 异步执行自愈动作
        task = asyncio.create_task(self._execute_healing_actions(record, matched_rule))
        self.running_tasks[record_id] = task
        
        return record_id
    
    def _find_matching_rule(self, alert_data: Dict[str, Any]) -> Optional[HealingRule]:
        """查找匹配的自愈规则"""
        alert_name = alert_data.get('alertname', '')
        alert_labels = alert_data.get('labels', {})
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            # 简单的模式匹配（可以扩展为正则表达式）
            if rule.alert_pattern in alert_name:
                # 检查严重级别
                alert_severity = alert_labels.get('severity', 'info')
                if alert_severity == rule.severity.value:
                    return rule
        
        return None
    
    def _check_cooldown(self, rule_id: str) -> bool:
        """检查规则冷却时间"""
        if rule_id not in self.last_execution:
            return True
        
        rule = self.rules[rule_id]
        last_time = self.last_execution[rule_id]
        cooldown_seconds = rule.cooldown
        
        elapsed = (datetime.now() - last_time).total_seconds()
        return elapsed >= cooldown_seconds
    
    async def _execute_healing_actions(self, record: HealingRecord, rule: HealingRule):
        """执行自愈动作"""
        try:
            record.status = HealingStatus.RUNNING
            self.logger.info(f"开始执行自愈动作: {rule.name}")
            
            for action in rule.actions:
                try:
                    # 执行Ansible Playbook
                    success = await self._execute_ansible_playbook(action, record)
                    
                    if success:
                        record.actions_executed.append(action.id)
                        record.logs.append(f"动作 {action.name} 执行成功")
                        self.logger.info(f"动作执行成功: {action.name}")
                    else:
                        record.logs.append(f"动作 {action.name} 执行失败")
                        self.logger.error(f"动作执行失败: {action.name}")
                        
                        # 如果关键动作失败，停止后续执行
                        if action.retry_count <= 0:
                            break
                            
                except Exception as e:
                    error_msg = f"执行动作 {action.name} 时发生异常: {e}"
                    record.logs.append(error_msg)
                    self.logger.error(error_msg)
            
            # 更新执行状态
            if len(record.actions_executed) == len(rule.actions):
                record.status = HealingStatus.SUCCESS
                self.logger.info(f"自愈执行成功: {rule.name}")
            else:
                record.status = HealingStatus.FAILED
                self.logger.error(f"自愈执行失败: {rule.name}")
            
        except Exception as e:
            record.status = HealingStatus.FAILED
            record.error_message = str(e)
            self.logger.error(f"自愈执行异常: {e}")
        
        finally:
            # 更新记录
            record.end_time = datetime.now()
            record.duration = (record.end_time - record.start_time).total_seconds()
            
            # 更新最后执行时间
            self.last_execution[rule.id] = record.start_time
            
            # 清理任务
            if record.id in self.running_tasks:
                del self.running_tasks[record.id]
            
            # 发送执行结果到Elasticsearch
            await self._send_to_elasticsearch(record)
    
    async def _execute_ansible_playbook(self, action: HealingAction, record: HealingRecord) -> bool:
        """执行Ansible Playbook"""
        try:
            ansible_config = self.config.get('ansible', {})
            playbook_dir = Path(ansible_config.get('playbook_dir', 'playbooks'))
            playbook_path = playbook_dir / action.playbook
            
            if not playbook_path.exists():
                error_msg = f"Playbook文件不存在: {playbook_path}"
                record.logs.append(error_msg)
                self.logger.error(error_msg)
                return False
            
            # 构建ansible-playbook命令
            cmd = [
                'ansible-playbook',
                str(playbook_path),
                '-i', ansible_config.get('inventory', 'inventory/hosts.yml')
            ]
            
            # 添加变量
            if action.variables:
                for key, value in action.variables.items():
                    cmd.extend(['-e', f'{key}={value}'])
            
            # 添加vault密码文件
            vault_file = ansible_config.get('vault_password_file')
            if vault_file and Path(vault_file).exists():
                cmd.extend(['--vault-password-file', vault_file])
            
            self.logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(playbook_dir.parent)
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=action.timeout
                )
                
                # 记录输出
                if stdout:
                    record.logs.append(f"STDOUT: {stdout.decode('utf-8')}")
                if stderr:
                    record.logs.append(f"STDERR: {stderr.decode('utf-8')}")
                
                return process.returncode == 0
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                record.logs.append(f"Playbook执行超时: {action.timeout}秒")
                return False
                
        except Exception as e:
            error_msg = f"执行Playbook异常: {e}"
            record.logs.append(error_msg)
            self.logger.error(error_msg)
            return False
    
    async def _send_to_elasticsearch(self, record: HealingRecord):
        """发送执行记录到Elasticsearch"""
        try:
            es_config = self.config.get('elasticsearch', {})
            if not es_config:
                return
            
            url = f"http://{es_config['host']}:{es_config['port']}/{es_config['index']}/_doc"
            
            # 转换记录为字典
            doc = record.dict()
            doc['@timestamp'] = record.start_time.isoformat()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=doc) as response:
                    if response.status == 201:
                        self.logger.debug(f"记录已发送到Elasticsearch: {record.id}")
                    else:
                        self.logger.warning(f"发送到Elasticsearch失败: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"发送到Elasticsearch异常: {e}")
    
    async def start_webhook_server(self):
        """启动Webhook服务器接收告警"""
        from aiohttp import web
        
        async def webhook_handler(request):
            """处理Webhook请求"""
            try:
                data = await request.json()
                alerts = data.get('alerts', [])
                
                results = []
                for alert in alerts:
                    record_id = await self.process_alert(alert)
                    if record_id:
                        results.append(record_id)
                
                return web.json_response({
                    'status': 'success',
                    'processed': len(results),
                    'records': results
                })
                
            except Exception as e:
                self.logger.error(f"处理Webhook请求异常: {e}")
                return web.json_response(
                    {'status': 'error', 'message': str(e)},
                    status=500
                )
        
        async def health_handler(request):
            """健康检查"""
            return web.json_response({
                'status': 'healthy',
                'rules_loaded': len(self.rules),
                'running_tasks': len(self.running_tasks),
                'total_records': len(self.records)
            })
        
        # 创建应用
        app = web.Application()
        app.router.add_post('/webhook', webhook_handler)
        app.router.add_get('/health', health_handler)
        
        # 启动服务器
        alertmanager_config = self.config.get('alertmanager', {})
        host = alertmanager_config.get('listen_host', '0.0.0.0')
        port = alertmanager_config.get('listen_port', 8080)
        
        self.logger.info(f"启动Webhook服务器: http://{host}:{port}")
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
    
    def get_status(self) -> Dict[str, Any]:
        """获取执行器状态"""
        return {
            'rules_loaded': len(self.rules),
            'running_tasks': len(self.running_tasks),
            'total_records': len(self.records),
            'success_rate': self._calculate_success_rate(),
            'last_execution_times': {
                rule_id: time.isoformat() 
                for rule_id, time in self.last_execution.items()
            }
        }
    
    def _calculate_success_rate(self) -> float:
        """计算成功率"""
        if not self.records:
            return 0.0
        
        success_count = sum(
            1 for record in self.records.values() 
            if record.status == HealingStatus.SUCCESS
        )
        
        return success_count / len(self.records) * 100


async def main():
    """主函数"""
    executor = SelfHealingExecutor()
    
    # 启动Webhook服务器
    await executor.start_webhook_server()
    
    # 保持运行
    try:
        while True:
            await asyncio.sleep(60)
            executor.logger.info(f"执行器状态: {executor.get_status()}")
    except KeyboardInterrupt:
        executor.logger.info("收到停止信号，正在关闭...")
    finally:
        # 等待所有任务完成
        if executor.running_tasks:
            executor.logger.info(f"等待 {len(executor.running_tasks)} 个任务完成...")
            await asyncio.gather(*executor.running_tasks.values(), return_exceptions=True)


if __name__ == '__main__':
    asyncio.run(main())