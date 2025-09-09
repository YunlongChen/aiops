#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库工具模块

本模块提供数据库连接和操作功能，包括：
- 多种数据库支持（SQLite、PostgreSQL、MySQL、MongoDB）
- 连接池管理
- 异步数据库操作
- 数据库迁移
- 查询构建器
- 事务管理
- 数据库监控

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple, AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import time
from pathlib import Path

# 可选依赖
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    import aiomysql
    AIOMYSQL_AVAILABLE = True
except ImportError:
    AIOMYSQL_AVAILABLE = False

try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False

try:
    import motor.motor_asyncio
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import text, MetaData, Table, Column, Integer, String, DateTime, Text, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """数据库配置"""
    type: str  # sqlite, postgresql, mysql, mongodb
    host: str = "localhost"
    port: int = 5432
    database: str = "aiops"
    username: str = ""
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"
    options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.options is None:
            self.options = {}
        
        # 设置默认端口
        if self.type == "postgresql" and self.port == 5432:
            pass
        elif self.type == "mysql" and self.port == 5432:
            self.port = 3306
        elif self.type == "mongodb" and self.port == 5432:
            self.port = 27017
    
    def get_connection_string(self) -> str:
        """获取连接字符串"""
        if self.type == "sqlite":
            return f"sqlite+aiosqlite:///{self.database}"
        elif self.type == "postgresql":
            return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == "mysql":
            return f"mysql+aiomysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == "mongodb":
            if self.username and self.password:
                return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            else:
                return f"mongodb://{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.type}")

class DatabaseStats:
    """数据库统计信息"""
    
    def __init__(self):
        self.queries_executed = 0
        self.queries_failed = 0
        self.total_query_time = 0.0
        self.connections_created = 0
        self.connections_closed = 0
        self.active_connections = 0
        self.start_time = time.time()
    
    def record_query(self, execution_time: float, success: bool = True):
        """记录查询统计"""
        self.queries_executed += 1
        self.total_query_time += execution_time
        if not success:
            self.queries_failed += 1
    
    def record_connection_created(self):
        """记录连接创建"""
        self.connections_created += 1
        self.active_connections += 1
    
    def record_connection_closed(self):
        """记录连接关闭"""
        self.connections_closed += 1
        self.active_connections = max(0, self.active_connections - 1)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = time.time() - self.start_time
        avg_query_time = self.total_query_time / self.queries_executed if self.queries_executed > 0 else 0
        success_rate = (self.queries_executed - self.queries_failed) / self.queries_executed if self.queries_executed > 0 else 0
        
        return {
            'queries_executed': self.queries_executed,
            'queries_failed': self.queries_failed,
            'total_query_time': self.total_query_time,
            'average_query_time': avg_query_time,
            'success_rate': success_rate,
            'connections_created': self.connections_created,
            'connections_closed': self.connections_closed,
            'active_connections': self.active_connections,
            'uptime_seconds': uptime
        }

class BaseDatabase(ABC):
    """数据库基类"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.stats = DatabaseStats()
        self._connection = None
        self._pool = None
        self._initialized = False
    
    @abstractmethod
    async def initialize(self):
        """初始化数据库连接"""
        pass
    
    @abstractmethod
    async def close(self):
        """关闭数据库连接"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """执行查询"""
        pass
    
    @abstractmethod
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        pass
    
    @abstractmethod
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """获取所有记录"""
        pass
    
    @abstractmethod
    async def begin_transaction(self):
        """开始事务"""
        pass
    
    @abstractmethod
    async def commit_transaction(self):
        """提交事务"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self):
        """回滚事务"""
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.get_stats()
    
    def _record_query_stats(self, start_time: float, success: bool = True):
        """记录查询统计"""
        execution_time = time.time() - start_time
        self.stats.record_query(execution_time, success)

