#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK堆栈性能监控和优化脚本
    
.DESCRIPTION
    该脚本用于监控ELK堆栈的性能指标，包括：
    - Elasticsearch集群健康状态和性能指标
    - Kibana响应时间和资源使用情况
    - Logstash处理性能和队列状态
    - 系统资源使用情况
    - 性能优化建议
    
.PARAMETER Action
    操作类型：monitor, optimize, report, alert
    
.PARAMETER Component
    组件名称：all, elasticsearch, kibana, logstash, system
    
.PARAMETER Duration
    监控持续时间（分钟）
    
.PARAMETER Interval
    监控间隔（秒）
    
.PARAMETER OutputFormat
    输出格式：console, json, html, csv
    
.PARAMETER AlertThreshold
    告警阈值配置文件路径
    
.EXAMPLE
    .\performance-monitor.ps1 -Action monitor -Component all -Duration 60
    监控所有组件60分钟
    
.EXAMPLE
    .\performance-monitor.ps1 -Action optimize -Component elasticsearch
    对Elasticsearch进行性能优化
    
.EXAMPLE
    .\performance-monitor.ps1 -Action report -OutputFormat html
    生成HTML格式的性能报告
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("monitor", "optimize", "report", "alert", "benchmark")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("all", "elasticsearch", "kibana", "logstash", "system")]
    [string]$Component = "all",
    
    [Parameter(Mandatory = $false)]
    [int]$Duration = 10,
    
    [Parameter(Mandatory = $false)]
    [int]$Interval = 30,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("console", "json", "html", "csv")]
    [string]$OutputFormat = "console",
    
    [Parameter(Mandatory = $false)]
    [string]$AlertThreshold = "configs/alerts/thresholds.json",
    
    [Parameter(Mandatory = $false)]
    [string]$ReportPath = "reports",
    
    [Parameter(Mandatory = $false)]
    [switch]$Continuous,
    
    [Parameter(Mandatory = $false)]
    [switch]$Verbose
)

# 全局变量
$script:LogPath = "logs/performance-monitor.log"
$script:ElasticsearchUrl = "http://localhost:9200"
$script:KibanaUrl = "http://localhost:5601"
$script:LogstashUrl = "http://localhost:9600"
$script:MetricsData = @{}
$script:AlertRules = @{}

# 颜色定义
$Colors = @{
    Green  = "Green"
    Red    = "Red"
    Yellow = "Yellow"
    Blue   = "Blue"
    Cyan   = "Cyan"
    White  = "White"
    Magenta = "Magenta"
}

# 性能阈值定义
$script:DefaultThresholds = @{
    elasticsearch = @{
        cluster_health = @{
            status = "yellow"  # red为严重告警
            active_shards_percent = 95
            unassigned_shards = 0
        }
        node_stats = @{
            heap_used_percent = 85
            disk_used_percent = 85
            cpu_percent = 80
            load_average = 2.0
        }
        indices_stats = @{
            search_time_per_query = 1000  # ms
            indexing_time_per_doc = 100   # ms
            merge_time_percent = 30
        }
    }
    kibana = @{
        response_time = 2000  # ms
        memory_usage_mb = 1024
        cpu_percent = 70
    }
    logstash = @{
        events_per_second = 1000
        pipeline_queue_size = 1000
        memory_usage_mb = 2048
        cpu_percent = 80
    }
    system = @{
        memory_used_percent = 85
        disk_used_percent = 85
        cpu_percent = 80
        network_errors_per_sec = 10
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
        "ALERT" { Write-Host $logEntry -ForegroundColor $Colors.Magenta }
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
        [int]$TimeoutSeconds = 30
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
        
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-RestMethod @params -ErrorAction Stop
        $stopwatch.Stop()
        
        return @{
            Success = $true
            Data = $response
            ResponseTime = $stopwatch.ElapsedMilliseconds
        }
    }
    catch {
        if ($Verbose) {
            Write-Log "API请求失败: $Url - $($_.Exception.Message)" "DEBUG"
        }
        return @{
            Success = $false
            Error = $_.Exception.Message
            ResponseTime = -1
        }
    }
}

<#
.SYNOPSIS
    加载告警阈值配置
