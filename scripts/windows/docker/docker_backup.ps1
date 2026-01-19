#!/usr/bin/env pwsh
<#
.SYNOPSIS
Docker Image Backup Script for Windows

.DESCRIPTION
Backup Docker images to specified directory with compression and restore script generation

.PARAMETER BackupDir
Backup directory path, default is D:\data\backup

.PARAMETER ImageNames
List of image names to backup, if empty backup all images

.PARAMETER NoRun
Syntax check only, do not execute actual backup

.EXAMPLE
.\docker_backup_simple.ps1
Backup all Docker images to default directory

.EXAMPLE
.\docker_backup_simple.ps1 -BackupDir "C:\backup" -ImageNames @('nginx', 'redis')
Backup specified images to specified directory

.EXAMPLE
.\docker_backup_simple.ps1 -NoRun
Syntax check only
#>

param(
    [string]$BackupDir = 'D:\data\backup',
    [string[]]$ImageNames = @(),
    [switch]$NoRun
)

# Set error handling
$ErrorActionPreference = "Stop"

# Create timestamp
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Function: Show usage
function Show-Usage {
    Write-Host "Usage: .\docker_backup_simple.ps1 [-BackupDir backup_dir] [-ImageNames image_list]" -ForegroundColor Yellow
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\docker_backup_simple.ps1 -BackupDir .\backups -ImageNames @('nginx', 'redis')" -ForegroundColor Green
    Write-Host "  .\docker_backup_simple.ps1 -ImageNames @('mysql:8.0')" -ForegroundColor Green
    Write-Host "  .\docker_backup_simple.ps1" -ForegroundColor Green
    Write-Host ""
}

# Function: Test Docker availability
function Test-Docker {
    try {
        $null = Get-Command docker -ErrorAction Stop
        $dockerVersion = docker --version
        Write-Host "Docker available: $dockerVersion" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Error: Docker command not found" -ForegroundColor Red
        Write-Host "Please ensure Docker Desktop is installed and running" -ForegroundColor Red
        return $false
    }
}

# Function: Create backup directory
function New-BackupDirectory {
    param([string]$Directory)
    
    if (-not (Test-Path $Directory)) {
        New-Item -ItemType Directory -Path $Directory -Force | Out-Null
        Write-Host "Created backup directory: $Directory" -ForegroundColor Green
    }
    return (Resolve-Path $Directory).Path
}

# Function: Sanitize image name for filename
function Get-SafeImageName {
    param([string]$ImageName)
    
    # Replace characters not allowed in filenames
    $safeName = $ImageName -replace '[/:\\]', '_' -replace '[:*?"<>|]', '_'
    return $safeName
}

