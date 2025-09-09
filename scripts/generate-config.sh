#!/bin/bash

# AIOps平台配置生成脚本 (Bash)
#
# 描述:
#   本脚本用于根据环境参数和用户配置生成Docker Compose和Kubernetes配置文件。
#   支持自定义配置、环境变量替换、密钥生成等功能。
#
# 用法:
#   ./generate-config.sh --config-type docker-compose --environment development
#   ./generate-config.sh --config-type kubernetes --environment production --force
#
# 参数:
#   --config-type     配置类型：docker-compose 或 kubernetes 或 both
#   --environment     部署环境：development, staging, production
#   --output-path     输出路径，默认为项目根目录
#   --config-file     自定义配置文件路径
#   --force           强制覆盖已存在的配置文件
#   --help            显示帮助信息
#
# 版本: 1.0.0
# 作者: AIOps Team
# 创建日期: 2024-01-01

set -euo pipefail

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_TYPE=""
ENVIRONMENT="development"
OUTPUT_PATH=""
CONFIG_FILE=""
FORCE=false

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_debug() {
    echo -e "${GRAY}[DEBUG]${NC} $1"
}

# 显示帮助信息
show_help() {
    cat << EOF
AIOps平台配置生成工具

用法:
    $0 --config-type TYPE --environment ENV [OPTIONS]

参数:
    --config-type TYPE      配置类型 (docker-compose|kubernetes|both)
    --environment ENV       部署环境 (development|staging|production)
    --output-path PATH      输出路径 (默认: generated/ENV)
    --config-file FILE      自定义配置文件路径
    --force                 强制覆盖已存在的文件
    --help                  显示此帮助信息

示例:
    $0 --config-type docker-compose --environment development
    $0 --config-type kubernetes --environment production --force
    $0 --config-type both --environment staging --output-path /tmp/aiops

EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --config-type)
                CONFIG_TYPE="$2"
                shift 2
                ;;
            --environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --output-path)
                OUTPUT_PATH="$2"
                shift 2
                ;;
            --config-file)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 验证必需参数
    if [[ -z "$CONFIG_TYPE" ]]; then
        log_error "缺少必需参数: --config-type"
        show_help
        exit 1
    fi
    
    # 验证配置类型
    case "$CONFIG_TYPE" in
        docker-compose|kubernetes|both)
            ;;
        *)
            log_error "无效的配置类型: $CONFIG_TYPE"
            log_error "支持的类型: docker-compose, kubernetes, both"
            exit 1
            ;;
    esac
    
    # 验证环境
    case "$ENVIRONMENT" in
        development|staging|production)
            ;;
        *)
            log_error "无效的环境: $ENVIRONMENT"
            log_error "支持的环境: development, staging, production"
            exit 1
            ;;
    esac
}

# 生成随机密码
generate_password() {
    local length=${1:-32}
    local include_symbols=${2:-false}
    
    local chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    if [[ "$include_symbols" == "true" ]]; then
        chars+="!@#$%^&*"
    fi
    
    # 使用 /dev/urandom 生成随机密码
    tr -dc "$chars" < /dev/urandom | head -c "$length"
}

# 生成JWT密钥
generate_jwt_secret() {
    openssl rand -base64 32 2>/dev/null || generate_password 32
}

# 生成所有必需的密钥
initialize_secrets() {
    log_info "生成安全密钥..."
    
    # 创建关联数组存储密钥
    declare -gA GENERATED_SECRETS
    
    # 数据库密码
    GENERATED_SECRETS["postgres_password"]=$(generate_password 24)
    GENERATED_SECRETS["redis_password"]=$(generate_password 24)
    
    # Elasticsearch密码
    GENERATED_SECRETS["elastic_password"]=$(generate_password 24)
    GENERATED_SECRETS["kibana_password"]=$(generate_password 24)
    
    # Grafana密码
    GENERATED_SECRETS["grafana_admin_password"]=$(generate_password 16)
    
    # API密钥
    GENERATED_SECRETS["api_key"]=$(generate_password 32 true)
    GENERATED_SECRETS["jwt_secret"]=$(generate_jwt_secret)
    
    # Webhook密钥
    GENERATED_SECRETS["webhook_secret"]=$(generate_password 32)
    
    # SMTP配置（示例）
    GENERATED_SECRETS["smtp_password"]=$(generate_password 16)
    
    # Slack Webhook（占位符）
    GENERATED_SECRETS["slack_webhook_url"]="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    
    # Traefik Dashboard认证
    GENERATED_SECRETS["traefik_dashboard_user"]="admin"
    GENERATED_SECRETS["traefik_dashboard_password"]=$(generate_password 16)
    
    log_info "密钥生成完成"
}

