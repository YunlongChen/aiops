# AIOps平台 Kubernetes用户手册

## 1. 概述

本手册提供AIOps平台在Kubernetes环境中的完整部署和运维指南，涵盖集群准备、应用部署、监控运维、故障处理等全生命周期管理。

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes集群                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Master    │  │   Master    │  │   Master    │        │
│  │   Node 1    │  │   Node 2    │  │   Node 3    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Worker    │  │   Worker    │  │   Worker    │        │
│  │   Node 1    │  │   Node 2    │  │   Node N    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

- **控制平面**: API Server, etcd, Controller Manager, Scheduler
- **工作节点**: kubelet, kube-proxy, Container Runtime
- **网络**: CNI插件 (Calico/Flannel/Weave)
- **存储**: CSI驱动 (Ceph/NFS/云存储)
- **监控**: Prometheus + Grafana
- **日志**: ELK Stack

## 2. 集群环境准备

### 2.1 硬件要求

#### 最小配置
- **Master节点**: 2核4GB内存，50GB存储
- **Worker节点**: 4核8GB内存，100GB存储
- **网络**: 1Gbps带宽

#### 生产环境推荐
- **Master节点**: 4核8GB内存，200GB SSD
- **Worker节点**: 8核16GB内存，500GB SSD
- **网络**: 10Gbps带宽

### 2.2 操作系统准备

```bash
# Ubuntu/Debian系统准备
#!/bin/bash
# 系统更新
sudo apt update && sudo apt upgrade -y

# 安装必要软件包
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 禁用swap
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# 配置内核模块
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
overlay
EOF

sudo modprobe br_netfilter
sudo modprobe overlay

# 配置内核参数
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
```

```powershell
# Windows节点准备 (如果使用Windows节点)
# 启用容器功能
Enable-WindowsOptionalFeature -Online -FeatureName containers -All
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All

# 重启系统
Restart-Computer
```

### 2.3 容器运行时安装

#### Docker安装
```bash
#!/bin/bash
# 添加Docker官方GPG密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓库
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# 配置Docker daemon
sudo mkdir -p /etc/docker
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "registry-mirrors": ["https://your-mirror.com"]
}
EOF

# 启动Docker服务
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

#### containerd安装
```bash
#!/bin/bash
# 安装containerd
sudo apt install -y containerd.io

# 生成默认配置
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml

# 配置systemd cgroup驱动
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml

# 重启containerd
sudo systemctl restart containerd
sudo systemctl enable containerd
```

## 3. Kubernetes集群部署

### 3.1 kubeadm安装

```bash
#!/bin/bash
# 添加Kubernetes仓库
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/kubernetes-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

# 安装kubeadm, kubelet, kubectl
sudo apt update
sudo apt install -y kubelet=1.28.0-00 kubeadm=1.28.0-00 kubectl=1.28.0-00
sudo apt-mark hold kubelet kubeadm kubectl

# 启用kubelet
sudo systemctl enable kubelet
```

### 3.2 初始化Master节点

```bash
#!/bin/bash
# 创建集群配置文件
cat <<EOF > kubeadm-config.yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "192.168.1.100"  # Master节点IP
  bindPort: 6443
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: ClusterConfiguration
kubernetesVersion: "v1.28.0"
controlPlaneEndpoint: "k8s-api.local:6443"  # 负载均衡器地址
networking:
  serviceSubnet: "10.96.0.0/12"
  podSubnet: "10.244.0.0/16"
  dnsDomain: "cluster.local"
etcd:
  local:
    dataDir: "/var/lib/etcd"
apiServer:
  certSANs:
  - "k8s-api.local"
  - "192.168.1.100"
  - "192.168.1.101"
  - "192.168.1.102"
---
apiVersion: kubeadm.k8s.io/v1beta3
kind: KubeletConfiguration
cgroupDriver: systemd
EOF

# 初始化集群
sudo kubeadm init --config=kubeadm-config.yaml --upload-certs

# 配置kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

