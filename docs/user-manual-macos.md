# AIOps智能运维平台用户手册 - macOS版

## 目录

1. [系统概述](#1-系统概述)
2. [环境准备](#2-环境准备)
3. [快速开始](#3-快速开始)
4. [详细安装指南](#4-详细安装指南)
5. [Shell脚本工具](#5-shell脚本工具)
6. [macOS特定配置](#6-macos特定配置)
7. [服务管理](#7-服务管理)
8. [监控和告警](#8-监控和告警)
9. [故障排除](#9-故障排除)
10. [性能优化](#10-性能优化)
11. [安全配置](#11-安全配置)
12. [备份和恢复](#12-备份和恢复)
13. [附录](#13-附录)

---

## 1. 系统概述

### 1.1 简介

AIOps智能运维平台是一个基于Docker容器化的现代化运维解决方案，专为macOS环境优化。平台集成了监控、告警、自愈、AI分析等核心功能，为macOS用户提供完整的运维自动化体验。

### 1.2 核心功能

- **智能监控**: 基于Prometheus + Grafana的全方位监控
- **自动告警**: 多渠道告警通知（邮件、Slack、钉钉等）
- **自愈系统**: 基于规则和AI的自动故障修复
- **AI分析**: 智能日志分析和异常检测
- **可视化**: 丰富的仪表板和报表
- **API网关**: 统一的服务入口和认证

### 1.3 架构组件

```
┌─────────────────────────────────────────────────────────────┐
│                    AIOps Platform - macOS                  │
├─────────────────────────────────────────────────────────────┤
│  Frontend Layer                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Grafana   │  │   Traefik   │  │  Dashboard  │        │
│  │  (监控面板)  │  │ (负载均衡器) │  │  (管理界面)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Application Layer                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ AI Engine   │  │Self-Healing │  │ API Gateway │        │
│  │ (AI分析引擎) │  │ (自愈系统)   │  │ (API网关)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Monitoring Layer                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Prometheus  │  │ Alertmanager│  │ Node Exporter│       │
│  │ (指标收集)   │  │ (告警管理)   │  │ (系统监控)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │    Redis    │  │ Docker Vols │        │
│  │ (主数据库)   │  │ (缓存/队列)  │  │ (存储卷)    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## 2. 环境准备

### 2.1 系统要求

#### 硬件要求
- **CPU**: Intel i5 或 Apple Silicon M1/M2 及以上
- **内存**: 8GB RAM (推荐16GB)
- **存储**: 50GB可用磁盘空间
- **网络**: 稳定的互联网连接

#### 软件要求
- **操作系统**: macOS 10.15 (Catalina) 或更高版本
- **Docker Desktop**: 4.0+ for Mac
- **Git**: 2.30+
- **Homebrew**: 最新版本
- **Zsh/Bash**: macOS默认Shell

### 2.2 Docker Desktop安装

```bash
#!/bin/bash
# install-docker.sh - Docker Desktop安装脚本

echo "🐳 开始安装Docker Desktop for Mac..."

# 检查是否已安装Homebrew
if ! command -v brew &> /dev/null; then
    echo "📦 安装Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# 使用Homebrew安装Docker Desktop
echo "📥 通过Homebrew安装Docker Desktop..."
brew install --cask docker

# 启动Docker Desktop
echo "🚀 启动Docker Desktop..."
open /Applications/Docker.app

# 等待Docker启动
echo "⏳ 等待Docker启动..."
while ! docker info &> /dev/null; do
    echo "等待Docker启动中..."
    sleep 5
done

echo "✅ Docker Desktop安装完成!"
docker --version
docker-compose --version
```

### 2.3 开发工具安装

```bash
#!/bin/bash
# install-tools.sh - 开发工具安装脚本

echo "🛠️ 安装开发工具..."

# 安装Git (如果未安装)
if ! command -v git &> /dev/null; then
    echo "📦 安装Git..."
    brew install git
fi

# 安装jq (JSON处理工具)
if ! command -v jq &> /dev/null; then
    echo "📦 安装jq..."
    brew install jq
fi

# 安装curl (如果未安装)
if ! command -v curl &> /dev/null; then
    echo "📦 安装curl..."
    brew install curl
fi

# 安装htop (系统监控)
if ! command -v htop &> /dev/null; then
    echo "📦 安装htop..."
    brew install htop
fi

# 安装watch (命令监控)
if ! command -v watch &> /dev/null; then
    echo "📦 安装watch..."
    brew install watch
fi

echo "✅ 开发工具安装完成!"
```

### 2.4 网络配置

```bash
#!/bin/bash
# configure-network.sh - 网络配置脚本

echo "🌐 配置网络设置..."

# 添加本地域名解析
echo "📝 配置本地域名解析..."
sudo tee -a /etc/hosts > /dev/null <<EOF

# AIOps Platform - macOS
127.0.0.1 aiops.local
127.0.0.1 grafana.aiops.local
127.0.0.1 prometheus.aiops.local
127.0.0.1 traefik.aiops.local
EOF

# 配置Docker网络
echo "🐳 配置Docker网络..."
docker network create aiops-network 2>/dev/null || echo "网络已存在"

echo "✅ 网络配置完成!"
echo "📋 可用域名:"
echo "   • http://aiops.local - 主界面"
echo "   • http://grafana.aiops.local - Grafana仪表板"
echo "   • http://prometheus.aiops.local - Prometheus监控"
echo "   • http://traefik.aiops.local - Traefik管理界面"
```

## 3. 快速开始

### 3.1 获取源码

```bash
# 克隆项目
git clone https://github.com/your-org/aiops.git
cd aiops

# 检查项目结构
ls -la
tree -L 2  # 如果安装了tree命令
```

### 3.2 一键部署脚本

```bash
#!/bin/bash
# deploy-aiops.sh - AIOps一键部署脚本 (macOS版)

set -e  # 遇到错误立即退出

# 参数解析
SKIP_PRECHECK=false
USE_LOCAL_VOLUMES=false
ENVIRONMENT="production"

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-precheck)
            SKIP_PRECHECK=true
            shift
            ;;
        --use-local-volumes)
            USE_LOCAL_VOLUMES=true
            shift
            ;;
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 颜色输出函数
function print_color() {
    local color=$1
    local message=$2
    case $color in
        "red") echo -e "\033[31m$message\033[0m" ;;
        "green") echo -e "\033[32m$message\033[0m" ;;
        "yellow") echo -e "\033[33m$message\033[0m" ;;
        "blue") echo -e "\033[34m$message\033[0m" ;;
        "cyan") echo -e "\033[36m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# 检查先决条件
function check_prerequisites() {
    print_color "cyan" "🔍 检查系统先决条件..."
    
    local errors=()
    
    # 检查Docker
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version)
        print_color "green" "✅ Docker: $docker_version"
    else
        errors+=("Docker未安装")
    fi
    
    # 检查Docker Compose
    if command -v docker-compose &> /dev/null; then
        local compose_version=$(docker-compose --version)
        print_color "green" "✅ Docker Compose: $compose_version"
    else
        errors+=("Docker Compose未安装")
    fi
    
    # 检查Git
    if command -v git &> /dev/null; then
        local git_version=$(git --version)
        print_color "green" "✅ Git: $git_version"
    else
        errors+=("Git未安装")
    fi
    
    # 检查磁盘空间
    local free_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
    if (( $(echo "$free_space < 10" | bc -l) )); then
        errors+=("磁盘空间不足，需要至少10GB可用空间，当前可用: ${free_space}GB")
    else
        print_color "green" "✅ 磁盘空间: ${free_space}GB 可用"
    fi
    
    # 检查内存
    local total_memory=$(sysctl -n hw.memsize | awk '{print int($1/1024/1024/1024)}')
    if (( total_memory < 8 )); then
        errors+=("内存不足，需要至少8GB内存，当前: ${total_memory}GB")
    else
        print_color "green" "✅ 系统内存: ${total_memory}GB"
    fi
    
    # 检查Docker是否运行
    if ! docker info &> /dev/null; then
        errors+=("Docker未运行，请启动Docker Desktop")
    else
        print_color "green" "✅ Docker服务运行正常"
    fi
    
    if [ ${#errors[@]} -gt 0 ]; then
        print_color "red" "❌ 发现以下问题:"
        for error in "${errors[@]}"; do
            print_color "red" "   - $error"
        done
        return 1
    fi
    
    return 0
}

# 创建环境配置文件
function create_env_file() {
    print_color "cyan" "📝 创建环境配置文件..."
    
    cat > .env << EOF
# AIOps平台环境配置 - macOS

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Redis配置
REDIS_PASSWORD=$(openssl rand -base64 32)

# Grafana配置
GF_SECURITY_ADMIN_PASSWORD=$(openssl rand -base64 16)
GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource

# JWT密钥
JWT_SECRET=$(openssl rand -base64 64)

# 域名配置
TRAEFIK_DOMAIN=aiops.local

# SSL配置
SSL_ENABLED=false

# 存储配置
EOF
    
    if [ "$USE_LOCAL_VOLUMES" = true ]; then
        cat >> .env << EOF

# 本地存储路径
DATA_PATH=/Users/$(whoami)/aiops-data
LOGS_PATH=/Users/$(whoami)/aiops-logs
BACKUPS_PATH=/Users/$(whoami)/aiops-backups
EOF
    fi
    
    print_color "green" "✅ 环境配置文件已创建"
}

# 启动服务
function start_services() {
    print_color "cyan" "🚀 启动AIOps服务..."
    
    local services=(
        "postgres"
        "redis"
        "traefik"
        "prometheus"
        "grafana"
        "ai-engine"
        "self-healing"
        "api-gateway"
    )
    
    for service in "${services[@]}"; do
        print_color "yellow" "🔄 启动服务: $service"
        if docker-compose up -d "$service"; then
            print_color "green" "✅ 服务启动成功: $service"
        else
            print_color "red" "❌ 服务启动失败: $service"
            return 1
        fi
        
        # 等待服务启动
        sleep 10
    done
    
    return 0
}

# 主函数
function main() {
    print_color "cyan" "🚀 开始部署AIOps平台 (macOS版)"
    print_color "yellow" "环境: $ENVIRONMENT"
    
    # 检查先决条件
    if [ "$SKIP_PRECHECK" = false ]; then
        if ! check_prerequisites; then
            print_color "red" "❌ 先决条件检查失败，请解决上述问题后重试"
            exit 1
        fi
    fi
    
    # 创建配置文件
    create_env_file
    
    # 拉取镜像
    print_color "cyan" "📥 拉取Docker镜像..."
    docker-compose pull
    
    # 启动服务
    if ! start_services; then
        print_color "red" "❌ 服务启动失败"
        exit 1
    fi
    
    # 等待服务完全启动
    print_color "yellow" "⏳ 等待服务完全启动..."
    sleep 30
    
    print_color "green" "🎉 AIOps平台部署完成！"
    print_color "cyan" "📊 访问地址:"
    print_color "white" "   • Grafana仪表板: http://localhost:3000"
    print_color "white" "   • Prometheus监控: http://localhost:9090"
    print_color "white" "   • API网关: http://localhost:8080"
    print_color "white" "   • Traefik管理: http://localhost:8080/dashboard/"
}

# 执行主函数
main "$@"
```

### 3.3 运行部署

```bash
# 标准部署（使用Docker卷）
./deploy-aiops.sh

# 使用本地存储卷部署
./deploy-aiops.sh --use-local-volumes

# 跳过先决条件检查
./deploy-aiops.sh --skip-precheck

# 指定环境
./deploy-aiops.sh --environment development
```

### 3.4 验证部署

```bash
#!/bin/bash
# verify-deployment.sh - 验证部署状态

function verify_aiops_deployment() {
    print_color "cyan" "🔍 验证AIOps平台部署状态"
    
    local services=(
        "Traefik:http://localhost:8080/dashboard/:8080"
        "Grafana:http://localhost:3000:3000"
        "Prometheus:http://localhost:9090:9090"
        "API Gateway:http://localhost:8000/health:8000"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r name url port <<< "$service_info"
        
        if curl -s --max-time 10 "$url" > /dev/null; then
            print_color "green" "✅ $name: 运行正常"
        else
            print_color "red" "❌ $name: 无法访问 ($url)"
        fi
    done
    
    # 检查Docker容器状态
    print_color "cyan" "\n📊 Docker容器状态:"
    docker-compose ps
}

# 运行验证
verify_aiops_deployment
```

## 4. 详细安装指南

### 4.1 环境变量配置

创建详细的 `.env` 配置文件：

```bash
# ===========================================
# AIOps平台环境配置文件 - macOS版本
# ===========================================

# 基础配置
COMPOSE_PROJECT_NAME=aiops
ENVIRONMENT=production

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here
REDIS_DB=0

# Grafana配置
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=your_grafana_password_here
GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource,grafana-piechart-panel
GF_SECURITY_ALLOW_EMBEDDING=true

# Prometheus配置
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_STORAGE_RETENTION_SIZE=10GB

# Traefik配置
TRAEFIK_DOMAIN=aiops.local
TRAEFIK_API_DASHBOARD=true
TRAEFIK_LOG_LEVEL=INFO

# SSL/TLS配置
SSL_ENABLED=false
SSL_CERT_PATH=./certs/cert.pem
SSL_KEY_PATH=./certs/key.pem

# JWT配置
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRATION=24h

# AI引擎配置
AI_ENGINE_MODEL_PATH=/app/models
AI_ENGINE_LOG_LEVEL=INFO
AI_ENGINE_MAX_WORKERS=4

# 自愈系统配置
SELF_HEALING_ENABLED=true
SELF_HEALING_CHECK_INTERVAL=30s
SELF_HEALING_MAX_RETRIES=3

# 监控配置
MONITORING_RETENTION_DAYS=30
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook

# 日志配置
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_MAX_SIZE=100MB
LOG_MAX_FILES=10

# 存储配置（可选：本地持久化）
# 取消注释以下行以启用本地存储
# DATA_PATH=/Users/$(whoami)/aiops-data
# LOGS_PATH=/Users/$(whoami)/aiops-logs
# BACKUPS_PATH=/Users/$(whoami)/aiops-backups
# CONFIG_PATH=/Users/$(whoami)/aiops-config
```

## 5. Shell脚本工具

### 5.1 服务管理脚本

```bash
#!/bin/bash
# manage-aiops.sh - AIOps服务管理脚本

set -e

# 参数解析
ACTION=""
SERVICE="all"
FOLLOW=false

while [[ $# -gt 0 ]]; do
    case $1 in
        start|stop|restart|status|logs|update)
            ACTION="$1"
            shift
            ;;
        --service)
            SERVICE="$2"
            shift 2
            ;;
        --follow)
            FOLLOW=true
            shift
            ;;
        *)
            echo "用法: $0 {start|stop|restart|status|logs|update} [--service SERVICE] [--follow]"
            exit 1
            ;;
    esac
done

if [ -z "$ACTION" ]; then
    echo "错误: 必须指定操作 (start|stop|restart|status|logs|update)"
    exit 1
fi

# 颜色输出函数
function print_color() {
    local color=$1
    local message=$2
    case $color in
        "red") echo -e "\033[31m$message\033[0m" ;;
        "green") echo -e "\033[32m$message\033[0m" ;;
        "yellow") echo -e "\033[33m$message\033[0m" ;;
        "blue") echo -e "\033[34m$message\033[0m" ;;
        "cyan") echo -e "\033[36m$message\033[0m" ;;
        "magenta") echo -e "\033[35m$message\033[0m" ;;
        *) echo "$message" ;;
    esac
}

