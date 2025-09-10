#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据推送器

该模块负责将生成的测试数据推送到各种监控系统，包括Prometheus、Elasticsearch等。
支持实时数据推送和批量数据导入。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import logging
from urllib.parse import urljoin

from scenario_generator import ScenarioGenerator, MetricData, ScenarioType
from anomaly_simulator import AnomalySimulator, AnomalyPattern


class DataPusher:
    """数据推送器类"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化数据推送器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        self.running = False
        self.push_threads = []
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "prometheus": {
                "pushgateway_url": "http://localhost:9091",
                "job_name": "aiops_test_metrics",
                "instance": "test_generator"
            },
            "elasticsearch": {
                "url": "http://localhost:9200",
                "index_prefix": "aiops-test",
                "doc_type": "_doc"
            },
            "ai_engine": {
                "url": "http://localhost:8000",
                "metrics_endpoint": "/metrics",
                "anomaly_endpoint": "/detect_anomaly"
            },
            "push_intervals": {
                "prometheus_interval": 15,  # seconds
                "elasticsearch_interval": 30,  # seconds
                "ai_engine_interval": 60  # seconds
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("DataPusher")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def push_to_prometheus(self, metrics: List[MetricData]) -> bool:
        """
        推送指标数据到Prometheus Pushgateway
        
        Args:
            metrics: 指标数据列表
            
        Returns:
            推送是否成功
        """
        try:
            prometheus_config = self.config["prometheus"]
            pushgateway_url = prometheus_config["pushgateway_url"]
            job_name = prometheus_config["job_name"]
            instance = prometheus_config["instance"]
            
            # 构建推送URL
            push_url = f"{pushgateway_url}/metrics/job/{job_name}/instance/{instance}"
            
            # 将指标转换为Prometheus格式
            generator = ScenarioGenerator()
            prometheus_data = generator.export_to_prometheus_format(metrics)
            
            # 发送POST请求
            response = requests.post(
                push_url,
                data=prometheus_data,
                headers={'Content-Type': 'text/plain; charset=utf-8'},
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Successfully pushed {len(metrics)} metrics to Prometheus")
                return True
            else:
                self.logger.error(f"Failed to push to Prometheus: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error pushing to Prometheus: {str(e)}")
            return False
    
    def push_to_elasticsearch(self, metrics: List[MetricData]) -> bool:
        """
        推送指标数据到Elasticsearch
        
        Args:
            metrics: 指标数据列表
            
        Returns:
            推送是否成功
        """
        try:
            es_config = self.config["elasticsearch"]
            es_url = es_config["url"]
            index_prefix = es_config["index_prefix"]
            
            # 按日期创建索引
            today = datetime.now().strftime("%Y.%m.%d")
            index_name = f"{index_prefix}-{today}"
            
            # 批量插入数据
            bulk_data = []
            for metric in metrics:
                # 创建索引操作
                index_action = {
                    "index": {
                        "_index": index_name,
                        "_type": es_config["doc_type"]
                    }
                }
                
                # 创建文档数据
                doc_data = {
                    "@timestamp": metric.timestamp.isoformat(),
                    "metric_name": metric.metric_name,
                    "value": metric.value,
                    "labels": metric.labels,
                    "scenario_type": metric.scenario_type.value,
                    "severity": metric.severity.value,
                    "source": "test_generator"
                }
                
                bulk_data.append(json.dumps(index_action))
                bulk_data.append(json.dumps(doc_data))
            
            # 发送批量请求
            bulk_body = "\n".join(bulk_data) + "\n"
            
            response = requests.post(
                f"{es_url}/_bulk",
                data=bulk_body,
                headers={'Content-Type': 'application/x-ndjson'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("errors", False):
                    self.logger.warning(f"Some documents failed to index: {result}")
                else:
                    self.logger.info(f"Successfully pushed {len(metrics)} metrics to Elasticsearch")
                return True
            else:
                self.logger.error(f"Failed to push to Elasticsearch: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error pushing to Elasticsearch: {str(e)}")
            return False
    
    def send_to_ai_engine(self, metrics: List[MetricData]) -> Dict[str, Any]:
        """
        发送数据到AI引擎进行异常检测
        
        Args:
            metrics: 指标数据列表
            
        Returns:
            AI引擎的响应结果
        """
        try:
            ai_config = self.config["ai_engine"]
            ai_url = ai_config["url"]
            anomaly_endpoint = ai_config["anomaly_endpoint"]
            
            # 准备发送给AI引擎的数据
            ai_data = {
                "metrics": [],
                "timestamp": datetime.now().isoformat(),
                "source": "test_generator"
            }
            
            for metric in metrics:
                ai_data["metrics"].append({
                    "name": metric.metric_name,
                    "value": metric.value,
                    "timestamp": metric.timestamp.isoformat(),
                    "labels": metric.labels,
                    "scenario_type": metric.scenario_type.value
                })
            
            # 发送到AI引擎
            response = requests.post(
                urljoin(ai_url, anomaly_endpoint),
                json=ai_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"AI Engine analysis completed: {result.get('status', 'unknown')}")
                return result
            else:
                self.logger.error(f"AI Engine request failed: {response.status_code} - {response.text}")
                return {"error": f"HTTP {response.status_code}", "message": response.text}
                
        except Exception as e:
            self.logger.error(f"Error sending to AI Engine: {str(e)}")
            return {"error": "exception", "message": str(e)}
    
    def start_real_time_push(self, 
                           scenario_generator: ScenarioGenerator,
                           anomaly_simulator: Optional[AnomalySimulator] = None,
                           anomaly_patterns: Optional[List[AnomalyPattern]] = None):
        """
        启动实时数据推送
        
        Args:
            scenario_generator: 场景生成器
            anomaly_simulator: 异常模拟器
            anomaly_patterns: 异常模式列表
        """
        self.running = True
        self.logger.info("Starting real-time data push...")
        
        # 启动Prometheus推送线程
        prometheus_thread = threading.Thread(
            target=self._prometheus_push_loop,
            args=(scenario_generator, anomaly_simulator, anomaly_patterns)
        )
        prometheus_thread.daemon = True
        prometheus_thread.start()
        self.push_threads.append(prometheus_thread)
        
        # 启动Elasticsearch推送线程
        elasticsearch_thread = threading.Thread(
            target=self._elasticsearch_push_loop,
            args=(scenario_generator, anomaly_simulator, anomaly_patterns)
        )
        elasticsearch_thread.daemon = True
        elasticsearch_thread.start()
        self.push_threads.append(elasticsearch_thread)
        
        # 启动AI引擎分析线程
        ai_engine_thread = threading.Thread(
            target=self._ai_engine_analysis_loop,
            args=(scenario_generator, anomaly_simulator, anomaly_patterns)
        )
        ai_engine_thread.daemon = True
        ai_engine_thread.start()
        self.push_threads.append(ai_engine_thread)
    
    def stop_real_time_push(self):
        """停止实时数据推送"""
        self.running = False
        self.logger.info("Stopping real-time data push...")
        
        # 等待所有线程结束
        for thread in self.push_threads:
            thread.join(timeout=5)
        
        self.push_threads.clear()
        self.logger.info("Real-time data push stopped")
    
    def _prometheus_push_loop(self, 
                            scenario_generator: ScenarioGenerator,
                            anomaly_simulator: Optional[AnomalySimulator],
                            anomaly_patterns: Optional[List[AnomalyPattern]]):
        """Prometheus推送循环"""
        interval = self.config["push_intervals"]["prometheus_interval"]
        
        while self.running:
            try:
                # 生成当前时刻的指标数据
                current_time = datetime.now()
                
                # 生成基础指标
                web_metrics = self._generate_current_metrics(
                    scenario_generator, "web", current_time
                )
                db_metrics = self._generate_current_metrics(
                    scenario_generator, "database", current_time
                )
                system_metrics = self._generate_current_metrics(
                    scenario_generator, "system", current_time
                )
                
                all_metrics = web_metrics + db_metrics + system_metrics
                
                # 应用异常模式
                if anomaly_simulator and anomaly_patterns:
                    all_metrics = self._apply_anomaly_patterns(
                        all_metrics, anomaly_simulator, anomaly_patterns, current_time
                    )
                
                # 推送到Prometheus
                self.push_to_prometheus(all_metrics)
                
            except Exception as e:
                self.logger.error(f"Error in Prometheus push loop: {str(e)}")
            
            time.sleep(interval)
    
    def _elasticsearch_push_loop(self,
                                scenario_generator: ScenarioGenerator,
                                anomaly_simulator: Optional[AnomalySimulator],
                                anomaly_patterns: Optional[List[AnomalyPattern]]):
        """Elasticsearch推送循环"""
        interval = self.config["push_intervals"]["elasticsearch_interval"]
        
        while self.running:
            try:
                # 生成过去30秒的指标数据
                current_time = datetime.now()
                
                # 生成更详细的历史数据
                web_metrics = self._generate_historical_metrics(
                    scenario_generator, "web", current_time, 30
                )
                db_metrics = self._generate_historical_metrics(
                    scenario_generator, "database", current_time, 30
                )
                system_metrics = self._generate_historical_metrics(
                    scenario_generator, "system", current_time, 30
                )
                
                all_metrics = web_metrics + db_metrics + system_metrics
                
                # 应用异常模式
                if anomaly_simulator and anomaly_patterns:
                    all_metrics = self._apply_anomaly_patterns(
                        all_metrics, anomaly_simulator, anomaly_patterns, current_time
                    )
                
                # 推送到Elasticsearch
                self.push_to_elasticsearch(all_metrics)
                
            except Exception as e:
                self.logger.error(f"Error in Elasticsearch push loop: {str(e)}")
            
            time.sleep(interval)
    
    def _ai_engine_analysis_loop(self,
                               scenario_generator: ScenarioGenerator,
                               anomaly_simulator: Optional[AnomalySimulator],
                               anomaly_patterns: Optional[List[AnomalyPattern]]):
        """AI引擎分析循环"""
        interval = self.config["push_intervals"]["ai_engine_interval"]
        
        while self.running:
            try:
                # 生成过去5分钟的指标数据用于异常检测
                current_time = datetime.now()
                
                web_metrics = self._generate_historical_metrics(
                    scenario_generator, "web", current_time, 300
                )
                db_metrics = self._generate_historical_metrics(
                    scenario_generator, "database", current_time, 300
                )
                system_metrics = self._generate_historical_metrics(
                    scenario_generator, "system", current_time, 300
                )
                
                all_metrics = web_metrics + db_metrics + system_metrics
                
                # 应用异常模式
                if anomaly_simulator and anomaly_patterns:
                    all_metrics = self._apply_anomaly_patterns(
                        all_metrics, anomaly_simulator, anomaly_patterns, current_time
                    )
                
                # 发送到AI引擎进行分析
                result = self.send_to_ai_engine(all_metrics)
                
                # 记录分析结果
                if "anomalies" in result:
                    anomaly_count = len(result["anomalies"])
                    if anomaly_count > 0:
                        self.logger.warning(f"AI Engine detected {anomaly_count} anomalies")
                        for anomaly in result["anomalies"]:
                            self.logger.warning(f"  - {anomaly}")
                
            except Exception as e:
                self.logger.error(f"Error in AI Engine analysis loop: {str(e)}")
            
            time.sleep(interval)
    
    def _generate_current_metrics(self, 
                                generator: ScenarioGenerator,
                                metric_type: str,
                                timestamp: datetime) -> List[MetricData]:
        """生成当前时刻的指标数据"""
        if metric_type == "web":
            return generator.generate_web_application_metrics(duration_minutes=1)
        elif metric_type == "database":
            return generator.generate_database_metrics(duration_minutes=1)
        elif metric_type == "system":
            return generator.generate_system_metrics(duration_minutes=1)
        else:
            return []
    
    def _generate_historical_metrics(self,
                                   generator: ScenarioGenerator,
                                   metric_type: str,
                                   end_time: datetime,
                                   duration_seconds: int) -> List[MetricData]:
        """生成历史指标数据"""
        duration_minutes = max(1, duration_seconds // 60)
        
        if metric_type == "web":
            return generator.generate_web_application_metrics(duration_minutes=duration_minutes)
        elif metric_type == "database":
            return generator.generate_database_metrics(duration_minutes=duration_minutes)
        elif metric_type == "system":
            return generator.generate_system_metrics(duration_minutes=duration_minutes)
        else:
            return []
    
    def _apply_anomaly_patterns(self,
                              metrics: List[MetricData],
                              simulator: AnomalySimulator,
                              patterns: List[AnomalyPattern],
                              current_time: datetime) -> List[MetricData]:
        """应用异常模式到指标数据"""
        modified_metrics = []
        
        for metric in metrics:
            modified_value = metric.value
            
            # 对每个异常模式应用变换
            for pattern in patterns:
                modified_value = simulator.apply_anomaly_to_value(
                    modified_value, metric.metric_name, metric.timestamp, pattern
                )
            
            # 创建修改后的指标
            modified_metric = MetricData(
                timestamp=metric.timestamp,
                metric_name=metric.metric_name,
                value=modified_value,
                labels=metric.labels,
                scenario_type=metric.scenario_type,
                severity=metric.severity
            )
            
            modified_metrics.append(modified_metric)
        
        return modified_metrics


if __name__ == "__main__":
    # 示例用法
    pusher = DataPusher()
    generator = ScenarioGenerator()
    simulator = AnomalySimulator()
    
    # 生成一些测试数据
    print("生成测试数据...")
    metrics = generator.generate_web_application_metrics(duration_minutes=5)
    
    # 推送到各个系统
    print("推送到Prometheus...")
    pusher.push_to_prometheus(metrics)
    
    print("推送到Elasticsearch...")
    pusher.push_to_elasticsearch(metrics)
    
    print("发送到AI引擎...")
    result = pusher.send_to_ai_engine(metrics)
    print(f"AI引擎响应: {result}")
    
    print("测试完成！")