# 加载默认配置
load_default_config() {
    # 创建临时JSON文件存储默认配置
    DEFAULT_CONFIG_FILE="/tmp/aiops-default-config-$$.json"
    
    cat > "$DEFAULT_CONFIG_FILE" << 'EOF'
{
  "project_name": "aiops",
  "namespace": "aiops",
  "domain": "aiops.local",
  "network": {
    "subnet": "172.20.0.0/16",
    "gateway": "172.20.0.1"
  },
  "services": {
    "traefik": {
      "enabled": true,
      "replicas": 1,
      "image": "traefik:v3.0",
      "ports": {
        "web": 80,
        "websecure": 443,
        "dashboard": 8080
      },
      "resources": {
        "requests": { "cpu": "100m", "memory": "128Mi" },
        "limits": { "cpu": "500m", "memory": "512Mi" }
      }
    },
    "prometheus": {
      "enabled": true,
      "replicas": 1,
      "image": "prom/prometheus:latest",
      "port": 9090,
      "retention": "15d",
      "storage_size": "50Gi",
      "resources": {
        "requests": { "cpu": "200m", "memory": "512Mi" },
        "limits": { "cpu": "1000m", "memory": "2Gi" }
      }
    },
    "grafana": {
      "enabled": true,
      "replicas": 1,
      "image": "grafana/grafana:latest",
      "port": 3000,
      "storage_size": "10Gi",
      "resources": {
        "requests": { "cpu": "100m", "memory": "256Mi" },
        "limits": { "cpu": "500m", "memory": "1Gi" }
      }
    },
    "alertmanager": {
      "enabled": true,
      "replicas": 1,
      "image": "prom/alertmanager:latest",
      "port": 9093,
      "storage_size": "5Gi",
      "resources": {
        "requests": { "cpu": "50m", "memory": "128Mi" },
        "limits": { "cpu": "200m", "memory": "512Mi" }
      }
    },
    "elasticsearch": {
      "enabled": true,
      "replicas": 3,
      "image": "docker.elastic.co/elasticsearch/elasticsearch:8.11.0",
      "port": 9200,
      "storage_size": "100Gi",
      "heap_size": "2g",
      "resources": {
        "requests": { "cpu": "500m", "memory": "2Gi" },
        "limits": { "cpu": "2000m", "memory": "4Gi" }
      }
    },
    "logstash": {
      "enabled": true,
      "replicas": 2,
      "image": "docker.elastic.co/logstash/logstash:8.11.0",
      "port": 5044,
      "heap_size": "1g",
      "resources": {
        "requests": { "cpu": "200m", "memory": "1Gi" },
        "limits": { "cpu": "1000m", "memory": "2Gi" }
      }
    },
    "kibana": {
      "enabled": true,
      "replicas": 1,
      "image": "docker.elastic.co/kibana/kibana:8.11.0",
      "port": 5601,
      "resources": {
        "requests": { "cpu": "200m", "memory": "512Mi" },
        "limits": { "cpu": "1000m", "memory": "2Gi" }
      }
    },
    "redis": {
      "enabled": true,
      "replicas": 1,
      "image": "redis:7-alpine",
      "port": 6379,
      "storage_size": "10Gi",
      "resources": {
        "requests": { "cpu": "100m", "memory": "256Mi" },
        "limits": { "cpu": "500m", "memory": "1Gi" }
      }
    },
    "postgresql": {
      "enabled": true,
      "replicas": 1,
      "image": "postgres:15-alpine",
      "port": 5432,
      "storage_size": "50Gi",
      "resources": {
        "requests": { "cpu": "200m", "memory": "512Mi" },
        "limits": { "cpu": "1000m", "memory": "2Gi" }
      }
    },
    "ai_engine": {
      "enabled": true,
      "replicas": 2,
      "image": "aiops/ai-engine:latest",
      "port": 8000,
      "resources": {
        "requests": { "cpu": "500m", "memory": "1Gi" },
        "limits": { "cpu": "2000m", "memory": "4Gi" }
      }
    },
    "api_gateway": {
      "enabled": true,
      "replicas": 2,
      "image": "aiops/api-gateway:latest",
      "port": 8080,
      "resources": {
        "requests": { "cpu": "200m", "memory": "512Mi" },
        "limits": { "cpu": "1000m", "memory": "2Gi" }
      }
    },
    "self_healing": {
      "enabled": true,
      "replicas": 1,
      "image": "aiops/self-healing:latest",
      "port": 8090,
      "resources": {
        "requests": { "cpu": "200m", "memory": "512Mi" },
        "limits": { "cpu": "1000m", "memory": "2Gi" }
      }
    }
  },
  "environments": {
    "development": {
      "debug": true,
      "log_level": "DEBUG",
      "replicas_multiplier": 1,
      "storage_class": "standard",
      "ingress_class": "traefik"
    },
    "staging": {
      "debug": false,
      "log_level": "INFO",
      "replicas_multiplier": 1,
      "storage_class": "fast-ssd",
      "ingress_class": "nginx"
    },
    "production": {
      "debug": false,
      "log_level": "WARN",
      "replicas_multiplier": 2,
      "storage_class": "fast-ssd",
      "ingress_class": "nginx"
    }
  }
}
EOF
}

