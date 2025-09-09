# AIOps平台 Helm部署用户手册

## 1. 概述

本手册提供AIOps平台的Helm部署指南，包括Chart安装、配置管理、升级维护等完整流程。

### 1.1 系统要求

- **Kubernetes版本**: >= 1.20.0
- **Helm版本**: >= 3.8.0
- **存储**: 支持动态存储卷供应
- **网络**: 支持LoadBalancer或Ingress
- **资源**: 最小8核16GB内存

### 1.2 架构组件

- **监控堆栈**: Prometheus + Grafana + AlertManager
- **日志处理**: Elasticsearch + Logstash + Kibana
- **缓存存储**: Redis Cluster
- **数据库**: PostgreSQL
- **网关代理**: Traefik
- **AI引擎**: 异常检测和自愈执行器

## 2. 环境准备

### 2.1 Kubernetes集群准备

```bash
# 检查集群状态
kubectl cluster-info
kubectl get nodes

# 检查存储类
kubectl get storageclass

# 创建命名空间
kubectl create namespace aiops
```

### 2.2 Helm安装和配置

```bash
# 安装Helm (如果未安装)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 验证Helm版本
helm version

# 添加必需的Helm仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add elastic https://helm.elastic.co
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add traefik https://traefik.github.io/charts

# 更新仓库索引
helm repo update
```

## 3. 快速部署

### 3.1 使用预构建Chart包

```bash
# 下载Chart包
wget https://releases.aiops-platform.com/aiops-platform-1.0.0.tgz

# 安装AIOps平台
helm install aiops aiops-platform-1.0.0.tgz \
  --namespace aiops \
  --create-namespace \
  --wait --timeout=30m
```

### 3.2 从源码部署

```bash
# 克隆项目
git clone https://github.com/aiops-platform/aiops-platform.git
cd aiops-platform

# 更新依赖
helm dependency update helm/

# 安装平台
helm install aiops helm/ \
  --namespace aiops \
  --create-namespace \
  --wait --timeout=30m
```

### 3.3 部署验证

```bash
# 检查部署状态
helm status aiops -n aiops

# 查看Pod状态
kubectl get pods -n aiops

# 查看服务状态
kubectl get svc -n aiops

# 查看Ingress状态
kubectl get ingress -n aiops
```

## 4. 配置管理

### 4.1 自定义配置文件

创建 `values-custom.yaml` 配置文件：

```yaml
# 全局配置
global:
  imageRegistry: "your-registry.com"
  storageClass: "fast-ssd"
  domain: "aiops.your-company.com"

# 监控配置
prometheus:
  enabled: true
  retention: "30d"
  storage:
    size: "100Gi"

grafana:
  enabled: true
  adminPassword: "your-secure-password"
  persistence:
    enabled: true
    size: "10Gi"

# 日志配置
elasticsearch:
  enabled: true
  replicas: 3
  storage:
    size: "200Gi"

kibana:
  enabled: true
  ingress:
    enabled: true
    hosts:
      - kibana.aiops.your-company.com

# 数据库配置
postgresql:
  enabled: true
  auth:
    postgresPassword: "your-db-password"
    database: "aiops"
  primary:
    persistence:
      size: "50Gi"

# 缓存配置
redis:
  enabled: true
  auth:
    enabled: true
    password: "your-redis-password"
  master:
    persistence:
      size: "20Gi"

# 网关配置
traefik:
  enabled: true
  service:
    type: LoadBalancer
  ports:
    web:
      port: 80
    websecure:
      port: 443

# AI引擎配置
aiEngine:
  enabled: true
  replicas: 2
  resources:
    requests:
      cpu: "1000m"
      memory: "2Gi"
    limits:
      cpu: "2000m"
      memory: "4Gi"

# 自愈执行器配置
selfHealing:
  enabled: true
  replicas: 1
  autoScaling:
    enabled: true
    minReplicas: 1
    maxReplicas: 5
```

