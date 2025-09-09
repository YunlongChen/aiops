<#
.SYNOPSIS
    ELK配置生成模块
.DESCRIPTION
    提供各种ELK安全配置文件的生成功能，包括Docker配置、Kubernetes配置等
.AUTHOR
    AI Assistant
.DATE
    $(Get-Date -Format 'yyyy-MM-dd')
#>

# 导入通用模块
. "$PSScriptRoot\security-common.ps1"

<#
.SYNOPSIS
    生成Docker Compose配置
#>
function New-DockerComposeConfig {
    param(
        [string]$OutputPath = "docker-compose.yml",
        [bool]$EnableSecurity = $true,
        [hashtable]$CustomSettings = @{}
    )
    
    Write-Log "生成Docker Compose配置" "INFO"
    
    try {
        $securityConfig = if ($EnableSecurity) {
            @"
      - xpack.security.enabled=true
      - xpack.security.http.ssl.enabled=true
      - xpack.security.transport.ssl.enabled=true
      - xpack.security.http.ssl.keystore.path=certs/elasticsearch/elasticsearch.p12
      - xpack.security.transport.ssl.keystore.path=certs/elasticsearch/elasticsearch.p12
"@
        } else {
            "      - xpack.security.enabled=false"
        }
        
        $dockerCompose = @"
# ELK Stack Docker Compose配置
# 生成时间: $(Get-Date)
# 安全模式: $($EnableSecurity ? '启用' : '禁用')

version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    hostname: elasticsearch
    environment:
      - node.name=elasticsearch-node-1
      - cluster.name=elk-cluster
      - discovery.type=single-node
      - bootstrap.memory_lock=true
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
$securityConfig
      - cluster.routing.allocation.disk.threshold_enabled=false
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
      - elasticsearch_logs:/usr/share/elasticsearch/logs
      - ./config/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml:ro
$(if ($EnableSecurity) { "      - ./certs:/usr/share/elasticsearch/config/certs:ro" })
    ports:
      - "9200:9200"
      - "9300:9300"
    networks:
      - elk-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f $(if ($EnableSecurity) { 'https' } else { 'http' })://localhost:9200/_cluster/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    hostname: kibana
    environment:
      - SERVERNAME=kibana
      - ELASTICSEARCH_HOSTS=$(if ($EnableSecurity) { 'https' } else { 'http' })://elasticsearch:9200
$(if ($EnableSecurity) {
@"
      - ELASTICSEARCH_USERNAME=kibana_system
      - ELASTICSEARCH_PASSWORD=$($Global:DefaultPasswords.kibana_system)
      - SERVER_SSL_ENABLED=true
      - SERVER_SSL_CERTIFICATE=config/certs/kibana/kibana.crt
      - SERVER_SSL_KEY=config/certs/kibana/kibana.key
"@
})
      - XPACK_SECURITY_ENABLED=$($EnableSecurity.ToString().ToLower())
      - XPACK_ENCRYPTEDSAVEDOBJECTS_ENCRYPTIONKEY=$(New-RandomPassword -Length 32)
    volumes:
      - kibana_data:/usr/share/kibana/data
      - ./config/kibana/kibana.yml:/usr/share/kibana/config/kibana.yml:ro
$(if ($EnableSecurity) { "      - ./certs:/usr/share/kibana/config/certs:ro" })
    ports:
      - "5601:5601"
    networks:
      - elk-network
    depends_on:
      elasticsearch:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f $(if ($EnableSecurity) { 'https' } else { 'http' })://localhost:5601/api/status || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: logstash
    hostname: logstash
    environment:
      - "LS_JAVA_OPTS=-Xms1g -Xmx1g"
      - XPACK_MONITORING_ENABLED=true
$(if ($EnableSecurity) {
@"
      - XPACK_MONITORING_ELASTICSEARCH_HOSTS=https://elasticsearch:9200
      - XPACK_MONITORING_ELASTICSEARCH_USERNAME=logstash_system
      - XPACK_MONITORING_ELASTICSEARCH_PASSWORD=$($Global:DefaultPasswords.logstash_system)
"@
} else {
      "      - XPACK_MONITORING_ELASTICSEARCH_HOSTS=http://elasticsearch:9200"
})
    volumes:
      - logstash_data:/usr/share/logstash/data
      - logstash_logs:/usr/share/logstash/logs
      - ./config/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
      - ./config/logstash/pipelines.yml:/usr/share/logstash/config/pipelines.yml:ro
      - ./config/logstash/pipeline:/usr/share/logstash/pipeline:ro
$(if ($EnableSecurity) { "      - ./certs:/usr/share/logstash/config/certs:ro" })
    ports:
      - "5044:5044"  # Beats input
      - "5000:5000"  # TCP input
      - "9600:9600"  # API
    networks:
      - elk-network
    depends_on:
      elasticsearch:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9600/_node/stats || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.11.0
    container_name: filebeat
    hostname: filebeat
    user: root
    environment:
      - ELASTICSEARCH_HOSTS=$(if ($EnableSecurity) { 'https' } else { 'http' })://elasticsearch:9200
$(if ($EnableSecurity) {
@"
      - ELASTICSEARCH_USERNAME=beats_system
      - ELASTICSEARCH_PASSWORD=$($Global:DefaultPasswords.beats_system)
"@
})
    volumes:
      - ./config/beats/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
$(if ($EnableSecurity) { "      - ./certs:/usr/share/filebeat/certs:ro" })
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /var/log:/var/log:ro
      - filebeat_data:/usr/share/filebeat/data
    networks:
      - elk-network
    depends_on:
      - logstash
    restart: unless-stopped

  metricbeat:
    image: docker.elastic.co/beats/metricbeat:8.11.0
    container_name: metricbeat
    hostname: metricbeat
    user: root
    environment:
      - ELASTICSEARCH_HOSTS=$(if ($EnableSecurity) { 'https' } else { 'http' })://elasticsearch:9200
$(if ($EnableSecurity) {
@"
      - ELASTICSEARCH_USERNAME=beats_system
      - ELASTICSEARCH_PASSWORD=$($Global:DefaultPasswords.beats_system)
"@
})
    volumes:
      - ./config/beats/metricbeat.yml:/usr/share/metricbeat/metricbeat.yml:ro
$(if ($EnableSecurity) { "      - ./certs:/usr/share/metricbeat/certs:ro" })
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /sys/fs/cgroup:/hostfs/sys/fs/cgroup:ro
      - /proc:/hostfs/proc:ro
      - /:/hostfs:ro
      - metricbeat_data:/usr/share/metricbeat/data
    networks:
      - elk-network
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  elasticsearch_data:
    driver: local
  elasticsearch_logs:
    driver: local
  kibana_data:
    driver: local
  logstash_data:
    driver: local
  logstash_logs:
    driver: local
  filebeat_data:
    driver: local
  metricbeat_data:
    driver: local

networks:
  elk-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
"@
        
        # 应用自定义设置
        foreach ($key in $CustomSettings.Keys) {
            $dockerCompose = $dockerCompose -replace $key, $CustomSettings[$key]
        }
        
        $dockerCompose | Out-File -FilePath $OutputPath -Encoding UTF8
        Write-Log "Docker Compose配置已生成: $OutputPath" "INFO"
        
        return $true
    }
    catch {
        Write-Log "生成Docker Compose配置失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成Kubernetes配置
#>
function New-KubernetesConfig {
    param(
        [string]$OutputPath = "k8s",
        [bool]$EnableSecurity = $true,
        [string]$Namespace = "elk",
        [hashtable]$CustomSettings = @{}
    )
    
    Write-Log "生成Kubernetes配置" "INFO"
    
    try {
        # 确保输出目录存在
        if (-not (Test-Path $OutputPath)) {
            New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        }
        
        # 1. 生成Namespace配置
        $namespaceConfig = @"
apiVersion: v1
kind: Namespace
metadata:
  name: $Namespace
  labels:
    name: $Namespace
    app: elk-stack
"@
        
        $namespaceConfig | Out-File -FilePath "$OutputPath\namespace.yaml" -Encoding UTF8
        
        # 2. 生成ConfigMap配置
        $configMapConfig = @"
apiVersion: v1
kind: ConfigMap
metadata:
  name: elk-config
  namespace: $Namespace
data:
  elasticsearch.yml: |
    cluster.name: elk-cluster
    node.name: elasticsearch-node-1
    network.host: 0.0.0.0
    http.port: 9200
    transport.port: 9300
    discovery.type: single-node
$(if ($EnableSecurity) {
@"
    xpack.security.enabled: true
    xpack.security.transport.ssl.enabled: true
    xpack.security.http.ssl.enabled: true
"@
} else {
    "    xpack.security.enabled: false"
})
  
  kibana.yml: |
    server.name: kibana
    server.host: 0.0.0.0
    server.port: 5601
    elasticsearch.hosts: ["$(if ($EnableSecurity) { 'https' } else { 'http' })://elasticsearch:9200"]
$(if ($EnableSecurity) {
@"
    elasticsearch.username: kibana_system
    elasticsearch.password: $($Global:DefaultPasswords.kibana_system)
    xpack.security.enabled: true
"@
} else {
    "    xpack.security.enabled: false"
})
  
  logstash.yml: |
    node.name: logstash-node-1
    path.data: /usr/share/logstash/data
    pipeline.workers: 2
    pipeline.batch.size: 125
    xpack.monitoring.enabled: true
    xpack.monitoring.elasticsearch.hosts: ["$(if ($EnableSecurity) { 'https' } else { 'http' })://elasticsearch:9200"]
$(if ($EnableSecurity) {
@"
    xpack.monitoring.elasticsearch.username: logstash_system
    xpack.monitoring.elasticsearch.password: $($Global:DefaultPasswords.logstash_system)
"@
})
"@
        
        $configMapConfig | Out-File -FilePath "$OutputPath\configmap.yaml" -Encoding UTF8
        
        # 3. 生成Secret配置（如果启用安全）
        if ($EnableSecurity) {
            $secretConfig = @"
apiVersion: v1
kind: Secret
metadata:
  name: elk-passwords
  namespace: $Namespace
type: Opaque
data:
  elastic-password: $([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Global:DefaultPasswords.elastic)))
  kibana-password: $([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Global:DefaultPasswords.kibana_system)))
  logstash-password: $([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Global:DefaultPasswords.logstash_system)))
  beats-password: $([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Global:DefaultPasswords.beats_system)))
"@
            
            $secretConfig | Out-File -FilePath "$OutputPath\secret.yaml" -Encoding UTF8
        }
        
        # 4. 生成Elasticsearch Deployment
        $esDeployment = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: elasticsearch
  namespace: $Namespace
  labels:
    app: elasticsearch