# 加载自定义配置
load_custom_config() {
    local config_file="$1"
    
    if [[ -z "$config_file" ]]; then
        config_file="$PROJECT_ROOT/config/aiops-config.json"
    fi
    
    if [[ -f "$config_file" ]]; then
        log_info "加载自定义配置: $config_file"
        
        # 验证JSON格式
        if ! jq empty "$config_file" 2>/dev/null; then
            log_error "自定义配置文件格式错误: $config_file"
            return 1
        fi
        
        # 合并配置（这里简化处理，实际应该递归合并）
        jq -s '.[0] * .[1]' "$DEFAULT_CONFIG_FILE" "$config_file" > "${DEFAULT_CONFIG_FILE}.tmp"
        mv "${DEFAULT_CONFIG_FILE}.tmp" "$DEFAULT_CONFIG_FILE"
        
        log_info "自定义配置加载完成"
    else
        log_debug "未找到自定义配置文件，使用默认配置"
    fi
}

# 应用环境特定配置
apply_environment_config() {
    local env="$1"
    
    log_info "应用环境配置: $env"
    
    # 从配置中提取环境特定设置
    local env_config
    env_config=$(jq -r ".environments.\"$env\"" "$DEFAULT_CONFIG_FILE")
    
    if [[ "$env_config" == "null" ]]; then
        log_warn "未找到环境配置: $env"
        return 1
    fi
    
    # 提取环境配置值
    DEBUG=$(echo "$env_config" | jq -r '.debug')
    LOG_LEVEL=$(echo "$env_config" | jq -r '.log_level')
    STORAGE_CLASS=$(echo "$env_config" | jq -r '.storage_class')
    INGRESS_CLASS=$(echo "$env_config" | jq -r '.ingress_class')
    REPLICAS_MULTIPLIER=$(echo "$env_config" | jq -r '.replicas_multiplier')
    
    # 应用副本数乘数
    if [[ "$REPLICAS_MULTIPLIER" != "null" && "$REPLICAS_MULTIPLIER" -gt 1 ]]; then
        log_debug "应用副本数乘数: $REPLICAS_MULTIPLIER"
        
        # 更新配置文件中的副本数
        jq --argjson multiplier "$REPLICAS_MULTIPLIER" '
            .services |= with_entries(
                .value.replicas = ((.value.replicas // 1) * $multiplier | if . < 1 then 1 else . end)
            )
        ' "$DEFAULT_CONFIG_FILE" > "${DEFAULT_CONFIG_FILE}.tmp"
        mv "${DEFAULT_CONFIG_FILE}.tmp" "$DEFAULT_CONFIG_FILE"
    fi
    
    log_info "环境配置应用完成"
}

# 生成Docker Compose配置
generate_docker_compose_config() {
    local output_dir="$1"
    
    log_info "生成Docker Compose配置..."
    
    local compose_file="$output_dir/docker-compose.yml"
    local env_file="$output_dir/.env"
    
    # 生成.env文件
    cat > "$env_file" << EOF
# AIOps平台环境变量
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
# 环境: $ENVIRONMENT

# 项目配置
PROJECT_NAME=$(jq -r '.project_name' "$DEFAULT_CONFIG_FILE")
ENVIRONMENT=$ENVIRONMENT
DOMAIN=$(jq -r '.domain' "$DEFAULT_CONFIG_FILE")

# 网络配置
NETWORK_SUBNET=$(jq -r '.network.subnet' "$DEFAULT_CONFIG_FILE")
NETWORK_GATEWAY=$(jq -r '.network.gateway' "$DEFAULT_CONFIG_FILE")

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops
POSTGRES_PASSWORD=${GENERATED_SECRETS[postgres_password]}

# Redis配置
REDIS_PASSWORD=${GENERATED_SECRETS[redis_password]}

# Elasticsearch配置
ELASTIC_PASSWORD=${GENERATED_SECRETS[elastic_password]}
KIBANA_PASSWORD=${GENERATED_SECRETS[kibana_password]}

# Grafana配置
GF_SECURITY_ADMIN_PASSWORD=${GENERATED_SECRETS[grafana_admin_password]}

# API配置
API_KEY=${GENERATED_SECRETS[api_key]}
JWT_SECRET=${GENERATED_SECRETS[jwt_secret]}

# Webhook配置
WEBHOOK_SECRET=${GENERATED_SECRETS[webhook_secret]}

# 通知配置
SMTP_PASSWORD=${GENERATED_SECRETS[smtp_password]}
SLACK_WEBHOOK_URL=${GENERATED_SECRETS[slack_webhook_url]}

# Traefik配置
TRAEFIK_DASHBOARD_USER=${GENERATED_SECRETS[traefik_dashboard_user]}
TRAEFIK_DASHBOARD_PASSWORD=${GENERATED_SECRETS[traefik_dashboard_password]}

# 日志级别
LOG_LEVEL=$LOG_LEVEL
DEBUG=$(echo "$DEBUG" | tr '[:upper:]' '[:lower:]')
EOF
    
    # 生成docker-compose.yml
    cat > "$compose_file" << 'EOF'
version: '3.8'

networks:
  aiops-network:
    driver: bridge
    ipam:
      config:
        - subnet: ${NETWORK_SUBNET}
          gateway: ${NETWORK_GATEWAY}

volumes:
  prometheus-data:
  grafana-data:
  alertmanager-data:
  elasticsearch-data:
  redis-data:
  postgres-data:

services:
EOF
    
    # 添加各个服务
    local services
    services=$(jq -r '.services | keys[]' "$DEFAULT_CONFIG_FILE")
    
    while IFS= read -r service_name; do
        local service_config
        service_config=$(jq -r ".services.\"$service_name\"" "$DEFAULT_CONFIG_FILE")
        
        local enabled
        enabled=$(echo "$service_config" | jq -r '.enabled')
        
        if [[ "$enabled" == "true" ]]; then
            local image
            image=$(echo "$service_config" | jq -r '.image')
            
            # 添加服务定义
            cat >> "$compose_file" << EOF

  $service_name:
    image: $image
    container_name: \${PROJECT_NAME}-$service_name
    restart: unless-stopped
    networks:
      - aiops-network
EOF
            
            # 添加端口映射
            local port
            port=$(echo "$service_config" | jq -r '.port // empty')
            if [[ -n "$port" ]]; then
                echo "    ports:" >> "$compose_file"
                echo "      - \"$port:$port\"" >> "$compose_file"
            fi
            
            # 添加环境变量
            echo "    environment:" >> "$compose_file"
            
            case "$service_name" in
                "traefik")
                    cat >> "$compose_file" << 'EOF'
      - TRAEFIK_API_DASHBOARD=true
      - TRAEFIK_API_INSECURE=true
EOF
                    ;;
                "prometheus")
                    local retention
                    retention=$(echo "$service_config" | jq -r '.retention')
                    echo "      - PROMETHEUS_RETENTION_TIME=$retention" >> "$compose_file"
                    ;;
                "grafana")
                    echo "      - GF_SECURITY_ADMIN_PASSWORD=\${GF_SECURITY_ADMIN_PASSWORD}" >> "$compose_file"
                    ;;
                "elasticsearch")
                    local heap_size
                    heap_size=$(echo "$service_config" | jq -r '.heap_size')
                    cat >> "$compose_file" << EOF
      - discovery.type=single-node
      - ES_JAVA_OPTS=-Xms$heap_size -Xmx$heap_size
      - ELASTIC_PASSWORD=\${ELASTIC_PASSWORD}
