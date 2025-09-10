#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统资源监控模拟器

该模块模拟系统资源使用情况，包括CPU、内存、磁盘、网络等指标。
支持多种操作系统和硬件配置的模拟。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import random
import threading
import math
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging


class OSType(Enum):
    """操作系统类型枚举"""
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"


class ServerRole(Enum):
    """服务器角色枚举"""
    WEB_SERVER = "web_server"
    DATABASE_SERVER = "database_server"
    APPLICATION_SERVER = "application_server"
    CACHE_SERVER = "cache_server"
    LOAD_BALANCER = "load_balancer"
    STORAGE_SERVER = "storage_server"


@dataclass
class SystemMetrics:
    """系统指标数据类"""
    timestamp: datetime
    hostname: str
    os_type: OSType
    server_role: ServerRole
    
    # CPU指标
    cpu_usage_percent: float
    cpu_user_percent: float
    cpu_system_percent: float
    cpu_idle_percent: float
    cpu_iowait_percent: float
    load_average_1m: float
    load_average_5m: float
    load_average_15m: float
    
    # 内存指标
    memory_total_mb: float
    memory_used_mb: float
    memory_free_mb: float
    memory_available_mb: float
    memory_usage_percent: float
    memory_cached_mb: float
    memory_buffers_mb: float
    swap_total_mb: float
    swap_used_mb: float
    swap_usage_percent: float
    
    # 磁盘指标
    disk_usage_percent: float
    disk_read_iops: float
    disk_write_iops: float
    disk_read_mbps: float
    disk_write_mbps: float
    disk_queue_length: float
    disk_response_time_ms: float
    
    # 网络指标
    network_rx_mbps: float
    network_tx_mbps: float
    network_rx_packets_per_sec: float
    network_tx_packets_per_sec: float
    network_rx_errors: int
    network_tx_errors: int
    network_connections_active: int
    network_connections_established: int
    
    # 进程指标
    processes_total: int
    processes_running: int
    processes_sleeping: int
    processes_zombie: int
    
    # 文件系统指标
    file_descriptors_used: int
    file_descriptors_max: int
    inodes_used: int
    inodes_total: int


@dataclass
class ProcessMetrics:
    """进程指标数据类"""
    timestamp: datetime
    hostname: str
    pid: int
    process_name: str
    command_line: str
    user: str
    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    threads_count: int
    file_descriptors_count: int
    status: str  # running, sleeping, stopped, zombie
    priority: int
    nice_value: int
    start_time: datetime
    uptime_seconds: int


