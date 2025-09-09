#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
指标收集器模块

本模块提供指标收集和监控功能，包括：
- 系统指标收集
- 应用指标收集
- 指标存储和查询
- 指标告警

Author: AIOps Team
Version: 1.0.0
Date: 2025-01-10
"""

import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from threading import Lock
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """指标数据类"""
    name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    unit: str = ""
    description: str = ""

class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化指标收集器
        
        Args:
            max_history: 最大历史记录数
        """
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()
        self.start_time = time.time()
        
    def counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None) -> None:
        """
        记录计数器指标
        
        Args:
            name: 指标名称
            value: 增量值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels or {})
            self.counters[key] += value
            
            metric = Metric(
                name=name,
                value=self.counters[key],
                labels=labels or {},
                unit="count"
            )
            self.metrics[key].append(metric)
            
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        记录仪表盘指标
        
        Args:
            name: 指标名称
            value: 当前值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels or {})
            self.gauges[key] = value
            
            metric = Metric(
                name=name,
                value=value,
                labels=labels or {},
                unit="gauge"
            )
            self.metrics[key].append(metric)
            
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None) -> None:
        """
        记录直方图指标
        
        Args:
            name: 指标名称
            value: 观测值
            labels: 标签
        """
        with self._lock:
            key = self._make_key(name, labels or {})
            self.histograms[key].append(value)
            
            metric = Metric(
                name=name,
                value=value,
                labels=labels or {},
                unit="histogram"
            )
            self.metrics[key].append(metric)
            
    def timing(self, name: str, duration: float, labels: Dict[str, str] = None) -> None:
        """
        记录时间指标
        
        Args:
            name: 指标名称
            duration: 持续时间（秒）
            labels: 标签
        """
        self.histogram(name, duration, labels)
        
    def get_metrics(self, name: str = None, labels: Dict[str, str] = None) -> List[Metric]:
        """
        获取指标数据
        
        Args:
            name: 指标名称过滤
            labels: 标签过滤
            
        Returns:
            指标列表
        """
        with self._lock:
            if name and labels:
                key = self._make_key(name, labels)
                return list(self.metrics.get(key, []))
            elif name:
                result = []
                for key, metrics in self.metrics.items():
                    if key.startswith(name):
                        result.extend(metrics)
                return result
            else:
                result = []
                for metrics in self.metrics.values():
                    result.extend(metrics)
                return result
                
    def get_summary(self) -> Dict[str, Any]:
        """
        获取指标摘要
        
        Returns:
            指标摘要信息
        """
        with self._lock:
            return {
                'uptime': time.time() - self.start_time,
                'total_metrics': sum(len(metrics) for metrics in self.metrics.values()),
                'counters_count': len(self.counters),
                'gauges_count': len(self.gauges),
                'histograms_count': len(self.histograms),
                'metric_names': list(set(key.split('|')[0] for key in self.metrics.keys()))
            }
            
    def clear(self) -> None:
        """清空所有指标"""
        with self._lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            
    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """
        生成指标键
        
        Args:
            name: 指标名称
            labels: 标签
            
        Returns:
            指标键
        """
        if not labels:
            return name
        
        label_str = ','.join(f'{k}={v}' for k, v in sorted(labels.items()))
        return f'{name}|{label_str}'
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

# 全局指标收集器实例
metrics_collector = MetricsCollector()