# 服务管理函数
function manage_service() {
    case $ACTION in
        "start")
            print_color "green" "🚀 启动服务: $SERVICE"
            if [ "$SERVICE" = "all" ]; then
                docker-compose up -d
            else
                docker-compose up -d "$SERVICE"
            fi
            ;;
        "stop")
            print_color "yellow" "🛑 停止服务: $SERVICE"
            if [ "$SERVICE" = "all" ]; then
                docker-compose down
            else
                docker-compose stop "$SERVICE"
            fi
            ;;
        "restart")
            print_color "cyan" "🔄 重启服务: $SERVICE"
            if [ "$SERVICE" = "all" ]; then
                docker-compose restart
            else
                docker-compose restart "$SERVICE"
            fi
            ;;
        "status")
            print_color "cyan" "📊 服务状态:"
            docker-compose ps
            ;;
        "logs")
            print_color "magenta" "📋 查看日志: $SERVICE"
            if [ "$FOLLOW" = true ]; then
                docker-compose logs -f "$SERVICE"
            else
                docker-compose logs --tail=100 "$SERVICE"
            fi
            ;;
        "update")
            print_color "blue" "⬆️ 更新服务: $SERVICE"
            docker-compose pull "$SERVICE"
            docker-compose up -d "$SERVICE"
            ;;
    esac
}

