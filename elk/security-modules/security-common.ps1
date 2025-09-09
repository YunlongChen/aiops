#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK安全配置通用模块
    
.DESCRIPTION
    包含ELK安全配置的通用函数、变量定义和工具函数
#>

# 全局变量
$script:LogPath = "logs/security-setup.log"
$script:ElasticsearchUrl = "http://localhost:9200"
$script:KibanaUrl = "http://localhost:5601"
$script:SecurityConfig = @{}

# 颜色定义
$Colors = @{
    Green   = "Green"
    Red     = "Red"
    Yellow  = "Yellow"
    Blue    = "Blue"
    Cyan    = "Cyan"
    White   = "White"
    Magenta = "Magenta"
}

# 默认用户配置
$script:DefaultUsers = @{
    elastic = @{
        password = "changeme"
        roles = @("superuser")
        full_name = "Elastic Superuser"
        email = "elastic@example.com"
    }
    kibana_system = @{
        password = "changeme"
        roles = @("kibana_system")
        full_name = "Kibana System User"
        email = "kibana@example.com"
    }
    logstash_system = @{
        password = "changeme"
        roles = @("logstash_system")
        full_name = "Logstash System User"
        email = "logstash@example.com"
    }
    beats_system = @{
        password = "changeme"
        roles = @("beats_system")
        full_name = "Beats System User"
        email = "beats@example.com"
    }
    aiops_admin = @{
        password = "AIOps@2024"
        roles = @("superuser", "aiops_admin")
        full_name = "AIOps Administrator"
        email = "admin@aiops.com"
    }
    aiops_user = @{
        password = "AIOps@User2024"
        roles = @("aiops_user")
        full_name = "AIOps User"
        email = "user@aiops.com"
    }
}

# 默认角色配置
$script:DefaultRoles = @{
    aiops_admin = @{
        cluster = @("all")
        indices = @(
            @{
                names = @("*")
                privileges = @("all")
            }
        )
        applications = @(
            @{
                application = "kibana-.kibana"
                privileges = @("all")
                resources = @("*")
            }
        )
    }
    aiops_user = @{
        cluster = @("monitor")
        indices = @(
            @{
                names = @("aiops-*", "logs-*", "metrics-*")
                privileges = @("read", "view_index_metadata")
            }
        )
        applications = @(
            @{
                application = "kibana-.kibana"
                privileges = @("read")
                resources = @("*")
            }
        )
    }
    aiops_readonly = @{
        cluster = @("monitor")
        indices = @(
            @{
                names = @("aiops-*")
                privileges = @("read")
            }
        )
    }
}

<#
.SYNOPSIS
    写入日志信息
#>
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"
    
    # 确保日志目录存在
    $logDir = Split-Path $script:LogPath -Parent
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    # 写入日志文件
    Add-Content -Path $script:LogPath -Value $logEntry
    
    # 根据级别显示不同颜色
    switch ($Level) {
        "ERROR" { Write-Host $logEntry -ForegroundColor $Colors.Red }
        "WARN"  { Write-Host $logEntry -ForegroundColor $Colors.Yellow }
        "INFO"  { Write-Host $logEntry -ForegroundColor $Colors.Green }
        "DEBUG" { Write-Host $logEntry -ForegroundColor $Colors.Cyan }
        "SECURITY" { Write-Host $logEntry -ForegroundColor $Colors.Magenta }
        default { Write-Host $logEntry }
    }
}

<#
.SYNOPSIS
    发送HTTP请求
#>
function Invoke-ApiRequest {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [object]$Body = $null,
        [PSCredential]$Credential = $null,
        [int]$TimeoutSeconds = 30
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            TimeoutSec = $TimeoutSeconds
        }
        
        if ($Credential) {
            $params.Credential = $Credential
        }
        
        if ($Body) {
            if ($Body -is [string]) {
                $params.Body = $Body
            }
            else {
                $params.Body = $Body | ConvertTo-Json -Depth 10
                $params.ContentType = "application/json"
            }
        }
        
        $response = Invoke-RestMethod @params -ErrorAction Stop
        return @{
            Success = $true
            Data = $response
        }
    }
    catch {
        Write-Log "API请求失败: $Url - $($_.Exception.Message)" "DEBUG"
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

<#
.SYNOPSIS
    生成随机密码
#>
function New-RandomPassword {
    param(
        [int]$Length = 16
    )
    
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    $password = ""
    
    for ($i = 0; $i -lt $Length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    
    return $password
}

<#
.SYNOPSIS
    检查服务是否运行
#>
function Test-ServiceRunning {
    param(
        [string]$ServiceUrl,
        [int]$TimeoutSeconds = 10
    )
    
    try {
        $response = Invoke-WebRequest -Uri $ServiceUrl -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

<#
.SYNOPSIS
    等待服务启动
#>
function Wait-ForService {
    param(
        [string]$ServiceUrl,
        [int]$MaxWaitSeconds = 60,
        [string]$ServiceName = "Service"
    )
    
    Write-Log "等待 $ServiceName 启动..." "INFO"
    
    $elapsed = 0
    $interval = 5
    
    while ($elapsed -lt $MaxWaitSeconds) {
        if (Test-ServiceRunning -ServiceUrl $ServiceUrl) {
            Write-Log "$ServiceName 已启动" "INFO"
            return $true
        }
        
        Start-Sleep -Seconds $interval
        $elapsed += $interval
        Write-Log "等待 $ServiceName 启动... ($elapsed/$MaxWaitSeconds 秒)" "DEBUG"
    }
    
    Write-Log "$ServiceName 启动超时" "ERROR"
    return $false
}

<#
.SYNOPSIS
    验证配置文件
#>
function Test-ConfigFile {
    param(
        [string]$FilePath,
        [string]$FileType = "YAML"
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Log "配置文件不存在: $FilePath" "ERROR"
        return $false
    }
    
    try {
        switch ($FileType.ToUpper()) {
            "YAML" {
                # 简单的YAML语法检查
                $content = Get-Content $FilePath -Raw
                if ($content -match "^\s*[^\s#].*:\s*$") {
                    return $true
                }
            }
            "JSON" {
                $content = Get-Content $FilePath -Raw
                $null = $content | ConvertFrom-Json
                return $true
            }
        }
        return $true
    }
    catch {
        Write-Log "配置文件格式错误: $FilePath - $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    备份配置文件
#>
function Backup-ConfigFile {
    param(
        [string]$FilePath,
        [string]$BackupDir = "backup"
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-Log "要备份的文件不存在: $FilePath" "WARN"
        return $false
    }
    
    try {
        if (-not (Test-Path $BackupDir)) {
            New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
        }
        
        $fileName = Split-Path $FilePath -Leaf
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $backupPath = Join-Path $BackupDir "${fileName}.${timestamp}.bak"
        
        Copy-Item $FilePath $backupPath -Force
        Write-Log "配置文件已备份: $backupPath" "INFO"
        return $true
    }
    catch {
        Write-Log "备份配置文件失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}