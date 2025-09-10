#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微服务生态系统模拟器
模拟复杂的微服务架构，包括服务间调用、负载均衡、故障传播等
支持服务发现、熔断器、重试机制等微服务模式
"""

import argparse
import json
import random
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
import os
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import uuid

class ServiceStatus(Enum):
    """服务状态枚举"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    DOWN = "down"

class RequestStatus(Enum):
    """请求状态枚举"""
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ERROR = "error"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    RATE_LIMITED = "rate_limited"

class ServiceType(Enum):
    """服务类型枚举"""
    GATEWAY = "gateway"
    WEB = "web"
    API = "api"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    AUTH = "auth"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    ANALYTICS = "analytics"

@dataclass
class ServiceMetrics:
    """服务指标数据类"""
    request_count: int = 0
    success_count: int = 0
    error_count: int = 0
    timeout_count: int = 0
    total_response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_connections: int = 0
    queue_size: int = 0
    circuit_breaker_state: str = "closed"
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ServiceDependency:
    """服务依赖关系数据类"""
    target_service: str
    dependency_type: str  # sync, async, optional
    timeout: float = 5.0
    retry_count: int = 3
    circuit_breaker_threshold: int = 5

@dataclass
class Request:
    """请求数据类"""
    id: str
    source_service: str
    target_service: str
    endpoint: str
    method: str
    timestamp: datetime
    response_time: Optional[float] = None
    status: Optional[RequestStatus] = None
    error_message: Optional[str] = None
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class CircuitBreaker:
    """熔断器实现"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        """执行函数调用，应用熔断逻辑"""
        if self.state == "open":
            if self.last_failure_time and \
               (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout:
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            
            raise e

class MicroService:
    """微服务类"""
    
    def __init__(self, name: str, service_type: ServiceType, port: int, 
                 dependencies: List[ServiceDependency] = None):
        self.name = name
        self.service_type = service_type
        self.port = port
        self.status = ServiceStatus.HEALTHY
        self.dependencies = dependencies or []
        self.metrics = ServiceMetrics()
        self.circuit_breakers = {}
        self.request_history = deque(maxlen=1000)
        self.failure_scenarios = []
        self.load_factor = 1.0
        self.version = "1.0.0"
        self.instance_id = str(uuid.uuid4())
        
        # 为每个依赖创建熔断器
        for dep in self.dependencies:
            self.circuit_breakers[dep.target_service] = CircuitBreaker(
                failure_threshold=dep.circuit_breaker_threshold
            )
    
    def process_request(self, request: Request) -> Request:
        """处理请求"""
        start_time = time.time()
        
        try:
            # 检查服务状态
            if self.status == ServiceStatus.DOWN:
                request.status = RequestStatus.ERROR
                request.error_message = "Service is down"
                return request
            
            # 模拟处理时间
            base_response_time = self._get_base_response_time(request.endpoint)
            actual_response_time = base_response_time * self.load_factor
            
            # 添加随机延迟
            if self.status == ServiceStatus.DEGRADED:
                actual_response_time *= random.uniform(2, 5)
            
            # 模拟故障
            if self._should_fail():
                request.status = RequestStatus.ERROR
                request.error_message = "Internal server error"
                self.metrics.error_count += 1
            else:
                time.sleep(actual_response_time / 1000)  # 转换为秒
                request.status = RequestStatus.SUCCESS
                self.metrics.success_count += 1
            
            request.response_time = actual_response_time
            
        except Exception as e:
            request.status = RequestStatus.ERROR
            request.error_message = str(e)
            self.metrics.error_count += 1
        
        finally:
            self.metrics.request_count += 1
            self.metrics.total_response_time += time.time() - start_time
            self.request_history.append(request)
            self._update_metrics()
        
        return request
    
    def call_dependency(self, target_service: str, endpoint: str, method: str = "GET") -> Request:
        """调用依赖服务"""
        dependency = next((dep for dep in self.dependencies if dep.target_service == target_service), None)
        if not dependency:
            raise ValueError(f"No dependency found for service: {target_service}")
        
        request = Request(
            id=str(uuid.uuid4()),
            source_service=self.name,
            target_service=target_service,
            endpoint=endpoint,
            method=method,
            timestamp=datetime.now()
        )
        
        circuit_breaker = self.circuit_breakers.get(target_service)
        
        try:
            if circuit_breaker:
                # 使用熔断器调用
                result = circuit_breaker.call(self._make_service_call, request, dependency)
            else:
                result = self._make_service_call(request, dependency)
            
            return result
            
        except Exception as e:
            request.status = RequestStatus.CIRCUIT_BREAKER_OPEN if "Circuit breaker" in str(e) else RequestStatus.ERROR
            request.error_message = str(e)
            return request
    
    def _make_service_call(self, request: Request, dependency: ServiceDependency) -> Request:
        """实际的服务调用"""
        # 模拟网络延迟
        network_delay = random.uniform(1, 10)
        time.sleep(network_delay / 1000)
        
        # 模拟超时
        if random.random() < 0.05:  # 5%概率超时
            request.status = RequestStatus.TIMEOUT
            request.error_message = "Request timeout"
            raise Exception("Request timeout")
        
        # 模拟错误
        if random.random() < 0.02:  # 2%概率错误
            request.status = RequestStatus.ERROR
            request.error_message = "Service unavailable"
            raise Exception("Service unavailable")
        
        request.status = RequestStatus.SUCCESS
        request.response_time = network_delay + random.uniform(10, 100)
        return request
    
    def _get_base_response_time(self, endpoint: str) -> float:
        """获取基础响应时间"""
        response_times = {
            "/health": 5,
            "/api/users": 50,
            "/api/orders": 100,
            "/api/products": 75,
            "/api/payments": 200,
            "/api/notifications": 30,
            "/api/analytics": 500
        }
        return response_times.get(endpoint, 100)
    
    def _should_fail(self) -> bool:
        """判断是否应该失败"""
        base_failure_rate = {
            ServiceStatus.HEALTHY: 0.01,
            ServiceStatus.DEGRADED: 0.05,
            ServiceStatus.UNHEALTHY: 0.15,
            ServiceStatus.DOWN: 1.0
        }
        
        failure_rate = base_failure_rate[self.status]
        
        # 应用故障场景
        for scenario in self.failure_scenarios:
            if scenario.get('active', False):
                failure_rate += scenario.get('additional_failure_rate', 0)
        
        return random.random() < failure_rate
    
    def _update_metrics(self):
        """更新服务指标"""
        # 模拟CPU和内存使用率
        base_cpu = {
            ServiceType.GATEWAY: 30,
            ServiceType.WEB: 25,
            ServiceType.API: 40,
            ServiceType.DATABASE: 60,
            ServiceType.CACHE: 20,
            ServiceType.MESSAGE_QUEUE: 35
        }.get(self.service_type, 30)
        
        self.metrics.cpu_usage = min(100, base_cpu * self.load_factor + random.uniform(-10, 10))
        self.metrics.memory_usage = min(100, base_cpu * 0.8 * self.load_factor + random.uniform(-5, 15))
        self.metrics.active_connections = max(0, int(self.metrics.request_count * 0.1 + random.uniform(-5, 5)))
        self.metrics.queue_size = max(0, int(self.load_factor * 10 + random.uniform(-3, 7)))
        self.metrics.last_updated = datetime.now()
    
    def inject_failure(self, scenario: Dict[str, Any]):
        """注入故障场景"""
        self.failure_scenarios.append(scenario)
    
    def set_load_factor(self, factor: float):
        """设置负载因子"""
        self.load_factor = factor
    
    def get_health_status(self) -> Dict[str, Any]:
        """获取健康状态"""
        return {
            'service': self.name,
            'status': self.status.value,
            'version': self.version,
            'instance_id': self.instance_id,
            'metrics': {
                'request_count': self.metrics.request_count,
                'success_rate': self.metrics.success_count / max(1, self.metrics.request_count),
                'error_rate': self.metrics.error_count / max(1, self.metrics.request_count),
                'avg_response_time': self.metrics.total_response_time / max(1, self.metrics.request_count) * 1000,
                'cpu_usage': self.metrics.cpu_usage,
                'memory_usage': self.metrics.memory_usage,
                'active_connections': self.metrics.active_connections,
                'queue_size': self.metrics.queue_size
            },
            'dependencies': [{
                'service': dep.target_service,
                'circuit_breaker_state': self.circuit_breakers.get(dep.target_service, {}).state if dep.target_service in self.circuit_breakers else 'closed'
            } for dep in self.dependencies],
            'timestamp': datetime.now().isoformat()
        }

class MicroservicesEcosystem:
    """微服务生态系统模拟器"""
    
    def __init__(self):
        self.services = {}
        self.service_registry = {}
        self.load_balancer = {}
        self.request_logs = []
        self.metrics_history = defaultdict(list)
        self.running = False
        self.simulation_thread = None
        
        # 初始化服务
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化微服务"""
        # API网关
        gateway = MicroService(
            name="api-gateway",
            service_type=ServiceType.GATEWAY,
            port=8080,
            dependencies=[
                ServiceDependency("user-service", "sync", timeout=5.0),
                ServiceDependency("order-service", "sync", timeout=5.0),
                ServiceDependency("product-service", "sync", timeout=5.0),
                ServiceDependency("auth-service", "sync", timeout=3.0)
            ]
        )
        
        # 用户服务
        user_service = MicroService(
            name="user-service",
            service_type=ServiceType.API,
            port=8081,
            dependencies=[
                ServiceDependency("user-db", "sync", timeout=2.0),
                ServiceDependency("cache-service", "sync", timeout=1.0),
                ServiceDependency("notification-service", "async", timeout=10.0)
            ]
        )
        
        # 订单服务
        order_service = MicroService(
            name="order-service",
            service_type=ServiceType.API,
            port=8082,
            dependencies=[
                ServiceDependency("order-db", "sync", timeout=2.0),
                ServiceDependency("payment-service", "sync", timeout=10.0),
                ServiceDependency("product-service", "sync", timeout=5.0),
                ServiceDependency("notification-service", "async", timeout=10.0)
            ]
        )
        
        # 产品服务
        product_service = MicroService(
            name="product-service",
            service_type=ServiceType.API,
            port=8083,
            dependencies=[
                ServiceDependency("product-db", "sync", timeout=2.0),
                ServiceDependency("cache-service", "sync", timeout=1.0)
            ]
        )
        
        # 认证服务
        auth_service = MicroService(
            name="auth-service",
            service_type=ServiceType.AUTH,
            port=8084,
            dependencies=[
                ServiceDependency("auth-db", "sync", timeout=2.0),
                ServiceDependency("cache-service", "sync", timeout=1.0)
            ]
        )
        
        # 支付服务
        payment_service = MicroService(
            name="payment-service",
            service_type=ServiceType.PAYMENT,
            port=8085,
            dependencies=[
                ServiceDependency("payment-db", "sync", timeout=2.0),
                ServiceDependency("notification-service", "async", timeout=10.0)
            ]
        )
        
        # 通知服务
        notification_service = MicroService(
            name="notification-service",
            service_type=ServiceType.NOTIFICATION,
            port=8086,
            dependencies=[
                ServiceDependency("message-queue", "async", timeout=5.0)
            ]
        )
        
        # 数据库服务
        user_db = MicroService("user-db", ServiceType.DATABASE, 5432)
        order_db = MicroService("order-db", ServiceType.DATABASE, 5433)
        product_db = MicroService("product-db", ServiceType.DATABASE, 5434)
        auth_db = MicroService("auth-db", ServiceType.DATABASE, 5435)
        payment_db = MicroService("payment-db", ServiceType.DATABASE, 5436)
        
        # 缓存服务
        cache_service = MicroService("cache-service", ServiceType.CACHE, 6379)
        
        # 消息队列
        message_queue = MicroService("message-queue", ServiceType.MESSAGE_QUEUE, 5672)
        
        # 分析服务
        analytics_service = MicroService(
            name="analytics-service",
            service_type=ServiceType.ANALYTICS,
            port=8087,
            dependencies=[
                ServiceDependency("analytics-db", "sync", timeout=5.0),
                ServiceDependency("message-queue", "async", timeout=5.0)
            ]
        )
        
        analytics_db = MicroService("analytics-db", ServiceType.DATABASE, 5437)
        
        # 注册所有服务
        services = [
            gateway, user_service, order_service, product_service, auth_service,
            payment_service, notification_service, analytics_service,
            user_db, order_db, product_db, auth_db, payment_db, analytics_db,
            cache_service, message_queue
        ]
        
        for service in services:
            self.services[service.name] = service
            self.service_registry[service.name] = {
                'host': 'localhost',
                'port': service.port,
                'status': service.status.value,
                'type': service.service_type.value
            }
    
    def start_simulation(self, duration: int = 3600, request_rate: int = 100):
        """启动模拟"""
        print(f"🚀 启动微服务生态系统模拟")
        print(f"服务数量: {len(self.services)}")
        print(f"模拟时长: {duration}秒")
        print(f"请求频率: {request_rate}请求/分钟")
        
        self.running = True
        self.simulation_thread = threading.Thread(
            target=self._run_simulation,
            args=(duration, request_rate)
        )
        self.simulation_thread.start()
    
    def _run_simulation(self, duration: int, request_rate: int):
        """运行模拟"""
        start_time = time.time()
        request_interval = 60.0 / request_rate  # 请求间隔
        
        while self.running and (time.time() - start_time) < duration:
            try:
                # 生成随机请求
                self._generate_random_request()
                
                # 更新服务指标
                self._update_all_metrics()
                
                # 应用负载变化
                self._apply_load_variations()
                
                # 检查故障场景
                self._check_failure_scenarios()
                
                time.sleep(request_interval)
                
            except Exception as e:
                print(f"模拟过程中出现错误: {e}")
                continue
        
        print("✅ 微服务生态系统模拟完成")
    
    def _generate_random_request(self):
        """生成随机请求"""
        # 选择入口服务（通常是API网关）
        entry_services = ["api-gateway"]
        source_service = random.choice(entry_services)
        
        # 选择目标端点
        endpoints = [
            "/api/users", "/api/users/{id}", "/api/orders", "/api/orders/{id}",
            "/api/products", "/api/products/{id}", "/api/auth/login", "/api/auth/logout",
            "/api/payments", "/health"
        ]
        endpoint = random.choice(endpoints)
        
        # 选择HTTP方法
        methods = ["GET", "POST", "PUT", "DELETE"]
        method = random.choice(methods)
        
        # 创建请求
        request = Request(
            id=str(uuid.uuid4()),
            source_service="client",
            target_service=source_service,
            endpoint=endpoint,
            method=method,
            timestamp=datetime.now()
        )
        
        # 处理请求
        self._process_request_chain(request)
    
    def _process_request_chain(self, request: Request):
        """处理请求链"""
        current_service = self.services.get(request.target_service)
        if not current_service:
            return
        
        # 处理当前服务的请求
        processed_request = current_service.process_request(request)
        self.request_logs.append(processed_request)
        
        # 如果请求成功，可能需要调用依赖服务
        if processed_request.status == RequestStatus.SUCCESS:
            self._handle_service_dependencies(current_service, request.endpoint)
    
    def _handle_service_dependencies(self, service: MicroService, endpoint: str):
        """处理服务依赖"""
        # 根据端点确定需要调用的依赖服务
        dependency_map = {
            "/api/users": ["user-service"],
            "/api/orders": ["order-service"],
            "/api/products": ["product-service"],
            "/api/auth/login": ["auth-service"],
            "/api/payments": ["payment-service"]
        }
        
        required_services = dependency_map.get(endpoint, [])
        
        for target_service in required_services:
            if target_service in [dep.target_service for dep in service.dependencies]:
                try:
                    dep_request = service.call_dependency(target_service, endpoint)
                    self.request_logs.append(dep_request)
                    
                    # 递归处理依赖服务的依赖
                    if dep_request.status == RequestStatus.SUCCESS:
                        dep_service = self.services.get(target_service)
                        if dep_service:
                            self._handle_service_dependencies(dep_service, endpoint)
                            
                except Exception as e:
                    print(f"调用依赖服务 {target_service} 失败: {e}")
    
    def _update_all_metrics(self):
        """更新所有服务指标"""
        current_time = datetime.now()
        
        for service_name, service in self.services.items():
            health_status = service.get_health_status()
            self.metrics_history[service_name].append({
                'timestamp': current_time.isoformat(),
                'metrics': health_status['metrics']
            })
            
            # 保持历史记录在合理范围内
            if len(self.metrics_history[service_name]) > 1000:
                self.metrics_history[service_name] = self.metrics_history[service_name][-1000:]
    
    def _apply_load_variations(self):
        """应用负载变化"""
        current_hour = datetime.now().hour
        
        # 模拟一天中的负载变化
        if 6 <= current_hour <= 9:  # 早高峰
            load_factor = random.uniform(1.2, 1.5)
        elif 10 <= current_hour <= 16:  # 工作时间
            load_factor = random.uniform(1.0, 1.3)
        elif 17 <= current_hour <= 20:  # 晚高峰
            load_factor = random.uniform(1.3, 1.6)
        elif 21 <= current_hour <= 23:  # 晚间
            load_factor = random.uniform(0.8, 1.1)
        else:  # 夜间
            load_factor = random.uniform(0.3, 0.7)
        
        # 应用负载因子到所有服务
        for service in self.services.values():
            service.set_load_factor(load_factor)
    
    def _check_failure_scenarios(self):
        """检查并应用故障场景"""
        # 随机故障注入
        if random.random() < 0.001:  # 0.1%概率注入故障
            service_name = random.choice(list(self.services.keys()))
            service = self.services[service_name]
            
            failure_types = [
                {'type': 'high_latency', 'duration': 300, 'additional_failure_rate': 0.1},
                {'type': 'memory_leak', 'duration': 600, 'additional_failure_rate': 0.05},
                {'type': 'cpu_spike', 'duration': 180, 'additional_failure_rate': 0.02},
                {'type': 'network_partition', 'duration': 120, 'additional_failure_rate': 0.3}
            ]
            
            failure_scenario = random.choice(failure_types)
            failure_scenario['active'] = True
            failure_scenario['start_time'] = datetime.now()
            
            service.inject_failure(failure_scenario)
            print(f"💥 故障注入: {service_name} - {failure_scenario['type']}")
    
    def inject_chaos(self, service_name: str, chaos_type: str, duration: int = 300):
        """注入混沌工程故障"""
        if service_name not in self.services:
            raise ValueError(f"Service {service_name} not found")
        
        service = self.services[service_name]
        
        chaos_scenarios = {
            'kill_service': {
                'type': 'kill_service',
                'duration': duration,
                'additional_failure_rate': 1.0,
                'active': True,
                'start_time': datetime.now()
            },
            'network_delay': {
                'type': 'network_delay',
                'duration': duration,
                'additional_failure_rate': 0.0,
                'network_delay_ms': random.uniform(1000, 5000),
                'active': True,
                'start_time': datetime.now()
            },
            'memory_pressure': {
                'type': 'memory_pressure',
                'duration': duration,
                'additional_failure_rate': 0.1,
                'memory_usage_increase': 50,
                'active': True,
                'start_time': datetime.now()
            },
            'cpu_stress': {
                'type': 'cpu_stress',
                'duration': duration,
                'additional_failure_rate': 0.05,
                'cpu_usage_increase': 70,
                'active': True,
                'start_time': datetime.now()
            }
        }
        
        if chaos_type not in chaos_scenarios:
            raise ValueError(f"Unknown chaos type: {chaos_type}")
        
        scenario = chaos_scenarios[chaos_type]
        service.inject_failure(scenario)
        
        print(f"🌪️ 混沌工程: 对 {service_name} 注入 {chaos_type} 故障，持续 {duration} 秒")
    
    def get_system_health(self) -> Dict[str, Any]:
        """获取系统整体健康状态"""
        total_services = len(self.services)
        healthy_services = sum(1 for s in self.services.values() if s.status == ServiceStatus.HEALTHY)
        
        total_requests = sum(len(s.request_history) for s in self.services.values())
        total_errors = sum(s.metrics.error_count for s in self.services.values())
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_services': total_services,
            'healthy_services': healthy_services,
            'service_health_rate': healthy_services / total_services if total_services > 0 else 0,
            'total_requests': total_requests,
            'total_errors': total_errors,
            'system_error_rate': total_errors / total_requests if total_requests > 0 else 0,
            'services': {name: service.get_health_status() for name, service in self.services.items()}
        }
    
    def export_metrics(self, export_dir: str = "./microservices_data"):
        """导出指标数据"""
        os.makedirs(export_dir, exist_ok=True)
        
        # 导出系统健康状态
        system_health = self.get_system_health()
        with open(f"{export_dir}/system_health.json", 'w', encoding='utf-8') as f:
            json.dump(system_health, f, indent=2, ensure_ascii=False)
        
        # 导出请求日志
        request_logs = [{
            'id': req.id,
            'source_service': req.source_service,
            'target_service': req.target_service,
            'endpoint': req.endpoint,
            'method': req.method,
            'timestamp': req.timestamp.isoformat(),
            'response_time': req.response_time,
            'status': req.status.value if req.status else None,
            'error_message': req.error_message,
            'trace_id': req.trace_id
        } for req in self.request_logs]
        
        with open(f"{export_dir}/request_logs.json", 'w', encoding='utf-8') as f:
            json.dump(request_logs, f, indent=2, ensure_ascii=False)
        
        # 导出指标历史
        with open(f"{export_dir}/metrics_history.json", 'w', encoding='utf-8') as f:
            json.dump(dict(self.metrics_history), f, indent=2, ensure_ascii=False)
        
        # 导出服务拓扑
        topology = {
            'services': {},
            'dependencies': []
        }
        
        for service_name, service in self.services.items():
            topology['services'][service_name] = {
                'name': service.name,
                'type': service.service_type.value,
                'port': service.port,
                'status': service.status.value
            }
            
            for dep in service.dependencies:
                topology['dependencies'].append({
                    'source': service_name,
                    'target': dep.target_service,
                    'type': dep.dependency_type,
                    'timeout': dep.timeout
                })
        
        with open(f"{export_dir}/service_topology.json", 'w', encoding='utf-8') as f:
            json.dump(topology, f, indent=2, ensure_ascii=False)
        
        print(f"📊 微服务指标已导出到: {export_dir}")
        print(f"  - 系统健康状态: system_health.json")
        print(f"  - 请求日志: request_logs.json ({len(request_logs)} 条记录)")
        print(f"  - 指标历史: metrics_history.json")
        print(f"  - 服务拓扑: service_topology.json")
    
    def stop_simulation(self):
        """停止模拟"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join()
        print("🛑 微服务生态系统模拟已停止")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='微服务生态系统模拟器')
    parser.add_argument('--duration', type=int, default=3600, help='模拟时长(秒)')
    parser.add_argument('--request-rate', type=int, default=100, help='请求频率(请求/分钟)')
    parser.add_argument('--export-dir', type=str, default='./microservices_data', help='导出目录')
    parser.add_argument('--chaos', type=str, help='混沌工程故障类型')
    parser.add_argument('--chaos-target', type=str, help='混沌工程目标服务')
    parser.add_argument('--chaos-duration', type=int, default=300, help='混沌工程持续时间(秒)')
    
    args = parser.parse_args()
    
    ecosystem = MicroservicesEcosystem()
    
    try:
        # 启动模拟
        ecosystem.start_simulation(duration=args.duration, request_rate=args.request_rate)
        
        # 如果指定了混沌工程参数，注入故障
        if args.chaos and args.chaos_target:
            time.sleep(60)  # 等待系统稳定
            ecosystem.inject_chaos(args.chaos_target, args.chaos, args.chaos_duration)
        
        # 等待模拟完成
        if ecosystem.simulation_thread:
            ecosystem.simulation_thread.join()
        
    except KeyboardInterrupt:
        print("\n收到中断信号，正在停止模拟...")
        ecosystem.stop_simulation()
    
    finally:
        # 导出结果
        ecosystem.export_metrics(export_dir=args.export_dir)

if __name__ == '__main__':
    main()