#>
function Initialize-AlertThresholds {
    if (Test-Path $AlertThreshold) {
        try {
            $customThresholds = Get-Content -Path $AlertThreshold -Raw | ConvertFrom-Json
            $script:AlertRules = $customThresholds
            Write-Log "已加载自定义告警阈值配置" "INFO"
        }
        catch {
            Write-Log "加载告警阈值配置失败，使用默认配置" "WARN"
            $script:AlertRules = $script:DefaultThresholds
        }
    }
    else {
        $script:AlertRules = $script:DefaultThresholds
        Write-Log "使用默认告警阈值配置" "INFO"
    }
}

<#
.SYNOPSIS
    获取Elasticsearch集群健康状态
#>
function Get-ElasticsearchHealth {
    Write-Log "获取Elasticsearch集群健康状态" "DEBUG"
    
    $healthResponse = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_cluster/health"
    $statsResponse = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_cluster/stats"
    $nodesResponse = Invoke-ApiRequest -Url "$script:ElasticsearchUrl/_nodes/stats"
    
    $metrics = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        available = $healthResponse.Success
        response_time = $healthResponse.ResponseTime
    }
    
    if ($healthResponse.Success) {
        $health = $healthResponse.Data
        $metrics.cluster_name = $health.cluster_name
        $metrics.status = $health.status
        $metrics.number_of_nodes = $health.number_of_nodes
        $metrics.number_of_data_nodes = $health.number_of_data_nodes
        $metrics.active_primary_shards = $health.active_primary_shards
        $metrics.active_shards = $health.active_shards
        $metrics.relocating_shards = $health.relocating_shards
        $metrics.initializing_shards = $health.initializing_shards
        $metrics.unassigned_shards = $health.unassigned_shards
        $metrics.active_shards_percent_as_number = $health.active_shards_percent_as_number
    }
    
    if ($statsResponse.Success) {
        $stats = $statsResponse.Data
        $metrics.indices_count = $stats.indices.count
        $metrics.indices_docs_count = $stats.indices.docs.count
        $metrics.indices_store_size_bytes = $stats.indices.store.size_in_bytes
    }
    
    if ($nodesResponse.Success) {
        $nodes = $nodesResponse.Data.nodes
        $totalHeapUsed = 0
        $totalHeapMax = 0
        $totalCpuPercent = 0
        $nodeCount = 0
        
        foreach ($nodeId in $nodes.PSObject.Properties.Name) {
            $node = $nodes.$nodeId
            $totalHeapUsed += $node.jvm.mem.heap_used_in_bytes
            $totalHeapMax += $node.jvm.mem.heap_max_in_bytes
            $totalCpuPercent += $node.os.cpu.percent
            $nodeCount++
        }
        
        if ($nodeCount -gt 0) {
            $metrics.heap_used_percent = [math]::Round(($totalHeapUsed / $totalHeapMax) * 100, 2)
            $metrics.avg_cpu_percent = [math]::Round($totalCpuPercent / $nodeCount, 2)
        }
    }
    
    return $metrics
}

<#
.SYNOPSIS
    获取Kibana性能指标
#>
function Get-KibanaMetrics {
    Write-Log "获取Kibana性能指标" "DEBUG"
    
    $statusResponse = Invoke-ApiRequest -Url "$script:KibanaUrl/api/status"
    $metricsResponse = Invoke-ApiRequest -Url "$script:KibanaUrl/api/stats"
    
    $metrics = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        available = $statusResponse.Success
        response_time = $statusResponse.ResponseTime
    }
    
    if ($statusResponse.Success) {
        $status = $statusResponse.Data
        $metrics.status = $status.status.overall.state
        $metrics.version = $status.version.number
    }
    
    if ($metricsResponse.Success) {
        $stats = $metricsResponse.Data
        if ($stats.process) {
            $metrics.memory_heap_used_bytes = $stats.process.memory.heap.used_in_bytes
            $metrics.memory_heap_max_bytes = $stats.process.memory.heap.max_in_bytes
            $metrics.uptime_ms = $stats.process.uptime_in_millis
        }
        
        if ($stats.requests) {
            $metrics.total_requests = $stats.requests.total
            $metrics.disconnects = $stats.requests.disconnects
        }
    }
    
    return $metrics
}

