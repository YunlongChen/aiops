#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试场景生成器

该工具用于生成各种类型的测试场景模板，帮助用户快速创建测试用例。
支持API测试、性能测试、集成测试等多种场景类型。

Author: AIOps Team
Date: 2025-01-11
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class TestScenarioGenerator:
    """测试场景生成器"""
    
    def __init__(self):
        """初始化生成器"""
        self.templates = {
            'api': self._generate_api_test_template,
            'performance': self._generate_performance_test_template,
            'integration': self._generate_integration_test_template,
            'security': self._generate_security_test_template,
            'database': self._generate_database_test_template,
            'ui': self._generate_ui_test_template,
            'load': self._generate_load_test_template,
            'smoke': self._generate_smoke_test_template
        }
    
    def _generate_api_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成API测试模板"""
        endpoint = kwargs.get('endpoint', '/api/example')
        method = kwargs.get('method', 'GET')
        
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": f"API测试 - {method} {endpoint}",
            "type": "api",
            "runtime_type": "docker",
            "tags": ["api", "automated", method.lower()],
            "config": {
                "endpoint": endpoint,
                "method": method,
                "timeout": 30,
                "retry_count": 3,
                "expected_status": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                "assertions": [
                    {
                        "type": "status_code",
                        "expected": 200
                    },
                    {
                        "type": "response_time",
                        "max_ms": 1000
                    },
                    {
                        "type": "json_schema",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "data": {"type": "object"}
                            }
                        }
                    }
                ]
            },
            "script_content": f"""
const axios = require('axios');
const assert = require('assert');

async function runTest() {{
    console.log('开始API测试: {name}');
    
    try {{
        const startTime = Date.now();
        const response = await axios({{
            method: '{method}',
            url: process.env.BASE_URL + '{endpoint}',
            timeout: 30000,
            headers: {{
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }}
        }});
        
        const responseTime = Date.now() - startTime;
        
        // 状态码检查
        assert.strictEqual(response.status, 200, '状态码应为200');
        
        // 响应时间检查
        assert(responseTime < 1000, `响应时间应小于1000ms，实际: ${{responseTime}}ms`);
        
        // 响应格式检查
        assert(typeof response.data === 'object', '响应应为JSON对象');
        
        console.log('✅ API测试通过');
        console.log(`响应时间: ${{responseTime}}ms`);
        console.log(`响应状态: ${{response.status}}`);
        
        return {{
            success: true,
            responseTime,
            status: response.status,
            data: response.data
        }};
        
    }} catch (error) {{
        console.error('❌ API测试失败:', error.message);
        throw error;
    }}
}}

module.exports = runTest;
"""
        }
    
    def _generate_performance_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成性能测试模板"""
        duration = kwargs.get('duration', 60)
        concurrent_users = kwargs.get('concurrent_users', 10)
        
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": f"性能测试 - {concurrent_users}并发用户，持续{duration}秒",
            "type": "performance",
            "runtime_type": "k6",
            "tags": ["performance", "load", "stress"],
            "config": {
                "duration": f"{duration}s",
                "vus": concurrent_users,
                "thresholds": {
                    "http_req_duration": ["p(95)<500"],
                    "http_req_failed": ["rate<0.1"]
                }
            },
            "script_content": f"""
import http from 'k6/http';
import {{ check, sleep }} from 'k6';
import {{ Rate }} from 'k6/metrics';

const errorRate = new Rate('errors');

export let options = {{
    vus: {concurrent_users},
    duration: '{duration}s',
    thresholds: {{
        'http_req_duration': ['p(95)<500'],
        'http_req_failed': ['rate<0.1'],
        'errors': ['rate<0.1']
    }}
}};

export default function() {{
    const baseUrl = __ENV.BASE_URL || 'http://localhost:3030';
    
    // 执行HTTP请求
    const response = http.get(`${{baseUrl}}/api/health`);
    
    // 检查响应
    const result = check(response, {{
        '状态码为200': (r) => r.status === 200,
        '响应时间<500ms': (r) => r.timings.duration < 500,
        '响应包含success': (r) => r.body.includes('success')
    }});
    
    errorRate.add(!result);
    
    // 模拟用户思考时间
    sleep(1);
}}

export function handleSummary(data) {{
    return {{
        'performance_report.json': JSON.stringify(data, null, 2),
        stdout: `
性能测试完成 - {name}
平均响应时间: ${{data.metrics.http_req_duration.values.avg.toFixed(2)}}ms
95%响应时间: ${{data.metrics.http_req_duration.values['p(95)'].toFixed(2)}}ms
错误率: ${{(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}}%
总请求数: ${{data.metrics.http_reqs.values.count}}
`
    }};
}}
"""
        }
    
    def _generate_integration_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成集成测试模板"""
        services = kwargs.get('services', ['api', 'database'])
        
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": f"集成测试 - 验证{', '.join(services)}服务间的协作",
            "type": "integration",
            "runtime_type": "docker-compose",
            "tags": ["integration", "e2e"] + services,
            "config": {
                "services": services,
                "setup_timeout": 120,
                "test_timeout": 300,
                "cleanup": True
            },
            "script_content": f"""
