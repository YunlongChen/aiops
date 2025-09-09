# 变更日志 (Changelog)

本文档记录了AIOps项目的所有重要变更和更新。

## 2025-01-09

### .gitignore文件完善

#### 📁 文件管理优化 (File Management Optimization)

**🔧 .gitignore规则完善**
- **IDE文件**: 添加.idea、.vscode等IDE相关文件忽略规则
- **操作系统文件**: 添加.DS_Store、Thumbs.db等系统文件忽略规则
- **日志文件**: 添加各类日志文件忽略规则（*.log、npm-debug.log等）
- **依赖包**: 添加node_modules、__pycache__等依赖目录忽略规则
- **缓存文件**: 添加各类缓存文件和临时文件忽略规则
- **环境变量**: 添加.env相关文件忽略规则
- **测试覆盖率**: 添加coverage、.pytest_cache等测试文件忽略规则
- **编译产物**: 添加build、dist等编译输出目录忽略规则
- **AI模型文件**: 添加大型模型文件忽略规则（*.pkl、*.h5、*.pt等）
- **监控数据**: 添加prometheus-data、grafana-data等数据目录忽略规则
- **证书密钥**: 添加*.pem、*.key等敏感文件忽略规则
- **配置覆盖**: 添加本地配置文件忽略规则

**📊 改进效果**
- 减少不必要文件的版本控制
- 提高Git操作效率
- 保护敏感信息安全
- 减小仓库体积

## 2025-01-09 (Docker服务修复)

### Docker Compose服务修复和优化

#### 🔧 问题修复 (Bug Fixes)

**🐛 服务配置修复**
- **API Gateway**: 修复Express依赖问题，重新构建镜像
- **Traefik**: 修复配置文件中的jaeger字段错误
- **Elasticsearch**: 暂时禁用服务（Windows兼容性问题）
- **Logstash**: 暂时禁用服务（依赖Elasticsearch）
- **Kibana**: 暂时禁用服务（依赖Elasticsearch）
- **Alertmanager**: 修复配置文件YAML语法错误，使用基础配置
- **Self-healing**: 修复健康检查问题
- **AI Engine**: 修复日志目录权限问题，添加专用日志卷

#### 🛠️ 技术改进 (Technical Improvements)

**📁 配置文件优化**
- **Alertmanager配置**: 简化配置文件，移除复杂的时间窗口和多渠道配置
- **Docker卷管理**: 为AI Engine添加专用日志卷，解决只读文件系统问题
- **服务依赖**: 优化服务启动顺序和依赖关系

**🔍 问题诊断**
- **系统化排查**: 逐一检查所有服务状态和日志
- **配置验证**: 验证YAML配置文件语法和结构
- **权限修复**: 解决容器文件系统权限问题

#### 📋 当前服务状态

**✅ 正常运行的服务**
- Traefik (反向代理)
- Prometheus (监控)
- Grafana (可视化)
- PostgreSQL (数据库)
- Redis (缓存)
- Node Exporter (系统监控)
- cAdvisor (容器监控)
- Alertmanager (告警管理)
- Self-healing (自愈服务)
- AI Engine (AI引擎)

**⏸️ 暂时禁用的服务**
- Elasticsearch (Windows兼容性问题)
- Logstash (依赖Elasticsearch)
- Kibana (依赖Elasticsearch)

**🔄 修复方法**
- 使用基础配置替代复杂配置
- 添加专用卷解决权限问题
- 暂时禁用有兼容性问题的服务

## 2024-01-15

### AIOps自愈系统用户手册完成

#### ✨ 新增功能 (Features)

**📚 用户手册文档**
- **完整用户手册**: 创建了详细的用户手册 `docs/user-manual.md`
- **系统概述**: 包含系统架构图和核心功能介绍
- **安装指南**: 提供Docker Compose和Kubernetes两种部署方式
- **配置说明**: 详细的系统配置和环境变量说明
- **使用指南**: 异常检测、自愈操作、监控告警的完整使用流程
- **故障排除**: 常见问题诊断和解决方案
- **API参考**: 完整的RESTful API接口文档
- **最佳实践**: 安全配置、性能优化、监控告警的最佳实践
- **维护指南**: 定期维护、系统升级、备份恢复的详细步骤

#### 🛠️ 技术改进 (Technical Improvements)

**📖 文档结构优化**
- **模块化组织**: 按功能模块组织文档结构
- **分层指南**: 从快速开始到高级配置的分层指导
- **实用示例**: 提供大量实际使用示例和代码片段
- **故障排除**: 系统化的问题诊断和解决流程

