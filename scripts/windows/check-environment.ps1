<#
.SYNOPSIS
    AIOps平台环境检查脚本 (PowerShell)

.DESCRIPTION
    本脚本用于检查系统环境是否满足AIOps平台的部署要求，包括硬件资源、软件依赖、网络配置等。

.PARAMETER DeploymentType
    部署类型：docker 或 kubernetes

.PARAMETER Detailed
    显示详细检查信息

.PARAMETER Fix
    尝试自动修复发现的问题

.EXAMPLE
    .\check-environment.ps1 -DeploymentType docker
    .\check-environment.ps1 -DeploymentType kubernetes -Detailed -Fix

.NOTES
    版本: 1.0.0
    作者: AIOps Team
    创建日期: 2024-01-01
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("docker", "kubernetes", "all")]
    [string]$DeploymentType = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$Detailed,
    
    [Parameter(Mandatory=$false)]
    [switch]$Fix
)

# 设置错误处理
$ErrorActionPreference = "Continue"

# 全局变量
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:CheckResults = @()
$script:FixActions = @()

# 检查结果类
class CheckResult {
    [string]$Category
    [string]$Item
    [string]$Status  # PASS, WARN, FAIL
    [string]$Message
    [string]$Recommendation
    [string]$FixAction
    
    CheckResult([string]$category, [string]$item, [string]$status, [string]$message, [string]$recommendation, [string]$fixAction = "") {
        $this.Category = $category
        $this.Item = $item
        $this.Status = $status
        $this.Message = $message
        $this.Recommendation = $recommendation
        $this.FixAction = $fixAction
    }
}

# 添加检查结果
function Add-CheckResult {
    param(
        [string]$Category,
        [string]$Item,
        [string]$Status,
        [string]$Message,
        [string]$Recommendation = "",
        [string]$FixAction = ""
    )
    
    $result = [CheckResult]::new($Category, $Item, $Status, $Message, $Recommendation, $FixAction)
    $script:CheckResults += $result
    
    # 实时输出
    $color = switch ($Status) {
        "PASS" { "Green" }
        "WARN" { "Yellow" }
        "FAIL" { "Red" }
        default { "White" }
    }
    
    Write-Host "[$Status] $Category - ${Item}: $Message" -ForegroundColor $color
    
    if ($Detailed -and $Recommendation) {
        Write-Host "    建议: $Recommendation" -ForegroundColor Gray
    }
}

# 检查系统信息
function Test-SystemInfo {
    Write-Host "`n=== 系统信息检查 ===" -ForegroundColor Cyan
    
    try {
        $os = Get-WmiObject -Class Win32_OperatingSystem
        $computer = Get-WmiObject -Class Win32_ComputerSystem
        
        Add-CheckResult "系统" "操作系统" "PASS" "$($os.Caption) $($os.Version)" ""
        Add-CheckResult "系统" "计算机名" "PASS" "$($computer.Name)" ""
        Add-CheckResult "系统" "域/工作组" "PASS" "$(if($computer.PartOfDomain) { $computer.Domain } else { $computer.Workgroup })" ""
        
        # 检查系统架构
        if ($os.OSArchitecture -eq "64-bit") {
            Add-CheckResult "系统" "架构" "PASS" "64位系统" ""
        } else {
            Add-CheckResult "系统" "架构" "WARN" "32位系统" "推荐使用64位系统以获得更好的性能"
        }
        
        # 检查系统版本
        $version = [System.Environment]::OSVersion.Version
        if ($version.Major -ge 10) {
            Add-CheckResult "系统" "版本兼容性" "PASS" "Windows 10/11 或 Windows Server 2016+" ""
        } elseif ($version.Major -eq 6 -and $version.Minor -ge 1) {
            Add-CheckResult "系统" "版本兼容性" "WARN" "Windows 7/8 或 Windows Server 2008+" "推荐升级到Windows 10或更新版本"
        } else {
            Add-CheckResult "系统" "版本兼容性" "FAIL" "不支持的Windows版本" "需要Windows 7或更新版本"
        }
        
    } catch {
        Add-CheckResult "系统" "信息获取" "FAIL" "无法获取系统信息: $($_.Exception.Message)" "检查WMI服务是否正常"
    }
}

