<!--
  性能监控组件
  功能：显示实时性能指标和服务健康状态
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="performance-monitoring">
    <div class="monitoring-grid">
      <!-- 实时性能指标卡片 -->
      <div class="monitoring-card">
        <div class="card-header">
          <h3>实时性能指标</h3>
          <div class="refresh-btn" @click="refreshMetrics">
            <i class="fas fa-sync-alt" :class="{ spinning: isRefreshing }"></i>
          </div>
        </div>
        <div class="metrics-grid">
          <div 
            v-for="metric in performanceMetrics" 
            :key="metric.id"
            class="metric-box"
          >
            <div :class="['metric-icon', metric.type]">
              <i :class="metric.icon"></i>
            </div>
            <div class="metric-info">
              <div class="metric-value">{{ metric.value }}</div>
              <div class="metric-label">{{ metric.label }}</div>
              <div :class="['metric-trend', metric.trend.type]">
                {{ metric.trend.value }}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 服务健康状态卡片 -->
      <div class="monitoring-card">
        <div class="card-header">
          <h3>服务健康状态</h3>
          <div class="status-summary">
            <span class="healthy-count">{{ healthyServices }}个正常</span>
            <span class="warning-count">{{ warningServices }}个警告</span>
          </div>
        </div>
        <div class="service-list">
          <div 
            v-for="service in services" 
            :key="service.id"
            :class="['service-item', service.status]"
          >
            <div class="service-status"></div>
            <div class="service-name">{{ service.name }}</div>
            <div class="service-metrics">
              <span 
                v-for="(metric, index) in service.metrics" 
                :key="index"
              >
                {{ metric }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细监控图表 -->
    <div class="detailed-charts">
      <div class="chart-container">
        <div class="chart-header">
          <h3>系统资源使用趋势</h3>
          <div class="chart-controls">
            <div class="time-selector">
              <button 
                v-for="period in timePeriods" 
                :key="period.value"
                :class="['time-btn', { active: selectedPeriod === period.value }]"
                @click="selectTimePeriod(period.value)"
              >
                {{ period.label }}
              </button>
            </div>
          </div>
        </div>
        <div class="chart-content">
          <canvas ref="resourceTrendChart" id="resource-trend-chart"></canvas>
        </div>
      </div>

      <div class="chart-container">
        <div class="chart-header">
          <h3>服务响应时间分布</h3>
          <div class="legend">
            <div class="legend-item">
              <span class="legend-color web"></span>
              <span>Web服务</span>
            </div>
            <div class="legend-item">
              <span class="legend-color api"></span>
              <span>API服务</span>
            </div>
            <div class="legend-item">
              <span class="legend-color database"></span>
              <span>数据库</span>
            </div>
          </div>
        </div>
        <div class="chart-content">
          <canvas ref="responseTimeChart" id="response-time-chart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 性能监控组件
 * 显示实时性能指标、服务健康状态和详细监控图表
 */
export default {
  name: 'PerformanceMonitoring',
  data() {
    return {
      // 刷新状态
      isRefreshing: false,
      // 选中的时间周期
      selectedPeriod: '1h',
      // 时间周期选项
      timePeriods: [
        { value: '15m', label: '15分钟' },
        { value: '1h', label: '1小时' },
        { value: '6h', label: '6小时' },
        { value: '24h', label: '24小时' }
      ],
      // 性能指标数据
      performanceMetrics: [
        {
          id: 1,
          type: 'cpu',
          icon: 'fas fa-microchip',
          value: '65.2%',
          label: 'CPU使用率',
          trend: {
            type: 'up',
            value: '+2.3%'
          }
        },
        {
          id: 2,
          type: 'memory',
          icon: 'fas fa-memory',
          value: '78.9%',
          label: '内存使用率',
          trend: {
            type: 'down',
            value: '-1.2%'
          }
        },
        {
          id: 3,
          type: 'disk',
          icon: 'fas fa-hdd',
          value: '45.6%',
          label: '磁盘使用率',
          trend: {
            type: 'stable',
            value: '0%'
          }
        },
        {
          id: 4,
          type: 'network',
          icon: 'fas fa-network-wired',
          value: '32.1%',
          label: '网络带宽',
          trend: {
            type: 'up',
            value: '+5.7%'
          }
        }
      ],
      // 服务状态数据
      services: [
        {
          id: 1,
          name: 'Web服务器',
          status: 'healthy',
          metrics: ['响应时间: 120ms', 'QPS: 1,234']
        },
        {
          id: 2,
          name: '数据库',
          status: 'warning',
          metrics: ['响应时间: 350ms', '连接数: 89/100']
        },
        {
          id: 3,
          name: '缓存服务',
          status: 'healthy',
          metrics: ['命中率: 95.2%', '内存: 2.1GB/4GB']
        },
        {
          id: 4,
          name: 'API网关',
          status: 'healthy',
          metrics: ['吞吐量: 2,456/s', '错误率: 0.1%']
        }
      ]
    }
  },
  computed: {
    /**
     * 计算健康服务数量
     */
    healthyServices() {
      return this.services.filter(service => service.status === 'healthy').length
    },
    
    /**
     * 计算警告服务数量
     */
    warningServices() {
      return this.services.filter(service => service.status === 'warning').length
    }
  },
  methods: {
    /**
     * 刷新性能指标
     */
    async refreshMetrics() {
      this.isRefreshing = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        // 这里应该调用实际的API来获取最新数据
        console.log('Metrics refreshed')
      } finally {
        this.isRefreshing = false
      }
    },
    
    /**
     * 选择时间周期
     * @param {string} period - 时间周期
     */
    selectTimePeriod(period) {
      this.selectedPeriod = period
      this.updateCharts()
    },
    
    /**
     * 更新图表
     */
    updateCharts() {
      console.log('Updating charts for period:', this.selectedPeriod)
      // 这里应该根据选中的时间周期更新图表数据
    },
    
    /**
     * 初始化图表
     */
    initCharts() {
      // 这里可以使用Chart.js或其他图表库初始化图表
      console.log('Initializing performance monitoring charts')
    }
  },
  mounted() {
    // 初始化图表
    this.initCharts()
    
    // 设置定时刷新
    this.refreshInterval = setInterval(() => {
      this.refreshMetrics()
    }, 30000) // 每30秒刷新一次
  },
  beforeUnmount() {
    // 清理定时器
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  }
}
</script>