**👥 用户体验提升**
- **快速开始**: 5分钟快速部署指南
- **分步指导**: 详细的安装和配置步骤
- **可视化说明**: 系统架构图和流程图
- **命令行工具**: 便捷的管理脚本和命令

#### 📋 文档内容

**核心章节**
1. **系统概述** - 架构介绍和功能概览
2. **环境要求** - 硬件、软件、网络要求
3. **快速开始** - 5分钟部署指南
4. **详细安装** - Docker和Kubernetes部署
5. **系统配置** - 基础和高级配置
6. **功能使用** - 异常检测和自愈操作
7. **监控告警** - Prometheus和Grafana配置
8. **故障排除** - 问题诊断和性能优化
9. **维护升级** - 定期维护和版本升级
10. **API参考** - 完整的接口文档
11. **最佳实践** - 安全和性能优化
12. **常见问题** - FAQ和技术支持

**附录内容**
- **端口列表**: 所有服务端口说明
- **环境变量**: 完整的配置参数
- **命令行工具**: 管理脚本使用说明
- **配置模板**: 各种配置文件模板

#### 🎯 核心特性
- ✅ **完整性**: 涵盖从安装到维护的完整生命周期
- ✅ **实用性**: 提供可直接执行的命令和脚本
- ✅ **可维护性**: 模块化文档结构便于更新
- ✅ **用户友好**: 分层指导适合不同技术水平用户

---

## 2024-01-15

### AIOps自愈系统核心架构完成

#### ✨ 新增功能 (Features)

**🏗️ 项目架构设计**
- **微服务架构**: 完成整体系统架构设计，包含AI引擎、自愈执行器、API网关等核心模块
- **容器化部署**: 实现Docker和Kubernetes完整部署方案
- **自动化部署**: 创建PowerShell和Bash自动化部署脚本

**🤖 AI引擎模块**
- `ai-engine/anomaly_detection.py`: 异常检测算法实现
  - 统计学方法：Z-score、IQR、移动平均
  - 机器学习：Isolation Forest、One-Class SVM、LSTM
  - 时间序列：ARIMA、Prophet、季节性分解
  - 集成学习：多算法ensemble和投票机制
- `ai-engine/models.py`: 预训练模型管理框架
  - 模型训练、推理、版本管理
  - 在线学习和增量更新
  - A/B测试和模型评估

**🔄 自愈执行器**
- `engine/strategy_engine.py`: 策略执行引擎
  - 策略规则加载和解析
  - 条件评估和动作执行
  - 并发执行和状态管理
  - Prometheus指标和Redis状态存储
- `engine/rule_engine.py`: 规则引擎实现
  - 规则验证和优先级管理
  - 依赖关系处理和动态更新
  - 执行状态跟踪和热重载
- `triggers/event_triggers.py`: 事件触发器系统
  - 多种触发器类型（阈值、模式、ML预测）
  - 事件聚合和去重机制
- `triggers/alert_integration.py`: 告警集成
  - Prometheus Alertmanager集成
  - 多渠道通知（Webhook、邮件、Slack）

**🌐 运维API网关**
- `api/app.py`: FastAPI主应用
  - RESTful API接口设计
  - 认证授权和安全中间件
  - Prometheus指标收集
  - 系统健康检查、规则管理、告警处理等功能
- `api/start.py`: 启动脚本和环境检查
- `api/test_api.py`: 完整的API测试套件

**📊 监控和可观测性**
- **Prometheus + Grafana**: 完整监控堆栈配置
  - 系统、应用、业务多层次指标
  - 自定义Dashboard和告警规则
- **ELK Stack**: 日志处理和分析
  - Elasticsearch存储和搜索
  - Logstash日志收集处理
  - Kibana可视化分析
- **Traefik**: 边缘路由和负载均衡
  - 动态路由和SSL终止
  - 中间件（认证、限流、CORS）

**🔧 自动化修复脚本**
- `playbooks/system/`: 系统级Ansible Playbooks
  - CPU、内存、磁盘、网络优化
  - 服务重启和配置修复
- `playbooks/elasticsearch/`: Elasticsearch专用脚本
  - `clear-cache.yml`: 缓存清理和内存优化
  - `rebuild-index.yml`: 索引重建和管理
- `playbooks/database/`: 数据库维护脚本
  - MySQL、PostgreSQL优化和修复
- `playbooks/containers/`: 容器管理脚本
- `playbooks/network/`: 网络优化脚本
- `playbooks/security/`: 安全处理脚本

**⚙️ 配置管理**
- `config/api-config.yaml`: API服务完整配置
  - 服务器、认证、数据库、外部服务配置
  - 监控、日志、安全、缓存配置
