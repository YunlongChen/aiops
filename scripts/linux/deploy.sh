#!/bin/bash

# AIOps智能运维平台自动化部署脚本 (Bash)
# 文件: deploy.sh
# 描述: 用于在Linux/macOS环境下自动化部署AIOps平台
# 版本: 1.0.0
# 作者: AIOps Team
# 创建日期: 2024-01-01

set -euo pipefail

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/deployment-$(date +%Y%m%d-%H%M%S).log"
REQUIRED_PORTS=(80 443 3000 5601 9090 9200 6379 5432)
MIN_DOCKER_VERSION="20.10.0"
MIN_KUBERNETES_VERSION="1.19.0"
MIN_HELM_VERSION="3.2.0"

# 默认参数
DEPLOYMENT_TYPE=""
ENVIRONMENT="development"
CONFIG_FILE=""
SKIP_CHECKS=false
VERBOSE=false

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 显示帮助信息
show_help() {
    cat << EOF
AIOps智能运维平台自动化部署脚本

用法: $0 [选项]

选项:
    -t, --type TYPE         部署类型 (docker|kubernetes)
    -e, --env ENV          部署环境 (development|staging|production)
    -c, --config FILE      自定义配置文件路径
    -s, --skip-checks      跳过环境检查
    -v, --verbose          详细输出
    -h, --help             显示此帮助信息

示例:
    $0 --type docker --env development
    $0 --type kubernetes --env production --config ./prod-config.yaml
    $0 -t docker -e staging -v

EOF
}

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_message="[$timestamp] [$level] $message"
    
    # 写入日志文件
    echo "$log_message" >> "$LOG_FILE"
    
    # 控制台输出
    case "$level" in
        "INFO")
            echo -e "${BLUE}$log_message${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}$log_message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}$log_message${NC}" >&2
            ;;
        "SUCCESS")
            echo -e "${GREEN}$log_message${NC}"
            ;;
        *)
            echo "$log_message"
            ;;
    esac
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 版本比较函数
version_compare() {
    local version1="$1"
    local version2="$2"
    
    if [[ "$version1" == "$version2" ]]; then
        return 0
    fi
    
    local IFS=.
    local i ver1=($version1) ver2=($version2)
    
    # 填充缺失的版本号部分
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    
    return 0
}

# 检查root权限
check_root_privileges() {
    if [[ $EUID -eq 0 ]]; then
        log "WARN" "正在以root用户运行，请确保这是必要的"
    fi
}

