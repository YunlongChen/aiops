#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则引擎
Rule Engine

该模块实现规则引擎的核心功能，负责:
1. 规则的加载、解析和验证
2. 规则条件的匹配和评估
3. 规则优先级和依赖关系管理
4. 规则执行状态跟踪
5. 动态规则更新和热重载

作者: AIOps Team
版本: 1.0.0
创建时间: 2024-01-10
"""

import asyncio
import logging
import time
import yaml
import json
import re
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from collections import defaultdict, deque
import hashlib
import copy

# 第三方库
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from prometheus_client import Counter, Histogram, Gauge

# 本地导入
from ..utils.logger import get_logger
from ..utils.config import ConfigManager
from ..utils.exceptions import (
    RuleEngineError,
    RuleValidationError,
    RuleEvaluationError,
    RuleNotFoundError
)

# 配置日志
logger = get_logger(__name__)

# Prometheus指标
rule_evaluations_total = Counter('rule_engine_evaluations_total', 
                                'Total rule evaluations', ['rule_id', 'result'])
rule_evaluation_duration = Histogram('rule_engine_evaluation_duration_seconds',
                                   'Rule evaluation duration')
active_rules_gauge = Gauge('rule_engine_active_rules', 'Number of active rules')
rule_reloads_total = Counter('rule_engine_reloads_total', 
                           'Total rule reloads', ['status'])

class RuleType(Enum):
    """规则类型枚举"""
    TRIGGER = "trigger"
    CONDITION = "condition"
    ACTION = "action"
    COMPOSITE = "composite"

class RuleStatus(Enum):
    """规则状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISABLED = "disabled"
    ERROR = "error"

class MatchResult(Enum):
    """匹配结果枚举"""
    MATCH = "match"
    NO_MATCH = "no_match"
    ERROR = "error"
    SKIP = "skip"

@dataclass
class RuleCondition:
    """规则条件数据类"""
    field: str
    operator: str
    value: Any
    type: str = "simple"  # simple, regex, function
    case_sensitive: bool = True
    negate: bool = False
    
@dataclass
class RuleAction:
    """规则动作数据类"""
    type: str
    params: Dict[str, Any]
    priority: int = 1
    timeout: int = 300
    retry_count: int = 1
    condition: Optional[str] = None
    
