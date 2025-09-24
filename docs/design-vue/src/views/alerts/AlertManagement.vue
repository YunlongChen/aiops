<!--
  告警管理页面
  提供告警列表、筛选、处理等功能
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="alert-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">告警管理</h1>
          <p class="page-description">实时监控系统告警，快速响应和处理异常情况</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="refreshAlerts">
            <i class="icon-refresh" :class="{ 'spinning': isRefreshing }"></i>
            刷新
          </button>
          <button class="btn btn-primary" @click="createAlert">
            <i class="icon-plus"></i>
            新建告警规则
          </button>
        </div>
      </div>
    </div>

    <!-- 告警统计 -->
    <div class="alert-stats">
      <div class="stats-grid">
        <div class="stat-card critical">
          <div class="stat-icon">
            <i class="icon-alert-triangle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ alertStats.critical }}</div>
            <div class="stat-label">严重告警</div>
          </div>
        </div>
        <div class="stat-card warning">
          <div class="stat-icon">
            <i class="icon-alert-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ alertStats.warning }}</div>
            <div class="stat-label">警告告警</div>
          </div>
        </div>
        <div class="stat-card info">
          <div class="stat-icon">
            <i class="icon-info"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ alertStats.info }}</div>
            <div class="stat-label">信息告警</div>
          </div>
        </div>
        <div class="stat-card resolved">
          <div class="stat-icon">
            <i class="icon-check-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ alertStats.resolved }}</div>
            <div class="stat-label">已解决</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">状态筛选</label>
          <div class="filter-tabs">
            <button 
              v-for="status in statusFilters" 
              :key="status.value"
              class="filter-tab"
              :class="{ active: activeStatus === status.value }"
              @click="setActiveStatus(status.value)"
            >
              <span class="tab-badge" :class="status.value"></span>
              {{ status.label }}
            </button>
          </div>
        </div>
        <div class="filter-group">
          <label class="filter-label">级别筛选</label>
          <select v-model="selectedSeverity" class="filter-select">
            <option value="">全部级别</option>
            <option value="critical">严重</option>
            <option value="warning">警告</option>
            <option value="info">信息</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">时间范围</label>
          <select v-model="selectedTimeRange" class="filter-select">
            <option value="1h">最近1小时</option>
            <option value="6h">最近6小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
          </select>
        </div>
        <div class="filter-group search-group">
          <div class="search-input">
            <i class="icon-search"></i>
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="搜索告警内容、主机、服务..."
              @input="handleSearch"
            >
            <button v-if="searchQuery" class="clear-btn" @click="clearSearch">
              <i class="icon-x"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 告警列表 -->
    <div class="alert-list">
      <div class="list-header">
        <div class="list-controls">
          <div class="bulk-actions">
            <input 
              type="checkbox" 
              v-model="selectAll"
              @change="toggleSelectAll"
              class="bulk-checkbox"
            >
            <span class="selected-count" v-if="selectedAlerts.length > 0">
              已选择 {{ selectedAlerts.length }} 项
            </span>
          </div>
          <div class="batch-actions" v-if="selectedAlerts.length > 0">
            <button class="btn btn-sm btn-outline" @click="batchAcknowledge">
              <i class="icon-check"></i>
              批量确认
            </button>
            <button class="btn btn-sm btn-outline" @click="batchResolve">
              <i class="icon-check-circle"></i>
              批量解决
            </button>
            <button class="btn btn-sm btn-danger" @click="batchDelete">
              <i class="icon-trash"></i>
              批量删除
            </button>
          </div>
          <div class="view-controls">
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'list' }"
              @click="setViewMode('list')"
            >
              <i class="icon-list"></i>
            </button>
            <button 
              class="view-btn"
              :class="{ active: viewMode === 'card' }"
              @click="setViewMode('card')"
            >
              <i class="icon-grid"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="table-container">
        <table class="alert-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <input 
                  type="checkbox" 
                  v-model="selectAll"
                  @change="toggleSelectAll"
                >
              </th>
              <th class="severity-col">级别</th>
              <th class="title-col">告警内容</th>
              <th class="source-col">来源</th>
              <th class="time-col">触发时间</th>
              <th class="status-col">状态</th>
              <th class="actions-col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="alert in filteredAlerts" 
              :key="alert.id"
              class="alert-row"
              :class="{ selected: selectedAlerts.includes(alert.id) }"
            >
              <td class="checkbox-col">
                <input 
                  type="checkbox" 
                  :value="alert.id"
                  v-model="selectedAlerts"
                >
              </td>
              <td class="severity-col">
                <StatusBadge 
                  :status="alert.severity" 
                  :variant="getSeverityVariant(alert.severity)"
                />
              </td>
              <td class="title-col">
                <div class="alert-title">
                  <span class="title-text">{{ alert.title }}</span>
                  <span class="alert-description">{{ alert.description }}</span>
                </div>
              </td>
              <td class="source-col">
                <div class="source-info">
                  <span class="source-name">{{ alert.source }}</span>
                  <span class="source-type">{{ alert.sourceType }}</span>
                </div>
              </td>
              <td class="time-col">
                <div class="time-info">
                  <span class="trigger-time">{{ formatTime(alert.triggerTime) }}</span>
                  <span class="duration">持续 {{ alert.duration }}</span>
                </div>
              </td>
              <td class="status-col">
                <StatusBadge 
                  :status="alert.status" 
                  :variant="getStatusVariant(alert.status)"
                />
              </td>
              <td class="actions-col">
                <div class="action-buttons">
                  <button 
                    class="action-btn"
                    @click="viewAlert(alert)"
                    title="查看详情"
                  >
                    <i class="icon-eye"></i>
                  </button>
                  <button 
                    v-if="alert.status === 'active'"
                    class="action-btn"
                    @click="acknowledgeAlert(alert)"
                    title="确认告警"
                  >
                    <i class="icon-check"></i>
                  </button>
                  <button 
                    v-if="alert.status !== 'resolved'"
                    class="action-btn"
                    @click="resolveAlert(alert)"
                    title="解决告警"
                  >
                    <i class="icon-check-circle"></i>
                  </button>
                  <button 
                    class="action-btn danger"
                    @click="deleteAlert(alert)"
                    title="删除告警"
                  >
                    <i class="icon-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 卡片视图 -->
      <div v-if="viewMode === 'card'" class="card-container">
        <div 
          v-for="alert in filteredAlerts" 
          :key="alert.id"
          class="alert-card"
          :class="{ selected: selectedAlerts.includes(alert.id) }"
        >
          <div class="card-header">
            <div class="card-left">
              <input 
                type="checkbox" 
                :value="alert.id"
                v-model="selectedAlerts"
                class="card-checkbox"
              >
              <StatusBadge 
                :status="alert.severity" 
                :variant="getSeverityVariant(alert.severity)"
              />
            </div>
            <div class="card-right">
              <StatusBadge 
                :status="alert.status" 
                :variant="getStatusVariant(alert.status)"
              />
            </div>
          </div>
          <div class="card-content">
            <h3 class="card-title">{{ alert.title }}</h3>
            <p class="card-description">{{ alert.description }}</p>
            <div class="card-meta">
              <div class="meta-item">
                <i class="icon-server"></i>
                <span>{{ alert.source }}</span>
              </div>
              <div class="meta-item">
                <i class="icon-clock"></i>
                <span>{{ formatTime(alert.triggerTime) }}</span>
              </div>
              <div class="meta-item">
                <i class="icon-timer"></i>
                <span>持续 {{ alert.duration }}</span>
              </div>
            </div>
          </div>
          <div class="card-actions">
            <button class="btn btn-sm btn-outline" @click="viewAlert(alert)">
              查看详情
            </button>
            <button 
              v-if="alert.status === 'active'"
              class="btn btn-sm btn-primary"
              @click="acknowledgeAlert(alert)"
            >
              确认
            </button>
            <button 
              v-if="alert.status !== 'resolved'"
              class="btn btn-sm btn-success"
              @click="resolveAlert(alert)"
            >
              解决
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-if="filteredAlerts.length === 0"
        icon="icon-bell-off"
        title="暂无告警"
        description="当前筛选条件下没有找到相关告警"
        :actions="[
          { text: '清除筛选', action: clearFilters },
          { text: '刷新数据', action: refreshAlerts }
        ]"
      />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="filteredAlerts.length > 0">
      <div class="pagination-info">
        显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalAlerts) }} 条，
        共 {{ totalAlerts }} 条记录
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
 * 告警管理页面组件
 * 提供告警列表、筛选、处理等功能
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import StatusBadge from '@components/common/StatusBadge.vue'
import EmptyState from '@components/common/EmptyState.vue'