- `config/self-healing-config.yaml`: 自愈策略配置
  - 全局配置和规则引擎设置
  - 执行器配置和通知设置
- `config/rules-config.yaml`: 详细的自愈规则配置
  - 系统级规则（CPU、内存、磁盘、网络）
  - 应用服务规则（状态、响应时间）
  - Elasticsearch规则（集群健康、内存、索引）
  - 数据库规则（MySQL、PostgreSQL）
  - 容器和网络规则
  - 安全规则（登录失败、可疑进程）

#### 🛠️ 技术改进 (Technical Improvements)
- **异步编程**: 全面使用asyncio提高并发性能
- **类型注解**: 完整的Python类型提示
- **错误处理**: 完善的异常处理和恢复机制
- **日志系统**: 结构化日志和多级别输出
- **指标收集**: Prometheus指标集成
- **配置管理**: 支持环境变量和热重载
- **安全性**: 认证授权、输入验证、安全中间件

#### 📁 新增文件结构
```
aiops/
├── ai-engine/                          # AI引擎模块
│   ├── anomaly_detection.py            # 异常检测算法
│   ├── models.py                       # 预训练模型管理
│   ├── Dockerfile                      # 容器配置
│   └── requirements.txt                # Python依赖
├── engine/                             # 自愈执行器
│   ├── strategy_engine.py              # 策略执行引擎
│   └── rule_engine.py                  # 规则引擎
├── triggers/                           # 触发器系统
│   ├── event_triggers.py               # 事件触发器
│   └── alert_integration.py            # 告警集成
├── api/                                # 运维API网关
│   ├── app.py                          # FastAPI主应用
│   ├── start.py                        # 启动脚本
│   ├── test_api.py                     # API测试
│   ├── Dockerfile                      # 容器配置
│   └── requirements.txt                # Python依赖
├── config/                             # 配置文件
│   ├── api-config.yaml                 # API服务配置
│   ├── self-healing-config.yaml        # 自愈策略配置
│   ├── rules-config.yaml               # 自愈规则配置
│   ├── traefik.yml                     # 负载均衡配置
│   ├── prometheus.yml                  # 监控配置
│   ├── alertmanager.yml                # 告警配置
│   ├── elasticsearch.yml               # ES配置
│   ├── logstash.conf                   # 日志处理配置
│   ├── kibana.yml                      # 可视化配置
│   └── grafana/                        # Grafana仪表板
├── playbooks/                          # Ansible自动化脚本
│   ├── system/                         # 系统级修复
│   ├── elasticsearch/                  # ES维护脚本
│   │   ├── clear-cache.yml             # 缓存清理
│   │   └── rebuild-index.yml           # 索引重建
│   ├── database/                       # 数据库维护
│   ├── services/                       # 服务管理
│   ├── containers/                     # 容器管理
│   ├── network/                        # 网络优化
│   └── security/                       # 安全处理
├── deploy/                             # 部署脚本
│   ├── deploy.ps1                      # PowerShell部署
│   ├── deploy.sh                       # Bash部署
│   ├── kubernetes/                     # K8s配置
│   └── helm/                           # Helm Chart
├── docker-compose.yml                  # 容器编排
└── docker-compose.override.yml         # 开发环境配置
```

#### 🎯 核心特性
- ✅ **智能异常检测**: 多算法融合的AI异常检测引擎
- ✅ **自动化修复**: 基于规则引擎的自愈执行器
- ✅ **微服务架构**: 模块化设计，易于扩展维护
- ✅ **容器化部署**: Docker和Kubernetes完整支持
- ✅ **全面监控**: Prometheus+Grafana+ELK完整可观测性
- ✅ **负载均衡**: Traefik动态路由和SSL终止
- ✅ **API网关**: FastAPI RESTful接口和认证授权
- ✅ **自动化运维**: Ansible Playbook自动化修复
- ✅ **配置管理**: 灵活的配置系统和热重载
- ✅ **安全性**: 多层安全防护和审计

#### 📋 技术栈
- **后端**: Python 3.11+, FastAPI, asyncio
- **数据库**: PostgreSQL, Redis, InfluxDB
- **消息队列**: RabbitMQ
- **容器**: Docker, Kubernetes, Helm
- **监控**: Prometheus, Grafana, Alertmanager
- **日志**: Elasticsearch, Logstash, Kibana
- **负载均衡**: Traefik
- **自动化**: Ansible
- **AI/ML**: scikit-learn, TensorFlow, PyTorch, Prophet

---

## 2025-01-09

### 部署问题修复和系统优化
    
#### 🐛 部署问题修复 (Deployment Fixes)

