#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试运行器

这个脚本整合了所有AIOps测试场景，提供统一的测试入口。
包括：
- Web应用监控测试
- 数据库性能监控
- 系统资源监控
- 异常检测测试
- 告警系统测试
- 仪表板数据生成
- 性能压力测试

作者: AIOps测试框架
创建时间: 2025-01-10
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

class IntegratedTestRunner:
    """综合测试运行器类"""
    
    def __init__(self):
        """初始化测试运行器"""
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def run_command(self, command, description):
        """运行命令并记录结果"""
        print(f"\n=== {description} ===")
        print(f"执行命令: {command}")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            self.test_results[description] = {
                'command': command,
                'success': success,
                'duration': duration,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
            if success:
                print(f"✅ {description} 完成 (耗时: {duration:.2f}秒)")
            else:
                print(f"❌ {description} 失败 (耗时: {duration:.2f}秒)")
                print(f"错误信息: {result.stderr}")
                
            return success
            
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            
            self.test_results[description] = {
                'command': command,
                'success': False,
                'duration': duration,
                'error': str(e)
            }
            
            print(f"❌ {description} 异常 (耗时: {duration:.2f}秒)")
            print(f"异常信息: {e}")
            return False
    
    def run_web_monitoring_test(self):
        """运行Web应用监控测试"""
        return self.run_command(
            "python web_app_simulator.py --duration 60",
            "Web应用监控测试"
        )
    
    def run_database_monitoring_test(self):
        """运行数据库监控测试"""
        return self.run_command(
            "python database_simulator.py --duration 120 --export db_test_metrics.json --report db_test_report.json",
            "数据库性能监控测试"
        )
    
    def run_system_monitoring_test(self):
        """运行系统监控测试"""
        return self.run_command(
            "python system_monitor.py --duration 90 --export sys_test_metrics.json --report sys_test_report.json",
            "系统资源监控测试"
        )
    
    def run_anomaly_detection_test(self):
        """运行异常检测测试"""
        return self.run_command(
            "python anomaly_simulator.py",
            "异常检测测试"
        )
    
    def run_alerting_test(self):
        """运行告警系统测试"""
        return self.run_command(
            "python alert_simulator.py",
            "告警系统测试"
        )
    
    def run_dashboard_data_generation(self):
        """运行仪表板数据生成"""
        return self.run_command(
            "python simple_dashboard_generator.py",
            "仪表板数据生成"
        )
    
    def run_performance_stress_test(self):
        """运行性能压力测试"""
        return self.run_command(
            "python simple_performance_tester.py --test-type comprehensive --duration 60",
            "性能压力测试"
        )
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始执行AIOps综合测试套件")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.start_time = time.time()
        
        # 定义测试序列
        tests = [
            self.run_web_monitoring_test,
            self.run_database_monitoring_test,
            self.run_system_monitoring_test,
            self.run_anomaly_detection_test,
            self.run_alerting_test,
            self.run_dashboard_data_generation,
            self.run_performance_stress_test
        ]
        
        # 执行所有测试
        for test_func in tests:
            test_func()
            time.sleep(2)  # 测试间隔
        
        self.end_time = time.time()
        
        # 生成测试报告
        self.generate_test_report()
    
    def run_quick_test(self):
        """运行快速测试（缩短测试时间）"""
        print("⚡ 开始执行AIOps快速测试套件")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.start_time = time.time()
        
        # 快速测试命令
        quick_tests = [
            ("python web_app_simulator.py --duration 30", "Web应用监控快速测试"),
            ("python database_simulator.py --duration 60 --export db_quick_metrics.json", "数据库监控快速测试"),
            ("python system_monitor.py --duration 45 --export sys_quick_metrics.json", "系统监控快速测试"),
            ("python anomaly_simulator.py", "异常检测快速测试"),
            ("python simple_dashboard_generator.py", "仪表板数据快速生成"),
            ("python simple_performance_tester.py --test-type cpu --duration 30", "CPU压力快速测试")
        ]
        
        for command, description in quick_tests:
            self.run_command(command, description)
            time.sleep(1)
        
        self.end_time = time.time()
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        total_duration = self.end_time - self.start_time
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        total_tests = len(self.test_results)
        
        # 控制台报告
        print("\n" + "="*60)
        print("🎯 AIOps测试套件执行完成")
        print("="*60)
        print(f"总耗时: {total_duration:.2f} 秒")
        print(f"测试总数: {total_tests}")
        print(f"成功测试: {successful_tests}")
        print(f"失败测试: {total_tests - successful_tests}")
        print(f"成功率: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\n📊 详细测试结果:")
        for test_name, result in self.test_results.items():
            status = "✅" if result['success'] else "❌"
            print(f"{status} {test_name}: {result['duration']:.2f}秒")
        
        # 保存JSON报告
        report_data = {
            'test_suite': 'AIOps综合测试',
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat(),
            'total_duration': total_duration,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'success_rate': (successful_tests/total_tests)*100,
            'test_results': self.test_results
        }
        
        # 创建报告目录
        report_dir = Path('test_reports')
        report_dir.mkdir(exist_ok=True)
        
        # 保存报告
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'aiops_test_report_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AIOps综合测试运行器')
    parser.add_argument(
        '--mode',
        choices=['full', 'quick'],
        default='full',
        help='测试模式: full=完整测试, quick=快速测试'
    )
    
    args = parser.parse_args()
    
    runner = IntegratedTestRunner()
    
    if args.mode == 'quick':
        runner.run_quick_test()
    else:
        runner.run_all_tests()

if __name__ == '__main__':
    main()