# 检查硬件资源
function Test-HardwareResources {
    Write-Host "`n=== 硬件资源检查 ===" -ForegroundColor Cyan
    
    try {
        # CPU检查
        $cpu = Get-WmiObject -Class Win32_Processor
        $totalCores = ($cpu | Measure-Object -Property NumberOfCores -Sum).Sum
        $totalLogicalProcessors = ($cpu | Measure-Object -Property NumberOfLogicalProcessors -Sum).Sum
        
        if ($totalCores -ge 8) {
            Add-CheckResult "硬件" "CPU核心" "PASS" "$totalCores 核心 / $totalLogicalProcessors 逻辑处理器" ""
        } elseif ($totalCores -ge 4) {
            Add-CheckResult "硬件" "CPU核心" "WARN" "$totalCores 核心 / $totalLogicalProcessors 逻辑处理器" "推荐8核心或更多以获得最佳性能"
        } else {
            Add-CheckResult "硬件" "CPU核心" "FAIL" "$totalCores 核心 / $totalLogicalProcessors 逻辑处理器" "至少需要4核心CPU"
        }
        
        # 内存检查
        $memory = Get-WmiObject -Class Win32_ComputerSystem
        $totalMemoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
        
        if ($totalMemoryGB -ge 32) {
            Add-CheckResult "硬件" "内存" "PASS" "${totalMemoryGB}GB" ""
        } elseif ($totalMemoryGB -ge 16) {
            Add-CheckResult "硬件" "内存" "WARN" "${totalMemoryGB}GB" "推荐32GB或更多内存以支持大规模部署"
        } elseif ($totalMemoryGB -ge 8) {
            Add-CheckResult "硬件" "内存" "WARN" "${totalMemoryGB}GB" "推荐16GB或更多内存"
        } else {
            Add-CheckResult "硬件" "内存" "FAIL" "${totalMemoryGB}GB" "至少需要8GB内存"
        }
        
        # 磁盘空间检查
        $systemDrive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DriveType=3 AND DeviceID='C:'"
        $freeSpaceGB = [math]::Round($systemDrive.FreeSpace / 1GB, 2)
        $totalSpaceGB = [math]::Round($systemDrive.Size / 1GB, 2)
        
        if ($freeSpaceGB -ge 200) {
            Add-CheckResult "硬件" "磁盘空间" "PASS" "可用: ${freeSpaceGB}GB / 总计: ${totalSpaceGB}GB" ""
        } elseif ($freeSpaceGB -ge 100) {
            Add-CheckResult "硬件" "磁盘空间" "WARN" "可用: ${freeSpaceGB}GB / 总计: ${totalSpaceGB}GB" "推荐至少200GB可用空间"
        } elseif ($freeSpaceGB -ge 50) {
            Add-CheckResult "硬件" "磁盘空间" "WARN" "可用: ${freeSpaceGB}GB / 总计: ${totalSpaceGB}GB" "推荐至少100GB可用空间"
        } else {
            Add-CheckResult "硬件" "磁盘空间" "FAIL" "可用: ${freeSpaceGB}GB / 总计: ${totalSpaceGB}GB" "至少需要50GB可用空间"
        }
        
        # 检查SSD
        $disks = Get-PhysicalDisk
        $hasSSD = $disks | Where-Object { $_.MediaType -eq "SSD" }
        
        if ($hasSSD) {
            Add-CheckResult "硬件" "存储类型" "PASS" "检测到SSD存储" ""
        } else {
            Add-CheckResult "硬件" "存储类型" "WARN" "未检测到SSD存储" "推荐使用SSD以获得更好的I/O性能"
        }
        
    } catch {
        Add-CheckResult "硬件" "资源检查" "FAIL" "无法获取硬件信息: $($_.Exception.Message)" "检查系统权限和WMI服务"
    }
}