spec:
  replicas: 1
  selector:
    matchLabels:
      app: elasticsearch
  template:
    metadata:
      labels:
        app: elasticsearch
    spec:
      containers:
      - name: elasticsearch
        image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
        ports:
        - containerPort: 9200
          name: http
        - containerPort: 9300
          name: transport
        env:
        - name: node.name
          value: elasticsearch-node-1
        - name: cluster.name
          value: elk-cluster
        - name: discovery.type
          value: single-node
        - name: ES_JAVA_OPTS
          value: "-Xms2g -Xmx2g"
$(if ($EnableSecurity) {
@"
        - name: ELASTIC_PASSWORD
          valueFrom:
            secretKeyRef:
              name: elk-passwords
              key: elastic-password
"@
})
        volumeMounts:
        - name: elasticsearch-config
          mountPath: /usr/share/elasticsearch/config/elasticsearch.yml
          subPath: elasticsearch.yml
        - name: elasticsearch-data
          mountPath: /usr/share/elasticsearch/data
$(if ($EnableSecurity) {
        "        - name: elasticsearch-certs\n          mountPath: /usr/share/elasticsearch/config/certs"
})
        resources:
          limits:
            memory: 4Gi
            cpu: 2000m
          requests:
            memory: 2Gi
            cpu: 1000m
      volumes:
      - name: elasticsearch-config
        configMap:
          name: elk-config
      - name: elasticsearch-data
        persistentVolumeClaim:
          claimName: elasticsearch-pvc
