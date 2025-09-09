#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自愈策略执行引擎
Self-Healing Strategy Execution Engine

该模块实现自愈策略的执行引擎，负责:
1. 策略规则的加载和解析
2. 策略条件的评估和匹配
3. 自愈动作的执行和监控
4. 执行结果的记录和通知

作者: AIOps Team
版本: 1.0.0
创建时间: 2024-01-10
"""

import asyncio
import logging
import time
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 第三方库
import aiohttp
import redis
from prometheus_client import Counter, Histogram, Gauge

# 本地导入
from .executor import AnsibleExecutor, ScriptExecutor, ContainerExecutor
from .notification import NotificationManager
from .metrics import MetricsCollector
from ..utils.logger import get_logger
from ..utils.config import ConfigManager
from ..utils.exceptions import (
    StrategyExecutionError,
    RuleEvaluationError,
    ConfigurationError
)

# 配置日志
logger = get_logger(__name__)

# Prometheus指标
strategy_executions = Counter('self_healing_strategy_executions_total', 
                             'Total strategy executions', ['strategy', 'status'])
strategy_duration = Histogram('self_healing_strategy_duration_seconds',
                             'Strategy execution duration')
active_strategies = Gauge('self_healing_active_strategies',
                         'Number of currently active strategies')
rule_evaluations = Counter('self_healing_rule_evaluations_total',
                          'Total rule evaluations', ['rule', 'result'])

class StrategyStatus(Enum):
    """策略执行状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class ActionType(Enum):
    """动作类型枚举"""
    ANSIBLE_PLAYBOOK = "ansible_playbook"
    SCRIPT = "script"
    CONTAINER_ACTION = "container_action"
    API_CALL = "api_call"
    NOTIFICATION = "notification"
    CUSTOM = "custom"

@dataclass
class StrategyAction:
    """策略动作数据类"""
    type: ActionType
    priority: int
    params: Dict[str, Any]
    timeout: int = 300
    retry_attempts: int = 1
    retry_delay: int = 10
    condition: Optional[str] = None
    
@dataclass
class StrategyRule:
    """策略规则数据类"""
    id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[StrategyAction]
    cooldown: int = 300
    max_executions: int = 3
    enabled: bool = True
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    
@dataclass
class ExecutionContext:
    """执行上下文数据类"""
    rule_id: str
    trigger_data: Dict[str, Any]
    start_time: datetime
    execution_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class ExecutionResult:
    """执行结果数据类"""
    execution_id: str
    rule_id: str
    status: StrategyStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    actions_executed: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class RuleEvaluator:
    """规则评估器"""
    
    def __init__(self):
        """初始化规则评估器"""
        self.logger = get_logger(f"{__name__}.RuleEvaluator")
        
    def evaluate_conditions(self, conditions: Dict[str, Any], 
                          trigger_data: Dict[str, Any]) -> bool:
        """
        评估规则条件
        
        Args:
            conditions: 规则条件
            trigger_data: 触发数据
            
        Returns:
            bool: 条件是否满足
        """
        try:
            return self._evaluate_condition_group(conditions, trigger_data)
        except Exception as e:
            self.logger.error(f"条件评估失败: {e}")
            rule_evaluations.labels(rule='unknown', result='error').inc()
            raise RuleEvaluationError(f"条件评估失败: {e}")
    
    def _evaluate_condition_group(self, conditions: Dict[str, Any], 
                                 data: Dict[str, Any]) -> bool:
        """
        评估条件组
        
        Args:
            conditions: 条件组
            data: 数据
            
        Returns:
            bool: 条件组是否满足
        """
        if 'and' in conditions:
            return all(self._evaluate_condition_group(cond, data) 
                      for cond in conditions['and'])
        
        if 'or' in conditions:
            return any(self._evaluate_condition_group(cond, data) 
                      for cond in conditions['or'])
        
        if 'not' in conditions:
            return not self._evaluate_condition_group(conditions['not'], data)
        
        # 单个条件评估
        return self._evaluate_single_condition(conditions, data)
    
    def _evaluate_single_condition(self, condition: Dict[str, Any], 
                                  data: Dict[str, Any]) -> bool:
        """
        评估单个条件
        
        Args:
            condition: 单个条件
            data: 数据
            
        Returns:
            bool: 条件是否满足
        """
        field = condition.get('field')
        operator = condition.get('operator')
        value = condition.get('value')
        
        if not all([field, operator, value is not None]):
            return False
        
        # 获取字段值
        field_value = self._get_field_value(data, field)
        if field_value is None:
            return False
        
        # 执行比较操作
        return self._compare_values(field_value, operator, value)
    
    def _get_field_value(self, data: Dict[str, Any], field: str) -> Any:
        """
        获取字段值（支持嵌套字段）
        
        Args:
            data: 数据字典
            field: 字段路径（如 'system.cpu.usage'）
            
        Returns:
            Any: 字段值
        """
        try:
            keys = field.split('.')
            value = data
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            return value
        except Exception:
            return None
    
    def _compare_values(self, field_value: Any, operator: str, 
                       expected_value: Any) -> bool:
        """
        比较值
        
        Args:
            field_value: 字段值
            operator: 比较操作符
            expected_value: 期望值
            
        Returns:
            bool: 比较结果
        """
        try:
            if operator == 'eq':
                return field_value == expected_value
            elif operator == 'ne':
                return field_value != expected_value
            elif operator == 'gt':
                return float(field_value) > float(expected_value)
            elif operator == 'gte':
                return float(field_value) >= float(expected_value)
            elif operator == 'lt':
                return float(field_value) < float(expected_value)
            elif operator == 'lte':
                return float(field_value) <= float(expected_value)
            elif operator == 'in':
                return field_value in expected_value
            elif operator == 'not_in':
                return field_value not in expected_value
            elif operator == 'contains':
                return str(expected_value) in str(field_value)
            elif operator == 'regex':
                import re
                return bool(re.search(expected_value, str(field_value)))
            else:
                self.logger.warning(f"未知的比较操作符: {operator}")
                return False
        except Exception as e:
            self.logger.error(f"值比较失败: {e}")
            return False

