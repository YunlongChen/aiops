# AIOps平台用户手册 - Linux版

## 文档信息
- **版本**: v3.0.0
- **适用系统**: Ubuntu 20.04+, CentOS 8+, RHEL 8+, Debian 11+
- **最后更新**: 2025-01-09
- **文档类型**: Linux专用部署指南

---

## 目录

1. [系统概述](#1-系统概述)
2. [Linux环境要求](#2-linux环境要求)
3. [快速开始](#3-快速开始)
4. [详细安装指南](#4-详细安装指南)
5. [Bash脚本工具](#5-bash脚本工具)
6. [Linux特定配置](#6-linux特定配置)
7. [服务管理](#7-服务管理)
8. [监控和告警](#8-监控和告警)
9. [故障排除](#9-故障排除)
10. [性能优化](#10-性能优化)
11. [安全配置](#11-安全配置)
12. [备份和恢复](#12-备份和恢复)

---

## 1. 系统概述

### 1.1 AIOps平台简介
AIOps（Artificial Intelligence for IT Operations）平台是一个基于人工智能的IT运维管理系统，专为Linux环境优化，提供企业级的智能监控、自动化运维和预测性维护功能。

### 1.2 核心功能
- **智能监控**: 实时监控Linux系统性能和应用状态
- **自动化运维**: 基于Bash/Python的自动化脚本执行
- **预测性维护**: AI驱动的故障预测和预防
- **可视化仪表板**: Grafana集成的Linux性能仪表板
- **告警管理**: 集成系统日志的智能告警
- **容器编排**: 基于Docker Compose的微服务架构

### 1.3 架构组件
```
┌─────────────────────────────────────────────────────────────┐
│                    AIOps平台架构 (Linux)                     │
├─────────────────────────────────────────────────────────────┤
│  前端层    │ Grafana仪表板 │ API网关 │ Traefik代理          │
├─────────────────────────────────────────────────────────────┤
│  应用层    │ AI引擎 │ 自愈系统 │ 告警管理 │ 任务调度        │
├─────────────────────────────────────────────────────────────┤
│  数据层    │ Prometheus │ PostgreSQL │ Redis │ ElasticSearch │
├─────────────────────────────────────────────────────────────┤
│  基础设施  │ Docker Engine │ Linux容器 │ systemd服务      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Linux环境要求

### 2.1 硬件要求
| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 4核心 | 8核心+ |
| 内存 | 8GB | 16GB+ |
| 存储 | 50GB可用空间 | 100GB+ SSD |
| 网络 | 100Mbps | 1Gbps |

### 2.2 操作系统支持
| 发行版 | 版本 | 状态 |
|--------|------|------|
| Ubuntu | 20.04 LTS, 22.04 LTS | ✅ 完全支持 |
| CentOS | 8.x, 9.x | ✅ 完全支持 |
| RHEL | 8.x, 9.x | ✅ 完全支持 |
| Debian | 11.x, 12.x | ✅ 完全支持 |
| Rocky Linux | 8.x, 9.x | ✅ 完全支持 |
| AlmaLinux | 8.x, 9.x | ✅ 完全支持 |

### 2.3 软件依赖
```bash
# 基础工具
sudo apt update && sudo apt install -y \
    curl wget git vim htop \
    ca-certificates gnupg lsb-release \
    apt-transport-https software-properties-common

# Docker Engine (Ubuntu/Debian)
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2.4 网络端口
| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| Traefik | 80, 443 | HTTP/HTTPS | 反向代理 |
| API网关 | 8080 | HTTP | API服务 |
| Grafana | 3000 | HTTP | 监控仪表板 |
| Prometheus | 9090 | HTTP | 指标收集 |
| AI引擎 | 8000 | HTTP | AI服务 |
| 自愈系统 | 8001 | HTTP | 自动化运维 |
| PostgreSQL | 5432 | TCP | 数据库 |
| Redis | 6379 | TCP | 缓存 |
| Node Exporter | 9100 | HTTP | 系统指标 |
| cAdvisor | 8081 | HTTP | 容器指标 |

---

## 3. 快速开始

### 3.1 一键部署脚本
```bash
#!/bin/bash
# 快速部署AIOps平台
set -e

echo "🚀 开始部署AIOps平台..."

# 检查系统要求
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose未安装，请先安装Docker Compose"
    exit 1
fi

# 克隆项目
git clone https://github.com/your-org/aiops.git
cd aiops

# 设置环境变量
cp .env.example .env

# 启动服务
docker-compose up -d

echo "✅ 部署完成！"
echo "📊 Grafana: http://localhost:3000 (admin/grafana-admin-2025)"
echo "🔧 API网关: http://localhost:8080"
echo "📈 Prometheus: http://localhost:9090"
```

### 3.2 验证安装
```bash
# 检查Docker服务状态
sudo systemctl status docker

# 检查容器运行状态
docker-compose ps

# 检查服务健康状态
curl -f http://localhost:3000/api/health || echo "Grafana未就绪"
curl -f http://localhost:9090/-/healthy || echo "Prometheus未就绪"
curl -f http://localhost:8080/health || echo "API网关未就绪"

# 查看日志
docker-compose logs --tail=50
```

---

## 4. 详细安装指南

### 4.1 环境准备

#### 4.1.1 系统更新
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL/Rocky/Alma
sudo dnf update -y
# 或者对于CentOS 7
# sudo yum update -y
```

#### 4.1.2 安装Docker Engine
```bash
#!/bin/bash
# install-docker.sh - Docker安装脚本

set -e

# 检测操作系统
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    echo "无法检测操作系统"
    exit 1
fi

echo "检测到操作系统: $OS $VER"

# Ubuntu/Debian安装
if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    # 卸载旧版本
    sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # 安装依赖
    sudo apt-get update
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加Docker官方GPG密钥
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # 添加Docker仓库
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# CentOS/RHEL/Rocky/Alma安装
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]] || [[ "$OS" == *"AlmaLinux"* ]]; then
    # 卸载旧版本
    sudo dnf remove -y docker docker-client docker-client-latest docker-common docker-latest docker-latest-logrotate docker-logrotate docker-engine || true
    
    # 安装依赖
    sudo dnf install -y dnf-plugins-core
    
    # 添加Docker仓库
    sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # 安装Docker Engine
    sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

else
    echo "不支持的操作系统: $OS"
    exit 1
fi

# 启动并启用Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 安装Docker Compose (独立版本)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "✅ Docker安装完成！"
echo "📝 请重新登录以使用户组更改生效"
echo "🔍 验证安装: docker --version && docker-compose --version"
```

#### 4.1.3 配置系统参数
```bash
#!/bin/bash
# configure-system.sh - 系统参数优化脚本

set -e

echo "🔧 配置系统参数..."

# 内核参数优化
cat << 'EOF' | sudo tee /etc/sysctl.d/99-aiops.conf
# AIOps平台系统参数优化

# 网络参数
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 1200
net.ipv4.tcp_keepalive_intvl = 30
net.ipv4.tcp_keepalive_probes = 3

# 内存参数
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.overcommit_memory = 1

# 文件系统参数
fs.file-max = 1000000
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 512

# 进程参数
kernel.pid_max = 4194304
EOF

# 应用内核参数
sudo sysctl -p /etc/sysctl.d/99-aiops.conf

# 配置系统限制
cat << 'EOF' | sudo tee /etc/security/limits.d/99-aiops.conf
# AIOps平台系统限制配置

* soft nofile 1000000
* hard nofile 1000000
* soft nproc 1000000
* hard nproc 1000000
* soft memlock unlimited
* hard memlock unlimited
EOF

# 配置systemd服务限制
sudo mkdir -p /etc/systemd/system/docker.service.d
cat << 'EOF' | sudo tee /etc/systemd/system/docker.service.d/override.conf
[Service]
LimitNOFILE=1000000
LimitNPROC=1000000
LimitMEMLOCK=infinity
EOF

# 重新加载systemd配置
sudo systemctl daemon-reload
sudo systemctl restart docker

echo "✅ 系统参数配置完成"
```

### 4.2 项目部署

#### 4.2.1 克隆项目
```bash
# 创建工作目录
sudo mkdir -p /opt/aiops
sudo chown $USER:$USER /opt/aiops
cd /opt/aiops

# 克隆项目代码
git clone https://github.com/your-org/aiops.git
cd aiops

# 检查项目结构
tree -L 2
```

#### 4.2.2 环境配置
```bash
#!/bin/bash
# setup-environment.sh - 环境配置脚本

set -e

echo "🔧 配置AIOps环境..."

# 创建环境配置文件
cat << 'EOF' > .env
# AIOps Linux环境配置
COMPOSE_PROJECT_NAME=aiops
DOCKER_BUILDKIT=1
COMPOSE_DOCKER_CLI_BUILD=1

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops
POSTGRES_PASSWORD=aiops-secure-password-2025

# Redis配置
REDIS_PASSWORD=redis-secure-password-2025

# AI引擎配置
AI_MODEL_PATH=/app/models
AI_LOG_LEVEL=INFO
AI_WORKERS=4

# 监控配置
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=grafana-admin-2025

# Linux特定配置
LINUX_SYSLOG_ENABLED=true
SYSTEMD_JOURNAL_ENABLED=true
NODE_EXPORTER_ENABLED=true

# 网络配置
TRAEFIK_DOMAIN=aiops.local
API_GATEWAY_HOST=0.0.0.0
API_GATEWAY_PORT=8080

# 安全配置
SSL_ENABLED=false
SSL_CERT_PATH=/opt/aiops/certs
JWT_SECRET=your-jwt-secret-key-2025
EOF

# 创建必要的目录
mkdir -p {logs,data,certs,backups}
mkdir -p configs/{prometheus,grafana,nginx,ssl}

# 设置目录权限
chmod 755 logs data certs backups
chmod 644 .env

echo "✅ 环境配置完成"
```

#### 4.2.3 启动服务
```bash
#!/bin/bash
# start-services.sh - 服务启动脚本

set -e

echo "🚀 启动AIOps服务..."

# 检查Docker服务
if ! systemctl is-active --quiet docker; then
    echo "启动Docker服务..."
    sudo systemctl start docker
fi

# 拉取镜像
echo "📥 拉取Docker镜像..."
docker-compose pull

# 构建自定义镜像
echo "🔨 构建自定义镜像..."
docker-compose build

# 启动服务
echo "▶️ 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "✅ AIOps平台启动完成！"
echo "🌐 访问地址:"
echo "  - Grafana仪表板: http://localhost:3000 (admin/grafana-admin-2025)"
echo "  - Prometheus监控: http://localhost:9090"
echo "  - API网关: http://localhost:8080"
echo "  - AI引擎: http://localhost:8000"
echo "  - 自愈系统: http://localhost:8001"
echo ""
echo "📋 查看日志: docker-compose logs -f [service-name]"
echo "🛑 停止服务: docker-compose down"
```

---

## 5. Bash脚本工具

### 5.1 系统管理脚本

#### 5.1.1 服务控制脚本
```bash
#!/bin/bash
# scripts/manage-aiops.sh - AIOps服务管理脚本

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/manage-aiops.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${CYAN}ℹ️ $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

# 帮助信息
show_help() {
    cat << EOF
AIOps服务管理脚本

用法: $0 [选项] <操作> [服务名]

操作:
  start     启动服务
  stop      停止服务
  restart   重启服务
  status    查看服务状态
  logs      查看服务日志
  update    更新服务
  backup    备份数据
  restore   恢复数据
  health    健康检查
  cleanup   清理资源

选项:
  -h, --help     显示帮助信息
  -v, --verbose  详细输出
  -f, --follow   跟踪日志输出
  -t, --tail N   显示最后N行日志 (默认: 100)

服务名:
  all           所有服务 (默认)
  traefik       反向代理
  prometheus    监控系统
  grafana       仪表板
  ai-engine     AI引擎
  self-healing  自愈系统
  api-gateway   API网关
  postgres      数据库
  redis         缓存

示例:
  $0 start                    # 启动所有服务
  $0 restart grafana          # 重启Grafana服务
  $0 logs -f ai-engine        # 跟踪AI引擎日志
  $0 status                   # 查看所有服务状态

EOF
}

# 检查Docker服务
check_docker() {
    if ! systemctl is-active --quiet docker; then
        log_warning "Docker服务未运行，正在启动..."
        sudo systemctl start docker
        sleep 5
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装"
        exit 1
    fi
}

# 切换到项目目录
cd "$PROJECT_ROOT"

# 启动服务
start_services() {
    local service="$1"
    
    log_info "启动AIOps服务: ${service:-all}"
    check_docker
    
    if [ "$service" = "all" ] || [ -z "$service" ]; then
        docker-compose up -d
    else
        docker-compose up -d "$service"
    fi
    
    log_success "服务启动完成"
}

# 停止服务
stop_services() {
    local service="$1"
    
    log_warning "停止AIOps服务: ${service:-all}"
    
    if [ "$service" = "all" ] || [ -z "$service" ]; then
        docker-compose down
    else
        docker-compose stop "$service"
    fi
    
    log_success "服务停止完成"
}

# 重启服务
restart_services() {
    local service="$1"
    
    log_info "重启AIOps服务: ${service:-all}"
    stop_services "$service"
    sleep 5
    start_services "$service"
}

# 查看服务状态
show_status() {
    log_info "AIOps服务状态:"
    
    echo -e "\n${CYAN}📊 容器状态:${NC}"
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${CYAN}💾 存储卷:${NC}"
    docker volume ls --filter "name=aiops" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
    
    echo -e "\n${CYAN}🌐 网络:${NC}"
    docker network ls --filter "name=aiops" --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"
    
    echo -e "\n${CYAN}💻 系统资源:${NC}"
    echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "内存使用率: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
    echo "磁盘使用率: $(df -h / | awk 'NR==2{print $5}')"
}

# 查看日志
show_logs() {
    local service="$1"
    local follow="$2"
    local tail_lines="$3"
    
    log_info "查看服务日志: ${service:-all}"
    
    local cmd="docker-compose logs"
    
    if [ "$tail_lines" ]; then
        cmd="$cmd --tail=$tail_lines"
    else
        cmd="$cmd --tail=100"
    fi
    
    if [ "$follow" = "true" ]; then
        cmd="$cmd -f"
    fi
    
    if [ "$service" ] && [ "$service" != "all" ]; then
        cmd="$cmd $service"
    fi
    
    eval "$cmd"
}

# 更新服务
update_services() {
    log_info "更新AIOps服务..."
    
    # 拉取最新代码
    if [ -d ".git" ]; then
        log_info "拉取最新代码..."
        git pull origin main
    fi
    
    # 停止服务
    docker-compose down
    
    # 拉取最新镜像
    log_info "拉取最新镜像..."
    docker-compose pull
    
    # 重新构建
    log_info "重新构建镜像..."
    docker-compose build --no-cache
    
    # 启动服务
    docker-compose up -d
    
    log_success "服务更新完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local services=(
        "grafana:http://localhost:3000/api/health"
        "prometheus:http://localhost:9090/-/healthy"
        "api-gateway:http://localhost:8080/health"
        "ai-engine:http://localhost:8000/health"
        "self-healing:http://localhost:8001/health"
    )
    
    echo -e "\n${CYAN}🏥 服务健康状态:${NC}"
    
    for service_url in "${services[@]}"; do
        IFS=':' read -r service_name url <<< "$service_url"
        
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name - 健康${NC}"
        else
            echo -e "${RED}❌ $service_name - 异常${NC}"
        fi
    done
    
    # 检查容器状态
    echo -e "\n${CYAN}📦 容器健康状态:${NC}"
    docker-compose ps --format "table {{.Name}}\t{{.Status}}"
}

# 清理资源
cleanup_resources() {
    log_warning "清理Docker资源..."
    
    read -p "确定要清理未使用的Docker资源吗？(y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker system prune -f
        docker volume prune -f
        docker network prune -f
        log_success "资源清理完成"
    else
        log_info "取消清理操作"
    fi
}

# 解析命令行参数
VERBOSE=false
FOLLOW=false
TAIL_LINES=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        -t|--tail)
            TAIL_LINES="$2"
            shift 2
            ;;
        start|stop|restart|status|logs|update|health|cleanup)
            ACTION="$1"
            shift
            ;;
        *)
            SERVICE="$1"
            shift
            ;;
    esac
done

# 执行操作
case "$ACTION" in
    start)
        start_services "$SERVICE"
        ;;
    stop)
        stop_services "$SERVICE"
        ;;
    restart)
        restart_services "$SERVICE"
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$SERVICE" "$FOLLOW" "$TAIL_LINES"
        ;;
    update)
        update_services
        ;;
    health)
        health_check
        ;;
    cleanup)
        cleanup_resources
        ;;
    *)
        log_error "未知操作: $ACTION"
        show_help
        exit 1
        ;;