# 检查网络配置
function Test-NetworkConfiguration {
    Write-Host "`n=== 网络配置检查 ===" -ForegroundColor Cyan
    
    try {
        # 检查网络适配器
        $adapters = Get-NetAdapter | Where-Object { $_.Status -eq "Up" }
        
        if ($adapters.Count -gt 0) {
            Add-CheckResult "网络" "网络适配器" "PASS" "$($adapters.Count) 个活动适配器" ""
            
            foreach ($adapter in $adapters) {
                if ($Detailed) {
                    $speed = if ($adapter.LinkSpeed) { "$([math]::Round($adapter.LinkSpeed / 1GB, 1))Gbps" } else { "未知" }
                    Add-CheckResult "网络" "适配器-$($adapter.Name)" "PASS" "速度: $speed" ""
                }
            }
        } else {
            Add-CheckResult "网络" "网络适配器" "FAIL" "没有活动的网络适配器" "检查网络连接"
        }
        
        # 检查DNS配置
        $dnsServers = Get-DnsClientServerAddress | Where-Object { $_.AddressFamily -eq 2 -and $_.ServerAddresses.Count -gt 0 }
        
        if ($dnsServers) {
            Add-CheckResult "网络" "DNS配置" "PASS" "DNS服务器已配置" ""
        } else {
            Add-CheckResult "网络" "DNS配置" "WARN" "DNS配置可能有问题" "检查DNS服务器设置"
        }
        
        # 检查防火墙状态
        $firewallProfiles = Get-NetFirewallProfile
        $enabledProfiles = $firewallProfiles | Where-Object { $_.Enabled -eq $true }
        
        if ($enabledProfiles.Count -gt 0) {
            Add-CheckResult "网络" "Windows防火墙" "WARN" "$($enabledProfiles.Count) 个配置文件已启用" "可能需要配置防火墙规则以允许AIOps服务通信"
        } else {
            Add-CheckResult "网络" "Windows防火墙" "PASS" "防火墙已禁用" ""
        }
        
        # 检查端口占用
        $requiredPorts = @(80, 443, 3000, 5601, 9090, 9200, 6379, 5432)
        $occupiedPorts = @()
        
        foreach ($port in $requiredPorts) {
            $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
            if ($connection) {
                $occupiedPorts += $port
            }
        }
        
        if ($occupiedPorts.Count -eq 0) {
            Add-CheckResult "网络" "端口可用性" "PASS" "所有必需端口都可用" ""
        } else {
            Add-CheckResult "网络" "端口可用性" "WARN" "以下端口被占用: $($occupiedPorts -join ', ')" "停止占用这些端口的服务或修改AIOps配置"
        }
        
    } catch {
        Add-CheckResult "网络" "配置检查" "FAIL" "网络检查失败: $($_.Exception.Message)" "检查网络服务和权限"
    }
}