// 响应式数据
const isRefreshing = ref(false)
const viewMode = ref('list')
const activeStatus = ref('all')
const selectedSeverity = ref('')
const selectedTimeRange = ref('24h')
const searchQuery = ref('')
const selectAll = ref(false)
const selectedAlerts = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

// 告警统计数据
const alertStats = ref({
  critical: 12,
  warning: 28,
  info: 45,
  resolved: 156
})

// 状态筛选选项
const statusFilters = [
  { label: '全部', value: 'all' },
  { label: '活跃', value: 'active' },
  { label: '已确认', value: 'acknowledged' },
  { label: '已解决', value: 'resolved' }
]

// 模拟告警数据
const alerts = ref([
  {
    id: 1,
    title: 'CPU使用率过高',
    description: 'web-server-01 CPU使用率达到 95%，持续超过5分钟',
    severity: 'critical',
    status: 'active',
    source: 'web-server-01',
    sourceType: '服务器',
    triggerTime: new Date(Date.now() - 30 * 60 * 1000),
    duration: '30分钟'
  },
  {
    id: 2,
    title: '内存使用率告警',
    description: 'db-server-02 内存使用率达到 85%',
    severity: 'warning',
    status: 'acknowledged',
    source: 'db-server-02',
    sourceType: '数据库服务器',
    triggerTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
    duration: '2小时'
  },
  {
    id: 3,
    title: '磁盘空间不足',
    description: '/var/log 分区使用率达到 90%',
    severity: 'warning',
    status: 'active',
    source: 'log-server-01',
    sourceType: '日志服务器',
    triggerTime: new Date(Date.now() - 4 * 60 * 60 * 1000),
    duration: '4小时'
  },
  {
    id: 4,
    title: '网络连接异常',
    description: '与外部API服务连接超时',
    severity: 'critical',
    status: 'resolved',
    source: 'api-gateway',
    sourceType: 'API网关',
    triggerTime: new Date(Date.now() - 6 * 60 * 60 * 1000),
    duration: '15分钟'
  },
  {
    id: 5,
    title: '服务响应时间过长',
    description: '用户服务平均响应时间超过2秒',
    severity: 'info',
    status: 'active',
    source: 'user-service',
    sourceType: '微服务',
    triggerTime: new Date(Date.now() - 1 * 60 * 60 * 1000),
    duration: '1小时'
  }
])