class SystemMonitor:
    """系统资源监控模拟器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化系统监控模拟器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._get_default_config()
        self.system_metrics = []
        self.process_metrics = []
        self.running = False
        self.simulation_threads = []
        self.logger = self._setup_logger()
        
        # 生成服务器列表
        self.servers = self._generate_servers()
        
        # 生成进程列表
        self.processes = self._generate_processes()
        
        # 历史数据用于趋势模拟
        self.history = {}
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "servers": {
                "web-01": {
                    "os": "linux",
                    "role": "web_server",
                    "cpu_cores": 8,
                    "memory_gb": 16,
                    "disk_gb": 500,
                    "network_mbps": 1000
                },
                "web-02": {
                    "os": "linux",
                    "role": "web_server",
                    "cpu_cores": 8,
                    "memory_gb": 16,
                    "disk_gb": 500,
                    "network_mbps": 1000
                },
                "db-01": {
                    "os": "linux",
                    "role": "database_server",
                    "cpu_cores": 16,
                    "memory_gb": 64,
                    "disk_gb": 2000,
                    "network_mbps": 10000
                },
                "app-01": {
                    "os": "linux",
                    "role": "application_server",
                    "cpu_cores": 12,
                    "memory_gb": 32,
                    "disk_gb": 1000,
                    "network_mbps": 1000
                },
                "cache-01": {
                    "os": "linux",
                    "role": "cache_server",
                    "cpu_cores": 4,
                    "memory_gb": 32,
                    "disk_gb": 200,
                    "network_mbps": 1000
                },
                "lb-01": {
                    "os": "linux",
                    "role": "load_balancer",
                    "cpu_cores": 4,
                    "memory_gb": 8,
                    "disk_gb": 100,
                    "network_mbps": 10000
                }
            },
            "monitoring": {
                "system_metrics_interval_seconds": 30,
                "process_metrics_interval_seconds": 60,
                "enable_anomalies": True,
                "anomaly_probability": 0.05
            },
            "workload_patterns": {
                "business_hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],
                "peak_hours": [10, 11, 14, 15, 16],
                "maintenance_hours": [2, 3, 4],
                "base_load_factor": 0.3,
                "peak_load_factor": 0.8,
                "maintenance_load_factor": 0.1
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("SystemMonitor")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _generate_servers(self) -> List[Dict]:
        """生成服务器列表"""
        servers = []
        for hostname, config in self.config["servers"].items():
            servers.append({
                "hostname": hostname,
                "os_type": OSType(config["os"]),
                "server_role": ServerRole(config["role"]),
                "cpu_cores": config["cpu_cores"],
                "memory_gb": config["memory_gb"],
                "disk_gb": config["disk_gb"],
                "network_mbps": config["network_mbps"]
            })
        return servers
    
    def _generate_processes(self) -> Dict[str, List[Dict]]:
        """为每个服务器生成进程列表"""
        processes = {}
        
        for server in self.servers:
            hostname = server["hostname"]
            role = server["server_role"]
            processes[hostname] = []
            
            # 系统进程
            system_processes = [
                {"name": "systemd", "user": "root", "cpu_base": 0.1, "memory_mb": 10},
                {"name": "kthreadd", "user": "root", "cpu_base": 0.0, "memory_mb": 0},
                {"name": "ksoftirqd", "user": "root", "cpu_base": 0.5, "memory_mb": 0},
                {"name": "migration", "user": "root", "cpu_base": 0.1, "memory_mb": 0},
                {"name": "rcu_gp", "user": "root", "cpu_base": 0.1, "memory_mb": 0},
                {"name": "watchdog", "user": "root", "cpu_base": 0.1, "memory_mb": 5},
                {"name": "sshd", "user": "root", "cpu_base": 0.1, "memory_mb": 15},
                {"name": "rsyslog", "user": "syslog", "cpu_base": 0.2, "memory_mb": 8},
                {"name": "cron", "user": "root", "cpu_base": 0.1, "memory_mb": 3},
                {"name": "dbus", "user": "messagebus", "cpu_base": 0.1, "memory_mb": 5}
            ]
            
            # 根据服务器角色添加特定进程
            if role == ServerRole.WEB_SERVER:
                role_processes = [
                    {"name": "nginx", "user": "www-data", "cpu_base": 5.0, "memory_mb": 50},
                    {"name": "nginx", "user": "www-data", "cpu_base": 3.0, "memory_mb": 30},
                    {"name": "nginx", "user": "www-data", "cpu_base": 3.0, "memory_mb": 30},
                    {"name": "nginx", "user": "www-data", "cpu_base": 3.0, "memory_mb": 30},
                    {"name": "php-fpm", "user": "www-data", "cpu_base": 8.0, "memory_mb": 80},
                    {"name": "php-fpm", "user": "www-data", "cpu_base": 6.0, "memory_mb": 70},
                    {"name": "php-fpm", "user": "www-data", "cpu_base": 6.0, "memory_mb": 70}
                ]
            elif role == ServerRole.DATABASE_SERVER:
                role_processes = [
                    {"name": "mysqld", "user": "mysql", "cpu_base": 15.0, "memory_mb": 2048},
                    {"name": "mysql-backup", "user": "mysql", "cpu_base": 2.0, "memory_mb": 100}
                ]
            elif role == ServerRole.APPLICATION_SERVER:
                role_processes = [
                    {"name": "java", "user": "app", "cpu_base": 12.0, "memory_mb": 1024},
                    {"name": "java", "user": "app", "cpu_base": 10.0, "memory_mb": 800},
                    {"name": "node", "user": "app", "cpu_base": 8.0, "memory_mb": 512}
                ]
            elif role == ServerRole.CACHE_SERVER:
                role_processes = [
                    {"name": "redis-server", "user": "redis", "cpu_base": 5.0, "memory_mb": 1024},
                    {"name": "memcached", "user": "memcache", "cpu_base": 3.0, "memory_mb": 512}
                ]
            elif role == ServerRole.LOAD_BALANCER:
                role_processes = [
                    {"name": "haproxy", "user": "haproxy", "cpu_base": 8.0, "memory_mb": 100},
                    {"name": "keepalived", "user": "root", "cpu_base": 1.0, "memory_mb": 20}
                ]
            else:
                role_processes = []
            
            # 合并进程列表
            all_processes = system_processes + role_processes
            
            # 为每个进程分配PID和启动时间
            for i, proc in enumerate(all_processes):
                proc["pid"] = 1000 + i
                proc["start_time"] = datetime.now() - timedelta(
                    seconds=random.randint(3600, 86400 * 30)
                )
                proc["threads"] = random.randint(1, 10)
                proc["file_descriptors"] = random.randint(5, 50)
            
            processes[hostname] = all_processes
        
        return processes
    
    def start_monitoring(self):
        """启动系统监控"""
        self.running = True
        
        # 为每个服务器启动系统指标监控线程
        for server in self.servers:
            hostname = server["hostname"]
            
            # 系统指标线程
            system_thread = threading.Thread(
                target=self._monitor_system_metrics,
                args=(server,),
                name=f"SystemMetrics-{hostname}"
            )
            system_thread.daemon = True
            system_thread.start()
            self.simulation_threads.append(system_thread)
            
            # 进程指标线程
            process_thread = threading.Thread(
                target=self._monitor_process_metrics,
                args=(server,),
                name=f"ProcessMetrics-{hostname}"
            )
            process_thread.daemon = True
            process_thread.start()
            self.simulation_threads.append(process_thread)
        
        self.logger.info(f"System monitoring started for {len(self.servers)} servers")
    
    def stop_monitoring(self):
        """停止系统监控"""
        self.running = False
        
        # 等待所有线程结束
        for thread in self.simulation_threads:
            thread.join(timeout=5)
        
        self.simulation_threads.clear()
        self.logger.info("System monitoring stopped")
    
    def _monitor_system_metrics(self, server: Dict):
        """监控系统指标"""
        hostname = server["hostname"]
        interval = self.config["monitoring"]["system_metrics_interval_seconds"]
        
        # 初始化历史数据
        if hostname not in self.history:
            self.history[hostname] = {
                "cpu_trend": random.uniform(0.2, 0.5),
                "memory_trend": random.uniform(0.4, 0.7),
                "disk_trend": random.uniform(0.3, 0.6),
                "network_trend": random.uniform(0.1, 0.3)
            }
        
        while self.running:
            try:
                metric = self._generate_system_metric(server)
                self.system_metrics.append(metric)
                
                # 保持最近1000条记录
                if len(self.system_metrics) > 1000:
                    self.system_metrics = self.system_metrics[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in system metrics monitoring for {hostname}: {e}")
                time.sleep(interval)
    
    def _monitor_process_metrics(self, server: Dict):
        """监控进程指标"""
        hostname = server["hostname"]
        interval = self.config["monitoring"]["process_metrics_interval_seconds"]
        
        while self.running:
            try:
                processes = self.processes.get(hostname, [])
                for process_config in processes:
                    metric = self._generate_process_metric(server, process_config)
                    self.process_metrics.append(metric)
                
                # 保持最近5000条记录
                if len(self.process_metrics) > 5000:
                    self.process_metrics = self.process_metrics[-5000:]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in process metrics monitoring for {hostname}: {e}")
                time.sleep(interval)
    
    def _generate_system_metric(self, server: Dict) -> SystemMetrics:
        """生成系统指标"""
        hostname = server["hostname"]
        os_type = server["os_type"]
        server_role = server["server_role"]
        
        # 获取负载因子
        load_factor = self._get_load_factor()
        
        # 获取历史趋势
        history = self.history[hostname]
        
        # 生成CPU指标
        cpu_metrics = self._generate_cpu_metrics(server, load_factor, history)
        
        # 生成内存指标
        memory_metrics = self._generate_memory_metrics(server, load_factor, history)
        
        # 生成磁盘指标
        disk_metrics = self._generate_disk_metrics(server, load_factor, history)
        
        # 生成网络指标
        network_metrics = self._generate_network_metrics(server, load_factor, history)
        
        # 生成进程指标
        process_metrics = self._generate_process_summary_metrics(server)
        
        # 生成文件系统指标
        fs_metrics = self._generate_filesystem_metrics(server, load_factor)
        
        # 更新历史趋势（缓慢变化）
        self._update_trends(history, load_factor)
        
        return SystemMetrics(
            timestamp=datetime.now(),
            hostname=hostname,
            os_type=os_type,
            server_role=server_role,
            **cpu_metrics,
            **memory_metrics,
            **disk_metrics,
            **network_metrics,
            **process_metrics,
            **fs_metrics
        )
    
    def _generate_process_metric(self, server: Dict, process_config: Dict) -> ProcessMetrics:
        """生成进程指标"""
        hostname = server["hostname"]
        load_factor = self._get_load_factor()
        
        # 基础CPU使用率
        base_cpu = process_config["cpu_base"]
        cpu_usage = base_cpu * load_factor * random.uniform(0.5, 1.5)
        cpu_usage = min(cpu_usage, 100.0)  # 限制最大值
        
        # 内存使用
        base_memory = process_config["memory_mb"]
        memory_usage = base_memory * random.uniform(0.8, 1.2)
        
        # 计算内存使用百分比
        total_memory_mb = server["memory_gb"] * 1024
        memory_percent = (memory_usage / total_memory_mb) * 100
        
        # 进程状态
        status_choices = ["running", "sleeping", "sleeping", "sleeping", "sleeping"]  # 大部分时间在睡眠
        if random.random() < 0.01:  # 1%概率出现异常状态
            status_choices.extend(["stopped", "zombie"])
        
        # 计算运行时间
        start_time = process_config["start_time"]
        uptime_seconds = int((datetime.now() - start_time).total_seconds())
        
        return ProcessMetrics(
            timestamp=datetime.now(),
            hostname=hostname,
            pid=process_config["pid"],
            process_name=process_config["name"],
            command_line=f"/usr/bin/{process_config['name']}",
            user=process_config["user"],
            cpu_usage_percent=round(cpu_usage, 2),
            memory_usage_mb=round(memory_usage, 2),
            memory_usage_percent=round(memory_percent, 3),
            threads_count=process_config["threads"] + random.randint(-2, 3),
            file_descriptors_count=process_config["file_descriptors"] + random.randint(-5, 10),
            status=random.choice(status_choices),
            priority=random.randint(0, 39),
            nice_value=random.randint(-20, 19),
            start_time=start_time,
            uptime_seconds=uptime_seconds
        )
    
    def _get_load_factor(self) -> float:
        """根据时间获取负载因子"""
        current_hour = datetime.now().hour
        patterns = self.config["workload_patterns"]
        
        if current_hour in patterns["maintenance_hours"]:
            base_factor = patterns["maintenance_load_factor"]
        elif current_hour in patterns["peak_hours"]:
            base_factor = patterns["peak_load_factor"]
        elif current_hour in patterns["business_hours"]:
            base_factor = (patterns["base_load_factor"] + patterns["peak_load_factor"]) / 2
        else:
            base_factor = patterns["base_load_factor"]
        
        # 添加随机变化
        return base_factor * random.uniform(0.7, 1.3)
    
    def _generate_cpu_metrics(self, server: Dict, load_factor: float, history: Dict) -> Dict:
        """生成CPU指标"""
        cpu_cores = server["cpu_cores"]
        
        # 基于历史趋势和当前负载
        base_usage = history["cpu_trend"] * load_factor
        cpu_usage = base_usage * random.uniform(0.8, 1.2)
        cpu_usage = min(cpu_usage, 0.95)  # 限制最大95%
        
        # 分解CPU使用率
        cpu_user = cpu_usage * random.uniform(0.6, 0.8)
        cpu_system = cpu_usage * random.uniform(0.15, 0.25)
        cpu_iowait = cpu_usage * random.uniform(0.05, 0.15)
        cpu_idle = 1.0 - cpu_usage
        
        # 负载平均值
        load_1m = cpu_cores * cpu_usage * random.uniform(0.8, 1.2)
        load_5m = load_1m * random.uniform(0.9, 1.1)
        load_15m = load_5m * random.uniform(0.95, 1.05)
        
        return {
            "cpu_usage_percent": round(cpu_usage * 100, 2),
            "cpu_user_percent": round(cpu_user * 100, 2),
            "cpu_system_percent": round(cpu_system * 100, 2),
            "cpu_idle_percent": round(cpu_idle * 100, 2),
            "cpu_iowait_percent": round(cpu_iowait * 100, 2),
            "load_average_1m": round(load_1m, 2),
            "load_average_5m": round(load_5m, 2),
            "load_average_15m": round(load_15m, 2)
        }
    
    def _generate_memory_metrics(self, server: Dict, load_factor: float, history: Dict) -> Dict:
        """生成内存指标"""
        total_memory_mb = server["memory_gb"] * 1024
        
        # 基于历史趋势
        base_usage_percent = history["memory_trend"] * load_factor
        usage_percent = base_usage_percent * random.uniform(0.9, 1.1)
        usage_percent = min(usage_percent, 0.95)
        
        used_mb = total_memory_mb * usage_percent
        free_mb = total_memory_mb - used_mb
        
        # 缓存和缓冲区
        cached_mb = used_mb * random.uniform(0.2, 0.4)
        buffers_mb = used_mb * random.uniform(0.05, 0.15)
        available_mb = free_mb + cached_mb + buffers_mb
        
        # Swap
        swap_total_mb = total_memory_mb * 0.5  # 通常是内存的一半
        swap_usage_percent = max(0, (usage_percent - 0.8) * 2)  # 内存使用超过80%时开始使用swap
        swap_used_mb = swap_total_mb * swap_usage_percent
        
        return {
            "memory_total_mb": round(total_memory_mb, 2),
            "memory_used_mb": round(used_mb, 2),
            "memory_free_mb": round(free_mb, 2),
            "memory_available_mb": round(available_mb, 2),
            "memory_usage_percent": round(usage_percent * 100, 2),
            "memory_cached_mb": round(cached_mb, 2),
            "memory_buffers_mb": round(buffers_mb, 2),
            "swap_total_mb": round(swap_total_mb, 2),
            "swap_used_mb": round(swap_used_mb, 2),
            "swap_usage_percent": round(swap_usage_percent * 100, 2)
        }
    
    def _generate_disk_metrics(self, server: Dict, load_factor: float, history: Dict) -> Dict:
        """生成磁盘指标"""
        total_disk_gb = server["disk_gb"]
        
        # 磁盘使用率（相对稳定）
        base_usage = history["disk_trend"]
        usage_percent = base_usage * random.uniform(0.95, 1.05)
        
        # 磁盘I/O
        base_iops = 100 * load_factor
        read_iops = base_iops * random.uniform(0.6, 1.4)
        write_iops = base_iops * random.uniform(0.4, 0.8)
        
        # 磁盘吞吐量（假设平均每个I/O操作4KB）
        read_mbps = (read_iops * 4) / 1024
        write_mbps = (write_iops * 4) / 1024
        
        # 磁盘队列长度和响应时间
        queue_length = load_factor * random.uniform(0.5, 3.0)
        response_time_ms = 5 + queue_length * random.uniform(2, 8)
        
        return {
            "disk_usage_percent": round(usage_percent * 100, 2),
            "disk_read_iops": round(read_iops, 2),
            "disk_write_iops": round(write_iops, 2),
            "disk_read_mbps": round(read_mbps, 2),
            "disk_write_mbps": round(write_mbps, 2),
            "disk_queue_length": round(queue_length, 2),
            "disk_response_time_ms": round(response_time_ms, 2)
        }
    
    def _generate_network_metrics(self, server: Dict, load_factor: float, history: Dict) -> Dict:
        """生成网络指标"""
        max_network_mbps = server["network_mbps"]
        
        # 网络使用率
        base_usage = history["network_trend"] * load_factor
        
        # 接收和发送流量
        rx_mbps = max_network_mbps * base_usage * random.uniform(0.5, 1.5)
        tx_mbps = max_network_mbps * base_usage * random.uniform(0.3, 1.2)
        
        # 数据包统计
        rx_packets_per_sec = rx_mbps * 1024 * 1024 / (random.uniform(500, 1500))  # 假设平均包大小
        tx_packets_per_sec = tx_mbps * 1024 * 1024 / (random.uniform(500, 1500))
        
        # 错误统计
        error_rate = 0.001 * load_factor  # 负载高时错误率增加
        rx_errors = int(rx_packets_per_sec * error_rate * random.uniform(0, 2))
        tx_errors = int(tx_packets_per_sec * error_rate * random.uniform(0, 2))
        
        # 连接统计
        base_connections = 100 * load_factor
        active_connections = int(base_connections * random.uniform(0.8, 1.2))
        established_connections = int(active_connections * random.uniform(0.7, 0.9))
        
        return {
            "network_rx_mbps": round(rx_mbps, 2),
            "network_tx_mbps": round(tx_mbps, 2),
            "network_rx_packets_per_sec": round(rx_packets_per_sec, 2),
            "network_tx_packets_per_sec": round(tx_packets_per_sec, 2),
            "network_rx_errors": rx_errors,
            "network_tx_errors": tx_errors,
            "network_connections_active": active_connections,
            "network_connections_established": established_connections
        }
    
    def _generate_process_summary_metrics(self, server: Dict) -> Dict:
        """生成进程汇总指标"""
        hostname = server["hostname"]
        processes = self.processes.get(hostname, [])
        
        total_processes = len(processes)
        running_processes = int(total_processes * random.uniform(0.1, 0.3))
        sleeping_processes = total_processes - running_processes - random.randint(0, 2)
        zombie_processes = random.randint(0, 1)
        
        return {
            "processes_total": total_processes,
            "processes_running": running_processes,
            "processes_sleeping": sleeping_processes,
            "processes_zombie": zombie_processes
        }
    
    def _generate_filesystem_metrics(self, server: Dict, load_factor: float) -> Dict:
        """生成文件系统指标"""
        # 文件描述符
        max_fd = 65536
        used_fd = int(max_fd * load_factor * random.uniform(0.1, 0.3))
        
        # inode
        total_inodes = 1000000
        used_inodes = int(total_inodes * random.uniform(0.1, 0.4))
        
        return {
            "file_descriptors_used": used_fd,
            "file_descriptors_max": max_fd,
            "inodes_used": used_inodes,
            "inodes_total": total_inodes
        }
    
    def _update_trends(self, history: Dict, load_factor: float):
        """更新历史趋势（模拟缓慢变化）"""
        # 趋势变化很慢，每次只调整一点点
        change_factor = 0.02
        
        for key in ["cpu_trend", "memory_trend", "disk_trend", "network_trend"]:
            # 向当前负载因子缓慢调整
            target = load_factor * random.uniform(0.8, 1.2)
            current = history[key]
            
            # 缓慢调整
            if target > current:
                history[key] = min(target, current + change_factor)
            else:
                history[key] = max(target, current - change_factor)
            
            # 确保在合理范围内
            history[key] = max(0.1, min(0.9, history[key]))
    
    def get_recent_system_metrics(self, hostname: Optional[str] = None, count: int = 10) -> List[SystemMetrics]:
        """获取最近的系统指标"""
        metrics = self.system_metrics
        if hostname:
            metrics = [m for m in metrics if m.hostname == hostname]
        return metrics[-count:] if metrics else []
    
    def get_recent_process_metrics(self, hostname: Optional[str] = None, count: int = 50) -> List[ProcessMetrics]:
        """获取最近的进程指标"""
        metrics = self.process_metrics
        if hostname:
            metrics = [m for m in metrics if m.hostname == hostname]
        return metrics[-count:] if metrics else []
    
    def get_high_cpu_processes(self, threshold: float = 80.0) -> List[ProcessMetrics]:
        """获取高CPU使用率的进程"""
        return [p for p in self.process_metrics if p.cpu_usage_percent > threshold]
    
    def get_high_memory_processes(self, threshold: float = 1000.0) -> List[ProcessMetrics]:
        """获取高内存使用的进程（MB）"""
        return [p for p in self.process_metrics if p.memory_usage_mb > threshold]
    
    def export_metrics_to_json(self, filename: str):
        """导出指标到JSON文件"""
        data = {
            "system_metrics": [],
            "process_metrics": [],
            "exported_at": datetime.now().isoformat()
        }
        
        # 转换系统指标
        for metric in self.system_metrics:
            data["system_metrics"].append({
                "timestamp": metric.timestamp.isoformat(),
                "hostname": metric.hostname,
                "os_type": metric.os_type.value,
                "server_role": metric.server_role.value,
                "cpu_usage_percent": metric.cpu_usage_percent,
                "cpu_user_percent": metric.cpu_user_percent,
                "cpu_system_percent": metric.cpu_system_percent,
                "cpu_idle_percent": metric.cpu_idle_percent,
                "cpu_iowait_percent": metric.cpu_iowait_percent,
                "load_average_1m": metric.load_average_1m,
                "load_average_5m": metric.load_average_5m,
                "load_average_15m": metric.load_average_15m,
                "memory_total_mb": metric.memory_total_mb,
                "memory_used_mb": metric.memory_used_mb,
                "memory_free_mb": metric.memory_free_mb,
                "memory_available_mb": metric.memory_available_mb,
                "memory_usage_percent": metric.memory_usage_percent,
                "memory_cached_mb": metric.memory_cached_mb,
                "memory_buffers_mb": metric.memory_buffers_mb,
                "swap_total_mb": metric.swap_total_mb,
                "swap_used_mb": metric.swap_used_mb,
                "swap_usage_percent": metric.swap_usage_percent,
                "disk_usage_percent": metric.disk_usage_percent,
                "disk_read_iops": metric.disk_read_iops,
                "disk_write_iops": metric.disk_write_iops,
                "disk_read_mbps": metric.disk_read_mbps,
                "disk_write_mbps": metric.disk_write_mbps,
                "disk_queue_length": metric.disk_queue_length,
                "disk_response_time_ms": metric.disk_response_time_ms,
                "network_rx_mbps": metric.network_rx_mbps,
                "network_tx_mbps": metric.network_tx_mbps,
                "network_rx_packets_per_sec": metric.network_rx_packets_per_sec,
                "network_tx_packets_per_sec": metric.network_tx_packets_per_sec,
                "network_rx_errors": metric.network_rx_errors,
                "network_tx_errors": metric.network_tx_errors,
                "network_connections_active": metric.network_connections_active,
                "network_connections_established": metric.network_connections_established,
                "processes_total": metric.processes_total,
                "processes_running": metric.processes_running,
                "processes_sleeping": metric.processes_sleeping,
                "processes_zombie": metric.processes_zombie,
                "file_descriptors_used": metric.file_descriptors_used,
                "file_descriptors_max": metric.file_descriptors_max,
                "inodes_used": metric.inodes_used,
                "inodes_total": metric.inodes_total
            })
        
        # 转换进程指标
        for metric in self.process_metrics:
            data["process_metrics"].append({
                "timestamp": metric.timestamp.isoformat(),
                "hostname": metric.hostname,
                "pid": metric.pid,
                "process_name": metric.process_name,
                "command_line": metric.command_line,
                "user": metric.user,
                "cpu_usage_percent": metric.cpu_usage_percent,
                "memory_usage_mb": metric.memory_usage_mb,
                "memory_usage_percent": metric.memory_usage_percent,
                "threads_count": metric.threads_count,
                "file_descriptors_count": metric.file_descriptors_count,
                "status": metric.status,
                "priority": metric.priority,
                "nice_value": metric.nice_value,
                "start_time": metric.start_time.isoformat(),
                "uptime_seconds": metric.uptime_seconds
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Metrics exported to {filename}")
    
    def generate_system_report(self) -> Dict[str, Any]:
        """生成系统报告"""
        if not self.system_metrics:
            return {"error": "No system metrics available"}
        
        report = {
            "summary": {
                "total_servers": len(self.servers),
                "monitoring_duration_minutes": 0,
                "total_system_metrics": len(self.system_metrics),
                "total_process_metrics": len(self.process_metrics)
            },
            "servers": {},
            "alerts": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # 计算监控时长
        if len(self.system_metrics) > 1:
            start_time = min(m.timestamp for m in self.system_metrics)
            end_time = max(m.timestamp for m in self.system_metrics)
            duration = (end_time - start_time).total_seconds() / 60
            report["summary"]["monitoring_duration_minutes"] = round(duration, 1)
        
        # 为每个服务器生成报告
        for server in self.servers:
            hostname = server["hostname"]
            server_metrics = [m for m in self.system_metrics if m.hostname == hostname]
            
            if not server_metrics:
                continue
            
            # 计算平均值
            avg_cpu = sum(m.cpu_usage_percent for m in server_metrics) / len(server_metrics)
            avg_memory = sum(m.memory_usage_percent for m in server_metrics) / len(server_metrics)
            avg_disk = sum(m.disk_usage_percent for m in server_metrics) / len(server_metrics)
            
            # 计算最大值
            max_cpu = max(m.cpu_usage_percent for m in server_metrics)
            max_memory = max(m.memory_usage_percent for m in server_metrics)
            max_load = max(m.load_average_1m for m in server_metrics)
            
            # 检查告警条件
            alerts = []
            if max_cpu > 90:
                alerts.append(f"High CPU usage: {max_cpu:.1f}%")
            if max_memory > 90:
                alerts.append(f"High memory usage: {max_memory:.1f}%")
            if avg_disk > 85:
                alerts.append(f"High disk usage: {avg_disk:.1f}%")
            if max_load > server["cpu_cores"] * 2:
                alerts.append(f"High load average: {max_load:.2f}")
            
            report["servers"][hostname] = {
                "role": server["server_role"].value,
                "os": server["os_type"].value,
                "specs": {
                    "cpu_cores": server["cpu_cores"],
                    "memory_gb": server["memory_gb"],
                    "disk_gb": server["disk_gb"]
                },
                "averages": {
                    "cpu_percent": round(avg_cpu, 1),
                    "memory_percent": round(avg_memory, 1),
                    "disk_percent": round(avg_disk, 1)
                },
                "peaks": {
                    "cpu_percent": round(max_cpu, 1),
                    "memory_percent": round(max_memory, 1),
                    "load_average": round(max_load, 2)
                },
                "alerts": alerts
            }
            
            # 添加到全局告警列表
            for alert in alerts:
                report["alerts"].append(f"{hostname}: {alert}")
        
        return report


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="System Monitor Simulator")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--duration", type=int, default=300, help="Monitoring duration in seconds")
    parser.add_argument("--export", help="Export metrics to JSON file")
    parser.add_argument("--report", help="Generate system report file")
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    
    # 创建监控器
    monitor = SystemMonitor(config)
    
    try:
        # 启动监控
        monitor.start_monitoring()
        
        print(f"System monitoring running for {args.duration} seconds...")
        print("Press Ctrl+C to stop early")
        
        time.sleep(args.duration)
        
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
    finally:
        monitor.stop_monitoring()
        
        # 导出数据
        if args.export:
            monitor.export_metrics_to_json(args.export)
        
        # 生成报告
        if args.report:
            report = monitor.generate_system_report()
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"System report saved to {args.report}")
        
        # 显示简要统计
        report = monitor.generate_system_report()
        if "error" not in report:
            print("\n=== Monitoring Summary ===")
            print(f"Monitored servers: {report['summary']['total_servers']}")
            print(f"Duration: {report['summary']['monitoring_duration_minutes']:.1f} minutes")
            print(f"System metrics collected: {report['summary']['total_system_metrics']}")
            print(f"Process metrics collected: {report['summary']['total_process_metrics']}")
            if report['alerts']:
                print(f"Alerts generated: {len(report['alerts'])}")
                for alert in report['alerts'][:5]:  # 显示前5个告警
                    print(f"  - {alert}")


if __name__ == "__main__":
    main()