<style scoped>
/* 性能监控容器 */
.performance-monitoring {
  padding: 20px;
}

/* 监控网格布局 */
.monitoring-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

/* 监控卡片样式 */
.monitoring-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.refresh-btn {
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  color: #6c757d;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: #f8f9fa;
  color: #3498db;
}

.refresh-btn .spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.status-summary {
  display: flex;
  gap: 15px;
  font-size: 12px;
}

.healthy-count {
  color: #28a745;
  font-weight: 500;
}

.warning-count {
  color: #ffc107;
  font-weight: 500;
}

/* 性能指标网格 */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px;
}

.metric-box {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: transform 0.2s ease;
}

.metric-box:hover {
  transform: translateY(-2px);
}

.metric-icon {
  width: 45px;
  height: 45px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.metric-icon.cpu {
  background: #e3f2fd;
  color: #1976d2;
}

.metric-icon.memory {
  background: #f3e5f5;
  color: #7b1fa2;
}

.metric-icon.disk {
  background: #e8f5e8;
  color: #388e3c;
}

.metric-icon.network {
  background: #fff3e0;
  color: #f57c00;
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 2px;
}

.metric-label {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 4px;
}

.metric-trend {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.metric-trend.up {
  background: #ffebee;
  color: #c62828;
}

.metric-trend.down {
  background: #e8f5e8;
  color: #2e7d32;
}

.metric-trend.stable {
  background: #f5f5f5;
  color: #616161;
}

/* 服务列表样式 */
.service-list {
  padding: 20px;
}

.service-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.service-item:last-child {
  border-bottom: none;
}

.service-status {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.service-item.healthy .service-status {
  background: #28a745;
}

.service-item.warning .service-status {
  background: #ffc107;
}

.service-item.error .service-status {
  background: #dc3545;
}

.service-name {
  font-weight: 500;
  color: #2c3e50;
  min-width: 100px;
}

.service-metrics {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #6c757d;
}

/* 详细图表区域 */
.detailed-charts {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.time-selector {
  display: flex;
  gap: 5px;
}

.time-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.time-btn:hover {
  background: #f8f9fa;
}

.time-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.legend {
  display: flex;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #6c757d;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-color.web {
  background: #3498db;
}

.legend-color.api {
  background: #e74c3c;
}

.legend-color.database {
  background: #f39c12;
}

.chart-content {
  padding: 20px;
  height: 300px;
}

.chart-content canvas {
  width: 100% !important;
  height: 100% !important;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .monitoring-grid {
    grid-template-columns: 1fr;
  }
  
  .detailed-charts {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .performance-monitoring {
    padding: 15px;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .time-selector {
    flex-wrap: wrap;
  }
  
  .legend {
    flex-wrap: wrap;
  }
}
</style>