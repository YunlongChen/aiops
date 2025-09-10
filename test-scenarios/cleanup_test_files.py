#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件清理脚本
清理测试过程中生成的临时文件和结果文件

功能:
- 清理测试结果文件 (*_metrics.json, *_report.json等)
- 清理临时文件和目录
- 清理日志文件
- 支持选择性清理和备份

作者: AIOps Team
创建时间: 2025-09-10
"""

import os
import shutil
import glob
import zipfile
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class TestFilesCleaner:
    """测试文件清理器类"""
    
    def __init__(self, base_dir: str = None):
        """初始化清理器
        
        Args:
            base_dir: 基础目录路径，默认为脚本所在目录
        """
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        
        # 要清理的文件模式
        self.cleanup_patterns = [
            '*_metrics.json',
            '*_report.json', 
            'test_report.json',
            'db_*.json',
            'sys_*.json',
            'web_*.json',
            'anomaly_*.json',
            'alert_*.json',
            'performance_*.json',
            '*.tmp',
            '*.temp',
            'temp_*',
            '*.log'
        ]
        
        # 要清理的目录
        self.cleanup_dirs = [
            'test_reports',
            'performance_test_results', 
            'dashboard_data',
            'temp_projects',
            'logs',
            'results',
            'output',
            'cache',
            '__pycache__'
        ]
        
        self.cleaned_files = []
        self.cleaned_dirs = []
        self.errors = []
    
    def scan_files(self) -> Dict[str, List[str]]:
        """扫描要清理的文件和目录
        
        Returns:
            包含文件和目录列表的字典
        """
        scan_result = {
            'files': [],
            'directories': [],
            'total_size': 0
        }
        
        # 扫描文件
        for pattern in self.cleanup_patterns:
            files = glob.glob(str(self.base_dir / pattern))
            for file_path in files:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    scan_result['files'].append({
                        'path': file_path,
                        'size': file_size,
                        'pattern': pattern
                    })
                    scan_result['total_size'] += file_size
        
        # 扫描目录
        for dir_name in self.cleanup_dirs:
            dir_path = self.base_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                dir_size = self._get_dir_size(dir_path)
                scan_result['directories'].append({
                    'path': str(dir_path),
                    'size': dir_size
                })
                scan_result['total_size'] += dir_size
        
        return scan_result
    
    def _get_dir_size(self, dir_path: Path) -> int:
        """获取目录大小
        
        Args:
            dir_path: 目录路径
            
        Returns:
            目录大小（字节）
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(dir_path):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
        except Exception as e:
            self.errors.append(f"计算目录大小失败 {dir_path}: {e}")
        return total_size
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小
        
        Args:
            size_bytes: 字节大小
            
        Returns:
            格式化的大小字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def backup_files(self, backup_path: str = None) -> str:
        """备份要清理的文件
        
        Args:
            backup_path: 备份文件路径
            
        Returns:
            备份文件路径
        """
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = str(self.base_dir / f"test_files_backup_{timestamp}.zip")
        
        scan_result = self.scan_files()
        
        if not scan_result['files'] and not scan_result['directories']:
            print("📦 没有文件需要备份")
            return None
        
        print(f"📦 开始备份文件到: {backup_path}")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 备份文件
                for file_info in scan_result['files']:
                    file_path = file_info['path']
                    arcname = os.path.relpath(file_path, self.base_dir)
                    zipf.write(file_path, arcname)
                    print(f"  备份文件: {arcname}")
                
                # 备份目录
                for dir_info in scan_result['directories']:
                    dir_path = Path(dir_info['path'])
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file():
                            arcname = os.path.relpath(file_path, self.base_dir)
                            zipf.write(file_path, arcname)
                            print(f"  备份文件: {arcname}")
            
            backup_size = os.path.getsize(backup_path)
            print(f"✅ 备份完成，备份文件大小: {self._format_size(backup_size)}")
            return backup_path
            
        except Exception as e:
            error_msg = f"备份失败: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return None
    
    def clean_files(self, dry_run: bool = False) -> Dict[str, int]:
        """清理文件
        
        Args:
            dry_run: 是否为试运行模式（不实际删除文件）
            
        Returns:
            清理统计信息
        """
        scan_result = self.scan_files()
        
        if not scan_result['files'] and not scan_result['directories']:
            print("🧹 没有文件需要清理")
            return {'files': 0, 'directories': 0, 'size': 0}
        
        action = "扫描" if dry_run else "清理"
        print(f"🧹 开始{action}测试文件...")
        
        stats = {'files': 0, 'directories': 0, 'size': 0}
        
        # 清理文件
        for file_info in scan_result['files']:
            file_path = file_info['path']
            file_size = file_info['size']
            
            if dry_run:
                print(f"  [试运行] 将删除文件: {file_path} ({self._format_size(file_size)})")
            else:
                try:
                    os.remove(file_path)
                    self.cleaned_files.append(file_path)
                    print(f"  删除文件: {file_path} ({self._format_size(file_size)})")
                except Exception as e:
                    error_msg = f"删除文件失败 {file_path}: {e}"
                    self.errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
                    continue
            
            stats['files'] += 1
            stats['size'] += file_size
        
        # 清理目录
        for dir_info in scan_result['directories']:
            dir_path = dir_info['path']
            dir_size = dir_info['size']
            
            if dry_run:
                print(f"  [试运行] 将删除目录: {dir_path} ({self._format_size(dir_size)})")
            else:
                try:
                    shutil.rmtree(dir_path)
                    self.cleaned_dirs.append(dir_path)
                    print(f"  删除目录: {dir_path} ({self._format_size(dir_size)})")
                except Exception as e:
                    error_msg = f"删除目录失败 {dir_path}: {e}"
                    self.errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
                    continue
            
            stats['directories'] += 1
            stats['size'] += dir_size
        
        return stats
    
    def print_summary(self, stats: Dict[str, int], dry_run: bool = False):
        """打印清理摘要
        
        Args:
            stats: 清理统计信息
            dry_run: 是否为试运行模式
        """
        action = "扫描" if dry_run else "清理"
        print(f"\n📊 {action}摘要:")
        print(f"  文件数量: {stats['files']}")
        print(f"  目录数量: {stats['directories']}")
        print(f"  总大小: {self._format_size(stats['size'])}")
        
        if self.errors:
            print(f"\n⚠️  错误数量: {len(self.errors)}")
            for error in self.errors:
                print(f"  - {error}")
        
        if not dry_run:
            print(f"\n✅ {action}完成")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='AIOps测试文件清理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python cleanup_test_files.py --scan                    # 扫描要清理的文件
  python cleanup_test_files.py --clean                   # 清理文件
  python cleanup_test_files.py --backup --clean          # 备份后清理
  python cleanup_test_files.py --dry-run                 # 试运行模式
        """
    )
    
    parser.add_argument('--scan', action='store_true', help='扫描要清理的文件（不删除）')
    parser.add_argument('--clean', action='store_true', help='清理文件')
    parser.add_argument('--backup', action='store_true', help='清理前备份文件')
    parser.add_argument('--backup-path', type=str, help='指定备份文件路径')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式（显示将要删除的文件但不实际删除）')
    parser.add_argument('--dir', type=str, help='指定要清理的目录路径')
    
    args = parser.parse_args()
    
    # 如果没有指定任何操作，默认为扫描
    if not any([args.scan, args.clean, args.dry_run]):
        args.scan = True
    
    # 创建清理器
    cleaner = TestFilesCleaner(args.dir)
    
    print("🧹 AIOps测试文件清理工具")
    print(f"📁 工作目录: {cleaner.base_dir}")
    print()
    
    try:
        if args.scan or args.dry_run:
            # 扫描模式
            stats = cleaner.clean_files(dry_run=True)
            cleaner.print_summary(stats, dry_run=True)
            
            if args.scan and not args.clean:
                print("\n💡 提示: 使用 --clean 参数来实际清理这些文件")
        
        if args.clean and not args.dry_run:
            # 备份（如果需要）
            if args.backup:
                backup_path = cleaner.backup_files(args.backup_path)
                if backup_path:
                    print(f"📦 备份文件已保存到: {backup_path}")
                print()
            
            # 确认清理
            scan_result = cleaner.scan_files()
            total_size = cleaner._format_size(scan_result['total_size'])
            total_items = len(scan_result['files']) + len(scan_result['directories'])
            
            if total_items > 0:
                print(f"⚠️  即将删除 {total_items} 个项目，总大小 {total_size}")
                confirm = input("确认继续吗？(y/N): ").strip().lower()
                
                if confirm in ['y', 'yes', '是']:
                    # 执行清理
                    stats = cleaner.clean_files(dry_run=False)
                    cleaner.print_summary(stats, dry_run=False)
                else:
                    print("❌ 清理操作已取消")
            else:
                print("🧹 没有文件需要清理")
    
    except KeyboardInterrupt:
        print("\n❌ 操作被用户中断")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == '__main__':
    main()