# 执行操作
manage_service
```

使用示例：

```bash
# 启动所有服务
./manage-aiops.sh start

# 重启特定服务
./manage-aiops.sh restart --service grafana

# 查看实时日志
./manage-aiops.sh logs --service prometheus --follow

# 检查服务状态
./manage-aiops.sh status
```

### 5.2 系统监控脚本

```bash
#!/bin/bash
# monitor-system.sh - macOS系统监控脚本

set -e

# 获取系统指标
function get_system_metrics() {
    print_color "cyan" "📊 收集系统指标..."
    
    # CPU使用率
    local cpu_usage=$(top -l 1 | grep "CPU usage" | awk '{print $3}' | sed 's/%//')
    
    # 内存使用情况
    local memory_info=$(vm_stat | grep -E "Pages (free|active|inactive|speculative|wired down)")
    local page_size=$(vm_stat | grep "page size" | awk '{print $8}')
    local free_pages=$(echo "$memory_info" | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    local active_pages=$(echo "$memory_info" | grep "Pages active" | awk '{print $3}' | sed 's/\.//')
    local inactive_pages=$(echo "$memory_info" | grep "Pages inactive" | awk '{print $3}' | sed 's/\.//')
    local wired_pages=$(echo "$memory_info" | grep "Pages wired down" | awk '{print $4}' | sed 's/\.//')
    
    local total_memory=$((($free_pages + $active_pages + $inactive_pages + $wired_pages) * $page_size / 1024 / 1024 / 1024))
    local used_memory=$((($active_pages + $inactive_pages + $wired_pages) * $page_size / 1024 / 1024 / 1024))
    local memory_usage=$(echo "scale=2; $used_memory * 100 / $total_memory" | bc)
    
    # 磁盘使用情况
    local disk_info=$(df -h / | tail -1)
    local disk_usage=$(echo "$disk_info" | awk '{print $5}' | sed 's/%//')
    
    # Docker容器状态
    local container_count=$(docker ps -q | wc -l | tr -d ' ')
    local running_containers=$(docker ps --filter "status=running" -q | wc -l | tr -d ' ')
    
    # 输出结果
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "{"
    echo "  \"timestamp\": \"$timestamp\","
    echo "  \"cpu_usage\": \"${cpu_usage}%\","
    echo "  \"memory_usage\": \"${memory_usage}% (${used_memory}GB / ${total_memory}GB)\","
    echo "  \"disk_usage\": \"${disk_usage}%\","
    echo "  \"container_count\": $container_count,"
    echo "  \"running_containers\": $running_containers"
    echo "}"
}

# 连续监控
function start_continuous_monitoring() {
    local interval=${1:-60}
    local log_file=${2:-"aiops-monitor.log"}
    
    print_color "green" "🔄 开始连续监控 (间隔: $interval 秒)"
    print_color "yellow" "📝 日志文件: $log_file"
    
    while true; do
        local metrics=$(get_system_metrics)
        
        # 控制台输出
        echo ""
        print_color "cyan" "=== $(date '+%H:%M:%S') ==="
        echo "$metrics" | jq -r 'to_entries[] | "\(.key): \(.value)"'
        
        # 写入日志文件
        echo "$(date '+%Y-%m-%d %H:%M:%S') - $metrics" >> "$log_file"
        
        # 检查告警条件
        local cpu_val=$(echo "$metrics" | jq -r '.cpu_usage' | sed 's/%//')
        local mem_val=$(echo "$metrics" | jq -r '.memory_usage' | cut -d'%' -f1)
        
        if (( $(echo "$cpu_val > 80" | bc -l) )); then
            print_color "red" "⚠️ CPU使用率过高: ${cpu_val}%"
        fi
        
        if (( $(echo "$mem_val > 85" | bc -l) )); then
            print_color "red" "⚠️ 内存使用率过高: ${mem_val}%"
        fi
        
        sleep "$interval"
    done
}

# 启动监控
start_continuous_monitoring 30
```

### 5.3 备份管理脚本

```bash
#!/bin/bash
# backup-aiops.sh - AIOps数据备份脚本

set -e

# 默认参数
BACKUP_PATH="$HOME/aiops-backups"
INCLUDE_VOLUMES=false
COMPRESS=false

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup-path)
            BACKUP_PATH="$2"
            shift 2
            ;;
        --include-volumes)
            INCLUDE_VOLUMES=true
            shift
            ;;
        --compress)
            COMPRESS=true
            shift
            ;;
        *)
            echo "用法: $0 [--backup-path PATH] [--include-volumes] [--compress]"
            exit 1
            ;;
    esac