### 4.2 使用自定义配置部署

```bash
# 使用自定义配置安装
helm install aiops helm/ \
  --namespace aiops \
  --create-namespace \
  --values values-custom.yaml \
  --wait --timeout=30m

# 或升级现有部署
helm upgrade aiops helm/ \
  --namespace aiops \
  --values values-custom.yaml \
  --wait --timeout=30m
```

## 5. 升级和维护

### 5.1 升级Chart

```bash
# 检查当前版本
helm list -n aiops

# 获取当前配置
helm get values aiops -n aiops > current-values.yaml

# 升级到新版本
helm upgrade aiops aiops-platform-1.1.0.tgz \
  --namespace aiops \
  --values current-values.yaml \
  --wait --timeout=30m

# 回滚到上一版本（如需要）
helm rollback aiops 1 -n aiops
```

### 5.2 配置更新

```bash
# 更新特定配置
helm upgrade aiops helm/ \
  --namespace aiops \
  --reuse-values \
  --set grafana.adminPassword=new-password \
  --wait

# 批量更新配置
helm upgrade aiops helm/ \
  --namespace aiops \
  --values updated-values.yaml \
  --wait
```

### 5.3 备份和恢复

```bash
# 备份Helm配置
helm get all aiops -n aiops > aiops-backup.yaml

# 备份持久化数据
kubectl get pvc -n aiops
# 根据存储后端执行相应备份操作

# 恢复部署
helm install aiops-restored helm/ \
  --namespace aiops-restore \
  --create-namespace \
  --values restored-values.yaml
```

## 6. 监控和告警

### 6.1 访问监控界面

```bash
# 获取Grafana访问地址
kubectl get ingress -n aiops grafana-ingress

# 或使用端口转发
kubectl port-forward -n aiops svc/aiops-grafana 3000:80
# 访问 http://localhost:3000

# 获取Grafana管理员密码
kubectl get secret -n aiops aiops-grafana -o jsonpath="{.data.admin-password}" | base64 -d
```

### 6.2 配置告警规则

```yaml
# prometheus-rules.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aiops-alert-rules
  namespace: aiops
data:
  aiops.rules: |
    groups:
    - name: aiops.rules
      rules:
      - alert: AIOpsServiceDown
        expr: up{job="aiops-api-gateway"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "AIOps API Gateway is down"
          description: "AIOps API Gateway has been down for more than 1 minute."
      
      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 90% for more than 5 minutes."
```

```bash
# 应用告警规则
kubectl apply -f prometheus-rules.yaml
```

## 7. 故障排除

### 7.1 常见问题诊断

```bash
# 检查Helm部署状态
helm status aiops -n aiops

# 查看部署历史
helm history aiops -n aiops

# 检查Pod日志
kubectl logs -n aiops deployment/aiops-api-gateway
kubectl logs -n aiops deployment/aiops-ai-engine

# 检查事件
kubectl get events -n aiops --sort-by='.lastTimestamp'

# 检查资源使用
kubectl top pods -n aiops
kubectl top nodes
```

### 7.2 存储问题

```bash
# 检查PVC状态
kubectl get pvc -n aiops

# 检查存储类
kubectl get storageclass

# 检查卷挂载
kubectl describe pod -n aiops <pod-name>
```

### 7.3 网络问题

```bash
# 检查服务端点
kubectl get endpoints -n aiops

# 检查网络策略
kubectl get networkpolicy -n aiops

# 测试服务连通性
kubectl run test-pod --image=busybox -it --rm -- /bin/sh
# 在Pod内执行: nslookup aiops-api-gateway.aiops.svc.cluster.local
```

## 8. 性能优化

### 8.1 资源调优