class SQLiteDatabase(BaseDatabase):
    """SQLite数据库实现"""
    
    def __init__(self, config: DatabaseConfig):
        if not AIOSQLITE_AVAILABLE:
            raise ImportError("aiosqlite库未安装，请运行: pip install aiosqlite")
        
        super().__init__(config)
        self._db_path = Path(config.database)
    
    async def initialize(self):
        """初始化SQLite连接"""
        try:
            # 确保数据库目录存在
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 测试连接
            async with aiosqlite.connect(str(self._db_path)) as conn:
                await conn.execute("SELECT 1")
            
            self._initialized = True
            self.stats.record_connection_created()
            logger.info(f"SQLite数据库已连接: {self._db_path}")
            
        except Exception as e:
            logger.error(f"SQLite连接失败: {e}")
            raise
    
    async def close(self):
        """关闭SQLite连接"""
        self._initialized = False
        self.stats.record_connection_closed()
        logger.info("SQLite连接已关闭")
    
    @asynccontextmanager
    async def _get_connection(self):
        """获取数据库连接"""
        if not self._initialized:
            raise RuntimeError("数据库未初始化")
        
        async with aiosqlite.connect(str(self._db_path)) as conn:
            conn.row_factory = aiosqlite.Row
            yield conn
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """执行查询"""
        start_time = time.time()
        
        try:
            async with self._get_connection() as conn:
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                
                await conn.commit()
                result = cursor.rowcount
                
                self._record_query_stats(start_time, True)
                return result
                
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"SQLite查询执行失败: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        start_time = time.time()
        
        try:
            async with self._get_connection() as conn:
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                
                row = await cursor.fetchone()
                
                self._record_query_stats(start_time, True)
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"SQLite查询失败: {e}")
            raise
    
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """获取所有记录"""
        start_time = time.time()
        
        try:
            async with self._get_connection() as conn:
                if params:
                    cursor = await conn.execute(query, params)
                else:
                    cursor = await conn.execute(query)
                
                rows = await cursor.fetchall()
                
                self._record_query_stats(start_time, True)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"SQLite查询失败: {e}")
            raise
    
    async def begin_transaction(self):
        """开始事务"""
        # SQLite的事务在连接级别管理
        pass
    
    async def commit_transaction(self):
        """提交事务"""
        # SQLite的事务在连接级别管理
        pass
    
    async def rollback_transaction(self):
        """回滚事务"""
        # SQLite的事务在连接级别管理
        pass

class PostgreSQLDatabase(BaseDatabase):
    """PostgreSQL数据库实现"""
    
    def __init__(self, config: DatabaseConfig):
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg库未安装，请运行: pip install asyncpg")
        
        super().__init__(config)
        self._transaction = None
    
    async def initialize(self):
        """初始化PostgreSQL连接池"""
        try:
            self._pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.database,
                min_size=1,
                max_size=self.config.pool_size,
                command_timeout=self.config.pool_timeout
            )
            
            # 测试连接
            async with self._pool.acquire() as conn:
                await conn.execute("SELECT 1")
            
            self._initialized = True
            self.stats.record_connection_created()
            logger.info(f"PostgreSQL连接池已创建: {self.config.host}:{self.config.port}/{self.config.database}")
            
        except Exception as e:
            logger.error(f"PostgreSQL连接失败: {e}")
            raise
    
    async def close(self):
        """关闭PostgreSQL连接池"""
        if self._pool:
            await self._pool.close()
            self._pool = None
        
        self._initialized = False
        self.stats.record_connection_closed()
        logger.info("PostgreSQL连接池已关闭")
    
    @asynccontextmanager
    async def _get_connection(self):
        """获取数据库连接"""
        if not self._initialized or not self._pool:
            raise RuntimeError("数据库未初始化")
        
        async with self._pool.acquire() as conn:
            yield conn
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """执行查询"""
        start_time = time.time()
        
        try:
            if self._transaction:
                # 在事务中执行
                if params:
                    result = await self._transaction.execute(query, *params.values())
                else:
                    result = await self._transaction.execute(query)
            else:
                # 普通执行
                async with self._get_connection() as conn:
                    if params:
                        result = await conn.execute(query, *params.values())
                    else:
                        result = await conn.execute(query)
            
            self._record_query_stats(start_time, True)
            return result
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"PostgreSQL查询执行失败: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        start_time = time.time()
        
        try:
            if self._transaction:
                # 在事务中执行
                if params:
                    row = await self._transaction.fetchrow(query, *params.values())
                else:
                    row = await self._transaction.fetchrow(query)
            else:
                # 普通执行
                async with self._get_connection() as conn:
                    if params:
                        row = await conn.fetchrow(query, *params.values())
                    else:
                        row = await conn.fetchrow(query)
            
            self._record_query_stats(start_time, True)
            
            if row:
                return dict(row)
            return None
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"PostgreSQL查询失败: {e}")
            raise
    
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """获取所有记录"""
        start_time = time.time()
        
        try:
            if self._transaction:
                # 在事务中执行
                if params:
                    rows = await self._transaction.fetch(query, *params.values())
                else:
                    rows = await self._transaction.fetch(query)
            else:
                # 普通执行
                async with self._get_connection() as conn:
                    if params:
                        rows = await conn.fetch(query, *params.values())
                    else:
                        rows = await conn.fetch(query)
            
            self._record_query_stats(start_time, True)
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"PostgreSQL查询失败: {e}")
            raise
    
    async def begin_transaction(self):
        """开始事务"""
        if self._transaction:
            raise RuntimeError("事务已经开始")
        
        async with self._get_connection() as conn:
            self._transaction = conn.transaction()
            await self._transaction.start()
    
    async def commit_transaction(self):
        """提交事务"""
        if not self._transaction:
            raise RuntimeError("没有活动的事务")
        
        await self._transaction.commit()
        self._transaction = None
    
    async def rollback_transaction(self):
        """回滚事务"""
        if not self._transaction:
            raise RuntimeError("没有活动的事务")
        
        await self._transaction.rollback()
        self._transaction = None

