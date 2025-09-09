#!/usr/bin/env pwsh
<#
.SYNOPSIS
    ELK堆栈安全配置脚本
    
.DESCRIPTION
    该脚本用于配置ELK堆栈的安全设置，包括：
    - Elasticsearch安全配置（X-Pack Security）
    - Kibana认证和授权配置
    - SSL/TLS证书生成和配置
    - 用户和角色管理
    - API密钥管理
    - 安全审计配置
    
.PARAMETER Action
    操作类型：setup, enable, disable, users, roles, certs, audit
    
.PARAMETER Component
    组件名称：all, elasticsearch, kibana, logstash, beats
    
.PARAMETER Username
    用户名（用于用户管理操作）
    
.PARAMETER Password
    密码（用于用户管理操作）
    
.PARAMETER Role
    角色名称（用于角色管理操作）
    
.PARAMETER CertDomain
    证书域名
    
.EXAMPLE
    .\security-setup.ps1 -Action setup -Component all
    设置所有组件的安全配置
    
.EXAMPLE
    .\security-setup.ps1 -Action users -Username "admin" -Password "password123"
    创建管理员用户
    
.EXAMPLE
    .\security-setup.ps1 -Action certs -CertDomain "localhost"
    生成SSL证书
#>

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("setup", "enable", "disable", "users", "roles", "certs", "audit", "reset")]
    [string]$Action,
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("all", "elasticsearch", "kibana", "logstash", "beats")]
    [string]$Component = "all",
    
    [Parameter(Mandatory = $false)]
    [string]$Username,
    
    [Parameter(Mandatory = $false)]
    [string]$Password,
    
    [Parameter(Mandatory = $false)]
    [string]$Role,
    
    [Parameter(Mandatory = $false)]
    [string]$CertDomain = "localhost",
    
    [Parameter(Mandatory = $false)]
    [string]$ConfigPath = "../configs",
    
    [Parameter(Mandatory = $false)]
    [string]$CertPath = "certs",
    
    [Parameter(Mandatory = $false)]
    [switch]$Force,
    
    [Parameter(Mandatory = $false)]
    [switch]$Interactive
)