### 3.3 安装网络插件

#### Calico网络插件
```bash
#!/bin/bash
# 下载Calico配置
curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/tigera-operator.yaml -O
curl https://raw.githubusercontent.com/projectcalico/calico/v3.26.0/manifests/custom-resources.yaml -O

# 修改Pod CIDR
sed -i 's|cidr: 192.168.0.0/16|cidr: 10.244.0.0/16|' custom-resources.yaml

# 安装Calico
kubectl create -f tigera-operator.yaml
kubectl create -f custom-resources.yaml

# 验证安装
kubectl get pods -n calico-system
```

#### Flannel网络插件
```bash
#!/bin/bash
# 安装Flannel
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml

# 验证安装
kubectl get pods -n kube-flannel
```

### 3.4 添加Worker节点

```bash
#!/bin/bash
# 在Master节点获取join命令
kubeadm token create --print-join-command

# 在Worker节点执行join命令
sudo kubeadm join k8s-api.local:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash>

# 在Master节点验证节点加入
kubectl get nodes
```

### 3.5 高可用Master节点

```bash
#!/bin/bash
# 在其他Master节点执行
sudo kubeadm join k8s-api.local:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash> \
    --control-plane --certificate-key <cert-key>

# 配置kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## 4. 存储配置

### 4.1 本地存储配置

```yaml
# local-storage-class.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-storage
provisioner: kubernetes.io/no-provisioner
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: local-pv-1
spec:
  capacity:
    storage: 100Gi
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Delete
  storageClassName: local-storage
  local:
    path: /mnt/disks/vol1
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - worker-node-1
```

### 4.2 NFS存储配置

```bash
#!/bin/bash
# 安装NFS客户端
sudo apt install -y nfs-common

# 安装NFS CSI驱动
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/deploy/example/nfs-provisioner/nfs-server.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/deploy/example/storageclass-nfs.yaml
```

```yaml
# nfs-storage-class.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
provisioner: nfs.csi.k8s.io
parameters:
  server: "192.168.1.200"  # NFS服务器地址
  share: "/nfs/k8s"        # NFS共享路径
reclaimPolicy: Delete
volumeBindingMode: Immediate
mountOptions:
  - nfsvers=4.1
  - proto=tcp
  - hard
  - intr
```

### 4.3 Ceph存储配置

```bash
#!/bin/bash
# 安装Rook Ceph Operator
kubectl create -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/crds.yaml
kubectl create -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/common.yaml
kubectl create -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/operator.yaml

# 等待Operator启动
kubectl -n rook-ceph get pod

# 创建Ceph集群
kubectl create -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/cluster.yaml

# 创建存储类
kubectl create -f https://raw.githubusercontent.com/rook/rook/master/deploy/examples/csi/rbd/storageclass.yaml
```

## 5. AIOps平台部署

### 5.1 命名空间准备

```yaml
# aiops-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: aiops
  labels:
    name: aiops
    monitoring: enabled
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: aiops-quota
  namespace: aiops
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    persistentvolumeclaims: "20"
    services: "10"
    secrets: "20"
    configmaps: "20"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: aiops-limits
  namespace: aiops
spec:
  limits:
  - default:
      cpu: "1"
      memory: "2Gi"
    defaultRequest:
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

### 5.2 使用Helm部署

```bash
#!/bin/bash
# 创建命名空间和资源配额
kubectl apply -f aiops-namespace.yaml

# 部署AIOps平台
helm install aiops ./helm/ \
  --namespace aiops \
  --values values-production.yaml \
  --wait --timeout=30m

# 验证部署
kubectl get all -n aiops
```

### 5.3 使用Kustomize部署

```yaml
# kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: aiops

resources:
- namespace.yaml
- configmap.yaml
- secret.yaml
- deployment.yaml
- service.yaml
- ingress.yaml
- pvc.yaml

images:
- name: aiops/api-gateway
  newTag: v1.0.0
- name: aiops/ai-engine
  newTag: v1.0.0

replicas:
- name: aiops-api-gateway
  count: 3
- name: aiops-ai-engine
  count: 2

patchesStrategicMerge:
- production-patch.yaml
```

