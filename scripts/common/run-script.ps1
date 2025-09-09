<#
.SYNOPSIS
    跨平台脚本启动器

.DESCRIPTION
    根据当前操作系统自动选择并执行相应平台的脚本

.PARAMETER ScriptName
    要执行的脚本名称（不包含扩展名）

.PARAMETER Arguments
    传递给脚本的参数

.EXAMPLE
    .\run-script.ps1 -ScriptName "cleanup" -Arguments "-DryRun -DeploymentType docker-compose"
    .\run-script.ps1 -ScriptName "monitor" -Arguments "-Environment development"

.NOTES
    文件名: run-script.ps1
    作者: AIOps Team
    创建日期: 2025-01-10
    版本: 1.0.0
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ScriptName,
    
    [Parameter(Mandatory=$false)]
    [string]$Arguments = ""
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 获取脚本根目录
$ScriptRoot = Split-Path -Parent $PSScriptRoot

# 检测操作系统
function Get-Platform {
    if ($IsWindows -or $env:OS -eq "Windows_NT") {
        return "windows"
    } elseif ($IsLinux) {
        return "linux"
    } elseif ($IsMacOS) {
        return "linux"  # MacOS使用Linux脚本
    } else {
        # 默认使用Windows
        return "windows"
    }
}

# 主函数
function Main {
    $platform = Get-Platform
    Write-Host "[INFO] 检测到平台: $platform" -ForegroundColor Green
    
    # 构建脚本路径
    if ($platform -eq "windows") {
        $scriptPath = Join-Path $ScriptRoot "$platform\$ScriptName.ps1"
        $executor = "powershell"
        $executorArgs = "-ExecutionPolicy Bypass -File"
    } else {
        $scriptPath = Join-Path $ScriptRoot "$platform\$ScriptName.sh"
        $executor = "bash"
        $executorArgs = ""
    }
    
    # 检查脚本是否存在
    if (-not (Test-Path $scriptPath)) {
        Write-Error "脚本不存在: $scriptPath"
        exit 1
    }
    
    Write-Host "[INFO] 执行脚本: $scriptPath" -ForegroundColor Green
    Write-Host "[INFO] 参数: $Arguments" -ForegroundColor Green
    
    # 执行脚本
    try {
        if ($platform -eq "windows") {
            if ($Arguments) {
                $cmd = "powershell -ExecutionPolicy Bypass -File `"$scriptPath`" $Arguments"
                Invoke-Expression $cmd
            } else {
                & powershell -ExecutionPolicy Bypass -File $scriptPath
            }
        } else {
            if ($Arguments) {
                $cmd = "bash `"$scriptPath`" $Arguments"
                Invoke-Expression $cmd
            } else {
                & bash $scriptPath
            }
        }
    } catch {
        Write-Error "脚本执行失败: $_"
        exit 1
    }
}

# 执行主函数
Main