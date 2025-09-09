# AIOps 自愈系统用户手册

## 目录

1. [系统概述](#系统概述)
2. [环境要求](#环境要求)
3. [快速开始](#快速开始)
4. [详细安装指南](#详细安装指南)
5. [系统配置](#系统配置)
6. [功能使用指南](#功能使用指南)
7. [监控和告警](#监控和告警)
8. [故障排除](#故障排除)
9. [维护和升级](#维护和升级)
10. [API参考](#api参考)
11. [最佳实践](#最佳实践)
12. [常见问题](#常见问题)

---

## 系统概述

### 什么是AIOps自愈系统

AIOps自愈系统是一个基于人工智能的智能运维平台，能够自动检测系统异常、预测潜在问题并执行自动化修复操作。系统采用微服务架构，提供完整的监控、告警、分析和自愈能力。

### 核心功能

- **智能异常检测**: 基于多种AI算法的异常检测引擎
- **自动化修复**: 基于规则引擎的自愈执行器
- **全面监控**: Prometheus+Grafana+ELK完整可观测性
- **API网关**: FastAPI RESTful接口和认证授权
- **容器化部署**: Docker和Kubernetes完整支持
- **负载均衡**: Traefik动态路由和SSL终止

### 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面      │    │   API网关       │    │   AI引擎        │
│   (Grafana)     │◄──►│   (FastAPI)     │◄──►│   (异常检测)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   监控系统      │    │   自愈执行器    │    │   数据存储      │
│   (Prometheus)  │◄──►│   (规则引擎)    │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   日志系统      │    │   自动化脚本    │    │   消息队列      │
│   (ELK Stack)   │    │   (Ansible)     │    │   (RabbitMQ)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 环境要求

### 硬件要求

**最低配置**
- CPU: 4核心
- 内存: 8GB RAM
- 存储: 50GB 可用空间
- 网络: 1Gbps

**推荐配置**
- CPU: 8核心或更多
- 内存: 16GB RAM或更多
- 存储: 100GB SSD
- 网络: 10Gbps

**生产环境配置**
- CPU: 16核心或更多
- 内存: 32GB RAM或更多
- 存储: 500GB SSD (建议使用分布式存储)
- 网络: 10Gbps或更高

### 软件要求

**操作系统**
- Windows 10/11 或 Windows Server 2019/2022
- Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- macOS 11+ (仅用于开发)

**必需软件**
- Docker Desktop 4.0+ 或 Docker Engine 20.10+
- Docker Compose 2.0+
- PowerShell 7.0+ (Windows)
- Bash 4.0+ (Linux/macOS)
- Git 2.30+

**可选软件**
- Kubernetes 1.24+ (生产环境)
- Helm 3.8+ (Kubernetes部署)
- Ansible 4.0+ (自动化脚本)
- Python 3.11+ (开发和调试)

### 网络要求

**端口配置**
- 80/443: HTTP/HTTPS (Traefik)
- 3000: Grafana Dashboard
- 9090: Prometheus
- 9093: Alertmanager
- 5601: Kibana
- 9200: Elasticsearch
- 8000: API Gateway
- 5432: PostgreSQL
- 6379: Redis
- 5672: RabbitMQ

**防火墙配置**
```powershell
# Windows防火墙配置示例
New-NetFirewallRule -DisplayName "AIOps-HTTP" -Direction Inbound -Protocol TCP -LocalPort 80
New-NetFirewallRule -DisplayName "AIOps-HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443
New-NetFirewallRule -DisplayName "AIOps-Grafana" -Direction Inbound -Protocol TCP -LocalPort 3000
```

---

## 快速开始

### 5分钟快速部署

#### 步骤1: 克隆项目

```powershell
# 克隆项目到本地
git clone https://github.com/YunlongChen/aiops.git
cd aiops
```

#### 步骤2: 环境检查

```powershell
# 运行环境检查脚本
.\scripts\check-environment.ps1
```

#### 步骤3: 快速部署

```powershell
# 使用自动化部署脚本
.\scripts\deploy.ps1 -Environment development -QuickStart
```

#### 步骤4: 验证部署

```powershell
# 检查服务状态
docker-compose ps

# 访问Web界面
# Grafana: http://localhost:3000 (admin/admin)
# Kibana: http://localhost:5601
# API文档: http://localhost:8000/docs
```

### 验证安装

访问以下URL验证各组件是否正常运行：

- **Grafana监控面板**: http://localhost:3000
  - 用户名: `admin`
  - 密码: `admin`

- **Kibana日志分析**: http://localhost:5601

- **API文档**: http://localhost:8000/docs

- **Prometheus指标**: http://localhost:9090

- **Alertmanager告警**: http://localhost:9093

---

## 详细安装指南

### 方式一: Docker Compose部署 (推荐)

#### 步骤1: 准备环境

```powershell
# 1. 检查Docker版本
docker --version
docker-compose --version

# 2. 检查系统资源
Get-ComputerInfo | Select-Object TotalPhysicalMemory, CsProcessors

# 3. 创建数据目录
New-Item -ItemType Directory -Force -Path "C:\aiops-data\elasticsearch"
New-Item -ItemType Directory -Force -Path "C:\aiops-data\prometheus"
New-Item -ItemType Directory -Force -Path "C:\aiops-data\grafana"
New-Item -ItemType Directory -Force -Path "C:\aiops-data\postgres"
```

#### 步骤2: 配置环境变量

```powershell
# 复制环境配置文件
Copy-Item ".env.example" ".env"

# 编辑环境配置
notepad .env
```

**关键环境变量配置**:
```bash
# 基础配置
ENVIRONMENT=production
DOMAIN=your-domain.com

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops_user
POSTGRES_PASSWORD=your_secure_password

# Redis配置
REDIS_PASSWORD=your_redis_password

# 安全配置
JWT_SECRET_KEY=your_jwt_secret_key
API_KEY=your_api_key

# 通知配置
SMTP_SERVER=smtp.your-domain.com
SMTP_USER=alerts@your-domain.com
SMTP_PASSWORD=your_smtp_password
WEBHOOK_URL=https://hooks.slack.com/your-webhook
```

#### 步骤3: 启动服务

```powershell
# 1. 构建镜像
docker-compose build

# 2. 启动基础服务
docker-compose up -d postgres redis rabbitmq

# 等待数据库启动
Start-Sleep -Seconds 30

# 3. 启动监控服务
docker-compose up -d prometheus grafana alertmanager

# 4. 启动日志服务
docker-compose up -d elasticsearch logstash kibana

# 等待Elasticsearch启动
Start-Sleep -Seconds 60

# 5. 启动应用服务
docker-compose up -d traefik ai-engine api-gateway self-healing-executor

# 6. 检查服务状态
docker-compose ps
```

#### 步骤4: 初始化配置

```powershell
# 1. 初始化数据库
docker-compose exec api-gateway python start.py --init-db

# 2. 导入Grafana仪表板
.\scripts\import-dashboards.ps1

# 3. 配置Elasticsearch索引模板
.\scripts\setup-elasticsearch.ps1

# 4. 验证配置
.\scripts\verify-installation.ps1
```

### 方式二: Kubernetes部署

#### 步骤1: 准备Kubernetes集群

```powershell
# 检查Kubernetes集群
kubectl cluster-info
kubectl get nodes

# 安装Helm
choco install kubernetes-helm

# 添加必要的Helm仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add elastic https://helm.elastic.co
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

#### 步骤2: 创建命名空间

```powershell
# 创建命名空间
kubectl create namespace aiops
kubectl create namespace monitoring
kubectl create namespace logging
```

#### 步骤3: 部署基础服务

```powershell
# 1. 部署PostgreSQL
helm install postgres bitnami/postgresql -n aiops -f helm/values/postgres.yaml

# 2. 部署Redis
helm install redis bitnami/redis -n aiops -f helm/values/redis.yaml

# 3. 部署RabbitMQ
helm install rabbitmq bitnami/rabbitmq -n aiops -f helm/values/rabbitmq.yaml
```

#### 步骤4: 部署监控服务

```powershell
# 1. 部署Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring -f helm/values/prometheus.yaml

# 2. 部署Grafana (如果不使用kube-prometheus-stack中的)
helm install grafana grafana/grafana -n monitoring -f helm/values/grafana.yaml
```

#### 步骤5: 部署日志服务

```powershell
# 1. 部署Elasticsearch
helm install elasticsearch elastic/elasticsearch -n logging -f helm/values/elasticsearch.yaml

# 2. 部署Logstash
helm install logstash elastic/logstash -n logging -f helm/values/logstash.yaml

# 3. 部署Kibana
helm install kibana elastic/kibana -n logging -f helm/values/kibana.yaml
```

#### 步骤6: 部署应用服务

```powershell
# 部署AIOps应用
helm install aiops ./helm -n aiops -f helm/values/production.yaml

# 检查部署状态
kubectl get pods -n aiops
kubectl get services -n aiops
kubectl get ingress -n aiops
```

---

## 系统配置

### 基础配置

#### API网关配置

编辑 `config/api-config.yaml`:

```yaml
# 服务器配置
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false
  log_level: "info"

# 认证配置
auth:
  jwt_secret_key: "${JWT_SECRET_KEY}"
  jwt_algorithm: "HS256"
  access_token_expire_minutes: 30
  refresh_token_expire_days: 7

# 数据库配置
database:
  url: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
```

#### 自愈策略配置

编辑 `config/self-healing-config.yaml`:

```yaml
# 全局配置
global:
  enabled: true
  dry_run: false
  log_level: "info"
  max_concurrent_actions: 5
  action_timeout: 600
  cooldown_period: 300

# 规则引擎配置
rule_engine:
  enabled: true
  check_interval: 30
  max_concurrent_rules: 10
  rule_timeout: 300
  retry_attempts: 3
  retry_delay: 60
```

#### 监控配置

编辑 `config/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts.yml"

scrape_configs:
  - job_name: 'aiops-api'
    static_configs:
      - targets: ['api-gateway:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'aiops-ai-engine'
    static_configs:
      - targets: ['ai-engine:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### 高级配置

#### SSL/TLS配置

```powershell
# 生成SSL证书
.\traefik\generate-certs.ps1 -Domain "your-domain.com"

# 配置Traefik SSL
# 编辑 config/traefik.yml
```

#### 负载均衡配置

编辑 `config/traefik.yml`:

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entrypoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@your-domain.com
      storage: /data/acme.json
      httpChallenge:
        entryPoint: web
```

#### 数据库优化配置

```sql
-- PostgreSQL优化配置
-- 编辑 postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
max_connections = 200
```

---

## 功能使用指南

### 异常检测

#### 配置异常检测规则

1. **访问API接口**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/rules" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "high_cpu_usage",
       "description": "CPU使用率过高检测",
       "conditions": [
         {
           "metric": "cpu_usage_percent",
           "operator": ">",
           "threshold": 80,
           "duration": 300
         }
       ],
       "actions": [
         {
           "type": "ansible_playbook",
           "playbook": "system/optimize-cpu.yml"
         }
       ]
     }'
   ```

2. **通过Web界面配置**:
   - 访问 Grafana: http://localhost:3000
   - 导航到 "AIOps" > "规则管理"
   - 点击 "新建规则"
   - 填写规则详情并保存

#### 查看异常检测结果

1. **Grafana仪表板**:
   - 访问 "AIOps Overview" 仪表板
   - 查看 "异常检测" 面板
   - 查看 "告警历史" 面板

2. **API查询**:
   ```bash
   # 查看最近的异常
   curl "http://localhost:8000/api/v1/anomalies?limit=10" \
     -H "Authorization: Bearer YOUR_TOKEN"
   
   # 查看特定时间范围的异常
   curl "http://localhost:8000/api/v1/anomalies?start_time=2024-01-15T00:00:00Z&end_time=2024-01-15T23:59:59Z" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

### 自愈操作

#### 手动触发自愈

1. **通过API**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/healing/trigger" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "rule_name": "high_cpu_usage",
       "target_hosts": ["server1", "server2"],
       "parameters": {
         "cpu_threshold": 80,
         "kill_processes": true
       }
     }'
   ```

2. **通过Grafana**:
   - 访问 "AIOps" > "自愈操作"
   - 选择要执行的规则
   - 配置参数并执行

#### 查看自愈历史

```bash
# 查看自愈执行历史
curl "http://localhost:8000/api/v1/healing/history" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看特定执行的详情
curl "http://localhost:8000/api/v1/healing/executions/{execution_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 监控和指标

#### 系统指标监控

**CPU监控**:
- 指标: `cpu_usage_percent`
- 告警阈值: > 80%
- 自愈动作: 优化CPU使用

**内存监控**:
- 指标: `memory_usage_percent`
- 告警阈值: > 85%
- 自愈动作: 清理内存缓存

**磁盘监控**:
- 指标: `disk_usage_percent`
- 告警阈值: > 85%
- 自愈动作: 清理临时文件

#### 应用指标监控

**响应时间**:
- 指标: `http_request_duration_seconds`
- 告警阈值: > 5秒
- 自愈动作: 重启服务或优化配置

**错误率**:
- 指标: `http_requests_total{status=~"5.."}`
- 告警阈值: > 5%
- 自愈动作: 检查日志并重启服务

### 日志分析

#### Kibana使用指南

1. **访问Kibana**: http://localhost:5601

2. **创建索引模式**:
   - 导航到 "Stack Management" > "Index Patterns"
   - 点击 "Create index pattern"
   - 输入 `aiops-*` 作为索引模式
   - 选择 `@timestamp` 作为时间字段

3. **创建可视化**:
   - 导航到 "Visualize Library"
   - 选择可视化类型 (柱状图、饼图等)
   - 配置数据源和聚合

4. **创建仪表板**:
   - 导航到 "Dashboard"
   - 点击 "Create dashboard"
   - 添加已创建的可视化

#### 日志查询示例

```json
# 查询错误日志
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "level": "ERROR"
          }
        },
        {
          "range": {
            "@timestamp": {
              "gte": "now-1h"
            }
          }
        }
      ]
    }
  }
}

# 查询特定服务的日志
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "service": "api-gateway"
          }
        },
        {
          "match": {
            "message": "authentication failed"
          }
        }
      ]
    }
  }
}
```

---

## 监控和告警

### Prometheus配置

#### 添加监控目标

编辑 `config/prometheus.yml`:

```yaml
scrape_configs:
  # 添加新的监控目标
  - job_name: 'custom-app'
    static_configs:
      - targets: ['app-server:8080']
    metrics_path: '/actuator/prometheus'
    scrape_interval: 15s
    scrape_timeout: 10s
```

#### 自定义指标

```python
# 在应用中添加自定义指标
from prometheus_client import Counter, Histogram, Gauge

# 计数器
request_count = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])