<#
.SYNOPSIS
    获取Logstash性能指标
#>
function Get-LogstashMetrics {
    Write-Log "获取Logstash性能指标" "DEBUG"
    
    $statsResponse = Invoke-ApiRequest -Url "$script:LogstashUrl/_node/stats"
    $hotThreadsResponse = Invoke-ApiRequest -Url "$script:LogstashUrl/_node/hot_threads"
    
    $metrics = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        available = $statsResponse.Success
        response_time = $statsResponse.ResponseTime
    }
    
    if ($statsResponse.Success) {
        $stats = $statsResponse.Data
        
        # JVM指标
        if ($stats.jvm) {
            $metrics.heap_used_percent = $stats.jvm.mem.heap_used_percent
            $metrics.heap_used_bytes = $stats.jvm.mem.heap_used_in_bytes
            $metrics.heap_max_bytes = $stats.jvm.mem.heap_max_in_bytes
            $metrics.gc_collection_time_ms = $stats.jvm.gc.collectors.old.collection_time_in_millis
        }
        
        # 进程指标
        if ($stats.process) {
            $metrics.cpu_percent = $stats.process.cpu.percent
            $metrics.open_file_descriptors = $stats.process.open_file_descriptors
        }
        
        # 管道指标
        if ($stats.pipelines) {
            $totalEvents = 0
            $totalQueueSize = 0
            
            foreach ($pipelineId in $stats.pipelines.PSObject.Properties.Name) {
                $pipeline = $stats.pipelines.$pipelineId
                $totalEvents += $pipeline.events.in
                if ($pipeline.queue) {
                    $totalQueueSize += $pipeline.queue.events
                }
            }
            
            $metrics.total_events_in = $totalEvents
            $metrics.total_queue_size = $totalQueueSize
        }
        
        # 重载指标
        if ($stats.reloads) {
            $metrics.config_reload_successes = $stats.reloads.successes
            $metrics.config_reload_failures = $stats.reloads.failures
        }
    }
    
    return $metrics
}

<#
.SYNOPSIS
    获取系统性能指标
#>
function Get-SystemMetrics {
    Write-Log "获取系统性能指标" "DEBUG"
    
    $metrics = @{
        timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    }
    
    try {
        # CPU使用率
        $cpu = Get-WmiObject -Class Win32_Processor | Measure-Object -Property LoadPercentage -Average
        $metrics.cpu_percent = [math]::Round($cpu.Average, 2)
        
        # 内存使用情况
        $memory = Get-WmiObject -Class Win32_OperatingSystem
        $totalMemory = [math]::Round($memory.TotalVisibleMemorySize / 1KB, 2)
        $freeMemory = [math]::Round($memory.FreePhysicalMemory / 1KB, 2)
        $usedMemory = $totalMemory - $freeMemory
        $metrics.memory_total_mb = $totalMemory
        $metrics.memory_used_mb = $usedMemory
        $metrics.memory_used_percent = [math]::Round(($usedMemory / $totalMemory) * 100, 2)
        
        # 磁盘使用情况
        $disks = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DriveType -eq 3 }
        $diskMetrics = @()
        
        foreach ($disk in $disks) {
            $totalSize = [math]::Round($disk.Size / 1GB, 2)
            $freeSpace = [math]::Round($disk.FreeSpace / 1GB, 2)
            $usedSpace = $totalSize - $freeSpace
            $usedPercent = if ($totalSize -gt 0) { [math]::Round(($usedSpace / $totalSize) * 100, 2) } else { 0 }
            
            $diskMetrics += @{
                drive = $disk.DeviceID
                total_gb = $totalSize
                used_gb = $usedSpace
                free_gb = $freeSpace
                used_percent = $usedPercent
            }
        }
        
        $metrics.disks = $diskMetrics
        
        # 网络统计
        $networkAdapters = Get-WmiObject -Class Win32_PerfRawData_Tcpip_NetworkInterface | Where-Object { $_.Name -notlike "*Loopback*" -and $_.Name -notlike "*isatap*" }
        $totalBytesReceived = ($networkAdapters | Measure-Object -Property BytesReceivedPerSec -Sum).Sum
        $totalBytesSent = ($networkAdapters | Measure-Object -Property BytesSentPerSec -Sum).Sum
        
        $metrics.network_bytes_received = $totalBytesReceived
        $metrics.network_bytes_sent = $totalBytesSent
        
        # Docker容器统计（如果可用）
        try {
            $dockerStats = docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>$null
            if ($dockerStats) {
                $metrics.docker_containers = $dockerStats.Count - 1  # 减去标题行
            }
        }
        catch {
            # Docker不可用，忽略
        }
    }
    catch {
        Write-Log "获取系统指标失败: $($_.Exception.Message)" "WARN"
    }
    
    return $metrics
}