# Function: Compress using .NET
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
        
        # Remove uncompressed tar after compression
        if (Test-Path $InputFile) { 
            Remove-Item $InputFile -Force 
        }
        return $outputFile
    }
    catch {
        Write-Host "Warning: Managed GZip compression failed - $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

# Function: Backup single image
function Backup-DockerImage {
    param(
        [string]$ImageName,
        [string]$BackupPath
    )
    
    $safeName = Get-SafeImageName $ImageName
    $backupFile = Join-Path $BackupPath "${safeName}_${Timestamp}.tar"
    $compressedFile = "${backupFile}.gz"
    
    Write-Host "Backing up image: $ImageName" -ForegroundColor Cyan
    Write-Host "Saving to: $compressedFile" -ForegroundColor Cyan
    
    try {
        # Save image
        docker save -o $backupFile $ImageName
        if ($LASTEXITCODE -ne 0) { 
            throw "docker save failed with exit code $LASTEXITCODE" 
        }
        
        # Compress file
        Write-Host "Compressing file..." -ForegroundColor Cyan
        $gzipCmd = Get-Command gzip -ErrorAction SilentlyContinue
        if ($gzipCmd) {
            & $gzipCmd.Source "-f" $backupFile
            if ($LASTEXITCODE -ne 0 -or -not (Test-Path $compressedFile)) {
                Write-Host "Warning: gzip compression failed, trying managed compression" -ForegroundColor Yellow
                $managed = Compress-WithGzip -InputFile $backupFile
                if (-not $managed) { 
                    throw "Compression failed" 
                } 
                else { 
                    $compressedFile = $managed 
                }
            }
        }
        else {
            $managed = Compress-WithGzip -InputFile $backupFile
            if (-not $managed) { 
                throw "Compression failed" 
            } 
            else { 
                $compressedFile = $managed 
            }
        }
        
        Write-Host "Successfully backed up: $ImageName" -ForegroundColor Green
        return $compressedFile
    }
    catch {
        Write-Host "Backup failed: $ImageName - $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function: Get all Docker images
function Get-AllDockerImages {
    try {
        $images = docker images --format '{{.Repository}}:{{.Tag}}' | Where-Object { $_ -notlike '<none>*' }
        return $images
    }
    catch {
        Write-Host "Error: Unable to get Docker image list" -ForegroundColor Red
        return @()
    }
}

# Function: Backup all images
function Backup-AllImages {
    param([string]$BackupPath)
    
    Write-Host "Getting Docker image list..." -ForegroundColor Cyan
    $images = Get-AllDockerImages
    
    if (-not $images) {
        Write-Host "No Docker images found" -ForegroundColor Yellow
        return 0
    }
    
    Write-Host "Found $($images.Count) images, starting backup..." -ForegroundColor Green
    
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
    
    Write-Host "Backup complete! Successfully backed up $successCount/$($images.Count) images" -ForegroundColor Green
    return $successCount
}

# Function: Backup specified images
function Backup-SpecifiedImages {
    param(
        [string[]]$Images,
        [string]$BackupPath
    )
    
    $successCount = 0
    $backupFiles = @()
    
    foreach ($image in $Images) {
        # Check if image exists
        $imageExists = docker image inspect $image 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $result = Backup-DockerImage -ImageName $image -BackupPath $BackupPath
            if ($result) {
                $backupFiles += $result
                $successCount++
            }
        }
        else {
            Write-Host "Warning: Image does not exist - $image" -ForegroundColor Yellow
        }
    }
    
    Write-Host "Specified image backup complete! Successfully backed up $successCount/$($Images.Count) images" -ForegroundColor Green
    return $successCount
}

# Function: Generate restore script
function New-RestoreScript {
    param([string]$BackupPath)
    
    $restoreScript = Join-Path $BackupPath "restore_images_${Timestamp}.ps1"
    
    # Build restore script content using array
    $lines = @()
    $lines += '#!/usr/bin/env pwsh'
    $lines += '<#'
    $lines += '.DESCRIPTION'
    $lines += 'Docker Image Restore Script - Auto Generated'
    $lines += '#>'
    $lines += ''
    $lines += 'param('
    $lines += '    [string]$BackupDir = "$PSScriptRoot"'
    $lines += ')'
    $lines += ''
    $lines += '$ErrorActionPreference = "Stop"'
    $lines += ''
    $lines += 'Write-Host "==========================================" -ForegroundColor Cyan'
    $lines += 'Write-Host "        Docker Image Restore Tool" -ForegroundColor Cyan'
    $lines += 'Write-Host "==========================================" -ForegroundColor Cyan'
    $lines += 'Write-Host ("Generated at: {0}" -f (Get-Date))'
    $lines += ''
    $lines += '# Check Docker'
    $lines += 'try {'
    $lines += '    $null = Get-Command docker -ErrorAction Stop'
    $lines += '    $dockerVersion = docker --version'
    $lines += '    Write-Host "Docker available: $dockerVersion" -ForegroundColor Green'
    $lines += '}'
    $lines += 'catch {'
    $lines += '    Write-Host "Error: Docker command not found" -ForegroundColor Red'
    $lines += '    exit 1'
    $lines += '}'
    $lines += ''
    $lines += '$backupFiles = Get-ChildItem "$BackupDir" -Filter "*.tar.gz" | Sort-Object Name'
    $lines += 'if (-not $backupFiles) {'
    $lines += '    Write-Host "No backup files (*.tar.gz) found in directory $BackupDir" -ForegroundColor Yellow'
    $lines += '    exit 1'
    $lines += '}'
    $lines += 'Write-Host ("Found {0} backup files:" -f $backupFiles.Count) -ForegroundColor Green'
    $lines += 'foreach ($file in $backupFiles) {'
    $lines += '    Write-Host ("  - {0}" -f $file.Name)'
    $lines += '}'
    $lines += ''
    $lines += '$successCount = 0'
    $lines += 'foreach ($backupFile in $backupFiles) {'
    $lines += '    Write-Host ("Restoring: {0}" -f $backupFile.Name) -ForegroundColor Cyan'
    $lines += '    try {'
    $lines += '        docker load -i $backupFile.FullName'
    $lines += '        if ($LASTEXITCODE -eq 0) {'
    $lines += '            Write-Host ("Successfully restored: {0}" -f $backupFile.Name) -ForegroundColor Green'
    $lines += '            $successCount++'
    $lines += '        }'
    $lines += '        else {'
    $lines += '            Write-Host ("Failed to restore: {0}" -f $backupFile.Name) -ForegroundColor Red'
    $lines += '        }'
    $lines += '    }'
    $lines += '    catch {'
    $lines += '        Write-Host ("Restore error: {0} - {1}" -f $backupFile.Name, $_.Exception.Message) -ForegroundColor Red'
    $lines += '    }'
    $lines += '    Write-Host "------------------------------------------" -ForegroundColor Gray'
    $lines += '}'
    $lines += ''
    $lines += 'Write-Host ("Restore complete! Successfully restored {0}/{1} images" -f $successCount, $backupFiles.Count) -ForegroundColor Green'
    $lines += 'Write-Host "`nCurrent Docker images in system:" -ForegroundColor Cyan'
    $lines += 'docker images'
    
    $restoreContent = $lines -join "`n"

    try {
        Set-Content -Path $restoreScript -Value $restoreContent -Encoding UTF8
        Write-Host "Generated restore script: $restoreScript" -ForegroundColor Green
        return $restoreScript
    }
    catch {
        Write-Host "Warning: Unable to generate restore script - $($_.Exception.Message)" -ForegroundColor Yellow
        return $null
    }
}

# Function: Generate backup report
function New-BackupReport {
    param(
        [string]$BackupPath,
        [int]$BackupCount
    )
    
    $reportFile = Join-Path $BackupPath "backup_report_${Timestamp}.txt"
    $fileList = (Get-ChildItem $BackupPath -Filter "*.tar.gz" | ForEach-Object { $_.Name }) -join "`n"
    
    $reportLines = @()
    $reportLines += "Docker Image Backup Report - Windows"
    $reportLines += "Backup Time: $(Get-Date)"
    $reportLines += "Backup Directory: $BackupPath"
    $reportLines += "Backup Image Count: $BackupCount"
    $reportLines += "=========================================="
    $reportLines += ""
    $reportLines += "Backup Files:"
    $reportLines += $fileList
    $reportLines += ""
    $reportLines += "=========================================="
    $reportLines += "Restore Instructions:"
    $reportLines += "1. Use auto restore script: .\restore_images_${Timestamp}.ps1"
    $reportLines += "2. Manual single image restore: docker load -i backup_file.tar.gz"
    $reportLines += "3. Batch restore: Get-ChildItem -Filter *.tar.gz | ForEach-Object { docker load -i `$_.FullName }"
    $reportLines += ""
    $reportLines += "System Information:"
    $reportLines += "Operating System: $([System.Environment]::OSVersion.VersionString)"
    $reportLines += "PowerShell Version: $($PSVersionTable.PSVersion)"
    $reportLines += "Docker Version: $(docker --version 2>&1)"
    
    $reportContent = $reportLines -join "`n"

    try {
        Set-Content -Path $reportFile -Value $reportContent -Encoding UTF8
        Write-Host "Generated backup report: $reportFile" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: Unable to generate backup report - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Function: Get free space in MB for specified path
function Get-FreeSpaceMB {
    param([string]$Path)
    
    try {
        $root = [System.IO.Path]::GetPathRoot((Resolve-Path $Path).Path)
    }
    catch {
        # If directory doesn't exist, parse drive letter from input path directly
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

# Function: Calculate total image size in MB
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
            Write-Host "Note: Unable to get image size - $image" -ForegroundColor Yellow
        }
    }
    return [math]::Round($totalBytes / 1MB, 2)
}

# Main program
function Main {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "        Docker Image Backup Tool - Windows" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Check Docker
    if (-not (Test-Docker)) { 
        exit 1 
    }
    
    # Check target disk space before running
    $imagesToBackup = $ImageNames
    if (-not $imagesToBackup -or $imagesToBackup.Count -eq 0) { 
        $imagesToBackup = Get-AllDockerImages 
    }
    
    $requiredMB = Get-ImagesTotalSizeMB -Images $imagesToBackup
    $freeMB = Get-FreeSpaceMB -Path $BackupDir
    Write-Host ("Target disk free space: {0} MB | Estimated backup size: {1} MB" -f $freeMB, $requiredMB) -ForegroundColor White
    
    if ($requiredMB -gt 0 -and ($freeMB -lt ($requiredMB + 512))) {
        Write-Host "Error: Insufficient disk space, please free up space or use a larger disk (recommend keeping at least 512MB extra space)" -ForegroundColor Red
        exit 1
    }
    
    # Create backup directory
    $resolvedBackupDir = New-BackupDirectory -Directory $BackupDir
    
    Write-Host "Backup directory: $resolvedBackupDir" -ForegroundColor Green
    Write-Host ""
    
    $backupCount = 0
    
    if ($ImageNames.Count -eq 0) {
        Write-Host "Mode: Backup all Docker images" -ForegroundColor Yellow
        $backupCount = Backup-AllImages -BackupPath $resolvedBackupDir
    }
    else {
        Write-Host "Mode: Backup specified images" -ForegroundColor Yellow
        Write-Host ("Specified images: {0}" -f ($ImageNames -join ", ")) -ForegroundColor White
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
        Write-Host "Backup Complete!" -ForegroundColor Green
        Write-Host "Backup Location: $resolvedBackupDir" -ForegroundColor White
        Write-Host "Backup Count: $backupCount images" -ForegroundColor White
        Write-Host "Total Size: $sizeMB MB" -ForegroundColor White
        if ($restoreScript) { 
            Write-Host "Restore Script: $restoreScript" -ForegroundColor White 
        }
        Write-Host "==========================================" -ForegroundColor Cyan
    }
    else {
        Write-Host "No images were successfully backed up" -ForegroundColor Yellow
    }
}

# Run main program
if (-not $NoRun) {
    try {
        Main
    }
    catch {
        Write-Host "Script execution error: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
} 
else {
    Write-Host "Syntax check mode: Functions loaded, main process not executed (-NoRun)" -ForegroundColor Yellow
}