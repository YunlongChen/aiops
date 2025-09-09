#!/bin/bash

# AIOps平台环境检查脚本 (Bash)
#
# 描述: 本脚本用于检查系统环境是否满足AIOps平台的部署要求，包括硬件资源、软件依赖、网络配置等。
#
# 参数:
#   -t, --type <type>     部署类型：docker 或 kubernetes 或 all (默认: all)
#   -d, --detailed        显示详细检查信息
#   -f, --fix            尝试自动修复发现的问题
#   -h, --help           显示帮助信息
#
# 示例:
#   ./check-environment.sh -t docker
#   ./check-environment.sh -t kubernetes -d -f
#
# 版本: 1.0.0
# 作者: AIOps Team
# 创建日期: 2024-01-01

set -euo pipefail

# 全局变量
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_TYPE="all"
DETAILED=false
FIX=false
CHECK_RESULTS=()
FIX_ACTIONS=()

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# 检查结果计数器
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

# 显示帮助信息
show_help() {
    cat << EOF
AIOps平台环境检查工具

用法: $0 [选项]

选项:
    -t, --type <type>     部署类型：docker, kubernetes, all (默认: all)
    -d, --detailed        显示详细检查信息
    -f, --fix            尝试自动修复发现的问题
    -h, --help           显示此帮助信息

示例:
    $0 -t docker
    $0 -t kubernetes -d -f
    $0 --type all --detailed --fix

EOF
}

# 解析命令行参数
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                DEPLOYMENT_TYPE="$2"
                if [[ ! "$DEPLOYMENT_TYPE" =~ ^(docker|kubernetes|all)$ ]]; then
                    echo -e "${RED}错误: 无效的部署类型 '$DEPLOYMENT_TYPE'${NC}" >&2
                    echo "有效选项: docker, kubernetes, all" >&2
                    exit 1
                fi
                shift 2
                ;;
            -d|--detailed)
                DETAILED=true
                shift
                ;;
            -f|--fix)
                FIX=true
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}错误: 未知选项 '$1'${NC}" >&2
                show_help
                exit 1
                ;;
        esac
    done
}

# 添加检查结果
add_check_result() {
    local category="$1"
    local item="$2"
    local status="$3"
    local message="$4"
    local recommendation="${5:-}"
    local fix_action="${6:-}"
    
    # 更新计数器
    case "$status" in
        "PASS") ((PASS_COUNT++)) ;;
        "WARN") ((WARN_COUNT++)) ;;
        "FAIL") ((FAIL_COUNT++)) ;;
    esac
    
    # 选择颜色
    local color
    case "$status" in
        "PASS") color="$GREEN" ;;
        "WARN") color="$YELLOW" ;;
        "FAIL") color="$RED" ;;
        *) color="$NC" ;;
    esac
    
    # 实时输出
    echo -e "${color}[$status] $category - $item: $message${NC}"
    
    if [[ "$DETAILED" == "true" && -n "$recommendation" ]]; then
        echo -e "${GRAY}    建议: $recommendation${NC}"
    fi
    
    # 保存结果
    local result="{\"category\":\"$category\",\"item\":\"$item\",\"status\":\"$status\",\"message\":\"$message\",\"recommendation\":\"$recommendation\",\"fix_action\":\"$fix_action\"}"
    CHECK_RESULTS+=("$result")
    
    if [[ -n "$fix_action" ]]; then
        FIX_ACTIONS+=("$fix_action")
    fi
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查服务是否运行
service_running() {
    if command_exists systemctl; then
        systemctl is-active --quiet "$1" 2>/dev/null
    elif command_exists service; then
        service "$1" status >/dev/null 2>&1
    else
        return 1
    fi
}

# 获取系统信息
get_os_info() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "$NAME $VERSION"
    elif command_exists lsb_release; then
        lsb_release -d | cut -f2
    elif [[ -f /etc/redhat-release ]]; then
        cat /etc/redhat-release
    elif [[ -f /etc/debian_version ]]; then
        echo "Debian $(cat /etc/debian_version)"
    else
        echo "Unknown"
    fi
}