<#
.SYNOPSIS
    检查性能告警
#>
function Test-PerformanceAlerts {
    param(
        [hashtable]$Metrics,
        [string]$Component
    )
    
    $alerts = @()
    $thresholds = $script:AlertRules.$Component
    
    if (-not $thresholds) {
        return $alerts
    }
    
    switch ($Component) {
        "elasticsearch" {
            # 集群状态检查
            if ($Metrics.status -eq "red") {
                $alerts += @{
                    level = "CRITICAL"
                    message = "Elasticsearch集群状态为红色"
                    metric = "cluster_status"
                    value = $Metrics.status
                }
            }
            elseif ($Metrics.status -eq "yellow" -and $thresholds.cluster_health.status -eq "green") {
                $alerts += @{
                    level = "WARNING"
                    message = "Elasticsearch集群状态为黄色"
                    metric = "cluster_status"
                    value = $Metrics.status
                }
            }
            
            # 堆内存使用率检查
            if ($Metrics.heap_used_percent -gt $thresholds.node_stats.heap_used_percent) {
                $alerts += @{
                    level = "WARNING"
                    message = "Elasticsearch堆内存使用率过高: $($Metrics.heap_used_percent)%"
                    metric = "heap_used_percent"
                    value = $Metrics.heap_used_percent
                    threshold = $thresholds.node_stats.heap_used_percent
                }
            }
            
            # 未分配分片检查
            if ($Metrics.unassigned_shards -gt $thresholds.cluster_health.unassigned_shards) {
                $alerts += @{
                    level = "WARNING"
                    message = "存在未分配的分片: $($Metrics.unassigned_shards)"
                    metric = "unassigned_shards"
                    value = $Metrics.unassigned_shards
                    threshold = $thresholds.cluster_health.unassigned_shards
                }
            }
        }
        
        "kibana" {
            # 响应时间检查
            if ($Metrics.response_time -gt $thresholds.response_time) {
                $alerts += @{
                    level = "WARNING"
                    message = "Kibana响应时间过长: $($Metrics.response_time)ms"
                    metric = "response_time"
                    value = $Metrics.response_time
                    threshold = $thresholds.response_time
                }
            }
        }
        
        "logstash" {
            # 堆内存使用率检查
            if ($Metrics.heap_used_percent -gt $thresholds.memory_usage_mb) {
                $alerts += @{
                    level = "WARNING"
                    message = "Logstash堆内存使用率过高: $($Metrics.heap_used_percent)%"
                    metric = "heap_used_percent"
                    value = $Metrics.heap_used_percent
                    threshold = $thresholds.memory_usage_mb
                }
            }
            
            # CPU使用率检查
            if ($Metrics.cpu_percent -gt $thresholds.cpu_percent) {
                $alerts += @{
                    level = "WARNING"
                    message = "Logstash CPU使用率过高: $($Metrics.cpu_percent)%"
                    metric = "cpu_percent"
                    value = $Metrics.cpu_percent
                    threshold = $thresholds.cpu_percent
                }
            }
        }
        
        "system" {
            # 内存使用率检查
            if ($Metrics.memory_used_percent -gt $thresholds.memory_used_percent) {
                $alerts += @{
                    level = "WARNING"
                    message = "系统内存使用率过高: $($Metrics.memory_used_percent)%"
                    metric = "memory_used_percent"
                    value = $Metrics.memory_used_percent
                    threshold = $thresholds.memory_used_percent
                }
            }
            
            # 磁盘使用率检查
            foreach ($disk in $Metrics.disks) {
                if ($disk.used_percent -gt $thresholds.disk_used_percent) {
                    $alerts += @{
                        level = "WARNING"
                        message = "磁盘 $($disk.drive) 使用率过高: $($disk.used_percent)%"
                        metric = "disk_used_percent"
                        value = $disk.used_percent
                        threshold = $thresholds.disk_used_percent
                    }
                }
            }
        }
    }
    
    return $alerts
}