const {{ spawn }} = require('child_process');
const axios = require('axios');
const assert = require('assert');

class IntegrationTest {{
    constructor() {{
        this.services = {json.dumps(services)};
        this.baseUrl = process.env.BASE_URL || 'http://localhost:3030';
    }}
    
    async waitForService(url, timeout = 60000) {{
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {{
            try {{
                await axios.get(url, {{ timeout: 5000 }});
                return true;
            }} catch (error) {{
                await new Promise(resolve => setTimeout(resolve, 1000));
            }}
        }}
        
        throw new Error(`服务在${{timeout}}ms内未就绪: ${{url}}`);
    }}
    
    async testServiceConnectivity() {{
        console.log('🔗 测试服务连通性...');
        
        // 测试API服务
        await this.waitForService(`${{this.baseUrl}}/api/health`);
        console.log('✅ API服务连通正常');
        
        // 测试数据库连接
        const dbResponse = await axios.get(`${{this.baseUrl}}/api/health/database`);
        assert.strictEqual(dbResponse.status, 200, '数据库连接失败');
        console.log('✅ 数据库连接正常');
    }}
    
    async testDataFlow() {{
        console.log('📊 测试数据流...');
        
        // 创建测试数据
        const createResponse = await axios.post(`${{this.baseUrl}}/api/test-cases`, {{
            name: 'Integration Test Case',
            description: 'Test case for integration testing',
            script_path: '/tmp/test.js',
            runtime_type: 'docker'
        }});
        
        assert.strictEqual(createResponse.status, 201, '创建测试用例失败');
        const testCaseId = createResponse.data.data.id;
        console.log(`✅ 创建测试用例: ${{testCaseId}}`);
        
        // 查询测试数据
        const getResponse = await axios.get(`${{this.baseUrl}}/api/test-cases/${{testCaseId}}`);
        assert.strictEqual(getResponse.status, 200, '查询测试用例失败');
        console.log('✅ 查询测试用例成功');
        
        // 清理测试数据
        const deleteResponse = await axios.delete(`${{this.baseUrl}}/api/test-cases/${{testCaseId}}`);
        assert.strictEqual(deleteResponse.status, 200, '删除测试用例失败');
        console.log('✅ 清理测试数据完成');
    }}
    
    async run() {{
        console.log('🚀 开始集成测试: {name}');
        
        try {{
            await this.testServiceConnectivity();
            await this.testDataFlow();
            
            console.log('🎉 集成测试全部通过');
            return {{ success: true }};
            
        }} catch (error) {{
            console.error('❌ 集成测试失败:', error.message);
            throw error;
        }}
    }}
}}

async function runTest() {{
    const test = new IntegrationTest();
    return await test.run();
}}