```yaml
# 高性能配置示例
aiEngine:
  resources:
    requests:
      cpu: "2000m"
      memory: "4Gi"
    limits:
      cpu: "4000m"
      memory: "8Gi"
  nodeSelector:
    node-type: "compute-optimized"
  tolerations:
    - key: "dedicated"
      operator: "Equal"
      value: "aiops"
      effect: "NoSchedule"

prometheus:
  server:
    resources:
      requests:
        cpu: "1000m"
        memory: "8Gi"
      limits:
        cpu: "2000m"
        memory: "16Gi"
    retention: "15d"
    retentionSize: "100GB"
```

### 8.2 自动扩缩容

```yaml
# HPA配置
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: aiops-api-gateway-hpa
  namespace: aiops
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: aiops-api-gateway
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

## 9. 安全配置

### 9.1 RBAC配置

```yaml
# rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aiops-service-account
  namespace: aiops
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: aiops-cluster-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "endpoints"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: aiops-cluster-role-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: aiops-cluster-role
subjects:
- kind: ServiceAccount
  name: aiops-service-account
  namespace: aiops
```

### 9.2 网络安全

```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: aiops-network-policy
  namespace: aiops
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: aiops
    - namespaceSelector:
        matchLabels:
          name: monitoring
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: aiops
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
```

## 10. 卸载和清理

### 10.1 卸载Helm部署

```bash
# 卸载AIOps平台
helm uninstall aiops -n aiops

# 删除命名空间（可选）
kubectl delete namespace aiops
```

### 10.2 清理持久化数据

```bash
# 查看剩余PVC
kubectl get pvc -n aiops

# 删除PVC（注意：这将永久删除数据）
kubectl delete pvc -n aiops --all

# 清理自定义资源
kubectl get crd | grep aiops
kubectl delete crd <crd-name>
```

## 11. 附录

### 11.1 常用命令速查

```bash
# Helm操作
helm list -A                          # 查看所有部署
helm status <release> -n <namespace>  # 查看部署状态
helm get values <release> -n <ns>     # 获取配置值
helm upgrade --reuse-values           # 保持现有配置升级
helm rollback <release> <revision>    # 回滚版本

# Kubernetes操作
kubectl get all -n aiops              # 查看所有资源
kubectl describe pod <pod-name>       # 查看Pod详情
kubectl logs -f <pod-name>            # 实时查看日志
kubectl exec -it <pod-name> -- /bin/sh # 进入Pod
```

### 11.2 端口映射表

| 服务 | 内部端口 | 外部端口 | 协议 | 说明 |
|------|----------|----------|------|------|
| API Gateway | 8080 | 80/443 | HTTP/HTTPS | 主要API入口 |
| Grafana | 3000 | 3000 | HTTP | 监控仪表板 |
| Kibana | 5601 | 5601 | HTTP | 日志分析界面 |
| Prometheus | 9090 | 9090 | HTTP | 指标收集 |
| AlertManager | 9093 | 9093 | HTTP | 告警管理 |
| Elasticsearch | 9200 | 9200 | HTTP | 搜索引擎 |
| Redis | 6379 | 6379 | TCP | 缓存服务 |
| PostgreSQL | 5432 | 5432 | TCP | 数据库 |

### 11.3 资源需求参考

| 组件 | CPU请求 | 内存请求 | 存储需求 | 副本数 |
|------|---------|----------|----------|--------|
| API Gateway | 500m | 1Gi | - | 2 |
| AI Engine | 1000m | 2Gi | - | 2 |
| Self Healing | 200m | 512Mi | - | 1 |
| Prometheus | 1000m | 8Gi | 100Gi | 1 |
| Grafana | 100m | 128Mi | 10Gi | 1 |
| Elasticsearch | 1000m | 2Gi | 200Gi | 3 |
| Kibana | 500m | 1Gi | - | 1 |
| Redis | 100m | 256Mi | 20Gi | 1 |
| PostgreSQL | 250m | 256Mi | 50Gi | 1 |

---

**注意**: 本手册基于AIOps平台v1.0.0版本编写，具体配置可能因版本而异。建议在生产环境部署前进行充分测试。