<#
.SYNOPSIS
    执行性能监控
#>
function Invoke-PerformanceMonitoring {
    Write-Log "开始性能监控" "INFO"
    
    $endTime = (Get-Date).AddMinutes($Duration)
    $iteration = 0
    
    do {
        $iteration++
        Write-Log "执行第 $iteration 次监控采集" "INFO"
        
        $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
        $allMetrics = @{
            timestamp = $timestamp
            iteration = $iteration
        }
        
        # 收集各组件指标
        if ($Component -eq "all" -or $Component -eq "elasticsearch") {
            $allMetrics.elasticsearch = Get-ElasticsearchHealth
            $alerts = Test-PerformanceAlerts -Metrics $allMetrics.elasticsearch -Component "elasticsearch"
            foreach ($alert in $alerts) {
                Write-Log "[ELASTICSEARCH] $($alert.message)" "ALERT"
            }
        }
        
        if ($Component -eq "all" -or $Component -eq "kibana") {
            $allMetrics.kibana = Get-KibanaMetrics
            $alerts = Test-PerformanceAlerts -Metrics $allMetrics.kibana -Component "kibana"
            foreach ($alert in $alerts) {
                Write-Log "[KIBANA] $($alert.message)" "ALERT"
            }
        }
        
        if ($Component -eq "all" -or $Component -eq "logstash") {
            $allMetrics.logstash = Get-LogstashMetrics
            $alerts = Test-PerformanceAlerts -Metrics $allMetrics.logstash -Component "logstash"
            foreach ($alert in $alerts) {
                Write-Log "[LOGSTASH] $($alert.message)" "ALERT"
            }
        }
        
        if ($Component -eq "all" -or $Component -eq "system") {
            $allMetrics.system = Get-SystemMetrics
            $alerts = Test-PerformanceAlerts -Metrics $allMetrics.system -Component "system"
            foreach ($alert in $alerts) {
                Write-Log "[SYSTEM] $($alert.message)" "ALERT"
            }
        }
        
        # 存储指标数据
        $script:MetricsData[$timestamp] = $allMetrics
        
        # 输出当前状态
        if ($OutputFormat -eq "console") {
            Show-MetricsSummary $allMetrics
        }
        
        # 等待下次采集
        if ((Get-Date) -lt $endTime -or $Continuous) {
            Start-Sleep -Seconds $Interval
        }
        
    } while ((Get-Date) -lt $endTime -or $Continuous)
    
    Write-Log "性能监控完成，共采集 $iteration 次数据" "INFO"
}

<#
.SYNOPSIS
    显示指标摘要
