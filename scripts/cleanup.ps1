<#
.SYNOPSIS
    AIOps平台清理脚本 (PowerShell)

.DESCRIPTION
    本脚本用于清理AIOps平台部署的服务和资源，包括Docker容器、Kubernetes资源、
    本地文件等。支持选择性清理和强制清理模式。

.PARAMETER DeploymentType
    部署类型：docker-compose, kubernetes, 或 all

.PARAMETER Environment
    环境名称：development, staging, production

.PARAMETER Force
    强制清理，不询问确认

.PARAMETER KeepData
    保留数据卷和持久化存储

.PARAMETER KeepImages
    保留Docker镜像

.PARAMETER DryRun
    预览模式，只显示将要执行的操作

.EXAMPLE
    .\cleanup.ps1 -DeploymentType docker-compose -Environment development
    .\cleanup.ps1 -DeploymentType kubernetes -Environment production -Force
    .\cleanup.ps1 -DeploymentType all -DryRun

.NOTES
    版本: 1.0.0
    作者: AIOps Team
    创建日期: 2024-01-01
#>

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("docker-compose", "kubernetes", "all")]
    [string]$DeploymentType = "all",
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production", "all")]
    [string]$Environment = "all",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force,
    
    [Parameter(Mandatory=$false)]
    [switch]$KeepData,
    
    [Parameter(Mandatory=$false)]
    [switch]$KeepImages,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 全局变量
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:ProjectName = "aiops"
$script:CleanupActions = @()
$script:CleanupStats = @{
    containers_removed = 0
    volumes_removed = 0
    images_removed = 0
    networks_removed = 0
    k8s_resources_removed = 0
    files_removed = 0
}

# 日志函数
function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("Info", "Warning", "Error", "Success", "Debug")]
        [string]$Level = "Info"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    switch ($Level) {
        "Info"    { Write-Host "[$timestamp] [INFO] $Message" -ForegroundColor White }
        "Warning" { Write-Host "[$timestamp] [WARN] $Message" -ForegroundColor Yellow }
        "Error"   { Write-Host "[$timestamp] [ERROR] $Message" -ForegroundColor Red }
        "Success" { Write-Host "[$timestamp] [SUCCESS] $Message" -ForegroundColor Green }
        "Debug"   { Write-Host "[$timestamp] [DEBUG] $Message" -ForegroundColor Gray }
    }
}

# 添加清理操作
function Add-CleanupAction {
    param(
        [string]$Description,
        [scriptblock]$Action,
        [string]$Type = "general"
    )
    
    $script:CleanupActions += @{
        Description = $Description
        Action = $Action
        Type = $Type
    }
}

# 执行命令（支持预览模式）
function Invoke-CleanupCommand {
    param(
        [string]$Command,
        [string]$Description = "",
        [switch]$IgnoreErrors
    )
    
    if ($Description) {
        Write-Log $Description -Level "Info"
    }
    
    if ($DryRun) {
        Write-Log "[DRY RUN] $Command" -Level "Debug"
        return $true
    }
    
    try {
        Write-Log "执行: $Command" -Level "Debug"
        Invoke-Expression $Command
        return $true
    } catch {
        if ($IgnoreErrors) {
            Write-Log "命令执行失败（已忽略）: $($_.Exception.Message)" -Level "Warning"
            return $false
        } else {
            Write-Log "命令执行失败: $($_.Exception.Message)" -Level "Error"
            throw
        }
    }
}

# 检查Docker是否可用
function Test-DockerAvailable {
    try {
        $null = docker version 2>$null
        return $true
    } catch {
        return $false
    }
}

# 检查Kubernetes是否可用
function Test-KubernetesAvailable {
    try {
        $null = kubectl version --client 2>$null
        return $true
    } catch {
        return $false
    }
}

# 检查Helm是否可用
function Test-HelmAvailable {
    try {
        $null = helm version 2>$null
        return $true
    } catch {
        return $false
    }
}

