# AIOps API文档同步工具

本工具用于将AIOps测试管理系统的后端API文档同步到各种在线文档平台，如Apifox、Postman、SwaggerHub等。

## 🚀 快速开始

### 1. 生成完整的OpenAPI文档

系统已自动生成完整的OpenAPI 3.0规范文档：
```
test-scenarios/test-web-service/openapi.json
```

### 2. 使用同步脚本

#### 导出到本地（推荐先试用）
```powershell
.\scripts\sync-api-docs.ps1 -Platform local -OutputPath .\exported-api-docs
```

#### 同步到Apifox
```powershell
.\scripts\sync-api-docs.ps1 -Platform apifox
```

#### 同步到Postman
```powershell
.\scripts\sync-api-docs.ps1 -Platform postman
```

#### 同步到SwaggerHub
```powershell
.\scripts\sync-api-docs.ps1 -Platform swaggerhub
```

## 📁 文件结构

```
aiops/
├── test-scenarios/test-web-service/
│   └── openapi.json                    # 完整的OpenAPI 3.0规范文档
├── docs/
│   └── api-sync-guide.md               # 详细的同步指南
├── scripts/
│   └── sync-api-docs.ps1               # PowerShell同步脚本
├── exported-api-docs/                  # 本地导出目录
│   ├── openapi.json                    # OpenAPI文档副本
│   ├── api-docs.html                   # 可视化HTML文档
│   └── sync-guide.md                   # 同步指南副本
└── README-API-SYNC.md                  # 本文件
```

## 📋 API文档内容

当前OpenAPI文档包含以下功能模块：

### 🔧 系统管理
- **健康检查** - `GET /health`
- **API文档** - `GET /docs`
- **系统统计** - `GET /stats`
- **版本信息** - `GET /version`

### 📝 测试用例管理
- **获取测试用例列表** - `GET /test-cases`
- **创建测试用例** - `POST /test-cases`
- **获取测试用例详情** - `GET /test-cases/{id}`
- **更新测试用例** - `PUT /test-cases/{id}`
- **删除测试用例** - `DELETE /test-cases/{id}`
- **运行测试用例** - `POST /test-cases/{id}/run`

### ⚙️ 运行时管理
- **获取运行时管理器列表** - `GET /runtime-managers`
- **创建运行时管理器** - `POST /runtime-managers`
- **运行时健康检查** - `POST /runtime-managers/{id}/health-check`

### 🛠️ 系统设置
- **获取系统配置** - `GET /settings/config`
- **更新系统配置** - `PUT /settings/config`

## 🎯 支持的平台

| 平台 | 状态 | 导入方式 | 自动同步 |
|------|------|----------|----------|
| **Apifox** | ✅ 支持 | 手动导入 | 🔄 计划中 |
| **Postman** | ✅ 支持 | 手动导入 | 🔄 计划中 |
| **SwaggerHub** | ✅ 支持 | 手动导入 | ❌ 不支持 |
| **本地HTML** | ✅ 支持 | 自动生成 | ✅ 支持 |

## 🔍 使用示例

### 示例1：首次导出和预览
```powershell
# 导出到本地并预览
.\scripts\sync-api-docs.ps1 -Platform local

# 脚本会自动：
# 1. 验证OpenAPI文档格式
# 2. 创建导出目录
# 3. 生成HTML可视化文档
# 4. 打开浏览器预览
```

### 示例2：同步到Apifox
```powershell
# 同步到Apifox
.\scripts\sync-api-docs.ps1 -Platform apifox

# 脚本会自动：
# 1. 验证文档格式
# 2. 显示手动导入步骤
# 3. 打开Apifox网站
# 4. 打开文件所在目录
```

## 🛡️ 验证清单

同步完成后，请验证以下内容：

- [ ] **API端点完整性** - 所有10个API端点都已正确导入
- [ ] **数据模型** - 请求和响应模型定义完整
- [ ] **参数验证** - 参数类型和验证规则正确
- [ ] **示例数据** - 示例数据和描述信息完整
- [ ] **服务器配置** - 服务器地址配置正确
- [ ] **认证设置** - Bearer Token认证配置（如需要）

## 🔧 高级配置

### 自定义服务器地址

如需修改服务器地址，请编辑 `openapi.json` 文件中的 `servers` 部分：

```json
{
  "servers": [
    {
      "url": "http://localhost:8888/api/v1",
      "description": "本地开发服务器"
    },
    {
      "url": "https://your-production-api.com/v1",
      "description": "生产环境服务器"
    }
  ]
}
```

### 添加认证配置

文档已包含Bearer Token认证配置。如需其他认证方式，请修改 `components.securitySchemes` 部分。

## 🚨 故障排除

### 常见问题

1. **脚本执行策略错误**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

2. **OpenAPI文档格式错误**
   - 检查JSON语法是否正确
   - 验证OpenAPI 3.0规范合规性

3. **文件路径问题**
   - 确保在项目根目录执行脚本
   - 检查文件路径是否正确

4. **浏览器无法打开**
   - 手动打开生成的HTML文件
   - 检查默认浏览器设置

### 获取帮助

```powershell
# 查看脚本帮助
Get-Help .\scripts\sync-api-docs.ps1 -Full

# 查看详细同步指南
Get-Content .\docs\api-sync-guide.md
```

## 📈 更新日志

- **2025-01-19**: 初始版本发布
  - 完整的OpenAPI 3.0文档生成
  - PowerShell同步脚本
  - 支持Apifox、Postman、SwaggerHub
  - 本地HTML文档生成
  - 详细的同步指南

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 📄 许可证

MIT License - 详见项目根目录的LICENSE文件

---

**最后更新**: 2025-01-19  
**文档版本**: 1.0.0  
**OpenAPI版本**: 3.0.3