#>
function Show-MetricsSummary {
    param(
        [hashtable]$Metrics
    )
    
    Write-Host "`n=== 性能指标摘要 ($(Get-Date -Format 'HH:mm:ss')) ===" -ForegroundColor $Colors.Blue
    
    if ($Metrics.elasticsearch) {
        $es = $Metrics.elasticsearch
        Write-Host "Elasticsearch:" -ForegroundColor $Colors.Cyan
        Write-Host "  状态: $($es.status)" -ForegroundColor $(if ($es.status -eq "green") { $Colors.Green } elseif ($es.status -eq "yellow") { $Colors.Yellow } else { $Colors.Red })
        Write-Host "  节点数: $($es.number_of_nodes)/$($es.number_of_data_nodes)"
        Write-Host "  活跃分片: $($es.active_shards) ($($es.active_shards_percent_as_number)%)"
        if ($es.heap_used_percent) {
            Write-Host "  堆内存: $($es.heap_used_percent)%" -ForegroundColor $(if ($es.heap_used_percent -gt 85) { $Colors.Red } elseif ($es.heap_used_percent -gt 70) { $Colors.Yellow } else { $Colors.Green })
        }
        Write-Host "  响应时间: $($es.response_time)ms"
    }
    
    if ($Metrics.kibana) {
        $kb = $Metrics.kibana
        Write-Host "Kibana:" -ForegroundColor $Colors.Cyan
        Write-Host "  状态: $($kb.status)" -ForegroundColor $(if ($kb.status -eq "green") { $Colors.Green } else { $Colors.Yellow })
        Write-Host "  响应时间: $($kb.response_time)ms" -ForegroundColor $(if ($kb.response_time -gt 2000) { $Colors.Red } elseif ($kb.response_time -gt 1000) { $Colors.Yellow } else { $Colors.Green })
        if ($kb.memory_heap_used_bytes -and $kb.memory_heap_max_bytes) {
            $heapPercent = [math]::Round(($kb.memory_heap_used_bytes / $kb.memory_heap_max_bytes) * 100, 2)
            Write-Host "  堆内存: $heapPercent%"
        }
    }
    
    if ($Metrics.logstash) {
        $ls = $Metrics.logstash
        Write-Host "Logstash:" -ForegroundColor $Colors.Cyan
        Write-Host "  可用: $(if ($ls.available) { '是' } else { '否' })" -ForegroundColor $(if ($ls.available) { $Colors.Green } else { $Colors.Red })
        if ($ls.heap_used_percent) {
            Write-Host "  堆内存: $($ls.heap_used_percent)%" -ForegroundColor $(if ($ls.heap_used_percent -gt 85) { $Colors.Red } elseif ($ls.heap_used_percent -gt 70) { $Colors.Yellow } else { $Colors.Green })
        }
        if ($ls.cpu_percent) {
            Write-Host "  CPU: $($ls.cpu_percent)%" -ForegroundColor $(if ($ls.cpu_percent -gt 80) { $Colors.Red } elseif ($ls.cpu_percent -gt 60) { $Colors.Yellow } else { $Colors.Green })
        }
        if ($ls.total_events_in) {
            Write-Host "  处理事件: $($ls.total_events_in)"
        }
    }
    
    if ($Metrics.system) {
        $sys = $Metrics.system
        Write-Host "系统:" -ForegroundColor $Colors.Cyan
        Write-Host "  CPU: $($sys.cpu_percent)%" -ForegroundColor $(if ($sys.cpu_percent -gt 80) { $Colors.Red } elseif ($sys.cpu_percent -gt 60) { $Colors.Yellow } else { $Colors.Green })
        Write-Host "  内存: $($sys.memory_used_percent)%" -ForegroundColor $(if ($sys.memory_used_percent -gt 85) { $Colors.Red } elseif ($sys.memory_used_percent -gt 70) { $Colors.Yellow } else { $Colors.Green })
        
        if ($sys.disks) {
            foreach ($disk in $sys.disks) {
                Write-Host "  磁盘 $($disk.drive): $($disk.used_percent)%" -ForegroundColor $(if ($disk.used_percent -gt 85) { $Colors.Red } elseif ($disk.used_percent -gt 70) { $Colors.Yellow } else { $Colors.Green })
            }
        }
    }
    
    Write-Host ""
}

<#
.SYNOPSIS
    生成性能报告
#>
function New-PerformanceReport {
    Write-Log "生成性能报告" "INFO"
    
    if ($script:MetricsData.Count -eq 0) {
        Write-Log "没有可用的指标数据" "WARN"
        return
    }
    
    # 确保报告目录存在
    if (-not (Test-Path $ReportPath)) {
        New-Item -ItemType Directory -Path $ReportPath -Force | Out-Null
    }
    
    $reportTimestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $reportFile = Join-Path $ReportPath "performance-report-$reportTimestamp.$OutputFormat"
    
    switch ($OutputFormat) {
        "json" {
            $script:MetricsData | ConvertTo-Json -Depth 10 | Out-File -FilePath $reportFile -Encoding UTF8
        }
        "csv" {
            # 简化的CSV输出
            $csvData = @()
            foreach ($timestamp in $script:MetricsData.Keys) {
                $metrics = $script:MetricsData[$timestamp]
                $row = [PSCustomObject]@{
                    Timestamp = $timestamp
                    ES_Status = $metrics.elasticsearch.status
                    ES_HeapPercent = $metrics.elasticsearch.heap_used_percent
                    KB_ResponseTime = $metrics.kibana.response_time
                    LS_HeapPercent = $metrics.logstash.heap_used_percent
                    SYS_CPUPercent = $metrics.system.cpu_percent
                    SYS_MemoryPercent = $metrics.system.memory_used_percent
                }
                $csvData += $row
            }
            $csvData | Export-Csv -Path $reportFile -NoTypeInformation -Encoding UTF8
        }
        "html" {
            $htmlContent = Generate-HtmlReport
            $htmlContent | Out-File -FilePath $reportFile -Encoding UTF8
        }
    }
    
    Write-Log "性能报告已生成: $reportFile" "INFO"
}

