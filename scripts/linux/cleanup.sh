#!/bin/bash

# AIOps平台清理脚本 (Bash)
#
# 本脚本用于清理AIOps平台部署的服务和资源，包括Docker容器、Kubernetes资源、
# 本地文件等。支持选择性清理和强制清理模式。
#
# 用法:
#   ./cleanup.sh [选项]
#
# 选项:
#   -t, --type TYPE          部署类型：docker-compose, kubernetes, 或 all (默认: all)
#   -e, --env ENVIRONMENT    环境名称：development, staging, production, 或 all (默认: all)
#   -f, --force              强制清理，不询问确认
#   -d, --keep-data          保留数据卷和持久化存储
#   -i, --keep-images        保留Docker镜像
#   -n, --dry-run            预览模式，只显示将要执行的操作
#   -h, --help               显示帮助信息
#
# 示例:
#   ./cleanup.sh -t docker-compose -e development
#   ./cleanup.sh -t kubernetes -e production -f
#   ./cleanup.sh -t all -n
#
# 版本: 1.0.0
# 作者: AIOps Team
# 创建日期: 2024-01-01

set -euo pipefail

# 默认参数
DEPLOYMENT_TYPE="all"
ENVIRONMENT="all"
FORCE=false
KEEP_DATA=false
KEEP_IMAGES=false
DRY_RUN=false

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="aiops"
CLEANUP_ACTIONS=()
CONTAINERS_REMOVED=0
VOLUMES_REMOVED=0
IMAGES_REMOVED=0
NETWORKS_REMOVED=0
K8S_RESOURCES_REMOVED=0
FILES_REMOVED=0

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "[$timestamp] [${WHITE}INFO${NC}] $message"
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
    esac
}

# 显示帮助信息
show_help() {
    cat << EOF
AIOps平台清理脚本

用法: $0 [选项]

选项:
  -t, --type TYPE          部署类型：docker-compose, kubernetes, 或 all (默认: all)
  -e, --env ENVIRONMENT    环境名称：development, staging, production, 或 all (默认: all)
  -f, --force              强制清理，不询问确认
  -d, --keep-data          保留数据卷和持久化存储
  -i, --keep-images        保留Docker镜像
  -n, --dry-run            预览模式，只显示将要执行的操作
  -h, --help               显示帮助信息

示例:
  $0 -t docker-compose -e development
  $0 -t kubernetes -e production -f
  $0 -t all -n

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
                if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production|all)$ ]]; then
                    log "ERROR" "无效的环境名称: $ENVIRONMENT"
                    exit 1
                fi
                shift 2
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            -d|--keep-data)
                KEEP_DATA=true
                shift
                ;;
            -i|--keep-images)
                KEEP_IMAGES=true
                shift
                ;;
            -n|--dry-run)
                DRY_RUN=true
                shift
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

# 添加清理操作
add_cleanup_action() {
    local description="$1"
    local command="$2"
    local type="${3:-general}"
    
    CLEANUP_ACTIONS+=("$type|$description|$command")
}

# 执行命令（支持预览模式）
execute_command() {
    local command="$1"
    local description="${2:-}"
    local ignore_errors="${3:-false}"
    
    if [[ -n "$description" ]]; then
        log "INFO" "$description"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DEBUG" "[DRY RUN] $command"
        return 0
    fi
    
    log "DEBUG" "执行: $command"
    
    if [[ "$ignore_errors" == "true" ]]; then
        if ! eval "$command" 2>/dev/null; then
            log "WARN" "命令执行失败（已忽略）: $command"
            return 1
        fi
    else
        eval "$command"
    fi
    
    return 0
}