$(if ($EnableSecurity) {
@"
      - name: elasticsearch-certs
        secret:
          secretName: elk-certs
"@
})
---
apiVersion: v1
kind: Service
metadata:
  name: elasticsearch
  namespace: $Namespace
  labels:
    app: elasticsearch
spec:
  selector:
    app: elasticsearch
  ports:
  - name: http
    port: 9200
    targetPort: 9200
  - name: transport
    port: 9300
    targetPort: 9300
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: elasticsearch-pvc
  namespace: $Namespace
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
"@
        
        $esDeployment | Out-File -FilePath "$OutputPath\elasticsearch.yaml" -Encoding UTF8
        
        # 5. 生成Kibana Deployment
        $kibanaDeployment = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kibana
  namespace: $Namespace
  labels:
    app: kibana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kibana
  template:
    metadata:
      labels:
        app: kibana
    spec:
      containers:
      - name: kibana
        image: docker.elastic.co/kibana/kibana:8.11.0
        ports:
        - containerPort: 5601
          name: http
        env:
        - name: SERVERNAME
          value: kibana
        - name: ELASTICSEARCH_HOSTS
          value: "$(if ($EnableSecurity) { 'https' } else { 'http' })://elasticsearch:9200"
$(if ($EnableSecurity) {
@"
        - name: ELASTICSEARCH_USERNAME
          value: kibana_system
        - name: ELASTICSEARCH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: elk-passwords
              key: kibana-password
"@
})
        volumeMounts:
        - name: kibana-config
          mountPath: /usr/share/kibana/config/kibana.yml
          subPath: kibana.yml
