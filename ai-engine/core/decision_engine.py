#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策引擎模块

本模块实现了智能决策引擎，包括：
- 规则引擎
- 决策树
- 强化学习决策
- 多目标优化
- 风险评估
- 决策执行

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
import json
import yaml
from enum import Enum
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# 机器学习库
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# 优化库
try:
    from scipy.optimize import minimize, differential_evolution
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy not available")

# 强化学习（简化版本）
try:
    import gym
    GYM_AVAILABLE = True
except ImportError:
    GYM_AVAILABLE = False
    logging.warning("Gym not available")

from utils.logger import setup_logger
from utils.cache import CacheManager

logger = setup_logger(__name__)

class ActionType(Enum):
    """动作类型枚举"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    RESTART_SERVICE = "restart_service"
    ALERT = "alert"
    OPTIMIZE = "optimize"
    MAINTAIN = "maintain"
    IGNORE = "ignore"
    INVESTIGATE = "investigate"
    ROLLBACK = "rollback"
    BACKUP = "backup"

class Priority(Enum):
    """优先级枚举"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    INFO = 5

class RiskLevel(Enum):
    """风险等级枚举"""
    VERY_HIGH = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    VERY_LOW = 1

@dataclass
class Decision:
    """决策数据类"""
    action: ActionType
    priority: Priority
    confidence: float
    risk_level: RiskLevel
    reasoning: str
    parameters: Dict[str, Any]
    estimated_impact: Dict[str, float]
    execution_time: Optional[datetime] = None
    dependencies: List[str] = None
    rollback_plan: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.execution_time is None:
            self.execution_time = datetime.now()

