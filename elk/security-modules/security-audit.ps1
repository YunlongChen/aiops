<#
.SYNOPSIS
    ELK安全审计模块
.DESCRIPTION
    提供安全事件记录、分析和报告功能
.AUTHOR
    AI Assistant
.DATE
    $(Get-Date -Format 'yyyy-MM-dd')
#>

# 导入通用模块
. "$PSScriptRoot\security-common.ps1"

<#
.SYNOPSIS
    记录安全事件
#>
function Write-SecurityEvent {
    param(
        [Parameter(Mandatory = $true)]
        [string]$EventType,
        
        [Parameter(Mandatory = $true)]
        [string]$Description,
        
        [string]$User = $env:USERNAME,
        [string]$Source = "ELK-Security",
        [string]$Severity = "INFO",
        [hashtable]$Details = @{}
    )
    
    try {
        $timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"
        $eventId = [System.Guid]::NewGuid().ToString()
        
        $securityEvent = @{
            "@timestamp" = $timestamp
            "event_id" = $eventId
            "event_type" = $EventType
            "description" = $Description
            "user" = $User
            "source" = $Source
            "severity" = $Severity.ToUpper()
            "host" = $env:COMPUTERNAME
            "details" = $Details
        }
        
        # 写入到审计日志文件
        $auditLogPath = Join-Path $Global:ELK_LOGS_PATH "security-audit.json"
        $securityEvent | ConvertTo-Json -Compress | Add-Content -Path $auditLogPath -Encoding UTF8
        
        # 如果Elasticsearch可用，直接发送事件
        if (Test-ElasticsearchConnection) {
            Send-SecurityEventToElasticsearch -Event $securityEvent
        }
        
        Write-Log "安全事件已记录: $EventType - $Description" "INFO"
        return $eventId
    }
    catch {
        Write-Log "记录安全事件失败: $($_.Exception.Message)" "ERROR"
        return $null
    }
}

<#
.SYNOPSIS
    发送安全事件到Elasticsearch
#>
function Send-SecurityEventToElasticsearch {
    param(
        [Parameter(Mandatory = $true)]
        [hashtable]$Event
    )
    
    try {
        $indexName = "security-audit-$(Get-Date -Format 'yyyy.MM')"
        $uri = "$Global:ELASTICSEARCH_URL/$indexName/_doc"
        
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        # 添加认证头
        if ($Global:SECURITY_ENABLED) {
            $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$($Global:DefaultPasswords.elastic)"))
            $headers["Authorization"] = "Basic $credentials"
        }
        
        $body = $Event | ConvertTo-Json -Depth 10
        
        $response = Invoke-RestMethod -Uri $uri -Method POST -Headers $headers -Body $body -SkipCertificateCheck
        
        Write-Log "安全事件已发送到Elasticsearch: $($response._id)" "DEBUG"
        return $response._id
    }
    catch {
        Write-Log "发送安全事件到Elasticsearch失败: $($_.Exception.Message)" "WARNING"
        return $null
    }
}

<#
.SYNOPSIS
    测试Elasticsearch连接
#>
function Test-ElasticsearchConnection {
    try {
        $uri = "$Global:ELASTICSEARCH_URL/_cluster/health"
        $headers = @{}
        
        if ($Global:SECURITY_ENABLED) {
            $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$($Global:DefaultPasswords.elastic)"))
            $headers["Authorization"] = "Basic $credentials"
        }
        
        $response = Invoke-RestMethod -Uri $uri -Method GET -Headers $headers -TimeoutSec 5 -SkipCertificateCheck
        return $response.status -eq "green" -or $response.status -eq "yellow"
    }
    catch {
        return $false
    }
}

<#
.SYNOPSIS
    生成安全审计报告
