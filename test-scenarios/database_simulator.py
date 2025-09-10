#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模拟器

该模块模拟数据库操作和性能指标，用于测试数据库监控功能。
支持多种数据库类型的模拟，包括MySQL、PostgreSQL、MongoDB等。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import sqlite3
import os


class DatabaseType(Enum):
    """数据库类型枚举"""
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    ELASTICSEARCH = "elasticsearch"


class QueryType(Enum):
    """查询类型枚举"""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    INDEX = "INDEX"
    AGGREGATE = "AGGREGATE"


@dataclass
class QueryMetrics:
    """查询指标数据类"""
    timestamp: datetime
    database_type: DatabaseType
    query_type: QueryType
    table_name: str
    duration_ms: float
    rows_affected: int
    rows_examined: int
    bytes_sent: int
    bytes_received: int
    connection_id: str
    user: str
    query_hash: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class DatabaseMetrics:
    """数据库系统指标数据类"""
    timestamp: datetime
    database_type: DatabaseType
    instance_name: str
    cpu_usage: float
    memory_usage_mb: float
    memory_usage_percent: float
    disk_usage_mb: float
    disk_io_read_mbps: float
    disk_io_write_mbps: float
    network_io_mbps: float
    active_connections: int
    max_connections: int
    queries_per_second: float
    slow_queries_count: int
    lock_waits: int
    deadlocks: int
    cache_hit_ratio: float
    buffer_pool_usage: float