# 检查系统信息
test_system_info() {
    echo -e "\n${CYAN}=== 系统信息检查 ===${NC}"
    
    # 操作系统
    local os_info
    os_info=$(get_os_info)
    add_check_result "系统" "操作系统" "PASS" "$os_info"
    
    # 主机名
    local hostname
    hostname=$(hostname)
    add_check_result "系统" "主机名" "PASS" "$hostname"
    
    # 系统架构
    local arch
    arch=$(uname -m)
    if [[ "$arch" == "x86_64" || "$arch" == "amd64" ]]; then
        add_check_result "系统" "架构" "PASS" "64位系统 ($arch)"
    else
        add_check_result "系统" "架构" "WARN" "$arch" "推荐使用x86_64架构以获得更好的兼容性"
    fi
    
    # 内核版本
    local kernel_version
    kernel_version=$(uname -r)
    add_check_result "系统" "内核版本" "PASS" "$kernel_version"
    
    # 系统负载
    if [[ -f /proc/loadavg ]]; then
        local load_avg
        load_avg=$(cat /proc/loadavg | cut -d' ' -f1-3)
        add_check_result "系统" "系统负载" "PASS" "$load_avg (1min 5min 15min)"
    fi
    
    # 系统运行时间
    local uptime_info
    if command_exists uptime; then
        uptime_info=$(uptime -p 2>/dev/null || uptime | sed 's/.*up \([^,]*\).*/\1/')
        add_check_result "系统" "运行时间" "PASS" "$uptime_info"
    fi
}