module.exports = runTest;
"""
        }
    
    def _generate_security_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成安全测试模板"""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": "安全测试 - 检查常见安全漏洞",
            "type": "security",
            "runtime_type": "docker",
            "tags": ["security", "vulnerability", "owasp"],
            "config": {
                "scan_types": ["sql_injection", "xss", "csrf", "auth_bypass"],
                "severity_threshold": "medium"
            },
            "script_content": """
const axios = require('axios');
const assert = require('assert');

class SecurityTest {
    constructor() {
        this.baseUrl = process.env.BASE_URL || 'http://localhost:3030';
        this.vulnerabilities = [];
    }
    
    async testSqlInjection() {
        console.log('🔍 测试SQL注入漏洞...');
        
        const payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --"
        ];
        
        for (const payload of payloads) {
            try {
                const response = await axios.get(`${this.baseUrl}/api/test-cases`, {
                    params: { search: payload },
                    timeout: 10000
                });
                
                // 检查是否返回了异常信息
                if (response.data && typeof response.data === 'string' && 
                    (response.data.includes('SQL') || response.data.includes('database'))) {
                    this.vulnerabilities.push({
                        type: 'SQL Injection',
                        severity: 'high',
                        payload: payload,
                        endpoint: '/api/test-cases'
                    });
                }
            } catch (error) {
                // 预期的错误，说明有适当的输入验证
            }
        }
    }
    
    async testXSS() {
        console.log('🔍 测试XSS漏洞...');
        
        const payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>"
        ];
        
        for (const payload of payloads) {
            try {
                const response = await axios.post(`${this.baseUrl}/api/test-cases`, {
                    name: payload,
                    description: 'XSS Test',
                    script_path: '/tmp/test.js',
                    runtime_type: 'docker'
                });
                
                // 检查响应中是否包含未转义的脚本
                if (response.data && JSON.stringify(response.data).includes('<script>')) {
                    this.vulnerabilities.push({
                        type: 'Cross-Site Scripting (XSS)',
                        severity: 'medium',
                        payload: payload,
                        endpoint: '/api/test-cases'
                    });
                }
            } catch (error) {
                // 预期的错误
            }
        }
    }
    
    async testAuthenticationBypass() {
        console.log('🔍 测试认证绕过...');
        
        try {
            // 尝试不带认证信息访问受保护的端点
            const response = await axios.get(`${this.baseUrl}/api/admin/users`, {
                timeout: 10000
            });
            
            if (response.status === 200) {
                this.vulnerabilities.push({
                    type: 'Authentication Bypass',
                    severity: 'critical',
                    description: '管理员端点未进行身份验证',
                    endpoint: '/api/admin/users'
                });
            }
        } catch (error) {
            // 预期的401或403错误
            if (error.response && [401, 403].includes(error.response.status)) {
                console.log('✅ 认证保护正常');
            }
        }
    }
    
    async run() {
        console.log('🛡️ 开始安全测试...');
        
        await this.testSqlInjection();
        await this.testXSS();
        await this.testAuthenticationBypass();
        
        console.log(`\n📊 安全测试完成，发现 ${this.vulnerabilities.length} 个潜在漏洞`);
        
        if (this.vulnerabilities.length > 0) {
            console.log('\n⚠️ 发现的安全问题:');
            this.vulnerabilities.forEach((vuln, index) => {
                console.log(`${index + 1}. ${vuln.type} (${vuln.severity})`);
                console.log(`   端点: ${vuln.endpoint}`);
                if (vuln.payload) console.log(`   载荷: ${vuln.payload}`);
                if (vuln.description) console.log(`   描述: ${vuln.description}`);
                console.log('');
            });
        } else {
            console.log('✅ 未发现明显的安全漏洞');
        }
        
        return {
            success: true,
            vulnerabilities: this.vulnerabilities,
            summary: {
                total: this.vulnerabilities.length,
                critical: this.vulnerabilities.filter(v => v.severity === 'critical').length,
                high: this.vulnerabilities.filter(v => v.severity === 'high').length,
                medium: this.vulnerabilities.filter(v => v.severity === 'medium').length
            }
        };
    }
}

async function runTest() {
    const test = new SecurityTest();
    return await test.run();
}

module.exports = runTest;
"""
        }
    
    def _generate_database_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成数据库测试模板"""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": "数据库测试 - 验证数据库连接和CRUD操作",
            "type": "database",
            "runtime_type": "docker",
            "tags": ["database", "crud", "data"],
            "config": {
                "connection_timeout": 30,
                "query_timeout": 60,
                "test_data_cleanup": True
            },
            "script_content": """
const axios = require('axios');
const assert = require('assert');

class DatabaseTest {
    constructor() {
        this.baseUrl = process.env.BASE_URL || 'http://localhost:3030';
        this.testData = [];
    }
    
    async testConnection() {
        console.log('🔗 测试数据库连接...');
        
        const response = await axios.get(`${this.baseUrl}/api/health/database`);
        assert.strictEqual(response.status, 200, '数据库连接失败');
        assert(response.data.success, '数据库健康检查失败');
        
        console.log('✅ 数据库连接正常');
    }
    
    async testCRUDOperations() {
        console.log('📝 测试CRUD操作...');
        
        // Create - 创建测试数据
        const createData = {
            name: `DB Test Case ${Date.now()}`,
            description: 'Database test case',
            script_path: '/tmp/db_test.js',
            runtime_type: 'docker'
        };
        
        const createResponse = await axios.post(`${this.baseUrl}/api/test-cases`, createData);
        assert.strictEqual(createResponse.status, 201, '创建数据失败');
        
        const testCaseId = createResponse.data.data.id;
        this.testData.push(testCaseId);
        console.log(`✅ 创建数据成功: ${testCaseId}`);
        
        // Read - 读取数据
        const readResponse = await axios.get(`${this.baseUrl}/api/test-cases/${testCaseId}`);
        assert.strictEqual(readResponse.status, 200, '读取数据失败');
        assert.strictEqual(readResponse.data.data.name, createData.name, '读取的数据不匹配');
        console.log('✅ 读取数据成功');
        
        // Update - 更新数据
        const updateData = {
            name: `Updated ${createData.name}`,
            description: 'Updated description'
        };
        
        const updateResponse = await axios.put(`${this.baseUrl}/api/test-cases/${testCaseId}`, updateData);
        assert.strictEqual(updateResponse.status, 200, '更新数据失败');
        console.log('✅ 更新数据成功');
        
        // Verify update
        const verifyResponse = await axios.get(`${this.baseUrl}/api/test-cases/${testCaseId}`);
        assert.strictEqual(verifyResponse.data.data.name, updateData.name, '更新后的数据不匹配');
        console.log('✅ 验证更新成功');
        
        // Delete - 删除数据
        const deleteResponse = await axios.delete(`${this.baseUrl}/api/test-cases/${testCaseId}`);
        assert.strictEqual(deleteResponse.status, 200, '删除数据失败');
        console.log('✅ 删除数据成功');
        
        // Verify deletion
        try {
            await axios.get(`${this.baseUrl}/api/test-cases/${testCaseId}`);
            throw new Error('删除后仍能查询到数据');
        } catch (error) {
            if (error.response && error.response.status === 404) {
                console.log('✅ 验证删除成功');
            } else {
                throw error;
            }
        }
    }
    
