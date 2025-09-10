# AIOps 多项目负载测试框架使用指南

## 概述

本框架扩展了原有的AIOps测试场景，新增了多项目负载测试和错误注入功能，支持Java、Rust、Node.js等多种项目类型的综合测试。

## 核心功能

### 1. 多项目负载测试
- 支持Java、Rust、Node.js项目的并发负载测试
- 可配置的测试场景和项目组合
- 自动化项目创建、构建和运行时测试
- 详细的性能指标收集和报告

### 2. 错误注入测试
- 编译时错误注入（语法错误、类型错误等）
- 运行时错误注入（异常、内存泄漏等）
- 构建错误注入（依赖冲突、版本问题等）
- 随机错误注入和特定错误场景

### 3. 综合测试场景
- 基础负载测试
- 综合负载测试
- 错误容错测试
- 混合场景测试
- 微服务生态系统测试
- 性能压力测试

## 快速开始

### 基本使用

```bash
# 运行所有测试（包括多项目负载测试和错误注入）
python integrated_test_runner.py --mode all

# 运行快速测试（仅基础测试场景）
python integrated_test_runner.py --mode quick

# 运行全面综合测试
python integrated_test_runner.py --mode comprehensive
```

### 多项目负载测试

```bash
# 基础多项目负载测试
python integrated_test_runner.py --mode multi-project --scenario basic_load_test

# 综合多项目负载测试
python integrated_test_runner.py --mode multi-project --scenario comprehensive_load_test

# 微服务生态系统测试
python integrated_test_runner.py --mode multi-project --scenario microservices_ecosystem_test

# 性能压力测试
python integrated_test_runner.py --mode multi-project --scenario performance_stress_test
```

### 错误注入测试

```bash
# 错误容错测试
python integrated_test_runner.py --mode error-injection --scenario error_prone_test

# 混合场景测试
python integrated_test_runner.py --mode error-injection --scenario mixed_scenario_test

# 构建失败场景测试
python integrated_test_runner.py --mode error-injection --scenario build_failure_scenarios

# 运行时失败场景测试
python integrated_test_runner.py --mode error-injection --scenario runtime_failure_scenarios
```

### 自定义测试

```bash
# 运行特定的基础测试场景
python integrated_test_runner.py --mode custom --tests web_monitor db_monitor system_monitor

# 禁用多项目负载测试
python integrated_test_runner.py --mode all --no-multi-project

# 禁用错误注入测试
python integrated_test_runner.py --mode all --no-error-injection

# 指定输出报告文件
python integrated_test_runner.py --mode all --output my_test_report.json
```

## 测试场景配置

### 项目配置文件 (project_configs.json)

配置文件定义了不同测试场景下的项目组合：

```json
{
  "basic_load_test": [
    {
      "type": "java",
      "name": "basic-java-service",
      "introduce_error": false,
      "description": "基础Java微服务"
    },
    {
      "type": "rust",
      "name": "basic-rust-api",
      "introduce_error": false,
      "description": "基础Rust API服务"
    }
  ]
}
```

### 可用测试场景

1. **basic_load_test** - 基础负载测试
   - 3个基础项目（Java、Rust、Node.js各1个）
   - 适合快速验证框架功能

2. **comprehensive_load_test** - 综合负载测试
   - 11个项目，模拟真实微服务架构
   - 包含用户服务、订单服务、支付服务等

3. **error_prone_test** - 错误容错测试
   - 5个有问题的项目
   - 测试系统对各种错误的处理能力

4. **mixed_scenario_test** - 混合场景测试
   - 6个项目，一半正常一半有问题
   - 模拟部分服务故障的真实场景

5. **microservices_ecosystem_test** - 微服务生态系统测试
   - 15个项目，完整的微服务生态
   - 包含认证、网关、负载均衡等组件

6. **performance_stress_test** - 性能压力测试
   - 6个高负载项目
   - 测试CPU、内存、I/O密集型场景

7. **build_failure_scenarios** - 构建失败场景
   - 6个有构建问题的项目
   - 测试依赖缺失、编译错误等

8. **runtime_failure_scenarios** - 运行时失败场景
   - 5个有运行时问题的项目
   - 测试异常处理、内存泄漏等

