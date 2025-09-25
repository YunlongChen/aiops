# 服务器热控制系统部署脚本
# PowerShell脚本用于部署和管理Docker容器服务

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("up", "down", "restart", "logs", "status", "clean", "backup", "restore")]
    [string]$Action = "up",
    
    [Parameter(Mandatory=$false)]
    [string]$Service = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Build,
    
    [Parameter(Mandatory=$false)]
    [switch]$Detach = $true,
    
    [Parameter(Mandatory=$false)]
    [switch]$Follow,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "backups"
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" "Yellow"
}

# 检查依赖
function Test-Dependencies {
    Write-Info "检查部署依赖..."
    
    # 检查Docker
    if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
        Write-Error "未找到Docker，请先安装Docker"
        exit 1
    }
    
    # 检查Docker Compose
    if (-not (Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
        Write-Error "未找到Docker Compose，请先安装Docker Compose"
        exit 1
    }
    
    # 检查docker-compose.yml文件
    if (-not (Test-Path "docker-compose.yml")) {
        Write-Error "未找到docker-compose.yml文件"
        exit 1
    }
    
    Write-Success "依赖检查完成"
}

# 创建必要的目录和文件
function Initialize-Environment {
    Write-Info "初始化部署环境..."
    
    # 创建必要的目录
    $directories = @(
        "data",
        "logs", 
        "config",
        "grafana/dashboards",
        "grafana/datasources",
        "prometheus",
        "nginx",
        "nginx/ssl",
        $BackupPath
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Info "创建目录: $dir"
        }
    }
    
    # 创建Prometheus配置文件
    if (-not (Test-Path "prometheus/prometheus.yml")) {
        $prometheusConfig = @"
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'thermal-control'
    static_configs:
      - targets: ['thermal-control:8080']
    metrics_path: '/api/v1/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
"@
        Set-Content -Path "prometheus/prometheus.yml" -Value $prometheusConfig
        Write-Info "创建Prometheus配置文件"
    }
    
    # 创建Nginx配置文件
    if (-not (Test-Path "nginx/nginx.conf")) {
        $nginxConfig = @"
events {
    worker_connections 1024;
}

http {
    upstream thermal_backend {
        server thermal-control:8080;
    }
    
    upstream grafana_backend {
        server grafana:3000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://thermal_backend;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }

        location /grafana/ {
            proxy_pass http://grafana_backend/;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto `$scheme;
        }
    }
}
"@
        Set-Content -Path "nginx/nginx.conf" -Value $nginxConfig
        Write-Info "创建Nginx配置文件"
    }
    
    Write-Success "环境初始化完成"
}

# 启动服务
function Start-Services {
    Write-Info "启动服务..."
    
    $composeArgs = @("up")
    
    if ($Detach) {
        $composeArgs += "-d"
    }
    
    if ($Build) {
        $composeArgs += "--build"
    }
    
    if ($Service) {
        $composeArgs += $Service
    }
    
    try {
        & docker-compose @composeArgs
        Write-Success "服务启动完成"
        
        if ($Detach) {
            Start-Sleep -Seconds 5
            Show-ServiceStatus
        }
    }
    catch {
        Write-Error "服务启动失败: $_"
        exit 1
    }
}

# 停止服务
function Stop-Services {
    Write-Info "停止服务..."
    
    $composeArgs = @("down")
    
    if ($Service) {
        $composeArgs = @("stop", $Service)
    }
    
    try {
        & docker-compose @composeArgs
        Write-Success "服务停止完成"
    }
    catch {
        Write-Error "服务停止失败: $_"
        exit 1
    }
}

# 重启服务
function Restart-Services {
    Write-Info "重启服务..."
    
    if ($Service) {
        try {
            & docker-compose restart $Service
            Write-Success "服务 $Service 重启完成"
        }
        catch {
            Write-Error "服务重启失败: $_"
            exit 1
        }
    } else {
        Stop-Services
        Start-Services
    }
}

# 查看日志
function Show-Logs {
    Write-Info "查看服务日志..."
    
    $logsArgs = @("logs")
    
    if ($Follow) {
        $logsArgs += "-f"
    }
    
    if ($Service) {
        $logsArgs += $Service
    }
    
    try {
        & docker-compose @logsArgs
    }
    catch {
        Write-Error "查看日志失败: $_"
        exit 1
    }
}

# 显示服务状态
function Show-ServiceStatus {
    Write-Info "服务状态:"
    
    try {
        & docker-compose ps
        
        Write-Info "`n网络状态:"
        & docker network ls | Where-Object { $_ -match "thermal" }
        
        Write-Info "`n存储卷状态:"
        & docker volume ls | Where-Object { $_ -match "thermal" }
        
        Write-Info "`n服务访问地址:"
        Write-ColorOutput "主应用: http://localhost:8080" "Green"
        Write-ColorOutput "Grafana: http://localhost:3000 (admin/admin123)" "Green"
        Write-ColorOutput "Prometheus: http://localhost:9090" "Green"
        Write-ColorOutput "API文档: http://localhost:8080/api/v1" "Green"
        Write-ColorOutput "健康检查: http://localhost:8080/api/v1/health" "Green"
    }
    catch {
        Write-Error "获取状态失败: $_"
        exit 1
    }
}

