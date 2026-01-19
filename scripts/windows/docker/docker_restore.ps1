#!/usr/bin/env pwsh
<#
.DESCRIPTION
Docker镜像恢复脚本 - Windows版本
#>

param(
    [string]$BackupDir = "D:\data\backup",
    [string]$BackupFile = ""
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 函数：显示用法
function Show-Usage {
    Write-Host "用法: .\docker_restore.ps1 [-BackupDir 备份目录] [-BackupFile 单个备份文件]" -ForegroundColor Yellow
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\docker_restore.ps1 -BackupDir .\backups" -ForegroundColor Green
    Write-Host "  .\docker_restore.ps1 -BackupFile .\backups\nginx_latest_20231201_1200.tar.gz" -ForegroundColor Green
    Write-Host "  .\docker_restore.ps1" -ForegroundColor Green
    Write-Host ""
}

# 函数：检查Docker是否可用
function Test-Docker {
    try {
        $null = Get-Command docker -ErrorAction Stop
        $dockerVersion = docker --version
        Write-Host "✓ Docker可用: $dockerVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "错误: 未找到Docker命令" -ForegroundColor Red
        Write-Host "请确保Docker Desktop已安装并运行" -ForegroundColor Red
        return $false
    }
}

# 函数：从目录恢复所有镜像
function Restore-FromDirectory {
    param([string]$Directory)
    
    if (-not (Test-Path $Directory)) {
        Write-Host "错误: 备份目录不存在: $Directory" -ForegroundColor Red
        return 0
    }
    
    $backupFiles = Get-ChildItem $Directory -Filter "*.tar.gz" | Sort-Object Name
    
    if (-not $backupFiles) {
        Write-Host "在目录 $Directory 中未找到备份文件 (*.tar.gz)" -ForegroundColor Yellow
        return 0
    }
    
    Write-Host "找到以下备份文件 ($($backupFiles.Count) 个):" -ForegroundColor Green
    foreach ($file in $backupFiles) {
        Write-Host "  - $($file.Name)" -ForegroundColor White
    }
    Write-Host ""
    
    $successCount = 0
    foreach ($backupFile in $backupFiles) {
        Write-Host "正在恢复: $($backupFile.Name)" -ForegroundColor Cyan
        try {
            if ($backupFile.Name -like "*.tar.gz") {
                $tarPath = Expand-GzipFile -GzFile $backupFile.FullName
                if ($tarPath) { docker load -i $tarPath }
            } else {
                docker load -i $backupFile.FullName
            }
            if ($LASTEXITCODE -eq 0) { Write-Host "✓ 恢复成功: $($backupFile.Name)" -ForegroundColor Green; $successCount++ }
            else { Write-Host "✗ 恢复失败: $($backupFile.Name)" -ForegroundColor Red }
        }
        catch {
            Write-Host "✗ 恢复出错: $($backupFile.Name) - $($_.Exception.Message)" -ForegroundColor Red
        }
        Write-Host "------------------------------------------" -ForegroundColor Gray
    }
    return $successCount
}

# 函数：从单个文件恢复
function Restore-FromFile {
    param([string]$File)
    
    if (-not (Test-Path $File)) {
        Write-Host "错误: 备份文件不存在: $File" -ForegroundColor Red
        return 0
    }
    
    Write-Host "正在从文件恢复: $File" -ForegroundColor Cyan
    
    try {
        if ($File -like "*.gz") {
            $tarPath = Expand-GzipFile -GzFile $File
            if ($tarPath) { docker load -i $tarPath }
        }
        else { docker load -i $File }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ 恢复成功: $(Split-Path $File -Leaf)" -ForegroundColor Green
            return 1
        }
        else {
            Write-Host "✗ 恢复失败: $(Split-Path $File -Leaf)" -ForegroundColor Red
            return 0
        }
    }
    catch {
        Write-Host "✗ 恢复出错: $($_.Exception.Message)" -ForegroundColor Red
        return 0
    }
}

# 函数：显示当前Docker镜像
function Show-DockerImages {
    Write-Host "`n当前系统中的Docker镜像:" -ForegroundColor Cyan
    try {
        docker images --format "table {{.Repository}}{{if .Tag}}:{{.Tag}}{{end}}`t{{.ID}}`t{{.CreatedAt}}"
    }
    catch {
        Write-Host "无法获取Docker镜像列表" -ForegroundColor Yellow
    }
}

# 主程序
function Main {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "        Docker镜像恢复工具 - Windows" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 检查Docker
    if (-not (Test-Docker)) {
        exit 1
    }
    
    $successCount = 0
    
    if ($BackupFile) {
        # 从单个文件恢复
        Write-Host "模式: 从单个文件恢复" -ForegroundColor Yellow
        $successCount = Restore-FromFile -File $BackupFile
    }
    else {
        # 从目录恢复
        Write-Host "模式: 从目录恢复" -ForegroundColor Yellow
        Write-Host "备份目录: $BackupDir" -ForegroundColor White
        $successCount = Restore-FromDirectory -Directory $BackupDir
    }
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    
    if ($successCount -gt 0) {
        Write-Host "恢复完成! 成功恢复 $successCount 个镜像" -ForegroundColor Green
        Show-DockerImages
    }
    else {
        Write-Host "没有成功恢复任何镜像" -ForegroundColor Yellow
    }
    
    Write-Host "==========================================" -ForegroundColor Cyan
}

# 运行主程序
try {
    Main
}
catch {
    Write-Host "脚本执行出错: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

function Expand-GzipFile {
    param([string]$GzFile)
    # 返回解压后的临时tar路径
    $tarTemp = [System.IO.Path]::ChangeExtension($GzFile, $null)
    try {
        $gunzip = Get-Command gunzip -ErrorAction SilentlyContinue
        if ($gunzip) {
            & $gunzip.Source "-c" $GzFile > $tarTemp
            return $tarTemp
        }
        else {
            # 托管解压
            $inStream = [System.IO.File]::OpenRead($GzFile)
            $outStream = [System.IO.File]::Create($tarTemp)
            $gzStream = New-Object System.IO.Compression.GZipStream($inStream, [System.IO.Compression.CompressionMode]::Decompress)
            $gzStream.CopyTo($outStream)
            $gzStream.Dispose(); $inStream.Dispose(); $outStream.Dispose()
            return $tarTemp
        }
    }
    catch {
        Write-Host "解压失败: $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}