// 计算属性
const filteredAlerts = computed(() => {
  let filtered = alerts.value

  // 状态筛选
  if (activeStatus.value !== 'all') {
    filtered = filtered.filter(alert => alert.status === activeStatus.value)
  }

  // 级别筛选
  if (selectedSeverity.value) {
    filtered = filtered.filter(alert => alert.severity === selectedSeverity.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(alert => 
      alert.title.toLowerCase().includes(query) ||
      alert.description.toLowerCase().includes(query) ||
      alert.source.toLowerCase().includes(query)
    )
  }

  return filtered
})

const totalAlerts = computed(() => filteredAlerts.value.length)
const totalPages = computed(() => Math.ceil(totalAlerts.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// 定时器
let refreshTimer = null

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
    active: 'danger',
    acknowledged: 'warning',
    resolved: 'success'
  }
  return variants[status] || 'default'
}

/**
 * 格式化时间
 */
const formatTime = (time) => {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(time)
}

/**
 * 设置活跃状态
 */
const setActiveStatus = (status) => {
  activeStatus.value = status
  currentPage.value = 1
}

/**
 * 设置视图模式
 */
const setViewMode = (mode) => {
  viewMode.value = mode
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
 * 清除筛选
 */
const clearFilters = () => {
  activeStatus.value = 'all'
  selectedSeverity.value = ''
  selectedTimeRange.value = '24h'
  searchQuery.value = ''
  currentPage.value = 1
}

/**
 * 切换全选
 */
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedAlerts.value = filteredAlerts.value.map(alert => alert.id)
  } else {
    selectedAlerts.value = []
  }
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
 * 刷新告警数据
 */
const refreshAlerts = async () => {
  isRefreshing.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 这里应该调用实际的API
    console.log('刷新告警数据')
  } catch (error) {
    console.error('刷新失败:', error)
  } finally {
    isRefreshing.value = false
  }
}

/**
 * 创建告警规则
 */
const createAlert = () => {
  console.log('创建告警规则')
}

/**
 * 查看告警详情
 */
const viewAlert = (alert) => {
  console.log('查看告警详情:', alert)
}

/**
 * 确认告警
 */
const acknowledgeAlert = (alert) => {
  alert.status = 'acknowledged'
  console.log('确认告警:', alert)
}

/**
 * 解决告警
 */
const resolveAlert = (alert) => {
  alert.status = 'resolved'
  console.log('解决告警:', alert)
}

/**
 * 删除告警
 */
const deleteAlert = (alert) => {
  if (confirm('确定要删除这个告警吗？')) {
    const index = alerts.value.findIndex(a => a.id === alert.id)
    if (index > -1) {
      alerts.value.splice(index, 1)
    }
  }
}

/**
 * 批量确认
 */
