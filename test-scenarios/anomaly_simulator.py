#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测测试场景模拟器

该模块专门用于生成各种异常场景，测试AI引擎的异常检测能力。
包括性能异常、错误率异常、资源耗尽、网络故障等场景。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AnomalyType(Enum):
    """异常类型枚举"""
    PERFORMANCE_DEGRADATION = "performance_degradation"  # 性能下降
    ERROR_SPIKE = "error_spike"                        # 错误率激增
    RESOURCE_EXHAUSTION = "resource_exhaustion"        # 资源耗尽
    NETWORK_LATENCY = "network_latency"                # 网络延迟
    MEMORY_LEAK = "memory_leak"                        # 内存泄漏
    CPU_SPIKE = "cpu_spike"                            # CPU峰值
    DATABASE_SLOWDOWN = "database_slowdown"            # 数据库慢查询
    CASCADING_FAILURE = "cascading_failure"            # 级联故障
    PERIODIC_ANOMALY = "periodic_anomaly"              # 周期性异常
    GRADUAL_DEGRADATION = "gradual_degradation"        # 渐进式性能下降


@dataclass
class AnomalyPattern:
    """异常模式定义"""
    anomaly_type: AnomalyType
    start_time: datetime
    duration_minutes: int
    severity_multiplier: float
    affected_metrics: List[str]
    description: str
    recovery_time_minutes: int = 5