#>
function New-SecurityAuditReport {
    param(
        [DateTime]$StartDate = (Get-Date).AddDays(-7),
        [DateTime]$EndDate = (Get-Date),
        [string]$OutputPath = "security-audit-report.html",
        [string[]]$EventTypes = @(),
        [string[]]$Severities = @("CRITICAL", "ERROR", "WARNING", "INFO")
    )
    
    Write-Log "生成安全审计报告" "INFO"
    
    try {
        # 从Elasticsearch获取审计数据
        $auditData = Get-SecurityAuditData -StartDate $StartDate -EndDate $EndDate -EventTypes $EventTypes -Severities $Severities
        
        if (-not $auditData -or $auditData.Count -eq 0) {
            Write-Log "指定时间范围内没有找到审计数据" "WARNING"
            return $false
        }
        
        # 生成统计信息
        $statistics = Get-AuditStatistics -AuditData $auditData
        
        # 生成HTML报告
        $htmlReport = Generate-AuditReportHTML -AuditData $auditData -Statistics $statistics -StartDate $StartDate -EndDate $EndDate
        
        # 保存报告
        $htmlReport | Out-File -FilePath $OutputPath -Encoding UTF8
        
        Write-Log "安全审计报告已生成: $OutputPath" "INFO"
        return $true
    }
    catch {
        Write-Log "生成安全审计报告失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    从Elasticsearch获取审计数据
#>
function Get-SecurityAuditData {
    param(
        [DateTime]$StartDate,
        [DateTime]$EndDate,
        [string[]]$EventTypes,
        [string[]]$Severities
    )
    
    try {
        $query = @{
            "query" = @{
                "bool" = @{
                    "must" = @(
                        @{
                            "range" = @{
                                "@timestamp" = @{
                                    "gte" = $StartDate.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                                    "lte" = $EndDate.ToString("yyyy-MM-ddTHH:mm:ss.fffZ")
                                }
                            }
                        }
                    )
                }
            }
            "sort" = @(
                @{
                    "@timestamp" = @{
                        "order" = "desc"
                    }
                }
            )
            "size" = 10000
        }
        
        # 添加事件类型过滤
        if ($EventTypes -and $EventTypes.Count -gt 0) {
            $query.query.bool.must += @{
                "terms" = @{
                    "event_type" = $EventTypes
                }
            }
        }
        
        # 添加严重性过滤
        if ($Severities -and $Severities.Count -gt 0) {
            $query.query.bool.must += @{
                "terms" = @{
                    "severity" = $Severities
                }
            }
        }
        
        $indexPattern = "security-audit-*"
        $uri = "$Global:ELASTICSEARCH_URL/$indexPattern/_search"
        
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($Global:SECURITY_ENABLED) {
            $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$($Global:DefaultPasswords.elastic)"))
            $headers["Authorization"] = "Basic $credentials"
        }
        
        $body = $query | ConvertTo-Json -Depth 10
        $response = Invoke-RestMethod -Uri $uri -Method POST -Headers $headers -Body $body -SkipCertificateCheck
        
        return $response.hits.hits | ForEach-Object { $_._source }
    }
    catch {
        Write-Log "获取审计数据失败: $($_.Exception.Message)" "ERROR"
        return @()
    }
}

<#
.SYNOPSIS
    计算审计统计信息
#>
function Get-AuditStatistics {
    param(
        [array]$AuditData
    )
    
    $statistics = @{
        "total_events" = $AuditData.Count
        "by_severity" = @{}
        "by_event_type" = @{}
        "by_user" = @{}
        "by_source" = @{}
        "timeline" = @{}
    }
    
    foreach ($event in $AuditData) {
        # 按严重性统计
        $severity = $event.severity
        if (-not $statistics.by_severity.ContainsKey($severity)) {
            $statistics.by_severity[$severity] = 0
        }
        $statistics.by_severity[$severity]++
        
        # 按事件类型统计
        $eventType = $event.event_type
        if (-not $statistics.by_event_type.ContainsKey($eventType)) {
            $statistics.by_event_type[$eventType] = 0
        }
        $statistics.by_event_type[$eventType]++
        
        # 按用户统计
        $user = $event.user
        if (-not $statistics.by_user.ContainsKey($user)) {
            $statistics.by_user[$user] = 0
        }
        $statistics.by_user[$user]++
        
        # 按来源统计
        $source = $event.source
        if (-not $statistics.by_source.ContainsKey($source)) {
            $statistics.by_source[$source] = 0
        }
        $statistics.by_source[$source]++
        
        # 按时间统计（按小时）
        $timestamp = [DateTime]::Parse($event.'@timestamp')
        $hour = $timestamp.ToString("yyyy-MM-dd HH:00")
        if (-not $statistics.timeline.ContainsKey($hour)) {
            $statistics.timeline[$hour] = 0
        }
        $statistics.timeline[$hour]++
    }
    
    return $statistics
}

<#
.SYNOPSIS
    生成HTML审计报告
#>
function Generate-AuditReportHTML {
    param(
        [array]$AuditData,
        [hashtable]$Statistics,
        [DateTime]$StartDate,
        [DateTime]$EndDate
    )
    
    $html = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ELK安全审计报告</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007acc;
        }
        .header h1 {
            color: #007acc;
            margin: 0;
        }
        .header p {
            color: #666;
            margin: 10px 0 0 0;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 2em;
        }
        .summary-card p {
            margin: 0;
            opacity: 0.9;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }
        .chart-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .chart {
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
        }
        .chart h3 {
            margin-top: 0;
            color: #333;
        }
        .bar {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .bar-label {
            width: 120px;
            font-size: 0.9em;
        }
        .bar-fill {
            height: 20px;
            background: linear-gradient(90deg, #007acc, #4CAF50);
            margin-right: 10px;
            border-radius: 10px;
        }
        .bar-value {
            font-weight: bold;
            color: #333;
        }
        .events-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .events-table th,
        .events-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .events-table th {
            background-color: #007acc;
            color: white;
        }
        .events-table tr:hover {
            background-color: #f5f5f5;
        }
        .severity-critical { color: #d32f2f; font-weight: bold; }
        .severity-error { color: #f57c00; font-weight: bold; }
        .severity-warning { color: #fbc02d; font-weight: bold; }
        .severity-info { color: #1976d2; }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ELK安全审计报告</h1>
            <p>报告时间范围: $($StartDate.ToString('yyyy-MM-dd HH:mm')) - $($EndDate.ToString('yyyy-MM-dd HH:mm'))</p>
            <p>生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <h3>$($Statistics.total_events)</h3>
                <p>总事件数</p>
            </div>
            <div class="summary-card">
                <h3>$($Statistics.by_severity['CRITICAL'] + $Statistics.by_severity['ERROR'])</h3>
                <p>严重事件</p>
            </div>
            <div class="summary-card">
                <h3>$($Statistics.by_user.Count)</h3>
                <p>涉及用户</p>
            </div>
            <div class="summary-card">
                <h3>$($Statistics.by_event_type.Count)</h3>
                <p>事件类型</p>
            </div>
        </div>

        <div class="section">
            <h2>统计图表</h2>
            <div class="chart-container">
                <div class="chart">
                    <h3>按严重性分布</h3>
"@
    
    # 生成严重性分布图表
    $maxSeverityCount = ($Statistics.by_severity.Values | Measure-Object -Maximum).Maximum
    foreach ($severity in @('CRITICAL', 'ERROR', 'WARNING', 'INFO')) {
        $count = if ($Statistics.by_severity.ContainsKey($severity)) { $Statistics.by_severity[$severity] } else { 0 }
        $percentage = if ($maxSeverityCount -gt 0) { [math]::Round(($count / $maxSeverityCount) * 100) } else { 0 }
        
        $html += @"
                    <div class="bar">
                        <div class="bar-label">$severity</div>
                        <div class="bar-fill" style="width: $percentage%;"></div>
                        <div class="bar-value">$count</div>
                    </div>
"@
    }
    
    $html += @"
                </div>
                <div class="chart">
                    <h3>按事件类型分布</h3>
"@
    
    # 生成事件类型分布图表
    $maxEventTypeCount = ($Statistics.by_event_type.Values | Measure-Object -Maximum).Maximum
    $topEventTypes = $Statistics.by_event_type.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 10
    
    foreach ($eventType in $topEventTypes) {
        $percentage = if ($maxEventTypeCount -gt 0) { [math]::Round(($eventType.Value / $maxEventTypeCount) * 100) } else { 0 }
        
        $html += @"
                    <div class="bar">
                        <div class="bar-label">$($eventType.Key)</div>
                        <div class="bar-fill" style="width: $percentage%;"></div>
                        <div class="bar-value">$($eventType.Value)</div>
                    </div>
"@
    }
    
    $html += @"
                </div>
            </div>
        </div>

        <div class="section">
            <h2>最近事件</h2>
            <table class="events-table">
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>严重性</th>
                        <th>事件类型</th>
                        <th>用户</th>
                        <th>描述</th>
                    </tr>
                </thead>
                <tbody>
"@
    
    # 生成最近事件表格（最多显示50条）
    $recentEvents = $AuditData | Select-Object -First 50
    
    foreach ($event in $recentEvents) {
        $timestamp = [DateTime]::Parse($event.'@timestamp').ToString('MM-dd HH:mm:ss')
        $severityClass = "severity-$($event.severity.ToLower())"
        
        $html += @"
                    <tr>
                        <td>$timestamp</td>
                        <td class="$severityClass">$($event.severity)</td>
                        <td>$($event.event_type)</td>
                        <td>$($event.user)</td>
                        <td>$($event.description)</td>
                    </tr>
"@
    }
    
    $html += @"
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>此报告由ELK安全审计系统自动生成</p>
        </div>
    </div>
</body>
</html>
"@
    
    return $html
}

<#
.SYNOPSIS
    清理过期的审计日志
#>
function Remove-ExpiredAuditLogs {
    param(
        [int]$RetentionDays = 90
    )
    
    Write-Log "清理过期审计日志" "INFO"
    
    try {
        $cutoffDate = (Get-Date).AddDays(-$RetentionDays)
        
        # 清理Elasticsearch中的过期索引
        $indexPattern = "security-audit-*"
        $uri = "$Global:ELASTICSEARCH_URL/_cat/indices/$indexPattern?format=json"
        
        $headers = @{}
        if ($Global:SECURITY_ENABLED) {
            $credentials = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("elastic:$($Global:DefaultPasswords.elastic)"))
            $headers["Authorization"] = "Basic $credentials"
        }
        
        $indices = Invoke-RestMethod -Uri $uri -Method GET -Headers $headers -SkipCertificateCheck
        
        foreach ($index in $indices) {
            # 从索引名称中提取日期
            if ($index.index -match "security-audit-(\d{4})\.(\d{2})") {
                $year = [int]$matches[1]
                $month = [int]$matches[2]
                $indexDate = Get-Date -Year $year -Month $month -Day 1
                
                if ($indexDate -lt $cutoffDate) {
                    Write-Log "删除过期索引: $($index.index)" "INFO"
                    $deleteUri = "$Global:ELASTICSEARCH_URL/$($index.index)"
                    Invoke-RestMethod -Uri $deleteUri -Method DELETE -Headers $headers -SkipCertificateCheck | Out-Null
                }
            }
        }
        
        # 清理本地审计日志文件
        $auditLogPath = Join-Path $Global:ELK_LOGS_PATH "security-audit.json"
        if (Test-Path $auditLogPath) {
            $logFile = Get-Item $auditLogPath
            if ($logFile.LastWriteTime -lt $cutoffDate) {
                Write-Log "删除过期本地审计日志: $auditLogPath" "INFO"
                Remove-Item $auditLogPath -Force
            }
        }
        
        Write-Log "审计日志清理完成" "INFO"
        return $true
    }
    catch {
        Write-Log "清理审计日志失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    导出审计数据
#>
function Export-AuditData {
    param(
        [DateTime]$StartDate = (Get-Date).AddDays(-30),
        [DateTime]$EndDate = (Get-Date),
        [string]$OutputPath = "audit-export.json",
        [string]$Format = "json" # json, csv, xml
    )
    
    Write-Log "导出审计数据" "INFO"
    
    try {
        # 获取审计数据
        $auditData = Get-SecurityAuditData -StartDate $StartDate -EndDate $EndDate
        
        if (-not $auditData -or $auditData.Count -eq 0) {
            Write-Log "没有找到要导出的审计数据" "WARNING"
            return $false
        }
        
        switch ($Format.ToLower()) {
            "json" {
                $auditData | ConvertTo-Json -Depth 10 | Out-File -FilePath $OutputPath -Encoding UTF8
            }
            "csv" {
                $auditData | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
            }
            "xml" {
                $auditData | Export-Clixml -Path $OutputPath
            }
            default {
                throw "不支持的导出格式: $Format"
            }
        }
        
        Write-Log "审计数据已导出: $OutputPath (格式: $Format, 记录数: $($auditData.Count))" "INFO"
        return $true
    }
    catch {
        Write-Log "导出审计数据失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    检查安全合规性
#>
function Test-SecurityCompliance {
    param(
        [string[]]$ComplianceRules = @("password_policy", "access_control", "audit_logging", "encryption")
    )
    
    Write-Log "检查安全合规性" "INFO"
    
    $complianceResults = @{
        "overall_status" = "PASS"
        "checks" = @{}
        "recommendations" = @()
    }
    
    try {
        foreach ($rule in $ComplianceRules) {
            $checkResult = switch ($rule) {
                "password_policy" {
                    Test-PasswordPolicy
                }
                "access_control" {
                    Test-AccessControl
                }
                "audit_logging" {
                    Test-AuditLogging
                }
                "encryption" {
                    Test-EncryptionCompliance
                }
                default {
                    @{ "status" = "SKIP"; "message" = "未知的合规性规则: $rule" }
                }
            }
            
            $complianceResults.checks[$rule] = $checkResult
            
            if ($checkResult.status -eq "FAIL") {
                $complianceResults.overall_status = "FAIL"
                if ($checkResult.recommendation) {
                    $complianceResults.recommendations += $checkResult.recommendation
                }
            }
        }
        
        # 记录合规性检查事件
        Write-SecurityEvent -EventType "COMPLIANCE_CHECK" -Description "安全合规性检查完成" -Severity "INFO" -Details $complianceResults
        
        Write-Log "安全合规性检查完成: $($complianceResults.overall_status)" "INFO"
        return $complianceResults
    }
    catch {
        Write-Log "安全合规性检查失败: $($_.Exception.Message)" "ERROR"
        return @{ "overall_status" = "ERROR"; "error" = $_.Exception.Message }
    }
}

<#
.SYNOPSIS
    检查密码策略合规性
#>
function Test-PasswordPolicy {
    try {
        # 检查默认密码是否已更改
        $defaultPasswords = @("changeme", "password", "admin", "elastic")
        $currentPassword = $Global:DefaultPasswords.elastic
        
        if ($defaultPasswords -contains $currentPassword) {
            return @{
                "status" = "FAIL"
                "message" = "检测到使用默认密码"
                "recommendation" = "请更改所有默认密码为强密码"
            }
        }
        
        # 检查密码强度
        if ($currentPassword.Length -lt 12) {
            return @{
                "status" = "FAIL"
                "message" = "密码长度不足"
                "recommendation" = "密码长度应至少12个字符"
            }
        }
        
        return @{
            "status" = "PASS"
            "message" = "密码策略符合要求"
        }
    }
    catch {
        return @{
            "status" = "ERROR"
            "message" = "密码策略检查失败: $($_.Exception.Message)"
        }
    }
}

<#
.SYNOPSIS
    检查访问控制合规性
#>
function Test-AccessControl {
    try {
        # 检查是否启用了安全功能
        if (-not $Global:SECURITY_ENABLED) {
            return @{
                "status" = "FAIL"
                "message" = "安全功能未启用"
                "recommendation" = "启用ELK Stack的安全功能"
            }
        }
        
        # 检查是否配置了适当的角色
        $roles = Get-ElasticsearchRoles
        if (-not $roles -or $roles.Count -eq 0) {
            return @{
                "status" = "FAIL"
                "message" = "未配置用户角色"
                "recommendation" = "配置适当的用户角色和权限"
            }
        }
        
        return @{
            "status" = "PASS"
            "message" = "访问控制配置正确"
        }
    }
    catch {
        return @{
            "status" = "ERROR"
            "message" = "访问控制检查失败: $($_.Exception.Message)"
        }
    }
}

<#
.SYNOPSIS
    检查审计日志合规性
#>
function Test-AuditLogging {
    try {
        # 检查审计日志是否启用
        $auditLogPath = Join-Path $Global:ELK_LOGS_PATH "security-audit.json"
        if (-not (Test-Path $auditLogPath)) {
            return @{
                "status" = "FAIL"
                "message" = "审计日志文件不存在"
                "recommendation" = "启用审计日志记录"
            }
        }
        
        # 检查最近是否有审计记录
        $recentEvents = Get-SecurityAuditData -StartDate (Get-Date).AddHours(-24) -EndDate (Get-Date)
        if (-not $recentEvents -or $recentEvents.Count -eq 0) {
            return @{
                "status" = "WARNING"
                "message" = "最近24小时内没有审计记录"
                "recommendation" = "检查审计日志配置是否正确"
            }
        }
        
        return @{
            "status" = "PASS"
            "message" = "审计日志配置正确"
        }
    }
    catch {
        return @{
            "status" = "ERROR"
            "message" = "审计日志检查失败: $($_.Exception.Message)"
        }
    }
}

<#
.SYNOPSIS
    检查加密合规性
#>
function Test-EncryptionCompliance {
    try {
        # 检查SSL/TLS是否启用
        if (-not $Global:SECURITY_ENABLED) {
            return @{
                "status" = "FAIL"
                "message" = "SSL/TLS加密未启用"
                "recommendation" = "启用SSL/TLS加密"
            }
        }
        
        # 检查证书是否存在
        $certPath = Join-Path $Global:ELK_CERTS_PATH "ca"
        if (-not (Test-Path $certPath)) {
            return @{
                "status" = "FAIL"
                "message" = "SSL证书不存在"
                "recommendation" = "生成并配置SSL证书"
            }
        }
        
        return @{
            "status" = "PASS"
            "message" = "加密配置符合要求"
        }
    }
    catch {
        return @{
            "status" = "ERROR"
            "message" = "加密合规性检查失败: $($_.Exception.Message)"
        }
    }
}

# 导出函数
Export-ModuleMember -Function *