# 检查硬件资源
test_hardware_resources() {
    echo -e "\n${CYAN}=== 硬件资源检查 ===${NC}"
    
    # CPU检查
    local cpu_cores
    if [[ -f /proc/cpuinfo ]]; then
        cpu_cores=$(grep -c ^processor /proc/cpuinfo)
        local cpu_model
        cpu_model=$(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^ *//')
        
        if [[ $cpu_cores -ge 8 ]]; then
            add_check_result "硬件" "CPU核心" "PASS" "$cpu_cores 核心 - $cpu_model"
        elif [[ $cpu_cores -ge 4 ]]; then
            add_check_result "硬件" "CPU核心" "WARN" "$cpu_cores 核心 - $cpu_model" "推荐8核心或更多以获得最佳性能"
        else
            add_check_result "硬件" "CPU核心" "FAIL" "$cpu_cores 核心 - $cpu_model" "至少需要4核心CPU"
        fi
    else
        add_check_result "硬件" "CPU信息" "WARN" "无法获取CPU信息" "检查/proc/cpuinfo文件"
    fi
    
    # 内存检查
    if [[ -f /proc/meminfo ]]; then
        local total_memory_kb
        total_memory_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        local total_memory_gb
        total_memory_gb=$((total_memory_kb / 1024 / 1024))
        
        local available_memory_kb
        available_memory_kb=$(grep MemAvailable /proc/meminfo | awk '{print $2}' || grep MemFree /proc/meminfo | awk '{print $2}')
        local available_memory_gb
        available_memory_gb=$((available_memory_kb / 1024 / 1024))
        
        if [[ $total_memory_gb -ge 32 ]]; then
            add_check_result "硬件" "内存" "PASS" "${total_memory_gb}GB 总计 / ${available_memory_gb}GB 可用"
        elif [[ $total_memory_gb -ge 16 ]]; then
            add_check_result "硬件" "内存" "WARN" "${total_memory_gb}GB 总计 / ${available_memory_gb}GB 可用" "推荐32GB或更多内存以支持大规模部署"
        elif [[ $total_memory_gb -ge 8 ]]; then
            add_check_result "硬件" "内存" "WARN" "${total_memory_gb}GB 总计 / ${available_memory_gb}GB 可用" "推荐16GB或更多内存"
        else
            add_check_result "硬件" "内存" "FAIL" "${total_memory_gb}GB 总计 / ${available_memory_gb}GB 可用" "至少需要8GB内存"
        fi
    else
        add_check_result "硬件" "内存信息" "WARN" "无法获取内存信息" "检查/proc/meminfo文件"
    fi
    
    # 磁盘空间检查
    local disk_info
    if command_exists df; then
        disk_info=$(df -h / | tail -1)
        local available_space
        available_space=$(echo "$disk_info" | awk '{print $4}' | sed 's/G//')
        local total_space
        total_space=$(echo "$disk_info" | awk '{print $2}' | sed 's/G//')
        
        # 处理不同的单位
        if [[ "$available_space" =~ ^[0-9]+$ ]]; then
            if [[ $available_space -ge 200 ]]; then
                add_check_result "硬件" "磁盘空间" "PASS" "可用: ${available_space}GB / 总计: ${total_space}"
            elif [[ $available_space -ge 100 ]]; then
                add_check_result "硬件" "磁盘空间" "WARN" "可用: ${available_space}GB / 总计: ${total_space}" "推荐至少200GB可用空间"
            elif [[ $available_space -ge 50 ]]; then
                add_check_result "硬件" "磁盘空间" "WARN" "可用: ${available_space}GB / 总计: ${total_space}" "推荐至少100GB可用空间"
            else
                add_check_result "硬件" "磁盘空间" "FAIL" "可用: ${available_space}GB / 总计: ${total_space}" "至少需要50GB可用空间"
            fi
        else
            add_check_result "硬件" "磁盘空间" "PASS" "可用: $available_space / 总计: $total_space"
        fi
    else
        add_check_result "硬件" "磁盘信息" "WARN" "无法获取磁盘信息" "安装df命令"
    fi
    
    # 检查存储类型（SSD检测）
    if [[ -d /sys/block ]]; then
        local ssd_found=false
        for disk in /sys/block/sd*; do
            if [[ -f "$disk/queue/rotational" ]]; then
                local rotational
                rotational=$(cat "$disk/queue/rotational")
                if [[ "$rotational" == "0" ]]; then
                    ssd_found=true
                    break
                fi
            fi
        done
        
        if [[ "$ssd_found" == "true" ]]; then
            add_check_result "硬件" "存储类型" "PASS" "检测到SSD存储"
        else
            add_check_result "硬件" "存储类型" "WARN" "未检测到SSD存储" "推荐使用SSD以获得更好的I/O性能"
        fi
    fi
}

# 检查网络配置
test_network_configuration() {
    echo -e "\n${CYAN}=== 网络配置检查 ===${NC}"
    
    # 检查网络接口
    if command_exists ip; then
        local active_interfaces
        active_interfaces=$(ip link show | grep "state UP" | wc -l)
        
        if [[ $active_interfaces -gt 0 ]]; then
            add_check_result "网络" "网络接口" "PASS" "$active_interfaces 个活动接口"
            
            if [[ "$DETAILED" == "true" ]]; then
                while IFS= read -r line; do
                    local interface
                    interface=$(echo "$line" | cut -d: -f2 | sed 's/^ *//')
                    add_check_result "网络" "接口-$interface" "PASS" "活动状态"
                done < <(ip link show | grep "state UP")
            fi
        else
            add_check_result "网络" "网络接口" "FAIL" "没有活动的网络接口" "检查网络连接"
        fi
    else
        add_check_result "网络" "网络工具" "WARN" "ip命令不可用" "安装iproute2包"
    fi
    
    # 检查DNS配置
    if [[ -f /etc/resolv.conf ]]; then
        local dns_servers
        dns_servers=$(grep -c "^nameserver" /etc/resolv.conf)
        
        if [[ $dns_servers -gt 0 ]]; then
            add_check_result "网络" "DNS配置" "PASS" "$dns_servers 个DNS服务器已配置"
        else
            add_check_result "网络" "DNS配置" "WARN" "未配置DNS服务器" "检查/etc/resolv.conf文件"
        fi
    else
        add_check_result "网络" "DNS配置" "WARN" "resolv.conf文件不存在" "检查DNS配置"
    fi
    
    # 检查防火墙状态
    if command_exists ufw; then
        local ufw_status
        ufw_status=$(ufw status | head -1 | awk '{print $2}')
        
        if [[ "$ufw_status" == "active" ]]; then
            add_check_result "网络" "UFW防火墙" "WARN" "防火墙已启用" "可能需要配置防火墙规则以允许AIOps服务通信"
        else
            add_check_result "网络" "UFW防火墙" "PASS" "防火墙已禁用或未配置"
        fi
    elif command_exists firewall-cmd; then
        if service_running firewalld; then
            add_check_result "网络" "Firewalld" "WARN" "防火墙服务运行中" "可能需要配置防火墙规则以允许AIOps服务通信"
        else
            add_check_result "网络" "Firewalld" "PASS" "防火墙服务未运行"
        fi
    elif command_exists iptables; then
        local iptables_rules
        iptables_rules=$(iptables -L | wc -l)
        
        if [[ $iptables_rules -gt 8 ]]; then
            add_check_result "网络" "iptables" "WARN" "检测到iptables规则" "可能需要配置防火墙规则以允许AIOps服务通信"
        else
            add_check_result "网络" "iptables" "PASS" "默认iptables配置"
        fi
    fi
    
    # 检查端口占用
    local required_ports=(80 443 3000 5601 9090 9200 6379 5432)
    local occupied_ports=()
    
    for port in "${required_ports[@]}"; do
        if command_exists netstat; then
            if netstat -tuln | grep -q ":$port "; then
                occupied_ports+=("$port")
            fi
        elif command_exists ss; then
            if ss -tuln | grep -q ":$port "; then
                occupied_ports+=("$port")
            fi
        fi
    done
    
    if [[ ${#occupied_ports[@]} -eq 0 ]]; then
        add_check_result "网络" "端口可用性" "PASS" "所有必需端口都可用"
    else
        local occupied_list
        occupied_list=$(IFS=', '; echo "${occupied_ports[*]}")
        add_check_result "网络" "端口可用性" "WARN" "以下端口被占用: $occupied_list" "停止占用这些端口的服务或修改AIOps配置"
    fi
    
    # 网络连通性测试
    if command_exists ping; then
        if ping -c 1 -W 3 8.8.8.8 >/dev/null 2>&1; then
            add_check_result "网络" "外网连通性" "PASS" "可以访问外网"
        else
            add_check_result "网络" "外网连通性" "WARN" "无法访问外网" "检查网络连接和防火墙设置"
        fi
    fi
}

# 检查Docker环境
test_docker_environment() {
    echo -e "\n${CYAN}=== Docker环境检查 ===${NC}"
    
    # 检查Docker是否安装
    if command_exists docker; then
        local docker_version
        docker_version=$(docker --version 2>/dev/null || echo "未知版本")
        
        if [[ "$docker_version" =~ Docker\ version\ ([0-9]+\.[0-9]+) ]]; then
            local version="${BASH_REMATCH[1]}"
            if awk "BEGIN {exit !($version >= 20.10)}"; then
                add_check_result "Docker" "版本" "PASS" "$docker_version"
            else
                add_check_result "Docker" "版本" "WARN" "$docker_version" "推荐升级到20.10.0或更新版本" "upgrade-docker"
            fi
        else
            add_check_result "Docker" "版本" "WARN" "无法解析版本信息: $docker_version" "检查Docker安装"
        fi
    else
        add_check_result "Docker" "安装" "FAIL" "Docker未安装" "安装Docker" "install-docker"
        return
    fi
    
    # 检查Docker服务状态
    if docker info >/dev/null 2>&1; then
        add_check_result "Docker" "服务状态" "PASS" "Docker服务运行正常"
        
        # 检查Docker资源配置
        local docker_info
        docker_info=$(docker info 2>/dev/null)
        
        # 检查内存配置
        if echo "$docker_info" | grep -q "Total Memory"; then
            local docker_memory
            docker_memory=$(echo "$docker_info" | grep "Total Memory" | awk '{print $3}' | sed 's/GiB//')
            
            if awk "BEGIN {exit !($docker_memory >= 8)}"; then
                add_check_result "Docker" "内存配置" "PASS" "${docker_memory}GB"
            else
                add_check_result "Docker" "内存配置" "WARN" "${docker_memory}GB" "推荐分配至少8GB内存给Docker" "increase-docker-memory"
            fi
        fi
        
        # 检查CPU配置
        if echo "$docker_info" | grep -q "CPUs"; then
            local docker_cpus
            docker_cpus=$(echo "$docker_info" | grep "CPUs" | awk '{print $2}')
            
            if [[ $docker_cpus -ge 4 ]]; then
                add_check_result "Docker" "CPU配置" "PASS" "${docker_cpus} CPUs"
            else
                add_check_result "Docker" "CPU配置" "WARN" "${docker_cpus} CPUs" "推荐分配至少4个CPU给Docker" "increase-docker-cpu"
            fi
        fi
        
        # 检查存储驱动
        local storage_driver
        storage_driver=$(echo "$docker_info" | grep "Storage Driver" | awk '{print $3}')
        
        if [[ "$storage_driver" == "overlay2" ]]; then
            add_check_result "Docker" "存储驱动" "PASS" "$storage_driver"
        else
            add_check_result "Docker" "存储驱动" "WARN" "$storage_driver" "推荐使用overlay2存储驱动"
        fi
        
    else
        add_check_result "Docker" "服务状态" "FAIL" "Docker服务未运行" "启动Docker服务" "start-docker"
    fi
    
    # 检查Docker Compose
    if command_exists docker-compose; then
        local compose_version
        compose_version=$(docker-compose --version 2>/dev/null || echo "未知版本")
        add_check_result "Docker" "Docker Compose" "PASS" "$compose_version"
    elif docker compose version >/dev/null 2>&1; then
        local compose_version
        compose_version=$(docker compose version 2>/dev/null || echo "未知版本")
        add_check_result "Docker" "Docker Compose" "PASS" "$compose_version (内置)"
    else
        add_check_result "Docker" "Docker Compose" "FAIL" "Docker Compose未安装" "安装Docker Compose" "install-docker-compose"
    fi
    
    # 检查Docker用户权限
    if groups "$USER" | grep -q docker; then
        add_check_result "Docker" "用户权限" "PASS" "用户在docker组中"
    else
        add_check_result "Docker" "用户权限" "WARN" "用户不在docker组中" "将用户添加到docker组" "add-user-to-docker-group"
    fi
}

# 检查Kubernetes环境
test_kubernetes_environment() {
    echo -e "\n${CYAN}=== Kubernetes环境检查 ===${NC}"
    
    # 检查kubectl
    if command_exists kubectl; then
        local kubectl_version
        kubectl_version=$(kubectl version --client --short 2>/dev/null || kubectl version --client 2>/dev/null | head -1)
        add_check_result "Kubernetes" "kubectl" "PASS" "$kubectl_version"
    else
        add_check_result "Kubernetes" "kubectl" "FAIL" "kubectl未安装" "安装kubectl" "install-kubectl"
        return
    fi
    
    # 检查集群连接
    if kubectl cluster-info >/dev/null 2>&1; then
        add_check_result "Kubernetes" "集群连接" "PASS" "集群连接正常"
        
        # 检查节点状态
        local nodes_info
        nodes_info=$(kubectl get nodes --no-headers 2>/dev/null)
        
        if [[ -n "$nodes_info" ]]; then
            local total_nodes
            total_nodes=$(echo "$nodes_info" | wc -l)
            local ready_nodes
            ready_nodes=$(echo "$nodes_info" | grep -c "Ready" || echo "0")
            
            if [[ $ready_nodes -eq $total_nodes ]]; then
                add_check_result "Kubernetes" "节点状态" "PASS" "$ready_nodes/$total_nodes 节点就绪"
            else
                add_check_result "Kubernetes" "节点状态" "WARN" "$ready_nodes/$total_nodes 节点就绪" "检查未就绪的节点"
            fi
            
            # 详细节点信息
            if [[ "$DETAILED" == "true" ]]; then
                while IFS= read -r line; do
                    local node_name
                    node_name=$(echo "$line" | awk '{print $1}')
                    local node_status
                    node_status=$(echo "$line" | awk '{print $2}')
                    local node_role
                    node_role=$(echo "$line" | awk '{print $3}')
                    
                    if [[ "$node_status" == "Ready" ]]; then
                        add_check_result "Kubernetes" "节点-$node_name" "PASS" "$node_status ($node_role)"
                    else
                        add_check_result "Kubernetes" "节点-$node_name" "WARN" "$node_status ($node_role)" "检查节点状态"
                    fi
                done <<< "$nodes_info"
            fi
        else
            add_check_result "Kubernetes" "节点状态" "FAIL" "无法获取节点信息" "检查集群配置"
        fi
        
        # 检查集群资源
        if kubectl top nodes >/dev/null 2>&1; then
            add_check_result "Kubernetes" "资源监控" "PASS" "metrics-server可用"
        else
            add_check_result "Kubernetes" "资源监控" "WARN" "metrics-server不可用" "安装metrics-server以启用资源监控" "install-metrics-server"
        fi
        
        # 检查存储类
        local storage_classes
        storage_classes=$(kubectl get storageclass --no-headers 2>/dev/null | wc -l)
        
        if [[ $storage_classes -gt 0 ]]; then
            add_check_result "Kubernetes" "存储类" "PASS" "$storage_classes 个存储类可用"
        else
            add_check_result "Kubernetes" "存储类" "WARN" "没有可用的存储类" "配置存储类以支持持久卷"
        fi
        
    else
        add_check_result "Kubernetes" "集群连接" "FAIL" "无法连接到集群" "检查kubeconfig配置" "configure-kubeconfig"
    fi
    
    # 检查Helm
    if command_exists helm; then
        local helm_version
        helm_version=$(helm version --short 2>/dev/null || helm version 2>/dev/null | head -1)
        
        if [[ "$helm_version" =~ v([0-9]+\.[0-9]+) ]]; then
            local version="${BASH_REMATCH[1]}"
            if awk "BEGIN {exit !($version >= 3.2)}"; then
                add_check_result "Kubernetes" "Helm" "PASS" "$helm_version"
            else
                add_check_result "Kubernetes" "Helm" "WARN" "$helm_version" "推荐升级到3.2.0或更新版本" "update-helm"
            fi
        else
            add_check_result "Kubernetes" "Helm" "PASS" "$helm_version"
        fi
    else
        add_check_result "Kubernetes" "Helm" "FAIL" "Helm未安装" "安装Helm" "install-helm"
    fi
}

# 检查Shell环境
test_shell_environment() {
    echo -e "\n${CYAN}=== Shell环境检查 ===${NC}"
    
    # 检查Bash版本
    local bash_version="$BASH_VERSION"
    local major_version
    major_version=$(echo "$bash_version" | cut -d. -f1)
    
    if [[ $major_version -ge 4 ]]; then
        add_check_result "Shell" "Bash版本" "PASS" "Bash $bash_version"
    else
        add_check_result "Shell" "Bash版本" "WARN" "Bash $bash_version" "推荐升级到Bash 4.0或更新版本"
    fi
    
    # 检查必需工具
    local required_tools=("curl" "wget" "jq" "yq" "git")
    
    for tool in "${required_tools[@]}"; do
        if command_exists "$tool"; then
            local tool_version
            case "$tool" in
                "curl") tool_version=$(curl --version | head -1) ;;
                "wget") tool_version=$(wget --version | head -1) ;;
                "jq") tool_version=$(jq --version) ;;
                "yq") tool_version=$(yq --version) ;;
                "git") tool_version=$(git --version) ;;
                *) tool_version="已安装" ;;
            esac
            add_check_result "Shell" "工具-$tool" "PASS" "$tool_version"
        else
            add_check_result "Shell" "工具-$tool" "WARN" "未安装" "安装$tool以支持脚本功能" "install-$tool"
        fi
    done
    
    # 检查包管理器
    local package_managers=("apt" "yum" "dnf" "pacman" "zypper")
    local found_pm=false
    
    for pm in "${package_managers[@]}"; do
        if command_exists "$pm"; then
            add_check_result "Shell" "包管理器" "PASS" "$pm 可用"
            found_pm=true
            break
        fi
    done
    
    if [[ "$found_pm" == "false" ]]; then
        add_check_result "Shell" "包管理器" "WARN" "未检测到标准包管理器" "可能影响自动修复功能"
    fi
}

