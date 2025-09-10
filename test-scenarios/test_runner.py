#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试运行器

该模块提供了一个统一的测试运行器，可以执行各种测试场景，
包括正常业务场景、异常场景、压力测试等。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import argparse
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
import logging

from scenario_generator import ScenarioGenerator
from anomaly_simulator import AnomalySimulator
from data_pusher import DataPusher


class TestRunner:
    """测试运行器主类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化测试运行器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.logger = self._setup_logger()
        self.generator = ScenarioGenerator(self.config.get("scenario_generator"))
        self.simulator = AnomalySimulator()
        self.pusher = DataPusher(self.config.get("data_pusher"))
        self.running = False
        self.test_results = []
        
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置文件"""
        if config_file:
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config file {config_file}: {e}")
        
        # 返回默认配置
        return {
            "test_scenarios": {
                "normal_business": {
                    "enabled": True,
                    "duration_hours": 2,
                    "data_points_per_minute": 12
                },
                "anomaly_scenarios": {
                    "enabled": True,
                    "scenarios": [
                        "morning_rush_failure",
                        "resource_exhaustion_cascade",
                        "database_crisis"
                    ]
                },
                "stress_test": {
                    "enabled": False,
                    "duration_minutes": 30,
                    "load_multiplier": 5.0
                }
            },
            "output": {
                "save_to_files": True,
                "file_formats": ["json", "prometheus"],
                "output_directory": "./test_output"
            },
            "real_time": {
                "enabled": False,
                "push_to_prometheus": True,
                "push_to_elasticsearch": True,
                "ai_engine_analysis": True
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("TestRunner")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
            
            # 文件处理器
            file_handler = logging.FileHandler('test_runner.log', encoding='utf-8')
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        self.logger.info(f"Received signal {signum}, stopping test runner...")
        self.stop_all_tests()
        sys.exit(0)
    
    def run_normal_business_scenario(self, duration_hours: int = 2) -> Dict[str, Any]:
        """
        运行正常业务场景测试
        
        Args:
            duration_hours: 测试持续时间（小时）
            
        Returns:
            测试结果字典
        """
        self.logger.info(f"Starting normal business scenario test for {duration_hours} hours")
        
        start_time = datetime.now()
        
        # 生成正常业务数据
        web_metrics = self.generator.generate_web_application_metrics(
            duration_minutes=duration_hours * 60
        )
        db_metrics = self.generator.generate_database_metrics(
            duration_minutes=duration_hours * 60
        )
        system_metrics = self.generator.generate_system_metrics(
            duration_minutes=duration_hours * 60
        )
        
        all_metrics = web_metrics + db_metrics + system_metrics
        
        # 保存测试数据
        if self.config["output"]["save_to_files"]:
            self._save_test_data(all_metrics, "normal_business", start_time)
        
        # 统计信息
        result = {
            "scenario_type": "normal_business",
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_hours": duration_hours,
            "total_metrics": len(all_metrics),
            "metrics_by_type": {
                "web_application": len(web_metrics),
                "database": len(db_metrics),
                "system": len(system_metrics)
            },
            "status": "completed"
        }
        
        self.test_results.append(result)
        self.logger.info(f"Normal business scenario completed: {len(all_metrics)} metrics generated")
        
        return result
    
    def run_anomaly_scenario(self, scenario_name: str, duration_hours: int = 6) -> Dict[str, Any]:
        """
        运行异常场景测试
        
        Args:
            scenario_name: 异常场景名称
            duration_hours: 测试持续时间（小时）
            
        Returns:
            测试结果字典
        """
        self.logger.info(f"Starting anomaly scenario test: {scenario_name}")
        
        start_time = datetime.now()
        
        # 生成异常模式
        base_time = start_time
        anomaly_patterns = self.simulator.generate_anomaly_scenario(
            scenario_name, base_time, duration_hours
        )
        
        # 生成基础指标数据
        web_metrics = self.generator.generate_web_application_metrics(
            duration_minutes=duration_hours * 60
        )
        db_metrics = self.generator.generate_database_metrics(
            duration_minutes=duration_hours * 60
        )
        system_metrics = self.generator.generate_system_metrics(
            duration_minutes=duration_hours * 60
        )
        
        all_metrics = web_metrics + db_metrics + system_metrics
        
        # 应用异常模式
        modified_metrics = []
        for metric in all_metrics:
            modified_value = metric.value
            
            for pattern in anomaly_patterns:
                modified_value = self.simulator.apply_anomaly_to_value(
                    modified_value, metric.metric_name, metric.timestamp, pattern
                )
            
            # 创建修改后的指标
            from scenario_generator import MetricData
            modified_metric = MetricData(
                timestamp=metric.timestamp,
                metric_name=metric.metric_name,
                value=modified_value,
                labels=metric.labels,
                scenario_type=metric.scenario_type,
                severity=metric.severity
            )
            modified_metrics.append(modified_metric)
        
        # 保存测试数据和异常时间线
        if self.config["output"]["save_to_files"]:
            self._save_test_data(modified_metrics, f"anomaly_{scenario_name}", start_time)
            self._save_anomaly_timeline(anomaly_patterns, scenario_name, start_time)
        
        # 统计异常影响
        anomaly_stats = self._analyze_anomaly_impact(all_metrics, modified_metrics)
        
        result = {
            "scenario_type": "anomaly",
            "scenario_name": scenario_name,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_hours": duration_hours,
            "total_metrics": len(modified_metrics),
            "anomaly_patterns": len(anomaly_patterns),
            "anomaly_impact": anomaly_stats,
            "status": "completed"
        }
        
        self.test_results.append(result)
        self.logger.info(f"Anomaly scenario '{scenario_name}' completed: {len(anomaly_patterns)} patterns applied")
        
        return result
    
    def run_stress_test(self, duration_minutes: int = 30, load_multiplier: float = 5.0) -> Dict[str, Any]:
        """
        运行压力测试
        
        Args:
            duration_minutes: 测试持续时间（分钟）
            load_multiplier: 负载倍数
            
        Returns:
            测试结果字典
        """
        self.logger.info(f"Starting stress test for {duration_minutes} minutes with {load_multiplier}x load")
        
        start_time = datetime.now()
        
        # 修改配置以增加负载
        stress_config = self.generator.config.copy()
        for category in ["web_application", "database", "system"]:
            if category in stress_config:
                for key, value in stress_config[category].items():
                    if isinstance(value, (int, float)) and key != "anomaly_probability":
                        stress_config[category][key] = value * load_multiplier
        
        # 创建压力测试生成器
        stress_generator = ScenarioGenerator(stress_config)
        
        # 生成高负载数据
        web_metrics = stress_generator.generate_web_application_metrics(
            duration_minutes=duration_minutes
        )
        db_metrics = stress_generator.generate_database_metrics(
            duration_minutes=duration_minutes
        )
        system_metrics = stress_generator.generate_system_metrics(
            duration_minutes=duration_minutes
        )
        
        all_metrics = web_metrics + db_metrics + system_metrics
        
        # 保存测试数据
        if self.config["output"]["save_to_files"]:
            self._save_test_data(all_metrics, "stress_test", start_time)
        
        # 分析压力测试结果
        stress_stats = self._analyze_stress_test_results(all_metrics, load_multiplier)
        
        result = {
            "scenario_type": "stress_test",
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "load_multiplier": load_multiplier,
            "total_metrics": len(all_metrics),
            "stress_analysis": stress_stats,
            "status": "completed"
        }
        
        self.test_results.append(result)
        self.logger.info(f"Stress test completed: {len(all_metrics)} metrics under {load_multiplier}x load")
        
        return result
    
    def start_real_time_testing(self, scenario_name: Optional[str] = None):
        """
        启动实时测试
        
        Args:
            scenario_name: 可选的异常场景名称
        """
        if not self.config["real_time"]["enabled"]:
            self.logger.warning("Real-time testing is disabled in configuration")
            return
        
        self.running = True
        self.logger.info("Starting real-time testing...")
        
        # 准备异常模式（如果指定）
        anomaly_patterns = None
        if scenario_name:
            base_time = datetime.now()
            anomaly_patterns = self.simulator.generate_anomaly_scenario(
                scenario_name, base_time, duration_hours=24
            )
            self.logger.info(f"Applied anomaly scenario: {scenario_name}")
        
        # 启动实时数据推送
        self.pusher.start_real_time_push(
            self.generator,
            self.simulator if anomaly_patterns else None,
            anomaly_patterns
        )
        
        self.logger.info("Real-time testing started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all_tests()
    
    def stop_all_tests(self):
        """停止所有测试"""
        self.running = False
        self.pusher.stop_real_time_push()
        self.logger.info("All tests stopped")
    
    def _save_test_data(self, metrics, test_type: str, start_time: datetime):
        """保存测试数据到文件"""
        import os
        
        output_dir = self.config["output"]["output_directory"]
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        
        for format_type in self.config["output"]["file_formats"]:
            filename = os.path.join(output_dir, f"{test_type}_{timestamp}.{format_type}")
            
            if format_type == "json":
                self.generator.save_metrics_to_file(metrics, filename, "json")
            elif format_type == "prometheus":
                self.generator.save_metrics_to_file(metrics, filename, "prometheus")
    
    def _save_anomaly_timeline(self, patterns, scenario_name: str, start_time: datetime):
        """保存异常时间线"""
        import os
        
        output_dir = self.config["output"]["output_directory"]
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(output_dir, f"anomaly_timeline_{scenario_name}_{timestamp}.json")
        
        timeline = self.simulator.export_anomaly_timeline(patterns)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(timeline, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Anomaly timeline saved to {filename}")
    
    def _analyze_anomaly_impact(self, original_metrics, modified_metrics) -> Dict[str, Any]:
        """分析异常影响"""
        impact_stats = {
            "metrics_affected": 0,
            "average_impact_ratio": 0.0,
            "max_impact_ratio": 0.0,
            "severely_affected_metrics": 0
        }
        
        if len(original_metrics) != len(modified_metrics):
            return impact_stats
        
        impact_ratios = []
        severely_affected = 0
        
        for orig, mod in zip(original_metrics, modified_metrics):
            if orig.value > 0:
                ratio = abs(mod.value - orig.value) / orig.value
                impact_ratios.append(ratio)
                
                if ratio > 0.1:  # 10%以上变化认为受到影响
                    impact_stats["metrics_affected"] += 1
                
                if ratio > 0.5:  # 50%以上变化认为严重影响
                    severely_affected += 1
        
        if impact_ratios:
            impact_stats["average_impact_ratio"] = sum(impact_ratios) / len(impact_ratios)
            impact_stats["max_impact_ratio"] = max(impact_ratios)
            impact_stats["severely_affected_metrics"] = severely_affected
        
        return impact_stats
    
    def _analyze_stress_test_results(self, metrics, load_multiplier: float) -> Dict[str, Any]:
        """分析压力测试结果"""
        from collections import defaultdict
        
        stats = defaultdict(list)
        
        # 按指标类型分组统计
        for metric in metrics:
            stats[metric.metric_name].append(metric.value)
        
        analysis = {
            "load_multiplier": load_multiplier,
            "metric_statistics": {},
            "performance_summary": {}
        }
        
        for metric_name, values in stats.items():
            if values:
                analysis["metric_statistics"][metric_name] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "median": sorted(values)[len(values) // 2]
                }
        
        # 性能摘要
        response_times = stats.get("http_request_duration_ms", [])
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            analysis["performance_summary"]["average_response_time_ms"] = avg_response_time
            analysis["performance_summary"]["slow_requests_ratio"] = \
                len([rt for rt in response_times if rt > 1000]) / len(response_times)
        
        error_rates = stats.get("http_error_rate", [])
        if error_rates:
            avg_error_rate = sum(error_rates) / len(error_rates)
            analysis["performance_summary"]["average_error_rate"] = avg_error_rate
        
        return analysis
    
    def generate_test_report(self) -> Dict[str, Any]:
        """
        生成测试报告
        
        Returns:
            测试报告字典
        """
        report = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "test_types": {},
                "total_duration": 0,
                "total_metrics_generated": 0
            },
            "test_results": self.test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        # 统计测试类型
        for result in self.test_results:
            test_type = result["scenario_type"]
            if test_type not in report["test_summary"]["test_types"]:
                report["test_summary"]["test_types"][test_type] = 0
            report["test_summary"]["test_types"][test_type] += 1
            
            # 累计指标数量
            report["test_summary"]["total_metrics_generated"] += result.get("total_metrics", 0)
        
        return report
    
    def save_test_report(self, filename: Optional[str] = None):
        """保存测试报告"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"
        
        report = self.generate_test_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Test report saved to {filename}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIOps Test Runner")
    parser.add_argument("--config", "-c", help="Configuration file path")
    parser.add_argument("--scenario", "-s", choices=[
        "normal", "anomaly", "stress", "realtime"
    ], default="normal", help="Test scenario type")
    parser.add_argument("--anomaly-type", "-a", help="Anomaly scenario name")
    parser.add_argument("--duration", "-d", type=int, default=2, help="Test duration (hours for normal/anomaly, minutes for stress)")
    parser.add_argument("--load-multiplier", "-l", type=float, default=5.0, help="Load multiplier for stress test")
    parser.add_argument("--output", "-o", help="Output report filename")
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = TestRunner(args.config)
    
    try:
        if args.scenario == "normal":
            runner.run_normal_business_scenario(args.duration)
        
        elif args.scenario == "anomaly":
            anomaly_type = args.anomaly_type or "morning_rush_failure"
            runner.run_anomaly_scenario(anomaly_type, args.duration)
        
        elif args.scenario == "stress":
            runner.run_stress_test(args.duration, args.load_multiplier)
        
        elif args.scenario == "realtime":
            runner.start_real_time_testing(args.anomaly_type)
        
        # 生成测试报告
        runner.save_test_report(args.output)
        
    except KeyboardInterrupt:
        runner.logger.info("Test interrupted by user")
    except Exception as e:
        runner.logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        runner.stop_all_tests()


if __name__ == "__main__":
    main()