<#
.SYNOPSIS
    AIOps平台配置生成脚本 (PowerShell)

.DESCRIPTION
    本脚本用于根据环境参数和用户配置生成Docker Compose和Kubernetes配置文件。
    支持自定义配置、环境变量替换、密钥生成等功能。

.PARAMETER ConfigType
    配置类型：docker-compose 或 kubernetes

.PARAMETER Environment
    部署环境：development, staging, production

.PARAMETER OutputPath
    输出路径，默认为项目根目录

.PARAMETER ConfigFile
    自定义配置文件路径

.PARAMETER Force
    强制覆盖已存在的配置文件

.EXAMPLE
    .\generate-config.ps1 -ConfigType docker-compose -Environment development
    .\generate-config.ps1 -ConfigType kubernetes -Environment production -Force

.NOTES
    版本: 1.0.0
    作者: AIOps Team
    创建日期: 2024-01-01
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("docker-compose", "kubernetes", "both")]
    [string]$ConfigType,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "development",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = "",
    
    [Parameter(Mandatory=$false)]
    [string]$ConfigFile = "",
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

# 设置错误处理
$ErrorActionPreference = "Stop"

# 全局变量
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot
$script:ConfigData = @{}
$script:GeneratedSecrets = @{}

# 默认配置
$script:DefaultConfig = @{
    # 基础配置
    project_name = "aiops"
    namespace = "aiops"
    domain = "aiops.local"
    
    # 网络配置
    network = @{
        subnet = "172.20.0.0/16"
        gateway = "172.20.0.1"
    }
    
    # 服务配置
    services = @{
        traefik = @{
            enabled = $true
            replicas = 1
            image = "traefik:v3.0"
            ports = @{
                web = 80
                websecure = 443
                dashboard = 8080
            }
            resources = @{
                requests = @{ cpu = "100m"; memory = "128Mi" }
                limits = @{ cpu = "500m"; memory = "512Mi" }
            }
        }
        
        prometheus = @{
            enabled = $true
            replicas = 1
            image = "prom/prometheus:latest"
            port = 9090
            retention = "15d"
            storage_size = "50Gi"
            resources = @{
                requests = @{ cpu = "200m"; memory = "512Mi" }
                limits = @{ cpu = "1000m"; memory = "2Gi" }
            }
        }
        
        grafana = @{
            enabled = $true
            replicas = 1
            image = "grafana/grafana:latest"
            port = 3000
            storage_size = "10Gi"
            resources = @{
                requests = @{ cpu = "100m"; memory = "256Mi" }
                limits = @{ cpu = "500m"; memory = "1Gi" }
            }
        }
        
        alertmanager = @{
            enabled = $true
            replicas = 1
            image = "prom/alertmanager:latest"
            port = 9093
            storage_size = "5Gi"
            resources = @{
                requests = @{ cpu = "50m"; memory = "128Mi" }
                limits = @{ cpu = "200m"; memory = "512Mi" }
            }
        }
        
        elasticsearch = @{
            enabled = $true
            replicas = 3
            image = "docker.elastic.co/elasticsearch/elasticsearch:8.11.0"
            port = 9200
            storage_size = "100Gi"
            heap_size = "2g"
            resources = @{
                requests = @{ cpu = "500m"; memory = "2Gi" }
                limits = @{ cpu = "2000m"; memory = "4Gi" }
            }
        }
        
        logstash = @{
            enabled = $true
            replicas = 2
            image = "docker.elastic.co/logstash/logstash:8.11.0"
            port = 5044
            heap_size = "1g"
            resources = @{
                requests = @{ cpu = "200m"; memory = "1Gi" }
                limits = @{ cpu = "1000m"; memory = "2Gi" }
            }
        }
        
        kibana = @{
            enabled = $true
            replicas = 1
            image = "docker.elastic.co/kibana/kibana:8.11.0"
            port = 5601
            resources = @{
                requests = @{ cpu = "200m"; memory = "512Mi" }
                limits = @{ cpu = "1000m"; memory = "2Gi" }
            }
        }
        
        redis = @{
            enabled = $true
            replicas = 1
            image = "redis:7-alpine"
            port = 6379
            storage_size = "10Gi"
            resources = @{
                requests = @{ cpu = "100m"; memory = "256Mi" }
                limits = @{ cpu = "500m"; memory = "1Gi" }
            }
        }
        
        postgresql = @{
            enabled = $true
            replicas = 1
            image = "postgres:15-alpine"
            port = 5432
            storage_size = "50Gi"
            resources = @{
                requests = @{ cpu = "200m"; memory = "512Mi" }
                limits = @{ cpu = "1000m"; memory = "2Gi" }
            }
        }
        
        ai_engine = @{
            enabled = $true
            replicas = 2
            image = "aiops/ai-engine:latest"
            port = 8000
            resources = @{
                requests = @{ cpu = "500m"; memory = "1Gi" }
                limits = @{ cpu = "2000m"; memory = "4Gi" }
            }
        }
        
        api_gateway = @{
            enabled = $true
            replicas = 2
            image = "aiops/api-gateway:latest"
            port = 8080
            resources = @{
                requests = @{ cpu = "200m"; memory = "512Mi" }
                limits = @{ cpu = "1000m"; memory = "2Gi" }
            }
        }
        
        self_healing = @{
            enabled = $true
            replicas = 1
            image = "aiops/self-healing:latest"
            port = 8090
            resources = @{
                requests = @{ cpu = "200m"; memory = "512Mi" }
                limits = @{ cpu = "1000m"; memory = "2Gi" }
            }
        }
    }
    
    # 环境特定配置
    environments = @{
        development = @{
            debug = $true
            log_level = "DEBUG"
            replicas_multiplier = 1
            storage_class = "standard"
            ingress_class = "traefik"
        }
        
        staging = @{
            debug = $false
            log_level = "INFO"
            replicas_multiplier = 1
            storage_class = "fast-ssd"
            ingress_class = "nginx"
        }
        
        production = @{
            debug = $false
            log_level = "WARN"
            replicas_multiplier = 2
            storage_class = "fast-ssd"
            ingress_class = "nginx"
        }
    }
}

