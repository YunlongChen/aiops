#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的AIOps测试运行器
用于验证基本功能
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
import argparse

class SimpleTestRunner:
    """简化的测试运行器"""
    
    def __init__(self):
        """初始化测试运行器"""
        self.test_results = []
        self.start_time = None
        
    def run_command(self, command: str, description: str = "") -> bool:
        """运行命令并记录结果"""
        print(f"\n正在执行: {description or command}")
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            self.test_results.append({
                'test': description or command,
                'success': success,
                'duration': duration,
                'output': result.stdout if success else result.stderr
            })
            
            if success:
                print(f"✓ 成功 (耗时: {duration:.2f}秒)")
            else:
                print(f"✗ 失败 (耗时: {duration:.2f}秒)")
                print(f"错误信息: {result.stderr}")
                
            return success
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"✗ 超时 (耗时: {duration:.2f}秒)")
            self.test_results.append({
                'test': description or command,
                'success': False,
                'duration': duration,
                'output': 'Command timeout'
            })
            return False
        except Exception as e:
            duration = time.time() - start_time
            print(f"✗ 异常: {str(e)} (耗时: {duration:.2f}秒)")
            self.test_results.append({
                'test': description or command,
                'success': False,
                'duration': duration,
                'output': str(e)
            })
            return False
    
    def run_basic_tests(self):
        """运行基础测试"""
        print("=== 开始基础测试 ===")
        self.start_time = datetime.now()
        
        # 测试Python环境
        self.run_command('python --version', 'Python版本检查')
        
        # 测试基础命令
        self.run_command('echo "Hello AIOps"', '基础命令测试')
        
        # 测试文件操作
        self.run_command('dir', '目录列表测试')
        
        # 测试网络连接
        self.run_command('ping -n 1 127.0.0.1', '本地网络测试')
        
        print("\n=== 基础测试完成 ===")
    
    def run_mock_load_test(self):
        """运行模拟负载测试"""
        print("\n=== 开始模拟负载测试 ===")
        
        # 模拟创建项目
        test_dir = Path('mock_test_projects')
        test_dir.mkdir(exist_ok=True)
        
        # 创建简单的测试文件
        java_file = test_dir / 'Test.java'
        java_file.write_text('public class Test { public static void main(String[] args) { System.out.println("Hello Java"); } }')
        
        js_file = test_dir / 'test.js'
        js_file.write_text('console.log("Hello Node.js");')
        
        py_file = test_dir / 'test.py'
        py_file.write_text('print("Hello Python")')
        
        # 测试文件执行
        self.run_command(f'python {py_file}', 'Python文件执行测试')
        
        # 检查Java编译器
        if self.run_command('javac -version', 'Java编译器检查'):
            self.run_command(f'javac {java_file}', 'Java编译测试')
            if (test_dir / 'Test.class').exists():
                self.run_command(f'java -cp {test_dir} Test', 'Java运行测试')
        
        # 检查Node.js
        if self.run_command('node --version', 'Node.js版本检查'):
            self.run_command(f'node {js_file}', 'Node.js执行测试')
        
        print("\n=== 模拟负载测试完成 ===")
    
    def run_error_simulation(self):
        """运行错误模拟测试"""
        print("\n=== 开始错误模拟测试 ===")
        
        # 模拟各种错误场景
        self.run_command('python -c "import non_existent_module"', '模块导入错误测试')
        self.run_command('python -c "print(undefined_variable)"', '变量未定义错误测试')
        self.run_command('python -c "1/0"', '除零错误测试')
        self.run_command('invalid_command_12345', '无效命令错误测试')
        
        print("\n=== 错误模拟测试完成 ===")
    
    def generate_report(self, output_file: str = None):
        """生成测试报告"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds() if self.start_time else 0
        
        successful_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = len(self.test_results) - successful_tests
        
        report = {
            'test_summary': {
                'total_tests': len(self.test_results),
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': f"{(successful_tests/len(self.test_results)*100):.1f}%" if self.test_results else "0%",
                'total_duration': total_duration,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': end_time.isoformat()
            },
            'test_results': self.test_results
        }
        
        # 控制台输出
        print("\n" + "="*50)
        print("测试报告摘要")
        print("="*50)
        print(f"总测试数: {report['test_summary']['total_tests']}")
        print(f"成功测试: {report['test_summary']['successful_tests']}")
        print(f"失败测试: {report['test_summary']['failed_tests']}")
        print(f"成功率: {report['test_summary']['success_rate']}")
        print(f"总耗时: {total_duration:.2f}秒")
        
        # 保存JSON报告
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n详细报告已保存到: {output_file}")
        
        return report

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='简化的AIOps测试运行器')
    parser.add_argument('--mode', choices=['basic', 'load', 'error', 'all'], 
                       default='basic', help='测试模式')
    parser.add_argument('--output', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    runner = SimpleTestRunner()
    
    try:
        if args.mode == 'basic':
            runner.run_basic_tests()
        elif args.mode == 'load':
            runner.run_mock_load_test()
        elif args.mode == 'error':
            runner.run_error_simulation()
        elif args.mode == 'all':
            runner.run_basic_tests()
            runner.run_mock_load_test()
            runner.run_error_simulation()
        
        # 生成报告
        runner.generate_report(args.output)
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {str(e)}")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())