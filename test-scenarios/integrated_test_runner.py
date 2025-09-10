#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIOps 整合的测试场景运行器
整合所有测试场景，提供统一的测试入口
支持多项目负载测试和错误注入

作者: AIOps Team
创建时间: 2025-01-10
更新时间: 2025-01-10
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import argparse

# 导入新的测试模块
try:
    from multi_project_load_tester import ProjectLoadTester
    from error_injector import ErrorInjector
except ImportError:
    print("警告: 无法导入多项目负载测试器或错误注入器模块")
    ProjectLoadTester = None
    ErrorInjector = None

class IntegratedTestRunner:
    """综合测试运行器类"""
    
    def __init__(self):
        """初始化测试运行器"""
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 测试场景脚本路径
        self.test_scripts = {
            'web_monitor': 'web_app_simulator.py',
            'db_monitor': 'database_simulator.py', 
            'system_monitor': 'system_monitor.py',
            'anomaly_detection': 'anomaly_simulator.py',
            'alert_system': 'alert_simulator.py',
            'dashboard_data': 'simple_dashboard_generator.py',
            'performance_test': 'simple_performance_tester.py'
        }
        
        # 初始化新的测试组件
        self.project_load_tester = ProjectLoadTester() if ProjectLoadTester else None
        self.error_injector = ErrorInjector() if ErrorInjector else None
        
        # 项目配置文件路径
        self.project_configs_path = os.path.join(self.current_dir, 'project_configs.json')
        self.project_configs = self._load_project_configs()
    
    def _load_project_configs(self) -> Dict[str, Any]:
        """加载项目配置文件"""
        try:
            if os.path.exists(self.project_configs_path):
                with open(self.project_configs_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"警告: 无法加载项目配置文件: {e}")
        return {}
    
    def run_multi_project_load_test(self, test_scenario: str = 'basic_load_test') -> Dict[str, Any]:
        """运行多项目负载测试"""
        if not self.project_load_tester:
            return {
                'success': False,
                'error': '多项目负载测试器未初始化',
                'duration': 0
            }
        
        start_time = time.time()
        
        try:
            # 获取测试场景配置
            projects = self.project_configs.get(test_scenario, [])
            if not projects:
                return {
                    'success': False,
                    'error': f'未找到测试场景配置: {test_scenario}',
                    'duration': time.time() - start_time
                }
            
            print(f"\n=== 开始多项目负载测试: {test_scenario} ===")
            print(f"测试项目数量: {len(projects)}")
            
            # 运行负载测试
            results = self.project_load_tester.run_load_test_from_config(projects)
            
            duration = time.time() - start_time
            print(f"多项目负载测试完成，耗时: {duration:.2f}秒")
            
            return {
                'success': True,
                'results': results,
                'duration': duration,
                'projects_tested': len(projects)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time
            }
    
    def run_error_injection_test(self, project_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """运行错误注入测试"""
        if not self.error_injector:
            return {
                'success': False,
                'error': '错误注入器未初始化',
                'duration': 0
            }
        
        start_time = time.time()
        injection_results = []
        
        try:
            print("\n=== 开始错误注入测试 ===")
            
            for project_config in project_configs:
                if project_config.get('introduce_error', False):
                    project_type = project_config.get('type')
                    project_name = project_config.get('name')
                    
                    print(f"正在为 {project_name} ({project_type}) 注入错误...")
                    
                    # 创建临时项目目录
                    temp_project_path = os.path.join(self.current_dir, 'temp_projects', project_name)
                    os.makedirs(temp_project_path, exist_ok=True)
                    
                    # 注入随机错误
                    result = self.error_injector.inject_random_error(temp_project_path, project_type)
                    result['project_name'] = project_name
                    injection_results.append(result)
            
            duration = time.time() - start_time
            successful_injections = sum(1 for r in injection_results if r.get('success', False))
            
            print(f"错误注入测试完成，成功注入: {successful_injections}/{len(injection_results)}")
            
            return {
                'success': True,
                'injection_results': injection_results,
                'duration': duration,
                'successful_injections': successful_injections,
                'total_attempts': len(injection_results)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start_time,
                'injection_results': injection_results
            }
        
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
            "py web_app_simulator.py --duration 60",
            "Web应用监控测试"
        )
    
    def run_database_monitoring_test(self):
        """运行数据库监控测试"""
        return self.run_command(
            "py database_simulator.py --duration 120 --export db_test_metrics.json --report db_test_report.json",
            "数据库性能监控测试"
        )
    
    def run_system_monitoring_test(self):
        """运行系统监控测试"""
        return self.run_command(
            "py system_monitor.py --duration 90 --export sys_test_metrics.json --report sys_test_report.json",
            "系统资源监控测试"
        )
    
    def run_anomaly_detection_test(self):
        """运行异常检测测试"""
        return self.run_command(
            "py anomaly_simulator.py",
            "异常检测测试"
        )
    
    def run_alerting_test(self):
        """运行告警系统测试"""
        return self.run_command(
            "py alert_simulator.py",
            "告警系统测试"
        )
    
    def run_dashboard_data_generation(self):
        """运行仪表板数据生成"""
        return self.run_command(
            "py simple_dashboard_generator.py",
            "仪表板数据生成"
        )
    
    def run_performance_stress_test(self):
        """运行性能压力测试"""
        return self.run_command(
            "py simple_performance_tester.py --test-type comprehensive --duration 60",
            "性能压力测试"
        )
    
    def run_all_tests(self, include_multi_project: bool = True, include_error_injection: bool = True):
        """运行所有测试"""
        print("🚀 开始执行AIOps综合测试套件")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.start_time = time.time()
        
        # 定义基础测试序列
        tests = [
            self.run_web_monitoring_test,
            self.run_database_monitoring_test,
            self.run_system_monitoring_test,
            self.run_anomaly_detection_test,
            self.run_alerting_test,
            self.run_dashboard_data_generation,
            self.run_performance_stress_test
        ]
        
        # 执行基础测试
        for test_func in tests:
            test_func()
            time.sleep(2)  # 测试间隔
        
        # 执行多项目负载测试
        if include_multi_project and self.project_load_tester:
            print("\n=== 开始多项目负载测试 ===")
            multi_project_scenarios = ['basic_load_test', 'comprehensive_load_test', 'performance_stress_test']
            
            for scenario in multi_project_scenarios:
                result = self.run_multi_project_load_test(scenario)
                self.test_results[f'多项目负载测试-{scenario}'] = {
                    'command': f'multi_project_load_test({scenario})',
                    'success': result.get('success', False),
                    'duration': result.get('duration', 0),
                    'details': result
                }
                time.sleep(2)
        
        # 执行错误注入测试
        if include_error_injection and self.error_injector:
            print("\n=== 开始错误注入测试 ===")
            error_scenarios = ['error_prone_test', 'mixed_scenario_test', 'build_failure_scenarios', 'runtime_failure_scenarios']
            
            for scenario in error_scenarios:
                projects = self.project_configs.get(scenario, [])
                if projects:
                    result = self.run_error_injection_test(projects)
                    self.test_results[f'错误注入测试-{scenario}'] = {
                        'command': f'error_injection_test({scenario})',
                        'success': result.get('success', False),
                        'duration': result.get('duration', 0),
                        'details': result
                    }
                    time.sleep(2)
        
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
            ("py web_app_simulator.py --duration 30", "Web应用监控快速测试"),
            ("py database_simulator.py --duration 60 --export db_quick_metrics.json", "数据库监控快速测试"),
            ("py system_monitor.py --duration 45 --export sys_quick_metrics.json", "系统监控快速测试"),
            ("py anomaly_simulator.py", "异常检测快速测试"),
            ("py simple_dashboard_generator.py", "仪表板数据快速生成"),
            ("py simple_performance_tester.py --test-type cpu --duration 30", "CPU压力快速测试")
        ]
        
        for command, description in quick_tests:
            self.run_command(command, description)
            time.sleep(1)
        
        self.end_time = time.time()
        self.generate_test_report()
    
    def run_custom_tests(self, test_list: List[str]):
        """运行自定义测试列表"""
        print(f"🎯 开始执行自定义测试: {', '.join(test_list)}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.start_time = time.time()
        
        test_mapping = {
            'web_monitor': self.run_web_monitoring_test,
            'db_monitor': self.run_database_monitoring_test,
            'system_monitor': self.run_system_monitoring_test,
            'anomaly_detection': self.run_anomaly_detection_test,
            'alert_system': self.run_alerting_test,
            'dashboard_data': self.run_dashboard_data_generation,
            'performance_test': self.run_performance_stress_test
        }
        
        for test_name in test_list:
            if test_name in test_mapping:
                test_mapping[test_name]()
                time.sleep(2)
            else:
                print(f"警告: 未知的测试场景 '{test_name}'")
        
        self.end_time = time.time()
        self.generate_test_report()
    
    def save_report(self, output_file: str):
        """保存测试报告到指定文件"""
        if not hasattr(self, 'start_time') or not hasattr(self, 'end_time'):
            print("警告: 没有可用的测试结果")
            return
            
        total_duration = self.end_time - self.start_time
        successful_tests = sum(1 for result in self.test_results.values() if result['success'])
        total_tests = len(self.test_results)
        
        report_data = {
            'test_suite': 'AIOps综合测试',
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat(),
            'total_duration': total_duration,
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'failed_tests': total_tests - successful_tests,
            'success_rate': (successful_tests/total_tests)*100 if total_tests > 0 else 0,
            'test_results': self.test_results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"测试报告已保存到: {output_file}")
    
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
    parser = argparse.ArgumentParser(description='AIOps 综合测试场景运行器')
    parser.add_argument('--mode', choices=['all', 'quick', 'custom', 'multi-project', 'error-injection', 'comprehensive'], 
                       default='all', help='测试模式')
    parser.add_argument('--tests', nargs='+', 
                       choices=['web_monitor', 'db_monitor', 'system_monitor', 
                               'anomaly_detection', 'alert_system', 'dashboard_data', 'performance_test'],
                       help='自定义测试场景 (仅在custom模式下有效)')
    parser.add_argument('--scenario', 
                       choices=['basic_load_test', 'comprehensive_load_test', 'error_prone_test', 
                               'mixed_scenario_test', 'microservices_ecosystem_test', 'performance_stress_test',
                               'build_failure_scenarios', 'runtime_failure_scenarios'],
                       help='多项目测试场景或错误注入场景')
    parser.add_argument('--output', default='test_report.json',
                       help='测试报告输出文件名')
    parser.add_argument('--no-multi-project', action='store_true',
                       help='禁用多项目负载测试')
    parser.add_argument('--no-error-injection', action='store_true',
                       help='禁用错误注入测试')
    
    args = parser.parse_args()
    
    runner = IntegratedTestRunner()
    
    try:
        if args.mode == 'all':
            runner.run_all_tests(
                include_multi_project=not args.no_multi_project,
                include_error_injection=not args.no_error_injection
            )
        elif args.mode == 'quick':
            runner.run_quick_test()
        elif args.mode == 'custom':
            if not args.tests:
                print("错误: 自定义模式需要指定测试场景 (--tests)")
                return 1
            runner.run_custom_tests(args.tests)
        elif args.mode == 'multi-project':
            scenario = args.scenario or 'basic_load_test'
            result = runner.run_multi_project_load_test(scenario)
            print(f"\n多项目负载测试结果: {result}")
        elif args.mode == 'error-injection':
            scenario = args.scenario or 'error_prone_test'
            projects = runner.project_configs.get(scenario, [])
            if projects:
                result = runner.run_error_injection_test(projects)
                print(f"\n错误注入测试结果: {result}")
            else:
                print(f"错误: 未找到场景配置 '{scenario}'")
                return 1
        elif args.mode == 'comprehensive':
            # 运行所有类型的测试，包括扩展测试
            print("\n=== 启动全面综合测试模式 ===")
            runner.run_all_tests(include_multi_project=True, include_error_injection=True)
            
            # 额外运行微服务生态系统测试
            if 'microservices_ecosystem_test' in runner.project_configs:
                print("\n=== 微服务生态系统测试 ===")
                result = runner.run_multi_project_load_test('microservices_ecosystem_test')
                runner.test_results['微服务生态系统测试'] = {
                    'command': 'microservices_ecosystem_test',
                    'success': result.get('success', False),
                    'duration': result.get('duration', 0),
                    'details': result
                }
        
        # 保存测试报告
        if args.output:
            runner.save_report(args.output)
            
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n测试执行出错: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    main()