done

function create_aiops_backup() {
    local timestamp=$(date '+%Y%m%d-%H%M%S')
    local backup_dir="$BACKUP_PATH/aiops-backup-$timestamp"
    
    print_color "cyan" "💾 开始备份AIOps数据..."
    print_color "yellow" "📁 备份目录: $backup_dir"
    
    # 创建备份目录
    mkdir -p "$backup_dir"
    
    # 1. 备份配置文件
    print_color "green" "📋 备份配置文件..."
    local config_files=(".env" "docker-compose.yml" "prometheus.yml" "grafana.ini")
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$backup_dir/"
            print_color "green" "✅ 已备份: $file"
        fi
    done
    
    # 2. 备份数据库
    print_color "green" "🗄️ 备份PostgreSQL数据库..."
    local db_backup_file="$backup_dir/postgres-backup.sql"
    docker-compose exec -T postgres pg_dumpall -U aiops > "$db_backup_file"
    
    # 3. 备份Grafana仪表板
    print_color "green" "📊 备份Grafana配置..."
    local grafana_backup="$backup_dir/grafana-backup.json"
    # 这里可以添加Grafana API调用来备份仪表板
    
    # 4. 备份Docker卷（可选）
    if [ "$INCLUDE_VOLUMES" = true ]; then
        print_color "green" "💿 备份Docker存储卷..."
        local volumes_dir="$backup_dir/volumes"
        mkdir -p "$volumes_dir"
        
        local volumes=$(docker volume ls --format "{{.Name}}" | grep "aiops")
        for volume in $volumes; do
            local volume_backup="$volumes_dir/$volume.tar.gz"
            docker run --rm -v "$volume:/data" -v "$volumes_dir:/backup" alpine tar czf "/backup/$volume.tar.gz" -C /data .
            print_color "green" "✅ 已备份卷: $volume"
        done
    fi
    
    # 5. 压缩备份（可选）
    if [ "$COMPRESS" = true ]; then
        print_color "green" "🗜️ 压缩备份文件..."
        local zip_file="$backup_dir.tar.gz"
        tar czf "$zip_file" -C "$BACKUP_PATH" "$(basename "$backup_dir")"
        rm -rf "$backup_dir"
        print_color "green" "✅ 备份已压缩: $zip_file"
    fi
    
    print_color "green" "🎉 备份完成!"
}