    async testTransactions() {
        console.log('🔄 测试事务处理...');
        
        // 创建多个相关数据，测试事务一致性
        const batchData = [
            { name: 'Batch Test 1', description: 'First batch item' },
            { name: 'Batch Test 2', description: 'Second batch item' },
            { name: 'Batch Test 3', description: 'Third batch item' }
        ];
        
        try {
            const promises = batchData.map(data => 
                axios.post(`${this.baseUrl}/api/test-cases`, {
                    ...data,
                    script_path: '/tmp/batch_test.js',
                    runtime_type: 'docker'
                })
            );
            
            const responses = await Promise.all(promises);
            
            responses.forEach(response => {
                assert.strictEqual(response.status, 201, '批量创建失败');
                this.testData.push(response.data.data.id);
            });
            
            console.log(`✅ 批量创建成功: ${responses.length} 条记录`);
            
        } catch (error) {
            console.error('❌ 批量操作失败:', error.message);
            throw error;
        }
    }
    
    async cleanup() {
        console.log('🧹 清理测试数据...');
        
        for (const id of this.testData) {
            try {
                await axios.delete(`${this.baseUrl}/api/test-cases/${id}`);
            } catch (error) {
                console.warn(`清理数据失败: ${id}`, error.message);
            }
        }
        
        console.log('✅ 测试数据清理完成');
    }
    
    async run() {
        console.log('🗄️ 开始数据库测试...');
        
        try {
            await this.testConnection();
            await this.testCRUDOperations();
            await this.testTransactions();
            
            console.log('🎉 数据库测试全部通过');
            return { success: true };
            
        } catch (error) {
            console.error('❌ 数据库测试失败:', error.message);
            throw error;
        } finally {
            await this.cleanup();
        }
    }
}

async function runTest() {
    const test = new DatabaseTest();
    return await test.run();
}