# 直方图
request_duration = Histogram('app_request_duration_seconds', 'Request duration')

# 仪表盘
active_users = Gauge('app_active_users', 'Active users')

# 使用示例
request_count.labels(method='GET', endpoint='/api/users').inc()
with request_duration.time():
    # 处理请求
    pass
active_users.set(100)
```

### Grafana仪表板

#### 导入预定义仪表板

```powershell
# 导入所有仪表板
.\scripts\import-dashboards.ps1

# 导入特定仪表板
.\scripts\import-dashboards.ps1 -Dashboard "system-overview"
```

#### 创建自定义仪表板

1. **访问Grafana**: http://localhost:3000
2. **登录**: admin/admin
3. **创建仪表板**:
   - 点击 "+" > "Dashboard"
   - 点击 "Add new panel"
   - 配置查询和可视化
   - 保存仪表板

#### 常用查询示例

```promql
# CPU使用率
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100

# 磁盘使用率
100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes)

# HTTP请求率
rate(http_requests_total[5m])

# HTTP错误率
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100
```

### 告警配置

#### Alertmanager配置

编辑 `config/alertmanager.yml`:

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@your-domain.com'
  smtp_auth_username: 'alerts@your-domain.com'
  smtp_auth_password: 'your-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    email_configs:
      - to: 'admin@your-domain.com'
        subject: 'AIOps Alert: {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
    webhook_configs:
      - url: 'http://localhost:8000/api/v1/webhooks/alerts'
        send_resolved: true
```

