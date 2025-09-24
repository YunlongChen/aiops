<!--
  健康监控页面
  系统健康状态实时监控和诊断
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="health-monitoring">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">健康监控</h1>
          <p class="page-description">系统健康状态实时监控和智能诊断</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="exportReport">
            <i class="icon-download"></i>
            导出报告
          </button>
          <button class="btn btn-outline" @click="runDiagnosis">
            <i class="icon-activity"></i>
            运行诊断
          </button>
          <button class="btn btn-primary" @click="refreshData">
            <i class="icon-refresh-cw"></i>
            刷新数据
          </button>
        </div>
      </div>
    </div>

    <!-- 系统健康概览 -->
    <div class="health-overview">
      <div class="overview-grid">
        <div class="overview-card overall-health" :class="overallHealthStatus">
          <div class="card-icon">
            <i class="icon-heart"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ healthStats.overallScore }}</div>
            <div class="card-label">整体健康度</div>
            <div class="card-status" :class="overallHealthStatus">
              {{ getHealthStatusText(overallHealthStatus) }}
            </div>
          </div>
        </div>
        <div class="overview-card services">
          <div class="card-icon">
            <i class="icon-server"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ healthStats.healthyServices }}/{{ healthStats.totalServices }}</div>
            <div class="card-label">健康服务</div>
            <div class="card-trend" :class="getServiceTrendClass()">
              <i :class="getServiceTrendIcon()"></i>
              {{ healthStats.serviceChangeText }}
            </div>
          </div>
        </div>
        <div class="overview-card alerts">
          <div class="card-icon">
            <i class="icon-alert-triangle"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ healthStats.activeAlerts }}</div>
            <div class="card-label">活跃告警</div>
            <div class="card-trend" :class="getAlertTrendClass()">
              <i :class="getAlertTrendIcon()"></i>
              {{ healthStats.alertChangeText }}
            </div>
          </div>
        </div>
        <div class="overview-card uptime">
          <div class="card-icon">
            <i class="icon-clock"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ healthStats.uptime }}%</div>
            <div class="card-label">系统可用性</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +0.2% 本周
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时监控面板 -->
    <div class="monitoring-panel">
      <div class="panel-header">
        <h2 class="panel-title">实时监控</h2>
        <div class="panel-controls">
          <select v-model="selectedTimeRange" class="time-range-select">
            <option value="1h">最近1小时</option>
            <option value="6h">最近6小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
          </select>
          <button class="control-btn" @click="toggleAutoRefresh">
            <i :class="autoRefresh ? 'icon-pause' : 'icon-play'"></i>
            {{ autoRefresh ? '暂停' : '开始' }}
          </button>
        </div>
      </div>
      
      <div class="monitoring-grid">
        <!-- 系统资源监控 -->
        <div class="monitor-card system-resources">
          <div class="card-header">
            <h3 class="card-title">系统资源</h3>
            <div class="card-actions">
              <button class="action-btn" @click="viewResourceDetails">
                <i class="icon-external-link"></i>
              </button>
            </div>
          </div>
          <div class="card-content">
            <div class="resource-metrics">
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">CPU使用率</span>
                  <span class="metric-value" :class="getCpuStatusClass()">{{ systemMetrics.cpu }}%</span>
                </div>
                <div class="metric-bar">
                  <div class="bar-fill" :style="{ width: systemMetrics.cpu + '%' }" :class="getCpuStatusClass()"></div>
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">内存使用率</span>
                  <span class="metric-value" :class="getMemoryStatusClass()">{{ systemMetrics.memory }}%</span>
                </div>
                <div class="metric-bar">
                  <div class="bar-fill" :style="{ width: systemMetrics.memory + '%' }" :class="getMemoryStatusClass()"></div>
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">磁盘使用率</span>
                  <span class="metric-value" :class="getDiskStatusClass()">{{ systemMetrics.disk }}%</span>
                </div>
                <div class="metric-bar">
                  <div class="bar-fill" :style="{ width: systemMetrics.disk + '%' }" :class="getDiskStatusClass()"></div>
                </div>
              </div>
              <div class="metric-item">
                <div class="metric-header">
                  <span class="metric-name">网络流量</span>
                  <span class="metric-value">{{ systemMetrics.network }} MB/s</span>
                </div>
                <div class="network-info">
                  <span class="network-in">↓ {{ systemMetrics.networkIn }} MB/s</span>
                  <span class="network-out">↑ {{ systemMetrics.networkOut }} MB/s</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 服务健康状态 -->
        <div class="monitor-card service-health">
          <div class="card-header">
            <h3 class="card-title">服务健康</h3>
            <div class="card-actions">
              <button class="action-btn" @click="viewServiceDetails">
                <i class="icon-external-link"></i>
              </button>
            </div>
          </div>
          <div class="card-content">
            <div class="service-list">
              <div 
                class="service-item"
                v-for="service in services"
                :key="service.id"
                :class="service.status"
              >
                <div class="service-info">
                  <div class="service-name">{{ service.name }}</div>
                  <div class="service-type">{{ service.type }}</div>
                </div>
                <div class="service-metrics">
                  <div class="metric">
                    <span class="metric-label">响应时间</span>
                    <span class="metric-value">{{ service.responseTime }}ms</span>
                  </div>
                  <div class="metric">
                    <span class="metric-label">错误率</span>
                    <span class="metric-value" :class="getErrorRateClass(service.errorRate)">
                      {{ service.errorRate }}%
                    </span>
                  </div>
                </div>
                <div class="service-status">
                  <span class="status-indicator" :class="service.status"></span>
                  <span class="status-text">{{ getServiceStatusText(service.status) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 性能指标 -->
        <div class="monitor-card performance-metrics">
          <div class="card-header">
            <h3 class="card-title">性能指标</h3>
            <div class="card-actions">
              <select v-model="selectedMetric" class="metric-select">
                <option value="response_time">响应时间</option>
                <option value="throughput">吞吐量</option>
                <option value="error_rate">错误率</option>
                <option value="availability">可用性</option>
              </select>
            </div>
          </div>
          <div class="card-content">
            <div class="performance-chart">
              <div class="chart-placeholder">
                <i class="icon-trending-up"></i>
                <span>性能趋势图表</span>
              </div>
            </div>
            <div class="performance-summary">
              <div class="summary-item">
                <span class="summary-label">平均值</span>
                <span class="summary-value">{{ performanceMetrics.average }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">最大值</span>
                <span class="summary-value">{{ performanceMetrics.max }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">最小值</span>
                <span class="summary-value">{{ performanceMetrics.min }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 告警信息 -->
        <div class="monitor-card alert-info">
          <div class="card-header">
            <h3 class="card-title">最新告警</h3>
            <div class="card-actions">
              <button class="action-btn" @click="viewAllAlerts">
                <i class="icon-external-link"></i>
              </button>
            </div>
          </div>
          <div class="card-content">
            <div class="alert-list">
              <div 
                class="alert-item"
                v-for="alert in recentAlerts"
                :key="alert.id"
                :class="alert.level"
              >
                <div class="alert-icon">
                  <i :class="getAlertIcon(alert.level)"></i>
                </div>
                <div class="alert-content">
                  <div class="alert-title">{{ alert.title }}</div>
                  <div class="alert-description">{{ alert.description }}</div>
                  <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
                </div>
                <div class="alert-actions">
                  <button class="alert-action" @click="acknowledgeAlert(alert)">
                    <i class="icon-check"></i>
                  </button>
                  <button class="alert-action" @click="viewAlertDetails(alert)">
                    <i class="icon-eye"></i>
                  </button>
                </div>
              </div>
            </div>
            <div class="alert-summary" v-if="recentAlerts.length === 0">
              <i class="icon-check-circle"></i>
              <span>暂无活跃告警</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 健康检查结果 -->
    <div class="health-checks">
      <div class="section-header">
        <h2 class="section-title">健康检查</h2>
        <div class="section-actions">
          <button class="btn btn-outline" @click="configureChecks">
            <i class="icon-settings"></i>
            配置检查
          </button>
          <button class="btn btn-primary" @click="runAllChecks">
            <i class="icon-play"></i>
            运行所有检查
          </button>
        </div>
      </div>
      
      <div class="checks-grid">
        <div 
          class="check-card"
          v-for="check in healthChecks"
          :key="check.id"
          :class="check.status"
        >
          <div class="check-header">
            <div class="check-info">
              <div class="check-name">{{ check.name }}</div>
              <div class="check-category">{{ check.category }}</div>
            </div>
            <div class="check-status">
              <span class="status-indicator" :class="check.status"></span>
              <span class="status-text">{{ getCheckStatusText(check.status) }}</span>
            </div>
          </div>
          
          <div class="check-content">
            <div class="check-description">{{ check.description }}</div>
            
            <div class="check-results" v-if="check.results">
              <div class="result-item" v-for="result in check.results" :key="result.key">
                <span class="result-key">{{ result.key }}:</span>
                <span class="result-value" :class="result.status">{{ result.value }}</span>
              </div>
            </div>
            
            <div class="check-metrics">
              <div class="metric">
                <span class="metric-label">执行时间</span>
                <span class="metric-value">{{ check.executionTime }}ms</span>
              </div>
              <div class="metric">
                <span class="metric-label">最后检查</span>
                <span class="metric-value">{{ formatTime(check.lastCheck) }}</span>
              </div>
            </div>
          </div>
          
          <div class="check-actions">
            <button class="check-action" @click="runSingleCheck(check)">
              <i class="icon-play"></i>
              运行
            </button>
            <button class="check-action" @click="viewCheckHistory(check)">
              <i class="icon-clock"></i>
              历史
            </button>
            <button class="check-action" @click="configureCheck(check)">
              <i class="icon-settings"></i>
              配置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 诊断建议 -->
    <div class="diagnosis-suggestions" v-if="diagnosticSuggestions.length > 0">
      <div class="section-header">
        <h2 class="section-title">诊断建议</h2>
        <div class="section-actions">
          <button class="btn btn-outline" @click="dismissAllSuggestions">
            <i class="icon-x"></i>
            忽略全部
          </button>
        </div>
      </div>
      
      <div class="suggestions-list">
        <div 
          class="suggestion-card"
          v-for="suggestion in diagnosticSuggestions"
          :key="suggestion.id"
          :class="suggestion.priority"
        >
          <div class="suggestion-header">
            <div class="suggestion-icon">
              <i :class="getSuggestionIcon(suggestion.type)"></i>
            </div>
            <div class="suggestion-info">
              <div class="suggestion-title">{{ suggestion.title }}</div>
              <div class="suggestion-category">{{ suggestion.category }}</div>
            </div>
            <div class="suggestion-priority">
              <span class="priority-badge" :class="suggestion.priority">
                {{ getPriorityText(suggestion.priority) }}
              </span>
            </div>
          </div>
          
          <div class="suggestion-content">
            <div class="suggestion-description">{{ suggestion.description }}</div>
            
            <div class="suggestion-details" v-if="suggestion.details">
              <div class="detail-item" v-for="detail in suggestion.details" :key="detail.key">
                <strong>{{ detail.key }}:</strong> {{ detail.value }}
              </div>
            </div>
            
            <div class="suggestion-actions">
              <button class="suggestion-action primary" @click="applySuggestion(suggestion)">
                <i class="icon-check"></i>
                应用建议
              </button>
              <button class="suggestion-action" @click="viewSuggestionDetails(suggestion)">
                <i class="icon-eye"></i>
                查看详情
              </button>
              <button class="suggestion-action" @click="dismissSuggestion(suggestion)">
                <i class="icon-x"></i>
                忽略
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 健康监控页面组件
 * 系统健康状态实时监控和诊断
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 响应式数据
const selectedTimeRange = ref('1h')
const selectedMetric = ref('response_time')
const autoRefresh = ref(true)
const refreshInterval = ref(null)

// 健康统计数据
const healthStats = ref({
  overallScore: 92,
  totalServices: 24,
  healthyServices: 22,
  activeAlerts: 3,
  uptime: 99.8,
  serviceChangeText: '+2个恢复',
  alertChangeText: '-1个解决'
})

// 系统指标
const systemMetrics = ref({
  cpu: 45,
  memory: 68,
  disk: 32,
  network: 125.6,
  networkIn: 78.3,
  networkOut: 47.3
})

// 服务列表
const services = ref([
  {
    id: 1,
    name: 'Web服务器',
    type: 'HTTP服务',
    status: 'healthy',
    responseTime: 245,
    errorRate: 0.1
  },
  {
    id: 2,
    name: '数据库服务',
    type: 'MySQL',
    status: 'healthy',
    responseTime: 12,
    errorRate: 0.0
  },
  {
    id: 3,
    name: '缓存服务',
    type: 'Redis',
    status: 'warning',
    responseTime: 8,
    errorRate: 0.3
  },
  {
    id: 4,
    name: '消息队列',
    type: 'RabbitMQ',
    status: 'healthy',
    responseTime: 15,
    errorRate: 0.0
  },
  {
    id: 5,
    name: 'API网关',
    type: 'Gateway',
    status: 'critical',
    responseTime: 1250,
    errorRate: 2.1
  }
])

// 性能指标
const performanceMetrics = ref({
  average: '245ms',
  max: '1.2s',
  min: '12ms'
})

// 最新告警
const recentAlerts = ref([
  {
    id: 1,
    level: 'critical',
    title: 'API网关响应超时',
    description: '网关服务响应时间超过1秒，影响用户体验',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: 2,
    level: 'warning',
    title: '缓存命中率下降',
    description: 'Redis缓存命中率降至85%以下',
    timestamp: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: 3,
    level: 'info',
    title: '磁盘空间预警',
    description: '系统磁盘使用率达到80%',
    timestamp: new Date(Date.now() - 30 * 60 * 1000)
  }
])

// 健康检查
const healthChecks = ref([
  {
    id: 1,
    name: '数据库连接检查',
    category: '数据库',
    status: 'passed',
    description: '检查数据库连接池状态和响应时间',
    executionTime: 125,
    lastCheck: new Date(Date.now() - 2 * 60 * 1000),
    results: [
      { key: '连接池大小', value: '20/50', status: 'normal' },
      { key: '活跃连接', value: '8', status: 'normal' },
      { key: '平均响应时间', value: '12ms', status: 'good' }
    ]
  },
  {
    id: 2,
    name: '服务端点检查',
    category: 'API',
    status: 'failed',
    description: '检查关键API端点的可用性和性能',
    executionTime: 2340,
    lastCheck: new Date(Date.now() - 1 * 60 * 1000),
    results: [
      { key: '用户API', value: '正常', status: 'good' },
      { key: '订单API', value: '超时', status: 'error' },
      { key: '支付API', value: '正常', status: 'good' }
    ]
  },
  {
    id: 3,
    name: '内存泄漏检查',
    category: '系统',
    status: 'warning',
    description: '检测应用程序内存使用情况和潜在泄漏',
    executionTime: 890,
    lastCheck: new Date(Date.now() - 5 * 60 * 1000),
    results: [
      { key: '堆内存使用', value: '68%', status: 'warning' },
      { key: '垃圾回收频率', value: '正常', status: 'good' },
      { key: '内存增长率', value: '2%/h', status: 'normal' }
    ]
  },
  {
    id: 4,
    name: '安全扫描',
    category: '安全',
    status: 'passed',
    description: '扫描系统安全漏洞和配置问题',
    executionTime: 1560,
    lastCheck: new Date(Date.now() - 10 * 60 * 1000),
    results: [
      { key: '漏洞数量', value: '0', status: 'good' },
      { key: '配置检查', value: '通过', status: 'good' },
      { key: '权限验证', value: '正常', status: 'good' }
    ]
  }
])

// 诊断建议
const diagnosticSuggestions = ref([
  {
    id: 1,
    type: 'performance',
    priority: 'high',
    category: '性能优化',
    title: '优化API网关配置',
    description: 'API网关响应时间过长，建议调整超时设置和连接池配置',
    details: [
      { key: '当前超时设置', value: '30秒' },
      { key: '建议超时设置', value: '10秒' },
      { key: '连接池大小', value: '增加到100' }
    ]
  },
  {
    id: 2,
    type: 'resource',
    priority: 'medium',
    category: '资源管理',
    title: '增加缓存容量',
    description: '缓存命中率下降，建议增加Redis内存配置或优化缓存策略',
    details: [
      { key: '当前内存', value: '2GB' },
      { key: '建议内存', value: '4GB' },
      { key: '命中率目标', value: '>95%' }
    ]
  }
])

// 计算属性
const overallHealthStatus = computed(() => {
  const score = healthStats.value.overallScore
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'warning'
  return 'critical'
})

/**
 * 获取健康状态文本
 */
const getHealthStatusText = (status) => {
  const texts = {
    excellent: '优秀',
    good: '良好',
    warning: '警告',
    critical: '严重'
  }
  return texts[status] || status
}

/**
 * 获取服务趋势样式类
 */
const getServiceTrendClass = () => {
  return 'positive' // 根据实际数据动态计算
}

/**
 * 获取服务趋势图标
 */
const getServiceTrendIcon = () => {
  return 'icon-trending-up' // 根据实际数据动态计算
}

/**
 * 获取告警趋势样式类
 */
const getAlertTrendClass = () => {
  return 'positive' // 根据实际数据动态计算
}

/**
 * 获取告警趋势图标
 */
const getAlertTrendIcon = () => {
  return 'icon-trending-down' // 根据实际数据动态计算
}

/**
 * 获取CPU状态样式类
 */
const getCpuStatusClass = () => {
  const cpu = systemMetrics.value.cpu
  if (cpu >= 90) return 'critical'
  if (cpu >= 80) return 'warning'
  if (cpu >= 70) return 'normal'
  return 'good'
}

/**
 * 获取内存状态样式类
 */
const getMemoryStatusClass = () => {
  const memory = systemMetrics.value.memory
  if (memory >= 90) return 'critical'
  if (memory >= 80) return 'warning'
  if (memory >= 70) return 'normal'
  return 'good'
}

/**
 * 获取磁盘状态样式类
 */
const getDiskStatusClass = () => {
  const disk = systemMetrics.value.disk
  if (disk >= 90) return 'critical'
  if (disk >= 80) return 'warning'
  if (disk >= 70) return 'normal'
  return 'good'
}

/**
 * 获取服务状态文本
 */
const getServiceStatusText = (status) => {
  const texts = {
    healthy: '健康',
    warning: '警告',
    critical: '严重',
    unknown: '未知'
  }
  return texts[status] || status
}

/**
 * 获取错误率样式类
 */
const getErrorRateClass = (rate) => {
  if (rate >= 5) return 'critical'
  if (rate >= 2) return 'warning'
  if (rate >= 1) return 'normal'
  return 'good'
}

/**
 * 获取告警图标
 */
const getAlertIcon = (level) => {
  const icons = {
    critical: 'icon-alert-circle',
    warning: 'icon-alert-triangle',
    info: 'icon-info'
  }
  return icons[level] || 'icon-info'
}

/**
 * 获取检查状态文本
 */
const getCheckStatusText = (status) => {
  const texts = {
    passed: '通过',
    failed: '失败',
    warning: '警告',
    running: '运行中'
  }
  return texts[status] || status
}

/**
 * 获取建议图标
 */
const getSuggestionIcon = (type) => {
  const icons = {
    performance: 'icon-zap',
    resource: 'icon-cpu',
    security: 'icon-shield',
    configuration: 'icon-settings'
  }
  return icons[type] || 'icon-lightbulb'
}

/**
 * 获取优先级文本
 */
const getPriorityText = (priority) => {
  const texts = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

/**
 * 格式化时间
 */
const formatTime = (datetime) => {
  if (!datetime) return '从未'
  
  const now = new Date()
  const diff = now - datetime
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return datetime.toLocaleDateString()
}

/**
 * 切换自动刷新
 */
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

/**
 * 开始自动刷新
 */
const startAutoRefresh = () => {
  refreshInterval.value = setInterval(() => {
    refreshData()
  }, 30000) // 30秒刷新一次
}

/**
 * 停止自动刷新
 */
const stopAutoRefresh = () => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
    refreshInterval.value = null
  }
}

/**
 * 刷新数据
 */
const refreshData = () => {
  console.log('刷新监控数据')
  // 模拟数据更新
  systemMetrics.value.cpu = Math.floor(Math.random() * 100)
  systemMetrics.value.memory = Math.floor(Math.random() * 100)
}

/**
 * 导出报告
 */
const exportReport = () => {
  console.log('导出健康监控报告')
}

/**
 * 运行诊断
 */
const runDiagnosis = () => {
  console.log('运行系统诊断')
}

/**
 * 查看资源详情
 */
const viewResourceDetails = () => {
  console.log('查看系统资源详情')
}

/**
 * 查看服务详情
 */
const viewServiceDetails = () => {
  console.log('查看服务详情')
}

/**
 * 查看所有告警
 */
const viewAllAlerts = () => {
  console.log('查看所有告警')
}

/**
 * 确认告警
 */
const acknowledgeAlert = (alert) => {
  console.log('确认告警:', alert)
}

/**
 * 查看告警详情
 */
const viewAlertDetails = (alert) => {
  console.log('查看告警详情:', alert)
}

/**
 * 配置健康检查
 */
const configureChecks = () => {
  console.log('配置健康检查')
}

/**
 * 运行所有检查
 */
const runAllChecks = () => {
  console.log('运行所有健康检查')
}

/**
 * 运行单个检查
 */
const runSingleCheck = (check) => {
  console.log('运行检查:', check)
}

/**
 * 查看检查历史
 */
const viewCheckHistory = (check) => {
  console.log('查看检查历史:', check)
}

/**
 * 配置检查
 */
const configureCheck = (check) => {
  console.log('配置检查:', check)
}

/**
 * 应用建议
 */
const applySuggestion = (suggestion) => {
  console.log('应用建议:', suggestion)
}

/**
 * 查看建议详情
 */
const viewSuggestionDetails = (suggestion) => {
  console.log('查看建议详情:', suggestion)
}

/**
 * 忽略建议
 */
const dismissSuggestion = (suggestion) => {
  const index = diagnosticSuggestions.value.findIndex(s => s.id === suggestion.id)
  if (index > -1) {
    diagnosticSuggestions.value.splice(index, 1)
  }
}

/**
 * 忽略所有建议
 */
const dismissAllSuggestions = () => {
  diagnosticSuggestions.value = []
}

// 生命周期
onMounted(() => {
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.health-monitoring {
  padding: $spacing-lg;
  background: $background-color;
  min-height: 100vh;
}

// 页面头部
.page-header {
  margin-bottom: $spacing-xl;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: $spacing-lg;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 $spacing-xs 0;
  font-size: 28px;
  font-weight: 700;
  color: $text-color;
}

.page-description {
  margin: 0;
  color: $text-color-secondary;
  font-size: 15px;
}

.header-right {
  display: flex;
  gap: $spacing-md;
}

// 健康概览
.health-overview {
  margin-bottom: $spacing-xl;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
}

.overview-card {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  border-left: 4px solid;
  
  &.overall-health {
    &.excellent {
      border-left-color: $success-color;
      
      .card-icon {
        background: rgba($success-color, 0.1);
        color: $success-color;
      }
    }
    
    &.good {
      border-left-color: $info-color;
      
      .card-icon {
        background: rgba($info-color, 0.1);
        color: $info-color;
      }
    }
    
    &.warning {
      border-left-color: $warning-color;
      
      .card-icon {
        background: rgba($warning-color, 0.1);
        color: $warning-color;
      }
    }
    
    &.critical {
      border-left-color: $danger-color;
      
      .card-icon {
        background: rgba($danger-color, 0.1);
        color: $danger-color;
      }
    }
  }
  
  &.services {
    border-left-color: $primary-color;
    
    .card-icon {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }
  
  &.alerts {
    border-left-color: $warning-color;
    
    .card-icon {
      background: rgba($warning-color, 0.1);
      color: $warning-color;
    }
  }
  
  &.uptime {
    border-left-color: $success-color;
    
    .card-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: $text-color;
  line-height: 1;
  margin-bottom: $spacing-xs;
}

.card-label {
  font-size: 14px;
  color: $text-color-secondary;
  margin-bottom: $spacing-xs;
}

.card-status {
  font-size: 12px;
  font-weight: 500;
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  
  &.excellent {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.good {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
  
  &.warning {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.critical {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
}

.card-trend {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  font-weight: 500;
  
  &.positive {
    color: $success-color;
  }
  
  &.negative {
    color: $danger-color;
  }
  
  &.neutral {
    color: $text-color-light;
  }
}

// 监控面板
.monitoring-panel {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  margin-bottom: $spacing-xl;
  overflow: hidden;
}

.panel-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: $text-color;
}

.panel-controls {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.time-range-select {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  font-size: 13px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.control-btn {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 13px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

.monitoring-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: $spacing-lg;
  padding: $spacing-lg;
}

.monitor-card {
  background: $background-color-light;
  border-radius: $border-radius-md;
  border: 1px solid $border-color-light;
  overflow: hidden;
}

.card-header {
  padding: $spacing-md;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.card-actions {
  display: flex;
  gap: $spacing-xs;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

.metric-select {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color;
  font-size: 12px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.card-content {
  padding: $spacing-md;
}

// 系统资源监控
.resource-metrics {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-name {
  font-size: 13px;
  color: $text-color;
  font-weight: 500;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  
  &.good {
    color: $success-color;
  }
  
  &.normal {
    color: $info-color;
  }
  
  &.warning {
    color: $warning-color;
  }
  
  &.critical {
    color: $danger-color;
  }
}

.metric-bar {
  height: 6px;
  background: $border-color-light;
  border-radius: 3px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  
  &.good {
    background: $success-color;
  }
  
  &.normal {
    background: $info-color;
  }
  
  &.warning {
    background: $warning-color;
  }
  
  &.critical {
    background: $danger-color;
  }
}

.network-info {
  display: flex;
  gap: $spacing-md;
  font-size: 12px;
  color: $text-color-secondary;
}

.network-in,
.network-out {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

// 服务健康状态
.service-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.service-item {
  padding: $spacing-sm;
  border: 1px solid $border-color-light;
  border-radius: $border-radius-sm;
  background: $white;
  border-left: 3px solid;
  
  &.healthy {
    border-left-color: $success-color;
  }
  
  &.warning {
    border-left-color: $warning-color;
  }
  
  &.critical {
    border-left-color: $danger-color;
  }
}

.service-info {
  margin-bottom: $spacing-xs;
}

.service-name {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
}

.service-type {
  font-size: 11px;
  color: $text-color-light;
}

.service-metrics {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-xs;
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.metric-label {
  font-size: 10px;
  color: $text-color-light;
}

.service-status {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  
  &.healthy {
    background: $success-color;
  }
  
  &.warning {
    background: $warning-color;
  }
  
  &.critical {
    background: $danger-color;
  }
  
  &.unknown {
    background: $text-color-light;
  }
}

.status-text {
  font-size: 11px;
  color: $text-color-secondary;
}

// 性能指标
.performance-chart {
  height: 200px;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: $spacing-xs;
  color: $text-color-light;
  margin-bottom: $spacing-md;
  
  i {
    font-size: 32px;
  }
}

.performance-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.summary-label {
  font-size: 11px;
  color: $text-color-light;
}

.summary-value {
  font-size: 14px;
  font-weight: 600;
  color: $text-color;
}

// 告警信息
.alert-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.alert-item {
  display: flex;
  gap: $spacing-sm;
  padding: $spacing-sm;
  border: 1px solid $border-color-light;
  border-radius: $border-radius-sm;
  background: $white;
  border-left: 3px solid;
  
  &.critical {
    border-left-color: $danger-color;
  }
  
  &.warning {
    border-left-color: $warning-color;
  }
  
  &.info {
    border-left-color: $info-color;
  }
}

.alert-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  
  .critical & {
    color: $danger-color;
  }
  
  .warning & {
    color: $warning-color;
  }
  
  .info & {
    color: $info-color;
  }
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
  margin-bottom: 2px;
}

.alert-description {
  font-size: 11px;
  color: $text-color-secondary;
  line-height: 1.3;
  margin-bottom: $spacing-xs;
}

.alert-time {
  font-size: 10px;
  color: $text-color-light;
}

.alert-actions {
  display: flex;
  gap: $spacing-xs;
}

.alert-action {
  width: 20px;
  height: 20px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

.alert-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  padding: $spacing-lg;
  color: $text-color-light;
  
  i {
    font-size: 20px;
    color: $success-color;
  }
}

// 健康检查
.health-checks {
  margin-bottom: $spacing-xl;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: $text-color;
}

.section-actions {
  display: flex;
  gap: $spacing-md;
}

.checks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: $spacing-lg;
}

.check-card {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
  border-left: 4px solid;
  
  &.passed {
    border-left-color: $success-color;
  }
  
  &.failed {
    border-left-color: $danger-color;
  }
  
  &.warning {
    border-left-color: $warning-color;
  }
  
  &.running {
    border-left-color: $info-color;
  }
}

.check-header {
  padding: $spacing-md;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.check-info {
  flex: 1;
}

.check-name {
  font-size: 15px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.check-category {
  font-size: 12px;
  color: $text-color-secondary;
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  display: inline-block;
}

.check-status {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.check-content {
  padding: $spacing-md;
}

.check-description {
  color: $text-color-secondary;
  font-size: 13px;
  line-height: 1.4;
  margin-bottom: $spacing-md;
}

.check-results {
  margin-bottom: $spacing-md;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-xs 0;
  font-size: 12px;
  border-bottom: 1px solid $border-color-light;
  
  &:last-child {
    border-bottom: none;
  }
}

.result-key {
  color: $text-color-secondary;
}

.result-value {
  font-weight: 500;
  
  &.good {
    color: $success-color;
  }
  
  &.normal {
    color: $info-color;
  }
  
  &.warning {
    color: $warning-color;
  }
  
  &.error {
    color: $danger-color;
  }
}

.check-metrics {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.check-actions {
  padding: $spacing-md;
  border-top: 1px solid $border-color-light;
  display: flex;
  gap: $spacing-xs;
}

.check-action {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 11px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

// 诊断建议
.diagnosis-suggestions {
  margin-bottom: $spacing-xl;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.suggestion-card {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
  border-left: 4px solid;
  
  &.high {
    border-left-color: $danger-color;
  }
  
  &.medium {
    border-left-color: $warning-color;
  }
  
  &.low {
    border-left-color: $info-color;
  }
}

.suggestion-header {
  padding: $spacing-md;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.suggestion-icon {
  width: 40px;
  height: 40px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  
  .high & {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  .medium & {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  .low & {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
}

.suggestion-info {
  flex: 1;
}

.suggestion-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.suggestion-category {
  font-size: 12px;
  color: $text-color-secondary;
}

.suggestion-priority {
  display: flex;
  align-items: center;
}

.priority-badge {
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
  
  &.high {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.medium {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.low {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
}

.suggestion-content {
  padding: $spacing-md;
}

.suggestion-description {
  color: $text-color-secondary;
  line-height: 1.5;
  margin-bottom: $spacing-md;
}

.suggestion-details {
  background: $background-color-light;
  border-radius: $border-radius-sm;
  padding: $spacing-sm;
  margin-bottom: $spacing-md;
}

.detail-item {
  font-size: 12px;
  color: $text-color-secondary;
  margin-bottom: $spacing-xs;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  strong {
    color: $text-color;
  }
}

.suggestion-actions {
  display: flex;
  gap: $spacing-sm;
}

.suggestion-action {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.primary {
    background: $primary-color;
    border-color: $primary-color;
    color: $white;
    
    &:hover {
      background: darken($primary-color, 5%);
      border-color: darken($primary-color, 5%);
    }
  }
}

// 按钮样式
.btn {
  padding: $spacing-sm $spacing-md;
  border: 1px solid;
  border-radius: $border-radius-md;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  text-decoration: none;
  
  &.btn-primary {
    background: $primary-color;
    border-color: $primary-color;
    color: $white;
    
    &:hover {
      background: darken($primary-color, 5%);
      border-color: darken($primary-color, 5%);
    }
  }
  
  &.btn-outline {
    background: $white;
    border-color: $border-color;
    color: $text-color;
    
    &:hover {
      border-color: $primary-color;
      color: $primary-color;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .monitoring-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
  
  .checks-grid {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .health-monitoring {
    padding: $spacing-md;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .header-right {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: $spacing-md;
  }
  
  .overview-card {
    padding: $spacing-md;
    flex-direction: column;
    text-align: center;
    gap: $spacing-sm;
  }
  
  .card-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
  
  .card-value {
    font-size: 24px;
  }
  
  .monitoring-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }
  
  .panel-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .panel-controls {
    justify-content: flex-start;
  }
  
  .service-metrics {
    flex-direction: column;
    gap: $spacing-xs;
  }
  
  .performance-summary {
    flex-direction: column;
    gap: $spacing-sm;
  }
  
  .checks-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }
  
  .check-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .check-metrics {
    flex-direction: column;
    gap: $spacing-xs;
  }
  
  .suggestion-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .suggestion-actions {
    flex-wrap: wrap;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .section-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .health-monitoring {
    padding: $spacing-sm;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-card {
    padding: $spacing-sm;
  }
  
  .card-value {
    font-size: 20px;
  }
  
  .panel-header {
    padding: $spacing-sm;
  }
  
  .monitoring-grid {
    padding: $spacing-sm;
  }
  
  .card-header {
    padding: $spacing-sm;
  }
  
  .card-content {
    padding: $spacing-sm;
  }
  
  .check-header {
    padding: $spacing-sm;
  }
  
  .check-content {
    padding: $spacing-sm;
  }
  
  .check-actions {
    padding: $spacing-sm;
    flex-wrap: wrap;
  }
  
  .suggestion-header {
    padding: $spacing-sm;
  }
  
  .suggestion-content {
    padding: $spacing-sm;
  }
  
  .suggestion-actions {
    flex-direction: column;
  }
  
  .btn {
    padding: $spacing-xs $spacing-sm;
    font-size: 12px;
  }
}
</style>