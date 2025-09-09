# Traefik启动管理脚本
# 用于启动、停止和管理Traefik边缘路由器服务
# 作者: AI Assistant
# 创建时间: 2024

<#
.SYNOPSIS
    Traefik服务管理脚本

.DESCRIPTION
    此脚本用于管理Traefik边缘路由器服务，包括启动、停止、重启、
    查看状态、查看日志等功能。

.PARAMETER Action
    要执行的操作：start, stop, restart, status, logs, clean

.PARAMETER Follow
    查看日志时是否跟随输出（仅用于logs操作）

.PARAMETER GenerateCerts
    启动前是否生成SSL证书

.PARAMETER Force
    强制执行操作

.EXAMPLE
    .\start-traefik.ps1 -Action start
    启动Traefik服务

.EXAMPLE
    .\start-traefik.ps1 -Action logs -Follow
    查看Traefik日志并跟随输出

.EXAMPLE
    .\start-traefik.ps1 -Action start -GenerateCerts
    生成SSL证书后启动Traefik服务
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "clean", "health")]
    [string]$Action,
    
    [switch]$Follow,
    [switch]$GenerateCerts,
    [switch]$Force
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 脚本配置
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile = Join-Path $ScriptDir "docker-compose.yml"
$CertsDir = Join-Path $ScriptDir "certs"
$LogsDir = Join-Path $ScriptDir "logs"
$LetsEncryptDir = Join-Path $ScriptDir "letsencrypt"

# 服务配置
$ServiceName = "traefik"
$ProjectName = "traefik"

# 函数：写入日志
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    switch ($Level) {
        "ERROR" { Write-Host $LogMessage -ForegroundColor Red }
        "WARN" { Write-Host $LogMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
        default { Write-Host $LogMessage }
    }
}

# 函数：检查Docker是否可用
function Test-Docker {
    try {
        $null = docker --version
        $null = docker-compose --version
        return $true
    }
    catch {
        return $false
    }
}

# 函数：检查必要文件
function Test-RequiredFiles {
    $RequiredFiles = @(
        $ComposeFile,
        (Join-Path $ScriptDir "traefik.yml"),
        (Join-Path $ScriptDir "dynamic.yml")
    )
    
    foreach ($File in $RequiredFiles) {
        if (-not (Test-Path $File)) {
            Write-Log "缺少必要文件: $File" "ERROR"
            return $false
        }
    }
    
    return $true
}

# 函数：创建必要目录
function New-RequiredDirectories {
    $Directories = @($CertsDir, $LogsDir, $LetsEncryptDir)
    
    foreach ($Dir in $Directories) {
        if (-not (Test-Path $Dir)) {
            New-Item -ItemType Directory -Path $Dir -Force | Out-Null
            Write-Log "创建目录: $Dir"
        }
    }
}

# 函数：生成SSL证书
function Invoke-GenerateCerts {
    Write-Log "生成SSL证书..."
    
    $CertScript = Join-Path $ScriptDir "generate-certs.ps1"
    
    if (Test-Path $CertScript) {
        try {
            & $CertScript -Force:$Force
            Write-Log "SSL证书生成完成" "SUCCESS"
        }
        catch {
            Write-Log "SSL证书生成失败: $($_.Exception.Message)" "ERROR"
            throw
        }
    } else {
        Write-Log "证书生成脚本不存在: $CertScript" "WARN"
    }
}

# 函数：检查服务状态
function Get-ServiceStatus {
    try {
        $Status = docker-compose -f $ComposeFile -p $ProjectName ps --services --filter "status=running"
        return $Status -contains $ServiceName
    }
    catch {
        return $false
    }
}

# 函数：等待服务就绪
function Wait-ServiceReady {
    param(
        [int]$TimeoutSeconds = 60,
        [int]$IntervalSeconds = 5
    )
    
    Write-Log "等待Traefik服务就绪..."
    
    $StartTime = Get-Date
    $Timeout = $StartTime.AddSeconds($TimeoutSeconds)
    
    while ((Get-Date) -lt $Timeout) {
        try {
            # 检查健康状态
            $HealthStatus = docker-compose -f $ComposeFile -p $ProjectName ps --format "table {{.Name}}\t{{.Status}}"
            
            if ($HealthStatus -match "healthy|Up") {
                Write-Log "Traefik服务已就绪" "SUCCESS"
                return $true
            }
            
            Write-Log "等待服务启动... ($((Get-Date) - $StartTime).TotalSeconds 秒)"
            Start-Sleep -Seconds $IntervalSeconds
        }
        catch {
            Write-Log "检查服务状态时出错: $($_.Exception.Message)" "WARN"
            Start-Sleep -Seconds $IntervalSeconds
        }
    }
    
    Write-Log "等待服务就绪超时" "ERROR"
    return $false
}