esac
```

#### 5.1.2 系统监控脚本
```bash
#!/bin/bash
# scripts/monitor-system.sh - Linux系统监控脚本

set -e

# 配置
MONITOR_INTERVAL=30
PROMETHEUS_GATEWAY="http://localhost:9091/metrics/job/linux-system/instance/$(hostname)"
LOG_FILE="/var/log/aiops-monitor.log"

# 日志函数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# 获取CPU使用率
get_cpu_usage() {
    local cpu_usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "${cpu_usage:-0}"
}

# 获取内存使用情况
get_memory_usage() {
    local mem_info
    mem_info=$(free -b | grep "Mem:")
    
    local total used available
    total=$(echo "$mem_info" | awk '{print $2}')
    used=$(echo "$mem_info" | awk '{print $3}')
    available=$(echo "$mem_info" | awk '{print $7}')
    
    local usage_percent
    usage_percent=$(awk "BEGIN {printf \"%.2f\", $used/$total*100}")
    
    echo "total:$total used:$used available:$available percent:$usage_percent"
}

# 获取磁盘使用情况
get_disk_usage() {
    local disk_info
    disk_info=$(df -B1 / | tail -1)
    
    local total used available usage_percent
    total=$(echo "$disk_info" | awk '{print $2}')
    used=$(echo "$disk_info" | awk '{print $3}')
    available=$(echo "$disk_info" | awk '{print $4}')
    usage_percent=$(echo "$disk_info" | awk '{print $5}' | sed 's/%//')
    
    echo "total:$total used:$used available:$available percent:$usage_percent"
}