# 执行备份
create_aiops_backup
```

## 6. macOS特定配置

### 6.1 系统集成配置

```bash
#!/bin/bash
# configure-macos.sh - macOS系统集成配置

function configure_launchd_service() {
    print_color "cyan" "🔧 配置macOS系统服务..."
    
    # 创建LaunchAgent配置
    local plist_file="$HOME/Library/LaunchAgents/com.aiops.platform.plist"
    
    cat > "$plist_file" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aiops.platform</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/docker-compose</string>
        <string>-f</string>
        <string>$(pwd)/docker-compose.yml</string>
        <string>up</string>
        <string>-d</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$(pwd)</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/aiops-platform.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/aiops-platform-error.log</string>
</dict>
</plist>
EOF
    
    # 加载服务
    launchctl load "$plist_file"
    print_color "green" "✅ macOS系统服务已配置"
}

# 配置Spotlight搜索排除
function configure_spotlight() {
    print_color "cyan" "🔍 配置Spotlight搜索排除..."
    
    # 排除Docker数据目录
    local docker_data_dir="$HOME/Library/Containers/com.docker.docker/Data"
    if [ -d "$docker_data_dir" ]; then
        sudo mdutil -i off "$docker_data_dir"
        print_color "green" "✅ 已排除Docker数据目录"
    fi
    
    # 排除备份目录
    if [ -d "$HOME/aiops-backups" ]; then
        sudo mdutil -i off "$HOME/aiops-backups"
        print_color "green" "✅ 已排除备份目录"
    fi
}

