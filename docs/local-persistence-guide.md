# AIOps平台本地持久化配置指南

## 概述

默认情况下，AIOps平台使用Docker存储卷来管理数据持久化，这是推荐的方式。但在某些场景下，您可能需要将数据持久化到本地目录，例如：

- 需要直接访问和备份数据文件
- 与现有备份系统集成
- 在多个环境间共享数据
- 便于数据迁移和管理

本指南将详细说明如何配置本地持久化存储。

## ⚠️ 重要提醒

**在修改存储配置前，请务必备份现有数据！**

## 配置步骤

### 1. 停止现有服务

```bash
# 停止所有服务
docker-compose down

# 备份现有数据（可选）
docker run --rm -v aiops_postgres-data:/source -v $(pwd)/backup:/backup alpine tar czf /backup/postgres-backup.tar.gz -C /source .
docker run --rm -v aiops_prometheus-data:/source -v $(pwd)/backup:/backup alpine tar czf /backup/prometheus-backup.tar.gz -C /source .
docker run --rm -v aiops_grafana-data:/source -v $(pwd)/backup:/backup alpine tar czf /backup/grafana-backup.tar.gz -C /source .
```

### 2. 创建本地数据目录

#### Windows (PowerShell)

```powershell
# 创建数据目录脚本
# create-data-dirs.ps1

# 设置数据根目录
$DataRoot = "C:\AIOps-Data"

# 创建所需目录
$Directories = @(
    "$DataRoot\postgres",
    "$DataRoot\redis", 
    "$DataRoot\prometheus",
    "$DataRoot\grafana",
    "$DataRoot\ai-models",
    "$DataRoot\ai-logs",
    "$DataRoot\traefik",
    "$DataRoot\node-exporter",
    "$DataRoot\cadvisor"
)

foreach ($Dir in $Directories) {
    if (!(Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir -Force
        Write-Host "✅ 已创建目录: $Dir" -ForegroundColor Green
    } else {
        Write-Host "📁 目录已存在: $Dir" -ForegroundColor Yellow
    }
}

# 设置目录权限
foreach ($Dir in $Directories) {
    $Acl = Get-Acl $Dir
    $AccessRule = New-Object System.Security.AccessControl.FileSystemAccessRule("Everyone", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $Acl.SetAccessRule($AccessRule)
    Set-Acl -Path $Dir -AclObject $Acl
}

Write-Host "🎉 本地数据目录创建完成!" -ForegroundColor Green
Write-Host "📍 数据根目录: $DataRoot" -ForegroundColor Cyan
```

#### Linux/macOS (Bash)

```bash
#!/bin/bash
# create-data-dirs.sh

# 设置数据根目录
DATA_ROOT="$HOME/aiops-data"

# 创建所需目录
directories=(
    "$DATA_ROOT/postgres"
    "$DATA_ROOT/redis"
    "$DATA_ROOT/prometheus"
    "$DATA_ROOT/grafana"
    "$DATA_ROOT/ai-models"
    "$DATA_ROOT/ai-logs"
    "$DATA_ROOT/traefik"
    "$DATA_ROOT/node-exporter"
    "$DATA_ROOT/cadvisor"
)

for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "✅ 已创建目录: $dir"
    else
        echo "📁 目录已存在: $dir"
    fi
done

# 设置目录权限
chmod -R 755 "$DATA_ROOT"
chown -R $(id -u):$(id -g) "$DATA_ROOT"

echo "🎉 本地数据目录创建完成!"
echo "📍 数据根目录: $DATA_ROOT"
```

### 3. 修改Docker Compose配置

创建本地持久化版本的 `docker-compose.local.yml`：

```yaml
# docker-compose.local.yml - 本地持久化配置
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    volumes:
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/postgres:/var/lib/postgresql/data
    environment:
      - PGDATA=/var/lib/postgresql/data/pgdata

  # Redis缓存
  redis:
    volumes:
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/redis:/data

  # Prometheus监控
  prometheus:
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=${PROMETHEUS_RETENTION_TIME:-30d}'
      - '--storage.tsdb.retention.size=${PROMETHEUS_STORAGE_RETENTION_SIZE:-10GB}'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'

  # Grafana仪表板
  grafana:
    volumes:
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/grafana:/var/lib/grafana
    user: "0:0"  # 以root用户运行以避免权限问题

  # AI引擎
  ai-engine:
    volumes:
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/ai-models:/app/models
      - ${DATA_PATH:-./data}/ai-logs:/app/logs

  # Traefik网关
  traefik:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/etc/traefik/traefik.yml:ro
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/traefik:/data

  # Node Exporter
  node-exporter:
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/node-exporter:/data

  # cAdvisor
  cadvisor:
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
      # 替换为本地目录挂载
      - ${DATA_PATH:-./data}/cadvisor:/data

# 移除volumes部分，因为我们使用本地目录挂载
# volumes:
#   postgres-data:
#   redis-data:
#   prometheus-data:
#   grafana-data:
#   ai-models:
#   ai-logs:
#   traefik-data:
#   node-exporter-data:
#   cadvisor-data:
```