const batchAcknowledge = () => {
  selectedAlerts.value.forEach(id => {
    const alert = alerts.value.find(a => a.id === id)
    if (alert && alert.status === 'active') {
      alert.status = 'acknowledged'
    }
  })
  selectedAlerts.value = []
  selectAll.value = false
}

/**
 * 批量解决
 */
const batchResolve = () => {
  selectedAlerts.value.forEach(id => {
    const alert = alerts.value.find(a => a.id === id)
    if (alert && alert.status !== 'resolved') {
      alert.status = 'resolved'
    }
  })
  selectedAlerts.value = []
  selectAll.value = false
}

/**
 * 批量删除
 */
const batchDelete = () => {
  if (confirm(`确定要删除选中的 ${selectedAlerts.value.length} 个告警吗？`)) {
    alerts.value = alerts.value.filter(alert => !selectedAlerts.value.includes(alert.id))
    selectedAlerts.value = []
    selectAll.value = false
  }
}

/**
 * 启动定时刷新
 */
const startAutoRefresh = () => {
  refreshTimer = setInterval(() => {
    refreshAlerts()
  }, 30000) // 30秒刷新一次
}

/**
 * 停止定时刷新
 */
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style lang="scss" scoped>
@import '@assets/styles/variables';

.alert-management {
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

.spinning {
  animation: spin 1s linear infinite;
}

// 告警统计
.alert-stats {
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
  
  &.critical {
    border-left-color: $danger-color;
    
    .stat-icon {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }
  }
  
  &.warning {
    border-left-color: $warning-color;
    
    .stat-icon {
      background: rgba($warning-color, 0.1);
      color: $warning-color;
    }
  }
  
  &.info {
    border-left-color: $info-color;
    
    .stat-icon {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }
  }
  
  &.resolved {
    border-left-color: $success-color;
    
    .stat-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
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

.filter-tabs {
  display: flex;
  gap: $spacing-xs;
}

.filter-tab {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color-secondary;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  transition: all 0.2s ease;
  
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

.tab-badge {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  
  &.all {
    background: $text-color-light;
  }
  
  &.active {
    background: $danger-color;
  }
  
  &.acknowledged {
    background: $warning-color;
  }
  
  &.resolved {
    background: $success-color;
  }
}

.filter-select {
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

// 告警列表
.alert-list {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.list-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
}

.list-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-lg;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.bulk-checkbox {
  margin: 0;
}

.selected-count {
  font-size: 13px;
  color: $text-color-secondary;
}

.batch-actions {
  display: flex;
  gap: $spacing-sm;
}

.view-controls {
  display: flex;
  gap: $spacing-xs;
}

.view-btn {
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

// 表格视图
.table-container {
  overflow-x: auto;
}

.alert-table {
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
  
  .checkbox-col {
    width: 40px;
  }
  
  .severity-col {
    width: 80px;
  }
  
  .title-col {
    min-width: 300px;
  }
  
  .source-col {
    width: 150px;
  }
  
  .time-col {
    width: 120px;
  }
  
  .status-col {
    width: 80px;
  }
  
  .actions-col {
    width: 120px;
  }
}

.alert-row {
  transition: background-color 0.2s ease;
  
  &:hover {
    background: $background-color-light;
  }
  
  &.selected {
    background: rgba($primary-color, 0.05);
  }
}

.alert-title {
  .title-text {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .alert-description {
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
  }
  
  .source-type {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
  }
}

.time-info {
  .trigger-time {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .duration {
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
  
  &.danger:hover {
    border-color: $danger-color;
    color: $danger-color;
  }
}

// 卡片视图
.card-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: $spacing-lg;
  padding: $spacing-lg;
}

.alert-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: $primary-color;
    box-shadow: $shadow-md;
  }
  
  &.selected {
    border-color: $primary-color;
    background: rgba($primary-color, 0.02);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.card-left {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.card-checkbox {
  margin: 0;
}

.card-content {
  margin-bottom: $spacing-lg;
}

.card-title {
  margin: 0 0 $spacing-sm 0;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.card-description {
  margin: 0 0 $spacing-md 0;
  font-size: 13px;
  color: $text-color-secondary;
  line-height: 1.5;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  color: $text-color-secondary;
  
  i {
    width: 14px;
    color: $text-color-light;
  }
}

.card-actions {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
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

// 动画
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .card-container {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .alert-management {
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
  
  .list-controls {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .batch-actions {
    justify-content: center;
  }
  
  .view-controls {
    justify-content: center;
  }
  
  .table-container {
    font-size: 12px;
    
    th, td {
      padding: $spacing-sm;
    }
  }
  
  .card-container {
    grid-template-columns: 1fr;
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
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .card-actions {
    .btn {
      flex: 1;
      min-width: 0;
    }
  }
}
</style>