<!--
  性能分析组件
  功能：提供性能趋势分析、资源利用率分布和性能洞察
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="performance-analysis">
    <!-- 分析过滤器 -->
    <div class="analysis-filters">
      <div class="filter-group">
        <label>时间范围:</label>
        <select v-model="selectedTimeRange" @change="updateAnalysis" class="time-selector">
          <option value="1h">最近1小时</option>
          <option value="6h">最近6小时</option>
          <option value="24h">最近24小时</option>
          <option value="7d">最近7天</option>
          <option value="30d">最近30天</option>
        </select>
      </div>
      <div class="filter-group">
        <label>服务类型:</label>
        <select v-model="selectedServiceType" @change="updateAnalysis" class="service-selector">
          <option value="all">全部服务</option>
          <option value="web">Web服务</option>
          <option value="database">数据库</option>
          <option value="cache">缓存</option>
          <option value="api">API服务</option>
        </select>
      </div>
      <div class="filter-group">
        <label>指标类型:</label>
        <select v-model="selectedMetricType" @change="updateAnalysis" class="metric-selector">
          <option value="all">全部指标</option>
          <option value="cpu">CPU使用率</option>
          <option value="memory">内存使用率</option>
          <option value="disk">磁盘I/O</option>
          <option value="network">网络流量</option>
        </select>
      </div>
      <div class="filter-actions">
        <button class="btn btn-primary" @click="refreshAnalysis">
          <i class="fas fa-sync-alt" :class="{ spinning: isRefreshing }"></i>
          刷新数据
        </button>
        <button class="btn btn-secondary" @click="exportReport">
          <i class="fas fa-download"></i>
          导出报告
        </button>
      </div>
    </div>
    
    <!-- 分析图表 -->
    <div class="analysis-charts">
      <div class="chart-card">
        <div class="chart-header">
          <h4>性能趋势分析</h4>
          <div class="chart-info">
            <span class="data-points">数据点: {{ dataPointsCount }}</span>
            <span class="last-update">最后更新: {{ lastUpdateTime }}</span>
          </div>
        </div>
        <div class="chart-content">
          <canvas ref="performanceTrendChart" id="performance-trend-chart"></canvas>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="chart-header">
          <h4>资源利用率分布</h4>
          <div class="distribution-legend">
            <div class="legend-item">
              <span class="legend-color high"></span>
              <span>高负载 (>80%)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color medium"></span>
              <span>中负载 (50-80%)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color low"></span>
              <span>低负载 (<50%)</span>
            </div>
          </div>
        </div>
        <div class="chart-content">
          <canvas ref="resourceDistributionChart" id="resource-distribution-chart"></canvas>
        </div>
      </div>
    </div>
    
    <!-- 性能统计摘要 -->
    <div class="performance-summary">
      <div class="summary-card">
        <div class="summary-icon">
          <i class="fas fa-chart-line"></i>
        </div>
        <div class="summary-content">
          <div class="summary-title">平均响应时间</div>
          <div class="summary-value">{{ averageResponseTime }}ms</div>
          <div class="summary-change positive">较昨日 -12.5%</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon">
          <i class="fas fa-tachometer-alt"></i>
        </div>
        <div class="summary-content">
          <div class="summary-title">峰值吞吐量</div>
          <div class="summary-value">{{ peakThroughput }}/s</div>
          <div class="summary-change positive">较昨日 +8.3%</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="summary-content">
          <div class="summary-title">错误率</div>
          <div class="summary-value">{{ errorRate }}%</div>
          <div class="summary-change negative">较昨日 +0.2%</div>
        </div>
      </div>
      
      <div class="summary-card">
        <div class="summary-icon">
          <i class="fas fa-server"></i>
        </div>
        <div class="summary-content">
          <div class="summary-title">资源利用率</div>
          <div class="summary-value">{{ resourceUtilization }}%</div>
          <div class="summary-change neutral">较昨日 0%</div>
        </div>
      </div>
    </div>
    
    <!-- 性能洞察 -->
    <div class="analysis-insights">
      <div class="insights-header">
        <h3>性能洞察与建议</h3>
        <div class="insights-filter">
          <select v-model="insightFilter" @change="filterInsights">
            <option value="all">全部洞察</option>
            <option value="critical">关键问题</option>
            <option value="optimization">优化建议</option>
            <option value="trend">趋势分析</option>
          </select>
        </div>
      </div>
      
      <div class="insights-list">
        <div 
          v-for="insight in filteredInsights" 
          :key="insight.id"
          :class="['insight-card', insight.type]"
        >
          <div class="insight-icon">
            <i :class="insight.icon"></i>
          </div>
          <div class="insight-content">
            <h4>{{ insight.title }}</h4>
            <p>{{ insight.description }}</p>
            <div class="insight-actions" v-if="insight.actions">
              <button 
                v-for="action in insight.actions" 
                :key="action.id"
                class="action-btn"
                @click="executeAction(action)"
              >
                {{ action.label }}
              </button>
            </div>
          </div>
          <div class="insight-meta">
            <span class="insight-time">{{ insight.timestamp }}</span>
            <span :class="['insight-priority', insight.priority]">
              {{ getPriorityText(insight.priority) }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 性能分析组件
 * 提供详细的性能分析功能，包括趋势分析、资源分布和性能洞察
 */
export default {
  name: 'PerformanceAnalysis',
  data() {
    return {
      // 刷新状态
      isRefreshing: false,
      // 过滤器选项
      selectedTimeRange: '24h',
      selectedServiceType: 'all',
      selectedMetricType: 'all',
      insightFilter: 'all',
      // 统计数据
      dataPointsCount: 1440,
      lastUpdateTime: '14:35:22',
      averageResponseTime: 245,
      peakThroughput: '2,456',
      errorRate: 0.3,
      resourceUtilization: 67.8,
      // 性能洞察数据
      insights: [
        {
          id: 1,
          type: 'critical',
          icon: 'fas fa-exclamation-triangle',
          title: '数据库查询性能异常',
          description: '数据库查询响应时间在14:00-16:00期间显著增加，平均响应时间从120ms增加到350ms，建议优化慢查询并检查索引使用情况。',
          priority: 'high',
          timestamp: '2分钟前',
          actions: [
            { id: 1, label: '查看慢查询日志', type: 'view' },
            { id: 2, label: '优化建议', type: 'optimize' }
          ]
        },
        {
          id: 2,
          type: 'optimization',
          icon: 'fas fa-lightbulb',
          title: 'CPU使用率优化建议',
          description: 'Web服务器CPU使用率出现异常峰值，检测到可能的内存泄漏问题。建议重启服务实例并检查应用程序内存管理。',
          priority: 'medium',
          timestamp: '5分钟前',
          actions: [
            { id: 3, label: '重启服务', type: 'restart' },
            { id: 4, label: '内存分析', type: 'analyze' }
          ]
        },
        {
          id: 3,
          type: 'trend',
          icon: 'fas fa-chart-line',
          title: '网络流量趋势分析',
          description: '过去7天网络流量呈上升趋势，峰值时段集中在工作日的9:00-11:00和14:00-16:00，建议考虑负载均衡优化。',
          priority: 'low',
          timestamp: '10分钟前',
          actions: [
            { id: 5, label: '查看详细报告', type: 'report' }
          ]
        },
        {
          id: 4,
          type: 'critical',
          icon: 'fas fa-server',
          title: '磁盘空间预警',
          description: '系统磁盘使用率已达到85%，预计在未来3天内可能达到临界值。建议立即清理临时文件或扩展存储空间。',
          priority: 'high',
          timestamp: '15分钟前',
          actions: [
            { id: 6, label: '清理磁盘', type: 'cleanup' },
            { id: 7, label: '扩展存储', type: 'expand' }
          ]
        }
      ]
    }
  },
  computed: {
    /**
     * 过滤后的洞察列表
     */
    filteredInsights() {
      if (this.insightFilter === 'all') {
        return this.insights
      }
      return this.insights.filter(insight => insight.type === this.insightFilter)
    }
  },
  methods: {
    /**
     * 更新分析数据
     */
    updateAnalysis() {
      console.log('Updating analysis with filters:', {
        timeRange: this.selectedTimeRange,
        serviceType: this.selectedServiceType,
        metricType: this.selectedMetricType
      })
      this.updateCharts()
    },
    
    /**
     * 刷新分析数据
     */
    async refreshAnalysis() {
      this.isRefreshing = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1500))
        this.updateAnalysis()
        this.lastUpdateTime = new Date().toLocaleTimeString()
      } finally {
        this.isRefreshing = false
      }
    },
    
    /**
     * 导出分析报告
     */
    exportReport() {
      console.log('Exporting performance analysis report')
      // 这里应该实现报告导出功能
    },
    
    /**
     * 过滤洞察
     */
    filterInsights() {
      console.log('Filtering insights by:', this.insightFilter)
    },
    
    /**
     * 执行洞察建议的操作
     * @param {Object} action - 操作对象
     */
    executeAction(action) {
      console.log('Executing action:', action)
      // 这里应该实现具体的操作逻辑
    },
    
    /**
     * 获取优先级文本
     * @param {string} priority - 优先级
     * @returns {string} 优先级文本
     */
    getPriorityText(priority) {
      const priorityMap = {
        high: '高优先级',
        medium: '中优先级',
        low: '低优先级'
      }
      return priorityMap[priority] || '未知'
    },
    
    /**
     * 更新图表
     */
    updateCharts() {
      console.log('Updating performance analysis charts')
      // 这里应该根据过滤条件更新图表数据
    },
    
    /**
     * 初始化图表
     */
    initCharts() {
      console.log('Initializing performance analysis charts')
      // 这里可以使用Chart.js或其他图表库初始化图表
    }
  },
  mounted() {
    // 初始化图表
    this.initCharts()
  }
}
</script>

