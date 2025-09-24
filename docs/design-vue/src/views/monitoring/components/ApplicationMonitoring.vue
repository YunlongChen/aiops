<!--
  应用监控组件
  功能：提供应用服务监控、API监控和应用性能分析
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="application-monitoring">
    <!-- 应用服务概览 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>应用服务概览</h3>
        <div class="section-actions">
          <select v-model="selectedEnvironment" class="env-selector">
            <option value="all">所有环境</option>
            <option value="production">生产环境</option>
            <option value="staging">测试环境</option>
            <option value="development">开发环境</option>
          </select>
          <button class="btn-icon" @click="refreshServices" title="刷新">
            <i class="fas fa-sync-alt" :class="{ spinning: isRefreshingServices }"></i>
          </button>
        </div>
      </div>

      <div class="services-grid">
        <div 
          v-for="service in filteredServices" 
          :key="service.id"
          :class="['service-card', service.status]"
        >
          <div class="service-header">
            <div class="service-info">
              <h4>{{ service.name }}</h4>
              <span class="service-version">v{{ service.version }}</span>
              <span class="service-env">{{ service.environment }}</span>
            </div>
            <div class="service-status">
              <span :class="['status-indicator', service.status]"></span>
              <span class="status-text">{{ getStatusText(service.status) }}</span>
            </div>
          </div>
          
          <div class="service-metrics">
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-label">响应时间</span>
                <span class="metric-value">{{ service.responseTime }}ms</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">吞吐量</span>
                <span class="metric-value">{{ service.throughput }}/s</span>
              </div>
            </div>
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-label">错误率</span>
                <span :class="['metric-value', getErrorRateLevel(service.errorRate)]">
                  {{ service.errorRate }}%
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">可用性</span>
                <span class="metric-value">{{ service.availability }}%</span>
              </div>
            </div>
          </div>
          
          <div class="service-actions">
            <button class="btn-small" @click="viewServiceDetails(service)">
              详情
            </button>
            <button class="btn-small" @click="viewServiceLogs(service)">
              日志
            </button>
            <button class="btn-small" @click="restartService(service)">
              重启
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- API监控 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>API监控</h3>
        <div class="section-actions">
          <input
            type="text"
            v-model="apiSearchQuery"
            @input="filterAPIs"
            placeholder="搜索API..."
            class="search-input"
          />
        </div>
      </div>

      <div class="api-stats">
        <div class="stat-card">
          <div class="stat-value">{{ apiStats.total }}</div>
          <div class="stat-label">总API数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ apiStats.healthy }}</div>
          <div class="stat-label">正常</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ apiStats.warning }}</div>
          <div class="stat-label">警告</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ apiStats.error }}</div>
          <div class="stat-label">错误</div>
        </div>
      </div>

      <div class="table-container">
        <table class="monitoring-table">
          <thead>
            <tr>
              <th>API端点</th>
              <th>方法</th>
              <th>状态</th>
              <th>响应时间</th>
              <th>请求数/分钟</th>
              <th>成功率</th>
              <th>最后检查</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="api in filteredAPIs" :key="api.id">
              <td>
                <div class="api-endpoint">
                  <span class="endpoint-path">{{ api.endpoint }}</span>
                </div>
              </td>
              <td>
                <span :class="['method-badge', api.method.toLowerCase()]">
                  {{ api.method }}
                </span>
              </td>
              <td>
                <span :class="['status-badge', api.status]">
                  {{ getStatusText(api.status) }}
                </span>
              </td>
              <td>
                <span :class="['response-time', getResponseTimeLevel(api.responseTime)]">
                  {{ api.responseTime }}ms
                </span>
              </td>
              <td>{{ api.requestsPerMinute }}</td>
              <td>
                <span :class="['success-rate', getSuccessRateLevel(api.successRate)]">
                  {{ api.successRate }}%
                </span>
              </td>
              <td>{{ api.lastCheck }}</td>
              <td>
                <button class="btn-icon" @click="testAPI(api)" title="测试">
                  <i class="fas fa-play"></i>
                </button>
                <button class="btn-icon" @click="viewAPIMetrics(api)" title="指标">
                  <i class="fas fa-chart-line"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 应用性能分析 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>应用性能分析</h3>
      </div>

      <div class="performance-charts">
        <div class="chart-row">
          <div class="chart-card">
            <div class="chart-header">
              <h4>响应时间趋势</h4>
              <div class="chart-controls">
                <select v-model="responseTimeMetric" class="metric-selector">
                  <option value="avg">平均值</option>
                  <option value="p95">95分位</option>
                  <option value="p99">99分位</option>
                </select>
              </div>
            </div>
            <div class="chart-content">
              <canvas ref="responseTimeChart" id="response-time-chart"></canvas>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h4>吞吐量趋势</h4>
              <div class="current-value">{{ performanceMetrics.currentThroughput }}/s</div>
            </div>
            <div class="chart-content">
              <canvas ref="throughputChart" id="throughput-chart"></canvas>
            </div>
          </div>
        </div>

        <div class="chart-row">
          <div class="chart-card">
            <div class="chart-header">
              <h4>错误率分布</h4>
              <div class="current-value error-rate">{{ performanceMetrics.currentErrorRate }}%</div>
            </div>
            <div class="chart-content">
              <canvas ref="errorRateChart" id="error-rate-chart"></canvas>
            </div>
          </div>

          <div class="chart-card">
            <div class="chart-header">
              <h4>资源使用情况</h4>
            </div>
            <div class="resource-metrics">
              <div class="resource-item">
                <span class="resource-label">CPU使用率</span>
                <div class="resource-bar">
                  <div 
                    class="resource-fill" 
                    :style="{ width: performanceMetrics.cpu + '%' }"
                  ></div>
                </div>
                <span class="resource-value">{{ performanceMetrics.cpu }}%</span>
              </div>
              <div class="resource-item">
                <span class="resource-label">内存使用率</span>
                <div class="resource-bar">
                  <div 
                    class="resource-fill" 
                    :style="{ width: performanceMetrics.memory + '%' }"
                  ></div>
                </div>
                <span class="resource-value">{{ performanceMetrics.memory }}%</span>
              </div>
              <div class="resource-item">
                <span class="resource-label">连接数</span>
                <div class="resource-bar">
                  <div 
                    class="resource-fill" 
                    :style="{ width: (performanceMetrics.connections / 1000) * 100 + '%' }"
                  ></div>
                </div>
                <span class="resource-value">{{ performanceMetrics.connections }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 应用监控组件
 * 提供应用服务、API监控和性能分析功能
 */
export default {
  name: 'ApplicationMonitoring',
  props: {
    timeRange: {
      type: String,
      default: '1h'
    },
    isRefreshing: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      // 环境和搜索
      selectedEnvironment: 'all',
      apiSearchQuery: '',
      isRefreshingServices: false,
      responseTimeMetric: 'avg',
      
      // 应用服务数据
      services: [
        {
          id: 1,
          name: 'User Service',
          version: '2.1.3',
          environment: 'production',
          status: 'healthy',
          responseTime: 45,
          throughput: 1250,
          errorRate: 0.2,
          availability: 99.9
        },
        {
          id: 2,
          name: 'Order Service',
          version: '1.8.7',
          environment: 'production',
          status: 'warning',
          responseTime: 120,
          throughput: 890,
          errorRate: 2.1,
          availability: 98.5
        },
        {
          id: 3,
          name: 'Payment Service',
          version: '3.0.1',
          environment: 'production',
          status: 'healthy',
          responseTime: 78,
          throughput: 650,
          errorRate: 0.1,
          availability: 99.8
        },
        {
          id: 4,
          name: 'Notification Service',
          version: '1.5.2',
          environment: 'staging',
          status: 'error',
          responseTime: 250,
          throughput: 120,
          errorRate: 8.5,
          availability: 95.2
        }
      ],
      
      // API数据
      apis: [
        {
          id: 1,
          endpoint: '/api/v1/users',
          method: 'GET',
          status: 'healthy',
          responseTime: 45,
          requestsPerMinute: 1250,
          successRate: 99.8,
          lastCheck: '2分钟前'
        },
        {
          id: 2,
          endpoint: '/api/v1/orders',
          method: 'POST',
          status: 'warning',
          responseTime: 120,
          requestsPerMinute: 890,
          successRate: 97.9,
          lastCheck: '1分钟前'
        },
        {
          id: 3,
          endpoint: '/api/v1/payments',
          method: 'POST',
          status: 'healthy',
          responseTime: 78,
          requestsPerMinute: 650,
          successRate: 99.9,
          lastCheck: '30秒前'
        },
        {
          id: 4,
          endpoint: '/api/v1/notifications',
          method: 'POST',
          status: 'error',
          responseTime: 250,
          requestsPerMinute: 120,
          successRate: 91.5,
          lastCheck: '5分钟前'
        }
      ],
      
      // 性能指标
      performanceMetrics: {
        currentThroughput: 2910,
        currentErrorRate: 1.8,
        cpu: 65,
        memory: 72,
        connections: 450
      },
      
      // 过滤后的数据
      filteredServices: [],
      filteredAPIs: []
    }
  },
  computed: {
    /**
     * API统计信息
     */
    apiStats() {
      return {
        total: this.apis.length,
        healthy: this.apis.filter(api => api.status === 'healthy').length,
        warning: this.apis.filter(api => api.status === 'warning').length,
        error: this.apis.filter(api => api.status === 'error').length
      }
    }
  },
  methods: {
    /**
     * 获取状态文本
     */
    getStatusText(status) {
      const statusMap = {
        healthy: '正常',
        warning: '警告',
        error: '错误',
        critical: '严重',
        offline: '离线'
      }
      return statusMap[status] || '未知'
    },
    
    /**
     * 获取错误率级别
     */
    getErrorRateLevel(rate) {
      if (rate >= 5) return 'critical'
      if (rate >= 1) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取响应时间级别
     */
    getResponseTimeLevel(time) {
      if (time >= 200) return 'critical'
      if (time >= 100) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取成功率级别
     */
    getSuccessRateLevel(rate) {
      if (rate < 95) return 'critical'
      if (rate < 98) return 'warning'
      return 'normal'
    },
    
    /**
     * 过滤服务
     */
    filterServices() {
      if (this.selectedEnvironment === 'all') {
        this.filteredServices = [...this.services]
      } else {
        this.filteredServices = this.services.filter(service =>
          service.environment === this.selectedEnvironment
        )
      }
    },
    
    /**
     * 过滤API
     */
    filterAPIs() {
      if (!this.apiSearchQuery) {
        this.filteredAPIs = [...this.apis]
      } else {
        const query = this.apiSearchQuery.toLowerCase()
        this.filteredAPIs = this.apis.filter(api =>
          api.endpoint.toLowerCase().includes(query) ||
          api.method.toLowerCase().includes(query)
        )
      }
    },
    
    /**
     * 刷新服务
     */
    async refreshServices() {
      this.isRefreshingServices = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('Services refreshed')
      } finally {
        this.isRefreshingServices = false
      }
    },
    
    /**
     * 查看服务详情
     */
    viewServiceDetails(service) {
      console.log(`Viewing details for service: ${service.name}`)
      // 这里可以打开服务详情弹窗或跳转到详情页面
    },
    
    /**
     * 查看服务日志
     */
    viewServiceLogs(service) {
      console.log(`Viewing logs for service: ${service.name}`)
      // 这里可以打开日志查看器
    },
    
    /**
     * 重启服务
     */
    restartService(service) {
      console.log(`Restarting service: ${service.name}`)
      // 这里可以实现服务重启逻辑
    },
    
    /**
     * 测试API
     */
    testAPI(api) {
      console.log(`Testing API: ${api.method} ${api.endpoint}`)
      // 这里可以实现API测试逻辑
    },
    
    /**
     * 查看API指标
     */
    viewAPIMetrics(api) {
      console.log(`Viewing metrics for API: ${api.endpoint}`)
      // 这里可以打开API指标详情
    },
    
    /**
     * 初始化图表
     */
    initCharts() {
      // 这里可以使用Chart.js或其他图表库初始化图表
      console.log('Initializing application performance charts')
    }
  },
  mounted() {
    // 初始化过滤数据
    this.filterServices()
    this.filterAPIs()
    // 初始化图表
    this.initCharts()
  },
  watch: {
    selectedEnvironment() {
      this.filterServices()
    },
    timeRange() {
      // 时间范围变化时重新加载数据
      console.log(`Time range changed to: ${this.timeRange}`)
      this.initCharts()
    },
    responseTimeMetric() {
      // 响应时间指标变化时重新加载图表
      this.initCharts()
    }
  }
}
</script>

<style scoped>
/* 应用监控容器 */
.application-monitoring {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 监控区块样式 */
.monitoring-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.env-selector,
.metric-selector {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.search-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 200px;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.btn-icon {
  padding: 6px 8px;
  border: none;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  color: #6c757d;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #e9ecef;
  color: #495057;
}

.btn-small {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #495057;
  transition: all 0.2s ease;
}

.btn-small:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

/* 服务网格样式 */
.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.service-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  border-left: 4px solid #28a745;
}

.service-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.service-card.warning {
  border-left-color: #ffc107;
}

.service-card.error {
  border-left-color: #dc3545;
}

.service-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.service-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 16px;
}

.service-version {
  background: #e9ecef;
  color: #495057;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
  margin-right: 8px;
}

.service-env {
  background: #3498db;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.service-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #28a745;
}

.status-indicator.warning {
  background: #ffc107;
}

.status-indicator.error {
  background: #dc3545;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: #495057;
}

/* 服务指标样式 */
.service-metrics {
  margin-bottom: 15px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.metric-label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 4px;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.metric-value.warning {
  color: #f39c12;
}

.metric-value.critical {
  color: #e74c3c;
}

.service-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* API统计样式 */
.api-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
  text-transform: uppercase;
  font-weight: 500;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
}

.monitoring-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.monitoring-table th,
.monitoring-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.monitoring-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 12px;
  text-transform: uppercase;
}