#### 告警规则

编辑 `config/alerts.yml`:

```yaml
groups:
  - name: system.rules
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for more than 5 minutes."

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for more than 3 minutes."

      - alert: DiskSpaceLow
        expr: 100 - ((node_filesystem_avail_bytes * 100) / node_filesystem_size_bytes) > 85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk usage is above 85% for more than 5 minutes."
```

---

## 故障排除

### 常见问题诊断

#### 服务启动失败

**问题**: Docker容器无法启动

**诊断步骤**:
```powershell
# 1. 检查容器状态
docker-compose ps

# 2. 查看容器日志
docker-compose logs [service-name]

# 3. 检查资源使用
docker stats

# 4. 检查端口占用
netstat -an | findstr :8000
```

**解决方案**:
```powershell
# 重启服务
docker-compose restart [service-name]

# 重建容器
docker-compose up -d --force-recreate [service-name]

# 清理并重启
docker-compose down
docker system prune -f
docker-compose up -d
```

#### 数据库连接问题

**问题**: 应用无法连接到数据库

**诊断步骤**:
```powershell
# 1. 检查数据库容器状态
docker-compose ps postgres

# 2. 测试数据库连接
docker-compose exec postgres psql -U aiops_user -d aiops -c "SELECT 1;"

# 3. 检查网络连接
docker-compose exec api-gateway ping postgres
```