# 获取网络流量
get_network_stats() {
    local interface
    interface=$(ip route | grep default | awk '{print $5}' | head -1)
    
    if [ -n "$interface" ]; then
        local rx_bytes tx_bytes
        rx_bytes=$(cat "/sys/class/net/$interface/statistics/rx_bytes")
        tx_bytes=$(cat "/sys/class/net/$interface/statistics/tx_bytes")
        
        echo "interface:$interface rx_bytes:$rx_bytes tx_bytes:$tx_bytes"
    else
        echo "interface:unknown rx_bytes:0 tx_bytes:0"
    fi
}

# 获取系统负载
get_load_average() {
    local load_avg
    load_avg=$(uptime | awk -F'load average:' '{print $2}' | sed 's/,//g')
    
    local load1 load5 load15
    load1=$(echo "$load_avg" | awk '{print $1}')
    load5=$(echo "$load_avg" | awk '{print $2}')
    load15=$(echo "$load_avg" | awk '{print $3}')
    
    echo "load1:$load1 load5:$load5 load15:$load15"
}

# 获取进程信息
get_process_stats() {
    local total_processes running_processes
    total_processes=$(ps aux | wc -l)
    running_processes=$(ps aux | awk '$8 ~ /^R/ {count++} END {print count+0}')
    
    echo "total:$total_processes running:$running_processes"
}

# 检查关键服务状态
check_services() {
    local services=("docker" "ssh" "systemd-resolved" "cron")
    local service_status=""
    
    for service in "${services[@]}"; do
        if systemctl is-active --quiet "$service"; then
            service_status="${service_status}${service}:1 "
        else
            service_status="${service_status}${service}:0 "
        fi
    done
    
    echo "$service_status"
}

# 发送指标到Prometheus
send_metrics() {
    local metrics="$1"
    
    if command -v curl &> /dev/null; then
        if curl -s -X POST "$PROMETHEUS_GATEWAY" -d "$metrics" > /dev/null; then
            log "指标已发送到Prometheus"
        else
            log "发送指标失败"
        fi
    else
        log "curl命令不可用，无法发送指标"
    fi
}

# 生成Prometheus指标格式
generate_metrics() {
    local timestamp
    timestamp=$(date +%s)000
    
    # CPU指标
    local cpu_usage
    cpu_usage=$(get_cpu_usage)
    echo "linux_cpu_usage_percent $cpu_usage $timestamp"
    
    # 内存指标
    local memory_stats
    memory_stats=$(get_memory_usage)
    
    local mem_total mem_used mem_available mem_percent
    mem_total=$(echo "$memory_stats" | grep -o 'total:[0-9]*' | cut -d':' -f2)
    mem_used=$(echo "$memory_stats" | grep -o 'used:[0-9]*' | cut -d':' -f2)
    mem_available=$(echo "$memory_stats" | grep -o 'available:[0-9]*' | cut -d':' -f2)
    mem_percent=$(echo "$memory_stats" | grep -o 'percent:[0-9.]*' | cut -d':' -f2)
    
    echo "linux_memory_total_bytes $mem_total $timestamp"
    echo "linux_memory_used_bytes $mem_used $timestamp"
    echo "linux_memory_available_bytes $mem_available $timestamp"
    echo "linux_memory_usage_percent $mem_percent $timestamp"
    
    # 磁盘指标
    local disk_stats
    disk_stats=$(get_disk_usage)
    
    local disk_total disk_used disk_available disk_percent
    disk_total=$(echo "$disk_stats" | grep -o 'total:[0-9]*' | cut -d':' -f2)
    disk_used=$(echo "$disk_stats" | grep -o 'used:[0-9]*' | cut -d':' -f2)
    disk_available=$(echo "$disk_stats" | grep -o 'available:[0-9]*' | cut -d':' -f2)
    disk_percent=$(echo "$disk_stats" | grep -o 'percent:[0-9]*' | cut -d':' -f2)
    
    echo "linux_disk_total_bytes $disk_total $timestamp"
    echo "linux_disk_used_bytes $disk_used $timestamp"
    echo "linux_disk_available_bytes $disk_available $timestamp"
    echo "linux_disk_usage_percent $disk_percent $timestamp"
    
    # 网络指标
    local network_stats
    network_stats=$(get_network_stats)
    
    local rx_bytes tx_bytes
    rx_bytes=$(echo "$network_stats" | grep -o 'rx_bytes:[0-9]*' | cut -d':' -f2)
    tx_bytes=$(echo "$network_stats" | grep -o 'tx_bytes:[0-9]*' | cut -d':' -f2)
    
    echo "linux_network_rx_bytes_total $rx_bytes $timestamp"
    echo "linux_network_tx_bytes_total $tx_bytes $timestamp"
    
    # 系统负载指标
    local load_stats
    load_stats=$(get_load_average)
    
    local load1 load5 load15
    load1=$(echo "$load_stats" | grep -o 'load1:[0-9.]*' | cut -d':' -f2)
    load5=$(echo "$load_stats" | grep -o 'load5:[0-9.]*' | cut -d':' -f2)
    load15=$(echo "$load_stats" | grep -o 'load15:[0-9.]*' | cut -d':' -f2)
    
    echo "linux_load_average_1m $load1 $timestamp"
    echo "linux_load_average_5m $load5 $timestamp"
    echo "linux_load_average_15m $load15 $timestamp"
    
    # 进程指标
    local process_stats
    process_stats=$(get_process_stats)
    
    local total_processes running_processes
    total_processes=$(echo "$process_stats" | grep -o 'total:[0-9]*' | cut -d':' -f2)
    running_processes=$(echo "$process_stats" | grep -o 'running:[0-9]*' | cut -d':' -f2)
    
    echo "linux_processes_total $total_processes $timestamp"
    echo "linux_processes_running $running_processes $timestamp"
    
    # 服务状态指标
    local service_stats
    service_stats=$(check_services)
    
    for service_stat in $service_stats; do
        local service_name service_status
        service_name=$(echo "$service_stat" | cut -d':' -f1)
        service_status=$(echo "$service_stat" | cut -d':' -f2)
        
        echo "linux_service_status{service=\"$service_name\"} $service_status $timestamp"
    done
}

# 主监控循环
main() {
    log "启动Linux系统监控..."
    
    while true; do
        local metrics
        metrics=$(generate_metrics)
        
        if [ -n "$metrics" ]; then
            send_metrics "$metrics"
        fi
        
        sleep "$MONITOR_INTERVAL"
    done
}

# 信号处理
trap 'log "监控脚本已停止"; exit 0' SIGTERM SIGINT

# 启动监控
main
```

### 5.2 自动化运维脚本

#### 5.2.1 备份脚本
```bash
#!/bin/bash
# scripts/backup-aiops.sh - AIOps数据备份脚本

set -e

# 配置
BACKUP_BASE_DIR="/opt/aiops/backups"
BACKUP_RETENTION_DAYS=30
COMPRESSION_LEVEL=6
EXCLUDE_PATTERNS=("*.log" "*.tmp" "cache/*")

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# 检查依赖
check_dependencies() {
    local deps=("docker" "docker-compose" "tar" "gzip")
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "缺少依赖: $dep"
            exit 1
        fi
    done
}

# 创建备份目录
create_backup_dir() {
    local backup_date
    backup_date=$(date '+%Y%m%d-%H%M%S')
    BACKUP_DIR="$BACKUP_BASE_DIR/$backup_date"
    
    mkdir -p "$BACKUP_DIR"/{volumes,configs,database,logs}
    log_info "创建备份目录: $BACKUP_DIR"
}

