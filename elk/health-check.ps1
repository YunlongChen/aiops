#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK堆栈健康检查脚本
    
.DESCRIPTION
    该脚本用于检查ELK堆栈中各个组件的健康状态，包括：
    - Elasticsearch集群状态
    - Kibana服务状态
    - Logstash管道状态
    - Beats代理状态
    - APM Server状态
    
.PARAMETER Component
    指定要检查的组件，可选值：all, elasticsearch, kibana, logstash, filebeat, metricbeat, heartbeat, apm
    
.PARAMETER Detailed
    显示详细的健康检查信息
    
.PARAMETER OutputFormat
    输出格式，可选值：table, json, csv
    
.EXAMPLE
    .\health-check.ps1
    检查所有组件的健康状态
    
.EXAMPLE
    .\health-check.ps1 -Component elasticsearch -Detailed
    详细检查Elasticsearch的健康状态
    
.EXAMPLE
    .\health-check.ps1 -OutputFormat json
    以JSON格式输出健康检查结果
#>

param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("all", "elasticsearch", "kibana", "logstash", "filebeat", "metricbeat", "heartbeat", "apm")]
    [string]$Component = "all",
    
    [Parameter(Mandatory = $false)]
    [switch]$Detailed,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("table", "json", "csv")]
    [string]$OutputFormat = "table",
    
    [Parameter(Mandatory = $false)]
    [int]$Timeout = 30,
    
    [Parameter(Mandatory = $false)]
    [switch]$Continuous,
    
    [Parameter(Mandatory = $false)]
    [int]$Interval = 60
)

# 全局变量
$script:HealthResults = @()
$script:StartTime = Get-Date
$script:ConfigPath = "..\configs"
$script:LogPath = "logs\health-check.log"

# 颜色定义
$Colors = @{
    Green  = "Green"
    Red    = "Red"
    Yellow = "Yellow"
    Blue   = "Blue"
    Cyan   = "Cyan"
    White  = "White"
}

# 服务端点配置
$Endpoints = @{
    Elasticsearch = @{
        Health = "http://localhost:9200/_cluster/health"
        Stats  = "http://localhost:9200/_cluster/stats"
        Nodes  = "http://localhost:9200/_nodes/stats"
    }
    Kibana = @{
        Status = "http://localhost:5601/api/status"
        Health = "http://localhost:5601/api/status"
    }
    Logstash = @{
        Stats = "http://localhost:9600/_node/stats"
        Health = "http://localhost:9600/_node/stats/pipeline"
    }
    Filebeat = @{
        Stats = "http://localhost:5066/stats"
    }
    Metricbeat = @{
        Stats = "http://localhost:5067/stats"
    }
    Heartbeat = @{
        Stats = "http://localhost:5068/stats"
    }
    APM = @{
        Health = "http://localhost:8200/"
        Stats = "http://localhost:5069/stats"
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
        default { Write-Host $logEntry }
    }
}

<#
.SYNOPSIS
    发送HTTP请求并处理响应
#>
function Invoke-HealthRequest {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 30,
        [hashtable]$Headers = @{}
    )
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -Headers $Headers -TimeoutSec $TimeoutSeconds -ErrorAction Stop
        return @{
            Success = $true
            Data = $response
            StatusCode = 200
        }
    }
    catch {
        Write-Log "HTTP请求失败: $Url - $($_.Exception.Message)" "ERROR"
        return @{
            Success = $false
            Error = $_.Exception.Message
            StatusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode } else { 0 }
        }
    }
}

<#
.SYNOPSIS
    检查Docker容器状态
#>
function Test-DockerContainer {
    param(
        [string]$ContainerName
    )
    
    try {
        $containerInfo = docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>$null
        
        if ($containerInfo -and $containerInfo.Count -gt 1) {
            $status = $containerInfo[1].Split("\t")[1]
            return @{
                Running = $status -like "*Up*"
                Status = $status
                Info = $containerInfo[1]
            }
        }
        else {
            return @{
                Running = $false
                Status = "Not Found"
                Info = "Container not found"
            }
        }
    }
    catch {
        Write-Log "检查Docker容器失败: $ContainerName - $($_.Exception.Message)" "ERROR"
        return @{
            Running = $false
            Status = "Error"
            Info = $_.Exception.Message
        }
    }
}

<#
.SYNOPSIS
    检查Elasticsearch健康状态
