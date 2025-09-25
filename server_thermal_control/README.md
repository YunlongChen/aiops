# 服务器热控制系统 (Server Thermal Control System)

一个基于Rust和Actix-web构建的服务器热管理系统，提供实时温度监控、风扇控制和智能热管理功能。

## 功能特性

### 🌡️ 温度监控
- 实时CPU、GPU、主板温度监控
- 多传感器数据采集和聚合
- 温度历史数据记录和分析
- 可配置的温度阈值告警

### 🌪️ 风扇控制
- 智能风扇转速调节
- 基于温度的自动控制算法
- 手动风扇转速设置
- 风扇状态监控和故障检测

### 📊 数据分析
- 温度趋势分析
- 性能统计报告
- 历史数据查询
- 实时监控仪表板

### 🔔 告警系统
- 多级温度告警
- 邮件和Webhook通知
- 告警历史记录
- 自定义告警规则

## 技术架构

- **后端框架**: Actix-web (Rust)
- **数据库**: SQLite/PostgreSQL/MySQL
- **缓存**: Redis
- **配置**: TOML格式配置文件
- **日志**: 结构化日志记录
- **API**: RESTful API设计

## 快速开始

### 环境要求

- Rust 1.70+
- SQLite 3.x (默认) 或 PostgreSQL/MySQL
- Redis (可选，用于缓存)

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd server_thermal_control
   ```

2. **安装依赖**
   ```bash
   cargo build --release
   ```

3. **配置系统**
   ```bash
   # 复制配置模板
   cp config/app.toml.example config/app.toml
   
   # 编辑配置文件
   nano config/app.toml
   ```

4. **启动服务**
   ```bash
   # 开发模式
   cargo run
   
   # 生产模式
   cargo run --release
   
   # 指定端口
   APP_PORT=8082 cargo run
   ```

### 配置说明

主要配置文件位于 `config/app.toml`，包含以下配置段：

```toml
[server]
host = "127.0.0.1"
port = 8081
workers = 4

[database]
url = "sqlite:data/thermal_control.db"

[monitoring]
enabled = true
interval = 30
alert_threshold_temp = 80.0

[control]
enabled = true
mode = "auto"
temp_target = 65.0
```

## API文档

### 基础端点

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 服务基本信息 |
| GET | `/version` | 版本信息 |
| GET | `/api` | API信息 |

### 健康检查

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/health` | 服务健康状态 |
| GET | `/api/v1/system/info` | 系统信息 |
| GET | `/api/v1/system/health` | 系统健康详情 |

### 温度监控

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/temperature` | 获取所有温度数据 |
| GET | `/api/v1/temperature/{sensor_id}` | 获取指定传感器温度 |
| GET | `/api/v1/stats/temperature` | 温度统计信息 |

### 风扇控制

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/fans` | 获取所有风扇数据 |
| POST | `/api/v1/fans/{fan_id}/speed` | 设置风扇转速 |
| GET | `/api/v1/stats/fan` | 风扇统计信息 |

### 告警管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/v1/alerts` | 获取告警列表 |
| POST | `/api/v1/alerts/{alert_id}/acknowledge` | 确认告警 |

## 开发指南

### 项目结构

```
src/
├── main.rs              # 应用入口
├── config/              # 配置管理
├── models/              # 数据模型
├── handlers/            # API处理器
├── services/            # 业务逻辑
├── controllers/         # 控制器
└── utils/               # 工具函数

config/
└── app.toml            # 配置文件

docs/
└── api/                # API文档
```

### 添加新功能

1. 在 `models/` 中定义数据模型
2. 在 `handlers/` 中实现API处理器
3. 在 `services/` 中实现业务逻辑
4. 在 `main.rs` 中注册路由

### 运行测试

```bash
# 运行所有测试
cargo test

# 运行特定测试
cargo test test_name

# 生成测试覆盖率报告
cargo tarpaulin --out Html
```

## 部署

### Docker部署

```bash
# 构建镜像
docker build -t thermal-control .

# 运行容器
docker run -d \
  --name thermal-control \
  -p 8081:8081 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/data:/app/data \
  thermal-control
```

### 系统服务

创建systemd服务文件 `/etc/systemd/system/thermal-control.service`：

```ini
[Unit]
Description=Server Thermal Control System
After=network.target

[Service]
Type=simple
User=thermal
WorkingDirectory=/opt/thermal-control
ExecStart=/opt/thermal-control/target/release/server_thermal_control
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 监控和日志

### 日志配置

系统支持多种日志级别和格式：

```toml
[logging]
level = "info"           # trace, debug, info, warn, error
format = "json"          # json, pretty
file_enabled = true
file_path = "logs/app.log"
```

### 监控指标

系统提供以下监控指标：

- 温度数据（实时和历史）
- 风扇转速和状态
- 系统性能指标
- API请求统计
- 错误率和响应时间

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   netstat -ano | findstr :8081
   
   # 使用其他端口
   APP_PORT=8082 cargo run
   ```

2. **配置文件错误**
   ```bash
   # 验证配置文件语法
   cargo run -- --check-config
   ```

3. **数据库连接失败**
   - 检查数据库URL配置
   - 确保数据库文件权限正确
   - 验证网络连接（远程数据库）

### 日志分析

查看详细日志：

```bash
# 实时日志
tail -f logs/app.log

# 错误日志
grep "ERROR" logs/app.log

# 调试模式
RUST_LOG=debug cargo run
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [GitHub Issues]
- 文档: [项目文档]

## 更新日志

### v0.1.0 (2025-09-25)
- 初始版本发布
- 基础温度监控功能
- 风扇控制API
- 配置管理系统
- RESTful API接口