# 检查Docker是否可用
check_docker() {
    if command -v docker >/dev/null 2>&1 && docker version >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查Kubernetes是否可用
check_kubernetes() {
    if command -v kubectl >/dev/null 2>&1 && kubectl version --client >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 检查Helm是否可用
check_helm() {
    if command -v helm >/dev/null 2>&1 && helm version >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 获取Docker Compose项目名称
get_docker_compose_projects() {
    local projects=()
    
    if [[ "$ENVIRONMENT" == "all" ]]; then
        local environments=("development" "staging" "production")
    else
        local environments=("$ENVIRONMENT")
    fi
    
    for env in "${environments[@]}"; do
        projects+=("$PROJECT_NAME-$env")
    done
    
    projects+=("$PROJECT_NAME")  # 默认项目名
    
    # 去重并输出
    printf '%s\n' "${projects[@]}" | sort -u
}

# 清理Docker Compose资源
cleanup_docker_compose() {
    log "INFO" "开始清理Docker Compose资源..."
    
    if ! check_docker; then
        log "WARN" "Docker不可用，跳过Docker Compose清理"
        return
    fi
    
    local projects
    readarray -t projects < <(get_docker_compose_projects)
    
    for project in "${projects[@]}"; do
        log "INFO" "清理项目: $project"
        
        # 停止并删除容器
        add_cleanup_action "停止Docker Compose服务: $project" \
            "containers=\$(docker ps -a --filter \"label=com.docker.compose.project=$project\" --format \"{{.ID}}\" 2>/dev/null || true); \
             if [[ -n \"\$containers\" ]]; then \
                 docker stop \$containers 2>/dev/null || true; \
                 docker rm \$containers 2>/dev/null || true; \
                 CONTAINERS_REMOVED=\$((CONTAINERS_REMOVED + \$(echo \"\$containers\" | wc -w))); \
             fi" \
            "docker"
        
        # 删除网络
        add_cleanup_action "删除Docker网络: $project" \
            "networks=\$(docker network ls --filter \"label=com.docker.compose.project=$project\" --format \"{{.ID}}\" 2>/dev/null || true); \
             if [[ -n \"\$networks\" ]]; then \
                 docker network rm \$networks 2>/dev/null || true; \
                 NETWORKS_REMOVED=\$((NETWORKS_REMOVED + \$(echo \"\$networks\" | wc -w))); \
             fi" \
            "docker"
        
        # 删除卷（如果不保留数据）
        if [[ "$KEEP_DATA" != "true" ]]; then
            add_cleanup_action "删除Docker卷: $project" \
                "volumes=\$(docker volume ls --filter \"label=com.docker.compose.project=$project\" --format \"{{.Name}}\" 2>/dev/null || true); \
                 if [[ -n \"\$volumes\" ]]; then \
                     docker volume rm \$volumes 2>/dev/null || true; \
                     VOLUMES_REMOVED=\$((VOLUMES_REMOVED + \$(echo \"\$volumes\" | wc -w))); \
                 fi" \
                "docker"
        fi
    done
    
    # 清理孤立的容器
    add_cleanup_action "清理孤立的AIOps容器" \
        "orphan_containers=\$(docker ps -a --filter \"name=$PROJECT_NAME\" --format \"{{.ID}}\" 2>/dev/null || true); \
         if [[ -n \"\$orphan_containers\" ]]; then \
             docker stop \$orphan_containers 2>/dev/null || true; \
             docker rm \$orphan_containers 2>/dev/null || true; \
             CONTAINERS_REMOVED=\$((CONTAINERS_REMOVED + \$(echo \"\$orphan_containers\" | wc -w))); \
         fi" \
        "docker"
    
    # 清理未使用的镜像（如果不保留镜像）
    if [[ "$KEEP_IMAGES" != "true" ]]; then
        add_cleanup_action "清理AIOps相关镜像" \
            "images=\$(docker images --filter \"reference=*aiops*\" --format \"{{.ID}}\" 2>/dev/null || true); \
             if [[ -n \"\$images\" ]]; then \
                 docker rmi \$images 2>/dev/null || true; \
                 IMAGES_REMOVED=\$((IMAGES_REMOVED + \$(echo \"\$images\" | wc -w))); \
             fi" \
            "docker"
    fi
    
    log "SUCCESS" "Docker Compose资源清理完成"
}

# 获取Kubernetes命名空间
get_kubernetes_namespaces() {
    local namespaces=()
    
    if [[ "$ENVIRONMENT" == "all" ]]; then
        namespaces+=("aiops" "aiops-development" "aiops-staging" "aiops-production")
    else
        namespaces+=("aiops" "aiops-$ENVIRONMENT")
    fi
    
    # 去重并输出
    printf '%s\n' "${namespaces[@]}" | sort -u
}

# 清理Kubernetes资源
cleanup_kubernetes() {
    log "INFO" "开始清理Kubernetes资源..."
    
    if ! check_kubernetes; then
        log "WARN" "kubectl不可用，跳过Kubernetes清理"
        return
    fi
    
    local namespaces
    readarray -t namespaces < <(get_kubernetes_namespaces)
    
    for namespace in "${namespaces[@]}"; do
        log "INFO" "检查命名空间: $namespace"
        
        # 检查命名空间是否存在
        if ! kubectl get namespace "$namespace" >/dev/null 2>&1; then
            log "DEBUG" "命名空间 $namespace 不存在，跳过"
            continue
        fi
        
        # 使用Helm删除发布
        if check_helm; then
            add_cleanup_action "删除Helm发布: aiops (命名空间: $namespace)" \
                "releases=\$(helm list -n $namespace --short 2>/dev/null | grep -E '.*aiops.*' || true); \
                 for release in \$releases; do \
                     helm uninstall \"\$release\" -n $namespace 2>/dev/null || true; \
                     K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + 1)); \
                 done" \
                "kubernetes"
        fi
        
        # 删除所有资源
        add_cleanup_action "删除命名空间中的所有资源: $namespace" \
            "# 删除部署
             deployments=\$(kubectl get deployments -n $namespace --no-headers 2>/dev/null | awk '{print \$1}' || true); \
             if [[ -n \"\$deployments\" ]]; then \
                 kubectl delete deployments --all -n $namespace 2>/dev/null || true; \
                 K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + \$(echo \"\$deployments\" | wc -w))); \
             fi; \
             # 删除StatefulSet
             statefulsets=\$(kubectl get statefulsets -n $namespace --no-headers 2>/dev/null | awk '{print \$1}' || true); \
             if [[ -n \"\$statefulsets\" ]]; then \
                 kubectl delete statefulsets --all -n $namespace 2>/dev/null || true; \
                 K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + \$(echo \"\$statefulsets\" | wc -w))); \
             fi; \
             # 删除服务
             services=\$(kubectl get services -n $namespace --no-headers 2>/dev/null | grep -v kubernetes | awk '{print \$1}' || true); \
             if [[ -n \"\$services\" ]]; then \
                 kubectl delete services \$services -n $namespace 2>/dev/null || true; \
                 K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + \$(echo \"\$services\" | wc -w))); \
             fi; \
             # 删除ConfigMap和Secret
             kubectl delete configmaps --all -n $namespace 2>/dev/null || true; \
             kubectl delete secrets --all -n $namespace 2>/dev/null || true; \
             # 删除Ingress
             kubectl delete ingress --all -n $namespace 2>/dev/null || true" \
            "kubernetes"
        
        # 删除PVC（如果不保留数据）
        if [[ "$KEEP_DATA" != "true" ]]; then
            add_cleanup_action "删除PVC: $namespace" \
                "pvcs=\$(kubectl get pvc -n $namespace --no-headers 2>/dev/null | awk '{print \$1}' || true); \
                 if [[ -n \"\$pvcs\" ]]; then \
                     kubectl delete pvc --all -n $namespace 2>/dev/null || true; \
                     K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + \$(echo \"\$pvcs\" | wc -w))); \
                 fi" \
                "kubernetes"
        fi
        
        # 删除命名空间（如果不是默认命名空间）
        if [[ "$namespace" != "default" && "$namespace" != "kube-system" ]]; then
            add_cleanup_action "删除命名空间: $namespace" \
                "kubectl delete namespace $namespace 2>/dev/null || true; \
                 K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + 1))" \
                "kubernetes"
        fi
    done
    
    # 清理集群级资源
    add_cleanup_action "清理集群级AIOps资源" \
        "# 删除ClusterRole和ClusterRoleBinding
         cluster_roles=\$(kubectl get clusterroles --no-headers 2>/dev/null | grep aiops | awk '{print \$1}' || true); \
         if [[ -n \"\$cluster_roles\" ]]; then \
             kubectl delete clusterroles \$cluster_roles 2>/dev/null || true; \
             K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + \$(echo \"\$cluster_roles\" | wc -w))); \
         fi; \
         cluster_role_bindings=\$(kubectl get clusterrolebindings --no-headers 2>/dev/null | grep aiops | awk '{print \$1}' || true); \
         if [[ -n \"\$cluster_role_bindings\" ]]; then \
             kubectl delete clusterrolebindings \$cluster_role_bindings 2>/dev/null || true; \
             K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + \$(echo \"\$cluster_role_bindings\" | wc -w))); \
         fi" \
        "kubernetes"
    
    # 删除PV（如果不保留数据）
    if [[ "$KEEP_DATA" != "true" ]]; then
        add_cleanup_action "删除PV" \
            "pvs=\$(kubectl get pv --no-headers 2>/dev/null | grep aiops | awk '{print \$1}' || true); \
             if [[ -n \"\$pvs\" ]]; then \
                 kubectl delete pv \$pvs 2>/dev/null || true; \
                 K8S_RESOURCES_REMOVED=\$((K8S_RESOURCES_REMOVED + \$(echo \"\$pvs\" | wc -w))); \
             fi" \
            "kubernetes"
    fi
    
    log "SUCCESS" "Kubernetes资源清理完成"
}

# 清理本地文件
cleanup_local_files() {
    log "INFO" "开始清理本地文件..."
    
    local files_to_clean=(
        "$PROJECT_ROOT/generated"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/tmp"
        "$PROJECT_ROOT/.env*"
        "$PROJECT_ROOT/docker-compose.override.yml"
    )
    
    for path in "${files_to_clean[@]}"; do
        add_cleanup_action "删除文件/目录: $path" \
            "if [[ -e \"$path\" ]]; then \
                 if [[ -d \"$path\" ]]; then \
                     item_count=\$(find \"$path\" -type f | wc -l); \
                     rm -rf \"$path\"; \
                     FILES_REMOVED=\$((FILES_REMOVED + item_count)); \
                 else \
                     rm -f $path; \
                     FILES_REMOVED=\$((FILES_REMOVED + 1)); \
                 fi; \
                 log \"DEBUG\" \"已删除: $path\"; \
             else \
                 log \"DEBUG\" \"文件不存在: $path\"; \
             fi" \
            "files"
    done
    
    log "SUCCESS" "本地文件清理完成"
}

# 显示清理预览
show_cleanup_preview() {
    log "INFO" "清理预览"
    echo -e "${CYAN}============================================================${NC}"
    
    # 按类型分组显示
    local types=("docker" "kubernetes" "files" "general")
    
    for type in "${types[@]}"; do
        local found=false
        for action in "${CLEANUP_ACTIONS[@]}"; do
            local action_type=$(echo "$action" | cut -d'|' -f1)
            if [[ "$action_type" == "$type" ]]; then
                if [[ "$found" == "false" ]]; then
                    echo -e "${YELLOW}[${type^^}] 操作:${NC}"
                    found=true
                fi
                local description=$(echo "$action" | cut -d'|' -f2)
                echo -e "  ${GRAY}- $description${NC}"
            fi
        done
        if [[ "$found" == "true" ]]; then
            echo ""
        fi
    done
    
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${WHITE}总计 ${#CLEANUP_ACTIONS[@]} 个清理操作${NC}"
}

# 执行清理操作
execute_cleanup_actions() {
    log "INFO" "开始执行清理操作..."
    
    local total_actions=${#CLEANUP_ACTIONS[@]}
    local current_action=0
    
    for action in "${CLEANUP_ACTIONS[@]}"; do
        current_action=$((current_action + 1))
        local progress=$(( (current_action * 100) / total_actions ))
        
        local description=$(echo "$action" | cut -d'|' -f2)
        local command=$(echo "$action" | cut -d'|' -f3-)
        
        echo -ne "\r进度: [$current_action/$total_actions] ($progress%) - $description"
        
        if ! execute_command "$command" "" "true"; then
            echo ""
            log "ERROR" "清理操作失败: $description"
            if [[ "$FORCE" != "true" ]]; then
                echo -n "是否继续执行剩余操作？(y/N): "
                read -r response
                if [[ "$response" != "y" && "$response" != "Y" ]]; then
                    log "WARN" "清理操作已中止"
                    return
                fi
            fi
        fi
    done
    
    echo ""
}

# 显示清理统计
show_cleanup_stats() {
    log "SUCCESS" "清理统计"
    echo -e "${GREEN}========================================${NC}"
    
    echo -e "${WHITE}Docker容器已删除: $CONTAINERS_REMOVED${NC}"
    echo -e "${WHITE}Docker卷已删除: $VOLUMES_REMOVED${NC}"
    echo -e "${WHITE}Docker镜像已删除: $IMAGES_REMOVED${NC}"
    echo -e "${WHITE}Docker网络已删除: $NETWORKS_REMOVED${NC}"
    echo -e "${WHITE}Kubernetes资源已删除: $K8S_RESOURCES_REMOVED${NC}"
    echo -e "${WHITE}本地文件已删除: $FILES_REMOVED${NC}"
    
    local total_items=$((CONTAINERS_REMOVED + VOLUMES_REMOVED + IMAGES_REMOVED + NETWORKS_REMOVED + K8S_RESOURCES_REMOVED + FILES_REMOVED))
    echo -e "${CYAN}总计删除项目: $total_items${NC}"
    
    echo -e "${GREEN}========================================${NC}"
}

# 确认清理操作
confirm_cleanup() {
    if [[ "$FORCE" == "true" || "$DRY_RUN" == "true" ]]; then
        return 0
    fi
    
    echo ""
    echo -e "${RED}警告: 此操作将删除以下资源:${NC}"
    
    if [[ "$DEPLOYMENT_TYPE" == "docker-compose" || "$DEPLOYMENT_TYPE" == "all" ]]; then
        echo -e "  ${YELLOW}- Docker容器、网络${NC}"
        if [[ "$KEEP_DATA" != "true" ]]; then
            echo -e "  ${YELLOW}- Docker卷和数据${NC}"
        fi
        if [[ "$KEEP_IMAGES" != "true" ]]; then
            echo -e "  ${YELLOW}- Docker镜像${NC}"
        fi
    fi
    
    if [[ "$DEPLOYMENT_TYPE" == "kubernetes" || "$DEPLOYMENT_TYPE" == "all" ]]; then
        echo -e "  ${YELLOW}- Kubernetes资源${NC}"
        if [[ "$KEEP_DATA" != "true" ]]; then
            echo -e "  ${YELLOW}- 持久化卷和数据${NC}"
        fi
    fi
    
    echo -e "  ${YELLOW}- 本地生成的文件${NC}"
    
    echo ""
    echo -n "确定要继续吗？(y/N): "
    read -r response
    
    [[ "$response" == "y" || "$response" == "Y" ]]
}

# 主函数
main() {
    log "INFO" "AIOps平台清理工具"
    log "INFO" "部署类型: $DEPLOYMENT_TYPE"
    log "INFO" "环境: $ENVIRONMENT"
    log "INFO" "保留数据: $KEEP_DATA"
    log "INFO" "保留镜像: $KEEP_IMAGES"
    log "INFO" "预览模式: $DRY_RUN"
    log "INFO" "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 准备清理操作
    case "$DEPLOYMENT_TYPE" in
        "docker-compose")
            cleanup_docker_compose
            ;;
        "kubernetes")
            cleanup_kubernetes
            ;;
        "all")
            cleanup_docker_compose
            cleanup_kubernetes
            ;;
    esac
    
    # 总是清理本地文件
    cleanup_local_files
    
    # 显示预览
    if [[ ${#CLEANUP_ACTIONS[@]} -eq 0 ]]; then
        log "WARN" "没有找到需要清理的资源"
        return
    fi
    
    show_cleanup_preview
    
    # 确认操作
    if ! confirm_cleanup; then
        log "WARN" "清理操作已取消"
        return
    fi
    
    # 执行清理
    if [[ "$DRY_RUN" != "true" ]]; then
        execute_cleanup_actions
        show_cleanup_stats
    else
        log "INFO" "预览模式完成，未执行实际清理操作"
    fi
    
    log "INFO" "完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 解析参数并执行主函数
parse_args "$@"
main