# 自动修复功能
invoke_auto_fix() {
    echo -e "\n${CYAN}=== 自动修复 ===${NC}"
    
    local fixable_count=0
    for result in "${CHECK_RESULTS[@]}"; do
        local fix_action
        fix_action=$(echo "$result" | grep -o '"fix_action":"[^"]*"' | cut -d'"' -f4)
        if [[ -n "$fix_action" ]]; then
            ((fixable_count++))
        fi
    done
    
    if [[ $fixable_count -eq 0 ]]; then
        echo -e "${GREEN}没有可自动修复的问题${NC}"
        return
    fi
    
    echo -e "${YELLOW}发现 $fixable_count 个可修复的问题:${NC}"
    
    for result in "${CHECK_RESULTS[@]}"; do
        local category
        category=$(echo "$result" | grep -o '"category":"[^"]*"' | cut -d'"' -f4)
        local item
        item=$(echo "$result" | grep -o '"item":"[^"]*"' | cut -d'"' -f4)
        local status
        status=$(echo "$result" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        local fix_action
        fix_action=$(echo "$result" | grep -o '"fix_action":"[^"]*"' | cut -d'"' -f4)
        
        if [[ "$status" =~ ^(WARN|FAIL)$ && -n "$fix_action" ]]; then
            echo -e "${YELLOW}修复: $category - $item${NC}"
            
            case "$fix_action" in
                "install-docker")
                    echo -e "${GRAY}  正在安装Docker...${NC}"
                    if command_exists apt; then
                        sudo apt update && sudo apt install -y docker.io
                    elif command_exists yum; then
                        sudo yum install -y docker
                    elif command_exists dnf; then
                        sudo dnf install -y docker
                    else
                        echo -e "${GRAY}  请手动安装Docker${NC}"
                    fi
                    ;;
                    
                "start-docker")
                    echo -e "${GRAY}  正在启动Docker服务...${NC}"
                    if command_exists systemctl; then
                        sudo systemctl start docker
                        sudo systemctl enable docker
                    elif command_exists service; then
                        sudo service docker start
                    fi
                    ;;
                    
                "install-kubectl")
                    echo -e "${GRAY}  正在安装kubectl...${NC}"
                    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
                    chmod +x kubectl
                    sudo mv kubectl /usr/local/bin/
                    ;;
                    
                "install-helm")
                    echo -e "${GRAY}  正在安装Helm...${NC}"
                    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
                    ;;
                    
                "add-user-to-docker-group")
                    echo -e "${GRAY}  正在将用户添加到docker组...${NC}"
                    sudo usermod -aG docker "$USER"
                    echo -e "${GRAY}  请重新登录以使更改生效${NC}"
                    ;;
                    
                install-*)
                    local tool
                    tool=$(echo "$fix_action" | sed 's/install-//')
                    echo -e "${GRAY}  正在安装 $tool...${NC}"
                    
                    if command_exists apt; then
                        sudo apt update && sudo apt install -y "$tool"
                    elif command_exists yum; then
                        sudo yum install -y "$tool"
                    elif command_exists dnf; then
                        sudo dnf install -y "$tool"
                    elif command_exists pacman; then
                        sudo pacman -S --noconfirm "$tool"
                    else
                        echo -e "${GRAY}  请手动安装 $tool${NC}"
                    fi
                    ;;
                    
                *)
                    echo -e "${GRAY}  执行: $fix_action${NC}"
                    eval "$fix_action" || echo -e "${RED}  修复失败${NC}"
                    ;;
            esac
            
            echo -e "${GREEN}  ✓ 修复完成${NC}"
        fi
    done
}

