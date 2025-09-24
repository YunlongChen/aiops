<!--
  告警历史记录页面
  显示系统的历史告警记录，支持筛选和搜索
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="alert-history">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">告警历史</h1>
          <p class="page-description">查看和分析系统历史告警记录</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="exportHistory">
            <i class="icon-download"></i>
            导出记录
          </button>
          <button class="btn btn-outline" @click="refreshHistory">
            <i class="icon-refresh-cw"></i>
            刷新
          </button>
        </div>
      </div>
    </div>

    <!-- 历史统计 -->
    <div class="history-stats">
      <div class="stats-grid">
        <div class="stat-card total">
          <div class="stat-icon">
            <i class="icon-activity"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ historyStats.total }}</div>
            <div class="stat-label">总告警数</div>
          </div>
        </div>
        <div class="stat-card resolved">
          <div class="stat-icon">
            <i class="icon-check-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ historyStats.resolved }}</div>
            <div class="stat-label">已解决</div>
          </div>
        </div>
        <div class="stat-card critical">
          <div class="stat-icon">
            <i class="icon-alert-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ historyStats.critical }}</div>
            <div class="stat-label">严重告警</div>
          </div>
        </div>
        <div class="stat-card avg-time">
          <div class="stat-icon">
            <i class="icon-clock"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ historyStats.avgResolveTime }}</div>
            <div class="stat-label">平均解决时间</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">时间范围</label>
          <select v-model="selectedTimeRange" class="filter-select">
            <option value="today">今天</option>
            <option value="week">最近7天</option>
            <option value="month">最近30天</option>
            <option value="quarter">最近3个月</option>
            <option value="custom">自定义</option>
          </select>
        </div>
        <div class="filter-group" v-if="selectedTimeRange === 'custom'">
          <label class="filter-label">开始时间</label>
          <input 
            type="datetime-local" 
            v-model="customStartTime"
            class="filter-input"
          >
        </div>
        <div class="filter-group" v-if="selectedTimeRange === 'custom'">
          <label class="filter-label">结束时间</label>
          <input 
            type="datetime-local" 
            v-model="customEndTime"
            class="filter-input"
          >
        </div>
        <div class="filter-group">
          <label class="filter-label">告警级别</label>
          <select v-model="selectedSeverity" class="filter-select">
            <option value="">全部级别</option>
            <option value="critical">严重</option>
            <option value="warning">警告</option>
            <option value="info">信息</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">告警状态</label>
          <select v-model="selectedStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="resolved">已解决</option>
            <option value="acknowledged">已确认</option>
            <option value="active">活跃</option>
          </select>
        </div>
        <div class="filter-group search-group">
          <div class="search-input">
            <i class="icon-search"></i>
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="搜索告警内容、来源..."
              @input="handleSearch"
            >
            <button v-if="searchQuery" class="clear-btn" @click="clearSearch">
              <i class="icon-x"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 告警历史列表 -->
    <div class="history-list">
      <div class="list-header">
        <div class="view-controls">
          <div class="view-toggle">
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
            >
              <i class="icon-list"></i>
              列表视图
            </button>
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'timeline' }"
              @click="viewMode = 'timeline'"
            >
              <i class="icon-activity"></i>
              时间线视图
            </button>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="table-container">
        <table class="history-table">
          <thead>
            <tr>
              <th class="time-col">触发时间</th>
              <th class="title-col">告警标题</th>
              <th class="source-col">告警来源</th>
              <th class="severity-col">级别</th>
              <th class="status-col">状态</th>
              <th class="duration-col">持续时间</th>
              <th class="actions-col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="alert in filteredHistory" 
              :key="alert.id"
              class="history-row"
            >
              <td class="time-col">
                <div class="time-info">
                  <span class="trigger-time">{{ formatTime(alert.triggeredAt) }}</span>
                  <span class="date-info">{{ formatDate(alert.triggeredAt) }}</span>
                </div>
              </td>
              <td class="title-col">
                <div class="alert-title">
                  <span class="title-text">{{ alert.title }}</span>
                  <span class="alert-message">{{ alert.message }}</span>
                </div>
              </td>
              <td class="source-col">
                <div class="source-info">
                  <span class="source-name">{{ alert.source }}</span>
                  <span class="source-type">{{ alert.sourceType }}</span>
                </div>
              </td>
              <td class="severity-col">
                <StatusBadge 
                  :status="alert.severity" 
                  :variant="getSeverityVariant(alert.severity)"
                />
              </td>
              <td class="status-col">
                <StatusBadge 
                  :status="alert.status" 
                  :variant="getStatusVariant(alert.status)"
                />
              </td>
              <td class="duration-col">
                <div class="duration-info">
                  <span class="duration-text">{{ formatDuration(alert.duration) }}</span>
                  <span class="resolve-time" v-if="alert.resolvedAt">
                    {{ formatTime(alert.resolvedAt) }}
                  </span>
                </div>
              </td>
              <td class="actions-col">
                <div class="action-buttons">
                  <button 
                    class="action-btn"
                    @click="viewAlertDetail(alert)"
                    title="查看详情"
                  >
                    <i class="icon-eye"></i>
                  </button>
                  <button 
                    class="action-btn"
                    @click="viewAlertTimeline(alert)"
                    title="查看时间线"
                  >
                    <i class="icon-activity"></i>
                  </button>
                  <button 
                    class="action-btn"
                    @click="exportAlertReport(alert)"
                    title="导出报告"
                  >
                    <i class="icon-download"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 时间线视图 -->
      <div v-if="viewMode === 'timeline'" class="timeline-container">
        <div class="timeline">
          <div 
            v-for="alert in filteredHistory" 
            :key="alert.id"
            class="timeline-item"
            :class="alert.severity"
          >
            <div class="timeline-marker">
              <i class="timeline-icon" :class="getTimelineIcon(alert.severity)"></i>
            </div>
            <div class="timeline-content">
              <div class="timeline-header">
                <div class="timeline-title">{{ alert.title }}</div>
                <div class="timeline-time">{{ formatTime(alert.triggeredAt) }}</div>
              </div>
              <div class="timeline-body">
                <div class="timeline-message">{{ alert.message }}</div>
                <div class="timeline-meta">
                  <span class="meta-item">
                    <i class="icon-server"></i>
                    {{ alert.source }}
                  </span>
                  <span class="meta-item">
                    <i class="icon-tag"></i>
                    {{ alert.sourceType }}
                  </span>
                  <span class="meta-item">
                    <i class="icon-clock"></i>
                    {{ formatDuration(alert.duration) }}
                  </span>
                </div>
              </div>
              <div class="timeline-footer">
                <StatusBadge 
                  :status="alert.severity" 
                  :variant="getSeverityVariant(alert.severity)"
                />
                <StatusBadge 
                  :status="alert.status" 
                  :variant="getStatusVariant(alert.status)"
                />
                <div class="timeline-actions">
                  <button class="timeline-action-btn" @click="viewAlertDetail(alert)">
                    查看详情
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-if="filteredHistory.length === 0"
        icon="icon-clock"
        title="暂无告警历史"
        description="在选定的时间范围内没有找到告警记录"
        :actions="[
          { text: '重置筛选', action: resetFilters },
          { text: '刷新数据', action: refreshHistory }
        ]"
      />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="filteredHistory.length > 0">
      <div class="pagination-info">
        显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalHistory) }} 条，
        共 {{ totalHistory }} 条记录
      </div>
      <div class="pagination-controls">
        <button 
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <i class="icon-chevron-left"></i>
        </button>
        <span class="pagination-pages">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            class="pagination-page"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </span>
        <button 
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          <i class="icon-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 告警历史记录页面组件
 * 显示系统的历史告警记录，支持筛选和搜索
 */
import { ref, computed, onMounted } from 'vue'
import StatusBadge from '@components/common/StatusBadge.vue'
import EmptyState from '@components/common/EmptyState.vue'

// 响应式数据
const selectedTimeRange = ref('week')
const customStartTime = ref('')
const customEndTime = ref('')
const selectedSeverity = ref('')
const selectedStatus = ref('')
const searchQuery = ref('')
const viewMode = ref('list')
const currentPage = ref(1)
const pageSize = ref(20)

// 历史统计数据
const historyStats = ref({
  total: 1247,
  resolved: 1156,
  critical: 89,
  avgResolveTime: '2.5小时'
})

// 模拟历史数据
const alertHistory = ref([
  {
    id: 1,
    title: 'CPU使用率过高',
    message: 'Web服务器CPU使用率达到95%，持续超过5分钟',
    source: 'web-server-01',
    sourceType: '服务器',
    severity: 'critical',
    status: 'resolved',
    triggeredAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    resolvedAt: new Date(Date.now() - 1.5 * 60 * 60 * 1000),
    duration: 30 * 60 * 1000 // 30分钟
  },
  {
    id: 2,
    title: '内存使用率告警',
    message: '数据库服务器内存使用率超过85%',
    source: 'db-server-02',
    sourceType: '数据库',
    severity: 'warning',
    status: 'resolved',
    triggeredAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    resolvedAt: new Date(Date.now() - 3.5 * 60 * 60 * 1000),
    duration: 30 * 60 * 1000
  },
  {
    id: 3,
    title: '磁盘空间不足',
    message: '日志服务器磁盘使用率达到90%',
    source: 'log-server-03',
    sourceType: '服务器',
    severity: 'warning',
    status: 'acknowledged',
    triggeredAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    resolvedAt: null,
    duration: 6 * 60 * 60 * 1000
  },
  {
    id: 4,
    title: '应用响应时间过长',
    message: 'API服务响应时间超过3秒',
    source: 'api-gateway',
    sourceType: '应用',
    severity: 'warning',
    status: 'resolved',
    triggeredAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
    resolvedAt: new Date(Date.now() - 7.5 * 60 * 60 * 1000),
    duration: 30 * 60 * 1000
  },
  {
    id: 5,
    title: '网络连接异常',
    message: '网络设备连接中断',
    source: 'switch-01',
    sourceType: '网络设备',
    severity: 'critical',
    status: 'resolved',
    triggeredAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
    resolvedAt: new Date(Date.now() - 11 * 60 * 60 * 1000),
    duration: 60 * 60 * 1000
  },
  {
    id: 6,
    title: '业务指标异常',
    message: '订单处理量低于正常水平',
    source: 'order-service',
    sourceType: '业务系统',
    severity: 'info',
    status: 'resolved',
    triggeredAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    resolvedAt: new Date(Date.now() - 23 * 60 * 60 * 1000),
    duration: 60 * 60 * 1000
  }
])

// 计算属性
const filteredHistory = computed(() => {
  let filtered = alertHistory.value

  // 时间范围筛选
  const now = new Date()
  let startTime, endTime

  switch (selectedTimeRange.value) {
    case 'today':
      startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      endTime = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)
      break
    case 'week':
      startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
      endTime = now
      break
    case 'month':
      startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      endTime = now
      break
    case 'quarter':
      startTime = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000)
      endTime = now
      break
    case 'custom':
      if (customStartTime.value && customEndTime.value) {
        startTime = new Date(customStartTime.value)
        endTime = new Date(customEndTime.value)
      }
      break
  }

  if (startTime && endTime) {
    filtered = filtered.filter(alert => 
      alert.triggeredAt >= startTime && alert.triggeredAt <= endTime
    )
  }

  // 级别筛选
  if (selectedSeverity.value) {
    filtered = filtered.filter(alert => alert.severity === selectedSeverity.value)
  }

  // 状态筛选
  if (selectedStatus.value) {
    filtered = filtered.filter(alert => alert.status === selectedStatus.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(alert => 
      alert.title.toLowerCase().includes(query) ||
      alert.message.toLowerCase().includes(query) ||
      alert.source.toLowerCase().includes(query)
    )
  }

  return filtered.sort((a, b) => b.triggeredAt - a.triggeredAt)
})

const totalHistory = computed(() => filteredHistory.value.length)
const totalPages = computed(() => Math.ceil(totalHistory.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

/**
 * 获取严重级别对应的变体
 */
const getSeverityVariant = (severity) => {
  const variants = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return variants[severity] || 'default'
}

/**
 * 获取状态对应的变体
 */
const getStatusVariant = (status) => {
  const variants = {
    resolved: 'success',
    acknowledged: 'warning',
    active: 'danger'
  }
  return variants[status] || 'default'
}

/**
 * 获取时间线图标
 */
const getTimelineIcon = (severity) => {
  const icons = {
    critical: 'icon-alert-circle',
    warning: 'icon-alert-triangle',
    info: 'icon-info'
  }
  return icons[severity] || 'icon-info'
}

/**
 * 格式化时间
 */
const formatTime = (time) => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(time)
}

/**
 * 格式化日期
 */
const formatDate = (time) => {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  }).format(time)
}

/**
 * 格式化持续时间
 */
const formatDuration = (duration) => {
  const hours = Math.floor(duration / (60 * 60 * 1000))
  const minutes = Math.floor((duration % (60 * 60 * 1000)) / (60 * 1000))
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
}

/**
 * 处理搜索
 */
const handleSearch = () => {
  currentPage.value = 1
}

/**
 * 清除搜索
 */
const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
}

/**
 * 重置筛选
 */
const resetFilters = () => {
  selectedTimeRange.value = 'week'
  selectedSeverity.value = ''
  selectedStatus.value = ''
  searchQuery.value = ''
  currentPage.value = 1
}

/**
 * 跳转到指定页面
 */
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

/**
 * 查看告警详情
 */
const viewAlertDetail = (alert) => {
  console.log('查看告警详情:', alert)
}

/**
 * 查看告警时间线
 */
const viewAlertTimeline = (alert) => {
  console.log('查看告警时间线:', alert)
}

/**
 * 导出告警报告
 */
const exportAlertReport = (alert) => {
  console.log('导出告警报告:', alert)
}

/**
 * 导出历史记录
 */
const exportHistory = () => {
  console.log('导出历史记录')
}

/**
 * 刷新历史记录
 */
const refreshHistory = () => {
  console.log('刷新历史记录')
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@assets/styles/variables';

.alert-history {
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

// 历史统计
.history-stats {
  margin-bottom: $spacing-xl;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-lg;
}

.stat-card {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  border-left: 4px solid;
  
  &.total {
    border-left-color: $primary-color;
    
    .stat-icon {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }
  
  &.resolved {
    border-left-color: $success-color;
    
    .stat-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
  
  &.critical {
    border-left-color: $danger-color;
    
    .stat-icon {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }
  }
  
  &.avg-time {
    border-left-color: $info-color;
    
    .stat-icon {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: $text-color;
  line-height: 1;
  margin-bottom: $spacing-xs;
}

.stat-label {
  font-size: 13px;
  color: $text-color-secondary;
}

// 筛选区域
.filter-section {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-lg;
  box-shadow: $shadow-sm;
}

.filter-row {
  display: flex;
  gap: $spacing-lg;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  
  &.search-group {
    flex: 1;
    min-width: 200px;
  }
}

.filter-label {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
}

.filter-select,
.filter-input {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  font-size: 13px;
  min-width: 120px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
  
  i {
    position: absolute;
    left: $spacing-md;
    color: $text-color-light;
    font-size: 14px;
  }
  
  input {
    width: 100%;
    padding: $spacing-sm $spacing-md $spacing-sm 36px;
    border: 1px solid $border-color;
    border-radius: $border-radius-md;
    font-size: 13px;
    
    &:focus {
      outline: none;
      border-color: $primary-color;
    }
    
    &::placeholder {
      color: $text-color-light;
    }
  }
  
  .clear-btn {
    position: absolute;
    right: $spacing-sm;
    width: 20px;
    height: 20px;
    border: none;
    background: $text-color-light;
    color: $white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 10px;
    
    &:hover {
      background: $text-color-secondary;
    }
  }
}

// 历史列表
.history-list {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.list-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
}

.view-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.view-toggle {
  display: flex;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  overflow: hidden;
}

.view-btn {
  padding: $spacing-sm $spacing-md;
  border: none;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  
  &:hover {
    background: $background-color-light;
  }
  
  &.active {
    background: $primary-color;
    color: $white;
  }
}

// 表格视图
.table-container {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: $spacing-md;
    text-align: left;
    border-bottom: 1px solid $border-color-light;
  }
  
  th {
    background: $background-color-light;
    font-weight: 600;
    color: $text-color;
    font-size: 13px;
  }
  
  .time-col {
    width: 120px;
  }
  
  .title-col {
    min-width: 300px;
  }
  
  .source-col {
    width: 150px;
  }
  
  .severity-col {
    width: 80px;
  }
  
  .status-col {
    width: 80px;
  }
  
  .duration-col {
    width: 120px;
  }
  
  .actions-col {
    width: 120px;
  }
}

.history-row {
  transition: background-color 0.2s ease;
  
  &:hover {
    background: $background-color-light;
  }
}

.time-info {
  .trigger-time {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .date-info {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
  }
}

.alert-title {
  .title-text {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .alert-message {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
    line-height: 1.4;
  }
}

.source-info {
  .source-name {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
    font-family: monospace;
    font-size: 12px;
  }
  
  .source-type {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
  }
}

.duration-info {
  .duration-text {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .resolve-time {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
  }
}

.action-buttons {
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
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

// 时间线视图
.timeline-container {
  padding: $spacing-lg;
}

.timeline {
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    left: 24px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: $border-color-light;
  }
}

.timeline-item {
  position: relative;
  padding-left: 60px;
  margin-bottom: $spacing-xl;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.timeline-marker {
  position: absolute;
  left: 0;
  top: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $white;
  border: 3px solid;
  
  .critical & {
    border-color: $danger-color;
    
    .timeline-icon {
      color: $danger-color;
    }
  }
  
  .warning & {
    border-color: $warning-color;
    
    .timeline-icon {
      color: $warning-color;
    }
  }
  
  .info & {
    border-color: $info-color;
    
    .timeline-icon {
      color: $info-color;
    }
  }
}

.timeline-icon {
  font-size: 18px;
}

.timeline-content {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  border: 1px solid $border-color-light;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.timeline-time {
  font-size: 13px;
  color: $text-color-secondary;
}

.timeline-body {
  margin-bottom: $spacing-md;
}

.timeline-message {
  color: $text-color-secondary;
  line-height: 1.5;
  margin-bottom: $spacing-md;
}

.timeline-meta {
  display: flex;
  gap: $spacing-lg;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  color: $text-color-light;
  
  i {
    font-size: 12px;
  }
}

.timeline-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-md;
}

.timeline-actions {
  display: flex;
  gap: $spacing-sm;
}

.timeline-action-btn {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

// 分页
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  background: $white;
  border-radius: $border-radius-lg;
  margin-top: $spacing-lg;
  box-shadow: $shadow-sm;
}

.pagination-info {
  font-size: 13px;
  color: $text-color-secondary;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.pagination-pages {
  display: flex;
  gap: $spacing-xs;
}

.pagination-page {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.active {
    background: $primary-color;
    border-color: $primary-color;
    color: $white;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .alert-history {
    padding: $spacing-md;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: flex-end;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    &.search-group {
      min-width: auto;
    }
  }
  
  .view-controls {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .table-container {
    font-size: 12px;
    
    th, td {
      padding: $spacing-sm;
    }
  }
  
  .timeline-item {
    padding-left: 40px;
  }
  
  .timeline-marker {
    width: 32px;
    height: 32px;
    
    .timeline-icon {
      font-size: 14px;
    }
  }
  
  .timeline {
    &::before {
      left: 16px;
    }
  }
  
  .pagination {
    flex-direction: column;
    gap: $spacing-md;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .header-right {
    flex-direction: column;
    gap: $spacing-sm;
    
    .btn {
      width: 100%;
    }
  }
  
  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-xs;
  }
  
  .timeline-meta {
    flex-direction: column;
    gap: $spacing-xs;
  }
  
  .timeline-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-sm;
  }
}
</style>