$(if ($EnableSecurity) {
        "        - name: kibana-certs\n          mountPath: /usr/share/kibana/config/certs"
})
        resources:
          limits:
            memory: 2Gi
            cpu: 1000m
          requests:
            memory: 1Gi
            cpu: 500m
      volumes:
      - name: kibana-config
        configMap:
          name: elk-config
$(if ($EnableSecurity) {
@"
      - name: kibana-certs
        secret:
          secretName: elk-certs
"@
})
---
apiVersion: v1
kind: Service
metadata:
  name: kibana
  namespace: $Namespace
  labels:
    app: kibana
spec:
  selector:
    app: kibana
  ports:
  - name: http
    port: 5601
    targetPort: 5601
  type: LoadBalancer
"@
        
        $kibanaDeployment | Out-File -FilePath "$OutputPath\kibana.yaml" -Encoding UTF8
        
        # 6. 生成Logstash Deployment
        $logstashDeployment = @"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: logstash
  namespace: $Namespace
  labels:
    app: logstash
spec:
  replicas: 1
  selector:
    matchLabels:
      app: logstash
  template:
    metadata:
      labels:
        app: logstash
    spec:
      containers:
      - name: logstash
        image: docker.elastic.co/logstash/logstash:8.11.0
        ports:
        - containerPort: 5044
          name: beats
        - containerPort: 5000
          name: tcp
        - containerPort: 9600
          name: api
        env:
        - name: LS_JAVA_OPTS
          value: "-Xms1g -Xmx1g"
