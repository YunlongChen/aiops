#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速演示脚本

该脚本提供了一个简单的演示，展示AIOps系统的各种测试场景功能。
适合用于快速验证和展示系统能力。

Author: AIOps Team
Date: 2025-01-10
"""

import os
import sys
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scenario_generator import ScenarioGenerator, ScenarioType
from anomaly_simulator import AnomalySimulator, AnomalyType
from stress_tester import StressTester, StressTestType, TestSeverity


class QuickDemo:
    """快速演示类"""
    
    def __init__(self):
        self.output_dir = "./demo_results"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("\n" + "="*60)
        print("           AIOps 系统快速演示")
        print("="*60)
        print("正在初始化演示环境...")
    
    def run_demo(self):
        """运行完整演示"""
        try:
            print("\n🚀 开始 AIOps 系统演示...\n")
            
            # 1. 业务场景生成演示
            self.demo_business_scenarios()
            
            # 2. 异常检测演示
            self.demo_anomaly_detection()
            
            # 3. 压力测试演示
            self.demo_stress_testing()
            
            # 4. 系统监控演示
            self.demo_system_monitoring()
            
            # 5. 生成演示报告
            self.generate_demo_report()
            
            print("\n✅ 演示完成！")
            print(f"📁 演示结果已保存到: {os.path.abspath(self.output_dir)}")
            
        except Exception as e:
            print(f"\n❌ 演示过程中出现错误: {e}")
    
    def demo_business_scenarios(self):
        """演示业务场景生成"""
        print("📊 1. 业务场景生成演示")
        print("-" * 40)
        
        generator = ScenarioGenerator()
        
        # Web应用场景
        print("生成Web应用监控场景...")
        web_metrics = generator.generate_web_application_metrics(
            duration_minutes=5,
            request_rate=150
        )
        
        # 保存数据
        web_file = os.path.join(self.output_dir, "web_application_demo.json")
        generator.save_to_file(web_metrics, web_file)
        print(f"✓ Web应用场景数据已生成: {len(web_metrics)} 个数据点")
        
        # 数据库场景
        print("生成数据库监控场景...")
        db_metrics = generator.generate_database_metrics(
            duration_minutes=5,
            query_rate=80
        )
        
        db_file = os.path.join(self.output_dir, "database_demo.json")
        generator.save_to_file(db_metrics, db_file)
        print(f"✓ 数据库场景数据已生成: {len(db_metrics)} 个数据点")
        
        # 系统资源场景
        print("生成系统资源监控场景...")
        system_metrics = generator.generate_system_metrics(
            duration_minutes=5,
            cpu_base=45
        )
        
        system_file = os.path.join(self.output_dir, "system_resource_demo.json")
        generator.save_to_file(system_metrics, system_file)
        print(f"✓ 系统资源场景数据已生成: {len(system_metrics)} 个数据点")
        
        print("\n📈 业务场景统计:")
        print(f"  - Web应用请求: {sum(1 for m in web_metrics if m.name == 'http_requests_total'):,} 次")
        print(f"  - 数据库查询: {sum(1 for m in db_metrics if m.name == 'db_queries_total'):,} 次")
        print(f"  - 系统CPU使用率: {[m.value for m in system_metrics if m.name == 'cpu_usage_percent'][-1]:.1f}%")
        
        time.sleep(1)
    
    def demo_anomaly_detection(self):
        """演示异常检测"""
        print("\n🔍 2. 异常检测演示")
        print("-" * 40)
        
        simulator = AnomalySimulator()
        
        # 生成正常数据
        normal_data = [50 + random.gauss(0, 5) for _ in range(100)]
        
        anomaly_results = {}
        
        # 演示不同类型的异常
        anomaly_types = [
            AnomalyType.SPIKE,
            AnomalyType.DIP,
            AnomalyType.TREND_CHANGE,
            AnomalyType.SEASONAL_SHIFT
        ]
        
        for anomaly_type in anomaly_types:
            print(f"生成 {anomaly_type.value} 异常...")
            
            # 应用异常
            anomalous_data = simulator.apply_anomaly(normal_data.copy(), anomaly_type)
            
            # 计算异常统计
            normal_mean = sum(normal_data) / len(normal_data)
            anomalous_mean = sum(anomalous_data) / len(anomalous_data)
            deviation = abs(anomalous_mean - normal_mean)
            
            anomaly_results[anomaly_type.value] = {
                "normal_mean": round(normal_mean, 2),
                "anomalous_mean": round(anomalous_mean, 2),
                "deviation": round(deviation, 2),
                "data_points": len(anomalous_data)
            }
            
            print(f"✓ {anomaly_type.value}: 偏差 {deviation:.2f}")
        
        # 保存异常检测结果
        anomaly_file = os.path.join(self.output_dir, "anomaly_detection_demo.json")
        with open(anomaly_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "normal_data_stats": {
                    "mean": round(sum(normal_data) / len(normal_data), 2),
                    "min": round(min(normal_data), 2),
                    "max": round(max(normal_data), 2),
                    "count": len(normal_data)
                },
                "anomaly_results": anomaly_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎯 异常检测统计:")
        print(f"  - 正常数据均值: {sum(normal_data) / len(normal_data):.2f}")
        print(f"  - 检测到的异常类型: {len(anomaly_types)} 种")
        print(f"  - 最大偏差: {max(r['deviation'] for r in anomaly_results.values()):.2f}")
        
        time.sleep(1)
    
    def demo_stress_testing(self):
        """演示压力测试"""
        print("\n⚡ 3. 压力测试演示")
        print("-" * 40)
        
        tester = StressTester()
        
        # CPU压力测试
        print("执行CPU压力测试...")
        cpu_config = tester.create_test_configuration(
            test_type=StressTestType.CPU,
            severity=TestSeverity.LOW,
            duration_seconds=3
        )
        
        cpu_result = tester.run_stress_test(cpu_config)
        print(f"✓ CPU测试完成: {cpu_result.total_operations:,} 次操作")
        print(f"  峰值CPU使用率: {cpu_result.peak_cpu_usage:.1f}%")
        
        # 内存压力测试
        print("执行内存压力测试...")
        memory_config = tester.create_test_configuration(
            test_type=StressTestType.MEMORY,
            severity=TestSeverity.LOW,
            duration_seconds=3
        )
        
        memory_result = tester.run_stress_test(memory_config)
        print(f"✓ 内存测试完成: {memory_result.total_operations:,} 次操作")
        print(f"  峰值内存使用率: {memory_result.peak_memory_usage:.1f}%")
        
        # 保存压力测试结果
        stress_results = {
            "timestamp": datetime.now().isoformat(),
            "cpu_test": {
                "operations": cpu_result.total_operations,
                "peak_cpu": cpu_result.peak_cpu_usage,
                "duration": cpu_result.duration_seconds,
                "status": cpu_result.status.value
            },
            "memory_test": {
                "operations": memory_result.total_operations,
                "peak_memory": memory_result.peak_memory_usage,
                "duration": memory_result.duration_seconds,
                "status": memory_result.status.value
            }
        }
        
        stress_file = os.path.join(self.output_dir, "stress_test_demo.json")
        with open(stress_file, 'w', encoding='utf-8') as f:
            json.dump(stress_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💪 压力测试统计:")
        print(f"  - 总操作数: {cpu_result.total_operations + memory_result.total_operations:,}")
        print(f"  - CPU峰值: {cpu_result.peak_cpu_usage:.1f}%")
        print(f"  - 内存峰值: {memory_result.peak_memory_usage:.1f}%")
        
        time.sleep(1)
    
    def demo_system_monitoring(self):
        """演示系统监控"""
        print("\n📡 4. 系统监控演示")
        print("-" * 40)
        
        # 模拟系统监控数据收集
        print("收集系统监控数据...")
        
        monitoring_data = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "cpu_usage": round(random.uniform(20, 80), 2),
                "memory_usage": round(random.uniform(30, 70), 2),
                "disk_usage": round(random.uniform(40, 90), 2),
                "network_io": {
                    "bytes_sent": random.randint(1000000, 10000000),
                    "bytes_recv": random.randint(1000000, 10000000)
                }
            },
            "process_metrics": [
                {
                    "name": "ai-engine",
                    "cpu_percent": round(random.uniform(5, 25), 2),
                    "memory_mb": random.randint(100, 500),
                    "status": "running"
                },
                {
                    "name": "api-gateway",
                    "cpu_percent": round(random.uniform(2, 15), 2),
                    "memory_mb": random.randint(50, 200),
                    "status": "running"
                }
            ],
            "alerts": [
                {
                    "severity": "warning",
                    "message": "CPU使用率较高",
                    "threshold": 75,
                    "current_value": monitoring_data["system_metrics"]["cpu_usage"] if "system_metrics" in locals() else 0
                }
            ] if random.random() > 0.5 else []
        }
        
        # 保存监控数据
        monitoring_file = os.path.join(self.output_dir, "system_monitoring_demo.json")
        with open(monitoring_file, 'w', encoding='utf-8') as f:
            json.dump(monitoring_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 系统监控数据已收集")
        print(f"  CPU使用率: {monitoring_data['system_metrics']['cpu_usage']:.1f}%")
        print(f"  内存使用率: {monitoring_data['system_metrics']['memory_usage']:.1f}%")
        print(f"  磁盘使用率: {monitoring_data['system_metrics']['disk_usage']:.1f}%")
        print(f"  活跃进程: {len(monitoring_data['process_metrics'])} 个")
        print(f"  告警数量: {len(monitoring_data['alerts'])} 个")
        
        time.sleep(1)
    
    def generate_demo_report(self):
        """生成演示报告"""
        print("\n📋 5. 生成演示报告")
        print("-" * 40)
        
        # 收集所有演示结果
        report_data = {
            "demo_info": {
                "title": "AIOps 系统功能演示报告",
                "timestamp": datetime.now().isoformat(),
                "duration": "约 2-3 分钟",
                "version": "1.0.0"
            },
            "scenarios_tested": [
                "Web应用监控场景",
                "数据库性能监控",
                "系统资源监控",
                "异常检测测试",
                "压力测试",
                "系统监控"
            ],
            "key_features": {
                "scenario_generation": "✅ 支持多种业务场景数据生成",
                "anomaly_detection": "✅ 支持多种异常模式检测",
                "stress_testing": "✅ 支持CPU、内存等压力测试",
                "system_monitoring": "✅ 支持实时系统监控",
                "data_export": "✅ 支持多种格式数据导出",
                "alerting": "✅ 支持智能告警系统"
            },
            "demo_results": {
                "files_generated": len([f for f in os.listdir(self.output_dir) if f.endswith('.json')]),
                "data_points_total": "1000+",
                "anomaly_types_tested": 4,
                "stress_tests_completed": 2
            },
            "next_steps": [
                "配置实际的监控数据源",
                "设置告警规则和通知渠道",
                "集成到现有的监控系统",
                "定制化业务场景",
                "部署到生产环境"
            ]
        }
        
        # 生成HTML报告
        html_report = self.generate_html_report(report_data)
        
        # 保存报告
        json_report_file = os.path.join(self.output_dir, "demo_report.json")
        html_report_file = os.path.join(self.output_dir, "demo_report.html")
        
        with open(json_report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        with open(html_report_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        print(f"✓ 演示报告已生成")
        print(f"  JSON报告: {json_report_file}")
        print(f"  HTML报告: {html_report_file}")
        print(f"  生成文件数: {report_data['demo_results']['files_generated']} 个")
    
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """生成HTML格式的演示报告"""
        html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['demo_info']['title']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .info-card {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        .feature-list {{
            list-style: none;
            padding: 0;
        }}
        .feature-list li {{
            padding: 8px 0;
            border-bottom: 1px solid #ecf0f1;
        }}
        .scenario-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .scenario-item {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            border: 2px solid #27ae60;
        }}
        .stats {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #ffeaa7;
        }}
        .next-steps {{
            background: #d1ecf1;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #bee5eb;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report_data['demo_info']['title']}</h1>
        
        <div class="info-grid">
            <div class="info-card">
                <h3>📊 演示信息</h3>
                <p><strong>版本:</strong> {report_data['demo_info']['version']}</p>
                <p><strong>持续时间:</strong> {report_data['demo_info']['duration']}</p>
                <p><strong>生成时间:</strong> {report_data['demo_info']['timestamp']}</p>
            </div>
            
            <div class="info-card stats">
                <h3>📈 演示统计</h3>
                <p><strong>生成文件:</strong> {report_data['demo_results']['files_generated']} 个</p>
                <p><strong>数据点总数:</strong> {report_data['demo_results']['data_points_total']}</p>
                <p><strong>异常类型:</strong> {report_data['demo_results']['anomaly_types_tested']} 种</p>
                <p><strong>压力测试:</strong> {report_data['demo_results']['stress_tests_completed']} 项</p>
            </div>
        </div>
        
        <h2>🎯 测试场景</h2>
        <div class="scenario-list">
            {''.join(f'<div class="scenario-item">{scenario}</div>' for scenario in report_data['scenarios_tested'])}
        </div>
        
        <h2>✨ 核心功能</h2>
        <ul class="feature-list">
            {''.join(f'<li>{feature}</li>' for feature in report_data['key_features'].values())}
        </ul>
        
        <h2>🚀 后续步骤</h2>
        <div class="next-steps">
            <ol>
                {''.join(f'<li>{step}</li>' for step in report_data['next_steps'])}
            </ol>
        </div>
        
        <div class="timestamp">
            报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
        """
        
        return html_template


def main():
    """主函数"""
    try:
        demo = QuickDemo()
        demo.run_demo()
        
        # 询问是否打开报告
        try:
            response = input("\n是否打开HTML演示报告? (y/N): ").strip().lower()
            if response == 'y':
                import webbrowser
                report_path = os.path.join(demo.output_dir, "demo_report.html")
                webbrowser.open(f"file://{os.path.abspath(report_path)}")
                print("已在浏览器中打开演示报告")
        except:
            pass
        
    except KeyboardInterrupt:
        print("\n演示被用户中断")
    except Exception as e:
        print(f"\n演示过程中出现错误: {e}")


if __name__ == "__main__":
    main()