### 4. 更新环境变量

在 `.env` 文件中添加本地数据路径配置：

```bash
# 本地持久化配置
# 取消注释并设置本地数据路径

# Windows示例
# DATA_PATH=C:/AIOps-Data

# Linux/macOS示例
# DATA_PATH=/home/username/aiops-data
# 或使用相对路径
DATA_PATH=./data

# 备份路径
BACKUP_PATH=${DATA_PATH}/backups

# 日志路径
LOGS_PATH=${DATA_PATH}/logs

# 配置路径
CONFIG_PATH=${DATA_PATH}/config
```

### 5. 数据迁移（可选）

如果您之前使用Docker卷存储数据，可以将数据迁移到本地目录：

#### Windows (PowerShell)

```powershell
# migrate-data.ps1 - 数据迁移脚本

$DataPath = "C:\AIOps-Data"

# 迁移函数
function Migrate-Volume {
    param(
        [string]$VolumeName,
        [string]$LocalPath
    )
    
    Write-Host "🔄 迁移卷 $VolumeName 到 $LocalPath..." -ForegroundColor Cyan
    
    # 检查卷是否存在
    $VolumeExists = docker volume ls --format "{{.Name}}" | Select-String -Pattern "^$VolumeName$"
    
    if ($VolumeExists) {
        # 创建临时容器进行数据复制
        docker run --rm -v "${VolumeName}:/source" -v "${LocalPath}:/target" alpine sh -c "cp -a /source/. /target/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ $VolumeName 迁移完成" -ForegroundColor Green
        } else {
            Write-Host "❌ $VolumeName 迁移失败" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ 卷 $VolumeName 不存在，跳过迁移" -ForegroundColor Yellow
    }
}

# 执行迁移
$Migrations = @{
    "aiops_postgres-data" = "$DataPath\postgres"
    "aiops_redis-data" = "$DataPath\redis"
    "aiops_prometheus-data" = "$DataPath\prometheus"
    "aiops_grafana-data" = "$DataPath\grafana"
    "aiops_ai-models" = "$DataPath\ai-models"
    "aiops_ai-logs" = "$DataPath\ai-logs"
}

foreach ($Volume in $Migrations.Keys) {
    Migrate-Volume -VolumeName $Volume -LocalPath $Migrations[$Volume]
}

Write-Host "🎉 数据迁移完成!" -ForegroundColor Green
```

#### Linux/macOS (Bash)

```bash
#!/bin/bash
# migrate-data.sh - 数据迁移脚本

DATA_PATH="$HOME/aiops-data"

# 迁移函数
migrate_volume() {
    local volume_name=$1
    local local_path=$2
    
    echo "🔄 迁移卷 $volume_name 到 $local_path..."
    
    # 检查卷是否存在
    if docker volume ls --format "{{.Name}}" | grep -q "^$volume_name$"; then
        # 创建临时容器进行数据复制
        docker run --rm -v "$volume_name:/source" -v "$local_path:/target" alpine sh -c "cp -a /source/. /target/"
        
        if [ $? -eq 0 ]; then
            echo "✅ $volume_name 迁移完成"
        else
            echo "❌ $volume_name 迁移失败"
        fi
    else
        echo "⚠️ 卷 $volume_name 不存在，跳过迁移"
    fi
}

# 执行迁移
declare -A migrations=(
    ["aiops_postgres-data"]="$DATA_PATH/postgres"
    ["aiops_redis-data"]="$DATA_PATH/redis"
    ["aiops_prometheus-data"]="$DATA_PATH/prometheus"
    ["aiops_grafana-data"]="$DATA_PATH/grafana"
    ["aiops_ai-models"]="$DATA_PATH/ai-models"
    ["aiops_ai-logs"]="$DATA_PATH/ai-logs"
)

for volume in "${!migrations[@]}"; do
    migrate_volume "$volume" "${migrations[$volume]}"
done

echo "🎉 数据迁移完成!"
```

### 6. 启动服务

使用本地持久化配置启动服务：

```bash
# 使用本地持久化配置启动
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

# 或者创建别名
alias aiops-local="docker-compose -f docker-compose.yml -f docker-compose.local.yml"
aiops-local up -d
```

## 管理脚本

### 本地数据备份脚本

#### Windows (PowerShell)

