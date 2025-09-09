# AIOps智能运维平台 Helm Chart

## 概述

本Helm Chart用于在Kubernetes集群中部署完整的AIOps智能运维平台，包含监控、日志、AI异常检测、自动修复等功能模块。

## 架构组件

### 核心服务
- **Traefik**: 边缘路由器和负载均衡器
- **Prometheus**: 指标收集和监控
- **Grafana**: 可视化监控面板
- **Alertmanager**: 告警管理和通知
- **Elasticsearch**: 日志存储和搜索
- **Logstash**: 日志处理和转换
- **Kibana**: 日志分析和可视化
- **Redis**: 缓存和会话存储
- **PostgreSQL**: 关系型数据库

### AI和自动化
- **AI引擎**: 异常检测和智能分析
- **API网关**: RESTful API接口
- **自愈执行器**: 自动故障修复

## 前置要求

- Kubernetes 1.19+
- Helm 3.2.0+
- 至少16GB内存和8核CPU的集群资源
- 支持动态存储卷供应（推荐使用SSD）

## 安装指南

### 1. 添加Helm依赖

```bash
# 添加必要的Helm仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add elastic https://helm.elastic.co
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add traefik https://helm.traefik.io/traefik
helm repo update
```

### 2. 创建命名空间

```bash
kubectl create namespace aiops-platform
```

### 3. 配置存储类（可选）

如果集群没有默认存储类，需要创建：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs  # 根据云提供商调整
parameters:
  type: gp3
  fsType: ext4
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### 4. 自定义配置

创建自定义values文件 `my-values.yaml`：

```yaml
# 全局配置
global:
  storageClass: "fast-ssd"
  development: false

# Ingress配置
ingress:
  enabled: true
  className: "traefik"
  hosts:
    - host: aiops.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: aiops-tls
      hosts:
        - aiops.example.com

# 监控配置
prometheus:
  enabled: true
  retention: "30d"
  storage:
    size: "50Gi"

grafana:
  enabled: true
  adminPassword: "your-secure-password"

# 日志配置
elasticsearch:
  enabled: true
  replicas: 3
  storage:
    size: "100Gi"
  auth:
    enabled: true
    password: "your-elastic-password"

# 数据库配置
postgresql:
  enabled: true
  auth:
    username: "aiops"
    database: "aiops"
    password: "your-db-password"
  storage:
    size: "20Gi"

# AI引擎配置
aiEngine:
  enabled: true
  replicas: 2
  resources:
    requests:
      memory: "2Gi"
      cpu: "1000m"
    limits:
      memory: "4Gi"
      cpu: "2000m"
```

### 5. 部署平台

```bash
# 使用默认配置部署
helm install aiops-platform ./helm -n aiops-platform

# 或使用自定义配置
helm install aiops-platform ./helm -n aiops-platform -f my-values.yaml
```

### 6. 验证部署

```bash
# 检查Pod状态
kubectl get pods -n aiops-platform

# 运行连接测试
helm test aiops-platform -n aiops-platform

# 查看服务状态
kubectl get svc -n aiops-platform
```

## 配置说明

### 主要配置项

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `global.storageClass` | 存储类名称 | `""` |
| `global.development` | 开发模式 | `true` |
| `ingress.enabled` | 启用Ingress | `true` |
| `ingress.hosts[0].host` | 主机名 | `aiops.local` |
| `prometheus.enabled` | 启用Prometheus | `true` |
| `prometheus.retention` | 数据保留期 | `15d` |
| `grafana.enabled` | 启用Grafana | `true` |
| `elasticsearch.enabled` | 启用Elasticsearch | `true` |
| `elasticsearch.replicas` | ES副本数 | `1` |
| `aiEngine.enabled` | 启用AI引擎 | `true` |
| `selfHealing.enabled` | 启用自愈功能 | `true` |

### 资源配置

每个组件都可以独立配置资源限制：

```yaml
prometheus:
  resources:
    requests:
      memory: "2Gi"
      cpu: "1000m"
    limits:
      memory: "4Gi"
      cpu: "2000m"
```

### 存储配置

```yaml
prometheus:
  persistence:
    enabled: true
    size: "50Gi"
    storageClass: "fast-ssd"
```

## 访问服务

部署完成后，可以通过以下方式访问各个服务：

### 通过Ingress（推荐）

- **主页**: https://aiops.example.com/
- **Grafana**: https://aiops.example.com/grafana/
- **Prometheus**: https://aiops.example.com/prometheus/
- **Kibana**: https://aiops.example.com/kibana/
- **AI引擎API**: https://aiops.example.com/ai/

