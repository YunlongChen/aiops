#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grafana仪表板数据生成器

该模块为Grafana仪表板生成各种测试数据，包括系统指标、应用指标、业务指标等。
支持多种数据源格式和时间序列数据生成。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class DataSourceType(Enum):
    """数据源类型枚举"""
    PROMETHEUS = "prometheus"
    ELASTICSEARCH = "elasticsearch"
    INFLUXDB = "influxdb"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    GRAPHITE = "graphite"


class MetricCategory(Enum):
    """指标分类枚举"""
    SYSTEM = "system"
    APPLICATION = "application"
    BUSINESS = "business"
    NETWORK = "network"
    DATABASE = "database"
    CUSTOM = "custom"


class TimeSeriesPattern(Enum):
    """时间序列模式枚举"""
    CONSTANT = "constant"  # 常量
    LINEAR = "linear"  # 线性增长/减少
    SINE = "sine"  # 正弦波
    COSINE = "cosine"  # 余弦波
    RANDOM_WALK = "random_walk"  # 随机游走
    SPIKE = "spike"  # 尖峰
    STEP = "step"  # 阶跃
    EXPONENTIAL = "exponential"  # 指数增长
    SEASONAL = "seasonal"  # 季节性


@dataclass
class MetricDefinition:
    """指标定义数据类"""
    name: str
    category: MetricCategory
    unit: str
    description: str
    min_value: float = 0.0
    max_value: float = 100.0
    pattern: TimeSeriesPattern = TimeSeriesPattern.RANDOM_WALK
    labels: Dict[str, str] = field(default_factory=dict)
    sample_interval_seconds: int = 60
    noise_level: float = 0.1  # 噪声水平 (0-1)
    

@dataclass
class TimeSeriesPoint:
    """时间序列数据点"""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class Dashboard:
    """仪表板定义"""
    id: str
    title: str
    description: str
    tags: List[str]
    metrics: List[MetricDefinition]
    refresh_interval: str = "30s"
    time_range: str = "1h"


