#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK堆栈备份和恢复脚本
    
.DESCRIPTION
    该脚本用于ELK堆栈的数据备份和恢复操作，包括：
    - Elasticsearch索引备份和恢复
    - Kibana配置备份和恢复
    - Logstash配置备份
    - 完整系统备份和恢复
    
.PARAMETER Action
    操作类型：backup, restore, list, cleanup
    
.PARAMETER Type
    备份类型：full, elasticsearch, kibana, logstash, configs
    
.PARAMETER BackupName
    备份名称
    
.PARAMETER RestorePoint
    恢复点名称
    
.PARAMETER Repository
    备份仓库名称
    
.EXAMPLE
    .\backup-restore.ps1 -Action backup -Type full
    创建完整系统备份
    
.EXAMPLE
    .\backup-restore.ps1 -Action restore -Type elasticsearch -RestorePoint "backup-20240101"
    恢复Elasticsearch数据
    
.EXAMPLE
    .\backup-restore.ps1 -Action list
    列出所有可用的备份
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("backup", "restore", "list", "cleanup", "verify")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("full", "elasticsearch", "kibana", "logstash", "configs")]
    [string]$Type = "full",
    
    [Parameter(Mandatory = $false)]
    [string]$BackupName,
    
    [Parameter(Mandatory = $false)]
    [string]$RestorePoint,
    
    [Parameter(Mandatory = $false)]
    [string]$Repository = "aiops-backup",
    
    [Parameter(Mandatory = $false)]
    [string]$BackupPath = "./data/backups",
    
    [Parameter(Mandatory = $false)]
    [int]$RetentionDays = 30,
    
    [Parameter(Mandatory = $false)]
    [switch]$Compress,
    
    [Parameter(Mandatory = $false)]
    [switch]$Verify,
    
    [Parameter(Mandatory = $false)]
    [switch]$Force
)

# 全局变量
$script:LogPath = "logs/backup-restore.log"
$script:ConfigPath = "../configs"
$script:ElasticsearchUrl = "http://localhost:9200"
$script:KibanaUrl = "http://localhost:5601"
$script:BackupMetadata = @{}

# 颜色定义
$Colors = @{
    Green  = "Green"
    Red    = "Red"
    Yellow = "Yellow"
    Blue   = "Blue"
    Cyan   = "Cyan"
    White  = "White"
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
        [int]$TimeoutSeconds = 60
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            TimeoutSec = $TimeoutSeconds
        }
        
        if ($Body) {
            $params.Body = $Body | ConvertTo-Json -Depth 10
            $params.ContentType = "application/json"
        }
        
        $response = Invoke-RestMethod @params -ErrorAction Stop
        return @{
            Success = $true
            Data = $response
        }
    }
    catch {
        Write-Log "API请求失败: $Url - $($_.Exception.Message)" "ERROR"
        return @{
            Success = $false
            Error = $_.Exception.Message
        }
    }
}

<#
.SYNOPSIS
    确保备份目录存在
#>
function Initialize-BackupDirectory {
    if (-not (Test-Path $BackupPath)) {
        Write-Log "创建备份目录: $BackupPath" "INFO"
        New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
    }
    
    # 创建子目录
    $subDirs = @("elasticsearch", "kibana", "logstash", "configs", "metadata")
    foreach ($dir in $subDirs) {
        $fullPath = Join-Path $BackupPath $dir
        if (-not (Test-Path $fullPath)) {
            New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
        }
    }
}

<#
.SYNOPSIS
    生成备份名称
#>
function New-BackupName {
    param(
        [string]$Prefix = "backup"
    )
    
    if ($BackupName) {
        return $BackupName
    }
    
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    return "${Prefix}-${timestamp}"
}

<#
.SYNOPSIS
    创建Elasticsearch快照仓库