EOF
                    ;;
                "redis")
                    echo "      - REDIS_PASSWORD=\${REDIS_PASSWORD}" >> "$compose_file"
                    ;;
                "postgresql")
                    cat >> "$compose_file" << 'EOF'
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
EOF
                    ;;
                *)
                    cat >> "$compose_file" << 'EOF'
      - LOG_LEVEL=${LOG_LEVEL}
      - DEBUG=${DEBUG}
EOF
                    ;;
            esac
            
            # 添加卷挂载
            if [[ "$service_name" =~ ^(prometheus|grafana|alertmanager|elasticsearch|redis|postgresql)$ ]]; then
                cat >> "$compose_file" << EOF
    volumes:
      - $service_name-data:/data
EOF
            fi
        fi
    done <<< "$services"
    
    log_info "Docker Compose配置生成完成:"
    log_debug "  - $compose_file"
    log_debug "  - $env_file"
}

# 生成Kubernetes配置
generate_kubernetes_config() {
    local output_dir="$1"
    
    log_info "生成Kubernetes配置..."
    
    local k8s_dir="$output_dir/k8s"
    mkdir -p "$k8s_dir"
    
    local values_file="$k8s_dir/values.yaml"
    
    # 生成values.yaml文件
    cat > "$values_file" << EOF
# AIOps平台Helm Values
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')
# 环境: $ENVIRONMENT

global:
  environment: $ENVIRONMENT
  namespace: $(jq -r '.namespace' "$DEFAULT_CONFIG_FILE")
  domain: $(jq -r '.domain' "$DEFAULT_CONFIG_FILE")
  storageClass: $STORAGE_CLASS
  ingressClass: $INGRESS_CLASS
  debug: $(echo "$DEBUG" | tr '[:upper:]' '[:lower:]')
  logLevel: $LOG_LEVEL

# 服务配置
EOF
    
    # 添加各个服务配置
    local services
    services=$(jq -r '.services | keys[]' "$DEFAULT_CONFIG_FILE")
    
    while IFS= read -r service_name; do
        local service_config
        service_config=$(jq -r ".services.\"$service_name\"" "$DEFAULT_CONFIG_FILE")
        
        local enabled replicas image_repo image_tag
        enabled=$(echo "$service_config" | jq -r '.enabled')
        replicas=$(echo "$service_config" | jq -r '.replicas')
        
        local image
        image=$(echo "$service_config" | jq -r '.image')
        image_repo=$(echo "$image" | cut -d':' -f1)
        image_tag=$(echo "$image" | cut -d':' -f2)
        
        cat >> "$values_file" << EOF

$service_name:
  enabled: $(echo "$enabled" | tr '[:upper:]' '[:lower:]')
  replicaCount: $replicas
  image:
    repository: $image_repo
    tag: $image_tag
    pullPolicy: IfNotPresent
EOF
        
        # 添加资源配置
        local resources
        resources=$(echo "$service_config" | jq -r '.resources // empty')
        if [[ -n "$resources" && "$resources" != "null" ]]; then
            cat >> "$values_file" << EOF
  resources:
    requests:
      cpu: $(echo "$resources" | jq -r '.requests.cpu')
      memory: $(echo "$resources" | jq -r '.requests.memory')
    limits:
      cpu: $(echo "$resources" | jq -r '.limits.cpu')
      memory: $(echo "$resources" | jq -r '.limits.memory')
EOF
        fi
        
        # 添加存储配置
        local storage_size
        storage_size=$(echo "$service_config" | jq -r '.storage_size // empty')
        if [[ -n "$storage_size" && "$storage_size" != "null" ]]; then
            cat >> "$values_file" << EOF
  persistence:
    enabled: true
    size: $storage_size
EOF
        fi
    done <<< "$services"
    
    # 添加密钥配置
    cat >> "$values_file" << EOF

# 密钥配置
secrets:
EOF
    
    for secret_name in "${!GENERATED_SECRETS[@]}"; do
        echo "  $secret_name: \"${GENERATED_SECRETS[$secret_name]}\"" >> "$values_file"
    done
    
    # 生成kustomization.yaml
    local kustomization_file="$k8s_dir/kustomization.yaml"
    
    cat > "$kustomization_file" << EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: $(jq -r '.namespace' "$DEFAULT_CONFIG_FILE")

resources:
  - ../helm/templates/

commonLabels:
  app.kubernetes.io/name: aiops
  app.kubernetes.io/instance: aiops-$ENVIRONMENT
  app.kubernetes.io/version: "1.0.0"
  app.kubernetes.io/managed-by: kustomize
  environment: $ENVIRONMENT

replicas:
EOF
    
    # 添加副本数配置
    while IFS= read -r service_name; do
        local service_config
        service_config=$(jq -r ".services.\"$service_name\"" "$DEFAULT_CONFIG_FILE")
        
        local enabled replicas
        enabled=$(echo "$service_config" | jq -r '.enabled')
        replicas=$(echo "$service_config" | jq -r '.replicas')
        
        if [[ "$enabled" == "true" ]]; then
            cat >> "$kustomization_file" << EOF
  - name: $service_name
    count: $replicas
EOF
        fi
    done <<< "$services"
    
    log_info "Kubernetes配置生成完成:"
    log_debug "  - $values_file"
    log_debug "  - $kustomization_file"
}

