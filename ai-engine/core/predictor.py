#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预测模块

本模块实现了多种时间序列预测算法，包括：
- LSTM神经网络
- ARIMA模型
- Prophet预测
- 线性回归
- 随机森林回归
- XGBoost回归

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
import warnings
warnings.filterwarnings('ignore')

# 机器学习库
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

# XGBoost
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available")

# 深度学习库
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, GRU, Conv1D, MaxPooling1D, Flatten
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

# 时间序列分析
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logging.warning("Statsmodels not available")

# Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logging.warning("Prophet not available")

from utils.logger import setup_logger
from utils.data_processor import TimeSeriesProcessor, ProcessingConfig
from utils.cache import CacheManager

logger = setup_logger(__name__)

class Predictor:
    """预测器类"""
    
    def __init__(self, config, model_manager):
        """
        初始化预测器
        
        Args:
            config: 配置对象
            model_manager: 模型管理器
        """
        self.config = config
        self.model_manager = model_manager
        # 创建默认配置
        config = ProcessingConfig()
        self.data_processor = TimeSeriesProcessor(config)
        self.cache_manager = CacheManager()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 预测算法配置
        self.algorithms = {
            'lstm': self._lstm_predict,
            'gru': self._gru_predict,
            'cnn_lstm': self._cnn_lstm_predict,
            'arima': self._arima_predict,
            'prophet': self._prophet_predict,
            'linear': self._linear_predict,
            'random_forest': self._random_forest_predict,
            'xgboost': self._xgboost_predict,
            'ensemble': self._ensemble_predict
        }
        
        # 模型缓存
        self.models = {}
        self.scalers = {}
        
        # 性能指标
        self.prediction_stats = {
            'total_predictions': 0,
            'successful_predictions': 0,
            'failed_predictions': 0,
            'processing_time': [],
            'accuracy_scores': []
        }
        
        self.is_initialized = False
        
    async def initialize(self):
        """初始化预测器"""
        try:
            logger.info("正在初始化预测器...")
            
            # 数据处理器已在构造函数中初始化，无需额外初始化步骤
            
            # 初始化缓存管理器
            await self.cache_manager.initialize()
            
            # 预加载模型
            await self._load_pretrained_models()
            
            self.is_initialized = True
            logger.info("预测器初始化完成")
            
        except Exception as e:
            logger.error(f"预测器初始化失败: {e}")
            raise
    
    async def cleanup(self):
        """清理资源"""
        logger.info("正在清理预测器资源...")
        
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)
        
        if hasattr(self, 'cache_manager'):
            await self.cache_manager.cleanup()
        
        logger.info("预测器资源清理完成")
    
    def is_ready(self) -> bool:
        """检查是否就绪"""
        return self.is_initialized
    
    async def predict(self, metrics: List[Dict], horizon: int = 60, 
                     model_type: str = 'lstm') -> Dict[str, Any]:
        """
        执行预测
        
        Args:
            metrics: 历史指标数据
            horizon: 预测时长（分钟）
            model_type: 预测模型类型
            
        Returns:
            预测结果字典
        """
        start_time = datetime.now()
        
        try:
            # 数据预处理
            processed_data = await self._preprocess_data(metrics)
            
            if processed_data.empty or len(processed_data) < 10:
                return {
                    'predictions': [],
                    'confidence': 0.0,
                    'processing_time': 0.0,
                    'message': '历史数据不足，无法进行预测'
                }
            
            # 选择预测算法
            if model_type not in self.algorithms:
                raise ValueError(f"不支持的模型类型: {model_type}")
            
            # 执行预测
            prediction_func = self.algorithms[model_type]
            result = await prediction_func(processed_data, horizon)
            
            # 后处理
            predictions = await self._postprocess_predictions(result, metrics, horizon)
            
            # 计算置信度
            confidence = self._calculate_confidence(result, processed_data)
            
            # 更新统计信息
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(True, processing_time, confidence)
            
            return {
                'predictions': predictions,
                'confidence': confidence,
                'model_type': model_type,
                'horizon': horizon,
                'processing_time': processing_time,
                'data_points': len(processed_data),
                'metrics': result.get('metrics', {})
            }
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(False, processing_time, 0.0)
            raise
    
    async def _preprocess_data(self, metrics: List[Dict]) -> pd.DataFrame:
        """
        数据预处理
        
        Args:
            metrics: 原始指标数据
            
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
                df = df.set_index('timestamp')
            
            # 数值列处理
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            # 缺失值处理
            df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(method='bfill').fillna(0)
            
            # 异常值处理
            for col in numeric_columns:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                df[col] = df[col].clip(lower_bound, upper_bound)
            
            # 重采样（确保时间间隔一致）
            if len(df) > 1:
                freq = self._infer_frequency(df.index)
                if freq:
                    df = df.resample(freq).mean().fillna(method='ffill')
            
            return df
            
        except Exception as e:
            logger.error(f"数据预处理失败: {e}")
            raise
    
    def _infer_frequency(self, time_index) -> Optional[str]:
        """
        推断时间序列频率
        
        Args:
            time_index: 时间索引
            
        Returns:
            频率字符串
        """
        try:
            if len(time_index) < 2:
                return None
            
            # 计算时间间隔
            intervals = time_index[1:] - time_index[:-1]
            median_interval = intervals.median()
            
            # 推断频率
            if median_interval <= timedelta(seconds=30):
                return '30S'
            elif median_interval <= timedelta(minutes=1):
                return '1T'
            elif median_interval <= timedelta(minutes=5):
                return '5T'
            elif median_interval <= timedelta(minutes=15):
                return '15T'
            elif median_interval <= timedelta(hours=1):
                return '1H'
            else:
                return '1D'
                
        except Exception:
            return '1T'  # 默认1分钟
    
    async def _lstm_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        LSTM预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            # 选择数值列
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                raise ValueError("没有数值数据可用于预测")
            
            # 数据标准化
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 创建序列数据
            sequence_length = min(20, len(scaled_data) // 3)
            X, y = [], []
            
            for i in range(len(scaled_data) - sequence_length):
                X.append(scaled_data[i:i + sequence_length])
                y.append(scaled_data[i + sequence_length])
            
            X, y = np.array(X), np.array(y)
            
            if len(X) == 0:
                raise ValueError("序列数据不足")
            
            # 分割训练和测试数据
            train_size = int(len(X) * 0.8)
            X_train, X_test = X[:train_size], X[train_size:]
            y_train, y_test = y[:train_size], y[train_size:]
            
            # 构建LSTM模型
            model = Sequential([
                LSTM(50, return_sequences=True, input_shape=(sequence_length, numeric_data.shape[1])),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25),
                Dense(numeric_data.shape[1])
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # 训练模型
            history = model.fit(
                X_train, y_train,
                epochs=50,
                batch_size=32,
                validation_data=(X_test, y_test) if len(X_test) > 0 else None,
                verbose=0,
                callbacks=[
                    EarlyStopping(patience=10, restore_best_weights=True),
                    ReduceLROnPlateau(patience=5, factor=0.5)
                ]
            )
            
            # 预测
            predictions = []
            current_sequence = scaled_data[-sequence_length:]
            
            for _ in range(horizon):
                # 预测下一个点
                next_pred = model.predict(current_sequence.reshape(1, sequence_length, -1), verbose=0)
                predictions.append(next_pred[0])
                
                # 更新序列
                current_sequence = np.vstack([current_sequence[1:], next_pred[0]])
            
            # 反标准化
            predictions = scaler.inverse_transform(np.array(predictions))
            
            # 计算评估指标
            metrics = {}
            if len(X_test) > 0:
                test_pred = model.predict(X_test, verbose=0)
                test_pred_rescaled = scaler.inverse_transform(test_pred)
                y_test_rescaled = scaler.inverse_transform(y_test)
                
                metrics = {
                    'mse': float(mean_squared_error(y_test_rescaled, test_pred_rescaled)),
                    'mae': float(mean_absolute_error(y_test_rescaled, test_pred_rescaled)),
                    'r2': float(r2_score(y_test_rescaled, test_pred_rescaled))
                }
            
            return {
                'predictions': predictions.tolist(),
                'feature_names': numeric_data.columns.tolist(),
                'metrics': metrics,
                'model_type': 'lstm'
            }
            
        except Exception as e:
            logger.error(f"LSTM预测失败: {e}")
            raise
    
    async def _gru_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        GRU预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            # 选择数值列
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                raise ValueError("没有数值数据可用于预测")
            
            # 数据标准化
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 创建序列数据
            sequence_length = min(15, len(scaled_data) // 3)
            X, y = [], []
            
            for i in range(len(scaled_data) - sequence_length):
                X.append(scaled_data[i:i + sequence_length])
                y.append(scaled_data[i + sequence_length])
            
            X, y = np.array(X), np.array(y)
            
            if len(X) == 0:
                raise ValueError("序列数据不足")
            
            # 构建GRU模型
            model = Sequential([
                GRU(64, return_sequences=True, input_shape=(sequence_length, numeric_data.shape[1])),
                Dropout(0.3),
                GRU(32, return_sequences=False),
                Dropout(0.3),
                Dense(16),
                Dense(numeric_data.shape[1])
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # 训练模型
            model.fit(
                X, y,
                epochs=30,
                batch_size=16,
                verbose=0,
                callbacks=[
                    EarlyStopping(patience=8, restore_best_weights=True)
                ]
            )
            
            # 预测
            predictions = []
            current_sequence = scaled_data[-sequence_length:]
            
            for _ in range(horizon):
                next_pred = model.predict(current_sequence.reshape(1, sequence_length, -1), verbose=0)
                predictions.append(next_pred[0])
                current_sequence = np.vstack([current_sequence[1:], next_pred[0]])
            
            # 反标准化
            predictions = scaler.inverse_transform(np.array(predictions))
            
            return {
                'predictions': predictions.tolist(),
                'feature_names': numeric_data.columns.tolist(),
                'model_type': 'gru'
            }
            
        except Exception as e:
            logger.error(f"GRU预测失败: {e}")
            raise
    
    async def _cnn_lstm_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        CNN-LSTM预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            # 选择数值列
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                raise ValueError("没有数值数据可用于预测")
            
            # 数据标准化
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(numeric_data)
            
            # 创建序列数据
            sequence_length = min(25, len(scaled_data) // 3)
            X, y = [], []
            
            for i in range(len(scaled_data) - sequence_length):
                X.append(scaled_data[i:i + sequence_length])
                y.append(scaled_data[i + sequence_length])
            
            X, y = np.array(X), np.array(y)
            
            if len(X) == 0:
                raise ValueError("序列数据不足")
            
            # 构建CNN-LSTM模型
            model = Sequential([
                Conv1D(filters=64, kernel_size=3, activation='relu', input_shape=(sequence_length, numeric_data.shape[1])),
                Conv1D(filters=64, kernel_size=3, activation='relu'),
                MaxPooling1D(pool_size=2),
                LSTM(50, return_sequences=True),
                Dropout(0.2),
                LSTM(50),
                Dropout(0.2),
                Dense(50),
                Dense(numeric_data.shape[1])
            ])
            
            model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
            
            # 训练模型
            model.fit(
                X, y,
                epochs=40,
                batch_size=32,
                verbose=0,
                callbacks=[
                    EarlyStopping(patience=10, restore_best_weights=True)
                ]
            )
            
            # 预测
            predictions = []
            current_sequence = scaled_data[-sequence_length:]
            
            for _ in range(horizon):
                next_pred = model.predict(current_sequence.reshape(1, sequence_length, -1), verbose=0)
                predictions.append(next_pred[0])
                current_sequence = np.vstack([current_sequence[1:], next_pred[0]])
            
            # 反标准化
            predictions = scaler.inverse_transform(np.array(predictions))
            
            return {
                'predictions': predictions.tolist(),
                'feature_names': numeric_data.columns.tolist(),
                'model_type': 'cnn_lstm'
            }
            
        except Exception as e:
            logger.error(f"CNN-LSTM预测失败: {e}")
            raise
    
    async def _arima_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        ARIMA预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            if not STATSMODELS_AVAILABLE:
                raise ImportError("Statsmodels not available")
            
            # 选择第一个数值列进行预测
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) == 0:
                raise ValueError("没有数值数据可用于预测")
            
            predictions_dict = {}
            
            for col in numeric_columns[:3]:  # 最多预测3个指标
                series = data[col].dropna()
                
                if len(series) < 20:
                    continue
                
                try:
                    # 自动选择ARIMA参数
                    model = ARIMA(series, order=(1, 1, 1))
                    fitted_model = model.fit()
                    
                    # 预测
                    forecast = fitted_model.forecast(steps=horizon)
                    predictions_dict[col] = forecast.tolist()
                    
                except Exception as e:
                    logger.warning(f"ARIMA预测列{col}失败: {e}")
                    continue
            
            if not predictions_dict:
                raise ValueError("所有列的ARIMA预测都失败")
            
            # 转换为统一格式
            predictions = []
            for i in range(horizon):
                pred_point = {}
                for col, pred_list in predictions_dict.items():
                    if i < len(pred_list):
                        pred_point[col] = pred_list[i]
                predictions.append(pred_point)
            
            return {
                'predictions': predictions,
                'feature_names': list(predictions_dict.keys()),
                'model_type': 'arima'
            }
            
        except Exception as e:
            logger.error(f"ARIMA预测失败: {e}")
            raise
    
    async def _prophet_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        Prophet预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            if not PROPHET_AVAILABLE:
                raise ImportError("Prophet not available")
            
            # 选择数值列
            numeric_columns = data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) == 0:
                raise ValueError("没有数值数据可用于预测")
            
            predictions_dict = {}
            
            for col in numeric_columns[:2]:  # 最多预测2个指标
                try:
                    # 准备Prophet数据格式
                    prophet_data = pd.DataFrame({
                        'ds': data.index,
                        'y': data[col]
                    }).dropna()
                    
                    if len(prophet_data) < 10:
                        continue
                    
                    # 创建和训练Prophet模型
                    model = Prophet(
                        daily_seasonality=False,
                        weekly_seasonality=False,
                        yearly_seasonality=False
                    )
                    model.fit(prophet_data)
                    
                    # 创建未来时间点
                    future = model.make_future_dataframe(periods=horizon, freq='T')
                    
                    # 预测
                    forecast = model.predict(future)
                    
                    # 提取预测值
                    predictions_dict[col] = forecast['yhat'].tail(horizon).tolist()
                    
                except Exception as e:
                    logger.warning(f"Prophet预测列{col}失败: {e}")
                    continue
            
            if not predictions_dict:
                raise ValueError("所有列的Prophet预测都失败")
            
            # 转换为统一格式
            predictions = []
            for i in range(horizon):
                pred_point = {}
                for col, pred_list in predictions_dict.items():
                    if i < len(pred_list):
                        pred_point[col] = pred_list[i]
                predictions.append(pred_point)
            
            return {
                'predictions': predictions,
                'feature_names': list(predictions_dict.keys()),
                'model_type': 'prophet'
            }
            
        except Exception as e:
            logger.error(f"Prophet预测失败: {e}")
            raise
    
    async def _linear_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        线性回归预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            # 选择数值列
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                raise ValueError("没有数值数据可用于预测")
            
            predictions_dict = {}
            
            for col in numeric_data.columns:
                series = numeric_data[col].dropna()
                
                if len(series) < 5:
                    continue
                
                # 创建时间特征
                X = np.arange(len(series)).reshape(-1, 1)
                y = series.values
                
                # 训练线性回归模型
                model = LinearRegression()
                model.fit(X, y)
                
                # 预测
                future_X = np.arange(len(series), len(series) + horizon).reshape(-1, 1)
                predictions = model.predict(future_X)
                
                predictions_dict[col] = predictions.tolist()
            
            if not predictions_dict:
                raise ValueError("线性回归预测失败")
            
            # 转换为统一格式
            predictions = []
            for i in range(horizon):
                pred_point = {}
                for col, pred_list in predictions_dict.items():
                    if i < len(pred_list):
                        pred_point[col] = pred_list[i]
                predictions.append(pred_point)
            
            return {
                'predictions': predictions,
                'feature_names': list(predictions_dict.keys()),
                'model_type': 'linear'
            }
            
        except Exception as e:
            logger.error(f"线性回归预测失败: {e}")
            raise
    
    async def _random_forest_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        随机森林预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            # 选择数值列
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                raise ValueError("没有数值数据可用于预测")
            
            predictions_dict = {}
            
            for col in numeric_data.columns:
                series = numeric_data[col].dropna()
                
                if len(series) < 10:
                    continue
                
                # 创建滞后特征
                lag_features = []
                target = []
                
                window_size = min(5, len(series) // 3)
                
                for i in range(window_size, len(series)):
                    lag_features.append(series[i-window_size:i].values)
                    target.append(series[i])
                
                if len(lag_features) == 0:
                    continue
                
                X = np.array(lag_features)
                y = np.array(target)
                
                # 训练随机森林模型
                model = RandomForestRegressor(n_estimators=50, random_state=42)
                model.fit(X, y)
                
                # 预测
                predictions = []
                current_window = series[-window_size:].values
                
                for _ in range(horizon):
                    next_pred = model.predict(current_window.reshape(1, -1))[0]
                    predictions.append(next_pred)
                    current_window = np.append(current_window[1:], next_pred)
                
                predictions_dict[col] = predictions
            
            if not predictions_dict:
                raise ValueError("随机森林预测失败")
            
            # 转换为统一格式
            predictions = []
            for i in range(horizon):
                pred_point = {}
                for col, pred_list in predictions_dict.items():
                    if i < len(pred_list):
                        pred_point[col] = pred_list[i]
                predictions.append(pred_point)
            
            return {
                'predictions': predictions,
                'feature_names': list(predictions_dict.keys()),
                'model_type': 'random_forest'
            }
            
        except Exception as e:
            logger.error(f"随机森林预测失败: {e}")
            raise
    
    async def _xgboost_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        XGBoost预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            if not XGBOOST_AVAILABLE:
                raise ImportError("XGBoost not available")
            
            # 选择数值列
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                raise ValueError("没有数值数据可用于预测")
            
            predictions_dict = {}
            
            for col in numeric_data.columns:
                series = numeric_data[col].dropna()
                
                if len(series) < 15:
                    continue
                
                # 创建滞后特征
                lag_features = []
                target = []
                
                window_size = min(7, len(series) // 3)
                
                for i in range(window_size, len(series)):
                    lag_features.append(series[i-window_size:i].values)
                    target.append(series[i])
                
                if len(lag_features) == 0:
                    continue
                
                X = np.array(lag_features)
                y = np.array(target)
                
                # 训练XGBoost模型
                model = xgb.XGBRegressor(
                    n_estimators=100,
                    max_depth=6,
                    learning_rate=0.1,
                    random_state=42
                )
                model.fit(X, y)
                
                # 预测
                predictions = []
                current_window = series[-window_size:].values
                
                for _ in range(horizon):
                    next_pred = model.predict(current_window.reshape(1, -1))[0]
                    predictions.append(float(next_pred))
                    current_window = np.append(current_window[1:], next_pred)
                
                predictions_dict[col] = predictions
            
            if not predictions_dict:
                raise ValueError("XGBoost预测失败")
            
            # 转换为统一格式
            predictions = []
            for i in range(horizon):
                pred_point = {}
                for col, pred_list in predictions_dict.items():
                    if i < len(pred_list):
                        pred_point[col] = pred_list[i]
                predictions.append(pred_point)
            
            return {
                'predictions': predictions,
                'feature_names': list(predictions_dict.keys()),
                'model_type': 'xgboost'
            }
            
        except Exception as e:
            logger.error(f"XGBoost预测失败: {e}")
            raise
    
    async def _ensemble_predict(self, data: pd.DataFrame, horizon: int) -> Dict[str, Any]:
        """
        集成预测
        
        Args:
            data: 输入数据
            horizon: 预测时长
            
        Returns:
            预测结果
        """
        try:
            # 运行多个算法
            algorithms = ['lstm', 'linear', 'random_forest']
            if XGBOOST_AVAILABLE:
                algorithms.append('xgboost')
            
            results = []
            weights = []
            
            for algo in algorithms:
                try:
                    result = await self.algorithms[algo](data, horizon)
                    results.append(result)
                    # 简单权重策略
                    if algo == 'lstm':
                        weights.append(0.4)
                    elif algo == 'xgboost':
                        weights.append(0.3)
                    else:
                        weights.append(0.15)
                except Exception as e:
                    logger.warning(f"集成预测中{algo}算法失败: {e}")
                    continue
            
            if not results:
                raise ValueError("所有算法都失败")
            
            # 权重归一化
            weights = weights[:len(results)]
            weights = np.array(weights) / np.sum(weights)
            
            # 加权平均
            ensemble_predictions = []
            feature_names = set()
            
            for result in results:
                feature_names.update(result.get('feature_names', []))
            
            feature_names = list(feature_names)
            
            for i in range(horizon):
                pred_point = {}
                
                for feature in feature_names:
                    weighted_values = []
                    valid_weights = []
                    
                    for j, result in enumerate(results):
                        predictions = result.get('predictions', [])
                        if i < len(predictions) and feature in predictions[i]:
                            weighted_values.append(predictions[i][feature])
                            valid_weights.append(weights[j])
                    
                    if weighted_values:
                        valid_weights = np.array(valid_weights) / np.sum(valid_weights)
                        pred_point[feature] = np.average(weighted_values, weights=valid_weights)
                
                ensemble_predictions.append(pred_point)
            
            return {
                'predictions': ensemble_predictions,
                'feature_names': feature_names,
                'model_type': 'ensemble',
                'component_models': [r.get('model_type') for r in results]
            }
            
        except Exception as e:
            logger.error(f"集成预测失败: {e}")
            raise
    
    async def _postprocess_predictions(self, result: Dict[str, Any], 
                                     original_metrics: List[Dict], 
                                     horizon: int) -> List[Dict[str, Any]]:
        """
        后处理预测结果
        
        Args:
            result: 预测结果
            original_metrics: 原始指标数据
            horizon: 预测时长
            
        Returns:
            处理后的预测列表
        """
        try:
            predictions = result.get('predictions', [])
            feature_names = result.get('feature_names', [])
            
            # 生成时间戳
            if original_metrics and 'timestamp' in original_metrics[-1]:
                last_timestamp = pd.to_datetime(original_metrics[-1]['timestamp'])
                timestamps = [last_timestamp + timedelta(minutes=i+1) for i in range(horizon)]
            else:
                base_time = datetime.now()
                timestamps = [base_time + timedelta(minutes=i+1) for i in range(horizon)]
            
            # 格式化预测结果
            formatted_predictions = []
            
            for i, pred in enumerate(predictions[:horizon]):
                if i < len(timestamps):
                    formatted_pred = {
                        'timestamp': timestamps[i].isoformat(),
                        'predictions': pred if isinstance(pred, dict) else {},
                        'horizon_step': i + 1
                    }
                    formatted_predictions.append(formatted_pred)
            
            return formatted_predictions
            
        except Exception as e:
            logger.error(f"预测后处理失败: {e}")
            return []
    
    def _calculate_confidence(self, result: Dict[str, Any], data: pd.DataFrame) -> float:
        """
        计算预测置信度
        
        Args:
            result: 预测结果
            data: 输入数据
            
        Returns:
            置信度分数
        """
        try:
            # 基于数据质量和模型性能计算置信度
            data_quality = min(1.0, len(data) / 100.0)
            
            # 基于模型指标
            metrics = result.get('metrics', {})
            model_performance = 0.5  # 默认值
            
            if 'r2' in metrics:
                model_performance = max(0.0, min(1.0, metrics['r2']))
            elif 'mse' in metrics and 'mae' in metrics:
                # 基于误差计算性能
                mse = metrics['mse']
                mae = metrics['mae']
                if mse > 0:
                    model_performance = 1.0 / (1.0 + np.sqrt(mse))
            
            # 综合置信度
            confidence = (data_quality * 0.3 + model_performance * 0.7)
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"置信度计算失败: {e}")
            return 0.5
    
    def _update_stats(self, success: bool, processing_time: float, accuracy: float):
        """
        更新统计信息
        
        Args:
            success: 是否成功
            processing_time: 处理时间
            accuracy: 准确度
        """
        self.prediction_stats['total_predictions'] += 1
        
        if success:
            self.prediction_stats['successful_predictions'] += 1
            self.prediction_stats['accuracy_scores'].append(accuracy)
        else:
            self.prediction_stats['failed_predictions'] += 1
        
        self.prediction_stats['processing_time'].append(processing_time)
        
        # 保持最近1000次记录
        for key in ['processing_time', 'accuracy_scores']:
            if len(self.prediction_stats[key]) > 1000:
                self.prediction_stats[key] = self.prediction_stats[key][-1000:]
    
    async def _load_pretrained_models(self):
        """
        加载预训练模型
        """
        try:
            logger.info("加载预训练预测模型...")
            
            # 这里可以加载预训练的模型
            # 例如从模型管理器加载
            
            logger.info("预训练预测模型加载完成")
            
        except Exception as e:
            logger.warning(f"预训练预测模型加载失败: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        获取预测统计信息
        
        Returns:
            统计信息字典
        """
        stats = self.prediction_stats.copy()
        
        if stats['processing_time']:
            stats['avg_processing_time'] = np.mean(stats['processing_time'])
            stats['max_processing_time'] = np.max(stats['processing_time'])
            stats['min_processing_time'] = np.min(stats['processing_time'])
        
        if stats['accuracy_scores']:
            stats['avg_accuracy'] = np.mean(stats['accuracy_scores'])
            stats['max_accuracy'] = np.max(stats['accuracy_scores'])
            stats['min_accuracy'] = np.min(stats['accuracy_scores'])
        
        if stats['total_predictions'] > 0:
            stats['success_rate'] = stats['successful_predictions'] / stats['total_predictions']
        
        return stats