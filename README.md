# AIOps-Platform 智能运维平台

> AI 运维，未来已来

## 项目概述

AIOps-Platform 是一个基于人工智能的智能运维平台，通过AI自动处理服务器监控、日志分析、异常检测和自愈操作。该平台集成了现代化的监控、日志处理、AI分析和自动化运维能力。

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        AIOps-Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                     Frontend Network                           │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │   Traefik   │────│   Grafana   │────│   Kibana    │        │
│  │ (Port 80/443)│    │ (Port 3000) │    │ (Port 5601) │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
├─────────────────────────────────────────────────────────────────┤
│                     Backend Network                            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ Prometheus  │────│Alertmanager │────│Elasticsearch│        │
│  │ (Port 9090) │    │ (Port 9093) │    │ (Port 9200) │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐                           │
│  │  Logstash   │────│ API Gateway │                           │
│  │ (Port 5044) │    │ (Port 8080) │                           │
│  └─────────────┘    └─────────────┘                           │
├─────────────────────────────────────────────────────────────────┤
│                       AI Network                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │ AI Engine   │────│Self-Healing │────│   Ansible   │        │
│  │ (Port 8000) │    │ (Port 8001) │    │ (Port 8002) │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 边缘路由层
- **Traefik**: 边缘路由和负载均衡器，提供SSL终止和服务发现

### 2. 测试脚本管理系统
- **测试脚本管理**: 支持多语言测试脚本的创建、编辑和执行
- **测试用例管理**: 完整的测试用例生命周期管理
- **运行时管理**: Docker、Kubernetes等多种运行时环境支持
- **执行引擎**: 分布式测试执行和结果收集

### 3. 监控堆栈
- **Prometheus**: 指标收集和存储
- **Grafana**: 可视化仪表板
- **Alertmanager**: 告警管理和通知

### 4. 日志处理栈
- **Elasticsearch**: 日志存储和搜索引擎
- **Logstash**: 日志处理和转换
- **Kibana**: 日志可视化和分析

### 4. AI引擎模块
- **异常检测**: 基于机器学习的时间序列异常检测
- **预测分析**: 资源使用趋势预测
- **智能告警**: 减少误报的智能告警系统

### 5. 自愈执行器
- **Ansible集成**: 自动化运维脚本执行
- **触发器系统**: 基于规则的自动响应
- **反馈循环**: 执行结果监控和学习

## 网络架构

### 网络分段
- **Frontend Network** (172.20.0.0/24): 用户界面和外部访问
- **Backend Network** (172.21.0.0/24): 核心服务和数据处理
- **AI Network** (172.22.0.0/24): AI引擎和自愈系统

### 端口映射
- **80/443**: Traefik (HTTP/HTTPS)
- **3000**: Grafana Dashboard
- **5601**: Kibana Dashboard
- **9090**: Prometheus Metrics
- **9093**: Alertmanager
- **9200**: Elasticsearch API
- **5044**: Logstash Input
- **8000**: AI Engine API
- **8001**: Self-Healing API
- **8002**: Ansible API
- **8080**: API Gateway

## 快速开始

### 环境要求
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.20+ (可选)
- Helm 3.0+ (可选)
- PowerShell 5.1+ (Windows)
- Bash 4.0+ (Linux/macOS)

### 部署方式

#### 1. Docker Compose 部署
```bash
# 检查环境
./scripts/deployment/check-environment.ps1

# 启动所有服务
docker-compose up -d

# 验证部署
./scripts/deployment/verify-deployment.ps1
```

#### 2. Kubernetes Helm 部署
```bash
# 安装 Helm Chart
helm install aiops-platform ./helm/aiops-platform

# 检查状态
kubectl get pods -n aiops
```

### 访问地址
- **主控制台**: https://localhost
- **测试管理平台**: http://localhost:3001
- **测试API服务**: http://localhost:3030
- **Grafana**: https://localhost/grafana
- **Kibana**: https://localhost/kibana
- **Prometheus**: https://localhost/prometheus
- **API文档**: https://localhost/api/docs

## 功能特性

### 测试脚本管理
- 多语言支持 (Python、JavaScript、Shell、Go等)
- 可视化脚本编辑器
- Docker容器化执行环境
- 分布式测试执行
- 实时执行结果监控
- 测试报告生成和分析

### 运行时管理
- 多种运行时环境支持 (Docker、Kubernetes、本地)
- 运行时健康检查和监控
- 标签化运行时分类管理
- 平台信息自动检测
- 负载均衡和资源调度

### 监控能力
- 实时系统指标监控 (CPU、内存、磁盘、网络)
- 应用性能监控 (APM)
- 自定义业务指标监控
- 多维度告警规则