# 配置防火墙
function configure_firewall() {
    print_color "cyan" "🔥 配置macOS防火墙..."
    
    # 启用防火墙
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
    
    # 允许Docker Desktop
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add /Applications/Docker.app/Contents/MacOS/Docker
    sudo /usr/libexec/ApplicationFirewall/socketfilterfw --unblockapp /Applications/Docker.app/Contents/MacOS/Docker
    
    print_color "green" "✅ 防火墙配置完成"
}

# 执行配置
configure_launchd_service
configure_spotlight
configure_firewall
```

### 6.2 网络配置

```bash
#!/bin/bash
# configure-network.sh - macOS网络配置脚本

function configure_hosts() {
    print_color "cyan" "🌐 配置本地域名解析..."
    
    # 备份hosts文件
    sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d)
    
    # 添加AIOps域名解析
    local hosts_entries=(
        "127.0.0.1 aiops.local"
        "127.0.0.1 grafana.aiops.local"
        "127.0.0.1 prometheus.aiops.local"
        "127.0.0.1 traefik.aiops.local"
    )
    
    for entry in "${hosts_entries[@]}"; do
        if ! grep -q "$entry" /etc/hosts; then
            echo "$entry" | sudo tee -a /etc/hosts > /dev/null
            print_color "green" "✅ 已添加: $entry"
        fi
    done
}

# 配置端口转发
function configure_port_forwarding() {
    print_color "cyan" "🔀 配置端口转发..."
    
    # 创建端口转发规则
    local pf_rules="/tmp/aiops-pf.conf"
    
    cat > "$pf_rules" << EOF
# AIOps平台端口转发规则
rdr pass on lo0 inet proto tcp from any to 127.0.0.1 port 80 -> 127.0.0.1 port 8080
rdr pass on lo0 inet proto tcp from any to 127.0.0.1 port 443 -> 127.0.0.1 port 8443
EOF
    
    # 加载规则（需要管理员权限）
    sudo pfctl -f "$pf_rules"
    print_color "green" "✅ 端口转发规则已配置"
}

configure_hosts
configure_port_forwarding
```

## 7. 服务管理

### 7.1 启动顺序管理

```bash
#!/bin/bash
# startup-sequence.sh - 服务启动顺序管理

function start_services_in_order() {
    print_color "cyan" "🚀 按顺序启动服务..."
    
    # 定义启动顺序
    local services=(
        "postgres:数据库服务"
        "redis:缓存服务"
        "prometheus:监控数据收集"
        "grafana:监控仪表板"
        "ai-engine:AI引擎"
        "self-healing:自愈系统"
        "traefik:API网关"
    )
    
    for service_info in "${services[@]}"; do
        local service=$(echo "$service_info" | cut -d':' -f1)
        local description=$(echo "$service_info" | cut -d':' -f2)
        
        print_color "yellow" "🔄 启动 $service ($description)..."
        
        # 启动服务
        docker-compose up -d "$service"
        
        # 等待服务就绪
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if docker-compose ps "$service" | grep -q "Up"; then
                print_color "green" "✅ $service 启动成功"
                break
            fi
            
            print_color "cyan" "⏳ 等待 $service 启动... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        done
        
        if [ $attempt -gt $max_attempts ]; then
            print_color "red" "❌ $service 启动超时"
            return 1
        fi
        
        # 服务间启动间隔
        sleep 3
    done
    
    print_color "green" "🎉 所有服务启动完成!"
}

start_services_in_order
```

### 7.2 健康检查

```bash
#!/bin/bash
# health-check.sh - 服务健康检查脚本

function check_service_health() {
    local service=$1
    local endpoint=$2
    local expected_status=${3:-200}
    
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$endpoint" 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        print_color "green" "✅ $service: 健康 (HTTP $response)"
        return 0
    else
        print_color "red" "❌ $service: 异常 (HTTP $response)"
        return 1
    fi
}