```bash
#!/bin/bash
# 使用Kustomize部署
kubectl apply -k ./k8s/overlays/production/

# 验证部署
kubectl get all -n aiops
```

## 6. 监控和日志

### 6.1 Prometheus监控部署

```bash
#!/bin/bash
# 添加Prometheus Helm仓库
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 创建监控命名空间
kubectl create namespace monitoring

# 部署Prometheus Stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi \
  --set grafana.adminPassword=admin123 \
  --wait
```

### 6.2 自定义监控规则

```yaml
# aiops-monitoring-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: aiops-rules
  namespace: monitoring
  labels:
    prometheus: kube-prometheus
    role: alert-rules
spec:
  groups:
  - name: aiops.rules
    rules:
    - alert: AIOpsAPIGatewayDown
      expr: up{job="aiops-api-gateway"} == 0
      for: 1m
      labels:
        severity: critical
        service: aiops
      annotations:
        summary: "AIOps API Gateway is down"
        description: "AIOps API Gateway has been down for more than 1 minute."
    
    - alert: AIOpsHighMemoryUsage
      expr: |
        (
          container_memory_working_set_bytes{namespace="aiops", container!=""}
          /
          container_spec_memory_limit_bytes{namespace="aiops", container!=""}
        ) > 0.9
      for: 5m
      labels:
        severity: warning
        service: aiops
      annotations:
        summary: "High memory usage in AIOps namespace"
        description: "Container {{ $labels.container }} in pod {{ $labels.pod }} is using more than 90% of its memory limit."
    
    - alert: AIOpsHighCPUUsage
      expr: |
        (
          rate(container_cpu_usage_seconds_total{namespace="aiops", container!=""}[5m])
          /
          container_spec_cpu_quota{namespace="aiops", container!=""} * 100000
        ) > 0.8
      for: 5m
      labels:
        severity: warning
        service: aiops
      annotations:
        summary: "High CPU usage in AIOps namespace"
        description: "Container {{ $labels.container }} in pod {{ $labels.pod }} is using more than 80% of its CPU limit."
```

### 6.3 ELK日志系统部署

```bash
#!/bin/bash
# 添加Elastic Helm仓库
helm repo add elastic https://helm.elastic.co
helm repo update

# 创建日志命名空间
kubectl create namespace logging

# 部署Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --set replicas=3 \
  --set minimumMasterNodes=2 \
  --set volumeClaimTemplate.resources.requests.storage=100Gi \
  --wait

# 部署Kibana
helm install kibana elastic/kibana \
  --namespace logging \
  --set service.type=LoadBalancer \
  --wait

# 部署Filebeat
helm install filebeat elastic/filebeat \
  --namespace logging \
  --wait
```

### 6.4 Fluentd日志收集

```yaml
# fluentd-daemonset.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
  namespace: logging
spec:
  selector:
    matchLabels:
      name: fluentd
  template:
    metadata:
      labels:
        name: fluentd
    spec:
      serviceAccountName: fluentd
      tolerations:
      - key: node-role.kubernetes.io/master
        effect: NoSchedule
      containers:
      - name: fluentd
        image: fluent/fluentd-kubernetes-daemonset:v1-debian-elasticsearch
        env:
        - name: FLUENT_ELASTICSEARCH_HOST
          value: "elasticsearch.logging.svc.cluster.local"
        - name: FLUENT_ELASTICSEARCH_PORT
          value: "9200"
        - name: FLUENT_ELASTICSEARCH_SCHEME
          value: "http"
        resources:
          limits:
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 200Mi
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
```

## 7. 网络和安全

### 7.1 Ingress控制器部署

```bash
#!/bin/bash
# 部署NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# 等待部署完成
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 7.2 SSL/TLS证书管理

```bash
#!/bin/bash
# 安装cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# 等待cert-manager启动
kubectl wait --for=condition=Available --timeout=300s deployment/cert-manager -n cert-manager
```

```yaml
# letsencrypt-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@your-domain.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