```powershell
# backup-local-data.ps1

param(
    [string]$BackupPath = "C:\AIOps-Backups",
    [switch]$Compress = $false
)

$DataPath = "C:\AIOps-Data"
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = "$BackupPath\aiops-backup-$Timestamp"

# 创建备份目录
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

Write-Host "💾 开始备份本地数据..." -ForegroundColor Cyan
Write-Host "📁 备份目录: $BackupDir" -ForegroundColor Yellow

# 复制数据目录
Write-Host "📋 复制数据文件..." -ForegroundColor Green
robocopy $DataPath $BackupDir /E /R:3 /W:10 /MT:8 /LOG:"$BackupDir\backup.log"

# 备份配置文件
Write-Host "📄 备份配置文件..." -ForegroundColor Green
$ConfigFiles = @(".env", "docker-compose.yml", "docker-compose.local.yml", "prometheus.yml")
foreach ($File in $ConfigFiles) {
    if (Test-Path $File) {
        Copy-Item $File $BackupDir
        Write-Host "✅ 已备份: $File" -ForegroundColor Green
    }
}

# 压缩备份（可选）
if ($Compress) {
    Write-Host "🗜️ 压缩备份文件..." -ForegroundColor Green
    $ZipFile = "$BackupPath\aiops-backup-$Timestamp.zip"
    Compress-Archive -Path $BackupDir -DestinationPath $ZipFile
    Remove-Item -Path $BackupDir -Recurse -Force
    Write-Host "✅ 备份已压缩: $ZipFile" -ForegroundColor Green
}

Write-Host "🎉 备份完成!" -ForegroundColor Green
```

#### Linux/macOS (Bash)

```bash
#!/bin/bash
# backup-local-data.sh

DATA_PATH="$HOME/aiops-data"
BACKUP_PATH="$HOME/aiops-backups"
COMPRESS=false

# 参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup-path)
            BACKUP_PATH="$2"
            shift 2
            ;;
        --compress)
            COMPRESS=true
            shift
            ;;
        *)
            echo "用法: $0 [--backup-path PATH] [--compress]"
            exit 1
            ;;
    esac
done

TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
BACKUP_DIR="$BACKUP_PATH/aiops-backup-$TIMESTAMP"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "💾 开始备份本地数据..."
echo "📁 备份目录: $BACKUP_DIR"

# 复制数据目录
echo "📋 复制数据文件..."
cp -r "$DATA_PATH"/* "$BACKUP_DIR/"

# 备份配置文件
echo "📄 备份配置文件..."
config_files=(".env" "docker-compose.yml" "docker-compose.local.yml" "prometheus.yml")
for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "✅ 已备份: $file"
    fi
done

# 压缩备份（可选）
if [ "$COMPRESS" = true ]; then
    echo "🗜️ 压缩备份文件..."
    tar czf "$BACKUP_PATH/aiops-backup-$TIMESTAMP.tar.gz" -C "$BACKUP_PATH" "$(basename "$BACKUP_DIR")"
    rm -rf "$BACKUP_DIR"
    echo "✅ 备份已压缩: $BACKUP_PATH/aiops-backup-$TIMESTAMP.tar.gz"
fi

echo "🎉 备份完成!"
```

## 注意事项

### 1. 权限问题

- **Linux/macOS**: 确保数据目录具有正确的权限（755或777）
- **Windows**: 确保Docker Desktop有权访问数据目录
- 某些服务可能需要特定的用户ID，请根据需要调整

### 2. 性能考虑

- 本地目录挂载的性能可能不如Docker卷
- 在Windows上，建议将数据目录放在SSD上
- 避免将数据目录放在网络驱动器上

### 3. 备份策略

- 定期备份数据目录
- 考虑使用增量备份以节省空间
- 测试备份恢复流程

### 4. 安全性

- 确保数据目录的访问权限设置正确
- 考虑对敏感数据进行加密
- 定期更新访问凭据

## 故障排除

### 常见问题

1. **权限被拒绝错误**
   ```bash
   # Linux/macOS
   sudo chown -R $(id -u):$(id -g) /path/to/data
   chmod -R 755 /path/to/data
   ```

2. **Windows路径问题**
   - 使用正斜杠 `/` 而不是反斜杠 `\`
   - 确保路径不包含空格或特殊字符

3. **数据库初始化失败**
   - 确保PostgreSQL数据目录为空或包含有效数据
   - 检查PGDATA环境变量设置

4. **Grafana权限问题**
   ```bash
   # 设置Grafana数据目录权限
   sudo chown -R 472:472 /path/to/grafana/data
   ```

## 回滚到Docker卷

如果需要回滚到Docker卷存储：

1. 停止服务：`docker-compose down`
2. 备份本地数据（可选）
3. 使用原始配置启动：`docker-compose up -d`
4. 如需迁移数据，反向执行迁移脚本

---

**注意**: 本地持久化配置需要更多的手动管理，请确保您了解相关的维护工作。如无特殊需求，建议使用默认的Docker卷配置。