class ActionExecutor:
    """动作执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化动作执行器"""
        self.config = config
        self.logger = get_logger(f"{__name__}.ActionExecutor")
        
        # 初始化各种执行器
        self.ansible_executor = AnsibleExecutor(config.get('ansible', {}))
        self.script_executor = ScriptExecutor(config.get('scripts', {}))
        self.container_executor = ContainerExecutor(config.get('containers', {}))
        
        # HTTP客户端
        self.http_session = None
        
    async def execute_action(self, action: StrategyAction, 
                           context: ExecutionContext) -> Dict[str, Any]:
        """
        执行单个动作
        
        Args:
            action: 策略动作
            context: 执行上下文
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        start_time = time.time()
        result = {
            'action_type': action.type.value,
            'priority': action.priority,
            'start_time': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        try:
            # 检查动作条件
            if action.condition and not self._check_action_condition(
                action.condition, context):
                result['status'] = 'skipped'
                result['message'] = '动作条件不满足'
                return result
            
            # 执行动作（带重试）
            for attempt in range(action.retry_attempts):
                try:
                    if action.type == ActionType.ANSIBLE_PLAYBOOK:
                        exec_result = await self._execute_ansible_action(
                            action, context)
                    elif action.type == ActionType.SCRIPT:
                        exec_result = await self._execute_script_action(
                            action, context)
                    elif action.type == ActionType.CONTAINER_ACTION:
                        exec_result = await self._execute_container_action(
                            action, context)
                    elif action.type == ActionType.API_CALL:
                        exec_result = await self._execute_api_action(
                            action, context)
                    elif action.type == ActionType.NOTIFICATION:
                        exec_result = await self._execute_notification_action(
                            action, context)
                    else:
                        exec_result = await self._execute_custom_action(
                            action, context)
                    
                    result.update(exec_result)
                    result['status'] = 'success'
                    break
                    
                except Exception as e:
                    if attempt < action.retry_attempts - 1:
                        self.logger.warning(
                            f"动作执行失败，第{attempt + 1}次重试: {e}")
                        await asyncio.sleep(action.retry_delay)
                    else:
                        raise e
                        
        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            self.logger.error(f"动作执行失败: {e}")
        
        finally:
            result['duration'] = time.time() - start_time
            result['end_time'] = datetime.now().isoformat()
            
        return result
    
    def _check_action_condition(self, condition: str, 
                               context: ExecutionContext) -> bool:
        """
        检查动作条件
        
        Args:
            condition: 条件表达式
            context: 执行上下文
            
        Returns:
            bool: 条件是否满足
        """
        try:
            # 简单的条件检查实现
            # 可以扩展为更复杂的表达式解析
            return True  # 暂时返回True
        except Exception as e:
            self.logger.error(f"动作条件检查失败: {e}")
            return False
    
    async def _execute_ansible_action(self, action: StrategyAction, 
                                     context: ExecutionContext) -> Dict[str, Any]:
        """执行Ansible动作"""
        playbook = action.params.get('playbook')
        inventory = action.params.get('inventory')
        extra_vars = action.params.get('extra_vars', {})
        
        # 添加上下文变量
        extra_vars.update({
            'execution_id': context.execution_id,
            'rule_id': context.rule_id,
            'trigger_data': context.trigger_data
        })
        
        result = await self.ansible_executor.execute_playbook(
            playbook, inventory, extra_vars, timeout=action.timeout)
        
        return {
            'playbook': playbook,
            'return_code': result.get('return_code'),
            'stdout': result.get('stdout'),
            'stderr': result.get('stderr')
        }
    
    async def _execute_script_action(self, action: StrategyAction, 
                                   context: ExecutionContext) -> Dict[str, Any]:
        """执行脚本动作"""
        script_path = action.params.get('script_path')
        script_content = action.params.get('script_content')
        args = action.params.get('args', [])
        env_vars = action.params.get('env_vars', {})
        
        # 添加上下文环境变量
        env_vars.update({
            'EXECUTION_ID': context.execution_id,
            'RULE_ID': context.rule_id,
            'TRIGGER_DATA': json.dumps(context.trigger_data)
        })
        
        if script_path:
            result = await self.script_executor.execute_script_file(
                script_path, args, env_vars, timeout=action.timeout)
        else:
            result = await self.script_executor.execute_script_content(
                script_content, args, env_vars, timeout=action.timeout)
        
        return {
            'script': script_path or 'inline',
            'return_code': result.get('return_code'),
            'stdout': result.get('stdout'),
            'stderr': result.get('stderr')
        }
    
    async def _execute_container_action(self, action: StrategyAction, 
                                      context: ExecutionContext) -> Dict[str, Any]:
        """执行容器动作"""
        action_type = action.params.get('action')
        container_name = action.params.get('container_name')
        image = action.params.get('image')
        
        if action_type == 'restart':
            result = await self.container_executor.restart_container(
                container_name, timeout=action.timeout)
        elif action_type == 'stop':
            result = await self.container_executor.stop_container(
                container_name, timeout=action.timeout)
        elif action_type == 'start':
            result = await self.container_executor.start_container(
                container_name, timeout=action.timeout)
        elif action_type == 'recreate':
            result = await self.container_executor.recreate_container(
                container_name, image, action.params.get('config', {}),
                timeout=action.timeout)
        else:
            raise ValueError(f"未知的容器动作: {action_type}")
        
        return {
            'container_action': action_type,
            'container_name': container_name,
            'result': result
        }
    
    async def _execute_api_action(self, action: StrategyAction, 
                                context: ExecutionContext) -> Dict[str, Any]:
        """执行API调用动作"""
        if not self.http_session:
            self.http_session = aiohttp.ClientSession()
        
        url = action.params.get('url')
        method = action.params.get('method', 'GET')
        headers = action.params.get('headers', {})
        data = action.params.get('data', {})
        
        # 添加上下文数据
        if method.upper() in ['POST', 'PUT', 'PATCH']:
            data.update({
                'execution_id': context.execution_id,
                'rule_id': context.rule_id,
                'trigger_data': context.trigger_data
            })
        
        async with self.http_session.request(
            method, url, headers=headers, json=data,
            timeout=aiohttp.ClientTimeout(total=action.timeout)
        ) as response:
            response_data = await response.text()
            
            return {
                'api_url': url,
                'method': method,
                'status_code': response.status,
                'response': response_data
            }
    
    async def _execute_notification_action(self, action: StrategyAction, 
                                         context: ExecutionContext) -> Dict[str, Any]:
        """执行通知动作"""
        # 这里应该集成通知管理器
        message = action.params.get('message', '自愈动作执行通知')
        channels = action.params.get('channels', ['email'])
        
        # 构建通知内容
        notification_data = {
            'title': f'自愈系统通知 - {context.rule_id}',
            'message': message,
            'execution_id': context.execution_id,
            'rule_id': context.rule_id,
            'trigger_data': context.trigger_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # 发送通知（这里需要实现具体的通知逻辑）
        return {
            'notification_sent': True,
            'channels': channels,
            'message': message
        }
    
    async def _execute_custom_action(self, action: StrategyAction, 
                                   context: ExecutionContext) -> Dict[str, Any]:
        """执行自定义动作"""
        # 自定义动作的实现
        custom_type = action.params.get('custom_type')
        
        return {
            'custom_action': custom_type,
            'executed': True,
            'message': '自定义动作执行完成'
        }
    
    async def cleanup(self):
        """清理资源"""
        if self.http_session:
            await self.http_session.close()

class StrategyEngine:
    """策略执行引擎主类"""
    
    def __init__(self, config_path: str = None):
        """初始化策略引擎"""
        self.logger = get_logger(f"{__name__}.StrategyEngine")
        
        # 加载配置
        self.config_manager = ConfigManager()
        if config_path:
            self.config = self.config_manager.load_config(config_path)
        else:
            self.config = self.config_manager.get_config()
        
        # 初始化组件
        self.rule_evaluator = RuleEvaluator()
        self.action_executor = ActionExecutor(
            self.config.get('executor', {}))
        self.notification_manager = NotificationManager(
            self.config.get('notifications', {}))
        self.metrics_collector = MetricsCollector()
        
        # 状态管理
        self.rules: Dict[str, StrategyRule] = {}
        self.execution_history: Dict[str, ExecutionResult] = {}
        self.active_executions: Dict[str, ExecutionContext] = {}
        self.cooldown_tracker: Dict[str, datetime] = {}
        self.execution_counter: Dict[str, int] = {}
        
        # 线程池
        self.executor_pool = ThreadPoolExecutor(
            max_workers=self.config.get('global', {}).get(
                'performance', {}).get('max_concurrent_healings', 5))
        
        # Redis连接（用于分布式状态管理）
        self.redis_client = None
        if self.config.get('storage', {}).get('state', {}).get('type') == 'redis':
            redis_config = self.config['storage']['state']['redis']
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                decode_responses=True
            )
        
        # 加载规则
        self._load_rules()
        
        # 启动后台任务
        self._start_background_tasks()
    
    def _load_rules(self):
        """加载策略规则"""
        try:
            rules_config = self.config.get('healing_strategies', {})
            
            # 从配置中解析规则
            for category, strategies in rules_config.items():
                for strategy_name, strategy_config in strategies.items():
                    rule_id = f"{category}.{strategy_name}"
                    
                    # 构建策略动作
                    actions = []
                    for action_config in strategy_config.get('actions', []):
                        action = StrategyAction(
                            type=ActionType(action_config.get('type', 'script')),
                            priority=action_config.get('priority', 1),
                            params=action_config.get('params', {}),
                            timeout=action_config.get('timeout', 300),
                            retry_attempts=action_config.get('retry_attempts', 1),
                            retry_delay=action_config.get('retry_delay', 10),
                            condition=action_config.get('condition')
                        )
                        actions.append(action)
                    
                    # 构建策略规则
                    rule = StrategyRule(
                        id=rule_id,
                        name=strategy_config.get('name', strategy_name),
                        description=strategy_config.get('description', ''),
                        conditions=strategy_config.get('conditions', {}),
                        actions=actions,
                        cooldown=strategy_config.get('cooldown', 300),
                        max_executions=strategy_config.get('max_executions', 3),
                        enabled=strategy_config.get('enabled', True),
                        priority=strategy_config.get('priority', 'medium'),
                        tags=strategy_config.get('tags', [])
                    )
                    
                    self.rules[rule_id] = rule
            
            self.logger.info(f"加载了 {len(self.rules)} 个策略规则")
            
        except Exception as e:
            self.logger.error(f"规则加载失败: {e}")
            raise ConfigurationError(f"规则加载失败: {e}")
    
    def _start_background_tasks(self):
        """启动后台任务"""
        # 启动规则重新加载任务
        if self.config.get('rule_engine', {}).get('storage', {}).get('auto_reload'):
            reload_interval = self.config['rule_engine']['storage'].get(
                'reload_interval', 60)
            threading.Timer(reload_interval, self._reload_rules_periodically).start()
        
        # 启动清理任务
        threading.Timer(300, self._cleanup_expired_data).start()
    
    def _reload_rules_periodically(self):
        """定期重新加载规则"""
        try:
            self._load_rules()
            self.logger.info("规则重新加载完成")
        except Exception as e:
            self.logger.error(f"规则重新加载失败: {e}")
        finally:
            # 设置下次重新加载
            reload_interval = self.config.get('rule_engine', {}).get(
                'storage', {}).get('reload_interval', 60)
            threading.Timer(reload_interval, self._reload_rules_periodically).start()
    
    def _cleanup_expired_data(self):
        """清理过期数据"""
        try:
            current_time = datetime.now()
            
            # 清理执行历史
            expired_executions = []
            for exec_id, result in self.execution_history.items():
                if (current_time - result.start_time).total_seconds() > 86400:  # 24小时
                    expired_executions.append(exec_id)
            
            for exec_id in expired_executions:
                del self.execution_history[exec_id]
            
            # 清理冷却时间跟踪
            expired_cooldowns = []
            for rule_id, cooldown_time in self.cooldown_tracker.items():
                if current_time > cooldown_time:
                    expired_cooldowns.append(rule_id)
            
            for rule_id in expired_cooldowns:
                del self.cooldown_tracker[rule_id]
            
            self.logger.debug(f"清理了 {len(expired_executions)} 个过期执行记录")
            
        except Exception as e:
            self.logger.error(f"数据清理失败: {e}")
        finally:
            # 设置下次清理
            threading.Timer(300, self._cleanup_expired_data).start()
    
    async def evaluate_and_execute(self, trigger_data: Dict[str, Any]) -> List[ExecutionResult]:
        """
        评估触发数据并执行匹配的策略
        
        Args:
            trigger_data: 触发数据
            
        Returns:
            List[ExecutionResult]: 执行结果列表
        """
        results = []
        
        try:
            # 获取匹配的规则
            matching_rules = self._find_matching_rules(trigger_data)
            
            if not matching_rules:
                self.logger.debug("没有找到匹配的规则")
                return results
            
            # 按优先级排序
            matching_rules.sort(key=lambda r: self._get_priority_value(r.priority))
            
            # 并发执行策略
            tasks = []
            for rule in matching_rules:
                if self._can_execute_rule(rule):
                    task = self._execute_strategy(rule, trigger_data)
                    tasks.append(task)
            
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # 处理异常结果
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        self.logger.error(f"策略执行异常: {result}")
                        results[i] = ExecutionResult(
                            execution_id=f"error_{int(time.time())}",
                            rule_id="unknown",
                            status=StrategyStatus.FAILED,
                            start_time=datetime.now(),
                            error_message=str(result)
                        )
            
        except Exception as e:
            self.logger.error(f"策略评估和执行失败: {e}")
            raise StrategyExecutionError(f"策略评估和执行失败: {e}")
        
        return results
    
    def _find_matching_rules(self, trigger_data: Dict[str, Any]) -> List[StrategyRule]:
        """
        查找匹配的规则
        
        Args:
            trigger_data: 触发数据
            
        Returns:
            List[StrategyRule]: 匹配的规则列表
        """
        matching_rules = []
        
        for rule in self.rules.values():
            if not rule.enabled:
                continue
            
            try:
                if self.rule_evaluator.evaluate_conditions(
                    rule.conditions, trigger_data):
                    matching_rules.append(rule)
                    rule_evaluations.labels(
                        rule=rule.id, result='match').inc()
                else:
                    rule_evaluations.labels(
                        rule=rule.id, result='no_match').inc()
            except Exception as e:
                self.logger.error(f"规则 {rule.id} 评估失败: {e}")
                rule_evaluations.labels(
                    rule=rule.id, result='error').inc()
        
        return matching_rules
    
    def _can_execute_rule(self, rule: StrategyRule) -> bool:
        """
        检查规则是否可以执行
        
        Args:
            rule: 策略规则
            
        Returns:
            bool: 是否可以执行
        """
        current_time = datetime.now()
        
        # 检查冷却时间
        if rule.id in self.cooldown_tracker:
            if current_time < self.cooldown_tracker[rule.id]:
                self.logger.debug(f"规则 {rule.id} 仍在冷却期")
                return False
        
        # 检查执行次数限制
        execution_count = self.execution_counter.get(rule.id, 0)
        if execution_count >= rule.max_executions:
            self.logger.debug(f"规则 {rule.id} 已达到最大执行次数")
            return False
        
        return True
    
    async def _execute_strategy(self, rule: StrategyRule, 
                              trigger_data: Dict[str, Any]) -> ExecutionResult:
        """
        执行策略
        
        Args:
            rule: 策略规则
            trigger_data: 触发数据
            
        Returns:
            ExecutionResult: 执行结果
        """
        execution_id = f"{rule.id}_{int(time.time() * 1000)}"
        start_time = datetime.now()
        
        # 创建执行上下文
        context = ExecutionContext(
            rule_id=rule.id,
            trigger_data=trigger_data,
            start_time=start_time,
            execution_id=execution_id
        )
        
        # 记录活跃执行
        self.active_executions[execution_id] = context
        active_strategies.inc()
        
        # 创建执行结果
        result = ExecutionResult(
            execution_id=execution_id,
            rule_id=rule.id,
            status=StrategyStatus.RUNNING,
            start_time=start_time
        )
        
        try:
            with strategy_duration.time():
                # 按优先级排序动作
                sorted_actions = sorted(rule.actions, key=lambda a: a.priority)
                
                # 执行动作
                for action in sorted_actions:
                    action_result = await self.action_executor.execute_action(
                        action, context)
                    result.actions_executed.append(action_result)
                    
                    # 如果动作失败且是关键动作，停止执行
                    if (action_result['status'] == 'failed' and 
                        action.priority == 1):
                        result.status = StrategyStatus.FAILED
                        result.error_message = action_result.get('error')
                        break
                
                # 如果所有动作都成功，标记为成功
                if result.status == StrategyStatus.RUNNING:
                    result.status = StrategyStatus.SUCCESS
            
            strategy_executions.labels(
                strategy=rule.id, status=result.status.value).inc()
            
        except Exception as e:
            result.status = StrategyStatus.FAILED
            result.error_message = str(e)
            self.logger.error(f"策略 {rule.id} 执行失败: {e}")
            strategy_executions.labels(
                strategy=rule.id, status='failed').inc()
        
        finally:
            # 更新执行结果
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            
            # 清理活跃执行
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            active_strategies.dec()
            
            # 记录执行历史
            self.execution_history[execution_id] = result
            
            # 更新冷却时间和执行计数
            self.cooldown_tracker[rule.id] = (
                datetime.now() + timedelta(seconds=rule.cooldown))
            self.execution_counter[rule.id] = (
                self.execution_counter.get(rule.id, 0) + 1)
            
            # 发送通知
            await self._send_execution_notification(result, rule)
        
        return result
    
    async def _send_execution_notification(self, result: ExecutionResult, 
                                         rule: StrategyRule):
        """
        发送执行通知
        
        Args:
            result: 执行结果
            rule: 策略规则
        """
        try:
            notification_config = self.config.get('notifications', {})
            if not notification_config.get('rules', {}).get(
                result.status.value, {}).get('enabled', False):
                return
            
            # 构建通知内容
            notification_data = {
                'title': f'自愈策略执行通知 - {rule.name}',
                'rule_id': rule.id,
                'rule_name': rule.name,
                'execution_id': result.execution_id,
                'status': result.status.value,
                'duration': result.duration,
                'start_time': result.start_time.isoformat(),
                'end_time': result.end_time.isoformat() if result.end_time else None,
                'actions_count': len(result.actions_executed),
                'error_message': result.error_message
            }
            
            # 发送通知
            await self.notification_manager.send_notification(
                notification_data, result.status.value)
            
        except Exception as e:
            self.logger.error(f"发送执行通知失败: {e}")
    
    def _get_priority_value(self, priority: str) -> int:
        """
        获取优先级数值
        
        Args:
            priority: 优先级字符串
            
        Returns:
            int: 优先级数值（越小优先级越高）
        """
        priority_map = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return priority_map.get(priority, 3)
    
    def get_execution_status(self, execution_id: str) -> Optional[ExecutionResult]:
        """
        获取执行状态
        
        Args:
            execution_id: 执行ID
            
        Returns:
            Optional[ExecutionResult]: 执行结果
        """
        return self.execution_history.get(execution_id)
    
    def get_active_executions(self) -> Dict[str, ExecutionContext]:
        """
        获取活跃执行
        
        Returns:
            Dict[str, ExecutionContext]: 活跃执行字典
        """
        return self.active_executions.copy()
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """
        获取规则统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        stats = {
            'total_rules': len(self.rules),
            'enabled_rules': sum(1 for r in self.rules.values() if r.enabled),
            'disabled_rules': sum(1 for r in self.rules.values() if not r.enabled),
            'active_executions': len(self.active_executions),
            'total_executions': len(self.execution_history),
            'execution_counter': self.execution_counter.copy(),
            'cooldown_tracker': {
                rule_id: cooldown_time.isoformat()
                for rule_id, cooldown_time in self.cooldown_tracker.items()
            }
        }
        
        # 按状态统计执行结果
        status_counts = {}
        for result in self.execution_history.values():
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        stats['execution_status_counts'] = status_counts
        
        return stats
    
    async def shutdown(self):
        """
        关闭策略引擎
        """
        self.logger.info("正在关闭策略引擎...")
        
        try:
            # 等待活跃执行完成
            if self.active_executions:
                self.logger.info(f"等待 {len(self.active_executions)} 个活跃执行完成...")
                # 这里可以实现更优雅的关闭逻辑
                await asyncio.sleep(5)
            
            # 关闭执行器
            await self.action_executor.cleanup()
            
            # 关闭线程池
            self.executor_pool.shutdown(wait=True)
            
            # 关闭Redis连接
            if self.redis_client:
                self.redis_client.close()
            
            self.logger.info("策略引擎已关闭")
            
        except Exception as e:
            self.logger.error(f"策略引擎关闭失败: {e}")