### 7.3 网络策略配置

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
          name: monitoring
    - namespaceSelector:
        matchLabels:
          name: logging
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  - from:
    - podSelector: {}
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 443
```

### 7.4 Pod安全策略

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: aiops-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## 8. 备份和恢复

### 8.1 etcd备份

```bash
#!/bin/bash
# etcd备份脚本
ETCD_BACKUP_DIR="/backup/etcd"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $ETCD_BACKUP_DIR

# 执行etcd备份
ETCDCTL_API=3 etcdctl snapshot save $ETCD_BACKUP_DIR/etcd-snapshot-$BACKUP_DATE.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 验证备份
ETCDCTL_API=3 etcdctl snapshot status $ETCD_BACKUP_DIR/etcd-snapshot-$BACKUP_DATE.db

# 清理旧备份（保留7天）
find $ETCD_BACKUP_DIR -name "etcd-snapshot-*.db" -mtime +7 -delete

echo "etcd backup completed: $ETCD_BACKUP_DIR/etcd-snapshot-$BACKUP_DATE.db"
```

### 8.2 应用数据备份

```bash
#!/bin/bash
# 应用数据备份脚本
NAMESPACE="aiops"
BACKUP_DIR="/backup/aiops"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR/$BACKUP_DATE

# 备份配置和密钥
kubectl get configmaps -n $NAMESPACE -o yaml > $BACKUP_DIR/$BACKUP_DATE/configmaps.yaml
kubectl get secrets -n $NAMESPACE -o yaml > $BACKUP_DIR/$BACKUP_DATE/secrets.yaml

# 备份PVC数据
for pvc in $(kubectl get pvc -n $NAMESPACE -o jsonpath='{.items[*].metadata.name}'); do
  echo "Backing up PVC: $pvc"
  kubectl exec -n $NAMESPACE deployment/backup-pod -- \
    tar czf /backup/$pvc-$BACKUP_DATE.tar.gz -C /data/$pvc .
done

# 压缩备份
tar czf $BACKUP_DIR/aiops-backup-$BACKUP_DATE.tar.gz -C $BACKUP_DIR $BACKUP_DATE
rm -rf $BACKUP_DIR/$BACKUP_DATE

echo "Application backup completed: $BACKUP_DIR/aiops-backup-$BACKUP_DATE.tar.gz"
```

### 8.3 Velero备份解决方案

```bash
#!/bin/bash
# 安装Velero
wget https://github.com/vmware-tanzu/velero/releases/download/v1.11.0/velero-v1.11.0-linux-amd64.tar.gz
tar -xzf velero-v1.11.0-linux-amd64.tar.gz
sudo mv velero-v1.11.0-linux-amd64/velero /usr/local/bin/

# 配置AWS S3存储
cat <<EOF > credentials-velero
[default]
aws_access_key_id = your-access-key
aws_secret_access_key = your-secret-key
EOF

# 安装Velero到集群
velero install \
    --provider aws \
    --plugins velero/velero-plugin-for-aws:v1.7.0 \
    --bucket velero-backups \
    --backup-location-config region=us-west-2 \
    --snapshot-location-config region=us-west-2 \
    --secret-file ./credentials-velero
```

```yaml
# velero-backup-schedule.yaml
apiVersion: velero.io/v1
kind: Schedule
metadata:
  name: aiops-daily-backup
  namespace: velero
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  template:
    includedNamespaces:
    - aiops
    - monitoring
    - logging
    storageLocation: default
    ttl: 720h0m0s  # 保留30天
```

## 9. 故障排除

### 9.1 集群诊断脚本

```bash
#!/bin/bash
# Kubernetes集群诊断脚本

echo "=== Kubernetes集群诊断报告 ==="
echo "生成时间: $(date)"
echo

# 集群基本信息
echo "=== 集群信息 ==="
kubectl cluster-info
echo