# 检查Docker环境
function Test-DockerEnvironment {
    Write-Host "`n=== Docker环境检查 ===" -ForegroundColor Cyan
    
    try {
        # 检查Docker是否安装
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $versionMatch = $dockerVersion -match "Docker version ([\d\.]+)"
            if ($versionMatch) {
                $currentVersion = $matches[1]
                try {
                    # 尝试解析版本号，如果失败则只检查主版本号
                    $versionParts = $currentVersion.Split('.')
                    $majorVersion = [int]$versionParts[0]
                    $minorVersion = if ($versionParts.Length -gt 1) { [int]$versionParts[1] } else { 0 }
                    
                    if ($majorVersion -gt 20 -or ($majorVersion -eq 20 -and $minorVersion -ge 10)) {
                        Add-CheckResult "Docker" "版本" "PASS" "$dockerVersion" ""
                    } else {
                        Add-CheckResult "Docker" "版本" "WARN" "$dockerVersion" "推荐升级到20.10.0或更新版本" "docker update"
                    }
                } catch {
                    # 如果版本解析失败，但Docker能运行，则标记为通过
                    Add-CheckResult "Docker" "版本" "PASS" "$dockerVersion (版本解析异常，但Docker可用)" ""
                }
            } else {
                Add-CheckResult "Docker" "版本" "WARN" "无法解析版本信息" "检查Docker安装"
            }
        } else {
            Add-CheckResult "Docker" "安装" "FAIL" "Docker未安装或不在PATH中" "安装Docker Desktop" "Install-Docker"
        }
        
        # 检查Docker服务状态
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -eq 0) {
            Add-CheckResult "Docker" "服务状态" "PASS" "Docker服务运行正常" ""
            
            # 检查Docker资源配置
            $memoryMatch = $dockerInfo | Select-String -Pattern "^\s*Total Memory: ([\d\.]+)GiB"
            if ($memoryMatch) {
                try {
                    $memoryValue = $memoryMatch.Matches[0].Groups[1].Value
                    $dockerMemory = [math]::Round([double]$memoryValue, 1)
                    if ($dockerMemory -ge 8) {
                        Add-CheckResult "Docker" "内存配置" "PASS" "${dockerMemory}GB" ""
                    } else {
                        Add-CheckResult "Docker" "内存配置" "WARN" "${dockerMemory}GB" "推荐分配至少8GB内存给Docker" "Increase-DockerMemory"
                    }
                } catch {
                    Add-CheckResult "Docker" "内存配置" "WARN" "无法解析内存信息: $memoryValue" "检查Docker配置"
                }
            } else {
                Add-CheckResult "Docker" "内存配置" "WARN" "无法获取Docker内存信息" "检查Docker配置"
            }
            
            $cpuMatch = $dockerInfo | Select-String -Pattern "^\s*CPUs: (\d+)"
            if ($cpuMatch) {
                try {
                    $cpuValue = $cpuMatch.Matches[0].Groups[1].Value
                    $dockerCPUs = [int]$cpuValue
                    if ($dockerCPUs -ge 4) {
                        Add-CheckResult "Docker" "CPU配置" "PASS" "${dockerCPUs} CPUs" ""
                    } else {
                        Add-CheckResult "Docker" "CPU配置" "WARN" "${dockerCPUs} CPUs" "推荐分配至少4个CPU给Docker" "Increase-DockerCPU"
                    }
                } catch {
                    Add-CheckResult "Docker" "CPU配置" "WARN" "无法解析CPU信息: $cpuValue" "检查Docker配置"
                }
            } else {
                Add-CheckResult "Docker" "CPU配置" "WARN" "无法获取Docker CPU信息" "检查Docker配置"
            }
            
        } else {
            Add-CheckResult "Docker" "服务状态" "FAIL" "Docker服务未运行" "启动Docker Desktop" "Start-Docker"
        }
        
        # 检查Docker Compose
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Add-CheckResult "Docker" "Docker Compose" "PASS" "$composeVersion" ""
        } else {
            Add-CheckResult "Docker" "Docker Compose" "FAIL" "Docker Compose未安装" "安装Docker Compose" "Install-DockerCompose"
        }
        
    } catch {
        Add-CheckResult "Docker" "环境检查" "FAIL" "Docker检查失败: $($_.Exception.Message)" "检查Docker安装和配置"
    }
}