# 备份Docker存储卷
backup_volumes() {
    log_info "备份Docker存储卷..."
    
    local volumes=(
        "aiops_prometheus-data"
        "aiops_grafana-data"
        "aiops_postgres-data"
        "aiops_redis-data"
        "aiops_ai-models"
        "aiops_ai-logs"
        "aiops_traefik-certs"
        "aiops_ansible-playbooks"
    )
    
    for volume in "${volumes[@]}"; do
        if docker volume inspect "$volume" &> /dev/null; then
            local volume_backup_file="$BACKUP_DIR/volumes/${volume}.tar.gz"
            
            log_info "备份卷: $volume"
            
            # 使用临时容器备份卷数据
            docker run --rm \
                -v "$volume:/data:ro" \
                -v "$BACKUP_DIR/volumes:/backup" \
                alpine:latest \
                tar czf "/backup/${volume}.tar.gz" -C /data .
            
            if [ $? -eq 0 ]; then
                log_success "已备份卷: $volume"
            else
                log_error "备份卷失败: $volume"
            fi
        else
            log_warning "卷不存在: $volume"
        fi
    done
}

# 备份配置文件
backup_configs() {
    log_info "备份配置文件..."
    
    local config_files=(
        "docker-compose.yml"
        ".env"
        "configs/"
        "scripts/"
    )
    
    for config in "${config_files[@]}"; do
        if [ -e "$config" ]; then
            cp -r "$config" "$BACKUP_DIR/configs/"
            log_success "已备份: $config"
        else
            log_warning "配置文件不存在: $config"
        fi
    done
}

# 备份数据库
backup_database() {
    log_info "备份PostgreSQL数据库..."
    
    local db_container
    db_container=$(docker-compose ps -q postgres)
    
    if [ -n "$db_container" ]; then
        local backup_file="$BACKUP_DIR/database/postgres_$(date '+%Y%m%d_%H%M%S').sql"
        
        docker exec "$db_container" pg_dumpall -U aiops > "$backup_file"
        
        if [ $? -eq 0 ]; then
            gzip "$backup_file"
            log_success "数据库备份完成: ${backup_file}.gz"
        else
            log_error "数据库备份失败"
        fi
    else
        log_warning "PostgreSQL容器未运行"
    fi
}

# 备份应用日志
backup_logs() {
    log_info "备份应用日志..."
    
    if [ -d "logs" ]; then
        tar czf "$BACKUP_DIR/logs/application-logs.tar.gz" logs/
        log_success "应用日志备份完成"
    else
        log_warning "日志目录不存在"
    fi
    
    # 备份Docker容器日志
    local containers
    containers=$(docker-compose ps -q)
    
    if [ -n "$containers" ]; then
        mkdir -p "$BACKUP_DIR/logs/containers"
        
        for container in $containers; do
            local container_name
            container_name=$(docker inspect --format='{{.Name}}' "$container" | sed 's/^\///')
            
            docker logs "$container" > "$BACKUP_DIR/logs/containers/${container_name}.log" 2>&1
            log_success "已备份容器日志: $container_name"
        done
    fi
}

# 创建备份清单
create_manifest() {
    log_info "创建备份清单..."
    
    local manifest_file="$BACKUP_DIR/backup-manifest.json"
    
    cat > "$manifest_file" << EOF
{
  "backup_info": {
    "timestamp": "$(date -Iseconds)",
    "hostname": "$(hostname)",
    "backup_version": "3.0.0",
    "backup_type": "full"
  },
  "system_info": {
    "os": "$(lsb_release -d | cut -f2)",
    "kernel": "$(uname -r)",
    "docker_version": "$(docker --version)",
    "compose_version": "$(docker-compose --version)"
  },
  "backup_contents": {
    "volumes": $(ls "$BACKUP_DIR/volumes/" 2>/dev/null | jq -R . | jq -s . || echo '[]'),
    "configs": $(find "$BACKUP_DIR/configs/" -type f 2>/dev/null | jq -R . | jq -s . || echo '[]'),
    "database": $(ls "$BACKUP_DIR/database/" 2>/dev/null | jq -R . | jq -s . || echo '[]'),
    "logs": $(ls "$BACKUP_DIR/logs/" 2>/dev/null | jq -R . | jq -s . || echo '[]')
  },
  "backup_size": "$(du -sh "$BACKUP_DIR" | cut -f1)"
}
EOF
    
    log_success "备份清单已创建: $manifest_file"
}

# 压缩备份
compress_backup() {
    log_info "压缩备份文件..."
    
    local backup_name
    backup_name=$(basename "$BACKUP_DIR")
    local compressed_file="${BACKUP_BASE_DIR}/${backup_name}.tar.gz"
    
    tar czf "$compressed_file" -C "$(dirname "$BACKUP_DIR")" "$backup_name"
    
    if [ $? -eq 0 ]; then
        rm -rf "$BACKUP_DIR"
        log_success "备份已压缩: $compressed_file"
        echo "$compressed_file"
    else
        log_error "备份压缩失败"
        exit 1
    fi
}

# 清理旧备份
cleanup_old_backups() {
    log_info "清理旧备份文件..."
    
    find "$BACKUP_BASE_DIR" -name "*.tar.gz" -type f -mtime +"$BACKUP_RETENTION_DAYS" -delete
    
    local remaining_backups
    remaining_backups=$(find "$BACKUP_BASE_DIR" -name "*.tar.gz" -type f | wc -l)
    
    log_success "清理完成，保留 $remaining_backups 个备份文件"
}

# 发送通知
send_notification() {
    local status="$1"
    local message="$2"
    
    # 这里可以集成邮件、Slack、钉钉等通知方式
    log_info "备份通知: $status - $message"
    
    # 示例：发送到系统日志
    logger -t "aiops-backup" "$status: $message"
}

# 主备份流程
main() {
    local start_time
    start_time=$(date +%s)
    
    log_info "开始AIOps平台备份..."
    
    # 检查依赖
    check_dependencies
    
    # 创建备份目录
    create_backup_dir
    
    # 切换到项目目录
    cd "$(dirname "$0")/.."
    
    # 执行备份
    backup_volumes
    backup_configs
    backup_database
    backup_logs
    
    # 创建清单
    create_manifest
    
    # 压缩备份
    local backup_file
    backup_file=$(compress_backup)
    
    # 清理旧备份
    cleanup_old_backups
    
    # 计算耗时
    local end_time duration
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    log_success "备份完成！耗时: ${duration}秒"
    log_success "备份文件: $backup_file"
    
    # 发送成功通知
    send_notification "SUCCESS" "AIOps备份完成，文件: $backup_file"
}

# 错误处理
trap 'log_error "备份过程中发生错误"; send_notification "ERROR" "AIOps备份失败"; exit 1' ERR

# 执行主流程
main "$@"
```

---

## 6. Linux特定配置

### 6.1 systemd服务配置
```bash
#!/bin/bash
# 创建AIOps systemd服务

# 创建服务文件
sudo tee /etc/systemd/system/aiops.service > /dev/null << 'EOF'
[Unit]
Description=AIOps智能运维平台
Requires=docker.service
After=docker.service
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/aiops/aiops
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

# 启用服务
sudo systemctl daemon-reload
sudo systemctl enable aiops.service

echo "✅ AIOps systemd服务已创建并启用"
echo "🚀 启动服务: sudo systemctl start aiops"
echo "📊 查看状态: sudo systemctl status aiops"
```

### 6.2 日志轮转配置
```bash
# 配置logrotate
sudo tee /etc/logrotate.d/aiops > /dev/null << 'EOF'
/opt/aiops/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        /usr/bin/docker-compose -f /opt/aiops/aiops/docker-compose.yml kill -s USR1 $(docker-compose -f /opt/aiops/aiops/docker-compose.yml ps -q) 2>/dev/null || true
    endscript
}
EOF

echo "✅ 日志轮转配置已创建"
```

### 6.3 防火墙配置
```bash
#!/bin/bash
# configure-firewall.sh - 防火墙配置脚本

set -e

# 检测防火墙类型
if command -v ufw &> /dev/null; then
    FIREWALL="ufw"
elif command -v firewall-cmd &> /dev/null; then
    FIREWALL="firewalld"
elif command -v iptables &> /dev/null; then
    FIREWALL="iptables"
else
    echo "❌ 未检测到支持的防火墙"
    exit 1
fi

echo "🔥 检测到防火墙: $FIREWALL"

# AIOps端口列表
PORTS=(80 443 3000 8080 9090 8000 8001 5432 6379 9100 8081)

# UFW配置
configure_ufw() {
    echo "配置UFW防火墙..."
    
    for port in "${PORTS[@]}"; do
        sudo ufw allow "$port"/tcp
        echo "✅ 已开放端口: $port/tcp"
    done
    
    # 启用UFW
    sudo ufw --force enable
    echo "✅ UFW防火墙已启用"
}

