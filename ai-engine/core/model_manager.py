#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型管理器模块

本模块实现了AI模型的生命周期管理，包括：
- 模型加载和保存
- 模型版本控制
- 模型性能监控
- 模型自动更新
- 模型A/B测试
- 模型部署管理

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import os
import json
import pickle
import hashlib
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 机器学习库
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import cross_val_score

# 深度学习库
import tensorflow as tf
from tensorflow.keras.models import load_model, save_model
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping

# 模型序列化
import joblib

# 版本控制
from packaging import version

from utils.logger import setup_logger
from utils.cache import CacheManager
from utils.config import Config

logger = setup_logger(__name__)

class ModelMetadata:
    """模型元数据类"""
    
    def __init__(self, model_id: str, model_type: str, version: str, 
                 created_at: datetime = None, **kwargs):
        self.model_id = model_id
        self.model_type = model_type
        self.version = version
        self.created_at = created_at or datetime.now()
        self.updated_at = self.created_at
        self.metadata = kwargs
        
        # 性能指标
        self.performance_metrics = {}
        
        # 训练信息
        self.training_info = {
            'dataset_size': 0,
            'training_time': 0.0,
            'epochs': 0,
            'loss': 0.0,
            'accuracy': 0.0
        }
        
        # 部署信息
        self.deployment_info = {
            'status': 'created',
            'deployed_at': None,
            'endpoint': None,
            'replicas': 1
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'model_id': self.model_id,
            'model_type': self.model_type,
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata,
            'performance_metrics': self.performance_metrics,
            'training_info': self.training_info,
            'deployment_info': self.deployment_info
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelMetadata':
        """从字典创建"""
        metadata = cls(
            model_id=data['model_id'],
            model_type=data['model_type'],
            version=data['version'],
            created_at=datetime.fromisoformat(data['created_at']),
            **data.get('metadata', {})
        )
        
        metadata.updated_at = datetime.fromisoformat(data['updated_at'])
        metadata.performance_metrics = data.get('performance_metrics', {})
        metadata.training_info = data.get('training_info', {})
        metadata.deployment_info = data.get('deployment_info', {})
        
        return metadata

class ModelStorage:
    """模型存储类"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.models_dir = self.base_path / 'models'
        self.metadata_dir = self.base_path / 'metadata'
        self.checkpoints_dir = self.base_path / 'checkpoints'
        self.exports_dir = self.base_path / 'exports'
        
        for dir_path in [self.models_dir, self.metadata_dir, 
                        self.checkpoints_dir, self.exports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def save_model(self, model: Any, metadata: ModelMetadata) -> str:
        """
        保存模型
        
        Args:
            model: 模型对象
            metadata: 模型元数据
            
        Returns:
            模型文件路径
        """
        try:
            model_dir = self.models_dir / metadata.model_id / metadata.version
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # 根据模型类型选择保存方式
            if isinstance(model, tf.keras.Model):
                model_path = model_dir / 'model.h5'
                model.save(str(model_path))
            elif hasattr(model, 'save'):
                model_path = model_dir / 'model.pkl'
                joblib.dump(model, str(model_path))
            else:
                model_path = model_dir / 'model.pkl'
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
            
            # 保存元数据
            metadata_path = self.metadata_dir / f"{metadata.model_id}_{metadata.version}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"模型已保存: {model_path}")
            return str(model_path)
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
            raise
    
    def load_model(self, model_id: str, version: str = None) -> Tuple[Any, ModelMetadata]:
        """
        加载模型
        
        Args:
            model_id: 模型ID
            version: 版本号，如果为None则加载最新版本
            
        Returns:
            模型对象和元数据
        """
        try:
            if version is None:
                version = self.get_latest_version(model_id)
            
            if version is None:
                raise ValueError(f"模型{model_id}不存在")
            
            # 加载元数据
            metadata_path = self.metadata_dir / f"{model_id}_{version}.json"
            if not metadata_path.exists():
                raise FileNotFoundError(f"元数据文件不存在: {metadata_path}")
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata_dict = json.load(f)
            
            metadata = ModelMetadata.from_dict(metadata_dict)
            
            # 加载模型
            model_dir = self.models_dir / model_id / version
            
            # 尝试不同的模型文件格式
            model_files = [
                model_dir / 'model.h5',
                model_dir / 'model.pkl',
                model_dir / 'model.joblib'
            ]
            
            model = None
            for model_path in model_files:
                if model_path.exists():
                    try:
                        if model_path.suffix == '.h5':
                            model = load_model(str(model_path))
                        elif model_path.suffix in ['.pkl', '.joblib']:
                            model = joblib.load(str(model_path))
                        break
                    except Exception as e:
                        logger.warning(f"加载模型文件{model_path}失败: {e}")
                        continue
            
            if model is None:
                raise ValueError(f"无法加载模型{model_id}版本{version}")
            
            logger.info(f"模型已加载: {model_id} v{version}")
            return model, metadata
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def delete_model(self, model_id: str, version: str = None) -> bool:
        """
        删除模型
        
        Args:
            model_id: 模型ID
            version: 版本号，如果为None则删除所有版本
            
        Returns:
            是否成功删除
        """
        try:
            if version is None:
                # 删除所有版本
                model_dir = self.models_dir / model_id
                if model_dir.exists():
                    shutil.rmtree(model_dir)
                
                # 删除所有元数据文件
                for metadata_file in self.metadata_dir.glob(f"{model_id}_*.json"):
                    metadata_file.unlink()
            else:
                # 删除特定版本
                version_dir = self.models_dir / model_id / version
                if version_dir.exists():
                    shutil.rmtree(version_dir)
                
                # 删除元数据文件
                metadata_file = self.metadata_dir / f"{model_id}_{version}.json"
                if metadata_file.exists():
                    metadata_file.unlink()
            
            logger.info(f"模型已删除: {model_id} v{version or 'all'}")
            return True
            
        except Exception as e:
            logger.error(f"删除模型失败: {e}")
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        列出所有模型
        
        Returns:
            模型列表
        """
        try:
            models = []
            
            for metadata_file in self.metadata_dir.glob("*.json"):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_dict = json.load(f)
                    models.append(metadata_dict)
                except Exception as e:
                    logger.warning(f"读取元数据文件{metadata_file}失败: {e}")
            
            return models
            
        except Exception as e:
            logger.error(f"列出模型失败: {e}")
            return []
    
    def get_latest_version(self, model_id: str) -> Optional[str]:
        """
        获取最新版本号
        
        Args:
            model_id: 模型ID
            
        Returns:
            最新版本号
        """
        try:
            versions = []
            
            for metadata_file in self.metadata_dir.glob(f"{model_id}_*.json"):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata_dict = json.load(f)
                    versions.append(metadata_dict['version'])
                except Exception:
                    continue
            
            if not versions:
                return None
            
            # 按版本号排序
            versions.sort(key=lambda v: version.parse(v), reverse=True)
            return versions[0]
            
        except Exception as e:
            logger.error(f"获取最新版本失败: {e}")
            return None
    
    def create_checkpoint(self, model: Any, model_id: str, epoch: int) -> str:
        """
        创建检查点
        
        Args:
            model: 模型对象
            model_id: 模型ID
            epoch: 训练轮次
            
        Returns:
            检查点路径
        """
        try:
            checkpoint_dir = self.checkpoints_dir / model_id
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            checkpoint_path = checkpoint_dir / f"checkpoint_epoch_{epoch}.h5"
            
            if isinstance(model, tf.keras.Model):
                model.save(str(checkpoint_path))
            else:
                joblib.dump(model, str(checkpoint_path))
            
            return str(checkpoint_path)
            
        except Exception as e:
            logger.error(f"创建检查点失败: {e}")
            raise

class ModelPerformanceMonitor:
    """模型性能监控器"""
    
    def __init__(self):
        self.performance_history = {}
        self.alert_thresholds = {
            'accuracy_drop': 0.05,  # 准确率下降5%触发告警
            'latency_increase': 0.2,  # 延迟增加20%触发告警
            'error_rate_increase': 0.1  # 错误率增加10%触发告警
        }
    
    def record_performance(self, model_id: str, metrics: Dict[str, float]):
        """
        记录性能指标
        
        Args:
            model_id: 模型ID
            metrics: 性能指标
        """
        if model_id not in self.performance_history:
            self.performance_history[model_id] = []
        
        record = {
            'timestamp': datetime.now(),
            'metrics': metrics.copy()
        }
        
        self.performance_history[model_id].append(record)
        
        # 保持最近1000条记录
        if len(self.performance_history[model_id]) > 1000:
            self.performance_history[model_id] = self.performance_history[model_id][-1000:]
        
        # 检查是否需要告警
        self._check_performance_alerts(model_id, metrics)
    
    def _check_performance_alerts(self, model_id: str, current_metrics: Dict[str, float]):
        """
        检查性能告警
        
        Args:
            model_id: 模型ID
            current_metrics: 当前指标
        """
        try:
            history = self.performance_history.get(model_id, [])
            
            if len(history) < 10:  # 需要足够的历史数据
                return
            
            # 计算基线（最近10次的平均值）
            recent_records = history[-10:]
            baseline_metrics = {}
            
            for metric_name in current_metrics.keys():
                values = [r['metrics'].get(metric_name, 0) for r in recent_records]
                if values:
                    baseline_metrics[metric_name] = np.mean(values)
            
            # 检查各项指标
            alerts = []
            
            for metric_name, current_value in current_metrics.items():
                if metric_name not in baseline_metrics:
                    continue
                
                baseline_value = baseline_metrics[metric_name]
                
                if baseline_value == 0:
                    continue
                
                change_ratio = (current_value - baseline_value) / baseline_value
                
                # 准确率下降告警
                if metric_name == 'accuracy' and change_ratio < -self.alert_thresholds['accuracy_drop']:
                    alerts.append(f"模型{model_id}准确率下降{abs(change_ratio)*100:.1f}%")
                
                # 延迟增加告警
                elif metric_name == 'latency' and change_ratio > self.alert_thresholds['latency_increase']:
                    alerts.append(f"模型{model_id}延迟增加{change_ratio*100:.1f}%")
                
                # 错误率增加告警
                elif metric_name == 'error_rate' and change_ratio > self.alert_thresholds['error_rate_increase']:
                    alerts.append(f"模型{model_id}错误率增加{change_ratio*100:.1f}%")
            
            # 发送告警
            for alert in alerts:
                logger.warning(f"性能告警: {alert}")
                # 这里可以集成告警系统
                
        except Exception as e:
            logger.error(f"性能告警检查失败: {e}")
    
    def get_performance_summary(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Args:
            model_id: 模型ID
            days: 天数
            
        Returns:
            性能摘要
        """
        try:
            history = self.performance_history.get(model_id, [])
            
            if not history:
                return {}
            
            # 过滤指定天数内的记录
            cutoff_time = datetime.now() - timedelta(days=days)
            recent_history = [r for r in history if r['timestamp'] >= cutoff_time]
            
            if not recent_history:
                return {}
            
            # 计算统计信息
            summary = {
                'model_id': model_id,
                'period_days': days,
                'total_records': len(recent_history),
                'metrics': {}
            }
            
            # 收集所有指标名称
            all_metrics = set()
            for record in recent_history:
                all_metrics.update(record['metrics'].keys())
            
            # 计算每个指标的统计信息
            for metric_name in all_metrics:
                values = [r['metrics'].get(metric_name, 0) for r in recent_history]
                values = [v for v in values if v is not None]
                
                if values:
                    summary['metrics'][metric_name] = {
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)),
                        'min': float(np.min(values)),
                        'max': float(np.max(values)),
                        'latest': float(values[-1])
                    }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取性能摘要失败: {e}")
            return {}

class ModelVersionControl:
    """模型版本控制"""
    
    def __init__(self, storage: ModelStorage):
        self.storage = storage
        self.version_graph = {}  # 版本依赖图
    
    def create_version(self, model_id: str, base_version: str = None) -> str:
        """
        创建新版本
        
        Args:
            model_id: 模型ID
            base_version: 基础版本
            
        Returns:
            新版本号
        """
        try:
            # 获取当前最新版本
            latest_version = self.storage.get_latest_version(model_id)
            
            if latest_version is None:
                new_version = "1.0.0"
            else:
                # 解析版本号并递增
                parts = latest_version.split('.')
                if len(parts) == 3:
                    major, minor, patch = map(int, parts)
                    new_version = f"{major}.{minor}.{patch + 1}"
                else:
                    new_version = f"{latest_version}.1"
            
            # 记录版本关系
            if model_id not in self.version_graph:
                self.version_graph[model_id] = {}
            
            self.version_graph[model_id][new_version] = {
                'parent': base_version or latest_version,
                'created_at': datetime.now(),
                'status': 'created'
            }
            
            return new_version
            
        except Exception as e:
            logger.error(f"创建版本失败: {e}")
            raise
    
    def tag_version(self, model_id: str, version: str, tag: str):
        """
        为版本添加标签
        
        Args:
            model_id: 模型ID
            version: 版本号
            tag: 标签
        """
        try:
            if model_id in self.version_graph and version in self.version_graph[model_id]:
                if 'tags' not in self.version_graph[model_id][version]:
                    self.version_graph[model_id][version]['tags'] = []
                
                if tag not in self.version_graph[model_id][version]['tags']:
                    self.version_graph[model_id][version]['tags'].append(tag)
                    logger.info(f"为模型{model_id}版本{version}添加标签: {tag}")
                
        except Exception as e:
            logger.error(f"添加标签失败: {e}")
    
    def get_version_history(self, model_id: str) -> List[Dict[str, Any]]:
        """
        获取版本历史
        
        Args:
            model_id: 模型ID
            
        Returns:
            版本历史列表
        """
        try:
            if model_id not in self.version_graph:
                return []
            
            versions = []
            for version, info in self.version_graph[model_id].items():
                version_info = {
                    'version': version,
                    'parent': info.get('parent'),
                    'created_at': info.get('created_at', datetime.now()).isoformat(),
                    'status': info.get('status', 'unknown'),
                    'tags': info.get('tags', [])
                }
                versions.append(version_info)
            
            # 按创建时间排序
            versions.sort(key=lambda x: x['created_at'], reverse=True)
            return versions
            
        except Exception as e:
            logger.error(f"获取版本历史失败: {e}")
            return []

class ModelManager:
    """模型管理器主类"""
    
    def __init__(self, config: Config):
        """
        初始化模型管理器
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.cache_manager = CacheManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 初始化组件
        storage_path = config.get('model_storage_path', './models')
        self.storage = ModelStorage(storage_path)
        self.performance_monitor = ModelPerformanceMonitor()
        self.version_control = ModelVersionControl(self.storage)
        
        # 模型缓存
        self.model_cache = {}
        self.cache_size_limit = config.get('model_cache_size', 5)
        
        # 部署状态
        self.deployed_models = {}
        
        # 统计信息
        self.stats = {
            'models_loaded': 0,
            'models_saved': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'deployment_count': 0
        }
        
        self.is_initialized = False
    
    async def initialize(self):
        """初始化模型管理器"""
        try:
            logger.info("正在初始化模型管理器...")
            
            # 初始化缓存管理器
            await self.cache_manager.initialize()
            
            # 加载已部署的模型信息
            await self._load_deployment_info()
            
            self.is_initialized = True
            logger.info("模型管理器初始化完成")
            
        except Exception as e:
            logger.error(f"模型管理器初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        logger.info("正在清理模型管理器资源...")
        
        # 清理模型缓存
        self.model_cache.clear()
        
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        
        if hasattr(self, 'cache_manager'):
            await self.cache_manager.cleanup()
        
        logger.info("模型管理器资源清理完成")
    
    def is_ready(self) -> bool:
        """检查是否就绪"""
        return self.is_initialized
    
    async def save_model(self, model: Any, model_id: str, model_type: str, 
                        version: str = None, **metadata) -> str:
        """
        保存模型
        
        Args:
            model: 模型对象
            model_id: 模型ID
            model_type: 模型类型
            version: 版本号
            **metadata: 额外元数据
            
        Returns:
            模型版本号
        """
        try:
            # 创建版本号
            if version is None:
                version = self.version_control.create_version(model_id)
            
            # 创建元数据
            model_metadata = ModelMetadata(
                model_id=model_id,
                model_type=model_type,
                version=version,
                **metadata
            )
            
            # 保存模型
            model_path = self.storage.save_model(model, model_metadata)
            
            # 更新统计
            self.stats['models_saved'] += 1
            
            logger.info(f"模型已保存: {model_id} v{version}")
            return version
            
        except Exception as e:
            logger.error(f"保存模型失败: {e}")
            raise
    
    async def load_model(self, model_id: str, version: str = None, 
                        use_cache: bool = True) -> Tuple[Any, ModelMetadata]:
        """
        加载模型
        
        Args:
            model_id: 模型ID
            version: 版本号
            use_cache: 是否使用缓存
            
        Returns:
            模型对象和元数据
        """
        try:
            cache_key = f"{model_id}_{version or 'latest'}"
            
            # 检查缓存
            if use_cache and cache_key in self.model_cache:
                self.stats['cache_hits'] += 1
                logger.debug(f"从缓存加载模型: {cache_key}")
                return self.model_cache[cache_key]
            
            # 从存储加载
            model, metadata = self.storage.load_model(model_id, version)
            
            # 更新缓存
            if use_cache:
                self._update_cache(cache_key, (model, metadata))
            
            # 更新统计
            self.stats['models_loaded'] += 1
            self.stats['cache_misses'] += 1
            
            logger.info(f"模型已加载: {model_id} v{metadata.version}")
            return model, metadata
            
        except Exception as e:
            logger.error(f"加载模型失败: {e}")
            raise
    
    def _update_cache(self, cache_key: str, model_data: Tuple[Any, ModelMetadata]):
        """
        更新模型缓存
        
        Args:
            cache_key: 缓存键
            model_data: 模型数据
        """
        try:
            # 如果缓存已满，移除最旧的项
            if len(self.model_cache) >= self.cache_size_limit:
                oldest_key = next(iter(self.model_cache))
                del self.model_cache[oldest_key]
            
            self.model_cache[cache_key] = model_data
            
        except Exception as e:
            logger.error(f"更新缓存失败: {e}")
    
    async def delete_model(self, model_id: str, version: str = None) -> bool:
        """
        删除模型
        
        Args:
            model_id: 模型ID
            version: 版本号
            
        Returns:
            是否成功删除
        """
        try:
            # 从存储删除
            success = self.storage.delete_model(model_id, version)
            
            if success:
                # 清理缓存
                cache_keys_to_remove = []
                for cache_key in self.model_cache.keys():
                    if cache_key.startswith(f"{model_id}_"):
                        if version is None or cache_key == f"{model_id}_{version}":
                            cache_keys_to_remove.append(cache_key)
                
                for cache_key in cache_keys_to_remove:
                    del self.model_cache[cache_key]
                
                # 清理部署信息
                if model_id in self.deployed_models:
                    if version is None:
                        del self.deployed_models[model_id]
                    elif version in self.deployed_models[model_id]:
                        del self.deployed_models[model_id][version]
            
            return success
            
        except Exception as e:
            logger.error(f"删除模型失败: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """
        列出所有模型
        
        Returns:
            模型列表
        """
        try:
            models = self.storage.list_models()
            
            # 添加部署状态信息
            for model in models:
                model_id = model['model_id']
                version = model['version']
                
                if (model_id in self.deployed_models and 
                    version in self.deployed_models[model_id]):
                    model['deployment_status'] = self.deployed_models[model_id][version]['status']
                else:
                    model['deployment_status'] = 'not_deployed'
            
            return models
            
        except Exception as e:
            logger.error(f"列出模型失败: {e}")
            return []
    
    async def deploy_model(self, model_id: str, version: str = None, 
                          replicas: int = 1, **deployment_config) -> Dict[str, Any]:
        """
        部署模型
        
        Args:
            model_id: 模型ID
            version: 版本号
            replicas: 副本数
            **deployment_config: 部署配置
            
        Returns:
            部署结果
        """
        try:
            # 加载模型以验证其存在
            model, metadata = await self.load_model(model_id, version)
            
            # 更新部署信息
            if model_id not in self.deployed_models:
                self.deployed_models[model_id] = {}
            
            self.deployed_models[model_id][metadata.version] = {
                'status': 'deployed',
                'deployed_at': datetime.now(),
                'replicas': replicas,
                'config': deployment_config
            }
            
            # 更新元数据
            metadata.deployment_info.update({
                'status': 'deployed',
                'deployed_at': datetime.now(),
                'replicas': replicas
            })
            
            # 保存更新的元数据
            metadata_path = self.storage.metadata_dir / f"{model_id}_{metadata.version}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
            
            # 更新统计
            self.stats['deployment_count'] += 1
            
            result = {
                'model_id': model_id,
                'version': metadata.version,
                'status': 'deployed',
                'replicas': replicas,
                'deployed_at': datetime.now().isoformat()
            }
            
            logger.info(f"模型已部署: {model_id} v{metadata.version}")
            return result
            
        except Exception as e:
            logger.error(f"部署模型失败: {e}")
            raise
    
    async def undeploy_model(self, model_id: str, version: str = None) -> bool:
        """
        取消部署模型
        
        Args:
            model_id: 模型ID
            version: 版本号
            
        Returns:
            是否成功
        """
        try:
            if model_id not in self.deployed_models:
                return True
            
            if version is None:
                # 取消部署所有版本
                del self.deployed_models[model_id]
            else:
                # 取消部署特定版本
                if version in self.deployed_models[model_id]:
                    del self.deployed_models[model_id][version]
                
                # 如果没有其他版本，删除模型记录
                if not self.deployed_models[model_id]:
                    del self.deployed_models[model_id]
            
            logger.info(f"模型已取消部署: {model_id} v{version or 'all'}")
            return True
            
        except Exception as e:
            logger.error(f"取消部署模型失败: {e}")
            return False
    
    async def evaluate_model(self, model_id: str, version: str, 
                           test_data: Any, test_labels: Any) -> Dict[str, float]:
        """
        评估模型性能
        
        Args:
            model_id: 模型ID
            version: 版本号
            test_data: 测试数据
            test_labels: 测试标签
            
        Returns:
            评估指标
        """
        try:
            # 加载模型
            model, metadata = await self.load_model(model_id, version)
            
            # 预测
            if hasattr(model, 'predict'):
                predictions = model.predict(test_data)
            else:
                raise ValueError("模型不支持预测")
            
            # 计算指标
            metrics = {}
            
            if hasattr(model, 'predict_proba'):
                # 分类模型
                if len(predictions.shape) > 1 and predictions.shape[1] > 1:
                    predicted_classes = np.argmax(predictions, axis=1)
                else:
                    predicted_classes = (predictions > 0.5).astype(int)
                
                metrics['accuracy'] = float(accuracy_score(test_labels, predicted_classes))
                metrics['precision'] = float(precision_score(test_labels, predicted_classes, average='weighted'))
                metrics['recall'] = float(recall_score(test_labels, predicted_classes, average='weighted'))
                metrics['f1'] = float(f1_score(test_labels, predicted_classes, average='weighted'))
            else:
                # 回归模型
                from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
                metrics['mse'] = float(mean_squared_error(test_labels, predictions))
                metrics['mae'] = float(mean_absolute_error(test_labels, predictions))
                metrics['r2'] = float(r2_score(test_labels, predictions))
            
            # 记录性能
            self.performance_monitor.record_performance(model_id, metrics)
            
            # 更新元数据
            metadata.performance_metrics.update(metrics)
            metadata.updated_at = datetime.now()
            
            # 保存更新的元数据
            metadata_path = self.storage.metadata_dir / f"{model_id}_{version}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"模型评估完成: {model_id} v{version}")
            return metrics
            
        except Exception as e:
            logger.error(f"模型评估失败: {e}")
            raise
    
    async def get_model_performance(self, model_id: str, days: int = 7) -> Dict[str, Any]:
        """
        获取模型性能报告
        
        Args:
            model_id: 模型ID
            days: 天数
            
        Returns:
            性能报告
        """
        return self.performance_monitor.get_performance_summary(model_id, days)
    
    async def compare_models(self, model_configs: List[Dict[str, str]], 
                           test_data: Any, test_labels: Any) -> Dict[str, Any]:
        """
        比较多个模型
        
        Args:
            model_configs: 模型配置列表，每个包含model_id和version
            test_data: 测试数据
            test_labels: 测试标签
            
        Returns:
            比较结果
        """
        try:
            comparison_results = {
                'models': [],
                'best_model': None,
                'comparison_metrics': []
            }
            
            model_results = []
            
            for config in model_configs:
                model_id = config['model_id']
                version = config.get('version')
                
                try:
                    # 评估模型
                    metrics = await self.evaluate_model(model_id, version, test_data, test_labels)
                    
                    result = {
                        'model_id': model_id,
                        'version': version,
                        'metrics': metrics
                    }
                    
                    model_results.append(result)
                    comparison_results['models'].append(result)
                    
                except Exception as e:
                    logger.error(f"评估模型{model_id}失败: {e}")
                    continue
            
            if model_results:
                # 确定最佳模型（基于准确率或R2分数）
                best_model = None
                best_score = -float('inf')
                
                for result in model_results:
                    metrics = result['metrics']
                    score = metrics.get('accuracy', metrics.get('r2', 0))
                    
                    if score > best_score:
                        best_score = score
                        best_model = result
                
                comparison_results['best_model'] = best_model
                
                # 生成比较指标
                if len(model_results) > 1:
                    all_metrics = set()
                    for result in model_results:
                        all_metrics.update(result['metrics'].keys())
                    
                    for metric_name in all_metrics:
                        metric_comparison = {
                            'metric': metric_name,
                            'values': []
                        }
                        
                        for result in model_results:
                            if metric_name in result['metrics']:
                                metric_comparison['values'].append({
                                    'model': f"{result['model_id']}_{result['version']}",
                                    'value': result['metrics'][metric_name]
                                })
                        
                        comparison_results['comparison_metrics'].append(metric_comparison)
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"模型比较失败: {e}")
            raise
    
    async def _load_deployment_info(self):
        """
        加载部署信息
        """
        try:
            # 从元数据文件加载部署信息
            models = self.storage.list_models()
            
            for model_dict in models:
                deployment_info = model_dict.get('deployment_info', {})
                
                if deployment_info.get('status') == 'deployed':
                    model_id = model_dict['model_id']
                    version = model_dict['version']
                    
                    if model_id not in self.deployed_models:
                        self.deployed_models[model_id] = {}
                    
                    self.deployed_models[model_id][version] = {
                        'status': 'deployed',
                        'deployed_at': datetime.fromisoformat(deployment_info.get('deployed_at', datetime.now().isoformat())),
                        'replicas': deployment_info.get('replicas', 1)
                    }
            
            logger.info(f"加载了{len(self.deployed_models)}个已部署模型的信息")
            
        except Exception as e:
            logger.warning(f"加载部署信息失败: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        stats = self.stats.copy()
        
        # 添加缓存信息
        stats['cache_size'] = len(self.model_cache)
        stats['cache_limit'] = self.cache_size_limit
        
        if stats['models_loaded'] > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses'])
        
        # 添加部署信息
        stats['deployed_models_count'] = len(self.deployed_models)
        
        total_deployed_versions = 0
        for model_versions in self.deployed_models.values():
            total_deployed_versions += len(model_versions)
        stats['deployed_versions_count'] = total_deployed_versions
        
        return stats