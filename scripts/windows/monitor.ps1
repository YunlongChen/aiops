<#
.SYNOPSIS
    AIOps平台监控脚本 (PowerShell)

.DESCRIPTION
    本脚本用于监控AIOps平台的部署状态和服务健康状况，包括Docker容器状态、
    Kubernetes资源状态、服务端点健康检查、资源使用情况等。

.PARAMETER DeploymentType
    部署类型：docker-compose, kubernetes, 或 all

.PARAMETER Environment
    环境名称：development, staging, production

.PARAMETER Continuous
    持续监控模式

.PARAMETER Interval
    监控间隔（秒），默认30秒

.PARAMETER OutputFormat
    输出格式：console, json, html

.PARAMETER OutputFile
    输出文件路径

.PARAMETER AlertThreshold
    告警阈值配置文件路径

.EXAMPLE
    .\monitor.ps1 -DeploymentType docker-compose -Environment development
    .\monitor.ps1 -DeploymentType kubernetes -Continuous -Interval 60
    .\monitor.ps1 -OutputFormat json -OutputFile monitoring-report.json

.NOTES
    版本: 1.0.0
    作者: AIOps Team
    创建日期: 2024-01-01
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("docker-compose", "kubernetes", "all")]
    [string]$DeploymentType = "all",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [switch]$Continuous,
    
    [Parameter(Mandatory=$false)]
    [int]$Interval = 30,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("console", "json", "html")]
    [string]$OutputFormat = "console",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputFile = "",
    
    [Parameter(Mandatory=$false)]
    [string]$AlertThreshold = ""
)

# 设置错误处理
$ErrorActionPreference = "Continue"

# 全局变量
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:ProjectName = "aiops"
$script:MonitoringData = @{
    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    deployment_type = $DeploymentType
    environment = $Environment
    docker_services = @()
    kubernetes_resources = @()
    health_checks = @()
    resource_usage = @{}
    alerts = @()
    summary = @{}
}

# 默认告警阈值
$script:DefaultThresholds = @{
    cpu_usage = 80
    memory_usage = 85
    disk_usage = 90
    response_time = 5000  # 毫秒
    error_rate = 5        # 百分比
}

# 服务端点配置
$script:ServiceEndpoints = @{
    traefik = @{
        url = "http://localhost:8080/api/rawdata"
        port = 8080
        path = "/api/rawdata"
    }
    prometheus = @{
        url = "http://localhost:9090/-/healthy"
        port = 9090
        path = "/-/healthy"
    }
    grafana = @{
        url = "http://localhost:3000/api/health"
        port = 3000
        path = "/api/health"
    }
    alertmanager = @{
        url = "http://localhost:9093/-/healthy"
        port = 9093
        path = "/-/healthy"
    }
    elasticsearch = @{
        url = "http://localhost:9200/_cluster/health"
        port = 9200
        path = "/_cluster/health"
    }
    kibana = @{
        url = "http://localhost:5601/api/status"
        port = 5601
        path = "/api/status"
    }
    redis = @{
        port = 6379
        command = "redis-cli ping"
    }
    postgresql = @{
        port = 5432
        command = "pg_isready -h localhost -p 5432"
    }
    "ai-engine" = @{
        url = "http://localhost:8001/health"
        port = 8001
        path = "/health"
    }
    "api-gateway" = @{
        url = "http://localhost:8000/health"
        port = 8000
        path = "/health"
    }
    "self-healing" = @{
        url = "http://localhost:8002/health"
        port = 8002
        path = "/health"
    }
}

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("Info", "Warning", "Error", "Success", "Debug")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    switch ($Level) {
        "Info"    { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor White }
        "Warning" { Write-Host "[$timestamp] [WARN] $Message" -ForegroundColor Yellow }
        "Error"   { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        "Success" { Write-Host "[$timestamp] [SUCCESS] $Message" -ForegroundColor Green }
        "Debug"   { Write-Host "[$timestamp] [DEBUG] $Message" -ForegroundColor Gray }
    }
}

# 加载告警阈值配置
function Load-AlertThresholds {
    if ($AlertThreshold -and (Test-Path $AlertThreshold)) {
        try {
            $thresholds = Get-Content $AlertThreshold | ConvertFrom-Json
            foreach ($key in $thresholds.PSObject.Properties.Name) {
                $script:DefaultThresholds[$key] = $thresholds.$key
            }
            Write-Log "已加载告警阈值配置: $AlertThreshold" -Level "Info"
        } catch {
            Write-Log "加载告警阈值配置失败: $($_.Exception.Message)" -Level "Warning"
        }
    }
}

# 检查Docker是否可用
function Test-DockerAvailable {
    try {
        $null = docker version 2>$null
        return $true
    } catch {
        return $false
    }
}