# firewalld配置
configure_firewalld() {
    echo "配置firewalld防火墙..."
    
    for port in "${PORTS[@]}"; do
        sudo firewall-cmd --permanent --add-port="$port"/tcp
        echo "✅ 已开放端口: $port/tcp"
    done
    
    # 重新加载配置
    sudo firewall-cmd --reload
    echo "✅ firewalld配置已重新加载"
}

# iptables配置
configure_iptables() {
    echo "配置iptables防火墙..."
    
    for port in "${PORTS[@]}"; do
        sudo iptables -A INPUT -p tcp --dport "$port" -j ACCEPT
        echo "✅ 已开放端口: $port/tcp"
    done
    
    # 保存规则
    if command -v iptables-save &> /dev/null; then
        sudo iptables-save > /etc/iptables/rules.v4
        echo "✅ iptables规则已保存"
    fi
}

# 根据防火墙类型执行配置
case "$FIREWALL" in
    "ufw")
        configure_ufw
        ;;
    "firewalld")
        configure_firewalld
        ;;
    "iptables")
        configure_iptables
        ;;
    *)
        echo "❌ 不支持的防火墙类型: $FIREWALL"
        exit 1
        ;;
esac

echo "✅ 防火墙配置完成"
```

### 6.4 系统监控集成
```bash
#!/bin/bash
# setup-monitoring.sh - 系统监控集成脚本

set -e

# 安装Node Exporter
install_node_exporter() {
    local version="1.7.0"
    local arch
    arch=$(uname -m)
    
    case $arch in
        x86_64) arch="amd64" ;;
        aarch64) arch="arm64" ;;
        armv7l) arch="armv7" ;;
        *) echo "不支持的架构: $arch"; exit 1 ;;
    esac
    
    echo "📥 下载Node Exporter..."
    wget -q "https://github.com/prometheus/node_exporter/releases/download/v${version}/node_exporter-${version}.linux-${arch}.tar.gz"
    
    tar xzf "node_exporter-${version}.linux-${arch}.tar.gz"
    sudo mv "node_exporter-${version}.linux-${arch}/node_exporter" /usr/local/bin/
    rm -rf "node_exporter-${version}.linux-${arch}"*
    
    # 创建systemd服务
    sudo tee /etc/systemd/system/node_exporter.service > /dev/null << 'EOF'
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # 创建用户
    sudo useradd --no-create-home --shell /bin/false node_exporter || true
    
    # 启动服务
    sudo systemctl daemon-reload
    sudo systemctl enable node_exporter
    sudo systemctl start node_exporter
    
    echo "✅ Node Exporter安装完成"
}

# 配置rsyslog集成
setup_rsyslog() {
    echo "📝 配置rsyslog集成..."
    
    # 创建AIOps日志配置
    sudo tee /etc/rsyslog.d/30-aiops.conf > /dev/null << 'EOF'
# AIOps平台日志配置

# 应用程序日志
:programname, isequal, "aiops" /var/log/aiops/application.log
& stop

# Docker容器日志
:programname, startswith, "docker/" /var/log/aiops/containers.log
& stop

# 系统监控日志
:programname, isequal, "aiops-monitor" /var/log/aiops/monitoring.log
& stop
EOF
    
    # 创建日志目录
    sudo mkdir -p /var/log/aiops
    sudo chown syslog:adm /var/log/aiops
    
    # 重启rsyslog
    sudo systemctl restart rsyslog
    
    echo "✅ rsyslog配置完成"
}

# 配置cron任务
setup_cron_jobs() {
    echo "⏰ 配置定时任务..."
    
    # 创建cron任务
    cat << 'EOF' | sudo tee /etc/cron.d/aiops > /dev/null
# AIOps平台定时任务

# 每5分钟检查服务状态
*/5 * * * * root /opt/aiops/aiops/scripts/health-check.sh >> /var/log/aiops/health-check.log 2>&1

# 每天凌晨2点执行备份
0 2 * * * root /opt/aiops/aiops/scripts/backup-aiops.sh >> /var/log/aiops/backup.log 2>&1

# 每周日凌晨3点清理日志
0 3 * * 0 root /opt/aiops/aiops/scripts/cleanup-logs.sh >> /var/log/aiops/cleanup.log 2>&1

# 每小时更新系统指标
0 * * * * root /opt/aiops/aiops/scripts/collect-metrics.sh >> /var/log/aiops/metrics.log 2>&1
EOF
    
    echo "✅ 定时任务配置完成"
}

# 主函数
main() {
    echo "🔧 开始配置Linux系统监控集成..."
    
    install_node_exporter
    setup_rsyslog
    setup_cron_jobs
    
    echo "✅ Linux系统监控集成配置完成"
}

main "$@"
```

---

## 7. 服务管理

### 7.1 服务启动顺序
```bash
#!/bin/bash
# 服务启动顺序管理

# 定义服务启动顺序
START_ORDER=(
    "postgres"      # 数据库服务
    "redis"         # 缓存服务
    "traefik"       # 反向代理
    "prometheus"    # 监控系统
    "grafana"       # 仪表板
    "ai-engine"     # AI引擎
    "self-healing"  # 自愈系统
    "api-gateway"   # API网关
)

# 按顺序启动服务
start_services_ordered() {
    for service in "${START_ORDER[@]}"; do
        echo "🚀 启动服务: $service"
        docker-compose up -d "$service"
        
        # 等待服务就绪
        sleep 10
        
        # 检查服务状态
        if docker-compose ps "$service" | grep -q "Up"; then
            echo "✅ 服务启动成功: $service"
        else
            echo "❌ 服务启动失败: $service"
            exit 1
        fi
    done
}

start_services_ordered
```

### 7.2 健康检查
```bash
#!/bin/bash
# scripts/health-check.sh - 服务健康检查脚本

set -e

# 健康检查配置
HEALTH_CHECKS=(
    "grafana:http://localhost:3000/api/health:Grafana仪表板"
    "prometheus:http://localhost:9090/-/healthy:Prometheus监控"
    "api-gateway:http://localhost:8080/health:API网关"
    "ai-engine:http://localhost:8000/health:AI引擎"
    "self-healing:http://localhost:8001/health:自愈系统"
)

# 数据库连接检查
check_database() {
    local db_container
    db_container=$(docker-compose ps -q postgres)
    
    if [ -n "$db_container" ]; then
        if docker exec "$db_container" pg_isready -U aiops > /dev/null 2>&1; then
            echo "✅ PostgreSQL数据库连接正常"
            return 0
        else
            echo "❌ PostgreSQL数据库连接失败"
            return 1
        fi
    else
        echo "❌ PostgreSQL容器未运行"
        return 1
    fi
}

# Redis连接检查
check_redis() {
    local redis_container
    redis_container=$(docker-compose ps -q redis)
    
    if [ -n "$redis_container" ]; then
        if docker exec "$redis_container" redis-cli ping | grep -q "PONG"; then
            echo "✅ Redis缓存连接正常"
            return 0
        else
            echo "❌ Redis缓存连接失败"
            return 1
        fi
    else
        echo "❌ Redis容器未运行"
        return 1
    fi
}

# HTTP服务检查
check_http_services() {
    local failed_services=()
    
    for check in "${HEALTH_CHECKS[@]}"; do
        IFS=':' read -r service_name url description <<< "$check"
        
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo "✅ $description 健康检查通过"
        else
            echo "❌ $description 健康检查失败"
            failed_services+=("$service_name")
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        echo "⚠️ 失败的服务: ${failed_services[*]}"
        return 1
    fi
    
    return 0
}

# 容器状态检查
check_containers() {
    local unhealthy_containers
    unhealthy_containers=$(docker-compose ps --format "table {{.Name}}\t{{.Status}}" | grep -v "Up" | tail -n +2)
    
    if [ -n "$unhealthy_containers" ]; then
        echo "❌ 发现异常容器:"
        echo "$unhealthy_containers"
        return 1
    else
        echo "✅ 所有容器状态正常"
        return 0
    fi
}

# 磁盘空间检查
check_disk_space() {
    local usage
    usage=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
    
    if [ "$usage" -gt 90 ]; then
        echo "❌ 磁盘空间不足: ${usage}%"
        return 1
    elif [ "$usage" -gt 80 ]; then
        echo "⚠️ 磁盘空间警告: ${usage}%"
        return 0
    else
        echo "✅ 磁盘空间充足: ${usage}%"
        return 0
    fi
}

# 内存使用检查
check_memory() {
    local usage
    usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    
    if [ "$usage" -gt 90 ]; then
        echo "❌ 内存使用过高: ${usage}%"
        return 1
    elif [ "$usage" -gt 80 ]; then
        echo "⚠️ 内存使用警告: ${usage}%"
        return 0
    else
        echo "✅ 内存使用正常: ${usage}%"
        return 0
    fi
}

