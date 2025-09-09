#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
缓存管理工具模块

本模块提供多种缓存实现和管理功能，包括：
- 内存缓存（LRU、LFU、TTL）
- Redis缓存
- 文件缓存
- 分布式缓存
- 缓存装饰器
- 缓存统计和监控

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import os
import json
import pickle
import hashlib
import time
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from collections import OrderedDict
from threading import Lock, RLock
from pathlib import Path
import weakref
from functools import wraps
import logging
from abc import ABC, abstractmethod

# 可选依赖
try:
    import redis
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import memcache
    MEMCACHE_AVAILABLE = True
except ImportError:
    MEMCACHE_AVAILABLE = False

logger = logging.getLogger(__name__)

class CacheStats:
    """缓存统计信息"""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        self.evictions = 0
        self.start_time = time.time()
        self._lock = Lock()
    
    def record_hit(self):
        """记录缓存命中"""
        with self._lock:
            self.hits += 1
    
    def record_miss(self):
        """记录缓存未命中"""
        with self._lock:
            self.misses += 1
    
    def record_set(self):
        """记录缓存设置"""
        with self._lock:
            self.sets += 1
    
    def record_delete(self):
        """记录缓存删除"""
        with self._lock:
            self.deletes += 1
    
    def record_eviction(self):
        """记录缓存驱逐"""
        with self._lock:
            self.evictions += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            uptime = time.time() - self.start_time
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'sets': self.sets,
                'deletes': self.deletes,
                'evictions': self.evictions,
                'total_requests': total_requests,
                'hit_rate': hit_rate,
                'uptime_seconds': uptime
            }
    
    def reset(self):
        """重置统计信息"""
        with self._lock:
            self.hits = 0
            self.misses = 0
            self.sets = 0
            self.deletes = 0
            self.evictions = 0
            self.start_time = time.time()

class CacheEntry:
    """缓存条目"""
    
    def __init__(self, value: Any, ttl: Optional[float] = None, access_count: int = 0):
        self.value = value
        self.created_at = time.time()
        self.last_accessed = self.created_at
        self.access_count = access_count
        self.ttl = ttl
        self.expires_at = self.created_at + ttl if ttl else None
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at
    
    def access(self) -> Any:
        """访问缓存条目"""
        self.last_accessed = time.time()
        self.access_count += 1
        return self.value
    
    def update_ttl(self, ttl: Optional[float]):
        """更新TTL"""
        self.ttl = ttl
        if ttl:
            self.expires_at = time.time() + ttl
        else:
            self.expires_at = None

