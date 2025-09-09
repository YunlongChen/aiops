<#
.SYNOPSIS
    AIOps智能运维平台自动化部署脚本 (PowerShell)

.DESCRIPTION
    本脚本用于在Windows环境下自动化部署AIOps平台，包括环境检查、依赖安装、配置生成和服务启动。
    支持Docker Compose和Kubernetes两种部署方式。

.PARAMETER DeploymentType
    部署类型：docker 或 kubernetes

.PARAMETER Environment
    部署环境：development, staging, production

.PARAMETER ConfigFile
    自定义配置文件路径

.PARAMETER SkipChecks
    跳过环境检查

.EXAMPLE
    .\deploy.ps1 -DeploymentType docker -Environment development
    .\deploy.ps1 -DeploymentType kubernetes -Environment production -ConfigFile .\prod-config.yaml

.NOTES
    版本: 1.0.0
    作者: AIOps Team
    创建日期: 2024-01-01
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("docker", "kubernetes")]
    [string]$DeploymentType,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$SkipChecks,
    
    [Parameter(Mandatory=$false)]
    [switch]$QuickStart
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 全局变量
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:LogFile = Join-Path $script:ProjectRoot "logs\deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
$script:RequiredPorts = @(80, 443, 3000, 5601, 9090, 9200, 6379, 5432)
$script:MinDockerVersion = "20.10.0"
$script:MinKubernetesVersion = "1.19.0"
$script:MinHelmVersion = "3.2.0"

# 创建日志目录
if (!(Test-Path (Split-Path $script:LogFile))) {
    New-Item -ItemType Directory -Path (Split-Path $script:LogFile) -Force | Out-Null
}

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"
    
    # 写入日志文件
    Add-Content -Path $script:LogFile -Value $logMessage
    
    # 控制台输出
    switch ($Level) {
        "INFO" { Write-Host $logMessage -ForegroundColor White }
        "WARN" { Write-Host $logMessage -ForegroundColor Yellow }
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "SUCCESS" { Write-Host $logMessage -ForegroundColor Green }
    }
}