# 导入安全模块
try {
    . "$PSScriptRoot\security-modules\security-common.ps1"
    . "$PSScriptRoot\security-modules\certificate-manager.ps1"
    . "$PSScriptRoot\security-modules\user-manager.ps1"
    . "$PSScriptRoot\security-modules\elasticsearch-security.ps1"
    . "$PSScriptRoot\security-modules\kibana-security.ps1"
    Write-Host "安全模块加载成功" -ForegroundColor Green
}
catch {
    Write-Host "加载安全模块失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

<#
.SYNOPSIS
    主函数 - 执行安全配置操作
#>
function Main {
    Write-Log "开始执行ELK安全配置操作: $Action" "INFO"
    
    try {
        # 初始化安全配置
        Initialize-SecurityConfig
        
        # 构建参数哈希表
        $Parameters = @{
            Username = $Username
            Password = $Password
            Role = $Role
            Domain = $CertDomain
            ConfigPath = $ConfigPath
            CertPath = $CertPath
            Force = $Force
            Interactive = $Interactive
            ElasticsearchUrl = $script:ElasticsearchUrl
            KibanaUrl = $script:KibanaUrl
        }
        
        switch ($Action.ToLower()) {
            "setup" {
                return Initialize-FullSecuritySetup -Component $Component -Parameters $Parameters
            }
            "enable" {
                return Enable-SecurityFeatures -Component $Component -Parameters $Parameters
            }
            "disable" {
                return Disable-SecurityFeatures -Component $Component -Parameters $Parameters
            }
            "reset" {
                return Reset-SecurityConfiguration -Component $Component -Parameters $Parameters
            }
            "certs" {
                $Parameters.Action = "generate"
                return Manage-Certificates -Parameters $Parameters
            }
            "users" {
                if ($Username -and $Password) {
                    $Parameters.Action = "create"
                } elseif ($Username) {
                    $Parameters.Action = "info"
                } else {
                    $Parameters.Action = "list"
                }
                return Manage-Users -Parameters $Parameters
            }
            "roles" {
                $Parameters.Action = if ($Role) { "info" } else { "list" }
                return Manage-Permissions -Parameters $Parameters
            }
            "audit" {
                return Generate-SecurityAudit -Parameters $Parameters
            }
            default {
                Write-Log "未知操作: $Action" "ERROR"
                Show-Usage
                return $false
            }
        }
        
        Write-Log "ELK安全配置操作完成" "INFO"
        return $true
    }
    catch {
        Write-Log "安全配置操作失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    初始化安全配置
#>
function Initialize-SecurityConfig {
    Write-Log "初始化安全配置" "INFO"
    
    # 创建必要的目录
    $directories = @(
        "logs",
        "certs",
        "security-modules",
        "config/security",
        "backup",
        "policies"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Log "创建目录: $dir" "DEBUG"
        }
    }
    
    # 设置全局变量
    $script:LogPath = "logs/security-setup.log"
    $script:ElasticsearchUrl = "http://localhost:9200"
    $script:KibanaUrl = "http://localhost:5601"
    $script:SecurityConfig = @{}
    $Global:ELK_SECURITY_PATH = $PWD.Path
    $Global:ELK_CERTS_PATH = Join-Path $PWD.Path "certs"
    $Global:ELK_CONFIG_PATH = Join-Path $PWD.Path "config"
    $Global:ELK_LOGS_PATH = Join-Path $PWD.Path "logs"
    
    Write-Log "安全配置初始化完成" "INFO"
    return $true
}

<#
.SYNOPSIS
    完整安全设置
#>
function Initialize-FullSecuritySetup {
    param(
        [string]$Component = "all",
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "开始完整安全设置" "INFO"
    
    try {
        # 1. 初始化基础配置
        if (-not (Initialize-SecurityConfiguration)) {
            throw "基础配置初始化失败"
        }
        
        # 2. 生成证书
        Write-Log "生成SSL/TLS证书" "INFO"
        if (-not (New-SecurityCertificates -Domain $Parameters.Domain -Force:$Parameters.Force)) {
            throw "证书生成失败"
        }
        
        # 3. 初始化用户和角色
        Write-Log "初始化用户和角色" "INFO"
        $createdUsers = Initialize-DefaultUsersAndRoles -ElasticsearchUrl $Parameters.ElasticsearchUrl
        
        # 4. 配置组件安全
        switch ($Component.ToLower()) {
            "all" {
                Setup-ElasticsearchSecurity -Parameters $Parameters
                Setup-KibanaSecurity -Parameters $Parameters
                Setup-LogstashSecurity -Parameters $Parameters
                Setup-BeatsSecurity -Parameters $Parameters
            }
            "elasticsearch" {
                Setup-ElasticsearchSecurity -Parameters $Parameters
            }
            "kibana" {
                Setup-KibanaSecurity -Parameters $Parameters
            }
            "logstash" {
                Setup-LogstashSecurity -Parameters $Parameters
            }
            "beats" {
                Setup-BeatsSecurity -Parameters $Parameters
            }
        }
        
        # 5. 生成配置文件
        Generate-SecurityConfigurations -Parameters $Parameters
        
        Write-Log "完整安全设置完成" "INFO"
        return $true
    }
    catch {
        Write-Log "完整安全设置失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    启用安全功能
#>
function Enable-SecurityFeatures {
    param(
        [string]$Component = "all",
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "启用安全功能: $Component" "INFO"
    
    try {
        switch ($Component.ToLower()) {
            "all" {
                Enable-ElasticsearchSecurity
                Enable-KibanaSecurity
                Enable-LogstashSecurity
            }
            "elasticsearch" {
                Enable-ElasticsearchSecurity
            }
            "kibana" {
                Enable-KibanaSecurity
            }
            "logstash" {
                Enable-LogstashSecurity
            }
        }
        
        Write-Log "安全功能启用完成" "INFO"
        return $true
    }
    catch {
        Write-Log "启用安全功能失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    禁用安全功能
#>
function Disable-SecurityFeatures {
    param(
        [string]$Component = "all",
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "禁用安全功能: $Component" "WARN"
    
    try {
        switch ($Component.ToLower()) {
            "all" {
                Disable-ElasticsearchSecurity
                Disable-KibanaSecurity
                Disable-LogstashSecurity
            }
            "elasticsearch" {
                Disable-ElasticsearchSecurity
            }
            "kibana" {
                Disable-KibanaSecurity
            }
            "logstash" {
                Disable-LogstashSecurity
            }
        }
        
        Write-Log "安全功能禁用完成" "INFO"
        return $true
    }
    catch {
        Write-Log "禁用安全功能失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    重置安全配置
#>
function Reset-SecurityConfiguration {
    param(
        [string]$Component = "all",
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "重置安全配置: $Component" "WARN"
    
    if (-not $Parameters.Force) {
        $confirmation = Read-Host "这将删除所有安全配置，是否继续？(y/N)"
        if ($confirmation -ne "y" -and $confirmation -ne "Y") {
            Write-Log "操作已取消" "INFO"
            return $false
        }
    }
    
    try {
        # 备份当前配置
        $backupPath = "backup\security-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
        
        if (Test-Path "config") {
            Copy-Item -Path "config" -Destination $backupPath -Recurse -Force
        }
        
        # 删除配置文件
        $configFiles = @(
            "config\elasticsearch\elasticsearch.yml",
            "config\kibana\kibana.yml",
            "config\logstash\logstash.yml"
        )
        
        foreach ($file in $configFiles) {
            if (Test-Path $file) {
                Remove-Item $file -Force
                Write-Log "删除配置文件: $file" "DEBUG"
            }
        }
        
        # 删除证书（可选）
        if ($Parameters.RemoveCertificates) {
            if (Test-Path "certs") {
                Remove-Item "certs" -Recurse -Force
                Write-Log "删除证书目录" "DEBUG"
            }
        }
        
        Write-Log "安全配置重置完成，备份保存在: $backupPath" "INFO"
        return $true
    }
    catch {
        Write-Log "重置安全配置失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    管理证书
#>
function Manage-Certificates {
    param(
        [hashtable]$Parameters = @{}
    )
    
    $action = $Parameters.Action
    
    switch ($action.ToLower()) {
        "generate" {
            return New-SecurityCertificates -Domain $Parameters.Domain -Force:$Parameters.Force
        }
        "verify" {
            return Test-Certificate -CertificatePath $Parameters.CertificatePath
        }
        "info" {
            return Get-CertificateInfo -CertificatePath $Parameters.CertificatePath
        }
        default {
            Write-Log "未知证书操作: $action" "ERROR"
            return $false
        }
    }
}

<#
.SYNOPSIS
    管理用户
#>
function Manage-Users {
    param(
        [hashtable]$Parameters = @{}
    )
    
    $action = $Parameters.Action
    
    switch ($action.ToLower()) {
        "create" {
            return New-ElasticsearchUser -Username $Parameters.Username -Password $Parameters.Password -Roles $Parameters.Role -FullName $Parameters.FullName -Email $Parameters.Email
        }
        "delete" {
            return Remove-ElasticsearchUser -Username $Parameters.Username
        }
        "reset-password" {
            return Reset-ElasticsearchUserPassword -Username $Parameters.Username
        }
        "list" {
            return Get-ElasticsearchUsers
        }
        "info" {
            return Get-ElasticsearchUser -Username $Parameters.Username
        }
        "test-auth" {
            return Test-ElasticsearchUserAuth -Username $Parameters.Username -Password $Parameters.Password
        }
        default {
            Write-Log "未知用户操作: $action" "ERROR"
            return $false
        }
    }
}

<#
.SYNOPSIS
    管理权限
#>
function Manage-Permissions {
    param(
        [hashtable]$Parameters = @{}
    )
    
    $action = $Parameters.Action
    
    switch ($action.ToLower()) {
        "set-index" {
            return Set-IndexPermissions -IndexPattern $Parameters.IndexPattern -Users $Parameters.Users -Roles $Parameters.Roles -Privileges $Parameters.Privileges
        }
        "set-cluster" {
            return Set-ClusterPermissions -RoleName $Parameters.RoleName -ClusterPrivileges $Parameters.ClusterPrivileges
        }
        "test" {
            return Test-UserPermissions -Username $Parameters.Username -IndexName $Parameters.IndexName -RequiredPrivileges $Parameters.RequiredPrivileges
        }
        "report" {
            return Get-PermissionsReport -OutputPath $Parameters.OutputPath
        }
        "cleanup" {
            return Remove-ExpiredPermissions -DaysOld $Parameters.DaysOld
        }
        "list" {
            return Get-AllElkRoles
        }
        "info" {
            return Get-ElkRole -RoleName $Parameters.Role
        }
        default {
            Write-Log "未知权限操作: $action" "ERROR"
            return $false
        }
    }
}

<#
.SYNOPSIS
    生成安全审计报告
#>
function Generate-SecurityAudit {
    param(
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "生成安全审计报告" "INFO"
    
    try {
        # 创建审计目录
        if (-not (Test-Path "audit")) {
            New-Item -ItemType Directory -Path "audit" -Force | Out-Null
        }
        
        # 生成权限报告
        Get-PermissionsReport -OutputPath "audit\permissions-report.html"
        
        # 检查证书状态
        $certStatus = @()
        $certFiles = Get-ChildItem -Path "certs" -Recurse -Filter "*.pem" -ErrorAction SilentlyContinue
        
        foreach ($cert in $certFiles) {
            $certInfo = Get-CertificateInfo -CertificatePath $cert.FullName
            $certStatus += $certInfo
        }
        
        # 生成审计报告
        $auditReport = @{
            GeneratedAt = Get-Date
            CertificateStatus = $certStatus
            SecurityConfiguration = $Global:SecurityConfig
        }
        
        $auditPath = "audit\security-audit-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
        $auditReport | ConvertTo-Json -Depth 4 | Out-File -FilePath $auditPath -Encoding UTF8
        
        Write-Log "安全审计报告已生成: $auditPath" "INFO"
        return $true
    }
    catch {
        Write-Log "生成安全审计报告失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    显示使用说明
#>
function Show-Usage {
    Write-Host @"

ELK安全配置脚本使用说明
========================

基本语法:
  .\security-setup.ps1 -Action <操作> [-Component <组件>] [其他参数]

操作 (Action):
  setup       - 完整安全设置
  enable      - 启用安全功能
  disable     - 禁用安全功能
  reset       - 重置安全配置
  certs       - 证书管理
  users       - 用户管理
  roles       - 角色管理
  audit       - 生成审计报告

组件 (Component):
  all         - 所有组件 (默认)
  elasticsearch- Elasticsearch
  kibana      - Kibana
  logstash    - Logstash
  beats       - Beats

示例:
  # 完整安全设置
  .\security-setup.ps1 -Action setup
  
  # 生成证书
  .\security-setup.ps1 -Action certs -CertDomain localhost
  
  # 创建用户
  .\security-setup.ps1 -Action users -Username testuser -Password testpass
  
  # 生成审计报告
  .\security-setup.ps1 -Action audit

"@ -ForegroundColor Cyan
}

# 执行主函数
if ($MyInvocation.InvocationName -ne '.') {
    $result = Main
    exit ($result ? 0 : 1)
}