@dataclass
class Rule:
    """规则数据类"""
    id: str
    name: str
    description: str
    type: RuleType
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    priority: int = 1
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 执行控制
    cooldown: int = 0  # 冷却时间（秒）
    max_executions: int = 0  # 最大执行次数（0表示无限制）
    execution_window: int = 3600  # 执行窗口（秒）
    
    # 依赖关系
    depends_on: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    
    # 时间限制
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    schedule: Optional[str] = None  # Cron表达式
    
    # 内部状态
    status: RuleStatus = RuleStatus.ACTIVE
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    last_match_time: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    
@dataclass
class EvaluationContext:
    """评估上下文数据类"""
    data: Dict[str, Any]
    timestamp: datetime
    rule_id: Optional[str] = None
    execution_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class EvaluationResult:
    """评估结果数据类"""
    rule_id: str
    result: MatchResult
    matched_conditions: List[str] = field(default_factory=list)
    evaluation_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConditionEvaluator:
    """条件评估器"""
    
    def __init__(self):
        """初始化条件评估器"""
        self.logger = get_logger(f"{__name__}.ConditionEvaluator")
        self.custom_functions: Dict[str, Callable] = {}
        self._register_builtin_functions()
    
    def _register_builtin_functions(self):
        """注册内置函数"""
        self.custom_functions.update({
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'abs': abs,
            'min': min,
            'max': max,
            'sum': sum,
            'avg': lambda x: sum(x) / len(x) if x else 0,
            'contains': lambda x, y: y in x,
            'startswith': lambda x, y: str(x).startswith(str(y)),
            'endswith': lambda x, y: str(x).endswith(str(y)),
            'regex_match': lambda pattern, text: bool(re.search(pattern, str(text))),
            'time_diff': lambda t1, t2: abs((t1 - t2).total_seconds()),
            'is_weekend': lambda dt: dt.weekday() >= 5,
            'hour_of_day': lambda dt: dt.hour,
            'day_of_week': lambda dt: dt.weekday(),
        })
    
    def register_function(self, name: str, func: Callable):
        """
        注册自定义函数
        
        Args:
            name: 函数名
            func: 函数对象
        """
        self.custom_functions[name] = func
        self.logger.debug(f"注册自定义函数: {name}")
    
    def evaluate_condition(self, condition: RuleCondition, 
                          context: EvaluationContext) -> bool:
        """
        评估单个条件
        
        Args:
            condition: 规则条件
            context: 评估上下文
            
        Returns:
            bool: 条件是否满足
        """
        try:
            # 获取字段值
            field_value = self._get_field_value(context.data, condition.field)
            
            # 执行条件评估
            if condition.type == "simple":
                result = self._evaluate_simple_condition(
                    field_value, condition.operator, condition.value, 
                    condition.case_sensitive)
            elif condition.type == "regex":
                result = self._evaluate_regex_condition(
                    field_value, condition.value, condition.case_sensitive)
            elif condition.type == "function":
                result = self._evaluate_function_condition(
                    field_value, condition.value, context)
            else:
                raise ValueError(f"未知的条件类型: {condition.type}")
            
            # 处理否定
            if condition.negate:
                result = not result
            
            return result
            
        except Exception as e:
            self.logger.error(f"条件评估失败: {e}")
            raise RuleEvaluationError(f"条件评估失败: {e}")
    
    def _get_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        获取字段值（支持嵌套路径）
        
        Args:
            data: 数据字典
            field_path: 字段路径（如 'system.cpu.usage'）
            
        Returns:
            Any: 字段值
        """
        try:
            keys = field_path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict):
                    if key in value:
                        value = value[key]
                    else:
                        return None
                elif isinstance(value, list) and key.isdigit():
                    index = int(key)
                    if 0 <= index < len(value):
                        value = value[index]
                    else:
                        return None
                else:
                    return None
            
            return value
            
        except Exception as e:
            self.logger.debug(f"获取字段值失败 {field_path}: {e}")
            return None
    
    def _evaluate_simple_condition(self, field_value: Any, operator: str, 
                                  expected_value: Any, case_sensitive: bool = True) -> bool:
        """
        评估简单条件
        
        Args:
            field_value: 字段值
            operator: 操作符
            expected_value: 期望值
            case_sensitive: 是否区分大小写
            
        Returns:
            bool: 条件是否满足
        """
        if field_value is None:
            return operator in ['is_null', 'is_empty']
        
        # 字符串比较时处理大小写
        if not case_sensitive and isinstance(field_value, str) and isinstance(expected_value, str):
            field_value = field_value.lower()
            expected_value = expected_value.lower()
        
        try:
            if operator == 'eq' or operator == '==':
                return field_value == expected_value
            elif operator == 'ne' or operator == '!=':
                return field_value != expected_value
            elif operator == 'gt' or operator == '>':
                return float(field_value) > float(expected_value)
            elif operator == 'gte' or operator == '>=':
                return float(field_value) >= float(expected_value)
            elif operator == 'lt' or operator == '<':
                return float(field_value) < float(expected_value)
            elif operator == 'lte' or operator == '<=':
                return float(field_value) <= float(expected_value)
            elif operator == 'in':
                return field_value in expected_value
            elif operator == 'not_in':
                return field_value not in expected_value
            elif operator == 'contains':
                return str(expected_value) in str(field_value)
            elif operator == 'not_contains':
                return str(expected_value) not in str(field_value)
            elif operator == 'startswith':
                return str(field_value).startswith(str(expected_value))
            elif operator == 'endswith':
                return str(field_value).endswith(str(expected_value))
            elif operator == 'is_null':
                return field_value is None
            elif operator == 'is_not_null':
                return field_value is not None
            elif operator == 'is_empty':
                return not field_value if hasattr(field_value, '__len__') else False
            elif operator == 'is_not_empty':
                return bool(field_value) if hasattr(field_value, '__len__') else True
            elif operator == 'between':
                if isinstance(expected_value, (list, tuple)) and len(expected_value) == 2:
                    return expected_value[0] <= float(field_value) <= expected_value[1]
                return False
            else:
                self.logger.warning(f"未知的操作符: {operator}")
                return False
                
        except (ValueError, TypeError) as e:
            self.logger.debug(f"条件比较失败: {e}")
            return False
    
    def _evaluate_regex_condition(self, field_value: Any, pattern: str, 
                                 case_sensitive: bool = True) -> bool:
        """
        评估正则表达式条件
        
        Args:
            field_value: 字段值
            pattern: 正则表达式模式
            case_sensitive: 是否区分大小写
            
        Returns:
            bool: 条件是否满足
        """
        try:
            if field_value is None:
                return False
            
            flags = 0 if case_sensitive else re.IGNORECASE
            return bool(re.search(pattern, str(field_value), flags))
            
        except re.error as e:
            self.logger.error(f"正则表达式错误: {e}")
            return False
    
    def _evaluate_function_condition(self, field_value: Any, function_expr: str, 
                                   context: EvaluationContext) -> bool:
        """
        评估函数条件
        
        Args:
            field_value: 字段值
            function_expr: 函数表达式
            context: 评估上下文
            
        Returns:
            bool: 条件是否满足
        """
        try:
            # 构建安全的执行环境
            safe_globals = {
                '__builtins__': {},
                'field_value': field_value,
                'context': context,
                'data': context.data,
                'timestamp': context.timestamp,
                'datetime': datetime,
                'timedelta': timedelta,
            }
            safe_globals.update(self.custom_functions)
            
            # 执行函数表达式
            result = eval(function_expr, safe_globals, {})
            return bool(result)
            
        except Exception as e:
            self.logger.error(f"函数条件评估失败: {e}")
            return False

class RuleValidator:
    """规则验证器"""
    
    def __init__(self):
        """初始化规则验证器"""
        self.logger = get_logger(f"{__name__}.RuleValidator")
        self.schema = self._load_rule_schema()
    
    def _load_rule_schema(self) -> Dict[str, Any]:
        """加载规则JSON Schema"""
        return {
            "type": "object",
            "properties": {
                "id": {"type": "string", "minLength": 1},
                "name": {"type": "string", "minLength": 1},
                "description": {"type": "string"},
                "type": {"type": "string", "enum": ["trigger", "condition", "action", "composite"]},
                "enabled": {"type": "boolean"},
                "priority": {"type": "integer", "minimum": 1},
                "conditions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string", "minLength": 1},
                            "operator": {"type": "string", "minLength": 1},
                            "value": {},
                            "type": {"type": "string", "enum": ["simple", "regex", "function"]},
                            "case_sensitive": {"type": "boolean"},
                            "negate": {"type": "boolean"}
                        },
                        "required": ["field", "operator", "value"]
                    }
                },
                "actions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "minLength": 1},
                            "params": {"type": "object"},
                            "priority": {"type": "integer", "minimum": 1},
                            "timeout": {"type": "integer", "minimum": 1},
                            "retry_count": {"type": "integer", "minimum": 0}
                        },
                        "required": ["type", "params"]
                    }
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "cooldown": {"type": "integer", "minimum": 0},
                "max_executions": {"type": "integer", "minimum": 0},
                "depends_on": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "conflicts_with": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["id", "name", "type", "conditions", "actions"]
        }
    
    def validate_rule(self, rule_data: Dict[str, Any]) -> List[str]:
        """
        验证规则数据
        
        Args:
            rule_data: 规则数据
            
        Returns:
            List[str]: 验证错误列表
        """
        errors = []
        
        try:
            # JSON Schema验证
            jsonschema.validate(rule_data, self.schema)
        except jsonschema.ValidationError as e:
            errors.append(f"Schema验证失败: {e.message}")
        
        # 自定义验证
        errors.extend(self._validate_conditions(rule_data.get('conditions', [])))
        errors.extend(self._validate_actions(rule_data.get('actions', [])))
        errors.extend(self._validate_dependencies(rule_data))
        
        return errors
    
    def _validate_conditions(self, conditions: List[Dict[str, Any]]) -> List[str]:
        """验证条件"""
        errors = []
        
        for i, condition in enumerate(conditions):
            # 验证操作符
            operator = condition.get('operator')
            valid_operators = [
                'eq', '==', 'ne', '!=', 'gt', '>', 'gte', '>=', 'lt', '<', 'lte', '<=',
                'in', 'not_in', 'contains', 'not_contains', 'startswith', 'endswith',
                'is_null', 'is_not_null', 'is_empty', 'is_not_empty', 'between'
            ]
            
            if operator not in valid_operators:
                errors.append(f"条件 {i}: 无效的操作符 '{operator}'")
            
            # 验证正则表达式
            if condition.get('type') == 'regex':
                try:
                    re.compile(str(condition.get('value', '')))
                except re.error as e:
                    errors.append(f"条件 {i}: 无效的正则表达式 - {e}")
        
        return errors
    
    def _validate_actions(self, actions: List[Dict[str, Any]]) -> List[str]:
        """验证动作"""
        errors = []
        
        valid_action_types = [
            'ansible_playbook', 'script', 'container_action', 'api_call', 
            'notification', 'custom'
        ]
        
        for i, action in enumerate(actions):
            action_type = action.get('type')
            if action_type not in valid_action_types:
                errors.append(f"动作 {i}: 无效的动作类型 '{action_type}'")
            
            # 验证必需参数
            params = action.get('params', {})
            if action_type == 'ansible_playbook' and 'playbook' not in params:
                errors.append(f"动作 {i}: Ansible动作缺少playbook参数")
            elif action_type == 'script' and not any(k in params for k in ['script_path', 'script_content']):
                errors.append(f"动作 {i}: 脚本动作缺少script_path或script_content参数")
        
        return errors
    
    def _validate_dependencies(self, rule_data: Dict[str, Any]) -> List[str]:
        """验证依赖关系"""
        errors = []
        
        depends_on = rule_data.get('depends_on', [])
        conflicts_with = rule_data.get('conflicts_with', [])
        
        # 检查依赖和冲突是否有重叠
        overlap = set(depends_on) & set(conflicts_with)
        if overlap:
            errors.append(f"规则不能同时依赖和冲突: {list(overlap)}")
        
        return errors

class RuleFileWatcher(FileSystemEventHandler):
    """规则文件监控器"""
    
    def __init__(self, rule_engine):
        """初始化文件监控器"""
        self.rule_engine = rule_engine
        self.logger = get_logger(f"{__name__}.RuleFileWatcher")
        self.last_modified = {}
        self.debounce_time = 1.0  # 防抖时间（秒）
    
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        if not file_path.endswith(('.yaml', '.yml', '.json')):
            return
        
        # 防抖处理
        current_time = time.time()
        if file_path in self.last_modified:
            if current_time - self.last_modified[file_path] < self.debounce_time:
                return
        
        self.last_modified[file_path] = current_time
        
        self.logger.info(f"检测到规则文件变更: {file_path}")
        
        # 异步重新加载规则
        threading.Thread(
            target=self.rule_engine.reload_rules_from_file,
            args=(file_path,),
            daemon=True
        ).start()

class RuleEngine:
    """规则引擎主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化规则引擎"""
        self.logger = get_logger(f"{__name__}.RuleEngine")
        
        # 配置管理
        self.config_manager = ConfigManager()
        self.config = config or self.config_manager.get_config().get('rule_engine', {})
        
        # 核心组件
        self.condition_evaluator = ConditionEvaluator()
        self.rule_validator = RuleValidator()
        
        # 规则存储
        self.rules: Dict[str, Rule] = {}
        self.rule_groups: Dict[str, List[str]] = defaultdict(list)
        self.rule_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.rule_conflicts: Dict[str, Set[str]] = defaultdict(set)
        
        # 执行状态跟踪
        self.execution_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000))
        self.cooldown_tracker: Dict[str, datetime] = {}
        self.execution_counter: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int))
        
        # 性能统计
        self.evaluation_stats: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                'total_evaluations': 0,
                'matches': 0,
                'errors': 0,
                'avg_duration': 0.0,
                'last_evaluation': None
            })
        
        # 文件监控
        self.file_observer = None
        self.file_watcher = None
        
        # 线程锁
        self.rules_lock = threading.RLock()
        self.stats_lock = threading.Lock()
        
        # 初始化
        self._initialize()
    
    def _initialize(self):
        """初始化规则引擎"""
        try:
            # 加载规则
            self._load_rules()
            
            # 启动文件监控
            if self.config.get('storage', {}).get('auto_reload', False):
                self._start_file_watcher()
            
            # 更新指标
            active_rules_gauge.set(len([r for r in self.rules.values() if r.enabled]))
            
            self.logger.info(f"规则引擎初始化完成，加载了 {len(self.rules)} 个规则")
            
        except Exception as e:
            self.logger.error(f"规则引擎初始化失败: {e}")
            raise RuleEngineError(f"规则引擎初始化失败: {e}")
    
    def _load_rules(self):
        """加载规则"""
        storage_config = self.config.get('storage', {})
        storage_type = storage_config.get('type', 'file')
        
        if storage_type == 'file':
            self._load_rules_from_file(storage_config.get('file_path'))
        elif storage_type == 'database':
            self._load_rules_from_database(storage_config)
        elif storage_type == 'redis':
            self._load_rules_from_redis(storage_config)
        else:
            raise ValueError(f"不支持的存储类型: {storage_type}")
    
    def _load_rules_from_file(self, file_path: Optional[str] = None):
        """从文件加载规则"""
        if not file_path:
            file_path = './rules/trigger-rules.yaml'
        
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.warning(f"规则文件不存在: {file_path}")
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    rules_data = yaml.safe_load(f)
                else:
                    rules_data = json.load(f)
            
            self._parse_and_load_rules(rules_data)
            rule_reloads_total.labels(status='success').inc()
            
        except Exception as e:
            self.logger.error(f"从文件加载规则失败: {e}")
            rule_reloads_total.labels(status='error').inc()
            raise
    
    def _load_rules_from_database(self, db_config: Dict[str, Any]):
        """从数据库加载规则"""
        # 这里应该实现数据库加载逻辑
        self.logger.info("从数据库加载规则（未实现）")
    
    def _load_rules_from_redis(self, redis_config: Dict[str, Any]):
        """从Redis加载规则"""
        # 这里应该实现Redis加载逻辑
        self.logger.info("从Redis加载规则（未实现）")
    
    def _parse_and_load_rules(self, rules_data: Dict[str, Any]):
        """解析和加载规则数据"""
        with self.rules_lock:
            # 清空现有规则
            self.rules.clear()
            self.rule_groups.clear()
            self.rule_dependencies.clear()
            self.rule_conflicts.clear()
            
            # 解析规则
            rules_config = rules_data.get('rules', {})
            
            for rule_id, rule_data in rules_config.items():
                try:
                    # 验证规则
                    validation_errors = self.rule_validator.validate_rule(rule_data)
                    if validation_errors:
                        self.logger.error(f"规则 {rule_id} 验证失败: {validation_errors}")
                        continue
                    
                    # 创建规则对象
                    rule = self._create_rule_from_data(rule_id, rule_data)
                    self.rules[rule_id] = rule
                    
                    # 建立依赖关系
                    for dep_rule_id in rule.depends_on:
                        self.rule_dependencies[rule_id].add(dep_rule_id)
                    
                    for conflict_rule_id in rule.conflicts_with:
                        self.rule_conflicts[rule_id].add(conflict_rule_id)
                    
                    # 按标签分组
                    for tag in rule.tags:
                        self.rule_groups[tag].append(rule_id)
                    
                except Exception as e:
                    self.logger.error(f"解析规则 {rule_id} 失败: {e}")
                    continue
            
            # 验证依赖关系
            self._validate_rule_dependencies()
            
            self.logger.info(f"成功加载 {len(self.rules)} 个规则")
    
    def _create_rule_from_data(self, rule_id: str, rule_data: Dict[str, Any]) -> Rule:
        """从数据创建规则对象"""
        # 解析条件
        conditions = []
        for cond_data in rule_data.get('conditions', []):
            condition = RuleCondition(
                field=cond_data['field'],
                operator=cond_data['operator'],
                value=cond_data['value'],
                type=cond_data.get('type', 'simple'),
                case_sensitive=cond_data.get('case_sensitive', True),
                negate=cond_data.get('negate', False)
            )
            conditions.append(condition)
        
        # 解析动作
        actions = []
        for action_data in rule_data.get('actions', []):
            action = RuleAction(
                type=action_data['type'],
                params=action_data['params'],
                priority=action_data.get('priority', 1),
                timeout=action_data.get('timeout', 300),
                retry_count=action_data.get('retry_count', 1),
                condition=action_data.get('condition')
            )
            actions.append(action)
        
        # 解析时间限制
        valid_from = None
        valid_until = None
        if 'valid_from' in rule_data:
            valid_from = datetime.fromisoformat(rule_data['valid_from'])
        if 'valid_until' in rule_data:
            valid_until = datetime.fromisoformat(rule_data['valid_until'])
        
        # 创建规则对象
        rule = Rule(
            id=rule_id,
            name=rule_data['name'],
            description=rule_data.get('description', ''),
            type=RuleType(rule_data['type']),
            conditions=conditions,
            actions=actions,
            priority=rule_data.get('priority', 1),
            enabled=rule_data.get('enabled', True),
            tags=rule_data.get('tags', []),
            metadata=rule_data.get('metadata', {}),
            cooldown=rule_data.get('cooldown', 0),
            max_executions=rule_data.get('max_executions', 0),
            execution_window=rule_data.get('execution_window', 3600),
            depends_on=rule_data.get('depends_on', []),
            conflicts_with=rule_data.get('conflicts_with', []),
            valid_from=valid_from,
            valid_until=valid_until,
            schedule=rule_data.get('schedule')
        )
        
        return rule
    
    def _validate_rule_dependencies(self):
        """验证规则依赖关系"""
        # 检查循环依赖
        for rule_id in self.rules:
            if self._has_circular_dependency(rule_id, set()):
                self.logger.error(f"检测到循环依赖: {rule_id}")
                # 可以选择禁用有循环依赖的规则
                self.rules[rule_id].status = RuleStatus.ERROR
                self.rules[rule_id].last_error = "循环依赖"
        
        # 检查依赖的规则是否存在
        for rule_id, dependencies in self.rule_dependencies.items():
            for dep_rule_id in dependencies:
                if dep_rule_id not in self.rules:
                    self.logger.warning(f"规则 {rule_id} 依赖的规则 {dep_rule_id} 不存在")
    
    def _has_circular_dependency(self, rule_id: str, visited: Set[str]) -> bool:
        """检查是否存在循环依赖"""
        if rule_id in visited:
            return True
        
        visited.add(rule_id)
        
        for dep_rule_id in self.rule_dependencies.get(rule_id, []):
            if self._has_circular_dependency(dep_rule_id, visited.copy()):
                return True
        
        return False
    
    def _start_file_watcher(self):
        """启动文件监控"""
        try:
            storage_config = self.config.get('storage', {})
            file_path = storage_config.get('file_path', './rules/trigger-rules.yaml')
            watch_dir = Path(file_path).parent
            
            if watch_dir.exists():
                self.file_watcher = RuleFileWatcher(self)
                self.file_observer = Observer()
                self.file_observer.schedule(
                    self.file_watcher, str(watch_dir), recursive=False)
                self.file_observer.start()
                
                self.logger.info(f"启动文件监控: {watch_dir}")
            else:
                self.logger.warning(f"监控目录不存在: {watch_dir}")
                
        except Exception as e:
            self.logger.error(f"启动文件监控失败: {e}")
    
    def reload_rules_from_file(self, file_path: str):
        """从指定文件重新加载规则"""
        try:
            self.logger.info(f"重新加载规则文件: {file_path}")
            self._load_rules_from_file(file_path)
            active_rules_gauge.set(len([r for r in self.rules.values() if r.enabled]))
        except Exception as e:
            self.logger.error(f"重新加载规则失败: {e}")
    
    def evaluate_rules(self, data: Dict[str, Any], 
                      rule_ids: Optional[List[str]] = None) -> List[EvaluationResult]:
        """
        评估规则
        
        Args:
            data: 输入数据
            rule_ids: 要评估的规则ID列表（None表示评估所有规则）
            
        Returns:
            List[EvaluationResult]: 评估结果列表
        """
        context = EvaluationContext(
            data=data,
            timestamp=datetime.now()
        )
        
        results = []
        
        # 确定要评估的规则
        if rule_ids:
            rules_to_evaluate = [(rid, self.rules[rid]) for rid in rule_ids 
                               if rid in self.rules]
        else:
            rules_to_evaluate = list(self.rules.items())
        
        # 按优先级排序
        rules_to_evaluate.sort(key=lambda x: x[1].priority)
        
        for rule_id, rule in rules_to_evaluate:
            if not self._should_evaluate_rule(rule, context):
                continue
            
            result = self._evaluate_single_rule(rule, context)
            results.append(result)
            
            # 更新统计信息
            self._update_evaluation_stats(rule_id, result)
        
        return results
    
    def _should_evaluate_rule(self, rule: Rule, context: EvaluationContext) -> bool:
        """
        检查是否应该评估规则
        
        Args:
            rule: 规则对象
            context: 评估上下文
            
        Returns:
            bool: 是否应该评估
        """
        # 检查规则状态
        if not rule.enabled or rule.status != RuleStatus.ACTIVE:
            return False
        
        # 检查时间有效性
        current_time = context.timestamp
        if rule.valid_from and current_time < rule.valid_from:
            return False
        if rule.valid_until and current_time > rule.valid_until:
            return False
        
        # 检查调度
        if rule.schedule and not self._matches_schedule(rule.schedule, current_time):
            return False
        
        # 检查冷却时间
        if rule.id in self.cooldown_tracker:
            if current_time < self.cooldown_tracker[rule.id]:
                return False
        
        # 检查执行次数限制
        if rule.max_executions > 0:
            window_start = current_time - timedelta(seconds=rule.execution_window)
            recent_executions = sum(
                1 for exec_time in self.execution_history[rule.id]
                if exec_time > window_start
            )
            if recent_executions >= rule.max_executions:
                return False
        
        # 检查依赖关系
        if not self._check_rule_dependencies(rule, context):
            return False
        
        return True
    
    def _matches_schedule(self, schedule: str, current_time: datetime) -> bool:
        """
        检查是否匹配调度
        
        Args:
            schedule: Cron表达式
            current_time: 当前时间
            
        Returns:
            bool: 是否匹配
        """
        # 这里应该实现Cron表达式解析
        # 暂时返回True
        return True
    
    def _check_rule_dependencies(self, rule: Rule, context: EvaluationContext) -> bool:
        """
        检查规则依赖关系
        
        Args:
            rule: 规则对象
            context: 评估上下文
            
        Returns:
            bool: 依赖关系是否满足
        """
        # 检查依赖规则是否都已执行成功
        for dep_rule_id in rule.depends_on:
            if dep_rule_id not in self.rules:
                continue
            
            # 检查依赖规则的最近执行状态
            recent_executions = list(self.execution_history[dep_rule_id])[-5:]
            if not recent_executions or not any(
                exec_result.get('success', False) for exec_result in recent_executions
            ):
                return False
        
        # 检查冲突规则是否正在执行
        for conflict_rule_id in rule.conflicts_with:
            if conflict_rule_id in self.cooldown_tracker:
                if context.timestamp < self.cooldown_tracker[conflict_rule_id]:
                    return False
        
        return True
    
    def _evaluate_single_rule(self, rule: Rule, context: EvaluationContext) -> EvaluationResult:
        """
        评估单个规则
        
        Args:
            rule: 规则对象
            context: 评估上下文
            
        Returns:
            EvaluationResult: 评估结果
        """
        start_time = time.time()
        context.rule_id = rule.id
        
        result = EvaluationResult(
            rule_id=rule.id,
            result=MatchResult.NO_MATCH
        )
        
        try:
            with rule_evaluation_duration.time():
                # 评估所有条件
                matched_conditions = []
                all_conditions_met = True
                
                for i, condition in enumerate(rule.conditions):
                    try:
                        condition_met = self.condition_evaluator.evaluate_condition(
                            condition, context)
                        
                        if condition_met:
                            matched_conditions.append(f"condition_{i}")
                        else:
                            all_conditions_met = False
                            break
                            
                    except Exception as e:
                        self.logger.error(f"条件评估失败 {rule.id}[{i}]: {e}")
                        result.result = MatchResult.ERROR
                        result.error_message = str(e)
                        all_conditions_met = False
                        break
                
                # 设置结果
                if result.result != MatchResult.ERROR:
                    if all_conditions_met and rule.conditions:
                        result.result = MatchResult.MATCH
                        rule_evaluations_total.labels(
                            rule_id=rule.id, result='match').inc()
                    else:
                        result.result = MatchResult.NO_MATCH
                        rule_evaluations_total.labels(
                            rule_id=rule.id, result='no_match').inc()
                
                result.matched_conditions = matched_conditions
                
        except Exception as e:
            self.logger.error(f"规则评估失败 {rule.id}: {e}")
            result.result = MatchResult.ERROR
            result.error_message = str(e)
            rule_evaluations_total.labels(
                rule_id=rule.id, result='error').inc()
        
        finally:
            result.evaluation_time = time.time() - start_time
        
        return result
    
    def _update_evaluation_stats(self, rule_id: str, result: EvaluationResult):
        """
        更新评估统计信息
        
        Args:
            rule_id: 规则ID
            result: 评估结果
        """
        with self.stats_lock:
            stats = self.evaluation_stats[rule_id]
            stats['total_evaluations'] += 1
            stats['last_evaluation'] = datetime.now().isoformat()
            
            if result.result == MatchResult.MATCH:
                stats['matches'] += 1
            elif result.result == MatchResult.ERROR:
                stats['errors'] += 1
            
            # 更新平均持续时间
            total_time = stats['avg_duration'] * (stats['total_evaluations'] - 1)
            stats['avg_duration'] = (total_time + result.evaluation_time) / stats['total_evaluations']
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """
        获取规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            Optional[Rule]: 规则对象
        """
        return self.rules.get(rule_id)
    
    def get_rules_by_tag(self, tag: str) -> List[Rule]:
        """
        根据标签获取规则
        
        Args:
            tag: 标签
            
        Returns:
            List[Rule]: 规则列表
        """
        rule_ids = self.rule_groups.get(tag, [])
        return [self.rules[rule_id] for rule_id in rule_ids if rule_id in self.rules]
    
    def get_active_rules(self) -> List[Rule]:
        """
        获取活跃规则
        
        Returns:
            List[Rule]: 活跃规则列表
        """
        return [rule for rule in self.rules.values() 
                if rule.enabled and rule.status == RuleStatus.ACTIVE]
    
    def enable_rule(self, rule_id: str) -> bool:
        """
        启用规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 是否成功
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = True
            self.rules[rule_id].status = RuleStatus.ACTIVE
            active_rules_gauge.inc()
            self.logger.info(f"启用规则: {rule_id}")
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """
        禁用规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 是否成功
        """
        if rule_id in self.rules:
            self.rules[rule_id].enabled = False
            self.rules[rule_id].status = RuleStatus.DISABLED
            active_rules_gauge.dec()
            self.logger.info(f"禁用规则: {rule_id}")
            return True
        return False
    
    def add_rule(self, rule: Rule) -> bool:
        """
        添加规则
        
        Args:
            rule: 规则对象
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.rules_lock:
                # 验证规则
                rule_data = self._rule_to_dict(rule)
                validation_errors = self.rule_validator.validate_rule(rule_data)
                if validation_errors:
                    self.logger.error(f"规则验证失败: {validation_errors}")
                    return False
                
                # 添加规则
                self.rules[rule.id] = rule
                
                # 更新分组和依赖关系
                for tag in rule.tags:
                    self.rule_groups[tag].append(rule.id)
                
                for dep_rule_id in rule.depends_on:
                    self.rule_dependencies[rule.id].add(dep_rule_id)
                
                for conflict_rule_id in rule.conflicts_with:
                    self.rule_conflicts[rule.id].add(conflict_rule_id)
                
                if rule.enabled:
                    active_rules_gauge.inc()
                
                self.logger.info(f"添加规则: {rule.id}")
                return True
                
        except Exception as e:
            self.logger.error(f"添加规则失败: {e}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        删除规则
        
        Args:
            rule_id: 规则ID
            
        Returns:
            bool: 是否成功
        """
        try:
            with self.rules_lock:
                if rule_id not in self.rules:
                    return False
                
                rule = self.rules[rule_id]
                
                # 删除规则
                del self.rules[rule_id]
                
                # 清理分组和依赖关系
                for tag in rule.tags:
                    if rule_id in self.rule_groups[tag]:
                        self.rule_groups[tag].remove(rule_id)
                
                if rule_id in self.rule_dependencies:
                    del self.rule_dependencies[rule_id]
                
                if rule_id in self.rule_conflicts:
                    del self.rule_conflicts[rule_id]
                
                # 清理统计数据
                if rule_id in self.evaluation_stats:
                    del self.evaluation_stats[rule_id]
                
                if rule_id in self.execution_history:
                    del self.execution_history[rule_id]
                
                if rule_id in self.cooldown_tracker:
                    del self.cooldown_tracker[rule_id]
                
                if rule.enabled:
                    active_rules_gauge.dec()
                
                self.logger.info(f"删除规则: {rule_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"删除规则失败: {e}")
            return False
    
    def _rule_to_dict(self, rule: Rule) -> Dict[str, Any]:
        """将规则对象转换为字典"""
        return {
            'id': rule.id,
            'name': rule.name,
            'description': rule.description,
            'type': rule.type.value,
            'enabled': rule.enabled,
            'priority': rule.priority,
            'conditions': [
                {
                    'field': cond.field,
                    'operator': cond.operator,
                    'value': cond.value,
                    'type': cond.type,
                    'case_sensitive': cond.case_sensitive,
                    'negate': cond.negate
                }
                for cond in rule.conditions
            ],
            'actions': [
                {
                    'type': action.type,
                    'params': action.params,
                    'priority': action.priority,
                    'timeout': action.timeout,
                    'retry_count': action.retry_count,
                    'condition': action.condition
                }
                for action in rule.actions
            ],
            'tags': rule.tags,
            'cooldown': rule.cooldown,
            'max_executions': rule.max_executions,
            'depends_on': rule.depends_on,
            'conflicts_with': rule.conflicts_with
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict[str, Any]: 统计信息
        """
        with self.stats_lock:
            total_rules = len(self.rules)
            active_rules = len([r for r in self.rules.values() if r.enabled])
            
            return {
                'total_rules': total_rules,
                'active_rules': active_rules,
                'inactive_rules': total_rules - active_rules,
                'rule_types': {
                    rule_type.value: len([
                        r for r in self.rules.values() if r.type == rule_type
                    ])
                    for rule_type in RuleType
                },
                'evaluation_stats': dict(self.evaluation_stats),
                'rule_groups': {
                    tag: len(rule_ids) for tag, rule_ids in self.rule_groups.items()
                },
                'dependencies_count': len(self.rule_dependencies),
                'conflicts_count': len(self.rule_conflicts)
            }
    
    def register_custom_function(self, name: str, func: Callable):
        """
        注册自定义函数
        
        Args:
            name: 函数名
            func: 函数对象
        """
        self.condition_evaluator.register_function(name, func)
    
    def shutdown(self):
        """
        关闭规则引擎
        """
        self.logger.info("正在关闭规则引擎...")
        
        try:
            # 停止文件监控
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
            
            # 清理资源
            self.rules.clear()
            self.rule_groups.clear()
            self.rule_dependencies.clear()
            self.rule_conflicts.clear()
            self.evaluation_stats.clear()
            self.execution_history.clear()
            self.cooldown_tracker.clear()
            
            active_rules_gauge.set(0)
            
            self.logger.info("规则引擎已关闭")
            
        except Exception as e:
            self.logger.error(f"规则引擎关闭失败: {e}")

# 工厂函数
def create_rule_engine(config: Optional[Dict[str, Any]] = None) -> RuleEngine:
    """
    创建规则引擎实例
    
    Args:
        config: 配置字典
        
    Returns:
        RuleEngine: 规则引擎实例
    """
    return RuleEngine(config)

if __name__ == "__main__":
    # 测试代码
    def test_rule_engine():
        """测试规则引擎"""
        engine = create_rule_engine()
        
        # 模拟数据
        test_data = {
            'system': {
                'cpu': {'usage': 85.5},
                'memory': {'usage': 90.2},
                'disk': {'usage': 75.0}
            },
            'service': {
                'name': 'web-server',
                'status': 'running',
                'response_time': 1500
            },
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 评估规则
            results = engine.evaluate_rules(test_data)
            
            print(f"评估了 {len(results)} 个规则")
            for result in results:
                print(f"规则 {result.rule_id}: {result.result.value}")
                if result.matched_conditions:
                    print(f"  匹配条件: {result.matched_conditions}")
                if result.error_message:
                    print(f"  错误: {result.error_message}")
                print(f"  评估时间: {result.evaluation_time:.4f}秒")
            
            # 获取统计信息
            stats = engine.get_statistics()
            print(f"\n统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
            
        finally:
            engine.shutdown()
    
    # 运行测试
    test_rule_engine()