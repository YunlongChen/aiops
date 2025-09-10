#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Grafana仪表板数据生成器

该模块为Grafana仪表板生成各种测试数据，包括系统指标、应用指标、业务指标等。
不依赖外部库，使用Python标准库实现。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import random
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DashboardGenerator')

class SimpleDashboardGenerator:
    """
    简化版仪表板数据生成器
    生成各种监控指标的时间序列数据
    """
    
    def __init__(self):
        """初始化数据生成器"""
        self.start_time = datetime.now() - timedelta(hours=24)
        self.end_time = datetime.now()
        self.interval = 60  # 1分钟间隔
        
    def generate_time_series(self, start_time: datetime, end_time: datetime, 
                           interval: int, pattern: str = 'normal') -> List[Dict]:
        """
        生成时间序列数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            interval: 时间间隔（秒）
            pattern: 数据模式
            
        Returns:
            时间序列数据列表
        """
        data_points = []
        current_time = start_time
        base_value = random.uniform(10, 100)
        
        while current_time <= end_time:
            timestamp = int(current_time.timestamp() * 1000)  # 毫秒时间戳
            
            if pattern == 'sine':
                # 正弦波模式
                hours = (current_time - start_time).total_seconds() / 3600
                value = base_value + 20 * math.sin(hours * math.pi / 12)
            elif pattern == 'spike':
                # 尖峰模式
                if random.random() < 0.05:  # 5%概率出现尖峰
                    value = base_value * random.uniform(2, 5)
                else:
                    value = base_value + random.uniform(-10, 10)
            elif pattern == 'trend':
                # 趋势模式
                hours = (current_time - start_time).total_seconds() / 3600
                value = base_value + hours * 2 + random.uniform(-5, 5)
            else:
                # 正常模式
                value = base_value + random.uniform(-20, 20)
            
            # 确保值不为负
            value = max(0, value)
            
            data_points.append({
                'timestamp': timestamp,
                'value': round(value, 2)
            })
            
            current_time += timedelta(seconds=interval)
            
        return data_points
    
    def generate_system_metrics(self) -> Dict[str, Any]:
        """
        生成系统指标数据
        
        Returns:
            系统指标数据字典
        """
        logger.info("生成系统指标数据")
        
        metrics = {
            'cpu_usage': {
                'name': 'CPU使用率',
                'unit': '%',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'sine'
                )
            },
            'memory_usage': {
                'name': '内存使用率',
                'unit': '%',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'trend'
                )
            },
            'disk_usage': {
                'name': '磁盘使用率',
                'unit': '%',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'normal'
                )
            },
            'network_io': {
                'name': '网络IO',
                'unit': 'MB/s',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'spike'
                )
            }
        }
        
        return metrics
    
    def generate_application_metrics(self) -> Dict[str, Any]:
        """
        生成应用指标数据
        
        Returns:
            应用指标数据字典
        """
        logger.info("生成应用指标数据")
        
        metrics = {
            'response_time': {
                'name': '响应时间',
                'unit': 'ms',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'spike'
                )
            },
            'throughput': {
                'name': '吞吐量',
                'unit': 'req/s',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'sine'
                )
            },
            'error_rate': {
                'name': '错误率',
                'unit': '%',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'spike'
                )
            },
            'active_connections': {
                'name': '活跃连接数',
                'unit': 'count',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'normal'
                )
            }
        }
        
        return metrics
    
    def generate_business_metrics(self) -> Dict[str, Any]:
        """
        生成业务指标数据
        
        Returns:
            业务指标数据字典
        """
        logger.info("生成业务指标数据")
        
        metrics = {
            'user_registrations': {
                'name': '用户注册数',
                'unit': 'count',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'normal'
                )
            },
            'order_count': {
                'name': '订单数量',
                'unit': 'count',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'sine'
                )
            },
            'revenue': {
                'name': '收入',
                'unit': 'USD',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'trend'
                )
            },
            'conversion_rate': {
                'name': '转化率',
                'unit': '%',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'normal'
                )
            }
        }
        
        return metrics
    
    def generate_database_metrics(self) -> Dict[str, Any]:
        """
        生成数据库指标数据
        
        Returns:
            数据库指标数据字典
        """
        logger.info("生成数据库指标数据")
        
        metrics = {
            'query_time': {
                'name': '查询时间',
                'unit': 'ms',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'spike'
                )
            },
            'connections': {
                'name': '数据库连接数',
                'unit': 'count',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'normal'
                )
            },
            'lock_waits': {
                'name': '锁等待时间',
                'unit': 'ms',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'spike'
                )
            },
            'buffer_hit_ratio': {
                'name': '缓冲区命中率',
                'unit': '%',
                'data': self.generate_time_series(
                    self.start_time, self.end_time, self.interval, 'normal'
                )
            }
        }
        
        return metrics
    
    def generate_dashboard_config(self) -> Dict[str, Any]:
        """
        生成Grafana仪表板配置
        
        Returns:
            仪表板配置字典
        """
        logger.info("生成仪表板配置")
        
        config = {
            'dashboard': {
                'id': None,
                'title': 'AIOps监控仪表板',
                'tags': ['aiops', 'monitoring', 'test'],
                'timezone': 'browser',
                'panels': [
                    {
                        'id': 1,
                        'title': 'CPU使用率',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'cpu_usage',
                            'legendFormat': 'CPU使用率'
                        }]
                    },
                    {
                        'id': 2,
                        'title': '内存使用率',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'memory_usage',
                            'legendFormat': '内存使用率'
                        }]
                    },
                    {
                        'id': 3,
                        'title': '响应时间',
                        'type': 'graph',
                        'targets': [{
                            'expr': 'response_time',
                            'legendFormat': '响应时间'
                        }]
                    },
                    {
                        'id': 4,
                        'title': '错误率',
                        'type': 'singlestat',
                        'targets': [{
                            'expr': 'error_rate',
                            'legendFormat': '错误率'
                        }]
                    }
                ],
                'time': {
                    'from': 'now-24h',
                    'to': 'now'
                },
                'refresh': '30s'
            }
        }
        
        return config
    
    def export_data(self, output_dir: str = 'dashboard_data') -> None:
        """
        导出所有生成的数据
        
        Args:
            output_dir: 输出目录
        """
        import os
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        logger.info(f"导出数据到目录: {output_dir}")
        
        # 生成各类指标数据
        system_metrics = self.generate_system_metrics()
        app_metrics = self.generate_application_metrics()
        business_metrics = self.generate_business_metrics()
        db_metrics = self.generate_database_metrics()
        dashboard_config = self.generate_dashboard_config()
        
        # 保存数据文件
        files_to_save = {
            'system_metrics.json': system_metrics,
            'application_metrics.json': app_metrics,
            'business_metrics.json': business_metrics,
            'database_metrics.json': db_metrics,
            'dashboard_config.json': dashboard_config
        }
        
        for filename, data in files_to_save.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"已保存: {filepath}")
        
        # 生成汇总报告
        summary = {
            'generation_time': datetime.now().isoformat(),
            'time_range': {
                'start': self.start_time.isoformat(),
                'end': self.end_time.isoformat()
            },
            'data_points_per_metric': len(system_metrics['cpu_usage']['data']),
            'total_metrics': (
                len(system_metrics) + len(app_metrics) + 
                len(business_metrics) + len(db_metrics)
            ),
            'files_generated': list(files_to_save.keys())
        }
        
        summary_path = os.path.join(output_dir, 'generation_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"生成汇总报告: {summary_path}")
        
        print(f"\n=== 仪表板数据生成完成 ===")
        print(f"输出目录: {output_dir}")
        print(f"生成文件数: {len(files_to_save) + 1}")
        print(f"总指标数: {summary['total_metrics']}")
        print(f"每个指标数据点数: {summary['data_points_per_metric']}")

def main():
    """
    主函数
    """
    print("=== 简化版Grafana仪表板数据生成器 ===")
    print("正在生成测试数据...")
    
    generator = SimpleDashboardGenerator()
    generator.export_data()
    
    print("\n数据生成完成！")
    print("可以将生成的数据导入到Grafana中进行可视化展示。")

if __name__ == '__main__':
    main()