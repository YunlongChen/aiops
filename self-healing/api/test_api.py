#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Self-Healing System API 测试套件
提供完整的API测试覆盖

测试类型:
- 单元测试
- 集成测试
- 性能测试
- 安全测试
"""

import os
import sys
import json
import asyncio
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any

import pytest
import httpx
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from app import app, trigger_system, self_healing_executor
from trigger_system import Alert, AlertSeverity, AlertStatus

# 测试客户端
client = TestClient(app)

# 测试配置
TEST_CONFIG = {
    "api_token": "test-token-123",
    "server": {
        "host": "localhost",
        "port": 8000
    },
    "auth": {
        "api_token": "test-token-123"
    }
}

class TestHealthCheck:
    """健康检查测试"""
    
    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "Self-Healing System API"
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "components" in data
        assert "uptime" in data
        
        # 验证组件状态
        components = data["components"]
        assert "api" in components
        assert components["api"] == "healthy"
    
    def test_metrics_endpoint(self):
        """测试指标端点"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

class TestAuthentication:
    """认证测试"""
    
    def test_protected_endpoint_without_token(self):
        """测试无token访问受保护端点"""
        response = client.get("/api/v1/alerts")
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self):
        """测试无效token访问受保护端点"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/api/v1/alerts", headers=headers)
        assert response.status_code == 401
    
    def test_protected_endpoint_with_valid_token(self):
        """测试有效token访问受保护端点"""
        headers = {"Authorization": "Bearer test-token-123"}
        
        with patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/alerts", headers=headers)
            # 可能返回503（服务不可用）或200，取决于trigger_system是否可用
            assert response.status_code in [200, 503]

class TestAlertsAPI:
    """告警API测试"""
    
    @pytest.fixture
    def auth_headers(self):
        """认证头部"""
        return {"Authorization": "Bearer test-token-123"}
    
    @pytest.fixture
    def mock_trigger_system(self):
        """模拟触发器系统"""
        mock_system = Mock()
        mock_alert_store = Mock()
        
        # 创建测试告警
        test_alert = Alert(
            id="test-alert-1",
            name="Test Alert",
            severity=AlertSeverity.WARNING,
            status=AlertStatus.ACTIVE,
            message="This is a test alert",
            labels={"service": "test", "environment": "dev"},
            annotations={"description": "Test alert description"}
        )
        
        mock_alert_store.get_active_alerts.return_value = [test_alert]
        mock_alert_store.get_alert.return_value = test_alert
        mock_system.alert_store = mock_alert_store
        
        return mock_system
    
    def test_get_alerts_without_trigger_system(self, auth_headers):
        """测试在没有触发器系统时获取告警"""
        with patch('app.trigger_system', None):
            response = client.get("/api/v1/alerts", headers=auth_headers)
            assert response.status_code == 503
            assert "Trigger system not available" in response.json()["detail"]
    
    def test_get_alerts_with_trigger_system(self, auth_headers, mock_trigger_system):
        """测试获取告警列表"""
        with patch('app.trigger_system', mock_trigger_system), \
             patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/alerts", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            
            alert = data[0]
            assert alert["id"] == "test-alert-1"
            assert alert["name"] == "Test Alert"
            assert alert["severity"] == "warning"
            assert alert["status"] == "active"
    
    def test_get_alert_by_id(self, auth_headers, mock_trigger_system):
        """测试根据ID获取告警"""
        with patch('app.trigger_system', mock_trigger_system), \
             patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/alerts/test-alert-1", headers=auth_headers)
            assert response.status_code == 200
            
            alert = response.json()
            assert alert["id"] == "test-alert-1"
            assert alert["name"] == "Test Alert"
    
    def test_get_nonexistent_alert(self, auth_headers, mock_trigger_system):
        """测试获取不存在的告警"""
        mock_trigger_system.alert_store.get_alert.return_value = None
        
        with patch('app.trigger_system', mock_trigger_system), \
             patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/alerts/nonexistent", headers=auth_headers)
            assert response.status_code == 404
            assert "Alert not found" in response.json()["detail"]
    
    def test_resolve_alert(self, auth_headers, mock_trigger_system):
        """测试解决告警"""
        with patch('app.trigger_system', mock_trigger_system), \
             patch('app.config', TEST_CONFIG):
            response = client.post("/api/v1/alerts/test-alert-1/resolve", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Alert resolved successfully"
            assert data["alert_id"] == "test-alert-1"

class TestRulesAPI:
    """规则API测试"""
    
    @pytest.fixture
    def auth_headers(self):
        """认证头部"""
        return {"Authorization": "Bearer test-token-123"}
    
    @pytest.fixture
    def mock_trigger_system_with_rules(self):
        """带规则的模拟触发器系统"""
        mock_system = Mock()
        mock_rule = Mock()
        mock_rule.id = "test-rule-1"
        mock_rule.name = "Test Rule"
        mock_rule.description = "Test rule description"
        mock_rule.pattern = "test.*"
        mock_rule.severity_threshold = AlertSeverity.WARNING
        mock_rule.actions = []
        mock_rule.cooldown_minutes = 5
        mock_rule.max_executions = 3
        mock_rule.enabled = True
        
        mock_system.rules = [mock_rule]
        return mock_system
    
    def test_get_rules(self, auth_headers, mock_trigger_system_with_rules):
        """测试获取规则列表"""
        with patch('app.trigger_system', mock_trigger_system_with_rules), \
             patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/rules", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 1
            
            rule = data[0]
            assert rule["id"] == "test-rule-1"
            assert rule["name"] == "Test Rule"
            assert rule["enabled"] is True
    
    def test_enable_rule(self, auth_headers, mock_trigger_system_with_rules):
        """测试启用规则"""
        with patch('app.trigger_system', mock_trigger_system_with_rules), \
             patch('app.config', TEST_CONFIG):
            response = client.put("/api/v1/rules/test-rule-1/enable", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Rule enabled successfully"
    
    def test_disable_rule(self, auth_headers, mock_trigger_system_with_rules):
        """测试禁用规则"""
        with patch('app.trigger_system', mock_trigger_system_with_rules), \
             patch('app.config', TEST_CONFIG):
            response = client.put("/api/v1/rules/test-rule-1/disable", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Rule disabled successfully"

class TestPlaybooksAPI:
    """Playbook API测试"""
    
    @pytest.fixture
    def auth_headers(self):
        """认证头部"""
        return {"Authorization": "Bearer test-token-123"}
    
    @pytest.fixture
    def temp_playbook(self):
        """临时Playbook文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("""
---
- name: Test Playbook
  hosts: localhost
  tasks:
    - name: Echo test
      debug:
        msg: "This is a test"
""")
            temp_path = f.name
        
        yield temp_path
        
        # 清理
        os.unlink(temp_path)
    
    def test_list_playbooks(self, auth_headers):
        """测试列出Playbook"""
        with patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/playbooks", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert "playbooks" in data
            assert isinstance(data["playbooks"], list)
    
    def test_execute_playbook(self, auth_headers, temp_playbook):
        """测试执行Playbook"""
        request_data = {
            "playbook_path": temp_playbook,
            "inventory": "localhost,",
            "extra_vars": {"test_var": "test_value"},
            "check_mode": True
        }
        
        with patch('app.self_healing_executor', Mock()), \
             patch('app.config', TEST_CONFIG):
            response = client.post("/api/v1/playbooks/execute", 
                                 json=request_data, 
                                 headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert "execution_id" in data
            assert data["status"] == "running"
            assert "started_at" in data
    
    def test_execute_nonexistent_playbook(self, auth_headers):
        """测试执行不存在的Playbook"""
        request_data = {
            "playbook_path": "/nonexistent/playbook.yml",
            "inventory": "localhost,"
        }
        
        with patch('app.self_healing_executor', Mock()), \
             patch('app.config', TEST_CONFIG):
            response = client.post("/api/v1/playbooks/execute", 
                                 json=request_data, 
                                 headers=auth_headers)
            assert response.status_code == 404
            assert "Playbook not found" in response.json()["detail"]

class TestSystemAPI:
    """系统API测试"""
    
    @pytest.fixture
    def auth_headers(self):
        """认证头部"""
        return {"Authorization": "Bearer test-token-123"}
    
    def test_get_system_metrics(self, auth_headers):
        """测试获取系统指标"""
        with patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/system/metrics", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert "timestamp" in data
            assert "cpu_usage" in data
            assert "memory_usage" in data
            assert "disk_usage" in data
            assert "network_io" in data
            assert "active_alerts_count" in data
            assert "services_status" in data
    
    def test_get_system_status(self, auth_headers):
        """测试获取系统状态"""
        with patch('app.config', TEST_CONFIG):
            response = client.get("/api/v1/system/status", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert "system" in data
            assert "components" in data
            assert "statistics" in data
            
            system_info = data["system"]
            assert "uptime_seconds" in system_info
            assert "start_time" in system_info
            assert "current_time" in system_info

class TestConfigAPI:
    """配置API测试"""
    
    @pytest.fixture
    def auth_headers(self):
        """认证头部"""
        return {"Authorization": "Bearer test-token-123"}
    
    def test_get_config(self, auth_headers):
        """测试获取配置"""
        test_config = {
            "server": {"host": "localhost", "port": 8000},
            "api_token": "secret",  # 应该被过滤掉
            "database_password": "secret",  # 应该被过滤掉
            "logging": {"level": "INFO"}
        }
        
        with patch('app.config', test_config):
            response = client.get("/api/v1/config", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert "server" in data
            assert "logging" in data
            # 敏感信息应该被过滤
            assert "api_token" not in data
            assert "database_password" not in data
    
    def test_reload_config(self, auth_headers):
        """测试重新加载配置"""
        with patch('app.config', TEST_CONFIG), \
             patch('aiofiles.open') as mock_open:
            # 模拟配置文件内容
            mock_open.return_value.__aenter__.return_value.read = AsyncMock(
                return_value="server:\n  host: localhost\n  port: 8000"
            )
            
            response = client.post("/api/v1/config/reload", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Configuration reloaded successfully"

class TestPerformance:
    """性能测试"""
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        import concurrent.futures
        import time
        
        def make_request():
            response = client.get("/health")
            return response.status_code
        
        start_time = time.time()
        
        # 并发发送10个请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        
        # 验证所有请求都成功
        assert all(status == 200 for status in results)
        
        # 验证响应时间合理（应该在5秒内完成）
        assert end_time - start_time < 5.0
    
    def test_large_payload(self):
        """测试大负载请求"""
        # 创建大的JSON负载
        large_data = {
            "data": [f"item_{i}" for i in range(1000)],
            "metadata": {f"key_{i}": f"value_{i}" for i in range(100)}
        }
        
        # 这个测试主要验证服务器能处理大负载而不崩溃
        # 实际的端点可能会返回错误，但不应该导致服务器崩溃
        try:
            response = client.post("/api/v1/test-large-payload", json=large_data)
            # 端点不存在，应该返回404
            assert response.status_code == 404
        except Exception as e:
            # 如果有异常，确保不是服务器崩溃
            assert "Connection" not in str(e)

class TestSecurity:
    """安全测试"""
    
    def test_sql_injection_attempt(self):
        """测试SQL注入尝试"""
        malicious_payload = "'; DROP TABLE users; --"
        
        # 尝试在查询参数中注入
        response = client.get(f"/api/v1/alerts?severity={malicious_payload}")
        # 应该返回401（未认证）而不是500（服务器错误）
        assert response.status_code == 401
    
    def test_xss_attempt(self):
        """测试XSS尝试"""
        malicious_script = "<script>alert('xss')</script>"
        
        # 尝试在请求中包含脚本
        response = client.get(f"/api/v1/alerts?name={malicious_script}")
        # 应该返回401（未认证）而不是执行脚本
        assert response.status_code == 401
    
    def test_path_traversal_attempt(self):
        """测试路径遍历尝试"""
        malicious_path = "../../../etc/passwd"
        
        # 尝试访问系统文件
        response = client.get(f"/api/v1/playbooks/{malicious_path}")
        # 应该返回404或401，而不是文件内容
        assert response.status_code in [401, 404]

# 测试运行器
if __name__ == "__main__":
    # 运行所有测试
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])