#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理工具模块

本模块提供数据处理功能，包括：
- 时间序列数据处理
- 数据清洗和预处理
- 特征工程
- 数据标准化和归一化
- 异常值检测和处理
- 数据采样和重采样
- 数据聚合和统计
- 数据转换和编码

Author: AIOps Team
Version: 1.0.0
Date: 2024-01-15
"""

import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import warnings
from scipy import stats
from scipy.signal import savgol_filter
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler, QuantileTransformer,
    LabelEncoder, OneHotEncoder, OrdinalEncoder
)
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.decomposition import PCA, FastICA
from sklearn.cluster import DBSCAN
import joblib

# 可选依赖
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False

try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False

logger = logging.getLogger(__name__)

class DataProcessingError(Exception):
    """数据处理错误"""
    pass

@dataclass
class ProcessingConfig:
    """数据处理配置"""
    # 缺失值处理
    missing_strategy: str = 'mean'  # mean, median, mode, constant, knn
    missing_fill_value: Any = None
    
    # 异常值处理
    outlier_method: str = 'iqr'  # iqr, zscore, isolation_forest, dbscan
    outlier_threshold: float = 3.0
    outlier_action: str = 'remove'  # remove, clip, transform
    
    # 数据标准化
    scaling_method: str = 'standard'  # standard, minmax, robust, quantile
    
    # 特征工程
    feature_selection: bool = False
    feature_selection_k: int = 10
    feature_selection_method: str = 'f_regression'
    
    # 时间序列处理
    resample_freq: Optional[str] = None
    resample_method: str = 'mean'
    seasonal_decompose: bool = False
    
    # 数据转换
    log_transform: bool = False
    box_cox_transform: bool = False
    
    # 降维
    dimensionality_reduction: bool = False
    reduction_method: str = 'pca'
    n_components: Optional[int] = None

class DataProcessor(ABC):
    """数据处理器基类"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.fitted_transformers = {}
        self.processing_stats = {}
    
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> 'DataProcessor':
        """拟合处理器"""
        pass
    
    @abstractmethod
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """转换数据"""
        pass
    
    def fit_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """拟合并转换数据"""
        return self.fit(data).transform(data)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取处理统计信息"""
        return self.processing_stats.copy()

class TimeSeriesProcessor(DataProcessor):
    """时间序列数据处理器"""
    
    def __init__(self, config: ProcessingConfig):
        super().__init__(config)
        self.time_column = None
        self.original_freq = None
    
    def fit(self, data: pd.DataFrame) -> 'TimeSeriesProcessor':
        """拟合时间序列处理器"""
        try:
            # 检测时间列
            self.time_column = self._detect_time_column(data)
            
            if self.time_column:
                # 确保时间列是datetime类型
                if not pd.api.types.is_datetime64_any_dtype(data[self.time_column]):
                    data[self.time_column] = pd.to_datetime(data[self.time_column])
                
                # 检测原始频率
                self.original_freq = self._detect_frequency(data[self.time_column])
                
                logger.info(f"检测到时间列: {self.time_column}, 频率: {self.original_freq}")
            
            # 拟合其他转换器
            self._fit_transformers(data)
            
            return self
            
        except Exception as e:
            logger.error(f"时间序列处理器拟合失败: {e}")
            raise DataProcessingError(f"拟合失败: {e}")
    
    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """转换时间序列数据"""
        try:
            result = data.copy()
            
            # 时间列处理
            if self.time_column and self.time_column in result.columns:
                result = self._process_time_series(result)
            
            # 应用其他转换
            result = self._apply_transformations(result)
            
            # 更新统计信息
            self._update_stats(data, result)
            
            return result
            
        except Exception as e:
            logger.error(f"时间序列数据转换失败: {e}")
            raise DataProcessingError(f"转换失败: {e}")
    
    def _detect_time_column(self, data: pd.DataFrame) -> Optional[str]:
        """检测时间列"""
        # 检查列名
        time_keywords = ['time', 'timestamp', 'date', 'datetime', 'created_at', 'updated_at']
        
        for col in data.columns:
            if any(keyword in col.lower() for keyword in time_keywords):
                return col
        
        # 检查数据类型
        for col in data.columns:
            if pd.api.types.is_datetime64_any_dtype(data[col]):
                return col
            
            # 尝试转换为datetime
            try:
                pd.to_datetime(data[col].head(100))
                return col
            except:
                continue
        
        return None
    
    def _detect_frequency(self, time_series: pd.Series) -> Optional[str]:
        """检测时间序列频率"""
        try:
            if len(time_series) < 2:
                return None
            
            # 计算时间间隔
            time_diffs = time_series.sort_values().diff().dropna()
            
            if len(time_diffs) == 0:
                return None
            
            # 获取最常见的时间间隔
            most_common_diff = time_diffs.mode().iloc[0] if len(time_diffs.mode()) > 0 else time_diffs.median()
            
            # 转换为频率字符串
            if most_common_diff <= pd.Timedelta(seconds=1):
                return 'S'  # 秒
            elif most_common_diff <= pd.Timedelta(minutes=1):
                return 'T'  # 分钟
            elif most_common_diff <= pd.Timedelta(hours=1):
                return 'H'  # 小时
            elif most_common_diff <= pd.Timedelta(days=1):
                return 'D'  # 天
            elif most_common_diff <= pd.Timedelta(weeks=1):
                return 'W'  # 周
            else:
                return 'M'  # 月
                
        except Exception as e:
            logger.warning(f"频率检测失败: {e}")
            return None
    
    def _process_time_series(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理时间序列"""
        result = data.copy()
        
        # 设置时间索引
        if self.time_column in result.columns:
            result = result.set_index(self.time_column)
            result.index = pd.to_datetime(result.index)
            result = result.sort_index()
        
        # 重采样
        if self.config.resample_freq:
            numeric_columns = result.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) > 0:
                if self.config.resample_method == 'mean':
                    result = result.resample(self.config.resample_freq).mean()
                elif self.config.resample_method == 'sum':
                    result = result.resample(self.config.resample_freq).sum()
                elif self.config.resample_method == 'max':
                    result = result.resample(self.config.resample_freq).max()
                elif self.config.resample_method == 'min':
                    result = result.resample(self.config.resample_freq).min()
                else:
                    result = result.resample(self.config.resample_freq).mean()
        
        # 季节性分解
        if self.config.seasonal_decompose and STATSMODELS_AVAILABLE:
            result = self._apply_seasonal_decompose(result)
        
        return result
    
    def _apply_seasonal_decompose(self, data: pd.DataFrame) -> pd.DataFrame:
        """应用季节性分解"""
        result = data.copy()
        numeric_columns = result.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if len(result[col].dropna()) >= 24:  # 至少需要2个周期的数据
                try:
                    decomposition = seasonal_decompose(
                        result[col].dropna(),
                        model='additive',
                        period=min(12, len(result[col].dropna()) // 2)
                    )
                    
                    # 添加分解后的组件
                    result[f'{col}_trend'] = decomposition.trend
                    result[f'{col}_seasonal'] = decomposition.seasonal
                    result[f'{col}_residual'] = decomposition.resid
                    
                except Exception as e:
                    logger.warning(f"列 {col} 季节性分解失败: {e}")
        
        return result
    
    def _fit_transformers(self, data: pd.DataFrame):
        """拟合转换器"""
        numeric_data = data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) == 0:
            return
        
        # 缺失值处理器
        if self.config.missing_strategy == 'knn':
            self.fitted_transformers['imputer'] = KNNImputer(n_neighbors=5)
        else:
            self.fitted_transformers['imputer'] = SimpleImputer(
                strategy=self.config.missing_strategy,
                fill_value=self.config.missing_fill_value
            )
        
        # 拟合缺失值处理器
        self.fitted_transformers['imputer'].fit(numeric_data)
        
        # 标准化器
        if self.config.scaling_method == 'standard':
            self.fitted_transformers['scaler'] = StandardScaler()
        elif self.config.scaling_method == 'minmax':
            self.fitted_transformers['scaler'] = MinMaxScaler()
        elif self.config.scaling_method == 'robust':
            self.fitted_transformers['scaler'] = RobustScaler()
        elif self.config.scaling_method == 'quantile':
            self.fitted_transformers['scaler'] = QuantileTransformer()
        
        # 拟合标准化器（使用填充后的数据）
        imputed_data = self.fitted_transformers['imputer'].transform(numeric_data)
        self.fitted_transformers['scaler'].fit(imputed_data)
        
        # 特征选择器
        if self.config.feature_selection and len(numeric_data.columns) > 1:
            # 需要目标变量，这里使用第一列作为目标
            X = imputed_data[:, 1:]
            y = imputed_data[:, 0]
            
            if X.shape[1] > 0:
                k = min(self.config.feature_selection_k, X.shape[1])
                
                if self.config.feature_selection_method == 'f_regression':
                    self.fitted_transformers['feature_selector'] = SelectKBest(
                        score_func=f_regression, k=k
                    )
                elif self.config.feature_selection_method == 'mutual_info':
                    self.fitted_transformers['feature_selector'] = SelectKBest(
                        score_func=mutual_info_regression, k=k
                    )
                
                self.fitted_transformers['feature_selector'].fit(X, y)
        
        # 降维器
        if self.config.dimensionality_reduction:
            n_components = self.config.n_components or min(10, len(numeric_data.columns))
            
            if self.config.reduction_method == 'pca':
                self.fitted_transformers['reducer'] = PCA(n_components=n_components)
            elif self.config.reduction_method == 'ica':
                self.fitted_transformers['reducer'] = FastICA(n_components=n_components)
            
            # 拟合降维器
            scaled_data = self.fitted_transformers['scaler'].transform(imputed_data)
            self.fitted_transformers['reducer'].fit(scaled_data)
    
    def _apply_transformations(self, data: pd.DataFrame) -> pd.DataFrame:
        """应用转换"""
        result = data.copy()
        numeric_columns = result.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) == 0:
            return result
        
        # 处理缺失值
        if 'imputer' in self.fitted_transformers:
            imputed_values = self.fitted_transformers['imputer'].transform(result[numeric_columns])
            result[numeric_columns] = imputed_values
        
        # 异常值处理
        result = self._handle_outliers(result)
        
        # 数据转换
        if self.config.log_transform:
            result = self._apply_log_transform(result)
        
        if self.config.box_cox_transform:
            result = self._apply_box_cox_transform(result)
        
        # 标准化
        if 'scaler' in self.fitted_transformers:
            scaled_values = self.fitted_transformers['scaler'].transform(result[numeric_columns])
            result[numeric_columns] = scaled_values
        
        # 特征选择
        if 'feature_selector' in self.fitted_transformers and len(numeric_columns) > 1:
            X = result[numeric_columns].iloc[:, 1:].values
            if X.shape[1] > 0:
                selected_features = self.fitted_transformers['feature_selector'].transform(X)
                selected_columns = [f'feature_{i}' for i in range(selected_features.shape[1])]
                
                # 保留第一列（目标变量）和选择的特征
                result_selected = pd.DataFrame(selected_features, columns=selected_columns, index=result.index)
                result_selected[numeric_columns[0]] = result[numeric_columns[0]]
                
                # 保留非数值列
                non_numeric_columns = result.select_dtypes(exclude=[np.number]).columns
                for col in non_numeric_columns:
                    result_selected[col] = result[col]
                
                result = result_selected
        
        # 降维
        if 'reducer' in self.fitted_transformers:
            reduced_values = self.fitted_transformers['reducer'].transform(result[numeric_columns])
            reduced_columns = [f'component_{i}' for i in range(reduced_values.shape[1])]
            
            result_reduced = pd.DataFrame(reduced_values, columns=reduced_columns, index=result.index)
            
            # 保留非数值列
            non_numeric_columns = result.select_dtypes(exclude=[np.number]).columns
            for col in non_numeric_columns:
                result_reduced[col] = result[col]
            
            result = result_reduced
        
        return result
    
    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """处理异常值"""
        result = data.copy()
        numeric_columns = result.select_dtypes(include=[np.number]).columns
        
        outlier_count = 0
        
        for col in numeric_columns:
            if self.config.outlier_method == 'iqr':
                Q1 = result[col].quantile(0.25)
                Q3 = result[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = (result[col] < lower_bound) | (result[col] > upper_bound)
                
            elif self.config.outlier_method == 'zscore':
                z_scores = np.abs(stats.zscore(result[col].dropna()))
                outliers = pd.Series(False, index=result.index)
                outliers.loc[result[col].dropna().index] = z_scores > self.config.outlier_threshold
                
            elif self.config.outlier_method == 'isolation_forest':
                from sklearn.ensemble import IsolationForest
                
                iso_forest = IsolationForest(contamination=0.1, random_state=42)
                outlier_labels = iso_forest.fit_predict(result[[col]].dropna())
                
                outliers = pd.Series(False, index=result.index)
                outliers.loc[result[col].dropna().index] = outlier_labels == -1
                
            else:
                continue
            
            outlier_count += outliers.sum()
            
            # 处理异常值
            if self.config.outlier_action == 'remove':
                result = result[~outliers]
            elif self.config.outlier_action == 'clip':
                if self.config.outlier_method == 'iqr':
                    result.loc[outliers, col] = result[col].clip(lower_bound, upper_bound)
                elif self.config.outlier_method == 'zscore':
                    median_val = result[col].median()
                    mad = np.median(np.abs(result[col] - median_val))
                    result.loc[outliers, col] = median_val
            elif self.config.outlier_action == 'transform':
                # 使用Winsorization
                result.loc[outliers, col] = result[col].clip(
                    result[col].quantile(0.05),
                    result[col].quantile(0.95)
                )
        
        self.processing_stats['outliers_detected'] = outlier_count
        
        return result
    
    def _apply_log_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """应用对数转换"""
        result = data.copy()
        numeric_columns = result.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if (result[col] > 0).all():
                result[f'{col}_log'] = np.log(result[col])
            else:
                # 对于包含非正值的列，使用log1p
                result[f'{col}_log1p'] = np.log1p(result[col] - result[col].min() + 1)
        
        return result
    
    def _apply_box_cox_transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """应用Box-Cox转换"""
        result = data.copy()
        numeric_columns = result.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            if (result[col] > 0).all():
                try:
                    transformed_data, lambda_param = stats.boxcox(result[col])
                    result[f'{col}_boxcox'] = transformed_data
                    self.processing_stats[f'{col}_boxcox_lambda'] = lambda_param
                except Exception as e:
                    logger.warning(f"列 {col} Box-Cox转换失败: {e}")
        
        return result
    
    def _update_stats(self, original_data: pd.DataFrame, processed_data: pd.DataFrame):
        """更新处理统计信息"""
        self.processing_stats.update({
            'original_shape': original_data.shape,
            'processed_shape': processed_data.shape,
            'missing_values_original': original_data.isnull().sum().sum(),
            'missing_values_processed': processed_data.isnull().sum().sum(),
            'processing_time': datetime.now().isoformat()
        })

class FeatureEngineer:
    """特征工程器"""
    
    def __init__(self):
        self.feature_stats = {}
    
    def create_time_features(self, data: pd.DataFrame, time_column: str) -> pd.DataFrame:
        """创建时间特征"""
        result = data.copy()
        
        if time_column not in result.columns:
            raise DataProcessingError(f"时间列 '{time_column}' 不存在")
        
        # 确保是datetime类型
        result[time_column] = pd.to_datetime(result[time_column])
        
        # 提取时间特征
        result[f'{time_column}_year'] = result[time_column].dt.year
        result[f'{time_column}_month'] = result[time_column].dt.month
        result[f'{time_column}_day'] = result[time_column].dt.day
        result[f'{time_column}_hour'] = result[time_column].dt.hour
        result[f'{time_column}_minute'] = result[time_column].dt.minute
        result[f'{time_column}_weekday'] = result[time_column].dt.weekday
        result[f'{time_column}_quarter'] = result[time_column].dt.quarter
        result[f'{time_column}_dayofyear'] = result[time_column].dt.dayofyear
        result[f'{time_column}_weekofyear'] = result[time_column].dt.isocalendar().week
        
        # 周期性特征（正弦余弦编码）
        result[f'{time_column}_hour_sin'] = np.sin(2 * np.pi * result[f'{time_column}_hour'] / 24)
        result[f'{time_column}_hour_cos'] = np.cos(2 * np.pi * result[f'{time_column}_hour'] / 24)
        result[f'{time_column}_month_sin'] = np.sin(2 * np.pi * result[f'{time_column}_month'] / 12)
        result[f'{time_column}_month_cos'] = np.cos(2 * np.pi * result[f'{time_column}_month'] / 12)
        result[f'{time_column}_weekday_sin'] = np.sin(2 * np.pi * result[f'{time_column}_weekday'] / 7)
        result[f'{time_column}_weekday_cos'] = np.cos(2 * np.pi * result[f'{time_column}_weekday'] / 7)
        
        return result
    
    def create_lag_features(self, data: pd.DataFrame, columns: List[str], lags: List[int]) -> pd.DataFrame:
        """创建滞后特征"""
        result = data.copy()
        
        for col in columns:
            if col not in result.columns:
                logger.warning(f"列 '{col}' 不存在，跳过滞后特征创建")
                continue
            
            for lag in lags:
                result[f'{col}_lag_{lag}'] = result[col].shift(lag)
        
        return result
    
    def create_rolling_features(self, data: pd.DataFrame, columns: List[str], 
                              windows: List[int], functions: List[str] = None) -> pd.DataFrame:
        """创建滚动窗口特征"""
        if functions is None:
            functions = ['mean', 'std', 'min', 'max']
        
        result = data.copy()
        
        for col in columns:
            if col not in result.columns:
                logger.warning(f"列 '{col}' 不存在，跳过滚动特征创建")
                continue
            
            for window in windows:
                rolling = result[col].rolling(window=window)
                
                for func in functions:
                    if hasattr(rolling, func):
                        result[f'{col}_rolling_{window}_{func}'] = getattr(rolling, func)()
        
        return result
    
    def create_statistical_features(self, data: pd.DataFrame, columns: List[str], 
                                  window: int = 100) -> pd.DataFrame:
        """创建统计特征"""
        result = data.copy()
        
        for col in columns:
            if col not in result.columns:
                logger.warning(f"列 '{col}' 不存在，跳过统计特征创建")
                continue
            
            rolling = result[col].rolling(window=window)
            
            # 基本统计量
            result[f'{col}_skew'] = rolling.skew()
            result[f'{col}_kurt'] = rolling.kurt()
            result[f'{col}_quantile_25'] = rolling.quantile(0.25)
            result[f'{col}_quantile_75'] = rolling.quantile(0.75)
            
            # 变化率
            result[f'{col}_pct_change'] = result[col].pct_change()
            result[f'{col}_diff'] = result[col].diff()
            
            # 累积统计
            result[f'{col}_cumsum'] = result[col].cumsum()
            result[f'{col}_cumprod'] = result[col].cumprod()
            
            # 排名特征
            result[f'{col}_rank'] = result[col].rolling(window=window).rank()
        
        return result
    
    def create_interaction_features(self, data: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """创建交互特征"""
        result = data.copy()
        
        for i, col1 in enumerate(columns):
            for col2 in columns[i+1:]:
                if col1 in result.columns and col2 in result.columns:
                    # 乘积交互
                    result[f'{col1}_x_{col2}'] = result[col1] * result[col2]
                    
                    # 比率交互（避免除零）
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        result[f'{col1}_div_{col2}'] = result[col1] / (result[col2] + 1e-8)
                    
                    # 差值交互
                    result[f'{col1}_minus_{col2}'] = result[col1] - result[col2]
        
        return result
    
    def create_technical_indicators(self, data: pd.DataFrame, price_column: str, 
                                  volume_column: Optional[str] = None) -> pd.DataFrame:
        """创建技术指标特征（需要ta库）"""
        if not TA_AVAILABLE:
            logger.warning("ta库未安装，跳过技术指标创建")
            return data
        
        result = data.copy()
        
        if price_column not in result.columns:
            raise DataProcessingError(f"价格列 '{price_column}' 不存在")
        
        try:
            # 移动平均
            result[f'{price_column}_sma_10'] = ta.trend.sma_indicator(result[price_column], window=10)
            result[f'{price_column}_sma_30'] = ta.trend.sma_indicator(result[price_column], window=30)
            result[f'{price_column}_ema_10'] = ta.trend.ema_indicator(result[price_column], window=10)
            
            # RSI
            result[f'{price_column}_rsi'] = ta.momentum.rsi(result[price_column])
            
            # MACD
            macd = ta.trend.MACD(result[price_column])
            result[f'{price_column}_macd'] = macd.macd()
            result[f'{price_column}_macd_signal'] = macd.macd_signal()
            result[f'{price_column}_macd_diff'] = macd.macd_diff()
            
            # 布林带
            bollinger = ta.volatility.BollingerBands(result[price_column])
            result[f'{price_column}_bb_high'] = bollinger.bollinger_hband()
            result[f'{price_column}_bb_low'] = bollinger.bollinger_lband()
            result[f'{price_column}_bb_mid'] = bollinger.bollinger_mavg()
            
            # 如果有成交量数据
            if volume_column and volume_column in result.columns:
                # 成交量移动平均
                result[f'{volume_column}_sma_10'] = ta.trend.sma_indicator(result[volume_column], window=10)
                
                # 价量指标
                result[f'price_volume'] = result[price_column] * result[volume_column]
                
        except Exception as e:
            logger.error(f"技术指标创建失败: {e}")
        
        return result
    
    def get_feature_importance(self, data: pd.DataFrame, target_column: str, 
                             method: str = 'mutual_info') -> pd.Series:
        """获取特征重要性"""
        if target_column not in data.columns:
            raise DataProcessingError(f"目标列 '{target_column}' 不存在")
        
        X = data.drop(columns=[target_column]).select_dtypes(include=[np.number])
        y = data[target_column]
        
        # 处理缺失值
        X = X.fillna(X.mean())
        y = y.fillna(y.mean())
        
        if method == 'mutual_info':
            scores = mutual_info_regression(X, y)
        elif method == 'f_regression':
            scores, _ = f_regression(X, y)
        else:
            raise DataProcessingError(f"不支持的特征重要性方法: {method}")
        
        importance = pd.Series(scores, index=X.columns).sort_values(ascending=False)
        
        return importance

class DataQualityChecker:
    """数据质量检查器"""
    
    def __init__(self):
        self.quality_report = {}
    
    def check_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查数据质量"""
        report = {
            'basic_info': self._check_basic_info(data),
            'missing_values': self._check_missing_values(data),
            'duplicates': self._check_duplicates(data),
            'data_types': self._check_data_types(data),
            'outliers': self._check_outliers(data),
            'correlations': self._check_correlations(data),
            'distributions': self._check_distributions(data)
        }
        
        self.quality_report = report
        return report
    
    def _check_basic_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查基本信息"""
        return {
            'shape': data.shape,
            'memory_usage': data.memory_usage(deep=True).sum(),
            'columns': list(data.columns),
            'dtypes': data.dtypes.to_dict()
        }
    
    def _check_missing_values(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查缺失值"""
        missing_count = data.isnull().sum()
        missing_percent = (missing_count / len(data)) * 100
        
        return {
            'total_missing': missing_count.sum(),
            'missing_by_column': missing_count.to_dict(),
            'missing_percent_by_column': missing_percent.to_dict(),
            'columns_with_missing': missing_count[missing_count > 0].index.tolist()
        }
    
    def _check_duplicates(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查重复值"""
        duplicate_rows = data.duplicated().sum()
        
        return {
            'duplicate_rows': duplicate_rows,
            'duplicate_percent': (duplicate_rows / len(data)) * 100
        }
    
    def _check_data_types(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查数据类型"""
        type_counts = data.dtypes.value_counts().to_dict()
        
        return {
            'type_distribution': type_counts,
            'numeric_columns': data.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': data.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime_columns': data.select_dtypes(include=['datetime64']).columns.tolist()
        }
    
    def _check_outliers(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查异常值"""
        numeric_data = data.select_dtypes(include=[np.number])
        outlier_info = {}
        
        for col in numeric_data.columns:
            Q1 = numeric_data[col].quantile(0.25)
            Q3 = numeric_data[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = ((numeric_data[col] < lower_bound) | (numeric_data[col] > upper_bound)).sum()
            
            outlier_info[col] = {
                'count': outliers,
                'percent': (outliers / len(numeric_data)) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound
            }
        
        return outlier_info
    
    def _check_correlations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查相关性"""
        numeric_data = data.select_dtypes(include=[np.number])
        
        if len(numeric_data.columns) < 2:
            return {'message': '数值列少于2个，无法计算相关性'}
        
        corr_matrix = numeric_data.corr()
        
        # 找出高相关性的特征对
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.8:
                    high_corr_pairs.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        return {
            'correlation_matrix': corr_matrix.to_dict(),
            'high_correlation_pairs': high_corr_pairs
        }
    
    def _check_distributions(self, data: pd.DataFrame) -> Dict[str, Any]:
        """检查分布"""
        numeric_data = data.select_dtypes(include=[np.number])
        distribution_info = {}
        
        for col in numeric_data.columns:
            col_data = numeric_data[col].dropna()
            
            if len(col_data) > 0:
                distribution_info[col] = {
                    'mean': col_data.mean(),
                    'median': col_data.median(),
                    'std': col_data.std(),
                    'skewness': col_data.skew(),
                    'kurtosis': col_data.kurtosis(),
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'unique_values': col_data.nunique(),
                    'zero_count': (col_data == 0).sum()
                }
        
        return distribution_info
    
    def generate_quality_report(self) -> str:
        """生成数据质量报告"""
        if not self.quality_report:
            return "请先运行 check_data_quality() 方法"
        
        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("数据质量报告")
        report_lines.append("=" * 50)
        
        # 基本信息
        basic_info = self.quality_report['basic_info']
        report_lines.append(f"\n数据形状: {basic_info['shape']}")
        report_lines.append(f"内存使用: {basic_info['memory_usage'] / 1024 / 1024:.2f} MB")
        
        # 缺失值
        missing_info = self.quality_report['missing_values']
        report_lines.append(f"\n总缺失值: {missing_info['total_missing']}")
        if missing_info['columns_with_missing']:
            report_lines.append("缺失值列:")
            for col in missing_info['columns_with_missing']:
                count = missing_info['missing_by_column'][col]
                percent = missing_info['missing_percent_by_column'][col]
                report_lines.append(f"  {col}: {count} ({percent:.2f}%)")
        
        # 重复值
        duplicate_info = self.quality_report['duplicates']
        report_lines.append(f"\n重复行: {duplicate_info['duplicate_rows']} ({duplicate_info['duplicate_percent']:.2f}%)")
        
        # 异常值
        outlier_info = self.quality_report['outliers']
        report_lines.append("\n异常值检测:")
        for col, info in outlier_info.items():
            if isinstance(info, dict) and info['count'] > 0:
                report_lines.append(f"  {col}: {info['count']} ({info['percent']:.2f}%)")
        
        # 高相关性
        corr_info = self.quality_report['correlations']
        if 'high_correlation_pairs' in corr_info and corr_info['high_correlation_pairs']:
            report_lines.append("\n高相关性特征对:")
            for pair in corr_info['high_correlation_pairs']:
                report_lines.append(f"  {pair['feature1']} - {pair['feature2']}: {pair['correlation']:.3f}")
        
        return "\n".join(report_lines)

# 便捷函数
def create_time_series_processor(config: Optional[ProcessingConfig] = None) -> TimeSeriesProcessor:
    """创建时间序列处理器"""
    if config is None:
        config = ProcessingConfig()
    return TimeSeriesProcessor(config)

def create_feature_engineer() -> FeatureEngineer:
    """创建特征工程器"""
    return FeatureEngineer()

def create_data_quality_checker() -> DataQualityChecker:
    """创建数据质量检查器"""
    return DataQualityChecker()

def quick_data_analysis(data: pd.DataFrame) -> Dict[str, Any]:
    """快速数据分析"""
    checker = DataQualityChecker()
    quality_report = checker.check_data_quality(data)
    
    # 添加快速统计
    quick_stats = {
        'shape': data.shape,
        'missing_rate': (data.isnull().sum().sum() / (data.shape[0] * data.shape[1])) * 100,
        'duplicate_rate': (data.duplicated().sum() / len(data)) * 100,
        'numeric_columns': len(data.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(data.select_dtypes(include=['object', 'category']).columns)
    }
    
    return {
        'quick_stats': quick_stats,
        'quality_report': quality_report,
        'recommendations': _generate_recommendations(quality_report)
    }

def _generate_recommendations(quality_report: Dict[str, Any]) -> List[str]:
    """生成数据处理建议"""
    recommendations = []
    
    # 缺失值建议
    missing_info = quality_report['missing_values']
    if missing_info['total_missing'] > 0:
        high_missing_cols = [
            col for col, percent in missing_info['missing_percent_by_column'].items()
            if percent > 50
        ]
        if high_missing_cols:
            recommendations.append(f"考虑删除缺失值超过50%的列: {', '.join(high_missing_cols)}")
        else:
            recommendations.append("使用适当的插值方法处理缺失值")
    
    # 重复值建议
    duplicate_info = quality_report['duplicates']
    if duplicate_info['duplicate_percent'] > 5:
        recommendations.append("检查并处理重复数据")
    
    # 异常值建议
    outlier_info = quality_report['outliers']
    high_outlier_cols = [
        col for col, info in outlier_info.items()
        if isinstance(info, dict) and info['percent'] > 10
    ]
    if high_outlier_cols:
        recommendations.append(f"检查异常值较多的列: {', '.join(high_outlier_cols)}")
    
    # 相关性建议
    corr_info = quality_report['correlations']
    if 'high_correlation_pairs' in corr_info and len(corr_info['high_correlation_pairs']) > 0:
        recommendations.append("考虑移除高相关性的冗余特征")
    
    return recommendations