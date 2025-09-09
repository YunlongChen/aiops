#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异常检测器测试模块

本模块包含异常检测器的测试用例，包括：
- 各种异常检测算法测试
- 数据预处理测试
- 性能测试
- 边界条件测试

Author: AIOps Team
Date: 2024-01-10
"""

import pytest
import numpy as np
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import warnings

# 导入被测试的模块
from core.anomaly_detector import (
    AnomalyDetector,
    AnomalyDetectionError,
    IsolationForestDetector,
    LocalOutlierFactorDetector,
    OneClassSVMDetector,
    StatisticalDetector,
    LSTMAutoencoderDetector,
    EnsembleDetector
)

# 忽略警告
warnings.filterwarnings("ignore")


class TestAnomalyDetector:
    """异常检测器基类测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = AnomalyDetector()
        
        # 创建测试数据
        np.random.seed(42)
        self.normal_data = np.random.normal(0, 1, 1000)
        
        # 添加异常值
        self.anomaly_data = self.normal_data.copy()
        self.anomaly_data[100] = 10  # 明显的异常值
        self.anomaly_data[500] = -8  # 另一个异常值
        
        # 创建时间序列数据
        dates = pd.date_range('2024-01-01', periods=1000, freq='H')
        self.ts_data = pd.DataFrame({
            'timestamp': dates,
            'value': self.anomaly_data,
            'feature1': np.random.normal(0, 0.5, 1000),
            'feature2': np.random.normal(1, 0.3, 1000)
        })
    
    def test_initialization(self):
        """测试初始化"""
        detector = AnomalyDetector()
        assert detector.algorithm == 'isolation_forest'
        assert detector.contamination == 0.1
        assert detector.model is None
        assert detector.scaler is None
        assert detector.feature_selector is None
    
    def test_custom_initialization(self):
        """测试自定义初始化"""
        detector = AnomalyDetector(
            algorithm='local_outlier_factor',
            contamination=0.05,
            random_state=123
        )
        assert detector.algorithm == 'local_outlier_factor'
        assert detector.contamination == 0.05
        assert detector.random_state == 123
    
    def test_preprocess_data_array(self):
        """测试数组数据预处理"""
        processed_data = self.detector._preprocess_data(self.anomaly_data)
        
        assert isinstance(processed_data, np.ndarray)
        assert processed_data.shape[0] == len(self.anomaly_data)
        assert not np.isnan(processed_data).any()
    
    def test_preprocess_data_dataframe(self):
        """测试DataFrame数据预处理"""
        processed_data = self.detector._preprocess_data(self.ts_data)
        
        assert isinstance(processed_data, np.ndarray)
        assert processed_data.shape[0] == len(self.ts_data)
        assert processed_data.shape[1] > 1  # 多个特征
    
    def test_preprocess_data_with_missing_values(self):
        """测试包含缺失值的数据预处理"""
        data_with_nan = self.anomaly_data.copy()
        data_with_nan[50:60] = np.nan
        
        processed_data = self.detector._preprocess_data(data_with_nan)
        
        assert not np.isnan(processed_data).any()
        assert len(processed_data) <= len(data_with_nan)
    
    def test_feature_engineering(self):
        """测试特征工程"""
        features = self.detector._feature_engineering(self.ts_data)
        
        assert isinstance(features, np.ndarray)
        assert features.shape[0] == len(self.ts_data)
        assert features.shape[1] >= self.ts_data.select_dtypes(include=[np.number]).shape[1]
    
    def test_postprocess_results(self):
        """测试结果后处理"""
        # 模拟原始结果
        raw_scores = np.array([0.1, 0.2, 0.8, 0.15, 0.9, 0.05])
        raw_labels = np.array([1, 1, -1, 1, -1, 1])
        
        results = self.detector._postprocess_results(
            raw_scores, raw_labels, self.ts_data[:6]
        )
        
        assert 'anomalies' in results
        assert 'statistics' in results
        assert len(results['anomalies']) == 2  # 两个异常点
    
    def test_invalid_algorithm(self):
        """测试无效算法"""
        with pytest.raises(ValueError):
            AnomalyDetector(algorithm='invalid_algorithm')
    
    def test_invalid_contamination(self):
        """测试无效污染率"""
        with pytest.raises(ValueError):
            AnomalyDetector(contamination=1.5)  # 超过1.0
        
        with pytest.raises(ValueError):
            AnomalyDetector(contamination=-0.1)  # 小于0


