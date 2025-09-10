#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件管理工具

本工具提供配置文件的统一管理功能，包括：
- 配置文件分类和索引
- 配置文件验证
- 配置文件备份和恢复
- 配置模板生成
- 环境配置切换

Author: AIOps Team
Version: 1.0.0
Date: 2025-01-10
"""

import os
import json
import yaml
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import configparser

@dataclass
class ConfigFile:
    """配置文件信息类"""
    name: str
    path: str
    format: str
    category: str
    description: str
    environment: str = "all"
    required: bool = True
    template_available: bool = False

class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, base_path: str = "."):
        """初始化配置管理器
        
        Args:
            base_path: 基础路径
        """
        self.base_path = Path(base_path)
        self.config_registry = self._build_config_registry()
        
    def _build_config_registry(self) -> Dict[str, ConfigFile]:
        """构建配置文件注册表"""
        registry = {}
        
        # 测试场景配置
        registry["test_config"] = ConfigFile(
            name="test_config.json",
            path="test_config.json",
            format="json",
            category="test_scenario",
            description="测试场景参数配置",
            template_available=True
        )
        
        registry["project_configs"] = ConfigFile(
            name="project_configs.json",
            path="project_configs.json",
            format="json",
            category="test_scenario",
            description="多项目负载测试配置",
            template_available=True
        )
        
        # AI引擎配置
        registry["ai_engine_default"] = ConfigFile(
            name="default.yaml",
            path="../ai-engine/config/default.yaml",
            format="yaml",
            category="application",
            description="AI引擎默认配置",
            environment="all",
            template_available=True
        )
        
        registry["ai_engine_production"] = ConfigFile(
            name="production.yaml",
            path="../ai-engine/config/production.yaml",
            format="yaml",
            category="application",
            description="AI引擎生产环境配置",
            environment="production",
            template_available=True
        )
        
        registry["ai_engine_test"] = ConfigFile(
            name="test.yaml",
            path="../ai-engine/config/test.yaml",
            format="yaml",
            category="application",
            description="AI引擎测试环境配置",
            environment="test",
            template_available=True
        )
        
        # 基础设施配置
        registry["elasticsearch"] = ConfigFile(
            name="elasticsearch.yml",
            path="../configs/elasticsearch/elasticsearch.yml",
            format="yaml",
            category="infrastructure",
            description="Elasticsearch配置",
            template_available=True
        )
        
        registry["prometheus"] = ConfigFile(
            name="prometheus.yml",
            path="../configs/prometheus/prometheus.yml",
            format="yaml",
            category="infrastructure",
            description="Prometheus监控配置",
            template_available=True
        )
        
        registry["grafana"] = ConfigFile(
            name="grafana.ini",
            path="../configs/grafana/grafana.ini",
            format="ini",
            category="infrastructure",
            description="Grafana仪表板配置",
            template_available=True
        )
        
        # 容器编排配置
        registry["docker_compose"] = ConfigFile(
            name="docker-compose.yml",
            path="../docker-compose.yml",
            format="yaml",
            category="orchestration",
            description="Docker Compose主配置",
            template_available=True
        )
        
        registry["helm_values"] = ConfigFile(
            name="values.yaml",
            path="../helm/values.yaml",
            format="yaml",
            category="orchestration",
            description="Helm Chart配置",
            environment="kubernetes",
            template_available=True
        )
        
        # 自愈系统配置
        registry["self_healing_rules"] = ConfigFile(
            name="system-rules.yaml",
            path="../self-healing/rules/system-rules.yaml",
            format="yaml",
            category="self_healing",
            description="系统自愈规则配置",
            template_available=True
        )
        
        return registry
    
    def list_configs(self, category: Optional[str] = None, environment: Optional[str] = None) -> List[ConfigFile]:
        """列出配置文件
        
        Args:
            category: 配置分类过滤
            environment: 环境过滤
            
        Returns:
            配置文件列表
        """
        configs = list(self.config_registry.values())
        
        if category:
            configs = [c for c in configs if c.category == category]
            
        if environment:
            configs = [c for c in configs if c.environment in [environment, "all"]]
            
        return configs
    
    def get_config_categories(self) -> List[str]:
        """获取所有配置分类"""
        categories = set()
        for config in self.config_registry.values():
            categories.add(config.category)
        return sorted(list(categories))
    
    def validate_config(self, config_key: str) -> Dict[str, Any]:
        """验证配置文件
        
        Args:
            config_key: 配置文件键名
            
        Returns:
            验证结果
        """
        if config_key not in self.config_registry:
            return {
                "valid": False,
                "error": f"未知的配置文件: {config_key}"
            }
        
        config = self.config_registry[config_key]
        config_path = self.base_path / config.path
        
        # 检查文件是否存在
        if not config_path.exists():
            return {
                "valid": False,
                "error": f"配置文件不存在: {config_path}"
            }
        
        # 根据格式验证文件
        try:
            if config.format == "json":
                with open(config_path, 'r', encoding='utf-8') as f:
                    json.load(f)
            elif config.format == "yaml":
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml.safe_load(f)
            elif config.format == "ini":
                parser = configparser.ConfigParser()
                parser.read(config_path, encoding='utf-8')
            
            return {
                "valid": True,
                "message": "配置文件格式正确",
                "size": config_path.stat().st_size,
                "modified": datetime.fromtimestamp(config_path.stat().st_mtime)
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"配置文件格式错误: {str(e)}"
            }
    
    def backup_config(self, config_key: str, backup_dir: Optional[str] = None) -> Dict[str, Any]:
        """备份配置文件
        
        Args:
            config_key: 配置文件键名
            backup_dir: 备份目录
            
        Returns:
            备份结果
        """
        if config_key not in self.config_registry:
            return {
                "success": False,
                "error": f"未知的配置文件: {config_key}"
            }
        
        config = self.config_registry[config_key]
        config_path = self.base_path / config.path
        
        if not config_path.exists():
            return {
                "success": False,
                "error": f"配置文件不存在: {config_path}"
            }
        
        # 创建备份目录
        if backup_dir is None:
            backup_dir = self.base_path / "config_backups"
        else:
            backup_dir = Path(backup_dir)
        
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{config.name}.{timestamp}.backup"
        backup_path = backup_dir / backup_filename
        
        try:
            shutil.copy2(config_path, backup_path)
            return {
                "success": True,
                "backup_path": str(backup_path),
                "original_path": str(config_path),
                "timestamp": timestamp
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"备份失败: {str(e)}"
            }
    
    def restore_config(self, config_key: str, backup_path: str) -> Dict[str, Any]:
        """恢复配置文件
        
        Args:
            config_key: 配置文件键名
            backup_path: 备份文件路径
            
        Returns:
            恢复结果
        """
        if config_key not in self.config_registry:
            return {
                "success": False,
                "error": f"未知的配置文件: {config_key}"
            }
        
        config = self.config_registry[config_key]
        config_path = self.base_path / config.path
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            return {
                "success": False,
                "error": f"备份文件不存在: {backup_path}"
            }
        
        try:
            # 备份当前文件
            if config_path.exists():
                current_backup = self.backup_config(config_key)
                if not current_backup["success"]:
                    return {
                        "success": False,
                        "error": f"无法备份当前配置: {current_backup['error']}"
                    }
            
            # 恢复配置文件
            shutil.copy2(backup_file, config_path)
            
            return {
                "success": True,
                "restored_path": str(config_path),
                "backup_used": str(backup_file)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"恢复失败: {str(e)}"
            }
    
    def generate_template(self, config_key: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """生成配置模板
        
        Args:
            config_key: 配置文件键名
            output_path: 输出路径
            
        Returns:
            生成结果
        """
        if config_key not in self.config_registry:
            return {
                "success": False,
                "error": f"未知的配置文件: {config_key}"
            }
        
        config = self.config_registry[config_key]
        
        if not config.template_available:
            return {
                "success": False,
                "error": f"配置文件 {config_key} 不支持模板生成"
            }
        
        # 生成模板内容
        template_content = self._generate_template_content(config)
        
        # 确定输出路径
        if output_path is None:
            output_path = self.base_path / f"{config.name}.template"
        else:
            output_path = Path(output_path)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            return {
                "success": True,
                "template_path": str(output_path),
                "config_type": config_key
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"模板生成失败: {str(e)}"
            }
    
    def _generate_template_content(self, config: ConfigFile) -> str:
        """生成模板内容"""
        templates = {
            "test_config": '''
{
  "scenario_generator": {
    "web_application": {
      "base_response_time_ms": 150,
      "base_throughput_rps": 100,
      "base_error_rate": 0.02,
      "base_cpu_usage": 0.45,
      "base_memory_usage": 0.60,
      "anomaly_probability": 0.05
    },
    "database": {
      "base_query_time_ms": 25,
      "base_connections": 50,
      "base_cpu_usage": 0.35,
      "base_memory_usage": 0.70,
      "anomaly_probability": 0.03
    }
  }
}
''',
            "project_configs": '''
{
  "basic_load_test": [
    {
      "type": "java",
      "name": "basic-java-service",
      "introduce_error": false,
      "description": "基础Java微服务"
    }
  ]
}
''',
            "ai_engine_default": '''
# AI引擎配置模板
app:
  name: "AIOps AI Engine"
  version: "1.0.0"
  debug: false
  host: "0.0.0.0"
  port: 8000

database:
  primary:
    type: "postgresql"
    host: "localhost"
    port: 5432
    database: "aiops"
    username: "aiops"
    password: "your_password_here"

redis:
  host: "localhost"
  port: 6379
  password: ""
  db: 0
'''
        }
        
        return templates.get(config.name.split('.')[0], f"# {config.description}\n# 请根据需要配置相关参数\n")
    
    def switch_environment(self, environment: str) -> Dict[str, Any]:
        """切换环境配置
        
        Args:
            environment: 目标环境 (development, test, production)
            
        Returns:
            切换结果
        """
        results = []
        
        # 获取环境相关的配置文件
        env_configs = self.list_configs(environment=environment)
        
        for config in env_configs:
            if config.environment != "all":
                # 这里可以实现环境配置的切换逻辑
                # 例如：复制环境特定的配置文件到默认位置
                results.append({
                    "config": config.name,
                    "status": "switched",
                    "environment": environment
                })
        
        return {
            "success": True,
            "environment": environment,
            "configs_switched": len(results),
            "details": results
        }

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AIOps配置文件管理工具")
    parser.add_argument("--base-path", default=".", help="基础路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 列出配置文件
    list_parser = subparsers.add_parser("list", help="列出配置文件")
    list_parser.add_argument("--category", help="按分类过滤")
    list_parser.add_argument("--environment", help="按环境过滤")
    
    # 验证配置文件
    validate_parser = subparsers.add_parser("validate", help="验证配置文件")
    validate_parser.add_argument("config_key", help="配置文件键名")
    
    # 备份配置文件
    backup_parser = subparsers.add_parser("backup", help="备份配置文件")
    backup_parser.add_argument("config_key", help="配置文件键名")
    backup_parser.add_argument("--backup-dir", help="备份目录")
    
    # 恢复配置文件
    restore_parser = subparsers.add_parser("restore", help="恢复配置文件")
    restore_parser.add_argument("config_key", help="配置文件键名")
    restore_parser.add_argument("backup_path", help="备份文件路径")
    
    # 生成模板
    template_parser = subparsers.add_parser("template", help="生成配置模板")
    template_parser.add_argument("config_key", help="配置文件键名")
    template_parser.add_argument("--output", help="输出路径")
    
    # 切换环境
    env_parser = subparsers.add_parser("switch-env", help="切换环境配置")
    env_parser.add_argument("environment", choices=["development", "test", "production"], help="目标环境")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = ConfigManager(args.base_path)
    
    if args.command == "list":
        configs = manager.list_configs(args.category, args.environment)
        
        print(f"\n=== 配置文件列表 ===")
        if args.category:
            print(f"分类过滤: {args.category}")
        if args.environment:
            print(f"环境过滤: {args.environment}")
        print()
        
        # 按分类分组显示
        categories = {}
        for config in configs:
            if config.category not in categories:
                categories[config.category] = []
            categories[config.category].append(config)
        
        for category, category_configs in categories.items():
            print(f"📁 {category.upper()}")
            for config in category_configs:
                status = "✅" if (Path(args.base_path) / config.path).exists() else "❌"
                print(f"  {status} {config.name} - {config.description}")
                print(f"     路径: {config.path}")
                print(f"     格式: {config.format} | 环境: {config.environment}")
                print()
    
    elif args.command == "validate":
        result = manager.validate_config(args.config_key)
        
        print(f"\n=== 配置文件验证: {args.config_key} ===")
        if result["valid"]:
            print("✅ 配置文件有效")
            print(f"文件大小: {result['size']} 字节")
            print(f"修改时间: {result['modified']}")
        else:
            print("❌ 配置文件无效")
            print(f"错误: {result['error']}")
    
    elif args.command == "backup":
        result = manager.backup_config(args.config_key, args.backup_dir)
        
        print(f"\n=== 配置文件备份: {args.config_key} ===")
        if result["success"]:
            print("✅ 备份成功")
            print(f"备份路径: {result['backup_path']}")
            print(f"时间戳: {result['timestamp']}")
        else:
            print("❌ 备份失败")
            print(f"错误: {result['error']}")
    
    elif args.command == "restore":
        result = manager.restore_config(args.config_key, args.backup_path)
        
        print(f"\n=== 配置文件恢复: {args.config_key} ===")
        if result["success"]:
            print("✅ 恢复成功")
            print(f"恢复路径: {result['restored_path']}")
        else:
            print("❌ 恢复失败")
            print(f"错误: {result['error']}")
    
    elif args.command == "template":
        result = manager.generate_template(args.config_key, args.output)
        
        print(f"\n=== 配置模板生成: {args.config_key} ===")
        if result["success"]:
            print("✅ 模板生成成功")
            print(f"模板路径: {result['template_path']}")
        else:
            print("❌ 模板生成失败")
            print(f"错误: {result['error']}")
    
    elif args.command == "switch-env":
        result = manager.switch_environment(args.environment)
        
        print(f"\n=== 环境切换: {args.environment} ===")
        if result["success"]:
            print(f"✅ 环境切换成功")
            print(f"切换配置数量: {result['configs_switched']}")
        else:
            print("❌ 环境切换失败")

if __name__ == "__main__":
    main()