**依赖版本问题**
- **cryptography版本冲突**: 修复cryptography依赖版本问题（41.0.8 -> 42.0.8）
- **Docker镜像重建**: 重建API Gateway镜像解决依赖缺失问题
- **依赖兼容性**: 解决Python包版本兼容性问题

**网络配置问题**
- **Docker网络冲突**: 解决Docker网络地址空间重叠冲突

**服务配置修复**
- **API Gateway**: 修复Express依赖缺失问题，重新构建镜像
- **Elasticsearch**: 添加用户权限配置(1000:1000)解决文件权限问题
- **Prometheus**: 移除无效的storage、query、web、log顶级配置字段
- **Traefik**: 移除不支持的swarmMode字段(v3.0兼容性)
- **Logstash**: 修正配置文件路径映射，解决配置文件找不到问题
- **Alertmanager**: 修复group_interval零值配置错误
- **Kibana**: 移除不支持的server.compression.threshold字段
- **子网配置优化**: 更新Docker网络子网配置避免与宿主机网络冲突
- **端口冲突解决**: 解决Traefik与API Gateway端口冲突（8080 -> 8090）

**服务配置问题**
- **Kibana日志配置**: 修复Kibana日志配置格式兼容性问题，适配8.8.0版本
- **Elasticsearch配置**: 创建缺失的Elasticsearch log4j2.properties配置文件
- **Traefik配置**: 调整Traefik仪表板端口配置，避免服务冲突

**服务启动优化**
- **启动顺序**: 优化服务启动顺序和依赖关系
- **健康检查**: 改进服务健康检查机制
- **容器编排**: 完善Docker Compose服务编排配置

#### 🛠️ 系统稳定性改进 (System Stability)
- **错误处理**: 增强部署脚本的错误处理和恢复机制
- **日志记录**: 改进部署过程的日志记录和问题诊断
- **配置验证**: 添加配置文件验证和格式检查
- **服务监控**: 完善服务状态监控和告警机制

### 环境检查脚本Bug修复

#### 🐛 修复 (Fixed)

**PowerShell脚本错误修复**
- **变量引用问题**: 修复环境检查脚本中的PowerShell语法错误
- **Docker版本检查**: 解决Docker版本检查中的类型转换错误
- **内存和CPU信息解析**: 修复Docker内存和CPU信息解析问题
- **正则表达式匹配**: 改进正则表达式匹配逻辑，避免$matches变量被覆盖
- **异常处理**: 添加异常处理机制，提高脚本健壮性

**部署脚本Bug修复**
- **PowerShell变量引用语法错误**: 使用${name}格式避免冒号解析问题
- **占位符转义问题**: 修复`<node-ip>`占位符的转义问题，使用反引号转义尖括号
- **重复参数定义**: 移除重复的Verbose参数定义，避免与PowerShell内置参数冲突
- **缺失参数定义**: 添加缺失的QuickStart参数定义，支持快速部署模式
- **Docker环境检查**: 修复Docker环境检查问题，正确处理Docker警告信息，避免将WARNING当作错误
- **PowerShell错误流处理**: 修复PowerShell错误流处理问题，正确捕获docker info命令输出

#### 🛠️ 技术改进 (Technical Improvements)
- **脚本稳定性**: 环境检查脚本现在运行完全正常
- **Docker集成**: 所有Docker相关的检查都能正确通过
- **错误处理**: 完善的错误处理和用户友好的错误信息
- **部署流程**: 部署脚本现已可正常启动，能够进行环境检查和部署流程

---

## 2024-01-09

### ELK Stack 安全配置模块化重构

#### 🔧 重构 (Refactor)
- **删除原有security-setup.ps1文件**: 原文件包含大量重复无效证书内容，导致输出过长问题
- **模块化架构设计**: 将安全配置功能拆分为多个专门的模块文件

#### ✨ 新增功能 (Features)

**主配置文件**
- `elk/security-setup.ps1`: 重新设计的主安全配置脚本
  - 支持多种操作类型：setup、enable、disable、reset、certificates、users、permissions、audit
  - 模块化导入机制，支持动态加载安全模块
  - 完整的参数处理和错误处理机制

**安全模块**
- `elk/security-modules/security-common.ps1`: 通用安全模块
  - 全局变量和颜色定义
  - 默认用户和角色配置
  - Write-Log、Invoke-ApiRequest、New-RandomPassword等通用函数

- `elk/security-modules/certificate-manager.ps1`: 证书管理模块
  - Initialize-CertificateDirectory: 初始化证书目录结构
  - New-CACertificate: 生成CA根证书
  - New-ServiceCertificate: 生成服务证书
  - New-AllSecurityCertificates: 批量生成所有安全证书
  - Test-CertificateValidity: 验证证书有效性
  - Get-CertificateInfo: 获取证书信息