**解决方案**:
```powershell
# 重启数据库
docker-compose restart postgres

# 检查环境变量
docker-compose exec api-gateway env | grep POSTGRES

# 重新初始化数据库
docker-compose exec api-gateway python start.py --init-db
```

#### 内存不足问题

**问题**: 系统内存使用过高

**诊断步骤**:
```powershell
# 1. 检查系统内存
Get-ComputerInfo | Select-Object TotalPhysicalMemory, AvailablePhysicalMemory

# 2. 检查容器内存使用
docker stats --no-stream

# 3. 检查Elasticsearch堆内存
curl "http://localhost:9200/_cat/nodes?v&h=name,heap.percent,heap.current,heap.max,ram.percent,ram.current,ram.max"
```

**解决方案**:
```powershell
# 调整Elasticsearch堆内存
# 编辑 docker-compose.yml
# environment:
#   - "ES_JAVA_OPTS=-Xms2g -Xmx2g"

# 重启服务
docker-compose restart elasticsearch

# 清理缓存
curl -X POST "http://localhost:9200/_cache/clear"
```

### 性能优化

#### Elasticsearch优化

```bash
# 1. 调整刷新间隔
curl -X PUT "http://localhost:9200/aiops-*/_settings" -H 'Content-Type: application/json' -d'
{
  "index": {
    "refresh_interval": "30s"
  }
}'

# 2. 优化索引模板
curl -X PUT "http://localhost:9200/_template/aiops" -H 'Content-Type: application/json' -d'
{
  "index_patterns": ["aiops-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "30s"
  }
}'

# 3. 强制合并索引
curl -X POST "http://localhost:9200/aiops-*/_forcemerge?max_num_segments=1"
```

#### PostgreSQL优化

```sql
-- 1. 分析表统计信息
ANALYZE;

-- 2. 重建索引
REINDEX DATABASE aiops;

-- 3. 清理死元组
VACUUM FULL;

-- 4. 查看慢查询
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

#### 应用性能优化

```python
# 1. 启用连接池
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30
)

