#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web应用模拟器

该模块提供了一个模拟的Web应用程序，用于生成真实的HTTP请求和响应数据，
以便测试监控系统的各项功能。

Author: AIOps Team
Date: 2025-01-10
"""

import json
import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, render_template_string
import requests
import logging
from dataclasses import dataclass


@dataclass
class RequestMetrics:
    """请求指标数据类"""
    timestamp: datetime
    method: str
    endpoint: str
    status_code: int
    response_time_ms: float
    request_size_bytes: int
    response_size_bytes: int
    user_agent: str
    client_ip: str


class WebSimulator:
    """Web应用模拟器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化Web模拟器
        
        Args:
            config: 配置字典
        """
        self.config = config or self._get_default_config()
        self.app = Flask(__name__)
        self.metrics = []
        self.running = False
        self.load_generator_thread = None
        self.logger = self._setup_logger()
        
        # 设置路由
        self._setup_routes()
        
        # 模拟用户数据
        self.users = self._generate_mock_users()
        self.products = self._generate_mock_products()
        
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False,
            "load_generation": {
                "enabled": True,
                "base_rps": 10,
                "peak_rps": 50,
                "peak_hours": [9, 10, 11, 14, 15, 16, 20, 21],
                "error_rate": 0.02,
                "slow_response_rate": 0.05
            },
            "endpoints": {
                "/": {"weight": 20, "avg_response_ms": 100},
                "/api/users": {"weight": 15, "avg_response_ms": 150},
                "/api/products": {"weight": 25, "avg_response_ms": 120},
                "/api/orders": {"weight": 10, "avg_response_ms": 200},
                "/api/search": {"weight": 20, "avg_response_ms": 300},
                "/api/analytics": {"weight": 5, "avg_response_ms": 500},
                "/health": {"weight": 5, "avg_response_ms": 50}
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger("WebSimulator")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _generate_mock_users(self) -> List[Dict]:
        """生成模拟用户数据"""
        users = []
        for i in range(100):
            users.append({
                "id": i + 1,
                "name": f"User{i+1}",
                "email": f"user{i+1}@example.com",
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                "status": random.choice(["active", "inactive", "suspended"])
            })
        return users
    
    def _generate_mock_products(self) -> List[Dict]:
        """生成模拟产品数据"""
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]
        products = []
        
        for i in range(200):
            products.append({
                "id": i + 1,
                "name": f"Product {i+1}",
                "category": random.choice(categories),
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(0, 100),
                "rating": round(random.uniform(1, 5), 1),
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 180))).isoformat()
            })
        return products
    
    def _setup_routes(self):
        """设置Flask路由"""
        
        @self.app.before_request
        def before_request():
            """请求前处理"""
            request.start_time = time.time()
        
        @self.app.after_request
        def after_request(response):
            """请求后处理，记录指标"""
            if hasattr(request, 'start_time'):
                response_time = (time.time() - request.start_time) * 1000
                
                # 记录请求指标
                metric = RequestMetrics(
                    timestamp=datetime.now(),
                    method=request.method,
                    endpoint=request.path,
                    status_code=response.status_code,
                    response_time_ms=response_time,
                    request_size_bytes=len(request.get_data()),
                    response_size_bytes=len(response.get_data()),
                    user_agent=request.headers.get('User-Agent', ''),
                    client_ip=request.remote_addr or '127.0.0.1'
                )
                self.metrics.append(metric)
                
                # 保持最近1000条记录
                if len(self.metrics) > 1000:
                    self.metrics = self.metrics[-1000:]
            
            return response
        
        @self.app.route('/')
        def home():
            """首页"""
            self._simulate_processing_time('/') 
            return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>AIOps Test Web Application</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
                    .stats { margin: 20px 0; }
                    .endpoint { margin: 10px 0; }
                    a { color: #007bff; text-decoration: none; }
                    a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>AIOps Test Web Application</h1>
                    <p>This is a simulated web application for testing monitoring systems.</p>
                </div>
                
                <div class="stats">
                    <h2>Available Endpoints:</h2>
                    <div class="endpoint"><a href="/api/users">GET /api/users</a> - User management</div>
                    <div class="endpoint"><a href="/api/products">GET /api/products</a> - Product catalog</div>
                    <div class="endpoint"><a href="/api/orders">GET /api/orders</a> - Order management</div>
                    <div class="endpoint"><a href="/api/search?q=test">GET /api/search</a> - Search functionality</div>
                    <div class="endpoint"><a href="/api/analytics">GET /api/analytics</a> - Analytics data</div>
                    <div class="endpoint"><a href="/health">GET /health</a> - Health check</div>
                    <div class="endpoint"><a href="/metrics">GET /metrics</a> - Application metrics</div>
                </div>
                
                <div class="stats">
                    <h2>Current Time:</h2>
                    <p>{{ current_time }}</p>
                </div>
            </body>
            </html>
            """, current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        @self.app.route('/api/users')
        def get_users():
            """获取用户列表"""
            self._simulate_processing_time('/api/users')
            
            # 模拟分页
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
            start = (page - 1) * limit
            end = start + limit
            
            return jsonify({
                "users": self.users[start:end],
                "total": len(self.users),
                "page": page,
                "limit": limit
            })
        
        @self.app.route('/api/products')
        def get_products():
            """获取产品列表"""
            self._simulate_processing_time('/api/products')
            
            category = request.args.get('category')
            products = self.products
            
            if category:
                products = [p for p in products if p['category'].lower() == category.lower()]
            
            # 模拟分页
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            start = (page - 1) * limit
            end = start + limit
            
            return jsonify({
                "products": products[start:end],
                "total": len(products),
                "page": page,
                "limit": limit,
                "category": category
            })
        
        @self.app.route('/api/orders')
        def get_orders():
            """获取订单列表"""
            self._simulate_processing_time('/api/orders')
            
            # 生成模拟订单数据
            orders = []
            for i in range(50):
                orders.append({
                    "id": i + 1,
                    "user_id": random.randint(1, 100),
                    "product_ids": random.sample(range(1, 201), random.randint(1, 5)),
                    "total_amount": round(random.uniform(20, 500), 2),
                    "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                })
            
            return jsonify({"orders": orders})
        
        @self.app.route('/api/search')
        def search():
            """搜索功能"""
            self._simulate_processing_time('/api/search')
            
            query = request.args.get('q', '')
            if not query:
                return jsonify({"error": "Query parameter 'q' is required"}), 400
            
            # 模拟搜索结果
            results = []
            for product in self.products:
                if query.lower() in product['name'].lower() or query.lower() in product['category'].lower():
                    results.append(product)
            
            return jsonify({
                "query": query,
                "results": results[:10],  # 限制返回10个结果
                "total_found": len(results)
            })
        
        @self.app.route('/api/analytics')
        def get_analytics():
            """获取分析数据"""
            self._simulate_processing_time('/api/analytics')
            
            # 生成模拟分析数据
            analytics = {
                "daily_visitors": random.randint(1000, 5000),
                "page_views": random.randint(5000, 25000),
                "bounce_rate": round(random.uniform(0.3, 0.7), 2),
                "avg_session_duration": random.randint(120, 600),
                "top_pages": [
                    {"/": random.randint(100, 500)},
                    {"/api/products": random.randint(50, 300)},
                    {"/api/users": random.randint(30, 200)}
                ],
                "user_agents": {
                    "Chrome": random.randint(40, 60),
                    "Firefox": random.randint(20, 30),
                    "Safari": random.randint(10, 20),
                    "Edge": random.randint(5, 15)
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return jsonify(analytics)
        
        @self.app.route('/health')
        def health_check():
            """健康检查"""
            self._simulate_processing_time('/health')
            
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime_seconds": time.time() - getattr(self, 'start_time', time.time()),
                "version": "1.0.0"
            })
        
        @self.app.route('/metrics')
        def get_metrics():
            """获取应用指标"""
            recent_metrics = self.metrics[-100:]  # 最近100个请求
            
            if not recent_metrics:
                return jsonify({"message": "No metrics available"})
            
            # 计算统计信息
            total_requests = len(recent_metrics)
            avg_response_time = sum(m.response_time_ms for m in recent_metrics) / total_requests
            error_count = len([m for m in recent_metrics if m.status_code >= 400])
            error_rate = error_count / total_requests if total_requests > 0 else 0
            
            # 按端点统计
            endpoint_stats = {}
            for metric in recent_metrics:
                if metric.endpoint not in endpoint_stats:
                    endpoint_stats[metric.endpoint] = {
                        "count": 0,
                        "total_response_time": 0,
                        "errors": 0
                    }
                
                endpoint_stats[metric.endpoint]["count"] += 1
                endpoint_stats[metric.endpoint]["total_response_time"] += metric.response_time_ms
                if metric.status_code >= 400:
                    endpoint_stats[metric.endpoint]["errors"] += 1
            
            # 计算每个端点的平均响应时间
            for endpoint, stats in endpoint_stats.items():
                stats["avg_response_time"] = stats["total_response_time"] / stats["count"]
                stats["error_rate"] = stats["errors"] / stats["count"]
                del stats["total_response_time"]  # 删除中间计算值
            
            return jsonify({
                "summary": {
                    "total_requests": total_requests,
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "error_rate": round(error_rate, 4),
                    "error_count": error_count
                },
                "endpoints": endpoint_stats,
                "generated_at": datetime.now().isoformat()
            })
        
        @self.app.route('/api/simulate/error')
        def simulate_error():
            """模拟错误"""
            error_type = request.args.get('type', 'server_error')
            
            if error_type == 'not_found':
                return jsonify({"error": "Resource not found"}), 404
            elif error_type == 'bad_request':
                return jsonify({"error": "Bad request"}), 400
            elif error_type == 'unauthorized':
                return jsonify({"error": "Unauthorized"}), 401
            elif error_type == 'timeout':
                time.sleep(5)  # 模拟超时
                return jsonify({"error": "Request timeout"}), 408
            else:
                return jsonify({"error": "Internal server error"}), 500
    
    def _simulate_processing_time(self, endpoint: str):
        """模拟处理时间"""
        base_time = self.config["endpoints"].get(endpoint, {}).get("avg_response_ms", 100)
        
        # 添加随机变化
        actual_time = base_time * random.uniform(0.5, 2.0)
        
        # 模拟慢响应
        if random.random() < self.config["load_generation"]["slow_response_rate"]:
            actual_time *= random.uniform(3, 10)
        
        # 模拟错误导致的延迟
        if random.random() < self.config["load_generation"]["error_rate"]:
            actual_time *= random.uniform(2, 5)
        
        time.sleep(actual_time / 1000)  # 转换为秒
    
    def start_load_generation(self):
        """启动负载生成"""
        if not self.config["load_generation"]["enabled"]:
            return
        
        self.running = True
        self.load_generator_thread = threading.Thread(target=self._generate_load)
        self.load_generator_thread.daemon = True
        self.load_generator_thread.start()
        self.logger.info("Load generation started")
    
    def stop_load_generation(self):
        """停止负载生成"""
        self.running = False
        if self.load_generator_thread:
            self.load_generator_thread.join(timeout=5)
        self.logger.info("Load generation stopped")
    
    def _generate_load(self):
        """生成负载"""
        base_url = f"http://localhost:{self.config['port']}"
        endpoints = list(self.config["endpoints"].keys())
        weights = [self.config["endpoints"][ep]["weight"] for ep in endpoints]
        
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
        while self.running:
            try:
                # 计算当前应该的RPS
                current_hour = datetime.now().hour
                if current_hour in self.config["load_generation"]["peak_hours"]:
                    target_rps = self.config["load_generation"]["peak_rps"]
                else:
                    target_rps = self.config["load_generation"]["base_rps"]
                
                # 添加随机变化
                actual_rps = target_rps * random.uniform(0.7, 1.3)
                interval = 1.0 / actual_rps
                
                # 选择端点
                endpoint = random.choices(endpoints, weights=weights)[0]
                url = base_url + endpoint
                
                # 添加查询参数（对某些端点）
                if endpoint == "/api/search":
                    url += "?q=" + random.choice(["test", "product", "user", "order"])
                elif endpoint in ["/api/users", "/api/products"]:
                    url += f"?page={random.randint(1, 5)}&limit={random.randint(5, 20)}"
                
                # 发送请求
                headers = {
                    "User-Agent": random.choice(user_agents),
                    "Accept": "application/json"
                }
                
                try:
                    response = requests.get(url, headers=headers, timeout=10)
                    self.logger.debug(f"Generated request: {endpoint} -> {response.status_code}")
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"Load generation request failed: {e}")
                
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in load generation: {e}")
                time.sleep(1)
    
    def run(self, threaded: bool = True):
        """运行Web应用"""
        self.start_time = time.time()
        
        # 启动负载生成
        self.start_load_generation()
        
        try:
            self.logger.info(f"Starting web simulator on {self.config['host']}:{self.config['port']}")
            self.app.run(
                host=self.config["host"],
                port=self.config["port"],
                debug=self.config["debug"],
                threaded=threaded
            )
        except KeyboardInterrupt:
            self.logger.info("Web simulator stopped by user")
        finally:
            self.stop_load_generation()
    
    def get_recent_metrics(self, count: int = 100) -> List[RequestMetrics]:
        """获取最近的指标数据"""
        return self.metrics[-count:] if self.metrics else []
    
    def export_metrics_to_prometheus_format(self) -> str:
        """导出指标为Prometheus格式"""
        recent_metrics = self.get_recent_metrics()
        
        if not recent_metrics:
            return "# No metrics available\n"
        
        # 计算指标
        total_requests = len(recent_metrics)
        avg_response_time = sum(m.response_time_ms for m in recent_metrics) / total_requests
        error_count = len([m for m in recent_metrics if m.status_code >= 400])
        
        prometheus_metrics = f"""
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total {total_requests}

# HELP http_request_duration_ms Average HTTP request duration in milliseconds
# TYPE http_request_duration_ms gauge
http_request_duration_ms {avg_response_time:.2f}

# HELP http_errors_total Total number of HTTP errors
# TYPE http_errors_total counter
http_errors_total {error_count}

# HELP http_error_rate HTTP error rate
# TYPE http_error_rate gauge
http_error_rate {error_count / total_requests if total_requests > 0 else 0:.4f}
"""
        
        return prometheus_metrics


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web Application Simulator")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--no-load-gen", action="store_true", help="Disable load generation")
    
    args = parser.parse_args()
    
    # 加载配置
    config = None
    if args.config:
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
    
    if not config:
        config = {}
    
    # 应用命令行参数
    config["host"] = args.host
    config["port"] = args.port
    
    if args.no_load_gen:
        config.setdefault("load_generation", {})["enabled"] = False
    
    # 创建并运行模拟器
    simulator = WebSimulator(config)
    simulator.run()


if __name__ == "__main__":
    main()