# AIOps 测试场景详细使用指南

## 📋 测试场景概述

### 当前测试框架测试了什么？

我们的AIOps测试框架模拟了完整的运维监控生态系统，包括：

#### 1. 🌐 Web应用监控测试 (`web_app_simulator.py`)
**测试内容：**
- HTTP请求处理性能（响应时间、吞吐量）
- 错误率监控（4xx、5xx错误）
- 用户会话管理
- 负载均衡效果
- 缓存命中率

**模拟场景：**
- 电商网站高峰期流量
- 金融系统交易处理
- 社交媒体内容分发
- 在线教育平台访问

#### 2. 🗄️ 数据库性能监控测试 (`database_simulator.py`)
**测试内容：**
- 查询执行时间分析
- 数据库连接池管理
- 锁等待和死锁检测
- 索引使用效率
- 缓存命中率
- 事务处理性能

**模拟场景：**
- OLTP高并发事务处理
- OLAP复杂查询分析
- 数据迁移和备份操作
- 读写分离性能测试

#### 3. 💻 系统资源监控测试 (`system_monitor.py`)
**测试内容：**
- CPU使用率和负载均衡
- 内存使用模式和泄漏检测
- 磁盘I/O性能和空间使用
- 网络带宽和延迟
- 进程和线程监控

**模拟场景：**
- 多服务器集群监控
- 容器化环境资源分配
- 微服务间通信监控

#### 4. 🚨 异常检测测试 (`anomaly_simulator.py`)
**测试内容：**
- 指标异常模式识别
- 趋势变化检测
- 周期性异常发现
- 多维度关联分析

**异常类型：**
- 突发峰值（Spike）
- 性能下降（Dip）
- 趋势变化（Trend Change）
- 周期性异常（Seasonal Anomaly）
- 数据缺失（Missing Data）

#### 5. 📢 告警系统测试 (`alert_simulator.py`)
**测试内容：**
- 告警规则触发机制
- 告警级别分类（Critical、Warning、Info）
- 通知渠道测试（邮件、短信、Webhook）
- 告警抑制和升级
- 告警恢复和确认

#### 6. 📊 仪表板数据生成 (`simple_dashboard_generator.py`)
**测试内容：**
- Grafana兼容数据格式
- 多种数据源支持（Prometheus、InfluxDB、Elasticsearch）
- 实时指标可视化
- 历史数据趋势分析

#### 7. ⚡ 性能压力测试 (`simple_performance_tester.py`)
**测试内容：**
- CPU密集型任务压力测试
- 内存分配和释放测试
- 磁盘I/O读写性能
- 网络并发连接测试

## 🚀 如何使用测试场景

### 1. 快速开始

```bash
# 运行快速测试套件（推荐首次使用）
py integrated_test_runner.py --mode quick

# 运行完整综合测试
py integrated_test_runner.py --mode comprehensive

# 运行所有测试（包括多项目负载测试）
py integrated_test_runner.py --mode all
```

### 2. 单独运行特定测试

```bash
# Web应用监控测试（60秒）
py web_app_simulator.py --duration 60

# 数据库性能测试（120秒，导出数据）
py database_simulator.py --duration 120 --export db_metrics.json --report db_report.json

# 系统资源监控（90秒）
py system_monitor.py --duration 90 --export sys_metrics.json

# 异常检测测试
py anomaly_simulator.py

# 告警系统测试
py alert_simulator.py

# 性能压力测试（CPU测试30秒）
py simple_performance_tester.py --test-type cpu --duration 30
```

### 3. 自定义测试组合

```bash
# 运行指定的测试模块
py integrated_test_runner.py --mode custom --tests web_monitor db_monitor system_monitor

# 指定输出报告文件
py integrated_test_runner.py --mode quick --output my_test_report.json
```

## 🔧 如何添加新的测试场景

### 方法1：创建新的独立测试脚本

#### 步骤1：创建新的测试脚本

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新测试场景模拟器
描述：你的测试场景功能描述