# 检查Kubernetes环境
function Test-KubernetesEnvironment {
    Write-Host "`n=== Kubernetes环境检查 ===" -ForegroundColor Cyan
    
    try {
        # 检查kubectl
        $kubectlVersion = kubectl version --client --short 2>$null
        if ($LASTEXITCODE -eq 0) {
            Add-CheckResult "Kubernetes" "kubectl" "PASS" "$kubectlVersion" ""
        } else {
            Add-CheckResult "Kubernetes" "kubectl" "FAIL" "kubectl未安装" "安装kubectl" "Install-Kubectl"
            return
        }
        
        # 检查集群连接
        $clusterInfo = kubectl cluster-info 2>$null
        if ($LASTEXITCODE -eq 0) {
            Add-CheckResult "Kubernetes" "集群连接" "PASS" "集群连接正常" ""
            
            # 检查节点状态
            $nodes = kubectl get nodes -o json 2>$null | ConvertFrom-Json
            if ($nodes -and $nodes.items) {
                $readyNodes = 0
                $totalNodes = $nodes.items.Count
                
                foreach ($node in $nodes.items) {
                    $conditions = $node.status.conditions | Where-Object { $_.type -eq "Ready" }
                    if ($conditions -and $conditions.status -eq "True") {
                        $readyNodes++
                    }
                }
                
                if ($readyNodes -eq $totalNodes) {
                    Add-CheckResult "Kubernetes" "节点状态" "PASS" "$readyNodes/$totalNodes 节点就绪" ""
                } else {
                    Add-CheckResult "Kubernetes" "节点状态" "WARN" "$readyNodes/$totalNodes 节点就绪" "检查未就绪的节点"
                }
            }
            
            # 检查集群资源
            $nodeMetrics = kubectl top nodes --no-headers 2>$null
            if ($LASTEXITCODE -eq 0) {
                Add-CheckResult "Kubernetes" "资源监控" "PASS" "metrics-server可用" ""
            } else {
                Add-CheckResult "Kubernetes" "资源监控" "WARN" "metrics-server不可用" "安装metrics-server以启用资源监控" "Install-MetricsServer"
            }
            
        } else {
            Add-CheckResult "Kubernetes" "集群连接" "FAIL" "无法连接到集群" "检查kubeconfig配置" "Configure-Kubeconfig"
        }
        
        # 检查Helm
        $helmVersion = helm version --short 2>$null
        if ($LASTEXITCODE -eq 0) {
            $versionMatch = $helmVersion -match "v([\d\.]+)"
            if ($versionMatch) {
                $currentVersion = $matches[1]
                if ([version]$currentVersion -ge [version]"3.2.0") {
                    Add-CheckResult "Kubernetes" "Helm" "PASS" "$helmVersion" ""
                } else {
                    Add-CheckResult "Kubernetes" "Helm" "WARN" "$helmVersion" "推荐升级到3.2.0或更新版本" "Update-Helm"
                }
            }
        } else {
            Add-CheckResult "Kubernetes" "Helm" "FAIL" "Helm未安装" "安装Helm" "Install-Helm"
        }
        
    } catch {
        Add-CheckResult "Kubernetes" "环境检查" "FAIL" "Kubernetes检查失败: $($_.Exception.Message)" "检查Kubernetes配置"
    }
}

# 检查PowerShell环境
function Test-PowerShellEnvironment {
    Write-Host "`n=== PowerShell环境检查 ===" -ForegroundColor Cyan
    
    try {
        # 检查PowerShell版本
        $psVersion = $PSVersionTable.PSVersion
        
        if ($psVersion.Major -ge 7) {
            Add-CheckResult "PowerShell" "版本" "PASS" "PowerShell $psVersion" ""
        } elseif ($psVersion.Major -eq 5 -and $psVersion.Minor -ge 1) {
            Add-CheckResult "PowerShell" "版本" "WARN" "PowerShell $psVersion" "推荐升级到PowerShell 7" "Install-PowerShell7"
        } else {
            Add-CheckResult "PowerShell" "版本" "FAIL" "PowerShell $psVersion" "需要PowerShell 5.1或更新版本"
        }
        
        # 检查执行策略
        $executionPolicy = Get-ExecutionPolicy
        
        if ($executionPolicy -in @("RemoteSigned", "Unrestricted", "Bypass")) {
            Add-CheckResult "PowerShell" "执行策略" "PASS" "$executionPolicy" ""
        } else {
            Add-CheckResult "PowerShell" "执行策略" "WARN" "$executionPolicy" "可能需要更改执行策略以运行脚本" "Set-ExecutionPolicy RemoteSigned"
        }
        
        # 检查必需模块
        $requiredModules = @("PSYaml", "powershell-yaml")
        
        foreach ($module in $requiredModules) {
            $installedModule = Get-Module -ListAvailable -Name $module -ErrorAction SilentlyContinue
            
            if ($installedModule) {
                Add-CheckResult "PowerShell" "模块-$module" "PASS" "已安装" ""
            } else {
                Add-CheckResult "PowerShell" "模块-$module" "WARN" "未安装" "安装模块以支持YAML处理" "Install-Module $module"
            }
        }
        
    } catch {
        Add-CheckResult "PowerShell" "环境检查" "FAIL" "PowerShell检查失败: $($_.Exception.Message)" "检查PowerShell配置"
    }
}