# 节点状态
echo "=== 节点状态 ==="
kubectl get nodes -o wide
echo

# 系统Pod状态
echo "=== 系统Pod状态 ==="
kubectl get pods -n kube-system
echo

# 资源使用情况
echo "=== 资源使用情况 ==="
kubectl top nodes
echo

# 存储状态
echo "=== 存储状态 ==="
kubectl get pv,pvc --all-namespaces
echo

# 网络状态
echo "=== 网络状态 ==="
kubectl get svc,endpoints --all-namespaces
echo

# 事件信息
echo "=== 最近事件 ==="
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -20
echo

# AIOps应用状态
echo "=== AIOps应用状态 ==="
kubectl get all -n aiops
echo

# 检查证书过期
echo "=== 证书状态 ==="
kubeadm certs check-expiration
echo

echo "=== 诊断完成 ==="
```

### 9.2 常见问题解决

#### Pod启动失败
```bash
# 查看Pod详细信息
kubectl describe pod <pod-name> -n <namespace>

# 查看Pod日志
kubectl logs <pod-name> -n <namespace> --previous

# 检查资源限制
kubectl get limitrange -n <namespace>
kubectl get resourcequota -n <namespace>

# 检查节点资源
kubectl describe node <node-name>
```

#### 网络连接问题
```bash
# 测试DNS解析
kubectl run test-dns --image=busybox -it --rm -- nslookup kubernetes.default

# 测试服务连通性
kubectl run test-connectivity --image=busybox -it --rm -- wget -qO- http://service-name.namespace.svc.cluster.local

# 检查网络策略
kubectl get networkpolicy --all-namespaces

# 检查CNI插件状态
kubectl get pods -n kube-system | grep -E '(calico|flannel|weave)'
```

#### 存储问题
```bash
# 检查存储类
kubectl get storageclass

# 检查PV状态
kubectl get pv

# 检查PVC绑定
kubectl get pvc -n <namespace>

# 查看存储事件
kubectl get events --field-selector involvedObject.kind=PersistentVolumeClaim
```

### 9.3 性能调优

#### 节点性能优化
```bash
#!/bin/bash
# 节点性能优化脚本

# 调整内核参数
cat <<EOF >> /etc/sysctl.conf
# 网络优化
net.core.somaxconn = 32768
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_syncookies = 1

# 内存优化
vm.swappiness = 1
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# 文件系统优化
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
EOF

sysctl -p

# 调整系统限制
cat <<EOF >> /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF

# 优化Docker配置
cat <<EOF > /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5
}
EOF

systemctl restart docker
```

#### 应用性能优化
```yaml
# 高性能配置示例
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aiops-api-gateway
  namespace: aiops
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - aiops-api-gateway
              topologyKey: kubernetes.io/hostname
      containers:
      - name: api-gateway
        image: aiops/api-gateway:v1.0.0
        resources:
          requests:
            cpu: "1000m"
            memory: "2Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: GOMAXPROCS
          valueFrom:
            resourceFieldRef:
              resource: limits.cpu
```

## 10. 升级和维护

### 10.1 Kubernetes集群升级

```bash
#!/bin/bash
# Kubernetes集群升级脚本

# 检查当前版本
kubectl version --short
kubeadm version

# 升级kubeadm
apt update
apt-cache madison kubeadm
apt-mark unhold kubeadm
apt install -y kubeadm=1.28.1-00
apt-mark hold kubeadm

# 验证升级计划
kubeadm upgrade plan

# 升级控制平面
kubeadm upgrade apply v1.28.1

# 升级kubelet和kubectl
apt-mark unhold kubelet kubectl
apt install -y kubelet=1.28.1-00 kubectl=1.28.1-00
apt-mark hold kubelet kubectl

# 重启kubelet
systemctl daemon-reload
systemctl restart kubelet

# 验证升级
kubectl get nodes
```

### 10.2 应用滚动升级

```bash
#!/bin/bash
# 应用滚动升级脚本