<#
.SYNOPSIS
    生成HTML报告
#>
function Generate-HtmlReport {
    $html = @"
<!DOCTYPE html>
<html>
<head>
    <title>ELK性能监控报告</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .metric-table { width: 100%; border-collapse: collapse; }
        .metric-table th, .metric-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .metric-table th { background-color: #f2f2f2; }
        .status-green { color: green; font-weight: bold; }
        .status-yellow { color: orange; font-weight: bold; }
        .status-red { color: red; font-weight: bold; }
        .chart-container { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>ELK性能监控报告</h1>
        <p>生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <p>监控时长: $Duration 分钟</p>
        <p>采集间隔: $Interval 秒</p>
        <p>数据点数: $($script:MetricsData.Count)</p>
    </div>
"@
    
    # 添加摘要统计
    $html += "`n    <div class='section'>`n        <h2>监控摘要</h2>`n"
    
    # 这里可以添加更多的HTML内容和图表
    
    $html += "`n    </div>`n</body>`n</html>"
    
    return $html
}

<#
.SYNOPSIS
    执行性能优化
#>
function Invoke-PerformanceOptimization {
    Write-Log "开始性能优化分析" "INFO"
    
    # 收集当前指标
    $currentMetrics = @{}
    
    if ($Component -eq "all" -or $Component -eq "elasticsearch") {
        $currentMetrics.elasticsearch = Get-ElasticsearchHealth
        Optimize-ElasticsearchPerformance $currentMetrics.elasticsearch
    }
    
    if ($Component -eq "all" -or $Component -eq "kibana") {
        $currentMetrics.kibana = Get-KibanaMetrics
        Optimize-KibanaPerformance $currentMetrics.kibana
    }
    
    if ($Component -eq "all" -or $Component -eq "logstash") {
        $currentMetrics.logstash = Get-LogstashMetrics
        Optimize-LogstashPerformance $currentMetrics.logstash
    }
    
    if ($Component -eq "all" -or $Component -eq "system") {
        $currentMetrics.system = Get-SystemMetrics
        Optimize-SystemPerformance $currentMetrics.system
    }
}

<#
.SYNOPSIS
    Elasticsearch性能优化建议
#>
function Optimize-ElasticsearchPerformance {
    param([hashtable]$Metrics)
    
    Write-Host "`n=== Elasticsearch性能优化建议 ===" -ForegroundColor $Colors.Blue
    
    $recommendations = @()
    
    # 堆内存优化
    if ($Metrics.heap_used_percent -gt 85) {
        $recommendations += "堆内存使用率过高($($Metrics.heap_used_percent)%)，建议增加JVM堆内存或优化查询"
    }
    
    # 集群状态优化
    if ($Metrics.status -ne "green") {
        $recommendations += "集群状态为$($Metrics.status)，检查分片分配和节点健康状态"
    }
    
    # 未分配分片
    if ($Metrics.unassigned_shards -gt 0) {
        $recommendations += "存在$($Metrics.unassigned_shards)个未分配分片，检查副本设置和磁盘空间"
    }
    
    # 响应时间优化
    if ($Metrics.response_time -gt 1000) {
        $recommendations += "API响应时间较长($($Metrics.response_time)ms)，考虑优化查询或增加节点"
    }
    
    if ($recommendations.Count -eq 0) {
        Write-Host "✓ Elasticsearch性能良好，无需优化" -ForegroundColor $Colors.Green
    }
    else {
        foreach ($rec in $recommendations) {
            Write-Host "• $rec" -ForegroundColor $Colors.Yellow
        }
    }
}

<#
.SYNOPSIS
    Kibana性能优化建议
#>
function Optimize-KibanaPerformance {
    param([hashtable]$Metrics)
    
    Write-Host "`n=== Kibana性能优化建议 ===" -ForegroundColor $Colors.Blue
    
    $recommendations = @()
    
    if ($Metrics.response_time -gt 2000) {
        $recommendations += "响应时间过长($($Metrics.response_time)ms)，检查Elasticsearch连接和查询复杂度"
    }
    
    if (-not $Metrics.available) {
        $recommendations += "Kibana服务不可用，检查服务状态和配置"
    }
    
    if ($recommendations.Count -eq 0) {
        Write-Host "✓ Kibana性能良好，无需优化" -ForegroundColor $Colors.Green
    }
    else {
        foreach ($rec in $recommendations) {
            Write-Host "• $rec" -ForegroundColor $Colors.Yellow
        }
    }
}

<#
.SYNOPSIS
    Logstash性能优化建议
#>
function Optimize-LogstashPerformance {
    param([hashtable]$Metrics)
    
    Write-Host "`n=== Logstash性能优化建议 ===" -ForegroundColor $Colors.Blue
    
    $recommendations = @()
    
    if ($Metrics.heap_used_percent -gt 85) {
        $recommendations += "堆内存使用率过高($($Metrics.heap_used_percent)%)，增加JVM堆内存"
    }
    
    if ($Metrics.cpu_percent -gt 80) {
        $recommendations += "CPU使用率过高($($Metrics.cpu_percent)%)，优化管道配置或增加worker数量"
    }
    
    if ($Metrics.total_queue_size -gt 1000) {
        $recommendations += "队列积压严重($($Metrics.total_queue_size)个事件)，检查输出性能"
    }
    
    if (-not $Metrics.available) {
        $recommendations += "Logstash服务不可用，检查服务状态和配置"
    }
    
    if ($recommendations.Count -eq 0) {
        Write-Host "✓ Logstash性能良好，无需优化" -ForegroundColor $Colors.Green
    }
    else {
        foreach ($rec in $recommendations) {
            Write-Host "• $rec" -ForegroundColor $Colors.Yellow
        }
    }
}

<#
.SYNOPSIS
    系统性能优化建议
#>
function Optimize-SystemPerformance {
    param([hashtable]$Metrics)
    
    Write-Host "`n=== 系统性能优化建议 ===" -ForegroundColor $Colors.Blue
    
    $recommendations = @()
    
    if ($Metrics.memory_used_percent -gt 85) {
        $recommendations += "系统内存使用率过高($($Metrics.memory_used_percent)%)，考虑增加内存或优化应用"
    }
    
    if ($Metrics.cpu_percent -gt 80) {
        $recommendations += "系统CPU使用率过高($($Metrics.cpu_percent)%)，检查高CPU进程"
    }
    
    foreach ($disk in $Metrics.disks) {
        if ($disk.used_percent -gt 85) {
            $recommendations += "磁盘$($disk.drive)使用率过高($($disk.used_percent)%)，清理磁盘空间"
        }
    }
    
    if ($recommendations.Count -eq 0) {
        Write-Host "✓ 系统性能良好，无需优化" -ForegroundColor $Colors.Green
    }
    else {
        foreach ($rec in $recommendations) {
            Write-Host "• $rec" -ForegroundColor $Colors.Yellow
        }
    }
}

<#
.SYNOPSIS
    主函数
#>
function Main {
    try {
        Write-Log "启动ELK性能监控脚本" "INFO"
        
        # 初始化告警阈值
        Initialize-AlertThresholds
        
        switch ($Action) {
            "monitor" {
                Invoke-PerformanceMonitoring
                
                # 生成报告（如果不是控制台输出）
                if ($OutputFormat -ne "console") {
                    New-PerformanceReport
                }
            }
            "optimize" {
                Invoke-PerformanceOptimization
            }
            "report" {
                if ($script:MetricsData.Count -eq 0) {
                    Write-Log "没有监控数据，先执行监控操作" "WARN"
                }
                else {
                    New-PerformanceReport
                }
            }
            "alert" {
                Write-Log "告警功能开发中" "INFO"
            }
            "benchmark" {
                Write-Log "基准测试功能开发中" "INFO"
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