### 日志分析
- 集中化日志收集
- 实时日志搜索和过滤
- 日志模式识别
- 异常日志自动标记

### AI智能分析
- 时间序列异常检测
- 根因分析
- 容量规划预测
- 智能告警降噪

### 自动化运维
- 故障自动恢复
- 服务自动扩缩容
- 配置自动同步
- 安全补丁自动应用

## API接口

### 测试脚本API
- `GET /api/test-scripts` - 获取测试脚本列表
- `POST /api/test-scripts` - 创建测试脚本
- `GET /api/test-scripts/{id}` - 获取测试脚本详情
- `PUT /api/test-scripts/{id}` - 更新测试脚本
- `DELETE /api/test-scripts/{id}` - 删除测试脚本
- `POST /api/test-scripts/{id}/execute` - 执行测试脚本
- `POST /api/test-scripts/batch-execute` - 批量执行测试脚本
- `GET /api/test-scripts/languages` - 获取支持的语言列表
- `POST /api/test-scripts/validate` - 验证测试脚本

### 测试用例API
- `GET /api/test-cases` - 获取测试用例列表
- `POST /api/test-cases` - 创建测试用例
- `GET /api/test-cases/{id}` - 获取测试用例详情
- `PUT /api/test-cases/{id}` - 更新测试用例
- `DELETE /api/test-cases/{id}` - 删除测试用例

### 运行时管理API
- `GET /api/runtime-managers` - 获取运行时管理器列表
- `POST /api/runtime-managers` - 创建运行时管理器
- `GET /api/runtime-managers/{id}` - 获取运行时管理器详情
- `PUT /api/runtime-managers/{id}` - 更新运行时管理器
- `DELETE /api/runtime-managers/{id}` - 删除运行时管理器
- `POST /api/runtime-managers/{id}/health-check` - 运行时健康检查

### 测试运行API
- `GET /api/test-runs` - 获取测试运行列表
- `POST /api/test-runs` - 创建测试运行
- `GET /api/test-runs/{id}` - 获取测试运行详情
- `POST /api/test-runs/{id}/start` - 开始测试运行
- `POST /api/test-runs/{id}/stop` - 停止测试运行

### 运维操作API
- `POST /api/v1/services/{service}/restart` - 重启服务
- `POST /api/v1/logs/cleanup` - 清理日志
- `POST /api/v1/containers/{container}/scale` - 扩容容器
- `GET /api/v1/health` - 健康检查
- `GET /api/v1/metrics` - 获取指标

### AI分析API
- `POST /api/v1/ai/detect-anomaly` - 异常检测
- `GET /api/v1/ai/predictions` - 获取预测结果
- `POST /api/v1/ai/train-model` - 训练模型

## 安全特性

- **TLS加密**: 所有服务间通信使用TLS加密
- **身份认证**: 基于JWT的API认证
- **访问控制**: RBAC权限管理
- **审计日志**: 完整的操作审计追踪
- **密钥管理**: 集成密钥管理系统

## 监控仪表板

### 系统监控
- CPU使用率趋势
- 内存使用情况
- 磁盘I/O性能
- 网络流量分析

### 应用监控
- 服务响应时间
- 错误率统计
- 吞吐量监控
- 依赖服务状态

### AI分析
- 异常检测结果
- 预测分析图表
- 模型性能指标
- 自愈操作统计

## 测试验证

### 功能测试
```bash
# 运行集成测试
./scripts/testing/run-integration-tests.ps1

# 运行性能测试
./scripts/testing/run-performance-tests.ps1

# 异常模拟测试
./scripts/testing/simulate-failures.ps1
```

### 验证命令
```bash
# 检查所有服务状态
docker-compose ps

# 验证网络连通性
docker network ls

# 检查健康状态
curl -f http://localhost/health

# 验证AI引擎
curl -f http://localhost/api/v1/ai/health
```

## 故障排除

### 常见问题
1. **服务启动失败**: 检查端口占用和依赖服务状态
2. **网络连接问题**: 验证Docker网络配置
3. **存储空间不足**: 清理日志和临时文件
4. **AI模型加载失败**: 检查模型文件完整性

### 日志查看
```bash
# 查看服务日志
docker-compose logs -f [service-name]

# 查看AI引擎日志
docker-compose logs -f ai-engine

# 查看系统事件
kubectl get events --sort-by=.metadata.creationTimestamp
```

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: https://github.com/your-org/aiops-platform
- 问题反馈: https://github.com/your-org/aiops-platform/issues
- 文档中心: https://docs.aiops-platform.com

---

**注意**: 本平台仍在积极开发中，部分功能可能不稳定。生产环境使用前请充分测试。