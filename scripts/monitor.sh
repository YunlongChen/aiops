#!/bin/bash

# AIOps平台监控脚本 (Bash)
#
# 本脚本用于监控AIOps平台的部署状态和服务健康状况，包括Docker容器状态、
# Kubernetes资源状态、服务端点健康检查、资源使用情况等。
#
# 用法:
#   ./monitor.sh [选项]
#
# 选项:
#   -t, --type TYPE          部署类型：docker-compose, kubernetes, 或 all (默认: all)
#   -e, --env ENV           环境名称：development, staging, production (默认: development)
#   -c, --continuous        持续监控模式
#   -i, --interval SECONDS  监控间隔（秒），默认30秒
#   -f, --format FORMAT     输出格式：console, json, html (默认: console)
#   -o, --output FILE       输出文件路径
#   -a, --alert-config FILE 告警阈值配置文件路径
#   -h, --help              显示帮助信息
#
# 示例:
#   ./monitor.sh -t docker-compose -e development
#   ./monitor.sh -t kubernetes -c -i 60
#   ./monitor.sh -f json -o monitoring-report.json
#
# 版本: 1.0.0
# 作者: AIOps Team
# 创建日期: 2024-01-01

set -euo pipefail

# 默认参数
DEPLOYMENT_TYPE="all"
ENVIRONMENT="development"
CONTINUOUS=false
INTERVAL=30
OUTPUT_FORMAT="console"
OUTPUT_FILE=""
ALERT_THRESHOLD=""

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="aiops"
MONITORING_DATA_FILE="/tmp/aiops_monitoring_data.json"

# 默认告警阈值
DEFAULT_CPU_THRESHOLD=80
DEFAULT_MEMORY_THRESHOLD=85
DEFAULT_DISK_THRESHOLD=90
DEFAULT_RESPONSE_TIME_THRESHOLD=5000
DEFAULT_ERROR_RATE_THRESHOLD=5

# 服务端点配置
declare -A SERVICE_ENDPOINTS=(
    ["traefik_url"]="http://localhost:8080/api/rawdata"
    ["traefik_port"]="8080"
    ["prometheus_url"]="http://localhost:9090/-/healthy"
    ["prometheus_port"]="9090"
    ["grafana_url"]="http://localhost:3000/api/health"
    ["grafana_port"]="3000"
    ["alertmanager_url"]="http://localhost:9093/-/healthy"
    ["alertmanager_port"]="9093"
    ["elasticsearch_url"]="http://localhost:9200/_cluster/health"
    ["elasticsearch_port"]="9200"
    ["kibana_url"]="http://localhost:5601/api/status"
    ["kibana_port"]="5601"
    ["redis_port"]="6379"
    ["redis_command"]="redis-cli ping"
    ["postgresql_port"]="5432"
    ["postgresql_command"]="pg_isready -h localhost -p 5432"
    ["ai_engine_url"]="http://localhost:8001/health"
    ["ai_engine_port"]="8001"
    ["api_gateway_url"]="http://localhost:8000/health"
    ["api_gateway_port"]="8000"
    ["self_healing_url"]="http://localhost:8002/health"
    ["self_healing_port"]="8002"
)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "[$timestamp] [${BLUE}INFO${NC}] $message"
            ;;
        "WARN")
            echo -e "[$timestamp] [${YELLOW}WARN${NC}] $message"
            ;;
        "ERROR")
            echo -e "[$timestamp] [${RED}ERROR${NC}] $message" >&2
            ;;
        "SUCCESS")
            echo -e "[$timestamp] [${GREEN}SUCCESS${NC}] $message"
            ;;
        "DEBUG")
            echo -e "[$timestamp] [${GRAY}DEBUG${NC}] $message"
            ;;
        *)
            echo -e "[$timestamp] $message"
            ;;
    esac
}