<style scoped>
/* 性能分析容器 */
.performance-analysis {
  padding: 20px;
}

/* 分析过滤器样式 */
.analysis-filters {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 500;
  color: #495057;
  white-space: nowrap;
}

.time-selector,
.service-selector,
.metric-selector {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  min-width: 120px;
}

.filter-actions {
  margin-left: auto;
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.spinning {
  animation: spin 1s linear infinite;
}

/* 分析图表样式 */
.analysis-charts {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
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

.chart-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.chart-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  font-size: 12px;
  color: #6c757d;
}

.distribution-legend {
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

.legend-color.high {
  background: #e74c3c;
}

.legend-color.medium {
  background: #f39c12;
}

.legend-color.low {
  background: #27ae60;
}

.chart-content {
  padding: 20px;
  height: 350px;
}

.chart-content canvas {
  width: 100% !important;
  height: 100% !important;
}

/* 性能统计摘要 */
.performance-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.summary-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #3498db;
}

.summary-content {
  flex: 1;
}

.summary-title {
  font-size: 12px;
  color: #6c757d;
  margin-bottom: 5px;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.summary-change {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 4px;
}

.summary-change.positive {
  background: #d4edda;
  color: #155724;
}

.summary-change.negative {
  background: #f8d7da;
  color: #721c24;
}

.summary-change.neutral {
  background: #f8f9fa;
  color: #6c757d;
}

/* 性能洞察样式 */
.analysis-insights {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.insights-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.insights-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.insights-filter select {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.insights-list {
  padding: 20px;
}

.insight-card {
  display: flex;
  gap: 15px;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid;
}

.insight-card:last-child {
  margin-bottom: 0;
}

.insight-card.critical {
  background: #fff5f5;
  border-left-color: #e74c3c;
}

.insight-card.optimization {
  background: #fffbf0;
  border-left-color: #f39c12;
}

.insight-card.trend {
  background: #f0f8ff;
  border-left-color: #3498db;
}

.insight-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  flex-shrink: 0;
}

.insight-card.critical .insight-icon {
  background: #e74c3c;
  color: white;
}

.insight-card.optimization .insight-icon {
  background: #f39c12;
  color: white;
}

.insight-card.trend .insight-icon {
  background: #3498db;
  color: white;
}

.insight-content {
  flex: 1;
}

.insight-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.insight-content p {
  margin: 0 0 15px 0;
  font-size: 14px;
  color: #495057;
  line-height: 1.5;
}

.insight-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

.insight-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.insight-time {
  font-size: 12px;
  color: #6c757d;
}

.insight-priority {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.insight-priority.high {
  background: #f8d7da;
  color: #721c24;
}

.insight-priority.medium {
  background: #fff3cd;
  color: #856404;
}

.insight-priority.low {
  background: #d1ecf1;
  color: #0c5460;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .analysis-charts {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .performance-analysis {
    padding: 15px;
  }
  
  .analysis-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
    justify-content: center;
  }
  
  .performance-summary {
    grid-template-columns: 1fr;
  }
  
  .insight-card {
    flex-direction: column;
  }
  
  .insight-meta {
    flex-direction: row;
    justify-content: space-between;
  }
}
</style>