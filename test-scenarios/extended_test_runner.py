#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展综合测试运行器

这个脚本扩展了原有的AIOps测试框架，集成了多项目负载测试功能，
支持更全面的系统负载和错误场景测试。

新增功能：
- 多语言项目负载测试 (Java/Rust/Node.js)
- 构建错误场景模拟
- 运行时错误场景模拟
- 并发项目测试
- 资源竞争测试
- 错误恢复测试

作者: AIOps测试框架
创建时间: 2025-01-10
"""

import os
import sys
import json
import time
import argparse
import subprocess
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 导入原有的测试运行器
try:
    from integrated_test_runner import IntegratedTestRunner
except ImportError:
    print("警告: 无法导入原有测试运行器，将使用简化版本")
    IntegratedTestRunner = None

# 导入多项目负载测试器
try:
    from multi_project_load_tester import ProjectLoadTester
except ImportError:
    print("警告: 无法导入多项目负载测试器")
    ProjectLoadTester = None

class ExtendedTestRunner:
    """扩展综合测试运行器类"""
    
    def __init__(self):
        """初始化扩展测试运行器"""
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.original_runner = IntegratedTestRunner() if IntegratedTestRunner else None
        self.project_tester = ProjectLoadTester() if ProjectLoadTester else None
        
    def run_command(self, command: str, description: str, timeout: int = 300) -> bool:
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
                encoding='utf-8',
                timeout=timeout
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
            
        except subprocess.TimeoutExpired:
            end_time = time.time()
            duration = end_time - start_time
            
            self.test_results[description] = {
                'command': command,
                'success': False,
                'duration': duration,
                'error': f'Command timeout after {timeout} seconds'
            }
            
            print(f"⏰ {description} 超时 (耗时: {duration:.2f}秒)")
            return False
            
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
    
    def run_infrastructure_stress_test(self) -> bool:
        """运行基础设施压力测试"""
        print("\n🏗️ 开始基础设施压力测试")
        
        # 创建多个并发的基础测试
        stress_commands = [
            ("python simple_performance_tester.py --test-type cpu --duration 120", "CPU压力测试"),
            ("python simple_performance_tester.py --test-type memory --duration 120", "内存压力测试"),
            ("python simple_performance_tester.py --test-type disk --duration 120", "磁盘I/O压力测试")
        ]
        
        # 并发执行压力测试
        threads = []
        results = {}
        
        def run_stress_command(cmd, desc):
            results[desc] = self.run_command(cmd, desc, timeout=180)
        
        for cmd, desc in stress_commands:
            thread = threading.Thread(target=run_stress_command, args=(cmd, desc))
            threads.append(thread)
            thread.start()
        
        # 等待所有压力测试完成
        for thread in threads:
            thread.join()
        
        # 检查是否所有测试都成功
        all_success = all(results.values())
        print(f"\n{'✅' if all_success else '❌'} 基础设施压力测试{'完成' if all_success else '部分失败'}")
        
        return all_success
    
    def run_error_injection_test(self) -> bool:
        """运行错误注入测试"""
        print("\n💥 开始错误注入测试")
        
        if not self.project_tester:
            print("❌ 多项目负载测试器不可用，跳过错误注入测试")
            return False
        
        # 配置错误场景项目
        error_configs = [
            {'type': 'java', 'name': 'error-prone-service', 'introduce_error': True},
            {'type': 'rust', 'name': 'failing-processor', 'introduce_error': True},
            {'type': 'nodejs', 'name': 'buggy-api', 'introduce_error': True}
        ]
        
        try:
            # 运行错误注入测试（较短时间）
            self.project_tester.run_concurrent_load_test(error_configs, duration=180)
            
            # 检查是否产生了预期的错误
            build_failures = self.project_tester.metrics['build_failure']
            runtime_failures = self.project_tester.metrics['runtime_failure']
            
            # 错误注入测试成功的标准是产生了错误
            success = build_failures > 0 or runtime_failures > 0
            
            print(f"\n{'✅' if success else '❌'} 错误注入测试{'成功' if success else '失败'}")
            print(f"构建错误: {build_failures}, 运行时错误: {runtime_failures}")
            
            return success
            
        except Exception as e:
            print(f"❌ 错误注入测试异常: {e}")
            return False
    
    def run_recovery_test(self) -> bool:
        """运行错误恢复测试"""
        print("\n🔄 开始错误恢复测试")
        
        if not self.project_tester:
            print("❌ 多项目负载测试器不可用，跳过恢复测试")
            return False
        
        # 先运行错误场景
        print("第一阶段: 引入错误")
        error_configs = [
            {'type': 'java', 'name': 'recovery-test-java', 'introduce_error': True},
            {'type': 'nodejs', 'name': 'recovery-test-node', 'introduce_error': True}
        ]
        
        try:
            self.project_tester.run_concurrent_load_test(error_configs, duration=60)
            initial_failures = self.project_tester.metrics['build_failure'] + self.project_tester.metrics['runtime_failure']
            
            # 重置指标
            self.project_tester.metrics = {
                'build_success': 0,
                'build_failure': 0,
                'runtime_success': 0,
                'runtime_failure': 0,
                'performance_tests': 0
            }
            
            # 再运行正常场景（模拟修复后）
            print("\n第二阶段: 错误修复后测试")
            recovery_configs = [
                {'type': 'java', 'name': 'recovery-test-java-fixed', 'introduce_error': False},
                {'type': 'nodejs', 'name': 'recovery-test-node-fixed', 'introduce_error': False}
            ]
            
            self.project_tester.run_concurrent_load_test(recovery_configs, duration=60)
            recovery_successes = self.project_tester.metrics['build_success'] + self.project_tester.metrics['runtime_success']
            
            # 恢复测试成功的标准是先有错误，后有成功
            success = initial_failures > 0 and recovery_successes > 0
            
            print(f"\n{'✅' if success else '❌'} 错误恢复测试{'成功' if success else '失败'}")
            print(f"初始错误: {initial_failures}, 恢复后成功: {recovery_successes}")
            
            return success
            
        except Exception as e:
            print(f"❌ 错误恢复测试异常: {e}")
            return False
    
    def run_comprehensive_load_test(self) -> bool:
        """运行全面负载测试"""
        print("\n🚀 开始全面负载测试")
        
        if not self.project_tester:
            print("❌ 多项目负载测试器不可用，跳过全面负载测试")
            return False
        
        # 配置全面测试场景
        comprehensive_configs = [
            # Java项目
            {'type': 'java', 'name': 'microservice-a', 'introduce_error': False},
            {'type': 'java', 'name': 'microservice-b', 'introduce_error': False},
            {'type': 'java', 'name': 'batch-job', 'introduce_error': False},
            
            # Rust项目
            {'type': 'rust', 'name': 'high-perf-api', 'introduce_error': False},
            {'type': 'rust', 'name': 'data-pipeline', 'introduce_error': False},
            
            # Node.js项目
            {'type': 'nodejs', 'name': 'web-frontend', 'introduce_error': False},
            {'type': 'nodejs', 'name': 'websocket-service', 'introduce_error': False},
            {'type': 'nodejs', 'name': 'api-gateway', 'introduce_error': False},
            
            # 混合错误场景
            {'type': 'java', 'name': 'unstable-service', 'introduce_error': True},
            {'type': 'rust', 'name': 'flaky-processor', 'introduce_error': True}
        ]
        
        try:
            # 运行全面负载测试
            self.project_tester.run_concurrent_load_test(comprehensive_configs, duration=300)
            
            # 评估测试结果
            total_tests = sum(self.project_tester.metrics.values())
            successful_tests = self.project_tester.metrics['build_success'] + self.project_tester.metrics['runtime_success']
            
            success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
            success = success_rate >= 70  # 70%成功率视为通过
            
            print(f"\n{'✅' if success else '❌'} 全面负载测试{'通过' if success else '未通过'}")
            print(f"成功率: {success_rate:.1f}% ({successful_tests}/{total_tests})")
            
            return success
            
        except Exception as e:
            print(f"❌ 全面负载测试异常: {e}")
            return False
    
    def run_original_tests(self) -> bool:
        """运行原有的AIOps测试"""
        print("\n📊 开始原有AIOps测试套件")
        
        if not self.original_runner:
            print("❌ 原有测试运行器不可用，使用简化版本")
            return self._run_simplified_original_tests()
        
        try:
            # 运行原有的快速测试
            self.original_runner.run_quick_test()
            
            # 检查原有测试结果
            if hasattr(self.original_runner, 'test_results'):
                original_results = self.original_runner.test_results
                successful_original = sum(1 for result in original_results.values() if result.get('success', False))
                total_original = len(original_results)
                
                success = successful_original >= total_original * 0.8  # 80%成功率
                
                print(f"\n{'✅' if success else '❌'} 原有AIOps测试{'通过' if success else '未通过'}")
                print(f"成功率: {successful_original}/{total_original}")
                
                return success
            else:
                print("✅ 原有AIOps测试完成（无详细结果）")
                return True
                
        except Exception as e:
            print(f"❌ 原有AIOps测试异常: {e}")
            return False
    
    def _run_simplified_original_tests(self) -> bool:
        """运行简化版原有测试"""
        simplified_tests = [
            ("python web_simulator.py --duration 30", "Web应用监控简化测试"),
            ("python database_simulator.py --duration 60", "数据库监控简化测试"),
            ("python system_monitor.py --duration 45", "系统监控简化测试"),
            ("python simple_performance_tester.py --test-type cpu --duration 30", "性能测试")
        ]
        
        success_count = 0
        for cmd, desc in simplified_tests:
            if self.run_command(cmd, desc, timeout=120):
                success_count += 1
        
        success = success_count >= len(simplified_tests) * 0.75  # 75%成功率
        print(f"\n{'✅' if success else '❌'} 简化AIOps测试{'通过' if success else '未通过'}")
        print(f"成功率: {success_count}/{len(simplified_tests)}")
        
        return success
    
    def run_extended_test_suite(self, test_mode: str = 'comprehensive'):
        """运行扩展测试套件"""
        print("🎯 开始扩展AIOps测试套件")
        print(f"测试模式: {test_mode}")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.start_time = time.time()
        
        # 定义不同模式的测试序列
        if test_mode == 'quick':
            test_sequence = [
                ('原有AIOps测试', self.run_original_tests),
                ('基础设施压力测试', self.run_infrastructure_stress_test)
            ]
        elif test_mode == 'error-focused':
            test_sequence = [
                ('错误注入测试', self.run_error_injection_test),
                ('错误恢复测试', self.run_recovery_test),
                ('基础设施压力测试', self.run_infrastructure_stress_test)
            ]
        elif test_mode == 'comprehensive':
            test_sequence = [
                ('原有AIOps测试', self.run_original_tests),
                ('基础设施压力测试', self.run_infrastructure_stress_test),
                ('错误注入测试', self.run_error_injection_test),
                ('错误恢复测试', self.run_recovery_test),
                ('全面负载测试', self.run_comprehensive_load_test)
            ]
        else:
            print(f"❌ 未知测试模式: {test_mode}")
            return
        
        # 执行测试序列
        test_results_summary = {}
        for test_name, test_func in test_sequence:
            print(f"\n{'='*60}")
            print(f"开始执行: {test_name}")
            print(f"{'='*60}")
            
            try:
                result = test_func()
                test_results_summary[test_name] = result
                print(f"\n{'✅' if result else '❌'} {test_name} {'完成' if result else '失败'}")
            except Exception as e:
                test_results_summary[test_name] = False
                print(f"\n❌ {test_name} 异常: {e}")
            
            # 测试间隔
            time.sleep(3)
        
        self.end_time = time.time()
        
        # 生成最终报告
        self._generate_extended_test_report(test_results_summary, test_mode)
    
    def _generate_extended_test_report(self, test_results_summary: Dict[str, bool], test_mode: str):
        """生成扩展测试报告"""
        total_duration = self.end_time - self.start_time
        successful_suites = sum(1 for result in test_results_summary.values() if result)
        total_suites = len(test_results_summary)
        
        print("\n" + "="*80)
        print("🎯 扩展AIOps测试套件执行完成")
        print("="*80)
        print(f"测试模式: {test_mode}")
        print(f"总耗时: {total_duration:.2f} 秒")
        print(f"测试套件总数: {total_suites}")
        print(f"成功套件: {successful_suites}")
        print(f"失败套件: {total_suites - successful_suites}")
        print(f"套件成功率: {(successful_suites/total_suites)*100:.1f}%")
        
        print("\n📊 测试套件详细结果:")
        for suite_name, result in test_results_summary.items():
            status = "✅" if result else "❌"
            print(f"{status} {suite_name}")
        
        # 汇总所有测试结果
        all_individual_tests = len(self.test_results)
        successful_individual_tests = sum(1 for result in self.test_results.values() if result.get('success', False))
        
        if all_individual_tests > 0:
            print(f"\n📈 个别测试统计:")
            print(f"总测试数: {all_individual_tests}")
            print(f"成功测试: {successful_individual_tests}")
            print(f"个别测试成功率: {(successful_individual_tests/all_individual_tests)*100:.1f}%")
        
        # 项目负载测试统计
        if self.project_tester and hasattr(self.project_tester, 'metrics'):
            metrics = self.project_tester.metrics
            total_project_tests = sum(metrics.values())
            if total_project_tests > 0:
                print(f"\n🏗️ 项目负载测试统计:")
                print(f"构建成功: {metrics['build_success']}")
                print(f"构建失败: {metrics['build_failure']}")
                print(f"运行成功: {metrics['runtime_success']}")
                print(f"运行失败: {metrics['runtime_failure']}")
        
        # 保存综合报告
        report_data = {
            'test_suite': '扩展AIOps测试套件',
            'test_mode': test_mode,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat(),
            'total_duration': total_duration,
            'suite_results': test_results_summary,
            'suite_success_rate': (successful_suites/total_suites)*100,
            'individual_test_results': self.test_results,
            'individual_success_rate': (successful_individual_tests/all_individual_tests)*100 if all_individual_tests > 0 else 0,
            'project_load_metrics': self.project_tester.metrics if self.project_tester else None
        }
        
        # 创建报告目录
        report_dir = Path('extended_test_reports')
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = report_dir / f'extended_aiops_test_{test_mode}_{timestamp}.json'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        # 生成测试建议
        self._generate_test_recommendations(test_results_summary, successful_suites, total_suites)
    
    def _generate_test_recommendations(self, test_results: Dict[str, bool], successful_suites: int, total_suites: int):
        """生成测试建议"""
        print("\n💡 测试建议:")
        
        success_rate = (successful_suites / total_suites) * 100
        
        if success_rate >= 90:
            print("🎉 系统表现优秀！所有测试套件基本通过。")
            print("建议: 可以考虑增加更复杂的负载场景或更长时间的压力测试。")
        elif success_rate >= 70:
            print("✅ 系统表现良好，大部分测试通过。")
            failed_tests = [name for name, result in test_results.items() if not result]
            if failed_tests:
                print(f"需要关注的测试: {', '.join(failed_tests)}")
        elif success_rate >= 50:
            print("⚠️ 系统存在一些问题，需要优化。")
            failed_tests = [name for name, result in test_results.items() if not result]
            print(f"失败的测试: {', '.join(failed_tests)}")
            print("建议: 检查系统资源配置和错误处理机制。")
        else:
            print("🚨 系统存在严重问题，需要立即处理。")
            print("建议: 全面检查系统配置、资源分配和代码质量。")
        
        print("\n📋 后续行动项:")
        print("1. 分析失败测试的详细日志")
        print("2. 检查系统资源使用情况")
        print("3. 优化错误处理和恢复机制")
        print("4. 考虑增加监控和告警")
        print("5. 定期运行测试以确保系统稳定性")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='扩展AIOps综合测试运行器')
    parser.add_argument(
        '--mode',
        choices=['quick', 'comprehensive', 'error-focused'],
        default='comprehensive',
        help='测试模式: quick=快速测试, comprehensive=全面测试, error-focused=错误场景测试'
    )
    
    args = parser.parse_args()
    
    runner = ExtendedTestRunner()
    runner.run_extended_test_suite(args.mode)

if __name__ == '__main__':
    main()