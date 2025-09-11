# AIOps API文档同步指南

本指南说明如何将AIOps测试管理系统的API文档同步到在线文档平台（如Apifox、Postman、Swagger Hub等）。

## 文档文件位置

完整的OpenAPI 3.0规范文件位于：
```
test-scenarios/test-web-service/openapi.json
```

## 支持的在线文档平台

### 1. Apifox

#### 导入步骤：
1. 登录 [Apifox](https://www.apifox.cn/)
2. 创建新项目或选择现有项目
3. 点击「导入」→「OpenAPI/Swagger」
4. 选择「从文件导入」
5. 上传 `openapi.json` 文件
6. 确认导入设置并完成导入

#### 自动同步设置：
1. 在Apifox项目设置中找到「数据同步」
2. 选择「Git仓库同步」或「URL同步」
3. 配置同步源（如果API文档托管在Git仓库中）
4. 设置自动同步频率

### 2. Postman

#### 导入步骤：
1. 打开 Postman 应用
2. 点击「Import」按钮
3. 选择「File」标签
4. 上传 `openapi.json` 文件
5. 选择导入选项并确认

### 3. Swagger Hub

#### 导入步骤：
1. 登录 [SwaggerHub](https://swagger.io/tools/swaggerhub/)
2. 点击「Create New」→「Import and Document API」
3. 选择「File Upload」
4. 上传 `openapi.json` 文件
5. 配置API信息并发布

### 4. GitBook

#### 导入步骤：
1. 在GitBook中创建新的Space
2. 使用OpenAPI集成插件
3. 配置OpenAPI文件路径
4. 自动生成API文档页面

## API文档内容概览

当前OpenAPI文档包含以下API端点：

### 系统管理
- `GET /health` - 健康检查
- `GET /docs` - API文档
- `GET /stats` - 系统统计
- `GET /version` - 版本信息

### 测试用例管理
- `GET /test-cases` - 获取测试用例列表
- `POST /test-cases` - 创建测试用例
- `GET /test-cases/{id}` - 获取测试用例详情
- `PUT /test-cases/{id}` - 更新测试用例
- `DELETE /test-cases/{id}` - 删除测试用例
- `POST /test-cases/{id}/run` - 运行测试用例

### 运行时管理
- `GET /runtime-managers` - 获取运行时管理器列表
- `POST /runtime-managers` - 创建运行时管理器
- `POST /runtime-managers/{id}/health-check` - 运行时健康检查

### 系统设置
- `GET /settings/config` - 获取系统配置
- `PUT /settings/config` - 更新系统配置

## 数据模型

文档包含完整的数据模型定义：
- `TestCase` - 测试用例模型
- `RuntimeManager` - 运行时管理器模型
- `RuntimeType` - 运行时类型枚举
- `TestStatus` - 测试状态枚举
- `ManagerStatus` - 管理器状态枚举
- 各种请求和响应模型

## 自动化同步脚本

### PowerShell脚本示例

创建 `sync-api-docs.ps1` 脚本：

```powershell
# AIOps API文档同步脚本
param(
    [Parameter(Mandatory=$true)]
    [string]$Platform,
    
    [Parameter(Mandatory=$false)]
    [string]$ApiKey,
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectId
)

$OpenApiFile = "test-scenarios/test-web-service/openapi.json"

switch ($Platform.ToLower()) {
    "apifox" {
        Write-Host "准备同步到Apifox..."
        Write-Host "请手动导入文件: $OpenApiFile"
        Write-Host "或使用Apifox CLI工具进行自动同步"
    }
    "postman" {
        Write-Host "准备同步到Postman..."
        if ($ApiKey) {
            # 使用Postman API进行同步
            Write-Host "使用API Key进行自动同步..."
        } else {
            Write-Host "请手动导入文件: $OpenApiFile"
        }
    }
    "swaggerhub" {
        Write-Host "准备同步到SwaggerHub..."
        Write-Host "请手动导入文件: $OpenApiFile"
    }
    default {
        Write-Host "支持的平台: apifox, postman, swaggerhub"
        Write-Host "用法: .\sync-api-docs.ps1 -Platform apifox"
    }
}
```

### 使用方法

```powershell
# 同步到Apifox
.\sync-api-docs.ps1 -Platform apifox

# 同步到Postman
.\sync-api-docs.ps1 -Platform postman

# 同步到SwaggerHub
.\sync-api-docs.ps1 -Platform swaggerhub
```

## 注意事项

1. **服务器地址更新**：导入后请根据实际部署环境更新服务器地址
2. **认证配置**：如果API需要认证，请在导入后配置相应的认证方式
3. **环境变量**：建议为不同环境（开发、测试、生产）配置不同的环境变量
4. **定期更新**：当API发生变更时，请重新导入更新后的OpenAPI文档

## 验证导入结果

导入完成后，请验证以下内容：
- [ ] 所有API端点都已正确导入
- [ ] 请求和响应模型定义完整
- [ ] 参数类型和验证规则正确
- [ ] 示例数据和描述信息完整
- [ ] 服务器地址配置正确

## 技术支持

如果在同步过程中遇到问题，请：
1. 检查OpenAPI文档格式是否正确
2. 确认目标平台支持OpenAPI 3.0规范
3. 查看平台的导入日志和错误信息
4. 联系技术支持团队获取帮助

---

**最后更新时间**: 2025-01-19  
**文档版本**: 1.0.0  
**OpenAPI版本**: 3.0.3