- `elk/security-modules/user-manager.ps1`: 用户管理模块
  - New-ElasticsearchUser: 创建Elasticsearch用户
  - New-ElasticsearchRole: 创建用户角色
  - Add-ElasticsearchUserRole: 分配用户角色
  - Remove-ElasticsearchUser: 删除用户
  - Initialize-DefaultUsers: 初始化默认用户
  - Test-UserAuthentication: 验证用户认证
  - Reset-UserPassword: 重置用户密码

- `elk/security-modules/permission-manager.ps1`: 权限管理模块
  - Set-IndexPermissions: 配置索引权限
  - Set-ClusterPermissions: 配置集群权限
  - Set-DataAccessPolicy: 配置数据访问策略
  - Set-FieldLevelSecurity: 配置字段级安全
  - Set-DocumentLevelSecurity: 配置文档级安全
  - Test-UserPermissions: 检查用户权限
  - New-PermissionReport: 生成权限报告
  - Write-PermissionAudit: 审计权限变更
  - Remove-ExpiredPermissions: 清理过期权限

- `elk/security-modules/component-security.ps1`: 组件安全配置模块
  - New-ElasticsearchSecurityConfig: 生成Elasticsearch安全配置
  - New-KibanaSecurityConfig: 生成Kibana安全配置
  - New-LogstashSecurityConfig: 生成Logstash安全配置
  - New-BeatsSecurityConfig: 生成Beats安全配置
  - Enable-ComponentSecurity: 启用组件安全功能
  - Disable-ComponentSecurity: 禁用组件安全功能
  - New-DockerComposeSecurityConfig: 生成Docker Compose安全配置
  - Test-ComponentConnection: 测试组件连接

- `elk/security-modules/config-generator.ps1`: 配置生成模块
  - New-DockerComposeConfig: 生成Docker Compose配置文件
  - New-KubernetesConfig: 生成Kubernetes配置文件
  - New-EnvironmentConfig: 生成环境配置文件(.env)
  - New-StartupScript: 生成启动脚本(Docker/Kubernetes)
  - New-MonitoringConfig: 生成监控配置(Prometheus/Grafana)

- `elk/security-modules/security-audit.ps1`: 安全审计模块
  - Write-SecurityEvent: 记录安全事件
  - Send-SecurityEventToElasticsearch: 发送事件到Elasticsearch
  - New-SecurityAuditReport: 生成安全审计报告
  - Get-SecurityAuditData: 获取审计数据
  - Remove-ExpiredAuditLogs: 清理过期审计日志
  - Export-AuditData: 导出审计数据
  - Test-SecurityCompliance: 检查安全合规性

#### 🛠️ 技术改进 (Technical Improvements)
- **模块化设计**: 每个模块专注于特定功能领域，提高代码可维护性
- **错误处理**: 完善的try-catch错误处理机制
- **日志记录**: 统一的日志记录格式和级别
- **参数验证**: 严格的参数验证和类型检查
- **文档注释**: 完整的PowerShell帮助文档注释

#### 📁 文件结构
```
elk/
├── security-setup.ps1                    # 主安全配置脚本
└── security-modules/                      # 安全模块目录
    ├── security-common.ps1               # 通用模块
    ├── certificate-manager.ps1           # 证书管理
    ├── user-manager.ps1                  # 用户管理
    ├── permission-manager.ps1             # 权限管理
    ├── component-security.ps1             # 组件安全配置
    ├── config-generator.ps1               # 配置生成
    └── security-audit.ps1                 # 安全审计
```

#### 🎯 解决的问题
- ✅ 解决了原security-setup.ps1文件输出过长的问题
- ✅ 提高了代码的可维护性和可扩展性
- ✅ 实现了功能模块的清晰分离
- ✅ 提供了完整的ELK安全配置解决方案

#### 📋 待办事项更新
- ✅ ELK堆栈安全配置模块化完成
- 🔄 继续进行ELK堆栈的其他配置工作

---

## 格式说明

- 🆕 新增 (Added)
- ✨ 功能 (Features) 
- 🔧 重构 (Refactor)
- 🐛 修复 (Fixed)
- 🛠️ 改进 (Improved)
- 📝 文档 (Documentation)
- 🔒 安全 (Security)
- ⚡ 性能 (Performance)
- 🎨 样式 (Style)
- 📋 任务 (Tasks)
- ✅ 完成 (Completed)
- 🔄 进行中 (In Progress)
- ⏸️ 暂停 (Paused)
- ❌ 取消 (Cancelled)