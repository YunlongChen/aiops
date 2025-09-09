#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI引擎应用测试模块

本模块包含AI引擎主应用的测试用例，包括：
- API端点测试
- 健康检查测试
- 异常处理测试
- 性能测试

Author: AIOps Team
Date: 2024-01-10
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
import time
from datetime import datetime, timedelta

# 导入应用模块
from app import app, get_ai_engine
from core.anomaly_detector import AnomalyDetector
from core.predictor import Predictor
from core.decision_engine import DecisionEngine
from core.model_manager import ModelManager
from utils.config import config_manager


class TestAIEngineApp:
    """AI引擎应用测试类"""
    
    def setup_method(self):
        """测试方法设置"""
        self.client = TestClient(app)
        
        # 创建模拟的AI引擎组件
        self.mock_anomaly_detector = Mock(spec=AnomalyDetector)
        self.mock_predictor = Mock(spec=Predictor)
        self.mock_decision_engine = Mock(spec=DecisionEngine)
        self.mock_model_manager = Mock(spec=ModelManager)
        
        # 设置模拟返回值
        self.mock_anomaly_detector.detect_anomalies.return_value = {
            'anomalies': [{'timestamp': '2024-01-10T10:00:00Z', 'score': 0.8, 'is_anomaly': True}],
            'statistics': {'total_points': 100, 'anomaly_count': 5, 'anomaly_rate': 0.05}
        }
        
        self.mock_predictor.predict.return_value = {
            'predictions': [1.2, 1.3, 1.1, 1.4],
            'confidence_intervals': [[1.0, 1.4], [1.1, 1.5], [0.9, 1.3], [1.2, 1.6]],
            'model_info': {'algorithm': 'lstm', 'accuracy': 0.95}
        }
        
        self.mock_decision_engine.make_decision.return_value = {
            'decision': 'scale_up',
            'confidence': 0.9,
            'reasoning': 'High CPU usage detected',
            'actions': [{'type': 'scale', 'parameters': {'instances': 3}}]
        }
        
        self.mock_model_manager.list_models.return_value = [
            {'name': 'anomaly_model_v1', 'type': 'isolation_forest', 'accuracy': 0.92},
            {'name': 'prediction_model_v1', 'type': 'lstm', 'accuracy': 0.95}
        ]
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "uptime" in data
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
    
    @patch('app.get_ai_engine')
    def test_get_metrics(self, mock_get_ai_engine):
        """测试获取指标端点"""
        # 设置模拟AI引擎
        mock_ai_engine = Mock()
        mock_ai_engine.anomaly_detector = self.mock_anomaly_detector
        mock_ai_engine.predictor = self.mock_predictor
        mock_ai_engine.decision_engine = self.mock_decision_engine
        mock_ai_engine.model_manager = self.mock_model_manager
        mock_get_ai_engine.return_value = mock_ai_engine
        
        # 模拟指标数据
        mock_metrics = {
            "cpu_usage": [70.5, 72.1, 68.9, 75.2],
            "memory_usage": [65.3, 67.8, 64.1, 69.5],
            "response_time": [120, 135, 110, 145]
        }
        
        response = self.client.post("/api/v1/metrics", json=mock_metrics)
        assert response.status_code == 200
        
        data = response.json()
        assert "metrics" in data
        assert "timestamp" in data
    
    @patch('app.get_ai_engine')
    def test_detect_anomalies(self, mock_get_ai_engine):
        """测试异常检测端点"""
        # 设置模拟AI引擎
        mock_ai_engine = Mock()
        mock_ai_engine.anomaly_detector = self.mock_anomaly_detector
        mock_get_ai_engine.return_value = mock_ai_engine
        
        # 测试数据
        test_data = {
            "data": [1.0, 1.1, 1.2, 5.0, 1.1, 1.0],  # 包含一个异常值
            "algorithm": "isolation_forest",
            "parameters": {"contamination": 0.1}
        }
        
        response = self.client.post("/api/v1/anomalies/detect", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "anomalies" in data
        assert "statistics" in data
        
        # 验证调用参数
        self.mock_anomaly_detector.detect_anomalies.assert_called_once()
    
    @patch('app.get_ai_engine')
    def test_predict_metrics(self, mock_get_ai_engine):
        """测试指标预测端点"""
        # 设置模拟AI引擎
        mock_ai_engine = Mock()
        mock_ai_engine.predictor = self.mock_predictor
        mock_get_ai_engine.return_value = mock_ai_engine
        
        # 测试数据
        test_data = {
            "data": [1.0, 1.1, 1.2, 1.3, 1.1, 1.0, 1.2, 1.4],
            "horizon": 4,
            "algorithm": "lstm",
            "parameters": {"sequence_length": 5}
        }
        
        response = self.client.post("/api/v1/predictions/predict", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "predictions" in data
        assert "confidence_intervals" in data
        assert "model_info" in data
        
        # 验证调用参数
        self.mock_predictor.predict.assert_called_once()
    
    @patch('app.get_ai_engine')
    def test_make_decision(self, mock_get_ai_engine):
        """测试自动决策端点"""
        # 设置模拟AI引擎
        mock_ai_engine = Mock()
        mock_ai_engine.decision_engine = self.mock_decision_engine
        mock_get_ai_engine.return_value = mock_ai_engine
        
        # 测试数据
        test_data = {
            "context": {
                "cpu_usage": 85.0,
                "memory_usage": 78.0,
                "response_time": 2500,
                "error_rate": 0.03
            },
            "constraints": {
                "max_instances": 10,
                "budget_limit": 1000
            }
        }
        
        response = self.client.post("/api/v1/decisions/decide", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "decision" in data
        assert "confidence" in data
        assert "reasoning" in data
        assert "actions" in data
        
        # 验证调用参数
        self.mock_decision_engine.make_decision.assert_called_once()
    
    @patch('app.get_ai_engine')
    def test_list_models(self, mock_get_ai_engine):
        """测试模型列表端点"""
        # 设置模拟AI引擎
        mock_ai_engine = Mock()
        mock_ai_engine.model_manager = self.mock_model_manager
        mock_get_ai_engine.return_value = mock_ai_engine
        
        response = self.client.get("/api/v1/models")
        assert response.status_code == 200
        
        data = response.json()
        assert "models" in data
        assert len(data["models"]) == 2
        
        # 验证模型信息
        model = data["models"][0]
        assert "name" in model
        assert "type" in model
        assert "accuracy" in model
    
    @patch('app.get_ai_engine')
    def test_train_model(self, mock_get_ai_engine):
        """测试模型训练端点"""
        # 设置模拟AI引擎
        mock_ai_engine = Mock()
        mock_ai_engine.model_manager = self.mock_model_manager
        mock_get_ai_engine.return_value = mock_ai_engine
        
        # 设置训练返回值
        self.mock_model_manager.train_model.return_value = {
            "model_id": "test_model_123",
            "status": "training_started",
            "estimated_time": 300
        }
        
        # 测试数据
        test_data = {
            "model_type": "anomaly_detection",
            "algorithm": "isolation_forest",
            "data_source": "metrics_db",
            "parameters": {
                "contamination": 0.1,
                "n_estimators": 100
            }
        }
        
        response = self.client.post("/api/v1/models/train", json=test_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "model_id" in data
        assert "status" in data
        assert "estimated_time" in data
    
    def test_invalid_endpoint(self):
        """测试无效端点"""
        response = self.client.get("/api/v1/invalid")
        assert response.status_code == 404
    
    def test_invalid_method(self):
        """测试无效HTTP方法"""
        response = self.client.delete("/api/v1/metrics")
        assert response.status_code == 405
    
    def test_invalid_json(self):
        """测试无效JSON数据"""
        response = self.client.post(
            "/api/v1/anomalies/detect",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        # 缺少data字段
        test_data = {
            "algorithm": "isolation_forest"
        }
        
        response = self.client.post("/api/v1/anomalies/detect", json=test_data)
        assert response.status_code == 422
    
    def test_cors_headers(self):
        """测试CORS头部"""
        response = self.client.options("/api/v1/health")
        assert response.status_code == 200
        
        # 检查CORS头部
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
    
    @patch('app.get_ai_engine')
    def test_performance_metrics(self, mock_get_ai_engine):
        """测试性能指标"""
        # 设置模拟AI引擎
        mock_ai_engine = Mock()
        mock_ai_engine.anomaly_detector = self.mock_anomaly_detector
        mock_get_ai_engine.return_value = mock_ai_engine
        
        # 测试响应时间
        start_time = time.time()
        
        test_data = {
            "data": list(range(1000)),  # 大量数据
            "algorithm": "isolation_forest"
        }
        
        response = self.client.post("/api/v1/anomalies/detect", json=test_data)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # 响应时间应小于5秒
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            """发送请求的函数"""
            try:
                response = self.client.get("/health")
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # 创建多个线程并发请求
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查结果
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        assert success_count == 10  # 所有请求都应该成功


class TestAIEngineIntegration:
    """AI引擎集成测试类"""
    
    def setup_method(self):
        """测试方法设置"""
        self.client = TestClient(app)
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 检查健康状态
        health_response = self.client.get("/health")
        assert health_response.status_code == 200
        
        # 2. 获取模型列表
        models_response = self.client.get("/api/v1/models")
        assert models_response.status_code == 200
        
        # 3. 模拟异常检测
        anomaly_data = {
            "data": [1.0, 1.1, 1.2, 5.0, 1.1, 1.0],
            "algorithm": "isolation_forest"
        }
        
        with patch('app.get_ai_engine') as mock_get_ai_engine:
            mock_ai_engine = Mock()
            mock_anomaly_detector = Mock()
            mock_anomaly_detector.detect_anomalies.return_value = {
                'anomalies': [{'timestamp': '2024-01-10T10:00:00Z', 'score': 0.8}],
                'statistics': {'anomaly_count': 1}
            }
            mock_ai_engine.anomaly_detector = mock_anomaly_detector
            mock_get_ai_engine.return_value = mock_ai_engine
            
            anomaly_response = self.client.post("/api/v1/anomalies/detect", json=anomaly_data)
            assert anomaly_response.status_code == 200
        
        # 4. 模拟预测
        prediction_data = {
            "data": [1.0, 1.1, 1.2, 1.3, 1.1, 1.0],
            "horizon": 3,
            "algorithm": "lstm"
        }
        
        with patch('app.get_ai_engine') as mock_get_ai_engine:
            mock_ai_engine = Mock()
            mock_predictor = Mock()
            mock_predictor.predict.return_value = {
                'predictions': [1.2, 1.3, 1.1],
                'confidence_intervals': [[1.0, 1.4], [1.1, 1.5], [0.9, 1.3]]
            }
            mock_ai_engine.predictor = mock_predictor
            mock_get_ai_engine.return_value = mock_ai_engine
            
            prediction_response = self.client.post("/api/v1/predictions/predict", json=prediction_data)
            assert prediction_response.status_code == 200
        
        # 5. 模拟决策
        decision_data = {
            "context": {
                "cpu_usage": 85.0,
                "memory_usage": 78.0
            }
        }
        
        with patch('app.get_ai_engine') as mock_get_ai_engine:
            mock_ai_engine = Mock()
            mock_decision_engine = Mock()
            mock_decision_engine.make_decision.return_value = {
                'decision': 'scale_up',
                'confidence': 0.9
            }
            mock_ai_engine.decision_engine = mock_decision_engine
            mock_get_ai_engine.return_value = mock_ai_engine
            
            decision_response = self.client.post("/api/v1/decisions/decide", json=decision_data)
            assert decision_response.status_code == 200


if __name__ == "__main__":
    # 运行测试
    pytest.main(["-v", __file__])