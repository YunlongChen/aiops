#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试场景快速启动脚本

该脚本提供了一个统一的入口点来运行各种测试场景，包括业务场景模拟、异常检测测试、
压力测试等。支持交互式菜单和命令行参数两种使用方式。

Author: AIOps Team
Date: 2025-01-10
"""

import os
import sys
import json
import time
import argparse
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum
import logging

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scenario_generator import ScenarioGenerator, ScenarioType
from anomaly_simulator import AnomalySimulator, AnomalyType
from stress_tester import StressTester, StressTestType, TestSeverity
from test_runner import TestRunner


class TestMode(Enum):
    """测试模式枚举"""
    INTERACTIVE = "interactive"
    BUSINESS_SCENARIOS = "business"
    ANOMALY_DETECTION = "anomaly"
    STRESS_TEST = "stress"
    FULL_SUITE = "full"
    CUSTOM = "custom"


class QuickTestRunner:
    """快速测试运行器"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        self.running_processes = []
        self.test_results = {}
        
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("QuickTestRunner")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def show_menu(self):
        """显示交互式菜单"""
        print("\n" + "="*60)
        print("           AIOps 测试场景快速启动器")
        print("="*60)
        print("1. 业务场景模拟测试")
        print("2. 异常检测测试")
        print("3. 系统压力测试")
        print("4. Web应用模拟")
        print("5. 数据库性能测试")
        print("6. 系统监控测试")
        print("7. 告警系统测试")
        print("8. 完整测试套件")
        print("9. 自定义测试配置")
        print("10. 查看测试结果")
        print("11. 停止所有测试")
        print("0. 退出")
        print("="*60)
    
    def run_interactive_mode(self):
        """运行交互式模式"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\n请选择测试类型 (0-11): ").strip()
                
                if choice == "0":
                    print("正在退出...")
                    self.cleanup()
                    break
                elif choice == "1":
                    self.run_business_scenarios()
                elif choice == "2":
                    self.run_anomaly_detection_tests()
                elif choice == "3":
                    self.run_stress_tests()
                elif choice == "4":
                    self.run_web_simulation()
                elif choice == "5":
                    self.run_database_tests()
                elif choice == "6":
                    self.run_system_monitoring()
                elif choice == "7":
                    self.run_alert_tests()
                elif choice == "8":
                    self.run_full_test_suite()
                elif choice == "9":
                    self.run_custom_tests()
                elif choice == "10":
                    self.show_test_results()
                elif choice == "11":
                    self.stop_all_tests()
                else:
                    print("无效选择，请重新输入。")
                
                input("\n按回车键继续...")
            
            except KeyboardInterrupt:
                print("\n正在退出...")
                self.cleanup()
                break
            except Exception as e:
                print(f"错误: {e}")
                input("\n按回车键继续...")
    
    def run_business_scenarios(self):
        """运行业务场景测试"""
        print("\n=== 业务场景模拟测试 ===")
        
        # 获取用户输入
        duration = self._get_user_input("测试持续时间 (分钟)", "10", int)
        scenario_count = self._get_user_input("场景数量", "5", int)
        
        print(f"\n正在生成 {scenario_count} 个业务场景，持续 {duration} 分钟...")
        
        try:
            # 创建场景生成器
            generator = ScenarioGenerator()
            
            # 生成不同类型的场景
            scenarios = []
            scenario_types = [ScenarioType.WEB_APPLICATION, ScenarioType.DATABASE, ScenarioType.SYSTEM_RESOURCE]
            
            for i in range(scenario_count):
                scenario_type = scenario_types[i % len(scenario_types)]
                
                if scenario_type == ScenarioType.WEB_APPLICATION:
                    metrics = generator.generate_web_application_metrics(
                        duration_minutes=duration,
                        request_rate=100 + i * 20
                    )
                elif scenario_type == ScenarioType.DATABASE:
                    metrics = generator.generate_database_metrics(
                        duration_minutes=duration,
                        query_rate=50 + i * 10
                    )
                else:
                    metrics = generator.generate_system_metrics(
                        duration_minutes=duration,
                        cpu_base=30 + i * 10
                    )
                
                scenarios.append((scenario_type, metrics))
            
            # 保存场景数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"./test_results/business_scenarios_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            for i, (scenario_type, metrics) in enumerate(scenarios):
                filename = f"{scenario_type.value}_scenario_{i+1}.json"
                generator.save_to_file(metrics, os.path.join(output_dir, filename))
            
            print(f"✓ 业务场景数据已生成并保存到: {output_dir}")
            
            # 记录测试结果
            self.test_results["business_scenarios"] = {
                "status": "completed",
                "timestamp": timestamp,
                "output_dir": output_dir,
                "scenario_count": scenario_count,
                "duration_minutes": duration
            }
        
        except Exception as e:
            print(f"✗ 业务场景测试失败: {e}")
            self.test_results["business_scenarios"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_anomaly_detection_tests(self):
        """运行异常检测测试"""
        print("\n=== 异常检测测试 ===")
        
        # 获取用户输入
        anomaly_types = self._select_anomaly_types()
        duration = self._get_user_input("测试持续时间 (分钟)", "15", int)
        
        print(f"\n正在生成异常检测测试数据，持续 {duration} 分钟...")
        
        try:
            simulator = AnomalySimulator()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"./test_results/anomaly_detection_{timestamp}"
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            
            for anomaly_type in anomaly_types:
                print(f"正在生成 {anomaly_type.value} 异常场景...")
                
                # 生成正常数据
                normal_data = list(range(100))
                
                # 应用异常
                anomalous_data = simulator.apply_anomaly(normal_data, anomaly_type)
                
                # 保存数据
                result_data = {
                    "anomaly_type": anomaly_type.value,
                    "normal_data": normal_data,
                    "anomalous_data": anomalous_data,
                    "timestamp": datetime.now().isoformat()
                }
                
                filename = f"{anomaly_type.value}_anomaly.json"
                with open(os.path.join(output_dir, filename), 'w') as f:
                    json.dump(result_data, f, indent=2)
                
                results.append(result_data)
            
            print(f"✓ 异常检测测试数据已生成并保存到: {output_dir}")
            
            # 记录测试结果
            self.test_results["anomaly_detection"] = {
                "status": "completed",
                "timestamp": timestamp,
                "output_dir": output_dir,
                "anomaly_types": [t.value for t in anomaly_types],
                "duration_minutes": duration
            }
        
        except Exception as e:
            print(f"✗ 异常检测测试失败: {e}")
            self.test_results["anomaly_detection"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_stress_tests(self):
        """运行压力测试"""
        print("\n=== 系统压力测试 ===")
        
        # 获取用户输入
        test_types = self._select_stress_test_types()
        severity = self._select_test_severity()
        duration = self._get_user_input("测试持续时间 (分钟)", "5", int)
        
        print(f"\n正在运行压力测试 ({severity.value} 强度)，持续 {duration} 分钟...")
        
        try:
            tester = StressTester()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"./test_results/stress_test_{timestamp}"
            
            results = []
            
            for test_type in test_types:
                print(f"正在运行 {test_type.value} 压力测试...")
                
                config = tester.create_test_configuration(
                    test_type=test_type,
                    severity=severity,
                    duration_seconds=duration * 60
                )
                
                result = tester.run_stress_test(config)
                results.append(result)
                
                print(f"✓ {test_type.value} 测试完成: {result.status.value}")
                print(f"  操作数: {result.total_operations:,}")
                print(f"  峰值CPU: {result.peak_cpu_usage:.1f}%")
                print(f"  峰值内存: {result.peak_memory_usage:.1f}%")
            
            # 导出结果
            tester.export_results(output_dir)
            
            print(f"✓ 压力测试完成，结果已保存到: {output_dir}")
            
            # 记录测试结果
            self.test_results["stress_test"] = {
                "status": "completed",
                "timestamp": timestamp,
                "output_dir": output_dir,
                "test_types": [t.value for t in test_types],
                "severity": severity.value,
                "duration_minutes": duration,
                "results_summary": [
                    {
                        "test_type": r.test_type.value,
                        "status": r.status.value,
                        "operations": r.total_operations,
                        "peak_cpu": r.peak_cpu_usage,
                        "peak_memory": r.peak_memory_usage
                    } for r in results
                ]
            }
        
        except Exception as e:
            print(f"✗ 压力测试失败: {e}")
            self.test_results["stress_test"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_web_simulation(self):
        """运行Web应用模拟"""
        print("\n=== Web应用模拟 ===")
        
        port = self._get_user_input("Web服务器端口", "8080", int)
        duration = self._get_user_input("运行时间 (分钟)", "10", int)
        
        print(f"\n正在启动Web应用模拟器 (端口: {port})...")
        
        try:
            # 启动Web模拟器
            cmd = [
                sys.executable, "web_simulator.py",
                "--port", str(port),
                "--duration", str(duration * 60)
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes.append(("web_simulator", process))
            
            print(f"✓ Web应用模拟器已启动 (PID: {process.pid})")
            print(f"  访问地址: http://localhost:{port}")
            print(f"  运行时间: {duration} 分钟")
            
            # 记录测试结果
            self.test_results["web_simulation"] = {
                "status": "running",
                "pid": process.pid,
                "port": port,
                "duration_minutes": duration,
                "url": f"http://localhost:{port}"
            }
        
        except Exception as e:
            print(f"✗ Web应用模拟启动失败: {e}")
            self.test_results["web_simulation"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_database_tests(self):
        """运行数据库性能测试"""
        print("\n=== 数据库性能测试 ===")
        
        db_type = self._select_database_type()
        duration = self._get_user_input("测试持续时间 (分钟)", "10", int)
        concurrent_connections = self._get_user_input("并发连接数", "10", int)
        
        print(f"\n正在运行 {db_type} 数据库性能测试...")
        
        try:
            # 启动数据库模拟器
            cmd = [
                sys.executable, "database_simulator.py",
                "--db-type", db_type,
                "--duration", str(duration * 60),
                "--connections", str(concurrent_connections)
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes.append(("database_simulator", process))
            
            print(f"✓ 数据库性能测试已启动 (PID: {process.pid})")
            print(f"  数据库类型: {db_type}")
            print(f"  并发连接: {concurrent_connections}")
            print(f"  运行时间: {duration} 分钟")
            
            # 记录测试结果
            self.test_results["database_test"] = {
                "status": "running",
                "pid": process.pid,
                "db_type": db_type,
                "duration_minutes": duration,
                "concurrent_connections": concurrent_connections
            }
        
        except Exception as e:
            print(f"✗ 数据库性能测试启动失败: {e}")
            self.test_results["database_test"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_system_monitoring(self):
        """运行系统监控测试"""
        print("\n=== 系统监控测试 ===")
        
        duration = self._get_user_input("监控持续时间 (分钟)", "15", int)
        interval = self._get_user_input("监控间隔 (秒)", "5", int)
        
        print(f"\n正在启动系统监控 (间隔: {interval}秒)...")
        
        try:
            # 启动系统监控器
            cmd = [
                sys.executable, "system_monitor.py",
                "--duration", str(duration * 60),
                "--interval", str(interval),
                "--export-metrics"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes.append(("system_monitor", process))
            
            print(f"✓ 系统监控已启动 (PID: {process.pid})")
            print(f"  监控间隔: {interval} 秒")
            print(f"  运行时间: {duration} 分钟")
            
            # 记录测试结果
            self.test_results["system_monitoring"] = {
                "status": "running",
                "pid": process.pid,
                "duration_minutes": duration,
                "interval_seconds": interval
            }
        
        except Exception as e:
            print(f"✗ 系统监控启动失败: {e}")
            self.test_results["system_monitoring"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_alert_tests(self):
        """运行告警系统测试"""
        print("\n=== 告警系统测试 ===")
        
        alert_count = self._get_user_input("告警数量", "20", int)
        duration = self._get_user_input("测试持续时间 (分钟)", "10", int)
        
        print(f"\n正在生成 {alert_count} 个告警事件...")
        
        try:
            # 启动告警模拟器
            cmd = [
                sys.executable, "alert_simulator.py",
                "--alert-count", str(alert_count),
                "--duration", str(duration * 60)
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes.append(("alert_simulator", process))
            
            print(f"✓ 告警系统测试已启动 (PID: {process.pid})")
            print(f"  告警数量: {alert_count}")
            print(f"  运行时间: {duration} 分钟")
            
            # 记录测试结果
            self.test_results["alert_test"] = {
                "status": "running",
                "pid": process.pid,
                "alert_count": alert_count,
                "duration_minutes": duration
            }
        
        except Exception as e:
            print(f"✗ 告警系统测试启动失败: {e}")
            self.test_results["alert_test"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_full_test_suite(self):
        """运行完整测试套件"""
        print("\n=== 完整测试套件 ===")
        print("这将运行所有测试场景，可能需要较长时间...")
        
        confirm = input("确认运行完整测试套件? (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消完整测试套件")
            return
        
        print("\n正在启动完整测试套件...")
        
        try:
            # 使用TestRunner运行完整测试
            config_file = "test_config.json"
            if not os.path.exists(config_file):
                print(f"配置文件 {config_file} 不存在")
                return
            
            cmd = [
                sys.executable, "test_runner.py",
                "--config", config_file,
                "--run-all"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes.append(("full_test_suite", process))
            
            print(f"✓ 完整测试套件已启动 (PID: {process.pid})")
            
            # 记录测试结果
            self.test_results["full_test_suite"] = {
                "status": "running",
                "pid": process.pid,
                "config_file": config_file
            }
        
        except Exception as e:
            print(f"✗ 完整测试套件启动失败: {e}")
            self.test_results["full_test_suite"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def run_custom_tests(self):
        """运行自定义测试配置"""
        print("\n=== 自定义测试配置 ===")
        
        config_file = input("请输入配置文件路径 (默认: test_config.json): ").strip()
        if not config_file:
            config_file = "test_config.json"
        
        if not os.path.exists(config_file):
            print(f"配置文件 {config_file} 不存在")
            return
        
        print(f"\n正在使用配置文件运行自定义测试: {config_file}")
        
        try:
            cmd = [
                sys.executable, "test_runner.py",
                "--config", config_file
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.running_processes.append(("custom_test", process))
            
            print(f"✓ 自定义测试已启动 (PID: {process.pid})")
            
            # 记录测试结果
            self.test_results["custom_test"] = {
                "status": "running",
                "pid": process.pid,
                "config_file": config_file
            }
        
        except Exception as e:
            print(f"✗ 自定义测试启动失败: {e}")
            self.test_results["custom_test"] = {
                "status": "failed",
                "error": str(e)
            }
    
    def show_test_results(self):
        """显示测试结果"""
        print("\n=== 测试结果概览 ===")
        
        if not self.test_results:
            print("暂无测试结果")
            return
        
        for test_name, result in self.test_results.items():
            print(f"\n{test_name.upper()}:")
            print(f"  状态: {result.get('status', 'unknown')}")
            
            if result.get('status') == 'running':
                pid = result.get('pid')
                if pid:
                    # 检查进程是否还在运行
                    try:
                        os.kill(pid, 0)  # 不发送信号，只检查进程是否存在
                        print(f"  进程ID: {pid} (运行中)")
                    except OSError:
                        print(f"  进程ID: {pid} (已结束)")
                        result['status'] = 'completed'
            
            elif result.get('status') == 'completed':
                if 'output_dir' in result:
                    print(f"  输出目录: {result['output_dir']}")
                if 'duration_minutes' in result:
                    print(f"  持续时间: {result['duration_minutes']} 分钟")
            
            elif result.get('status') == 'failed':
                if 'error' in result:
                    print(f"  错误: {result['error']}")
            
            # 显示其他相关信息
            for key, value in result.items():
                if key not in ['status', 'pid', 'output_dir', 'duration_minutes', 'error']:
                    print(f"  {key}: {value}")
    
    def stop_all_tests(self):
        """停止所有运行中的测试"""
        print("\n=== 停止所有测试 ===")
        
        if not self.running_processes:
            print("没有运行中的测试进程")
            return
        
        stopped_count = 0
        
        for test_name, process in self.running_processes:
            try:
                if process.poll() is None:  # 进程还在运行
                    print(f"正在停止 {test_name} (PID: {process.pid})...")
                    process.terminate()
                    
                    # 等待进程结束
                    try:
                        process.wait(timeout=5)
                        print(f"✓ {test_name} 已停止")
                        stopped_count += 1
                    except subprocess.TimeoutExpired:
                        print(f"强制终止 {test_name}...")
                        process.kill()
                        process.wait()
                        stopped_count += 1
                else:
                    print(f"{test_name} 已经结束")
            
            except Exception as e:
                print(f"停止 {test_name} 时出错: {e}")
        
        self.running_processes.clear()
        print(f"\n已停止 {stopped_count} 个测试进程")
    
    def cleanup(self):
        """清理资源"""
        print("正在清理资源...")
        self.stop_all_tests()
    
    def _get_user_input(self, prompt: str, default: str, input_type=str):
        """获取用户输入"""
        while True:
            try:
                value = input(f"{prompt} (默认: {default}): ").strip()
                if not value:
                    value = default
                return input_type(value)
            except ValueError:
                print(f"无效输入，请输入 {input_type.__name__} 类型的值")
    
    def _select_anomaly_types(self) -> List[AnomalyType]:
        """选择异常类型"""
        print("\n可用的异常类型:")
        anomaly_types = list(AnomalyType)
        
        for i, anomaly_type in enumerate(anomaly_types, 1):
            print(f"{i}. {anomaly_type.value}")
        
        selected = input("\n请选择异常类型 (用逗号分隔，默认: 1,2,3): ").strip()
        if not selected:
            selected = "1,2,3"
        
        try:
            indices = [int(x.strip()) - 1 for x in selected.split(',')]
            return [anomaly_types[i] for i in indices if 0 <= i < len(anomaly_types)]
        except (ValueError, IndexError):
            print("无效选择，使用默认异常类型")
            return anomaly_types[:3]
    
    def _select_stress_test_types(self) -> List[StressTestType]:
        """选择压力测试类型"""
        print("\n可用的压力测试类型:")
        test_types = [StressTestType.CPU, StressTestType.MEMORY, StressTestType.DISK_IO, StressTestType.NETWORK]
        
        for i, test_type in enumerate(test_types, 1):
            print(f"{i}. {test_type.value}")
        
        selected = input("\n请选择测试类型 (用逗号分隔，默认: 1,2): ").strip()
        if not selected:
            selected = "1,2"
        
        try:
            indices = [int(x.strip()) - 1 for x in selected.split(',')]
            return [test_types[i] for i in indices if 0 <= i < len(test_types)]
        except (ValueError, IndexError):
            print("无效选择，使用默认测试类型")
            return [StressTestType.CPU, StressTestType.MEMORY]
    
    def _select_test_severity(self) -> TestSeverity:
        """选择测试强度"""
        print("\n测试强度级别:")
        severities = list(TestSeverity)
        
        for i, severity in enumerate(severities, 1):
            print(f"{i}. {severity.value}")
        
        selected = input("\n请选择测试强度 (默认: 2): ").strip()
        if not selected:
            selected = "2"
        
        try:
            index = int(selected) - 1
            if 0 <= index < len(severities):
                return severities[index]
        except ValueError:
            pass
        
        print("无效选择，使用默认强度")
        return TestSeverity.MEDIUM
    
    def _select_database_type(self) -> str:
        """选择数据库类型"""
        db_types = ["mysql", "postgresql", "mongodb", "redis"]
        
        print("\n数据库类型:")
        for i, db_type in enumerate(db_types, 1):
            print(f"{i}. {db_type}")
        
        selected = input("\n请选择数据库类型 (默认: 1): ").strip()
        if not selected:
            selected = "1"
        
        try:
            index = int(selected) - 1
            if 0 <= index < len(db_types):
                return db_types[index]
        except ValueError:
            pass
        
        print("无效选择，使用默认类型")
        return "mysql"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIOps 测试场景快速启动器")
    parser.add_argument("--mode", choices=[m.value for m in TestMode], 
                       default="interactive", help="运行模式")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--duration", type=int, default=10, help="测试持续时间 (分钟)")
    parser.add_argument("--output-dir", default="./test_results", help="输出目录")
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    runner = QuickTestRunner()
    
    try:
        if args.mode == TestMode.INTERACTIVE.value:
            runner.run_interactive_mode()
        
        elif args.mode == TestMode.BUSINESS_SCENARIOS.value:
            runner.run_business_scenarios()
        
        elif args.mode == TestMode.ANOMALY_DETECTION.value:
            runner.run_anomaly_detection_tests()
        
        elif args.mode == TestMode.STRESS_TEST.value:
            runner.run_stress_tests()
        
        elif args.mode == TestMode.FULL_SUITE.value:
            runner.run_full_test_suite()
        
        elif args.mode == TestMode.CUSTOM.value:
            runner.run_custom_tests()
        
        else:
            print(f"不支持的运行模式: {args.mode}")
    
    except KeyboardInterrupt:
        print("\n用户中断")
        runner.cleanup()
    
    except Exception as e:
        print(f"运行错误: {e}")
        runner.cleanup()


if __name__ == "__main__":
    main()