function run_health_checks() {
    print_color "cyan" "🏥 执行健康检查..."
    
    local failed_services=()
    
    # 检查各服务健康状态
    local services=(
        "Grafana:http://localhost:3000/api/health"
        "Prometheus:http://localhost:9090/-/healthy"
        "Traefik:http://localhost:8080/ping"
    )
    
    for service_info in "${services[@]}"; do
        local service=$(echo "$service_info" | cut -d':' -f1)
        local endpoint=$(echo "$service_info" | cut -d':' -f2)
        
        if ! check_service_health "$service" "$endpoint"; then
            failed_services+=("$service")
        fi
    done
    
    # 检查Docker容器状态
    print_color "cyan" "🐳 检查Docker容器状态..."
    local unhealthy_containers=$(docker-compose ps --filter "health=unhealthy" -q)
    
    if [ -n "$unhealthy_containers" ]; then
        print_color "red" "❌ 发现不健康的容器:"
        docker-compose ps --filter "health=unhealthy"
        failed_services+=("Docker容器")
    fi
    
    # 汇总结果
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_color "green" "🎉 所有服务健康!"
        return 0
    else
        print_color "red" "⚠️ 以下服务存在问题: ${failed_services[*]}"
        return 1
    fi
}

run_health_checks
```

## 8. 监控和告警

### 8.1 Grafana仪表板配置

```bash
#!/bin/bash
# setup-grafana-dashboards.sh - Grafana仪表板自动配置

function import_dashboards() {
    print_color "cyan" "📊 导入Grafana仪表板..."
    
    local grafana_url="http://localhost:3000"
    local admin_user="admin"
    local admin_pass="admin"
    
    # 等待Grafana启动
    while ! curl -s "$grafana_url/api/health" > /dev/null; do
        print_color "yellow" "⏳ 等待Grafana启动..."
        sleep 5
    done
    
    # 导入系统监控仪表板
    local dashboard_json='{
        "dashboard": {
            "title": "AIOps系统监控",
            "panels": [
                {
                    "title": "CPU使用率",
                    "type": "graph",
                    "targets": [{
                        "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
                    }]
                },
                {
                    "title": "内存使用率",
                    "type": "graph", 
                    "targets": [{
                        "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
                    }]
                }
            ]
        },
        "overwrite": true
    }'
    
    # 导入仪表板
    curl -X POST \
        -H "Content-Type: application/json" \
        -d "$dashboard_json" \
        "$grafana_url/api/dashboards/db" \
        -u "$admin_user:$admin_pass"
    
    print_color "green" "✅ 仪表板导入完成"
}

import_dashboards
```

### 8.2 告警规则配置

```yaml
# alerts.yml - Prometheus告警规则
groups:
  - name: aiops-alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CPU使用率过高"
          description: "实例 {{ $labels.instance }} CPU使用率为 {{ $value }}%"
      
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "内存使用率过高"
          description: "实例 {{ $labels.instance }} 内存使用率为 {{ $value }}%"
      
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "服务不可用"
          description: "服务 {{ $labels.job }} 在实例 {{ $labels.instance }} 上不可用"
```

## 9. 故障排除

### 9.1 常见问题解决

```bash
#!/bin/bash
# troubleshoot.sh - 故障排除脚本

function diagnose_docker_issues() {
    print_color "cyan" "🔍 诊断Docker问题..."
    
    # 检查Docker Desktop状态
    if ! docker info > /dev/null 2>&1; then
        print_color "red" "❌ Docker未运行，请启动Docker Desktop"
        return 1
    fi
    
    # 检查Docker资源限制
    local docker_info=$(docker system info)
    local memory_limit=$(echo "$docker_info" | grep "Total Memory" | awk '{print $3}')
    local cpu_count=$(echo "$docker_info" | grep "CPUs" | awk '{print $2}')
    
    print_color "green" "✅ Docker状态正常"
    print_color "cyan" "💾 可用内存: $memory_limit"
    print_color "cyan" "🖥️ CPU核心数: $cpu_count"
    
    # 检查磁盘空间
    local disk_usage=$(docker system df)
    print_color "cyan" "💿 Docker磁盘使用情况:"
    echo "$disk_usage"
}

function fix_common_issues() {
    print_color "cyan" "🔧 修复常见问题..."
    
    # 清理Docker资源
    print_color "yellow" "🧹 清理Docker资源..."
    docker system prune -f
    docker volume prune -f
    
    # 重置网络
    print_color "yellow" "🌐 重置Docker网络..."
    docker network prune -f
    
    # 重启服务
    print_color "yellow" "🔄 重启AIOps服务..."
    docker-compose down
    sleep 5
    docker-compose up -d
    
    print_color "green" "✅ 常见问题修复完成"
}

function collect_debug_info() {
    local debug_file="aiops-debug-$(date +%Y%m%d-%H%M%S).log"
    
    print_color "cyan" "📋 收集调试信息..."
    
    {
        echo "=== AIOps调试信息 ==="
        echo "时间: $(date)"
        echo "系统: $(uname -a)"
        echo ""
        
        echo "=== Docker信息 ==="
        docker version
        echo ""
        docker info
        echo ""
        
        echo "=== 容器状态 ==="
        docker-compose ps
        echo ""
        
        echo "=== 容器日志 ==="
        docker-compose logs --tail=50
        echo ""
        
        echo "=== 系统资源 ==="
        top -l 1 | head -20
        echo ""
        df -h
        echo ""
        
        echo "=== 网络状态 ==="
        netstat -an | grep LISTEN
        
    } > "$debug_file"
    
    print_color "green" "✅ 调试信息已保存到: $debug_file"
}

