#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试场景生成器

该模块提供了各种业务场景的数据生成和模拟功能，用于测试AIOps平台的各个组件。
包括Web应用监控、数据库性能监控、系统资源监控等场景。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import psutil
from dataclasses import dataclass
from enum import Enum


class ScenarioType(Enum):
    """场景类型枚举"""
    WEB_APPLICATION = "web_application"
    DATABASE_PERFORMANCE = "database_performance"
    SYSTEM_METRICS = "system_metrics"
    NETWORK_MONITORING = "network_monitoring"
    APPLICATION_LOGS = "application_logs"
    SECURITY_EVENTS = "security_events"


class SeverityLevel(Enum):
    """严重程度枚举"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MetricData:
    """指标数据结构"""
    timestamp: datetime
    metric_name: str
    value: float
    labels: Dict[str, str]
    scenario_type: ScenarioType
    severity: SeverityLevel = SeverityLevel.INFO


class ScenarioGenerator:
    """场景生成器主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化场景生成器
        
        Args:
            config: 配置字典，包含各种场景的参数设置
        """
        self.config = config or self._get_default_config()
        self.running_scenarios = {}
        self.generated_data = []
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "web_application": {
                "base_response_time": 200,  # ms
                "base_throughput": 100,     # requests/sec
                "error_rate": 0.01,         # 1%
                "anomaly_probability": 0.05  # 5%
            },
            "database": {
                "base_query_time": 50,      # ms
                "base_connections": 20,
                "max_connections": 100,
                "deadlock_probability": 0.001
            },
            "system": {
                "cpu_base": 30,             # %
                "memory_base": 60,          # %
                "disk_base": 40,            # %
                "network_base": 1024        # KB/s
            },
            "intervals": {
                "metrics_interval": 5,      # seconds
                "logs_interval": 1,         # seconds
                "anomaly_duration": 300     # seconds
            }
        }
    
    def generate_web_application_metrics(self, duration_minutes: int = 60) -> List[MetricData]:
        """
        生成Web应用程序监控指标
        
        Args:
            duration_minutes: 生成数据的时长（分钟）
            
        Returns:
            生成的指标数据列表
        """
        metrics = []
        config = self.config["web_application"]
        start_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        # 模拟不同的服务端点
        endpoints = ["/api/users", "/api/orders", "/api/products", "/api/auth", "/api/dashboard"]
        
        for i in range(duration_minutes * 12):  # 每5秒一个数据点
            timestamp = start_time + timedelta(seconds=i * 5)
            
            # 模拟业务高峰期（9-11点，14-16点，19-21点）
            hour = timestamp.hour
            is_peak = (9 <= hour <= 11) or (14 <= hour <= 16) or (19 <= hour <= 21)
            peak_multiplier = 2.5 if is_peak else 1.0
            
            # 模拟异常情况
            is_anomaly = random.random() < config["anomaly_probability"]
            anomaly_multiplier = random.uniform(3, 8) if is_anomaly else 1.0
            
            for endpoint in endpoints:
                # 响应时间指标
                base_rt = config["base_response_time"]
                response_time = base_rt * peak_multiplier * anomaly_multiplier
                response_time += random.gauss(0, base_rt * 0.2)  # 添加噪声
                response_time = max(1, response_time)  # 确保非负
                
                severity = SeverityLevel.CRITICAL if response_time > 2000 else \
                          SeverityLevel.ERROR if response_time > 1000 else \
                          SeverityLevel.WARNING if response_time > 500 else \
                          SeverityLevel.INFO
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="http_request_duration_ms",
                    value=response_time,
                    labels={"endpoint": endpoint, "method": "GET", "status": "200"},
                    scenario_type=ScenarioType.WEB_APPLICATION,
                    severity=severity
                ))
                
                # 吞吐量指标
                base_throughput = config["base_throughput"]
                throughput = base_throughput * peak_multiplier
                if is_anomaly:
                    throughput *= random.uniform(0.1, 0.5)  # 异常时吞吐量下降
                throughput += random.gauss(0, base_throughput * 0.1)
                throughput = max(0, throughput)
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="http_requests_per_second",
                    value=throughput,
                    labels={"endpoint": endpoint},
                    scenario_type=ScenarioType.WEB_APPLICATION,
                    severity=SeverityLevel.WARNING if throughput < base_throughput * 0.5 else SeverityLevel.INFO
                ))
                
                # 错误率指标
                error_rate = config["error_rate"]
                if is_anomaly:
                    error_rate *= random.uniform(10, 50)  # 异常时错误率激增
                error_rate = min(1.0, error_rate)
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="http_error_rate",
                    value=error_rate,
                    labels={"endpoint": endpoint},
                    scenario_type=ScenarioType.WEB_APPLICATION,
                    severity=SeverityLevel.CRITICAL if error_rate > 0.1 else \
                            SeverityLevel.ERROR if error_rate > 0.05 else \
                            SeverityLevel.WARNING if error_rate > 0.02 else \
                            SeverityLevel.INFO
                ))
        
        return metrics
    
    def generate_database_metrics(self, duration_minutes: int = 60) -> List[MetricData]:
        """
        生成数据库性能监控指标
        
        Args:
            duration_minutes: 生成数据的时长（分钟）
            
        Returns:
            生成的指标数据列表
        """
        metrics = []
        config = self.config["database"]
        start_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        databases = ["users_db", "orders_db", "products_db", "analytics_db"]
        
        for i in range(duration_minutes * 12):  # 每5秒一个数据点
            timestamp = start_time + timedelta(seconds=i * 5)
            
            # 模拟数据库负载变化
            hour = timestamp.hour
            is_heavy_load = (8 <= hour <= 10) or (13 <= hour <= 15) or (20 <= hour <= 22)
            load_multiplier = 3.0 if is_heavy_load else 1.0
            
            # 模拟数据库异常
            is_db_anomaly = random.random() < 0.02  # 2%概率
            
            for db_name in databases:
                # 查询响应时间
                base_query_time = config["base_query_time"]
                query_time = base_query_time * load_multiplier
                if is_db_anomaly:
                    query_time *= random.uniform(5, 20)  # 异常时查询时间激增
                query_time += random.gauss(0, base_query_time * 0.3)
                query_time = max(1, query_time)
                
                severity = SeverityLevel.CRITICAL if query_time > 5000 else \
                          SeverityLevel.ERROR if query_time > 2000 else \
                          SeverityLevel.WARNING if query_time > 500 else \
                          SeverityLevel.INFO
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="db_query_duration_ms",
                    value=query_time,
                    labels={"database": db_name, "query_type": "SELECT"},
                    scenario_type=ScenarioType.DATABASE_PERFORMANCE,
                    severity=severity
                ))
                
                # 数据库连接数
                base_connections = config["base_connections"]
                connections = base_connections * load_multiplier
                if is_db_anomaly:
                    connections = min(config["max_connections"], connections * random.uniform(2, 4))
                connections += random.gauss(0, base_connections * 0.2)
                connections = max(0, min(config["max_connections"], connections))
                
                connection_ratio = connections / config["max_connections"]
                severity = SeverityLevel.CRITICAL if connection_ratio > 0.9 else \
                          SeverityLevel.ERROR if connection_ratio > 0.8 else \
                          SeverityLevel.WARNING if connection_ratio > 0.7 else \
                          SeverityLevel.INFO
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="db_active_connections",
                    value=connections,
                    labels={"database": db_name},
                    scenario_type=ScenarioType.DATABASE_PERFORMANCE,
                    severity=severity
                ))
                
                # 数据库锁等待时间
                lock_wait_time = 0
                if random.random() < config["deadlock_probability"]:
                    lock_wait_time = random.uniform(1000, 10000)  # 1-10秒
                
                if lock_wait_time > 0:
                    metrics.append(MetricData(
                        timestamp=timestamp,
                        metric_name="db_lock_wait_time_ms",
                        value=lock_wait_time,
                        labels={"database": db_name},
                        scenario_type=ScenarioType.DATABASE_PERFORMANCE,
                        severity=SeverityLevel.ERROR if lock_wait_time > 5000 else SeverityLevel.WARNING
                    ))
        
        return metrics
    
    def generate_system_metrics(self, duration_minutes: int = 60) -> List[MetricData]:
        """
        生成系统资源监控指标
        
        Args:
            duration_minutes: 生成数据的时长（分钟）
            
        Returns:
            生成的指标数据列表
        """
        metrics = []
        config = self.config["system"]
        start_time = datetime.now() - timedelta(minutes=duration_minutes)
        
        servers = ["web-server-01", "web-server-02", "db-server-01", "cache-server-01"]
        
        for i in range(duration_minutes * 12):  # 每5秒一个数据点
            timestamp = start_time + timedelta(seconds=i * 5)
            
            # 模拟系统负载变化
            hour = timestamp.hour
            is_busy = (9 <= hour <= 11) or (14 <= hour <= 17) or (20 <= hour <= 22)
            load_factor = 1.8 if is_busy else 1.0
            
            # 模拟系统异常
            is_system_anomaly = random.random() < 0.03  # 3%概率
            
            for server in servers:
                # CPU使用率
                base_cpu = config["cpu_base"]
                cpu_usage = base_cpu * load_factor
                if is_system_anomaly:
                    cpu_usage = min(100, cpu_usage * random.uniform(2, 4))
                cpu_usage += random.gauss(0, base_cpu * 0.15)
                cpu_usage = max(0, min(100, cpu_usage))
                
                severity = SeverityLevel.CRITICAL if cpu_usage > 90 else \
                          SeverityLevel.ERROR if cpu_usage > 80 else \
                          SeverityLevel.WARNING if cpu_usage > 70 else \
                          SeverityLevel.INFO
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="system_cpu_usage_percent",
                    value=cpu_usage,
                    labels={"server": server, "core": "total"},
                    scenario_type=ScenarioType.SYSTEM_METRICS,
                    severity=severity
                ))
                
                # 内存使用率
                base_memory = config["memory_base"]
                memory_usage = base_memory * load_factor
                if is_system_anomaly:
                    memory_usage = min(100, memory_usage * random.uniform(1.5, 3))
                memory_usage += random.gauss(0, base_memory * 0.1)
                memory_usage = max(0, min(100, memory_usage))
                
                severity = SeverityLevel.CRITICAL if memory_usage > 95 else \
                          SeverityLevel.ERROR if memory_usage > 85 else \
                          SeverityLevel.WARNING if memory_usage > 75 else \
                          SeverityLevel.INFO
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="system_memory_usage_percent",
                    value=memory_usage,
                    labels={"server": server},
                    scenario_type=ScenarioType.SYSTEM_METRICS,
                    severity=severity
                ))
                
                # 磁盘I/O
                base_disk_io = 50  # MB/s
                disk_io = base_disk_io * load_factor
                if is_system_anomaly:
                    disk_io *= random.uniform(3, 10)
                disk_io += random.gauss(0, base_disk_io * 0.2)
                disk_io = max(0, disk_io)
                
                metrics.append(MetricData(
                    timestamp=timestamp,
                    metric_name="system_disk_io_mbps",
                    value=disk_io,
                    labels={"server": server, "device": "/dev/sda1"},
                    scenario_type=ScenarioType.SYSTEM_METRICS,
                    severity=SeverityLevel.WARNING if disk_io > 200 else SeverityLevel.INFO
                ))
                
                # 网络流量
                base_network = config["network_base"]
                network_in = base_network * load_factor * random.uniform(0.8, 1.2)
                network_out = base_network * load_factor * random.uniform(0.6, 1.0)
                
                metrics.extend([
                    MetricData(
                        timestamp=timestamp,
                        metric_name="system_network_bytes_in",
                        value=network_in * 1024,  # 转换为bytes
                        labels={"server": server, "interface": "eth0"},
                        scenario_type=ScenarioType.SYSTEM_METRICS,
                        severity=SeverityLevel.INFO
                    ),
                    MetricData(
                        timestamp=timestamp,
                        metric_name="system_network_bytes_out",
                        value=network_out * 1024,
                        labels={"server": server, "interface": "eth0"},
                        scenario_type=ScenarioType.SYSTEM_METRICS,
                        severity=SeverityLevel.INFO
                    )
                ])
        
        return metrics
    
    def export_to_prometheus_format(self, metrics: List[MetricData]) -> str:
        """
        将指标数据导出为Prometheus格式
        
        Args:
            metrics: 指标数据列表
            
        Returns:
            Prometheus格式的字符串
        """
        lines = []
        
        # 按指标名称分组
        metrics_by_name = {}
        for metric in metrics:
            if metric.metric_name not in metrics_by_name:
                metrics_by_name[metric.metric_name] = []
            metrics_by_name[metric.metric_name].append(metric)
        
        for metric_name, metric_list in metrics_by_name.items():
            # 添加HELP和TYPE注释
            lines.append(f"# HELP {metric_name} Generated test metric for {metric_name}")
            lines.append(f"# TYPE {metric_name} gauge")
            
            for metric in metric_list:
                # 构建标签字符串
                label_parts = []
                for key, value in metric.labels.items():
                    label_parts.append(f'{key}="{value}"')
                
                label_str = "{" + ",".join(label_parts) + "}" if label_parts else ""
                
                # 转换时间戳为毫秒
                timestamp_ms = int(metric.timestamp.timestamp() * 1000)
                
                lines.append(f"{metric_name}{label_str} {metric.value} {timestamp_ms}")
        
        return "\n".join(lines)
    
    def export_to_json(self, metrics: List[MetricData]) -> str:
        """
        将指标数据导出为JSON格式
        
        Args:
            metrics: 指标数据列表
            
        Returns:
            JSON格式的字符串
        """
        data = []
        for metric in metrics:
            data.append({
                "timestamp": metric.timestamp.isoformat(),
                "metric_name": metric.metric_name,
                "value": metric.value,
                "labels": metric.labels,
                "scenario_type": metric.scenario_type.value,
                "severity": metric.severity.value
            })
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def save_metrics_to_file(self, metrics: List[MetricData], filename: str, format_type: str = "json"):
        """
        将指标数据保存到文件
        
        Args:
            metrics: 指标数据列表
            filename: 文件名
            format_type: 格式类型 ('json' 或 'prometheus')
        """
        if format_type == "json":
            content = self.export_to_json(metrics)
        elif format_type == "prometheus":
            content = self.export_to_prometheus_format(metrics)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Metrics saved to {filename} in {format_type} format")


if __name__ == "__main__":
    # 示例用法
    generator = ScenarioGenerator()
    
    print("生成Web应用程序监控数据...")
    web_metrics = generator.generate_web_application_metrics(duration_minutes=30)
    
    print("生成数据库性能监控数据...")
    db_metrics = generator.generate_database_metrics(duration_minutes=30)
    
    print("生成系统资源监控数据...")
    system_metrics = generator.generate_system_metrics(duration_minutes=30)
    
    # 合并所有指标
    all_metrics = web_metrics + db_metrics + system_metrics
    
    print(f"总共生成了 {len(all_metrics)} 个指标数据点")
    
    # 保存到文件
    generator.save_metrics_to_file(all_metrics, "test_metrics.json", "json")
    generator.save_metrics_to_file(all_metrics, "test_metrics.prom", "prometheus")
    
    print("测试数据生成完成！")