#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试场景导入工具

该工具用于将示例测试用例导入到AIOps测试管理平台中。
支持批量导入测试用例、环境配置和运行时管理器。

Author: AIOps Team
Date: 2025-01-11
"""

import json
import requests
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import time

class TestImporter:
    """测试用例导入器"""
    
    def __init__(self, base_url: str = "http://localhost:3030", api_key: Optional[str] = None):
        """
        初始化导入器
        
        Args:
            base_url: API服务器地址
            api_key: API密钥（如果需要认证）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AIOps-Test-Importer/1.0'
        })
    
    def check_server_health(self) -> bool:
        """
        检查服务器健康状态
        
        Returns:
            bool: 服务器是否健康
        """
        try:
            response = self.session.get(f'{self.base_url}/api/health', timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ 服务器连接失败: {e}")
            return False
    
    def import_runtime_managers(self, environments_config: Dict[str, Any]) -> Dict[str, str]:
        """
        导入运行时管理器
        
        Args:
            environments_config: 环境配置
            
        Returns:
            Dict[str, str]: 运行时管理器名称到ID的映射
        """
        runtime_id_map = {}
        
        print("📦 导入运行时管理器...")
        
        for env_name, env_config in environments_config.get('environments', {}).items():
            for runtime_config in env_config.get('runtime_managers', []):
                runtime_data = {
                    'name': runtime_config['name'],
                    'runtime_type': runtime_config['type'],
                    'endpoint': runtime_config.get('endpoint', ''),
                    'config': json.dumps(runtime_config),
                    'tags': runtime_config.get('tags', [])
                }
                
                try:
                    response = self.session.post(
                        f'{self.base_url}/api/runtime-managers',
                        json=runtime_data
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        runtime_id = result.get('data', {}).get('id')
                        runtime_id_map[runtime_config['name']] = runtime_id
                        print(f"  ✅ {runtime_config['name']} -> {runtime_id}")
                    else:
                        print(f"  ❌ 导入失败: {runtime_config['name']} - {response.text}")
                        
                except Exception as e:
                    print(f"  ❌ 导入异常: {runtime_config['name']} - {e}")
        
        return runtime_id_map
    
    def import_test_cases(self, test_cases: List[Dict[str, Any]], runtime_id_map: Dict[str, str]) -> List[str]:
        """
        导入测试用例
        
        Args:
            test_cases: 测试用例列表
            runtime_id_map: 运行时管理器ID映射
            
        Returns:
            List[str]: 成功导入的测试用例ID列表
        """
        imported_ids = []
        
        print("📋 导入测试用例...")
        
        for test_case in test_cases:
            # 查找对应的运行时管理器ID
            runtime_id = None
            if 'runtime_type' in test_case:
                # 根据类型查找第一个匹配的运行时管理器
                for name, rid in runtime_id_map.items():
                    if test_case['runtime_type'].lower() in name.lower():
                        runtime_id = rid
                        break
            
            if not runtime_id and runtime_id_map:
                # 使用第一个可用的运行时管理器
                runtime_id = list(runtime_id_map.values())[0]
            
            test_case_data = {
                'name': test_case['name'],
                'description': test_case.get('description', ''),
                'script_path': f"/tmp/{test_case['name'].replace(' ', '_').lower()}.js",
                'config_path': None,
                'runtime_type': test_case.get('runtime_type', 'docker'),
                'tags': json.dumps(test_case.get('tags', [])),
                'script_content': test_case.get('script_content', ''),
                'config': json.dumps(test_case.get('config', {}))
            }
            
            try:
                response = self.session.post(
                    f'{self.base_url}/api/test-cases',
                    json=test_case_data
                )
                
                if response.status_code == 201:
                    result = response.json()
                    test_case_id = result.get('data', {}).get('id')
                    imported_ids.append(test_case_id)
                    print(f"  ✅ {test_case['name']} -> {test_case_id}")
                else:
                    print(f"  ❌ 导入失败: {test_case['name']} - {response.text}")
                    
            except Exception as e:
                print(f"  ❌ 导入异常: {test_case['name']} - {e}")
        
        return imported_ids
    
    def import_from_files(self, test_cases_file: str, environments_file: str) -> bool:
        """
        从文件导入测试数据
        
        Args:
            test_cases_file: 测试用例文件路径
            environments_file: 环境配置文件路径
            
        Returns:
            bool: 导入是否成功
        """
        try:
            # 检查服务器健康状态
            if not self.check_server_health():
                print("❌ 服务器不可用，请检查服务器状态")
                return False
            
            print(f"🚀 开始导入测试数据到 {self.base_url}")
            
            # 加载配置文件
            with open(environments_file, 'r', encoding='utf-8') as f:
                environments_config = json.load(f)
            
            with open(test_cases_file, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
            
            # 导入运行时管理器
            runtime_id_map = self.import_runtime_managers(environments_config)
            
            # 等待一下确保运行时管理器创建完成
            time.sleep(1)
            
            # 导入测试用例
            imported_test_ids = self.import_test_cases(test_cases, runtime_id_map)
            
            print(f"\n📊 导入完成统计:")
            print(f"  运行时管理器: {len(runtime_id_map)} 个")
            print(f"  测试用例: {len(imported_test_ids)} 个")
            
            return len(imported_test_ids) > 0
            
        except FileNotFoundError as e:
            print(f"❌ 文件未找到: {e}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return False
        except Exception as e:
            print(f"❌ 导入过程中发生错误: {e}")
            return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AIOps测试场景导入工具')
    parser.add_argument('--server', '-s', default='http://localhost:3030',
                       help='API服务器地址 (默认: http://localhost:3030)')
    parser.add_argument('--api-key', '-k', help='API密钥')
    parser.add_argument('--test-cases', '-t', 
                       default='sample_test_cases.json',
                       help='测试用例文件路径 (默认: sample_test_cases.json)')
    parser.add_argument('--environments', '-e',
                       default='test_environments.json', 
                       help='环境配置文件路径 (默认: test_environments.json)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                       help='仅验证文件，不实际导入')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    test_cases_path = Path(args.test_cases)
    environments_path = Path(args.environments)
    
    if not test_cases_path.exists():
        print(f"❌ 测试用例文件不存在: {test_cases_path}")
        sys.exit(1)
    
    if not environments_path.exists():
        print(f"❌ 环境配置文件不存在: {environments_path}")
        sys.exit(1)
    
    if args.dry_run:
        print("🔍 验证模式 - 仅检查文件格式")
        try:
            with open(test_cases_path, 'r', encoding='utf-8') as f:
                test_cases = json.load(f)
            print(f"✅ 测试用例文件格式正确，包含 {len(test_cases)} 个测试用例")
            
            with open(environments_path, 'r', encoding='utf-8') as f:
                environments = json.load(f)
            print(f"✅ 环境配置文件格式正确，包含 {len(environments.get('environments', {}))} 个环境")
            
            print("✅ 所有文件验证通过")
            
        except Exception as e:
            print(f"❌ 文件验证失败: {e}")
            sys.exit(1)
        
        return
    
    # 创建导入器并执行导入
    importer = TestImporter(args.server, args.api_key)
    
    success = importer.import_from_files(
        str(test_cases_path),
        str(environments_path)
    )
    
    if success:
        print("\n🎉 导入完成！")
        print(f"访问 {args.server} 查看导入的测试数据")
    else:
        print("\n❌ 导入失败，请检查错误信息")
        sys.exit(1)

if __name__ == '__main__':
    main()