# 检查端口占用
check_port_availability() {
    local unavailable_ports=()
    
    for port in "${REQUIRED_PORTS[@]}"; do
        if command_exists netstat; then
            if netstat -tuln 2>/dev/null | grep -q ":$port "; then
                unavailable_ports+=("$port")
            fi
        elif command_exists ss; then
            if ss -tuln 2>/dev/null | grep -q ":$port "; then
                unavailable_ports+=("$port")
            fi
        elif command_exists lsof; then
            if lsof -i ":$port" >/dev/null 2>&1; then
                unavailable_ports+=("$port")
            fi
        fi
    done
    
    if [[ ${#unavailable_ports[@]} -gt 0 ]]; then
        log "WARN" "以下端口被占用: ${unavailable_ports[*]}"
        log "WARN" "请确保这些端口可用或修改配置文件中的端口设置"
    fi
}

# 检查系统资源
check_system_resources() {
    local cpu_cores
    local total_memory_gb
    local available_disk_gb
    local warnings=()
    
    # 检查CPU核心数
    if command_exists nproc; then
        cpu_cores=$(nproc)
    elif [[ -f /proc/cpuinfo ]]; then
        cpu_cores=$(grep -c ^processor /proc/cpuinfo)
    else
        cpu_cores="未知"
    fi
    
    # 检查内存
    if [[ -f /proc/meminfo ]]; then
        local total_memory_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        total_memory_gb=$((total_memory_kb / 1024 / 1024))
    else
        total_memory_gb="未知"
    fi
    
    # 检查磁盘空间
    if command_exists df; then
        available_disk_gb=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    else
        available_disk_gb="未知"
    fi
    
    log "INFO" "系统资源检查:"
    log "INFO" "  CPU核心数: $cpu_cores"
    log "INFO" "  总内存: ${total_memory_gb}GB"
    log "INFO" "  可用磁盘空间: ${available_disk_gb}GB"
    
    # 资源警告
    if [[ "$cpu_cores" != "未知" && $cpu_cores -lt 4 ]]; then
        warnings+=("CPU核心数不足，推荐至少4核")
    fi
    
    if [[ "$total_memory_gb" != "未知" && $total_memory_gb -lt 8 ]]; then
        warnings+=("内存不足，推荐至少8GB")
    fi
    
    if [[ "$available_disk_gb" != "未知" && $available_disk_gb -lt 50 ]]; then
        warnings+=("磁盘空间不足，推荐至少50GB可用空间")
    fi
    
    for warning in "${warnings[@]}"; do
        log "WARN" "$warning"
    done
}

# 检查Docker环境
check_docker_environment() {
    if ! command_exists docker; then
        log "ERROR" "Docker未安装或不在PATH中"
        return 1
    fi
    
    # 检查Docker版本
    local docker_version
    docker_version=$(docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    
    if ! version_compare "$docker_version" "$MIN_DOCKER_VERSION"; then
        if [[ $? -eq 2 ]]; then
            log "ERROR" "Docker版本过低，当前版本: $docker_version，最低要求: $MIN_DOCKER_VERSION"
            return 1
        fi
    fi
    
    # 检查Docker Compose
    if ! command_exists docker-compose; then
        log "ERROR" "Docker Compose未安装或不在PATH中"
        return 1
    fi
    
    # 检查Docker服务状态
    if ! docker info >/dev/null 2>&1; then
        log "ERROR" "Docker服务未运行或无权限访问"
        log "INFO" "请尝试: sudo systemctl start docker"
        return 1
    fi
    
    local compose_version
    compose_version=$(docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    
    log "SUCCESS" "Docker环境检查通过"
    log "INFO" "  Docker版本: $docker_version"
    log "INFO" "  Docker Compose版本: $compose_version"
    
    return 0
}

# 检查Kubernetes环境
check_kubernetes_environment() {
    if ! command_exists kubectl; then
        log "ERROR" "kubectl未安装或不在PATH中"
        return 1
    fi
    
    # 检查集群连接
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log "ERROR" "无法连接到Kubernetes集群"
        log "INFO" "请检查kubeconfig配置"
        return 1
    fi
    
    # 检查Helm
    if ! command_exists helm; then
        log "ERROR" "Helm未安装或不在PATH中"
        return 1
    fi
    
    local helm_version
    helm_version=$(helm version --short | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | sed 's/v//')
    
    if ! version_compare "$helm_version" "$MIN_HELM_VERSION"; then
        if [[ $? -eq 2 ]]; then
            log "ERROR" "Helm版本过低，当前版本: $helm_version，最低要求: $MIN_HELM_VERSION"
            return 1
        fi
    fi
    
    local kubectl_version
    kubectl_version=$(kubectl version --client --short | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | sed 's/v//')
    
    log "SUCCESS" "Kubernetes环境检查通过"
    log "INFO" "  kubectl版本: $kubectl_version"
    log "INFO" "  Helm版本: $helm_version"
    
    return 0
}

# 环境检查主函数
perform_environment_check() {
    log "INFO" "开始环境检查..."
    
    # 检查root权限
    check_root_privileges
    
    # 检查系统资源
    check_system_resources
    
    # 检查端口占用
    check_port_availability
    
    # 根据部署类型检查环境
    case "$DEPLOYMENT_TYPE" in
        "docker")
            if ! check_docker_environment; then
                log "ERROR" "Docker环境检查失败"
                return 1
            fi
            ;;
        "kubernetes")
            if ! check_kubernetes_environment; then
                log "ERROR" "Kubernetes环境检查失败"
                return 1
            fi
            ;;
    esac
    
    log "SUCCESS" "环境检查完成"
    return 0
}

# 生成Docker Compose配置
generate_docker_compose_config() {
    local config_path="$PROJECT_ROOT/docker-compose.override.yml"
    
    local log_level="INFO"
    local dashboard="false"
    local retention="30d"
    local admin_password="admin"
    local allow_signup="false"
    local discovery_type="single-node"
    local java_opts="-Xms1g -Xmx1g"
    
    case "$ENVIRONMENT" in
        "development")
            log_level="DEBUG"
            dashboard="true"
            admin_password="admin"
            allow_signup="true"
            ;;
        "production")
            retention="90d"
            admin_password="aiops-admin-2024"
            discovery_type="zen"
            java_opts="-Xms2g -Xmx2g"
            ;;
    esac
    
    cat > "$config_path" << EOF
# AIOps平台 - $ENVIRONMENT 环境配置
# 自动生成于: $(date '+%Y-%m-%d %H:%M:%S')

version: '3.8'

services:
  # 环境特定配置
  traefik:
    environment:
      - TRAEFIK_LOG_LEVEL=$log_level
      - TRAEFIK_API_DASHBOARD=$dashboard
  
  prometheus:
    environment:
      - PROMETHEUS_RETENTION=$retention
  
  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=$admin_password
      - GF_USERS_ALLOW_SIGN_UP=$allow_signup
  
  elasticsearch:
    environment:
      - discovery.type=$discovery_type
      - "ES_JAVA_OPTS=$java_opts"
EOF
    
    log "SUCCESS" "Docker Compose配置已生成: $config_path"
}

# 生成Kubernetes配置
generate_kubernetes_config() {
    local config_path="$PROJECT_ROOT/k8s-values-$ENVIRONMENT.yaml"
    
    local development="false"
    local storage_class="standard"
    local host="aiops.example.com"
    local tls="false"
    local retention="30d"
    local prometheus_storage="20Gi"
    local prometheus_memory="2Gi"
    local prometheus_cpu="1000m"
    local admin_password="aiops-admin-2024"
    local persistence="false"
    local grafana_storage="5Gi"
    local es_replicas="1"
    local es_storage="50Gi"
    local es_memory="2Gi"
    local es_cpu="500m"
    local ai_replicas="1"
    local ai_memory="2Gi"
    local ai_cpu="1000m"
    
    case "$ENVIRONMENT" in
        "development")
            development="true"
            host="aiops.local"
            admin_password="admin"
            ;;
        "production")
            storage_class="fast-ssd"
            tls="true"
            retention="90d"
            prometheus_storage="100Gi"
            prometheus_memory="4Gi"
            prometheus_cpu="2000m"
            persistence="true"
            grafana_storage="10Gi"
            es_replicas="3"
            es_storage="200Gi"
            es_memory="4Gi"
            es_cpu="1000m"
            ai_replicas="3"
            ai_memory="4Gi"
            ai_cpu="2000m"
            ;;
    esac
    
    cat > "$config_path" << EOF