# 检查Kubernetes是否可用
function Test-KubernetesAvailable {
    try {
        $null = kubectl version --client 2>$null
        return $true
    } catch {
        return $false
    }
}

# 检查端口是否开放
function Test-Port {
    param(
        [string]$HostName = "localhost",
        [int]$Port,
        [int]$Timeout = 3
    )
    
    try {
        $tcpClient = New-Object System.Net.Sockets.TcpClient
        $asyncResult = $tcpClient.BeginConnect($HostName, $Port, $null, $null)
        $wait = $asyncResult.AsyncWaitHandle.WaitOne($Timeout * 1000, $false)
        
        if ($wait) {
            $tcpClient.EndConnect($asyncResult)
            $tcpClient.Close()
            return $true
        } else {
            $tcpClient.Close()
            return $false
        }
    } catch {
        return $false
    }
}

# HTTP健康检查
function Test-HttpEndpoint {
    param(
        [string]$Url,
        [int]$Timeout = 5
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec $Timeout -UseBasicParsing
        return @{
            status = "healthy"
            status_code = $response.StatusCode
            response_time = 0  # PowerShell doesn't provide easy access to response time
            content_length = $response.Content.Length
        }
    } catch {
        return @{
            status = "unhealthy"
            error = $_.Exception.Message
            status_code = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { 0 }
        }
    }
}

