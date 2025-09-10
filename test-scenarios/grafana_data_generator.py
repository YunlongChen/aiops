#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grafana数据生成器
为Grafana仪表板生成各种格式的测试数据
支持InfluxDB、Prometheus、Elasticsearch等数据源格式
"""

import argparse
import json
import random
import time
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from enum import Enum
from dataclasses import dataclass

class DataSourceType(Enum):
    """数据源类型枚举"""
    INFLUXDB = "influxdb"
    PROMETHEUS = "prometheus"
    ELASTICSEARCH = "elasticsearch"
    MYSQL = "mysql"
    POSTGRES = "postgres"
    GRAPHITE = "graphite"

class MetricType(Enum):
    """指标类型枚举"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class MetricDefinition:
    """指标定义数据类"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    labels: Dict[str, List[str]]
    value_range: tuple
    pattern: str = "normal"  # normal, seasonal, trending, spiky

class GrafanaDataGenerator:
    """Grafana数据生成器"""
    
    def __init__(self, duration: int = 3600, interval: int = 60, data_source: DataSourceType = DataSourceType.INFLUXDB):
        """
        初始化数据生成器
        
        Args:
            duration: 数据时间跨度(秒)
            interval: 数据点间隔(秒)
            data_source: 数据源类型
        """
        self.duration = duration
        self.interval = interval
        self.data_source = data_source
        self.start_time = datetime.now() - timedelta(seconds=duration)
        self.end_time = datetime.now()
        self.data_points = []
        
        # 定义指标
        self.metrics = {
            # 系统指标
            'system_cpu_usage': MetricDefinition(
                name='system_cpu_usage',
                metric_type=MetricType.GAUGE,
                description='系统CPU使用率',
                unit='percent',
                labels={
                    'host': ['web-01', 'web-02', 'db-01', 'cache-01'],
                    'cpu': ['cpu0', 'cpu1', 'cpu2', 'cpu3'],
                    'mode': ['user', 'system', 'idle', 'iowait']
                },
                value_range=(0, 100),
                pattern='seasonal'
            ),
            'system_memory_usage': MetricDefinition(
                name='system_memory_usage',
                metric_type=MetricType.GAUGE,
                description='系统内存使用率',
                unit='percent',
                labels={
                    'host': ['web-01', 'web-02', 'db-01', 'cache-01'],
                    'type': ['used', 'free', 'cached', 'buffers']
                },
                value_range=(0, 100),
                pattern='trending'
            ),
            'system_disk_usage': MetricDefinition(
                name='system_disk_usage',
                metric_type=MetricType.GAUGE,
                description='磁盘使用率',
                unit='percent',
                labels={
                    'host': ['web-01', 'web-02', 'db-01', 'cache-01'],
                    'device': ['/dev/sda1', '/dev/sda2', '/dev/nvme0n1'],
                    'mountpoint': ['/', '/home', '/var']
                },
                value_range=(0, 100),
                pattern='normal'
            ),
            'system_network_bytes': MetricDefinition(
                name='system_network_bytes',
                metric_type=MetricType.COUNTER,
                description='网络流量字节数',
                unit='bytes',
                labels={
                    'host': ['web-01', 'web-02', 'db-01', 'cache-01'],
                    'interface': ['eth0', 'eth1', 'lo'],
                    'direction': ['rx', 'tx']
                },
                value_range=(0, 1000000000),
                pattern='seasonal'
            ),
            
            # 应用指标
            'http_requests_total': MetricDefinition(
                name='http_requests_total',
                metric_type=MetricType.COUNTER,
                description='HTTP请求总数',
                unit='requests',
                labels={
                    'method': ['GET', 'POST', 'PUT', 'DELETE'],
                    'status': ['200', '201', '400', '404', '500'],
                    'endpoint': ['/api/users', '/api/orders', '/api/products', '/health']
                },
                value_range=(0, 10000),
                pattern='seasonal'
            ),
            'http_request_duration': MetricDefinition(
                name='http_request_duration',
                metric_type=MetricType.HISTOGRAM,
                description='HTTP请求持续时间',
                unit='seconds',
                labels={
                    'method': ['GET', 'POST', 'PUT', 'DELETE'],
                    'endpoint': ['/api/users', '/api/orders', '/api/products']
                },
                value_range=(0.001, 5.0),
                pattern='spiky'
            ),
            'database_connections': MetricDefinition(
                name='database_connections',
                metric_type=MetricType.GAUGE,
                description='数据库连接数',
                unit='connections',
                labels={
                    'database': ['users_db', 'orders_db', 'products_db'],
                    'state': ['active', 'idle', 'waiting']
                },
                value_range=(0, 200),
                pattern='normal'
            ),
            'database_query_duration': MetricDefinition(
                name='database_query_duration',
                metric_type=MetricType.HISTOGRAM,
                description='数据库查询持续时间',
                unit='seconds',
                labels={
                    'database': ['users_db', 'orders_db', 'products_db'],
                    'operation': ['select', 'insert', 'update', 'delete']
                },
                value_range=(0.001, 2.0),
                pattern='spiky'
            ),
            
            # 业务指标
            'user_registrations': MetricDefinition(
                name='user_registrations',
                metric_type=MetricType.COUNTER,
                description='用户注册数',
                unit='users',
                labels={
                    'source': ['web', 'mobile', 'api'],
                    'country': ['US', 'CN', 'UK', 'DE', 'JP']
                },
                value_range=(0, 1000),
                pattern='seasonal'
            ),
            'order_amount': MetricDefinition(
                name='order_amount',
                metric_type=MetricType.GAUGE,
                description='订单金额',
                unit='dollars',
                labels={
                    'currency': ['USD', 'EUR', 'CNY', 'JPY'],
                    'category': ['electronics', 'clothing', 'books', 'food']
                },
                value_range=(10, 5000),
                pattern='seasonal'
            ),
            'active_users': MetricDefinition(
                name='active_users',
                metric_type=MetricType.GAUGE,
                description='活跃用户数',
                unit='users',
                labels={
                    'platform': ['web', 'ios', 'android'],
                    'region': ['north_america', 'europe', 'asia']
                },
                value_range=(100, 50000),
                pattern='seasonal'
            )
        }
    
    def generate_value(self, metric: MetricDefinition, timestamp: datetime, base_value: float = None) -> float:
        """
        根据模式生成指标值
        
        Args:
            metric: 指标定义
            timestamp: 时间戳
            base_value: 基础值
            
        Returns:
            生成的指标值
        """
        min_val, max_val = metric.value_range
        
        if base_value is None:
            base_value = (min_val + max_val) / 2
        
        if metric.pattern == 'normal':
            # 正态分布
            std_dev = (max_val - min_val) * 0.1
            value = random.normalvariate(base_value, std_dev)
            
        elif metric.pattern == 'seasonal':
            # 季节性模式
            hour = timestamp.hour
            day_of_week = timestamp.weekday()
            
            # 工作日vs周末
            weekend_factor = 0.7 if day_of_week >= 5 else 1.0
            
            # 一天中的时间模式
            if 6 <= hour <= 9:  # 早高峰
                time_factor = 1.3
            elif 10 <= hour <= 16:  # 工作时间
                time_factor = 1.1
            elif 17 <= hour <= 20:  # 晚高峰
                time_factor = 1.4
            elif 21 <= hour <= 23:  # 晚间
                time_factor = 0.9
            else:  # 夜间
                time_factor = 0.5
            
            seasonal_factor = weekend_factor * time_factor
            value = base_value * seasonal_factor + random.uniform(-base_value * 0.1, base_value * 0.1)
            
        elif metric.pattern == 'trending':
            # 趋势模式
            hours_since_start = (timestamp - self.start_time).total_seconds() / 3600
            trend_factor = 1 + (hours_since_start * 0.02)  # 每小时增长2%
            value = base_value * trend_factor + random.uniform(-base_value * 0.05, base_value * 0.05)
            
        elif metric.pattern == 'spiky':
            # 尖峰模式
            if random.random() < 0.05:  # 5%概率出现尖峰
                spike_factor = random.uniform(2, 5)
                value = base_value * spike_factor
            else:
                value = base_value + random.uniform(-base_value * 0.2, base_value * 0.2)
        
        else:
            value = base_value
        
        # 确保值在范围内
        return max(min_val, min(max_val, value))
    
    def generate_label_combinations(self, labels: Dict[str, List[str]], max_combinations: int = 50) -> List[Dict[str, str]]:
        """
        生成标签组合
        
        Args:
            labels: 标签定义
            max_combinations: 最大组合数
            
        Returns:
            标签组合列表
        """
        import itertools
        
        label_keys = list(labels.keys())
        label_values = [labels[key] for key in label_keys]
        
        # 生成所有可能的组合
        all_combinations = list(itertools.product(*label_values))
        
        # 如果组合太多，随机选择一部分
        if len(all_combinations) > max_combinations:
            selected_combinations = random.sample(all_combinations, max_combinations)
        else:
            selected_combinations = all_combinations
        
        # 转换为字典格式
        result = []
        for combination in selected_combinations:
            label_dict = {label_keys[i]: combination[i] for i in range(len(label_keys))}
            result.append(label_dict)
        
        return result
    
    def generate_influxdb_data(self) -> List[Dict[str, Any]]:
        """
        生成InfluxDB格式的数据
        
        Returns:
            InfluxDB数据点列表
        """
        data_points = []
        
        current_time = self.start_time
        while current_time <= self.end_time:
            timestamp_ns = int(current_time.timestamp() * 1000000000)
            
            for metric_name, metric in self.metrics.items():
                label_combinations = self.generate_label_combinations(metric.labels)
                
                for labels in label_combinations:
                    value = self.generate_value(metric, current_time)
                    
                    # InfluxDB格式
                    point = {
                        'measurement': metric_name,
                        'tags': labels,
                        'fields': {
                            'value': value
                        },
                        'time': timestamp_ns
                    }
                    
                    data_points.append(point)
            
            current_time += timedelta(seconds=self.interval)
        
        return data_points
    
    def generate_prometheus_data(self) -> List[Dict[str, Any]]:
        """
        生成Prometheus格式的数据
        
        Returns:
            Prometheus数据点列表
        """
        data_points = []
        
        current_time = self.start_time
        while current_time <= self.end_time:
            timestamp_ms = int(current_time.timestamp() * 1000)
            
            for metric_name, metric in self.metrics.items():
                label_combinations = self.generate_label_combinations(metric.labels)
                
                for labels in label_combinations:
                    value = self.generate_value(metric, current_time)
                    
                    # Prometheus格式
                    label_str = ','.join([f'{k}="{v}"' for k, v in labels.items()])
                    
                    if metric.metric_type == MetricType.HISTOGRAM:
                        # 生成直方图数据
                        buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
                        cumulative_count = 0
                        
                        for bucket in buckets:
                            if value <= bucket:
                                cumulative_count += random.randint(1, 100)
                            
                            point = {
                                'metric': f'{metric_name}_bucket',
                                'labels': {**labels, 'le': str(bucket)},
                                'value': cumulative_count,
                                'timestamp': timestamp_ms
                            }
                            data_points.append(point)
                        
                        # 添加_count和_sum指标
                        data_points.append({
                            'metric': f'{metric_name}_count',
                            'labels': labels,
                            'value': cumulative_count,
                            'timestamp': timestamp_ms
                        })
                        
                        data_points.append({
                            'metric': f'{metric_name}_sum',
                            'labels': labels,
                            'value': value * cumulative_count,
                            'timestamp': timestamp_ms
                        })
                    
                    else:
                        point = {
                            'metric': metric_name,
                            'labels': labels,
                            'value': value,
                            'timestamp': timestamp_ms
                        }
                        data_points.append(point)
            
            current_time += timedelta(seconds=self.interval)
        
        return data_points
    
    def generate_elasticsearch_data(self) -> List[Dict[str, Any]]:
        """
        生成Elasticsearch格式的数据
        
        Returns:
            Elasticsearch文档列表
        """
        documents = []
        
        current_time = self.start_time
        while current_time <= self.end_time:
            timestamp_iso = current_time.isoformat()
            
            for metric_name, metric in self.metrics.items():
                label_combinations = self.generate_label_combinations(metric.labels)
                
                for labels in label_combinations:
                    value = self.generate_value(metric, current_time)
                    
                    # Elasticsearch文档格式
                    doc = {
                        '@timestamp': timestamp_iso,
                        'metric_name': metric_name,
                        'metric_type': metric.metric_type.value,
                        'value': value,
                        'unit': metric.unit,
                        'description': metric.description,
                        **labels
                    }
                    
                    documents.append(doc)
            
            current_time += timedelta(seconds=self.interval)
        
        return documents
    
    def generate_sql_data(self) -> List[str]:
        """
        生成SQL插入语句
        
        Returns:
            SQL语句列表
        """
        sql_statements = []
        
        # 创建表结构
        create_table_sql = """
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_type VARCHAR(20) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    labels JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_metrics_labels ON metrics USING GIN(labels);
"""
        sql_statements.append(create_table_sql)
        
        current_time = self.start_time
        while current_time <= self.end_time:
            timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
            
            for metric_name, metric in self.metrics.items():
                label_combinations = self.generate_label_combinations(metric.labels, max_combinations=10)
                
                for labels in label_combinations:
                    value = self.generate_value(metric, current_time)
                    labels_json = json.dumps(labels)
                    
                    insert_sql = f"""