module.exports = runTest;
"""
        }
    
    def _generate_ui_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成UI测试模板"""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": "UI测试 - 验证用户界面功能和交互",
            "type": "ui",
            "runtime_type": "cypress",
            "tags": ["ui", "e2e", "frontend"],
            "config": {
                "browser": "chrome",
                "viewport": {"width": 1280, "height": 720},
                "video": True,
                "screenshots": True
            },
            "script_content": """
describe('UI功能测试', () => {
    beforeEach(() => {
        cy.visit('/');
    });
    
    it('应该正确加载主页', () => {
        cy.title().should('contain', 'AIOps');
        cy.get('[data-testid="main-content"]').should('be.visible');
    });
    
    it('应该能够导航到测试用例页面', () => {
        cy.get('[data-testid="nav-test-cases"]').click();
        cy.url().should('include', '/test-cases');
        cy.get('h1').should('contain', '测试用例');
    });
    
    it('应该能够创建新的测试用例', () => {
        cy.get('[data-testid="nav-test-cases"]').click();
        cy.get('[data-testid="create-test-case"]').click();
        
        // 填写表单
        cy.get('[data-testid="test-case-name"]').type('UI测试用例');
        cy.get('[data-testid="test-case-description"]').type('通过UI创建的测试用例');
        cy.get('[data-testid="runtime-type"]').select('docker');
        
        // 提交表单
        cy.get('[data-testid="submit-test-case"]').click();
        
        // 验证创建成功
        cy.get('[data-testid="success-message"]').should('be.visible');
        cy.get('[data-testid="test-case-list"]').should('contain', 'UI测试用例');
    });
    
    it('应该能够运行测试用例', () => {
        // 假设已有测试用例
        cy.get('[data-testid="nav-test-cases"]').click();
        cy.get('[data-testid="test-case-item"]').first().within(() => {
            cy.get('[data-testid="run-test"]').click();
        });
        
        // 验证运行状态
        cy.get('[data-testid="test-status"]').should('contain', '运行中');
        
        // 等待运行完成（最多30秒）
        cy.get('[data-testid="test-status"]', { timeout: 30000 })
          .should('not.contain', '运行中');
    });
    
    it('应该能够查看测试结果', () => {
        cy.get('[data-testid="nav-test-results"]').click();
        cy.url().should('include', '/results');
        
        // 检查结果列表
        cy.get('[data-testid="results-table"]').should('be.visible');
        cy.get('[data-testid="result-item"]').should('have.length.at.least', 1);
        
        // 查看详细结果
        cy.get('[data-testid="result-item"]').first().click();
        cy.get('[data-testid="result-details"]').should('be.visible');
    });
    
    it('应该响应式设计在移动设备上正常工作', () => {
        cy.viewport('iphone-6');
        
        // 检查移动端导航
        cy.get('[data-testid="mobile-menu-toggle"]').should('be.visible');
        cy.get('[data-testid="mobile-menu-toggle"]').click();
        cy.get('[data-testid="mobile-nav"]').should('be.visible');
        
        // 检查内容适配
        cy.get('[data-testid="main-content"]').should('be.visible');
    });
    
    it('应该处理错误状态', () => {
        // 模拟网络错误
        cy.intercept('GET', '/api/test-cases', { forceNetworkError: true });
        
        cy.get('[data-testid="nav-test-cases"]').click();
        cy.get('[data-testid="error-message"]').should('be.visible');
        cy.get('[data-testid="retry-button"]').should('be.visible');
    });
});
"""
        }
    
    def _generate_load_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成负载测试模板"""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": "负载测试 - 验证系统在高负载下的表现",
            "type": "load",
            "runtime_type": "k6",
            "tags": ["load", "performance", "stress"],
            "config": {
                "stages": [
                    {"duration": "2m", "target": 10},
                    {"duration": "5m", "target": 50},
                    {"duration": "2m", "target": 100},
                    {"duration": "5m", "target": 100},
                    {"duration": "2m", "target": 0}
                ]
            },
            "script_content": """
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export let options = {
    stages: [
        { duration: '2m', target: 10 },   // 预热
        { duration: '5m', target: 50 },   // 正常负载
        { duration: '2m', target: 100 },  // 峰值负载
        { duration: '5m', target: 100 },  // 持续峰值
        { duration: '2m', target: 0 },    // 冷却
    ],
    thresholds: {
        'http_req_duration': ['p(95)<1000', 'p(99)<2000'],
        'http_req_failed': ['rate<0.05'],
        'errors': ['rate<0.05']
    }
};

const baseUrl = __ENV.BASE_URL || 'http://localhost:3030';

export default function() {
    // 模拟用户行为序列
    const scenarios = [
        () => testHealthCheck(),
        () => testListTestCases(),
        () => testCreateTestCase(),
        () => testGetTestCase(),
        () => testRunTest()
    ];
    
    // 随机选择一个场景
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    scenario();
    
    // 用户思考时间
    sleep(Math.random() * 3 + 1);
}

function testHealthCheck() {
    const response = http.get(`${baseUrl}/api/health`);
    
    const result = check(response, {
        '健康检查状态码为200': (r) => r.status === 200,
        '健康检查响应时间<200ms': (r) => r.timings.duration < 200
    });
    
    errorRate.add(!result);
    responseTime.add(response.timings.duration);
}

function testListTestCases() {
    const response = http.get(`${baseUrl}/api/test-cases`);
    
    const result = check(response, {
        '列表查询状态码为200': (r) => r.status === 200,
        '列表查询响应时间<500ms': (r) => r.timings.duration < 500,
        '返回数据格式正确': (r) => {
            try {
                const data = JSON.parse(r.body);
                return data.hasOwnProperty('data');
            } catch (e) {
                return false;
            }
        }
    });
    
    errorRate.add(!result);
    responseTime.add(response.timings.duration);
}

function testCreateTestCase() {
    const payload = {
        name: `Load Test Case ${Math.random().toString(36).substr(2, 9)}`,
        description: 'Created during load test',
        script_path: '/tmp/load_test.js',
        runtime_type: 'docker'
    };
    
    const response = http.post(`${baseUrl}/api/test-cases`, JSON.stringify(payload), {
        headers: { 'Content-Type': 'application/json' }
    });
    
    const result = check(response, {
        '创建测试用例状态码为201': (r) => r.status === 201,
        '创建测试用例响应时间<1000ms': (r) => r.timings.duration < 1000
    });
    
    errorRate.add(!result);
    responseTime.add(response.timings.duration);
    
    return result ? JSON.parse(response.body).data.id : null;
}

function testGetTestCase() {
    // 假设系统中有测试用例，使用一个可能存在的ID
    const testCaseId = 1;
    const response = http.get(`${baseUrl}/api/test-cases/${testCaseId}`);
    
    const result = check(response, {
        '获取测试用例状态码正确': (r) => [200, 404].includes(r.status),
        '获取测试用例响应时间<300ms': (r) => r.timings.duration < 300
    });
    
    errorRate.add(!result);
    responseTime.add(response.timings.duration);
}