# 生成报告
generate_report() {
    echo -e "\n${CYAN}=== 检查报告 ===${NC}"
    
    local total_count=$((PASS_COUNT + WARN_COUNT + FAIL_COUNT))
    
    echo -e "检查项目总数: $total_count"
    echo -e "${GREEN}通过: $PASS_COUNT${NC}"
    echo -e "${YELLOW}警告: $WARN_COUNT${NC}"
    echo -e "${RED}失败: $FAIL_COUNT${NC}"
    
    # 按类别分组显示
    local categories=()
    for result in "${CHECK_RESULTS[@]}"; do
        local category
        category=$(echo "$result" | grep -o '"category":"[^"]*"' | cut -d'"' -f4)
        if [[ ! " ${categories[*]} " =~ \ $category\  ]]; then
            categories+=("$category")
        fi
    done
    
    for category in "${categories[@]}"; do
        echo -e "\n${MAGENTA}--- $category ---${NC}"
        
        for result in "${CHECK_RESULTS[@]}"; do
            local result_category
            result_category=$(echo "$result" | grep -o '"category":"[^"]*"' | cut -d'"' -f4)
            
            if [[ "$result_category" == "$category" ]]; then
                local item
                item=$(echo "$result" | grep -o '"item":"[^"]*"' | cut -d'"' -f4)
                local status
                status=$(echo "$result" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
                local message
                message=$(echo "$result" | grep -o '"message":"[^"]*"' | cut -d'"' -f4)
                local recommendation
                recommendation=$(echo "$result" | grep -o '"recommendation":"[^"]*"' | cut -d'"' -f4)
                
                local color
                case "$status" in
                    "PASS") color="$GREEN" ;;
                    "WARN") color="$YELLOW" ;;
                    "FAIL") color="$RED" ;;
                esac
                
                echo -e "  ${color}[$status] $item: $message${NC}"
                
                if [[ "$status" != "PASS" && -n "$recommendation" ]]; then
                    echo -e "${GRAY}    建议: $recommendation${NC}"
                fi
            fi
        done
    done
    
    # 总体评估
    echo -e "\n${CYAN}=== 总体评估 ===${NC}"
    
    if [[ $FAIL_COUNT -eq 0 && $WARN_COUNT -eq 0 ]]; then
        echo -e "${GREEN}✓ 系统环境完全满足AIOps平台部署要求${NC}"
    elif [[ $FAIL_COUNT -eq 0 ]]; then
        echo -e "${YELLOW}⚠ 系统环境基本满足要求，但有一些建议改进的地方${NC}"
    else
        echo -e "${RED}✗ 系统环境存在问题，需要解决后才能部署${NC}"
    fi
    
    # 保存报告到文件
    local report_path="$PROJECT_ROOT/logs/environment-check-$(date +%Y%m%d-%H%M%S).json"
    local log_dir
    log_dir=$(dirname "$report_path")
    
    # 确保日志目录存在
    mkdir -p "$log_dir"
    
    # 生成JSON报告
    cat > "$report_path" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "deployment_type": "$DEPLOYMENT_TYPE",
  "summary": {
    "total": $total_count,
    "pass": $PASS_COUNT,
    "warn": $WARN_COUNT,
    "fail": $FAIL_COUNT
  },
  "results": [
EOF
    
    local first=true
    for result in "${CHECK_RESULTS[@]}"; do
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$report_path"
        fi
        echo "    $result" >> "$report_path"
    done
    
    cat >> "$report_path" << EOF

  ]
}
EOF
    
    echo -e "\n${CYAN}详细报告已保存到: $report_path${NC}"
}

# 主函数
main() {
    echo -e "${GREEN}AIOps平台环境检查工具${NC}"
    echo -e "检查类型: $DEPLOYMENT_TYPE"
    echo -e "详细模式: $DETAILED"
    echo -e "自动修复: $FIX"
    echo -e "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 执行检查
    test_system_info
    test_hardware_resources
    test_network_configuration
    test_shell_environment
    
    if [[ "$DEPLOYMENT_TYPE" =~ ^(docker|all)$ ]]; then
        test_docker_environment
    fi
    
    if [[ "$DEPLOYMENT_TYPE" =~ ^(kubernetes|all)$ ]]; then
        test_kubernetes_environment
    fi
    
    # 自动修复
    if [[ "$FIX" == "true" ]]; then
        invoke_auto_fix
    fi
    
    # 生成报告
    generate_report
    
    echo -e "\n检查完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # 返回适当的退出码
    if [[ $FAIL_COUNT -gt 0 ]]; then
        exit 1
    elif [[ $WARN_COUNT -gt 0 ]]; then
        exit 2
    else
        exit 0
    fi
}

# 解析参数并执行主函数
parse_args "$@"
main