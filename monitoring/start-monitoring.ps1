#!/usr/bin/env pwsh
# 监控堆栈启动脚本
# 管理Prometheus、Grafana、Alertmanager等监控服务
# 作者: AI Assistant
# 创建时间: 2024

<#
.SYNOPSIS
    AIOps监控堆栈管理脚本

.DESCRIPTION
    此脚本用于管理AIOps平台的监控堆栈，包括Prometheus、Grafana、Alertmanager等服务。
    支持启动、停止、重启、状态检查、日志查看等操作。

.PARAMETER Action
    要执行的操作：start, stop, restart, status, logs, clean, health, backup, restore

.PARAMETER Service
    指定服务名称（可选）：prometheus, grafana, alertmanager, loki, jaeger等

.PARAMETER Follow
    是否跟踪日志输出（仅用于logs操作）

.PARAMETER Lines
    显示日志行数（默认100行）

.EXAMPLE
    .\start-monitoring.ps1 -Action start
    启动所有监控服务

.EXAMPLE
    .\start-monitoring.ps1 -Action logs -Service prometheus -Follow
    跟踪查看Prometheus日志

.EXAMPLE
    .\start-monitoring.ps1 -Action health
    检查所有服务健康状态
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs', 'clean', 'health', 'backup', 'restore', 'update')]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet('prometheus', 'grafana', 'alertmanager', 'node-exporter', 'cadvisor', 'loki', 'promtail', 'jaeger', 'blackbox-exporter')]
    [string]$Service,
    
    [Parameter(Mandatory = $false)]
    [switch]$Follow,
    
    [Parameter(Mandatory = $false)]
    [int]$Lines = 100,
    
    [Parameter(Mandatory = $false)]
    [string]$BackupPath = "./backups",
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

# ===========================================
# 全局变量
# ===========================================
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_DIR
$COMPOSE_FILE = Join-Path $SCRIPT_DIR "docker-compose.yml"
$ENV_FILE = Join-Path $SCRIPT_DIR ".env"
$BACKUP_DIR = Join-Path $SCRIPT_DIR "backups"

# 服务列表
$SERVICES = @(
    'prometheus',
    'grafana', 
    'alertmanager',
    'node-exporter',
    'cadvisor',
    'loki',
    'promtail',
    'jaeger',
    'blackbox-exporter'
)

# 颜色定义
$Colors = @{
    Red = 'Red'
    Green = 'Green'
    Yellow = 'Yellow'
    Blue = 'Blue'
    Cyan = 'Cyan'
    Magenta = 'Magenta'
    White = 'White'
}

# ===========================================
# 辅助函数
# ===========================================

<#
.SYNOPSIS
    输出彩色日志信息
#>
function Write-ColorLog {
    param(
        [string]$Message,
        [string]$Color = 'White',
        [string]$Level = 'INFO'
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    Write-Host $logMessage -ForegroundColor $Colors[$Color]
}

<#
.SYNOPSIS
    检查Docker是否运行
#>
function Test-DockerRunning {
    try {
        $null = docker version 2>$null
        return $true
    }
    catch {
        return $false
    }
}

<#
.SYNOPSIS
    检查Docker Compose是否可用
#>
function Test-DockerCompose {
    try {
        $null = docker compose version 2>$null
        return $true
    }
    catch {
        try {
            $null = docker-compose version 2>$null
            return $true
        }
        catch {
            return $false
        }
    }
}

<#
.SYNOPSIS
    获取Docker Compose命令
#>
function Get-DockerComposeCommand {
    if (Get-Command "docker" -ErrorAction SilentlyContinue) {
        try {
            $null = docker compose version 2>$null
            return "docker compose"
        }
        catch {
            # Fallback to docker-compose
        }
    }
    
    if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
        return "docker-compose"
    }
    
    throw "Docker Compose not found. Please install Docker Desktop or docker-compose."
}

<#
.SYNOPSIS
    检查必要文件是否存在