.monitoring-table tr:hover {
  background: #f8f9fa;
}

.api-endpoint {
  font-family: monospace;
  font-size: 13px;
}

.endpoint-path {
  color: #2c3e50;
}

.method-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.method-badge.get {
  background: #d4edda;
  color: #155724;
}

.method-badge.post {
  background: #cce5ff;
  color: #004085;
}

.method-badge.put {
  background: #fff3cd;
  color: #856404;
}

.method-badge.delete {
  background: #f8d7da;
  color: #721c24;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.healthy {
  background: #d4edda;
  color: #155724;
}

.status-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.status-badge.error {
  background: #f8d7da;
  color: #721c24;
}

.response-time.warning {
  color: #f39c12;
}

.response-time.critical {
  color: #e74c3c;
}

.success-rate.warning {
  color: #f39c12;
}

.success-rate.critical {
  color: #e74c3c;
}

/* 性能图表样式 */
.performance-charts {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.chart-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  background: white;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-header h4 {
  margin: 0;
  font-size: 14px;
  color: #2c3e50;
}

.chart-controls {
  display: flex;
  gap: 10px;
}

.current-value {
  font-size: 16px;
  font-weight: 600;
  color: #3498db;
}

.current-value.error-rate {
  color: #e74c3c;
}

.chart-content {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 4px;
  color: #6c757d;
}

.chart-content canvas {
  max-width: 100%;
  max-height: 100%;
}

/* 资源指标样式 */
.resource-metrics {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px 0;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.resource-label {
  width: 80px;
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.resource-bar {
  flex: 1;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  background: #3498db;
  transition: width 0.3s ease;
}

.resource-value {
  width: 50px;
  text-align: right;
  font-size: 12px;
  font-weight: 600;
  color: #495057;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .services-grid {
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  }
  
  .chart-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .monitoring-section {
    padding: 15px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .section-actions {
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
  
  .services-grid {
    grid-template-columns: 1fr;
  }
  
  .api-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .metric-row {
    flex-direction: column;
    gap: 10px;
  }
  
  .service-actions {
    justify-content: center;
  }
  
  .resource-item {
    flex-direction: column;
    align-items: stretch;
    gap: 5px;
  }
  
  .resource-label {
    width: auto;
  }
  
  .resource-value {
    width: auto;
    text-align: left;
  }
}

@media (max-width: 480px) {
  .application-monitoring {
    gap: 20px;
  }
  
  .monitoring-section {
    padding: 12px;
  }
  
  .section-header h3 {
    font-size: 16px;
  }
  
  .api-stats {
    grid-template-columns: 1fr;
  }
  
  .chart-content {
    height: 150px;
  }
}
</style>