# 自动修复功能
function Invoke-AutoFix {
    Write-Host "`n=== 自动修复 ===" -ForegroundColor Cyan
    
    $fixableIssues = $script:CheckResults | Where-Object { $_.Status -in @("WARN", "FAIL") -and $_.FixAction }
    
    if ($fixableIssues.Count -eq 0) {
        Write-Host "没有可自动修复的问题" -ForegroundColor Green
        return
    }
    
    Write-Host "发现 $($fixableIssues.Count) 个可修复的问题:" -ForegroundColor Yellow
    
    foreach ($issue in $fixableIssues) {
        Write-Host "修复: $($issue.Category) - $($issue.Item)" -ForegroundColor Yellow
        
        try {
            switch ($issue.FixAction) {
                "Install-Docker" {
                    Write-Host "  正在下载Docker Desktop安装程序..." -ForegroundColor Gray
                    $url = "https://desktop.docker.com/win/stable/Docker%20Desktop%20Installer.exe"
                    $output = "$env:TEMP\DockerDesktopInstaller.exe"
                    Invoke-WebRequest -Uri $url -OutFile $output
                    Write-Host "  请手动运行安装程序: $output" -ForegroundColor Gray
                }
                
                "Start-Docker" {
                    Write-Host "  正在启动Docker Desktop..." -ForegroundColor Gray
                    Start-Process "Docker Desktop" -ErrorAction SilentlyContinue
                }
                
                "Install-Kubectl" {
                    Write-Host "  正在安装kubectl..." -ForegroundColor Gray
                    if (Get-Command choco -ErrorAction SilentlyContinue) {
                        choco install kubernetes-cli -y
                    } else {
                        Write-Host "  请手动安装kubectl或先安装Chocolatey" -ForegroundColor Gray
                    }
                }
                
                "Install-Helm" {
                    Write-Host "  正在安装Helm..." -ForegroundColor Gray
                    if (Get-Command choco -ErrorAction SilentlyContinue) {
                        choco install kubernetes-helm -y
                    } else {
                        Write-Host "  请手动安装Helm或先安装Chocolatey" -ForegroundColor Gray
                    }
                }
                
                "Install-PowerShell7" {
                    Write-Host "  正在安装PowerShell 7..." -ForegroundColor Gray
                    if (Get-Command winget -ErrorAction SilentlyContinue) {
                        winget install Microsoft.PowerShell
                    } else {
                        Write-Host "  请从Microsoft Store或GitHub安装PowerShell 7" -ForegroundColor Gray
                    }
                }
                
                default {
                    if ($issue.FixAction.StartsWith("Install-Module")) {
                        $moduleName = $issue.FixAction.Split(" ")[1]
                        Write-Host "  正在安装模块: $moduleName" -ForegroundColor Gray
                        Install-Module -Name $moduleName -Force -AllowClobber -Scope CurrentUser
                    } else {
                        Write-Host "  执行: $($issue.FixAction)" -ForegroundColor Gray
                        Invoke-Expression $issue.FixAction
                    }
                }
            }
            
            Write-Host "  ✓ 修复完成" -ForegroundColor Green
            
        } catch {
            Write-Host "  ✗ 修复失败: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# 生成报告
function New-Report {
    Write-Host "`n=== 检查报告 ===" -ForegroundColor Cyan
    
    $passCount = ($script:CheckResults | Where-Object { $_.Status -eq "PASS" }).Count
    $warnCount = ($script:CheckResults | Where-Object { $_.Status -eq "WARN" }).Count
    $failCount = ($script:CheckResults | Where-Object { $_.Status -eq "FAIL" }).Count
    $totalCount = $script:CheckResults.Count
    
    Write-Host "检查项目总数: $totalCount" -ForegroundColor White
    Write-Host "通过: $passCount" -ForegroundColor Green
    Write-Host "警告: $warnCount" -ForegroundColor Yellow
    Write-Host "失败: $failCount" -ForegroundColor Red
    
    # 按类别分组显示
    $categories = $script:CheckResults | Group-Object Category
    
    foreach ($category in $categories) {
        Write-Host "`n--- $($category.Name) ---" -ForegroundColor Magenta
        
        foreach ($result in $category.Group) {
            $color = switch ($result.Status) {
                "PASS" { "Green" }
                "WARN" { "Yellow" }
                "FAIL" { "Red" }
            }
            
            Write-Host "  [$($result.Status)] $($result.Item): $($result.Message)" -ForegroundColor $color
            
            if ($result.Status -ne "PASS" -and $result.Recommendation) {
                Write-Host "    建议: $($result.Recommendation)" -ForegroundColor Gray
            }
        }
    }
    
    # 总体评估
    Write-Host "`n=== 总体评估 ===" -ForegroundColor Cyan
    
    if ($failCount -eq 0 -and $warnCount -eq 0) {
        Write-Host "✓ 系统环境完全满足AIOps平台部署要求" -ForegroundColor Green
    } elseif ($failCount -eq 0) {
        Write-Host "⚠ 系统环境基本满足要求，但有一些建议改进的地方" -ForegroundColor Yellow
    } else {
        Write-Host "✗ 系统环境存在问题，需要解决后才能部署" -ForegroundColor Red
    }
    
    # 保存报告到文件
    $reportPath = Join-Path $script:ProjectRoot "logs\environment-check-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $reportData = @{
        Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        DeploymentType = $DeploymentType
        Summary = @{
            Total = $totalCount
            Pass = $passCount
            Warn = $warnCount
            Fail = $failCount
        }
        Results = $script:CheckResults
    }
    
    # 确保日志目录存在
    $logDir = Split-Path $reportPath
    if (!(Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    $reportData | ConvertTo-Json -Depth 10 | Set-Content -Path $reportPath -Encoding UTF8
    Write-Host "`n详细报告已保存到: $reportPath" -ForegroundColor Cyan
}

# 主函数
function Main {
    Write-Host "AIOps平台环境检查工具" -ForegroundColor Green
    Write-Host "检查类型: $DeploymentType" -ForegroundColor White
    Write-Host "详细模式: $($Detailed.IsPresent)" -ForegroundColor White
    Write-Host "自动修复: $($Fix.IsPresent)" -ForegroundColor White
    Write-Host "开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    
    # 执行检查
    Test-SystemInfo
    Test-HardwareResources
    Test-NetworkConfiguration
    Test-PowerShellEnvironment
    
    if ($DeploymentType -in @("docker", "all")) {
        Test-DockerEnvironment
    }
    
    if ($DeploymentType -in @("kubernetes", "all")) {
        Test-KubernetesEnvironment
    }
    
    # 自动修复
    if ($Fix) {
        Invoke-AutoFix
    }
    
    # 生成报告
    New-Report
    
    Write-Host "`n检查完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
}

# 执行主函数
Main