class AnomalySimulator:
    """异常场景模拟器"""
    
    def __init__(self):
        """
        初始化异常模拟器
        """
        self.anomaly_patterns = []
        self.current_anomalies = []
        
    def create_performance_degradation_pattern(self, 
                                             start_time: datetime,
                                             duration_minutes: int = 30,
                                             severity: float = 3.0) -> AnomalyPattern:
        """
        创建性能下降异常模式
        
        Args:
            start_time: 异常开始时间
            duration_minutes: 持续时间（分钟）
            severity: 严重程度倍数
            
        Returns:
            异常模式对象
        """
        return AnomalyPattern(
            anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity_multiplier=severity,
            affected_metrics=[
                "http_request_duration_ms",
                "db_query_duration_ms",
                "http_requests_per_second"
            ],
            description=f"Performance degradation lasting {duration_minutes} minutes with {severity}x impact",
            recovery_time_minutes=10
        )
    
    def create_error_spike_pattern(self,
                                 start_time: datetime,
                                 duration_minutes: int = 15,
                                 error_multiplier: float = 20.0) -> AnomalyPattern:
        """
        创建错误率激增异常模式
        
        Args:
            start_time: 异常开始时间
            duration_minutes: 持续时间（分钟）
            error_multiplier: 错误率倍数
            
        Returns:
            异常模式对象
        """
        return AnomalyPattern(
            anomaly_type=AnomalyType.ERROR_SPIKE,
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity_multiplier=error_multiplier,
            affected_metrics=[
                "http_error_rate",
                "http_requests_per_second",
                "http_request_duration_ms"
            ],
            description=f"Error rate spike with {error_multiplier}x normal error rate for {duration_minutes} minutes",
            recovery_time_minutes=5
        )
    
    def create_resource_exhaustion_pattern(self,
                                         start_time: datetime,
                                         resource_type: str = "memory",
                                         duration_minutes: int = 45) -> AnomalyPattern:
        """
        创建资源耗尽异常模式
        
        Args:
            start_time: 异常开始时间
            resource_type: 资源类型 ('memory', 'cpu', 'disk')
            duration_minutes: 持续时间（分钟）
            
        Returns:
            异常模式对象
        """
        if resource_type == "memory":
            affected_metrics = ["system_memory_usage_percent"]
            severity = 1.5
        elif resource_type == "cpu":
            affected_metrics = ["system_cpu_usage_percent"]
            severity = 2.5
        elif resource_type == "disk":
            affected_metrics = ["system_disk_io_mbps"]
            severity = 5.0
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")
        
        return AnomalyPattern(
            anomaly_type=AnomalyType.RESOURCE_EXHAUSTION,
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity_multiplier=severity,
            affected_metrics=affected_metrics,
            description=f"{resource_type.title()} exhaustion for {duration_minutes} minutes",
            recovery_time_minutes=15
        )
    
    def create_memory_leak_pattern(self,
                                 start_time: datetime,
                                 duration_minutes: int = 120) -> AnomalyPattern:
        """
        创建内存泄漏异常模式（渐进式增长）
        
        Args:
            start_time: 异常开始时间
            duration_minutes: 持续时间（分钟）
            
        Returns:
            异常模式对象
        """
        return AnomalyPattern(
            anomaly_type=AnomalyType.MEMORY_LEAK,
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity_multiplier=1.8,
            affected_metrics=["system_memory_usage_percent"],
            description=f"Memory leak causing gradual memory increase over {duration_minutes} minutes",
            recovery_time_minutes=20
        )
    
    def create_database_slowdown_pattern(self,
                                       start_time: datetime,
                                       duration_minutes: int = 25,
                                       slowdown_factor: float = 8.0) -> AnomalyPattern:
        """
        创建数据库慢查询异常模式
        
        Args:
            start_time: 异常开始时间
            duration_minutes: 持续时间（分钟）
            slowdown_factor: 慢查询倍数
            
        Returns:
            异常模式对象
        """
        return AnomalyPattern(
            anomaly_type=AnomalyType.DATABASE_SLOWDOWN,
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity_multiplier=slowdown_factor,
            affected_metrics=[
                "db_query_duration_ms",
                "db_active_connections",
                "db_lock_wait_time_ms"
            ],
            description=f"Database slowdown with {slowdown_factor}x query time for {duration_minutes} minutes",
            recovery_time_minutes=8
        )
    
    def create_cascading_failure_pattern(self,
                                       start_time: datetime,
                                       duration_minutes: int = 40) -> AnomalyPattern:
        """
        创建级联故障异常模式
        
        Args:
            start_time: 异常开始时间
            duration_minutes: 持续时间（分钟）
            
        Returns:
            异常模式对象
        """
        return AnomalyPattern(
            anomaly_type=AnomalyType.CASCADING_FAILURE,
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity_multiplier=4.0,
            affected_metrics=[
                "http_request_duration_ms",
                "http_error_rate",
                "db_query_duration_ms",
                "system_cpu_usage_percent",
                "system_memory_usage_percent"
            ],
            description=f"Cascading failure affecting multiple systems for {duration_minutes} minutes",
            recovery_time_minutes=25
        )
    
    def create_periodic_anomaly_pattern(self,
                                      start_time: datetime,
                                      duration_minutes: int = 180,
                                      cycle_minutes: int = 30) -> AnomalyPattern:
        """
        创建周期性异常模式
        
        Args:
            start_time: 异常开始时间
            duration_minutes: 总持续时间（分钟）
            cycle_minutes: 周期长度（分钟）
            
        Returns:
            异常模式对象
        """
        return AnomalyPattern(
            anomaly_type=AnomalyType.PERIODIC_ANOMALY,
            start_time=start_time,
            duration_minutes=duration_minutes,
            severity_multiplier=2.5,
            affected_metrics=[
                "http_request_duration_ms",
                "system_cpu_usage_percent"
            ],
            description=f"Periodic anomaly with {cycle_minutes}-minute cycles over {duration_minutes} minutes",
            recovery_time_minutes=5
        )
    
    def apply_anomaly_to_value(self, 
                              base_value: float,
                              metric_name: str,
                              timestamp: datetime,
                              pattern: AnomalyPattern) -> float:
        """
        将异常模式应用到指标值上
        
        Args:
            base_value: 基础值
            metric_name: 指标名称
            timestamp: 时间戳
            pattern: 异常模式
            
        Returns:
            应用异常后的值
        """
        if metric_name not in pattern.affected_metrics:
            return base_value
        
        # 检查是否在异常时间范围内
        anomaly_end = pattern.start_time + timedelta(minutes=pattern.duration_minutes)
        if not (pattern.start_time <= timestamp <= anomaly_end):
            return base_value
        
        # 计算异常进度（0-1）
        elapsed = (timestamp - pattern.start_time).total_seconds()
        total_duration = pattern.duration_minutes * 60
        progress = elapsed / total_duration
        
        # 根据异常类型应用不同的变化模式
        if pattern.anomaly_type == AnomalyType.MEMORY_LEAK:
            # 内存泄漏：线性增长
            multiplier = 1.0 + (pattern.severity_multiplier - 1.0) * progress
        
        elif pattern.anomaly_type == AnomalyType.PERIODIC_ANOMALY:
            # 周期性异常：正弦波模式
            cycle_seconds = 30 * 60  # 30分钟周期
            sine_value = math.sin(2 * math.pi * elapsed / cycle_seconds)
            multiplier = 1.0 + (pattern.severity_multiplier - 1.0) * max(0, sine_value)
        
        elif pattern.anomaly_type == AnomalyType.GRADUAL_DEGRADATION:
            # 渐进式下降：指数增长
            multiplier = 1.0 + (pattern.severity_multiplier - 1.0) * (1 - math.exp(-3 * progress))
        
        elif pattern.anomaly_type == AnomalyType.CASCADING_FAILURE:
            # 级联故障：阶梯式增长
            if progress < 0.2:
                multiplier = 1.5
            elif progress < 0.4:
                multiplier = 2.0
            elif progress < 0.7:
                multiplier = 3.0
            else:
                multiplier = pattern.severity_multiplier
        
        else:
            # 其他异常类型：使用钟形曲线
            # 在异常中期达到峰值，开始和结束时影响较小
            bell_curve = math.exp(-((progress - 0.5) * 4) ** 2)
            multiplier = 1.0 + (pattern.severity_multiplier - 1.0) * bell_curve
        
        # 对于错误率指标，使用加法而不是乘法
        if "error_rate" in metric_name:
            return min(1.0, base_value + (pattern.severity_multiplier - 1.0) * 0.05 * bell_curve)
        
        # 对于吞吐量指标，异常时应该降低
        if "requests_per_second" in metric_name:
            return base_value / multiplier
        
        # 对于其他指标，直接乘以倍数
        return base_value * multiplier
    
    def generate_anomaly_scenario(self, 
                                scenario_name: str,
                                base_time: datetime,
                                duration_hours: int = 6) -> List[AnomalyPattern]:
        """
        生成预定义的异常场景
        
        Args:
            scenario_name: 场景名称
            base_time: 基准时间
            duration_hours: 场景持续时间（小时）
            
        Returns:
            异常模式列表
        """
        patterns = []
        
        if scenario_name == "morning_rush_failure":
            # 早高峰故障场景
            patterns.extend([
                self.create_performance_degradation_pattern(
                    base_time + timedelta(hours=1), 45, 2.5
                ),
                self.create_database_slowdown_pattern(
                    base_time + timedelta(hours=1, minutes=15), 30, 6.0
                ),
                self.create_error_spike_pattern(
                    base_time + timedelta(hours=1, minutes=30), 20, 15.0
                )
            ])
        
        elif scenario_name == "resource_exhaustion_cascade":
            # 资源耗尽级联故障
            patterns.extend([
                self.create_resource_exhaustion_pattern(
                    base_time + timedelta(minutes=30), "memory", 60
                ),
                self.create_resource_exhaustion_pattern(
                    base_time + timedelta(hours=1), "cpu", 45
                ),
                self.create_cascading_failure_pattern(
                    base_time + timedelta(hours=1, minutes=30), 40
                )
            ])
        
        elif scenario_name == "gradual_system_degradation":
            # 渐进式系统性能下降
            patterns.extend([
                self.create_memory_leak_pattern(
                    base_time + timedelta(minutes=15), 180
                ),
                self.create_performance_degradation_pattern(
                    base_time + timedelta(hours=2), 90, 1.8
                ),
                self.create_database_slowdown_pattern(
                    base_time + timedelta(hours=3), 60, 4.0
                )
            ])
        
        elif scenario_name == "periodic_instability":
            # 周期性不稳定
            patterns.extend([
                self.create_periodic_anomaly_pattern(
                    base_time + timedelta(minutes=30), 300, 20
                ),
                self.create_error_spike_pattern(
                    base_time + timedelta(hours=2), 15, 25.0
                ),
                self.create_error_spike_pattern(
                    base_time + timedelta(hours=4), 15, 25.0
                )
            ])
        
        elif scenario_name == "database_crisis":
            # 数据库危机场景
            patterns.extend([
                self.create_database_slowdown_pattern(
                    base_time + timedelta(minutes=45), 40, 10.0
                ),
                self.create_resource_exhaustion_pattern(
                    base_time + timedelta(hours=1, minutes=15), "memory", 50
                ),
                self.create_cascading_failure_pattern(
                    base_time + timedelta(hours=2), 35
                )
            ])
        
        else:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        return patterns
    
    def get_available_scenarios(self) -> List[str]:
        """
        获取可用的异常场景列表
        
        Returns:
            场景名称列表
        """
        return [
            "morning_rush_failure",
            "resource_exhaustion_cascade", 
            "gradual_system_degradation",
            "periodic_instability",
            "database_crisis"
        ]
    
    def export_anomaly_timeline(self, patterns: List[AnomalyPattern]) -> Dict[str, Any]:
        """
        导出异常时间线
        
        Args:
            patterns: 异常模式列表
            
        Returns:
            异常时间线字典
        """
        timeline = {
            "scenario_summary": {
                "total_patterns": len(patterns),
                "start_time": min(p.start_time for p in patterns).isoformat(),
                "end_time": max(p.start_time + timedelta(minutes=p.duration_minutes) 
                               for p in patterns).isoformat()
            },
            "anomaly_patterns": []
        }
        
        for i, pattern in enumerate(patterns):
            timeline["anomaly_patterns"].append({
                "id": i + 1,
                "type": pattern.anomaly_type.value,
                "start_time": pattern.start_time.isoformat(),
                "end_time": (pattern.start_time + timedelta(minutes=pattern.duration_minutes)).isoformat(),
                "duration_minutes": pattern.duration_minutes,
                "severity_multiplier": pattern.severity_multiplier,
                "affected_metrics": pattern.affected_metrics,
                "description": pattern.description,
                "recovery_time_minutes": pattern.recovery_time_minutes
            })
        
        return timeline


if __name__ == "__main__":
    # 示例用法
    simulator = AnomalySimulator()
    
    print("可用的异常场景:")
    for scenario in simulator.get_available_scenarios():
        print(f"  - {scenario}")
    
    # 生成早高峰故障场景
    base_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    patterns = simulator.generate_anomaly_scenario("morning_rush_failure", base_time)
    
    print(f"\n生成了 {len(patterns)} 个异常模式")
    
    # 导出时间线
    timeline = simulator.export_anomaly_timeline(patterns)
    
    with open("anomaly_timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2, ensure_ascii=False)
    
    print("异常时间线已保存到 anomaly_timeline.json")