# 显示帮助信息
show_help() {
    cat << EOF
AIOps平台监控工具

用法: $0 [选项]

选项:
  -t, --type TYPE          部署类型：docker-compose, kubernetes, 或 all (默认: all)
  -e, --env ENV           环境名称：development, staging, production (默认: development)
  -c, --continuous        持续监控模式
  -i, --interval SECONDS  监控间隔（秒），默认30秒
  -f, --format FORMAT     输出格式：console, json, html (默认: console)
  -o, --output FILE       输出文件路径
  -a, --alert-config FILE 告警阈值配置文件路径
  -h, --help              显示帮助信息

示例:
  $0 -t docker-compose -e development
  $0 -t kubernetes -c -i 60
  $0 -f json -o monitoring-report.json

EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                DEPLOYMENT_TYPE="$2"
                if [[ ! "$DEPLOYMENT_TYPE" =~ ^(docker-compose|kubernetes|all)$ ]]; then
                    log "ERROR" "无效的部署类型: $DEPLOYMENT_TYPE"
                    exit 1
                fi
                shift 2
                ;;
            -e|--env)
                ENVIRONMENT="$2"
                if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
                    log "ERROR" "无效的环境名称: $ENVIRONMENT"
                    exit 1
                fi
                shift 2
                ;;
            -c|--continuous)
                CONTINUOUS=true
                shift
                ;;
            -i|--interval)
                INTERVAL="$2"
                if ! [[ "$INTERVAL" =~ ^[0-9]+$ ]] || [ "$INTERVAL" -lt 1 ]; then
                    log "ERROR" "无效的监控间隔: $INTERVAL"
                    exit 1
                fi
                shift 2
                ;;
            -f|--format)
                OUTPUT_FORMAT="$2"
                if [[ ! "$OUTPUT_FORMAT" =~ ^(console|json|html)$ ]]; then
                    log "ERROR" "无效的输出格式: $OUTPUT_FORMAT"
                    exit 1
                fi
                shift 2
                ;;
            -o|--output)
                OUTPUT_FILE="$2"
                shift 2
                ;;
            -a|--alert-config)
                ALERT_THRESHOLD="$2"
                shift 2
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log "ERROR" "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Docker是否可用
test_docker_available() {
    if command_exists docker && docker version >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查Kubernetes是否可用
test_kubernetes_available() {
    if command_exists kubectl && kubectl version --client >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查端口是否开放
test_port() {
    local host="${1:-localhost}"
    local port="$2"
    local timeout="${3:-3}"
    
    if command_exists nc; then
        nc -z -w"$timeout" "$host" "$port" >/dev/null 2>&1
    elif command_exists telnet; then
        timeout "$timeout" telnet "$host" "$port" >/dev/null 2>&1
    else
        # 使用bash内置的网络功能
        timeout "$timeout" bash -c "</dev/tcp/$host/$port" >/dev/null 2>&1
    fi
}

# HTTP健康检查
test_http_endpoint() {
    local url="$1"
    local timeout="${2:-5}"
    
    if command_exists curl; then
        local response
        local status_code
        local response_time
        
        response=$(curl -s -w "\n%{http_code}\n%{time_total}" --max-time "$timeout" "$url" 2>/dev/null || echo "ERROR\n0\n0")
        
        local content=$(echo "$response" | head -n -2)
        status_code=$(echo "$response" | tail -n 2 | head -n 1)
        response_time=$(echo "$response" | tail -n 1)
        
        if [[ "$status_code" =~ ^[2-3][0-9][0-9]$ ]]; then
            echo "healthy|$status_code|$response_time|${#content}"
        else
            echo "unhealthy|$status_code|$response_time|curl_error"
        fi
    elif command_exists wget; then
        if wget --timeout="$timeout" --tries=1 -q -O /dev/null "$url" 2>/dev/null; then
            echo "healthy|200|0|0"
        else
            echo "unhealthy|0|0|wget_error"
        fi
    else
        echo "unhealthy|0|0|no_http_client"
    fi
}

# 初始化监控数据
init_monitoring_data() {
    cat > "$MONITORING_DATA_FILE" << EOF
{
    "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')",
    "deployment_type": "$DEPLOYMENT_TYPE",
    "environment": "$ENVIRONMENT",
    "docker_services": [],
    "kubernetes_resources": [],
    "health_checks": [],
    "resource_usage": {},
    "alerts": [],
    "summary": {}
}
EOF
}

# 添加告警
add_alert() {
    local alert_type="$1"
    local alert_data="$2"
    
    local temp_file=$(mktemp)
    jq --arg type "$alert_type" --arg timestamp "$(date '+%Y-%m-%d %H:%M:%S')" --argjson data "$alert_data" \
        '.alerts += [{"type": $type, "timestamp": $timestamp} + $data]' \
        "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
}

# 加载告警阈值配置
load_alert_thresholds() {
    if [[ -n "$ALERT_THRESHOLD" && -f "$ALERT_THRESHOLD" ]]; then
        if command_exists jq; then
            local cpu_threshold=$(jq -r '.cpu_usage // empty' "$ALERT_THRESHOLD" 2>/dev/null)
            local memory_threshold=$(jq -r '.memory_usage // empty' "$ALERT_THRESHOLD" 2>/dev/null)
            local disk_threshold=$(jq -r '.disk_usage // empty' "$ALERT_THRESHOLD" 2>/dev/null)
            local response_time_threshold=$(jq -r '.response_time // empty' "$ALERT_THRESHOLD" 2>/dev/null)
            local error_rate_threshold=$(jq -r '.error_rate // empty' "$ALERT_THRESHOLD" 2>/dev/null)
            
            [[ -n "$cpu_threshold" ]] && DEFAULT_CPU_THRESHOLD="$cpu_threshold"
            [[ -n "$memory_threshold" ]] && DEFAULT_MEMORY_THRESHOLD="$memory_threshold"
            [[ -n "$disk_threshold" ]] && DEFAULT_DISK_THRESHOLD="$disk_threshold"
            [[ -n "$response_time_threshold" ]] && DEFAULT_RESPONSE_TIME_THRESHOLD="$response_time_threshold"
            [[ -n "$error_rate_threshold" ]] && DEFAULT_ERROR_RATE_THRESHOLD="$error_rate_threshold"
            
            log "INFO" "已加载告警阈值配置: $ALERT_THRESHOLD"
        else
            log "WARN" "jq命令不可用，无法加载告警阈值配置"
        fi
    fi
}

# 监控Docker Compose服务
monitor_docker_compose_services() {
    log "INFO" "监控Docker Compose服务..."
    
    if ! test_docker_available; then
        log "WARN" "Docker不可用，跳过Docker监控"
        return
    fi
    
    local project_name="${PROJECT_NAME}-${ENVIRONMENT}"
    local containers
    
    # 尝试通过项目标签获取容器
    containers=$(docker ps -a --filter "label=com.docker.compose.project=$project_name" --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>/dev/null || true)
    
    # 如果没有找到，尝试通过名称过滤
    if [[ -z "$containers" ]]; then
        containers=$(docker ps -a --filter "name=$PROJECT_NAME" --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>/dev/null || true)
    fi
    
    if [[ -z "$containers" ]]; then
        log "WARN" "未找到Docker容器"
        return
    fi
    
    local temp_file=$(mktemp)
    
    while IFS='|' read -r name status ports; do
        if [[ -n "$name" ]]; then
            # 获取容器详细信息
            local inspect_data
            inspect_data=$(docker inspect "$name" 2>/dev/null || echo '[]')
            
            if [[ "$inspect_data" != '[]' ]]; then
                local image created started health restart_count
                image=$(echo "$inspect_data" | jq -r '.[0].Config.Image // "unknown"')
                created=$(echo "$inspect_data" | jq -r '.[0].Created // "unknown"')
                started=$(echo "$inspect_data" | jq -r '.[0].State.StartedAt // "unknown"')
                health=$(echo "$inspect_data" | jq -r '.[0].State.Health.Status // "unknown"')
                restart_count=$(echo "$inspect_data" | jq -r '.[0].RestartCount // 0')
                
                # 获取资源使用情况
                local cpu_usage="" memory_usage="" memory_percent=""
                local stats
                stats=$(docker stats "$name" --no-stream --format "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}" 2>/dev/null || echo "||")
                
                if [[ -n "$stats" ]]; then
                    IFS='|' read -r cpu_usage memory_usage memory_percent <<< "$stats"
                    cpu_usage=${cpu_usage%\%}
                    memory_percent=${memory_percent%\%}
                fi
                
                # 构建服务信息JSON
                local service_info
                service_info=$(jq -n \
                    --arg name "$name" \
                    --arg status "$status" \
                    --arg ports "$ports" \
                    --arg image "$image" \
                    --arg created "$created" \
                    --arg started "$started" \
                    --arg health "$health" \
                    --arg restart_count "$restart_count" \
                    --arg cpu_usage "$cpu_usage" \
                    --arg memory_usage "$memory_usage" \
                    --arg memory_percent "$memory_percent" \
                    '{
                        name: $name,
                        status: $status,
                        ports: $ports,
                        image: $image,
                        created: $created,
                        started: $started,
                        health: $health,
                        restart_count: ($restart_count | tonumber),
                        cpu_usage: (if $cpu_usage != "" then ($cpu_usage | tonumber) else null end),
                        memory_usage: $memory_usage,
                        memory_percent: (if $memory_percent != "" then ($memory_percent | tonumber) else null end)
                    }')
                
                # 添加到监控数据
                jq --argjson service "$service_info" '.docker_services += [$service]' "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
                
                # 检查告警条件
                if [[ -n "$cpu_usage" ]] && (( $(echo "$cpu_usage > $DEFAULT_CPU_THRESHOLD" | bc -l) )); then
                    add_alert "high_cpu" "{\"service\": \"$name\", \"value\": $cpu_usage, \"threshold\": $DEFAULT_CPU_THRESHOLD}"
                fi
                
                if [[ -n "$memory_percent" ]] && (( $(echo "$memory_percent > $DEFAULT_MEMORY_THRESHOLD" | bc -l) )); then
                    add_alert "high_memory" "{\"service\": \"$name\", \"value\": $memory_percent, \"threshold\": $DEFAULT_MEMORY_THRESHOLD}"
                fi
            fi
        fi
    done <<< "$containers"
    
    local service_count
    service_count=$(jq '.docker_services | length' "$MONITORING_DATA_FILE")
    log "SUCCESS" "Docker服务监控完成，发现 $service_count 个服务"
}

# 监控Kubernetes资源
monitor_kubernetes_resources() {
    log "INFO" "监控Kubernetes资源..."
    
    if ! test_kubernetes_available; then
        log "WARN" "kubectl不可用，跳过Kubernetes监控"
        return
    fi
    
    local namespace="aiops-$ENVIRONMENT"
    
    # 检查命名空间是否存在
    if ! kubectl get namespace "$namespace" >/dev/null 2>&1; then
        namespace="aiops"
        if ! kubectl get namespace "$namespace" >/dev/null 2>&1; then
            log "WARN" "未找到AIOps命名空间"
            return
        fi
    fi
    
    local temp_file=$(mktemp)
    
    # 监控Deployment
    local deployments
    deployments=$(kubectl get deployments -n "$namespace" -o json 2>/dev/null || echo '{"items":[]}')
    
    if [[ "$(echo "$deployments" | jq '.items | length')" -gt 0 ]]; then
        echo "$deployments" | jq -r '.items[] | @base64' | while read -r deployment_data; do
            local deployment
            deployment=$(echo "$deployment_data" | base64 -d)
            
            local name namespace replicas ready_replicas available_replicas created
            name=$(echo "$deployment" | jq -r '.metadata.name')
            namespace=$(echo "$deployment" | jq -r '.metadata.namespace')
            replicas=$(echo "$deployment" | jq -r '.spec.replicas // 0')
            ready_replicas=$(echo "$deployment" | jq -r '.status.readyReplicas // 0')
            available_replicas=$(echo "$deployment" | jq -r '.status.availableReplicas // 0')
            created=$(echo "$deployment" | jq -r '.metadata.creationTimestamp')
            
            local resource_info
            resource_info=$(jq -n \
                --arg type "deployment" \
                --arg name "$name" \
                --arg namespace "$namespace" \
                --arg replicas "$replicas" \
                --arg ready_replicas "$ready_replicas" \
                --arg available_replicas "$available_replicas" \
                --arg created "$created" \
                '{
                    type: $type,
                    name: $name,
                    namespace: $namespace,
                    replicas: ($replicas | tonumber),
                    ready_replicas: ($ready_replicas | tonumber),
                    available_replicas: ($available_replicas | tonumber),
                    created: $created
                }')
            
            jq --argjson resource "$resource_info" '.kubernetes_resources += [$resource]' "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
            
            # 检查副本状态
            if [[ "$ready_replicas" -lt "$replicas" ]]; then
                add_alert "deployment_not_ready" "{\"resource\": \"$namespace/$name\", \"ready\": $ready_replicas, \"desired\": $replicas}"
            fi
        done
    fi
    
    # 监控StatefulSet
    local statefulsets
    statefulsets=$(kubectl get statefulsets -n "$namespace" -o json 2>/dev/null || echo '{"items":[]}')
    
    if [[ "$(echo "$statefulsets" | jq '.items | length')" -gt 0 ]]; then
        echo "$statefulsets" | jq -r '.items[] | @base64' | while read -r statefulset_data; do
            local statefulset
            statefulset=$(echo "$statefulset_data" | base64 -d)
            
            local name namespace replicas ready_replicas current_replicas created
            name=$(echo "$statefulset" | jq -r '.metadata.name')
            namespace=$(echo "$statefulset" | jq -r '.metadata.namespace')
            replicas=$(echo "$statefulset" | jq -r '.spec.replicas // 0')
            ready_replicas=$(echo "$statefulset" | jq -r '.status.readyReplicas // 0')
            current_replicas=$(echo "$statefulset" | jq -r '.status.currentReplicas // 0')
            created=$(echo "$statefulset" | jq -r '.metadata.creationTimestamp')
            
            local resource_info
            resource_info=$(jq -n \
                --arg type "statefulset" \
                --arg name "$name" \
                --arg namespace "$namespace" \
                --arg replicas "$replicas" \
                --arg ready_replicas "$ready_replicas" \
                --arg current_replicas "$current_replicas" \
                --arg created "$created" \
                '{
                    type: $type,
                    name: $name,
                    namespace: $namespace,
                    replicas: ($replicas | tonumber),
                    ready_replicas: ($ready_replicas | tonumber),
                    current_replicas: ($current_replicas | tonumber),
                    created: $created
                }')
            
            jq --argjson resource "$resource_info" '.kubernetes_resources += [$resource]' "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
            
            # 检查副本状态
            if [[ "$ready_replicas" -lt "$replicas" ]]; then
                add_alert "statefulset_not_ready" "{\"resource\": \"$namespace/$name\", \"ready\": $ready_replicas, \"desired\": $replicas}"
            fi
        done
    fi
    
    # 监控Pod
    local pods
    pods=$(kubectl get pods -n "$namespace" -o json 2>/dev/null || echo '{"items":[]}')
    
    if [[ "$(echo "$pods" | jq '.items | length')" -gt 0 ]]; then
        echo "$pods" | jq -r '.items[] | @base64' | while read -r pod_data; do
            local pod
            pod=$(echo "$pod_data" | base64 -d)
            
            local name namespace phase ready restart_count node created
            name=$(echo "$pod" | jq -r '.metadata.name')
            namespace=$(echo "$pod" | jq -r '.metadata.namespace')
            phase=$(echo "$pod" | jq -r '.status.phase')
            ready=$(echo "$pod" | jq -r '.status.conditions[] | select(.type=="Ready") | .status // "Unknown"')
            restart_count=$(echo "$pod" | jq -r '[.status.containerStatuses[]?.restartCount // 0] | add')
            node=$(echo "$pod" | jq -r '.spec.nodeName // "unknown"')
            created=$(echo "$pod" | jq -r '.metadata.creationTimestamp')
            
            local resource_info
            resource_info=$(jq -n \
                --arg type "pod" \
                --arg name "$name" \
                --arg namespace "$namespace" \
                --arg phase "$phase" \
                --arg ready "$ready" \
                --arg restart_count "$restart_count" \
                --arg node "$node" \
                --arg created "$created" \
                '{
                    type: $type,
                    name: $name,
                    namespace: $namespace,
                    phase: $phase,
                    ready: $ready,
                    restart_count: ($restart_count | tonumber),
                    node: $node,
                    created: $created
                }')
            
            jq --argjson resource "$resource_info" '.kubernetes_resources += [$resource]' "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
            
            # 检查Pod状态
            if [[ "$phase" != "Running" || "$ready" != "True" ]]; then
                add_alert "pod_not_ready" "{\"resource\": \"$namespace/$name\", \"phase\": \"$phase\", \"ready\": \"$ready\"}"
            fi
            
            # 检查重启次数
            if [[ "$restart_count" -gt 5 ]]; then
                add_alert "high_restart_count" "{\"resource\": \"$namespace/$name\", \"restart_count\": $restart_count}"
            fi
        done
    fi
    
    local resource_count
    resource_count=$(jq '.kubernetes_resources | length' "$MONITORING_DATA_FILE")
    log "SUCCESS" "Kubernetes资源监控完成，发现 $resource_count 个资源"
}

# 执行健康检查
invoke_health_checks() {
    log "INFO" "执行服务健康检查..."
    
    local services=("traefik" "prometheus" "grafana" "alertmanager" "elasticsearch" "kibana" "redis" "postgresql" "ai_engine" "api_gateway" "self_healing")
    local temp_file=$(mktemp)
    
    for service in "${services[@]}"; do
        local health_check
        health_check=$(jq -n \
            --arg service "$service" \
            --arg timestamp "$(date '+%Y-%m-%d %H:%M:%S')" \
            '{
                service: $service,
                timestamp: $timestamp
            }')
        
        # 端口检查
        local port_key="${service}_port"
        if [[ -n "${SERVICE_ENDPOINTS[$port_key]:-}" ]]; then
            local port="${SERVICE_ENDPOINTS[$port_key]}"
            if test_port "localhost" "$port"; then
                health_check=$(echo "$health_check" | jq '. + {port_status: "open"}')
            else
                health_check=$(echo "$health_check" | jq '. + {port_status: "closed"}')
                add_alert "port_closed" "{\"service\": \"$service\", \"port\": $port}"
            fi
        fi
        
        # HTTP健康检查
        local url_key="${service}_url"
        if [[ -n "${SERVICE_ENDPOINTS[$url_key]:-}" ]]; then
            local url="${SERVICE_ENDPOINTS[$url_key]}"
            local http_result
            http_result=$(test_http_endpoint "$url")
            
            IFS='|' read -r status status_code response_time content_length <<< "$http_result"
            
            health_check=$(echo "$health_check" | jq \
                --arg status "$status" \
                --arg status_code "$status_code" \
                --arg response_time "$response_time" \
                '. + {
                    http_status: $status,
                    status_code: ($status_code | tonumber),
                    response_time: ($response_time | tonumber)
                }')
            
            if [[ "$status" == "unhealthy" ]]; then
                add_alert "http_unhealthy" "{\"service\": \"$service\", \"url\": \"$url\", \"error\": \"$content_length\"}"
            fi
        fi
        
        # 命令检查
        local command_key="${service}_command"
        if [[ -n "${SERVICE_ENDPOINTS[$command_key]:-}" ]]; then
            local command="${SERVICE_ENDPOINTS[$command_key]}"
            if eval "$command" >/dev/null 2>&1; then
                health_check=$(echo "$health_check" | jq '. + {command_status: "success"}')
            else
                health_check=$(echo "$health_check" | jq '. + {command_status: "failed"}')
                add_alert "command_failed" "{\"service\": \"$service\", \"command\": \"$command\", \"error\": \"command_execution_failed\"}"
            fi
        fi
        
        # 添加健康检查结果
        jq --argjson check "$health_check" '.health_checks += [$check]' "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
    done
    
    log "SUCCESS" "健康检查完成，检查了 ${#services[@]} 个服务"
}

# 获取系统资源使用情况
get_system_resource_usage() {
    log "INFO" "获取系统资源使用情况..."
    
    local temp_file=$(mktemp)
    local resource_usage="{}"
    
    # CPU使用率
    if command_exists top; then
        local cpu_usage
        cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
        resource_usage=$(echo "$resource_usage" | jq --arg cpu "$cpu_usage" '. + {cpu_usage: ($cpu | tonumber)}')
        
        # 检查CPU使用率告警
        if (( $(echo "$cpu_usage > $DEFAULT_CPU_THRESHOLD" | bc -l) )); then
            add_alert "high_system_cpu" "{\"value\": $cpu_usage, \"threshold\": $DEFAULT_CPU_THRESHOLD}"
        fi
    fi
    
    # 内存使用率
    if command_exists free; then
        local memory_info
        memory_info=$(free -m | awk 'NR==2{printf "%.2f %.2f %.2f %.2f", $3*1024/1024/1024, $2*1024/1024/1024, $4*1024/1024/1024, $3*100/$2}')
        read -r memory_used memory_total memory_free memory_percent <<< "$memory_info"
        
        resource_usage=$(echo "$resource_usage" | jq \
            --arg total "$memory_total" \
            --arg used "$memory_used" \
            --arg free "$memory_free" \
            --arg percent "$memory_percent" \
            '. + {
                memory_total: ($total | tonumber),
                memory_used: ($used | tonumber),
                memory_free: ($free | tonumber),
                memory_usage_percent: ($percent | tonumber)
            }')
        
        # 检查内存使用率告警
        if (( $(echo "$memory_percent > $DEFAULT_MEMORY_THRESHOLD" | bc -l) )); then
            add_alert "high_system_memory" "{\"value\": $memory_percent, \"threshold\": $DEFAULT_MEMORY_THRESHOLD}"
        fi
    fi
    
    # 磁盘使用率
    if command_exists df; then
        local disk_info="[]"
        while read -r filesystem size used avail use_percent mount; do
            if [[ "$filesystem" != "Filesystem" && "$mount" =~ ^/.*$ ]]; then
                local total_gb used_gb free_gb usage_percent
                total_gb=$(echo "scale=2; $size / 1024 / 1024" | bc)
                used_gb=$(echo "scale=2; $used / 1024 / 1024" | bc)
                free_gb=$(echo "scale=2; $avail / 1024 / 1024" | bc)
                usage_percent=${use_percent%\%}
                
                local disk_entry
                disk_entry=$(jq -n \
                    --arg drive "$mount" \
                    --arg total "$total_gb" \
                    --arg used "$used_gb" \
                    --arg free "$free_gb" \
                    --arg usage_percent "$usage_percent" \
                    '{
                        drive: $drive,
                        total: ($total | tonumber),
                        used: ($used | tonumber),
                        free: ($free | tonumber),
                        usage_percent: ($usage_percent | tonumber)
                    }')
                
                disk_info=$(echo "$disk_info" | jq --argjson entry "$disk_entry" '. += [$entry]')
                
                # 检查磁盘使用率告警
                if (( $(echo "$usage_percent > $DEFAULT_DISK_THRESHOLD" | bc -l) )); then
                    add_alert "high_disk_usage" "{\"drive\": \"$mount\", \"usage_percent\": $usage_percent, \"threshold\": $DEFAULT_DISK_THRESHOLD}"
                fi
            fi
        done <<< "$(df -k)"
        
        resource_usage=$(echo "$resource_usage" | jq --argjson disks "$disk_info" '. + {disks: $disks}')
    fi
    
    # 网络统计
    if [[ -f /proc/net/dev ]]; then
        local network_info="[]"
        while read -r line; do
            if [[ "$line" =~ ^[[:space:]]*([^:]+):[[:space:]]*([0-9]+)[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+([0-9]+) ]]; then
                local interface="${BASH_REMATCH[1]}"
                local bytes_received="${BASH_REMATCH[2]}"
                local bytes_sent="${BASH_REMATCH[3]}"
                
                if [[ "$interface" != "lo" ]]; then
                    local network_entry
                    network_entry=$(jq -n \
                        --arg name "$interface" \
                        --arg bytes_received "$bytes_received" \
                        --arg bytes_sent "$bytes_sent" \
                        '{
                            name: $name,
                            bytes_received: ($bytes_received | tonumber),
                            bytes_sent: ($bytes_sent | tonumber)
                        }')
                    
                    network_info=$(echo "$network_info" | jq --argjson entry "$network_entry" '. += [$entry]')
                fi
            fi
        done < /proc/net/dev
        
        resource_usage=$(echo "$resource_usage" | jq --argjson network "$network_info" '. + {network: $network}')
    fi
    
    # 更新监控数据
    jq --argjson usage "$resource_usage" '.resource_usage = $usage' "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
    
    log "SUCCESS" "系统资源监控完成"
}

# 生成监控摘要
generate_monitoring_summary() {
    local temp_file=$(mktemp)
    
    # 使用jq计算摘要统计
    local summary
    summary=$(jq '
        {
            total_services: (.docker_services | length),
            healthy_services: ([.docker_services[] | select(.status | test("Up") and (.health != "unhealthy"))] | length),
            unhealthy_services: ([.docker_services[] | select((.status | test("Up") | not) or .health == "unhealthy")] | length),
            total_resources: (.kubernetes_resources | length),
            ready_resources: ([
                .kubernetes_resources[] | 
                select(
                    (.type == "deployment" and .ready_replicas == .replicas) or
                    (.type == "statefulset" and .ready_replicas == .replicas) or
                    (.type == "pod" and .phase == "Running" and .ready == "True") or
                    (.type == "service")
                )
            ] | length),
            not_ready_resources: ([
                .kubernetes_resources[] | 
                select(
                    (.type == "deployment" and .ready_replicas != .replicas) or
                    (.type == "statefulset" and .ready_replicas != .replicas) or
                    (.type == "pod" and (.phase != "Running" or .ready != "True"))
                )
            ] | length),
            total_alerts: (.alerts | length),
            critical_alerts: ([.alerts[] | select(.type | IN("port_closed", "http_unhealthy", "deployment_not_ready", "statefulset_not_ready", "pod_not_ready"))] | length),
            warning_alerts: ([.alerts[] | select(.type | IN("port_closed", "http_unhealthy", "deployment_not_ready", "statefulset_not_ready", "pod_not_ready") | not)] | length)
        } | 
        . + {
            system_health: (
                if .critical_alerts > 0 then "critical"
                elif .warning_alerts > 0 or .unhealthy_services > 0 or .not_ready_resources > 0 then "warning"
                else "healthy"
                end
            )
        }
    ' "$MONITORING_DATA_FILE")
    
    jq --argjson summary "$summary" '.summary = $summary' "$MONITORING_DATA_FILE" > "$temp_file" && mv "$temp_file" "$MONITORING_DATA_FILE"
}

# 输出控制台格式
output_console_format() {
    echo
    echo -e "${CYAN}$(printf '=%.0s' {1..80})${NC}"
    echo -e "${CYAN}AIOps平台监控报告${NC}"
    
    local timestamp deployment_type environment
    timestamp=$(jq -r '.timestamp' "$MONITORING_DATA_FILE")
    deployment_type=$(jq -r '.deployment_type' "$MONITORING_DATA_FILE")
    environment=$(jq -r '.environment' "$MONITORING_DATA_FILE")
    
    echo -e "${GRAY}时间: $timestamp${NC}"
    echo -e "${GRAY}部署类型: $deployment_type${NC}"
    echo -e "${GRAY}环境: $environment${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..80})${NC}"
    
    # 系统摘要
    local system_health healthy_services total_services ready_resources total_resources total_alerts critical_alerts warning_alerts
    system_health=$(jq -r '.summary.system_health' "$MONITORING_DATA_FILE")
    healthy_services=$(jq -r '.summary.healthy_services' "$MONITORING_DATA_FILE")
    total_services=$(jq -r '.summary.total_services' "$MONITORING_DATA_FILE")
    ready_resources=$(jq -r '.summary.ready_resources' "$MONITORING_DATA_FILE")
    total_resources=$(jq -r '.summary.total_resources' "$MONITORING_DATA_FILE")
    total_alerts=$(jq -r '.summary.total_alerts' "$MONITORING_DATA_FILE")
    critical_alerts=$(jq -r '.summary.critical_alerts' "$MONITORING_DATA_FILE")
    warning_alerts=$(jq -r '.summary.warning_alerts' "$MONITORING_DATA_FILE")
    
    echo -n "系统健康状态: "
    case "$system_health" in
        "healthy") echo -e "${GREEN}健康${NC}" ;;
        "warning") echo -e "${YELLOW}警告${NC}" ;;
        "critical") echo -e "${RED}严重${NC}" ;;
    esac
    
    echo "服务状态: $healthy_services/$total_services 健康"
    echo "资源状态: $ready_resources/$total_resources 就绪"
    echo "告警数量: $total_alerts (严重: $critical_alerts, 警告: $warning_alerts)"
    
    # 系统资源
    local cpu_usage memory_usage_percent memory_used memory_total
    cpu_usage=$(jq -r '.resource_usage.cpu_usage // "N/A"' "$MONITORING_DATA_FILE")
    memory_usage_percent=$(jq -r '.resource_usage.memory_usage_percent // "N/A"' "$MONITORING_DATA_FILE")
    memory_used=$(jq -r '.resource_usage.memory_used // "N/A"' "$MONITORING_DATA_FILE")
    memory_total=$(jq -r '.resource_usage.memory_total // "N/A"' "$MONITORING_DATA_FILE")
    
    if [[ "$cpu_usage" != "N/A" ]]; then
        echo
        echo -e "${YELLOW}系统资源使用情况:${NC}"
        echo "  CPU使用率: $cpu_usage%"
        echo "  内存使用率: $memory_usage_percent% (${memory_used}GB/${memory_total}GB)"
        
        # 磁盘信息
        jq -r '.resource_usage.disks[]? | "  磁盘 " + .drive + ": " + (.usage_percent | tostring) + "% (" + (.used | tostring) + "GB/" + (.total | tostring) + "GB)"' "$MONITORING_DATA_FILE"
    fi
    
    # Docker服务
    local docker_service_count
    docker_service_count=$(jq '.docker_services | length' "$MONITORING_DATA_FILE")
    
    if [[ "$docker_service_count" -gt 0 ]]; then
        echo
        echo -e "${YELLOW}Docker服务状态:${NC}"
        
        jq -r '.docker_services[] | 
            "  " + .name + ": " + .status + 
            (if .cpu_usage then "\n    CPU: " + (.cpu_usage | tostring) + "%, 内存: " + (.memory_percent | tostring) + "%" else "" end)' \
            "$MONITORING_DATA_FILE" | while read -r line; do
            if [[ "$line" =~ Up ]]; then
                echo -e "${GREEN}$line${NC}"
            else
                echo -e "${RED}$line${NC}"
            fi
        done
    fi
    
    # Kubernetes资源
    local k8s_resource_count
    k8s_resource_count=$(jq '.kubernetes_resources | length' "$MONITORING_DATA_FILE")
    
    if [[ "$k8s_resource_count" -gt 0 ]]; then
        echo
        echo -e "${YELLOW}Kubernetes资源状态:${NC}"
        
        # 按类型分组显示
        local resource_types
        resource_types=$(jq -r '.kubernetes_resources | group_by(.type) | .[] | .[0].type' "$MONITORING_DATA_FILE" | sort -u)
        
        while read -r resource_type; do
            if [[ -n "$resource_type" ]]; then
                echo -e "  ${CYAN}${resource_type^^}:${NC}"
                
                jq -r --arg type "$resource_type" '
                    .kubernetes_resources[] | select(.type == $type) | 
                    "    " + .name + ": " + 
                    (if .type == "deployment" or .type == "statefulset" then
                        (if .ready_replicas == .replicas then "就绪 (" + (.ready_replicas | tostring) + "/" + (.replicas | tostring) + ")"
                         else "未就绪 (" + (.ready_replicas | tostring) + "/" + (.replicas | tostring) + ")" end)
                     elif .type == "pod" then
                        (if .phase == "Running" and .ready == "True" then "运行中" else .phase end)
                     else "活跃" end)' \
                    "$MONITORING_DATA_FILE" | while read -r line; do
                    if [[ "$line" =~ 就绪|运行中|活跃 ]]; then
                        echo -e "${GREEN}$line${NC}"
                    else
                        echo -e "${RED}$line${NC}"
                    fi
                done
            fi
        done <<< "$resource_types"
    fi
    
    # 健康检查
    local health_check_count
    health_check_count=$(jq '.health_checks | length' "$MONITORING_DATA_FILE")
    
    if [[ "$health_check_count" -gt 0 ]]; then
        echo
        echo -e "${YELLOW}服务健康检查:${NC}"
        
        jq -r '.health_checks[] | 
            "  " + .service + ":\n" +
            (if .port_status then "    端口: " + .port_status + "\n" else "" end) +
            (if .http_status then "    HTTP: " + .http_status + (if .status_code then " (" + (.status_code | tostring) + ")" else "" end) + "\n" else "" end) +
            (if .command_status then "    命令: " + .command_status + "\n" else "" end)' \
            "$MONITORING_DATA_FILE" | while read -r line; do
            if [[ "$line" =~ open|healthy|success ]]; then
                echo -e "${GREEN}$line${NC}"
            elif [[ "$line" =~ closed|unhealthy|failed ]]; then
                echo -e "${RED}$line${NC}"
            else
                echo "$line"
            fi
        done
    fi
    
    # 告警信息
    if [[ "$total_alerts" -gt 0 ]]; then
        echo
        echo -e "${RED}告警信息:${NC}"
        
        jq -r '.alerts[] | 
            "  [" + .timestamp + "] " + .type + "\n" +
            (if .service then "    服务: " + .service else "" end) +
            (if .resource then "    资源: " + .resource else "" end) +
            (if .value then "    值: " + (.value | tostring) else "" end) +
            (if .threshold then " (阈值: " + (.threshold | tostring) + ")" else "" end) +
            (if .port then "    端口: " + (.port | tostring) else "" end) +
            (if .url then "    URL: " + .url else "" end) +
            (if .error then "    错误: " + .error else "" end) +
            (if .drive then "    磁盘: " + .drive else "" end) +
            (if .usage_percent then "    使用率: " + (.usage_percent | tostring) + "%" else "" end) +
            (if .ready and .desired then "    就绪副本: " + (.ready | tostring) + "/" + (.desired | tostring) else "" end) +
            (if .phase then "    状态: " + .phase else "" end) +
            (if .restart_count then "    重启次数: " + (.restart_count | tostring) else "" end)' \
            "$MONITORING_DATA_FILE" | while read -r line; do
            if [[ "$line" =~ \[.*\] ]]; then
                # 告警标题行
                if [[ "$line" =~ port_closed|http_unhealthy|deployment_not_ready|statefulset_not_ready|pod_not_ready ]]; then
                    echo -e "${RED}$line${NC}"
                else
                    echo -e "${YELLOW}$line${NC}"
                fi
            else
                # 告警详情行
                echo -e "${GRAY}$line${NC}"
            fi
        done
    fi
    
    echo
    echo -e "${CYAN}$(printf '=%.0s' {1..80})${NC}"
}

# 输出JSON格式
output_json_format() {
    jq '.' "$MONITORING_DATA_FILE"
}

# 输出HTML格式
output_html_format() {
    local timestamp deployment_type environment system_health
    timestamp=$(jq -r '.timestamp' "$MONITORING_DATA_FILE")
    deployment_type=$(jq -r '.deployment_type' "$MONITORING_DATA_FILE")
    environment=$(jq -r '.environment' "$MONITORING_DATA_FILE")
    system_health=$(jq -r '.summary.system_health' "$MONITORING_DATA_FILE")
    
    cat << EOF
<!DOCTYPE html>
<html>
<head>
    <title>AIOps平台监控报告</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid #007acc; padding-bottom: 20px; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .summary-card { background-color: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #007acc; }
        .healthy { border-left-color: #28a745; }
        .warning { border-left-color: #ffc107; }
        .critical { border-left-color: #dc3545; }
        .section { margin-bottom: 30px; }
        .section h3 { color: #007acc; border-bottom: 1px solid #dee2e6; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px 12px; text-align: left; border-bottom: 1px solid #dee2e6; }
        th { background-color: #f8f9fa; font-weight: bold; }
        .status-healthy { color: #28a745; font-weight: bold; }
        .status-warning { color: #ffc107; font-weight: bold; }
        .status-critical { color: #dc3545; font-weight: bold; }
        .alert { padding: 10px; margin: 5px 0; border-radius: 4px; }
        .alert-warning { background-color: #fff3cd; border: 1px solid #ffeaa7; }
        .alert-critical { background-color: #f8d7da; border: 1px solid #f5c6cb; }
        .timestamp { color: #6c757d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AIOps平台监控报告</h1>
            <p class="timestamp">生成时间: $timestamp</p>
            <p>部署类型: $deployment_type | 环境: $environment</p>
        </div>
        
        <div class="summary">
            <div class="summary-card $system_health">
                <h4>系统健康状态</h4>
                <p class="status-$system_health">${system_health^^}</p>
            </div>
EOF
    
    # 添加摘要卡片
    jq -r '
        "            <div class=\"summary-card\">\n" +
        "                <h4>服务状态</h4>\n" +
        "                <p>" + (.summary.healthy_services | tostring) + "/" + (.summary.total_services | tostring) + " 健康</p>\n" +
        "            </div>\n" +
        "            <div class=\"summary-card\">\n" +
        "                <h4>资源状态</h4>\n" +
        "                <p>" + (.summary.ready_resources | tostring) + "/" + (.summary.total_resources | tostring) + " 就绪</p>\n" +
        "            </div>\n" +
        "            <div class=\"summary-card\">\n" +
        "                <h4>告警数量</h4>\n" +
        "                <p>" + (.summary.total_alerts | tostring) + " (严重: " + (.summary.critical_alerts | tostring) + ")</p>\n" +
        "            </div>"
    ' "$MONITORING_DATA_FILE"
    
    echo "        </div>"
    
    # 添加系统资源部分
    local cpu_usage memory_usage_percent memory_used memory_total
    cpu_usage=$(jq -r '.resource_usage.cpu_usage // "N/A"' "$MONITORING_DATA_FILE")
    
    if [[ "$cpu_usage" != "N/A" ]]; then
        echo "        <div class=\"section\">"
        echo "            <h3>系统资源使用情况</h3>"
        echo "            <table>"
        echo "                <tr><th>资源类型</th><th>使用情况</th><th>状态</th></tr>"
        
        jq -r '
            "                <tr>\n" +
            "                    <td>CPU</td>\n" +
            "                    <td>" + (.resource_usage.cpu_usage | tostring) + "%</td>\n" +
            "                    <td>" + (if .resource_usage.cpu_usage > 80 then "<span class=\"status-critical\">高</span>" elif .resource_usage.cpu_usage > 60 then "<span class=\"status-warning\">中</span>" else "<span class=\"status-healthy\">正常</span>" end) + "</td>\n" +
            "                </tr>\n" +
            "                <tr>\n" +
            "                    <td>内存</td>\n" +
            "                    <td>" + (.resource_usage.memory_usage_percent | tostring) + "% (" + (.resource_usage.memory_used | tostring) + "GB/" + (.resource_usage.memory_total | tostring) + "GB)</td>\n" +
            "                    <td>" + (if .resource_usage.memory_usage_percent > 85 then "<span class=\"status-critical\">高</span>" elif .resource_usage.memory_usage_percent > 70 then "<span class=\"status-warning\">中</span>" else "<span class=\"status-healthy\">正常</span>" end) + "</td>\n" +
            "                </tr>"
        ' "$MONITORING_DATA_FILE"
        
        # 添加磁盘信息
        jq -r '.resource_usage.disks[]? | 
            "                <tr>\n" +
            "                    <td>磁盘 " + .drive + "</td>\n" +
            "                    <td>" + (.usage_percent | tostring) + "% (" + (.used | tostring) + "GB/" + (.total | tostring) + "GB)</td>\n" +
            "                    <td>" + (if .usage_percent > 90 then "<span class=\"status-critical\">高</span>" elif .usage_percent > 75 then "<span class=\"status-warning\">中</span>" else "<span class=\"status-healthy\">正常</span>" end) + "</td>\n" +
            "                </tr>"' "$MONITORING_DATA_FILE"
        
        echo "            </table>"
        echo "        </div>"
    fi
    
    # 添加Docker服务部分
    local docker_service_count
    docker_service_count=$(jq '.docker_services | length' "$MONITORING_DATA_FILE")
    
    if [[ "$docker_service_count" -gt 0 ]]; then
        echo "        <div class=\"section\">"
        echo "            <h3>Docker服务状态</h3>"
        echo "            <table>"
        echo "                <tr><th>服务名称</th><th>状态</th><th>镜像</th><th>CPU使用率</th><th>内存使用率</th><th>重启次数</th></tr>"
        
        jq -r '.docker_services[] | 
            "                <tr>\n" +
            "                    <td>" + .name + "</td>\n" +
            "                    <td>" + (if (.status | test("Up")) then "<span class=\"status-healthy\">" + .status + "</span>" else "<span class=\"status-critical\">" + .status + "</span>" end) + "</td>\n" +
            "                    <td>" + .image + "</td>\n" +
            "                    <td>" + (if .cpu_usage then (.cpu_usage | tostring) + "%" else "N/A" end) + "</td>\n" +
            "                    <td>" + (if .memory_percent then (.memory_percent | tostring) + "%" else "N/A" end) + "</td>\n" +
            "                    <td>" + (.restart_count | tostring) + "</td>\n" +
            "                </tr>"' "$MONITORING_DATA_FILE"
        
        echo "            </table>"
        echo "        </div>"
    fi
    
    # 添加Kubernetes资源部分
    local k8s_resource_count
    k8s_resource_count=$(jq '.kubernetes_resources | length' "$MONITORING_DATA_FILE")
    
    if [[ "$k8s_resource_count" -gt 0 ]]; then
        echo "        <div class=\"section\">"
        echo "            <h3>Kubernetes资源状态</h3>"
        echo "            <table>"
        echo "                <tr><th>资源类型</th><th>名称</th><th>命名空间</th><th>状态</th><th>副本数</th><th>创建时间</th></tr>"
        
        jq -r '.kubernetes_resources[] | 
            "                <tr>\n" +
            "                    <td>" + (.type | ascii_upcase) + "</td>\n" +
            "                    <td>" + .name + "</td>\n" +
            "                    <td>" + .namespace + "</td>\n" +
            "                    <td>" + (
                if .type == "deployment" or .type == "statefulset" then
                    if .ready_replicas == .replicas then "<span class=\"status-healthy\">就绪</span>"
                    else "<span class=\"status-critical\">未就绪</span>" end
                elif .type == "pod" then
                    if .phase == "Running" and .ready == "True" then "<span class=\"status-healthy\">运行中</span>"
                    else "<span class=\"status-critical\">" + .phase + "</span>" end
                else "<span class=\"status-healthy\">活跃</span>" end
            ) + "</td>\n" +
            "                    <td>" + (
                if .type == "deployment" or .type == "statefulset" then
                    (.ready_replicas | tostring) + "/" + (.replicas | tostring)
                elif .type == "pod" then
                    "1/1"
                else "N/A" end
            ) + "</td>\n" +
            "                    <td>" + .created + "</td>\n" +
            "                </tr>"' "$MONITORING_DATA_FILE"
        
        echo "            </table>"
        echo "        </div>"
    fi
    
    # 添加健康检查部分
    local health_check_count
    health_check_count=$(jq '.health_checks | length' "$MONITORING_DATA_FILE")
    
    if [[ "$health_check_count" -gt 0 ]]; then
        echo "        <div class=\"section\">"
        echo "            <h3>服务健康检查</h3>"
        echo "            <table>"
        echo "                <tr><th>服务</th><th>端口状态</th><th>HTTP状态</th><th>命令状态</th><th>检查时间</th></tr>"
        
        jq -r '.health_checks[] | 
            "                <tr>\n" +
            "                    <td>" + .service + "</td>\n" +
            "                    <td>" + (if .port_status then (if .port_status == "open" then "<span class=\"status-healthy\">开放</span>" else "<span class=\"status-critical\">关闭</span>" end) else "N/A" end) + "</td>\n" +
            "                    <td>" + (if .http_status then (if .http_status == "healthy" then "<span class=\"status-healthy\">健康</span>" else "<span class=\"status-critical\">不健康</span>" end) else "N/A" end) + "</td>\n" +
            "                    <td>" + (if .command_status then (if .command_status == "success" then "<span class=\"status-healthy\">成功</span>" else "<span class=\"status-critical\">失败</span>" end) else "N/A" end) + "</td>\n" +
            "                    <td>" + .timestamp + "</td>\n" +
            "                </tr>"' "$MONITORING_DATA_FILE"
        
        echo "            </table>"
        echo "        </div>"
    fi
    
    # 添加告警部分
    local total_alerts
    total_alerts=$(jq '.alerts | length' "$MONITORING_DATA_FILE")
    
    if [[ "$total_alerts" -gt 0 ]]; then
        echo "        <div class=\"section\">"
        echo "            <h3>告警信息</h3>"
        
        jq -r '.alerts[] | 
            "            <div class=\"alert " + (if .type | IN("port_closed", "http_unhealthy", "deployment_not_ready", "statefulset_not_ready", "pod_not_ready") then "alert-critical" else "alert-warning" end) + "\">\n" +
            "                <strong>[" + .timestamp + "] " + .type + "</strong><br>\n" +
            (if .service then "                服务: " + .service + "<br>\n" else "" end) +
            (if .resource then "                资源: " + .resource + "<br>\n" else "" end) +
            (if .value then "                值: " + (.value | tostring) else "" end) +
            (if .threshold then " (阈值: " + (.threshold | tostring) + ")" else "" end) +
            (if .value or .threshold then "<br>\n" else "" end) +
            (if .port then "                端口: " + (.port | tostring) + "<br>\n" else "" end) +
            (if .url then "                URL: " + .url + "<br>\n" else "" end) +
            (if .error then "                错误: " + .error + "<br>\n" else "" end) +
            (if .drive then "                磁盘: " + .drive + "<br>\n" else "" end) +
            (if .usage_percent then "                使用率: " + (.usage_percent | tostring) + "%<br>\n" else "" end) +
            (if .ready and .desired then "                就绪副本: " + (.ready | tostring) + "/" + (.desired | tostring) + "<br>\n" else "" end) +
            (if .phase then "                状态: " + .phase + "<br>\n" else "" end) +
            (if .restart_count then "                重启次数: " + (.restart_count | tostring) + "<br>\n" else "" end) +
            "            </div>"' "$MONITORING_DATA_FILE"
        
        echo "        </div>"
    fi
    
    cat << 'EOF'
        <div class="section">
            <p class="timestamp">报告生成完成</p>
        </div>
    </div>
</body>
</html>
EOF
}

# 输出监控结果
output_monitoring_results() {
    case "$OUTPUT_FORMAT" in
        "console")
            if [[ -n "$OUTPUT_FILE" ]]; then
                output_console_format > "$OUTPUT_FILE"
                log "SUCCESS" "监控报告已保存到: $OUTPUT_FILE"
            else
                output_console_format
            fi
            ;;
        "json")
            if [[ -n "$OUTPUT_FILE" ]]; then
                output_json_format > "$OUTPUT_FILE"
                log "SUCCESS" "监控报告已保存到: $OUTPUT_FILE"
            else
                output_json_format
            fi
            ;;
        "html")
            if [[ -n "$OUTPUT_FILE" ]]; then
                output_html_format > "$OUTPUT_FILE"
                log "SUCCESS" "监控报告已保存到: $OUTPUT_FILE"
            else
                output_html_format
            fi
            ;;
    esac
}

# 执行单次监控
run_single_monitoring() {
    log "INFO" "开始执行AIOps平台监控..."
    
    # 初始化监控数据
    init_monitoring_data
    
    # 加载告警阈值
    load_alert_thresholds
    
    # 根据部署类型执行监控
    case "$DEPLOYMENT_TYPE" in
        "docker-compose")
            monitor_docker_compose_services
            ;;
        "kubernetes")
            monitor_kubernetes_resources
            ;;
        "all")
            monitor_docker_compose_services
            monitor_kubernetes_resources
            ;;
    esac
    
    # 执行健康检查
    invoke_health_checks
    
    # 获取系统资源使用情况
    get_system_resource_usage
    
    # 生成监控摘要
    generate_monitoring_summary
    
    # 输出监控结果
    output_monitoring_results
    
    log "SUCCESS" "监控执行完成"
}

# 持续监控模式
run_continuous_monitoring() {
    log "INFO" "启动持续监控模式，间隔: ${INTERVAL}秒"
    log "INFO" "按 Ctrl+C 停止监控"
    
    # 设置信号处理
    trap 'log "INFO" "停止持续监控"; exit 0' INT TERM
    
    local iteration=1
    
    while true; do
        echo
        log "INFO" "执行第 $iteration 次监控检查"
        
        run_single_monitoring
        
        log "INFO" "等待 ${INTERVAL} 秒后进行下次检查..."
        sleep "$INTERVAL"
        
        ((iteration++))
    done
}

# 主函数
main() {
    # 解析命令行参数
    parse_args "$@"
    
    # 检查依赖
    if ! command_exists jq; then
        log "ERROR" "jq命令不可用，请安装jq"
        exit 1
    fi
    
    # 检查bc命令（用于浮点数比较）
    if ! command_exists bc; then
        log "WARN" "bc命令不可用，某些数值比较功能可能受限"
    fi
    
    # 创建临时目录
    mkdir -p "$(dirname "$MONITORING_DATA_FILE")"
    
    # 执行监控
    if [[ "$CONTINUOUS" == true ]]; then
        run_continuous_monitoring
    else
        run_single_monitoring
    fi
    
    # 清理临时文件
    [[ -f "$MONITORING_DATA_FILE" ]] && rm -f "$MONITORING_DATA_FILE"
}

# 脚本入口点
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi