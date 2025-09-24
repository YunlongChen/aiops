<!--
  仪表板页面
  显示系统整体状态和关键指标
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>

  <!-- 侧边栏 -->
<!--  <AppSidebar/>-->

  <div class="dashboard">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">仪表板</h1>
      <p class="page-subtitle">系统整体状态和关键指标概览</p>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-grid">
      <div class="metric-card" v-for="metric in keyMetrics" :key="metric.id">
        <div class="metric-icon" :class="metric.iconClass">
          <i :class="metric.icon"></i>
        </div>
        <div class="metric-content">
          <div class="metric-value">{{ metric.value }}</div>
          <div class="metric-label">{{ metric.label }}</div>
          <div class="metric-change" :class="metric.changeClass">
            <i :class="metric.changeIcon"></i>
            {{ metric.change }}
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-section">
      <div class="charts-row">
        <!-- 系统性能趋势 -->
        <div class="chart-container">
          <BaseChart
              title="系统性能趋势"
              subtitle="CPU、内存、磁盘使用率"
              height="350px"
              :loading="performanceLoading"
              :has-data="performanceData.length > 0"
          >
            <template #header>
              <div class="chart-controls">
                <select v-model="performanceTimeRange" class="time-range-select">
                  <option value="1h">最近1小时</option>
                  <option value="6h">最近6小时</option>
                  <option value="24h">最近24小时</option>
                  <option value="7d">最近7天</option>
                </select>
              </div>
            </template>
            <div class="performance-chart">
              <!-- 这里将来会集成实际的图表库 -->
              <div class="chart-placeholder">
                <div class="chart-lines">
                  <div class="chart-line cpu" :style="{ height: cpuUsage + '%' }">
                    <span class="line-label">CPU {{ cpuUsage }}%</span>
                  </div>
                  <div class="chart-line memory" :style="{ height: memoryUsage + '%' }">
                    <span class="line-label">内存 {{ memoryUsage }}%</span>
                  </div>
                  <div class="chart-line disk" :style="{ height: diskUsage + '%' }">
                    <span class="line-label">磁盘 {{ diskUsage }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>

        <!-- 服务状态分布 -->
        <div class="chart-container">
          <BaseChart
              title="服务状态分布"
              subtitle="各服务运行状态统计"
              height="350px"
              :loading="serviceLoading"
              :has-data="serviceData.length > 0"
          >
            <div class="service-chart">
              <div class="service-stats">
                <div class="stat-item" v-for="stat in serviceStats" :key="stat.status">
                  <div class="stat-color" :style="{ backgroundColor: stat.color }"></div>
                  <div class="stat-info">
                    <div class="stat-count">{{ stat.count }}</div>
                    <div class="stat-label">{{ stat.label }}</div>
                  </div>
                </div>
              </div>
              <div class="service-pie">
                <!-- 饼图占位符 -->
                <div class="pie-placeholder">
                  <div class="pie-center">
                    <div class="total-services">{{ totalServices }}</div>
                    <div class="total-label">总服务数</div>
                  </div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>
      </div>

      <div class="charts-row">
        <!-- 告警趋势 -->
        <div class="chart-container">
          <BaseChart
              title="告警趋势"
              subtitle="最近24小时告警数量变化"
              height="300px"
              :loading="alertLoading"
              :has-data="alertData.length > 0"
          >
            <div class="alert-chart">
              <div class="alert-timeline">
                <div class="timeline-item" v-for="(item, index) in alertTimeline" :key="index">
                  <div class="timeline-time">{{ item.time }}</div>
                  <div class="timeline-bar">
                    <div class="bar-critical" :style="{ height: item.critical * 2 + 'px' }"></div>
                    <div class="bar-warning" :style="{ height: item.warning * 2 + 'px' }"></div>
                    <div class="bar-info" :style="{ height: item.info * 2 + 'px' }"></div>
                  </div>
                  <div class="timeline-count">{{ item.total }}</div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>

        <!-- 网络流量 -->
        <div class="chart-container">
          <BaseChart
              title="网络流量"
              subtitle="入站和出站流量监控"
              height="300px"
              :loading="networkLoading"
              :has-data="networkData.length > 0"
          >
            <div class="network-chart">
              <div class="traffic-stats">
                <div class="traffic-item">
                  <div class="traffic-label">入站流量</div>
                  <div class="traffic-value">{{ inboundTraffic }} MB/s</div>
                  <div class="traffic-bar">
                    <div class="bar-fill inbound" :style="{ width: inboundPercent + '%' }"></div>
                  </div>
                </div>
                <div class="traffic-item">
                  <div class="traffic-label">出站流量</div>
                  <div class="traffic-value">{{ outboundTraffic }} MB/s</div>
                  <div class="traffic-bar">
                    <div class="bar-fill outbound" :style="{ width: outboundPercent + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="actions-grid">
        <div class="action-card" v-for="action in quickActions" :key="action.id" @click="handleQuickAction(action)">
          <div class="action-icon" :class="action.iconClass">
            <i :class="action.icon"></i>
          </div>
          <div class="action-content">
            <div class="action-title">{{ action.title }}</div>
            <div class="action-description">{{ action.description }}</div>
          </div>
          <div class="action-arrow">
            <i class="icon-chevron-right"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 仪表板页面组件
 * 显示系统整体状态和关键指标
 */
import {ref, reactive, computed, onMounted, onUnmounted} from 'vue'
import {useRouter} from 'vue-router'
import BaseChart from '@/components/charts/BaseChart.vue'
import AppSidebar from "@components/layout/AppSidebar.vue";

const router = useRouter()

// 响应式数据
const performanceLoading = ref(false)
const serviceLoading = ref(false)
const alertLoading = ref(false)
const networkLoading = ref(false)

const performanceTimeRange = ref('24h')
const performanceData = ref([])
const serviceData = ref([])
const alertData = ref([])
const networkData = ref([])

// 模拟数据
const cpuUsage = ref(65)
const memoryUsage = ref(78)
const diskUsage = ref(45)
const inboundTraffic = ref(125.6)
const outboundTraffic = ref(89.3)

// 关键指标
const keyMetrics = reactive([
  {
    id: 'servers',
    icon: 'icon-server',
    iconClass: 'metric-icon-blue',
    value: '156',
    label: '在线服务器',
    change: '+2.5%',
    changeClass: 'metric-change-up',
    changeIcon: 'icon-trending-up'
  },
  {
    id: 'services',
    icon: 'icon-layers',
    iconClass: 'metric-icon-green',
    value: '89',
    label: '运行服务',
    change: '+1.2%',
    changeClass: 'metric-change-up',
    changeIcon: 'icon-trending-up'
  },
  {
    id: 'alerts',
    icon: 'icon-alert-triangle',
    iconClass: 'metric-icon-orange',
    value: '23',
    label: '活跃告警',
    change: '-15.3%',
    changeClass: 'metric-change-down',
    changeIcon: 'icon-trending-down'
  },
  {
    id: 'uptime',
    icon: 'icon-clock',
    iconClass: 'metric-icon-purple',
    value: '99.9%',
    label: '系统可用性',
    change: '+0.1%',
    changeClass: 'metric-change-up',
    changeIcon: 'icon-trending-up'
  }
])

// 服务状态统计
const serviceStats = reactive([
  {status: 'running', label: '正常', count: 67, color: '#10b981'},
  {status: 'warning', label: '警告', count: 15, color: '#f59e0b'},
  {status: 'error', label: '异常', count: 5, color: '#ef4444'},
  {status: 'stopped', label: '停止', count: 2, color: '#6b7280'}
])

// 告警时间线数据
const alertTimeline = reactive([
  {time: '00:00', critical: 2, warning: 5, info: 8, total: 15},
  {time: '04:00', critical: 1, warning: 3, info: 6, total: 10},
  {time: '08:00', critical: 3, warning: 7, info: 12, total: 22},
  {time: '12:00', critical: 1, warning: 4, info: 9, total: 14},
  {time: '16:00', critical: 2, warning: 6, info: 11, total: 19},
  {time: '20:00', critical: 1, warning: 2, info: 5, total: 8}
])

// 快速操作
const quickActions = reactive([
  {
    id: 'server-monitor',
    icon: 'icon-monitor',
    iconClass: 'action-icon-blue',
    title: '服务器监控',
    description: '查看服务器详细状态'
  },
  {
    id: 'alert-manage',
    icon: 'icon-bell',
    iconClass: 'action-icon-orange',
    title: '告警管理',
    description: '处理和配置告警规则'
  },
  {
    id: 'log-analysis',
    icon: 'icon-file-text',
    iconClass: 'action-icon-green',
    title: '日志分析',
    description: '查看和分析系统日志'
  },
  {
    id: 'performance-tune',
    icon: 'icon-zap',
    iconClass: 'action-icon-purple',
    title: '性能调优',
    description: '系统性能优化建议'
  }
])

// 计算属性
const totalServices = computed(() => {
  return serviceStats.reduce((total, stat) => total + stat.count, 0)
})

const inboundPercent = computed(() => {
  return Math.min((inboundTraffic.value / 200) * 100, 100)
})

const outboundPercent = computed(() => {
  return Math.min((outboundTraffic.value / 200) * 100, 100)
})

/**
 * 处理快速操作点击
 */
const handleQuickAction = (action) => {
  switch (action.id) {
    case 'server-monitor':
      router.push('/monitoring/infrastructure/servers')
      break
    case 'alert-manage':
      router.push('/alerts/rules')
      break
    case 'log-analysis':
      router.push('/monitoring/logs')
      break
    case 'performance-tune':
      router.push('/monitoring/performance')
      break
    default:
      console.log('Quick action:', action.id)
  }
}

/**
 * 加载仪表板数据
 */
const loadDashboardData = async () => {
  try {
    performanceLoading.value = true
    serviceLoading.value = true
    alertLoading.value = true
    networkLoading.value = true

    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 模拟数据加载
    performanceData.value = Array.from({length: 24}, (_, i) => ({
      time: i,
      cpu: Math.random() * 100,
      memory: Math.random() * 100,
      disk: Math.random() * 100
    }))

    serviceData.value = serviceStats
    alertData.value = alertTimeline
    networkData.value = Array.from({length: 24}, (_, i) => ({
      time: i,
      inbound: Math.random() * 200,
      outbound: Math.random() * 200
    }))

  } catch (error) {
    console.error('加载仪表板数据失败:', error)
  } finally {
    performanceLoading.value = false
    serviceLoading.value = false
    alertLoading.value = false
    networkLoading.value = false
  }
}

/**
 * 定时更新数据
 */
let updateTimer = null
const startDataUpdate = () => {
  updateTimer = setInterval(() => {
    // 模拟实时数据更新
    cpuUsage.value = Math.floor(Math.random() * 100)
    memoryUsage.value = Math.floor(Math.random() * 100)
    diskUsage.value = Math.floor(Math.random() * 100)
    inboundTraffic.value = Math.floor(Math.random() * 200 * 100) / 100
    outboundTraffic.value = Math.floor(Math.random() * 200 * 100) / 100
  }, 5000)
}

const stopDataUpdate = () => {
  if (updateTimer) {
    clearInterval(updateTimer)
    updateTimer = null
  }
}

// 生命周期
onMounted(() => {
  loadDashboardData()
  startDataUpdate()
})

onUnmounted(() => {
  stopDataUpdate()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.dashboard {
  padding: $spacing-lg;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: $spacing-xl;
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

// 关键指标卡片
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.metric-card {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
}

.metric-icon {
  width: 60px;
  height: 60px;
  border-radius: $border-radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-lg;

  i {
    font-size: 24px;
    color: $white;
  }

  &.metric-icon-blue {
    background: linear-gradient(135deg, $primary-color, lighten($primary-color, 10%));
  }

  &.metric-icon-green {
    background: linear-gradient(135deg, $success-color, lighten($success-color, 10%));
  }

  &.metric-icon-orange {
    background: linear-gradient(135deg, $warning-color, lighten($warning-color, 10%));
  }

  &.metric-icon-purple {
    background: linear-gradient(135deg, #8b5cf6, lighten(#8b5cf6, 10%));
  }
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 32px;
  font-weight: 700;
  color: $text-color;
  line-height: 1;
  margin-bottom: $spacing-xs;
}

.metric-label {
  font-size: 14px;
  color: $text-color-secondary;
  margin-bottom: $spacing-xs;
}

.metric-change {
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;

  i {
    margin-right: $spacing-xs;
  }

  &.metric-change-up {
    color: $success-color;
  }

  &.metric-change-down {
    color: $error-color;
  }
}

// 图表区域
.charts-section {
  margin-bottom: $spacing-xl;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-lg;

  &:last-child {
    margin-bottom: 0;
  }
}

.chart-container {
  min-height: 400px;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
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

// 图表占位符样式
.chart-placeholder {
  height: 250px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: $spacing-lg;
}

.chart-lines {
  display: flex;
  align-items: flex-end;
  gap: $spacing-lg;
  height: 200px;
}

.chart-line {
  width: 60px;
  border-radius: $border-radius $border-radius 0 0;
  position: relative;
  transition: height 0.3s ease;

  &.cpu {
    background: linear-gradient(to top, $primary-color, lighten($primary-color, 20%));
  }

  &.memory {
    background: linear-gradient(to top, $success-color, lighten($success-color, 20%));
  }

  &.disk {
    background: linear-gradient(to top, $warning-color, lighten($warning-color, 20%));
  }
}

.line-label {
  position: absolute;
  top: -25px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: $text-color-secondary;
  white-space: nowrap;
}

.service-chart {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-lg;
  height: 250px;
}

.service-stats {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.stat-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.stat-info {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.stat-count {
  font-size: 18px;
  font-weight: 600;
  color: $text-color;
  min-width: 30px;
}

.stat-label {
  font-size: 14px;
  color: $text-color-secondary;
}

.service-pie {
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-placeholder {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  border: 20px solid $border-color-light;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  background: $background-color-light;
}

.total-services {
  font-size: 32px;
  font-weight: 700;
  color: $text-color;
}

.total-label {
  font-size: 12px;
  color: $text-color-secondary;
}

.alert-chart {
  padding: $spacing-lg;
  height: 200px;
}

.alert-timeline {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 100%;
  gap: $spacing-sm;
}

.timeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
}

.timeline-time {
  font-size: 12px;
  color: $text-color-secondary;
  margin-bottom: $spacing-xs;
}

.timeline-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  width: 30px;
  justify-content: flex-end;
  gap: 1px;
}

.bar-critical,
.bar-warning,
.bar-info {
  width: 100%;
  border-radius: 2px;
  min-height: 2px;
}

.bar-critical {
  background: $error-color;
}

.bar-warning {
  background: $warning-color;
}

.bar-info {
  background: $info-color;
}

.timeline-count {
  font-size: 12px;
  font-weight: 500;
  color: $text-color;
  margin-top: $spacing-xs;
}

.network-chart {
  padding: $spacing-lg;
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: $spacing-lg;
}

.traffic-item {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.traffic-label {
  font-size: 14px;
  color: $text-color-secondary;
}

.traffic-value {
  font-size: 24px;
  font-weight: 600;
  color: $text-color;
}

.traffic-bar {
  height: 8px;
  background: $border-color-light;
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;

  &.inbound {
    background: linear-gradient(90deg, $primary-color, lighten($primary-color, 20%));
  }

  &.outbound {
    background: linear-gradient(90deg, $success-color, lighten($success-color, 20%));
  }
}

// 快速操作
.section-title {
  margin: 0 0 $spacing-lg 0;
  font-size: 20px;
  font-weight: 600;
  color: $text-color;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: $spacing-lg;
}

.action-card {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
    border-color: $primary-color;
  }
}

.action-icon {
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

  &.action-icon-blue {
    background: $primary-color;
  }

  &.action-icon-orange {
    background: $warning-color;
  }

  &.action-icon-green {
    background: $success-color;
  }

  &.action-icon-purple {
    background: #8b5cf6;
  }
}

.action-content {
  flex: 1;
}

.action-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.action-description {
  font-size: 14px;
  color: $text-color-secondary;
}

.action-arrow {
  color: $text-color-secondary;
  font-size: 16px;
}

// 响应式设计
@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: $spacing-md;
  }

  .metrics-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }

  .metric-card {
    padding: $spacing-md;
  }

  .metric-icon {
    width: 50px;
    height: 50px;
    margin-right: $spacing-md;

    i {
      font-size: 20px;
    }
  }

  .metric-value {
    font-size: 24px;
  }

  .actions-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }

  .action-card {
    padding: $spacing-md;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }

  .page-subtitle {
    font-size: 14px;
  }

  .metric-value {
    font-size: 20px;
  }

  .chart-lines {
    gap: $spacing-sm;
  }

  .chart-line {
    width: 40px;
  }
}
</style>