$(if ($EnableSecurity) {
@"
        - name: XPACK_MONITORING_ELASTICSEARCH_USERNAME
          value: logstash_system
        - name: XPACK_MONITORING_ELASTICSEARCH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: elk-passwords
              key: logstash-password
"@
})
        volumeMounts:
        - name: logstash-config
          mountPath: /usr/share/logstash/config/logstash.yml
          subPath: logstash.yml
        - name: logstash-pipeline
          mountPath: /usr/share/logstash/pipeline
$(if ($EnableSecurity) {
        "        - name: logstash-certs\n          mountPath: /usr/share/logstash/config/certs"
})
        resources:
          limits:
            memory: 2Gi
            cpu: 1000m
          requests:
            memory: 1Gi
            cpu: 500m
      volumes:
      - name: logstash-config
        configMap:
          name: elk-config
      - name: logstash-pipeline
        configMap:
          name: logstash-pipeline
$(if ($EnableSecurity) {
@"
      - name: logstash-certs
        secret:
          secretName: elk-certs
"@
})
---
apiVersion: v1
kind: Service
metadata:
  name: logstash
  namespace: $Namespace
  labels:
    app: logstash
spec:
  selector:
    app: logstash
  ports:
  - name: beats
    port: 5044
    targetPort: 5044
  - name: tcp
    port: 5000
    targetPort: 5000
  - name: api
    port: 9600
    targetPort: 9600
  type: ClusterIP
"@
        
        $logstashDeployment | Out-File -FilePath "$OutputPath\logstash.yaml" -Encoding UTF8
        
        Write-Log "Kubernetes配置已生成到目录: $OutputPath" "INFO"
        return $true
    }
    catch {
        Write-Log "生成Kubernetes配置失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成环境配置文件
#>
function New-EnvironmentConfig {
    param(
        [string]$Environment = "production",
        [string]$OutputPath = ".env",
        [bool]$EnableSecurity = $true
    )
    
    Write-Log "生成环境配置文件" "INFO"
    
    try {
        $envConfig = @"
# ELK Stack环境配置
# 环境: $Environment
# 生成时间: $(Get-Date)
# 安全模式: $($EnableSecurity ? '启用' : '禁用')

# 基础配置
COMPOSE_PROJECT_NAME=elk-stack
ELK_VERSION=8.11.0
ENVIRONMENT=$Environment

# 网络配置
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
KIBANA_HOST=kibana
KIBANA_PORT=5601
LOGSTASH_HOST=logstash
LOGSTASH_PORT=5044

# 资源配置
ES_JAVA_OPTS=-Xms2g -Xmx2g
LS_JAVA_OPTS=-Xms1g -Xmx1g

# 安全配置
SECURITY_ENABLED=$($EnableSecurity.ToString().ToLower())
$(if ($EnableSecurity) {
@"
ELASTIC_PASSWORD=$($Global:DefaultPasswords.elastic)
KIBANA_SYSTEM_PASSWORD=$($Global:DefaultPasswords.kibana_system)
LOGSTASH_SYSTEM_PASSWORD=$($Global:DefaultPasswords.logstash_system)
BEATS_SYSTEM_PASSWORD=$($Global:DefaultPasswords.beats_system)
REMOTE_MONITORING_USER_PASSWORD=$($Global:DefaultPasswords.remote_monitoring_user)
APM_SYSTEM_PASSWORD=$($Global:DefaultPasswords.apm_system)

# SSL配置
SSL_CERTIFICATE_PATH=./certs
SSL_VERIFICATION_MODE=certificate
"@
})

# 监控配置
MONITORING_ENABLED=true
LOGGING_LEVEL=info

# 数据持久化
DATA_PATH_HOST=./data
LOGS_PATH_HOST=./logs

# 备份配置
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"
BACKUP_RETENTION_DAYS=30

# 性能配置
INDEX_REFRESH_INTERVAL=30s
INDEX_NUMBER_OF_SHARDS=1
INDEX_NUMBER_OF_REPLICAS=0

# 集群配置
CLUSTER_NAME=elk-cluster
NODE_NAME=elk-node-1
DISCOVERY_TYPE=single-node
"@
        
        $envConfig | Out-File -FilePath $OutputPath -Encoding UTF8
        Write-Log "环境配置文件已生成: $OutputPath" "INFO"
        
        return $true
    }
    catch {
        Write-Log "生成环境配置文件失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成启动脚本
#>
function New-StartupScript {
    param(
        [string]$Platform = "docker", # docker, kubernetes, native
        [string]$OutputPath = "start-elk.ps1",
        [bool]$EnableSecurity = $true
    )
    
    Write-Log "生成启动脚本" "INFO"
    
    try {
        switch ($Platform.ToLower()) {
            "docker" {
                $startupScript = @"
<#
.SYNOPSIS
    ELK Stack Docker启动脚本
.DESCRIPTION
    自动启动ELK Stack Docker容器，包括安全配置检查
.AUTHOR
    AI Assistant
.DATE
    $(Get-Date -Format 'yyyy-MM-dd')
#>

param(
    [switch]`$Security = `$$($EnableSecurity.ToString().ToLower()),
    [switch]`$Development,
    [switch]`$Production,
    [switch]`$Clean,
    [switch]`$Logs,
    [switch]`$Status
)

# 颜色定义
`$Colors = @{
    Red = 'Red'
    Green = 'Green'
    Yellow = 'Yellow'
    Blue = 'Blue'
    Cyan = 'Cyan'
    Magenta = 'Magenta'
}

function Write-ColorOutput {
    param([string]`$Message, [string]`$Color = 'White')
    Write-Host `$Message -ForegroundColor `$Color
}

function Test-DockerRunning {
    try {
        docker version | Out-Null
        return `$true
    }
    catch {
        return `$false
    }
}

function Test-DockerComposeFile {
    param([string]`$FilePath)
    return Test-Path `$FilePath
}

function Start-ELKStack {
    param([bool]`$SecurityEnabled)
    
    Write-ColorOutput "启动ELK Stack..." `$Colors.Blue
    
    # 检查Docker
    if (-not (Test-DockerRunning)) {
        Write-ColorOutput "错误: Docker未运行" `$Colors.Red
        return `$false
    }
    
    # 选择配置文件
    `$composeFile = if (`$SecurityEnabled) { "docker-compose.secure.yml" } else { "docker-compose.yml" }
    
    if (-not (Test-DockerComposeFile `$composeFile)) {
        Write-ColorOutput "错误: 配置文件不存在: `$composeFile" `$Colors.Red
        return `$false
    }
    
    # 清理旧容器（如果需要）
    if (`$Clean) {
        Write-ColorOutput "清理旧容器..." `$Colors.Yellow
        docker-compose -f `$composeFile down -v
    }
    
    # 启动服务
    Write-ColorOutput "启动服务..." `$Colors.Green
    docker-compose -f `$composeFile up -d
    
    # 等待服务启动
    Write-ColorOutput "等待服务启动..." `$Colors.Cyan
    Start-Sleep -Seconds 30
    
    # 检查服务状态
    Show-ServiceStatus
    
    return `$true
}

function Show-ServiceStatus {
    Write-ColorOutput "检查服务状态..." `$Colors.Blue
    
    `$services = @("elasticsearch", "kibana", "logstash")
    
    foreach (`$service in `$services) {
        `$status = docker ps --filter "name=`$service" --format "table {{.Names}}\t{{.Status}}"
        if (`$status -match `$service) {
            Write-ColorOutput "✓ `$service: 运行中" `$Colors.Green
        } else {
            Write-ColorOutput "✗ `$service: 未运行" `$Colors.Red
        }
    }
    
    # 显示访问地址
    Write-ColorOutput "\n访问地址:" `$Colors.Cyan
    Write-ColorOutput "Elasticsearch: $(if (`$Security) { 'https' } else { 'http' })://localhost:9200" `$Colors.White
    Write-ColorOutput "Kibana: $(if (`$Security) { 'https' } else { 'http' })://localhost:5601" `$Colors.White
    Write-ColorOutput "Logstash API: http://localhost:9600" `$Colors.White
}

function Show-Logs {
    param([string]`$Service = "")
    
    if (`$Service) {
        docker-compose logs -f `$Service
    } else {
        docker-compose logs -f
    }
}

# 主逻辑
if (`$Status) {
    Show-ServiceStatus
    exit 0
}

if (`$Logs) {
    Show-Logs
    exit 0
}

# 确定环境
`$isProduction = `$Production -or (-not `$Development)
`$securityEnabled = `$Security -or `$isProduction

Write-ColorOutput "ELK Stack 启动脚本" `$Colors.Magenta
Write-ColorOutput "环境: $(`$isProduction ? '生产' : '开发')" `$Colors.Yellow
Write-ColorOutput "安全: $(`$securityEnabled ? '启用' : '禁用')" `$Colors.Yellow
Write-ColorOutput "" `$Colors.White

# 启动ELK Stack
if (Start-ELKStack -SecurityEnabled `$securityEnabled) {
    Write-ColorOutput "ELK Stack启动成功!" `$Colors.Green
} else {
    Write-ColorOutput "ELK Stack启动失败!" `$Colors.Red
    exit 1
}
"@
            }
            "kubernetes" {
                $startupScript = @"
<#
.SYNOPSIS
    ELK Stack Kubernetes启动脚本
.DESCRIPTION
    自动部署ELK Stack到Kubernetes集群
.AUTHOR
    AI Assistant
.DATE
    $(Get-Date -Format 'yyyy-MM-dd')
#>

param(
    [string]`$Namespace = "elk",
    [string]`$ConfigPath = "k8s",
    [switch]`$Security = `$$($EnableSecurity.ToString().ToLower()),
    [switch]`$Clean,
    [switch]`$Status
)

function Test-KubectlAvailable {
    try {
        kubectl version --client | Out-Null
        return `$true
    }
    catch {
        return `$false
    }
}

function Deploy-ELKStack {
    param([string]`$Namespace, [string]`$ConfigPath)
    
    Write-Host "部署ELK Stack到Kubernetes..." -ForegroundColor Blue
    
    # 检查kubectl
    if (-not (Test-KubectlAvailable)) {
        Write-Host "错误: kubectl未安装或不可用" -ForegroundColor Red
        return `$false
    }
    
    # 检查配置文件
    if (-not (Test-Path `$ConfigPath)) {
        Write-Host "错误: 配置目录不存在: `$ConfigPath" -ForegroundColor Red
        return `$false
    }
    
    # 创建命名空间
    kubectl apply -f "`$ConfigPath/namespace.yaml"
    
    # 部署配置
    `$configFiles = Get-ChildItem -Path `$ConfigPath -Filter "*.yaml" | Where-Object { `$_.Name -ne "namespace.yaml" }
    
    foreach (`$file in `$configFiles) {
        Write-Host "应用配置: `$(`$file.Name)" -ForegroundColor Cyan
        kubectl apply -f `$file.FullName
    }
    
    return `$true
}

function Show-KubernetesStatus {
    param([string]`$Namespace)
    
    Write-Host "检查Kubernetes部署状态..." -ForegroundColor Blue
    
    kubectl get pods -n `$Namespace
    kubectl get services -n `$Namespace
    kubectl get pvc -n `$Namespace
}

# 主逻辑
if (`$Status) {
    Show-KubernetesStatus -Namespace `$Namespace
    exit 0
}

if (`$Clean) {
    Write-Host "清理Kubernetes资源..." -ForegroundColor Yellow
    kubectl delete namespace `$Namespace
    exit 0
}

Write-Host "ELK Stack Kubernetes部署脚本" -ForegroundColor Magenta
Write-Host "命名空间: `$Namespace" -ForegroundColor Yellow
Write-Host "配置路径: `$ConfigPath" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White

# 部署ELK Stack
if (Deploy-ELKStack -Namespace `$Namespace -ConfigPath `$ConfigPath) {
    Write-Host "ELK Stack部署成功!" -ForegroundColor Green
    Show-KubernetesStatus -Namespace `$Namespace
} else {
    Write-Host "ELK Stack部署失败!" -ForegroundColor Red
    exit 1
}
"@
            }
            default {
                throw "不支持的平台: $Platform"
            }
        }
        
        $startupScript | Out-File -FilePath $OutputPath -Encoding UTF8
        Write-Log "启动脚本已生成: $OutputPath" "INFO"
        
        return $true
    }
    catch {
        Write-Log "生成启动脚本失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成监控配置
#>
function New-MonitoringConfig {
    param(
        [string]$OutputPath = "monitoring",
        [bool]$EnableSecurity = $true
    )
    
    Write-Log "生成监控配置" "INFO"
    
    try {
        # 确保输出目录存在
        if (-not (Test-Path $OutputPath)) {
            New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
        }
        
        # 生成Prometheus配置
        $prometheusConfig = @"
# Prometheus配置
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "elk_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['elasticsearch:9200']
$(if ($EnableSecurity) {
@"
    basic_auth:
      username: 'elastic'
      password: '$($Global:DefaultPasswords.elastic)'
    scheme: https
    tls_config:
      insecure_skip_verify: true
"@
})
    metrics_path: '/_prometheus/metrics'
    scrape_interval: 30s

  - job_name: 'kibana'
    static_configs:
      - targets: ['kibana:5601']
$(if ($EnableSecurity) {
@"
    basic_auth:
      username: 'elastic'
      password: '$($Global:DefaultPasswords.elastic)'
    scheme: https
    tls_config:
      insecure_skip_verify: true
"@
})
    metrics_path: '/api/status'
    scrape_interval: 30s

  - job_name: 'logstash'
    static_configs:
      - targets: ['logstash:9600']
    metrics_path: '/_node/stats'
    scrape_interval: 30s
"@
        
        $prometheusConfig | Out-File -FilePath "$OutputPath\prometheus.yml" -Encoding UTF8
        
        # 生成告警规则
        $alertRules = @"
groups:
- name: elk_alerts
  rules:
  - alert: ElasticsearchDown
    expr: up{job="elasticsearch"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Elasticsearch is down"
      description: "Elasticsearch has been down for more than 1 minute."

  - alert: ElasticsearchHighCPU
    expr: elasticsearch_process_cpu_percent > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Elasticsearch high CPU usage"
      description: "Elasticsearch CPU usage is above 80% for more than 5 minutes."

  - alert: ElasticsearchHighMemory
    expr: elasticsearch_jvm_memory_used_bytes / elasticsearch_jvm_memory_max_bytes > 0.9
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Elasticsearch high memory usage"
      description: "Elasticsearch memory usage is above 90% for more than 5 minutes."

  - alert: KibanaDown
    expr: up{job="kibana"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Kibana is down"
      description: "Kibana has been down for more than 1 minute."

  - alert: LogstashDown
    expr: up{job="logstash"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Logstash is down"
      description: "Logstash has been down for more than 1 minute."
"@
        
        $alertRules | Out-File -FilePath "$OutputPath\elk_rules.yml" -Encoding UTF8
        
        Write-Log "监控配置已生成到目录: $OutputPath" "INFO"
        return $true
    }
    catch {
        Write-Log "生成监控配置失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# 导出函数
Export-ModuleMember -Function *