class DashboardDataGenerator:
    """仪表板数据生成器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化数据生成器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        self.dashboards = self._create_default_dashboards()
        self.data_cache = {}  # 数据缓存
        self.running = False
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "data_sources": {
                "prometheus": {
                    "enabled": True,
                    "url": "http://localhost:9090",
                    "push_gateway_url": "http://localhost:9091"
                },
                "elasticsearch": {
                    "enabled": True,
                    "url": "http://localhost:9200",
                    "index_pattern": "metrics-*"
                },
                "influxdb": {
                    "enabled": False,
                    "url": "http://localhost:8086",
                    "database": "metrics",
                    "username": "admin",
                    "password": "admin"
                }
            },
            "generation": {
                "batch_size": 100,
                "max_workers": 4,
                "retry_attempts": 3,
                "retry_delay_seconds": 5,
                "data_retention_hours": 168  # 7天
            },
            "output": {
                "export_json": True,
                "export_csv": True,
                "export_prometheus": True,
                "output_directory": "./dashboard_data"
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("DashboardDataGenerator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_default_dashboards(self) -> List[Dashboard]:
        """创建默认仪表板"""
        dashboards = []
        
        # 系统监控仪表板
        system_metrics = [
            MetricDefinition(
                name="cpu_usage_percent",
                category=MetricCategory.SYSTEM,
                unit="percent",
                description="CPU使用率",
                min_value=0,
                max_value=100,
                pattern=TimeSeriesPattern.SINE,
                labels={"instance": "server-01", "job": "node-exporter"}
            ),
            MetricDefinition(
                name="memory_usage_percent",
                category=MetricCategory.SYSTEM,
                unit="percent",
                description="内存使用率",
                min_value=0,
                max_value=100,
                pattern=TimeSeriesPattern.RANDOM_WALK,
                labels={"instance": "server-01", "job": "node-exporter"}
            ),
            MetricDefinition(
                name="disk_usage_percent",
                category=MetricCategory.SYSTEM,
                unit="percent",
                description="磁盘使用率",
                min_value=0,
                max_value=100,
                pattern=TimeSeriesPattern.LINEAR,
                labels={"instance": "server-01", "device": "/dev/sda1"}
            ),
            MetricDefinition(
                name="network_bytes_received",
                category=MetricCategory.NETWORK,
                unit="bytes/sec",
                description="网络接收字节数",
                min_value=0,
                max_value=1000000000,  # 1GB/s
                pattern=TimeSeriesPattern.SEASONAL,
                labels={"instance": "server-01", "device": "eth0"}
            ),
            MetricDefinition(
                name="load_average_1m",
                category=MetricCategory.SYSTEM,
                unit="",
                description="1分钟负载平均值",
                min_value=0,
                max_value=16,
                pattern=TimeSeriesPattern.RANDOM_WALK,
                labels={"instance": "server-01"}
            )
        ]
        
        dashboards.append(Dashboard(
            id="system-overview",
            title="System Overview",
            description="系统资源监控概览",
            tags=["system", "infrastructure"],
            metrics=system_metrics
        ))
        
        # 应用监控仪表板
        app_metrics = [
            MetricDefinition(
                name="http_requests_total",
                category=MetricCategory.APPLICATION,
                unit="requests/sec",
                description="HTTP请求总数",
                min_value=0,
                max_value=10000,
                pattern=TimeSeriesPattern.SEASONAL,
                labels={"method": "GET", "status": "200", "service": "web-api"}
            ),
            MetricDefinition(
                name="http_request_duration_seconds",
                category=MetricCategory.APPLICATION,
                unit="seconds",
                description="HTTP请求响应时间",
                min_value=0.001,
                max_value=5.0,
                pattern=TimeSeriesPattern.SPIKE,
                labels={"method": "GET", "service": "web-api"}
            ),
            MetricDefinition(
                name="http_errors_total",
                category=MetricCategory.APPLICATION,
                unit="errors/sec",
                description="HTTP错误总数",
                min_value=0,
                max_value=100,
                pattern=TimeSeriesPattern.RANDOM_WALK,
                labels={"status": "500", "service": "web-api"}
            ),
            MetricDefinition(
                name="active_connections",
                category=MetricCategory.APPLICATION,
                unit="connections",
                description="活跃连接数",
                min_value=0,
                max_value=1000,
                pattern=TimeSeriesPattern.SINE,
                labels={"service": "web-api"}
            ),
            MetricDefinition(
                name="queue_size",
                category=MetricCategory.APPLICATION,
                unit="messages",
                description="队列大小",
                min_value=0,
                max_value=10000,
                pattern=TimeSeriesPattern.STEP,
                labels={"queue": "task-queue", "service": "worker"}
            )
        ]
        
        dashboards.append(Dashboard(
            id="application-metrics",
            title="Application Metrics",
            description="应用程序性能监控",
            tags=["application", "performance"],
            metrics=app_metrics
        ))
        
        # 数据库监控仪表板
        db_metrics = [
            MetricDefinition(
                name="db_connections_active",
                category=MetricCategory.DATABASE,
                unit="connections",
                description="活跃数据库连接数",
                min_value=0,
                max_value=200,
                pattern=TimeSeriesPattern.RANDOM_WALK,
                labels={"database": "mysql", "instance": "db-01"}
            ),
            MetricDefinition(
                name="db_query_duration_seconds",
                category=MetricCategory.DATABASE,
                unit="seconds",
                description="数据库查询响应时间",
                min_value=0.001,
                max_value=10.0,
                pattern=TimeSeriesPattern.SPIKE,
                labels={"database": "mysql", "query_type": "select"}
            ),
            MetricDefinition(
                name="db_slow_queries_total",
                category=MetricCategory.DATABASE,
                unit="queries",
                description="慢查询总数",
                min_value=0,
                max_value=50,
                pattern=TimeSeriesPattern.RANDOM_WALK,
                labels={"database": "mysql", "instance": "db-01"}
            ),
            MetricDefinition(
                name="db_buffer_pool_usage_percent",
                category=MetricCategory.DATABASE,
                unit="percent",
                description="缓冲池使用率",
                min_value=0,
                max_value=100,
                pattern=TimeSeriesPattern.SINE,
                labels={"database": "mysql", "instance": "db-01"}
            )
        ]
        
        dashboards.append(Dashboard(
            id="database-performance",
            title="Database Performance",
            description="数据库性能监控",
            tags=["database", "mysql"],
            metrics=db_metrics
        ))
        
        # 业务指标仪表板
        business_metrics = [
            MetricDefinition(
                name="user_registrations_total",
                category=MetricCategory.BUSINESS,
                unit="users",
                description="用户注册总数",
                min_value=0,
                max_value=1000,
                pattern=TimeSeriesPattern.SEASONAL,
                labels={"source": "web", "country": "CN"}
            ),
            MetricDefinition(
                name="orders_total",
                category=MetricCategory.BUSINESS,
                unit="orders",
                description="订单总数",
                min_value=0,
                max_value=500,
                pattern=TimeSeriesPattern.SEASONAL,
                labels={"status": "completed", "payment_method": "credit_card"}
            ),
            MetricDefinition(
                name="revenue_total",
                category=MetricCategory.BUSINESS,
                unit="currency",
                description="总收入",
                min_value=0,
                max_value=100000,
                pattern=TimeSeriesPattern.LINEAR,
                labels={"currency": "USD", "region": "US"}
            ),
            MetricDefinition(
                name="active_users",
                category=MetricCategory.BUSINESS,
                unit="users",
                description="活跃用户数",
                min_value=0,
                max_value=10000,
                pattern=TimeSeriesPattern.SINE,
                labels={"time_window": "1h"}
            )
        ]
        
        dashboards.append(Dashboard(
            id="business-metrics",
            title="Business Metrics",
            description="业务指标监控",
            tags=["business", "kpi"],
            metrics=business_metrics
        ))
        
        return dashboards
    
    def generate_time_series_data(self, metric: MetricDefinition, 
                                 start_time: datetime, 
                                 end_time: datetime,
                                 interval_seconds: int = None) -> List[TimeSeriesPoint]:
        """生成时间序列数据"""
        if interval_seconds is None:
            interval_seconds = metric.sample_interval_seconds
        
        points = []
        current_time = start_time
        base_value = (metric.min_value + metric.max_value) / 2
        
        # 用于随机游走的状态
        random_walk_value = base_value
        
        # 用于阶跃函数的状态
        step_level = 0
        step_change_probability = 0.05
        
        while current_time <= end_time:
            # 计算时间相关的参数
            time_offset = (current_time - start_time).total_seconds()
            time_normalized = time_offset / 3600  # 小时为单位
            
            # 根据模式生成值
            if metric.pattern == TimeSeriesPattern.CONSTANT:
                value = base_value
            
            elif metric.pattern == TimeSeriesPattern.LINEAR:
                # 线性增长
                slope = (metric.max_value - metric.min_value) / 24  # 24小时内从最小到最大
                value = metric.min_value + slope * time_normalized
                value = max(metric.min_value, min(metric.max_value, value))
            
            elif metric.pattern == TimeSeriesPattern.SINE:
                # 正弦波，24小时周期
                amplitude = (metric.max_value - metric.min_value) / 2
                value = base_value + amplitude * math.sin(2 * math.pi * time_normalized / 24)
            
            elif metric.pattern == TimeSeriesPattern.COSINE:
                # 余弦波，24小时周期
                amplitude = (metric.max_value - metric.min_value) / 2
                value = base_value + amplitude * math.cos(2 * math.pi * time_normalized / 24)
            
            elif metric.pattern == TimeSeriesPattern.RANDOM_WALK:
                # 随机游走
                change = random.uniform(-1, 1) * (metric.max_value - metric.min_value) * 0.02
                random_walk_value += change
                random_walk_value = max(metric.min_value, min(metric.max_value, random_walk_value))
                value = random_walk_value
            
            elif metric.pattern == TimeSeriesPattern.SPIKE:
                # 基础值加上偶尔的尖峰
                value = base_value
                if random.random() < 0.05:  # 5%概率出现尖峰
                    spike_magnitude = random.uniform(0.5, 1.0) * (metric.max_value - base_value)
                    value += spike_magnitude
            
            elif metric.pattern == TimeSeriesPattern.STEP:
                # 阶跃函数
                if random.random() < step_change_probability:
                    step_level = random.randint(0, 4)
                value = metric.min_value + (metric.max_value - metric.min_value) * step_level / 4
            
            elif metric.pattern == TimeSeriesPattern.EXPONENTIAL:
                # 指数增长（有限制）
                growth_rate = 0.1  # 每小时10%增长
                value = metric.min_value * math.exp(growth_rate * time_normalized)
                value = min(metric.max_value, value)
            
            elif metric.pattern == TimeSeriesPattern.SEASONAL:
                # 季节性模式（日周期 + 周周期）
                daily_amplitude = (metric.max_value - metric.min_value) * 0.3
                weekly_amplitude = (metric.max_value - metric.min_value) * 0.2
                
                daily_component = daily_amplitude * math.sin(2 * math.pi * time_normalized / 24)
                weekly_component = weekly_amplitude * math.sin(2 * math.pi * time_normalized / (24 * 7))
                
                value = base_value + daily_component + weekly_component
            
            else:
                value = base_value
            
            # 添加噪声
            if metric.noise_level > 0:
                noise_range = (metric.max_value - metric.min_value) * metric.noise_level
                noise = random.uniform(-noise_range/2, noise_range/2)
                value += noise
            
            # 确保值在范围内
            value = max(metric.min_value, min(metric.max_value, value))
            
            # 创建数据点
            point = TimeSeriesPoint(
                timestamp=current_time,
                value=round(value, 3),
                labels=metric.labels.copy()
            )
            
            points.append(point)
            current_time += timedelta(seconds=interval_seconds)
        
        return points
    
    def generate_dashboard_data(self, dashboard_id: str, 
                               hours: int = 24,
                               interval_seconds: int = 60) -> Dict[str, List[TimeSeriesPoint]]:
        """为指定仪表板生成数据"""
        dashboard = next((d for d in self.dashboards if d.id == dashboard_id), None)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        dashboard_data = {}
        
        for metric in dashboard.metrics:
            self.logger.info(f"Generating data for metric: {metric.name}")
            
            # 为每个标签组合生成数据
            if metric.labels:
                # 生成多个实例的数据
                instances = self._generate_metric_instances(metric)
                for instance_labels in instances:
                    instance_metric = MetricDefinition(
                        name=metric.name,
                        category=metric.category,
                        unit=metric.unit,
                        description=metric.description,
                        min_value=metric.min_value,
                        max_value=metric.max_value,
                        pattern=metric.pattern,
                        labels=instance_labels,
                        sample_interval_seconds=metric.sample_interval_seconds,
                        noise_level=metric.noise_level
                    )
                    
                    instance_key = f"{metric.name}_{self._labels_to_string(instance_labels)}"
                    dashboard_data[instance_key] = self.generate_time_series_data(
                        instance_metric, start_time, end_time, interval_seconds
                    )
            else:
                dashboard_data[metric.name] = self.generate_time_series_data(
                    metric, start_time, end_time, interval_seconds
                )
        
        return dashboard_data
    
    def _generate_metric_instances(self, metric: MetricDefinition) -> List[Dict[str, str]]:
        """为指标生成多个实例"""
        instances = []
        
        # 基于指标类型生成不同的实例
        if metric.category == MetricCategory.SYSTEM:
            servers = ["server-01", "server-02", "server-03"]
            for server in servers:
                labels = metric.labels.copy()
                labels["instance"] = server
                instances.append(labels)
        
        elif metric.category == MetricCategory.APPLICATION:
            services = ["web-api", "user-service", "payment-service"]
            for service in services:
                labels = metric.labels.copy()
                labels["service"] = service
                instances.append(labels)
        
        elif metric.category == MetricCategory.DATABASE:
            databases = ["db-01", "db-02"]
            for db in databases:
                labels = metric.labels.copy()
                labels["instance"] = db
                instances.append(labels)
        
        elif metric.category == MetricCategory.BUSINESS:
            regions = ["US", "EU", "APAC"]
            for region in regions:
                labels = metric.labels.copy()
                labels["region"] = region
                instances.append(labels)
        
        else:
            instances.append(metric.labels.copy())
        
        return instances if instances else [metric.labels.copy()]
    
    def _labels_to_string(self, labels: Dict[str, str]) -> str:
        """将标签字典转换为字符串"""
        return "_".join([f"{k}_{v}" for k, v in sorted(labels.items())])
    
    def export_to_prometheus_format(self, dashboard_data: Dict[str, List[TimeSeriesPoint]], 
                                   filename: str):
        """导出为Prometheus格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            for metric_name, points in dashboard_data.items():
                if not points:
                    continue
                
                # 写入HELP和TYPE注释
                base_name = metric_name.split('_')[0] + '_' + metric_name.split('_')[1]
                f.write(f"# HELP {base_name} Generated metric for dashboard\n")
                f.write(f"# TYPE {base_name} gauge\n")
                
                # 写入数据点
                for point in points:
                    labels_str = ""
                    if point.labels:
                        labels_list = [f'{k}="{v}"' for k, v in point.labels.items()]
                        labels_str = "{" + ",".join(labels_list) + "}"
                    
                    timestamp_ms = int(point.timestamp.timestamp() * 1000)
                    f.write(f"{base_name}{labels_str} {point.value} {timestamp_ms}\n")
        
        self.logger.info(f"Data exported to Prometheus format: {filename}")
    
    def export_to_json(self, dashboard_data: Dict[str, List[TimeSeriesPoint]], 
                      filename: str):
        """导出为JSON格式"""
        json_data = {
            "exported_at": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for metric_name, points in dashboard_data.items():
            json_data["metrics"][metric_name] = [
                {
                    "timestamp": point.timestamp.isoformat(),
                    "value": point.value,
                    "labels": point.labels
                }
                for point in points
            ]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Data exported to JSON format: {filename}")
    
    def export_to_csv(self, dashboard_data: Dict[str, List[TimeSeriesPoint]], 
                     filename: str):
        """导出为CSV格式"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入表头
            writer.writerow(["metric_name", "timestamp", "value", "labels"])
            
            # 写入数据
            for metric_name, points in dashboard_data.items():
                for point in points:
                    labels_str = json.dumps(point.labels) if point.labels else "{}"
                    writer.writerow([
                        metric_name,
                        point.timestamp.isoformat(),
                        point.value,
                        labels_str
                    ])
        
        self.logger.info(f"Data exported to CSV format: {filename}")
    
    def push_to_prometheus(self, dashboard_data: Dict[str, List[TimeSeriesPoint]], 
                          job_name: str = "dashboard_generator"):
        """推送数据到Prometheus Push Gateway"""
        push_gateway_url = self.config["data_sources"]["prometheus"]["push_gateway_url"]
        
        if not push_gateway_url:
            self.logger.warning("Prometheus Push Gateway URL not configured")
            return
        
        try:
            # 构建推送数据
            metrics_text = ""
            
            for metric_name, points in dashboard_data.items():
                if not points:
                    continue
                
                # 使用最新的数据点
                latest_point = max(points, key=lambda p: p.timestamp)
                
                base_name = metric_name.replace('-', '_').replace('.', '_')
                labels_str = ""
                if latest_point.labels:
                    labels_list = [f'{k}="{v}"' for k, v in latest_point.labels.items()]
                    labels_str = "{" + ",".join(labels_list) + "}"
                
                metrics_text += f"{base_name}{labels_str} {latest_point.value}\n"
            
            # 推送到Push Gateway
            url = f"{push_gateway_url}/metrics/job/{job_name}"
            response = requests.post(
                url,
                data=metrics_text,
                headers={'Content-Type': 'text/plain'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully pushed metrics to Prometheus Push Gateway")
            else:
                self.logger.error(f"Failed to push metrics: {response.status_code} {response.text}")
        
        except Exception as e:
            self.logger.error(f"Error pushing to Prometheus: {e}")
    
    def push_to_elasticsearch(self, dashboard_data: Dict[str, List[TimeSeriesPoint]], 
                             index_name: str = None):
        """推送数据到Elasticsearch"""
        es_url = self.config["data_sources"]["elasticsearch"]["url"]
        
        if not es_url:
            self.logger.warning("Elasticsearch URL not configured")
            return
        
        if not index_name:
            index_name = f"metrics-{datetime.now().strftime('%Y.%m.%d')}"
        
        try:
            for metric_name, points in dashboard_data.items():
                for point in points:
                    doc = {
                        "@timestamp": point.timestamp.isoformat(),
                        "metric_name": metric_name,
                        "value": point.value,
                        "labels": point.labels
                    }
                    
                    # 推送到Elasticsearch
                    url = f"{es_url}/{index_name}/_doc"
                    response = requests.post(
                        url,
                        json=doc,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    
                    if response.status_code not in [200, 201]:
                        self.logger.error(f"Failed to push to Elasticsearch: {response.status_code}")
                        break
            
            self.logger.info(f"Successfully pushed metrics to Elasticsearch index: {index_name}")
        
        except Exception as e:
            self.logger.error(f"Error pushing to Elasticsearch: {e}")
    
    def generate_grafana_dashboard_json(self, dashboard_id: str) -> Dict:
        """生成Grafana仪表板JSON配置"""
        dashboard = next((d for d in self.dashboards if d.id == dashboard_id), None)
        if not dashboard:
            raise ValueError(f"Dashboard {dashboard_id} not found")
        
        panels = []
        panel_id = 1
        
        for i, metric in enumerate(dashboard.metrics):
            # 计算面板位置
            x = (i % 2) * 12
            y = (i // 2) * 8
            
            panel = {
                "id": panel_id,
                "title": metric.name.replace('_', ' ').title(),
                "type": "graph",
                "gridPos": {
                    "h": 8,
                    "w": 12,
                    "x": x,
                    "y": y
                },
                "targets": [
                    {
                        "expr": metric.name,
                        "legendFormat": "{{instance}}",
                        "refId": "A"
                    }
                ],
                "yAxes": [
                    {
                        "label": metric.unit,
                        "min": metric.min_value,
                        "max": metric.max_value
                    },
                    {
                        "show": False
                    }
                ],
                "tooltip": {
                    "shared": True,
                    "sort": 0,
                    "value_type": "individual"
                },
                "legend": {
                    "show": True,
                    "values": False,
                    "min": False,
                    "max": False,
                    "current": False,
                    "total": False,
                    "avg": False
                }
            }
            
            panels.append(panel)
            panel_id += 1
        
        dashboard_json = {
            "id": None,
            "title": dashboard.title,
            "description": dashboard.description,
            "tags": dashboard.tags,
            "timezone": "browser",
            "panels": panels,
            "time": {
                "from": "now-1h",
                "to": "now"
            },
            "timepicker": {
                "refresh_intervals": ["5s", "10s", "30s", "1m", "5m", "15m", "30m", "1h", "2h", "1d"],
                "time_options": ["5m", "15m", "1h", "6h", "12h", "24h", "2d", "7d", "30d"]
            },
            "refresh": dashboard.refresh_interval,
            "schemaVersion": 16,
            "version": 1
        }
        
        return dashboard_json
    
    def list_dashboards(self) -> List[Dict[str, str]]:
        """列出所有可用的仪表板"""
        return [
            {
                "id": dashboard.id,
                "title": dashboard.title,
                "description": dashboard.description,
                "tags": ", ".join(dashboard.tags),
                "metrics_count": len(dashboard.metrics)
            }
            for dashboard in self.dashboards
        ]
    
    def generate_all_dashboards_data(self, hours: int = 24, 
                                   interval_seconds: int = 60) -> Dict[str, Dict]:
        """为所有仪表板生成数据"""
        all_data = {}
        
        for dashboard in self.dashboards:
            self.logger.info(f"Generating data for dashboard: {dashboard.title}")
            dashboard_data = self.generate_dashboard_data(
                dashboard.id, hours, interval_seconds
            )
            all_data[dashboard.id] = dashboard_data
        
        return all_data
    
    def start_real_time_generation(self, dashboard_id: str, 
                                  interval_seconds: int = 60):
        """启动实时数据生成"""
        import threading
        
        def generate_loop():
            while self.running:
                try:
                    # 生成最近一个时间间隔的数据
                    end_time = datetime.now()
                    start_time = end_time - timedelta(seconds=interval_seconds)
                    
                    dashboard_data = self.generate_dashboard_data(
                        dashboard_id, hours=interval_seconds/3600, 
                        interval_seconds=interval_seconds
                    )
                    
                    # 推送到配置的数据源
                    if self.config["data_sources"]["prometheus"]["enabled"]:
                        self.push_to_prometheus(dashboard_data)
                    
                    if self.config["data_sources"]["elasticsearch"]["enabled"]:
                        self.push_to_elasticsearch(dashboard_data)
                    
                    time.sleep(interval_seconds)
                    
                except Exception as e:
                    self.logger.error(f"Error in real-time generation: {e}")
                    time.sleep(interval_seconds)
        
        self.running = True
        thread = threading.Thread(target=generate_loop, daemon=True)
        thread.start()
        
        self.logger.info(f"Started real-time data generation for dashboard: {dashboard_id}")
        return thread
    
    def stop_real_time_generation(self):
        """停止实时数据生成"""
        self.running = False
        self.logger.info("Stopped real-time data generation")


def main():
    """主函数"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description="Dashboard Data Generator")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--dashboard", help="Dashboard ID to generate data for")
    parser.add_argument("--list-dashboards", action="store_true", help="List available dashboards")
    parser.add_argument("--hours", type=int, default=24, help="Hours of data to generate")
    parser.add_argument("--interval", type=int, default=60, help="Sample interval in seconds")
    parser.add_argument("--output-dir", default="./dashboard_data", help="Output directory")
    parser.add_argument("--format", choices=["json", "csv", "prometheus", "all"], 
                       default="all", help="Output format")
    parser.add_argument("--real-time", action="store_true", help="Start real-time data generation")
    parser.add_argument("--push-prometheus", action="store_true", help="Push data to Prometheus")
    parser.add_argument("--push-elasticsearch", action="store_true", help="Push data to Elasticsearch")
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    
    # 创建生成器
    generator = DashboardDataGenerator(config)
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 列出仪表板
    if args.list_dashboards:
        dashboards = generator.list_dashboards()
        print("\nAvailable Dashboards:")
        print("-" * 80)
        for dashboard in dashboards:
            print(f"ID: {dashboard['id']}")
            print(f"Title: {dashboard['title']}")
            print(f"Description: {dashboard['description']}")
            print(f"Tags: {dashboard['tags']}")
            print(f"Metrics: {dashboard['metrics_count']}")
            print("-" * 80)
        return
    
    # 实时数据生成
    if args.real_time:
        if not args.dashboard:
            print("Dashboard ID is required for real-time generation")
            return
        
        print(f"Starting real-time data generation for dashboard: {args.dashboard}")
        print("Press Ctrl+C to stop")
        
        try:
            generator.start_real_time_generation(args.dashboard, args.interval)
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            generator.stop_real_time_generation()
            print("\nReal-time generation stopped")
        return
    
    # 生成数据
    if args.dashboard:
        # 生成指定仪表板的数据
        print(f"Generating data for dashboard: {args.dashboard}")
        dashboard_data = generator.generate_dashboard_data(
            args.dashboard, args.hours, args.interval
        )
        
        # 导出数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if args.format in ["json", "all"]:
            filename = os.path.join(args.output_dir, f"{args.dashboard}_{timestamp}.json")
            generator.export_to_json(dashboard_data, filename)
        
        if args.format in ["csv", "all"]:
            filename = os.path.join(args.output_dir, f"{args.dashboard}_{timestamp}.csv")
            generator.export_to_csv(dashboard_data, filename)
        
        if args.format in ["prometheus", "all"]:
            filename = os.path.join(args.output_dir, f"{args.dashboard}_{timestamp}.prom")
            generator.export_to_prometheus_format(dashboard_data, filename)
        
        # 推送数据
        if args.push_prometheus:
            generator.push_to_prometheus(dashboard_data)
        
        if args.push_elasticsearch:
            generator.push_to_elasticsearch(dashboard_data)
        
        print(f"Data generation completed for dashboard: {args.dashboard}")
        print(f"Generated {sum(len(points) for points in dashboard_data.values())} data points")
    
    else:
        # 生成所有仪表板的数据
        print("Generating data for all dashboards")
        all_data = generator.generate_all_dashboards_data(args.hours, args.interval)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for dashboard_id, dashboard_data in all_data.items():
            if args.format in ["json", "all"]:
                filename = os.path.join(args.output_dir, f"{dashboard_id}_{timestamp}.json")
                generator.export_to_json(dashboard_data, filename)
            
            if args.format in ["csv", "all"]:
                filename = os.path.join(args.output_dir, f"{dashboard_id}_{timestamp}.csv")
                generator.export_to_csv(dashboard_data, filename)
            
            if args.format in ["prometheus", "all"]:
                filename = os.path.join(args.output_dir, f"{dashboard_id}_{timestamp}.prom")
                generator.export_to_prometheus_format(dashboard_data, filename)
        
        total_points = sum(
            sum(len(points) for points in dashboard_data.values()) 
            for dashboard_data in all_data.values()
        )
        print(f"Data generation completed for all dashboards")
        print(f"Generated {total_points} total data points")


if __name__ == "__main__":
    main()