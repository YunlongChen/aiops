<!--
  应用监控页面
  显示应用服务状态和性能监控信息
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="application-monitoring">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">应用监控</h1>
        <p class="page-subtitle">实时监控应用服务状态和性能指标</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="refreshData">
          <i class="icon-refresh-cw"></i>
          刷新
        </button>
        <button class="btn btn-primary" @click="showAddApplication">
          <i class="icon-plus"></i>
          添加应用
        </button>
      </div>
    </div>
    
    <!-- 应用概览 -->
    <div class="application-overview">
      <div class="overview-cards">
        <div class="overview-card" v-for="metric in applicationMetrics" :key="metric.key">
          <div class="card-icon" :class="metric.iconClass">
            <i :class="metric.icon"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ metric.value }}</div>
            <div class="card-label">{{ metric.label }}</div>
            <div class="card-change" :class="metric.changeClass">
              <i :class="metric.changeIcon"></i>
              {{ metric.change }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 应用性能图表 -->
    <div class="performance-charts">
      <div class="charts-row">
        <div class="chart-container">
          <BaseChart
            title="响应时间趋势"
            subtitle="应用平均响应时间变化"
            height="300px"
            :loading="responseTimeLoading"
            :has-data="responseTimeData.length > 0"
          >
            <template #header>
              <select v-model="responseTimeRange" class="time-range-select">
                <option value="1h">最近1小时</option>
                <option value="6h">最近6小时</option>
                <option value="24h">最近24小时</option>
                <option value="7d">最近7天</option>
              </select>
            </template>
            <div class="response-time-chart">
              <div class="chart-legend">
                <div class="legend-item" v-for="app in responseTimeApps" :key="app.name">
                  <div class="legend-color" :style="{ backgroundColor: app.color }"></div>
                  <span>{{ app.name }}</span>
                </div>
              </div>
              <div class="chart-lines">
                <svg class="chart-svg" viewBox="0 0 400 200">
                  <g v-for="app in responseTimeApps" :key="app.name">
                    <polyline
                      :points="getResponseTimePoints(app.data)"
                      :stroke="app.color"
                      stroke-width="2"
                      fill="none"
                    />
                  </g>
                </svg>
              </div>
            </div>
          </BaseChart>
        </div>
        
        <div class="chart-container">
          <BaseChart
            title="错误率统计"
            subtitle="应用错误率分布"
            height="300px"
            :loading="errorRateLoading"
            :has-data="errorRateData.length > 0"
          >
            <div class="error-rate-chart">
              <div class="error-rate-grid">
                <div
                  v-for="app in errorRateData"
                  :key="app.name"
                  class="error-rate-item"
                >
                  <div class="app-info">
                    <div class="app-name">{{ app.name }}</div>
                    <div class="app-requests">{{ app.requests }} 请求</div>
                  </div>
                  <div class="error-rate-bar">
                    <div
                      class="error-rate-fill"
                      :style="{ width: app.errorRate + '%' }"
                      :class="getErrorRateClass(app.errorRate)"
                    ></div>
                  </div>
                  <div class="error-rate-value">{{ app.errorRate }}%</div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>
      </div>
    </div>
    
    <!-- 应用列表 -->
    <div class="applications-section">
      <div class="section-header">
        <h2 class="section-title">应用服务</h2>
        <div class="section-filters">
          <select v-model="applicationTypeFilter" class="filter-select">
            <option value="">全部类型</option>
            <option value="web">Web应用</option>
            <option value="api">API服务</option>
            <option value="microservice">微服务</option>
            <option value="database">数据库</option>
          </select>
          <select v-model="applicationStatusFilter" class="filter-select">
            <option value="">全部状态</option>
            <option value="running">运行中</option>
            <option value="stopped">已停止</option>
            <option value="error">错误</option>
            <option value="warning">警告</option>
          </select>
          <div class="search-box">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索应用..."
              class="search-input"
            />
            <i class="icon-search search-icon"></i>
          </div>
        </div>
      </div>
      
      <div class="applications-grid">
        <div
          v-for="app in filteredApplications"
          :key="app.id"
          class="application-card"
          @click="showApplicationDetail(app)"
        >
          <div class="app-header">
            <div class="app-icon" :class="'icon-' + app.type">
              <i :class="getApplicationIcon(app.type)"></i>
            </div>
            <div class="app-info">
              <h3 class="app-name">{{ app.name }}</h3>
              <p class="app-version">v{{ app.version }}</p>
              <p class="app-type">{{ getApplicationTypeLabel(app.type) }}</p>
            </div>
            <StatusBadge :status="app.status" :animated="true" />
          </div>
          
          <div class="app-metrics">
            <div class="metric-row">
              <div class="metric-item">
                <div class="metric-label">CPU使用率</div>
                <div class="metric-value">{{ app.cpu }}%</div>
                <div class="metric-bar">
                  <div
                    class="metric-fill"
                    :style="{ width: app.cpu + '%' }"
                    :class="getMetricClass(app.cpu)"
                  ></div>
                </div>
              </div>
            </div>
            
            <div class="metric-row">
              <div class="metric-item">
                <div class="metric-label">内存使用率</div>
                <div class="metric-value">{{ app.memory }}%</div>
                <div class="metric-bar">
                  <div
                    class="metric-fill"
                    :style="{ width: app.memory + '%' }"
                    :class="getMetricClass(app.memory)"
                  ></div>
                </div>
              </div>
            </div>
            
            <div class="metric-row">
              <div class="metric-item">
                <div class="metric-label">响应时间</div>
                <div class="metric-value">{{ app.responseTime }}ms</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">错误率</div>
                <div class="metric-value" :class="getErrorRateClass(app.errorRate)">
                  {{ app.errorRate }}%
                </div>
              </div>
            </div>
            
            <div class="metric-row">
              <div class="metric-item">
                <div class="metric-label">QPS</div>
                <div class="metric-value">{{ app.qps }}</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">连接数</div>
                <div class="metric-value">{{ app.connections }}</div>
              </div>
            </div>
          </div>
          
          <div class="app-footer">
            <div class="app-uptime">
              <i class="icon-clock"></i>
              运行时间: {{ app.uptime }}
            </div>
            <div class="app-actions">
              <button class="btn-icon" @click.stop="restartApplication(app)" title="重启">
                <i class="icon-refresh-cw"></i>
              </button>
              <button class="btn-icon" @click.stop="viewLogs(app)" title="查看日志">
                <i class="icon-file-text"></i>
              </button>
              <button class="btn-icon" @click.stop="editApplication(app)" title="编辑">
                <i class="icon-edit"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <EmptyState
        v-if="filteredApplications.length === 0"
        icon="icon-layers"
        title="暂无应用服务"
        description="没有找到符合条件的应用服务"
        :actions="[
          { id: 'add', title: '添加应用', icon: 'icon-plus', type: 'primary' },
          { id: 'clear', title: '清除筛选', icon: 'icon-x', type: 'outline' }
        ]"
        @action="handleEmptyAction"
      />
    </div>
  </div>