# 2. 启用查询缓存
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_by_id(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# 3. 异步处理
import asyncio

async def process_alerts():
    tasks = []
    for alert in alerts:
        task = asyncio.create_task(process_single_alert(alert))
        tasks.append(task)
    await asyncio.gather(*tasks)
```

### 日志分析

#### 查看系统日志

```powershell
# 1. 查看所有服务日志
docker-compose logs -f

# 2. 查看特定服务日志
docker-compose logs -f api-gateway

# 3. 查看最近的错误日志
docker-compose logs --tail=100 | Select-String "ERROR"

# 4. 导出日志到文件
docker-compose logs > aiops-logs.txt
```

#### Kibana日志查询

```json
# 查询API错误
{
  "query": {
    "bool": {
      "must": [
        {"match": {"service": "api-gateway"}},
        {"match": {"level": "ERROR"}},
        {"range": {"@timestamp": {"gte": "now-1h"}}}
      ]
    }
  }
}

# 查询慢查询
{
  "query": {
    "bool": {
      "must": [
        {"match": {"message": "slow query"}},
        {"range": {"duration": {"gte": 1000}}}
      ]
    }
  }
}
```

---

## 维护和升级

### 定期维护任务

#### 每日维护

```powershell
# 创建每日维护脚本
# daily-maintenance.ps1

# 1. 检查服务状态
docker-compose ps

# 2. 检查磁盘空间
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name="Size(GB)";Expression={[math]::Round($_.Size/1GB,2)}}, @{Name="FreeSpace(GB)";Expression={[math]::Round($_.FreeSpace/1GB,2)}}

# 3. 清理旧日志
docker system prune -f --filter "until=24h"

# 4. 备份配置文件
Compress-Archive -Path "config\*" -DestinationPath "backups\config-$(Get-Date -Format 'yyyyMMdd').zip"

# 5. 检查告警状态
curl -s "http://localhost:9093/api/v1/alerts" | ConvertFrom-Json
```

#### 每周维护

```powershell
# 创建每周维护脚本
# weekly-maintenance.ps1

# 1. 数据库维护
docker-compose exec postgres psql -U aiops_user -d aiops -c "VACUUM ANALYZE;"

# 2. Elasticsearch索引优化
curl -X POST "http://localhost:9200/_forcemerge?max_num_segments=1"

# 3. 清理旧索引
.\scripts\cleanup-old-indices.ps1 -RetentionDays 30

# 4. 更新仪表板
.\scripts\update-dashboards.ps1

# 5. 性能报告
.\scripts\generate-performance-report.ps1
```

#### 每月维护

```powershell
# 创建每月维护脚本
# monthly-maintenance.ps1

# 1. 完整备份
.\scripts\full-backup.ps1

# 2. 安全更新检查
.\scripts\security-scan.ps1

# 3. 容量规划
.\scripts\capacity-planning.ps1

# 4. 性能基准测试
.\scripts\benchmark-test.ps1
```

### 系统升级

#### 升级准备

```powershell
# 1. 备份当前系统
.\scripts\full-backup.ps1

# 2. 检查系统状态
.\scripts\health-check.ps1

# 3. 下载新版本
git fetch origin
git checkout v2.0.0

# 4. 检查变更
git diff v1.0.0..v2.0.0 --name-only
```

#### 滚动升级

```powershell
# 1. 升级数据库
docker-compose exec postgres pg_dump aiops > backup-$(Get-Date -Format 'yyyyMMdd').sql
docker-compose pull postgres
docker-compose up -d postgres

# 2. 升级应用服务 (逐个升级)
$services = @('ai-engine', 'api-gateway', 'self-healing-executor')
foreach ($service in $services) {
    Write-Host "Upgrading $service..."
    docker-compose pull $service
    docker-compose up -d --no-deps $service
    Start-Sleep -Seconds 30
    
    # 健康检查
    $health = docker-compose ps $service
    if ($health -notmatch "Up") {
        Write-Error "$service upgrade failed"
        # 回滚
        docker-compose up -d --no-deps $service
        break
    }
}

# 3. 升级监控服务
docker-compose pull prometheus grafana
docker-compose up -d prometheus grafana
```

#### 回滚计划

```powershell
# 创建回滚脚本
# rollback.ps1

param(
    [Parameter(Mandatory=$true)]
    [string]$Version
)

# 1. 停止当前服务
docker-compose down

# 2. 切换到指定版本
git checkout $Version

# 3. 恢复配置文件
Expand-Archive -Path "backups\config-backup.zip" -DestinationPath "config" -Force

# 4. 恢复数据库
docker-compose up -d postgres
Start-Sleep -Seconds 30
docker-compose exec postgres psql -U aiops_user -d aiops < backup.sql

# 5. 启动服务
docker-compose up -d

# 6. 验证回滚
.\scripts\health-check.ps1
```

### 备份和恢复

#### 自动备份脚本

```powershell
# backup.ps1
param(
    [string]$BackupPath = "C:\aiops-backups",
    [int]$RetentionDays = 30
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $BackupPath $timestamp

# 创建备份目录
New-Item -ItemType Directory -Force -Path $backupDir

# 1. 备份配置文件
Compress-Archive -Path "config\*" -DestinationPath "$backupDir\config.zip"

# 2. 备份数据库
docker-compose exec postgres pg_dump -U aiops_user aiops > "$backupDir\database.sql"

# 3. 备份Elasticsearch数据
curl -X PUT "http://localhost:9200/_snapshot/backup/snapshot_$timestamp" -H 'Content-Type: application/json' -d'{
  "indices": "aiops-*",
  "ignore_unavailable": true,
  "include_global_state": false
}'