#>
function Test-ElasticsearchHealth {
    Write-Log "检查Elasticsearch健康状态..." "INFO"
    
    $result = @{
        Component = "Elasticsearch"
        Status = "Unknown"
        Details = @{}
        Timestamp = Get-Date
    }
    
    # 检查Docker容器状态
    $containerStatus = Test-DockerContainer "elasticsearch"
    $result.Details.Container = $containerStatus
    
    if (-not $containerStatus.Running) {
        $result.Status = "Down"
        $result.Details.Error = "Container is not running"
        return $result
    }
    
    # 检查集群健康状态
    $healthResponse = Invoke-HealthRequest -Url $Endpoints.Elasticsearch.Health -TimeoutSeconds $Timeout
    
    if ($healthResponse.Success) {
        $health = $healthResponse.Data
        $result.Status = $health.status
        $result.Details.ClusterName = $health.cluster_name
        $result.Details.NumberOfNodes = $health.number_of_nodes
        $result.Details.ActiveShards = $health.active_shards
        $result.Details.RelocatingShards = $health.relocating_shards
        $result.Details.InitializingShards = $health.initializing_shards
        $result.Details.UnassignedShards = $health.unassigned_shards
        
        if ($Detailed) {
            # 获取集群统计信息
            $statsResponse = Invoke-HealthRequest -Url $Endpoints.Elasticsearch.Stats -TimeoutSeconds $Timeout
            if ($statsResponse.Success) {
                $stats = $statsResponse.Data
                $result.Details.Indices = $stats.indices.count
                $result.Details.DocsCount = $stats.indices.docs.count
                $result.Details.StoreSize = $stats.indices.store.size_in_bytes
            }
        }
    }
    else {
        $result.Status = "Down"
        $result.Details.Error = $healthResponse.Error
    }
    
    return $result
}

<#
.SYNOPSIS
    检查Kibana健康状态
#>
function Test-KibanaHealth {
    Write-Log "检查Kibana健康状态..." "INFO"
    
    $result = @{
        Component = "Kibana"
        Status = "Unknown"
        Details = @{}
        Timestamp = Get-Date
    }
    
    # 检查Docker容器状态
    $containerStatus = Test-DockerContainer "kibana"
    $result.Details.Container = $containerStatus
    
    if (-not $containerStatus.Running) {
        $result.Status = "Down"
        $result.Details.Error = "Container is not running"
        return $result
    }
    
    # 检查Kibana状态
    $statusResponse = Invoke-HealthRequest -Url $Endpoints.Kibana.Status -TimeoutSeconds $Timeout
    
    if ($statusResponse.Success) {
        $status = $statusResponse.Data
        $result.Status = $status.status.overall.state
        $result.Details.Version = $status.version.number
        $result.Details.BuildHash = $status.version.build_hash
        
        if ($Detailed -and $status.status.statuses) {
            $result.Details.Services = @{}
            foreach ($service in $status.status.statuses) {
                $result.Details.Services[$service.id] = $service.state
            }
        }
    }
    else {
        $result.Status = "Down"
        $result.Details.Error = $statusResponse.Error
    }
    
    return $result
}

<#
.SYNOPSIS
    检查Logstash健康状态
#>
function Test-LogstashHealth {
    Write-Log "检查Logstash健康状态..." "INFO"
    
    $result = @{
        Component = "Logstash"
        Status = "Unknown"
        Details = @{}
        Timestamp = Get-Date
    }
    
    # 检查Docker容器状态
    $containerStatus = Test-DockerContainer "logstash"
    $result.Details.Container = $containerStatus
    
    if (-not $containerStatus.Running) {
        $result.Status = "Down"
        $result.Details.Error = "Container is not running"
        return $result
    }
    
    # 检查Logstash统计信息
    $statsResponse = Invoke-HealthRequest -Url $Endpoints.Logstash.Stats -TimeoutSeconds $Timeout
    
    if ($statsResponse.Success) {
        $stats = $statsResponse.Data
        $result.Status = "Up"
        $result.Details.Version = $stats.version
        $result.Details.Uptime = $stats.jvm.uptime_in_millis
        $result.Details.HeapUsed = $stats.jvm.mem.heap_used_percent
        
        if ($Detailed) {
            # 检查管道状态
            $pipelineResponse = Invoke-HealthRequest -Url $Endpoints.Logstash.Health -TimeoutSeconds $Timeout
            if ($pipelineResponse.Success) {
                $pipeline = $pipelineResponse.Data
                $result.Details.Pipelines = @{}
                foreach ($p in $pipeline.pipelines.PSObject.Properties) {
                    $result.Details.Pipelines[$p.Name] = @{
                        EventsIn = $p.Value.events.in
                        EventsOut = $p.Value.events.out
                        EventsFiltered = $p.Value.events.filtered
                    }
                }
            }
        }
    }
    else {
        $result.Status = "Down"
        $result.Details.Error = $statsResponse.Error
    }
    
    return $result
}