</template>

<script setup>
/**
 * 应用监控页面组件
 * 显示应用服务状态和性能监控信息
 */
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseChart from '@/components/charts/BaseChart.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()

// 响应式数据
const responseTimeLoading = ref(false)
const errorRateLoading = ref(false)
const responseTimeRange = ref('24h')
const applicationTypeFilter = ref('')
const applicationStatusFilter = ref('')
const searchQuery = ref('')

// 应用指标
const applicationMetrics = reactive([
  {
    key: 'total',
    icon: 'icon-layers',
    iconClass: 'card-icon-blue',
    value: '18',
    label: '应用总数',
    change: '+3',
    changeClass: 'card-change-up',
    changeIcon: 'icon-trending-up'
  },
  {
    key: 'running',
    icon: 'icon-play-circle',
    iconClass: 'card-icon-green',
    value: '15',
    label: '运行中',
    change: '+2',
    changeClass: 'card-change-up',
    changeIcon: 'icon-trending-up'
  },
  {
    key: 'response-time',
    icon: 'icon-zap',
    iconClass: 'card-icon-purple',
    value: '245ms',
    label: '平均响应时间',
    change: '-15ms',
    changeClass: 'card-change-down',
    changeIcon: 'icon-trending-down'
  },
  {
    key: 'error-rate',
    icon: 'icon-alert-triangle',
    iconClass: 'card-icon-orange',
    value: '0.8%',
    label: '错误率',
    change: '+0.2%',
    changeClass: 'card-change-up',
    changeIcon: 'icon-trending-up'
  }
])

// 响应时间应用数据
const responseTimeApps = reactive([
  {
    name: 'Web Portal',
    color: '#3b82f6',
    data: [120, 135, 145, 130, 125, 140, 135, 150, 145, 140]
  },
  {
    name: 'API Gateway',
    color: '#10b981',
    data: [80, 85, 90, 88, 82, 95, 90, 100, 95, 92]
  },
  {
    name: 'User Service',
    color: '#8b5cf6',
    data: [200, 210, 220, 215, 205, 225, 220, 235, 230, 225]
  }
])