# 检查管理员权限
function Test-AdminRights {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 检查端口占用
function Test-PortAvailability {
    param([int[]]$Ports)
    
    $unavailablePorts = @()
    
    foreach ($port in $Ports) {
        try {
            $connection = Test-NetConnection -ComputerName "localhost" -Port $port -InformationLevel Quiet -WarningAction SilentlyContinue
            if ($connection) {
                $unavailablePorts += $port
            }
        }
        catch {
            # 端口可用
        }
    }
    
    return $unavailablePorts
}

# 检查系统资源
function Test-SystemResources {
    $cpu = Get-WmiObject -Class Win32_Processor | Measure-Object -Property NumberOfCores -Sum
    $memory = Get-WmiObject -Class Win32_ComputerSystem
    $disk = Get-WmiObject -Class Win32_LogicalDisk -Filter "DriveType=3" | Where-Object { $_.DeviceID -eq "C:" }
    
    $totalCores = $cpu.Sum
    $totalMemoryGB = [math]::Round($memory.TotalPhysicalMemory / 1GB, 2)
    $availableDiskGB = [math]::Round($disk.FreeSpace / 1GB, 2)
    
    Write-Log "系统资源检查:"
    Write-Log "  CPU核心数: $totalCores"
    Write-Log "  总内存: ${totalMemoryGB}GB"
    Write-Log "  可用磁盘空间: ${availableDiskGB}GB"
    
    $warnings = @()
    
    if ($totalCores -lt 4) {
        $warnings += "CPU核心数不足，推荐至少4核"
    }
    
    if ($totalMemoryGB -lt 8) {
        $warnings += "内存不足，推荐至少8GB"
    }
    
    if ($availableDiskGB -lt 50) {
        $warnings += "磁盘空间不足，推荐至少50GB可用空间"
    }
    
    return $warnings
}

# 检查Docker环境
function Test-DockerEnvironment {
    try {
        $dockerVersion = docker --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker未安装或不可用"
        }
        
        $versionMatch = $dockerVersion -match "Docker version ([\d\.]+)"
        if ($versionMatch) {
            $currentVersion = $matches[1]
            if ([version]$currentVersion -lt [version]$script:MinDockerVersion) {
                throw "Docker版本过低，当前版本: $currentVersion，最低要求: $script:MinDockerVersion"
            }
        }
        
        # 检查Docker Compose
        $composeVersion = docker-compose --version 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose未安装或不可用"
        }
        
        # 检查Docker服务状态（忽略PowerShell的错误流处理）
        $dockerInfo = $null
        $dockerExitCode = 0
        try {
            $dockerInfo = docker info 2>&1
            $dockerExitCode = $LASTEXITCODE
        }
        catch {
            # PowerShell可能将WARNING当作错误，但我们需要检查实际内容
            $dockerInfo = $_.Exception.Message
            $dockerExitCode = 1
        }
        
        # 检查是否有关键错误（忽略警告）
        $criticalErrors = $dockerInfo | Where-Object { 
            $_ -match "ERROR" -or 
            $_ -match "Cannot connect" -or 
            $_ -match "daemon not running" -or
            $_ -match "Is the docker daemon running"
        }
        
        if ($criticalErrors) {
            throw ($criticalErrors -join "; ")
        }
        
        # 检查是否只有警告
        $warningLines = $dockerInfo | Where-Object { $_ -match "WARNING" }
        $errorLines = $dockerInfo | Where-Object { 
            ($_ -match "Error" -or $_ -match "error") -and $_ -notmatch "WARNING" 
        }
        
        # 如果有真正的错误（非警告），抛出异常
        if ($errorLines) {
            throw "Docker服务错误: $($errorLines -join '; ')"
        }
        
        # 如果退出码非零但只有警告，记录警告但继续
        if ($dockerExitCode -ne 0 -and $warningLines -and -not $errorLines) {
            Write-Log "Docker警告（可忽略）: $($warningLines -join '; ')" "WARN"
        }
        
        # 如果退出码非零且没有警告也没有错误，可能是其他问题
        if ($dockerExitCode -ne 0 -and -not $warningLines -and -not $errorLines) {
            throw "Docker服务状态未知错误"
        }
         
        Write-Log "Docker环境检查通过" "SUCCESS"
        Write-Log "  Docker版本: $dockerVersion"
        Write-Log "  Docker Compose版本: $composeVersion"
        
        return $true
    }
    catch {
        Write-Log "Docker环境检查失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 检查Kubernetes环境
function Test-KubernetesEnvironment {
    try {
        # 检查kubectl
        $kubectlVersion = kubectl version --client --short 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "kubectl未安装或不可用"
        }
        
        # 检查集群连接
        kubectl cluster-info 2>$null | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "无法连接到Kubernetes集群"
        }
        
        # 检查Helm
        $helmVersion = helm version --short 2>$null
        if ($LASTEXITCODE -ne 0) {
            throw "Helm未安装或不可用"
        }
        
        $versionMatch = $helmVersion -match "v([\d\.]+)"
        if ($versionMatch) {
            $currentVersion = $matches[1]
            if ([version]$currentVersion -lt [version]$script:MinHelmVersion) {
                throw "Helm版本过低，当前版本: $currentVersion，最低要求: $script:MinHelmVersion"
            }
        }
        
        Write-Log "Kubernetes环境检查通过" "SUCCESS"
        Write-Log "  kubectl版本: $kubectlVersion"
        Write-Log "  Helm版本: $helmVersion"
        
        return $true
    }
    catch {
        Write-Log "Kubernetes环境检查失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 环境检查主函数
function Invoke-EnvironmentCheck {
    Write-Log "开始环境检查..." "INFO"
    
    # 检查管理员权限
    if (!(Test-AdminRights)) {
        Write-Log "警告: 未以管理员身份运行，某些操作可能失败" "WARN"
    }
    
    # 检查系统资源
    $resourceWarnings = Test-SystemResources
    foreach ($warning in $resourceWarnings) {
        Write-Log $warning "WARN"
    }
    
    # 检查端口占用
    $unavailablePorts = Test-PortAvailability -Ports $script:RequiredPorts
    if ($unavailablePorts.Count -gt 0) {
        Write-Log "以下端口被占用: $($unavailablePorts -join ', ')" "WARN"
        Write-Log "请确保这些端口可用或修改配置文件中的端口设置" "WARN"
    }
    
    # 根据部署类型检查环境
    $envCheckPassed = $false
    
    switch ($DeploymentType) {
        "docker" {
            $envCheckPassed = Test-DockerEnvironment
        }
        "kubernetes" {
            $envCheckPassed = Test-KubernetesEnvironment
        }
    }
    
    if (!$envCheckPassed) {
        throw "环境检查失败，请解决上述问题后重试"
    }
    
    Write-Log "环境检查完成" "SUCCESS"
}

# 生成Docker Compose配置
function New-DockerComposeConfig {
    $configPath = Join-Path $script:ProjectRoot "docker-compose.override.yml"
    
    $config = @"
# AIOps平台 - $Environment 环境配置
# 自动生成于: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

version: '3.8'

services:
  # 环境特定配置
  traefik:
    environment:
      - TRAEFIK_LOG_LEVEL=$(if ($Environment -eq 'development') { 'DEBUG' } else { 'INFO' })
      - TRAEFIK_API_DASHBOARD=$(if ($Environment -eq 'development') { 'true' } else { 'false' })
  
  prometheus:
    environment:
      - PROMETHEUS_RETENTION=$(if ($Environment -eq 'production') { '90d' } else { '30d' })
  
  grafana:
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=$(if ($Environment -eq 'development') { 'admin' } else { 'aiops-admin-2024' })
      - GF_USERS_ALLOW_SIGN_UP=$(if ($Environment -eq 'development') { 'true' } else { 'false' })
  
  elasticsearch:
    environment:
      - discovery.type=$(if ($Environment -eq 'development') { 'single-node' } else { 'zen' })
      - "ES_JAVA_OPTS=-Xms$(if ($Environment -eq 'production') { '2g' } else { '1g' }) -Xmx$(if ($Environment -eq 'production') { '2g' } else { '1g' })"
"@
    
    Set-Content -Path $configPath -Value $config -Encoding UTF8
    Write-Log "Docker Compose配置已生成: $configPath" "SUCCESS"
}

# 生成Kubernetes配置
function New-KubernetesConfig {
    $configPath = Join-Path $script:ProjectRoot "k8s-values-$Environment.yaml"
    
    $config = @"
# AIOps平台 - $Environment 环境配置
# 自动生成于: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

global:
  environment: $Environment
  development: $(if ($Environment -eq 'development') { 'true' } else { 'false' })
  storageClass: "$(if ($Environment -eq 'production') { 'fast-ssd' } else { 'standard' })"

ingress:
  enabled: true
  className: "traefik"
  hosts:
    - host: $(if ($Environment -eq 'development') { 'aiops.local' } else { 'aiops.example.com' })
      paths:
        - path: /
          pathType: Prefix
  tls: $(if ($Environment -eq 'production') { 'true' } else { 'false' })

prometheus:
  enabled: true
  retention: "$(if ($Environment -eq 'production') { '90d' } else { '30d' })"
  storage:
    size: "$(if ($Environment -eq 'production') { '100Gi' } else { '20Gi' })"
  resources:
    requests:
      memory: "$(if ($Environment -eq 'production') { '4Gi' } else { '2Gi' })"
      cpu: "$(if ($Environment -eq 'production') { '2000m' } else { '1000m' })"

grafana:
  enabled: true
  adminPassword: "$(if ($Environment -eq 'development') { 'admin' } else { 'aiops-admin-2024' })"
  persistence:
    enabled: $(if ($Environment -eq 'production') { 'true' } else { 'false' })
    size: "$(if ($Environment -eq 'production') { '10Gi' } else { '5Gi' })"

elasticsearch:
  enabled: true
  replicas: $(if ($Environment -eq 'production') { '3' } else { '1' })
  storage:
    size: "$(if ($Environment -eq 'production') { '200Gi' } else { '50Gi' })"
  resources:
    requests:
      memory: "$(if ($Environment -eq 'production') { '4Gi' } else { '2Gi' })"
      cpu: "$(if ($Environment -eq 'production') { '1000m' } else { '500m' })"

aiEngine:
  enabled: true
  replicas: $(if ($Environment -eq 'production') { '3' } else { '1' })
  resources:
    requests:
      memory: "$(if ($Environment -eq 'production') { '4Gi' } else { '2Gi' })"
      cpu: "$(if ($Environment -eq 'production') { '2000m' } else { '1000m' })"
"@
    
    Set-Content -Path $configPath -Value $config -Encoding UTF8
    Write-Log "Kubernetes配置已生成: $configPath" "SUCCESS"
    
    return $configPath
}

# Docker部署
function Invoke-DockerDeployment {
    Write-Log "开始Docker部署..." "INFO"
    
    try {
        # 生成配置
        New-DockerComposeConfig
        
        # 拉取镜像
        Write-Log "拉取Docker镜像..." "INFO"
        Set-Location $script:ProjectRoot
        docker-compose pull
        
        if ($LASTEXITCODE -ne 0) {
            throw "镜像拉取失败"
        }
        
        # 启动服务
        Write-Log "启动服务..." "INFO"
        docker-compose up -d
        
        if ($LASTEXITCODE -ne 0) {
            throw "服务启动失败"
        }
        
        # 等待服务就绪
        Write-Log "等待服务启动完成..." "INFO"
        Start-Sleep -Seconds 30
        
        # 检查服务状态
        $services = docker-compose ps --services
        $healthyServices = 0
        $totalServices = ($services | Measure-Object).Count
        
        foreach ($service in $services) {
            $status = docker-compose ps $service
            if ($status -match "Up") {
                $healthyServices++
                Write-Log "服务 $service 运行正常" "SUCCESS"
            } else {
                Write-Log "服务 $service 状态异常" "WARN"
            }
        }
        
        Write-Log "Docker部署完成: $healthyServices/$totalServices 服务运行正常" "SUCCESS"
        
        # 显示访问信息
        Write-Log "服务访问地址:" "INFO"
        Write-Log "  Grafana: http://localhost:3000 (admin/admin)" "INFO"
        Write-Log "  Prometheus: http://localhost:9090" "INFO"
        Write-Log "  Kibana: http://localhost:5601" "INFO"
        Write-Log "  Traefik Dashboard: http://localhost:8080" "INFO"
        
    }
    catch {
        Write-Log "Docker部署失败: $($_.Exception.Message)" "ERROR"
        
        # 显示日志以便调试
        Write-Log "显示服务日志:" "INFO"
        docker-compose logs --tail=50
        
        throw
    }
}

# Kubernetes部署
function Invoke-KubernetesDeployment {
    Write-Log "开始Kubernetes部署..." "INFO"
    
    try {
        # 生成配置
        $valuesFile = New-KubernetesConfig
        
        # 如果指定了自定义配置文件，使用它
        if ($ConfigFile -and (Test-Path $ConfigFile)) {
            $valuesFile = $ConfigFile
            Write-Log "使用自定义配置文件: $ConfigFile" "INFO"
        }
        
        # 创建命名空间
        $namespace = "aiops-platform"
        Write-Log "创建命名空间: $namespace" "INFO"
        kubectl create namespace $namespace --dry-run=client -o yaml | kubectl apply -f -
        
        # 添加Helm仓库
        Write-Log "添加Helm仓库..." "INFO"
        $helmRepos = @(
            @{Name="prometheus-community"; Url="https://prometheus-community.github.io/helm-charts"},
            @{Name="grafana"; Url="https://grafana.github.io/helm-charts"},
            @{Name="elastic"; Url="https://helm.elastic.co"},
            @{Name="bitnami"; Url="https://charts.bitnami.com/bitnami"},
            @{Name="traefik"; Url="https://helm.traefik.io/traefik"}
        )
        
        foreach ($repo in $helmRepos) {
            helm repo add $repo.Name $repo.Url 2>$null
        }
        
        helm repo update
        
        # 部署Helm Chart
        $chartPath = Join-Path $script:ProjectRoot "helm"
        Write-Log "部署Helm Chart..." "INFO"
        
        helm upgrade --install aiops-platform $chartPath `
            --namespace $namespace `
            --values $valuesFile `
            --timeout 10m `
            --wait
        
        if ($LASTEXITCODE -ne 0) {
            throw "Helm部署失败"
        }
        
        # 运行测试
        Write-Log "运行部署测试..." "INFO"
        helm test aiops-platform --namespace $namespace
        
        # 检查Pod状态
        Write-Log "检查Pod状态..." "INFO"
        $pods = kubectl get pods -n $namespace -o json | ConvertFrom-Json
        $runningPods = 0
        $totalPods = $pods.items.Count
        
        foreach ($pod in $pods.items) {
            $status = $pod.status.phase
            $name = $pod.metadata.name
            
            if ($status -eq "Running") {
                $runningPods++
                Write-Log "Pod $name 运行正常" "SUCCESS"
            } else {
                Write-Log "Pod $name 状态: $status" "WARN"
            }
        }
        
        Write-Log "Kubernetes部署完成: $runningPods/$totalPods Pod运行正常" "SUCCESS"
        
        # 显示访问信息
        Write-Log "获取服务访问信息..." "INFO"
        $services = kubectl get svc -n $namespace -o json | ConvertFrom-Json
        
        foreach ($service in $services.items) {
            $name = $service.metadata.name
            $type = $service.spec.type
            
            if ($type -eq "LoadBalancer") {
                $ip = $service.status.loadBalancer.ingress[0].ip
                if ($ip) {
                    Write-Log "服务 ${name}: http://$ip" "INFO"
                }
            } elseif ($type -eq "NodePort") {
                $nodePort = $service.spec.ports[0].nodePort
                Write-Log "服务 ${name}: http://`<node-ip`>:$nodePort" "INFO"
            }
        }
        
        Write-Log "使用 'kubectl port-forward' 进行本地访问" "INFO"
        
    }
    catch {
        Write-Log "Kubernetes部署失败: $($_.Exception.Message)" "ERROR"
        
        # 显示Pod日志以便调试
        Write-Log "显示Pod状态:" "INFO"
        kubectl get pods -n $namespace
        
        throw
    }
}

# 主函数
function Main {
    try {
        Write-Log "AIOps智能运维平台部署开始" "INFO"
        Write-Log "部署类型: $DeploymentType" "INFO"
        Write-Log "环境: $Environment" "INFO"
        Write-Log "日志文件: $script:LogFile" "INFO"
        
        # 环境检查
        if (!$SkipChecks) {
            Invoke-EnvironmentCheck
        } else {
            Write-Log "跳过环境检查" "WARN"
        }
        
        # 执行部署
        switch ($DeploymentType) {
            "docker" {
                Invoke-DockerDeployment
            }
            "kubernetes" {
                Invoke-KubernetesDeployment
            }
        }
        
        Write-Log "AIOps平台部署成功完成！" "SUCCESS"
        Write-Log "详细日志请查看: $script:LogFile" "INFO"
        
    }
    catch {
        Write-Log "部署失败: $($_.Exception.Message)" "ERROR"
        Write-Log "详细错误信息请查看日志文件: $script:LogFile" "ERROR"
        exit 1
    }
}

# 执行主函数
Main