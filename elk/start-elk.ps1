<#
.SYNOPSIS
    ELK Stack启动和管理脚本
    
.DESCRIPTION
    AIOps平台ELK日志处理堆栈的启动、停止、重启和管理脚本
    支持Elasticsearch、Logstash、Kibana及相关Beat组件的管理
    
.PARAMETER Action
    操作类型: start, stop, restart, status, logs, cleanup, health, setup
    
.PARAMETER Service
    指定服务: elasticsearch, logstash, kibana, filebeat, metricbeat, heartbeat, apm-server, all
    
.PARAMETER Follow
    是否跟踪日志输出
    
.PARAMETER Lines
    显示日志行数
    
.EXAMPLE
    .\start-elk.ps1 -Action start
    启动所有ELK服务
    
.EXAMPLE
    .\start-elk.ps1 -Action stop -Service elasticsearch
    停止Elasticsearch服务
    
.EXAMPLE
    .\start-elk.ps1 -Action logs -Service kibana -Follow
    跟踪Kibana日志
    
.NOTES
    作者: AI Assistant
    版本: 1.0.0
    创建时间: 2024
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "cleanup", "health", "setup", "backup", "restore")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("elasticsearch", "logstash", "kibana", "filebeat", "metricbeat", "heartbeat", "apm-server", "elasticsearch-exporter", "all")]
    [string]$Service = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$Follow,
    
    [Parameter(Mandatory=$false)]
    [int]$Lines = 100,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [string]$BackupPath = "./backups",
    
    [Parameter(Mandatory=$false)]
    [switch]$Verbose
)

# ===========================================
# 全局变量
# ===========================================
$script:ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$script:ProjectRoot = Split-Path -Parent $script:ScriptPath
$script:ComposeFile = Join-Path $script:ScriptPath "docker-compose.yml"
$script:EnvFile = Join-Path $script:ScriptPath ".env"
$script:DataDir = Join-Path $script:ScriptPath "data"
$script:LogsDir = Join-Path $script:ScriptPath "logs"
$script:BackupsDir = Join-Path $script:ScriptPath "backups"

# 服务列表
$script:AllServices = @(
    "elasticsearch",
    "logstash", 
    "kibana",
    "filebeat",
    "metricbeat",
    "heartbeat",
    "apm-server",
    "elasticsearch-exporter"
)

# 核心服务（启动顺序）
$script:CoreServices = @(
    "elasticsearch",
    "logstash",
    "kibana"
)

# Beat服务
$script:BeatServices = @(
    "filebeat",
    "metricbeat",
    "heartbeat"
)

# 颜色配置
$script:Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Debug = "Magenta"
}

# ===========================================
# 辅助函数
# ===========================================

<#
.SYNOPSIS
    写入彩色日志消息