// 响应时间数据
const responseTimeData = reactive([
  { time: '00:00', webPortal: 120, apiGateway: 80, userService: 200 },
  { time: '04:00', webPortal: 135, apiGateway: 85, userService: 210 },
  { time: '08:00', webPortal: 145, apiGateway: 90, userService: 220 },
  { time: '12:00', webPortal: 130, apiGateway: 88, userService: 215 },
  { time: '16:00', webPortal: 125, apiGateway: 82, userService: 205 },
  { time: '20:00', webPortal: 140, apiGateway: 95, userService: 225 }
])

// 错误率数据
const errorRateData = reactive([
  { name: 'Web Portal', requests: 15420, errorRate: 0.5 },
  { name: 'API Gateway', requests: 28650, errorRate: 0.3 },
  { name: 'User Service', requests: 12340, errorRate: 1.2 },
  { name: 'Order Service', requests: 8920, errorRate: 0.8 },
  { name: 'Payment Service', requests: 5680, errorRate: 2.1 }
])

// 应用数据
const applications = reactive([
  {
    id: 1,
    name: 'Web Portal',
    version: '2.1.0',
    type: 'web',
    status: 'running',
    cpu: 45,
    memory: 62,
    responseTime: 245,
    errorRate: 0.5,
    qps: 1250,
    connections: 856,
    uptime: '15天 8小时'
  },
  {
    id: 2,
    name: 'API Gateway',
    version: '1.8.2',
    type: 'api',
    status: 'running',
    cpu: 35,
    memory: 48,
    responseTime: 125,
    errorRate: 0.3,
    qps: 2840,
    connections: 1245,
    uptime: '23天 12小时'
  },
  {
    id: 3,
    name: 'User Service',
    version: '3.0.1',
    type: 'microservice',
    status: 'warning',
    cpu: 78,
    memory: 85,
    responseTime: 380,
    errorRate: 1.2,
    qps: 680,
    connections: 324,
    uptime: '8天 4小时'
  },
  {
    id: 4,
    name: 'Order Service',
    version: '2.5.3',
    type: 'microservice',
    status: 'running',
    cpu: 52,
    memory: 68,
    responseTime: 195,
    errorRate: 0.8,
    qps: 920,
    connections: 456,
    uptime: '12天 16小时'
  },
  {
    id: 5,
    name: 'Payment Service',
    version: '1.9.0',
    type: 'microservice',
    status: 'error',
    cpu: 95,
    memory: 92,
    responseTime: 850,
    errorRate: 2.1,
    qps: 180,
    connections: 89,
    uptime: '2天 6小时'
  },
  {
    id: 6,
    name: 'MySQL Database',
    version: '8.0.28',
    type: 'database',
    status: 'running',
    cpu: 25,
    memory: 55,
    responseTime: 45,
    errorRate: 0.1,
    qps: 3200,
    connections: 128,
    uptime: '45天 20小时'
  }
])

// 计算属性
const filteredApplications = computed(() => {
  let filtered = applications
  
  if (applicationTypeFilter.value) {
    filtered = filtered.filter(app => app.type === applicationTypeFilter.value)
  }
  
  if (applicationStatusFilter.value) {
    filtered = filtered.filter(app => app.status === applicationStatusFilter.value)
  }
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(app => 
      app.name.toLowerCase().includes(query) ||
      app.version.toLowerCase().includes(query)
    )
  }
  
  return filtered
})

/**
 * 获取应用类型标签
 */
const getApplicationTypeLabel = (type) => {
  const labels = {
    web: 'Web应用',
    api: 'API服务',
    microservice: '微服务',
    database: '数据库'
  }
  return labels[type] || type
}

/**
 * 获取应用图标
 */
const getApplicationIcon = (type) => {
  const icons = {
    web: 'icon-globe',
    api: 'icon-code',
    microservice: 'icon-layers',
    database: 'icon-database'
  }
  return icons[type] || 'icon-layers'
}

/**
 * 获取错误率样式类
 */
const getErrorRateClass = (errorRate) => {
  if (errorRate >= 2) return 'error-rate-high'
  if (errorRate >= 1) return 'error-rate-medium'
  return 'error-rate-low'
}

/**
 * 获取指标样式类
 */