class TestIsolationForestDetector:
    """孤立森林检测器测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = IsolationForestDetector(contamination=0.1, random_state=42)
        
        # 创建测试数据
        np.random.seed(42)
        self.normal_data = np.random.normal(0, 1, (1000, 2))
        
        # 添加异常值
        self.anomaly_data = self.normal_data.copy()
        self.anomaly_data[100] = [10, 10]  # 明显的异常值
        self.anomaly_data[500] = [-8, -8]  # 另一个异常值
    
    def test_fit_and_predict(self):
        """测试训练和预测"""
        # 训练模型
        self.detector.fit(self.normal_data)
        assert self.detector.model is not None
        
        # 预测异常
        scores = self.detector.predict(self.anomaly_data)
        labels = self.detector.predict_labels(self.anomaly_data)
        
        assert len(scores) == len(self.anomaly_data)
        assert len(labels) == len(self.anomaly_data)
        assert np.sum(labels == -1) > 0  # 应该检测到异常
    
    def test_detect_anomalies_array(self):
        """测试数组异常检测"""
        results = self.detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results
        assert 'statistics' in results
        assert len(results['anomalies']) > 0
        assert results['statistics']['total_points'] == len(self.anomaly_data)
    
    def test_detect_anomalies_dataframe(self):
        """测试DataFrame异常检测"""
        df = pd.DataFrame(self.anomaly_data, columns=['feature1', 'feature2'])
        df['timestamp'] = pd.date_range('2024-01-01', periods=len(df), freq='H')
        
        results = self.detector.detect_anomalies(df)
        
        assert 'anomalies' in results
        assert 'statistics' in results
        assert len(results['anomalies']) > 0
    
    def test_custom_parameters(self):
        """测试自定义参数"""
        detector = IsolationForestDetector(
            n_estimators=200,
            max_samples=0.8,
            contamination=0.05
        )
        
        results = detector.detect_anomalies(self.anomaly_data)
        assert 'anomalies' in results
    
    def test_small_dataset(self):
        """测试小数据集"""
        small_data = self.anomaly_data[:50]
        results = self.detector.detect_anomalies(small_data)
        
        assert 'anomalies' in results
        assert 'statistics' in results


class TestLocalOutlierFactorDetector:
    """局部异常因子检测器测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = LocalOutlierFactorDetector(contamination=0.1)
        
        # 创建测试数据
        np.random.seed(42)
        self.normal_data = np.random.normal(0, 1, (500, 2))
        
        # 添加异常值
        self.anomaly_data = self.normal_data.copy()
        self.anomaly_data[50] = [5, 5]
        self.anomaly_data[250] = [-5, -5]
    
    def test_detect_anomalies(self):
        """测试异常检测"""
        results = self.detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results
        assert 'statistics' in results
        assert len(results['anomalies']) > 0
    
    def test_custom_neighbors(self):
        """测试自定义邻居数"""
        detector = LocalOutlierFactorDetector(n_neighbors=30)
        results = detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results


class TestOneClassSVMDetector:
    """单类支持向量机检测器测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = OneClassSVMDetector(nu=0.1)
        
        # 创建测试数据
        np.random.seed(42)
        self.normal_data = np.random.normal(0, 1, (500, 2))
        
        # 添加异常值
        self.anomaly_data = self.normal_data.copy()
        self.anomaly_data[50] = [4, 4]
        self.anomaly_data[250] = [-4, -4]
    
    def test_detect_anomalies(self):
        """测试异常检测"""
        results = self.detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results
        assert 'statistics' in results
    
    def test_different_kernels(self):
        """测试不同核函数"""
        for kernel in ['rbf', 'linear', 'poly']:
            detector = OneClassSVMDetector(kernel=kernel)
            results = detector.detect_anomalies(self.anomaly_data)
            assert 'anomalies' in results


class TestStatisticalDetector:
    """统计方法检测器测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = StatisticalDetector(method='zscore', threshold=3.0)
        
        # 创建测试数据
        np.random.seed(42)
        self.normal_data = np.random.normal(0, 1, 1000)
        
        # 添加异常值
        self.anomaly_data = self.normal_data.copy()
        self.anomaly_data[100] = 5  # 5个标准差
        self.anomaly_data[500] = -5  # -5个标准差
    
    def test_zscore_method(self):
        """测试Z-score方法"""
        results = self.detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results
        assert 'statistics' in results
        assert len(results['anomalies']) >= 2  # 至少检测到两个异常
    
    def test_modified_zscore_method(self):
        """测试修正Z-score方法"""
        detector = StatisticalDetector(method='modified_zscore', threshold=3.5)
        results = detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results
    
    def test_iqr_method(self):
        """测试IQR方法"""
        detector = StatisticalDetector(method='iqr', threshold=1.5)
        results = detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results
    
    def test_invalid_method(self):
        """测试无效方法"""
        with pytest.raises(ValueError):
            StatisticalDetector(method='invalid_method')


