#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测模拟器
模拟各种异常检测场景，包括时间序列异常、统计异常、模式异常等
用于AIOps测试场景
"""

import argparse
import json
import random
import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import os
from enum import Enum
from dataclasses import dataclass

class AnomalyType(Enum):
    """异常类型枚举"""
    SPIKE = "spike"  # 尖峰异常
    DIP = "dip"  # 下降异常
    TREND = "trend"  # 趋势异常
    SEASONAL = "seasonal"  # 季节性异常
    OUTLIER = "outlier"  # 离群点异常
    PATTERN = "pattern"  # 模式异常
    DRIFT = "drift"  # 漂移异常
    NOISE = "noise"  # 噪声异常

class Severity(Enum):
    """异常严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AnomalyEvent:
    """异常事件数据类"""
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: Severity
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_score: float
    confidence: float
    description: str
    context: Dict[str, Any]

class AnomalyDetector:
    """异常检测模拟器"""
    
    def __init__(self, duration: int = 300, detection_interval: int = 30):
        """
        初始化异常检测器
        
        Args:
            duration: 模拟运行时长(秒)
            detection_interval: 检测间隔(秒)
        """
        self.duration = duration
        self.detection_interval = detection_interval
        self.start_time = datetime.now()
        self.anomalies = []
        self.metrics_history = []
        self.running = False
        
        # 基线配置
        self.baselines = {
            'cpu_usage': {'mean': 45.0, 'std': 15.0, 'min': 0, 'max': 100},
            'memory_usage': {'mean': 65.0, 'std': 20.0, 'min': 0, 'max': 100},
            'disk_usage': {'mean': 70.0, 'std': 10.0, 'min': 0, 'max': 100},
            'network_throughput': {'mean': 500.0, 'std': 200.0, 'min': 0, 'max': 2000},
            'response_time': {'mean': 150.0, 'std': 50.0, 'min': 0, 'max': 5000},
            'error_rate': {'mean': 2.0, 'std': 1.5, 'min': 0, 'max': 100},
            'transaction_count': {'mean': 1000.0, 'std': 300.0, 'min': 0, 'max': 5000}
        }
        
        # 异常检测阈值
        self.thresholds = {
            'z_score': 2.5,  # Z-score阈值
            'iqr_multiplier': 1.5,  # IQR倍数
            'percentage_change': 50.0,  # 百分比变化阈值
            'confidence_threshold': 0.8  # 置信度阈值
        }
    
    def generate_normal_metrics(self) -> Dict[str, float]:
        """
        生成正常的指标数据
        
        Returns:
            正常指标数据字典
        """
        metrics = {}
        current_time = datetime.now()
        
        for metric_name, baseline in self.baselines.items():
            # 基础值
            base_value = np.random.normal(baseline['mean'], baseline['std'])
            
            # 添加时间相关的周期性变化
            hour = current_time.hour
            if metric_name in ['cpu_usage', 'memory_usage', 'transaction_count']:
                # 工作时间负载更高
                if 9 <= hour <= 17:
                    base_value *= random.uniform(1.2, 1.5)
                elif 18 <= hour <= 22:
                    base_value *= random.uniform(1.0, 1.2)
                else:
                    base_value *= random.uniform(0.7, 1.0)
            
            # 添加随机噪声
            noise = np.random.normal(0, baseline['std'] * 0.1)
            value = base_value + noise
            
            # 确保值在合理范围内
            value = max(baseline['min'], min(baseline['max'], value))
            metrics[metric_name] = round(value, 2)
        
        return metrics
    
    def inject_anomaly(self, metrics: Dict[str, float], anomaly_type: AnomalyType) -> Dict[str, float]:
        """
        向指标数据中注入异常
        
        Args:
            metrics: 原始指标数据
            anomaly_type: 异常类型
            
        Returns:
            包含异常的指标数据
        """
        anomalous_metrics = metrics.copy()
        metric_name = random.choice(list(metrics.keys()))
        baseline = self.baselines[metric_name]
        original_value = metrics[metric_name]
        
        if anomaly_type == AnomalyType.SPIKE:
            # 尖峰异常：值突然增大
            multiplier = random.uniform(2.0, 5.0)
            anomalous_value = min(baseline['max'], original_value * multiplier)
            
        elif anomaly_type == AnomalyType.DIP:
            # 下降异常：值突然减小
            multiplier = random.uniform(0.1, 0.5)
            anomalous_value = max(baseline['min'], original_value * multiplier)
            
        elif anomaly_type == AnomalyType.OUTLIER:
            # 离群点异常：远离正常范围的值
            if random.random() < 0.5:
                anomalous_value = baseline['mean'] + baseline['std'] * random.uniform(4, 6)
            else:
                anomalous_value = baseline['mean'] - baseline['std'] * random.uniform(4, 6)
            anomalous_value = max(baseline['min'], min(baseline['max'], anomalous_value))
            
        elif anomaly_type == AnomalyType.TREND:
            # 趋势异常：持续上升或下降
            trend_direction = random.choice([1, -1])
            trend_magnitude = random.uniform(0.1, 0.3)
            anomalous_value = original_value * (1 + trend_direction * trend_magnitude)
            anomalous_value = max(baseline['min'], min(baseline['max'], anomalous_value))
            
        elif anomaly_type == AnomalyType.DRIFT:
            # 漂移异常：基线缓慢变化
            drift_amount = random.uniform(0.05, 0.15) * baseline['mean']
            drift_direction = random.choice([1, -1])
            anomalous_value = original_value + drift_direction * drift_amount
            anomalous_value = max(baseline['min'], min(baseline['max'], anomalous_value))
            
        else:
            # 默认为噪声异常
            noise_multiplier = random.uniform(2, 4)
            noise = np.random.normal(0, baseline['std'] * noise_multiplier)
            anomalous_value = original_value + noise
            anomalous_value = max(baseline['min'], min(baseline['max'], anomalous_value))
        
        anomalous_metrics[metric_name] = round(anomalous_value, 2)
        return anomalous_metrics, metric_name, original_value, anomalous_value
    
    def calculate_z_score(self, value: float, metric_name: str) -> float:
        """
        计算Z-score
        
        Args:
            value: 当前值
            metric_name: 指标名称
            
        Returns:
            Z-score值
        """
        baseline = self.baselines[metric_name]
        return abs(value - baseline['mean']) / baseline['std']
    
    def calculate_deviation_score(self, expected: float, actual: float) -> float:
        """
        计算偏差分数
        
        Args:
            expected: 期望值
            actual: 实际值
            
        Returns:
            偏差分数 (0-100)
        """
        if expected == 0:
            return 100.0 if actual != 0 else 0.0
        
        deviation = abs(actual - expected) / expected * 100
        return min(100.0, deviation)
    
    def detect_anomalies(self, metrics: Dict[str, float]) -> List[AnomalyEvent]:
        """
        检测指标中的异常
        
        Args:
            metrics: 指标数据
            
        Returns:
            检测到的异常事件列表
        """
        anomalies = []
        current_time = datetime.now()
        
        for metric_name, value in metrics.items():
            baseline = self.baselines[metric_name]
            expected_value = baseline['mean']
            
            # Z-score检测
            z_score = self.calculate_z_score(value, metric_name)
            
            if z_score > self.thresholds['z_score']:
                # 确定异常类型
                if value > expected_value * 2:
                    anomaly_type = AnomalyType.SPIKE
                elif value < expected_value * 0.5:
                    anomaly_type = AnomalyType.DIP
                else:
                    anomaly_type = AnomalyType.OUTLIER
                
                # 确定严重程度
                if z_score > 4:
                    severity = Severity.CRITICAL
                elif z_score > 3:
                    severity = Severity.HIGH
                elif z_score > 2.5:
                    severity = Severity.MEDIUM
                else:
                    severity = Severity.LOW
                
                # 计算置信度
                confidence = min(1.0, z_score / 5.0)
                
                # 计算偏差分数
                deviation_score = self.calculate_deviation_score(expected_value, value)
                
                # 创建异常事件
                anomaly = AnomalyEvent(
                    timestamp=current_time,
                    anomaly_type=anomaly_type,
                    severity=severity,
                    metric_name=metric_name,
                    expected_value=expected_value,
                    actual_value=value,
                    deviation_score=deviation_score,
                    confidence=confidence,
                    description=f"{metric_name}异常: 期望值{expected_value:.2f}, 实际值{value:.2f}, Z-score: {z_score:.2f}",
                    context={
                        'z_score': z_score,
                        'baseline_mean': baseline['mean'],
                        'baseline_std': baseline['std'],
                        'detection_method': 'z_score'
                    }
                )
                
                anomalies.append(anomaly)
        
        return anomalies
    
    def generate_anomaly_patterns(self) -> List[Dict[str, Any]]:
        """
        生成异常模式数据
        
        Returns:
            异常模式列表
        """
        patterns = []
        
        # 模式1: 连锁反应异常
        if random.random() < 0.3:
            patterns.append({
                'type': 'cascade_failure',
                'description': '连锁故障模式',
                'affected_metrics': ['cpu_usage', 'memory_usage', 'response_time'],
                'duration': random.randint(60, 300),
                'severity': random.choice(['medium', 'high', 'critical'])
            })
        
        # 模式2: 周期性异常
        if random.random() < 0.2:
            patterns.append({
                'type': 'periodic_anomaly',
                'description': '周期性异常模式',
                'period': random.choice([60, 300, 900]),  # 1分钟、5分钟、15分钟
                'affected_metrics': [random.choice(list(self.baselines.keys()))],
                'amplitude': random.uniform(1.5, 3.0)
            })
        
        # 模式3: 渐进式异常
        if random.random() < 0.25:
            patterns.append({
                'type': 'gradual_degradation',
                'description': '渐进式性能下降',
                'affected_metrics': ['response_time', 'error_rate'],
                'degradation_rate': random.uniform(0.01, 0.05),
                'duration': random.randint(300, 1800)
            })
        
        return patterns
    
    def simulate_real_world_scenarios(self) -> Dict[str, Any]:
        """
        模拟真实世界的异常场景
        
        Returns:
            场景信息字典
        """
        scenarios = [
            {
                'name': 'memory_leak',
                'description': '内存泄漏导致系统性能下降',
                'affected_metrics': {'memory_usage': 'increasing', 'response_time': 'increasing'},
                'duration': random.randint(600, 1800),
                'probability': 0.15
            },
            {
                'name': 'ddos_attack',
                'description': 'DDoS攻击导致网络拥塞',
                'affected_metrics': {'network_throughput': 'spike', 'response_time': 'spike', 'error_rate': 'spike'},
                'duration': random.randint(300, 900),
                'probability': 0.1
            },
            {
                'name': 'database_slowdown',
                'description': '数据库查询性能下降',
                'affected_metrics': {'response_time': 'increasing', 'cpu_usage': 'increasing'},
                'duration': random.randint(180, 600),
                'probability': 0.2
            },
            {
                'name': 'cache_miss_storm',
                'description': '缓存失效导致的性能问题',
                'affected_metrics': {'response_time': 'spike', 'cpu_usage': 'spike', 'transaction_count': 'decreasing'},
                'duration': random.randint(120, 300),
                'probability': 0.12
            },
            {
                'name': 'disk_io_bottleneck',
                'description': '磁盘I/O瓶颈',
                'affected_metrics': {'disk_usage': 'spike', 'response_time': 'increasing'},
                'duration': random.randint(240, 720),
                'probability': 0.18
            }
        ]
        
        active_scenarios = []
        for scenario in scenarios:
            if random.random() < scenario['probability']:
                active_scenarios.append(scenario)
        
        return {
            'active_scenarios': active_scenarios,
            'scenario_count': len(active_scenarios)
        }
    
    def run_detection(self, export_file: str = None, inject_anomalies: bool = True):
        """
        运行异常检测模拟
        
        Args:
            export_file: 导出文件路径
            inject_anomalies: 是否注入异常
        """
        print(f"🔍 启动异常检测模拟器")
        print(f"模拟时长: {self.duration}秒")
        print(f"检测间隔: {self.detection_interval}秒")
        print(f"异常注入: {'启用' if inject_anomalies else '禁用'}")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.running = True
        end_time = self.start_time + timedelta(seconds=self.duration)
        
        # 生成异常模式
        patterns = self.generate_anomaly_patterns()
        scenarios = self.simulate_real_world_scenarios()
        
        print(f"生成异常模式: {len(patterns)}个")
        print(f"激活场景: {scenarios['scenario_count']}个")
        
        try:
            while datetime.now() < end_time and self.running:
                # 生成指标数据
                metrics = self.generate_normal_metrics()
                
                # 可能注入异常
                injected_anomaly = None
                if inject_anomalies and random.random() < 0.2:  # 20%概率注入异常
                    anomaly_type = random.choice(list(AnomalyType))
                    metrics, affected_metric, original_value, anomalous_value = self.inject_anomaly(metrics, anomaly_type)
                    injected_anomaly = {
                        'type': anomaly_type.value,
                        'metric': affected_metric,
                        'original_value': original_value,
                        'anomalous_value': anomalous_value
                    }
                
                # 检测异常
                detected_anomalies = self.detect_anomalies(metrics)
                
                # 记录数据
                data_point = {
                    'timestamp': datetime.now().isoformat(),
                    'metrics': metrics,
                    'detected_anomalies': [
                        {
                            'type': anomaly.anomaly_type.value,
                            'severity': anomaly.severity.value,
                            'metric_name': anomaly.metric_name,
                            'expected_value': anomaly.expected_value,
                            'actual_value': anomaly.actual_value,
                            'deviation_score': anomaly.deviation_score,
                            'confidence': anomaly.confidence,
                            'description': anomaly.description,
                            'context': anomaly.context
                        } for anomaly in detected_anomalies
                    ],
                    'injected_anomaly': injected_anomaly
                }
                
                self.metrics_history.append(data_point)
                self.anomalies.extend(detected_anomalies)
                
                # 显示实时信息
                anomaly_count = len(detected_anomalies)
                if anomaly_count > 0:
                    severity_counts = {}
                    for anomaly in detected_anomalies:
                        severity = anomaly.severity.value
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    severity_str = ", ".join([f"{k}: {v}" for k, v in severity_counts.items()])
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"检测到 {anomaly_count} 个异常 ({severity_str})")
                    
                    if injected_anomaly:
                        print(f"  ↳ 注入异常: {injected_anomaly['type']} in {injected_anomaly['metric']}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 系统正常")
                
                time.sleep(self.detection_interval)
                
        except KeyboardInterrupt:
            print("\n检测被用户中断")
            self.running = False
        
        print(f"\n✅ 异常检测完成")
        print(f"总数据点: {len(self.metrics_history)}")
        print(f"检测到异常: {len(self.anomalies)}")
        
        # 统计异常类型
        anomaly_stats = {}
        severity_stats = {}
        for anomaly in self.anomalies:
            anomaly_type = anomaly.anomaly_type.value
            severity = anomaly.severity.value
            anomaly_stats[anomaly_type] = anomaly_stats.get(anomaly_type, 0) + 1
            severity_stats[severity] = severity_stats.get(severity, 0) + 1
        
        print("\n📊 异常统计:")
        for anomaly_type, count in anomaly_stats.items():
            print(f"  {anomaly_type}: {count}")
        
        print("\n⚠️  严重程度统计:")
        for severity, count in severity_stats.items():
            print(f"  {severity}: {count}")
        
        # 导出数据
        if export_file:
            self.export_results(export_file, patterns, scenarios)
    
    def export_results(self, filename: str, patterns: List[Dict], scenarios: Dict):
        """
        导出检测结果到JSON文件
        
        Args:
            filename: 导出文件名
            patterns: 异常模式
            scenarios: 场景信息
        """
        export_data = {
            'simulation_info': {
                'type': 'anomaly_detection',
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': self.duration,
                'detection_interval': self.detection_interval,
                'data_points': len(self.metrics_history),
                'total_anomalies': len(self.anomalies)
            },
            'configuration': {
                'baselines': self.baselines,
                'thresholds': self.thresholds
            },
            'patterns': patterns,
            'scenarios': scenarios,
            'metrics_history': self.metrics_history,
            'summary': {
                'anomaly_types': {},
                'severity_distribution': {},
                'affected_metrics': {}
            }
        }
        
        # 生成汇总统计
        for anomaly in self.anomalies:
            anomaly_type = anomaly.anomaly_type.value
            severity = anomaly.severity.value
            metric_name = anomaly.metric_name
            
            export_data['summary']['anomaly_types'][anomaly_type] = \
                export_data['summary']['anomaly_types'].get(anomaly_type, 0) + 1
            export_data['summary']['severity_distribution'][severity] = \
                export_data['summary']['severity_distribution'].get(severity, 0) + 1
            export_data['summary']['affected_metrics'][metric_name] = \
                export_data['summary']['affected_metrics'].get(metric_name, 0) + 1
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 异常检测结果已导出到: {filename}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='异常检测模拟器')
    parser.add_argument('--duration', type=int, default=300, help='检测时长(秒)')
    parser.add_argument('--interval', type=int, default=30, help='检测间隔(秒)')
    parser.add_argument('--export', type=str, help='导出文件路径')
    parser.add_argument('--no-inject', action='store_true', help='禁用异常注入')
    
    args = parser.parse_args()
    
    detector = AnomalyDetector(duration=args.duration, detection_interval=args.interval)
    detector.run_detection(export_file=args.export, inject_anomalies=not args.no_inject)

if __name__ == '__main__':
    main()