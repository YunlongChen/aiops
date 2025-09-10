#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的AIOps测试场景演示脚本
不依赖外部库，仅使用Python标准库

功能:
- 生成Web应用监控数据
- 生成数据库监控数据
- 生成系统监控数据
- 执行异常检测
- 生成告警信息
- 保存测试结果
"""

import json
import random
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class SimpleDemo:
    """简化的演示类，不依赖外部库"""
    
    def __init__(self):
        """初始化演示"""
        self.start_time = datetime.now()
        self.output_dir = "demo_output"
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def generate_web_metrics(self, duration_minutes: int = 5) -> List[Dict[str, Any]]:
        """生成Web应用指标数据"""
        print("🌐 生成Web应用监控数据...")
        
        metrics = []
        base_time = self.start_time
        
        for i in range(duration_minutes * 12):  # 每5秒一个数据点
            timestamp = base_time + timedelta(seconds=i * 5)
            
            # 模拟正常和异常情况
            is_anomaly = random.random() < 0.1  # 10%概率异常
            
            if is_anomaly:
                response_time = random.uniform(2000, 5000)  # 异常响应时间
                error_rate = random.uniform(0.05, 0.2)     # 高错误率
                cpu_usage = random.uniform(80, 95)         # 高CPU使用率
            else:
                response_time = random.uniform(100, 500)   # 正常响应时间
                error_rate = random.uniform(0, 0.02)       # 低错误率
                cpu_usage = random.uniform(20, 60)         # 正常CPU使用率
                
            metric = {
                "timestamp": timestamp.isoformat(),
                "service": "web-app",
                "response_time_ms": round(response_time, 2),
                "error_rate": round(error_rate, 4),
                "requests_per_second": random.randint(50, 200),
                "cpu_usage_percent": round(cpu_usage, 2),
                "memory_usage_mb": random.randint(512, 2048),
                "is_anomaly": is_anomaly
            }
            metrics.append(metric)
            
        print(f"✅ 生成了 {len(metrics)} 个Web指标数据点")
        return metrics
        
    def generate_database_metrics(self, duration_minutes: int = 5) -> List[Dict[str, Any]]:
        """生成数据库指标数据"""
        print("🗄️ 生成数据库监控数据...")
        
        metrics = []
        base_time = self.start_time
        
        for i in range(duration_minutes * 6):  # 每10秒一个数据点
            timestamp = base_time + timedelta(seconds=i * 10)
            
            # 模拟数据库负载变化
            is_high_load = random.random() < 0.15  # 15%概率高负载
            
            if is_high_load:
                query_time = random.uniform(1000, 3000)   # 慢查询
                connections = random.randint(80, 100)     # 高连接数
                lock_waits = random.randint(5, 20)        # 锁等待
            else:
                query_time = random.uniform(10, 200)      # 正常查询时间
                connections = random.randint(10, 50)      # 正常连接数
                lock_waits = random.randint(0, 2)         # 少量锁等待
                
            metric = {
                "timestamp": timestamp.isoformat(),
                "service": "database",
                "avg_query_time_ms": round(query_time, 2),
                "active_connections": connections,
                "lock_waits": lock_waits,
                "buffer_hit_ratio": round(random.uniform(0.85, 0.99), 4),
                "disk_io_ops": random.randint(100, 1000),
                "is_high_load": is_high_load
            }
            metrics.append(metric)
            
        print(f"✅ 生成了 {len(metrics)} 个数据库指标数据点")
        return metrics
        
    def generate_system_metrics(self, duration_minutes: int = 5) -> List[Dict[str, Any]]:
        """生成系统指标数据"""
        print("💻 生成系统监控数据...")
        
        metrics = []
        base_time = self.start_time
        
        for i in range(duration_minutes * 20):  # 每15秒一个数据点
            timestamp = base_time + timedelta(seconds=i * 15)
            
            # 模拟系统资源使用情况
            is_stressed = random.random() < 0.08  # 8%概率系统压力大
            
            if is_stressed:
                cpu_usage = random.uniform(85, 98)
                memory_usage = random.uniform(80, 95)
                disk_usage = random.uniform(85, 95)
                network_in = random.uniform(800, 1000)  # MB/s
            else:
                cpu_usage = random.uniform(10, 70)
                memory_usage = random.uniform(30, 75)
                disk_usage = random.uniform(40, 80)
                network_in = random.uniform(10, 200)
                
            metric = {
                "timestamp": timestamp.isoformat(),
                "service": "system",
                "cpu_usage_percent": round(cpu_usage, 2),
                "memory_usage_percent": round(memory_usage, 2),
                "disk_usage_percent": round(disk_usage, 2),
                "network_in_mbps": round(network_in, 2),
                "network_out_mbps": round(random.uniform(5, network_in * 0.3), 2),
                "load_average": round(random.uniform(0.5, 4.0), 2),
                "is_stressed": is_stressed
            }
            metrics.append(metric)
            
        print(f"✅ 生成了 {len(metrics)} 个系统指标数据点")
        return metrics
        
    def detect_anomalies(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """简单的异常检测"""
        print("🔍 执行异常检测分析...")
        
        anomalies = []
        total_points = len(metrics)
        
        for metric in metrics:
            if metric.get('is_anomaly') or metric.get('is_high_load') or metric.get('is_stressed'):
                anomalies.append({
                    "timestamp": metric["timestamp"],
                    "service": metric["service"],
                    "anomaly_type": self._get_anomaly_type(metric),
                    "severity": self._get_severity(metric),
                    "details": metric
                })
                
        anomaly_rate = len(anomalies) / total_points if total_points > 0 else 0
        
        result = {
            "total_data_points": total_points,
            "anomalies_detected": len(anomalies),
            "anomaly_rate": round(anomaly_rate, 4),
            "anomalies": anomalies[:10]  # 只显示前10个异常
        }
        
        print(f"✅ 检测到 {len(anomalies)} 个异常 (异常率: {anomaly_rate:.2%})")
        return result
        
    def _get_anomaly_type(self, metric: Dict[str, Any]) -> str:
        """获取异常类型"""
        service = metric.get('service', '')
        if service == 'web-app':
            if metric.get('response_time_ms', 0) > 1000:
                return 'high_response_time'
            elif metric.get('error_rate', 0) > 0.05:
                return 'high_error_rate'
            else:
                return 'performance_degradation'
        elif service == 'database':
            if metric.get('avg_query_time_ms', 0) > 500:
                return 'slow_query'
            else:
                return 'high_load'
        elif service == 'system':
            if metric.get('cpu_usage_percent', 0) > 85:
                return 'high_cpu'
            elif metric.get('memory_usage_percent', 0) > 80:
                return 'high_memory'
            else:
                return 'resource_stress'
        return 'unknown'
        
    def _get_severity(self, metric: Dict[str, Any]) -> str:
        """获取严重程度"""
        service = metric.get('service', '')
        if service == 'web-app':
            if metric.get('response_time_ms', 0) > 3000 or metric.get('error_rate', 0) > 0.1:
                return 'critical'
            else:
                return 'warning'
        elif service == 'database':
            if metric.get('avg_query_time_ms', 0) > 2000:
                return 'critical'
            else:
                return 'warning'
        elif service == 'system':
            if metric.get('cpu_usage_percent', 0) > 90 or metric.get('memory_usage_percent', 0) > 90:
                return 'critical'
            else:
                return 'warning'
        return 'info'
        
    def generate_alerts(self, anomalies: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成告警"""
        print("🚨 生成告警信息...")
        
        alerts = []
        for anomaly in anomalies.get('anomalies', []):
            alert = {
                "alert_id": f"alert_{len(alerts) + 1:04d}",
                "timestamp": anomaly["timestamp"],
                "service": anomaly["service"],
                "severity": anomaly["severity"],
                "title": f"{anomaly['service'].title()} {anomaly['anomaly_type'].replace('_', ' ').title()}",
                "description": self._generate_alert_description(anomaly),
                "status": "active"
            }
            alerts.append(alert)
            
        print(f"✅ 生成了 {len(alerts)} 个告警")
        return alerts
        
    def _generate_alert_description(self, anomaly: Dict[str, Any]) -> str:
        """生成告警描述"""
        service = anomaly["service"]
        anomaly_type = anomaly["anomaly_type"]
        details = anomaly["details"]
        
        if service == "web-app":
            if anomaly_type == "high_response_time":
                return f"响应时间异常高: {details.get('response_time_ms', 0):.2f}ms"
            elif anomaly_type == "high_error_rate":
                return f"错误率异常高: {details.get('error_rate', 0):.2%}"
        elif service == "database":
            if anomaly_type == "slow_query":
                return f"查询时间过长: {details.get('avg_query_time_ms', 0):.2f}ms"
            elif anomaly_type == "high_load":
                return f"数据库负载过高: {details.get('active_connections', 0)} 个活跃连接"
        elif service == "system":
            if anomaly_type == "high_cpu":
                return f"CPU使用率过高: {details.get('cpu_usage_percent', 0):.2f}%"
            elif anomaly_type == "high_memory":
                return f"内存使用率过高: {details.get('memory_usage_percent', 0):.2f}%"
                
        return f"{service} 服务出现 {anomaly_type} 异常"
        
    def save_results(self, web_metrics: List, db_metrics: List, sys_metrics: List, 
                    anomalies: Dict, alerts: List) -> str:
        """保存结果到文件"""
        print("💾 保存测试结果...")
        
        # 保存各类指标数据
        with open(os.path.join(self.output_dir, "web_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(web_metrics, f, indent=2, ensure_ascii=False)
            
        with open(os.path.join(self.output_dir, "database_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(db_metrics, f, indent=2, ensure_ascii=False)
            
        with open(os.path.join(self.output_dir, "system_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(sys_metrics, f, indent=2, ensure_ascii=False)
            
        # 保存异常检测结果
        with open(os.path.join(self.output_dir, "anomalies.json"), "w", encoding="utf-8") as f:
            json.dump(anomalies, f, indent=2, ensure_ascii=False)
            
        # 保存告警信息
        with open(os.path.join(self.output_dir, "alerts.json"), "w", encoding="utf-8") as f:
            json.dump(alerts, f, indent=2, ensure_ascii=False)
            
        # 生成汇总报告
        report = self._generate_summary_report(web_metrics, db_metrics, sys_metrics, anomalies, alerts)
        report_file = os.path.join(self.output_dir, "summary_report.json")
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 结果已保存到 {self.output_dir} 目录")
        return report_file
        
    def _generate_summary_report(self, web_metrics: List, db_metrics: List, 
                               sys_metrics: List, anomalies: Dict, alerts: List) -> Dict:
        """生成汇总报告"""
        return {
            "test_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_minutes": 5,
                "total_data_points": len(web_metrics) + len(db_metrics) + len(sys_metrics)
            },
            "metrics_summary": {
                "web_metrics_count": len(web_metrics),
                "database_metrics_count": len(db_metrics),
                "system_metrics_count": len(sys_metrics)
            },
            "anomaly_summary": {
                "total_anomalies": anomalies.get("anomalies_detected", 0),
                "anomaly_rate": anomalies.get("anomaly_rate", 0),
                "critical_alerts": len([a for a in alerts if a["severity"] == "critical"]),
                "warning_alerts": len([a for a in alerts if a["severity"] == "warning"])
            },
            "service_health": {
                "web_app": self._calculate_service_health(web_metrics),
                "database": self._calculate_service_health(db_metrics),
                "system": self._calculate_service_health(sys_metrics)
            }
        }
        
    def _calculate_service_health(self, metrics: List[Dict]) -> str:
        """计算服务健康状态"""
        if not metrics:
            return "unknown"
            
        anomaly_count = sum(1 for m in metrics if m.get('is_anomaly') or m.get('is_high_load') or m.get('is_stressed'))
        anomaly_rate = anomaly_count / len(metrics)
        
        if anomaly_rate > 0.2:
            return "critical"
        elif anomaly_rate > 0.1:
            return "warning"
        else:
            return "healthy"
            
    def run_demo(self):
        """运行完整演示"""
        print("🚀 开始AIOps测试场景演示")
        print("=" * 50)
        
        try:
            # 1. 生成各类监控数据
            web_metrics = self.generate_web_metrics()
            db_metrics = self.generate_database_metrics()
            sys_metrics = self.generate_system_metrics()
            
            # 2. 合并所有指标进行异常检测
            all_metrics = web_metrics + db_metrics + sys_metrics
            anomalies = self.detect_anomalies(all_metrics)
            
            # 3. 生成告警
            alerts = self.generate_alerts(anomalies)
            
            # 4. 保存结果
            report_file = self.save_results(web_metrics, db_metrics, sys_metrics, anomalies, alerts)
            
            # 5. 显示汇总信息
            print("\n📊 测试结果汇总:")
            print(f"   • Web应用指标: {len(web_metrics)} 个数据点")
            print(f"   • 数据库指标: {len(db_metrics)} 个数据点")
            print(f"   • 系统指标: {len(sys_metrics)} 个数据点")
            print(f"   • 检测到异常: {anomalies['anomalies_detected']} 个")
            print(f"   • 生成告警: {len(alerts)} 个")
            print(f"   • 异常率: {anomalies['anomaly_rate']:.2%}")
            
            print(f"\n📁 详细结果已保存到: {os.path.abspath(self.output_dir)}")
            print(f"📋 汇总报告: {os.path.abspath(report_file)}")
            
            print("\n✅ 演示完成!")
            
        except Exception as e:
            print(f"❌ 演示过程中出现错误: {e}")
            raise
            
def main():
    """主函数"""
    print("AIOps测试场景框架 - 简化演示版本")
    print("使用Python标准库，无需额外依赖")
    print()
    
    demo = SimpleDemo()
    demo.run_demo()
    
if __name__ == "__main__":
    main()