class MySQLDatabase(BaseDatabase):
    """MySQL数据库实现"""
    
    def __init__(self, config: DatabaseConfig):
        if not AIOMYSQL_AVAILABLE:
            raise ImportError("aiomysql库未安装，请运行: pip install aiomysql")
        
        super().__init__(config)
        self._transaction_conn = None
    
    async def initialize(self):
        """初始化MySQL连接池"""
        try:
            self._pool = await aiomysql.create_pool(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                db=self.config.database,
                minsize=1,
                maxsize=self.config.pool_size,
                autocommit=True
            )
            
            # 测试连接
            async with self._pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute("SELECT 1")
            
            self._initialized = True
            self.stats.record_connection_created()
            logger.info(f"MySQL连接池已创建: {self.config.host}:{self.config.port}/{self.config.database}")
            
        except Exception as e:
            logger.error(f"MySQL连接失败: {e}")
            raise
    
    async def close(self):
        """关闭MySQL连接池"""
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
        
        self._initialized = False
        self.stats.record_connection_closed()
        logger.info("MySQL连接池已关闭")
    
    @asynccontextmanager
    async def _get_connection(self):
        """获取数据库连接"""
        if not self._initialized or not self._pool:
            raise RuntimeError("数据库未初始化")
        
        if self._transaction_conn:
            yield self._transaction_conn
        else:
            async with self._pool.acquire() as conn:
                yield conn
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """执行查询"""
        start_time = time.time()
        
        try:
            async with self._get_connection() as conn:
                async with conn.cursor() as cursor:
                    if params:
                        await cursor.execute(query, tuple(params.values()))
                    else:
                        await cursor.execute(query)
                    
                    result = cursor.rowcount
                    
                    if not self._transaction_conn:
                        await conn.commit()
            
            self._record_query_stats(start_time, True)
            return result
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MySQL查询执行失败: {e}")
            raise
    
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """获取单条记录"""
        start_time = time.time()
        
        try:
            async with self._get_connection() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    if params:
                        await cursor.execute(query, tuple(params.values()))
                    else:
                        await cursor.execute(query)
                    
                    row = await cursor.fetchone()
            
            self._record_query_stats(start_time, True)
            return row
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MySQL查询失败: {e}")
            raise
    
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """获取所有记录"""
        start_time = time.time()
        
        try:
            async with self._get_connection() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    if params:
                        await cursor.execute(query, tuple(params.values()))
                    else:
                        await cursor.execute(query)
                    
                    rows = await cursor.fetchall()
            
            self._record_query_stats(start_time, True)
            return rows
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MySQL查询失败: {e}")
            raise
    
    async def begin_transaction(self):
        """开始事务"""
        if self._transaction_conn:
            raise RuntimeError("事务已经开始")
        
        self._transaction_conn = await self._pool.acquire()
        await self._transaction_conn.begin()
    
    async def commit_transaction(self):
        """提交事务"""
        if not self._transaction_conn:
            raise RuntimeError("没有活动的事务")
        
        await self._transaction_conn.commit()
        self._pool.release(self._transaction_conn)
        self._transaction_conn = None
    
    async def rollback_transaction(self):
        """回滚事务"""
        if not self._transaction_conn:
            raise RuntimeError("没有活动的事务")
        
        await self._transaction_conn.rollback()
        self._pool.release(self._transaction_conn)
        self._transaction_conn = None