#>
function Write-ColorLog {
    param(
        [string]$Message,
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = $script:Colors[$Level]
    
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
    Write-Host "[$Level] " -NoNewline -ForegroundColor $color
    Write-Host $Message
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
function Test-DockerComposeAvailable {
    try {
        $null = docker-compose version 2>$null
        return $true
    }
    catch {
        try {
            $null = docker compose version 2>$null
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
    if (Get-Command "docker-compose" -ErrorAction SilentlyContinue) {
        return "docker-compose"
    }
    elseif (Get-Command "docker" -ErrorAction SilentlyContinue) {
        try {
            $null = docker compose version 2>$null
            return "docker compose"
        }
        catch {
            return $null
        }
    }
    return $null
}

<#
.SYNOPSIS
    创建必要的目录
#>
function Initialize-Directories {
    Write-ColorLog "创建必要的目录..." "Info"
    
    $directories = @(
        $script:DataDir,
        (Join-Path $script:DataDir "elasticsearch"),
        (Join-Path $script:DataDir "logstash"),
        (Join-Path $script:DataDir "kibana"),
        $script:LogsDir,
        $script:BackupsDir
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-ColorLog "创建目录: $dir" "Success"
        }
    }
    
    # 设置Elasticsearch数据目录权限
    $esDataDir = Join-Path $script:DataDir "elasticsearch"
    if (Test-Path $esDataDir) {
        try {
            # 在Windows上设置目录权限
            $acl = Get-Acl $esDataDir
            $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
            $acl.SetAccessRule($accessRule)
            Set-Acl -Path $esDataDir -AclObject $acl
            Write-ColorLog "设置Elasticsearch数据目录权限" "Success"
        }
        catch {
            Write-ColorLog "设置目录权限失败: $($_.Exception.Message)" "Warning"
        }
    }
}

<#
.SYNOPSIS
    检查配置文件
#>
function Test-ConfigFiles {
    Write-ColorLog "检查配置文件..." "Info"
    
    $configFiles = @(
        (Join-Path $script:ProjectRoot "configs\elasticsearch\elasticsearch.yml"),
        (Join-Path $script:ProjectRoot "configs\logstash\logstash.yml"),
        (Join-Path $script:ProjectRoot "configs\kibana\kibana.yml")
    )
    
    $missing = @()
    foreach ($file in $configFiles) {
        if (-not (Test-Path $file)) {
            $missing += $file
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-ColorLog "缺少配置文件:" "Error"
        foreach ($file in $missing) {
            Write-ColorLog "  - $file" "Error"
        }
        return $false
    }
    
    Write-ColorLog "所有配置文件检查通过" "Success"
    return $true
}

<#
.SYNOPSIS
    等待服务健康
#>
function Wait-ServiceHealthy {
    param(
        [string]$ServiceName,
        [int]$TimeoutSeconds = 300
    )
    
    Write-ColorLog "等待 $ServiceName 服务健康..." "Info"
    
    $dockerCompose = Get-DockerComposeCommand
    $startTime = Get-Date
    
    while ((Get-Date) - $startTime -lt [TimeSpan]::FromSeconds($TimeoutSeconds)) {
        try {
            $health = & $dockerCompose.Split() ps --format json | ConvertFrom-Json | Where-Object { $_.Service -eq $ServiceName }
            
            if ($health -and $health.State -eq "running") {
                # 检查健康状态
                $containerId = $health.Name
                $healthStatus = docker inspect --format='{{.State.Health.Status}}' $containerId 2>$null
                
                if ($healthStatus -eq "healthy" -or $healthStatus -eq "") {
                    Write-ColorLog "$ServiceName 服务已健康" "Success"
                    return $true
                }
            }
        }
        catch {
            # 忽略错误，继续等待
        }
        
        Start-Sleep -Seconds 5
    }
    
    Write-ColorLog "$ServiceName 服务健康检查超时" "Warning"
    return $false
}

<#
.SYNOPSIS
    获取服务状态
#>
function Get-ServiceStatus {
    param([string]$ServiceName = "all")
    
    $dockerCompose = Get-DockerComposeCommand
    
    try {
        if ($ServiceName -eq "all") {
            $services = $script:AllServices
        } else {
            $services = @($ServiceName)
        }
        
        Write-ColorLog "ELK服务状态:" "Info"
        Write-Host ""
        
        foreach ($service in $services) {
            try {
                $status = & $dockerCompose.Split() ps $service --format "table" 2>$null
                if ($status) {
                    Write-Host $status
                } else {
                    Write-ColorLog "$service : 未运行" "Warning"
                }
            }
            catch {
                Write-ColorLog "$service : 状态未知" "Error"
            }
        }
        
        Write-Host ""
        
        # 显示网络信息
        Write-ColorLog "网络信息:" "Info"
        try {
            docker network ls --filter name=elk
        }
        catch {
            Write-ColorLog "获取网络信息失败" "Warning"
        }
        
        # 显示卷信息
        Write-ColorLog "卷信息:" "Info"
        try {
            docker volume ls --filter name=elk
        }
        catch {
            Write-ColorLog "获取卷信息失败" "Warning"
        }
    }
    catch {
        Write-ColorLog "获取服务状态失败: $($_.Exception.Message)" "Error"
        return $false
    }
    
    return $true
}

# ===========================================
# 主要功能函数
# ===========================================

<#
.SYNOPSIS
    启动ELK服务
#>
function Start-ELKServices {
    param([string]$ServiceName = "all")
    
    Write-ColorLog "启动ELK服务..." "Info"
    
    $dockerCompose = Get-DockerComposeCommand
    
    try {
        if ($ServiceName -eq "all") {
            # 按顺序启动核心服务
            foreach ($service in $script:CoreServices) {
                Write-ColorLog "启动 $service..." "Info"
                & $dockerCompose.Split() up -d $service
                
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorLog "$service 启动成功" "Success"
                    
                    # 等待服务健康
                    if ($service -eq "elasticsearch") {
                        Wait-ServiceHealthy $service 180
                    } elseif ($service -eq "logstash") {
                        Wait-ServiceHealthy $service 120
                    } else {
                        Wait-ServiceHealthy $service 60
                    }
                } else {
                    Write-ColorLog "$service 启动失败" "Error"
                    return $false
                }
            }
            
            # 启动Beat服务
            Write-ColorLog "启动Beat服务..." "Info"
            & $dockerCompose.Split() up -d @($script:BeatServices)
            
            # 启动其他服务
            Write-ColorLog "启动其他服务..." "Info"
            & $dockerCompose.Split() up -d apm-server elasticsearch-exporter
        } else {
            Write-ColorLog "启动 $ServiceName..." "Info"
            & $dockerCompose.Split() up -d $ServiceName
            
            if ($LASTEXITCODE -eq 0) {
                Write-ColorLog "$ServiceName 启动成功" "Success"
                Wait-ServiceHealthy $ServiceName
            } else {
                Write-ColorLog "$ServiceName 启动失败" "Error"
                return $false
            }
        }
        
        Write-ColorLog "ELK服务启动完成" "Success"
        
        # 显示访问信息
        Write-Host ""
        Write-ColorLog "服务访问地址:" "Info"
        Write-Host "  Elasticsearch: http://localhost:9200" -ForegroundColor Green
        Write-Host "  Kibana: http://localhost:5601" -ForegroundColor Green
        Write-Host "  Logstash API: http://localhost:9600" -ForegroundColor Green
        Write-Host "  APM Server: http://localhost:8200" -ForegroundColor Green
        Write-Host ""
        
        return $true
    }
    catch {
        Write-ColorLog "启动服务失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

<#
.SYNOPSIS
    停止ELK服务
#>
function Stop-ELKServices {
    param([string]$ServiceName = "all")
    
    Write-ColorLog "停止ELK服务..." "Info"
    
    $dockerCompose = Get-DockerComposeCommand
    
    try {
        if ($ServiceName -eq "all") {
            & $dockerCompose.Split() down
        } else {
            & $dockerCompose.Split() stop $ServiceName
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorLog "ELK服务停止成功" "Success"
            return $true
        } else {
            Write-ColorLog "停止服务失败" "Error"
            return $false
        }
    }
    catch {
        Write-ColorLog "停止服务失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

<#
.SYNOPSIS
    重启ELK服务
#>
function Restart-ELKServices {
    param([string]$ServiceName = "all")
    
    Write-ColorLog "重启ELK服务..." "Info"
    
    if (Stop-ELKServices $ServiceName) {
        Start-Sleep -Seconds 5
        return Start-ELKServices $ServiceName
    }
    
    return $false
}

<#
.SYNOPSIS
    查看服务日志
#>
function Show-ServiceLogs {
    param(
        [string]$ServiceName = "all",
        [bool]$FollowLogs = $false,
        [int]$LogLines = 100
    )
    
    $dockerCompose = Get-DockerComposeCommand
    
    try {
        $args = @("logs")
        
        if ($FollowLogs) {
            $args += "-f"
        }
        
        $args += "--tail=$LogLines"
        
        if ($ServiceName -ne "all") {
            $args += $ServiceName
        }
        
        Write-ColorLog "显示服务日志 (按Ctrl+C退出)..." "Info"
        & $dockerCompose.Split() @args
    }
    catch {
        Write-ColorLog "查看日志失败: $($_.Exception.Message)" "Error"
        return $false
    }
    
    return $true
}

<#
.SYNOPSIS
    清理ELK资源
#>
function Clear-ELKResources {
    Write-ColorLog "清理ELK资源..." "Info"
    
    $dockerCompose = Get-DockerComposeCommand
    
    try {
        # 停止并删除容器
        & $dockerCompose.Split() down -v --remove-orphans
        
        if ($Force) {
            # 删除镜像
            Write-ColorLog "删除ELK镜像..." "Info"
            $images = docker images --filter="reference=*elastic*" --filter="reference=*logstash*" --filter="reference=*kibana*" -q
            if ($images) {
                docker rmi $images -f
            }
            
            # 清理数据目录
            if (Test-Path $script:DataDir) {
                Write-ColorLog "清理数据目录..." "Warning"
                Remove-Item -Path $script:DataDir -Recurse -Force
            }
        }
        
        Write-ColorLog "ELK资源清理完成" "Success"
        return $true
    }
    catch {
        Write-ColorLog "清理资源失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

<#
.SYNOPSIS
    健康检查
#>
function Test-ELKHealth {
    Write-ColorLog "执行ELK健康检查..." "Info"
    
    $healthChecks = @{
        "Elasticsearch" = "http://localhost:9200/_cluster/health"
        "Kibana" = "http://localhost:5601/api/status"
        "Logstash" = "http://localhost:9600/_node/stats"
        "APM Server" = "http://localhost:8200/"
    }
    
    $allHealthy = $true
    
    foreach ($service in $healthChecks.Keys) {
        $url = $healthChecks[$service]
        
        try {
            $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10
            Write-ColorLog "$service : 健康" "Success"
        }
        catch {
            Write-ColorLog "$service : 不健康 - $($_.Exception.Message)" "Error"
            $allHealthy = $false
        }
    }
    
    if ($allHealthy) {
        Write-ColorLog "所有服务健康检查通过" "Success"
    } else {
        Write-ColorLog "部分服务健康检查失败" "Warning"
    }
    
    return $allHealthy
}

<#
.SYNOPSIS
    设置ELK环境
#>
function Initialize-ELKSetup {
    Write-ColorLog "初始化ELK环境..." "Info"
    
    try {
        # 等待Elasticsearch启动
        Write-ColorLog "等待Elasticsearch启动..." "Info"
        $timeout = 300
        $elapsed = 0
        
        while ($elapsed -lt $timeout) {
            try {
                $response = Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health" -Method Get -TimeoutSec 5
                if ($response.status -in @("green", "yellow")) {
                    Write-ColorLog "Elasticsearch已启动" "Success"
                    break
                }
            }
            catch {
                Start-Sleep -Seconds 5
                $elapsed += 5
            }
        }
        
        # 设置索引模板
        Write-ColorLog "设置索引模板..." "Info"
        
        # 创建日志索引模板
        $logTemplate = @{
            "index_patterns" = @("logs-*")
            "template" = @{
                "settings" = @{
                    "number_of_shards" = 1
                    "number_of_replicas" = 0
                    "index.refresh_interval" = "5s"
                }
                "mappings" = @{
                    "properties" = @{
                        "@timestamp" = @{ "type" = "date" }
                        "level" = @{ "type" = "keyword" }
                        "message" = @{ "type" = "text" }
                        "service" = @{ "type" = "keyword" }
                        "host" = @{ "type" = "keyword" }
                    }
                }
            }
        }
        
        $templateJson = $logTemplate | ConvertTo-Json -Depth 10
        Invoke-RestMethod -Uri "http://localhost:9200/_index_template/logs-template" -Method Put -Body $templateJson -ContentType "application/json"
        
        Write-ColorLog "ELK环境初始化完成" "Success"
        return $true
    }
    catch {
        Write-ColorLog "初始化ELK环境失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

<#
.SYNOPSIS
    备份Elasticsearch数据
#>
function Backup-ElasticsearchData {
    param([string]$BackupName)
    
    if (-not $BackupName) {
        $BackupName = "backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    }
    
    Write-ColorLog "备份Elasticsearch数据: $BackupName" "Info"
    
    try {
        # 创建备份目录
        $backupDir = Join-Path $BackupsDir $BackupName
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        
        # 创建快照仓库
        $repoConfig = @{
            "type" = "fs"
            "settings" = @{
                "location" = "/usr/share/elasticsearch/backup/$BackupName"
            }
        }
        
        $repoJson = $repoConfig | ConvertTo-Json -Depth 5
        Invoke-RestMethod -Uri "http://localhost:9200/_snapshot/backup_repo" -Method Put -Body $repoJson -ContentType "application/json"
        
        # 创建快照
        $snapshotConfig = @{
            "indices" = "*"
            "ignore_unavailable" = $true
            "include_global_state" = $false
        }
        
        $snapshotJson = $snapshotConfig | ConvertTo-Json -Depth 5
        Invoke-RestMethod -Uri "http://localhost:9200/_snapshot/backup_repo/$BackupName" -Method Put -Body $snapshotJson -ContentType "application/json"
        
        Write-ColorLog "数据备份完成: $BackupName" "Success"
        return $true
    }
    catch {
        Write-ColorLog "备份失败: $($_.Exception.Message)" "Error"
        return $false
    }
}

# ===========================================
# 主程序
# ===========================================

function Main {
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host "    AIOps ELK Stack 管理脚本" -ForegroundColor Cyan
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 检查Docker环境
    if (-not (Test-DockerRunning)) {
        Write-ColorLog "Docker未运行，请先启动Docker" "Error"
        exit 1
    }
    
    if (-not (Test-DockerComposeAvailable)) {
        Write-ColorLog "Docker Compose不可用" "Error"
        exit 1
    }
    
    # 切换到脚本目录
    Set-Location $script:ScriptPath
    
    # 检查Compose文件
    if (-not (Test-Path $script:ComposeFile)) {
        Write-ColorLog "Docker Compose文件不存在: $script:ComposeFile" "Error"
        exit 1
    }
    
    # 执行操作
    switch ($Action.ToLower()) {
        "start" {
            Initialize-Directories
            if (Test-ConfigFiles) {
                $success = Start-ELKServices $Service
                if ($success -and $Service -eq "all") {
                    Start-Sleep -Seconds 10
                    Initialize-ELKSetup
                }
            }
        }
        
        "stop" {
            Stop-ELKServices $Service
        }
        
        "restart" {
            Restart-ELKServices $Service
        }
        
        "status" {
            Get-ServiceStatus $Service
        }
        
        "logs" {
            Show-ServiceLogs $Service $Follow $Lines
        }
        
        "cleanup" {
            Clear-ELKResources
        }
        
        "health" {
            Test-ELKHealth
        }
        
        "setup" {
            Initialize-Directories
            Initialize-ELKSetup
        }
        
        "backup" {
            Backup-ElasticsearchData
        }
        
        "restore" {
            Write-ColorLog "恢复功能待实现" "Warning"
        }
        
        default {
            Write-ColorLog "未知操作: $Action" "Error"
            exit 1
        }
    }
}

# 执行主程序
if ($MyInvocation.InvocationName -ne '.') {
    Main
}