# 主健康检查函数
main() {
    echo "🏥 开始AIOps平台健康检查..."
    echo "检查时间: $(date)"
    echo "========================================"
    
    local exit_code=0
    
    # 执行各项检查
    check_containers || exit_code=1
    check_database || exit_code=1
    check_redis || exit_code=1
    check_http_services || exit_code=1
    check_disk_space || exit_code=1
    check_memory || exit_code=1
    
    echo "========================================"
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ 所有健康检查通过"
    else
        echo "❌ 发现健康问题，请检查上述错误"
    fi
    
    exit $exit_code
}

main "$@"
```

---

## 8. 监控和告警

### 8.1 Grafana仪表板配置
```json
{
  "dashboard": {
    "id": null,
    "title": "AIOps Linux系统监控",
    "tags": ["aiops", "linux", "system"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "系统概览",
        "type": "stat",
        "targets": [
          {
            "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU使用率"
          },
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "内存使用率"
          },
          {
            "expr": "100 - ((node_filesystem_avail_bytes{mountpoint=\"/\"} * 100) / node_filesystem_size_bytes{mountpoint=\"/\"})",
            "legendFormat": "磁盘使用率"
          }
        ]
      },
      {
        "id": 2,
        "title": "CPU使用率趋势",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU使用率"
          }
        ]
      },
      {
        "id": 3,
        "title": "内存使用情况",
        "type": "graph",
        "targets": [
          {
            "expr": "node_memory_MemTotal_bytes",
            "legendFormat": "总内存"
          },
          {
            "expr": "node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes",
            "legendFormat": "已用内存"
          },
          {
            "expr": "node_memory_MemAvailable_bytes",
            "legendFormat": "可用内存"
          }
        ]
      },
      {
        "id": 4,
        "title": "磁盘I/O",
        "type": "graph",
        "targets": [
          {
            "expr": "irate(node_disk_read_bytes_total[5m])",
            "legendFormat": "读取速率"
          },
          {
            "expr": "irate(node_disk_written_bytes_total[5m])",
            "legendFormat": "写入速率"
          }
        ]
      },
      {
        "id": 5,
        "title": "网络流量",
        "type": "graph",
        "targets": [
          {
            "expr": "irate(node_network_receive_bytes_total{device!=\"lo\"}[5m])",
            "legendFormat": "接收流量"
          },
          {
            "expr": "irate(node_network_transmit_bytes_total{device!=\"lo\"}[5m])",
            "legendFormat": "发送流量"
          }
        ]
      },
      {
        "id": 6,
        "title": "容器状态",
        "type": "table",
        "targets": [
          {
            "expr": "container_last_seen",
            "legendFormat": "{{name}}"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

### 8.2 告警规则配置
```yaml
# configs/prometheus/alert-rules-linux.yml
groups:
  - name: linux-system
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg(irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "Linux系统CPU使用率过高"
          description: "CPU使用率已超过80%，当前值: {{ $value }}%"
      
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "Linux系统内存使用率过高"
          description: "内存使用率已超过85%，当前值: {{ $value }}%"
      
      - alert: HighDiskUsage
        expr: 100 - ((node_filesystem_avail_bytes{mountpoint="/"} * 100) / node_filesystem_size_bytes{mountpoint="/"}) > 90
        for: 5m
        labels:
          severity: critical
          service: system
        annotations:
          summary: "Linux系统磁盘空间不足"
          description: "根分区磁盘使用率已超过90%，当前值: {{ $value }}%"
      
      - alert: SystemLoadHigh
        expr: node_load15 > 2
        for: 10m
        labels:
          severity: warning
          service: system
        annotations:
          summary: "Linux系统负载过高"
          description: "15分钟平均负载过高，当前值: {{ $value }}"
      
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
          service: "{{ $labels.job }}"
        annotations:
          summary: "服务不可用"
          description: "服务 {{ $labels.job }} 已停止响应"
      
      - alert: ContainerDown
        expr: absent(container_last_seen{name=~".+"})
        for: 1m
        labels:
          severity: critical
          service: docker
        annotations:
          summary: "容器已停止"
          description: "容器 {{ $labels.name }} 已停止运行"
```

---

## 9. 故障排除

### 9.1 常见问题解决

#### 9.1.1 Docker相关问题
```bash
# 问题1: Docker服务无法启动
sudo systemctl status docker
sudo journalctl -u docker.service

# 解决方案:
sudo systemctl restart docker
sudo systemctl enable docker

# 问题2: 容器无法访问网络
docker network ls
docker network inspect aiops_default

# 解决方案:
docker-compose down
docker network prune -f
docker-compose up -d

# 问题3: 存储卷权限问题
docker volume inspect aiops_postgres-data
sudo chown -R 999:999 /var/lib/docker/volumes/aiops_postgres-data/_data
```

#### 9.1.2 服务启动问题
```bash
# 检查服务日志
docker-compose logs grafana
docker-compose logs prometheus
docker-compose logs postgres

# 检查端口占用
sudo netstat -tlnp | grep :3000
sudo ss -tlnp | grep :3000

# 释放端口
sudo fuser -k 3000/tcp
```

#### 9.1.3 性能问题诊断
```bash
#!/bin/bash
# 性能诊断脚本

echo "=== 系统性能诊断 ==="

# CPU信息
echo "CPU信息:"
lscpu | grep -E "Model name|CPU\(s\):|Thread|Core"

# 内存信息
echo -e "\n内存信息:"
free -h

# 磁盘信息
echo -e "\n磁盘使用:"
df -h

# 系统负载
echo -e "\n系统负载:"
uptime

# 进程信息
echo -e "\n占用资源最多的进程:"
ps aux --sort=-%cpu | head -10

# Docker资源使用
echo -e "\nDocker容器资源使用:"
docker stats --no-stream

# 网络连接
echo -e "\n网络连接状态:"
ss -tuln | grep LISTEN
```

### 9.2 日志分析

#### 9.2.1 集中化日志查看
```bash
#!/bin/bash
# 日志分析脚本

# 查看所有服务日志
view_all_logs() {
    echo "📋 查看所有服务日志 (最近100行):"
    docker-compose logs --tail=100
}

# 查看错误日志
view_error_logs() {
    echo "❌ 查看错误日志:"
    docker-compose logs | grep -i "error\|exception\|failed\|fatal"
}

# 查看特定服务日志
view_service_logs() {
    local service="$1"
    echo "📊 查看 $service 服务日志:"
    docker-compose logs --tail=50 "$service"
}

# 实时监控日志
monitor_logs() {
    echo "👁️ 实时监控所有服务日志:"
    docker-compose logs -f
}

# 分析日志统计
analyze_logs() {
    echo "📈 日志统计分析:"
    
    local log_file="/tmp/aiops-logs.txt"
    docker-compose logs > "$log_file"
    
    echo "总日志行数: $(wc -l < "$log_file")"
    echo "错误日志数: $(grep -ci "error" "$log_file")"
    echo "警告日志数: $(grep -ci "warning" "$log_file")"
    echo "信息日志数: $(grep -ci "info" "$log_file")"
    
    echo -e "\n最近的错误:"
    grep -i "error" "$log_file" | tail -5
    
    rm "$log_file"
}

# 根据参数执行相应功能
case "${1:-all}" in
    "all") view_all_logs ;;
    "error") view_error_logs ;;
    "monitor") monitor_logs ;;
    "analyze") analyze_logs ;;
    *) view_service_logs "$1" ;;
esac
```

---

## 10. 性能优化

### 10.1 Docker配置优化
```json
{
  "data-root": "/var/lib/docker",
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 1000000,
      "Soft": 1000000
    },
    "nproc": {
      "Name": "nproc",
      "Hard": 1000000,
      "Soft": 1000000
    }
  },
  "live-restore": true,
  "userland-proxy": false,
  "experimental": false,
  "metrics-addr": "127.0.0.1:9323",
  "experimental": true
}
```

### 10.2 系统调优脚本
```bash
#!/bin/bash
# system-tuning.sh - Linux系统性能调优脚本

set -e

echo "🚀 开始Linux系统性能调优..."

# 内核参数调优
tune_kernel_parameters() {
    echo "⚙️ 调优内核参数..."
    
    cat << 'EOF' | sudo tee /etc/sysctl.d/99-aiops-performance.conf
# AIOps性能调优参数

# 网络性能优化
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 30000
net.ipv4.tcp_congestion_control = bbr

# 文件系统优化
fs.file-max = 2097152
fs.nr_open = 2097152
vm.max_map_count = 262144

# 内存管理优化
vm.swappiness = 1
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
vm.vfs_cache_pressure = 50

# 进程调度优化
kernel.sched_migration_cost_ns = 5000000
kernel.sched_autogroup_enabled = 0
EOF
    
    sudo sysctl -p /etc/sysctl.d/99-aiops-performance.conf
    echo "✅ 内核参数调优完成"
}

# 文件描述符限制调优
tune_file_limits() {
    echo "📁 调优文件描述符限制..."
    
    cat << 'EOF' | sudo tee /etc/security/limits.d/99-aiops-performance.conf
# AIOps性能调优 - 文件描述符限制

* soft nofile 1048576
* hard nofile 1048576
* soft nproc 1048576
* hard nproc 1048576
* soft memlock unlimited
* hard memlock unlimited
root soft nofile 1048576
root hard nofile 1048576
root soft nproc 1048576
root hard nproc 1048576
EOF
    
    echo "✅ 文件描述符限制调优完成"
}

# I/O调度器优化
tune_io_scheduler() {
    echo "💾 优化I/O调度器..."
    
    # 检测存储设备类型并设置合适的调度器
    for device in /sys/block/*/queue/scheduler; do
        device_name=$(echo "$device" | cut -d'/' -f4)
        
        # 检查是否为SSD
        if [ -f "/sys/block/$device_name/queue/rotational" ]; then
            rotational=$(cat "/sys/block/$device_name/queue/rotational")
            
            if [ "$rotational" = "0" ]; then
                # SSD使用noop或none调度器
                if grep -q "none" "$device"; then
                    echo "none" | sudo tee "$device" > /dev/null
                    echo "✅ SSD $device_name 设置为none调度器"
                elif grep -q "noop" "$device"; then
                    echo "noop" | sudo tee "$device" > /dev/null
                    echo "✅ SSD $device_name 设置为noop调度器"
                fi
            else
                # HDD使用deadline调度器
                if grep -q "deadline" "$device"; then
                    echo "deadline" | sudo tee "$device" > /dev/null
                    echo "✅ HDD $device_name 设置为deadline调度器"
                fi
            fi
        fi
    done
}

# CPU调频优化
tune_cpu_governor() {
    echo "⚡ 优化CPU调频策略..."
    
    # 设置CPU调频器为performance模式
    if command -v cpupower &> /dev/null; then
        sudo cpupower frequency-set -g performance
        echo "✅ CPU调频器设置为performance模式"
    else
        # 手动设置
        for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
            if [ -f "$cpu" ]; then
                echo "performance" | sudo tee "$cpu" > /dev/null
            fi
        done
        echo "✅ 手动设置CPU调频器为performance模式"
    fi
}

# 透明大页优化
tune_transparent_hugepages() {
    echo "📄 优化透明大页设置..."
    
    # 禁用透明大页（对数据库性能有益）
    echo "never" | sudo tee /sys/kernel/mm/transparent_hugepage/enabled > /dev/null
    echo "never" | sudo tee /sys/kernel/mm/transparent_hugepage/defrag > /dev/null
    
    # 永久禁用
    if ! grep -q "transparent_hugepage=never" /etc/default/grub; then
        sudo sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="transparent_hugepage=never /' /etc/default/grub
        sudo update-grub
        echo "✅ 透明大页已永久禁用（重启后生效）"
    else
        echo "✅ 透明大页优化完成"
    fi
}

# 网络优化
tune_network() {
    echo "🌐 优化网络设置..."
    
    # 启用BBR拥塞控制
    if ! lsmod | grep -q tcp_bbr; then
        echo "tcp_bbr" | sudo tee -a /etc/modules-load.d/modules.conf
        sudo modprobe tcp_bbr
        echo "✅ BBR拥塞控制已启用"
    fi
    
    # 优化网络接口
    for interface in $(ip link show | grep -E '^[0-9]+:' | grep -v lo | cut -d':' -f2 | tr -d ' '); do
        # 增加接收队列长度
        sudo ethtool -G "$interface" rx 4096 tx 4096 2>/dev/null || true
        
        # 启用网络卸载功能
        sudo ethtool -K "$interface" gso on tso on gro on lro on 2>/dev/null || true
        
        echo "✅ 网络接口 $interface 优化完成"
    done
}

# 主函数
main() {
    echo "🔧 Linux系统性能调优开始..."
    
    tune_kernel_parameters
    tune_file_limits
    tune_io_scheduler
    tune_cpu_governor
    tune_transparent_hugepages
    tune_network
    
    echo ""
    echo "✅ Linux系统性能调优完成！"
    echo "📝 建议重启系统以确保所有优化生效"
    echo "🔍 可以使用以下命令验证优化效果:"
    echo "   - sysctl -a | grep -E 'net.core|vm.'"
    echo "   - cat /proc/sys/kernel/sched_*"
    echo "   - cat /sys/kernel/mm/transparent_hugepage/enabled"
}

main "$@"
```

---

## 11. 安全配置

### 11.1 SSL/TLS配置
```bash
#!/bin/bash
# setup-ssl.sh - SSL/TLS证书配置脚本

set -e

# 配置
DOMAIN="aiops.local"
CERT_DIR="/opt/aiops/certs"
COUNTRY="CN"
STATE="Beijing"
CITY="Beijing"
ORG="AIOps"
ORG_UNIT="IT"

# 创建证书目录
mkdir -p "$CERT_DIR"
cd "$CERT_DIR"

echo "🔐 生成SSL/TLS证书..."

# 生成私钥
openssl genrsa -out "$DOMAIN.key" 2048

# 生成证书签名请求
openssl req -new -key "$DOMAIN.key" -out "$DOMAIN.csr" -subj "/C=$COUNTRY/ST=$STATE/L=$CITY/O=$ORG/OU=$ORG_UNIT/CN=$DOMAIN"

# 生成自签名证书
openssl x509 -req -days 365 -in "$DOMAIN.csr" -signkey "$DOMAIN.key" -out "$DOMAIN.crt"

# 设置权限
chmod 600 "$DOMAIN.key"
chmod 644 "$DOMAIN.crt"

echo "✅ SSL证书生成完成"
echo "📁 证书位置: $CERT_DIR"
echo "🔑 私钥: $DOMAIN.key"
echo "📜 证书: $DOMAIN.crt"
```

### 11.2 访问控制配置
```yaml
# configs/traefik/dynamic.yml - Traefik动态配置
http:
  middlewares:
    # 基础认证
    basic-auth:
      basicAuth:
        users:
          - "admin:$2y$10$..."
    
    # IP白名单
    ip-whitelist:
      ipWhiteList:
        sourceRange:
          - "127.0.0.1/32"
          - "10.0.0.0/8"
          - "172.16.0.0/12"
          - "192.168.0.0/16"
    
    # 速率限制
    rate-limit:
      rateLimit:
        average: 100
        burst: 200
    
    # 安全头
    security-headers:
      headers:
        customRequestHeaders:
          X-Forwarded-Proto: "https"
        customResponseHeaders:
          X-Frame-Options: "DENY"
          X-Content-Type-Options: "nosniff"
          X-XSS-Protection: "1; mode=block"
          Strict-Transport-Security: "max-age=31536000; includeSubDomains"
          Content-Security-Policy: "default-src 'self'"

  routers:
    # Grafana路由
    grafana-secure:
      rule: "Host(`grafana.aiops.local`)"
      service: "grafana"
      middlewares:
        - "basic-auth"
        - "ip-whitelist"
        - "rate-limit"
        - "security-headers"
      tls:
        certResolver: "letsencrypt"
    
    # API网关路由
    api-gateway-secure:
      rule: "Host(`api.aiops.local`)"
      service: "api-gateway"
      middlewares:
        - "rate-limit"
        - "security-headers"
      tls:
        certResolver: "letsencrypt"

  services:
    grafana:
      loadBalancer:
        servers:
          - url: "http://grafana:3000"
    
    api-gateway:
      loadBalancer:
        servers:
          - url: "http://api-gateway:8080"
```

---

## 12. 备份和恢复

### 12.1 自动备份配置
```bash
#!/bin/bash
# setup-backup-cron.sh - 配置自动备份任务

set -e

BACKUP_SCRIPT="/opt/aiops/aiops/scripts/backup-aiops.sh"
LOG_FILE="/var/log/aiops/backup.log"

# 创建日志目录
sudo mkdir -p /var/log/aiops
sudo chown $USER:$USER /var/log/aiops

# 创建备份cron任务
cat << EOF | sudo tee /etc/cron.d/aiops-backup > /dev/null
# AIOps自动备份任务
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# 每天凌晨2点执行完整备份
0 2 * * * root $BACKUP_SCRIPT >> $LOG_FILE 2>&1

# 每6小时执行增量备份
0 */6 * * * root $BACKUP_SCRIPT --incremental >> $LOG_FILE 2>&1

# 每周日凌晨1点清理旧备份
0 1 * * 0 root find /opt/aiops/backups -name "*.tar.gz" -mtime +30 -delete
EOF

echo "✅ 自动备份任务配置完成"
echo "📋 查看任务: sudo crontab -l"
echo "📊 查看日志: tail -f $LOG_FILE"
```

### 12.2 数据恢复脚本
```bash
#!/bin/bash
# restore-aiops.sh - AIOps数据恢复脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')] ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
AIOps数据恢复脚本

用法: $0 [选项] <备份文件>

选项:
  -h, --help          显示帮助信息
  -f, --force         强制恢复（不询问确认）
  -v, --volumes-only  仅恢复存储卷数据
  -c, --configs-only  仅恢复配置文件
  -d, --database-only 仅恢复数据库

示例:
  $0 /opt/aiops/backups/20250109-120000.tar.gz
  $0 --volumes-only backup.tar.gz
  $0 --force --database-only backup.tar.gz

EOF
}

# 检查备份文件
check_backup_file() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "备份文件不存在: $backup_file"
        exit 1
    fi
    
    if ! tar -tzf "$backup_file" > /dev/null 2>&1; then
        log_error "备份文件格式错误或已损坏: $backup_file"
        exit 1
    fi
    
    log_success "备份文件验证通过: $backup_file"
}

# 停止服务
stop_services() {
    log_warning "停止AIOps服务..."
    docker-compose down
    log_success "服务已停止"
}

# 恢复存储卷
restore_volumes() {
    local backup_dir="$1"
    
    log_info "恢复Docker存储卷..."
    
    local volumes_dir="$backup_dir/volumes"
    
    if [ ! -d "$volumes_dir" ]; then
        log_warning "备份中未找到存储卷数据"
        return 0
    fi
    
    for volume_backup in "$volumes_dir"/*.tar.gz; do
        if [ -f "$volume_backup" ]; then
            local volume_name
            volume_name=$(basename "$volume_backup" .tar.gz)
            
            log_info "恢复存储卷: $volume_name"
            
            # 删除现有卷
            docker volume rm "$volume_name" 2>/dev/null || true
            
            # 创建新卷
            docker volume create "$volume_name"
            
            # 恢复数据
            docker run --rm \
                -v "$volume_name:/data" \
                -v "$volumes_dir:/backup:ro" \
                alpine:latest \
                tar xzf "/backup/$(basename "$volume_backup")" -C /data
            
            log_success "存储卷恢复完成: $volume_name"
        fi
    done
}

# 恢复配置文件
restore_configs() {
    local backup_dir="$1"
    
    log_info "恢复配置文件..."
    
    local configs_dir="$backup_dir/configs"
    
    if [ ! -d "$configs_dir" ]; then
        log_warning "备份中未找到配置文件"
        return 0
    fi
    
    # 备份当前配置
    if [ -d "configs" ]; then
        mv configs "configs.backup.$(date +%s)"
        log_info "当前配置已备份"
    fi
    
    # 恢复配置文件
    cp -r "$configs_dir"/* .
    
    log_success "配置文件恢复完成"
}

# 恢复数据库
restore_database() {
    local backup_dir="$1"
    
    log_info "恢复PostgreSQL数据库..."
    
    local database_dir="$backup_dir/database"
    
    if [ ! -d "$database_dir" ]; then
        log_warning "备份中未找到数据库文件"
        return 0
    fi
    
    # 查找数据库备份文件
    local db_backup
    db_backup=$(find "$database_dir" -name "*.sql.gz" | head -1)
    
    if [ -z "$db_backup" ]; then
        log_warning "未找到数据库备份文件"
        return 0
    fi
    
    # 启动数据库服务
    docker-compose up -d postgres
    
    # 等待数据库就绪
    log_info "等待数据库服务启动..."
    sleep 30
    
    # 恢复数据库
    local db_container
    db_container=$(docker-compose ps -q postgres)
    
    if [ -n "$db_container" ]; then
        zcat "$db_backup" | docker exec -i "$db_container" psql -U aiops
        log_success "数据库恢复完成"
    else
        log_error "数据库容器未运行"
        return 1
    fi
}

# 主恢复流程
main() {
    local backup_file="$1"
    local force=false
    local volumes_only=false
    local configs_only=false
    local database_only=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -f|--force)
                force=true
                shift
                ;;
            -v|--volumes-only)
                volumes_only=true
                shift
                ;;
            -c|--configs-only)
                configs_only=true
                shift
                ;;
            -d|--database-only)
                database_only=true
                shift
                ;;
            -*)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
            *)
                backup_file="$1"
                shift
                ;;
        esac
    done
    
    if [ -z "$backup_file" ]; then
        log_error "请指定备份文件"
        show_help
        exit 1
    fi
    
    # 检查备份文件
    check_backup_file "$backup_file"
    
    # 确认恢复操作
    if [ "$force" != "true" ]; then
        echo -e "${YELLOW}⚠️ 警告: 恢复操作将覆盖现有数据！${NC}"
        read -p "确定要继续吗？(y/N): " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "恢复操作已取消"
            exit 0
        fi
    fi
    
    # 创建临时目录
    local temp_dir
    temp_dir=$(mktemp -d)
    
    log_info "解压备份文件到临时目录: $temp_dir"
    tar xzf "$backup_file" -C "$temp_dir"
    
    local backup_dir
    backup_dir=$(find "$temp_dir" -maxdepth 1 -type d | tail -1)
    
    # 切换到项目目录
    cd "$(dirname "$0")/.."
    
    # 执行恢复操作
    if [ "$volumes_only" = "true" ]; then
        stop_services
        restore_volumes "$backup_dir"
    elif [ "$configs_only" = "true" ]; then
        restore_configs "$backup_dir"
    elif [ "$database_only" = "true" ]; then
        restore_database "$backup_dir"
    else
        # 完整恢复
        stop_services
        restore_volumes "$backup_dir"
        restore_configs "$backup_dir"
        restore_database "$backup_dir"
    fi
    
    # 启动服务
    if [ "$configs_only" != "true" ]; then
        log_info "启动AIOps服务..."
        docker-compose up -d
        
        # 等待服务启动
        sleep 30
        
        # 检查服务状态
        docker-compose ps
    fi
    
    # 清理临时文件
    rm -rf "$temp_dir"
    
    log_success "AIOps数据恢复完成！"
}

# 错误处理
trap 'log_error "恢复过程中发生错误"; exit 1' ERR

# 执行主流程
main "$@"
```

---

## 附录

### A. 模块依赖关系
```
AIOps平台模块依赖图:

┌─────────────────┐    ┌─────────────────┐
│   Traefik       │────│   API Gateway   │
│  (反向代理)      │    │   (API网关)     │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Grafana       │    │   AI Engine     │
│  (监控仪表板)    │    │   (AI引擎)      │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Prometheus     │    │ Self-Healing    │
│  (指标收集)      │    │  (自愈系统)     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────┬───────────────┘
                 ▼
┌─────────────────┐    ┌─────────────────┐
│  PostgreSQL     │    │     Redis       │
│   (数据库)      │    │    (缓存)       │
└─────────────────┘    └─────────────────┘
```

### B. 环境变量说明
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| POSTGRES_DB | aiops | PostgreSQL数据库名 |
| POSTGRES_USER | aiops | PostgreSQL用户名 |
| POSTGRES_PASSWORD | - | PostgreSQL密码 |
| REDIS_PASSWORD | - | Redis密码 |
| GRAFANA_ADMIN_PASSWORD | - | Grafana管理员密码 |
| AI_MODEL_PATH | /app/models | AI模型存储路径 |
| PROMETHEUS_RETENTION | 30d | Prometheus数据保留期 |
| TRAEFIK_DOMAIN | aiops.local | Traefik域名 |
| SSL_ENABLED | false | 是否启用SSL |
| JWT_SECRET | - | JWT密钥 |

### C. 端口映射表
| 服务 | 内部端口 | 外部端口 | 协议 | 说明 |
|------|----------|----------|------|------|
| Traefik | 80, 443 | 80, 443 | HTTP/HTTPS | 反向代理 |
| Grafana | 3000 | 3000 | HTTP | 监控仪表板 |
| Prometheus | 9090 | 9090 | HTTP | 指标收集 |
| API Gateway | 8080 | 8080 | HTTP | API服务 |
| AI Engine | 8000 | 8000 | HTTP | AI服务 |
| Self-Healing | 8001 | 8001 | HTTP | 自愈系统 |
| PostgreSQL | 5432 | - | TCP | 数据库 |
| Redis | 6379 | - | TCP | 缓存 |
| Node Exporter | 9100 | 9100 | HTTP | 系统指标 |
| cAdvisor | 8081 | 8081 | HTTP | 容器指标 |

### D. 技术支持
- **文档**: https://docs.aiops.local
- **问题反馈**: https://github.com/your-org/aiops/issues
- **社区论坛**: https://community.aiops.local
- **邮件支持**: support@aiops.local

---

*本文档最后更新: 2025-01-09*
*适用版本: AIOps v3.0.0*
*操作系统: Linux (Ubuntu/CentOS/RHEL/Debian)*