function testRunTest() {
    // 模拟运行测试的请求
    const testCaseId = 1;
    const response = http.post(`${baseUrl}/api/test-cases/${testCaseId}/run`, '{}', {
        headers: { 'Content-Type': 'application/json' }
    });
    
    const result = check(response, {
        '运行测试状态码正确': (r) => [200, 202, 404].includes(r.status),
        '运行测试响应时间<2000ms': (r) => r.timings.duration < 2000
    });
    
    errorRate.add(!result);
    responseTime.add(response.timings.duration);
}

export function handleSummary(data) {
    const avgResponseTime = data.metrics.http_req_duration.values.avg;
    const p95ResponseTime = data.metrics.http_req_duration.values['p(95)'];
    const p99ResponseTime = data.metrics.http_req_duration.values['p(99)'];
    const errorRate = data.metrics.http_req_failed.values.rate * 100;
    const totalRequests = data.metrics.http_reqs.values.count;
    
    return {
        'load_test_report.json': JSON.stringify(data, null, 2),
        stdout: `
负载测试完成报告
==================
总请求数: ${totalRequests}
平均响应时间: ${avgResponseTime.toFixed(2)}ms
95%响应时间: ${p95ResponseTime.toFixed(2)}ms
99%响应时间: ${p99ResponseTime.toFixed(2)}ms
错误率: ${errorRate.toFixed(2)}%

性能评估:
${avgResponseTime < 500 ? '✅' : '❌'} 平均响应时间 ${avgResponseTime < 500 ? '良好' : '需要优化'}
${p95ResponseTime < 1000 ? '✅' : '❌'} 95%响应时间 ${p95ResponseTime < 1000 ? '良好' : '需要优化'}
${errorRate < 5 ? '✅' : '❌'} 错误率 ${errorRate < 5 ? '良好' : '过高'}
`
    };
}
"""
        }
    
    def _generate_smoke_test_template(self, name: str, **kwargs) -> Dict[str, Any]:
        """生成冒烟测试模板"""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": "冒烟测试 - 验证系统基本功能正常",
            "type": "smoke",
            "runtime_type": "docker",
            "tags": ["smoke", "basic", "quick"],
            "config": {
                "timeout": 300,
                "critical_only": True
            },
            "script_content": """
const axios = require('axios');
const assert = require('assert');

class SmokeTest {
    constructor() {
        this.baseUrl = process.env.BASE_URL || 'http://localhost:3030';
        this.results = [];
    }
    
    async testSystemHealth() {
        console.log('🏥 检查系统健康状态...');
        
        try {
            const response = await axios.get(`${this.baseUrl}/api/health`, { timeout: 10000 });
            assert.strictEqual(response.status, 200, '健康检查失败');
            
            this.results.push({ test: '系统健康检查', status: 'PASS' });
            console.log('✅ 系统健康检查通过');
        } catch (error) {
            this.results.push({ test: '系统健康检查', status: 'FAIL', error: error.message });
            throw new Error(`系统健康检查失败: ${error.message}`);
        }
    }
    
    async testDatabaseConnection() {
        console.log('🗄️ 检查数据库连接...');
        
        try {
            const response = await axios.get(`${this.baseUrl}/api/health/database`, { timeout: 10000 });
            assert.strictEqual(response.status, 200, '数据库连接失败');
            
            this.results.push({ test: '数据库连接', status: 'PASS' });
            console.log('✅ 数据库连接正常');
        } catch (error) {
            this.results.push({ test: '数据库连接', status: 'FAIL', error: error.message });
            throw new Error(`数据库连接失败: ${error.message}`);
        }
    }
    
    async testCoreAPI() {
        console.log('🔌 检查核心API...');
        
        const coreEndpoints = [
            { path: '/api/test-cases', method: 'GET', name: '测试用例列表' },
            { path: '/api/runtime-managers', method: 'GET', name: '运行时管理器列表' },
            { path: '/api/test-results', method: 'GET', name: '测试结果列表' }
        ];
        
        for (const endpoint of coreEndpoints) {
            try {
                const response = await axios({
                    method: endpoint.method,
                    url: `${this.baseUrl}${endpoint.path}`,
                    timeout: 10000
                });
                
                assert(response.status >= 200 && response.status < 300, 
                      `${endpoint.name} 返回错误状态码: ${response.status}`);
                
                this.results.push({ test: endpoint.name, status: 'PASS' });
                console.log(`✅ ${endpoint.name} 正常`);
                
            } catch (error) {
                this.results.push({ 
                    test: endpoint.name, 
                    status: 'FAIL', 
                    error: error.message 
                });
                console.error(`❌ ${endpoint.name} 失败: ${error.message}`);
            }
        }
    }
    
