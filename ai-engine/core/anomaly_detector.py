#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测模块

本模块实现了多种异常检测算法，包括：
- 孤立森林（Isolation Forest）
- 局部异常因子（Local Outlier Factor）
- 单类支持向量机（One-Class SVM）
- 统计方法（Z-Score, IQR）
- 时间序列异常检测（LSTM Autoencoder）

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

# 机器学习库
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import classification_report, confusion_matrix

# 深度学习库
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# 时间序列分析
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from scipy import stats

from utils.logger import setup_logger
from utils.data_processor import DataProcessor
from utils.cache import CacheManager

logger = setup_logger(__name__)

class AnomalyDetector:
    """异常检测器类"""
    
    def __init__(self, config, model_manager):
        """
        初始化异常检测器
        
        Args:
            config: 配置对象
            model_manager: 模型管理器
        """
        self.config = config
        self.model_manager = model_manager
        self.data_processor = DataProcessor()
        self.cache_manager = CacheManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 算法配置
        self.algorithms = {
            'isolation_forest': self._isolation_forest_detect,
            'lof': self._lof_detect,
            'one_class_svm': self._one_class_svm_detect,
            'statistical': self._statistical_detect,
            'lstm_autoencoder': self._lstm_autoencoder_detect,
            'ensemble': self._ensemble_detect
        }
        
        # 模型缓存
        self.models = {}
        self.scalers = {}
        
        # 性能指标
        self.detection_stats = {
            'total_detections': 0,
            'anomalies_found': 0,
            'false_positives': 0,
            'processing_time': []
        }
        
        self.is_initialized = False
        
    async def initialize(self):
        """初始化异常检测器"""
        try:
            logger.info("正在初始化异常检测器...")
            
            # 初始化数据处理器
            await self.data_processor.initialize()
            
            # 初始化缓存管理器
            await self.cache_manager.initialize()
            
            # 预加载模型
            await self._load_pretrained_models()
            
            self.is_initialized = True
            logger.info("异常检测器初始化完成")
            
        except Exception as e:
            logger.error(f"异常检测器初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        logger.info("正在清理异常检测器资源...")
        
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        
        if hasattr(self, 'cache_manager'):
            await self.cache_manager.cleanup()
        
        logger.info("异常检测器资源清理完成")
    
    def is_ready(self) -> bool:
        """检查是否就绪"""
        return self.is_initialized
    
    async def detect(self, metrics: List[Dict], algorithm: str = 'isolation_forest', 
                    threshold: float = 0.1, window_size: int = 100) -> Dict[str, Any]:
        """
        执行异常检测
        
        Args:
            metrics: 指标数据列表
            algorithm: 检测算法
            threshold: 异常阈值
            window_size: 时间窗口大小
            
        Returns:
            检测结果字典
        """
        start_time = datetime.now()
        
        try:
            # 数据预处理
            processed_data = await self._preprocess_data(metrics, window_size)
            
            if processed_data.empty:
                return {
                    'anomalies': [],
                    'confidence': 0.0,
                    'processing_time': 0.0,
                    'message': '没有足够的数据进行检测'
                }
            
            # 选择检测算法
            if algorithm not in self.algorithms:
                raise ValueError(f"不支持的算法: {algorithm}")
            
            # 执行检测
            detection_func = self.algorithms[algorithm]
            result = await detection_func(processed_data, threshold)
            
            # 后处理
            anomalies = await self._postprocess_anomalies(result, metrics)
            
            # 计算置信度
            confidence = self._calculate_confidence(result, processed_data)
            
            # 更新统计信息
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(len(anomalies), processing_time)
            
            return {
                'anomalies': anomalies,
                'confidence': confidence,
                'algorithm': algorithm,
                'processing_time': processing_time,
                'data_points': len(processed_data),
                'threshold': threshold
            }
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            raise
    
    async def _preprocess_data(self, metrics: List[Dict], window_size: int) -> pd.DataFrame:
        """
        数据预处理
        
        Args:
            metrics: 原始指标数据
            window_size: 时间窗口大小
            
        Returns:
            处理后的DataFrame
        """
        try:
            # 转换为DataFrame
            df = pd.DataFrame(metrics)
            
            if df.empty:
                return df
            
            # 时间戳处理
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df = df.sort_values('timestamp')
            
            # 数值列处理
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            # 缺失值处理
            df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(0)
            
            # 异常值预处理（极端值处理）
            for col in numeric_columns:
                if col != 'timestamp':
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 3 * IQR
                    upper_bound = Q3 + 3 * IQR
                    df[col] = df[col].clip(lower_bound, upper_bound)
            
            # 滑动窗口处理
            if len(df) > window_size:
                df = df.tail(window_size)
            
            # 特征工程
            df = await self._feature_engineering(df)
            
            return df
            
        except Exception as e:
            logger.error(f"数据预处理失败: {e}")
            raise
    
    async def _feature_engineering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        特征工程
        
        Args:
            df: 输入DataFrame
            
        Returns:
            增强特征后的DataFrame
        """
        try:
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_columns:
                if col != 'timestamp' and len(df) > 1:
                    # 移动平均
                    df[f'{col}_ma_5'] = df[col].rolling(window=5, min_periods=1).mean()
                    df[f'{col}_ma_10'] = df[col].rolling(window=10, min_periods=1).mean()
                    
                    # 移动标准差
                    df[f'{col}_std_5'] = df[col].rolling(window=5, min_periods=1).std().fillna(0)
                    
                    # 变化率
                    df[f'{col}_pct_change'] = df[col].pct_change().fillna(0)
                    
                    # Z-Score
                    if df[col].std() > 0:
                        df[f'{col}_zscore'] = (df[col] - df[col].mean()) / df[col].std()
                    else:
                        df[f'{col}_zscore'] = 0
            
            return df
            
        except Exception as e:
            logger.error(f"特征工程失败: {e}")
            return df
    
    async def _isolation_forest_detect(self, data: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """
        孤立森林异常检测
        
        Args:
            data: 输入数据
            threshold: 异常阈值
            
        Returns:
            检测结果
        """
        try:
            # 选择数值特征
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return {'anomalies': [], 'scores': []}
            
            # 数据标准化
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 训练模型
            model = IsolationForest(
                contamination=threshold,
                random_state=42,
                n_estimators=100
            )
            
            # 预测
            predictions = model.fit_predict(scaled_data)
            scores = model.decision_function(scaled_data)
            
            # 异常点索引（-1表示异常）
            anomaly_indices = np.where(predictions == -1)[0]
            
            return {
                'anomaly_indices': anomaly_indices.tolist(),
                'scores': scores.tolist(),
                'predictions': predictions.tolist()
            }
            
        except Exception as e:
            logger.error(f"孤立森林检测失败: {e}")
            raise
    
    async def _lof_detect(self, data: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """
        局部异常因子检测
        
        Args:
            data: 输入数据
            threshold: 异常阈值
            
        Returns:
            检测结果
        """
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty or len(numeric_data) < 10:
                return {'anomalies': [], 'scores': []}
            
            # 数据标准化
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 训练模型
            n_neighbors = min(20, len(numeric_data) - 1)
            model = LocalOutlierFactor(
                n_neighbors=n_neighbors,
                contamination=threshold
            )
            
            # 预测
            predictions = model.fit_predict(scaled_data)
            scores = model.negative_outlier_factor_
            
            # 异常点索引
            anomaly_indices = np.where(predictions == -1)[0]
            
            return {
                'anomaly_indices': anomaly_indices.tolist(),
                'scores': scores.tolist(),
                'predictions': predictions.tolist()
            }
            
        except Exception as e:
            logger.error(f"LOF检测失败: {e}")
            raise
    
    async def _one_class_svm_detect(self, data: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """
        单类支持向量机检测
        
        Args:
            data: 输入数据
            threshold: 异常阈值
            
        Returns:
            检测结果
        """
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return {'anomalies': [], 'scores': []}
            
            # 数据标准化
            scaler = StandardScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 训练模型
            model = OneClassSVM(
                nu=threshold,
                kernel='rbf',
                gamma='scale'
            )
            
            # 预测
            predictions = model.fit_predict(scaled_data)
            scores = model.decision_function(scaled_data)
            
            # 异常点索引
            anomaly_indices = np.where(predictions == -1)[0]
            
            return {
                'anomaly_indices': anomaly_indices.tolist(),
                'scores': scores.tolist(),
                'predictions': predictions.tolist()
            }
            
        except Exception as e:
            logger.error(f"One-Class SVM检测失败: {e}")
            raise
    
    async def _statistical_detect(self, data: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """
        统计方法异常检测
        
        Args:
            data: 输入数据
            threshold: 异常阈值
            
        Returns:
            检测结果
        """
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return {'anomalies': [], 'scores': []}
            
            anomaly_indices = []
            scores = []
            
            for idx, row in numeric_data.iterrows():
                row_scores = []
                
                for col in numeric_data.columns:
                    col_data = numeric_data[col]
                    
                    # Z-Score方法
                    if col_data.std() > 0:
                        z_score = abs((row[col] - col_data.mean()) / col_data.std())
                        row_scores.append(z_score)
                    
                    # IQR方法
                    Q1 = col_data.quantile(0.25)
                    Q3 = col_data.quantile(0.75)
                    IQR = Q3 - Q1
                    
                    if IQR > 0:
                        iqr_score = max(
                            (Q1 - row[col]) / IQR if row[col] < Q1 else 0,
                            (row[col] - Q3) / IQR if row[col] > Q3 else 0
                        )
                        row_scores.append(iqr_score)
                
                # 综合评分
                if row_scores:
                    combined_score = np.mean(row_scores)
                    scores.append(combined_score)
                    
                    # 判断是否异常
                    if combined_score > (3.0 * (1 - threshold)):
                        anomaly_indices.append(idx)
                else:
                    scores.append(0.0)
            
            return {
                'anomaly_indices': anomaly_indices,
                'scores': scores,
                'predictions': [-1 if i in anomaly_indices else 1 for i in range(len(scores))]
            }
            
        except Exception as e:
            logger.error(f"统计方法检测失败: {e}")
            raise
    
    async def _lstm_autoencoder_detect(self, data: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """
        LSTM自编码器异常检测
        
        Args:
            data: 输入数据
            threshold: 异常阈值
            
        Returns:
            检测结果
        """
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty or len(numeric_data) < 50:
                # 数据不足，使用统计方法
                return await self._statistical_detect(data, threshold)
            
            # 数据预处理
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 创建时间序列数据
            sequence_length = min(10, len(scaled_data) // 5)
            X = []
            
            for i in range(len(scaled_data) - sequence_length + 1):
                X.append(scaled_data[i:i + sequence_length])
            
            X = np.array(X)
            
            if len(X) == 0:
                return await self._statistical_detect(data, threshold)
            
            # 构建LSTM自编码器
            input_dim = X.shape[2]
            
            # 编码器
            encoder_inputs = Input(shape=(sequence_length, input_dim))
            encoder = LSTM(32, activation='relu', return_sequences=False)(encoder_inputs)
            
            # 解码器
            decoder = RepeatVector(sequence_length)(encoder)
            decoder = LSTM(32, activation='relu', return_sequences=True)(decoder)
            decoder_outputs = TimeDistributed(Dense(input_dim))(decoder)
            
            # 模型
            autoencoder = Model(encoder_inputs, decoder_outputs)
            autoencoder.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # 训练
            autoencoder.fit(
                X, X,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                verbose=0,
                callbacks=[
                    EarlyStopping(patience=10, restore_best_weights=True)
                ]
            )
            
            # 预测和计算重构误差
            predictions = autoencoder.predict(X, verbose=0)
            mse = np.mean(np.power(X - predictions, 2), axis=(1, 2))
            
            # 确定阈值
            threshold_value = np.percentile(mse, (1 - threshold) * 100)
            
            # 异常检测
            anomaly_indices = np.where(mse > threshold_value)[0]
            
            # 调整索引（因为序列长度的影响）
            adjusted_indices = [i + sequence_length - 1 for i in anomaly_indices]
            
            return {
                'anomaly_indices': adjusted_indices,
                'scores': mse.tolist(),
                'predictions': [-1 if i in adjusted_indices else 1 for i in range(len(data))]
            }
            
        except Exception as e:
            logger.error(f"LSTM自编码器检测失败: {e}")
            # 回退到统计方法
            return await self._statistical_detect(data, threshold)
    
    async def _ensemble_detect(self, data: pd.DataFrame, threshold: float) -> Dict[str, Any]:
        """
        集成方法异常检测
        
        Args:
            data: 输入数据
            threshold: 异常阈值
            
        Returns:
            检测结果
        """
        try:
            # 运行多个算法
            algorithms = ['isolation_forest', 'lof', 'statistical']
            results = []
            
            for algo in algorithms:
                try:
                    result = await self.algorithms[algo](data, threshold)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"集成检测中{algo}算法失败: {e}")
                    continue
            
            if not results:
                return {'anomalies': [], 'scores': []}
            
            # 投票机制
            data_length = len(data)
            vote_counts = np.zeros(data_length)
            combined_scores = np.zeros(data_length)
            
            for result in results:
                anomaly_indices = result.get('anomaly_indices', [])
                scores = result.get('scores', [])
                
                # 投票
                for idx in anomaly_indices:
                    if idx < data_length:
                        vote_counts[idx] += 1
                
                # 分数归一化和累加
                if scores and len(scores) <= data_length:
                    normalized_scores = np.abs(scores) / (np.max(np.abs(scores)) + 1e-8)
                    combined_scores[:len(normalized_scores)] += normalized_scores
            
            # 确定异常点（至少2个算法认为是异常）
            min_votes = max(1, len(results) // 2)
            anomaly_indices = np.where(vote_counts >= min_votes)[0]
            
            return {
                'anomaly_indices': anomaly_indices.tolist(),
                'scores': combined_scores.tolist(),
                'predictions': [-1 if i in anomaly_indices else 1 for i in range(data_length)],
                'vote_counts': vote_counts.tolist()
            }
            
        except Exception as e:
            logger.error(f"集成检测失败: {e}")
            raise
    
    async def _postprocess_anomalies(self, result: Dict[str, Any], original_metrics: List[Dict]) -> List[Dict[str, Any]]:
        """
        后处理异常结果
        
        Args:
            result: 检测结果
            original_metrics: 原始指标数据
            
        Returns:
            处理后的异常列表
        """
        try:
            anomalies = []
            anomaly_indices = result.get('anomaly_indices', [])
            scores = result.get('scores', [])
            
            for idx in anomaly_indices:
                if idx < len(original_metrics):
                    anomaly = {
                        'index': idx,
                        'timestamp': original_metrics[idx].get('timestamp'),
                        'metric_name': original_metrics[idx].get('metric_name'),
                        'value': original_metrics[idx].get('value'),
                        'labels': original_metrics[idx].get('labels', {}),
                        'source': original_metrics[idx].get('source'),
                        'anomaly_score': scores[idx] if idx < len(scores) else 0.0,
                        'severity': self._calculate_severity(scores[idx] if idx < len(scores) else 0.0)
                    }
                    anomalies.append(anomaly)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"异常后处理失败: {e}")
            return []
    
    def _calculate_confidence(self, result: Dict[str, Any], data: pd.DataFrame) -> float:
        """
        计算检测置信度
        
        Args:
            result: 检测结果
            data: 输入数据
            
        Returns:
            置信度分数
        """
        try:
            scores = result.get('scores', [])
            anomaly_indices = result.get('anomaly_indices', [])
            
            if not scores or not anomaly_indices:
                return 0.0
            
            # 基于分数分布计算置信度
            anomaly_scores = [abs(scores[i]) for i in anomaly_indices if i < len(scores)]
            
            if not anomaly_scores:
                return 0.0
            
            # 归一化置信度
            max_score = max(abs(s) for s in scores)
            if max_score > 0:
                confidence = np.mean(anomaly_scores) / max_score
            else:
                confidence = 0.0
            
            # 考虑数据质量
            data_quality_factor = min(1.0, len(data) / 100.0)
            
            return min(1.0, confidence * data_quality_factor)
            
        except Exception as e:
            logger.error(f"置信度计算失败: {e}")
            return 0.0
    
    def _calculate_severity(self, score: float) -> str:
        """
        计算异常严重程度
        
        Args:
            score: 异常分数
            
        Returns:
            严重程度字符串
        """
        abs_score = abs(score)
        
        if abs_score > 2.0:
            return 'critical'
        elif abs_score > 1.0:
            return 'high'
        elif abs_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _update_stats(self, anomaly_count: int, processing_time: float):
        """
        更新统计信息
        
        Args:
            anomaly_count: 异常数量
            processing_time: 处理时间
        """
        self.detection_stats['total_detections'] += 1
        self.detection_stats['anomalies_found'] += anomaly_count
        self.detection_stats['processing_time'].append(processing_time)
        
        # 保持最近1000次记录
        if len(self.detection_stats['processing_time']) > 1000:
            self.detection_stats['processing_time'] = self.detection_stats['processing_time'][-1000:]
    
    async def _load_pretrained_models(self):
        """
        加载预训练模型
        """
        try:
            # 这里可以加载预训练的模型
            # 例如从模型管理器加载
            logger.info("加载预训练模型...")
            
            # 示例：加载预训练的LSTM模型
            # self.models['lstm'] = await self.model_manager.load_model('lstm_anomaly_detector')
            
            logger.info("预训练模型加载完成")
            
        except Exception as e:
            logger.warning(f"预训练模型加载失败: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取检测统计信息
        
        Returns:
            统计信息字典
        """
        stats = self.detection_stats.copy()
        
        if stats['processing_time']:
            stats['avg_processing_time'] = np.mean(stats['processing_time'])
            stats['max_processing_time'] = np.max(stats['processing_time'])
            stats['min_processing_time'] = np.min(stats['processing_time'])
        
        if stats['total_detections'] > 0:
            stats['anomaly_rate'] = stats['anomalies_found'] / stats['total_detections']
        
        return stats