# 函数：启动服务
function Start-TraefikService {
    Write-Log "启动Traefik服务..."
    
    try {
        # 检查是否已运行
        if (Get-ServiceStatus) {
            if (-not $Force) {
                Write-Log "Traefik服务已在运行" "WARN"
                return
            } else {
                Write-Log "强制重启服务..."
                Stop-TraefikService
            }
        }
        
        # 生成证书（如果需要）
        if ($GenerateCerts) {
            Invoke-GenerateCerts
        }
        
        # 创建必要目录
        New-RequiredDirectories
        
        # 启动服务
        docker-compose -f $ComposeFile -p $ProjectName up -d
        
        # 等待服务就绪
        if (Wait-ServiceReady) {
            Write-Log "Traefik服务启动成功" "SUCCESS"
            Write-Log "仪表板地址: https://traefik.local:8080"
            Write-Log "测试地址: https://whoami.local"
        } else {
            throw "服务启动超时"
        }
    }
    catch {
        Write-Log "启动Traefik服务失败: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 函数：停止服务
function Stop-TraefikService {
    Write-Log "停止Traefik服务..."
    
    try {
        docker-compose -f $ComposeFile -p $ProjectName down
        Write-Log "Traefik服务已停止" "SUCCESS"
    }
    catch {
        Write-Log "停止Traefik服务失败: $($_.Exception.Message)" "ERROR"
        throw
    }
}

# 函数：重启服务
function Restart-TraefikService {
    Write-Log "重启Traefik服务..."
    
    Stop-TraefikService
    Start-Sleep -Seconds 3
    Start-TraefikService
}

# 函数：查看服务状态
function Show-ServiceStatus {
    Write-Log "查看Traefik服务状态..."
    
    try {
        # 显示容器状态
        Write-Host "`n=== 容器状态 ===" -ForegroundColor Cyan
        docker-compose -f $ComposeFile -p $ProjectName ps
        
        # 显示网络信息
        Write-Host "`n=== 网络信息 ===" -ForegroundColor Cyan
        docker network ls | Where-Object { $_ -match "traefik" }
        
        # 显示端口信息
        Write-Host "`n=== 端口信息 ===" -ForegroundColor Cyan
        docker-compose -f $ComposeFile -p $ProjectName port traefik 80 2>$null
        docker-compose -f $ComposeFile -p $ProjectName port traefik 443 2>$null
        docker-compose -f $ComposeFile -p $ProjectName port traefik 8080 2>$null
        
        # 显示健康检查
        Write-Host "`n=== 健康检查 ===" -ForegroundColor Cyan
        $ContainerId = docker-compose -f $ComposeFile -p $ProjectName ps -q traefik
        if ($ContainerId) {
            docker inspect $ContainerId --format='{{.State.Health.Status}}' 2>$null
        }
        
    }
    catch {
        Write-Log "查看服务状态失败: $($_.Exception.Message)" "ERROR"
    }
}

# 函数：查看日志
function Show-ServiceLogs {
    Write-Log "查看Traefik服务日志..."
    
    try {
        if ($Follow) {
            docker-compose -f $ComposeFile -p $ProjectName logs -f traefik
        } else {
            docker-compose -f $ComposeFile -p $ProjectName logs --tail=100 traefik
        }
    }
    catch {
        Write-Log "查看服务日志失败: $($_.Exception.Message)" "ERROR"
    }
}

# 函数：清理资源
function Clear-TraefikResources {
    Write-Log "清理Traefik资源..."
    
    try {
        # 停止并删除容器
        docker-compose -f $ComposeFile -p $ProjectName down -v --remove-orphans
        
        # 删除未使用的镜像（可选）
        if ($Force) {
            Write-Log "清理未使用的Docker镜像..."
            docker image prune -f --filter="label=traefik"
        }
        
        # 清理日志文件（可选）
        if ($Force -and (Test-Path $LogsDir)) {
            Write-Log "清理日志文件..."
            Remove-Item -Path "$LogsDir\*" -Recurse -Force -ErrorAction SilentlyContinue
        }
        
        Write-Log "Traefik资源清理完成" "SUCCESS"
    }
    catch {
        Write-Log "清理Traefik资源失败: $($_.Exception.Message)" "ERROR"
    }
}

# 函数：健康检查
function Test-ServiceHealth {
    Write-Log "执行Traefik健康检查..."
    
    try {
        # 检查容器状态
        $IsRunning = Get-ServiceStatus
        Write-Log "容器运行状态: $(if ($IsRunning) { '运行中' } else { '已停止' })"
        
        if (-not $IsRunning) {
            Write-Log "Traefik服务未运行" "ERROR"
            return
        }
        
        # 检查API端点
        try {
            $Response = Invoke-WebRequest -Uri "http://localhost:8080/ping" -TimeoutSec 10 -UseBasicParsing
            if ($Response.StatusCode -eq 200) {
                Write-Log "API端点健康检查: 正常" "SUCCESS"
            } else {
                Write-Log "API端点健康检查: 异常 (状态码: $($Response.StatusCode))" "WARN"
            }
        }
        catch {
            Write-Log "API端点健康检查: 失败 - $($_.Exception.Message)" "ERROR"
        }
        
        # 检查路由配置
        try {
            $Response = Invoke-WebRequest -Uri "http://localhost:8080/api/http/routers" -TimeoutSec 10 -UseBasicParsing
            $Routers = $Response.Content | ConvertFrom-Json
            Write-Log "已配置路由数量: $($Routers.Count)" "INFO"
        }
        catch {
            Write-Log "路由配置检查失败: $($_.Exception.Message)" "WARN"
        }
        
        Write-Log "健康检查完成" "SUCCESS"
    }
    catch {
        Write-Log "健康检查失败: $($_.Exception.Message)" "ERROR"
    }
}

# 主函数
function Main {
    Write-Log "Traefik服务管理 - 操作: $Action"
    
    try {
        # 检查Docker环境
        if (-not (Test-Docker)) {
            throw "Docker或Docker Compose不可用，请确保已正确安装"
        }
        
        # 检查必要文件
        if (-not (Test-RequiredFiles)) {
            throw "缺少必要的配置文件"
        }
        
        # 执行相应操作
        switch ($Action) {
            "start" { Start-TraefikService }
            "stop" { Stop-TraefikService }
            "restart" { Restart-TraefikService }
            "status" { Show-ServiceStatus }
            "logs" { Show-ServiceLogs }
            "clean" { Clear-TraefikResources }
            "health" { Test-ServiceHealth }
        }
        
    }
    catch {
        Write-Log "操作失败: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

# 执行主函数
Main