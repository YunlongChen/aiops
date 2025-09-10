#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版性能压力测试器

该模块执行系统性能压力测试，包括CPU、内存、磁盘IO等测试。
不依赖外部库，使用Python标准库实现。

Author: AIOps Team
Date: 2025-01-10
"""

import os
import sys
import time
import json
import random
import threading
import multiprocessing
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('PerformanceTester')

class SimplePerformanceTester:
    """
    简化版性能压力测试器
    执行各种系统性能测试
    """
    
    def __init__(self):
        """初始化性能测试器"""
        self.cpu_count = multiprocessing.cpu_count()
        self.test_results = {}
        
    def cpu_stress_test(self, duration: int = 60, threads: int = None) -> Dict[str, Any]:
        """
        CPU压力测试
        
        Args:
            duration: 测试持续时间（秒）
            threads: 线程数，默认为CPU核心数
            
        Returns:
            测试结果字典
        """
        if threads is None:
            threads = self.cpu_count
            
        logger.info(f"开始CPU压力测试: {threads}线程, {duration}秒")
        
        start_time = time.time()
        stop_event = threading.Event()
        
        def cpu_worker(worker_id: int):
            """CPU密集型工作线程"""
            operations = 0
            while not stop_event.is_set():
                # 执行CPU密集型计算
                for i in range(1000):
                    _ = sum(j * j for j in range(100))
                operations += 1000
            return operations
        
        # 启动工作线程
        workers = []
        for i in range(threads):
            worker = threading.Thread(target=cpu_worker, args=(i,))
            worker.start()
            workers.append(worker)
        
        # 运行指定时间
        time.sleep(duration)
        stop_event.set()
        
        # 等待所有线程结束
        for worker in workers:
            worker.join()
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        result = {
            'test_type': 'cpu_stress',
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat(),
            'duration_seconds': round(actual_duration, 2),
            'threads_used': threads,
            'cpu_cores': self.cpu_count,
            'status': 'completed'
        }
        
        logger.info(f"CPU压力测试完成: {actual_duration:.2f}秒")
        return result
    
    def memory_stress_test(self, duration: int = 60, memory_mb: int = 100) -> Dict[str, Any]:
        """
        内存压力测试
        
        Args:
            duration: 测试持续时间（秒）
            memory_mb: 分配内存大小（MB）
            
        Returns:
            测试结果字典
        """
        logger.info(f"开始内存压力测试: {memory_mb}MB, {duration}秒")
        
        start_time = time.time()
        memory_blocks = []
        
        try:
            # 分配内存块
            block_size = 1024 * 1024  # 1MB
            for i in range(memory_mb):
                # 创建1MB的随机数据块
                block = bytearray(random.getrandbits(8) for _ in range(block_size))
                memory_blocks.append(block)
                
                # 每分配10MB检查一次时间
                if i % 10 == 0 and i > 0:
                    if time.time() - start_time > duration:
                        break
            
            # 保持内存占用
            allocated_mb = len(memory_blocks)
            logger.info(f"已分配内存: {allocated_mb}MB")
            
            # 在剩余时间内进行内存访问操作
            remaining_time = duration - (time.time() - start_time)
            if remaining_time > 0:
                end_time = time.time() + remaining_time
                operations = 0
                
                while time.time() < end_time:
                    # 随机访问内存块
                    if memory_blocks:
                        block_idx = random.randint(0, len(memory_blocks) - 1)
                        pos = random.randint(0, len(memory_blocks[block_idx]) - 1)
                        _ = memory_blocks[block_idx][pos]
                        operations += 1
                    
                    # 避免过度消耗CPU
                    if operations % 10000 == 0:
                        time.sleep(0.001)
            
        except MemoryError:
            logger.warning("内存分配失败，可能系统内存不足")
            allocated_mb = len(memory_blocks)
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        result = {
            'test_type': 'memory_stress',
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(end_time).isoformat(),
            'duration_seconds': round(actual_duration, 2),
            'requested_memory_mb': memory_mb,
            'allocated_memory_mb': allocated_mb,
            'status': 'completed'
        }
        
        logger.info(f"内存压力测试完成: {actual_duration:.2f}秒, 分配{allocated_mb}MB")
        return result
    
    def disk_io_stress_test(self, duration: int = 60, file_size_mb: int = 10) -> Dict[str, Any]:
        """
        磁盘IO压力测试
        
        Args:
            duration: 测试持续时间（秒）
            file_size_mb: 测试文件大小（MB）
            
        Returns:
            测试结果字典
        """
        logger.info(f"开始磁盘IO压力测试: {file_size_mb}MB文件, {duration}秒")
        
        start_time = time.time()
        test_file = f"stress_test_{int(start_time)}.tmp"
        
        try:
            # 创建测试数据
            test_data = bytearray(random.getrandbits(8) for _ in range(1024 * 1024))  # 1MB
            
            write_operations = 0
            read_operations = 0
            bytes_written = 0
            bytes_read = 0
            
            end_time = start_time + duration
            
            while time.time() < end_time:
                # 写入操作
                with open(test_file, 'wb') as f:
                    for i in range(file_size_mb):
                        f.write(test_data)
                        bytes_written += len(test_data)
                        write_operations += 1
                        
                        if time.time() >= end_time:
                            break
                
                if time.time() >= end_time:
                    break
                
                # 读取操作
                if os.path.exists(test_file):
                    with open(test_file, 'rb') as f:
                        while True:
                            chunk = f.read(1024 * 1024)  # 读取1MB
                            if not chunk:
                                break
                            bytes_read += len(chunk)
                            read_operations += 1
                            
                            if time.time() >= end_time:
                                break
                
                if time.time() >= end_time:
                    break
            
        except Exception as e:
            logger.error(f"磁盘IO测试错误: {e}")
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                except:
                    pass
        
        actual_end_time = time.time()
        actual_duration = actual_end_time - start_time
        
        result = {
            'test_type': 'disk_io_stress',
            'start_time': datetime.fromtimestamp(start_time).isoformat(),
            'end_time': datetime.fromtimestamp(actual_end_time).isoformat(),
            'duration_seconds': round(actual_duration, 2),
            'file_size_mb': file_size_mb,
            'write_operations': write_operations,
            'read_operations': read_operations,
            'bytes_written': bytes_written,
            'bytes_read': bytes_read,
            'write_throughput_mbps': round(bytes_written / (1024 * 1024) / actual_duration, 2),
            'read_throughput_mbps': round(bytes_read / (1024 * 1024) / actual_duration, 2),
            'status': 'completed'
        }
        
        logger.info(f"磁盘IO压力测试完成: {actual_duration:.2f}秒")
        return result
    
    def run_comprehensive_test(self, duration: int = 120) -> Dict[str, Any]:
        """
        运行综合性能测试
        
        Args:
            duration: 每个测试的持续时间（秒）
            
        Returns:
            综合测试结果
        """
        logger.info(f"开始综合性能测试，每项测试{duration}秒")
        
        comprehensive_start = time.time()
        results = {}
        
        # CPU压力测试
        logger.info("=== 执行CPU压力测试 ===")
        results['cpu_test'] = self.cpu_stress_test(duration, self.cpu_count)
        
        # 内存压力测试
        logger.info("=== 执行内存压力测试 ===")
        results['memory_test'] = self.memory_stress_test(duration, 200)
        
        # 磁盘IO压力测试
        logger.info("=== 执行磁盘IO压力测试 ===")
        results['disk_io_test'] = self.disk_io_stress_test(duration, 50)
        
        comprehensive_end = time.time()
        total_duration = comprehensive_end - comprehensive_start
        
        # 生成综合报告
        summary = {
            'test_suite': 'comprehensive_performance_test',
            'start_time': datetime.fromtimestamp(comprehensive_start).isoformat(),
            'end_time': datetime.fromtimestamp(comprehensive_end).isoformat(),
            'total_duration_seconds': round(total_duration, 2),
            'system_info': {
                'cpu_cores': self.cpu_count,
                'platform': sys.platform,
                'python_version': sys.version
            },
            'test_results': results,
            'summary_stats': {
                'tests_completed': len(results),
                'all_tests_passed': all(r.get('status') == 'completed' for r in results.values())
            }
        }
        
        logger.info(f"综合性能测试完成，总耗时: {total_duration:.2f}秒")
        return summary
    
    def export_results(self, results: Dict[str, Any], output_dir: str = 'performance_test_results') -> None:
        """
        导出测试结果
        
        Args:
            results: 测试结果
            output_dir: 输出目录
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存JSON结果
        json_file = os.path.join(output_dir, f'performance_test_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"测试结果已保存到: {json_file}")
        
        # 生成简单的文本报告
        report_file = os.path.join(output_dir, f'performance_report_{timestamp}.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== 性能压力测试报告 ===\n\n")
            f.write(f"测试时间: {results.get('start_time', 'N/A')} - {results.get('end_time', 'N/A')}\n")
            f.write(f"总耗时: {results.get('total_duration_seconds', 'N/A')}秒\n")
            f.write(f"CPU核心数: {results.get('system_info', {}).get('cpu_cores', 'N/A')}\n\n")
            
            if 'test_results' in results:
                for test_name, test_result in results['test_results'].items():
                    f.write(f"--- {test_name.upper()} ---\n")
                    f.write(f"状态: {test_result.get('status', 'N/A')}\n")
                    f.write(f"持续时间: {test_result.get('duration_seconds', 'N/A')}秒\n")
                    
                    if test_name == 'cpu_test':
                        f.write(f"使用线程数: {test_result.get('threads_used', 'N/A')}\n")
                    elif test_name == 'memory_test':
                        f.write(f"分配内存: {test_result.get('allocated_memory_mb', 'N/A')}MB\n")
                    elif test_name == 'disk_io_test':
                        f.write(f"写入吞吐量: {test_result.get('write_throughput_mbps', 'N/A')} MB/s\n")
                        f.write(f"读取吞吐量: {test_result.get('read_throughput_mbps', 'N/A')} MB/s\n")
                    
                    f.write("\n")
        
        logger.info(f"测试报告已保存到: {report_file}")
        
        print(f"\n=== 性能测试完成 ===")
        print(f"结果文件: {json_file}")
        print(f"报告文件: {report_file}")

def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='简化版性能压力测试器')
    parser.add_argument('--test-type', choices=['cpu', 'memory', 'disk', 'comprehensive'], 
                       default='comprehensive', help='测试类型')
    parser.add_argument('--duration', type=int, default=60, help='测试持续时间（秒）')
    parser.add_argument('--threads', type=int, help='CPU测试线程数')
    parser.add_argument('--memory-mb', type=int, default=100, help='内存测试分配大小（MB）')
    parser.add_argument('--file-size-mb', type=int, default=10, help='磁盘IO测试文件大小（MB）')
    
    args = parser.parse_args()
    
    print("=== 简化版性能压力测试器 ===")
    print(f"测试类型: {args.test_type}")
    print(f"持续时间: {args.duration}秒")
    print("开始测试...\n")
    
    tester = SimplePerformanceTester()
    
    if args.test_type == 'cpu':
        result = tester.cpu_stress_test(args.duration, args.threads)
    elif args.test_type == 'memory':
        result = tester.memory_stress_test(args.duration, args.memory_mb)
    elif args.test_type == 'disk':
        result = tester.disk_io_stress_test(args.duration, args.file_size_mb)
    else:  # comprehensive
        result = tester.run_comprehensive_test(args.duration)
    
    # 导出结果
    tester.export_results(result)
    
    print("\n测试完成！")

if __name__ == '__main__':
    main()