<#
.SYNOPSIS
    检查Beats健康状态
#>
function Test-BeatsHealth {
    param(
        [string]$BeatName
    )
    
    Write-Log "检查${BeatName}健康状态..." "INFO"
    
    $result = @{
        Component = $BeatName
        Status = "Unknown"
        Details = @{}
        Timestamp = Get-Date
    }
    
    # 检查Docker容器状态
    $containerStatus = Test-DockerContainer $BeatName.ToLower()
    $result.Details.Container = $containerStatus
    
    if (-not $containerStatus.Running) {
        $result.Status = "Down"
        $result.Details.Error = "Container is not running"
        return $result
    }
    
    # 检查Beat统计信息
    $endpoint = $Endpoints[$BeatName]
    if ($endpoint -and $endpoint.Stats) {
        $statsResponse = Invoke-HealthRequest -Url $endpoint.Stats -TimeoutSeconds $Timeout
        
        if ($statsResponse.Success) {
            $stats = $statsResponse.Data
            $result.Status = "Up"
            $result.Details.Version = $stats.beat.version
            $result.Details.Uptime = $stats.beat.info.uptime.ms
            
            if ($Detailed) {
                $result.Details.EventsPublished = $stats.libbeat.output.events.total
                $result.Details.EventsDropped = $stats.libbeat.output.events.dropped
                $result.Details.BytesWritten = $stats.libbeat.output.write.bytes
            }
        }
        else {
            $result.Status = "Down"
            $result.Details.Error = $statsResponse.Error
        }
    }
    else {
        $result.Status = "Up"  # 如果没有监控端点，但容器在运行，则认为是正常的
    }
    
    return $result
}

<#
.SYNOPSIS
    检查APM Server健康状态
#>
function Test-APMHealth {
    Write-Log "检查APM Server健康状态..." "INFO"
    
    $result = @{
        Component = "APM Server"
        Status = "Unknown"
        Details = @{}
        Timestamp = Get-Date
    }
    
    # 检查Docker容器状态
    $containerStatus = Test-DockerContainer "apm-server"
    $result.Details.Container = $containerStatus
    
    if (-not $containerStatus.Running) {
        $result.Status = "Down"
        $result.Details.Error = "Container is not running"
        return $result
    }
    
    # 检查APM Server健康状态
    $healthResponse = Invoke-HealthRequest -Url $Endpoints.APM.Health -TimeoutSeconds $Timeout
    
    if ($healthResponse.Success) {
        $result.Status = "Up"
        $result.Details.Version = $healthResponse.Data.version
        
        if ($Detailed) {
            # 检查APM统计信息
            $statsResponse = Invoke-HealthRequest -Url $Endpoints.APM.Stats -TimeoutSeconds $Timeout
            if ($statsResponse.Success) {
                $stats = $statsResponse.Data
                $result.Details.EventsReceived = $stats.apm.server.events.received
                $result.Details.EventsProcessed = $stats.apm.server.events.processed
            }
        }
    }
    else {
        $result.Status = "Down"
        $result.Details.Error = $healthResponse.Error
    }
    
    return $result
}

<#
.SYNOPSIS
    执行健康检查