# 执行诊断
diagnose_docker_issues
fix_common_issues
collect_debug_info
```

## 10. 性能优化

### 10.1 macOS系统优化

```bash
#!/bin/bash
# optimize-macos.sh - macOS系统优化脚本

function optimize_docker_settings() {
    print_color "cyan" "⚡ 优化Docker设置..."
    
    # Docker Desktop配置建议
    cat << EOF
📋 Docker Desktop优化建议:

1. 资源分配:
   - CPU: 至少4核心
   - 内存: 至少8GB
   - 磁盘: 至少50GB

2. 高级设置:
   - 启用 "Use gRPC FUSE for file sharing"
   - 启用 "Use Virtualization framework"
   - 启用 "Use Rosetta for x86/amd64 emulation on Apple Silicon"

3. 网络设置:
   - 使用 "Use kernel networking for UDP"

EOF
}

function optimize_system_settings() {
    print_color "cyan" "🔧 优化系统设置..."
    
    # 增加文件描述符限制
    echo "kern.maxfiles=65536" | sudo tee -a /etc/sysctl.conf
    echo "kern.maxfilesperproc=32768" | sudo tee -a /etc/sysctl.conf
    
    # 优化网络设置
    echo "net.inet.tcp.msl=1000" | sudo tee -a /etc/sysctl.conf
    
    # 应用设置
    sudo sysctl -p
    
    print_color "green" "✅ 系统设置优化完成"
}

optimize_docker_settings
optimize_system_settings
```

## 11. 安全配置

### 11.1 访问控制

```bash
#!/bin/bash
# security-setup.sh - 安全配置脚本

function setup_ssl_certificates() {
    print_color "cyan" "🔒 配置SSL证书..."
    
    local cert_dir="./certs"
    mkdir -p "$cert_dir"
    
    # 生成自签名证书
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$cert_dir/key.pem" \
        -out "$cert_dir/cert.pem" \
        -subj "/C=CN/ST=State/L=City/O=AIOps/CN=aiops.local"
    
    print_color "green" "✅ SSL证书生成完成"
}

function configure_access_control() {
    print_color "cyan" "🛡️ 配置访问控制..."
    
    # 创建访问控制配置
    cat > "traefik-auth.yml" << EOF
http:
  middlewares:
    auth:
      basicAuth:
        users:
          - "admin:$2y$10$..."
    secure-headers:
      headers:
        accessControlAllowMethods:
          - GET
          - OPTIONS
          - PUT
        accessControlAllowOriginList:
          - "https://aiops.local"
        accessControlMaxAge: 100
        hostsProxyHeaders:
          - "X-Forwarded-Host"
        sslRedirect: true
        stsSeconds: 31536000
        stsIncludeSubdomains: true
        stsPreload: true
EOF
    
    print_color "green" "✅ 访问控制配置完成"
}

setup_ssl_certificates
configure_access_control
```

## 12. 备份和恢复

### 12.1 自动备份配置

```bash
#!/bin/bash
# setup-auto-backup.sh - 自动备份配置

function setup_cron_backup() {
    print_color "cyan" "⏰ 配置定时备份..."
    
    # 创建备份脚本
    local backup_script="$HOME/bin/aiops-backup.sh"
    mkdir -p "$(dirname "$backup_script")"
    
    cat > "$backup_script" << 'EOF'
#!/bin/bash
cd /path/to/aiops
./backup-aiops.sh --compress --include-volumes
EOF
    
    chmod +x "$backup_script"
    
    # 添加到crontab
    (crontab -l 2>/dev/null; echo "0 2 * * * $backup_script") | crontab -
    
    print_color "green" "✅ 定时备份已配置 (每日2:00AM)"
}

setup_cron_backup
```

## 附录

### A. 端口映射表

| 服务 | 内部端口 | 外部端口 | 协议 | 描述 |
|------|----------|----------|------|------|
| Traefik | 80/443 | 8080/8443 | HTTP/HTTPS | API网关 |
| Grafana | 3000 | 3000 | HTTP | 监控仪表板 |
| Prometheus | 9090 | 9090 | HTTP | 监控数据收集 |
| PostgreSQL | 5432 | 5432 | TCP | 数据库 |
| Redis | 6379 | 6379 | TCP | 缓存 |

### B. 环境变量参考

详细的环境变量配置请参考 `.env` 文件示例。

### C. 技术支持

- 📧 邮箱: support@aiops.local
- 🐛 问题反馈: https://github.com/your-org/aiops/issues
- 📖 文档: https://docs.aiops.local

---

*本手册专为macOS系统优化，包含了macOS特有的配置和脚本。如需其他操作系统的手册，请参考对应的文档。*