# AIOps平台 - $ENVIRONMENT 环境配置
# 自动生成于: $(date '+%Y-%m-%d %H:%M:%S')

global:
  environment: $ENVIRONMENT
  development: $development
  storageClass: "$storage_class"

ingress:
  enabled: true
  className: "traefik"
  hosts:
    - host: $host
      paths:
        - path: /
          pathType: Prefix
  tls: $tls

prometheus:
  enabled: true
  retention: "$retention"
  storage:
    size: "$prometheus_storage"
  resources:
    requests:
      memory: "$prometheus_memory"
      cpu: "$prometheus_cpu"

grafana:
  enabled: true
  adminPassword: "$admin_password"
  persistence:
    enabled: $persistence
    size: "$grafana_storage"

elasticsearch:
  enabled: true
  replicas: $es_replicas
  storage:
    size: "$es_storage"
  resources:
    requests:
      memory: "$es_memory"
      cpu: "$es_cpu"

aiEngine:
  enabled: true
  replicas: $ai_replicas
  resources:
    requests:
      memory: "$ai_memory"
      cpu: "$ai_cpu"
EOF
    
    log "SUCCESS" "Kubernetes配置已生成: $config_path"
    echo "$config_path"
}

# Docker部署
deploy_docker() {
    log "INFO" "开始Docker部署..."
    
    # 生成配置
    generate_docker_compose_config
    
    # 切换到项目根目录
    cd "$PROJECT_ROOT"
    
    # 拉取镜像
    log "INFO" "拉取Docker镜像..."
    if ! docker-compose pull; then
        log "ERROR" "镜像拉取失败"
        return 1
    fi
    
    # 启动服务
    log "INFO" "启动服务..."
    if ! docker-compose up -d; then
        log "ERROR" "服务启动失败"
        return 1
    fi
    
    # 等待服务就绪
    log "INFO" "等待服务启动完成..."
    sleep 30
    
    # 检查服务状态
    local services
    services=$(docker-compose ps --services)
    local healthy_services=0
    local total_services=0
    
    while IFS= read -r service; do
        ((total_services++))
        local status
        status=$(docker-compose ps "$service" | tail -n +3 | awk '{print $4}')
        
        if [[ "$status" == "Up" ]]; then
            ((healthy_services++))
            log "SUCCESS" "服务 $service 运行正常"
        else
            log "WARN" "服务 $service 状态异常: $status"
        fi
    done <<< "$services"
    
    log "SUCCESS" "Docker部署完成: $healthy_services/$total_services 服务运行正常"
    
    # 显示访问信息
    log "INFO" "服务访问地址:"
    log "INFO" "  Grafana: http://localhost:3000 (admin/admin)"
    log "INFO" "  Prometheus: http://localhost:9090"
    log "INFO" "  Kibana: http://localhost:5601"
    log "INFO" "  Traefik Dashboard: http://localhost:8080"
    
    return 0
}