# 生成配置摘要
generate_config_summary() {
    local output_dir="$1"
    
    local summary_file="$output_dir/config-summary.md"
    
    cat > "$summary_file" << EOF
# AIOps平台配置摘要

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**环境**: $ENVIRONMENT
**配置类型**: $CONFIG_TYPE

## 基础配置

- **项目名称**: $(jq -r '.project_name' "$DEFAULT_CONFIG_FILE")
- **命名空间**: $(jq -r '.namespace' "$DEFAULT_CONFIG_FILE")
- **域名**: $(jq -r '.domain' "$DEFAULT_CONFIG_FILE")
- **调试模式**: $DEBUG
- **日志级别**: $LOG_LEVEL

## 服务配置

| 服务名称 | 启用状态 | 副本数 | 镜像 | 端口 |
|---------|---------|-------|------|------|
EOF
    
    # 添加服务配置表格
    local services
    services=$(jq -r '.services | keys[]' "$DEFAULT_CONFIG_FILE")
    
    while IFS= read -r service_name; do
        local service_config
        service_config=$(jq -r ".services.\"$service_name\"" "$DEFAULT_CONFIG_FILE")
        
        local enabled replicas image port
        enabled=$(echo "$service_config" | jq -r '.enabled')
        replicas=$(echo "$service_config" | jq -r '.replicas')
        image=$(echo "$service_config" | jq -r '.image')
        port=$(echo "$service_config" | jq -r '.port // "N/A"')
        
        echo "| $service_name | $enabled | $replicas | $image | $port |" >> "$summary_file"
    done <<< "$services"
    
    cat >> "$summary_file" << EOF

## 生成的密钥

以下密钥已自动生成，请妥善保管：

EOF
    
    for secret_name in "${!GENERATED_SECRETS[@]}"; do
        if [[ "$secret_name" =~ password|secret ]]; then
            echo "- **$secret_name**: [已生成，长度 ${#GENERATED_SECRETS[$secret_name]} 字符]" >> "$summary_file"
        else
            echo "- **$secret_name**: ${GENERATED_SECRETS[$secret_name]}" >> "$summary_file"
        fi
    done
    
    cat >> "$summary_file" << EOF

## 安全注意事项

1. 请立即更改所有默认密码
2. 在生产环境中使用强密码和证书
3. 定期轮换密钥和证书
4. 限制网络访问和端口暴露
5. 启用审计日志和监控

## 下一步操作

EOF
    
    if [[ "$CONFIG_TYPE" == "docker-compose" || "$CONFIG_TYPE" == "both" ]]; then
        cat >> "$summary_file" << 'EOF'
### Docker Compose部署

```bash
# 启动服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

EOF
    fi
    
    if [[ "$CONFIG_TYPE" == "kubernetes" || "$CONFIG_TYPE" == "both" ]]; then
        local namespace
        namespace=$(jq -r '.namespace' "$DEFAULT_CONFIG_FILE")
        
        cat >> "$summary_file" << EOF
### Kubernetes部署

\`\`\`bash
# 使用Helm部署
helm install aiops ./helm -f k8s/values.yaml

# 或使用Kustomize部署
kubectl apply -k k8s/

# 查看部署状态
kubectl get pods -n $namespace
\`\`\`

EOF
    fi
    
    log_info "配置摘要生成完成: $summary_file"
}

# 清理临时文件
cleanup() {
    if [[ -f "$DEFAULT_CONFIG_FILE" ]]; then
        rm -f "$DEFAULT_CONFIG_FILE" "${DEFAULT_CONFIG_FILE}.tmp"
    fi
}

# 主函数
main() {
    log_info "AIOps平台配置生成工具"
    log_info "配置类型: $CONFIG_TYPE"
    log_info "环境: $ENVIRONMENT"
    log_info "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 设置输出路径
    if [[ -z "$OUTPUT_PATH" ]]; then
        OUTPUT_PATH="$PROJECT_ROOT/generated/$ENVIRONMENT"
    fi
    
    # 创建输出目录
    if [[ ! -d "$OUTPUT_PATH" ]]; then
        mkdir -p "$OUTPUT_PATH"
        log_debug "创建输出目录: $OUTPUT_PATH"
    elif [[ "$FORCE" != "true" ]]; then
        echo -n "输出目录已存在，是否覆盖？(y/N): "
        read -r response
        if [[ "$response" != "y" && "$response" != "Y" ]]; then
            log_warn "操作已取消"
            return 0
        fi
    fi
    
    # 设置清理陷阱
    trap cleanup EXIT
    
    # 初始化
    initialize_secrets
    load_default_config
    load_custom_config "$CONFIG_FILE"
    apply_environment_config "$ENVIRONMENT"
    
    # 生成配置
    case "$CONFIG_TYPE" in
        "docker-compose")
            generate_docker_compose_config "$OUTPUT_PATH"
            ;;
        "kubernetes")
            generate_kubernetes_config "$OUTPUT_PATH"
            ;;
        "both")
            generate_docker_compose_config "$OUTPUT_PATH"
            generate_kubernetes_config "$OUTPUT_PATH"
            ;;
    esac
    
    # 生成摘要
    generate_config_summary "$OUTPUT_PATH"
    
    log_info "配置生成完成！"
    echo -e "${CYAN}输出目录: $OUTPUT_PATH${NC}"
    
    log_info "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 检查依赖
check_dependencies() {
    local missing_deps=()
    
    # 检查必需的命令
    for cmd in jq openssl; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        log_error "缺少必需的依赖: ${missing_deps[*]}"
        log_error "请安装缺少的依赖后重试"
        exit 1
    fi
}

# 脚本入口点
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # 检查依赖
    check_dependencies
    
    # 解析参数
    parse_args "$@"
    
    # 执行主函数
    main
fi