# 获取Docker Compose项目名称
function Get-DockerComposeProjects {
    $projects = @()
    
    if ($Environment -eq "all") {
        $environments = @("development", "staging", "production")
    } else {
        $environments = @($Environment)
    }
    
    foreach ($env in $environments) {
        $projects += "$script:ProjectName-$env"
        $projects += $script:ProjectName  # 默认项目名
    }
    
    return $projects | Select-Object -Unique
}

# 清理Docker Compose资源
function Clear-DockerComposeResources {
    Write-Log "开始清理Docker Compose资源..." -Level "Info"
    
    if (!(Test-DockerAvailable)) {
        Write-Log "Docker不可用，跳过Docker Compose清理" -Level "Warning"
        return
    }
    
    $projects = Get-DockerComposeProjects
    
    foreach ($project in $projects) {
        Write-Log "清理项目: $project" -Level "Info"
        
        # 停止并删除容器
        Add-CleanupAction -Description "停止Docker Compose服务: $project" -Action {
            $containers = docker ps -a --filter "label=com.docker.compose.project=$project" --format "{{.ID}}" 2>$null
            if ($containers) {
                Invoke-CleanupCommand "docker stop $($containers -join ' ')" -IgnoreErrors
                Invoke-CleanupCommand "docker rm $($containers -join ' ')" -IgnoreErrors
                $script:CleanupStats.containers_removed += ($containers | Measure-Object).Count
            }
        } -Type "docker"
        
        # 删除网络
        Add-CleanupAction -Description "删除Docker网络: $project" -Action {
            $networks = docker network ls --filter "label=com.docker.compose.project=$project" --format "{{.ID}}" 2>$null
            if ($networks) {
                Invoke-CleanupCommand "docker network rm $($networks -join ' ')" -IgnoreErrors
                $script:CleanupStats.networks_removed += ($networks | Measure-Object).Count
            }
        } -Type "docker"
        
        # 删除卷（如果不保留数据）
        if (!$KeepData) {
            Add-CleanupAction -Description "删除Docker卷: $project" -Action {
                $volumes = docker volume ls --filter "label=com.docker.compose.project=$project" --format "{{.Name}}" 2>$null
                if ($volumes) {
                    Invoke-CleanupCommand "docker volume rm $($volumes -join ' ')" -IgnoreErrors
                    $script:CleanupStats.volumes_removed += ($volumes | Measure-Object).Count
                }
            } -Type "docker"
        }
    }
    
    # 清理孤立的容器
    Add-CleanupAction -Description "清理孤立的AIOps容器" -Action {
        $orphanContainers = docker ps -a --filter "name=$script:ProjectName" --format "{{.ID}}" 2>$null
        if ($orphanContainers) {
            Invoke-CleanupCommand "docker stop $($orphanContainers -join ' ')" -IgnoreErrors
            Invoke-CleanupCommand "docker rm $($orphanContainers -join ' ')" -IgnoreErrors
            $script:CleanupStats.containers_removed += ($orphanContainers | Measure-Object).Count
        }
    } -Type "docker"
    
    # 清理未使用的镜像（如果不保留镜像）
    if (!$KeepImages) {
        Add-CleanupAction -Description "清理AIOps相关镜像" -Action {
            $images = docker images --filter "reference=*aiops*" --format "{{.ID}}" 2>$null
            if ($images) {
                Invoke-CleanupCommand "docker rmi $($images -join ' ')" -IgnoreErrors
                $script:CleanupStats.images_removed += ($images | Measure-Object).Count
            }
        } -Type "docker"
    }
    
    Write-Log "Docker Compose资源清理完成" -Level "Success"
}

# 获取Kubernetes命名空间
function Get-KubernetesNamespaces {
    $namespaces = @()
    
    if ($Environment -eq "all") {
        $namespaces += @("aiops", "aiops-development", "aiops-staging", "aiops-production")
    } else {
        $namespaces += @("aiops", "aiops-$Environment")
    }
    
    return $namespaces | Select-Object -Unique
}