#>
function Test-RequiredFiles {
    $requiredFiles = @(
        $COMPOSE_FILE,
        (Join-Path $PROJECT_ROOT "configs\prometheus\prometheus.yml"),
        (Join-Path $PROJECT_ROOT "configs\grafana\grafana.ini")
    )
    
    foreach ($file in $requiredFiles) {
        if (-not (Test-Path $file)) {
            Write-ColorLog "Required file not found: $file" 'Red' 'ERROR'
            return $false
        }
    }
    
    return $true
}

<#
.SYNOPSIS
    创建必要的目录
#>
function New-RequiredDirectories {
    $directories = @(
        $BACKUP_DIR,
        (Join-Path $PROJECT_ROOT "data\prometheus"),
        (Join-Path $PROJECT_ROOT "data\grafana"),
        (Join-Path $PROJECT_ROOT "data\alertmanager"),
        (Join-Path $PROJECT_ROOT "data\loki"),
        (Join-Path $PROJECT_ROOT "data\jaeger")
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColorLog "Created directory: $dir" 'Green'
        }
    }
}

<#
.SYNOPSIS
    获取服务状态
#>
function Get-ServiceStatus {
    param([string]$ServiceName = "")
    
    try {
        $composeCmd = Get-DockerComposeCommand
        
        if ($ServiceName) {
            $result = Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' ps $ServiceName" 2>$null
        }
        else {
            $result = Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' ps" 2>$null
        }
        
        return $result
    }
    catch {
        Write-ColorLog "Failed to get service status: $($_.Exception.Message)" 'Red' 'ERROR'
        return $null
    }
}

<#
.SYNOPSIS
    检查服务健康状态
#>
function Test-ServiceHealth {
    param([string]$ServiceName)
    
    $healthEndpoints = @{
        'prometheus' = 'http://localhost:9090/-/healthy'
        'grafana' = 'http://localhost:3000/api/health'
        'alertmanager' = 'http://localhost:9093/-/healthy'
        'loki' = 'http://localhost:3100/ready'
        'jaeger' = 'http://localhost:16686/'
        'node-exporter' = 'http://localhost:9100/metrics'
        'cadvisor' = 'http://localhost:8080/healthz'
        'blackbox-exporter' = 'http://localhost:9115/'
    }
    
    if ($healthEndpoints.ContainsKey($ServiceName)) {
        try {
            $response = Invoke-WebRequest -Uri $healthEndpoints[$ServiceName] -TimeoutSec 5 -UseBasicParsing
            return $response.StatusCode -eq 200
        }
        catch {
            return $false
        }
    }
    
    return $false
}

# ===========================================
# 主要功能函数
# ===========================================

<#
.SYNOPSIS
    启动监控服务
#>
function Start-MonitoringServices {
    param([string]$ServiceName = "")
    
    Write-ColorLog "Starting monitoring services..." 'Blue'
    
    try {
        $composeCmd = Get-DockerComposeCommand
        
        if ($ServiceName) {
            Write-ColorLog "Starting service: $ServiceName" 'Cyan'
            Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' up -d $ServiceName"
        }
        else {
            Write-ColorLog "Starting all monitoring services" 'Cyan'
            Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' up -d"
        }
        
        Write-ColorLog "Services started successfully" 'Green'
        
        # 等待服务启动
        Start-Sleep -Seconds 10
        
        # 显示服务状态
        Show-ServiceStatus $ServiceName
        
    }
    catch {
        Write-ColorLog "Failed to start services: $($_.Exception.Message)" 'Red' 'ERROR'
        exit 1
    }
}

<#
.SYNOPSIS
    停止监控服务
#>
function Stop-MonitoringServices {
    param([string]$ServiceName = "")
    
    Write-ColorLog "Stopping monitoring services..." 'Blue'
    
    try {
        $composeCmd = Get-DockerComposeCommand
        
        if ($ServiceName) {
            Write-ColorLog "Stopping service: $ServiceName" 'Cyan'
            Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' stop $ServiceName"
        }
        else {
            Write-ColorLog "Stopping all monitoring services" 'Cyan'
            Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' stop"
        }
        
        Write-ColorLog "Services stopped successfully" 'Green'
        
    }
    catch {
        Write-ColorLog "Failed to stop services: $($_.Exception.Message)" 'Red' 'ERROR'
        exit 1
    }
}

<#
.SYNOPSIS
    重启监控服务