# 4. 备份Grafana仪表板
curl -H "Authorization: Bearer $GRAFANA_API_KEY" "http://localhost:3000/api/search" | ConvertFrom-Json | ForEach-Object {
    $dashboard = curl -H "Authorization: Bearer $GRAFANA_API_KEY" "http://localhost:3000/api/dashboards/uid/$($_.uid)"
    $dashboard | Out-File "$backupDir\dashboard-$($_.uid).json"
}

# 5. 清理旧备份
Get-ChildItem $BackupPath | Where-Object {$_.CreationTime -lt (Get-Date).AddDays(-$RetentionDays)} | Remove-Item -Recurse -Force

Write-Host "Backup completed: $backupDir"
```

#### 恢复脚本

```powershell
# restore.ps1
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath
)

if (-not (Test-Path $BackupPath)) {
    Write-Error "Backup path not found: $BackupPath"
    exit 1
}

# 1. 停止服务
docker-compose down

# 2. 恢复配置文件
Expand-Archive -Path "$BackupPath\config.zip" -DestinationPath "config" -Force

# 3. 启动数据库
docker-compose up -d postgres
Start-Sleep -Seconds 30

# 4. 恢复数据库
docker-compose exec postgres psql -U aiops_user -d aiops < "$BackupPath\database.sql"

# 5. 启动Elasticsearch
docker-compose up -d elasticsearch
Start-Sleep -Seconds 60

# 6. 恢复Elasticsearch数据
$snapshotName = (Get-Item $BackupPath).Name
curl -X POST "http://localhost:9200/_snapshot/backup/$snapshotName/_restore" -H 'Content-Type: application/json' -d'{
  "indices": "aiops-*",
  "ignore_unavailable": true,
  "include_global_state": false
}'

# 7. 启动所有服务
docker-compose up -d

# 8. 验证恢复
Start-Sleep -Seconds 60
.\scripts\health-check.ps1

Write-Host "Restore completed from: $BackupPath"
```

---

## API参考

### 认证

#### 获取访问令牌

```bash
# 用户名密码登录
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password"
  }'

# 响应
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### 刷新令牌

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Authorization: Bearer REFRESH_TOKEN"
```

### 系统管理

#### 健康检查

```bash
# 系统健康状态
curl "http://localhost:8000/api/v1/health"

# 响应
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "elasticsearch": "healthy",
    "ai_engine": "healthy"
  },
  "metrics": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "disk_usage": 23.1
  }
}
```

#### 系统信息

```bash
# 获取系统信息
curl "http://localhost:8000/api/v1/system/info" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 响应
{
  "version": "2.0.0",
  "build_time": "2024-01-15T08:00:00Z",
  "uptime": 86400,
  "environment": "production",
  "components": {
    "ai_engine": "2.0.0",
    "rule_engine": "2.0.0",
    "api_gateway": "2.0.0"
  }
}
```

### 规则管理

#### 创建规则

```bash
curl -X POST "http://localhost:8000/api/v1/rules" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "high_memory_usage",
    "description": "内存使用率过高自愈",
    "enabled": true,
    "priority": 1,
    "conditions": [
      {
        "metric": "memory_usage_percent",
        "operator": ">",
        "threshold": 85,
        "duration": 180
      }
    ],
    "actions": [
      {
        "type": "ansible_playbook",
        "playbook": "system/clear-memory.yml",
        "parameters": {
          "clear_cache": true,
          "restart_services": false
        }
      },
      {
        "type": "notification",
        "message": "内存使用率过高，已清理缓存"
      }
    ],
    "cooldown": 300
  }'
```

#### 查询规则

```bash
# 获取所有规则
curl "http://localhost:8000/api/v1/rules" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取特定规则
curl "http://localhost:8000/api/v1/rules/high_memory_usage" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 搜索规则
curl "http://localhost:8000/api/v1/rules?search=memory&enabled=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 更新规则

```bash
curl -X PUT "http://localhost:8000/api/v1/rules/high_memory_usage" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "threshold": 90
  }'
```

#### 删除规则

```bash
curl -X DELETE "http://localhost:8000/api/v1/rules/high_memory_usage" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 异常检测

#### 查询异常

```bash
# 获取最近的异常
curl "http://localhost:8000/api/v1/anomalies?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按时间范围查询
curl "http://localhost:8000/api/v1/anomalies?start_time=2024-01-15T00:00:00Z&end_time=2024-01-15T23:59:59Z" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 按严重程度查询
curl "http://localhost:8000/api/v1/anomalies?severity=critical" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 异常统计

```bash
# 获取异常统计
curl "http://localhost:8000/api/v1/anomalies/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 响应
{
  "total_count": 156,
  "by_severity": {
    "critical": 12,
    "warning": 89,
    "info": 55
  },
  "by_category": {
    "system": 78,
    "application": 45,
    "network": 33
  },
  "trend": {
    "last_24h": 23,
    "last_7d": 156,
    "last_30d": 678
  }
}
```

### 自愈操作

#### 手动触发自愈

```bash
curl -X POST "http://localhost:8000/api/v1/healing/trigger" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "high_cpu_usage",
    "target_hosts": ["server1", "server2"],
    "parameters": {
      "cpu_threshold": 80,
      "kill_processes": true
    },
    "dry_run": false
  }'
```

