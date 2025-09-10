# AIOps 测试场景框架

这是一个全面的AIOps（智能运维）测试场景框架，用于模拟各种运维监控场景，生成测试数据，并验证监控系统的功能。

## 🎯 项目概述

本框架提供了完整的AIOps测试环境，包括：
- Web应用程序监控模拟
- 数据库性能监控测试
- 系统资源监控场景
- 异常检测和告警测试
- 性能压力测试
- Grafana仪表板数据生成

## 📁 项目结构

```
test-scenarios/
├── web_app_simulator.py          # Web应用监控模拟器
├── database_simulator.py         # 数据库性能监控模拟器
├── system_monitor.py             # 系统资源监控器
├── anomaly_simulator.py          # 异常检测模拟器
├── alert_simulator.py            # 告警系统模拟器
├── simple_dashboard_generator.py # 仪表板数据生成器
├── simple_performance_tester.py  # 性能压力测试器
├── integrated_test_runner.py     # 综合测试运行器
├── scenario_config.json          # 场景配置文件
└── README.md                     # 项目说明文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 2. 快速演示

```bash
# 运行快速演示（推荐首次使用）
python quick_demo.py
```

### 3. 交互式测试

```bash
# 启动交互式测试菜单
python run_tests.py
```

## 📋 功能模块

### 🎯 核心模块

| 模块 | 文件 | 功能描述 |
|------|------|----------|
| **场景生成器** | `scenario_generator.py` | 生成Web应用、数据库、系统资源等监控场景数据 |
| **异常模拟器** | `anomaly_simulator.py` | 模拟各种异常模式（峰值、下降、趋势变化等） |
| **压力测试器** | `stress_tester.py` | 执行CPU、内存、磁盘、网络等压力测试 |
| **数据推送器** | `data_pusher.py` | 向Prometheus、Elasticsearch等推送测试数据 |
| **测试运行器** | `test_runner.py` | 综合测试运行和管理 |

### 🔧 专用模拟器

| 模块 | 文件 | 功能描述 |
|------|------|----------|
| **Web模拟器** | `web_simulator.py` | 模拟Web应用程序的HTTP请求和响应 |
| **数据库模拟器** | `database_simulator.py` | 模拟数据库查询和性能指标 |
| **系统监控器** | `system_monitor.py` | 监控系统资源使用情况 |
| **告警模拟器** | `alert_simulator.py` | 模拟告警系统的触发和处理 |
| **仪表板数据生成器** | `dashboard_data_generator.py` | 为Grafana等仪表板生成数据 |

### 🛠️ 工具脚本

| 脚本 | 功能描述 |
|------|----------|
| `run_tests.py` | 交互式测试启动器，提供菜单式操作 |
| `quick_demo.py` | 快速演示脚本，展示所有功能 |
| `test_config.json` | 测试配置文件 |

## 📊 支持的场景类型

### 1. 业务场景

- **Web应用监控**
  - HTTP请求量、响应时间、错误率
  - 用户会话、页面访问统计
  - API调用频率和性能

- **数据库性能**
  - 查询执行时间、连接数
  - 锁等待、死锁检测
  - 缓存命中率、索引使用

- **系统资源**
  - CPU、内存、磁盘使用率
  - 网络I/O、进程监控
  - 服务状态检查

### 2. 异常类型

- **峰值异常** (Spike): 数据突然上升
- **下降异常** (Dip): 数据突然下降
- **趋势变化** (Trend Change): 长期趋势改变
- **季节性偏移** (Seasonal Shift): 周期性模式变化
- **噪声增加** (Noise Increase): 数据波动增大
- **平台偏移** (Level Shift): 基准值永久改变

### 3. 压力测试

- **CPU密集型**: 计算密集任务
- **内存密集型**: 大量内存分配
- **磁盘I/O**: 文件读写操作
- **网络I/O**: 网络请求和传输
- **应用程序**: 模拟真实应用负载

## 🎮 使用示例

### 基础使用

```python
from scenario_generator import ScenarioGenerator, ScenarioType
from anomaly_simulator import AnomalySimulator, AnomalyType

# 生成Web应用场景
generator = ScenarioGenerator()
web_metrics = generator.generate_web_application_metrics(
    duration_minutes=30,
    request_rate=200
)

# 应用异常
simulator = AnomalySimulator()
anomalous_data = simulator.apply_anomaly(web_metrics, AnomalyType.SPIKE)

# 保存数据
generator.save_to_file(anomalous_data, "web_anomaly_test.json")
```

### 压力测试

```python
from stress_tester import StressTester, StressTestType, TestSeverity