@dataclass
class Context:
    """决策上下文"""
    metrics: Dict[str, float]
    anomalies: List[Dict[str, Any]]
    predictions: List[Dict[str, Any]]
    system_state: Dict[str, Any]
    historical_decisions: List[Decision]
    constraints: Dict[str, Any]
    objectives: List[str]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules = []
        self.rule_stats = {}
    
    def add_rule(self, name: str, condition: callable, action: ActionType, 
                priority: Priority, parameters: Dict[str, Any] = None):
        """
        添加规则
        
        Args:
            name: 规则名称
            condition: 条件函数
            action: 动作类型
            priority: 优先级
            parameters: 参数
        """
        rule = {
            'name': name,
            'condition': condition,
            'action': action,
            'priority': priority,
            'parameters': parameters or {},
            'created_at': datetime.now(),
            'triggered_count': 0,
            'success_count': 0
        }
        self.rules.append(rule)
        self.rule_stats[name] = {'triggered': 0, 'success': 0}
    
    def evaluate(self, context: Context) -> List[Decision]:
        """
        评估规则
        
        Args:
            context: 决策上下文
            
        Returns:
            决策列表
        """
        decisions = []
        
        for rule in self.rules:
            try:
                if rule['condition'](context):
                    decision = Decision(
                        action=rule['action'],
                        priority=rule['priority'],
                        confidence=0.9,  # 规则引擎置信度较高
                        risk_level=RiskLevel.LOW,
                        reasoning=f"规则触发: {rule['name']}",
                        parameters=rule['parameters']
                    )
                    decisions.append(decision)
                    
                    # 更新统计
                    rule['triggered_count'] += 1
                    self.rule_stats[rule['name']]['triggered'] += 1
                    
            except Exception as e:
                logger.error(f"规则{rule['name']}评估失败: {e}")
        
        return decisions
    
    def load_rules_from_config(self, config_path: str):
        """
        从配置文件加载规则
        
        Args:
            config_path: 配置文件路径
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)
            
            for rule_config in config.get('rules', []):
                # 这里需要根据配置动态创建条件函数
                # 简化实现，实际应该支持更复杂的条件表达式
                condition = self._create_condition_from_config(rule_config['condition'])
                
                self.add_rule(
                    name=rule_config['name'],
                    condition=condition,
                    action=ActionType(rule_config['action']),
                    priority=Priority(rule_config['priority']),
                    parameters=rule_config.get('parameters', {})
                )
                
        except Exception as e:
            logger.error(f"加载规则配置失败: {e}")
    
    def _create_condition_from_config(self, condition_config: Dict[str, Any]) -> callable:
        """
        从配置创建条件函数
        
        Args:
            condition_config: 条件配置
            
        Returns:
            条件函数
        """
        def condition(context: Context) -> bool:
            try:
                metric = condition_config.get('metric')
                operator = condition_config.get('operator')
                threshold = condition_config.get('threshold')
                
                if metric not in context.metrics:
                    return False
                
                value = context.metrics[metric]
                
                if operator == 'gt':
                    return value > threshold
                elif operator == 'lt':
                    return value < threshold
                elif operator == 'eq':
                    return value == threshold
                elif operator == 'gte':
                    return value >= threshold
                elif operator == 'lte':
                    return value <= threshold
                else:
                    return False
                    
            except Exception:
                return False
        
        return condition

class DecisionTree:
    """决策树"""
    
    def __init__(self):
        self.model = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, training_data: List[Dict[str, Any]]):
        """
        训练决策树
        
        Args:
            training_data: 训练数据
        """
        try:
            if not training_data:
                raise ValueError("训练数据为空")
            
            # 准备训练数据
            df = pd.DataFrame(training_data)
            
            # 特征列
            feature_columns = [col for col in df.columns if col not in ['action', 'decision']]
            X = df[feature_columns]
            
            # 目标列
            if 'action' in df.columns:
                y = df['action']
            elif 'decision' in df.columns:
                y = df['decision']
            else:
                raise ValueError("缺少目标列")
            
            # 处理分类特征
            for col in X.select_dtypes(include=['object']).columns:
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.label_encoders[col] = le
            
            # 标准化数值特征
            numeric_columns = X.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                X[numeric_columns] = self.scaler.fit_transform(X[numeric_columns])
            
            # 编码目标变量
            if y.dtype == 'object':
                le_target = LabelEncoder()
                y = le_target.fit_transform(y)
                self.label_encoders['target'] = le_target
            
            # 训练模型
            self.model = DecisionTreeClassifier(
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.model.fit(X, y)
            self.feature_columns = feature_columns
            self.is_trained = True
            
            logger.info(f"决策树训练完成，特征数: {len(feature_columns)}")
            
        except Exception as e:
            logger.error(f"决策树训练失败: {e}")
            raise
    
    def predict(self, context: Context) -> Optional[Decision]:
        """
        预测决策
        
        Args:
            context: 决策上下文
            
        Returns:
            决策结果
        """
        try:
            if not self.is_trained:
                return None
            
            # 准备特征数据
            features = self._extract_features(context)
            
            if not features:
                return None
            
            # 预测
            prediction = self.model.predict([features])[0]
            probabilities = self.model.predict_proba([features])[0]
            confidence = max(probabilities)
            
            # 解码预测结果
            if 'target' in self.label_encoders:
                action_name = self.label_encoders['target'].inverse_transform([prediction])[0]
                action = ActionType(action_name)
            else:
                action = ActionType(list(ActionType)[prediction])
            
            decision = Decision(
                action=action,
                priority=Priority.MEDIUM,
                confidence=float(confidence),
                risk_level=RiskLevel.MEDIUM,
                reasoning="决策树预测",
                parameters={},
                estimated_impact={'confidence': float(confidence)}
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"决策树预测失败: {e}")
            return None
    
    def _extract_features(self, context: Context) -> List[float]:
        """
        提取特征
        
        Args:
            context: 决策上下文
            
        Returns:
            特征列表
        """
        try:
            features = []
            
            # 从上下文提取特征
            for col in self.feature_columns:
                if col in context.metrics:
                    features.append(context.metrics[col])
                elif col == 'anomaly_count':
                    features.append(len(context.anomalies))
                elif col == 'prediction_confidence':
                    if context.predictions:
                        avg_confidence = np.mean([p.get('confidence', 0.5) for p in context.predictions])
                        features.append(avg_confidence)
                    else:
                        features.append(0.5)
                else:
                    features.append(0.0)  # 默认值
            
            return features
            
        except Exception as e:
            logger.error(f"特征提取失败: {e}")
            return []

class MultiObjectiveOptimizer:
    """多目标优化器"""
    
    def __init__(self):
        self.objectives = []
        self.constraints = []
    
    def add_objective(self, name: str, weight: float, maximize: bool = True):
        """
        添加优化目标
        
        Args:
            name: 目标名称
            weight: 权重
            maximize: 是否最大化
        """
        self.objectives.append({
            'name': name,
            'weight': weight,
            'maximize': maximize
        })
    
    def add_constraint(self, name: str, constraint_func: callable):
        """
        添加约束
        
        Args:
            name: 约束名称
            constraint_func: 约束函数
        """
        self.constraints.append({
            'name': name,
            'func': constraint_func
        })
    
    def optimize(self, decisions: List[Decision], context: Context) -> List[Decision]:
        """
        优化决策
        
        Args:
            decisions: 候选决策列表
            context: 决策上下文
            
        Returns:
            优化后的决策列表
        """
        try:
            if not decisions:
                return []
            
            # 计算每个决策的目标函数值
            scored_decisions = []
            
            for decision in decisions:
                score = self._calculate_score(decision, context)
                if self._check_constraints(decision, context):
                    scored_decisions.append((decision, score))
            
            # 按分数排序
            scored_decisions.sort(key=lambda x: x[1], reverse=True)
            
            # 返回排序后的决策
            return [decision for decision, score in scored_decisions]
            
        except Exception as e:
            logger.error(f"多目标优化失败: {e}")
            return decisions
    
    def _calculate_score(self, decision: Decision, context: Context) -> float:
        """
        计算决策分数
        
        Args:
            decision: 决策
            context: 上下文
            
        Returns:
            分数
        """
        total_score = 0.0
        total_weight = 0.0
        
        for objective in self.objectives:
            weight = objective['weight']
            maximize = objective['maximize']
            
            # 根据目标类型计算分数
            if objective['name'] == 'confidence':
                score = decision.confidence
            elif objective['name'] == 'priority':
                score = 1.0 / decision.priority.value  # 优先级越高分数越高
            elif objective['name'] == 'risk':
                score = 1.0 / decision.risk_level.value  # 风险越低分数越高
            else:
                score = 0.5  # 默认分数
            
            if not maximize:
                score = 1.0 - score
            
            total_score += weight * score
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _check_constraints(self, decision: Decision, context: Context) -> bool:
        """
        检查约束条件
        
        Args:
            decision: 决策
            context: 上下文
            
        Returns:
            是否满足约束
        """
        for constraint in self.constraints:
            try:
                if not constraint['func'](decision, context):
                    return False
            except Exception as e:
                logger.warning(f"约束{constraint['name']}检查失败: {e}")
                return False
        
        return True

class RiskAssessment:
    """风险评估"""
    
    def __init__(self):
        self.risk_factors = {
            'system_load': 0.3,
            'error_rate': 0.4,
            'response_time': 0.2,
            'resource_usage': 0.1
        }
    
    def assess_risk(self, decision: Decision, context: Context) -> RiskLevel:
        """
        评估决策风险
        
        Args:
            decision: 决策
            context: 上下文
            
        Returns:
            风险等级
        """
        try:
            risk_score = 0.0
            
            # 基于动作类型的基础风险
            action_risks = {
                ActionType.SCALE_UP: 0.3,
                ActionType.SCALE_DOWN: 0.4,
                ActionType.RESTART_SERVICE: 0.8,
                ActionType.ROLLBACK: 0.7,
                ActionType.ALERT: 0.1,
                ActionType.OPTIMIZE: 0.5,
                ActionType.MAINTAIN: 0.2,
                ActionType.IGNORE: 0.1,
                ActionType.INVESTIGATE: 0.1,
                ActionType.BACKUP: 0.2
            }
            
            base_risk = action_risks.get(decision.action, 0.5)
            risk_score += base_risk * 0.4
            
            # 基于系统状态的风险
            system_risk = self._calculate_system_risk(context)
            risk_score += system_risk * 0.3
            
            # 基于历史决策的风险
            history_risk = self._calculate_history_risk(decision, context)
            risk_score += history_risk * 0.2
            
            # 基于置信度的风险（置信度越低风险越高）
            confidence_risk = 1.0 - decision.confidence
            risk_score += confidence_risk * 0.1
            
            # 转换为风险等级
            if risk_score >= 0.8:
                return RiskLevel.VERY_HIGH
            elif risk_score >= 0.6:
                return RiskLevel.HIGH
            elif risk_score >= 0.4:
                return RiskLevel.MEDIUM
            elif risk_score >= 0.2:
                return RiskLevel.LOW
            else:
                return RiskLevel.VERY_LOW
                
        except Exception as e:
            logger.error(f"风险评估失败: {e}")
            return RiskLevel.MEDIUM
    
    def _calculate_system_risk(self, context: Context) -> float:
        """
        计算系统风险
        
        Args:
            context: 上下文
            
        Returns:
            系统风险分数
        """
        try:
            risk_score = 0.0
            
            # CPU使用率风险
            if 'cpu_usage' in context.metrics:
                cpu_usage = context.metrics['cpu_usage']
                if cpu_usage > 90:
                    risk_score += 0.4
                elif cpu_usage > 80:
                    risk_score += 0.2
            
            # 内存使用率风险
            if 'memory_usage' in context.metrics:
                memory_usage = context.metrics['memory_usage']
                if memory_usage > 90:
                    risk_score += 0.3
                elif memory_usage > 80:
                    risk_score += 0.15
            
            # 错误率风险
            if 'error_rate' in context.metrics:
                error_rate = context.metrics['error_rate']
                if error_rate > 5:
                    risk_score += 0.3
                elif error_rate > 1:
                    risk_score += 0.1
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"系统风险计算失败: {e}")
            return 0.5
    
    def _calculate_history_risk(self, decision: Decision, context: Context) -> float:
        """
        计算历史风险
        
        Args:
            decision: 当前决策
            context: 上下文
            
        Returns:
            历史风险分数
        """
        try:
            if not context.historical_decisions:
                return 0.3  # 无历史数据时的默认风险
            
            # 检查最近的相似决策
            recent_decisions = [d for d in context.historical_decisions 
                             if d.action == decision.action and 
                             (datetime.now() - d.execution_time).total_seconds() < 3600]
            
            if len(recent_decisions) > 3:
                return 0.8  # 短时间内频繁执行相同动作风险较高
            elif len(recent_decisions) > 1:
                return 0.4
            else:
                return 0.1
                
        except Exception as e:
            logger.error(f"历史风险计算失败: {e}")
            return 0.3

class DecisionEngine:
    """决策引擎主类"""
    
    def __init__(self, config):
        """
        初始化决策引擎
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.cache_manager = CacheManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 初始化组件
        self.rule_engine = RuleEngine()
        self.decision_tree = DecisionTree()
        self.optimizer = MultiObjectiveOptimizer()
        self.risk_assessment = RiskAssessment()
        
        # 决策历史
        self.decision_history = []
        
        # 性能统计
        self.decision_stats = {
            'total_decisions': 0,
            'successful_decisions': 0,
            'failed_decisions': 0,
            'processing_time': [],
            'risk_distribution': {level.name: 0 for level in RiskLevel}
        }
        
        self.is_initialized = False
    
    async def initialize(self):
        """初始化决策引擎"""
        try:
            logger.info("正在初始化决策引擎...")
            
            # 初始化缓存管理器
            await self.cache_manager.initialize()
            
            # 设置优化目标
            self.optimizer.add_objective('confidence', 0.4, maximize=True)
            self.optimizer.add_objective('priority', 0.3, maximize=True)
            self.optimizer.add_objective('risk', 0.3, maximize=False)
            
            # 添加约束
            self.optimizer.add_constraint('risk_limit', self._risk_constraint)
            
            # 加载默认规则
            await self._load_default_rules()
            
            # 加载训练数据（如果有）
            await self._load_training_data()
            
            self.is_initialized = True
            logger.info("决策引擎初始化完成")
            
        except Exception as e:
            logger.error(f"决策引擎初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        logger.info("正在清理决策引擎资源...")
        
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        
        if hasattr(self, 'cache_manager'):
            await self.cache_manager.cleanup()
        
        logger.info("决策引擎资源清理完成")
    
    def is_ready(self) -> bool:
        """检查是否就绪"""
        return self.is_initialized
    
    async def make_decision(self, context: Context) -> List[Decision]:
        """
        制定决策
        
        Args:
            context: 决策上下文
            
        Returns:
            决策列表
        """
        start_time = datetime.now()
        
        try:
            # 收集候选决策
            candidate_decisions = []
            
            # 规则引擎决策
            rule_decisions = self.rule_engine.evaluate(context)
            candidate_decisions.extend(rule_decisions)
            
            # 决策树决策
            tree_decision = self.decision_tree.predict(context)
            if tree_decision:
                candidate_decisions.append(tree_decision)
            
            # 如果没有候选决策，生成默认决策
            if not candidate_decisions:
                default_decision = self._generate_default_decision(context)
                if default_decision:
                    candidate_decisions.append(default_decision)
            
            # 风险评估
            for decision in candidate_decisions:
                decision.risk_level = self.risk_assessment.assess_risk(decision, context)
            
            # 多目标优化
            optimized_decisions = self.optimizer.optimize(candidate_decisions, context)
            
            # 生成回滚计划
            for decision in optimized_decisions:
                decision.rollback_plan = self._generate_rollback_plan(decision)
            
            # 更新统计信息
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(True, processing_time, optimized_decisions)
            
            # 记录决策历史
            self.decision_history.extend(optimized_decisions)
            
            # 保持历史记录在合理范围内
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-1000:]
            
            return optimized_decisions
            
        except Exception as e:
            logger.error(f"决策制定失败: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, [])
            raise
    
    def _generate_default_decision(self, context: Context) -> Optional[Decision]:
        """
        生成默认决策
        
        Args:
            context: 决策上下文
            
        Returns:
            默认决策
        """
        try:
            # 基于异常数量决定默认动作
            if len(context.anomalies) > 5:
                action = ActionType.INVESTIGATE
                priority = Priority.HIGH
            elif len(context.anomalies) > 0:
                action = ActionType.ALERT
                priority = Priority.MEDIUM
            else:
                action = ActionType.MAINTAIN
                priority = Priority.LOW
            
            return Decision(
                action=action,
                priority=priority,
                confidence=0.5,
                risk_level=RiskLevel.MEDIUM,
                reasoning="默认决策：基于异常数量",
                parameters={},
                estimated_impact={'default': True}
            )
            
        except Exception as e:
            logger.error(f"生成默认决策失败: {e}")
            return None
    
    def _generate_rollback_plan(self, decision: Decision) -> Dict[str, Any]:
        """
        生成回滚计划
        
        Args:
            decision: 决策
            
        Returns:
            回滚计划
        """
        rollback_actions = {
            ActionType.SCALE_UP: ActionType.SCALE_DOWN,
            ActionType.SCALE_DOWN: ActionType.SCALE_UP,
            ActionType.RESTART_SERVICE: ActionType.INVESTIGATE,
            ActionType.OPTIMIZE: ActionType.ROLLBACK,
            ActionType.ROLLBACK: ActionType.INVESTIGATE
        }
        
        rollback_action = rollback_actions.get(decision.action)
        
        if rollback_action:
            return {
                'action': rollback_action.value,
                'parameters': decision.parameters,
                'timeout': 300,  # 5分钟超时
                'conditions': ['execution_failed', 'negative_impact']
            }
        
        return {}
    
    def _risk_constraint(self, decision: Decision, context: Context) -> bool:
        """
        风险约束
        
        Args:
            decision: 决策
            context: 上下文
            
        Returns:
            是否满足风险约束
        """
        # 高风险决策需要更高的置信度
        if decision.risk_level in [RiskLevel.VERY_HIGH, RiskLevel.HIGH]:
            return decision.confidence >= 0.8
        elif decision.risk_level == RiskLevel.MEDIUM:
            return decision.confidence >= 0.6
        else:
            return decision.confidence >= 0.3
    
    async def _load_default_rules(self):
        """
        加载默认规则
        """
        try:
            # CPU使用率过高规则
            self.rule_engine.add_rule(
                name="cpu_high",
                condition=lambda ctx: ctx.metrics.get('cpu_usage', 0) > 80,
                action=ActionType.SCALE_UP,
                priority=Priority.HIGH,
                parameters={'resource': 'cpu', 'threshold': 80}
            )
            
            # 内存使用率过高规则
            self.rule_engine.add_rule(
                name="memory_high",
                condition=lambda ctx: ctx.metrics.get('memory_usage', 0) > 85,
                action=ActionType.SCALE_UP,
                priority=Priority.HIGH,
                parameters={'resource': 'memory', 'threshold': 85}
            )
            
            # 错误率过高规则
            self.rule_engine.add_rule(
                name="error_rate_high",
                condition=lambda ctx: ctx.metrics.get('error_rate', 0) > 5,
                action=ActionType.INVESTIGATE,
                priority=Priority.CRITICAL,
                parameters={'metric': 'error_rate', 'threshold': 5}
            )
            
            # 响应时间过长规则
            self.rule_engine.add_rule(
                name="response_time_high",
                condition=lambda ctx: ctx.metrics.get('response_time', 0) > 2000,
                action=ActionType.OPTIMIZE,
                priority=Priority.MEDIUM,
                parameters={'metric': 'response_time', 'threshold': 2000}
            )
            
            # 异常数量过多规则
            self.rule_engine.add_rule(
                name="anomaly_count_high",
                condition=lambda ctx: len(ctx.anomalies) > 10,
                action=ActionType.ALERT,
                priority=Priority.HIGH,
                parameters={'anomaly_threshold': 10}
            )
            
            logger.info("默认规则加载完成")
            
        except Exception as e:
            logger.error(f"加载默认规则失败: {e}")
    
    async def _load_training_data(self):
        """
        加载训练数据
        """
        try:
            # 这里可以从文件或数据库加载历史决策数据
            # 用于训练决策树
            
            # 示例训练数据
            training_data = [
                {
                    'cpu_usage': 85, 'memory_usage': 70, 'error_rate': 2,
                    'anomaly_count': 3, 'action': 'scale_up'
                },
                {
                    'cpu_usage': 60, 'memory_usage': 80, 'error_rate': 1,
                    'anomaly_count': 1, 'action': 'maintain'
                },
                {
                    'cpu_usage': 95, 'memory_usage': 90, 'error_rate': 8,
                    'anomaly_count': 15, 'action': 'restart_service'
                }
            ]
            
            if training_data:
                self.decision_tree.train(training_data)
                logger.info("决策树训练完成")
            
        except Exception as e:
            logger.warning(f"加载训练数据失败: {e}")
    
    def _update_stats(self, success: bool, processing_time: float, decisions: List[Decision]):
        """
        更新统计信息
        
        Args:
            success: 是否成功
            processing_time: 处理时间
            decisions: 决策列表
        """
        self.decision_stats['total_decisions'] += 1
        
        if success:
            self.decision_stats['successful_decisions'] += 1
            
            # 更新风险分布
            for decision in decisions:
                risk_name = decision.risk_level.name
                self.decision_stats['risk_distribution'][risk_name] += 1
        else:
            self.decision_stats['failed_decisions'] += 1
        
        self.decision_stats['processing_time'].append(processing_time)
        
        # 保持最近1000次记录
        if len(self.decision_stats['processing_time']) > 1000:
            self.decision_stats['processing_time'] = self.decision_stats['processing_time'][-1000:]
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取决策统计信息
        
        Returns:
            统计信息字典
        """
        stats = self.decision_stats.copy()
        
        if stats['processing_time']:
            stats['avg_processing_time'] = np.mean(stats['processing_time'])
            stats['max_processing_time'] = np.max(stats['processing_time'])
            stats['min_processing_time'] = np.min(stats['processing_time'])
        
        if stats['total_decisions'] > 0:
            stats['success_rate'] = stats['successful_decisions'] / stats['total_decisions']
        
        # 规则引擎统计
        stats['rule_stats'] = self.rule_engine.rule_stats
        
        # 决策历史统计
        stats['decision_history_count'] = len(self.decision_history)
        
        return stats
    
    async def execute_decision(self, decision: Decision) -> Dict[str, Any]:
        """
        执行决策（接口，具体实现由执行器完成）
        
        Args:
            decision: 要执行的决策
            
        Returns:
            执行结果
        """
        try:
            logger.info(f"准备执行决策: {decision.action.value}")
            
            # 这里应该调用具体的执行器
            # 例如：Ansible执行器、Kubernetes执行器等
            
            result = {
                'decision_id': id(decision),
                'action': decision.action.value,
                'status': 'pending',
                'message': '决策已提交执行',
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"决策执行失败: {e}")
            return {
                'decision_id': id(decision),
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }