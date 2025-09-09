<#
.SYNOPSIS
    ELK组件安全配置模块
.DESCRIPTION
    提供各个ELK组件的安全配置功能，包括Elasticsearch、Kibana、Logstash和Beats的安全设置
.AUTHOR
    AI Assistant
.DATE
    $(Get-Date -Format 'yyyy-MM-dd')
#>

# 导入通用模块
. "$PSScriptRoot\security-common.ps1"

<#
.SYNOPSIS
    配置Elasticsearch安全
#>
function Setup-ElasticsearchSecurity {
    param(
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "配置Elasticsearch安全" "INFO"
    
    try {
        # 1. 生成Elasticsearch配置
        $esConfig = @"
# Elasticsearch安全配置
# 生成时间: $(Get-Date)

# 集群配置
cluster.name: elk-cluster
node.name: elasticsearch-node-1
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300

# 安全配置
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.client_authentication: required
xpack.security.transport.ssl.keystore.path: certs/elasticsearch/elasticsearch.p12
xpack.security.transport.ssl.truststore.path: certs/elasticsearch/elasticsearch.p12

# HTTP SSL配置
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: certs/elasticsearch/elasticsearch.p12
xpack.security.http.ssl.truststore.path: certs/elasticsearch/elasticsearch.p12

# 审计配置
xpack.security.audit.enabled: true
xpack.security.audit.logfile.events.include: [
  "access_denied", "access_granted", "anonymous_access_denied", 
  "authentication_failed", "connection_denied", "tampered_request",
  "run_as_denied", "run_as_granted"
]

# 监控配置
xpack.monitoring.collection.enabled: true
xpack.monitoring.elasticsearch.collection.enabled: false

# 发现配置
discovery.type: single-node

# 路径配置
path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs
"@
        
        # 确保配置目录存在
        $configDir = "config\elasticsearch"
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        # 写入配置文件
        $esConfig | Out-File -FilePath "$configDir\elasticsearch.yml" -Encoding UTF8
        Write-Log "Elasticsearch配置文件已生成" "INFO"
        
        # 2. 生成JVM配置
        $jvmConfig = @"
# JVM配置
-Xms1g
-Xmx1g

# GC配置
-XX:+UseG1GC
-XX:G1HeapRegionSize=16m
-XX:+UseG1GC
-XX:+UnlockExperimentalVMOptions
-XX:+UseCGroupMemoryLimitForHeap

# 安全配置
-Djava.security.policy=all.policy
-Dlog4j2.formatMsgNoLookups=true

# 网络配置
-Djava.net.preferIPv4Stack=true
"@
        
        $jvmConfig | Out-File -FilePath "$configDir\jvm.options" -Encoding UTF8
        Write-Log "Elasticsearch JVM配置已生成" "INFO"
        
        return $true
    }
    catch {
        Write-Log "配置Elasticsearch安全失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    配置Kibana安全
#>
function Setup-KibanaSecurity {
    param(
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "配置Kibana安全" "INFO"
    
    try {
        # 生成Kibana配置
        $kibanaConfig = @"
# Kibana安全配置
# 生成时间: $(Get-Date)

# 服务器配置
server.port: 5601
server.host: "0.0.0.0"
server.name: kibana

# Elasticsearch连接配置
elasticsearch.hosts: ["https://elasticsearch:9200"]
elasticsearch.username: "kibana_system"
elasticsearch.password: "$($Global:DefaultPasswords.kibana_system)"

# SSL配置
server.ssl.enabled: true
server.ssl.certificate: certs/kibana/kibana.crt
server.ssl.key: certs/kibana/kibana.key

# Elasticsearch SSL配置
elasticsearch.ssl.certificateAuthorities: ["certs/ca/ca.crt"]
elasticsearch.ssl.verificationMode: certificate

# 安全配置
xpack.security.enabled: true
xpack.security.encryptionKey: "$(New-RandomPassword -Length 32)"
xpack.security.session.idleTimeout: "1h"
xpack.security.session.lifespan: "30d"

# 监控配置
xpack.monitoring.ui.container.elasticsearch.enabled: true
xpack.monitoring.kibana.collection.enabled: false

# 日志配置
logging.appenders.file.type: file
logging.appenders.file.fileName: /usr/share/kibana/logs/kibana.log
logging.appenders.file.layout.type: json

# 国际化配置
i18n.locale: "zh-CN"

# 安全策略
csp.rules:
  - "script-src 'self' 'unsafe-eval'"
  - "worker-src blob:"
  - "child-src blob:"
"@
        
        # 确保配置目录存在
        $configDir = "config\kibana"
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        # 写入配置文件
        $kibanaConfig | Out-File -FilePath "$configDir\kibana.yml" -Encoding UTF8
        Write-Log "Kibana配置文件已生成" "INFO"
        
        return $true
    }
    catch {
        Write-Log "配置Kibana安全失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    配置Logstash安全
#>
function Setup-LogstashSecurity {
    param(
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "配置Logstash安全" "INFO"
    
    try {
        # 1. 生成Logstash主配置
        $logstashConfig = @"
# Logstash安全配置
# 生成时间: $(Get-Date)

# 节点配置
node.name: logstash-node-1

# 路径配置
path.data: /usr/share/logstash/data
path.logs: /usr/share/logstash/logs
path.settings: /usr/share/logstash/config

# 管道配置
pipeline.workers: 2
pipeline.batch.size: 125
pipeline.batch.delay: 50

# 监控配置
xpack.monitoring.enabled: true
xpack.monitoring.elasticsearch.hosts: ["https://elasticsearch:9200"]
xpack.monitoring.elasticsearch.username: "logstash_system"
xpack.monitoring.elasticsearch.password: "$($Global:DefaultPasswords.logstash_system)"
xpack.monitoring.elasticsearch.ssl.certificate_authority: "certs/ca/ca.crt"
xpack.monitoring.elasticsearch.ssl.verification_mode: certificate

# 管理API配置
api.http.host: 0.0.0.0
api.http.port: 9600
api.ssl.enabled: true
api.ssl.keystore.path: certs/logstash/logstash.p12
api.ssl.keystore.password: changeit

# 日志配置
log.level: info
log.format: json
"@
        
        # 确保配置目录存在
        $configDir = "config\logstash"
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        # 写入主配置文件
        $logstashConfig | Out-File -FilePath "$configDir\logstash.yml" -Encoding UTF8
        Write-Log "Logstash主配置文件已生成" "INFO"
        
        # 2. 生成管道配置
        $pipelineConfig = @"
# Logstash管道配置
input {
  beats {
    port => 5044
    ssl => true
    ssl_certificate => "certs/logstash/logstash.crt"
    ssl_key => "certs/logstash/logstash.key"
    ssl_certificate_authorities => ["certs/ca/ca.crt"]
    ssl_verify_mode => "force_peer"
  }
  
  tcp {
    port => 5000
    codec => json_lines
  }
  
  http {
    port => 8080
    ssl => true
    ssl_certificate => "certs/logstash/logstash.crt"
    ssl_key => "certs/logstash/logstash.key"
  }
}

filter {
  # 添加时间戳
  if !["@timestamp"] {
    mutate {
      add_field => { "[@timestamp]" => "%{+YYYY-MM-dd'T'HH:mm:ss.SSSZ}" }
    }
  }
  
  # 解析日志级别
  if [message] =~ /ERROR|WARN|INFO|DEBUG/ {
    grok {
      match => { "message" => "%{WORD:log_level}" }
    }
  }
  
  # 添加安全标签
  mutate {
    add_tag => [ "elk-security" ]
    add_field => { "pipeline" => "secure-pipeline" }
  }
}

output {
  elasticsearch {
    hosts => ["https://elasticsearch:9200"]
    user => "logstash_writer"
    password => "$($Global:DefaultPasswords.logstash_writer)"
    ssl => true
    cacert => "certs/ca/ca.crt"
    ssl_certificate_verification => true
    index => "logstash-%{+YYYY.MM.dd}"
    
    # 模板配置
    template_name => "logstash"
    template_pattern => "logstash-*"
    template_overwrite => true
  }
  
  # 调试输出（可选）
  # stdout { codec => rubydebug }
}
"@
        
        $pipelineConfig | Out-File -FilePath "$configDir\pipeline.conf" -Encoding UTF8
        Write-Log "Logstash管道配置已生成" "INFO"
        
        # 3. 生成JVM配置
        $jvmConfig = @"
# JVM配置
-Xms1g
-Xmx1g

# GC配置
-XX:+UseG1GC
-XX:G1HeapRegionSize=16m

# 安全配置
-Djava.security.policy=all.policy
-Dlog4j2.formatMsgNoLookups=true
"@
        
        $jvmConfig | Out-File -FilePath "$configDir\jvm.options" -Encoding UTF8
        Write-Log "Logstash JVM配置已生成" "INFO"
        
        return $true
    }
    catch {
        Write-Log "配置Logstash安全失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    配置Beats安全
#>
function Setup-BeatsSecurity {
    param(
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "配置Beats安全" "INFO"
    
    try {
        # 确保配置目录存在
        $configDir = "config\beats"
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        # 1. 生成Filebeat配置
        $filebeatConfig = @"
# Filebeat安全配置
# 生成时间: $(Get-Date)

filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/*.log
    - /var/log/messages
    - /var/log/syslog
  fields:
    logtype: system
  fields_under_root: true

- type: docker
  containers.ids:
    - '*'
  fields:
    logtype: docker
  fields_under_root: true

# 输出配置
output.logstash:
  hosts: ["logstash:5044"]
  ssl.enabled: true
  ssl.certificate: "certs/beats/filebeat.crt"
  ssl.key: "certs/beats/filebeat.key"
  ssl.certificate_authorities: ["certs/ca/ca.crt"]
  ssl.verification_mode: full

# 监控配置
monitoring.enabled: true
monitoring.elasticsearch:
  hosts: ["https://elasticsearch:9200"]
  username: "beats_system"
  password: "$($Global:DefaultPasswords.beats_system)"
  ssl.enabled: true
  ssl.certificate_authorities: ["certs/ca/ca.crt"]
  ssl.verification_mode: certificate

# 处理器配置
processors:
  - add_host_metadata:
      when.not.contains.tags: forwarded
  - add_docker_metadata: ~
  - add_kubernetes_metadata: ~

# 日志配置
logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
"@
        
        $filebeatConfig | Out-File -FilePath "$configDir\filebeat.yml" -Encoding UTF8
        Write-Log "Filebeat配置文件已生成" "INFO"
        
        # 2. 生成Metricbeat配置
        $metricbeatConfig = @"
# Metricbeat安全配置
# 生成时间: $(Get-Date)

metricbeat.config.modules:
  path: `${path.config}/modules.d/*.yml
  reload.enabled: false

# 系统模块
metricbeat.modules:
- module: system
  metricsets:
    - cpu
    - load
    - memory
    - network
    - process
    - process_summary
    - socket_summary
    - filesystem
    - fsstat
  enabled: true
  period: 10s
  processes: ['.*']

- module: docker
  metricsets:
    - container
    - cpu
    - diskio
    - healthcheck
    - info
    - memory
    - network
  hosts: ["unix:///var/run/docker.sock"]
  period: 10s
  enabled: true

# 输出配置
output.elasticsearch:
  hosts: ["https://elasticsearch:9200"]
  username: "beats_system"
  password: "$($Global:DefaultPasswords.beats_system)"
  ssl.enabled: true
  ssl.certificate_authorities: ["certs/ca/ca.crt"]
  ssl.verification_mode: certificate
  index: "metricbeat-%{+yyyy.MM.dd}"

# 监控配置
monitoring.enabled: true
monitoring.elasticsearch:
  hosts: ["https://elasticsearch:9200"]
  username: "beats_system"
  password: "$($Global:DefaultPasswords.beats_system)"
  ssl.enabled: true
  ssl.certificate_authorities: ["certs/ca/ca.crt"]

# 处理器配置
processors:
  - add_host_metadata: ~
  - add_docker_metadata: ~

# 日志配置
logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/metricbeat
  name: metricbeat
  keepfiles: 7
  permissions: 0644
"@
        
        $metricbeatConfig | Out-File -FilePath "$configDir\metricbeat.yml" -Encoding UTF8
        Write-Log "Metricbeat配置文件已生成" "INFO"
        
        return $true
    }
    catch {
        Write-Log "配置Beats安全失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    启用Elasticsearch安全
#>
function Enable-ElasticsearchSecurity {
    Write-Log "启用Elasticsearch安全功能" "INFO"
    
    try {
        # 检查Elasticsearch是否运行
        $esStatus = Test-ElasticsearchConnection
        if (-not $esStatus) {
            Write-Log "Elasticsearch未运行，无法启用安全功能" "WARN"
            return $false
        }
        
        # 启用安全功能的API调用
        $apiUrl = "$($Global:ElasticsearchUrl)/_cluster/settings"
        $body = @{
            "persistent" = @{
                "xpack.security.enabled" = $true
            }
        } | ConvertTo-Json
        
        $response = Invoke-ApiRequest -Url $apiUrl -Method "PUT" -Body $body
        
        if ($response.acknowledged) {
            Write-Log "Elasticsearch安全功能已启用" "INFO"
            return $true
        } else {
            Write-Log "启用Elasticsearch安全功能失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "启用Elasticsearch安全功能异常: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    启用Kibana安全
#>
function Enable-KibanaSecurity {
    Write-Log "启用Kibana安全功能" "INFO"
    
    try {
        # Kibana安全功能通过配置文件启用，这里检查配置
        $kibanaConfigPath = "config\kibana\kibana.yml"
        
        if (Test-Path $kibanaConfigPath) {
            $config = Get-Content $kibanaConfigPath -Raw
            if ($config -match "xpack.security.enabled: true") {
                Write-Log "Kibana安全功能已在配置中启用" "INFO"
                return $true
            } else {
                Write-Log "Kibana配置中未启用安全功能" "WARN"
                return $false
            }
        } else {
            Write-Log "Kibana配置文件不存在" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "检查Kibana安全功能异常: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    启用Logstash安全
#>
function Enable-LogstashSecurity {
    Write-Log "启用Logstash安全功能" "INFO"
    
    try {
        # Logstash安全功能通过配置文件启用
        $logstashConfigPath = "config\logstash\logstash.yml"
        
        if (Test-Path $logstashConfigPath) {
            Write-Log "Logstash安全配置已存在" "INFO"
            return $true
        } else {
            Write-Log "Logstash配置文件不存在" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "检查Logstash安全功能异常: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    禁用Elasticsearch安全
#>
function Disable-ElasticsearchSecurity {
    Write-Log "禁用Elasticsearch安全功能" "WARN"
    
    try {
        # 禁用安全功能的API调用
        $apiUrl = "$($Global:ElasticsearchUrl)/_cluster/settings"
        $body = @{
            "persistent" = @{
                "xpack.security.enabled" = $false
            }
        } | ConvertTo-Json
        
        $response = Invoke-ApiRequest -Url $apiUrl -Method "PUT" -Body $body
        
        if ($response.acknowledged) {
            Write-Log "Elasticsearch安全功能已禁用" "INFO"
            return $true
        } else {
            Write-Log "禁用Elasticsearch安全功能失败" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "禁用Elasticsearch安全功能异常: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    禁用Kibana安全
#>
function Disable-KibanaSecurity {
    Write-Log "禁用Kibana安全功能" "WARN"
    
    try {
        # 修改Kibana配置文件
        $kibanaConfigPath = "config\kibana\kibana.yml"
        
        if (Test-Path $kibanaConfigPath) {
            $config = Get-Content $kibanaConfigPath
            $newConfig = $config -replace "xpack.security.enabled: true", "xpack.security.enabled: false"
            $newConfig | Out-File -FilePath $kibanaConfigPath -Encoding UTF8
            
            Write-Log "Kibana安全功能已在配置中禁用" "INFO"
            return $true
        } else {
            Write-Log "Kibana配置文件不存在" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "禁用Kibana安全功能异常: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    禁用Logstash安全
#>
function Disable-LogstashSecurity {
    Write-Log "禁用Logstash安全功能" "WARN"
    
    try {
        # Logstash安全功能禁用需要修改配置
        Write-Log "Logstash安全功能禁用需要手动修改配置文件" "INFO"
        return $true
    }
    catch {
        Write-Log "禁用Logstash安全功能异常: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    生成安全配置文件
#>
function Generate-SecurityConfigurations {
    param(
        [hashtable]$Parameters = @{}
    )
    
    Write-Log "生成安全配置文件" "INFO"
    
    try {
        # 生成Docker Compose安全配置
        $dockerComposeSecure = @"
# Docker Compose安全配置
# 生成时间: $(Get-Date)

version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - node.name=elasticsearch
      - cluster.name=elk-cluster
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
      - xpack.security.enabled=true
      - xpack.security.http.ssl.enabled=true
      - xpack.security.transport.ssl.enabled=true
    volumes:
      - ./config/elasticsearch/elasticsearch.yml:/usr/share/elasticsearch/config/elasticsearch.yml:ro
      - ./certs:/usr/share/elasticsearch/config/certs:ro
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
      - "9300:9300"
    networks:
      - elk-network
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    environment:
      - SERVERNAME=kibana
      - ELASTICSEARCH_HOSTS=https://elasticsearch:9200
    volumes:
      - ./config/kibana/kibana.yml:/usr/share/kibana/config/kibana.yml:ro
      - ./certs:/usr/share/kibana/config/certs:ro
    ports:
      - "5601:5601"
    networks:
      - elk-network
    depends_on:
      - elasticsearch
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.11.0
    container_name: logstash
    volumes:
      - ./config/logstash/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
      - ./config/logstash/pipeline.conf:/usr/share/logstash/pipeline/logstash.conf:ro
      - ./certs:/usr/share/logstash/config/certs:ro
    ports:
      - "5044:5044"
      - "5000:5000"
      - "9600:9600"
    networks:
      - elk-network
    depends_on:
      - elasticsearch
    restart: unless-stopped

volumes:
  elasticsearch_data:
    driver: local

networks:
  elk-network:
    driver: bridge
"@
        
        $dockerComposeSecure | Out-File -FilePath "docker-compose.secure.yml" -Encoding UTF8
        Write-Log "Docker Compose安全配置已生成" "INFO"
        
        return $true
    }
    catch {
        Write-Log "生成安全配置文件失败: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

<#
.SYNOPSIS
    测试Elasticsearch连接
#>
function Test-ElasticsearchConnection {
    try {
        $response = Invoke-RestMethod -Uri "$($Global:ElasticsearchUrl)/_cluster/health" -Method GET -TimeoutSec 10
        return $response.status -ne "red"
    }
    catch {
        return $false
    }
}

# 导出函数
Export-ModuleMember -Function *