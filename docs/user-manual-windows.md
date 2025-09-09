# AIOps平台用户手册 - Windows版

## 目录

1. [系统要求](#1-系统要求)
2. [环境准备](#2-环境准备)
3. [快速开始](#3-快速开始)
4. [配置说明](#4-配置说明)
5. [服务管理](#5-服务管理)
6. [监控和告警](#6-监控和告警)
7. [故障排除](#7-故障排除)
8. [性能优化](#8-性能优化)
9. [安全配置](#9-安全配置)
10. [备份和恢复](#10-备份和恢复)
11. [附录](#附录)

---

## 1. 系统要求

### 1.1 硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4核心 | 8核心+ |
| 内存 | 8GB | 16GB+ |
| 存储 | 50GB可用空间 | 200GB+ SSD |
| 网络 | 100Mbps | 1Gbps+ |

### 1.2 软件要求

- **操作系统**: Windows 10/11 Pro, Windows Server 2019/2022
- **PowerShell**: 5.1+ (推荐PowerShell 7+)
- **Docker Desktop**: 4.15.0+
- **Git**: 2.30.0+
- **.NET Framework**: 4.8+ (如需要)

### 1.3 网络要求

- 互联网连接（用于下载镜像和依赖）
- 防火墙开放端口：80, 443, 3000, 8080, 9090
- DNS解析正常

---

## 2. 环境准备

### 2.1 安装Docker Desktop

#### 2.1.1 下载和安装
```powershell
# 使用Chocolatey安装（推荐）
choco install docker-desktop -y

# 或者手动下载安装
# 访问 https://www.docker.com/products/docker-desktop/
# 下载Docker Desktop for Windows
```

#### 2.1.2 配置Docker Desktop
```powershell
# 启动Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 等待Docker启动
do {
    Start-Sleep -Seconds 5
    $dockerStatus = docker version 2>$null
} while (-not $dockerStatus)

Write-Host "✅ Docker Desktop已启动" -ForegroundColor Green
```

#### 2.1.3 Docker配置优化
```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "features": {
    "buildkit": true
  },
  "insecure-registries": [],
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 2.2 安装Git

```powershell
# 使用Chocolatey安装
choco install git -y

# 或使用winget安装
winget install Git.Git

# 验证安装
git --version
```

### 2.3 安装PowerShell 7（可选但推荐）

```powershell
# 使用winget安装
winget install Microsoft.PowerShell

# 或使用Chocolatey安装
choco install powershell-core -y

# 验证安装
pwsh --version
```

### 2.4 配置Windows防火墙

```powershell
# setup-firewall.ps1 - Windows防火墙配置脚本

# 检查是否以管理员身份运行
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "请以管理员身份运行此脚本"
    exit 1
}

Write-Host "🔥 配置Windows防火墙规则..." -ForegroundColor Cyan

# AIOps平台端口列表
$ports = @(
    @{Name="AIOps-HTTP"; Port=80; Protocol="TCP"; Description="HTTP访问"}
    @{Name="AIOps-HTTPS"; Port=443; Protocol="TCP"; Description="HTTPS访问"}
    @{Name="AIOps-Grafana"; Port=3000; Protocol="TCP"; Description="Grafana仪表板"}
    @{Name="AIOps-API"; Port=8080; Protocol="TCP"; Description="API网关"}
    @{Name="AIOps-Prometheus"; Port=9090; Protocol="TCP"; Description="Prometheus监控"}
    @{Name="AIOps-AI-Engine"; Port=8000; Protocol="TCP"; Description="AI引擎"}
    @{Name="AIOps-Self-Healing"; Port=8001; Protocol="TCP"; Description="自愈系统"}
    @{Name="AIOps-Node-Exporter"; Port=9100; Protocol="TCP"; Description="系统指标"}
)

# 创建防火墙规则
foreach ($port in $ports) {
    try {
        # 删除现有规则（如果存在）
        Remove-NetFirewallRule -DisplayName $port.Name -ErrorAction SilentlyContinue
        
        # 创建入站规则
        New-NetFirewallRule -DisplayName $port.Name `
                           -Direction Inbound `
                           -Protocol $port.Protocol `
                           -LocalPort $port.Port `
                           -Action Allow `
                           -Description $port.Description
        
        Write-Host "✅ 已创建防火墙规则: $($port.Name) (端口 $($port.Port))" -ForegroundColor Green
    }
    catch {
        Write-Warning "❌ 创建防火墙规则失败: $($port.Name) - $($_.Exception.Message)"
    }
}

Write-Host "✅ Windows防火墙配置完成" -ForegroundColor Green
```



---

## 3. 快速开始

### 3.1 获取源码

```powershell
# 克隆项目
git clone https://github.com/your-org/aiops.git
cd aiops

# 检查项目结构
Get-ChildItem -Recurse -Depth 2
```

### 3.2 一键部署脚本

```powershell
# deploy-aiops.ps1 - AIOps一键部署脚本

param(
    [switch]$SkipPreCheck,
    [switch]$UseLocalVolumes,
    [string]$Environment = "production"
)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

# 检查先决条件
function Test-Prerequisites {
    Write-ColorOutput "🔍 检查系统先决条件..." "Cyan"
    
    $errors = @()
    
    # 检查Docker
    try {
        $dockerVersion = docker --version
        Write-ColorOutput "✅ Docker: $dockerVersion" "Green"
    }
    catch {
        $errors += "Docker未安装或未启动"
    }
    
    # 检查Docker Compose
    try {
        $composeVersion = docker-compose --version
        Write-ColorOutput "✅ Docker Compose: $composeVersion" "Green"
    }
    catch {
        $errors += "Docker Compose未安装"
    }
    
    # 检查Git
    try {
        $gitVersion = git --version
        Write-ColorOutput "✅ Git: $gitVersion" "Green"
    }
    catch {
        $errors += "Git未安装"
    }
    
    # 检查磁盘空间
    $freeSpace = [math]::Round((Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace / 1GB, 2)
    if ($freeSpace -lt 10) {
        $errors += "磁盘空间不足，需要至少10GB可用空间，当前可用: ${freeSpace}GB"
    } else {
        Write-ColorOutput "✅ 磁盘空间: ${freeSpace}GB 可用" "Green"
    }
    
    # 检查内存
    $totalMemory = [math]::Round((Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
    if ($totalMemory -lt 8) {
        $errors += "内存不足，需要至少8GB内存，当前: ${totalMemory}GB"
    } else {
        Write-ColorOutput "✅ 系统内存: ${totalMemory}GB" "Green"
    }
    
    if ($errors.Count -gt 0) {
        Write-ColorOutput "❌ 发现以下问题:" "Red"
        foreach ($error in $errors) {
            Write-ColorOutput "   - $error" "Red"
        }
        return $false
    }
    
    return $true
}

# 创建环境配置文件
function New-EnvironmentFile {
    Write-ColorOutput "📝 创建环境配置文件..." "Cyan"
    
    $envContent = @"
# AIOps平台环境配置 - Windows

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops
POSTGRES_PASSWORD=$(New-Guid | Select-Object -ExpandProperty Guid)

# Redis配置
REDIS_PASSWORD=$(New-Guid | Select-Object -ExpandProperty Guid)

# Grafana配置
GF_SECURITY_ADMIN_PASSWORD=$(New-Guid | Select-Object -ExpandProperty Guid)
GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource

# JWT密钥
JWT_SECRET=$(New-Guid | Select-Object -ExpandProperty Guid)

# 域名配置
TRAEFIK_DOMAIN=aiops.local

# SSL配置
SSL_ENABLED=false

# 存储配置
"@
    
    if ($UseLocalVolumes) {
        $envContent += @"

# 本地存储路径
DATA_PATH=C:\aiops-data
LOGS_PATH=C:\aiops-logs
BACKUPS_PATH=C:\aiops-backups
"@
    }
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-ColorOutput "✅ 环境配置文件已创建" "Green"
}

# 启动服务
function Start-AIOpsServices {
    Write-ColorOutput "🚀 启动AIOps服务..." "Cyan"
    
    try {
        # 按顺序启动服务
        $services = @(
            "postgres",
            "redis", 
            "traefik",
            "prometheus",
            "grafana",
            "ai-engine",
            "self-healing",
            "api-gateway"
        )
        
        foreach ($service in $services) {
            Write-ColorOutput "🔄 启动服务: $service" "Yellow"
            docker-compose up -d $service
            
            # 等待服务启动
            Start-Sleep -Seconds 10
            
            # 检查服务状态
            $status = docker-compose ps $service
            if ($status -match "Up") {
                Write-ColorOutput "✅ 服务启动成功: $service" "Green"
            } else {
                Write-ColorOutput "❌ 服务启动失败: $service" "Red"
                return $false
            }
        }
        
        return $true
    }
    catch {
        Write-ColorOutput "❌ 服务启动失败: $($_.Exception.Message)" "Red"
        return $false
    }
}

# 主函数
function Main {
    Write-ColorOutput "🚀 开始部署AIOps平台 (Windows版)" "Cyan"
    Write-ColorOutput "环境: $Environment" "Yellow"
    
    # 检查先决条件
    if (-not $SkipPreCheck) {
        if (-not (Test-Prerequisites)) {
            Write-ColorOutput "❌ 先决条件检查失败，请解决上述问题后重试" "Red"
            exit 1
        }
    }
    
    # 创建配置文件
    New-EnvironmentFile
    
    # 拉取镜像
    Write-ColorOutput "📥 拉取Docker镜像..." "Cyan"
    docker-compose pull
    
    # 启动服务
    if (-not (Start-AIOpsServices)) {
        Write-ColorOutput "❌ 服务启动失败" "Red"
        exit 1
    }
    
    # 等待服务完全启动
    Write-ColorOutput "⏳ 等待服务完全启动..." "Yellow"
    Start-Sleep -Seconds 30
    
    Write-ColorOutput "🎉 AIOps平台部署完成！" "Green"
    Write-ColorOutput "📊 访问地址:" "Cyan"
    Write-ColorOutput "   • Grafana仪表板: http://localhost:3000" "White"
    Write-ColorOutput "   • Prometheus监控: http://localhost:9090" "White"
    Write-ColorOutput "   • API网关: http://localhost:8080" "White"
}

# 执行主函数
Main
```

### 3.3 运行部署

```powershell
# 标准部署（使用Docker卷）
.\deploy-aiops.ps1

# 使用本地存储卷部署
.\deploy-aiops.ps1 -UseLocalVolumes

# 跳过先决条件检查
.\deploy-aiops.ps1 -SkipPreCheck
```

### 3.2 验证安装
```powershell
# 检查Docker服务状态
Get-Service -Name "Docker Desktop Service"

# 检查容器运行状态
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 访问Web界面
Start-Process "http://localhost:3000"  # Grafana
Start-Process "http://localhost:8080" # API网关
```

### 3.3 首次登录配置
```powershell
# 等待所有服务启动完成
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 120

# 检查服务健康状态
$services = @{
    "Grafana" = "http://localhost:3000/api/health"
    "Prometheus" = "http://localhost:9090/-/healthy"
    "API Gateway" = "http://localhost:8080/health"
}

foreach ($service in $services.Keys) {
    try {
        $response = Invoke-WebRequest -Uri $services[$service] -TimeoutSec 10 -UseBasicParsing
        Write-Host "✅ $service 服务正常" -ForegroundColor Green
    } catch {
        Write-Host "❌ $service 服务异常" -ForegroundColor Red
    }
}

# 打开管理界面
Write-Host "🌐 正在打开管理界面..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"  # Grafana (admin/grafana-admin-2025)
Start-Process "http://localhost:8080" # API网关
```

### 3.4 验证部署

```powershell
# 验证部署状态
function Test-AIOpsDeployment {
    Write-Host "🔍 验证AIOps平台部署状态" -ForegroundColor Cyan
    
    $services = @(
        @{Name="Traefik"; URL="http://localhost:8080/dashboard/"; Port=8080},
        @{Name="Grafana"; URL="http://localhost:3000"; Port=3000},
        @{Name="Prometheus"; URL="http://localhost:9090"; Port=9090},
        @{Name="API Gateway"; URL="http://localhost:8000/health"; Port=8000}
    )
    
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.URL -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $($service.Name): 运行正常" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "❌ $($service.Name): 无法访问 ($($service.URL))" -ForegroundColor Red
        }
    }
    
    # 检查Docker容器状态
    Write-Host "\n📊 Docker容器状态:" -ForegroundColor Cyan
    docker-compose ps
}

# 运行验证
Test-AIOpsDeployment
```

## 4. 详细安装指南

### 4.1 环境变量配置

创建 `.env` 文件进行详细配置：

```bash
# ===========================================
# AIOps平台环境配置文件 - Windows版本
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
# DATA_PATH=C:\aiops-data
# LOGS_PATH=C:\aiops-logs
# BACKUPS_PATH=C:\aiops-backups
# CONFIG_PATH=C:\aiops-config
```

### 4.2 Windows防火墙配置

```powershell
# 配置Windows防火墙规则
function Set-AIOpsFirewallRules {
    Write-Host "🔥 配置Windows防火墙规则" -ForegroundColor Cyan
    
    $ports = @(
        @{Name="AIOps-Traefik-HTTP"; Port=80; Protocol="TCP"},
        @{Name="AIOps-Traefik-HTTPS"; Port=443; Protocol="TCP"},
        @{Name="AIOps-Traefik-Dashboard"; Port=8080; Protocol="TCP"},
        @{Name="AIOps-Grafana"; Port=3000; Protocol="TCP"},
        @{Name="AIOps-Prometheus"; Port=9090; Protocol="TCP"},
        @{Name="AIOps-API-Gateway"; Port=8000; Protocol="TCP"},
        @{Name="AIOps-PostgreSQL"; Port=5432; Protocol="TCP"},
        @{Name="AIOps-Redis"; Port=6379; Protocol="TCP"}
    )
    
    foreach ($port in $ports) {
        try {
            New-NetFirewallRule -DisplayName $port.Name -Direction Inbound -Protocol $port.Protocol -LocalPort $port.Port -Action Allow -Profile Domain,Private
            Write-Host "✅ 已添加防火墙规则: $($port.Name) (端口 $($port.Port))" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ 添加防火墙规则失败: $($port.Name)" -ForegroundColor Red
        }
    }
}

# 执行防火墙配置
Set-AIOpsFirewallRules
```

### 4.3 服务管理脚本

```powershell
# manage-aiops.ps1 - AIOps服务管理脚本

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "update")]
    [string]$Action,
    
    [string]$Service = "all",
    [switch]$Follow
)

# 服务管理函数
function Invoke-ServiceAction {
    param(
        [string]$Action,
        [string]$Service
    )
    
    switch ($Action) {
        "start" {
            Write-Host "🚀 启动服务: $Service" -ForegroundColor Green
            if ($Service -eq "all") {
                docker-compose up -d
            } else {
                docker-compose up -d $Service
            }
        }
        
        "stop" {
            Write-Host "🛑 停止服务: $Service" -ForegroundColor Yellow
            if ($Service -eq "all") {
                docker-compose down
            } else {
                docker-compose stop $Service
            }
        }
        
        "restart" {
            Write-Host "🔄 重启服务: $Service" -ForegroundColor Cyan
            if ($Service -eq "all") {
                docker-compose restart
            } else {
                docker-compose restart $Service
            }
        }
        
        "status" {
            Write-Host "📊 服务状态:" -ForegroundColor Cyan
            docker-compose ps
        }
        
        "logs" {
            Write-Host "📋 查看日志: $Service" -ForegroundColor Magenta
            if ($Follow) {
                docker-compose logs -f $Service
            } else {
                docker-compose logs --tail=100 $Service
            }
        }
        
        "update" {
            Write-Host "⬆️ 更新服务: $Service" -ForegroundColor Blue
            docker-compose pull $Service
            docker-compose up -d $Service
        }
    }
}

# 执行操作
Invoke-ServiceAction -Action $Action -Service $Service
```

使用示例：

```powershell
# 启动所有服务
.\manage-aiops.ps1 -Action start

# 重启特定服务
.\manage-aiops.ps1 -Action restart -Service grafana

# 查看实时日志
.\manage-aiops.ps1 -Action logs -Service prometheus -Follow

# 检查服务状态
.\manage-aiops.ps1 -Action status
```

## 5. PowerShell脚本工具

### 5.1 系统监控脚本

```powershell
# monitor-system.ps1 - Windows系统监控脚本

function Get-SystemMetrics {
    Write-Host "📊 收集系统指标..." -ForegroundColor Cyan
    
    # CPU使用率
    $cpu = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 3
    $avgCpu = ($cpu.CounterSamples | Measure-Object CookedValue -Average).Average
    
    # 内存使用情况
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem
    $totalMemory = [math]::Round($memory.TotalVisibleMemorySize / 1MB, 2)
    $freeMemory = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
    $usedMemory = $totalMemory - $freeMemory
    $memoryUsage = [math]::Round(($usedMemory / $totalMemory) * 100, 2)
    
    # 磁盘使用情况
    $disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
    $diskUsage = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
    
    # Docker容器状态
    $containers = docker ps --format "table {{.Names}}\t{{.Status}}" | ConvertFrom-Csv -Delimiter "\t"
    
    # 输出结果
    $metrics = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        CPU_Usage = "$([math]::Round($avgCpu, 2))%"
        Memory_Usage = "$memoryUsage% ($usedMemory GB / $totalMemory GB)"
        Disk_Usage = "$diskUsage%"
        Container_Count = $containers.Count
        Running_Containers = ($containers | Where-Object { $_.Status -like "*Up*" }).Count
    }
    
    return $metrics
}

# 监控循环
function Start-ContinuousMonitoring {
    param(
        [int]$IntervalSeconds = 60,
        [string]$LogFile = "aiops-monitor.log"
    )
    
    Write-Host "🔄 开始连续监控 (间隔: $IntervalSeconds 秒)" -ForegroundColor Green
    Write-Host "📝 日志文件: $LogFile" -ForegroundColor Yellow
    
    while ($true) {
        try {
            $metrics = Get-SystemMetrics
            
            # 控制台输出
            Write-Host "\n=== $(Get-Date -Format 'HH:mm:ss') ===" -ForegroundColor Cyan
            $metrics.GetEnumerator() | ForEach-Object {
                Write-Host "$($_.Key): $($_.Value)" -ForegroundColor White
            }
            
            # 写入日志文件
            $logEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $($metrics | ConvertTo-Json -Compress)"
            Add-Content -Path $LogFile -Value $logEntry
            
            # 检查告警条件
            if ([float]($metrics.CPU_Usage -replace '%', '') -gt 80) {
                Write-Host "⚠️ CPU使用率过高: $($metrics.CPU_Usage)" -ForegroundColor Red
            }
            
            if ([float]($metrics.Memory_Usage.Split('%')[0]) -gt 85) {
                Write-Host "⚠️ 内存使用率过高: $($metrics.Memory_Usage)" -ForegroundColor Red
            }
            
            Start-Sleep -Seconds $IntervalSeconds
        }
        catch {
            Write-Host "❌ 监控错误: $($_.Exception.Message)" -ForegroundColor Red
            Start-Sleep -Seconds 10
        }
    }
}

# 启动监控
Start-ContinuousMonitoring -IntervalSeconds 30
```

### 5.2 备份管理脚本

```powershell
# backup-aiops.ps1 - AIOps数据备份脚本

param(
    [string]$BackupPath = "C:\aiops-backups",
    [switch]$IncludeVolumes,
    [switch]$Compress
)

function New-AIOpsBackup {
    param(
        [string]$BackupPath,
        [bool]$IncludeVolumes,
        [bool]$Compress
    )
    
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupDir = Join-Path $BackupPath "aiops-backup-$timestamp"
    
    Write-Host "💾 开始备份AIOps数据..." -ForegroundColor Cyan
    Write-Host "📁 备份目录: $backupDir" -ForegroundColor Yellow
    
    # 创建备份目录
    New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
    
    try {
        # 1. 备份配置文件
        Write-Host "📋 备份配置文件..." -ForegroundColor Green
        $configFiles = @(".env", "docker-compose.yml", "prometheus.yml", "grafana.ini")
        foreach ($file in $configFiles) {
            if (Test-Path $file) {
                Copy-Item $file -Destination $backupDir
                Write-Host "✅ 已备份: $file" -ForegroundColor Green
            }
        }
        
        # 2. 备份数据库
        Write-Host "🗄️ 备份PostgreSQL数据库..." -ForegroundColor Green
        $dbBackupFile = Join-Path $backupDir "postgres-backup.sql"
        docker-compose exec -T postgres pg_dumpall -U aiops > $dbBackupFile
        
        # 3. 备份Grafana仪表板
        Write-Host "📊 备份Grafana配置..." -ForegroundColor Green
        $grafanaBackup = Join-Path $backupDir "grafana-backup.json"
        # 这里可以添加Grafana API调用来备份仪表板
        
        # 4. 备份Docker卷（可选）
        if ($IncludeVolumes) {
            Write-Host "💿 备份Docker存储卷..." -ForegroundColor Green
            $volumesDir = Join-Path $backupDir "volumes"
            New-Item -Path $volumesDir -ItemType Directory -Force | Out-Null
            
            $volumes = docker volume ls --format "{{.Name}}" | Where-Object { $_ -like "aiops*" }
            foreach ($volume in $volumes) {
                $volumeBackup = Join-Path $volumesDir "$volume.tar"
                docker run --rm -v "${volume}:/data" -v "${volumesDir}:/backup" alpine tar czf "/backup/$volume.tar" -C /data .
                Write-Host "✅ 已备份卷: $volume" -ForegroundColor Green
            }
        }
        
        # 5. 压缩备份（可选）
        if ($Compress) {
            Write-Host "🗜️ 压缩备份文件..." -ForegroundColor Green
            $zipFile = "$backupDir.zip"
            Compress-Archive -Path $backupDir -DestinationPath $zipFile
            Remove-Item -Path $backupDir -Recurse -Force
            Write-Host "✅ 备份已压缩: $zipFile" -ForegroundColor Green
        }
        
        Write-Host "🎉 备份完成!" -ForegroundColor Green
        
    }
    catch {
        Write-Host "❌ 备份失败: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
    
    return $true
}

# 执行备份
New-AIOpsBackup -BackupPath $BackupPath -IncludeVolumes:$IncludeVolumes -Compress:$Compress
```

---

#### 4.1.1 安装Docker Desktop
```powershell
# 下载Docker Desktop for Windows
$dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$installerPath = "$env:TEMP\DockerDesktopInstaller.exe"

Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath
Start-Process -FilePath $installerPath -ArgumentList "install", "--quiet" -Wait

# 启动Docker Desktop
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

#### 4.1.2 配置PowerShell执行策略
```powershell
# 设置执行策略允许本地脚本运行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# 验证PowerShell版本
$PSVersionTable.PSVersion
```

#### 4.1.3 安装Git
```powershell
# 使用Chocolatey安装Git (如果已安装Chocolatey)
choco install git -y

# 或者使用winget安装
winget install --id Git.Git -e --source winget
```

### 4.2 克隆项目
```powershell
# 创建工作目录
$workDir = "C:\AIOps"
New-Item -ItemType Directory -Path $workDir -Force
Set-Location $workDir

# 克隆项目代码
git clone https://github.com/your-org/aiops.git
Set-Location .\aiops
```

### 4.3 配置环境变量
```powershell
# 创建环境配置文件
$envContent = @"
# AIOps Windows环境配置
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

# 监控配置
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=grafana-admin-2025

# Windows特定配置
WINDOWS_EVENT_LOG_ENABLED=true
POWERSHELL_EXECUTION_POLICY=RemoteSigned
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8
```

### 4.4 启动服务
```powershell
# 构建并启动所有服务
docker-compose up -d --build

# 等待服务启动完成
Start-Sleep -Seconds 60

# 检查服务健康状态
docker-compose ps
```

---

## 5. PowerShell脚本工具

### 5.1 系统管理脚本

#### 5.1.1 服务控制脚本
```powershell
# scripts/Manage-AIOpsServices.ps1
<#
.SYNOPSIS
    AIOps服务管理脚本
.DESCRIPTION
    用于启动、停止、重启和监控AIOps平台服务
.PARAMETER Action
    操作类型: start, stop, restart, status, logs
.PARAMETER Service
    指定服务名称，默认为所有服务
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "update")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Service = "all"
)

# 设置工作目录
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$projectRoot = Split-Path -Parent $scriptPath
Set-Location $projectRoot

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Start-AIOpsServices {
    Write-ColorOutput "🚀 启动AIOps服务..." "Green"
    
    if ($Service -eq "all") {
        docker-compose up -d
    } else {
        docker-compose up -d $Service
    }
    
    Write-ColorOutput "✅ 服务启动完成" "Green"
}

function Stop-AIOpsServices {
    Write-ColorOutput "🛑 停止AIOps服务..." "Yellow"
    
    if ($Service -eq "all") {
        docker-compose down
    } else {
        docker-compose stop $Service
    }
    
    Write-ColorOutput "✅ 服务停止完成" "Yellow"
}

function Restart-AIOpsServices {
    Write-ColorOutput "🔄 重启AIOps服务..." "Cyan"
    Stop-AIOpsServices
    Start-Sleep -Seconds 5
    Start-AIOpsServices
}

function Get-AIOpsStatus {
    Write-ColorOutput "📊 AIOps服务状态:" "Cyan"
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    
    Write-ColorOutput "\n💾 存储卷使用情况:" "Cyan"
    docker volume ls --filter "name=aiops"
    
    Write-ColorOutput "\n🌐 网络状态:" "Cyan"
    docker network ls --filter "name=aiops"
}

function Get-AIOpsLogs {
    Write-ColorOutput "📋 获取服务日志..." "Cyan"
    
    if ($Service -eq "all") {
        docker-compose logs --tail=100 -f
    } else {
        docker-compose logs --tail=100 -f $Service
    }
}

function Update-AIOpsServices {
    Write-ColorOutput "⬆️ 更新AIOps服务..." "Magenta"
    
    # 拉取最新代码
    git pull origin main
    
    # 重新构建并启动服务
    docker-compose down
    docker-compose pull
    docker-compose up -d --build
    
    Write-ColorOutput "✅ 更新完成" "Green"
}

# 主逻辑
switch ($Action) {
    "start" { Start-AIOpsServices }
    "stop" { Stop-AIOpsServices }
    "restart" { Restart-AIOpsServices }
    "status" { Get-AIOpsStatus }
    "logs" { Get-AIOpsLogs }
    "update" { Update-AIOpsServices }
}
```

#### 5.1.2 系统监控脚本
```powershell
# scripts/Monitor-WindowsSystem.ps1
<#
.SYNOPSIS
    Windows系统监控脚本
.DESCRIPTION
    监控Windows系统性能并发送到Prometheus
#>

function Get-WindowsMetrics {
    $metrics = @{}
    
    # CPU使用率
    $cpu = Get-Counter "\Processor(_Total)\% Processor Time" -SampleInterval 1 -MaxSamples 1
    $metrics["cpu_usage_percent"] = [math]::Round(100 - $cpu.CounterSamples.CookedValue, 2)
    
    # 内存使用情况
    $memory = Get-CimInstance -ClassName Win32_OperatingSystem
    $totalMemory = $memory.TotalVisibleMemorySize * 1KB
    $freeMemory = $memory.FreePhysicalMemory * 1KB
    $usedMemory = $totalMemory - $freeMemory
    $metrics["memory_usage_percent"] = [math]::Round(($usedMemory / $totalMemory) * 100, 2)
    $metrics["memory_total_bytes"] = $totalMemory
    $metrics["memory_used_bytes"] = $usedMemory
    
    # 磁盘使用情况
    $disks = Get-CimInstance -ClassName Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
    foreach ($disk in $disks) {
        $driveLetter = $disk.DeviceID.Replace(":", "")
        $metrics["disk_usage_percent_$driveLetter"] = [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 2)
        $metrics["disk_total_bytes_$driveLetter"] = $disk.Size
        $metrics["disk_free_bytes_$driveLetter"] = $disk.FreeSpace
    }
    
    # 网络流量
    $networkAdapters = Get-Counter "\Network Interface(*)\Bytes Total/sec" -SampleInterval 1 -MaxSamples 1
    $totalNetworkBytes = ($networkAdapters.CounterSamples | Where-Object { $_.InstanceName -ne "_Total" -and $_.InstanceName -notlike "*Loopback*" } | Measure-Object -Property CookedValue -Sum).Sum
    $metrics["network_bytes_per_second"] = [math]::Round($totalNetworkBytes, 2)
    
    # Windows服务状态
    $criticalServices = @("Docker Desktop Service", "Hyper-V Host Compute Service", "Windows Management Instrumentation")
    foreach ($serviceName in $criticalServices) {
        $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
        if ($service) {
            $metrics["service_status_$($serviceName.Replace(' ', '_'))"] = if ($service.Status -eq "Running") { 1 } else { 0 }
        }
    }
    
    return $metrics
}

function Send-MetricsToPrometheus {
    param([hashtable]$Metrics)
    
    $prometheusGateway = "http://localhost:9091/metrics/job/windows-system/instance/localhost"
    
    $metricsText = ""
    foreach ($key in $Metrics.Keys) {
        $metricsText += "windows_$key $($Metrics[$key])\n"
    }
    
    try {
        Invoke-RestMethod -Uri $prometheusGateway -Method Post -Body $metricsText -ContentType "text/plain"
        Write-Host "✅ 指标已发送到Prometheus" -ForegroundColor Green
    } catch {
        Write-Host "❌ 发送指标失败: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 主循环
while ($true) {
    try {
        $metrics = Get-WindowsMetrics
        Send-MetricsToPrometheus -Metrics $metrics
        
        Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - 系统指标已更新" -ForegroundColor Cyan
        Start-Sleep -Seconds 30
    } catch {
        Write-Host "❌ 监控脚本错误: $($_.Exception.Message)" -ForegroundColor Red
        Start-Sleep -Seconds 60
    }
}
```

### 5.2 自动化运维脚本

#### 5.2.1 备份脚本
```powershell
# scripts/Backup-AIOpsData.ps1
<#
.SYNOPSIS
    AIOps数据备份脚本
.DESCRIPTION
    备份Docker存储卷和配置文件
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "C:\AIOps\Backups\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
)

function New-BackupDirectory {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "✅ 创建备份目录: $Path" -ForegroundColor Green
    }
}

function Backup-DockerVolumes {
    param([string]$BackupPath)
    
    Write-Host "📦 备份Docker存储卷..." -ForegroundColor Cyan
    
    $volumes = @(
        "aiops_prometheus-data",
        "aiops_grafana-data", 
        "aiops_postgres-data",
        "aiops_redis-data",
        "aiops_ai-models",
        "aiops_ai-logs"
    )
    
    foreach ($volume in $volumes) {
        $volumeBackupPath = Join-Path $BackupPath "volumes\$volume"
        New-Item -ItemType Directory -Path $volumeBackupPath -Force | Out-Null
        
        # 使用临时容器备份卷数据
        docker run --rm -v "${volume}:/data" -v "${volumeBackupPath}:/backup" alpine tar czf "/backup/data.tar.gz" -C /data .
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 已备份卷: $volume" -ForegroundColor Green
        } else {
            Write-Host "❌ 备份卷失败: $volume" -ForegroundColor Red
        }
    }
}

function Backup-ConfigFiles {
    param([string]$BackupPath)
    
    Write-Host "📄 备份配置文件..." -ForegroundColor Cyan
    
    $configPath = Join-Path $BackupPath "configs"
    New-Item -ItemType Directory -Path $configPath -Force | Out-Null
    
    # 备份主要配置文件
    $filesToBackup = @(
        "docker-compose.yml",
        ".env",
        "configs\*"
    )
    
    foreach ($file in $filesToBackup) {
        if (Test-Path $file) {
            Copy-Item -Path $file -Destination $configPath -Recurse -Force
            Write-Host "✅ 已备份: $file" -ForegroundColor Green
        }
    }
}

function Create-BackupManifest {
    param([string]$BackupPath)
    
    $manifest = @{
        "backup_time" = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        "backup_version" = "3.0.0"
        "system_info" = @{
            "os" = "Windows"
            "powershell_version" = $PSVersionTable.PSVersion.ToString()
            "docker_version" = (docker --version)
        }
        "volumes_backed_up" = @(
            "prometheus-data", "grafana-data", "postgres-data", 
            "redis-data", "ai-models", "ai-logs"
        )
    }
    
    $manifestPath = Join-Path $BackupPath "backup-manifest.json"
    $manifest | ConvertTo-Json -Depth 3 | Out-File -FilePath $manifestPath -Encoding UTF8
    
    Write-Host "📋 备份清单已创建: $manifestPath" -ForegroundColor Green
}

# 主备份流程
Write-Host "🚀 开始AIOps数据备份..." -ForegroundColor Yellow

New-BackupDirectory -Path $BackupPath
Backup-DockerVolumes -BackupPath $BackupPath
Backup-ConfigFiles -BackupPath $BackupPath
Create-BackupManifest -BackupPath $BackupPath

Write-Host "✅ 备份完成! 备份位置: $BackupPath" -ForegroundColor Green
```

---

## 6. Windows特定配置

### 6.1 Windows事件日志集成
```powershell
# 配置Windows事件日志收集
$eventLogConfig = @"
windows:
  event_logs:
    - name: Application
      level: Error,Warning
    - name: System  
      level: Error,Warning,Critical
    - name: Security
      level: Failure Audit
  performance_counters:
    - "\Processor(_Total)\% Processor Time"
    - "\Memory\Available MBytes"
    - "\PhysicalDisk(_Total)\% Disk Time"
"@

$eventLogConfig | Out-File -FilePath "configs\windows-monitoring.yml" -Encoding UTF8
```

### 6.2 防火墙配置
```powershell
# 配置Windows防火墙规则
function Set-AIOpsFirewallRules {
    $ports = @(80, 443, 3000, 8080, 9090, 8000, 8001, 5432, 6379)
    
    foreach ($port in $ports) {
        New-NetFirewallRule -DisplayName "AIOps-Port-$port" -Direction Inbound -Protocol TCP -LocalPort $port -Action Allow -ErrorAction SilentlyContinue
        Write-Host "✅ 已开放端口: $port" -ForegroundColor Green
    }
}

Set-AIOpsFirewallRules
```

### 6.3 Windows服务注册
```powershell
# 将AIOps注册为Windows服务
$serviceName = "AIOps-Platform"
$serviceDisplayName = "AIOps智能运维平台"
$servicePath = "C:\AIOps\scripts\AIOps-Service.ps1"

# 创建服务包装脚本
$serviceScript = @"
Set-Location "C:\AIOps\aiops"
docker-compose up -d

while (`$true) {
    Start-Sleep -Seconds 30
    `$status = docker-compose ps -q
    if (-not `$status) {
        Write-EventLog -LogName Application -Source "AIOps" -EventId 1001 -EntryType Warning -Message "AIOps服务异常，正在重启..."
        docker-compose up -d
    }
}
"@

$serviceScript | Out-File -FilePath $servicePath -Encoding UTF8

# 使用NSSM注册服务 (需要先安装NSSM)
# nssm install $serviceName powershell.exe "-ExecutionPolicy Bypass -File $servicePath"
```

---

## 7. 服务管理

### 7.1 服务启动顺序
```powershell
# 按依赖关系启动服务
function Start-AIOpsInOrder {
    $startupOrder = @(
        @("traefik", "postgres", "redis"),           # 基础服务
        @("prometheus", "grafana"),                   # 监控服务  
        @("ai-engine"),                              # AI服务
        @("self-healing", "api-gateway"),           # 应用服务
        @("node-exporter", "cadvisor")              # 指标收集
    )
    
    foreach ($group in $startupOrder) {
        Write-Host "🚀 启动服务组: $($group -join ', ')" -ForegroundColor Cyan
        
        foreach ($service in $group) {
            docker-compose up -d $service
            Start-Sleep -Seconds 10
        }
        
        # 等待服务组启动完成
        Start-Sleep -Seconds 30
    }
}
```

### 7.2 健康检查
```powershell
# 服务健康检查脚本
function Test-AIOpsHealth {
    $healthChecks = @{
        "Grafana" = "http://localhost:3000/api/health"
        "Prometheus" = "http://localhost:9090/-/healthy"
        "API Gateway" = "http://localhost:8080/health"
        "AI Engine" = "http://localhost:8000/health"
        "Self Healing" = "http://localhost:8001/health"
    }
    
    Write-Host "🏥 执行健康检查..." -ForegroundColor Cyan
    
    foreach ($service in $healthChecks.Keys) {
        try {
            $response = Invoke-WebRequest -Uri $healthChecks[$service] -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $service - 健康" -ForegroundColor Green
            } else {
                Write-Host "⚠️ $service - 状态码: $($response.StatusCode)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ $service - 不可访问" -ForegroundColor Red
        }
    }
}
```

---

## 8. 监控和告警

### 8.1 Grafana仪表板配置
访问 http://localhost:3000 配置Windows专用仪表板:

- **默认登录**: admin / grafana-admin-2025
- **Windows系统监控**: CPU、内存、磁盘、网络
- **Docker容器监控**: 容器状态、资源使用
- **应用性能监控**: 响应时间、错误率

### 8.2 告警规则配置
```yaml
# configs/prometheus/windows-alerts.yml
groups:
  - name: windows-system
    rules:
      - alert: WindowsHighCPU
        expr: windows_cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Windows CPU使用率过高"
          description: "CPU使用率已超过80%，当前值: {{ $value }}%"
      
      - alert: WindowsHighMemory
        expr: windows_memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Windows内存使用率过高"
          description: "内存使用率已超过85%，当前值: {{ $value }}%"
      
      - alert: WindowsServiceDown
        expr: windows_service_status_Docker_Desktop_Service == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Docker Desktop服务已停止"
          description: "Docker Desktop服务不可用，请检查服务状态"
```

---

## 9. 故障排除

### 9.1 常见问题

#### 9.1.1 Docker Desktop启动失败
```powershell
# 检查Hyper-V状态
Get-WindowsOptionalFeature -FeatureName Microsoft-Hyper-V-All -Online

# 重启Docker Desktop
Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"

# 检查Docker守护进程
docker version
```

#### 9.1.2 容器无法启动
```powershell
# 查看容器日志
docker-compose logs [service-name]

# 检查端口占用
netstat -ano | findstr :3000

# 清理Docker资源
docker system prune -f
docker volume prune -f
```

#### 9.1.3 网络连接问题
```powershell
# 检查Docker网络
docker network ls
docker network inspect aiops_frontend

# 重建网络
docker-compose down
docker network prune -f
docker-compose up -d
```

### 9.2 日志分析
```powershell
# 收集系统日志
function Collect-AIOpsLogs {
    $logPath = "C:\AIOps\Logs\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    New-Item -ItemType Directory -Path $logPath -Force
    
    # Docker日志
    docker-compose logs > "$logPath\docker-compose.log"
    
    # Windows事件日志
    Get-EventLog -LogName Application -After (Get-Date).AddHours(-24) | Export-Csv "$logPath\application-events.csv"
    Get-EventLog -LogName System -After (Get-Date).AddHours(-24) | Export-Csv "$logPath\system-events.csv"
    
    # 系统信息
    Get-ComputerInfo | Out-File "$logPath\system-info.txt"
    
    Write-Host "📋 日志已收集到: $logPath" -ForegroundColor Green
}
```

---

## 10. 性能优化

### 10.1 Docker配置优化
```json
// C:\Users\[用户名]\.docker\daemon.json
{
  "experimental": false,
  "features": {
    "buildkit": true
  },
  "builder": {
    "gc": {
      "enabled": true,
      "defaultKeepStorage": "20GB"
    }
  },
  "max-concurrent-downloads": 6,
  "max-concurrent-uploads": 6,
  "storage-driver": "windowsfilter",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

### 10.2 系统性能调优
```powershell
# Windows性能优化脚本
function Optimize-WindowsForAIOps {
    # 设置高性能电源计划
    powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
    
    # 优化虚拟内存
    $totalRAM = (Get-CimInstance -ClassName Win32_ComputerSystem).TotalPhysicalMemory
    $recommendedPageFile = [math]::Round($totalRAM / 1GB * 1.5, 0)
    
    Write-Host "💡 建议设置虚拟内存为: ${recommendedPageFile}GB" -ForegroundColor Yellow
    
    # 禁用不必要的服务
    $servicesToDisable = @("Fax", "TabletInputService", "WSearch")
    foreach ($service in $servicesToDisable) {
        Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
    }
    
    # 优化网络设置
    netsh int tcp set global autotuninglevel=normal
    netsh int tcp set global chimney=enabled
    netsh int tcp set global rss=enabled
    
    Write-Host "✅ Windows性能优化完成" -ForegroundColor Green
}
```

---

## 11. 安全配置

### 11.1 访问控制
```powershell
# 配置基于角色的访问控制
$securityConfig = @"
security:
  authentication:
    method: "ldap"  # 或 "local"
    ldap:
      server: "ldap://your-domain-controller:389"
      base_dn: "DC=company,DC=com"
      user_filter: "(sAMAccountName={username})"
  
  authorization:
    roles:
      admin:
        - "*"
      operator:
        - "read:*"
        - "write:monitoring"
      viewer:
        - "read:dashboard"
        - "read:metrics"
"@

$securityConfig | Out-File -FilePath "configs\security.yml" -Encoding UTF8
```

### 11.2 SSL/TLS配置
```powershell
# 生成自签名证书 (开发环境)
function New-AIOpsSSLCertificate {
    $certPath = "C:\AIOps\certs"
    New-Item -ItemType Directory -Path $certPath -Force
    
    # 使用OpenSSL或PowerShell生成证书
    $cert = New-SelfSignedCertificate -DnsName "localhost", "aiops.local" -CertStoreLocation "cert:\LocalMachine\My" -KeyLength 2048 -NotAfter (Get-Date).AddYears(1)
    
    # 导出证书
    $certPassword = ConvertTo-SecureString -String "aiops-cert-2025" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "$certPath\aiops.pfx" -Password $certPassword
    
    Write-Host "🔒 SSL证书已生成: $certPath\aiops.pfx" -ForegroundColor Green
}
```

---

## 12. 备份和恢复

### 12.1 自动备份配置
```powershell
# 配置定时备份任务
function Register-AIOpsBackupTask {
    $taskName = "AIOps-Daily-Backup"
    $scriptPath = "C:\AIOps\scripts\Backup-AIOpsData.ps1"
    
    # 创建计划任务
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File '$scriptPath'"
    $trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"
    $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2)
    
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "AIOps平台每日自动备份"
    
    Write-Host "⏰ 已注册每日备份任务: $taskName" -ForegroundColor Green
}
```

### 12.2 数据恢复
```powershell
# 数据恢复脚本
function Restore-AIOpsData {
    param(
        [Parameter(Mandatory=$true)]
        [string]$BackupPath
    )
    
    if (-not (Test-Path $BackupPath)) {
        Write-Host "❌ 备份路径不存在: $BackupPath" -ForegroundColor Red
        return
    }
    
    Write-Host "🔄 开始恢复AIOps数据..." -ForegroundColor Yellow
    
    # 停止服务
    docker-compose down
    
    # 恢复存储卷
    $volumesPath = Join-Path $BackupPath "volumes"
    if (Test-Path $volumesPath) {
        $volumes = Get-ChildItem $volumesPath -Directory
        
        foreach ($volume in $volumes) {
            $volumeName = $volume.Name
            $backupFile = Join-Path $volume.FullName "data.tar.gz"
            
            if (Test-Path $backupFile) {
                # 创建临时容器恢复数据
                docker volume create $volumeName
                docker run --rm -v "${volumeName}:/data" -v "${backupFile}:/backup/data.tar.gz" alpine tar xzf "/backup/data.tar.gz" -C /data
                
                Write-Host "✅ 已恢复卷: $volumeName" -ForegroundColor Green
            }
        }
    }
    
    # 恢复配置文件
    $configsPath = Join-Path $BackupPath "configs"
    if (Test-Path $configsPath) {
        Copy-Item -Path "$configsPath\*" -Destination "." -Recurse -Force
        Write-Host "✅ 已恢复配置文件" -ForegroundColor Green
    }
    
    # 重启服务
    docker-compose up -d
    
    Write-Host "✅ 数据恢复完成!" -ForegroundColor Green
}
```

---

## 附录

### A. PowerShell模块依赖
```powershell
# 安装必需的PowerShell模块
Install-Module -Name DockerMsftProvider -Force
Install-Module -Name Posh-Docker -Force
Install-Module -Name PSWindowsUpdate -Force
```

### B. 环境变量参考
| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| COMPOSE_PROJECT_NAME | aiops | Docker Compose项目名 |
| POSTGRES_PASSWORD | aiops-secure-password-2025 | PostgreSQL密码 |
| REDIS_PASSWORD | redis-secure-password-2025 | Redis密码 |
| GRAFANA_ADMIN_PASSWORD | grafana-admin-2025 | Grafana管理员密码 |
| WINDOWS_EVENT_LOG_ENABLED | true | 启用Windows事件日志 |

### C. 端口映射表
| 内部端口 | 外部端口 | 服务 | 协议 |
|----------|----------|------|------|
| 80 | 80 | Traefik HTTP | HTTP |
| 443 | 443 | Traefik HTTPS | HTTPS |
| 3000 | 3000 | Grafana | HTTP |
| 8080 | 8080 | API Gateway | HTTP |
| 9090 | 9090 | Prometheus | HTTP |
| 8000 | 8000 | AI Engine | HTTP |
| 8001 | 8001 | Self Healing | HTTP |
| 5432 | 5432 | PostgreSQL | TCP |
| 6379 | 6379 | Redis | TCP |

### D. 技术支持
- **文档版本**: v3.0.0
- **支持邮箱**: support@aiops-platform.com
- **技术论坛**: https://forum.aiops-platform.com
- **GitHub仓库**: https://github.com/your-org/aiops

---

*本文档专为Windows环境设计，包含完整的PowerShell脚本和Windows特定配置。如需其他操作系统版本，请参考对应的用户手册。*