class BaseCache(ABC):
    """缓存基类"""
    
    def __init__(self, name: str = "cache"):
        self.name = name
        self.stats = CacheStats()
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空缓存"""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """获取缓存大小"""
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.get_stats()
    
    def _generate_key(self, key: str) -> str:
        """生成缓存键"""
        if isinstance(key, str):
            return key
        return hashlib.md5(str(key).encode()).hexdigest()

class MemoryCache(BaseCache):
    """内存缓存实现"""
    
    def __init__(self, name: str = "memory_cache", max_size: int = 1000, 
                 default_ttl: Optional[float] = None, eviction_policy: str = "lru"):
        super().__init__(name)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.eviction_policy = eviction_policy.lower()
        self._cache = OrderedDict()
        self._lock = RLock()
        
        # 启动清理任务
        self._cleanup_task = None
        self._should_stop_cleanup = False
    
    async def initialize(self):
        """初始化缓存"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_expired())
    
    async def cleanup(self):
        """清理资源"""
        self._should_stop_cleanup = True
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache_key = self._generate_key(key)
        
        with self._lock:
            if cache_key not in self._cache:
                self.stats.record_miss()
                return None
            
            entry = self._cache[cache_key]
            
            # 检查是否过期
            if entry.is_expired():
                del self._cache[cache_key]
                self.stats.record_miss()
                self.stats.record_eviction()
                return None
            
            # 更新访问信息（用于LRU和LFU）
            value = entry.access()
            
            # LRU: 移动到末尾
            if self.eviction_policy == "lru":
                self._cache.move_to_end(cache_key)
            
            self.stats.record_hit()
            return value
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        cache_key = self._generate_key(key)
        effective_ttl = ttl if ttl is not None else self.default_ttl
        
        with self._lock:
            # 如果缓存已满，执行驱逐策略
            if len(self._cache) >= self.max_size and cache_key not in self._cache:
                self._evict_one()
            
            # 创建或更新缓存条目
            if cache_key in self._cache:
                # 更新现有条目
                entry = self._cache[cache_key]
                entry.value = value
                entry.update_ttl(effective_ttl)
            else:
                # 创建新条目
                entry = CacheEntry(value, effective_ttl)
                self._cache[cache_key] = entry
            
            # LRU: 移动到末尾
            if self.eviction_policy == "lru":
                self._cache.move_to_end(cache_key)
            
            self.stats.record_set()
            return True
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        cache_key = self._generate_key(key)
        
        with self._lock:
            if cache_key in self._cache:
                del self._cache[cache_key]
                self.stats.record_delete()
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        cache_key = self._generate_key(key)
        
        with self._lock:
            if cache_key not in self._cache:
                return False
            
            entry = self._cache[cache_key]
            if entry.is_expired():
                del self._cache[cache_key]
                self.stats.record_eviction()
                return False
            
            return True
    
    async def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            return True
    
    async def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def _evict_one(self):
        """驱逐一个缓存条目"""
        if not self._cache:
            return
        
        if self.eviction_policy == "lru":
            # 删除最久未使用的（第一个）
            self._cache.popitem(last=False)
        elif self.eviction_policy == "lfu":
            # 删除使用频率最低的
            min_key = min(self._cache.keys(), 
                         key=lambda k: self._cache[k].access_count)
            del self._cache[min_key]
        elif self.eviction_policy == "fifo":
            # 删除最先进入的（第一个）
            self._cache.popitem(last=False)
        else:
            # 默认删除第一个
            self._cache.popitem(last=False)
        
        self.stats.record_eviction()
    
    async def _cleanup_expired(self):
        """清理过期条目的后台任务"""
        while not self._should_stop_cleanup:
            try:
                await asyncio.sleep(60)  # 每分钟清理一次
                
                with self._lock:
                    expired_keys = []
                    for key, entry in self._cache.items():
                        if entry.is_expired():
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self._cache[key]
                        self.stats.record_eviction()
                
                if expired_keys:
                    logger.debug(f"清理了{len(expired_keys)}个过期缓存条目")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理过期缓存条目时出错: {e}")