INSERT INTO metrics (timestamp, metric_name, metric_type, value, unit, labels)
VALUES ('{timestamp_str}', '{metric_name}', '{metric.metric_type.value}', {value}, '{metric.unit}', '{labels_json}');
"""
                    sql_statements.append(insert_sql)
            
            current_time += timedelta(seconds=self.interval)
        
        return sql_statements
    
    def generate_dashboard_config(self) -> Dict[str, Any]:
        """
        生成Grafana仪表板配置
        
        Returns:
            仪表板配置字典
        """
        dashboard = {
            'dashboard': {
                'id': None,
                'title': 'AIOps Test Dashboard',
                'description': 'AIOps测试场景仪表板',
                'tags': ['aiops', 'test', 'monitoring'],
                'timezone': 'browser',
                'refresh': '30s',
                'time': {
                    'from': 'now-1h',
                    'to': 'now'
                },
                'panels': []
            }
        }
        
        panel_id = 1
        y_position = 0
        
        # 系统指标面板
        system_panels = [
            {
                'title': 'CPU使用率',
                'type': 'graph',
                'targets': [{
                    'expr': 'system_cpu_usage',
                    'legendFormat': '{{host}} - {{cpu}}'
                }],
                'yAxes': [{
                    'unit': 'percent',
                    'max': 100
                }]
            },
            {
                'title': '内存使用率',
                'type': 'graph',
                'targets': [{
                    'expr': 'system_memory_usage',
                    'legendFormat': '{{host}} - {{type}}'
                }],
                'yAxes': [{
                    'unit': 'percent',
                    'max': 100
                }]
            },
            {
                'title': '磁盘使用率',
                'type': 'graph',
                'targets': [{
                    'expr': 'system_disk_usage',
                    'legendFormat': '{{host}} - {{device}}'
                }],
                'yAxes': [{
                    'unit': 'percent',
                    'max': 100
                }]
            },
            {
                'title': '网络流量',
                'type': 'graph',
                'targets': [{
                    'expr': 'rate(system_network_bytes[5m])',
                    'legendFormat': '{{host}} - {{interface}} {{direction}}'
                }],
                'yAxes': [{
                    'unit': 'bytes'
                }]
            }
        ]
        
        # 应用指标面板
        app_panels = [
            {
                'title': 'HTTP请求率',
                'type': 'graph',
                'targets': [{
                    'expr': 'rate(http_requests_total[5m])',
                    'legendFormat': '{{method}} {{status}}'
                }],
                'yAxes': [{
                    'unit': 'reqps'
                }]
            },
            {
                'title': 'HTTP响应时间',
                'type': 'graph',
                'targets': [{
                    'expr': 'histogram_quantile(0.95, rate(http_request_duration_bucket[5m]))',
                    'legendFormat': '95th percentile'
                }],
                'yAxes': [{
                    'unit': 's'
                }]
            },
            {
                'title': '数据库连接',
                'type': 'graph',
                'targets': [{
                    'expr': 'database_connections',
                    'legendFormat': '{{database}} - {{state}}'
                }],
                'yAxes': [{
                    'unit': 'short'
                }]
            }
        ]
        
        # 业务指标面板
        business_panels = [
            {
                'title': '用户注册',
                'type': 'stat',
                'targets': [{
                    'expr': 'increase(user_registrations[1h])',
                    'legendFormat': '每小时注册数'
                }]
            },
            {
                'title': '订单金额',
                'type': 'graph',
                'targets': [{
                    'expr': 'order_amount',
                    'legendFormat': '{{currency}} - {{category}}'
                }],
                'yAxes': [{
                    'unit': 'currencyUSD'
                }]
            },
            {
                'title': '活跃用户',
                'type': 'graph',
                'targets': [{
                    'expr': 'active_users',
                    'legendFormat': '{{platform}} - {{region}}'
                }],
                'yAxes': [{
                    'unit': 'short'
                }]
            }
        ]
        
        all_panels = system_panels + app_panels + business_panels
        
        for i, panel_config in enumerate(all_panels):
            panel = {
                'id': panel_id,
                'title': panel_config['title'],
                'type': panel_config['type'],
                'gridPos': {
                    'h': 8,
                    'w': 12,
                    'x': (i % 2) * 12,
                    'y': y_position
                },
                'targets': panel_config['targets'],
                'options': {},
                'fieldConfig': {
                    'defaults': {
                        'unit': panel_config.get('yAxes', [{}])[0].get('unit', 'short')
                    }
                }
            }
            
            dashboard['dashboard']['panels'].append(panel)
            panel_id += 1
            
            if i % 2 == 1:
                y_position += 8
        
        return dashboard
    
    def generate_data(self, export_dir: str = "./grafana_data"):
        """
        生成所有格式的数据
        
        Args:
            export_dir: 导出目录
        """
        print(f"📊 启动Grafana数据生成器")
        print(f"数据源类型: {self.data_source.value}")
        print(f"时间范围: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据间隔: {self.interval}秒")
        print(f"指标数量: {len(self.metrics)}")
        
        os.makedirs(export_dir, exist_ok=True)
        
        # 生成不同格式的数据
        if self.data_source == DataSourceType.INFLUXDB:
            print("生成InfluxDB格式数据...")
            data = self.generate_influxdb_data()
            with open(f"{export_dir}/influxdb_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"InfluxDB数据已保存: {len(data)}个数据点")
        
        elif self.data_source == DataSourceType.PROMETHEUS:
            print("生成Prometheus格式数据...")
            data = self.generate_prometheus_data()
            with open(f"{export_dir}/prometheus_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Prometheus数据已保存: {len(data)}个数据点")
        
        elif self.data_source == DataSourceType.ELASTICSEARCH:
            print("生成Elasticsearch格式数据...")
            data = self.generate_elasticsearch_data()
            with open(f"{export_dir}/elasticsearch_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Elasticsearch数据已保存: {len(data)}个文档")
        
        elif self.data_source in [DataSourceType.MYSQL, DataSourceType.POSTGRES]:
            print("生成SQL格式数据...")
            sql_statements = self.generate_sql_data()
            with open(f"{export_dir}/sql_data.sql", 'w', encoding='utf-8') as f:
                f.write('\n'.join(sql_statements))
            print(f"SQL数据已保存: {len(sql_statements)}条语句")
        
        # 生成仪表板配置
        print("生成Grafana仪表板配置...")
        dashboard_config = self.generate_dashboard_config()
        with open(f"{export_dir}/dashboard.json", 'w', encoding='utf-8') as f:
            json.dump(dashboard_config, f, indent=2, ensure_ascii=False)
        
        # 生成指标文档
        print("生成指标文档...")
        metrics_doc = {
            'metrics': {
                name: {
                    'name': metric.name,
                    'type': metric.metric_type.value,
                    'description': metric.description,
                    'unit': metric.unit,
                    'labels': metric.labels,
                    'value_range': metric.value_range,
                    'pattern': metric.pattern
                }
                for name, metric in self.metrics.items()
            },
            'generation_info': {
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'interval': self.interval,
                'data_source': self.data_source.value,
                'total_metrics': len(self.metrics)
            }
        }
        
        with open(f"{export_dir}/metrics_documentation.json", 'w', encoding='utf-8') as f:
            json.dump(metrics_doc, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 数据生成完成")
        print(f"导出目录: {export_dir}")
        print(f"生成文件:")
        for file in os.listdir(export_dir):
            file_path = os.path.join(export_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"  - {file} ({file_size:,} bytes)")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Grafana数据生成器')
    parser.add_argument('--duration', type=int, default=3600, help='数据时间跨度(秒)')
    parser.add_argument('--interval', type=int, default=60, help='数据点间隔(秒)')
    parser.add_argument('--datasource', type=str, default='influxdb', 
                       choices=['influxdb', 'prometheus', 'elasticsearch', 'mysql', 'postgres'],
                       help='数据源类型')
    parser.add_argument('--export-dir', type=str, default='./grafana_data', help='导出目录')
    
    args = parser.parse_args()
    
    data_source = DataSourceType(args.datasource)
    generator = GrafanaDataGenerator(
        duration=args.duration,
        interval=args.interval,
        data_source=data_source
    )
    
    generator.generate_data(export_dir=args.export_dir)

if __name__ == '__main__':
    main()