# 清理Kubernetes资源
function Clear-KubernetesResources {
    Write-Log "开始清理Kubernetes资源..." -Level "Info"
    
    if (!(Test-KubernetesAvailable)) {
        Write-Log "kubectl不可用，跳过Kubernetes清理" -Level "Warning"
        return
    }
    
    $namespaces = Get-KubernetesNamespaces
    
    foreach ($namespace in $namespaces) {
        Write-Log "检查命名空间: $namespace" -Level "Info"
        
        # 检查命名空间是否存在
        $nsExists = $false
        try {
            $null = kubectl get namespace $namespace 2>$null
            $nsExists = $true
        } catch {
            Write-Log "命名空间 $namespace 不存在，跳过" -Level "Debug"
            continue
        }
        
        if ($nsExists) {
            # 使用Helm删除发布
            if (Test-HelmAvailable) {
                Add-CleanupAction -Description "删除Helm发布: aiops (命名空间: $namespace)" -Action {
                    $releases = helm list -n $namespace --short 2>$null | Where-Object { $_ -like "*aiops*" }
                    foreach ($release in $releases) {
                        Invoke-CleanupCommand "helm uninstall $release -n $namespace" -IgnoreErrors
                        $script:CleanupStats.k8s_resources_removed++
                    }
                } -Type "kubernetes"
            }
            
            # 删除所有资源
            Add-CleanupAction -Description "删除命名空间中的所有资源: $namespace" -Action {
                # 删除部署
                $deployments = kubectl get deployments -n $namespace --no-headers 2>$null | ForEach-Object { ($_ -split '\s+')[0] }
                if ($deployments) {
                    Invoke-CleanupCommand "kubectl delete deployments --all -n $namespace" -IgnoreErrors
                    $script:CleanupStats.k8s_resources_removed += ($deployments | Measure-Object).Count
                }
                
                # 删除StatefulSet
                $statefulsets = kubectl get statefulsets -n $namespace --no-headers 2>$null | ForEach-Object { ($_ -split '\s+')[0] }
                if ($statefulsets) {
                    Invoke-CleanupCommand "kubectl delete statefulsets --all -n $namespace" -IgnoreErrors
                    $script:CleanupStats.k8s_resources_removed += ($statefulsets | Measure-Object).Count
                }
                
                # 删除服务
                $services = kubectl get services -n $namespace --no-headers 2>$null | Where-Object { $_ -notlike "*kubernetes*" } | ForEach-Object { ($_ -split '\s+')[0] }
                if ($services) {
                    Invoke-CleanupCommand "kubectl delete services $($services -join ' ') -n $namespace" -IgnoreErrors
                    $script:CleanupStats.k8s_resources_removed += ($services | Measure-Object).Count
                }
                
                # 删除ConfigMap和Secret
                Invoke-CleanupCommand "kubectl delete configmaps --all -n $namespace" -IgnoreErrors
                Invoke-CleanupCommand "kubectl delete secrets --all -n $namespace" -IgnoreErrors
                
                # 删除Ingress
                Invoke-CleanupCommand "kubectl delete ingress --all -n $namespace" -IgnoreErrors
                
                # 删除PVC（如果不保留数据）
                if (!$KeepData) {
                    $pvcs = kubectl get pvc -n $namespace --no-headers 2>$null | ForEach-Object { ($_ -split '\s+')[0] }
                    if ($pvcs) {
                        Invoke-CleanupCommand "kubectl delete pvc --all -n $namespace" -IgnoreErrors
                        $script:CleanupStats.k8s_resources_removed += ($pvcs | Measure-Object).Count
                    }
                }
            } -Type "kubernetes"
            
            # 删除命名空间（如果不是默认命名空间）
            if ($namespace -ne "default" -and $namespace -ne "kube-system") {
                Add-CleanupAction -Description "删除命名空间: $namespace" -Action {
                    Invoke-CleanupCommand "kubectl delete namespace $namespace" -IgnoreErrors
                    $script:CleanupStats.k8s_resources_removed++
                } -Type "kubernetes"
            }
        }
    }
    
    # 清理集群级资源
    Add-CleanupAction -Description "清理集群级AIOps资源" -Action {
        # 删除ClusterRole和ClusterRoleBinding
        $clusterRoles = kubectl get clusterroles --no-headers 2>$null | Where-Object { $_ -like "*aiops*" } | ForEach-Object { ($_ -split '\s+')[0] }
        if ($clusterRoles) {
            Invoke-CleanupCommand "kubectl delete clusterroles $($clusterRoles -join ' ')" -IgnoreErrors
            $script:CleanupStats.k8s_resources_removed += ($clusterRoles | Measure-Object).Count
        }
        
        $clusterRoleBindings = kubectl get clusterrolebindings --no-headers 2>$null | Where-Object { $_ -like "*aiops*" } | ForEach-Object { ($_ -split '\s+')[0] }
        if ($clusterRoleBindings) {
            Invoke-CleanupCommand "kubectl delete clusterrolebindings $($clusterRoleBindings -join ' ')" -IgnoreErrors
            $script:CleanupStats.k8s_resources_removed += ($clusterRoleBindings | Measure-Object).Count
        }
        
        # 删除PV（如果不保留数据）
        if (!$KeepData) {
            $pvs = kubectl get pv --no-headers 2>$null | Where-Object { $_ -like "*aiops*" } | ForEach-Object { ($_ -split '\s+')[0] }
            if ($pvs) {
                Invoke-CleanupCommand "kubectl delete pv $($pvs -join ' ')" -IgnoreErrors
                $script:CleanupStats.k8s_resources_removed += ($pvs | Measure-Object).Count
            }
        }
    } -Type "kubernetes"
    
    Write-Log "Kubernetes资源清理完成" -Level "Success"
}