# 清理资源
function Invoke-Clean {
    Write-Warning "这将删除所有容器、网络和存储卷，是否继续? (y/N)"
    $confirm = Read-Host
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Info "清理Docker资源..."
        
        try {
            # 停止并删除容器
            & docker-compose down -v --remove-orphans
            
            # 删除镜像
            $images = & docker images --filter "reference=*thermal*" -q
            if ($images) {
                & docker rmi $images -f
            }
            
            # 清理未使用的资源
            & docker system prune -f
            
            Write-Success "清理完成"
        }
        catch {
            Write-Error "清理失败: $_"
            exit 1
        }
    } else {
        Write-Info "取消清理操作"
    }
}

# 备份数据
function Invoke-Backup {
    Write-Info "备份数据..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = Join-Path $BackupPath $timestamp
    
    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    }
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    try {
        # 备份数据库
        Write-Info "备份数据库..."
        & docker-compose exec -T postgres pg_dump -U thermal_user thermal_control > "$backupDir/database.sql"
        
        # 备份配置文件
        Write-Info "备份配置文件..."
        Copy-Item -Path "config" -Destination "$backupDir/config" -Recurse -Force
        
        # 备份数据目录
        if (Test-Path "data") {
            Write-Info "备份数据目录..."
            Copy-Item -Path "data" -Destination "$backupDir/data" -Recurse -Force
        }
        
        # 创建备份信息文件
        $backupInfo = @{
            timestamp = $timestamp
            version = "1.0.0"
            services = @(& docker-compose ps --services)
        } | ConvertTo-Json -Depth 3
        
        Set-Content -Path "$backupDir/backup_info.json" -Value $backupInfo
        
        Write-Success "备份完成: $backupDir"
    }
    catch {
        Write-Error "备份失败: $_"
        exit 1
    }
}

# 恢复数据
function Invoke-Restore {
    param([string]$RestorePath)
    
    if (-not $RestorePath) {
        Write-Info "可用的备份:"
        Get-ChildItem $BackupPath -Directory | Sort-Object Name -Descending | ForEach-Object {
            Write-ColorOutput $_.Name "Yellow"
        }
        
        $RestorePath = Read-Host "请输入要恢复的备份目录名"
    }
    
    $fullRestorePath = Join-Path $BackupPath $RestorePath
    
    if (-not (Test-Path $fullRestorePath)) {
        Write-Error "备份目录不存在: $fullRestorePath"
        exit 1
    }
    
    Write-Warning "这将覆盖当前数据，是否继续? (y/N)"
    $confirm = Read-Host
    
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        Write-Info "恢复数据..."
        
        try {
            # 停止服务
            & docker-compose stop
            
            # 恢复数据库
            if (Test-Path "$fullRestorePath/database.sql") {
                Write-Info "恢复数据库..."
                & docker-compose up -d postgres
                Start-Sleep -Seconds 10
                Get-Content "$fullRestorePath/database.sql" | & docker-compose exec -T postgres psql -U thermal_user -d thermal_control
            }
            
            # 恢复配置文件
            if (Test-Path "$fullRestorePath/config") {
                Write-Info "恢复配置文件..."
                Remove-Item -Path "config" -Recurse -Force -ErrorAction SilentlyContinue
                Copy-Item -Path "$fullRestorePath/config" -Destination "config" -Recurse -Force
            }
            
            # 恢复数据目录
            if (Test-Path "$fullRestorePath/data") {
                Write-Info "恢复数据目录..."
                Remove-Item -Path "data" -Recurse -Force -ErrorAction SilentlyContinue
                Copy-Item -Path "$fullRestorePath/data" -Destination "data" -Recurse -Force
            }
            
            # 重启所有服务
            & docker-compose up -d
            
            Write-Success "恢复完成"
        }
        catch {
            Write-Error "恢复失败: $_"
            exit 1
        }
    } else {
        Write-Info "取消恢复操作"
    }
}

# 主函数
function Main {
    Write-ColorOutput "=== 服务器热控制系统部署脚本 ===" "Magenta"
    Write-Info "操作: $Action"
    
    # 检查依赖
    Test-Dependencies
    
    # 初始化环境
    if ($Action -ne "clean") {
        Initialize-Environment
    }
    
    switch ($Action) {
        "up" {
            Start-Services
        }
        "down" {
            Stop-Services
        }
        "restart" {
            Restart-Services
        }
        "logs" {
            Show-Logs
        }
        "status" {
            Show-ServiceStatus
        }
        "clean" {
            Invoke-Clean
        }
        "backup" {
            Invoke-Backup
        }
        "restore" {
            Invoke-Restore
        }
        default {
            Write-Error "未知操作: $Action"
            exit 1
        }
    }
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput @"
服务器热控制系统部署脚本

用法: .\deploy.ps1 [选项]

选项:
  -Action <action>     执行的操作 (up, down, restart, logs, status, clean, backup, restore)
  -Service <service>   指定服务名称
  -Build              构建镜像
  -Detach             后台运行 (默认启用)
  -Follow             跟踪日志输出
  -BackupPath <path>  备份路径 (默认: backups)

示例:
  .\deploy.ps1 -Action up -Build
  .\deploy.ps1 -Action logs -Service thermal-control -Follow
  .\deploy.ps1 -Action restart -Service postgres
  .\deploy.ps1 -Action backup
  .\deploy.ps1 -Action restore

"@ "Yellow"
}

# 脚本入口点
if ($args -contains "-h" -or $args -contains "--help") {
    Show-Help
    exit 0
}

try {
    Main
}
catch {
    Write-Error "脚本执行失败: $_"
    exit 1
}