#>
function New-ElasticsearchRepository {
    Write-Log "创建Elasticsearch快照仓库: $Repository" "INFO"
    
    $repoPath = Join-Path $BackupPath "elasticsearch"
    $repoConfig = @{
        type = "fs"
        settings = @{
            location = $repoPath
            compress = $Compress.IsPresent
        }
    }
    
    $response = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_snapshot/$Repository" -Method "PUT" -Body $repoConfig
    
    if ($response.Success) {
        Write-Log "快照仓库创建成功" "INFO"
        return $true
    }
    else {
        Write-Log "快照仓库创建失败: $($response.Error)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    备份Elasticsearch数据
#>
function Backup-ElasticsearchData {
    param(
        [string]$SnapshotName
    )
    
    Write-Log "开始备份Elasticsearch数据: $SnapshotName" "INFO"
    
    # 确保仓库存在
    if (-not (New-ElasticsearchRepository)) {
        return $false
    }
    
    # 创建快照
    $snapshotConfig = @{
        indices = "*"
        ignore_unavailable = $true
        include_global_state = $true
        metadata = @{
            taken_by = "aiops-backup-script"
            taken_because = "Scheduled backup"
            timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        }
    }
    
    $response = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_snapshot/$Repository/$SnapshotName" -Method "PUT" -Body $snapshotConfig
    
    if ($response.Success) {
        Write-Log "Elasticsearch快照创建成功" "INFO"
        
        # 等待快照完成
        do {
            Start-Sleep -Seconds 5
            $statusResponse = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_snapshot/$Repository/$SnapshotName"
            if ($statusResponse.Success) {
                $status = $statusResponse.Data.snapshots[0].state
                Write-Log "快照状态: $status" "INFO"
            }
        } while ($status -eq "IN_PROGRESS")
        
        if ($status -eq "SUCCESS") {
            Write-Log "Elasticsearch备份完成" "INFO"
            return $true
        }
        else {
            Write-Log "Elasticsearch备份失败: $status" "ERROR"
            return $false
        }
    }
    else {
        Write-Log "Elasticsearch快照创建失败: $($response.Error)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    备份Kibana配置
#>
function Backup-KibanaConfig {
    param(
        [string]$BackupName
    )
    
    Write-Log "开始备份Kibana配置: $BackupName" "INFO"
    
    $kibanaBackupPath = Join-Path $BackupPath "kibana/$BackupName"
    if (-not (Test-Path $kibanaBackupPath)) {
        New-Item -ItemType Directory -Path $kibanaBackupPath -Force | Out-Null
    }
    
    try {
        # 导出Kibana对象
        $exportTypes = @(
            "dashboard", "visualization", "search", "index-pattern",
            "config", "timelion-sheet", "canvas-workpad", "lens",
            "map", "ml-job", "data-view"
        )
        
        foreach ($type in $exportTypes) {
            Write-Log "导出Kibana对象类型: $type" "INFO"
            
            $exportUrl = "$script:KibanaUrl/api/saved_objects/_export"
            $exportBody = @{
                type = $type
                includeReferencesDeep = $true
            }
            
            $response = Invoke-ApiRequest -Url $exportUrl -Method "POST" -Body $exportBody
            
            if ($response.Success) {
                $exportFile = Join-Path $kibanaBackupPath "$type.ndjson"
                $response.Data | Out-File -FilePath $exportFile -Encoding UTF8
                Write-Log "$type 导出成功" "INFO"
            }
            else {
                Write-Log "$type 导出失败: $($response.Error)" "WARN"
            }
        }
        
        # 备份Kibana配置文件
        $kibanaConfigSource = Join-Path $script:ConfigPath "kibana"
        $kibanaConfigDest = Join-Path $kibanaBackupPath "config"
        
        if (Test-Path $kibanaConfigSource) {
            Copy-Item -Path $kibanaConfigSource -Destination $kibanaConfigDest -Recurse -Force
            Write-Log "Kibana配置文件备份完成" "INFO"
        }
        
        Write-Log "Kibana配置备份完成" "INFO"
        return $true
    }
    catch {
        Write-Log "Kibana配置备份失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    备份Logstash配置
#>
function Backup-LogstashConfig {
    param(
        [string]$BackupName
    )
    
    Write-Log "开始备份Logstash配置: $BackupName" "INFO"
    
    $logstashBackupPath = Join-Path $BackupPath "logstash/$BackupName"
    if (-not (Test-Path $logstashBackupPath)) {
        New-Item -ItemType Directory -Path $logstashBackupPath -Force | Out-Null
    }
    
    try {
        # 备份Logstash配置文件
        $logstashConfigSource = Join-Path $script:ConfigPath "logstash"
        
        if (Test-Path $logstashConfigSource) {
            Copy-Item -Path $logstashConfigSource -Destination $logstashBackupPath -Recurse -Force
            Write-Log "Logstash配置备份完成" "INFO"
            return $true
        }
        else {
            Write-Log "Logstash配置目录不存在: $logstashConfigSource" "WARN"
            return $false
        }
    }
    catch {
        Write-Log "Logstash配置备份失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    备份所有配置文件
#>
function Backup-AllConfigs {
    param(
        [string]$BackupName
    )
    
    Write-Log "开始备份所有配置文件: $BackupName" "INFO"
    
    $configBackupPath = Join-Path $BackupPath "configs/$BackupName"
    if (-not (Test-Path $configBackupPath)) {
        New-Item -ItemType Directory -Path $configBackupPath -Force | Out-Null
    }
    
    try {
        # 备份所有配置文件
        if (Test-Path $script:ConfigPath) {
            Copy-Item -Path $script:ConfigPath -Destination $configBackupPath -Recurse -Force
            Write-Log "配置文件备份完成" "INFO"
        }
        
        # 备份Docker Compose文件
        $composeFiles = @("docker-compose.yml", ".env", "start-elk.ps1")
        foreach ($file in $composeFiles) {
            if (Test-Path $file) {
                Copy-Item -Path $file -Destination $configBackupPath -Force
            }
        }
        
        Write-Log "所有配置文件备份完成" "INFO"
        return $true
    }
    catch {
        Write-Log "配置文件备份失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    创建备份元数据
#>
function New-BackupMetadata {
    param(
        [string]$BackupName,
        [string]$Type,
        [hashtable]$Details = @{}
    )
    
    $metadata = @{
        name = $BackupName
        type = $Type
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        version = "1.0.0"
        details = $Details
        size = 0
        files = @()
    }
    
    # 计算备份大小
    $backupDir = Join-Path $BackupPath $Type
    if (Test-Path $backupDir) {
        $size = (Get-ChildItem -Path $backupDir -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $metadata.size = $size
        $metadata.files = (Get-ChildItem -Path $backupDir -Recurse -File).FullName
    }
    
    # 保存元数据
    $metadataPath = Join-Path $BackupPath "metadata/$BackupName.json"
    $metadata | ConvertTo-Json -Depth 10 | Out-File -FilePath $metadataPath -Encoding UTF8
    
    Write-Log "备份元数据已保存: $metadataPath" "INFO"
}

<#
.SYNOPSIS
    执行备份操作
#>
function Invoke-Backup {
    Write-Log "开始执行备份操作" "INFO"
    
    Initialize-BackupDirectory
    
    $backupName = New-BackupName
    $success = $true
    $details = @{}
    
    switch ($Type) {
        "full" {
            Write-Log "执行完整系统备份" "INFO"
            $details.elasticsearch = Backup-ElasticsearchData $backupName
            $details.kibana = Backup-KibanaConfig $backupName
            $details.logstash = Backup-LogstashConfig $backupName
            $details.configs = Backup-AllConfigs $backupName
            $success = $details.elasticsearch -and $details.kibana -and $details.logstash -and $details.configs
        }
        "elasticsearch" {
            $success = Backup-ElasticsearchData $backupName
            $details.elasticsearch = $success
        }
        "kibana" {
            $success = Backup-KibanaConfig $backupName
            $details.kibana = $success
        }
        "logstash" {
            $success = Backup-LogstashConfig $backupName
            $details.logstash = $success
        }
        "configs" {
            $success = Backup-AllConfigs $backupName
            $details.configs = $success
        }
    }
    
    # 创建备份元数据
    New-BackupMetadata -BackupName $backupName -Type $Type -Details $details
    
    if ($success) {
        Write-Log "备份操作完成: $backupName" "INFO"
        
        # 压缩备份（如果启用）
        if ($Compress) {
            Compress-Backup $backupName
        }
        
        # 验证备份（如果启用）
        if ($Verify) {
            Test-BackupIntegrity $backupName
        }
    }
    else {
        Write-Log "备份操作失败" "ERROR"
        exit 1
    }
}

<#
.SYNOPSIS
    恢复Elasticsearch数据
#>
function Restore-ElasticsearchData {
    param(
        [string]$SnapshotName
    )
    
    Write-Log "开始恢复Elasticsearch数据: $SnapshotName" "INFO"
    
    # 检查快照是否存在
    $response = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_snapshot/$Repository/$SnapshotName"
    
    if (-not $response.Success) {
        Write-Log "快照不存在: $SnapshotName" "ERROR"
        return $false
    }
    
    # 关闭所有索引（如果强制恢复）
    if ($Force) {
        Write-Log "关闭所有索引" "INFO"
        Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_all/_close" -Method "POST" | Out-Null
    }
    
    # 执行恢复
    $restoreConfig = @{
        ignore_unavailable = $true
        include_global_state = $true
    }
    
    $restoreResponse = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_snapshot/$Repository/$SnapshotName/_restore" -Method "POST" -Body $restoreConfig
    
    if ($restoreResponse.Success) {
        Write-Log "Elasticsearch数据恢复完成" "INFO"
        return $true
    }
    else {
        Write-Log "Elasticsearch数据恢复失败: $($restoreResponse.Error)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    恢复Kibana配置
#>
function Restore-KibanaConfig {
    param(
        [string]$BackupName
    )
    
    Write-Log "开始恢复Kibana配置: $BackupName" "INFO"
    
    $kibanaBackupPath = Join-Path $BackupPath "kibana/$BackupName"
    
    if (-not (Test-Path $kibanaBackupPath)) {
        Write-Log "Kibana备份不存在: $kibanaBackupPath" "ERROR"
        return $false
    }
    
    try {
        # 恢复Kibana对象
        $exportFiles = Get-ChildItem -Path $kibanaBackupPath -Filter "*.ndjson"
        
        foreach ($file in $exportFiles) {
            Write-Log "导入Kibana对象: $($file.BaseName)" "INFO"
            
            $importUrl = "$script:KibanaUrl/api/saved_objects/_import"
            $fileContent = Get-Content -Path $file.FullName -Raw
            
            # 这里需要使用multipart/form-data格式，简化处理
            Write-Log "跳过Kibana对象导入（需要手动处理）" "WARN"
        }
        
        # 恢复配置文件
        $configSource = Join-Path $kibanaBackupPath "config"
        $configDest = Join-Path $script:ConfigPath "kibana"
        
        if (Test-Path $configSource) {
            if ($Force -or -not (Test-Path $configDest)) {
                Copy-Item -Path $configSource -Destination $configDest -Recurse -Force
                Write-Log "Kibana配置文件恢复完成" "INFO"
            }
            else {
                Write-Log "Kibana配置文件已存在，使用 -Force 参数覆盖" "WARN"
            }
        }
        
        return $true
    }
    catch {
        Write-Log "Kibana配置恢复失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    列出所有备份
#>
function Get-BackupList {
    Write-Log "列出所有可用备份" "INFO"
    
    if (-not (Test-Path $BackupPath)) {
        Write-Log "备份目录不存在: $BackupPath" "WARN"
        return
    }
    
    $metadataPath = Join-Path $BackupPath "metadata"
    if (-not (Test-Path $metadataPath)) {
        Write-Log "没有找到备份元数据" "WARN"
        return
    }
    
    $metadataFiles = Get-ChildItem -Path $metadataPath -Filter "*.json"
    
    if ($metadataFiles.Count -eq 0) {
        Write-Log "没有找到任何备份" "INFO"
        return
    }
    
    Write-Host "`n=== 可用备份列表 ===" -ForegroundColor $Colors.Blue
    Write-Host ""
    
    $backups = @()
    foreach ($file in $metadataFiles) {
        try {
            $metadata = Get-Content -Path $file.FullName -Raw | ConvertFrom-Json
            $backups += [PSCustomObject]@{
                "备份名称" = $metadata.name
                "类型" = $metadata.type
                "创建时间" = $metadata.timestamp
                "大小" = "{0:N2} MB" -f ($metadata.size / 1MB)
                "文件数" = $metadata.files.Count
            }
        }
        catch {
            Write-Log "读取备份元数据失败: $($file.Name)" "WARN"
        }
    }
    
    $backups | Sort-Object "创建时间" -Descending | Format-Table -AutoSize
}

<#
.SYNOPSIS
    清理过期备份
#>
function Remove-ExpiredBackups {
    Write-Log "清理过期备份（保留天数: $RetentionDays）" "INFO"
    
    $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
    $metadataPath = Join-Path $BackupPath "metadata"
    
    if (-not (Test-Path $metadataPath)) {
        Write-Log "备份元数据目录不存在" "WARN"
        return
    }
    
    $metadataFiles = Get-ChildItem -Path $metadataPath -Filter "*.json"
    $removedCount = 0
    
    foreach ($file in $metadataFiles) {
        try {
            $metadata = Get-Content -Path $file.FullName -Raw | ConvertFrom-Json
            $backupDate = [DateTime]::Parse($metadata.timestamp)
            
            if ($backupDate -lt $cutoffDate) {
                Write-Log "删除过期备份: $($metadata.name)" "INFO"
                
                # 删除备份文件
                $backupDir = Join-Path $BackupPath $metadata.type
                $backupSubDir = Join-Path $backupDir $metadata.name
                if (Test-Path $backupSubDir) {
                    Remove-Item -Path $backupSubDir -Recurse -Force
                }
                
                # 删除元数据文件
                Remove-Item -Path $file.FullName -Force
                $removedCount++
            }
        }
        catch {
            Write-Log "处理备份元数据失败: $($file.Name) - $($_.Exception.Message)" "WARN"
        }
    }
    
    Write-Log "清理完成，删除了 $removedCount 个过期备份" "INFO"
}

<#
.SYNOPSIS
    验证备份完整性
#>
function Test-BackupIntegrity {
    param(
        [string]$BackupName
    )
    
    Write-Log "验证备份完整性: $BackupName" "INFO"
    
    $metadataFile = Join-Path $BackupPath "metadata/$BackupName.json"
    
    if (-not (Test-Path $metadataFile)) {
        Write-Log "备份元数据不存在: $BackupName" "ERROR"
        return $false
    }
    
    try {
        $metadata = Get-Content -Path $metadataFile -Raw | ConvertFrom-Json
        $allFilesExist = $true
        
        foreach ($filePath in $metadata.files) {
            if (-not (Test-Path $filePath)) {
                Write-Log "备份文件缺失: $filePath" "ERROR"
                $allFilesExist = $false
            }
        }
        
        if ($allFilesExist) {
            Write-Log "备份完整性验证通过" "INFO"
            return $true
        }
        else {
            Write-Log "备份完整性验证失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "备份完整性验证失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    主函数
#>
function Main {
    try {
        Write-Log "启动ELK备份恢复脚本" "INFO"
        
        switch ($Action) {
            "backup" {
                Invoke-Backup
            }
            "restore" {
                if (-not $RestorePoint) {
                    Write-Log "恢复操作需要指定恢复点" "ERROR"
                    exit 1
                }
                
                switch ($Type) {
                    "elasticsearch" {
                        Restore-ElasticsearchData $RestorePoint
                    }
                    "kibana" {
                        Restore-KibanaConfig $RestorePoint
                    }
                    default {
                        Write-Log "暂不支持的恢复类型: $Type" "ERROR"
                        exit 1
                    }
                }
            }
            "list" {
                Get-BackupList
            }
            "cleanup" {
                Remove-ExpiredBackups
            }
            "verify" {
                if (-not $BackupName) {
                    Write-Log "验证操作需要指定备份名称" "ERROR"
                    exit 1
                }
                Test-BackupIntegrity $BackupName
            }
        }
        
        Write-Log "操作完成" "INFO"
    }
    catch {
        Write-Log "操作过程中发生错误: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

# 脚本入口点
if ($MyInvocation.InvocationName -ne '.') {
    Main
}