#>
function Invoke-HealthCheck {
    Write-Log "开始ELK堆栈健康检查..." "INFO"
    
    $script:HealthResults = @()
    
    switch ($Component) {
        "all" {
            $script:HealthResults += Test-ElasticsearchHealth
            $script:HealthResults += Test-KibanaHealth
            $script:HealthResults += Test-LogstashHealth
            $script:HealthResults += Test-BeatsHealth "Filebeat"
            $script:HealthResults += Test-BeatsHealth "Metricbeat"
            $script:HealthResults += Test-BeatsHealth "Heartbeat"
            $script:HealthResults += Test-APMHealth
        }
        "elasticsearch" { $script:HealthResults += Test-ElasticsearchHealth }
        "kibana" { $script:HealthResults += Test-KibanaHealth }
        "logstash" { $script:HealthResults += Test-LogstashHealth }
        "filebeat" { $script:HealthResults += Test-BeatsHealth "Filebeat" }
        "metricbeat" { $script:HealthResults += Test-BeatsHealth "Metricbeat" }
        "heartbeat" { $script:HealthResults += Test-BeatsHealth "Heartbeat" }
        "apm" { $script:HealthResults += Test-APMHealth }
    }
    
    Write-Log "健康检查完成" "INFO"
}

<#
.SYNOPSIS
    格式化输出结果
#>
function Format-HealthResults {
    switch ($OutputFormat) {
        "json" {
            $script:HealthResults | ConvertTo-Json -Depth 10
        }
        "csv" {
            $csvData = @()
            foreach ($result in $script:HealthResults) {
                $csvData += [PSCustomObject]@{
                    Component = $result.Component
                    Status = $result.Status
                    Timestamp = $result.Timestamp
                    ContainerRunning = $result.Details.Container.Running
                    Error = $result.Details.Error
                }
            }
            $csvData | ConvertTo-Csv -NoTypeInformation
        }
        "table" {
            Write-Host "`n=== ELK堆栈健康检查报告 ===" -ForegroundColor $Colors.Blue
            Write-Host "检查时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $Colors.Cyan
            Write-Host "检查耗时: $((Get-Date) - $script:StartTime)" -ForegroundColor $Colors.Cyan
            Write-Host ""
            
            $tableData = @()
            foreach ($result in $script:HealthResults) {
                $statusColor = switch ($result.Status) {
                    "green" { $Colors.Green }
                    "yellow" { $Colors.Yellow }
                    "red" { $Colors.Red }
                    "Up" { $Colors.Green }
                    "Down" { $Colors.Red }
                    default { $Colors.White }
                }
                
                $tableData += [PSCustomObject]@{
                    "组件" = $result.Component
                    "状态" = $result.Status
                    "容器" = if ($result.Details.Container.Running) { "运行中" } else { "已停止" }
                    "详情" = if ($result.Details.Error) { $result.Details.Error } else { "正常" }
                }
            }
            
            $tableData | Format-Table -AutoSize
            
            if ($Detailed) {
                Write-Host "`n=== 详细信息 ===" -ForegroundColor $Colors.Blue
                foreach ($result in $script:HealthResults) {
                    Write-Host "`n[$($result.Component)]" -ForegroundColor $Colors.Yellow
                    $result.Details | ConvertTo-Json -Depth 5 | Write-Host
                }
            }
            
            # 显示总体状态
            $healthyCount = ($script:HealthResults | Where-Object { $_.Status -in @("green", "Up") }).Count
            $totalCount = $script:HealthResults.Count
            
            Write-Host "`n=== 总体状态 ===" -ForegroundColor $Colors.Blue
            Write-Host "健康组件: $healthyCount/$totalCount" -ForegroundColor $(if ($healthyCount -eq $totalCount) { $Colors.Green } else { $Colors.Yellow })
            
            if ($healthyCount -eq $totalCount) {
                Write-Host "✅ 所有组件运行正常" -ForegroundColor $Colors.Green
            }
            else {
                Write-Host "⚠️  部分组件存在问题" -ForegroundColor $Colors.Yellow
            }
        }
    }
}

<#
.SYNOPSIS
    主函数
#>
function Main {
    try {
        Write-Log "启动ELK堆栈健康检查" "INFO"
        
        if ($Continuous) {
            Write-Log "启动连续监控模式，检查间隔: ${Interval}秒" "INFO"
            
            do {
                Clear-Host
                Invoke-HealthCheck
                Format-HealthResults
                
                if ($Continuous) {
                    Write-Host "`n按 Ctrl+C 停止监控..." -ForegroundColor $Colors.Cyan
                    Start-Sleep -Seconds $Interval
                }
            } while ($Continuous)
        }
        else {
            Invoke-HealthCheck
            Format-HealthResults
        }
        
        Write-Log "健康检查完成" "INFO"
    }
    catch {
        Write-Log "健康检查过程中发生错误: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

# 脚本入口点
if ($MyInvocation.InvocationName -ne '.') {
    Main
}