# 工厂函数
def create_strategy_engine(config_path: str = None) -> StrategyEngine:
    """
    创建策略引擎实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        StrategyEngine: 策略引擎实例
    """
    return StrategyEngine(config_path)

if __name__ == "__main__":
    # 测试代码
    async def test_strategy_engine():
        """测试策略引擎"""
        engine = create_strategy_engine()
        
        # 模拟触发数据
        trigger_data = {
            'system': {
                'cpu': {'usage': 90.5},
                'memory': {'usage': 85.2},
                'disk': {'usage': 95.0}
            },
            'service': {
                'name': 'web-server',
                'status': 'down',
                'response_time': 5000
            },
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 执行策略
            results = await engine.evaluate_and_execute(trigger_data)
            
            print(f"执行了 {len(results)} 个策略")
            for result in results:
                print(f"策略 {result.rule_id}: {result.status.value}")
                if result.error_message:
                    print(f"  错误: {result.error_message}")
                print(f"  执行时间: {result.duration:.2f}秒")
                print(f"  动作数量: {len(result.actions_executed)}")
            
            # 获取统计信息
            stats = engine.get_rule_statistics()
            print(f"\n统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
            
        finally:
            await engine.shutdown()
    
    # 运行测试
    asyncio.run(test_strategy_engine())