#>
function Restart-MonitoringServices {
    param([string]$ServiceName = "")
    
    Write-ColorLog "Restarting monitoring services..." 'Blue'
    
    Stop-MonitoringServices $ServiceName
    Start-Sleep -Seconds 5
    Start-MonitoringServices $ServiceName
}

<#
.SYNOPSIS
    显示服务状态
#>
function Show-ServiceStatus {
    param([string]$ServiceName = "")
    
    Write-ColorLog "Checking service status..." 'Blue'
    
    $status = Get-ServiceStatus $ServiceName
    
    if ($status) {
        Write-Host $status
        
        # 显示访问URL
        Write-ColorLog "Service URLs:" 'Cyan'
        Write-Host "  Prometheus:    http://localhost:9090" -ForegroundColor Yellow
        Write-Host "  Grafana:       http://localhost:3000 (admin/admin123)" -ForegroundColor Yellow
        Write-Host "  Alertmanager:  http://localhost:9093" -ForegroundColor Yellow
        Write-Host "  Loki:          http://localhost:3100" -ForegroundColor Yellow
        Write-Host "  Jaeger:        http://localhost:16686" -ForegroundColor Yellow
        Write-Host "  Node Exporter: http://localhost:9100" -ForegroundColor Yellow
        Write-Host "  cAdvisor:      http://localhost:8080" -ForegroundColor Yellow
    }
    else {
        Write-ColorLog "No services running" 'Yellow' 'WARN'
    }
}

<#
.SYNOPSIS
    查看服务日志
#>
function Show-ServiceLogs {
    param(
        [string]$ServiceName = "",
        [bool]$FollowLogs = $false,
        [int]$LogLines = 100
    )
    
    try {
        $composeCmd = Get-DockerComposeCommand
        
        $logCmd = "$composeCmd -f '$COMPOSE_FILE' logs --tail $LogLines"
        
        if ($FollowLogs) {
            $logCmd += " -f"
        }
        
        if ($ServiceName) {
            $logCmd += " $ServiceName"
            Write-ColorLog "Showing logs for service: $ServiceName" 'Cyan'
        }
        else {
            Write-ColorLog "Showing logs for all services" 'Cyan'
        }
        
        Invoke-Expression $logCmd
        
    }
    catch {
        Write-ColorLog "Failed to show logs: $($_.Exception.Message)" 'Red' 'ERROR'
        exit 1
    }
}

<#
.SYNOPSIS
    清理监控服务
#>
function Clear-MonitoringServices {
    Write-ColorLog "Cleaning up monitoring services..." 'Blue'
    
    if (-not $Force) {
        $confirmation = Read-Host "This will remove all containers and volumes. Continue? (y/N)"
        if ($confirmation -ne 'y' -and $confirmation -ne 'Y') {
            Write-ColorLog "Operation cancelled" 'Yellow'
            return
        }
    }
    
    try {
        $composeCmd = Get-DockerComposeCommand
        
        Write-ColorLog "Stopping and removing containers..." 'Cyan'
        Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' down -v --remove-orphans"
        
        Write-ColorLog "Removing unused Docker resources..." 'Cyan'
        docker system prune -f
        
        Write-ColorLog "Cleanup completed" 'Green'
        
    }
    catch {
        Write-ColorLog "Failed to clean up: $($_.Exception.Message)" 'Red' 'ERROR'
        exit 1
    }
}

<#
.SYNOPSIS
    检查服务健康状态
#>
function Test-ServicesHealth {
    Write-ColorLog "Checking services health..." 'Blue'
    
    $healthyServices = 0
    $totalServices = 0
    
    foreach ($service in $SERVICES) {
        $totalServices++
        
        if (Test-ServiceHealth $service) {
            Write-ColorLog "✓ $service is healthy" 'Green'
            $healthyServices++
        }
        else {
            Write-ColorLog "✗ $service is unhealthy" 'Red'
        }
    }
    
    Write-ColorLog "Health check completed: $healthyServices/$totalServices services healthy" 'Cyan'
    
    if ($healthyServices -eq $totalServices) {
        Write-ColorLog "All services are healthy!" 'Green'
    }
    else {
        Write-ColorLog "Some services are unhealthy. Check logs for details." 'Yellow' 'WARN'
    }
}