# 生成随机密码
function New-RandomPassword {
    param(
        [int]$Length = 32,
        [switch]$IncludeSymbols
    )
    
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    if ($IncludeSymbols) {
        $chars += "!@#$%^&*"
    }
    
    $password = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    
    return $password
}

# 生成JWT密钥
function New-JWTSecret {
    $bytes = New-Object byte[] 32
    [System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes($bytes)
    return [Convert]::ToBase64String($bytes)
}

# 生成所有必需的密钥
function Initialize-Secrets {
    Write-Host "生成安全密钥..." -ForegroundColor Yellow
    
    $script:GeneratedSecrets = @{
        # 数据库密码
        postgres_password = New-RandomPassword -Length 24
        redis_password = New-RandomPassword -Length 24
        
        # Elasticsearch密码
        elastic_password = New-RandomPassword -Length 24
        kibana_password = New-RandomPassword -Length 24
        
        # Grafana密码
        grafana_admin_password = New-RandomPassword -Length 16
        
        # API密钥
        api_key = New-RandomPassword -Length 32 -IncludeSymbols
        jwt_secret = New-JWTSecret
        
        # Webhook密钥
        webhook_secret = New-RandomPassword -Length 32
        
        # SMTP配置（示例）
        smtp_password = New-RandomPassword -Length 16
        
        # Slack Webhook（占位符）
        slack_webhook_url = "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
        
        # Traefik Dashboard认证
        traefik_dashboard_user = "admin"
        traefik_dashboard_password = New-RandomPassword -Length 16
    }
    
    Write-Host "密钥生成完成" -ForegroundColor Green
}

# 加载自定义配置
function Import-CustomConfig {
    param([string]$ConfigFilePath)
    
    if ([string]::IsNullOrEmpty($ConfigFilePath)) {
        $ConfigFilePath = Join-Path $script:ProjectRoot "config\aiops-config.json"
    }
    
    if (Test-Path $ConfigFilePath) {
        Write-Host "加载自定义配置: $ConfigFilePath" -ForegroundColor Yellow
        
        try {
            $customConfig = Get-Content $ConfigFilePath -Raw | ConvertFrom-Json -AsHashtable
            
            # 合并配置
            foreach ($key in $customConfig.Keys) {
                if ($script:DefaultConfig.ContainsKey($key)) {
                    if ($customConfig[$key] -is [hashtable] -and $script:DefaultConfig[$key] -is [hashtable]) {
                        # 递归合并哈希表
                        $script:DefaultConfig[$key] = Merge-Hashtables $script:DefaultConfig[$key] $customConfig[$key]
                    } else {
                        $script:DefaultConfig[$key] = $customConfig[$key]
                    }
                } else {
                    $script:DefaultConfig[$key] = $customConfig[$key]
                }
            }
            
            Write-Host "自定义配置加载完成" -ForegroundColor Green
        } catch {
            Write-Warning "加载自定义配置失败: $($_.Exception.Message)"
        }
    } else {
        Write-Host "未找到自定义配置文件，使用默认配置" -ForegroundColor Gray
    }
}

# 合并哈希表
function Merge-Hashtables {
    param(
        [hashtable]$Target,
        [hashtable]$Source
    )
    
    $result = $Target.Clone()
    
    foreach ($key in $Source.Keys) {
        if ($result.ContainsKey($key)) {
            if ($Source[$key] -is [hashtable] -and $result[$key] -is [hashtable]) {
                $result[$key] = Merge-Hashtables $result[$key] $Source[$key]
            } else {
                $result[$key] = $Source[$key]
            }
        } else {
            $result[$key] = $Source[$key]
        }
    }
    
    return $result
}

# 应用环境特定配置
function Apply-EnvironmentConfig {
    param([string]$EnvironmentName)
    
    if ($script:DefaultConfig.environments.ContainsKey($EnvironmentName)) {
        $envConfig = $script:DefaultConfig.environments[$EnvironmentName]
        
        Write-Host "应用环境配置: $EnvironmentName" -ForegroundColor Yellow
        
        # 应用副本数乘数
        if ($envConfig.ContainsKey("replicas_multiplier")) {
            $multiplier = $envConfig.replicas_multiplier
            
            foreach ($serviceName in $script:DefaultConfig.services.Keys) {
                $service = $script:DefaultConfig.services[$serviceName]
                if ($service.ContainsKey("replicas")) {
                    $service.replicas = [math]::Max(1, $service.replicas * $multiplier)
                }
            }
        }
        
        # 应用其他环境配置
        $script:ConfigData = @{
            environment = $EnvironmentName
            debug = $envConfig.debug
            log_level = $envConfig.log_level
            storage_class = $envConfig.storage_class
            ingress_class = $envConfig.ingress_class
        }
        
        Write-Host "环境配置应用完成" -ForegroundColor Green
    } else {
        Write-Warning "未找到环境配置: $EnvironmentName"
    }
}

# 生成Docker Compose配置
function New-DockerComposeConfig {
    param([string]$OutputDir)
    
    Write-Host "生成Docker Compose配置..." -ForegroundColor Yellow
    
    $composeFile = Join-Path $OutputDir "docker-compose.yml"
    $envFile = Join-Path $OutputDir ".env"
    
    # 生成.env文件
    $envContent = @"
# AIOps平台环境变量
# 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# 环境: $Environment

# 项目配置
PROJECT_NAME=$($script:DefaultConfig.project_name)
ENVIRONMENT=$Environment
DOMAIN=$($script:DefaultConfig.domain)

# 网络配置
NETWORK_SUBNET=$($script:DefaultConfig.network.subnet)
NETWORK_GATEWAY=$($script:DefaultConfig.network.gateway)

# 数据库配置
POSTGRES_DB=aiops
POSTGRES_USER=aiops
POSTGRES_PASSWORD=$($script:GeneratedSecrets.postgres_password)

# Redis配置
REDIS_PASSWORD=$($script:GeneratedSecrets.redis_password)

# Elasticsearch配置
ELASTIC_PASSWORD=$($script:GeneratedSecrets.elastic_password)
KIBANA_PASSWORD=$($script:GeneratedSecrets.kibana_password)

# Grafana配置
GF_SECURITY_ADMIN_PASSWORD=$($script:GeneratedSecrets.grafana_admin_password)

# API配置
API_KEY=$($script:GeneratedSecrets.api_key)
JWT_SECRET=$($script:GeneratedSecrets.jwt_secret)

# Webhook配置
WEBHOOK_SECRET=$($script:GeneratedSecrets.webhook_secret)

# 通知配置
SMTP_PASSWORD=$($script:GeneratedSecrets.smtp_password)
SLACK_WEBHOOK_URL=$($script:GeneratedSecrets.slack_webhook_url)

# Traefik配置
TRAEFIK_DASHBOARD_USER=$($script:GeneratedSecrets.traefik_dashboard_user)
TRAEFIK_DASHBOARD_PASSWORD=$($script:GeneratedSecrets.traefik_dashboard_password)

# 日志级别
LOG_LEVEL=$($script:ConfigData.log_level)
DEBUG=$($script:ConfigData.debug.ToString().ToLower())
"@
    
    Set-Content -Path $envFile -Value $envContent -Encoding UTF8
    
    # 生成docker-compose.yml
    $composeContent = @"
version: '3.8'

networks:
  aiops-network:
    driver: bridge
    ipam:
      config:
        - subnet: `${NETWORK_SUBNET}
          gateway: `${NETWORK_GATEWAY}

volumes:
  prometheus-data:
  grafana-data:
  alertmanager-data:
  elasticsearch-data:
  redis-data:
  postgres-data:

services:
"@
    
    # 添加各个服务
    foreach ($serviceName in $script:DefaultConfig.services.Keys) {
        $service = $script:DefaultConfig.services[$serviceName]
        
        if ($service.enabled) {
            $composeContent += "`n`n  $serviceName:`n"
            $composeContent += "    image: $($service.image)`n"
            $composeContent += "    container_name: `${PROJECT_NAME}-$serviceName`n"
            $composeContent += "    restart: unless-stopped`n"
            $composeContent += "    networks:`n      - aiops-network`n"
            
            # 添加端口映射
            if ($service.ContainsKey("port")) {
                $composeContent += "    ports:`n      - `"$($service.port):$($service.port)`"`n"
            } elseif ($service.ContainsKey("ports")) {
                $composeContent += "    ports:`n"
                foreach ($portName in $service.ports.Keys) {
                    $port = $service.ports[$portName]
                    $composeContent += "      - `"$port:$port`"`n"
                }
            }
            
            # 添加环境变量
            $composeContent += "    environment:`n"
            
            switch ($serviceName) {
                "traefik" {
                    $composeContent += "      - TRAEFIK_API_DASHBOARD=true`n"
                    $composeContent += "      - TRAEFIK_API_INSECURE=true`n"
                }
                
                "prometheus" {
                    $composeContent += "      - PROMETHEUS_RETENTION_TIME=$($service.retention)`n"
                }
                
                "grafana" {
                    $composeContent += "      - GF_SECURITY_ADMIN_PASSWORD=`${GF_SECURITY_ADMIN_PASSWORD}`n"
                }
                
                "elasticsearch" {
                    $composeContent += "      - discovery.type=single-node`n"
                    $composeContent += "      - ES_JAVA_OPTS=-Xms$($service.heap_size) -Xmx$($service.heap_size)`n"
                    $composeContent += "      - ELASTIC_PASSWORD=`${ELASTIC_PASSWORD}`n"
                }
                
                "redis" {
                    $composeContent += "      - REDIS_PASSWORD=`${REDIS_PASSWORD}`n"
                }
                
                "postgresql" {
                    $composeContent += "      - POSTGRES_DB=`${POSTGRES_DB}`n"
                    $composeContent += "      - POSTGRES_USER=`${POSTGRES_USER}`n"
                    $composeContent += "      - POSTGRES_PASSWORD=`${POSTGRES_PASSWORD}`n"
                }
                
                default {
                    $composeContent += "      - LOG_LEVEL=`${LOG_LEVEL}`n"
                    $composeContent += "      - DEBUG=`${DEBUG}`n"
                }
            }
            
            # 添加卷挂载
            if ($serviceName -in @("prometheus", "grafana", "alertmanager", "elasticsearch", "redis", "postgresql")) {
                $composeContent += "    volumes:`n"
                $composeContent += "      - $serviceName-data:/data`n"
            }
        }
    }
    
    Set-Content -Path $composeFile -Value $composeContent -Encoding UTF8
    
    Write-Host "Docker Compose配置生成完成:" -ForegroundColor Green
    Write-Host "  - $composeFile" -ForegroundColor Gray
    Write-Host "  - $envFile" -ForegroundColor Gray
}

# 生成Kubernetes配置
function New-KubernetesConfig {
    param([string]$OutputDir)
    
    Write-Host "生成Kubernetes配置..." -ForegroundColor Yellow
    
    $k8sDir = Join-Path $OutputDir "k8s"
    if (!(Test-Path $k8sDir)) {
        New-Item -ItemType Directory -Path $k8sDir -Force | Out-Null
    }
    
    # 生成values.yaml文件
    $valuesFile = Join-Path $k8sDir "values.yaml"
    
    $valuesContent = @"
# AIOps平台Helm Values
# 生成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# 环境: $Environment

global:
  environment: $Environment
  namespace: $($script:DefaultConfig.namespace)
  domain: $($script:DefaultConfig.domain)
  storageClass: $($script:ConfigData.storage_class)
  ingressClass: $($script:ConfigData.ingress_class)
  debug: $($script:ConfigData.debug.ToString().ToLower())
  logLevel: $($script:ConfigData.log_level)

# 服务配置
"@
    
    foreach ($serviceName in $script:DefaultConfig.services.Keys) {
        $service = $script:DefaultConfig.services[$serviceName]
        
        $valuesContent += "`n$serviceName:`n"
        $valuesContent += "  enabled: $($service.enabled.ToString().ToLower())`n"
        $valuesContent += "  replicaCount: $($service.replicas)`n"
        $valuesContent += "  image:`n"
        $valuesContent += "    repository: $($service.image.Split(':')[0])`n"
        $valuesContent += "    tag: $($service.image.Split(':')[1])`n"
        $valuesContent += "    pullPolicy: IfNotPresent`n"
        
        if ($service.ContainsKey("resources")) {
            $valuesContent += "  resources:`n"
            $valuesContent += "    requests:`n"
            $valuesContent += "      cpu: $($service.resources.requests.cpu)`n"
            $valuesContent += "      memory: $($service.resources.requests.memory)`n"
            $valuesContent += "    limits:`n"
            $valuesContent += "      cpu: $($service.resources.limits.cpu)`n"
            $valuesContent += "      memory: $($service.resources.limits.memory)`n"
        }
        
        if ($service.ContainsKey("storage_size")) {
            $valuesContent += "  persistence:`n"
            $valuesContent += "    enabled: true`n"
            $valuesContent += "    size: $($service.storage_size)`n"
        }
    }
    
    # 添加密钥配置
    $valuesContent += "`n# 密钥配置`n"
    $valuesContent += "secrets:`n"
    foreach ($secretName in $script:GeneratedSecrets.Keys) {
        $valuesContent += "  $secretName: `"$($script:GeneratedSecrets[$secretName])`"`n"
    }
    
    Set-Content -Path $valuesFile -Value $valuesContent -Encoding UTF8
    
    # 生成kustomization.yaml
    $kustomizationFile = Join-Path $k8sDir "kustomization.yaml"
    
    $kustomizationContent = @"
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: $($script:DefaultConfig.namespace)

resources:
  - ../helm/templates/

commonLabels:
  app.kubernetes.io/name: aiops
  app.kubernetes.io/instance: aiops-$Environment
  app.kubernetes.io/version: "1.0.0"
  app.kubernetes.io/managed-by: kustomize
  environment: $Environment

replicas:
"@
    
    foreach ($serviceName in $script:DefaultConfig.services.Keys) {
        $service = $script:DefaultConfig.services[$serviceName]
        if ($service.enabled) {
            $kustomizationContent += "`n  - name: $serviceName`n    count: $($service.replicas)"
        }
    }
    
    Set-Content -Path $kustomizationFile -Value $kustomizationContent -Encoding UTF8
    
    Write-Host "Kubernetes配置生成完成:" -ForegroundColor Green
    Write-Host "  - $valuesFile" -ForegroundColor Gray
    Write-Host "  - $kustomizationFile" -ForegroundColor Gray
}

# 生成配置摘要
function New-ConfigSummary {
    param([string]$OutputDir)
    
    $summaryFile = Join-Path $OutputDir "config-summary.md"
    
    $summaryContent = @"
# AIOps平台配置摘要

**生成时间**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**环境**: $Environment
**配置类型**: $ConfigType

## 基础配置

- **项目名称**: $($script:DefaultConfig.project_name)
- **命名空间**: $($script:DefaultConfig.namespace)
- **域名**: $($script:DefaultConfig.domain)
- **调试模式**: $($script:ConfigData.debug)
- **日志级别**: $($script:ConfigData.log_level)

## 服务配置

| 服务名称 | 启用状态 | 副本数 | 镜像 | 端口 |
|---------|---------|-------|------|------|
"@
    
    foreach ($serviceName in $script:DefaultConfig.services.Keys) {
        $service = $script:DefaultConfig.services[$serviceName]
        $port = if ($service.ContainsKey("port")) { $service.port } elseif ($service.ContainsKey("ports")) { ($service.ports.Values -join ", ") } else { "N/A" }
        
        $summaryContent += "| $serviceName | $($service.enabled) | $($service.replicas) | $($service.image) | $port |`n"
    }
    
    $summaryContent += "`n## 生成的密钥`n`n"
    $summaryContent += "以下密钥已自动生成，请妥善保管：`n`n"
    
    foreach ($secretName in $script:GeneratedSecrets.Keys) {
        if ($secretName -notlike "*password*" -and $secretName -ne "jwt_secret") {
            $summaryContent += "- **$secretName**: $($script:GeneratedSecrets[$secretName])`n"
        } else {
            $summaryContent += "- **$secretName**: [已生成，长度 $($script:GeneratedSecrets[$secretName].Length) 字符]`n"
        }
    }
    
    $summaryContent += "`n## 安全注意事项`n`n"
    $summaryContent += "1. 请立即更改所有默认密码`n"
    $summaryContent += "2. 在生产环境中使用强密码和证书`n"
    $summaryContent += "3. 定期轮换密钥和证书`n"
    $summaryContent += "4. 限制网络访问和端口暴露`n"
    $summaryContent += "5. 启用审计日志和监控`n"
    
    $summaryContent += "`n## 下一步操作`n`n"
    
    if ($ConfigType -eq "docker-compose" -or $ConfigType -eq "both") {
        $summaryContent += "### Docker Compose部署`n`n"
        $summaryContent += "\`\`\`bash`n"
        $summaryContent += "# 启动服务`n"
        $summaryContent += "docker-compose up -d`n`n"
        $summaryContent += "# 查看服务状态`n"
        $summaryContent += "docker-compose ps`n`n"
        $summaryContent += "# 查看日志`n"
        $summaryContent += "docker-compose logs -f`n"
        $summaryContent += "\`\`\``n`n"
    }
    
    if ($ConfigType -eq "kubernetes" -or $ConfigType -eq "both") {
        $summaryContent += "### Kubernetes部署`n`n"
        $summaryContent += "\`\`\`bash`n"
        $summaryContent += "# 使用Helm部署`n"
        $summaryContent += "helm install aiops ./helm -f k8s/values.yaml`n`n"
        $summaryContent += "# 或使用Kustomize部署`n"
        $summaryContent += "kubectl apply -k k8s/`n`n"
        $summaryContent += "# 查看部署状态`n"
        $summaryContent += "kubectl get pods -n $($script:DefaultConfig.namespace)`n"
        $summaryContent += "\`\`\``n`n"
    }
    
    Set-Content -Path $summaryFile -Value $summaryContent -Encoding UTF8
    
    Write-Host "配置摘要生成完成: $summaryFile" -ForegroundColor Green
}

# 主函数
function Main {
    Write-Host "AIOps平台配置生成工具" -ForegroundColor Green
    Write-Host "配置类型: $ConfigType" -ForegroundColor White
    Write-Host "环境: $Environment" -ForegroundColor White
    Write-Host "开始时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
    
    # 设置输出路径
    if ([string]::IsNullOrEmpty($OutputPath)) {
        $OutputPath = Join-Path $script:ProjectRoot "generated\$Environment"
    }
    
    # 创建输出目录
    if (!(Test-Path $OutputPath)) {
        New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        Write-Host "创建输出目录: $OutputPath" -ForegroundColor Gray
    } elseif (!$Force) {
        $response = Read-Host "输出目录已存在，是否覆盖？(y/N)"
        if ($response -ne "y" -and $response -ne "Y") {
            Write-Host "操作已取消" -ForegroundColor Yellow
            return
        }
    }
    
    try {
        # 初始化
        Initialize-Secrets
        Import-CustomConfig -ConfigFilePath $ConfigFile
        Apply-EnvironmentConfig -EnvironmentName $Environment
        
        # 生成配置
        switch ($ConfigType) {
            "docker-compose" {
                New-DockerComposeConfig -OutputDir $OutputPath
            }
            
            "kubernetes" {
                New-KubernetesConfig -OutputDir $OutputPath
            }
            
            "both" {
                New-DockerComposeConfig -OutputDir $OutputPath
                New-KubernetesConfig -OutputDir $OutputPath
            }
        }
        
        # 生成摘要
        New-ConfigSummary -OutputDir $OutputPath
        
        Write-Host "`n配置生成完成！" -ForegroundColor Green
        Write-Host "输出目录: $OutputPath" -ForegroundColor Cyan
        
    } catch {
        Write-Error "配置生成失败: $($_.Exception.Message)"
        Write-Error $_.ScriptStackTrace
        exit 1
    }
    
    Write-Host "完成时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White
}

# 执行主函数
Main