class MongoDatabase(BaseDatabase):
    """MongoDB数据库实现"""
    
    def __init__(self, config: DatabaseConfig):
        if not MOTOR_AVAILABLE:
            raise ImportError("motor库未安装，请运行: pip install motor")
        
        super().__init__(config)
        self._client = None
        self._db = None
    
    async def initialize(self):
        """初始化MongoDB连接"""
        try:
            connection_string = self.config.get_connection_string()
            self._client = motor.motor_asyncio.AsyncIOMotorClient(
                connection_string,
                maxPoolSize=self.config.pool_size
            )
            
            self._db = self._client[self.config.database]
            
            # 测试连接
            await self._client.admin.command('ping')
            
            self._initialized = True
            self.stats.record_connection_created()
            logger.info(f"MongoDB已连接: {self.config.host}:{self.config.port}/{self.config.database}")
            
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
    
    async def close(self):
        """关闭MongoDB连接"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
        
        self._initialized = False
        self.stats.record_connection_closed()
        logger.info("MongoDB连接已关闭")
    
    def get_collection(self, name: str):
        """获取集合"""
        if not self._initialized or not self._db:
            raise RuntimeError("数据库未初始化")
        
        return self._db[name]
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """执行查询（MongoDB不适用）"""
        raise NotImplementedError("MongoDB不支持SQL查询，请使用集合操作")
    
    async def fetch_one(self, query: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """获取单条记录（MongoDB不适用）"""
        raise NotImplementedError("MongoDB不支持SQL查询，请使用集合操作")
    
    async def fetch_all(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """获取所有记录（MongoDB不适用）"""
        raise NotImplementedError("MongoDB不支持SQL查询，请使用集合操作")
    
    async def begin_transaction(self):
        """开始事务"""
        # MongoDB事务需要在会话中管理
        pass
    
    async def commit_transaction(self):
        """提交事务"""
        pass
    
    async def rollback_transaction(self):
        """回滚事务"""
        pass
    
    # MongoDB特有方法
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """插入单个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            result = await coll.insert_one(document)
            
            self._record_query_stats(start_time, True)
            return str(result.inserted_id)
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB插入失败: {e}")
            raise
    
    async def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """插入多个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            result = await coll.insert_many(documents)
            
            self._record_query_stats(start_time, True)
            return [str(oid) for oid in result.inserted_ids]
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB批量插入失败: {e}")
            raise
    
    async def find_one(self, collection: str, filter_dict: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """查找单个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            result = await coll.find_one(filter_dict or {})
            
            self._record_query_stats(start_time, True)
            
            if result:
                result['_id'] = str(result['_id'])
            
            return result
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB查询失败: {e}")
            raise
    
    async def find_many(self, collection: str, filter_dict: Dict[str, Any] = None, 
                       limit: int = None, skip: int = None) -> List[Dict[str, Any]]:
        """查找多个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            cursor = coll.find(filter_dict or {})
            
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            results = []
            async for doc in cursor:
                doc['_id'] = str(doc['_id'])
                results.append(doc)
            
            self._record_query_stats(start_time, True)
            return results
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB查询失败: {e}")
            raise
    
    async def update_one(self, collection: str, filter_dict: Dict[str, Any], 
                        update_dict: Dict[str, Any]) -> int:
        """更新单个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            result = await coll.update_one(filter_dict, {'$set': update_dict})
            
            self._record_query_stats(start_time, True)
            return result.modified_count
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB更新失败: {e}")
            raise
    
    async def update_many(self, collection: str, filter_dict: Dict[str, Any], 
                         update_dict: Dict[str, Any]) -> int:
        """更新多个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            result = await coll.update_many(filter_dict, {'$set': update_dict})
            
            self._record_query_stats(start_time, True)
            return result.modified_count
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB批量更新失败: {e}")
            raise
    
    async def delete_one(self, collection: str, filter_dict: Dict[str, Any]) -> int:
        """删除单个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            result = await coll.delete_one(filter_dict)
            
            self._record_query_stats(start_time, True)
            return result.deleted_count
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB删除失败: {e}")
            raise
    
    async def delete_many(self, collection: str, filter_dict: Dict[str, Any]) -> int:
        """删除多个文档"""
        start_time = time.time()
        
        try:
            coll = self.get_collection(collection)
            result = await coll.delete_many(filter_dict)
            
            self._record_query_stats(start_time, True)
            return result.deleted_count
            
        except Exception as e:
            self._record_query_stats(start_time, False)
            logger.error(f"MongoDB批量删除失败: {e}")
            raise