    async testStaticResources() {
        console.log('📁 检查静态资源...');
        
        try {
            const response = await axios.get(`${this.baseUrl}/`, { timeout: 10000 });
            assert.strictEqual(response.status, 200, '主页加载失败');
            assert(response.data.includes('html'), '主页内容格式错误');
            
            this.results.push({ test: '静态资源加载', status: 'PASS' });
            console.log('✅ 静态资源加载正常');
        } catch (error) {
            this.results.push({ test: '静态资源加载', status: 'FAIL', error: error.message });
            console.error(`❌ 静态资源加载失败: ${error.message}`);
        }
    }
    
    async testBasicCRUD() {
        console.log('📝 检查基本CRUD操作...');
        
        let testCaseId = null;
        
        try {
            // Create
            const createData = {
                name: `Smoke Test ${Date.now()}`,
                description: 'Smoke test case',
                script_path: '/tmp/smoke_test.js',
                runtime_type: 'docker'
            };
            
            const createResponse = await axios.post(`${this.baseUrl}/api/test-cases`, createData);
            assert.strictEqual(createResponse.status, 201, '创建操作失败');
            testCaseId = createResponse.data.data.id;
            
            // Read
            const readResponse = await axios.get(`${this.baseUrl}/api/test-cases/${testCaseId}`);
            assert.strictEqual(readResponse.status, 200, '读取操作失败');
            
            // Update
            const updateData = { name: `Updated ${createData.name}` };
            const updateResponse = await axios.put(`${this.baseUrl}/api/test-cases/${testCaseId}`, updateData);
            assert.strictEqual(updateResponse.status, 200, '更新操作失败');
            
            // Delete
            const deleteResponse = await axios.delete(`${this.baseUrl}/api/test-cases/${testCaseId}`);
            assert.strictEqual(deleteResponse.status, 200, '删除操作失败');
            
            this.results.push({ test: '基本CRUD操作', status: 'PASS' });
            console.log('✅ 基本CRUD操作正常');
            
        } catch (error) {
            this.results.push({ test: '基本CRUD操作', status: 'FAIL', error: error.message });
            console.error(`❌ 基本CRUD操作失败: ${error.message}`);
            
            // 清理可能创建的数据
            if (testCaseId) {
                try {
                    await axios.delete(`${this.baseUrl}/api/test-cases/${testCaseId}`);
                } catch (cleanupError) {
                    console.warn('清理测试数据失败:', cleanupError.message);
                }
            }
        }
    }
    
    async run() {
        console.log('💨 开始冒烟测试...');
        
        const startTime = Date.now();
        
        try {
            await this.testSystemHealth();
            await this.testDatabaseConnection();
            await this.testCoreAPI();
            await this.testStaticResources();
            await this.testBasicCRUD();
            
            const duration = Date.now() - startTime;
            const passedTests = this.results.filter(r => r.status === 'PASS').length;
            const failedTests = this.results.filter(r => r.status === 'FAIL').length;
            
            console.log('\n📊 冒烟测试完成');
            console.log(`执行时间: ${duration}ms`);
            console.log(`通过: ${passedTests} 个`);
            console.log(`失败: ${failedTests} 个`);
            
            if (failedTests > 0) {
                console.log('\n❌ 失败的测试:');
                this.results.filter(r => r.status === 'FAIL').forEach(result => {
                    console.log(`  - ${result.test}: ${result.error}`);
                });
            }
            
            return {
                success: failedTests === 0,
                duration,
                results: this.results,
                summary: {
                    total: this.results.length,
                    passed: passedTests,
                    failed: failedTests
                }
            };
            
        } catch (error) {
            console.error('❌ 冒烟测试中断:', error.message);
            throw error;
        }
    }
}

async function runTest() {
    const test = new SmokeTest();
    return await test.run();
}