const getMetricClass = (value) => {
  if (value >= 80) return 'metric-high'
  if (value >= 60) return 'metric-medium'
  return 'metric-low'
}

/**
 * 获取响应时间图表点坐标
 */
const getResponseTimePoints = (data) => {
  const width = 400
  const height = 200
  const padding = 20
  
  const maxValue = Math.max(...data)
  const minValue = Math.min(...data)
  const range = maxValue - minValue || 1
  
  return data.map((value, index) => {
    const x = padding + (index / (data.length - 1)) * (width - 2 * padding)
    const y = height - padding - ((value - minValue) / range) * (height - 2 * padding)
    return `${x},${y}`
  }).join(' ')
}

/**
 * 刷新数据
 */
const refreshData = async () => {
  try {
    console.log('刷新应用监控数据...')
    // 模拟数据更新
    applications.forEach(app => {
      if (app.status !== 'stopped') {
        app.cpu = Math.floor(Math.random() * 100)
        app.memory = Math.floor(Math.random() * 100)
        app.responseTime = Math.floor(Math.random() * 500) + 50
        app.qps = Math.floor(Math.random() * 3000) + 100
      }
    })
  } catch (error) {
    console.error('刷新数据失败:', error)
  }
}

/**
 * 显示添加应用对话框
 */
const showAddApplication = () => {
  console.log('显示添加应用对话框')
  // TODO: 实现添加应用功能
}

/**
 * 显示应用详情
 */
const showApplicationDetail = (app) => {
  console.log('显示应用详情:', app.name)
  // TODO: 跳转到应用详情页面
}

/**
 * 重启应用
 */
const restartApplication = (app) => {
  console.log('重启应用:', app.name)
  // TODO: 实现重启应用功能
}

/**
 * 查看日志
 */
const viewLogs = (app) => {
  console.log('查看应用日志:', app.name)
  // TODO: 跳转到日志页面
}

/**
 * 编辑应用
 */
const editApplication = (app) => {
  console.log('编辑应用:', app.name)
  // TODO: 实现编辑应用功能
}

/**
 * 处理空状态操作
 */
const handleEmptyAction = (action) => {
  switch (action.id) {
    case 'add':
      showAddApplication()
      break
    case 'clear':
      applicationTypeFilter.value = ''
      applicationStatusFilter.value = ''
      searchQuery.value = ''
      break
  }
}

// 定时更新数据
let updateTimer = null
const startDataUpdate = () => {
  updateTimer = setInterval(() => {
    refreshData()
  }, 30000) // 30秒更新一次
}

const stopDataUpdate = () => {
  if (updateTimer) {
    clearInterval(updateTimer)
    updateTimer = null
  }
}

// 生命周期
onMounted(() => {
  startDataUpdate()
})

