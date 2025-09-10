#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统性能压力测试工具

该模块实现了全面的系统压力测试功能，包括CPU、内存、磁盘I/O、网络等各种压力测试场景。
支持多线程并发测试、资源监控和性能报告生成。

Author: AIOps Team
Date: 2025-01-10
"""

import os
import sys
import time
import json
import threading
import multiprocessing
import random
import math
import psutil
import requests
import socket
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import subprocess
import tempfile
import hashlib


class StressTestType(Enum):
    """压力测试类型枚举"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK_IO = "disk_io"
    NETWORK = "network"
    DATABASE = "database"
    APPLICATION = "application"
    MIXED = "mixed"


class TestSeverity(Enum):
    """测试强度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


@dataclass
class TestConfiguration:
    """测试配置数据类"""
    test_type: StressTestType
    severity: TestSeverity
    duration_seconds: int
    concurrent_workers: int = 1
    target_resource_usage: float = 80.0  # 目标资源使用率 (%)
    ramp_up_seconds: int = 30  # 压力递增时间
    ramp_down_seconds: int = 30  # 压力递减时间
    monitoring_interval: int = 5  # 监控间隔 (秒)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io_read_bytes: int
    disk_io_write_bytes: int
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: Tuple[float, float, float]
    process_count: int
    thread_count: int
    open_files: int


@dataclass
class TestResult:
    """测试结果数据类"""
    test_id: str
    test_type: StressTestType
    severity: TestSeverity
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    peak_cpu_usage: float = 0.0
    peak_memory_usage: float = 0.0
    average_cpu_usage: float = 0.0
    average_memory_usage: float = 0.0
    total_operations: int = 0
    operations_per_second: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0
    metrics_history: List[SystemMetrics] = field(default_factory=list)
    error_messages: List[str] = field(default_factory=list)
    additional_data: Dict[str, Any] = field(default_factory=dict)


class CPUStressTester:
    """CPU压力测试器"""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.running = False
        self.operations_count = 0
        
    def _cpu_intensive_task(self, worker_id: int) -> int:
        """CPU密集型任务"""
        operations = 0
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.config.duration_seconds:
            # 执行数学计算
            for i in range(10000):
                math.sqrt(random.random() * 1000000)
                math.sin(random.random() * math.pi)
                math.cos(random.random() * math.pi)
                operations += 3
            
            # 短暂休息以控制CPU使用率
            if self.config.target_resource_usage < 100:
                sleep_ratio = (100 - self.config.target_resource_usage) / 100
                time.sleep(0.001 * sleep_ratio)
        
        return operations
    
    def run_test(self) -> int:
        """运行CPU压力测试"""
        self.running = True
        self.operations_count = 0
        
        with ThreadPoolExecutor(max_workers=self.config.concurrent_workers) as executor:
            futures = []
            
            for i in range(self.config.concurrent_workers):
                future = executor.submit(self._cpu_intensive_task, i)
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    operations = future.result()
                    self.operations_count += operations
                except Exception as e:
                    print(f"CPU stress test error: {e}")
        
        return self.operations_count
    
    def stop_test(self):
        """停止测试"""
        self.running = False


class MemoryStressTester:
    """内存压力测试器"""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.running = False
        self.allocated_memory = []
        
    def _memory_intensive_task(self, worker_id: int) -> int:
        """内存密集型任务"""
        operations = 0
        local_memory = []
        
        # 计算每个worker应该分配的内存大小
        total_memory_gb = psutil.virtual_memory().total / (1024**3)
        target_memory_gb = total_memory_gb * (self.config.target_resource_usage / 100)
        memory_per_worker_mb = (target_memory_gb * 1024) / self.config.concurrent_workers
        
        chunk_size_mb = 10  # 每次分配10MB
        max_chunks = int(memory_per_worker_mb / chunk_size_mb)
        
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.config.duration_seconds:
            try:
                # 分配内存
                if len(local_memory) < max_chunks:
                    # 创建10MB的数据块
                    chunk = bytearray(chunk_size_mb * 1024 * 1024)
                    # 写入随机数据以确保内存真正被使用
                    for i in range(0, len(chunk), 4096):
                        chunk[i:i+4] = random.randint(0, 255).to_bytes(4, 'big')
                    local_memory.append(chunk)
                    operations += 1
                
                # 随机访问已分配的内存
                if local_memory:
                    chunk_idx = random.randint(0, len(local_memory) - 1)
                    chunk = local_memory[chunk_idx]
                    # 随机读写操作
                    for _ in range(100):
                        pos = random.randint(0, len(chunk) - 4)
                        chunk[pos:pos+4] = random.randint(0, 255).to_bytes(4, 'big')
                        operations += 1
                
                # 偶尔释放一些内存
                if len(local_memory) > max_chunks * 0.8 and random.random() < 0.1:
                    if local_memory:
                        local_memory.pop(0)
                
                time.sleep(0.01)  # 短暂休息
                
            except MemoryError:
                # 内存不足时释放一些内存
                if local_memory:
                    local_memory.pop(0)
                time.sleep(0.1)
            
            except Exception as e:
                print(f"Memory stress test error: {e}")
                break
        
        # 清理内存
        local_memory.clear()
        return operations
    
    def run_test(self) -> int:
        """运行内存压力测试"""
        self.running = True
        operations_count = 0
        
        with ThreadPoolExecutor(max_workers=self.config.concurrent_workers) as executor:
            futures = []
            
            for i in range(self.config.concurrent_workers):
                future = executor.submit(self._memory_intensive_task, i)
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    operations = future.result()
                    operations_count += operations
                except Exception as e:
                    print(f"Memory stress test error: {e}")
        
        return operations_count
    
    def stop_test(self):
        """停止测试"""
        self.running = False


class DiskIOStressTester:
    """磁盘I/O压力测试器"""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.running = False
        self.temp_files = []
        
    def _disk_io_task(self, worker_id: int) -> int:
        """磁盘I/O任务"""
        operations = 0
        
        # 创建临时文件
        temp_dir = self.config.parameters.get('temp_dir', tempfile.gettempdir())
        temp_file = os.path.join(temp_dir, f"stress_test_{worker_id}_{int(time.time())}.tmp")
        self.temp_files.append(temp_file)
        
        # 文件大小配置
        file_size_mb = self.config.parameters.get('file_size_mb', 100)
        block_size = self.config.parameters.get('block_size', 4096)  # 4KB blocks
        
        start_time = time.time()
        
        try:
            while self.running and (time.time() - start_time) < self.config.duration_seconds:
                # 写入测试
                with open(temp_file, 'wb') as f:
                    bytes_written = 0
                    target_bytes = file_size_mb * 1024 * 1024
                    
                    while bytes_written < target_bytes and self.running:
                        # 生成随机数据块
                        data = os.urandom(block_size)
                        f.write(data)
                        f.flush()  # 强制写入磁盘
                        os.fsync(f.fileno())  # 同步到磁盘
                        
                        bytes_written += block_size
                        operations += 1
                        
                        # 控制I/O速率
                        if self.config.target_resource_usage < 100:
                            time.sleep(0.001)
                
                # 读取测试
                if os.path.exists(temp_file) and self.running:
                    with open(temp_file, 'rb') as f:
                        while self.running:
                            data = f.read(block_size)
                            if not data:
                                break
                            
                            # 验证数据（可选）
                            if self.config.parameters.get('verify_data', False):
                                hashlib.md5(data).hexdigest()
                            
                            operations += 1
                            
                            # 控制I/O速率
                            if self.config.target_resource_usage < 100:
                                time.sleep(0.001)
                
                # 随机访问测试
                if os.path.exists(temp_file) and self.running:
                    file_size = os.path.getsize(temp_file)
                    with open(temp_file, 'r+b') as f:
                        for _ in range(100):
                            if not self.running:
                                break
                            
                            # 随机定位
                            pos = random.randint(0, max(0, file_size - block_size))
                            f.seek(pos)
                            
                            # 读取
                            data = f.read(block_size)
                            operations += 1
                            
                            # 写入
                            f.seek(pos)
                            f.write(os.urandom(len(data)))
                            f.flush()
                            operations += 1
                            
                            time.sleep(0.01)
        
        except Exception as e:
            print(f"Disk I/O stress test error: {e}")
        
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        
        return operations
    
    def run_test(self) -> int:
        """运行磁盘I/O压力测试"""
        self.running = True
        operations_count = 0
        
        with ThreadPoolExecutor(max_workers=self.config.concurrent_workers) as executor:
            futures = []
            
            for i in range(self.config.concurrent_workers):
                future = executor.submit(self._disk_io_task, i)
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    operations = future.result()
                    operations_count += operations
                except Exception as e:
                    print(f"Disk I/O stress test error: {e}")
        
        return operations_count
    
    def stop_test(self):
        """停止测试"""
        self.running = False
        
        # 清理所有临时文件
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        self.temp_files.clear()


class NetworkStressTester:
    """网络压力测试器"""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.running = False
        
    def _network_client_task(self, worker_id: int) -> int:
        """网络客户端任务"""
        operations = 0
        
        target_host = self.config.parameters.get('target_host', 'localhost')
        target_port = self.config.parameters.get('target_port', 8080)
        request_size = self.config.parameters.get('request_size_bytes', 1024)
        
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.config.duration_seconds:
            try:
                # HTTP请求测试
                if self.config.parameters.get('test_type', 'http') == 'http':
                    url = f"http://{target_host}:{target_port}/"
                    
                    # 生成请求数据
                    data = os.urandom(request_size)
                    
                    response = requests.post(
                        url,
                        data=data,
                        timeout=5,
                        headers={'Content-Type': 'application/octet-stream'}
                    )
                    
                    if response.status_code == 200:
                        operations += 1
                
                # TCP Socket测试
                elif self.config.parameters.get('test_type', 'http') == 'tcp':
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    
                    try:
                        sock.connect((target_host, target_port))
                        
                        # 发送数据
                        data = os.urandom(request_size)
                        sock.sendall(data)
                        
                        # 接收响应
                        response = sock.recv(request_size)
                        
                        if response:
                            operations += 1
                    
                    finally:
                        sock.close()
                
                # UDP测试
                elif self.config.parameters.get('test_type', 'http') == 'udp':
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(5)
                    
                    try:
                        data = os.urandom(request_size)
                        sock.sendto(data, (target_host, target_port))
                        
                        response, addr = sock.recvfrom(request_size)
                        
                        if response:
                            operations += 1
                    
                    finally:
                        sock.close()
                
                # 控制请求速率
                if self.config.target_resource_usage < 100:
                    delay = (100 - self.config.target_resource_usage) / 1000
                    time.sleep(delay)
            
            except Exception as e:
                print(f"Network stress test error: {e}")
                time.sleep(1)  # 错误后等待
        
        return operations
    
    def run_test(self) -> int:
        """运行网络压力测试"""
        self.running = True
        operations_count = 0
        
        with ThreadPoolExecutor(max_workers=self.config.concurrent_workers) as executor:
            futures = []
            
            for i in range(self.config.concurrent_workers):
                future = executor.submit(self._network_client_task, i)
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    operations = future.result()
                    operations_count += operations
                except Exception as e:
                    print(f"Network stress test error: {e}")
        
        return operations_count
    
    def stop_test(self):
        """停止测试"""
        self.running = False


class ApplicationStressTester:
    """应用程序压力测试器"""
    
    def __init__(self, config: TestConfiguration):
        self.config = config
        self.running = False
        
    def _application_task(self, worker_id: int) -> int:
        """应用程序压力任务"""
        operations = 0
        
        base_url = self.config.parameters.get('base_url', 'http://localhost:8000')
        endpoints = self.config.parameters.get('endpoints', ['/'])
        request_methods = self.config.parameters.get('methods', ['GET'])
        
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < self.config.duration_seconds:
            try:
                # 随机选择端点和方法
                endpoint = random.choice(endpoints)
                method = random.choice(request_methods)
                url = f"{base_url}{endpoint}"
                
                # 准备请求数据
                headers = {'User-Agent': f'StressTester-Worker-{worker_id}'}
                data = None
                
                if method in ['POST', 'PUT', 'PATCH']:
                    data = {
                        'worker_id': worker_id,
                        'timestamp': time.time(),
                        'data': os.urandom(100).hex()
                    }
                    headers['Content-Type'] = 'application/json'
                
                # 发送请求
                response = requests.request(
                    method=method,
                    url=url,
                    json=data,
                    headers=headers,
                    timeout=10
                )
                
                # 检查响应
                if response.status_code < 500:
                    operations += 1
                
                # 模拟用户思考时间
                think_time = self.config.parameters.get('think_time_ms', 100) / 1000
                time.sleep(think_time)
            
            except Exception as e:
                print(f"Application stress test error: {e}")
                time.sleep(1)
        
        return operations
    
    def run_test(self) -> int:
        """运行应用程序压力测试"""
        self.running = True
        operations_count = 0
        
        with ThreadPoolExecutor(max_workers=self.config.concurrent_workers) as executor:
            futures = []
            
            for i in range(self.config.concurrent_workers):
                future = executor.submit(self._application_task, i)
                futures.append(future)
            
            # 等待所有任务完成
            for future in as_completed(futures):
                try:
                    operations = future.result()
                    operations_count += operations
                except Exception as e:
                    print(f"Application stress test error: {e}")
        
        return operations_count
    
    def stop_test(self):
        """停止测试"""
        self.running = False


class SystemMonitor:
    """系统监控器"""
    
    def __init__(self, interval_seconds: int = 5):
        self.interval_seconds = interval_seconds
        self.running = False
        self.metrics_history = []
        self.initial_stats = None
        
    def start_monitoring(self):
        """开始监控"""
        self.running = True
        self.metrics_history.clear()
        
        # 记录初始状态
        self.initial_stats = {
            'disk_io': psutil.disk_io_counters(),
            'network_io': psutil.net_io_counters()
        }
        
        def monitor_loop():
            while self.running:
                try:
                    metrics = self._collect_metrics()
                    self.metrics_history.append(metrics)
                    time.sleep(self.interval_seconds)
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(self.interval_seconds)
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
    
    def _collect_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用率
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 磁盘I/O
        disk_io = psutil.disk_io_counters()
        disk_io_read = disk_io.read_bytes - self.initial_stats['disk_io'].read_bytes
        disk_io_write = disk_io.write_bytes - self.initial_stats['disk_io'].write_bytes
        
        # 网络I/O
        network_io = psutil.net_io_counters()
        network_sent = network_io.bytes_sent - self.initial_stats['network_io'].bytes_sent
        network_recv = network_io.bytes_recv - self.initial_stats['network_io'].bytes_recv
        
        # 负载平均值
        if hasattr(os, 'getloadavg'):
            load_avg = os.getloadavg()
        else:
            # Windows系统没有getloadavg，使用CPU使用率估算
            load_avg = (cpu_percent / 100 * multiprocessing.cpu_count(), 0, 0)
        
        # 进程和线程数
        process_count = len(psutil.pids())
        thread_count = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info['num_threads'])
        
        # 打开文件数（仅Unix系统）
        try:
            open_files = len(psutil.Process().open_files())
        except:
            open_files = 0
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_io_read_bytes=disk_io_read,
            disk_io_write_bytes=disk_io_write,
            network_bytes_sent=network_sent,
            network_bytes_recv=network_recv,
            load_average=load_avg,
            process_count=process_count,
            thread_count=thread_count,
            open_files=open_files
        )
    
    def get_metrics_summary(self) -> Dict[str, float]:
        """获取指标摘要"""
        if not self.metrics_history:
            return {}
        
        cpu_values = [m.cpu_percent for m in self.metrics_history]
        memory_values = [m.memory_percent for m in self.metrics_history]
        
        return {
            'peak_cpu_usage': max(cpu_values),
            'average_cpu_usage': sum(cpu_values) / len(cpu_values),
            'peak_memory_usage': max(memory_values),
            'average_memory_usage': sum(memory_values) / len(memory_values),
            'total_disk_read_bytes': sum(m.disk_io_read_bytes for m in self.metrics_history),
            'total_disk_write_bytes': sum(m.disk_io_write_bytes for m in self.metrics_history),
            'total_network_sent_bytes': sum(m.network_bytes_sent for m in self.metrics_history),
            'total_network_recv_bytes': sum(m.network_bytes_recv for m in self.metrics_history)
        }


class StressTester:
    """主压力测试器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.logger = self._setup_logger()
        self.monitor = SystemMonitor()
        self.active_tests = {}
        self.test_results = []
        
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置"""
        default_config = {
            "severity_profiles": {
                "low": {
                    "target_resource_usage": 30,
                    "concurrent_workers": 2,
                    "duration_seconds": 300
                },
                "medium": {
                    "target_resource_usage": 60,
                    "concurrent_workers": 4,
                    "duration_seconds": 600
                },
                "high": {
                    "target_resource_usage": 80,
                    "concurrent_workers": 8,
                    "duration_seconds": 900
                },
                "extreme": {
                    "target_resource_usage": 95,
                    "concurrent_workers": 16,
                    "duration_seconds": 1200
                }
            },
            "test_parameters": {
                "cpu": {},
                "memory": {},
                "disk_io": {
                    "file_size_mb": 100,
                    "block_size": 4096,
                    "verify_data": False
                },
                "network": {
                    "target_host": "localhost",
                    "target_port": 8080,
                    "test_type": "http",
                    "request_size_bytes": 1024
                },
                "application": {
                    "base_url": "http://localhost:8000",
                    "endpoints": ["/", "/api/health", "/api/metrics"],
                    "methods": ["GET", "POST"],
                    "think_time_ms": 100
                }
            },
            "monitoring": {
                "interval_seconds": 5,
                "export_metrics": True,
                "alert_thresholds": {
                    "cpu_percent": 90,
                    "memory_percent": 90,
                    "disk_usage_percent": 90
                }
            },
            "output": {
                "results_directory": "./stress_test_results",
                "export_json": True,
                "export_csv": True,
                "generate_report": True
            }
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    default_config.update(user_config)
            except Exception as e:
                print(f"Failed to load config file: {e}")
        
        return default_config
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("StressTester")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def create_test_configuration(self, test_type: StressTestType, 
                                 severity: TestSeverity,
                                 duration_seconds: Optional[int] = None,
                                 **kwargs) -> TestConfiguration:
        """创建测试配置"""
        severity_profile = self.config["severity_profiles"][severity.value]
        test_params = self.config["test_parameters"][test_type.value].copy()
        
        # 更新参数
        test_params.update(kwargs)
        
        config = TestConfiguration(
            test_type=test_type,
            severity=severity,
            duration_seconds=duration_seconds or severity_profile["duration_seconds"],
            concurrent_workers=severity_profile["concurrent_workers"],
            target_resource_usage=severity_profile["target_resource_usage"],
            parameters=test_params
        )
        
        return config
    
    def run_stress_test(self, config: TestConfiguration) -> TestResult:
        """运行压力测试"""
        test_id = f"{config.test_type.value}_{config.severity.value}_{int(time.time())}"
        
        self.logger.info(f"Starting stress test: {test_id}")
        
        # 创建测试结果
        result = TestResult(
            test_id=test_id,
            test_type=config.test_type,
            severity=config.severity,
            status=TestStatus.RUNNING,
            start_time=datetime.now()
        )
        
        # 选择测试器
        tester = None
        if config.test_type == StressTestType.CPU:
            tester = CPUStressTester(config)
        elif config.test_type == StressTestType.MEMORY:
            tester = MemoryStressTester(config)
        elif config.test_type == StressTestType.DISK_IO:
            tester = DiskIOStressTester(config)
        elif config.test_type == StressTestType.NETWORK:
            tester = NetworkStressTester(config)
        elif config.test_type == StressTestType.APPLICATION:
            tester = ApplicationStressTester(config)
        else:
            raise ValueError(f"Unsupported test type: {config.test_type}")
        
        self.active_tests[test_id] = tester
        
        try:
            # 开始监控
            self.monitor.start_monitoring()
            
            # 运行测试
            start_time = time.time()
            operations = tester.run_test()
            end_time = time.time()
            
            # 停止监控
            self.monitor.stop_monitoring()
            
            # 更新结果
            result.end_time = datetime.now()
            result.duration_seconds = end_time - start_time
            result.total_operations = operations
            result.operations_per_second = operations / result.duration_seconds if result.duration_seconds > 0 else 0
            result.status = TestStatus.COMPLETED
            result.metrics_history = self.monitor.metrics_history.copy()
            
            # 计算性能指标
            metrics_summary = self.monitor.get_metrics_summary()
            result.peak_cpu_usage = metrics_summary.get('peak_cpu_usage', 0)
            result.average_cpu_usage = metrics_summary.get('average_cpu_usage', 0)
            result.peak_memory_usage = metrics_summary.get('peak_memory_usage', 0)
            result.average_memory_usage = metrics_summary.get('average_memory_usage', 0)
            
            self.logger.info(f"Stress test completed: {test_id}")
            self.logger.info(f"Operations: {operations}, Duration: {result.duration_seconds:.2f}s")
            self.logger.info(f"Peak CPU: {result.peak_cpu_usage:.1f}%, Peak Memory: {result.peak_memory_usage:.1f}%")
        
        except Exception as e:
            result.status = TestStatus.FAILED
            result.error_messages.append(str(e))
            result.error_count = 1
            result.error_rate = 1.0
            
            self.logger.error(f"Stress test failed: {test_id}, Error: {e}")
        
        finally:
            # 清理
            if test_id in self.active_tests:
                del self.active_tests[test_id]
            
            self.monitor.stop_monitoring()
        
        self.test_results.append(result)
        return result
    
    def run_mixed_stress_test(self, configs: List[TestConfiguration]) -> List[TestResult]:
        """运行混合压力测试"""
        self.logger.info(f"Starting mixed stress test with {len(configs)} test types")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=len(configs)) as executor:
            futures = []
            
            for config in configs:
                future = executor.submit(self.run_stress_test, config)
                futures.append(future)
            
            # 等待所有测试完成
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Mixed stress test error: {e}")
        
        return results
    
    def stop_test(self, test_id: str):
        """停止指定的测试"""
        if test_id in self.active_tests:
            tester = self.active_tests[test_id]
            tester.stop_test()
            self.logger.info(f"Stopped test: {test_id}")
    
    def stop_all_tests(self):
        """停止所有测试"""
        for test_id, tester in self.active_tests.items():
            tester.stop_test()
        
        self.active_tests.clear()
        self.monitor.stop_monitoring()
        self.logger.info("Stopped all tests")
    
    def export_results(self, output_dir: str):
        """导出测试结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 导出JSON格式
        if self.config["output"]["export_json"]:
            json_file = os.path.join(output_dir, f"stress_test_results_{timestamp}.json")
            
            json_data = {
                "test_session": {
                    "timestamp": timestamp,
                    "total_tests": len(self.test_results)
                },
                "results": []
            }
            
            for result in self.test_results:
                result_data = {
                    "test_id": result.test_id,
                    "test_type": result.test_type.value,
                    "severity": result.severity.value,
                    "status": result.status.value,
                    "start_time": result.start_time.isoformat(),
                    "end_time": result.end_time.isoformat() if result.end_time else None,
                    "duration_seconds": result.duration_seconds,
                    "total_operations": result.total_operations,
                    "operations_per_second": result.operations_per_second,
                    "peak_cpu_usage": result.peak_cpu_usage,
                    "average_cpu_usage": result.average_cpu_usage,
                    "peak_memory_usage": result.peak_memory_usage,
                    "average_memory_usage": result.average_memory_usage,
                    "error_count": result.error_count,
                    "error_rate": result.error_rate,
                    "error_messages": result.error_messages
                }
                
                json_data["results"].append(result_data)
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Results exported to JSON: {json_file}")
        
        # 导出CSV格式
        if self.config["output"]["export_csv"]:
            import csv
            
            csv_file = os.path.join(output_dir, f"stress_test_results_{timestamp}.csv")
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 写入表头
                writer.writerow([
                    "test_id", "test_type", "severity", "status", "start_time", "end_time",
                    "duration_seconds", "total_operations", "operations_per_second",
                    "peak_cpu_usage", "average_cpu_usage", "peak_memory_usage", "average_memory_usage",
                    "error_count", "error_rate"
                ])
                
                # 写入数据
                for result in self.test_results:
                    writer.writerow([
                        result.test_id,
                        result.test_type.value,
                        result.severity.value,
                        result.status.value,
                        result.start_time.isoformat(),
                        result.end_time.isoformat() if result.end_time else "",
                        result.duration_seconds,
                        result.total_operations,
                        result.operations_per_second,
                        result.peak_cpu_usage,
                        result.average_cpu_usage,
                        result.peak_memory_usage,
                        result.average_memory_usage,
                        result.error_count,
                        result.error_rate
                    ])
            
            self.logger.info(f"Results exported to CSV: {csv_file}")
        
        # 生成HTML报告
        if self.config["output"]["generate_report"]:
            self._generate_html_report(output_dir, timestamp)
    
    def _generate_html_report(self, output_dir: str, timestamp: str):
        """生成HTML测试报告"""
        html_file = os.path.join(output_dir, f"stress_test_report_{timestamp}.html")
        
        # 计算统计信息
        total_tests = len(self.test_results)
        completed_tests = len([r for r in self.test_results if r.status == TestStatus.COMPLETED])
        failed_tests = len([r for r in self.test_results if r.status == TestStatus.FAILED])
        
        if completed_tests > 0:
            avg_cpu = sum(r.average_cpu_usage for r in self.test_results if r.status == TestStatus.COMPLETED) / completed_tests
            avg_memory = sum(r.average_memory_usage for r in self.test_results if r.status == TestStatus.COMPLETED) / completed_tests
            total_operations = sum(r.total_operations for r in self.test_results if r.status == TestStatus.COMPLETED)
        else:
            avg_cpu = avg_memory = total_operations = 0
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Stress Test Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .summary-item {{ text-align: center; padding: 10px; background-color: #e9e9e9; border-radius: 5px; }}
        .summary-item h3 {{ margin: 0; color: #333; }}
        .summary-item p {{ margin: 5px 0; font-size: 24px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .status-completed {{ color: green; }}
        .status-failed {{ color: red; }}
        .status-running {{ color: orange; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Stress Test Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Test Session: {timestamp}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <h3>Total Tests</h3>
            <p>{total_tests}</p>
        </div>
        <div class="summary-item">
            <h3>Completed</h3>
            <p class="status-completed">{completed_tests}</p>
        </div>
        <div class="summary-item">
            <h3>Failed</h3>
            <p class="status-failed">{failed_tests}</p>
        </div>
        <div class="summary-item">
            <h3>Avg CPU Usage</h3>
            <p>{avg_cpu:.1f}%</p>
        </div>
        <div class="summary-item">
            <h3>Avg Memory Usage</h3>
            <p>{avg_memory:.1f}%</p>
        </div>
        <div class="summary-item">
            <h3>Total Operations</h3>
            <p>{total_operations:,}</p>
        </div>
    </div>
    
    <h2>Test Results</h2>
    <table>
        <thead>
            <tr>
                <th>Test ID</th>
                <th>Type</th>
                <th>Severity</th>
                <th>Status</th>
                <th>Duration (s)</th>
                <th>Operations</th>
                <th>Ops/sec</th>
                <th>Peak CPU (%)</th>
                <th>Peak Memory (%)</th>
                <th>Errors</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for result in self.test_results:
            status_class = f"status-{result.status.value}"
            html_content += f"""
            <tr>
                <td>{result.test_id}</td>
                <td>{result.test_type.value}</td>
                <td>{result.severity.value}</td>
                <td class="{status_class}">{result.status.value}</td>
                <td>{result.duration_seconds:.2f}</td>
                <td>{result.total_operations:,}</td>
                <td>{result.operations_per_second:.2f}</td>
                <td>{result.peak_cpu_usage:.1f}</td>
                <td>{result.peak_memory_usage:.1f}</td>
                <td>{result.error_count}</td>
            </tr>
"""
        
        html_content += """
        </tbody>
    </table>
</body>
</html>
"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"HTML report generated: {html_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Stress Tester")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--test-type", choices=[t.value for t in StressTestType], 
                       help="Type of stress test to run")
    parser.add_argument("--severity", choices=[s.value for s in TestSeverity], 
                       default="medium", help="Test severity level")
    parser.add_argument("--duration", type=int, help="Test duration in seconds")
    parser.add_argument("--workers", type=int, help="Number of concurrent workers")
    parser.add_argument("--target-usage", type=float, help="Target resource usage percentage")
    parser.add_argument("--mixed-test", action="store_true", help="Run mixed stress test")
    parser.add_argument("--output-dir", default="./stress_test_results", help="Output directory")
    
    args = parser.parse_args()
    
    # 创建压力测试器
    tester = StressTester(args.config)
    
    try:
        if args.mixed_test:
            # 运行混合测试
            configs = []
            severity = TestSeverity(args.severity)
            
            for test_type in [StressTestType.CPU, StressTestType.MEMORY, StressTestType.DISK_IO]:
                config = tester.create_test_configuration(
                    test_type=test_type,
                    severity=severity,
                    duration_seconds=args.duration
                )
                
                if args.workers:
                    config.concurrent_workers = args.workers
                if args.target_usage:
                    config.target_resource_usage = args.target_usage
                
                configs.append(config)
            
            print(f"Starting mixed stress test with {len(configs)} test types...")
            results = tester.run_mixed_stress_test(configs)
            
            print(f"\nMixed stress test completed. Results:")
            for result in results:
                print(f"- {result.test_type.value}: {result.status.value}, "
                      f"Operations: {result.total_operations}, "
                      f"Peak CPU: {result.peak_cpu_usage:.1f}%")
        
        elif args.test_type:
            # 运行单个测试
            test_type = StressTestType(args.test_type)
            severity = TestSeverity(args.severity)
            
            config = tester.create_test_configuration(
                test_type=test_type,
                severity=severity,
                duration_seconds=args.duration
            )
            
            if args.workers:
                config.concurrent_workers = args.workers
            if args.target_usage:
                config.target_resource_usage = args.target_usage
            
            print(f"Starting {test_type.value} stress test ({severity.value} severity)...")
            print(f"Duration: {config.duration_seconds}s, Workers: {config.concurrent_workers}, "
                  f"Target Usage: {config.target_resource_usage}%")
            
            result = tester.run_stress_test(config)
            
            print(f"\nStress test completed!")
            print(f"Status: {result.status.value}")
            print(f"Duration: {result.duration_seconds:.2f} seconds")
            print(f"Total Operations: {result.total_operations:,}")
            print(f"Operations/sec: {result.operations_per_second:.2f}")
            print(f"Peak CPU Usage: {result.peak_cpu_usage:.1f}%")
            print(f"Average CPU Usage: {result.average_cpu_usage:.1f}%")
            print(f"Peak Memory Usage: {result.peak_memory_usage:.1f}%")
            print(f"Average Memory Usage: {result.average_memory_usage:.1f}%")
            
            if result.error_count > 0:
                print(f"Errors: {result.error_count} ({result.error_rate:.1%})")
        
        else:
            print("Please specify --test-type or --mixed-test")
            return
        
        # 导出结果
        tester.export_results(args.output_dir)
        print(f"\nResults exported to: {args.output_dir}")
    
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        tester.stop_all_tests()
    
    except Exception as e:
        print(f"Error: {e}")
        tester.stop_all_tests()


if __name__ == "__main__":
    main()