<#
.SYNOPSIS
    备份监控数据
#>
function Backup-MonitoringData {
    Write-ColorLog "Creating backup of monitoring data..." 'Blue'
    
    try {
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupName = "monitoring_backup_$timestamp"
        $backupPath = Join-Path $BACKUP_DIR $backupName
        
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
        
        # 备份配置文件
        $configBackup = Join-Path $backupPath "configs"
        Copy-Item -Path (Join-Path $PROJECT_ROOT "configs") -Destination $configBackup -Recurse -Force
        
        # 备份数据卷
        $composeCmd = Get-DockerComposeCommand
        
        Write-ColorLog "Backing up Prometheus data..." 'Cyan'
        docker run --rm -v monitoring_prometheus_data:/data -v "${backupPath}:/backup" alpine tar czf /backup/prometheus_data.tar.gz -C /data .
        
        Write-ColorLog "Backing up Grafana data..." 'Cyan'
        docker run --rm -v monitoring_grafana_data:/data -v "${backupPath}:/backup" alpine tar czf /backup/grafana_data.tar.gz -C /data .
        
        Write-ColorLog "Backing up Alertmanager data..." 'Cyan'
        docker run --rm -v monitoring_alertmanager_data:/data -v "${backupPath}:/backup" alpine tar czf /backup/alertmanager_data.tar.gz -C /data .
        
        Write-ColorLog "Backup completed: $backupPath" 'Green'
        
    }
    catch {
        Write-ColorLog "Failed to create backup: $($_.Exception.Message)" 'Red' 'ERROR'
        exit 1
    }
}

<#
.SYNOPSIS
    更新监控服务
#>
function Update-MonitoringServices {
    Write-ColorLog "Updating monitoring services..." 'Blue'
    
    try {
        $composeCmd = Get-DockerComposeCommand
        
        Write-ColorLog "Pulling latest images..." 'Cyan'
        Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' pull"
        
        Write-ColorLog "Recreating services with new images..." 'Cyan'
        Invoke-Expression "$composeCmd -f '$COMPOSE_FILE' up -d --force-recreate"
        
        Write-ColorLog "Services updated successfully" 'Green'
        
        # 显示更新后的状态
        Start-Sleep -Seconds 10
        Show-ServiceStatus
        
    }
    catch {
        Write-ColorLog "Failed to update services: $($_.Exception.Message)" 'Red' 'ERROR'
        exit 1
    }
}

# ===========================================
# 主程序逻辑
# ===========================================

# 检查环境
Write-ColorLog "AIOps Monitoring Stack Manager" 'Magenta'
Write-ColorLog "==============================" 'Magenta'

if (-not (Test-DockerRunning)) {
    Write-ColorLog "Docker is not running. Please start Docker Desktop." 'Red' 'ERROR'
    exit 1
}

if (-not (Test-DockerCompose)) {
    Write-ColorLog "Docker Compose is not available. Please install Docker Desktop or docker-compose." 'Red' 'ERROR'
    exit 1
}

if (-not (Test-RequiredFiles)) {
    Write-ColorLog "Required configuration files are missing." 'Red' 'ERROR'
    exit 1
}

# 创建必要目录
New-RequiredDirectories

# 切换到脚本目录
Set-Location $SCRIPT_DIR

# 执行操作
switch ($Action) {
    'start' {
        Start-MonitoringServices $Service
    }
    'stop' {
        Stop-MonitoringServices $Service
    }
    'restart' {
        Restart-MonitoringServices $Service
    }
    'status' {
        Show-ServiceStatus $Service
    }
    'logs' {
        Show-ServiceLogs $Service $Follow.IsPresent $Lines
    }
    'clean' {
        Clear-MonitoringServices
    }
    'health' {
        Test-ServicesHealth
    }
    'backup' {
        Backup-MonitoringData
    }
    'update' {
        Update-MonitoringServices
    }
    default {
        Write-ColorLog "Unknown action: $Action" 'Red' 'ERROR'
        exit 1
    }
}

Write-ColorLog "Operation completed successfully" 'Green'