class DatabaseSimulator:
    """数据库模拟器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化数据库模拟器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._get_default_config()
        self.query_metrics = []
        self.system_metrics = []
        self.running = False
        self.simulation_threads = []
        self.logger = self._setup_logger()
        
        # 初始化模拟数据库
        self.mock_db_path = "mock_database.db"
        self._setup_mock_database()
        
        # 模拟数据
        self.tables = self._generate_mock_tables()
        self.users = self._generate_mock_users()
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "databases": {
                "mysql_primary": {
                    "type": "mysql",
                    "host": "localhost",
                    "port": 3306,
                    "max_connections": 100,
                    "buffer_pool_size_mb": 1024,
                    "query_cache_size_mb": 256
                },
                "postgresql_analytics": {
                    "type": "postgresql",
                    "host": "localhost",
                    "port": 5432,
                    "max_connections": 200,
                    "shared_buffers_mb": 512,
                    "work_mem_mb": 64
                },
                "mongodb_logs": {
                    "type": "mongodb",
                    "host": "localhost",
                    "port": 27017,
                    "max_connections": 1000,
                    "cache_size_mb": 2048
                },
                "redis_cache": {
                    "type": "redis",
                    "host": "localhost",
                    "port": 6379,
                    "max_memory_mb": 512,
                    "max_connections": 10000
                }
            },
            "workload": {
                "base_qps": 50,
                "peak_qps": 200,
                "peak_hours": [9, 10, 11, 14, 15, 16, 20, 21],
                "slow_query_threshold_ms": 1000,
                "slow_query_rate": 0.05,
                "error_rate": 0.01,
                "query_distribution": {
                    "SELECT": 0.70,
                    "INSERT": 0.15,
                    "UPDATE": 0.10,
                    "DELETE": 0.03,
                    "AGGREGATE": 0.02
                }
            },
            "monitoring": {
                "metrics_interval_seconds": 30,
                "query_log_enabled": True,
                "slow_query_log_enabled": True
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("DatabaseSimulator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_mock_database(self):
        """设置模拟数据库"""
        if os.path.exists(self.mock_db_path):
            os.remove(self.mock_db_path)
        
        conn = sqlite3.connect(self.mock_db_path)
        cursor = conn.cursor()
        
        # 创建模拟表
        tables_sql = [
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username VARCHAR(50),
                email VARCHAR(100),
                created_at TIMESTAMP,
                last_login TIMESTAMP,
                status VARCHAR(20)
            )
            """,
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100),
                category VARCHAR(50),
                price DECIMAL(10,2),
                stock INTEGER,
                created_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                total_amount DECIMAL(10,2),
                status VARCHAR(20),
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """,
            """
            CREATE TABLE order_items (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                price DECIMAL(10,2),
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """,
            """
            CREATE TABLE analytics_events (
                id INTEGER PRIMARY KEY,
                event_type VARCHAR(50),
                user_id INTEGER,
                properties TEXT,
                timestamp TIMESTAMP
            )
            """
        ]
        
        for sql in tables_sql:
            cursor.execute(sql)
        
        # 插入一些示例数据
        self._insert_sample_data(cursor)
        
        conn.commit()
        conn.close()
        
        self.logger.info("Mock database setup completed")
    
    def _insert_sample_data(self, cursor):
        """插入示例数据"""
        # 插入用户数据
        for i in range(1000):
            cursor.execute(
                "INSERT INTO users (username, email, created_at, last_login, status) VALUES (?, ?, ?, ?, ?)",
                (f"user{i}", f"user{i}@example.com", datetime.now() - timedelta(days=random.randint(1, 365)),
                 datetime.now() - timedelta(hours=random.randint(1, 168)), 
                 random.choice(["active", "inactive", "suspended"]))
            )
        
        # 插入产品数据
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
        for i in range(500):
            cursor.execute(
                "INSERT INTO products (name, category, price, stock, created_at) VALUES (?, ?, ?, ?, ?)",
                (f"Product {i}", random.choice(categories), round(random.uniform(10, 1000), 2),
                 random.randint(0, 100), datetime.now() - timedelta(days=random.randint(1, 180)))
            )
        
        # 插入订单数据
        for i in range(2000):
            cursor.execute(
                "INSERT INTO orders (user_id, total_amount, status, created_at) VALUES (?, ?, ?, ?)",
                (random.randint(1, 1000), round(random.uniform(20, 500), 2),
                 random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
                 datetime.now() - timedelta(days=random.randint(0, 90)))
            )
    
    def _generate_mock_tables(self) -> List[Dict]:
        """生成模拟表信息"""
        return [
            {"name": "users", "rows": 1000, "size_mb": 5.2, "indexes": 3},
            {"name": "products", "rows": 500, "size_mb": 2.8, "indexes": 2},
            {"name": "orders", "rows": 2000, "size_mb": 8.5, "indexes": 4},
            {"name": "order_items", "rows": 5000, "size_mb": 12.3, "indexes": 3},
            {"name": "analytics_events", "rows": 50000, "size_mb": 125.6, "indexes": 2}
        ]
    
    def _generate_mock_users(self) -> List[str]:
        """生成模拟用户列表"""
        return [f"app_user_{i}" for i in range(1, 21)] + ["admin", "readonly", "backup_user"]
    
    def start_simulation(self):
        """启动数据库模拟"""
        self.running = True
        
        # 为每个数据库实例启动模拟线程
        for db_name, db_config in self.config["databases"].items():
            # 查询模拟线程
            query_thread = threading.Thread(
                target=self._simulate_queries,
                args=(db_name, db_config),
                name=f"QuerySim-{db_name}"
            )
            query_thread.daemon = True
            query_thread.start()
            self.simulation_threads.append(query_thread)
            
            # 系统指标模拟线程
            metrics_thread = threading.Thread(
                target=self._simulate_system_metrics,
                args=(db_name, db_config),
                name=f"MetricsSim-{db_name}"
            )
            metrics_thread.daemon = True
            metrics_thread.start()
            self.simulation_threads.append(metrics_thread)
        
        self.logger.info(f"Database simulation started for {len(self.config['databases'])} instances")
    
    def stop_simulation(self):
        """停止数据库模拟"""
        self.running = False
        
        # 等待所有线程结束
        for thread in self.simulation_threads:
            thread.join(timeout=5)
        
        self.simulation_threads.clear()
        self.logger.info("Database simulation stopped")
    
    def _simulate_queries(self, db_name: str, db_config: Dict):
        """模拟数据库查询"""
        db_type = DatabaseType(db_config["type"])
        
        while self.running:
            try:
                # 计算当前QPS
                current_hour = datetime.now().hour
                if current_hour in self.config["workload"]["peak_hours"]:
                    target_qps = self.config["workload"]["peak_qps"]
                else:
                    target_qps = self.config["workload"]["base_qps"]
                
                # 添加随机变化
                actual_qps = target_qps * random.uniform(0.7, 1.3)
                interval = 1.0 / actual_qps
                
                # 生成查询
                query_metric = self._generate_query_metric(db_name, db_type)
                self.query_metrics.append(query_metric)
                
                # 保持最近10000条记录
                if len(self.query_metrics) > 10000:
                    self.query_metrics = self.query_metrics[-10000:]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in query simulation for {db_name}: {e}")
                time.sleep(1)
    
    def _simulate_system_metrics(self, db_name: str, db_config: Dict):
        """模拟系统指标"""
        db_type = DatabaseType(db_config["type"])
        interval = self.config["monitoring"]["metrics_interval_seconds"]
        
        while self.running:
            try:
                metric = self._generate_system_metric(db_name, db_type, db_config)
                self.system_metrics.append(metric)
                
                # 保持最近1000条记录
                if len(self.system_metrics) > 1000:
                    self.system_metrics = self.system_metrics[-1000:]
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in system metrics simulation for {db_name}: {e}")
                time.sleep(interval)
    
    def _generate_query_metric(self, db_name: str, db_type: DatabaseType) -> QueryMetrics:
        """生成查询指标"""
        # 选择查询类型
        query_types = list(self.config["workload"]["query_distribution"].keys())
        weights = list(self.config["workload"]["query_distribution"].values())
        query_type_str = random.choices(query_types, weights=weights)[0]
        query_type = QueryType(query_type_str)
        
        # 选择表
        table = random.choice(self.tables)
        table_name = table["name"]
        
        # 生成查询时间
        base_duration = self._get_base_query_duration(query_type, db_type)
        duration_ms = base_duration * random.uniform(0.3, 3.0)
        
        # 模拟慢查询
        if random.random() < self.config["workload"]["slow_query_rate"]:
            duration_ms *= random.uniform(5, 20)
        
        # 模拟错误
        success = random.random() > self.config["workload"]["error_rate"]
        error_message = None
        if not success:
            error_message = random.choice([
                "Table doesn't exist",
                "Syntax error",
                "Lock wait timeout",
                "Deadlock found",
                "Connection lost",
                "Out of memory"
            ])
            duration_ms *= random.uniform(0.1, 2.0)  # 错误查询可能很快或很慢
        
        # 生成其他指标
        rows_affected, rows_examined = self._calculate_row_metrics(query_type, table, success)
        bytes_sent, bytes_received = self._calculate_byte_metrics(query_type, rows_affected)
        
        return QueryMetrics(
            timestamp=datetime.now(),
            database_type=db_type,
            query_type=query_type,
            table_name=table_name,
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            rows_examined=rows_examined,
            bytes_sent=bytes_sent,
            bytes_received=bytes_received,
            connection_id=f"conn_{random.randint(1, 100)}",
            user=random.choice(self.users),
            query_hash=f"hash_{random.randint(100000, 999999)}",
            success=success,
            error_message=error_message
        )
    
    def _generate_system_metric(self, db_name: str, db_type: DatabaseType, db_config: Dict) -> DatabaseMetrics:
        """生成系统指标"""
        # 基础负载
        base_cpu = random.uniform(0.2, 0.6)
        base_memory_percent = random.uniform(0.4, 0.8)
        
        # 根据时间调整负载
        current_hour = datetime.now().hour
        if current_hour in self.config["workload"]["peak_hours"]:
            load_factor = random.uniform(1.2, 2.0)
        else:
            load_factor = random.uniform(0.7, 1.1)
        
        cpu_usage = min(0.95, base_cpu * load_factor)
        memory_usage_percent = min(0.95, base_memory_percent * load_factor)
        
        # 计算内存使用量（MB）
        max_memory_mb = db_config.get("buffer_pool_size_mb", 1024) + 512  # 加上系统开销
        memory_usage_mb = max_memory_mb * memory_usage_percent
        
        # 磁盘I/O
        disk_io_read = random.uniform(5, 50) * load_factor
        disk_io_write = random.uniform(2, 20) * load_factor
        
        # 网络I/O
        network_io = random.uniform(1, 10) * load_factor
        
        # 连接数
        max_connections = db_config.get("max_connections", 100)
        active_connections = int(max_connections * random.uniform(0.1, 0.8) * load_factor)
        active_connections = min(active_connections, max_connections)
        
        # QPS
        base_qps = self.config["workload"]["base_qps"]
        queries_per_second = base_qps * load_factor * random.uniform(0.8, 1.2)
        
        # 慢查询数量
        slow_queries_count = int(queries_per_second * self.config["workload"]["slow_query_rate"] * 30)  # 30秒内
        
        # 锁等待和死锁
        lock_waits = random.randint(0, int(queries_per_second * 0.1))
        deadlocks = random.randint(0, max(1, int(queries_per_second * 0.01)))
        
        # 缓存命中率
        cache_hit_ratio = random.uniform(0.85, 0.98)
        if load_factor > 1.5:  # 高负载时缓存命中率可能下降
            cache_hit_ratio *= random.uniform(0.9, 1.0)
        
        # 缓冲池使用率
        buffer_pool_usage = random.uniform(0.6, 0.9)
        
        return DatabaseMetrics(
            timestamp=datetime.now(),
            database_type=db_type,
            instance_name=db_name,
            cpu_usage=cpu_usage,
            memory_usage_mb=memory_usage_mb,
            memory_usage_percent=memory_usage_percent,
            disk_usage_mb=random.uniform(1000, 10000),  # 磁盘使用量相对稳定
            disk_io_read_mbps=disk_io_read,
            disk_io_write_mbps=disk_io_write,
            network_io_mbps=network_io,
            active_connections=active_connections,
            max_connections=max_connections,
            queries_per_second=queries_per_second,
            slow_queries_count=slow_queries_count,
            lock_waits=lock_waits,
            deadlocks=deadlocks,
            cache_hit_ratio=cache_hit_ratio,
            buffer_pool_usage=buffer_pool_usage
        )
    
    def _get_base_query_duration(self, query_type: QueryType, db_type: DatabaseType) -> float:
        """获取基础查询时间（毫秒）"""
        base_times = {
            QueryType.SELECT: {
                DatabaseType.MYSQL: 50,
                DatabaseType.POSTGRESQL: 45,
                DatabaseType.MONGODB: 30,
                DatabaseType.REDIS: 5,
                DatabaseType.ELASTICSEARCH: 100
            },
            QueryType.INSERT: {
                DatabaseType.MYSQL: 20,
                DatabaseType.POSTGRESQL: 25,
                DatabaseType.MONGODB: 15,
                DatabaseType.REDIS: 2,
                DatabaseType.ELASTICSEARCH: 50
            },
            QueryType.UPDATE: {
                DatabaseType.MYSQL: 30,
                DatabaseType.POSTGRESQL: 35,
                DatabaseType.MONGODB: 20,
                DatabaseType.REDIS: 3,
                DatabaseType.ELASTICSEARCH: 80
            },
            QueryType.DELETE: {
                DatabaseType.MYSQL: 25,
                DatabaseType.POSTGRESQL: 30,
                DatabaseType.MONGODB: 18,
                DatabaseType.REDIS: 2,
                DatabaseType.ELASTICSEARCH: 60
            },
            QueryType.AGGREGATE: {
                DatabaseType.MYSQL: 200,
                DatabaseType.POSTGRESQL: 180,
                DatabaseType.MONGODB: 150,
                DatabaseType.REDIS: 10,
                DatabaseType.ELASTICSEARCH: 300
            }
        }
        
        return base_times.get(query_type, {}).get(db_type, 50)
    
    def _calculate_row_metrics(self, query_type: QueryType, table: Dict, success: bool) -> Tuple[int, int]:
        """计算行相关指标"""
        if not success:
            return 0, 0
        
        table_rows = table["rows"]
        
        if query_type == QueryType.SELECT:
            rows_examined = random.randint(1, min(1000, table_rows))
            rows_affected = random.randint(1, min(100, rows_examined))
        elif query_type == QueryType.INSERT:
            rows_affected = random.randint(1, 10)
            rows_examined = 0
        elif query_type == QueryType.UPDATE:
            rows_affected = random.randint(1, min(50, table_rows // 10))
            rows_examined = rows_affected * random.randint(1, 5)
        elif query_type == QueryType.DELETE:
            rows_affected = random.randint(1, min(20, table_rows // 20))
            rows_examined = rows_affected * random.randint(1, 3)
        elif query_type == QueryType.AGGREGATE:
            rows_examined = random.randint(100, min(10000, table_rows))
            rows_affected = 1  # 聚合查询通常返回一行结果
        else:
            rows_affected = 0
            rows_examined = 0
        
        return rows_affected, rows_examined
    
    def _calculate_byte_metrics(self, query_type: QueryType, rows_affected: int) -> Tuple[int, int]:
        """计算字节相关指标"""
        if query_type == QueryType.SELECT:
            # SELECT查询发送少量数据，接收较多数据
            bytes_sent = random.randint(100, 500)
            bytes_received = rows_affected * random.randint(50, 200)
        elif query_type in [QueryType.INSERT, QueryType.UPDATE]:
            # INSERT/UPDATE发送较多数据，接收少量确认
            bytes_sent = rows_affected * random.randint(100, 500)
            bytes_received = random.randint(50, 200)
        elif query_type == QueryType.DELETE:
            # DELETE发送少量数据，接收少量确认
            bytes_sent = random.randint(50, 200)
            bytes_received = random.randint(50, 100)
        elif query_type == QueryType.AGGREGATE:
            # 聚合查询发送中等数据，接收少量结果
            bytes_sent = random.randint(200, 800)
            bytes_received = random.randint(100, 1000)
        else:
            bytes_sent = random.randint(50, 200)
            bytes_received = random.randint(50, 200)
        
        return bytes_sent, bytes_received
    
    def get_recent_query_metrics(self, count: int = 100) -> List[QueryMetrics]:
        """获取最近的查询指标"""
        return self.query_metrics[-count:] if self.query_metrics else []
    
    def get_recent_system_metrics(self, count: int = 10) -> List[DatabaseMetrics]:
        """获取最近的系统指标"""
        return self.system_metrics[-count:] if self.system_metrics else []
    
    def get_slow_queries(self, threshold_ms: Optional[float] = None) -> List[QueryMetrics]:
        """获取慢查询"""
        if threshold_ms is None:
            threshold_ms = self.config["workload"]["slow_query_threshold_ms"]
        
        return [q for q in self.query_metrics if q.duration_ms > threshold_ms]
    
    def get_failed_queries(self) -> List[QueryMetrics]:
        """获取失败的查询"""
        return [q for q in self.query_metrics if not q.success]
    
    def export_metrics_to_json(self, filename: str):
        """导出指标到JSON文件"""
        data = {
            "query_metrics": [],
            "system_metrics": [],
            "exported_at": datetime.now().isoformat()
        }
        
        # 转换查询指标
        for metric in self.query_metrics:
            data["query_metrics"].append({
                "timestamp": metric.timestamp.isoformat(),
                "database_type": metric.database_type.value,
                "query_type": metric.query_type.value,
                "table_name": metric.table_name,
                "duration_ms": metric.duration_ms,
                "rows_affected": metric.rows_affected,
                "rows_examined": metric.rows_examined,
                "bytes_sent": metric.bytes_sent,
                "bytes_received": metric.bytes_received,
                "connection_id": metric.connection_id,
                "user": metric.user,
                "query_hash": metric.query_hash,
                "success": metric.success,
                "error_message": metric.error_message
            })
        
        # 转换系统指标
        for metric in self.system_metrics:
            data["system_metrics"].append({
                "timestamp": metric.timestamp.isoformat(),
                "database_type": metric.database_type.value,
                "instance_name": metric.instance_name,
                "cpu_usage": metric.cpu_usage,
                "memory_usage_mb": metric.memory_usage_mb,
                "memory_usage_percent": metric.memory_usage_percent,
                "disk_usage_mb": metric.disk_usage_mb,
                "disk_io_read_mbps": metric.disk_io_read_mbps,
                "disk_io_write_mbps": metric.disk_io_write_mbps,
                "network_io_mbps": metric.network_io_mbps,
                "active_connections": metric.active_connections,
                "max_connections": metric.max_connections,
                "queries_per_second": metric.queries_per_second,
                "slow_queries_count": metric.slow_queries_count,
                "lock_waits": metric.lock_waits,
                "deadlocks": metric.deadlocks,
                "cache_hit_ratio": metric.cache_hit_ratio,
                "buffer_pool_usage": metric.buffer_pool_usage
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Metrics exported to {filename}")
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """生成性能报告"""
        if not self.query_metrics or not self.system_metrics:
            return {"error": "No metrics available"}
        
        # 查询统计
        total_queries = len(self.query_metrics)
        successful_queries = len([q for q in self.query_metrics if q.success])
        failed_queries = total_queries - successful_queries
        
        # 响应时间统计
        response_times = [q.duration_ms for q in self.query_metrics if q.success]
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = 0
        
        # 慢查询统计
        slow_queries = self.get_slow_queries()
        slow_query_rate = len(slow_queries) / total_queries if total_queries > 0 else 0
        
        # 按查询类型统计
        query_type_stats = {}
        for query in self.query_metrics:
            query_type = query.query_type.value
            if query_type not in query_type_stats:
                query_type_stats[query_type] = {"count": 0, "total_time": 0, "errors": 0}
            
            query_type_stats[query_type]["count"] += 1
            query_type_stats[query_type]["total_time"] += query.duration_ms
            if not query.success:
                query_type_stats[query_type]["errors"] += 1
        
        # 计算平均时间
        for stats in query_type_stats.values():
            stats["avg_time"] = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
            stats["error_rate"] = stats["errors"] / stats["count"] if stats["count"] > 0 else 0
            del stats["total_time"]  # 删除中间计算值
        
        # 系统资源统计
        recent_system_metrics = self.get_recent_system_metrics(10)
        if recent_system_metrics:
            avg_cpu = sum(m.cpu_usage for m in recent_system_metrics) / len(recent_system_metrics)
            avg_memory = sum(m.memory_usage_percent for m in recent_system_metrics) / len(recent_system_metrics)
            avg_connections = sum(m.active_connections for m in recent_system_metrics) / len(recent_system_metrics)
            avg_qps = sum(m.queries_per_second for m in recent_system_metrics) / len(recent_system_metrics)
        else:
            avg_cpu = avg_memory = avg_connections = avg_qps = 0
        
        return {
            "summary": {
                "total_queries": total_queries,
                "successful_queries": successful_queries,
                "failed_queries": failed_queries,
                "success_rate": successful_queries / total_queries if total_queries > 0 else 0,
                "slow_queries": len(slow_queries),
                "slow_query_rate": slow_query_rate
            },
            "response_times": {
                "average_ms": round(avg_response_time, 2),
                "min_ms": round(min_response_time, 2),
                "max_ms": round(max_response_time, 2),
                "p95_ms": round(p95_response_time, 2)
            },
            "query_types": query_type_stats,
            "system_resources": {
                "avg_cpu_usage": round(avg_cpu, 3),
                "avg_memory_usage": round(avg_memory, 3),
                "avg_active_connections": round(avg_connections, 1),
                "avg_queries_per_second": round(avg_qps, 1)
            },
            "generated_at": datetime.now().isoformat()
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Simulator")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--duration", type=int, default=300, help="Simulation duration in seconds")
    parser.add_argument("--export", help="Export metrics to JSON file")
    parser.add_argument("--report", help="Generate performance report file")
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    
    # 创建模拟器
    simulator = DatabaseSimulator(config)
    
    try:
        # 启动模拟
        simulator.start_simulation()
        
        print(f"Database simulation running for {args.duration} seconds...")
        print("Press Ctrl+C to stop early")
        
        time.sleep(args.duration)
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user")
    finally:
        simulator.stop_simulation()
        
        # 导出数据
        if args.export:
            simulator.export_metrics_to_json(args.export)
        
        # 生成报告
        if args.report:
            report = simulator.generate_performance_report()
            with open(args.report, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"Performance report saved to {args.report}")
        
        # 显示简要统计
        report = simulator.generate_performance_report()
        if "error" not in report:
            print("\n=== Simulation Summary ===")
            print(f"Total queries: {report['summary']['total_queries']}")
            print(f"Success rate: {report['summary']['success_rate']:.2%}")
            print(f"Average response time: {report['response_times']['average_ms']:.2f}ms")
            print(f"Slow query rate: {report['summary']['slow_query_rate']:.2%}")


if __name__ == "__main__":
    main()