#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用程序监控模拟器
模拟Web应用程序的各种监控指标，包括响应时间、错误率、吞吐量等
用于AIOps测试场景
"""

import argparse
import json
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import os

class WebAppSimulator:
    """Web应用程序监控数据模拟器"""
    
    def __init__(self, duration: int = 300):
        """
        初始化Web应用模拟器
        
        Args:
            duration: 模拟运行时长(秒)
        """
        self.duration = duration
        self.start_time = datetime.now()
        self.metrics = []
        self.running = False
        
        # 模拟的Web应用服务
        self.services = [
            {'name': 'user-service', 'base_response_time': 120, 'error_rate': 0.02},
            {'name': 'order-service', 'base_response_time': 200, 'error_rate': 0.01},
            {'name': 'payment-service', 'base_response_time': 300, 'error_rate': 0.005},
            {'name': 'inventory-service', 'base_response_time': 150, 'error_rate': 0.015},
            {'name': 'notification-service', 'base_response_time': 80, 'error_rate': 0.03}
        ]
        
    def generate_web_metrics(self) -> Dict[str, Any]:
        """
        生成Web应用监控指标
        
        Returns:
            包含各种Web监控指标的字典
        """
        current_time = datetime.now()
        
        # 模拟时间相关的负载变化
        hour = current_time.hour
        load_factor = 1.0
        if 9 <= hour <= 17:  # 工作时间高负载
            load_factor = 1.5 + random.uniform(-0.2, 0.3)
        elif 18 <= hour <= 22:  # 晚间中等负载
            load_factor = 1.2 + random.uniform(-0.1, 0.2)
        else:  # 夜间低负载
            load_factor = 0.6 + random.uniform(-0.1, 0.2)
            
        metrics = {
            'timestamp': current_time.isoformat(),
            'services': {},
            'overall': {
                'total_requests': int(random.uniform(800, 1500) * load_factor),
                'successful_requests': 0,
                'failed_requests': 0,
                'avg_response_time': 0,
                'p95_response_time': 0,
                'p99_response_time': 0,
                'throughput_rps': 0,
                'cpu_usage': random.uniform(20, 80) * load_factor,
                'memory_usage': random.uniform(40, 85),
                'active_connections': int(random.uniform(50, 200) * load_factor)
            }
        }
        
        total_response_times = []
        total_requests = 0
        total_errors = 0
        
        # 为每个服务生成指标
        for service in self.services:
            service_requests = int(random.uniform(100, 300) * load_factor)
            base_rt = service['base_response_time']
            error_rate = service['error_rate']
            
            # 添加一些随机波动和异常情况
            if random.random() < 0.1:  # 10%概率出现性能问题
                response_time_factor = random.uniform(2.0, 5.0)
                error_rate *= random.uniform(2.0, 10.0)
            else:
                response_time_factor = random.uniform(0.8, 1.3)
                
            avg_response_time = base_rt * response_time_factor * load_factor
            p95_response_time = avg_response_time * random.uniform(1.5, 2.5)
            p99_response_time = avg_response_time * random.uniform(2.0, 4.0)
            
            errors = int(service_requests * min(error_rate, 0.5))
            successful = service_requests - errors
            
            # 生成响应时间分布
            for _ in range(service_requests):
                if random.random() < error_rate:
                    rt = random.uniform(avg_response_time * 2, avg_response_time * 10)
                else:
                    rt = max(10, random.gauss(avg_response_time, avg_response_time * 0.3))
                total_response_times.append(rt)
            
            metrics['services'][service['name']] = {
                'requests': service_requests,
                'successful_requests': successful,
                'failed_requests': errors,
                'error_rate': errors / service_requests if service_requests > 0 else 0,
                'avg_response_time': avg_response_time,
                'p95_response_time': p95_response_time,
                'p99_response_time': p99_response_time,
                'throughput_rps': service_requests / 60,  # 假设每分钟的请求数
                'status_codes': {
                    '200': successful,
                    '400': int(errors * 0.3),
                    '404': int(errors * 0.2),
                    '500': int(errors * 0.4),
                    '503': int(errors * 0.1)
                }
            }
            
            total_requests += service_requests
            total_errors += errors
        
        # 计算总体指标
        if total_response_times:
            total_response_times.sort()
            metrics['overall']['avg_response_time'] = sum(total_response_times) / len(total_response_times)
            metrics['overall']['p95_response_time'] = total_response_times[int(len(total_response_times) * 0.95)]
            metrics['overall']['p99_response_time'] = total_response_times[int(len(total_response_times) * 0.99)]
        
        metrics['overall']['total_requests'] = total_requests
        metrics['overall']['successful_requests'] = total_requests - total_errors
        metrics['overall']['failed_requests'] = total_errors
        metrics['overall']['error_rate'] = total_errors / total_requests if total_requests > 0 else 0
        metrics['overall']['throughput_rps'] = total_requests / 60
        
        return metrics
    
    def simulate_incident(self) -> Dict[str, Any]:
        """
        模拟Web应用故障场景
        
        Returns:
            故障场景的指标数据
        """
        incident_types = [
            'high_error_rate',
            'slow_response',
            'service_unavailable',
            'memory_leak',
            'database_connection_issue'
        ]
        
        incident_type = random.choice(incident_types)
        metrics = self.generate_web_metrics()
        
        if incident_type == 'high_error_rate':
            # 模拟高错误率
            for service_name in metrics['services']:
                service = metrics['services'][service_name]
                service['error_rate'] = random.uniform(0.15, 0.4)
                service['failed_requests'] = int(service['requests'] * service['error_rate'])
                service['successful_requests'] = service['requests'] - service['failed_requests']
                
        elif incident_type == 'slow_response':
            # 模拟响应时间过慢
            for service_name in metrics['services']:
                service = metrics['services'][service_name]
                service['avg_response_time'] *= random.uniform(3.0, 8.0)
                service['p95_response_time'] *= random.uniform(4.0, 10.0)
                service['p99_response_time'] *= random.uniform(5.0, 15.0)
                
        elif incident_type == 'service_unavailable':
            # 模拟服务不可用
            affected_service = random.choice(list(metrics['services'].keys()))
            service = metrics['services'][affected_service]
            service['error_rate'] = 1.0
            service['failed_requests'] = service['requests']
            service['successful_requests'] = 0
            service['status_codes']['503'] = service['requests']
            
        elif incident_type == 'memory_leak':
            # 模拟内存泄漏
            metrics['overall']['memory_usage'] = random.uniform(85, 98)
            metrics['overall']['cpu_usage'] = random.uniform(70, 95)
            
        elif incident_type == 'database_connection_issue':
            # 模拟数据库连接问题
            for service_name in ['user-service', 'order-service']:
                if service_name in metrics['services']:
                    service = metrics['services'][service_name]
                    service['avg_response_time'] *= random.uniform(5.0, 20.0)
                    service['error_rate'] = random.uniform(0.3, 0.8)
        
        metrics['incident'] = {
            'type': incident_type,
            'severity': random.choice(['warning', 'critical', 'major']),
            'description': f'模拟{incident_type}故障场景'
        }
        
        return metrics
    
    def run_simulation(self, export_file: str = None, incident_mode: bool = False):
        """
        运行Web应用监控模拟
        
        Args:
            export_file: 导出文件路径
            incident_mode: 是否启用故障模拟模式
        """
        print(f"🌐 启动Web应用监控模拟器")
        print(f"模拟时长: {self.duration}秒")
        print(f"故障模式: {'启用' if incident_mode else '禁用'}")
        print(f"开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.running = True
        end_time = self.start_time + timedelta(seconds=self.duration)
        
        try:
            while datetime.now() < end_time and self.running:
                if incident_mode and random.random() < 0.2:  # 20%概率触发故障
                    metrics = self.simulate_incident()
                    print(f"⚠️  故障模拟: {metrics['incident']['type']} - {metrics['incident']['severity']}")
                else:
                    metrics = self.generate_web_metrics()
                
                self.metrics.append(metrics)
                
                # 显示实时指标
                overall = metrics['overall']
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"请求: {overall['total_requests']}, "
                      f"错误率: {overall['error_rate']:.2%}, "
                      f"响应时间: {overall['avg_response_time']:.1f}ms, "
                      f"CPU: {overall['cpu_usage']:.1f}%")
                
                time.sleep(5)  # 每5秒生成一次数据
                
        except KeyboardInterrupt:
            print("\n模拟被用户中断")
            self.running = False
        
        print(f"\n✅ Web应用监控模拟完成")
        print(f"总共生成 {len(self.metrics)} 个数据点")
        
        # 导出数据
        if export_file:
            self.export_metrics(export_file)
    
    def export_metrics(self, filename: str):
        """
        导出监控指标到JSON文件
        
        Args:
            filename: 导出文件名
        """
        export_data = {
            'simulation_info': {
                'type': 'web_application_monitoring',
                'start_time': self.start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'duration': self.duration,
                'data_points': len(self.metrics)
            },
            'services': [service['name'] for service in self.services],
            'metrics': self.metrics
        }
        
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 监控数据已导出到: {filename}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Web应用程序监控模拟器')
    parser.add_argument('--duration', type=int, default=300, help='模拟时长(秒)')
    parser.add_argument('--export', type=str, help='导出文件路径')
    parser.add_argument('--incident', action='store_true', help='启用故障模拟模式')
    
    args = parser.parse_args()
    
    simulator = WebAppSimulator(duration=args.duration)
    simulator.run_simulation(export_file=args.export, incident_mode=args.incident)

if __name__ == '__main__':
    main()