NAMESPACE="aiops"
APP_NAME="aiops-api-gateway"
NEW_IMAGE="aiops/api-gateway:v1.1.0"

# 更新镜像
kubectl set image deployment/$APP_NAME -n $NAMESPACE api-gateway=$NEW_IMAGE

# 监控升级进度
kubectl rollout status deployment/$APP_NAME -n $NAMESPACE --timeout=600s

# 验证升级结果
if kubectl rollout status deployment/$APP_NAME -n $NAMESPACE | grep -q "successfully rolled out"; then
    echo "升级成功"
    kubectl get pods -n $NAMESPACE -l app=$APP_NAME
else
    echo "升级失败，执行回滚"
    kubectl rollout undo deployment/$APP_NAME -n $NAMESPACE
fi
```

### 10.3 定期维护任务

```bash
#!/bin/bash
# 定期维护脚本

echo "开始执行Kubernetes集群维护任务..."

# 清理未使用的镜像
echo "清理Docker镜像..."
docker system prune -af --volumes

# 清理已完成的Pod
echo "清理已完成的Pod..."
kubectl delete pods --field-selector=status.phase=Succeeded --all-namespaces
kubectl delete pods --field-selector=status.phase=Failed --all-namespaces

# 清理未绑定的PV
echo "清理未绑定的PV..."
kubectl get pv | grep Available | awk '{print $1}' | xargs -r kubectl delete pv

# 检查证书过期时间
echo "检查证书过期时间..."
kubeadm certs check-expiration

# 备份etcd
echo "备份etcd..."
./backup-etcd.sh

# 生成集群健康报告
echo "生成集群健康报告..."
./cluster-health-check.sh > /var/log/k8s-health-$(date +%Y%m%d).log

echo "维护任务完成"
```

## 11. 附录

### 11.1 常用命令速查

```bash
# 集群管理
kubectl cluster-info                    # 集群信息
kubectl get nodes                       # 节点列表
kubectl describe node <node-name>       # 节点详情
kubectl top nodes                       # 节点资源使用

# Pod管理
kubectl get pods -A                     # 所有Pod
kubectl describe pod <pod-name>         # Pod详情
kubectl logs <pod-name> -f              # 查看日志
kubectl exec -it <pod-name> -- /bin/sh  # 进入Pod

# 服务管理
kubectl get svc -A                      # 所有服务
kubectl port-forward svc/<svc-name> 8080:80  # 端口转发

# 配置管理
kubectl get configmap -A                # 配置映射
kubectl get secret -A                   # 密钥

# 存储管理
kubectl get pv,pvc -A                   # 存储卷
kubectl get storageclass                # 存储类

# 网络管理
kubectl get ingress -A                  # Ingress
kubectl get networkpolicy -A            # 网络策略

# 事件和调试
kubectl get events --sort-by='.lastTimestamp'  # 事件
kubectl describe <resource> <name>      # 资源详情
```

### 11.2 故障排除检查清单

- [ ] 检查节点状态和资源使用
- [ ] 检查Pod状态和日志
- [ ] 检查服务端点和网络连通性
- [ ] 检查存储卷挂载状态
- [ ] 检查配置和密钥
- [ ] 检查RBAC权限
- [ ] 检查网络策略
- [ ] 检查资源配额和限制
- [ ] 检查镜像拉取状态
- [ ] 检查DNS解析

### 11.3 性能调优参数

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| --max-pods | 110 | 每个节点最大Pod数 |
| --kube-api-qps | 50 | API请求QPS |
| --kube-api-burst | 100 | API请求突发数 |
| --image-pull-progress-deadline | 5m | 镜像拉取超时 |
| --runtime-request-timeout | 15m | 运行时请求超时 |
| --node-status-update-frequency | 10s | 节点状态更新频率 |
| --sync-frequency | 30s | 同步频率 |

---

**注意**: 本手册基于Kubernetes v1.28版本编写，不同版本可能存在差异。建议在生产环境部署前进行充分测试。