class RedisCache(BaseCache):
    """Redis缓存实现"""
    
    def __init__(self, name: str = "redis_cache", host: str = "localhost", 
                 port: int = 6379, db: int = 0, password: Optional[str] = None,
                 key_prefix: str = "aiops:", default_ttl: Optional[float] = None):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis库未安装，请运行: pip install redis")
        
        super().__init__(name)
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self._redis = None
    
    async def initialize(self):
        """初始化Redis连接"""
        try:
            self._redis = aioredis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=False  # 保持二进制数据
            )
            
            # 测试连接
            await self._redis.ping()
            logger.info(f"Redis缓存已连接: {self.host}:{self.port}/{self.db}")
            
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    async def cleanup(self):
        """清理Redis连接"""
        if self._redis:
            await self._redis.close()
    
    def _get_full_key(self, key: str) -> str:
        """获取完整的Redis键"""
        return f"{self.key_prefix}{self._generate_key(key)}"
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            full_key = self._get_full_key(key)
            data = await self._redis.get(full_key)
            
            if data is None:
                self.stats.record_miss()
                return None
            
            # 反序列化数据
            value = pickle.loads(data)
            self.stats.record_hit()
            return value
            
        except Exception as e:
            logger.error(f"Redis获取缓存失败: {e}")
            self.stats.record_miss()
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            full_key = self._get_full_key(key)
            effective_ttl = ttl if ttl is not None else self.default_ttl
            
            # 序列化数据
            data = pickle.dumps(value)
            
            if effective_ttl:
                await self._redis.setex(full_key, int(effective_ttl), data)
            else:
                await self._redis.set(full_key, data)
            
            self.stats.record_set()
            return True
            
        except Exception as e:
            logger.error(f"Redis设置缓存失败: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            full_key = self._get_full_key(key)
            result = await self._redis.delete(full_key)
            
            if result > 0:
                self.stats.record_delete()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Redis删除缓存失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            full_key = self._get_full_key(key)
            result = await self._redis.exists(full_key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis检查键存在失败: {e}")
            return False
    
    async def clear(self) -> bool:
        """清空缓存"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            # 删除所有带前缀的键
            pattern = f"{self.key_prefix}*"
            keys = await self._redis.keys(pattern)
            
            if keys:
                await self._redis.delete(*keys)
            
            return True
            
        except Exception as e:
            logger.error(f"Redis清空缓存失败: {e}")
            return False
    
    async def size(self) -> int:
        """获取缓存大小"""
        if not self._redis:
            raise RuntimeError("Redis未初始化")
        
        try:
            pattern = f"{self.key_prefix}*"
            keys = await self._redis.keys(pattern)
            return len(keys)
            
        except Exception as e:
            logger.error(f"Redis获取缓存大小失败: {e}")
            return 0

class FileCache(BaseCache):
    """文件缓存实现"""
    
    def __init__(self, name: str = "file_cache", cache_dir: str = "./cache",
                 max_size: int = 1000, default_ttl: Optional[float] = None):
        super().__init__(name)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._lock = Lock()
        
        # 元数据文件
        self.metadata_file = self.cache_dir / "metadata.json"
        self._metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """加载元数据"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"加载缓存元数据失败: {e}")
        
        return {}
    
    def _save_metadata(self):
        """保存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            logger.error(f"保存缓存元数据失败: {e}")
    
    def _get_file_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        cache_key = self._generate_key(key)
        return self.cache_dir / f"{cache_key}.cache"
    
    def _is_expired(self, key: str) -> bool:
        """检查是否过期"""
        if key not in self._metadata:
            return True
        
        metadata = self._metadata[key]
        expires_at = metadata.get('expires_at')
        
        if expires_at is None:
            return False
        
        return time.time() > expires_at
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        cache_key = self._generate_key(key)
        file_path = self._get_file_path(key)
        
        with self._lock:
            if not file_path.exists() or cache_key not in self._metadata:
                self.stats.record_miss()
                return None
            
            # 检查是否过期
            if self._is_expired(cache_key):
                self._remove_cache_file(cache_key, file_path)
                self.stats.record_miss()
                self.stats.record_eviction()
                return None
            
            try:
                # 读取缓存文件
                with open(file_path, 'rb') as f:
                    value = pickle.load(f)
                
                # 更新访问时间
                self._metadata[cache_key]['last_accessed'] = time.time()
                self._metadata[cache_key]['access_count'] += 1
                self._save_metadata()
                
                self.stats.record_hit()
                return value
                
            except Exception as e:
                logger.error(f"读取缓存文件失败: {e}")
                self._remove_cache_file(cache_key, file_path)
                self.stats.record_miss()
                return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置缓存值"""
        cache_key = self._generate_key(key)
        file_path = self._get_file_path(key)
        effective_ttl = ttl if ttl is not None else self.default_ttl
        
        with self._lock:
            try:
                # 如果缓存已满，执行驱逐策略
                if len(self._metadata) >= self.max_size and cache_key not in self._metadata:
                    self._evict_one()
                
                # 写入缓存文件
                with open(file_path, 'wb') as f:
                    pickle.dump(value, f)
                
                # 更新元数据
                now = time.time()
                self._metadata[cache_key] = {
                    'created_at': now,
                    'last_accessed': now,
                    'access_count': 0,
                    'expires_at': now + effective_ttl if effective_ttl else None,
                    'file_size': file_path.stat().st_size
                }
                
                self._save_metadata()
                self.stats.record_set()
                return True
                
            except Exception as e:
                logger.error(f"写入缓存文件失败: {e}")
                return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        cache_key = self._generate_key(key)
        file_path = self._get_file_path(key)
        
        with self._lock:
            if cache_key in self._metadata:
                self._remove_cache_file(cache_key, file_path)
                self.stats.record_delete()
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        cache_key = self._generate_key(key)
        file_path = self._get_file_path(key)
        
        with self._lock:
            if not file_path.exists() or cache_key not in self._metadata:
                return False
            
            if self._is_expired(cache_key):
                self._remove_cache_file(cache_key, file_path)
                self.stats.record_eviction()
                return False
            
            return True
    
    async def clear(self) -> bool:
        """清空缓存"""
        with self._lock:
            try:
                # 删除所有缓存文件
                for cache_key in list(self._metadata.keys()):
                    file_path = self._get_file_path(cache_key)
                    self._remove_cache_file(cache_key, file_path)
                
                return True
                
            except Exception as e:
                logger.error(f"清空文件缓存失败: {e}")
                return False
    
    async def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._metadata)
    
    def _remove_cache_file(self, cache_key: str, file_path: Path):
        """删除缓存文件"""
        try:
            if file_path.exists():
                file_path.unlink()
            
            if cache_key in self._metadata:
                del self._metadata[cache_key]
                self._save_metadata()
                
        except Exception as e:
            logger.error(f"删除缓存文件失败: {e}")
    
    def _evict_one(self):
        """驱逐一个缓存条目（LRU策略）"""
        if not self._metadata:
            return
        
        # 找到最久未访问的条目
        oldest_key = min(self._metadata.keys(), 
                        key=lambda k: self._metadata[k]['last_accessed'])
        
        file_path = self._get_file_path(oldest_key)
        self._remove_cache_file(oldest_key, file_path)
        self.stats.record_eviction()

class MultiLevelCache(BaseCache):
    """多级缓存实现"""
    
    def __init__(self, name: str = "multi_level_cache", caches: List[BaseCache] = None):
        super().__init__(name)
        self.caches = caches or []
        self._initialized = False
    
    async def initialize(self):
        """初始化所有缓存层"""
        for cache in self.caches:
            if hasattr(cache, 'initialize'):
                await cache.initialize()
        self._initialized = True
    
    async def cleanup(self):
        """清理所有缓存层"""
        for cache in self.caches:
            if hasattr(cache, 'cleanup'):
                await cache.cleanup()
    
    def add_cache_level(self, cache: BaseCache):
        """添加缓存层"""
        self.caches.append(cache)
    
    async def get(self, key: str) -> Optional[Any]:
        """从多级缓存获取值"""
        if not self._initialized:
            raise RuntimeError("多级缓存未初始化")
        
        for i, cache in enumerate(self.caches):
            try:
                value = await cache.get(key)
                if value is not None:
                    # 将值写入更高级别的缓存
                    for j in range(i):
                        try:
                            await self.caches[j].set(key, value)
                        except Exception as e:
                            logger.warning(f"写入L{j}缓存失败: {e}")
                    
                    self.stats.record_hit()
                    return value
            except Exception as e:
                logger.warning(f"L{i}缓存获取失败: {e}")
                continue
        
        self.stats.record_miss()
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """设置多级缓存值"""
        if not self._initialized:
            raise RuntimeError("多级缓存未初始化")
        
        success = False
        for i, cache in enumerate(self.caches):
            try:
                if await cache.set(key, value, ttl):
                    success = True
            except Exception as e:
                logger.warning(f"L{i}缓存设置失败: {e}")
        
        if success:
            self.stats.record_set()
        
        return success
    
    async def delete(self, key: str) -> bool:
        """删除多级缓存值"""
        if not self._initialized:
            raise RuntimeError("多级缓存未初始化")
        
        success = False
        for i, cache in enumerate(self.caches):
            try:
                if await cache.delete(key):
                    success = True
            except Exception as e:
                logger.warning(f"L{i}缓存删除失败: {e}")
        
        if success:
            self.stats.record_delete()
        
        return success
    
    async def exists(self, key: str) -> bool:
        """检查键是否存在于任何缓存层"""
        if not self._initialized:
            raise RuntimeError("多级缓存未初始化")
        
        for cache in self.caches:
            try:
                if await cache.exists(key):
                    return True
            except Exception as e:
                logger.warning(f"缓存存在检查失败: {e}")
        
        return False
    
    async def clear(self) -> bool:
        """清空所有缓存层"""
        if not self._initialized:
            raise RuntimeError("多级缓存未初始化")
        
        success = True
        for cache in self.caches:
            try:
                await cache.clear()
            except Exception as e:
                logger.warning(f"缓存清空失败: {e}")
                success = False
        
        return success
    
    async def size(self) -> int:
        """获取第一级缓存的大小"""
        if not self._initialized or not self.caches:
            return 0
        
        try:
            return await self.caches[0].size()
        except Exception:
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取所有缓存层的统计信息"""
        stats = await super().get_stats()
        stats['cache_levels'] = []
        
        for i, cache in enumerate(self.caches):
            try:
                level_stats = await cache.get_stats()
                level_stats['level'] = i
                level_stats['name'] = cache.name
                stats['cache_levels'].append(level_stats)
            except Exception as e:
                logger.warning(f"获取L{i}缓存统计失败: {e}")
        
        return stats

class CacheManager:
    """缓存管理器"""
    
    def __init__(self):
        self.caches: Dict[str, BaseCache] = {}
        self._default_cache = None
        self._initialized = False
    
    async def initialize(self):
        """初始化缓存管理器"""
        # 创建默认内存缓存
        self._default_cache = MemoryCache("default")
        await self._default_cache.initialize()
        self.caches["default"] = self._default_cache
        
        self._initialized = True
        logger.info("缓存管理器已初始化")
    
    async def cleanup(self):
        """清理所有缓存"""
        for cache in self.caches.values():
            if hasattr(cache, 'cleanup'):
                await cache.cleanup()
        
        self.caches.clear()
        self._default_cache = None
        self._initialized = False
        logger.info("缓存管理器已清理")
    
    def add_cache(self, name: str, cache: BaseCache):
        """添加缓存实例"""
        self.caches[name] = cache
    
    def get_cache(self, name: str = "default") -> BaseCache:
        """获取缓存实例"""
        if not self._initialized:
            raise RuntimeError("缓存管理器未初始化")
        
        if name not in self.caches:
            raise ValueError(f"缓存'{name}'不存在")
        
        return self.caches[name]
    
    async def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """获取所有缓存的统计信息"""
        stats = {}
        for name, cache in self.caches.items():
            try:
                stats[name] = await cache.get_stats()
            except Exception as e:
                logger.warning(f"获取缓存'{name}'统计失败: {e}")
                stats[name] = {'error': str(e)}
        
        return stats

# 缓存装饰器
def cached(cache_name: str = "default", ttl: Optional[float] = None, 
          key_func: Optional[Callable] = None):
    """
    缓存装饰器
    
    Args:
        cache_name: 缓存名称
        ttl: 过期时间
        key_func: 键生成函数
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # 获取缓存
            cache = _cache_manager.get_cache(cache_name)
            
            # 尝试从缓存获取
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 对于同步函数，需要在事件循环中运行
            import asyncio
            
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            async def _async_operation():
                # 获取缓存
                cache = _cache_manager.get_cache(cache_name)
                
                # 尝试从缓存获取
                cached_result = await cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # 执行函数并缓存结果
                result = func(*args, **kwargs)
                await cache.set(cache_key, result, ttl)
                
                return result
            
            try:
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(_async_operation())
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                return asyncio.run(_async_operation())
        
        # 根据函数类型返回相应的包装器
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# 全局缓存管理器实例
_cache_manager = CacheManager()

# 便捷函数
async def get_cache_manager() -> CacheManager:
    """获取缓存管理器"""
    if not _cache_manager._initialized:
        await _cache_manager.initialize()
    return _cache_manager

async def get_cache(name: str = "default") -> BaseCache:
    """获取缓存实例"""
    manager = await get_cache_manager()
    return manager.get_cache(name)

async def setup_redis_cache(name: str, host: str = "localhost", port: int = 6379, 
                           db: int = 0, password: Optional[str] = None) -> RedisCache:
    """设置Redis缓存"""
    cache = RedisCache(name, host, port, db, password)
    await cache.initialize()
    
    manager = await get_cache_manager()
    manager.add_cache(name, cache)
    
    return cache

async def setup_multi_level_cache(name: str, cache_configs: List[Dict[str, Any]]) -> MultiLevelCache:
    """设置多级缓存"""
    caches = []
    
    for config in cache_configs:
        cache_type = config.get('type', 'memory')
        
        if cache_type == 'memory':
            cache = MemoryCache(**{k: v for k, v in config.items() if k != 'type'})
        elif cache_type == 'redis':
            cache = RedisCache(**{k: v for k, v in config.items() if k != 'type'})
        elif cache_type == 'file':
            cache = FileCache(**{k: v for k, v in config.items() if k != 'type'})
        else:
            raise ValueError(f"不支持的缓存类型: {cache_type}")
        
        await cache.initialize()
        caches.append(cache)
    
    multi_cache = MultiLevelCache(name, caches)
    await multi_cache.initialize()
    
    manager = await get_cache_manager()
    manager.add_cache(name, multi_cache)
    
    return multi_cache