class QueryBuilder:
    """SQL查询构建器"""
    
    def __init__(self, table: str):
        self.table = table
        self._select_fields = []
        self._where_conditions = []
        self._join_clauses = []
        self._order_by = []
        self._group_by = []
        self._having_conditions = []
        self._limit_value = None
        self._offset_value = None
        self._params = {}
        self._param_counter = 0
    
    def select(self, *fields: str) -> 'QueryBuilder':
        """选择字段"""
        self._select_fields.extend(fields)
        return self
    
    def where(self, condition: str, **params) -> 'QueryBuilder':
        """添加WHERE条件"""
        # 替换参数占位符
        for key, value in params.items():
            param_name = f"param_{self._param_counter}"
            condition = condition.replace(f":{key}", f":{param_name}")
            self._params[param_name] = value
            self._param_counter += 1
        
        self._where_conditions.append(condition)
        return self
    
    def join(self, table: str, on_condition: str, join_type: str = "INNER") -> 'QueryBuilder':
        """添加JOIN"""
        self._join_clauses.append(f"{join_type} JOIN {table} ON {on_condition}")
        return self
    
    def order_by(self, field: str, direction: str = "ASC") -> 'QueryBuilder':
        """添加ORDER BY"""
        self._order_by.append(f"{field} {direction}")
        return self
    
    def group_by(self, *fields: str) -> 'QueryBuilder':
        """添加GROUP BY"""
        self._group_by.extend(fields)
        return self
    
    def having(self, condition: str, **params) -> 'QueryBuilder':
        """添加HAVING条件"""
        # 替换参数占位符
        for key, value in params.items():
            param_name = f"param_{self._param_counter}"
            condition = condition.replace(f":{key}", f":{param_name}")
            self._params[param_name] = value
            self._param_counter += 1
        
        self._having_conditions.append(condition)
        return self
    
    def limit(self, count: int) -> 'QueryBuilder':
        """添加LIMIT"""
        self._limit_value = count
        return self
    
    def offset(self, count: int) -> 'QueryBuilder':
        """添加OFFSET"""
        self._offset_value = count
        return self
    
    def build_select(self) -> Tuple[str, Dict[str, Any]]:
        """构建SELECT查询"""
        # SELECT子句
        if self._select_fields:
            select_clause = f"SELECT {', '.join(self._select_fields)}"
        else:
            select_clause = "SELECT *"
        
        # FROM子句
        from_clause = f"FROM {self.table}"
        
        # JOIN子句
        join_clause = " ".join(self._join_clauses) if self._join_clauses else ""
        
        # WHERE子句
        where_clause = f"WHERE {' AND '.join(self._where_conditions)}" if self._where_conditions else ""
        
        # GROUP BY子句
        group_by_clause = f"GROUP BY {', '.join(self._group_by)}" if self._group_by else ""
        
        # HAVING子句
        having_clause = f"HAVING {' AND '.join(self._having_conditions)}" if self._having_conditions else ""
        
        # ORDER BY子句
        order_by_clause = f"ORDER BY {', '.join(self._order_by)}" if self._order_by else ""
        
        # LIMIT和OFFSET子句
        limit_clause = ""
        if self._limit_value is not None:
            limit_clause = f"LIMIT {self._limit_value}"
            if self._offset_value is not None:
                limit_clause += f" OFFSET {self._offset_value}"
        
        # 组合查询
        query_parts = [select_clause, from_clause, join_clause, where_clause, 
                      group_by_clause, having_clause, order_by_clause, limit_clause]
        
        query = " ".join(part for part in query_parts if part)
        
        return query, self._params
    
    def build_insert(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """构建INSERT查询"""
        fields = list(data.keys())
        placeholders = []
        params = {}
        
        for field in fields:
            param_name = f"param_{self._param_counter}"
            placeholders.append(f":{param_name}")
            params[param_name] = data[field]
            self._param_counter += 1
        
        query = f"INSERT INTO {self.table} ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        
        return query, params
    
    def build_update(self, data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """构建UPDATE查询"""
        set_clauses = []
        params = dict(self._params)
        
        for field, value in data.items():
            param_name = f"param_{self._param_counter}"
            set_clauses.append(f"{field} = :{param_name}")
            params[param_name] = value
            self._param_counter += 1
        
        query = f"UPDATE {self.table} SET {', '.join(set_clauses)}"
        
        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"
        
        return query, params
    
    def build_delete(self) -> Tuple[str, Dict[str, Any]]:
        """构建DELETE查询"""
        query = f"DELETE FROM {self.table}"
        
        if self._where_conditions:
            query += f" WHERE {' AND '.join(self._where_conditions)}"
        
        return query, self._params

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.databases: Dict[str, BaseDatabase] = {}
        self._default_db = None
        self._initialized = False
    
    async def initialize(self):
        """初始化数据库管理器"""
        self._initialized = True
        logger.info("数据库管理器已初始化")
    
    async def cleanup(self):
        """清理所有数据库连接"""
        for db in self.databases.values():
            await db.close()
        
        self.databases.clear()
        self._default_db = None
        self._initialized = False
        logger.info("数据库管理器已清理")
    
    def add_database(self, name: str, config: DatabaseConfig) -> BaseDatabase:
        """添加数据库"""
        if config.type == "sqlite":
            db = SQLiteDatabase(config)
        elif config.type == "postgresql":
            db = PostgreSQLDatabase(config)
        elif config.type == "mysql":
            db = MySQLDatabase(config)
        elif config.type == "mongodb":
            db = MongoDatabase(config)
        else:
            raise ValueError(f"不支持的数据库类型: {config.type}")
        
        self.databases[name] = db
        
        # 设置默认数据库
        if self._default_db is None:
            self._default_db = db
        
        return db
    
    async def initialize_database(self, name: str):
        """初始化指定数据库"""
        if name not in self.databases:
            raise ValueError(f"数据库'{name}'不存在")
        
        await self.databases[name].initialize()
    
    async def initialize_all_databases(self):
        """初始化所有数据库"""
        for name, db in self.databases.items():
            try:
                await db.initialize()
                logger.info(f"数据库'{name}'初始化成功")
            except Exception as e:
                logger.error(f"数据库'{name}'初始化失败: {e}")
    
    def get_database(self, name: str = None) -> BaseDatabase:
        """获取数据库实例"""
        if not self._initialized:
            raise RuntimeError("数据库管理器未初始化")
        
        if name is None:
            if self._default_db is None:
                raise ValueError("没有默认数据库")
            return self._default_db
        
        if name not in self.databases:
            raise ValueError(f"数据库'{name}'不存在")
        
        return self.databases[name]
    
    def query_builder(self, table: str) -> QueryBuilder:
        """创建查询构建器"""
        return QueryBuilder(table)
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有数据库的统计信息"""
        stats = {}
        for name, db in self.databases.items():
            try:
                stats[name] = await db.get_stats()
            except Exception as e:
                logger.warning(f"获取数据库'{name}'统计失败: {e}")
                stats[name] = {'error': str(e)}
        
        return stats

# 全局数据库管理器实例
_db_manager = DatabaseManager()

# 便捷函数
async def get_database_manager() -> DatabaseManager:
    """获取数据库管理器"""
    if not _db_manager._initialized:
        await _db_manager.initialize()
    return _db_manager

async def get_database(name: str = None) -> BaseDatabase:
    """获取数据库实例"""
    manager = await get_database_manager()
    return manager.get_database(name)

async def setup_sqlite_database(name: str, database_path: str) -> SQLiteDatabase:
    """设置SQLite数据库"""
    config = DatabaseConfig(type="sqlite", database=database_path)
    
    manager = await get_database_manager()
    db = manager.add_database(name, config)
    await manager.initialize_database(name)
    
    return db

async def setup_postgresql_database(name: str, host: str, port: int, database: str, 
                                   username: str, password: str) -> PostgreSQLDatabase:
    """设置PostgreSQL数据库"""
    config = DatabaseConfig(
        type="postgresql",
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )
    
    manager = await get_database_manager()
    db = manager.add_database(name, config)
    await manager.initialize_database(name)
    
    return db

async def setup_mysql_database(name: str, host: str, port: int, database: str, 
                              username: str, password: str) -> MySQLDatabase:
    """设置MySQL数据库"""
    config = DatabaseConfig(
        type="mysql",
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )
    
    manager = await get_database_manager()
    db = manager.add_database(name, config)
    await manager.initialize_database(name)
    
    return db

async def setup_mongodb_database(name: str, host: str, port: int, database: str, 
                                username: str = "", password: str = "") -> MongoDatabase:
    """设置MongoDB数据库"""
    config = DatabaseConfig(
        type="mongodb",
        host=host,
        port=port,
        database=database,
        username=username,
        password=password
    )
    
    manager = await get_database_manager()
    db = manager.add_database(name, config)
    await manager.initialize_database(name)
    
    return db

def query_builder(table: str) -> QueryBuilder:
    """创建查询构建器"""
    return QueryBuilder(table)