# Kubernetes部署
deploy_kubernetes() {
    log "INFO" "开始Kubernetes部署..."
    
    # 生成配置
    local values_file
    values_file=$(generate_kubernetes_config)
    
    # 如果指定了自定义配置文件，使用它
    if [[ -n "$CONFIG_FILE" && -f "$CONFIG_FILE" ]]; then
        values_file="$CONFIG_FILE"
        log "INFO" "使用自定义配置文件: $CONFIG_FILE"
    fi
    
    # 创建命名空间
    local namespace="aiops-platform"
    log "INFO" "创建命名空间: $namespace"
    kubectl create namespace "$namespace" --dry-run=client -o yaml | kubectl apply -f -
    
    # 添加Helm仓库
    log "INFO" "添加Helm仓库..."
    local helm_repos=(
        "prometheus-community https://prometheus-community.github.io/helm-charts"
        "grafana https://grafana.github.io/helm-charts"
        "elastic https://helm.elastic.co"
        "bitnami https://charts.bitnami.com/bitnami"
        "traefik https://helm.traefik.io/traefik"
    )
    
    for repo in "${helm_repos[@]}"; do
        local name url
        name=$(echo "$repo" | cut -d' ' -f1)
        url=$(echo "$repo" | cut -d' ' -f2)
        helm repo add "$name" "$url" 2>/dev/null || true
    done
    
    helm repo update
    
    # 部署Helm Chart
    local chart_path="$PROJECT_ROOT/helm"
    log "INFO" "部署Helm Chart..."
    
    if ! helm upgrade --install aiops-platform "$chart_path" \
        --namespace "$namespace" \
        --values "$values_file" \
        --timeout 10m \
        --wait; then
        log "ERROR" "Helm部署失败"
        return 1
    fi
    
    # 运行测试
    log "INFO" "运行部署测试..."
    helm test aiops-platform --namespace "$namespace" || true
    
    # 检查Pod状态
    log "INFO" "检查Pod状态..."
    local pods_json
    pods_json=$(kubectl get pods -n "$namespace" -o json)
    
    local running_pods=0
    local total_pods
    total_pods=$(echo "$pods_json" | jq '.items | length')
    
    for ((i=0; i<total_pods; i++)); do
        local pod_name pod_status
        pod_name=$(echo "$pods_json" | jq -r ".items[$i].metadata.name")
        pod_status=$(echo "$pods_json" | jq -r ".items[$i].status.phase")
        
        if [[ "$pod_status" == "Running" ]]; then
            ((running_pods++))
            log "SUCCESS" "Pod $pod_name 运行正常"
        else
            log "WARN" "Pod $pod_name 状态: $pod_status"
        fi
    done
    
    log "SUCCESS" "Kubernetes部署完成: $running_pods/$total_pods Pod运行正常"
    
    # 显示访问信息
    log "INFO" "获取服务访问信息..."
    local services_json
    services_json=$(kubectl get svc -n "$namespace" -o json)
    
    local service_count
    service_count=$(echo "$services_json" | jq '.items | length')
    
    for ((i=0; i<service_count; i++)); do
        local service_name service_type
        service_name=$(echo "$services_json" | jq -r ".items[$i].metadata.name")
        service_type=$(echo "$services_json" | jq -r ".items[$i].spec.type")
        
        case "$service_type" in
            "LoadBalancer")
                local external_ip
                external_ip=$(echo "$services_json" | jq -r ".items[$i].status.loadBalancer.ingress[0].ip // empty")
                if [[ -n "$external_ip" ]]; then
                    log "INFO" "服务 $service_name: http://$external_ip"
                fi
                ;;
            "NodePort")
                local node_port
                node_port=$(echo "$services_json" | jq -r ".items[$i].spec.ports[0].nodePort // empty")
                if [[ -n "$node_port" ]]; then
                    log "INFO" "服务 $service_name: http://<node-ip>:$node_port"
                fi
                ;;
        esac
    done
    
    log "INFO" "使用 'kubectl port-forward' 进行本地访问"
    
    return 0
}