onUnmounted(() => {
  stopDataUpdate()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.application-monitoring {
  padding: $spacing-lg;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: $spacing-xl;
}

.header-content {
  flex: 1;
}

.page-title {
  margin: 0 0 $spacing-xs 0;
  font-size: 28px;
  font-weight: 700;
  color: $text-color;
}

.page-subtitle {
  margin: 0;
  font-size: 16px;
  color: $text-color-secondary;
}

.header-actions {
  display: flex;
  gap: $spacing-sm;
}

// 应用概览
.application-overview {
  margin-bottom: $spacing-xl;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
}

.overview-card {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: $border-radius;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-md;
  
  i {
    font-size: 20px;
    color: $white;
  }
  
  &.card-icon-blue {
    background: $primary-color;
  }
  
  &.card-icon-green {
    background: $success-color;
  }
  
  &.card-icon-purple {
    background: #8b5cf6;
  }
  
  &.card-icon-orange {
    background: $warning-color;
  }
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 24px;
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

.card-change {
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  
  i {
    margin-right: $spacing-xs;
  }
  
  &.card-change-up {
    color: $success-color;
  }
  
  &.card-change-down {
    color: $error-color;
  }
}

// 性能图表
.performance-charts {
  margin-bottom: $spacing-xl;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: $spacing-lg;
}

.chart-container {
  min-height: 350px;
}

.time-range-select {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  font-size: 13px;
  background: $white;
  color: $text-color;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.response-time-chart {
  padding: $spacing-lg;
  height: 250px;
}

.chart-legend {
  display: flex;
  gap: $spacing-lg;
  margin-bottom: $spacing-lg;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 13px;
  color: $text-color-secondary;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.chart-lines {
  height: 150px;
  position: relative;
}

.chart-svg {
  width: 100%;
  height: 100%;
}

.error-rate-chart {
  padding: $spacing-lg;
  height: 250px;
}

.error-rate-grid {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  height: 100%;
  justify-content: center;
}

.error-rate-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.app-info {
  min-width: 120px;
}

.app-name {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.app-requests {
  font-size: 12px;
  color: $text-color-secondary;
}

.error-rate-bar {
  flex: 1;
  height: 8px;
  background: $border-color-light;
  border-radius: 4px;
  overflow: hidden;
}

.error-rate-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
  
  &.error-rate-low {
    background: $success-color;
  }
  
  &.error-rate-medium {
    background: $warning-color;
  }
  
  &.error-rate-high {
    background: $error-color;
  }
}

.error-rate-value {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
  min-width: 35px;
  text-align: right;
  
  &.error-rate-low {
    color: $success-color;
  }
  
  &.error-rate-medium {
    color: $warning-color;
  }
  
  &.error-rate-high {
    color: $error-color;
  }
}

// 应用列表
.applications-section {
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  background: $background-light;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: $text-color;
}

.section-filters {
  display: flex;
  gap: $spacing-sm;
  align-items: center;
}

.filter-select {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  font-size: 13px;
  background: $white;
  color: $text-color;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.search-box {
  position: relative;
}

.search-input {
  padding: $spacing-xs $spacing-sm $spacing-xs 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  font-size: 13px;
  background: $white;
  color: $text-color;
  width: 200px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
  
  &::placeholder {
    color: $text-color-light;
  }
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: $text-color-light;
  font-size: 14px;
}

.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: $spacing-lg;
  padding: $spacing-lg;
}

.application-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
    border-color: $primary-color;
  }
}

.app-header {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.app-icon {
  width: 50px;
  height: 50px;
  border-radius: $border-radius;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $background-light;
  border: 1px solid $border-color-light;
  
  i {
    font-size: 20px;
    color: $primary-color;
  }
  
  &.icon-web i {
    color: $primary-color;
  }
  
  &.icon-api i {
    color: $success-color;
  }
  
  &.icon-microservice i {
    color: #8b5cf6;
  }
  
  &.icon-database i {
    color: $warning-color;
  }
}

.app-info {
  flex: 1;
}

.app-name {
  margin: 0 0 $spacing-xs 0;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.app-version {
  margin: 0 0 $spacing-xs 0;
  font-size: 14px;
  color: $text-color-secondary;
  font-family: monospace;
}

.app-type {
  margin: 0;
  font-size: 13px;
  color: $text-color-light;
}

.app-metrics {
  margin-bottom: $spacing-md;
}

.metric-row {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-sm;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.metric-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.metric-label {
  font-size: 13px;
  color: $text-color-secondary;
}

.metric-value {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
}

.metric-bar {
  height: 4px;
  background: $border-color-light;
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
  
  &.metric-low {
    background: $success-color;
  }
  
  &.metric-medium {
    background: $warning-color;
  }
  
  &.metric-high {
    background: $error-color;
  }
}

.app-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-uptime {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  color: $text-color-secondary;
  
  i {
    font-size: 12px;
  }
}

.app-actions {
  display: flex;
  gap: $spacing-xs;
}

.btn-icon {
  padding: $spacing-xs;
  border: none;
  background: none;
  color: $text-color-light;
  cursor: pointer;
  border-radius: $border-radius;
  transition: all 0.3s ease;
  
  &:hover {
    background: $background-light;
    color: $text-color;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .applications-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}

@media (max-width: 768px) {
  .application-monitoring {
    padding: $spacing-md;
  }
  
  .page-header {
    flex-direction: column;
    gap: $spacing-md;
    
    .header-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
  
  .overview-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: $spacing-md;
  }
  
  .overview-card {
    padding: $spacing-md;
  }
  
  .applications-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
    padding: $spacing-md;
  }
  
  .application-card {
    padding: $spacing-md;
  }
  
  .section-header {
    flex-direction: column;
    gap: $spacing-md;
    align-items: flex-start;
    
    .section-filters {
      width: 100%;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
  }
  
  .search-input {
    width: 150px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .page-subtitle {
    font-size: 14px;
  }
  
  .card-value {
    font-size: 20px;
  }
  
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-sm;
  }
  
  .app-icon {
    width: 40px;
    height: 40px;
    
    i {
      font-size: 16px;
    }
  }
  
  .section-filters {
    flex-direction: column;
    align-items: stretch;
    
    .search-input {
      width: 100%;
    }
  }
}
</style>