class TestLSTMAutoencoderDetector:
    """LSTM自编码器检测器测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = LSTMAutoencoderDetector(
            sequence_length=10,
            encoding_dim=5,
            epochs=2,  # 减少训练轮数以加快测试
            batch_size=16
        )
        
        # 创建时间序列数据
        np.random.seed(42)
        self.ts_data = np.sin(np.linspace(0, 10*np.pi, 200)) + np.random.normal(0, 0.1, 200)
        
        # 添加异常值
        self.ts_data[50] = 5
        self.ts_data[150] = -5
    
    @pytest.mark.slow
    def test_detect_anomalies(self):
        """测试异常检测（标记为慢速测试）"""
        results = self.detector.detect_anomalies(self.ts_data)
        
        assert 'anomalies' in results
        assert 'statistics' in results
    
    def test_create_sequences(self):
        """测试序列创建"""
        sequences = self.detector._create_sequences(self.ts_data, 10)
        
        assert sequences.shape[0] == len(self.ts_data) - 10 + 1
        assert sequences.shape[1] == 10
    
    @patch('tensorflow.keras.models.Sequential')
    def test_build_model_mock(self, mock_sequential):
        """测试模型构建（使用模拟）"""
        mock_model = MagicMock()
        mock_sequential.return_value = mock_model
        
        model = self.detector._build_model(10, 5)
        assert model is not None


class TestEnsembleDetector:
    """集成检测器测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = EnsembleDetector(
            algorithms=['isolation_forest', 'local_outlier_factor', 'statistical'],
            voting='soft',
            weights=[0.4, 0.3, 0.3]
        )
        
        # 创建测试数据
        np.random.seed(42)
        self.normal_data = np.random.normal(0, 1, (500, 2))
        
        # 添加异常值
        self.anomaly_data = self.normal_data.copy()
        self.anomaly_data[50] = [4, 4]
        self.anomaly_data[250] = [-4, -4]
    
    def test_detect_anomalies(self):
        """测试集成异常检测"""
        results = self.detector.detect_anomalies(self.anomaly_data)
        
        assert 'anomalies' in results
        assert 'statistics' in results
        assert len(results['anomalies']) > 0
    
    def test_hard_voting(self):
        """测试硬投票"""
        detector = EnsembleDetector(
            algorithms=['isolation_forest', 'statistical'],
            voting='hard'
        )
        
        results = detector.detect_anomalies(self.anomaly_data)
        assert 'anomalies' in results
    
    def test_invalid_weights(self):
        """测试无效权重"""
        with pytest.raises(ValueError):
            EnsembleDetector(
                algorithms=['isolation_forest', 'statistical'],
                weights=[0.3, 0.4, 0.3]  # 权重数量不匹配
            )


class TestAnomalyDetectorPerformance:
    """异常检测器性能测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = IsolationForestDetector()
        
        # 创建大数据集
        np.random.seed(42)
        self.large_data = np.random.normal(0, 1, (10000, 5))
    
    @pytest.mark.slow
    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        import time
        
        start_time = time.time()
        results = self.detector.detect_anomalies(self.large_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert 'anomalies' in results
        assert processing_time < 30  # 应在30秒内完成
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss
        
        # 处理数据
        results = self.detector.detect_anomalies(self.large_data)
        
        memory_after = process.memory_info().rss
        memory_increase = memory_after - memory_before
        
        assert 'anomalies' in results
        # 内存增长应该合理（小于1GB）
        assert memory_increase < 1024 * 1024 * 1024


class TestAnomalyDetectorEdgeCases:
    """异常检测器边界条件测试"""
    
    def setup_method(self):
        """测试方法设置"""
        self.detector = IsolationForestDetector()
    
    def test_empty_data(self):
        """测试空数据"""
        with pytest.raises(AnomalyDetectionError):
            self.detector.detect_anomalies(np.array([]))
    
    def test_single_point(self):
        """测试单点数据"""
        with pytest.raises(AnomalyDetectionError):
            self.detector.detect_anomalies(np.array([1.0]))
    
    def test_all_same_values(self):
        """测试所有值相同的数据"""
        same_values = np.ones(100)
        
        # 应该能处理但可能不会检测到异常
        results = self.detector.detect_anomalies(same_values)
        assert 'anomalies' in results
        assert 'statistics' in results
    
    def test_all_nan_values(self):
        """测试所有NaN值的数据"""
        nan_values = np.full(100, np.nan)
        
        with pytest.raises(AnomalyDetectionError):
            self.detector.detect_anomalies(nan_values)
    
    def test_infinite_values(self):
        """测试包含无穷值的数据"""
        data_with_inf = np.random.normal(0, 1, 100)
        data_with_inf[50] = np.inf
        data_with_inf[60] = -np.inf
        
        # 应该能处理无穷值
        results = self.detector.detect_anomalies(data_with_inf)
        assert 'anomalies' in results


if __name__ == "__main__":
    # 运行测试
    pytest.main(["-v", __file__])