# 清理本地文件
function Clear-LocalFiles {
    Write-Log "开始清理本地文件..." -Level "Info"
    
    $filesToClean = @(
        "$script:ProjectRoot\generated",
        "$script:ProjectRoot\logs",
        "$script:ProjectRoot\tmp",
        "$script:ProjectRoot\.env*",
        "$script:ProjectRoot\docker-compose.override.yml"
    )
    
    foreach ($path in $filesToClean) {
        Add-CleanupAction -Description "删除文件/目录: $path" -Action {
            if (Test-Path $path) {
                if ((Get-Item $path).PSIsContainer) {
                    $itemCount = (Get-ChildItem $path -Recurse | Measure-Object).Count
                    Remove-Item $path -Recurse -Force
                    $script:CleanupStats.files_removed += $itemCount
                } else {
                    Remove-Item $path -Force
                    $script:CleanupStats.files_removed++
                }
                Write-Log "已删除: $path" -Level "Debug"
            } else {
                Write-Log "文件不存在: $path" -Level "Debug"
            }
        } -Type "files"
    }
    
    Write-Log "本地文件清理完成" -Level "Success"
}

# 显示清理预览
function Show-CleanupPreview {
    Write-Log "清理预览" -Level "Info"
    Write-Host "=" * 60 -ForegroundColor Cyan
    
    $actionsByType = $script:CleanupActions | Group-Object Type
    
    foreach ($group in $actionsByType) {
        Write-Host "[$($group.Name.ToUpper())] 操作:" -ForegroundColor Yellow
        foreach ($action in $group.Group) {
            Write-Host "  - $($action.Description)" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "总计 $($script:CleanupActions.Count) 个清理操作" -ForegroundColor White
}

# 执行清理操作
function Invoke-CleanupActions {
    Write-Log "开始执行清理操作..." -Level "Info"
    
    $totalActions = $script:CleanupActions.Count
    $currentAction = 0
    
    foreach ($action in $script:CleanupActions) {
        $currentAction++
        $progress = [math]::Round(($currentAction / $totalActions) * 100, 1)
        
        Write-Progress -Activity "执行清理操作" -Status "$($action.Description) ($currentAction/$totalActions)" -PercentComplete $progress
        
        try {
            & $action.Action
        } catch {
            Write-Log "清理操作失败: $($action.Description) - $($_.Exception.Message)" -Level "Error"
            if (!$Force) {
                $response = Read-Host "是否继续执行剩余操作？(y/N)"
                if ($response -ne "y" -and $response -ne "Y") {
                    Write-Log "清理操作已中止" -Level "Warning"
                    return
                }
            }
        }
    }
    
    Write-Progress -Activity "执行清理操作" -Completed
}

# 显示清理统计
function Show-CleanupStats {
    Write-Log "清理统计" -Level "Success"
    Write-Host "=" * 40 -ForegroundColor Green
    
    Write-Host "Docker容器已删除: $($script:CleanupStats.containers_removed)" -ForegroundColor White
    Write-Host "Docker卷已删除: $($script:CleanupStats.volumes_removed)" -ForegroundColor White
    Write-Host "Docker镜像已删除: $($script:CleanupStats.images_removed)" -ForegroundColor White
    Write-Host "Docker网络已删除: $($script:CleanupStats.networks_removed)" -ForegroundColor White
    Write-Host "Kubernetes资源已删除: $($script:CleanupStats.k8s_resources_removed)" -ForegroundColor White
    Write-Host "本地文件已删除: $($script:CleanupStats.files_removed)" -ForegroundColor White
    
    $totalItems = ($script:CleanupStats.Values | Measure-Object -Sum).Sum
    Write-Host "总计删除项目: $totalItems" -ForegroundColor Cyan
    
    Write-Host "=" * 40 -ForegroundColor Green
}

# 确认清理操作
function Confirm-CleanupOperation {
    if ($Force -or $DryRun) {
        return $true
    }
    
    Write-Host ""
    Write-Host "警告: 此操作将删除以下资源:" -ForegroundColor Red
    
    if ($DeploymentType -eq "docker-compose" -or $DeploymentType -eq "all") {
        Write-Host "  - Docker容器、网络" -ForegroundColor Yellow
        if (!$KeepData) {
            Write-Host "  - Docker卷和数据" -ForegroundColor Yellow
        }
        if (!$KeepImages) {
            Write-Host "  - Docker镜像" -ForegroundColor Yellow
        }
    }
    
    if ($DeploymentType -eq "kubernetes" -or $DeploymentType -eq "all") {
        Write-Host "  - Kubernetes资源" -ForegroundColor Yellow
        if (!$KeepData) {
            Write-Host "  - 持久化卷和数据" -ForegroundColor Yellow
        }
    }
    
    Write-Host "  - 本地生成的文件" -ForegroundColor Yellow
    
    Write-Host ""
    $response = Read-Host "确定要继续吗？(y/N)"
    
    return ($response -eq "y" -or $response -eq "Y")
}

# 主函数
function Main {
    Write-Log "AIOps平台清理工具" -Level "Info"
    Write-Log "部署类型: $DeploymentType" -Level "Info"
    Write-Log "环境: $Environment" -Level "Info"
    Write-Log "保留数据: $KeepData" -Level "Info"
    Write-Log "保留镜像: $KeepImages" -Level "Info"
    Write-Log "预览模式: $DryRun" -Level "Info"
    Write-Log "开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Level "Info"
    
    try {
        # 准备清理操作
        switch ($DeploymentType) {
            "docker-compose" {
                Clear-DockerComposeResources
            }
            
            "kubernetes" {
                Clear-KubernetesResources
            }
            
            "all" {
                Clear-DockerComposeResources
                Clear-KubernetesResources
            }
        }
        
        # 总是清理本地文件
        Clear-LocalFiles
        
        # 显示预览
        if ($script:CleanupActions.Count -eq 0) {
            Write-Log "没有找到需要清理的资源" -Level "Warning"
            return
        }
        
        Show-CleanupPreview
        
        # 确认操作
        if (!(Confirm-CleanupOperation)) {
            Write-Log "清理操作已取消" -Level "Warning"
            return
        }
        
        # 执行清理
        if (!$DryRun) {
            Invoke-CleanupActions
            Show-CleanupStats
        } else {
            Write-Log "预览模式完成，未执行实际清理操作" -Level "Info"
        }
        
    } catch {
        Write-Log "清理过程中发生错误: $($_.Exception.Message)" -Level "Error"
        Write-Log $_.ScriptStackTrace -Level "Debug"
        exit 1
    }
    
    Write-Log "完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -Level "Info"
}

# 执行主函数
Main