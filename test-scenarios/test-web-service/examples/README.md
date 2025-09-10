# AIOps 测试场景示例

本目录包含了AIOps测试管理平台的各种测试场景示例和工具，帮助用户快速上手和创建自己的测试用例。

## 📁 文件说明

### 测试数据文件
- `sample_test_cases.json` - 示例测试用例集合
- `test_environments.json` - 测试环境配置
- `sample_test_suite_config.json` - 完整测试套件配置示例

### 工具脚本
- `import_sample_tests.py` - 测试数据导入工具
- `test_scenario_generator.py` - 测试场景生成器

## 🚀 快速开始

### 1. 导入示例测试数据

首先确保AIOps服务器正在运行：

```bash
# 启动后端服务器
cd ../
cargo run
```

然后导入示例数据：

```bash
# 进入examples目录
cd examples

# 验证文件格式（可选）
python import_sample_tests.py --dry-run

# 导入测试数据
python import_sample_tests.py

# 指定自定义服务器地址
python import_sample_tests.py --server http://localhost:3030
```

### 2. 生成新的测试场景

#### 生成单个测试场景

```bash
# 查看支持的测试类型
python test_scenario_generator.py --list-types

# 生成API测试
python test_scenario_generator.py -t api -n "用户登录API测试" --endpoint /api/login --method POST

# 生成性能测试
python test_scenario_generator.py -t performance -n "系统负载测试" --duration 300 --concurrent-users 50

# 生成集成测试
python test_scenario_generator.py -t integration -n "微服务集成测试" --services api database redis

# 生成安全测试
python test_scenario_generator.py -t security -n "安全漏洞扫描"
```

#### 生成测试套件

```bash
# 使用示例配置生成测试套件
python test_scenario_generator.py -s sample_test_suite_config.json -o my_test_suite.json
```

## 📋 测试类型说明

### API测试 (api)
- **用途**: 验证REST API接口的功能和性能
- **特点**: 支持各种HTTP方法，包含响应时间和状态码检查
- **参数**: `--endpoint`, `--method`

### 性能测试 (performance)
- **用途**: 测试系统在指定负载下的性能表现
- **特点**: 使用K6进行负载测试，包含详细的性能指标
- **参数**: `--duration`, `--concurrent-users`

### 集成测试 (integration)
- **用途**: 验证多个服务之间的协作和数据流
- **特点**: 端到端测试，包含服务连通性和数据一致性检查
- **参数**: `--services`

### 安全测试 (security)
- **用途**: 检查常见的安全漏洞
- **特点**: 包含SQL注入、XSS、认证绕过等安全检查
- **参数**: 无额外参数

### 数据库测试 (database)
- **用途**: 验证数据库连接和CRUD操作
- **特点**: 包含事务测试和数据一致性检查
- **参数**: 无额外参数

### UI测试 (ui)
- **用途**: 验证用户界面功能和交互
- **特点**: 使用Cypress进行端到端UI测试
- **参数**: 无额外参数

### 负载测试 (load)
- **用途**: 模拟高并发场景下的系统表现
- **特点**: 分阶段负载测试，包含详细的性能报告
- **参数**: 无额外参数

### 冒烟测试 (smoke)
- **用途**: 快速验证系统基本功能
- **特点**: 轻量级测试，适合部署后的快速验证
- **参数**: 无额外参数

## 🔧 自定义测试场景

### 创建自定义测试套件配置

参考 `sample_test_suite_config.json` 创建自己的测试套件配置：

```json
{
  "name": "我的测试套件",
  "description": "自定义测试套件描述",
  "tests": [
    {
      "type": "api",
      "name": "自定义API测试",
      "endpoint": "/api/custom",
      "method": "GET"
    }
  ],
  "environment": {
    "base_url": "http://localhost:3030",
    "timeout": 30000
  }
}
```

### 修改测试环境配置

编辑 `test_environments.json` 来配置不同的测试环境：

```json
{
  "environments": {
    "development": {
      "base_url": "http://localhost:3030",
      "database_url": "sqlite:./dev.db",
      "runtime_managers": [
        {
          "name": "本地Docker",
          "type": "docker",
          "endpoint": "unix:///var/run/docker.sock"
        }
      ]
    }
  }
}
```

## 📊 测试报告

测试执行后会生成详细的报告：

- **JSON报告**: 包含完整的测试数据和指标
- **控制台输出**: 实时显示测试进度和结果
- **性能指标**: 响应时间、吞吐量、错误率等
- **安全报告**: 发现的安全漏洞和风险评估

## 🛠️ 故障排除

### 常见问题

1. **服务器连接失败**
   ```
   ❌ 服务器连接失败: Connection refused
   ```
   - 确保AIOps服务器正在运行
   - 检查服务器地址和端口是否正确

2. **导入失败**
   ```
   ❌ 导入失败: 400 Bad Request
   ```
   - 检查JSON文件格式是否正确
   - 确保必填字段都已提供

3. **权限错误**
   ```
   ❌ 权限错误: 403 Forbidden
   ```
   - 检查API密钥是否正确
   - 确保有足够的权限执行操作

### 调试模式

使用 `--dry-run` 参数进行文件验证：

```bash
python import_sample_tests.py --dry-run
```

## 📚 进阶用法

### 批量生成测试场景

```bash
# 创建批量生成脚本
cat > generate_batch_tests.sh << 'EOF'
#!/bin/bash

# 生成API测试套件
for endpoint in "/api/health" "/api/test-cases" "/api/runtime-managers"; do
    python test_scenario_generator.py -t api -n "API测试-${endpoint}" --endpoint "$endpoint" --method GET
done

# 生成不同负载的性能测试
for users in 10 50 100; do
    python test_scenario_generator.py -t performance -n "性能测试-${users}用户" --concurrent-users $users --duration 120
done
EOF

chmod +x generate_batch_tests.sh
./generate_batch_tests.sh
```

### 集成到CI/CD

```yaml
# .github/workflows/test.yml
name: AIOps Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install requests
      
      - name: Start AIOps Server
        run: |
          cargo run &
          sleep 30
      
      - name: Import test data
        run: |
          cd examples
          python import_sample_tests.py
      
      - name: Run smoke tests
        run: |
          cd examples
          python test_scenario_generator.py -t smoke -n "CI冒烟测试"
```

## 🤝 贡献指南

欢迎贡献新的测试场景和工具！

1. Fork本项目
2. 创建特性分支
3. 添加新的测试模板或工具
4. 更新文档
5. 提交Pull Request

### 添加新的测试类型

在 `test_scenario_generator.py` 中添加新的模板方法：

```python
def _generate_custom_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
    """生成自定义测试模板"""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": "自定义测试描述",
        "type": "custom",
        "runtime_type": "docker",
        "tags": ["custom"],
        "config": {},
        "script_content": "// 自定义测试脚本"
    }
```

然后在 `__init__` 方法中注册：

```python
self.templates['custom'] = self._generate_custom_test_template
```

## 📞 支持

如有问题或建议，请：

1. 查看本文档的故障排除部分
2. 在项目仓库中创建Issue
3. 联系AIOps团队

---

**注意**: 本工具集仍在持续开发中，功能和API可能会有变化。请关注项目更新。