## 错误注入类型

### Java项目错误

**编译错误:**
- missing_semicolon - 缺少分号
- undefined_variable - 未定义变量
- type_mismatch - 类型不匹配
- missing_import - 缺少导入
- syntax_error - 语法错误

**运行时错误:**
- null_pointer_exception - 空指针异常
- array_index_out_of_bounds - 数组越界
- class_cast_exception - 类型转换异常
- out_of_memory_error - 内存溢出
- stack_overflow_error - 栈溢出

**构建错误:**
- missing_dependency - 缺少依赖
- version_conflict - 版本冲突
- plugin_error - 插件错误
- resource_not_found - 资源未找到

### Rust项目错误

**编译错误:**
- borrow_checker_error - 借用检查错误
- lifetime_error - 生命周期错误
- type_mismatch - 类型不匹配
- missing_trait_impl - 缺少trait实现
- macro_error - 宏错误

**运行时错误:**
- panic_unwrap - unwrap导致的panic
- index_out_of_bounds - 索引越界
- thread_panic - 线程panic
- deadlock - 死锁

### Node.js项目错误

**编译错误:**
- syntax_error - 语法错误
- reference_error - 引用错误
- type_error - 类型错误
- module_not_found - 模块未找到

**运行时错误:**
- uncaught_exception - 未捕获异常
- promise_rejection - Promise拒绝
- memory_leak - 内存泄漏
- callback_error - 回调错误
- async_error - 异步错误

## 输出和报告

### 测试报告格式

测试完成后会生成JSON格式的详细报告：

```json
{
  "test_summary": {
    "total_tests": 15,
    "successful_tests": 12,
    "failed_tests": 3,
    "total_duration": 245.67,
    "start_time": "2025-01-10T10:00:00",
    "end_time": "2025-01-10T10:04:05"
  },
  "test_results": [
    {
      "test": "基础多项目负载测试",
      "success": true,
      "duration": 45.23,
      "details": {
        "projects_tested": 3,
        "successful_builds": 3,
        "successful_runs": 3
      }
    }
  ]
}
```

### 控制台输出

运行过程中会显示详细的进度信息：

```
=== 开始多项目负载测试: basic_load_test ===
测试项目数量: 3

正在创建项目: basic-java-service (java)
✓ 项目创建成功
✓ 构建成功
✓ 运行测试成功

正在创建项目: basic-rust-api (rust)
✓ 项目创建成功
✓ 构建成功
✓ 运行测试成功

多项目负载测试完成，耗时: 45.23秒
```

## 扩展和自定义

### 添加新的项目类型

1. 在 `multi_project_load_tester.py` 中添加新的项目模板
2. 在 `error_injector.py` 中添加对应的错误注入逻辑
3. 更新 `project_configs.json` 配置文件

### 添加新的测试场景

1. 在 `project_configs.json` 中定义新的场景配置
2. 可选：在测试运行器中添加特定的处理逻辑

### 自定义错误注入

```python
from error_injector import ErrorInjector

injector = ErrorInjector()

# 注入特定错误
result = injector.inject_java_error(
    '/path/to/project', 
    'null_pointer_exception', 
    'runtime'
)

# 注入随机错误
result = injector.inject_random_error('/path/to/project', 'java')
```

## 故障排除

### 常见问题

1. **模块导入失败**
   - 确保所有依赖文件在同一目录下
   - 检查Python路径配置

2. **项目创建失败**
   - 检查磁盘空间
   - 确保有写入权限
   - 检查项目模板配置

3. **构建失败**
   - 检查相关编译器是否安装（javac、rustc、node等）
   - 检查网络连接（依赖下载）

4. **测试超时**
   - 调整超时配置
   - 检查系统资源使用情况

### 调试模式

可以通过修改代码中的日志级别来获取更详细的调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 性能优化建议

1. **并发控制** - 根据系统资源调整并发项目数量
2. **资源清理** - 定期清理临时项目文件
3. **缓存优化** - 缓存项目模板和依赖
4. **选择性测试** - 使用特定场景而非全面测试

## 贡献指南

欢迎贡献新的项目类型、错误场景或测试功能：

1. Fork 项目
2. 创建功能分支
3. 添加测试用例
4. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证。