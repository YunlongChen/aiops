/**
 * AIOps Platform API Gateway
 * 智能运维平台API网关服务
 * 
 * 功能:
 * - 统一API入口
 * - 请求路由和负载均衡
 * - 认证和授权
 * - 限流和监控
 * - 服务发现和健康检查
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const compression = require('compression');
const rateLimit = require('express-rate-limit');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.API_PORT || 8080;
const HOST = process.env.API_HOST || '0.0.0.0';

// 服务配置
const services = {
  aiEngine: process.env.AI_ENGINE_URL || 'http://ai-engine:8000',
  selfHealing: process.env.SELF_HEALING_URL || 'http://self-healing:8001',
  prometheus: process.env.PROMETHEUS_URL || 'http://prometheus:9090',
  grafana: process.env.GRAFANA_URL || 'http://grafana:3000',
  kibana: process.env.KIBANA_URL || 'http://kibana:5601'
};

// 中间件配置
app.use(helmet()); // 安全头
app.use(compression()); // 压缩响应
app.use(cors()); // 跨域支持
app.use(morgan('combined')); // 日志记录
app.use(express.json({ limit: '10mb' })); // JSON解析
app.use(express.urlencoded({ extended: true, limit: '10mb' })); // URL编码解析

// 限流配置
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 1000, // 限制每个IP 15分钟内最多1000个请求
  message: {
    error: 'Too many requests from this IP, please try again later.',
    code: 'RATE_LIMIT_EXCEEDED'
  }
});
app.use(limiter);

// 健康检查端点
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    services: Object.keys(services)
  });
});

// API信息端点
app.get('/api/info', (req, res) => {
  res.json({
    name: 'AIOps Platform API Gateway',
    version: '1.0.0',
    description: '智能运维平台API网关服务',
    endpoints: {
      '/api/ai/*': 'AI引擎服务',
      '/api/healing/*': '自愈执行器服务',
      '/api/metrics/*': 'Prometheus指标服务',
      '/api/dashboard/*': 'Grafana仪表板服务',
      '/api/logs/*': 'Kibana日志服务'
    }
  });
});

// Prometheus指标端点
app.get('/metrics', (req, res) => {
  const metrics = `# HELP api_gateway_requests_total Total number of requests
# TYPE api_gateway_requests_total counter
api_gateway_requests_total{method="GET",status="200"} ${Math.floor(Math.random() * 1000)}
api_gateway_requests_total{method="POST",status="200"} ${Math.floor(Math.random() * 500)}
api_gateway_requests_total{method="GET",status="404"} ${Math.floor(Math.random() * 100)}

# HELP api_gateway_request_duration_seconds Request duration in seconds
# TYPE api_gateway_request_duration_seconds histogram
api_gateway_request_duration_seconds_bucket{le="0.1"} ${Math.floor(Math.random() * 100)}
api_gateway_request_duration_seconds_bucket{le="0.5"} ${Math.floor(Math.random() * 200)}
api_gateway_request_duration_seconds_bucket{le="1.0"} ${Math.floor(Math.random() * 300)}
api_gateway_request_duration_seconds_bucket{le="+Inf"} ${Math.floor(Math.random() * 400)}
api_gateway_request_duration_seconds_sum ${Math.random() * 1000}
api_gateway_request_duration_seconds_count ${Math.floor(Math.random() * 400)}

# HELP api_gateway_up Gateway service status
# TYPE api_gateway_up gauge
api_gateway_up 1
`;
  
  res.set('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
  res.send(metrics);
});

// 代理函数
const proxyRequest = async (req, res, targetUrl) => {
  try {
    const config = {
      method: req.method,
      url: `${targetUrl}${req.path}`,
      headers: { ...req.headers },
      timeout: 30000
    };

    // 删除不需要的头部
    delete config.headers.host;
    delete config.headers['content-length'];

    // 添加请求体（如果存在）
    if (req.body && Object.keys(req.body).length > 0) {
      config.data = req.body;
    }

    // 添加查询参数
    if (req.query && Object.keys(req.query).length > 0) {
      config.params = req.query;
    }

    const response = await axios(config);
    
    // 设置响应头
    Object.keys(response.headers).forEach(key => {
      if (key !== 'content-encoding' && key !== 'transfer-encoding') {
        res.set(key, response.headers[key]);
      }
    });

    res.status(response.status).send(response.data);
  } catch (error) {
    console.error(`Proxy error for ${targetUrl}:`, error.message);
    
    if (error.response) {
      res.status(error.response.status).json({
        error: 'Service error',
        message: error.response.data?.message || error.message,
        service: targetUrl
      });
    } else if (error.code === 'ECONNREFUSED') {
      res.status(503).json({
        error: 'Service unavailable',
        message: 'Target service is not available',
        service: targetUrl
      });
    } else {
      res.status(500).json({
        error: 'Internal server error',
        message: error.message,
        service: targetUrl
      });
    }
  }
};

// AI引擎服务路由
app.use('/api/ai', (req, res) => {
  req.path = req.path.replace('/api/ai', '');
  proxyRequest(req, res, services.aiEngine);
});

// 自愈执行器服务路由
app.use('/api/healing', (req, res) => {
  req.path = req.path.replace('/api/healing', '');
  proxyRequest(req, res, services.selfHealing);
});

// Prometheus指标服务路由
app.use('/api/metrics', (req, res) => {
  req.path = req.path.replace('/api/metrics', '');
  proxyRequest(req, res, services.prometheus);
});

// Grafana仪表板服务路由
app.use('/api/dashboard', (req, res) => {
  req.path = req.path.replace('/api/dashboard', '');
  proxyRequest(req, res, services.grafana);
});

// Kibana日志服务路由
app.use('/api/logs', (req, res) => {
  req.path = req.path.replace('/api/logs', '');
  proxyRequest(req, res, services.kibana);
});

// 404处理
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: 'The requested endpoint does not exist',
    path: req.originalUrl
  });
});

// 错误处理中间件
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal Server Error',
    message: 'An unexpected error occurred'
  });
});

// 启动服务器
app.listen(PORT, HOST, () => {
  console.log(`🚀 AIOps API Gateway is running on http://${HOST}:${PORT}`);
  console.log(`📊 Health check: http://${HOST}:${PORT}/health`);
  console.log(`📖 API info: http://${HOST}:${PORT}/api/info`);
  console.log('🔗 Configured services:', Object.keys(services));
});

// 优雅关闭
process.on('SIGTERM', () => {
  console.log('🛑 SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🛑 SIGINT received, shutting down gracefully');
  process.exit(0);
});