# 创建压力测试器
tester = StressTester()

# 配置CPU压力测试
config = tester.create_test_configuration(
    test_type=StressTestType.CPU,
    severity=TestSeverity.MEDIUM,
    duration_seconds=60
)

# 运行测试
result = tester.run_stress_test(config)
print(f"测试完成: {result.total_operations} 次操作")
```

### 数据推送

```python
from data_pusher import DataPusher

# 创建数据推送器
pusher = DataPusher()

# 推送到Prometheus
pusher.push_to_prometheus(metrics_data, "http://localhost:9091")

# 推送到AI引擎进行异常检测
result = pusher.send_to_ai_engine(metrics_data, "http://localhost:8000")
```

## 🔧 配置说明

### test_config.json 配置文件

```json
{
  "scenario_generator": {
    "default_duration_minutes": 60,
    "default_interval_seconds": 30,
    "output_format": "json"
  },
  "data_pusher": {
    "prometheus_gateway": "http://localhost:9091",
    "elasticsearch_url": "http://localhost:9200",
    "ai_engine_url": "http://localhost:8000"
  },
  "test_scenarios": {
    "web_application": {
      "enabled": true,
      "request_rate_range": [50, 500],
      "error_rate_range": [0.01, 0.1]
    },
    "database": {
      "enabled": true,
      "query_rate_range": [10, 200],
      "connection_pool_size": 20
    }
  }
}
```

## 📈 输出格式

### JSON格式

```json
{
  "timestamp": "2025-01-10T10:30:00Z",
  "metrics": [
    {
      "name": "http_requests_total",
      "value": 1250,
      "labels": {
        "method": "GET",
        "status": "200"
      },
      "timestamp": "2025-01-10T10:30:00Z"
    }
  ]
}
```

### Prometheus格式

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1250 1641811800000
```

### CSV格式

```csv
timestamp,metric_name,value,labels
2025-01-10T10:30:00Z,http_requests_total,1250,"method=GET,status=200"
```

## 🚀 高级功能

### 1. 实时数据流

```python
# 启动实时数据生成
from test_runner import TestRunner

runner = TestRunner("test_config.json")
runner.start_realtime_testing(duration_minutes=60)
```

### 2. 自定义异常模式

```python
from anomaly_simulator import AnomalyPattern

# 定义自定义异常模式
custom_pattern = AnomalyPattern(
    anomaly_type=AnomalyType.CUSTOM,
    intensity=0.8,
    duration_ratio=0.2,
    parameters={"custom_param": 1.5}
)

simulator.apply_custom_anomaly(data, custom_pattern)
```

### 3. 批量测试

```bash
# 运行预定义的测试套件
python test_runner.py --config test_config.json --run-all

# 运行特定场景
python test_runner.py --scenario web_application --duration 30
```

## 📊 监控集成

### Prometheus集成

```python
# 配置Prometheus推送
pusher.configure_prometheus(
    gateway_url="http://localhost:9091",
    job_name="aiops_test",
    instance="test_instance"
)
```

### Grafana仪表板

框架提供了预配置的Grafana仪表板模板，可以直接导入使用：

- `dashboards/aiops_overview.json` - 总览仪表板
- `dashboards/anomaly_detection.json` - 异常检测仪表板
- `dashboards/stress_testing.json` - 压力测试仪表板

### Elasticsearch集成

```python
# 推送日志数据到Elasticsearch
pusher.push_to_elasticsearch(
    data=log_data,
    index="aiops-logs",
    doc_type="test_log"
)
```

## 🔍 故障排除

### 常见问题

1. **依赖安装失败**
   ```bash
   # 使用国内镜像源
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

2. **端口冲突**
   - 检查8000、9091、9200等端口是否被占用
   - 修改配置文件中的端口设置

3. **内存不足**
   - 降低测试强度和持续时间
   - 调整配置文件中的并发参数

4. **权限问题**
   ```bash
   # Windows下以管理员身份运行
   # Linux/Mac下使用sudo（如需要）
   ```

### 日志调试

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看测试日志
tail -f test_results/test_*.log
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题或建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 提交 [Issue](https://github.com/your-repo/aiops/issues)
3. 联系开发团队

## 🎯 路线图

- [ ] 支持更多数据源集成
- [ ] 增加机器学习异常检测算法
- [ ] 提供Web界面管理
- [ ] 支持分布式测试
- [ ] 增加更多可视化选项
- [ ] 支持云原生部署

---

**AIOps Team** - 让智能运维更简单！ 🚀