#### 查询执行历史

```bash
# 获取执行历史
curl "http://localhost:8000/api/v1/healing/executions" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取特定执行详情
curl "http://localhost:8000/api/v1/healing/executions/12345" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 停止执行

```bash
curl -X POST "http://localhost:8000/api/v1/healing/executions/12345/stop" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 监控指标

#### 获取指标

```bash
# 获取系统指标
curl "http://localhost:8000/api/v1/metrics/system" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 获取应用指标
curl "http://localhost:8000/api/v1/metrics/application" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 自定义查询
curl "http://localhost:8000/api/v1/metrics/query?metric=cpu_usage&start_time=2024-01-15T00:00:00Z&end_time=2024-01-15T23:59:59Z" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 最佳实践

### 安全配置

#### 1. 网络安全

```yaml
# docker-compose.yml 网络配置
networks:
  aiops-internal:
    driver: bridge
    internal: true
  aiops-external:
    driver: bridge

services:
  api-gateway:
    networks:
      - aiops-external
      - aiops-internal
  
  postgres:
    networks:
      - aiops-internal  # 仅内部网络
```

#### 2. 密码和密钥管理

```powershell
# 生成强密码
function New-SecurePassword {
    param([int]$Length = 32)
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*'
    $password = ''
    for ($i = 0; $i -lt $Length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

# 使用Docker Secrets
docker secret create postgres_password password.txt
docker secret create jwt_secret jwt_secret.txt
```

#### 3. SSL/TLS配置

```yaml
# traefik.yml
entryPoints:
  websecure:
    address: ":443"
    http:
      tls:
        options: default

tls:
  options:
    default:
      sslProtocols:
        - "TLSv1.2"
        - "TLSv1.3"
      cipherSuites:
        - "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
        - "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305"
```

### 性能优化

#### 1. 数据库优化

```sql
-- 创建适当的索引
CREATE INDEX CONCURRENTLY idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX CONCURRENTLY idx_executions_status ON executions(status, created_at);

-- 分区表
CREATE TABLE anomalies_2024_01 PARTITION OF anomalies
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 定期维护
SET maintenance_work_mem = '1GB';
VACUUM ANALYZE;
REINDEX DATABASE aiops;
```

#### 2. 缓存策略

```python
# Redis缓存配置
from redis import Redis
from functools import wraps
import json

redis_client = Redis(host='redis', port=6379, decode_responses=True)

def cache_result(expiration=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expiration, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(expiration=600)
def get_system_metrics():
    # 获取系统指标的耗时操作
    pass
```

#### 3. 异步处理

```python
# 异步任务处理
import asyncio
from celery import Celery

# Celery配置
celery_app = Celery('aiops', broker='redis://redis:6379/0')

@celery_app.task
def process_anomaly_async(anomaly_data):
    """异步处理异常数据"""
    # 处理异常检测逻辑
    return process_anomaly(anomaly_data)

# 批量异步处理
async def process_multiple_anomalies(anomalies):
    tasks = []
    for anomaly in anomalies:
        task = process_anomaly_async.delay(anomaly)
        tasks.append(task)
    
    # 等待所有任务完成
    results = [task.get() for task in tasks]
    return results
```

### 监控和告警

#### 1. 告警规则设计

```yaml
# 分层告警策略
groups:
  - name: critical.rules
    rules:
      - alert: SystemDown
        expr: up == 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "系统服务不可用"
          description: "{{ $labels.instance }} 服务已停止"

  - name: warning.rules
    rules:
      - alert: HighResourceUsage
        expr: cpu_usage > 80 or memory_usage > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "资源使用率过高"
```

#### 2. 告警抑制和分组

```yaml
# alertmanager.yml
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['instance']

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
    - match:
        severity: warning
      receiver: 'warning-alerts'
```

### 容量规划

#### 1. 资源监控

```promql
# CPU使用率趋势
rate(cpu_usage_total[1h])

# 内存使用率预测
predict_linear(memory_usage_bytes[1h], 3600 * 24)

# 磁盘空间预测
predict_linear(disk_free_bytes[1h], 3600 * 24 * 7)

# 网络流量趋势
rate(network_bytes_total[1h])
```

#### 2. 自动扩缩容

```yaml
# kubernetes HPA配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aiops-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 常见问题

### Q1: 系统启动后无法访问Web界面

**A**: 检查以下几点：
1. 确认所有容器都已启动：`docker-compose ps`
2. 检查端口是否被占用：`netstat -an | findstr :3000`
3. 查看Traefik日志：`docker-compose logs traefik`
4. 检查防火墙设置

### Q2: Elasticsearch内存使用过高

**A**: 优化方案：
1. 调整堆内存大小：`ES_JAVA_OPTS=-Xms2g -Xmx2g`
2. 清理旧索引：`curl -X DELETE "http://localhost:9200/aiops-2024-01-*"`
3. 优化索引设置：减少副本数量
4. 启用索引生命周期管理

### Q3: 自愈脚本执行失败

**A**: 排查步骤：
1. 检查Ansible连接：`ansible all -m ping`
2. 验证脚本语法：`ansible-playbook --syntax-check playbook.yml`
3. 查看执行日志：检查API日志和Ansible日志
4. 确认目标主机权限和依赖

### Q4: 告警通知未收到

**A**: 检查配置：
1. 验证Alertmanager配置：`curl http://localhost:9093/api/v1/status`
2. 测试SMTP连接：使用telnet测试邮件服务器
3. 检查Webhook URL：确认Slack/Teams配置正确
4. 查看Alertmanager日志

### Q5: 数据库连接池耗尽

**A**: 优化方案：
1. 增加连接池大小：`pool_size=20, max_overflow=30`
2. 优化查询性能：添加索引，优化SQL
3. 启用连接池监控
4. 检查长时间运行的查询

### Q6: AI模型预测准确率低

**A**: 改进方法：
1. 增加训练数据量
2. 调整模型参数和特征工程
3. 使用集成学习方法
4. 定期重新训练模型
5. 验证数据质量和标注准确性

### Q7: 系统性能下降

**A**: 性能调优：
1. 分析性能瓶颈：使用APM工具
2. 数据库优化：索引、查询优化
3. 缓存策略：Redis缓存热点数据
4. 负载均衡：增加实例数量
5. 资源监控：CPU、内存、磁盘、网络

---

## 技术支持

### 联系方式

- **技术支持邮箱**: support@aiops.com
- **文档网站**: https://docs.aiops.com
- **GitHub仓库**: https://github.com/YunlongChen/aiops
- **社区论坛**: https://community.aiops.com

### 支持级别

**基础支持**:
- 文档和FAQ
- 社区论坛支持
- GitHub Issues

**标准支持**:
- 邮件技术支持
- 8x5工作时间响应
- 远程协助

**企业支持**:
- 7x24小时支持
- 专属技术顾问
- 现场服务
- 定制开发

### 版本支持策略

- **当前版本**: 完整支持和更新
- **前一版本**: 安全更新和重要修复
- **更早版本**: 仅安全更新

---

## 附录

### A. 端口列表

| 服务 | 端口 | 协议 | 描述 |
|------|------|------|------|
| Traefik | 80/443 | HTTP/HTTPS | 反向代理和负载均衡 |
| API Gateway | 8000 | HTTP | RESTful API接口 |
| AI Engine | 8001 | HTTP | AI异常检测服务 |
| Grafana | 3000 | HTTP | 监控仪表板 |
| Prometheus | 9090 | HTTP | 指标收集和存储 |
| Alertmanager | 9093 | HTTP | 告警管理 |
| Elasticsearch | 9200 | HTTP | 搜索和分析引擎 |
| Kibana | 5601 | HTTP | 日志分析界面 |
| PostgreSQL | 5432 | TCP | 关系型数据库 |
| Redis | 6379 | TCP | 缓存和消息队列 |
| RabbitMQ | 5672/15672 | AMQP/HTTP | 消息队列和管理界面 |

### B. 环境变量参考

```bash
# 基础配置
ENVIRONMENT=production
DOMAIN=aiops.example.com
TIMEZONE=Asia/Shanghai

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops_user
POSTGRES_PASSWORD=secure_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=redis_password
REDIS_DB=0

# 安全配置
JWT_SECRET_KEY=your_jwt_secret_key_here
API_KEY=your_api_key_here
ENCRYPTION_KEY=your_encryption_key_here

# 监控配置
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=admin_password
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
ELK_RETENTION_DAYS=30

# AI引擎配置
AI_MODEL_PATH=/app/models
AI_BATCH_SIZE=32
AI_PREDICTION_THRESHOLD=0.8

# 通知配置
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=smtp_password
SMTP_TLS=true
```

### C. 命令行工具

```powershell
# 系统管理命令
.\scripts\aiops.ps1 status          # 查看系统状态
.\scripts\aiops.ps1 start           # 启动系统
.\scripts\aiops.ps1 stop            # 停止系统
.\scripts\aiops.ps1 restart         # 重启系统
.\scripts\aiops.ps1 logs [service]  # 查看日志
.\scripts\aiops.ps1 backup          # 创建备份
.\scripts\aiops.ps1 restore [path]  # 恢复备份
.\scripts\aiops.ps1 update          # 更新系统
.\scripts\aiops.ps1 health          # 健康检查

# 规则管理命令
.\scripts\rules.ps1 list            # 列出所有规则
.\scripts\rules.ps1 create [file]   # 创建规则
.\scripts\rules.ps1 update [name]   # 更新规则
.\scripts\rules.ps1 delete [name]   # 删除规则
.\scripts\rules.ps1 test [name]     # 测试规则

# 监控命令
.\scripts\monitor.ps1 metrics       # 查看系统指标
.\scripts\monitor.ps1 alerts        # 查看告警
.\scripts\monitor.ps1 dashboard     # 打开仪表板
```

### D. 配置文件模板

详细的配置文件模板请参考项目中的 `config/templates/` 目录。

---

**文档版本**: v2.0.0  
**最后更新**: 2024-01-15  
**维护者**: AIOps开发团队

---

*本手册将持续更新，请关注最新版本。如有问题或建议，请联系技术支持团队。*