# 清理函数
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        log "ERROR" "部署过程中发生错误，退出码: $exit_code"
        log "INFO" "详细日志请查看: $LOG_FILE"
    fi
    exit $exit_code
}

# 主函数
main() {
    # 设置信号处理
    trap cleanup EXIT INT TERM
    
    log "INFO" "AIOps智能运维平台部署开始"
    log "INFO" "部署类型: $DEPLOYMENT_TYPE"
    log "INFO" "环境: $ENVIRONMENT"
    log "INFO" "日志文件: $LOG_FILE"
    
    # 环境检查
    if [[ "$SKIP_CHECKS" != "true" ]]; then
        if ! perform_environment_check; then
            log "ERROR" "环境检查失败，请解决上述问题后重试"
            return 1
        fi
    else
        log "WARN" "跳过环境检查"
    fi
    
    # 执行部署
    case "$DEPLOYMENT_TYPE" in
        "docker")
            if ! deploy_docker; then
                log "ERROR" "Docker部署失败"
                return 1
            fi
            ;;
        "kubernetes")
            if ! deploy_kubernetes; then
                log "ERROR" "Kubernetes部署失败"
                return 1
            fi
            ;;
    esac
    
    log "SUCCESS" "AIOps平台部署成功完成！"
    log "INFO" "详细日志请查看: $LOG_FILE"
    
    return 0
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -s|--skip-checks)
            SKIP_CHECKS=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            set -x
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log "ERROR" "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 验证必需参数
if [[ -z "$DEPLOYMENT_TYPE" ]]; then
    log "ERROR" "必须指定部署类型 (-t|--type)"
    show_help
    exit 1
fi

if [[ "$DEPLOYMENT_TYPE" != "docker" && "$DEPLOYMENT_TYPE" != "kubernetes" ]]; then
    log "ERROR" "无效的部署类型: $DEPLOYMENT_TYPE"
    show_help
    exit 1
fi

if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    log "ERROR" "无效的环境: $ENVIRONMENT"
    show_help
    exit 1
fi

# 执行主函数
main "$@"