### 通过端口转发

```bash
# Grafana
kubectl port-forward svc/aiops-platform-grafana 3000:3000 -n aiops-platform

# Prometheus
kubectl port-forward svc/aiops-platform-prometheus 9090:9090 -n aiops-platform

# Kibana
kubectl port-forward svc/aiops-platform-kibana 5601:5601 -n aiops-platform
```

## 监控和告警

### 预配置的监控指标

- 系统资源使用率（CPU、内存、磁盘、网络）
- 应用性能指标（响应时间、错误率、吞吐量）
- 数据库性能（连接数、查询时间、锁等待）
- 缓存命中率和延迟
- AI模型推理性能

### 告警规则

- CPU使用率超过80%
- 内存使用率超过85%
- 磁盘使用率超过90%
- 应用响应时间超过5秒
- 错误率超过5%
- 数据库连接数超过阈值

### 自愈规则

- 自动重启异常Pod
- 自动扩容高负载服务
- 自动清理磁盘空间
- 自动优化数据库查询

## 升级和维护

### 升级Chart

```bash
# 查看当前版本
helm list -n aiops-platform

# 升级到新版本
helm upgrade aiops-platform ./helm -n aiops-platform -f my-values.yaml

# 回滚到上一版本
helm rollback aiops-platform -n aiops-platform
```

### 备份和恢复

```bash
# 备份Prometheus数据
kubectl exec -n aiops-platform aiops-platform-prometheus-0 -- tar czf /tmp/prometheus-backup.tar.gz /prometheus

# 备份Elasticsearch数据
kubectl exec -n aiops-platform aiops-platform-elasticsearch-0 -- elasticsearch-dump --input=http://localhost:9200 --output=/tmp/es-backup.json

# 备份PostgreSQL数据
kubectl exec -n aiops-platform aiops-platform-postgresql-0 -- pg_dump -U postgres aiops > /tmp/postgres-backup.sql
```

## 故障排除

### 常见问题

1. **Pod启动失败**
   ```bash
   kubectl describe pod <pod-name> -n aiops-platform
   kubectl logs <pod-name> -n aiops-platform
   ```

2. **存储问题**
   ```bash
   kubectl get pvc -n aiops-platform
   kubectl describe pvc <pvc-name> -n aiops-platform
   ```

3. **网络连接问题**
   ```bash
   kubectl get svc -n aiops-platform
   kubectl get ingress -n aiops-platform
   ```

4. **资源不足**
   ```bash
   kubectl top nodes
   kubectl top pods -n aiops-platform
   ```

### 调试模式

启用调试模式获取更多日志信息：

```yaml
global:
  development: true
  logLevel: "debug"
```

## 安全考虑

### 生产环境配置

```yaml
global:
  development: false

# 启用认证
elasticsearch:
  auth:
    enabled: true
    password: "strong-password"

redis:
  auth:
    enabled: true
    password: "strong-password"

# 配置TLS
ingress:
  tls:
    - secretName: aiops-tls
      hosts:
        - aiops.example.com

# 网络策略
networkPolicy:
  enabled: true
  defaultDeny: true

# Pod安全策略
podSecurityPolicy:
  enabled: true
```

### 密钥管理

建议使用外部密钥管理系统（如HashiCorp Vault）：

```yaml
secrets:
  external: true
  provider: "vault"
  vaultPath: "secret/aiops"
```

## 性能优化

### 资源调优

```yaml
# 高性能配置
prometheus:
  resources:
    requests:
      memory: "8Gi"
      cpu: "2000m"
    limits:
      memory: "16Gi"
      cpu: "4000m"
  retention: "90d"
  storage:
    size: "500Gi"

elasticsearch:
  replicas: 3
  resources:
    requests:
      memory: "4Gi"
      cpu: "1000m"
    limits:
      memory: "8Gi"
      cpu: "2000m"
  storage:
    size: "1Ti"
```

### 缓存优化

```yaml
redis:
  cluster:
    enabled: true
    nodes: 6
  resources:
    requests:
      memory: "2Gi"
      cpu: "500m"
```

## 贡献指南

1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

- 📧 邮箱: support@aiops-platform.com
- 💬 Slack: [AIOps Community](https://aiops-community.slack.com)
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-org/aiops-platform/issues)
- 📖 文档: [官方文档](https://docs.aiops-platform.com)

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。