作者: Your Name
创建时间: 2025-09-10
"""

import os
import sys
import time
import json
import random
from datetime import datetime
from typing import Dict, List, Any

class NewTestSimulator:
    """新测试场景模拟器类"""
    
    def __init__(self, duration: int = 60):
        """初始化模拟器
        
        Args:
            duration: 测试持续时间（秒）
        """
        self.duration = duration
        self.metrics = []
        self.start_time = None
        self.end_time = None
    
    def generate_metrics(self) -> Dict[str, Any]:
        """生成测试指标数据"""
        # 实现你的指标生成逻辑
        return {
            'timestamp': datetime.now().isoformat(),
            'metric_name': random.uniform(0, 100),
            # 添加更多指标...
        }
    
    def run_simulation(self):
        """运行模拟测试"""
        print(f"🚀 开始新测试场景模拟 (持续时间: {self.duration}秒)")
        self.start_time = time.time()
        
        while time.time() - self.start_time < self.duration:
            metrics = self.generate_metrics()
            self.metrics.append(metrics)
            
            # 打印实时指标
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 指标: {metrics['metric_name']:.2f}")
            
            time.sleep(5)  # 每5秒生成一次数据
        
        self.end_time = time.time()
        print(f"✅ 新测试场景模拟完成")
        print(f"总共生成 {len(self.metrics)} 个数据点")
    
    def export_data(self, filename: str = None):
        """导出测试数据"""
        if not filename:
            filename = f"new_test_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'test_type': 'new_test_scenario',
            'duration': self.duration,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'total_metrics': len(self.metrics),
            'metrics': self.metrics
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 测试数据已导出到: {filename}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='新测试场景模拟器')
    parser.add_argument('--duration', type=int, default=60, help='测试持续时间（秒）')
    parser.add_argument('--export', type=str, help='导出数据文件名')
    
    args = parser.parse_args()
    
    # 创建并运行模拟器
    simulator = NewTestSimulator(duration=args.duration)
    simulator.run_simulation()
    
    # 导出数据
    if args.export:
        simulator.export_data(args.export)
    else:
        simulator.export_data()

if __name__ == '__main__':
    main()
```

#### 步骤2：将新测试添加到集成测试运行器

编辑 `integrated_test_runner.py`，添加新的测试方法：

```python
# 在test_scripts字典中添加新测试
self.test_scripts = {
    'web_monitor': 'web_app_simulator.py',
    'db_monitor': 'database_simulator.py', 
    'system_monitor': 'system_monitor.py',
    'anomaly_detection': 'anomaly_simulator.py',
    'alert_system': 'alert_simulator.py',
    'dashboard_data': 'simple_dashboard_generator.py',
    'performance_test': 'simple_performance_tester.py',
    'new_test': 'new_test_simulator.py'  # 添加新测试
}

# 添加新的测试方法
def run_new_test(self):
    """运行新测试场景"""
    return self.run_command(
        "py new_test_simulator.py --duration 60",
        "新测试场景"
    )

# 在test_mapping中添加映射
test_mapping = {
    'web_monitor': self.run_web_monitoring_test,
    'db_monitor': self.run_database_monitoring_test,
    'system_monitor': self.run_system_monitoring_test,
    'anomaly_detection': self.run_anomaly_detection_test,
    'alert_system': self.run_alerting_test,
    'dashboard_data': self.run_dashboard_data_generation,
    'performance_test': self.run_performance_stress_test,
    'new_test': self.run_new_test  # 添加新测试映射
}
```

### 方法2：扩展现有测试脚本

如果新测试场景与现有测试相关，可以直接扩展现有脚本：

```python
# 在现有测试脚本中添加新的测试场景
class WebAppSimulator:
    def __init__(self):
        self.scenarios = {
            'ecommerce': self.ecommerce_scenario,
            'financial': self.financial_scenario,
            'social_media': self.social_media_scenario,
            'education': self.education_scenario,
            'new_scenario': self.new_scenario  # 添加新场景
        }
    
    def new_scenario(self):
        """新的Web应用场景"""
        # 实现新场景逻辑
        pass
```

## 📁 测试文件管理和.gitignore配置

### 当前文件结构问题

你说得对，测试结果文件确实会让仓库变得混乱。让我们优化文件管理：

### 推荐的.gitignore规则

需要在 `.gitignore` 中添加以下规则：

```gitignore
# AIOps测试结果文件
test-scenarios/test_reports/
test-scenarios/performance_test_results/
test-scenarios/dashboard_data/
test-scenarios/temp_projects/
test-scenarios/*_metrics.json
test-scenarios/*_report.json
test-scenarios/test_report.json
test-scenarios/db_*.json
test-scenarios/sys_*.json

# 临时测试文件
test-scenarios/*.tmp
test-scenarios/*.temp
test-scenarios/temp_*

# 测试生成的日志文件
test-scenarios/*.log
test-scenarios/logs/
```

### 优化后的文件结构

```
test-scenarios/
├── core/                          # 核心测试脚本（提交到Git）
│   ├── web_app_simulator.py
│   ├── database_simulator.py
│   ├── system_monitor.py
│   ├── anomaly_simulator.py
│   ├── alert_simulator.py
│   └── ...
├── config/                        # 配置文件（提交到Git）
│   ├── test_config.json
│   ├── project_configs.json
│   └── scenario_config.json
├── templates/                     # 测试模板（提交到Git）
│   ├── test_template.py
│   └── scenario_template.py
├── results/                       # 测试结果（不提交到Git）
│   ├── test_reports/
│   ├── performance_results/
│   ├── metrics_data/
│   └── logs/
├── temp/                          # 临时文件（不提交到Git）
│   ├── temp_projects/
│   └── cache/
├── integrated_test_runner.py      # 主测试运行器（提交到Git）
├── README.md                      # 文档（提交到Git）
├── TESTING_GUIDE.md              # 使用指南（提交到Git）
└── requirements.txt               # 依赖文件（提交到Git）
```

### 自动清理脚本

创建一个清理脚本 `cleanup_test_files.py`：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件清理脚本
清理测试过程中生成的临时文件和结果文件
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_test_files():
    """清理测试文件"""
    current_dir = Path(__file__).parent
    
    # 要清理的文件模式
    cleanup_patterns = [
        '*_metrics.json',
        '*_report.json', 
        'test_report.json',
        'db_*.json',
        'sys_*.json',
        '*.tmp',
        '*.temp',
        'temp_*'
    ]
    
    # 要清理的目录
    cleanup_dirs = [
        'test_reports',
        'performance_test_results', 
        'temp_projects',
        'logs'
    ]
    
    print("🧹 开始清理测试文件...")
    
    # 清理文件
    for pattern in cleanup_patterns:
        files = glob.glob(str(current_dir / pattern))
        for file in files:
            try:
                os.remove(file)
                print(f"删除文件: {file}")
            except Exception as e:
                print(f"删除文件失败 {file}: {e}")
    
    # 清理目录
    for dir_name in cleanup_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path)
                print(f"删除目录: {dir_path}")
            except Exception as e:
                print(f"删除目录失败 {dir_path}: {e}")
    
    print("✅ 测试文件清理完成")

if __name__ == '__main__':
    cleanup_test_files()
```

## 🎯 最佳实践建议

### 1. 测试场景开发规范

- **命名规范**: 使用描述性的文件名，如 `kafka_monitoring_simulator.py`
- **代码结构**: 遵循现有模拟器的结构模式
- **文档注释**: 添加详细的类和方法注释
- **配置化**: 支持命令行参数和配置文件
- **数据导出**: 统一的JSON格式数据导出

### 2. 测试数据管理

- **结果分离**: 测试结果文件不提交到Git仓库
- **定期清理**: 使用清理脚本定期清理临时文件
- **结构化存储**: 按日期和测试类型组织结果文件
- **压缩归档**: 重要的测试结果可以压缩归档保存

### 3. 扩展性设计

- **插件化**: 新测试场景可以作为插件动态加载
- **配置驱动**: 通过配置文件定义测试场景参数
- **模块化**: 将通用功能抽取为公共模块
- **标准化**: 统一的接口和数据格式

## 📞 获取帮助

如果你需要添加新的测试场景或有其他问题，可以：

1. 参考现有的测试脚本作为模板
2. 查看 `USAGE.md` 了解详细的使用方法
3. 运行 `py integrated_test_runner.py --help` 查看所有可用选项
4. 使用 `py cleanup_test_files.py` 清理测试文件

希望这个指南能帮助你更好地理解和使用AIOps测试框架！