module.exports = runTest;
"""
        }
    
    def generate_test_scenario(self, test_type: str, name: str, **kwargs) -> Dict[str, Any]:
        """
        生成指定类型的测试场景
        
        Args:
            test_type: 测试类型
            name: 测试名称
            **kwargs: 额外参数
            
        Returns:
            Dict[str, Any]: 生成的测试场景
        """
        if test_type not in self.templates:
            raise ValueError(f"不支持的测试类型: {test_type}。支持的类型: {list(self.templates.keys())}")
        
        return self.templates[test_type](name, **kwargs)
    
    def generate_test_suite(self, suite_name: str, test_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        生成测试套件
        
        Args:
            suite_name: 套件名称
            test_configs: 测试配置列表
            
        Returns:
            Dict[str, Any]: 测试套件配置
        """
        test_cases = []
        
        for config in test_configs:
            test_type = config.get('type')
            test_name = config.get('name')
            test_params = {k: v for k, v in config.items() if k not in ['type', 'name']}
            
            if test_type and test_name:
                test_case = self.generate_test_scenario(test_type, test_name, **test_params)
                test_cases.append(test_case)
        
        return {
            "suite_name": suite_name,
            "created_at": datetime.now().isoformat(),
            "test_cases": test_cases,
            "metadata": {
                "total_tests": len(test_cases),
                "test_types": list(set(tc['type'] for tc in test_cases)),
                "estimated_duration": self._estimate_suite_duration(test_cases)
            }
        }
    
    def _estimate_suite_duration(self, test_cases: List[Dict[str, Any]]) -> str:
        """
        估算测试套件执行时间
        
        Args:
            test_cases: 测试用例列表
            
        Returns:
            str: 估算时间描述
        """
        duration_map = {
            'api': 30,
            'performance': 300,
            'integration': 180,
            'security': 240,
            'database': 120,
            'ui': 180,
            'load': 600,
            'smoke': 60
        }
        
        total_seconds = sum(duration_map.get(tc['type'], 60) for tc in test_cases)
        
        if total_seconds < 60:
            return f"{total_seconds}秒"
        elif total_seconds < 3600:
            return f"{total_seconds // 60}分钟"
        else:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{hours}小时{minutes}分钟"
    
    def save_to_file(self, data: Dict[str, Any], file_path: str) -> None:
        """
        保存数据到文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 已保存到: {file_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AIOps测试场景生成器')
    parser.add_argument('--type', '-t', 
                       choices=['api', 'performance', 'integration', 'security', 
                               'database', 'ui', 'load', 'smoke'],
                       help='测试类型')
    parser.add_argument('--name', '-n', help='测试名称')
    parser.add_argument('--suite', '-s', help='生成测试套件（JSON配置文件路径）')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--list-types', '-l', action='store_true', help='列出所有支持的测试类型')
    
    # 测试特定参数
    parser.add_argument('--endpoint', help='API端点（用于API测试）')
    parser.add_argument('--method', help='HTTP方法（用于API测试）')
    parser.add_argument('--duration', type=int, help='测试持续时间（秒）')
    parser.add_argument('--concurrent-users', type=int, help='并发用户数')
    parser.add_argument('--services', nargs='+', help='服务列表（用于集成测试）')
    
    args = parser.parse_args()
    
    generator = TestScenarioGenerator()
    
    if args.list_types:
        print("支持的测试类型:")
        for test_type in generator.templates.keys():
            print(f"  - {test_type}")
        return
    
    if args.suite:
        # 生成测试套件
        try:
            with open(args.suite, 'r', encoding='utf-8') as f:
                suite_config = json.load(f)
            
            suite_name = suite_config.get('name', 'Generated Test Suite')
            test_configs = suite_config.get('tests', [])
            
            suite = generator.generate_test_suite(suite_name, test_configs)
            
            output_file = args.output or f"{suite_name.replace(' ', '_').lower()}_suite.json"
            generator.save_to_file(suite, output_file)
            
            print(f"\n📦 测试套件生成完成:")
            print(f"  名称: {suite['suite_name']}")
            print(f"  测试数量: {suite['metadata']['total_tests']}")
            print(f"  测试类型: {', '.join(suite['metadata']['test_types'])}")
            print(f"  预计时长: {suite['metadata']['estimated_duration']}")
            
        except Exception as e:
            print(f"❌ 生成测试套件失败: {e}")
            sys.exit(1)
    
    elif args.type and args.name:
        # 生成单个测试场景
        try:
            kwargs = {}
            if args.endpoint:
                kwargs['endpoint'] = args.endpoint
            if args.method:
                kwargs['method'] = args.method
            if args.duration:
                kwargs['duration'] = args.duration
            if args.concurrent_users:
                kwargs['concurrent_users'] = args.concurrent_users
            if args.services:
                kwargs['services'] = args.services
            
            test_scenario = generator.generate_test_scenario(args.type, args.name, **kwargs)
            
            output_file = args.output or f"{args.name.replace(' ', '_').lower()}_{args.type}_test.json"
            generator.save_to_file(test_scenario, output_file)
            
            print(f"\n🎯 测试场景生成完成:")
            print(f"  名称: {test_scenario['name']}")
            print(f"  类型: {test_scenario['type']}")
            print(f"  运行时: {test_scenario['runtime_type']}")
            print(f"  标签: {', '.join(test_scenario['tags'])}")
            
        except Exception as e:
            print(f"❌ 生成测试场景失败: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()
        print("\n示例用法:")
        print("  生成API测试: python test_scenario_generator.py -t api -n \"用户登录API测试\" --endpoint /api/login --method POST")
        print("  生成性能测试: python test_scenario_generator.py -t performance -n \"系统负载测试\" --duration 300 --concurrent-users 50")
        print("  生成测试套件: python test_scenario_generator.py -s suite_config.json -o my_test_suite.json")

if __name__ == '__main__':
    main()