# 监控Docker Compose服务
function Monitor-DockerComposeServices {
    Write-Log "监控Docker Compose服务..." -Level "Info"
    
    if (!(Test-DockerAvailable)) {
        Write-Log "Docker不可用，跳过Docker监控" -Level "Warning"
        return
    }
    
    try {
        # 获取项目容器
        $projectName = "$script:ProjectName-$Environment"
        $containers = docker ps -a --filter "label=com.docker.compose.project=$projectName" --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>$null
        
        if (!$containers) {
            $containers = docker ps -a --filter "name=$script:ProjectName" --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>$null
        }
        
        foreach ($container in $containers) {
            if ($container) {
                $parts = $container -split '\|'
                $name = $parts[0]
                $status = $parts[1]
                $ports = if ($parts.Length -gt 2) { $parts[2] } else { "" }
                
                # 获取容器详细信息
                $inspect = docker inspect $name 2>$null | ConvertFrom-Json
                
                $serviceInfo = @{
                    name = $name
                    status = $status
                    ports = $ports
                    image = $inspect.Config.Image
                    created = $inspect.Created
                    started = $inspect.State.StartedAt
                    health = if ($inspect.State.Health) { $inspect.State.Health.Status } else { "unknown" }
                    restart_count = $inspect.RestartCount
                }
                
                # 获取资源使用情况
                try {
                    $stats = docker stats $name --no-stream --format "{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}" 2>$null
                    if ($stats) {
                        $statsParts = $stats -split '\|'
                        $serviceInfo.cpu_usage = $statsParts[0] -replace '%', ''
                        $serviceInfo.memory_usage = $statsParts[1]
                        $serviceInfo.memory_percent = $statsParts[2] -replace '%', ''
                    }
                } catch {
                    Write-Log "获取容器 $name 资源使用情况失败" -Level "Debug"
                }
                
                $script:MonitoringData.docker_services += $serviceInfo
                
                # 检查告警条件
                if ($serviceInfo.cpu_usage -and [float]$serviceInfo.cpu_usage -gt $script:DefaultThresholds.cpu_usage) {
                    $script:MonitoringData.alerts += @{
                        type = "high_cpu"
                        service = $name
                        value = $serviceInfo.cpu_usage
                        threshold = $script:DefaultThresholds.cpu_usage
                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                }
                
                if ($serviceInfo.memory_percent -and [float]$serviceInfo.memory_percent -gt $script:DefaultThresholds.memory_usage) {
                    $script:MonitoringData.alerts += @{
                        type = "high_memory"
                        service = $name
                        value = $serviceInfo.memory_percent
                        threshold = $script:DefaultThresholds.memory_usage
                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }
        }
        
        Write-Log "Docker服务监控完成，发现 $($script:MonitoringData.docker_services.Count) 个服务" -Level "Success"
        
    } catch {
        Write-Log "Docker服务监控失败: $($_.Exception.Message)" -Level "Error"
    }
}

# 监控Kubernetes资源
function Monitor-KubernetesResources {
    Write-Log "监控Kubernetes资源..." -Level "Info"
    
    if (!(Test-KubernetesAvailable)) {
        Write-Log "kubectl不可用，跳过Kubernetes监控" -Level "Warning"
        return
    }
    
    try {
        $namespace = "aiops-$Environment"
        
        # 检查命名空间是否存在
        $nsExists = $false
        try {
            $null = kubectl get namespace $namespace 2>$null
            $nsExists = $true
        } catch {
            $namespace = "aiops"
            try {
                $null = kubectl get namespace $namespace 2>$null
                $nsExists = $true
            } catch {
                Write-Log "未找到AIOps命名空间" -Level "Warning"
                return
            }
        }
        
        # 监控Deployment
        $deployments = kubectl get deployments -n $namespace -o json 2>$null | ConvertFrom-Json
        if ($deployments.items) {
            foreach ($deployment in $deployments.items) {
                $resourceInfo = @{
                    type = "deployment"
                    name = $deployment.metadata.name
                    namespace = $deployment.metadata.namespace
                    replicas = $deployment.spec.replicas
                    ready_replicas = if ($deployment.status.readyReplicas) { $deployment.status.readyReplicas } else { 0 }
                    available_replicas = if ($deployment.status.availableReplicas) { $deployment.status.availableReplicas } else { 0 }
                    conditions = $deployment.status.conditions
                    created = $deployment.metadata.creationTimestamp
                }
                
                $script:MonitoringData.kubernetes_resources += $resourceInfo
                
                # 检查副本状态
                if ($resourceInfo.ready_replicas -lt $resourceInfo.replicas) {
                    $script:MonitoringData.alerts += @{
                        type = "deployment_not_ready"
                        resource = "$($resourceInfo.namespace)/$($resourceInfo.name)"
                        ready = $resourceInfo.ready_replicas
                        desired = $resourceInfo.replicas
                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }
        }
        
        # 监控StatefulSet
        $statefulsets = kubectl get statefulsets -n $namespace -o json 2>$null | ConvertFrom-Json
        if ($statefulsets.items) {
            foreach ($statefulset in $statefulsets.items) {
                $resourceInfo = @{
                    type = "statefulset"
                    name = $statefulset.metadata.name
                    namespace = $statefulset.metadata.namespace
                    replicas = $statefulset.spec.replicas
                    ready_replicas = if ($statefulset.status.readyReplicas) { $statefulset.status.readyReplicas } else { 0 }
                    current_replicas = if ($statefulset.status.currentReplicas) { $statefulset.status.currentReplicas } else { 0 }
                    created = $statefulset.metadata.creationTimestamp
                }
                
                $script:MonitoringData.kubernetes_resources += $resourceInfo
                
                # 检查副本状态
                if ($resourceInfo.ready_replicas -lt $resourceInfo.replicas) {
                    $script:MonitoringData.alerts += @{
                        type = "statefulset_not_ready"
                        resource = "$($resourceInfo.namespace)/$($resourceInfo.name)"
                        ready = $resourceInfo.ready_replicas
                        desired = $resourceInfo.replicas
                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }
        }
        
        # 监控Service
        $services = kubectl get services -n $namespace -o json 2>$null | ConvertFrom-Json
        if ($services.items) {
            foreach ($service in $services.items) {
                $resourceInfo = @{
                    type = "service"
                    name = $service.metadata.name
                    namespace = $service.metadata.namespace
                    cluster_ip = $service.spec.clusterIP
                    ports = $service.spec.ports
                    selector = $service.spec.selector
                    created = $service.metadata.creationTimestamp
                }
                
                $script:MonitoringData.kubernetes_resources += $resourceInfo
            }
        }
        
        # 监控Pod
        $pods = kubectl get pods -n $namespace -o json 2>$null | ConvertFrom-Json
        if ($pods.items) {
            foreach ($pod in $pods.items) {
                $resourceInfo = @{
                    type = "pod"
                    name = $pod.metadata.name
                    namespace = $pod.metadata.namespace
                    phase = $pod.status.phase
                    ready = ($pod.status.conditions | Where-Object { $_.type -eq "Ready" }).status
                    restart_count = ($pod.status.containerStatuses | Measure-Object -Property restartCount -Sum).Sum
                    node = $pod.spec.nodeName
                    created = $pod.metadata.creationTimestamp
                }
                
                $script:MonitoringData.kubernetes_resources += $resourceInfo
                
                # 检查Pod状态
                if ($resourceInfo.phase -ne "Running" -or $resourceInfo.ready -ne "True") {
                    $script:MonitoringData.alerts += @{
                        type = "pod_not_ready"
                        resource = "$($resourceInfo.namespace)/$($resourceInfo.name)"
                        phase = $resourceInfo.phase
                        ready = $resourceInfo.ready
                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                }
                
                # 检查重启次数
                if ($resourceInfo.restart_count -gt 5) {
                    $script:MonitoringData.alerts += @{
                        type = "high_restart_count"
                        resource = "$($resourceInfo.namespace)/$($resourceInfo.name)"
                        restart_count = $resourceInfo.restart_count
                        timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                    }
                }
            }
        }
        
        Write-Log "Kubernetes资源监控完成，发现 $($script:MonitoringData.kubernetes_resources.Count) 个资源" -Level "Success"
        
    } catch {
        Write-Log "Kubernetes资源监控失败: $($_.Exception.Message)" -Level "Error"
    }
}

# 执行健康检查
function Invoke-HealthChecks {
    Write-Log "执行服务健康检查..." -Level "Info"
    
    foreach ($serviceName in $script:ServiceEndpoints.Keys) {
        $endpoint = $script:ServiceEndpoints[$serviceName]
        
        $healthCheck = @{
            service = $serviceName
            timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        }
        
        # 端口检查
        if ($endpoint.port) {
            $portOpen = Test-Port -Port $endpoint.port
            $healthCheck.port_status = if ($portOpen) { "open" } else { "closed" }
            
            if (!$portOpen) {
                $script:MonitoringData.alerts += @{
                    type = "port_closed"
                    service = $serviceName
                    port = $endpoint.port
                    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                }
            }
        }
        
        # HTTP健康检查
        if ($endpoint.url) {
            $httpResult = Test-HttpEndpoint -Url $endpoint.url
            $healthCheck.http_status = $httpResult.status
            $healthCheck.status_code = $httpResult.status_code
            $healthCheck.response_time = $httpResult.response_time
            
            if ($httpResult.status -eq "unhealthy") {
                $script:MonitoringData.alerts += @{
                    type = "http_unhealthy"
                    service = $serviceName
                    url = $endpoint.url
                    error = $httpResult.error
                    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                }
            }
        }
        
        # 命令检查
        if ($endpoint.command) {
            try {
                $result = Invoke-Expression $endpoint.command 2>$null
                $healthCheck.command_status = "success"
                $healthCheck.command_output = $result
            } catch {
                $healthCheck.command_status = "failed"
                $healthCheck.command_error = $_.Exception.Message
                
                $script:MonitoringData.alerts += @{
                    type = "command_failed"
                    service = $serviceName
                    command = $endpoint.command
                    error = $_.Exception.Message
                    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                }
            }
        }
        
        $script:MonitoringData.health_checks += $healthCheck
    }
    
    Write-Log "健康检查完成，检查了 $($script:ServiceEndpoints.Keys.Count) 个服务" -Level "Success"
}

# 获取系统资源使用情况
function Get-SystemResourceUsage {
    Write-Log "获取系统资源使用情况..." -Level "Info"
    
    try {
        # CPU使用率
        $cpu = Get-WmiObject -Class Win32_Processor | Measure-Object -Property LoadPercentage -Average
        $script:MonitoringData.resource_usage.cpu_usage = [math]::Round($cpu.Average, 2)
        
        # 内存使用率
        $memory = Get-WmiObject -Class Win32_OperatingSystem
        $totalMemory = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
        $freeMemory = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
        $usedMemory = $totalMemory - $freeMemory
        $memoryUsagePercent = [math]::Round(($usedMemory / $totalMemory) * 100, 2)
        
        $script:MonitoringData.resource_usage.memory_total = $totalMemory
        $script:MonitoringData.resource_usage.memory_used = $usedMemory
        $script:MonitoringData.resource_usage.memory_free = $freeMemory
        $script:MonitoringData.resource_usage.memory_usage_percent = $memoryUsagePercent
        
        # 磁盘使用率
        $disks = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
        $diskInfo = @()
        foreach ($disk in $disks) {
            $totalSize = [math]::Round($disk.Size / 1GB, 2)
            $freeSpace = [math]::Round($disk.FreeSpace / 1GB, 2)
            $usedSpace = $totalSize - $freeSpace
            $usagePercent = if ($totalSize -gt 0) { [math]::Round(($usedSpace / $totalSize) * 100, 2) } else { 0 }
            
            $diskInfo += @{
                drive = $disk.DeviceID
                total = $totalSize
                used = $usedSpace
                free = $freeSpace
                usage_percent = $usagePercent
            }
            
            # 检查磁盘使用率告警
            if ($usagePercent -gt $script:DefaultThresholds.disk_usage) {
                $script:MonitoringData.alerts += @{
                    type = "high_disk_usage"
                    drive = $disk.DeviceID
                    usage_percent = $usagePercent
                    threshold = $script:DefaultThresholds.disk_usage
                    timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                }
            }
        }
        $script:MonitoringData.resource_usage.disks = $diskInfo
        
        # 网络统计
        $networkAdapters = Get-WmiObject -Class Win32_PerfRawData_Tcpip_NetworkInterface | Where-Object { $_.Name -notlike "*Loopback*" -and $_.Name -notlike "*isatap*" }
        $networkInfo = @()
        foreach ($adapter in $networkAdapters) {
            $networkInfo += @{
                name = $adapter.Name
                bytes_received = $adapter.BytesReceivedPerSec
                bytes_sent = $adapter.BytesSentPerSec
            }
        }
        $script:MonitoringData.resource_usage.network = $networkInfo
        
        # 检查系统资源告警
        if ($script:MonitoringData.resource_usage.cpu_usage -gt $script:DefaultThresholds.cpu_usage) {
            $script:MonitoringData.alerts += @{
                type = "high_system_cpu"
                value = $script:MonitoringData.resource_usage.cpu_usage
                threshold = $script:DefaultThresholds.cpu_usage
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
        
        if ($memoryUsagePercent -gt $script:DefaultThresholds.memory_usage) {
            $script:MonitoringData.alerts += @{
                type = "high_system_memory"
                value = $memoryUsagePercent
                threshold = $script:DefaultThresholds.memory_usage
                timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
            }
        }
        
        Write-Log "系统资源监控完成" -Level "Success"
        
    } catch {
        Write-Log "获取系统资源使用情况失败: $($_.Exception.Message)" -Level "Error"
    }
}

# 生成监控摘要
function Generate-MonitoringSummary {
    $summary = @{
        total_services = 0
        healthy_services = 0
        unhealthy_services = 0
        total_resources = 0
        ready_resources = 0
        not_ready_resources = 0
        total_alerts = $script:MonitoringData.alerts.Count
        critical_alerts = 0
        warning_alerts = 0
        system_health = "unknown"
    }
    
    # Docker服务统计
    foreach ($service in $script:MonitoringData.docker_services) {
        $summary.total_services++
        if ($service.status -like "*Up*" -and $service.health -ne "unhealthy") {
            $summary.healthy_services++
        } else {
            $summary.unhealthy_services++
        }
    }
    
    # Kubernetes资源统计
    foreach ($resource in $script:MonitoringData.kubernetes_resources) {
        $summary.total_resources++
        
        $isReady = $false
        switch ($resource.type) {
            "deployment" {
                $isReady = $resource.ready_replicas -eq $resource.replicas
            }
            "statefulset" {
                $isReady = $resource.ready_replicas -eq $resource.replicas
            }
            "pod" {
                $isReady = $resource.phase -eq "Running" -and $resource.ready -eq "True"
            }
            default {
                $isReady = $true
            }
        }
        
        if ($isReady) {
            $summary.ready_resources++
        } else {
            $summary.not_ready_resources++
        }
    }
    
    # 告警分类
    $criticalAlertTypes = @("port_closed", "http_unhealthy", "deployment_not_ready", "statefulset_not_ready", "pod_not_ready")
    foreach ($alert in $script:MonitoringData.alerts) {
        if ($alert.type -in $criticalAlertTypes) {
            $summary.critical_alerts++
        } else {
            $summary.warning_alerts++
        }
    }
    
    # 系统健康状态
    if ($summary.critical_alerts -gt 0) {
        $summary.system_health = "critical"
    } elseif ($summary.warning_alerts -gt 0 -or $summary.unhealthy_services -gt 0 -or $summary.not_ready_resources -gt 0) {
        $summary.system_health = "warning"
    } else {
        $summary.system_health = "healthy"
    }
    
    $script:MonitoringData.summary = $summary
}

# 输出控制台格式
function Output-ConsoleFormat {
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
    Write-Host "AIOps平台监控报告" -ForegroundColor White
    Write-Host "时间: $($script:MonitoringData.timestamp)" -ForegroundColor Gray
    Write-Host "部署类型: $($script:MonitoringData.deployment_type)" -ForegroundColor Gray
    Write-Host "环境: $($script:MonitoringData.environment)" -ForegroundColor Gray
    Write-Host "=" * 80 -ForegroundColor Cyan
    
    # 系统摘要
    $summary = $script:MonitoringData.summary
    Write-Host "系统健康状态: " -NoNewline
    switch ($summary.system_health) {
        "healthy" { Write-Host "健康" -ForegroundColor Green }
        "warning" { Write-Host "警告" -ForegroundColor Yellow }
        "critical" { Write-Host "严重" -ForegroundColor Red }
    }
    
    Write-Host "服务状态: $($summary.healthy_services)/$($summary.total_services) 健康" -ForegroundColor White
    Write-Host "资源状态: $($summary.ready_resources)/$($summary.total_resources) 就绪" -ForegroundColor White
    Write-Host "告警数量: $($summary.total_alerts) (严重: $($summary.critical_alerts), 警告: $($summary.warning_alerts))" -ForegroundColor White
    
    # 系统资源
    if ($script:MonitoringData.resource_usage.Count -gt 0) {
        Write-Host ""
        Write-Host "系统资源使用情况:" -ForegroundColor Yellow
        Write-Host "  CPU使用率: $($script:MonitoringData.resource_usage.cpu_usage)%" -ForegroundColor White
        Write-Host "  内存使用率: $($script:MonitoringData.resource_usage.memory_usage_percent)% ($($script:MonitoringData.resource_usage.memory_used)GB/$($script:MonitoringData.resource_usage.memory_total)GB)" -ForegroundColor White
        
        foreach ($disk in $script:MonitoringData.resource_usage.disks) {
            Write-Host "  磁盘 $($disk.drive): $($disk.usage_percent)% ($($disk.used)GB/$($disk.total)GB)" -ForegroundColor White
        }
    }
    
    # Docker服务
    if ($script:MonitoringData.docker_services.Count -gt 0) {
        Write-Host ""
        Write-Host "Docker服务状态:" -ForegroundColor Yellow
        foreach ($service in $script:MonitoringData.docker_services) {
            $statusColor = if ($service.status -like "*Up*") { "Green" } else { "Red" }
            Write-Host "  $($service.name): " -NoNewline
            Write-Host $service.status -ForegroundColor $statusColor
            if ($service.cpu_usage) {
                Write-Host "    CPU: $($service.cpu_usage)%, 内存: $($service.memory_percent)%" -ForegroundColor Gray
            }
        }
    }
    
    # Kubernetes资源
    if ($script:MonitoringData.kubernetes_resources.Count -gt 0) {
        Write-Host ""
        Write-Host "Kubernetes资源状态:" -ForegroundColor Yellow
        
        $resourceGroups = $script:MonitoringData.kubernetes_resources | Group-Object type
        foreach ($group in $resourceGroups) {
            Write-Host "  $($group.Name.ToUpper()):" -ForegroundColor Cyan
            foreach ($resource in $group.Group) {
                $status = "未知"
                $statusColor = "Gray"
                
                switch ($resource.type) {
                    "deployment" {
                        if ($resource.ready_replicas -eq $resource.replicas) {
                            $status = "就绪 ($($resource.ready_replicas)/$($resource.replicas))"
                            $statusColor = "Green"
                        } else {
                            $status = "未就绪 ($($resource.ready_replicas)/$($resource.replicas))"
                            $statusColor = "Red"
                        }
                    }
                    "statefulset" {
                        if ($resource.ready_replicas -eq $resource.replicas) {
                            $status = "就绪 ($($resource.ready_replicas)/$($resource.replicas))"
                            $statusColor = "Green"
                        } else {
                            $status = "未就绪 ($($resource.ready_replicas)/$($resource.replicas))"
                            $statusColor = "Red"
                        }
                    }
                    "pod" {
                        if ($resource.phase -eq "Running" -and $resource.ready -eq "True") {
                            $status = "运行中"
                            $statusColor = "Green"
                        } else {
                            $status = "$($resource.phase)"
                            $statusColor = "Red"
                        }
                    }
                    "service" {
                        $status = "活跃"
                        $statusColor = "Green"
                    }
                }
                
                Write-Host "    $($resource.name): " -NoNewline
                Write-Host $status -ForegroundColor $statusColor
            }
        }
    }
    
    # 健康检查
    if ($script:MonitoringData.health_checks.Count -gt 0) {
        Write-Host ""
        Write-Host "服务健康检查:" -ForegroundColor Yellow
        foreach ($check in $script:MonitoringData.health_checks) {
            Write-Host "  $($check.service):" -ForegroundColor White
            
            if ($check.port_status) {
                $portColor = if ($check.port_status -eq "open") { "Green" } else { "Red" }
                Write-Host "    端口: " -NoNewline
                Write-Host $check.port_status -ForegroundColor $portColor
            }
            
            if ($check.http_status) {
                $httpColor = if ($check.http_status -eq "healthy") { "Green" } else { "Red" }
                Write-Host "    HTTP: " -NoNewline
                Write-Host $check.http_status -ForegroundColor $httpColor
                if ($check.status_code) {
                    Write-Host "    状态码: $($check.status_code)" -ForegroundColor Gray
                }
            }
            
            if ($check.command_status) {
                $cmdColor = if ($check.command_status -eq "success") { "Green" } else { "Red" }
                Write-Host "    命令: " -NoNewline
                Write-Host $check.command_status -ForegroundColor $cmdColor
            }
        }
    }
    
    # 告警信息
    if ($script:MonitoringData.alerts.Count -gt 0) {
        Write-Host ""
        Write-Host "告警信息:" -ForegroundColor Red
        foreach ($alert in $script:MonitoringData.alerts) {
            $alertColor = if ($alert.type -in @("port_closed", "http_unhealthy", "deployment_not_ready", "statefulset_not_ready", "pod_not_ready")) { "Red" } else { "Yellow" }
            Write-Host "  [$($alert.timestamp)] $($alert.type)" -ForegroundColor $alertColor
            
            switch ($alert.type) {
                "high_cpu" {
                    Write-Host "    服务: $($alert.service), CPU使用率: $($alert.value)% (阈值: $($alert.threshold)%)" -ForegroundColor Gray
                }
                "high_memory" {
                    Write-Host "    服务: $($alert.service), 内存使用率: $($alert.value)% (阈值: $($alert.threshold)%)" -ForegroundColor Gray
                }
                "high_disk_usage" {
                    Write-Host "    磁盘: $($alert.drive), 使用率: $($alert.usage_percent)% (阈值: $($alert.threshold)%)" -ForegroundColor Gray
                }
                "port_closed" {
                    Write-Host "    服务: $($alert.service), 端口: $($alert.port)" -ForegroundColor Gray
                }
                "http_unhealthy" {
                    Write-Host "    服务: $($alert.service), URL: $($alert.url), 错误: $($alert.error)" -ForegroundColor Gray
                }
                "deployment_not_ready" {
                    Write-Host "    资源: $($alert.resource), 就绪副本: $($alert.ready)/$($alert.desired)" -ForegroundColor Gray
                }
                "statefulset_not_ready" {
                    Write-Host "    资源: $($alert.resource), 就绪副本: $($alert.ready)/$($alert.desired)" -ForegroundColor Gray
                }
                "pod_not_ready" {
                    Write-Host "    资源: $($alert.resource), 状态: $($alert.phase), 就绪: $($alert.ready)" -ForegroundColor Gray
                }
                "high_restart_count" {
                    Write-Host "    资源: $($alert.resource), 重启次数: $($alert.restart_count)" -ForegroundColor Gray
                }
            }
        }
    }
    
    Write-Host ""
    Write-Host "=" * 80 -ForegroundColor Cyan
}

# 输出JSON格式
function Output-JsonFormat {
    return $script:MonitoringData | ConvertTo-Json -Depth 10
}

# 输出HTML格式
function Output-HtmlFormat {
    $html = @"
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
            <p class="timestamp">生成时间: $($script:MonitoringData.timestamp)</p>
            <p>部署类型: $($script:MonitoringData.deployment_type) | 环境: $($script:MonitoringData.environment)</p>
        </div>
        
        <div class="summary">
            <div class="summary-card $($script:MonitoringData.summary.system_health)">
                <h4>系统健康状态</h4>
                <p class="status-$($script:MonitoringData.summary.system_health)">$($script:MonitoringData.summary.system_health.ToUpper())</p>
            </div>
            <div class="summary-card">
                <h4>服务状态</h4>
                <p>$($script:MonitoringData.summary.healthy_services)/$($script:MonitoringData.summary.total_services) 健康</p>
            </div>
            <div class="summary-card">
                <h4>资源状态</h4>
                <p>$($script:MonitoringData.summary.ready_resources)/$($script:MonitoringData.summary.total_resources) 就绪</p>
            </div>
            <div class="summary-card">
                <h4>告警数量</h4>
                <p>$($script:MonitoringData.summary.total_alerts) (严重: $($script:MonitoringData.summary.critical_alerts))</p>
            </div>
        </div>
"@
    
    # 添加系统资源部分
    if ($script:MonitoringData.resource_usage.Count -gt 0) {
        $html += @"
        <div class="section">
            <h3>系统资源使用情况</h3>
            <table>
                <tr><th>资源类型</th><th>使用情况</th><th>状态</th></tr>
                <tr>
                    <td>CPU</td>
                    <td>$($script:MonitoringData.resource_usage.cpu_usage)%</td>
                    <td class="$(if ($script:MonitoringData.resource_usage.cpu_usage -gt $script:DefaultThresholds.cpu_usage) { 'status-critical' } else { 'status-healthy' })">$(if ($script:MonitoringData.resource_usage.cpu_usage -gt $script:DefaultThresholds.cpu_usage) { '高' } else { '正常' })</td>
                </tr>
                <tr>
                    <td>内存</td>
                    <td>$($script:MonitoringData.resource_usage.memory_usage_percent)% ($($script:MonitoringData.resource_usage.memory_used)GB/$($script:MonitoringData.resource_usage.memory_total)GB)</td>
                    <td class="$(if ($script:MonitoringData.resource_usage.memory_usage_percent -gt $script:DefaultThresholds.memory_usage) { 'status-critical' } else { 'status-healthy' })">$(if ($script:MonitoringData.resource_usage.memory_usage_percent -gt $script:DefaultThresholds.memory_usage) { '高' } else { '正常' })</td>
                </tr>
"@
        
        foreach ($disk in $script:MonitoringData.resource_usage.disks) {
            $html += @"
                <tr>
                    <td>磁盘 $($disk.drive)</td>
                    <td>$($disk.usage_percent)% ($($disk.used)GB/$($disk.total)GB)</td>
                    <td class="$(if ($disk.usage_percent -gt $script:DefaultThresholds.disk_usage) { 'status-critical' } else { 'status-healthy' })">$(if ($disk.usage_percent -gt $script:DefaultThresholds.disk_usage) { '高' } else { '正常' })</td>
                </tr>
"@
        }
        
        $html += @"
            </table>
        </div>
"@
    }
    
    # 添加告警部分
    if ($script:MonitoringData.alerts.Count -gt 0) {
        $html += @"
        <div class="section">
            <h3>告警信息</h3>
"@
        
        foreach ($alert in $script:MonitoringData.alerts) {
            $alertClass = if ($alert.type -in @("port_closed", "http_unhealthy", "deployment_not_ready", "statefulset_not_ready", "pod_not_ready")) { "alert-critical" } else { "alert-warning" }
            $html += @"
            <div class="alert $alertClass">
                <strong>$($alert.type)</strong> - $($alert.timestamp)<br>
"@
            
            switch ($alert.type) {
                "high_cpu" {
                    $html += "服务: $($alert.service), CPU使用率: $($alert.value)% (阈值: $($alert.threshold)%)"
                }
                "high_memory" {
                    $html += "服务: $($alert.service), 内存使用率: $($alert.value)% (阈值: $($alert.threshold)%)"
                }
                "high_disk_usage" {
                    $html += "磁盘: $($alert.drive), 使用率: $($alert.usage_percent)% (阈值: $($alert.threshold)%)"
                }
                "port_closed" {
                    $html += "服务: $($alert.service), 端口: $($alert.port)"
                }
                "http_unhealthy" {
                    $html += "服务: $($alert.service), URL: $($alert.url), 错误: $($alert.error)"
                }
                default {
                    $html += ($alert | ConvertTo-Json -Compress)
                }
            }
            
            $html += @"
            </div>
"@
        }
        
        $html += @"
        </div>
"@
    }
    
    $html += @"
    </div>
</body>
</html>
"@
    
    return $html
}

# 保存输出到文件
function Save-OutputToFile {
    param(
        [string]$Content,
        [string]$FilePath
    )
    
    try {
        $Content | Out-File -FilePath $FilePath -Encoding UTF8
        Write-Log "监控报告已保存到: $FilePath" -Level "Success"
    } catch {
        Write-Log "保存监控报告失败: $($_.Exception.Message)" -Level "Error"
    }
}

# 执行单次监控
function Invoke-SingleMonitoring {
    Write-Log "开始执行监控检查..." -Level "Info"
    
    # 重置监控数据
    $script:MonitoringData.timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $script:MonitoringData.docker_services = @()
    $script:MonitoringData.kubernetes_resources = @()
    $script:MonitoringData.health_checks = @()
    $script:MonitoringData.resource_usage = @{}
    $script:MonitoringData.alerts = @()
    
    # 执行监控
    switch ($DeploymentType) {
        "docker-compose" {
            Monitor-DockerComposeServices
        }
        "kubernetes" {
            Monitor-KubernetesResources
        }
        "all" {
            Monitor-DockerComposeServices
            Monitor-KubernetesResources
        }
    }
    
    Invoke-HealthChecks
    Get-SystemResourceUsage
    Generate-MonitoringSummary
    
    # 输出结果
    switch ($OutputFormat) {
        "console" {
            Output-ConsoleFormat
        }
        "json" {
            $jsonOutput = Output-JsonFormat
            if ($OutputFile) {
                Save-OutputToFile -Content $jsonOutput -FilePath $OutputFile
            } else {
                Write-Output $jsonOutput
            }
        }
        "html" {
            $htmlOutput = Output-HtmlFormat
            if ($OutputFile) {
                Save-OutputToFile -Content $htmlOutput -FilePath $OutputFile
            } else {
                Write-Output $htmlOutput
            }
        }
    }
    
    Write-Log "监控检查完成" -Level "Success"
}

# 主函数
function Main {
    Write-Log "AIOps平台监控工具" -Level "Info"
    Write-Log "部署类型: $DeploymentType" -Level "Info"
    Write-Log "环境: $Environment" -Level "Info"
    Write-Log "输出格式: $OutputFormat" -Level "Info"
    Write-Log "持续监控: $Continuous" -Level "Info"
    if ($Continuous) {
        Write-Log "监控间隔: $Interval 秒" -Level "Info"
    }
    Write-Log "开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Level "Info"
    
    try {
        # 加载告警阈值
        Load-AlertThresholds
        
        if ($Continuous) {
            Write-Log "开始持续监控模式，按 Ctrl+C 停止..." -Level "Info"
            
            while ($true) {
                Invoke-SingleMonitoring
                
                Write-Log "等待 $Interval 秒后进行下次检查..." -Level "Debug"
                Start-Sleep -Seconds $Interval
            }
        } else {
            Invoke-SingleMonitoring
        }
        
    } catch {
        Write-Log "监控过程中发生错误: $($_.Exception.Message)" -Level "Error"
        Write-Log $_.ScriptStackTrace -Level "Debug"
        exit 1
    }
    
    Write-Log "完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Level "Info"
}

# 执行主函数
Main