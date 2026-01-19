#!/usr/bin/env pwsh
<#
.DESCRIPTION
Docker镜像备份脚本 - Windows版本
.PARAMETER BackupDir
备份目录路径
.PARAMETER ImageNames
要备份的镜像名称列表
.PARAMETER NoRun
仅进行语法检查，不执行实际备份
#>

param(
    [string]$BackupDir = 'D:\data\backup',
    [string[]]$ImageNames = @(),
    [switch]$NoRun
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 创建时间戳
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# 函数：显示用法
function Show-Usage {
    Write-Host "用法: .\docker_backup.ps1 [-BackupDir 备份目录] [-ImageNames 镜像列表]" -ForegroundColor Yellow
    Write-Host "示例:" -ForegroundColor Yellow
    Write-Host "  .\docker_backup.ps1 -BackupDir .\backups -ImageNames @('nginx', 'redis')" -ForegroundColor Green
    Write-Host "  .\docker_backup.ps1 -ImageNames @('mysql:8.0')" -ForegroundColor Green
    Write-Host "  .\docker_backup.ps1" -ForegroundColor Green
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

# 函数：创建备份目录
function New-BackupDirectory {
    param([string]$Directory)
    
    if (-not (Test-Path $Directory)) {
        New-Item -ItemType Directory -Path $Directory -Force | Out-Null
        Write-Host "创建备份目录: $Directory" -ForegroundColor Green
    }
    return (Resolve-Path $Directory).Path
}

# 函数：安全化镜像名称（用于文件名）
function Get-SafeImageName {
    param([string]$ImageName)
    
    # 替换不允许在文件名中使用的字符
    $safeName = $ImageName -replace '[/:\\]', '_' -replace '[:*?"<>|]', '_'
    return $safeName
}

# 函数：使用.NET压缩
function Compress-WithGzip {
    param([string]$InputFile)
    
    $outputFile = "$InputFile.gz"
    try {
        $inStream = [System.IO.File]::OpenRead($InputFile)
        $outStream = [System.IO.File]::Create($outputFile)
        $gzStream = New-Object System.IO.Compression.GZipStream($outStream, [System.IO.Compression.CompressionLevel]::Optimal)
        $inStream.CopyTo($gzStream)
        $gzStream.Dispose()
        $inStream.Dispose()
        $outStream.Dispose()
        
        # 压缩完成后删除未压缩的tar
        if (Test-Path $InputFile) { 
            Remove-Item $InputFile -Force 
        }
        return $outputFile
    }
    catch {
        Write-Host "警告: 托管GZip压缩失败 - $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

# 函数：备份单个镜像
function Backup-DockerImage {
    param(
        [string]$ImageName,
        [string]$BackupPath
    )
    
    $safeName = Get-SafeImageName $ImageName
    $backupFile = Join-Path $BackupPath "${safeName}_${Timestamp}.tar"
    $compressedFile = "${backupFile}.gz"
    
    Write-Host "正在备份镜像: $ImageName" -ForegroundColor Cyan
    Write-Host "保存到: $compressedFile" -ForegroundColor Cyan
    
    try {
        # 保存镜像
        docker save -o $backupFile $ImageName
        if ($LASTEXITCODE -ne 0) { 
            throw "docker save failed with exit code $LASTEXITCODE" 
        }
        
        # 压缩文件
        Write-Host "正在压缩文件..." -ForegroundColor Cyan
        $gzipCmd = Get-Command gzip -ErrorAction SilentlyContinue
        if ($gzipCmd) {
            & $gzipCmd.Source "-f" $backupFile
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path $compressedFile)) {
                Write-Host "警告: gzip压缩失败，尝试托管压缩" -ForegroundColor Yellow
                $managed = Compress-WithGzip -InputFile $backupFile
                if (-not $managed) { 
                    throw "压缩失败" 
                } 
                else { 
                    $compressedFile = $managed 
                }
            }
        }
        else {
            $managed = Compress-WithGzip -InputFile $backupFile
            if (-not $managed) { 
                throw "压缩失败" 
            } 
            else { 
                $compressedFile = $managed 
            }
        }
        
        Write-Host "✓ 成功备份: $ImageName" -ForegroundColor Green
        return $compressedFile
    }
    catch {
        Write-Host "✗ 备份失败: $ImageName - $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# 函数：获取所有Docker镜像
function Get-AllDockerImages {
    try {
        $images = docker images --format '{{.Repository}}:{{.Tag}}' | Where-Object { $_ -notlike '<none>*' }
        return $images
    }
    catch {
        Write-Host "错误: 无法获取Docker镜像列表" -ForegroundColor Red
        return @()
    }
}

# 函数：备份所有镜像
function Backup-AllImages {
    param([string]$BackupPath)
    
    Write-Host "正在获取Docker镜像列表..." -ForegroundColor Cyan
    $images = Get-AllDockerImages
    
    if (-not $images) {
        Write-Host "没有找到任何Docker镜像" -ForegroundColor Yellow
        return 0
    }
    
    Write-Host "找到 $($images.Count) 个镜像，开始备份..." -ForegroundColor Green
    
    $successCount = 0
    $backupFiles = @()
    
    foreach ($image in $images) {
        if ($image.Trim()) {
            $result = Backup-DockerImage -ImageName $image -BackupPath $BackupPath
            if ($result) {
                $backupFiles += $result
                $successCount++
            }
        }
    }
    
    Write-Host "备份完成! 成功备份 $successCount/$($images.Count) 个镜像" -ForegroundColor Green
    return $successCount
}

# 函数：备份指定镜像
function Backup-SpecifiedImages {
    param(
        [string[]]$Images,
        [string]$BackupPath
    )
    
    $successCount = 0
    $backupFiles = @()
    
    foreach ($image in $Images) {
        # 检查镜像是否存在
        $imageExists = docker image inspect $image 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $result = Backup-DockerImage -ImageName $image -BackupPath $BackupPath
            if ($result) {
                $backupFiles += $result
                $successCount++
            }
        }
        else {
            Write-Host "警告: 镜像不存在 - $image" -ForegroundColor Yellow
        }
    }
    
    Write-Host "指定镜像备份完成! 成功备份 $successCount/$($Images.Count) 个镜像" -ForegroundColor Green
    return $successCount
}

# 函数：生成恢复脚本
function New-RestoreScript {
    param([string]$BackupPath)
    
    $restoreScript = Join-Path $BackupPath "restore_images_${Timestamp}.ps1"
    
    # 使用数组构建恢复脚本内容
    $lines = @()
    $lines += '#!/usr/bin/env pwsh'
    $lines += '<#'
    $lines += '.DESCRIPTION'
    $lines += 'Docker镜像恢复脚本 - 自动生成'
    $lines += '#>'
    $lines += ''
    $lines += 'param('
    $lines += '    [string]$BackupDir = "$PSScriptRoot"'
    $lines += ')'
    $lines += ''
    $lines += '$ErrorActionPreference = "Stop"'
    $lines += ''
    $lines += 'Write-Host "==========================================" -ForegroundColor Cyan'
    $lines += 'Write-Host "        Docker镜像恢复工具" -ForegroundColor Cyan'
    $lines += 'Write-Host "==========================================" -ForegroundColor Cyan'
    $lines += 'Write-Host ("生成时间: {0}" -f (Get-Date))'
    $lines += ''
    $lines += '# 检查Docker'
    $lines += 'try {'
    $lines += '    $null = Get-Command docker -ErrorAction Stop'
    $lines += '    $dockerVersion = docker --version'
    $lines += '    Write-Host "✓ Docker可用: $dockerVersion" -ForegroundColor Green'
    $lines += '}'
    $lines += 'catch {'
    $lines += '    Write-Host "错误: 未找到Docker命令" -ForegroundColor Red'
    $lines += '    exit 1'
    $lines += '}'
    $lines += ''
    $lines += '$backupFiles = Get-ChildItem "$BackupDir" -Filter "*.tar.gz" | Sort-Object Name'
    $lines += 'if (-not $backupFiles) {'
    $lines += '    Write-Host "在目录 $BackupDir 中未找到备份文件 (*.tar.gz)" -ForegroundColor Yellow'
    $lines += '    exit 1'
    $lines += '}'
    $lines += 'Write-Host ("找到 {0} 个备份文件:" -f $backupFiles.Count) -ForegroundColor Green'
    $lines += 'foreach ($file in $backupFiles) {'
    $lines += '    Write-Host ("  - {0}" -f $file.Name)'
    $lines += '}'
    $lines += ''
    $lines += '$successCount = 0'
    $lines += 'foreach ($backupFile in $backupFiles) {'
    $lines += '    Write-Host ("正在恢复: {0}" -f $backupFile.Name) -ForegroundColor Cyan'
    $lines += '    try {'
    $lines += '        docker load -i $backupFile.FullName'
    $lines += '        if ($LASTEXITCODE -eq 0) {'
    $lines += '            Write-Host ("✓ 恢复成功: {0}" -f $backupFile.Name) -ForegroundColor Green'
    $lines += '            $successCount++'
    $lines += '        }'
    $lines += '        else {'
    $lines += '            Write-Host ("✗ 恢复失败: {0}" -f $backupFile.Name) -ForegroundColor Red'
    $lines += '        }'
    $lines += '    }'
    $lines += '    catch {'
    $lines += '        Write-Host ("✗ 恢复出错: {0} - {1}" -f $backupFile.Name, $_.Exception.Message) -ForegroundColor Red'
    $lines += '    }'
    $lines += '    Write-Host "------------------------------------------" -ForegroundColor Gray'
    $lines += '}'
    $lines += ''
    $lines += 'Write-Host ("恢复完成! 成功恢复 {0}/{1} 个镜像" -f $successCount, $backupFiles.Count) -ForegroundColor Green'
    $lines += 'Write-Host "`n当前系统中的Docker镜像:" -ForegroundColor Cyan'
    $lines += 'docker images'
    
    $restoreContent = $lines -join "`n"

    try {
        Set-Content -Path $restoreScript -Value $restoreContent -Encoding UTF8
        Write-Host "✓ 已生成恢复脚本: $restoreScript" -ForegroundColor Green
        return $restoreScript
    }
    catch {
        Write-Host "警告: 无法生成恢复脚本 - $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

# 函数：生成备份报告
function New-BackupReport {
    param(
        [string]$BackupPath,
        [int]$BackupCount
    )
    
    $reportFile = Join-Path $BackupPath "backup_report_${Timestamp}.txt"
    $fileList = (Get-ChildItem $BackupPath -Filter "*.tar.gz" | ForEach-Object { $_.Name }) -join "`n"
    
    $reportLines = @()
    $reportLines += "Docker镜像备份报告 - Windows"
    $reportLines += "备份时间: $(Get-Date)"
    $reportLines += "备份目录: $BackupPath"
    $reportLines += "备份镜像数量: $BackupCount"
    $reportLines += "=========================================="
    $reportLines += ""
    $reportLines += "备份的镜像文件:"
    $reportLines += $fileList
    $reportLines += ""
    $reportLines += "=========================================="
    $reportLines += "恢复说明:"
    $reportLines += "1. 使用自动恢复脚本: .\restore_images_${Timestamp}.ps1"
    $reportLines += "2. 手动恢复单个镜像: docker load -i 备份文件.tar.gz"
    $reportLines += "3. 批量恢复: Get-ChildItem -Filter *.tar.gz | ForEach-Object { docker load -i `$_.FullName }"
    $reportLines += ""
    $reportLines += "系统信息:"
    $reportLines += "操作系统: $([System.Environment]::OSVersion.VersionString)"
    $reportLines += "PowerShell版本: $($PSVersionTable.PSVersion)"
    $reportLines += "Docker版本: $(docker --version 2>&1)"
    
    $reportContent = $reportLines -join "`n"

    try {
        Set-Content -Path $reportFile -Value $reportContent -Encoding UTF8
        Write-Host "✓ 备份报告已生成: $reportFile" -ForegroundColor Green
    }
    catch {
        Write-Host "警告: 无法生成备份报告 - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 函数：获取指定路径所在磁盘的可用空间(MB)
function Get-FreeSpaceMB {
    param([string]$Path)
    
    try {
        $root = [System.IO.Path]::GetPathRoot((Resolve-Path $Path).Path)
    }
    catch {
        # 如果目录不存在，直接根据输入路径解析盘符
        $root = [System.IO.Path]::GetPathRoot($Path)
    }
    
    $driveLetter = $root.Substring(0,1)
    $disk = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DeviceID -eq "${driveLetter}:" }
    if ($disk) { 
        return [math]::Round($disk.FreeSpace / 1MB, 2) 
    } 
    else { 
        return 0 
    }
}

# 函数：计算镜像总大小(MB)
function Get-ImagesTotalSizeMB {
    param([string[]]$Images)
    
    $totalBytes = 0
    foreach ($image in $Images) {
        try {
            $info = docker image inspect $image 2>$null | ConvertFrom-Json
            if ($info) {
                foreach ($i in $info) { 
                    $totalBytes += [int64]$i.Size 
                }
            }
        }
        catch {
            Write-Host "提示: 无法获取镜像大小 - $image" -ForegroundColor Yellow
        }
    }
    return [math]::Round($totalBytes / 1MB, 2)
}

# 主程序
function Main {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "        Docker镜像备份工具 - Windows" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # 检查Docker
    if (-not (Test-Docker)) { 
        exit 1 
    }
    
    # 在运行前检查目标盘空间
    $imagesToBackup = $ImageNames
    if (-not $imagesToBackup -or $imagesToBackup.Count -eq 0) { 
        $imagesToBackup = Get-AllDockerImages 
    }
    
    $requiredMB = Get-ImagesTotalSizeMB -Images $imagesToBackup
    $freeMB = Get-FreeSpaceMB -Path $BackupDir
    Write-Host ("目标盘可用空间: {0} MB | 预计备份体积: {1} MB" -f $freeMB, $requiredMB) -ForegroundColor White
    
    if ($requiredMB -gt 0 -and ($freeMB -lt ($requiredMB + 512))) {
        Write-Host "错误: 目标盘可用空间不足，请释放空间或更换到更大磁盘 (建议保留至少512MB额外空间)" -ForegroundColor Red
        exit 1
    }
    
    # 创建备份目录
    $resolvedBackupDir = New-BackupDirectory -Directory $BackupDir
    
    Write-Host "备份目录: $resolvedBackupDir" -ForegroundColor Green
    Write-Host ""
    
    $backupCount = 0
    
    if ($ImageNames.Count -eq 0) {
        Write-Host "模式: 备份所有Docker镜像" -ForegroundColor Yellow
        $backupCount = Backup-AllImages -BackupPath $resolvedBackupDir
    }
    else {
        Write-Host "模式: 备份指定镜像" -ForegroundColor Yellow
        Write-Host ("指定镜像: {0}" -f ($ImageNames -join ", ")) -ForegroundColor White
        $backupCount = Backup-SpecifiedImages -Images $ImageNames -BackupPath $resolvedBackupDir
    }
    
    if ($backupCount -gt 0) {
        $restoreScript = New-RestoreScript -BackupPath $resolvedBackupDir
        New-BackupReport -BackupPath $resolvedBackupDir -BackupCount $backupCount
        
        $totalSize = (Get-ChildItem $resolvedBackupDir -Filter "*.tar.gz" | Measure-Object -Property Length -Sum).Sum
        $sizeMB = if ($totalSize) { 
            [math]::Round($totalSize / 1MB, 2) 
        } 
        else { 
            0 
        }
        
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Cyan
        Write-Host "备份完成!" -ForegroundColor Green
        Write-Host "备份位置: $resolvedBackupDir" -ForegroundColor White
        Write-Host "备份数量: $backupCount 个镜像" -ForegroundColor White
        Write-Host "总大小: $sizeMB MB" -ForegroundColor White
        if ($restoreScript) { 
            Write-Host "恢复脚本: $restoreScript" -ForegroundColor White 
        }
        Write-Host "==========================================" -ForegroundColor Cyan
    }
    else {
        Write-Host "没有成功备份任何镜像" -ForegroundColor Yellow
    }
}

# 运行主程序
if (-not $NoRun) {
    try {
        Main
    }
    catch {
        Write-Host "脚本执行出错: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} 
else {
    Write-Host "语法检查模式: 已加载函数，未执行主流程 (-NoRun)" -ForegroundColor Yellow
}