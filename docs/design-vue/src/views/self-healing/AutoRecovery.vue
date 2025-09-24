<!--
  自动恢复页面
  系统故障自动检测和恢复功能管理
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="auto-recovery">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">自动恢复</h1>
          <p class="page-description">系统故障自动检测和智能恢复管理</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="exportRecoveryLog">
            <i class="icon-download"></i>
            导出日志
          </button>
          <button class="btn btn-outline" @click="refreshData">
            <i class="icon-refresh"></i>
            刷新数据
          </button>
          <button class="btn btn-primary" @click="runHealthCheck">
            <i class="icon-heart"></i>
            健康检查
          </button>
        </div>
      </div>
    </div>

    <!-- 恢复概览 -->
    <div class="recovery-overview">
      <div class="overview-grid">
        <div class="overview-card total">
          <div class="card-icon">
            <i class="icon-activity"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ recoveryStats.totalRecoveries }}</div>
            <div class="card-label">总恢复次数</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +12次今日
            </div>
          </div>
        </div>
        <div class="overview-card success">
          <div class="card-icon">
            <i class="icon-check-circle"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ recoveryStats.successRate }}%</div>
            <div class="card-label">成功率</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +2.3%
            </div>
          </div>
        </div>
        <div class="overview-card avg-time">
          <div class="card-icon">
            <i class="icon-clock"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ recoveryStats.avgRecoveryTime }}s</div>
            <div class="card-label">平均恢复时间</div>
            <div class="card-trend negative">
              <i class="icon-trending-down"></i>
              -15s
            </div>
          </div>
        </div>
        <div class="overview-card active">
          <div class="card-icon">
            <i class="icon-zap"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ recoveryStats.activeRecoveries }}</div>
            <div class="card-label">进行中</div>
            <div class="card-trend neutral">
              <i class="icon-minus"></i>
              无变化
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统健康状态 -->
    <div class="system-health">
      <div class="health-header">
        <h2 class="section-title">系统健康状态</h2>
        <div class="health-controls">
          <select v-model="selectedTimeRange" class="time-range-select">
            <option value="1h">最近1小时</option>
            <option value="6h">最近6小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
          </select>
          <div class="health-status" :class="systemHealthStatus">
            <i :class="getHealthIcon(systemHealthStatus)"></i>
            <span>{{ getHealthText(systemHealthStatus) }}</span>
          </div>
        </div>
      </div>

      <div class="health-content">
        <div class="health-grid">
          <!-- 服务健康度 -->
          <div class="health-card services">
            <div class="card-header">
              <h3 class="card-title">服务健康度</h3>
              <div class="health-score" :class="getHealthScoreClass(serviceHealth.score)">
                {{ serviceHealth.score }}
              </div>
            </div>
            <div class="card-content">
              <div class="service-list">
                <div 
                  class="service-item"
                  v-for="service in serviceHealth.services"
                  :key="service.name"
                  :class="service.status"
                >
                  <div class="service-info">
                    <div class="service-name">{{ service.name }}</div>
                    <div class="service-status">{{ getServiceStatusText(service.status) }}</div>
                  </div>
                  <div class="service-indicator">
                    <div class="indicator-dot" :class="service.status"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 资源监控 -->
          <div class="health-card resources">
            <div class="card-header">
              <h3 class="card-title">资源监控</h3>
            </div>
            <div class="card-content">
              <BaseChart
                title="资源使用趋势"
                :loading="false"
                :error="false"
                :no-data="false"
              >
                <div class="resource-chart">
                  <div class="resource-metrics">
                    <div class="metric-item" v-for="metric in resourceMetrics" :key="metric.name">
                      <div class="metric-header">
                        <span class="metric-name">{{ metric.name }}</span>
                        <span class="metric-value" :class="getMetricStatus(metric.value, metric.threshold)">
                          {{ metric.value }}%
                        </span>
                      </div>
                      <div class="metric-bar">
                        <div 
                          class="metric-fill"
                          :class="getMetricStatus(metric.value, metric.threshold)"
                          :style="{ width: metric.value + '%' }"
                        ></div>
                      </div>
                      <div class="metric-threshold">阈值: {{ metric.threshold }}%</div>
                    </div>
                  </div>
                </div>
              </BaseChart>
            </div>
          </div>

          <!-- 故障检测 -->
          <div class="health-card detection">
            <div class="card-header">
              <h3 class="card-title">故障检测</h3>
              <button class="btn btn-sm btn-outline" @click="runDetection">
                <i class="icon-search"></i>
                运行检测
              </button>
            </div>
            <div class="card-content">
              <div class="detection-results">
                <div 
                  class="detection-item"
                  v-for="detection in detectionResults"
                  :key="detection.id"
                  :class="detection.severity"
                >
                  <div class="detection-icon">
                    <i :class="getDetectionIcon(detection.type)"></i>
                  </div>
                  <div class="detection-info">
                    <div class="detection-title">{{ detection.title }}</div>
                    <div class="detection-time">{{ formatTime(detection.detectedAt) }}</div>
                  </div>
                  <div class="detection-status">
                    <span class="status-badge" :class="detection.status">
                      {{ getDetectionStatusText(detection.status) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 恢复策略 -->
    <div class="recovery-strategies">
      <div class="strategies-header">
        <h2 class="section-title">恢复策略</h2>
        <div class="strategies-controls">
          <select v-model="selectedStrategy" class="strategy-select">
            <option value="">全部策略</option>
            <option value="restart">服务重启</option>
            <option value="failover">故障转移</option>
            <option value="scaling">自动扩容</option>
            <option value="rollback">版本回滚</option>
          </select>
          <button class="btn btn-outline btn-sm" @click="addStrategy">
            <i class="icon-plus"></i>
            新增策略
          </button>
        </div>
      </div>

      <div class="strategies-content">
        <div class="strategies-grid">
          <div 
            class="strategy-card"
            v-for="strategy in filteredStrategies"
            :key="strategy.id"
            :class="[strategy.type, strategy.status]"
          >
            <div class="strategy-header">
              <div class="strategy-info">
                <div class="strategy-name">{{ strategy.name }}</div>
                <div class="strategy-type">{{ getStrategyTypeText(strategy.type) }}</div>
              </div>
              <div class="strategy-actions">
                <label class="strategy-toggle">
                  <input 
                    type="checkbox" 
                    v-model="strategy.enabled"
                    @change="toggleStrategy(strategy)"
                  >
                  <span class="toggle-slider"></span>
                </label>
                <button class="action-btn" @click="editStrategy(strategy)">
                  <i class="icon-edit"></i>
                </button>
                <button class="action-btn" @click="deleteStrategy(strategy)">
                  <i class="icon-trash"></i>
                </button>
              </div>
            </div>
            
            <div class="strategy-content">
              <div class="strategy-description">{{ strategy.description }}</div>
              
              <div class="strategy-conditions">
                <div class="condition-title">触发条件:</div>
                <div class="condition-list">
                  <div class="condition-item" v-for="condition in strategy.conditions" :key="condition.id">
                    <span class="condition-metric">{{ condition.metric }}</span>
                    <span class="condition-operator">{{ condition.operator }}</span>
                    <span class="condition-value">{{ condition.value }}</span>
                  </div>
                </div>
              </div>
              
              <div class="strategy-actions-list">
                <div class="actions-title">恢复动作:</div>
                <div class="actions-list">
                  <div class="action-item" v-for="action in strategy.actions" :key="action.id">
                    <i :class="getActionIcon(action.type)"></i>
                    <span class="action-text">{{ action.description }}</span>
                  </div>
                </div>
              </div>
              
              <div class="strategy-stats">
                <div class="stat-item">
                  <span class="stat-label">执行次数:</span>
                  <span class="stat-value">{{ strategy.executionCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">成功率:</span>
                  <span class="stat-value" :class="getSuccessRateClass(strategy.successRate)">
                    {{ strategy.successRate }}%
                  </span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均时间:</span>
                  <span class="stat-value">{{ strategy.avgTime }}s</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <EmptyState
          v-if="filteredStrategies.length === 0"
          icon="icon-settings"
          title="暂无恢复策略"
          description="还没有配置任何自动恢复策略"
          :actions="[
            { text: '新增策略', action: addStrategy },
            { text: '导入模板', action: importTemplate }
          ]"
        />
      </div>
    </div>

    <!-- 恢复历史 -->
    <div class="recovery-history">
      <div class="history-header">
        <h2 class="section-title">恢复历史</h2>
        <div class="history-controls">
          <select v-model="selectedStatus" class="status-select">
            <option value="">全部状态</option>
            <option value="success">成功</option>
            <option value="failed">失败</option>
            <option value="running">进行中</option>
          </select>
          <div class="search-box">
            <i class="icon-search"></i>
            <input 
              type="text" 
              v-model="searchKeyword"
              placeholder="搜索恢复记录..."
              class="search-input"
            >
          </div>
        </div>
      </div>

      <div class="history-content">
        <div class="history-table">
          <div class="table-header">
            <div class="header-cell time">时间</div>
            <div class="header-cell service">服务</div>
            <div class="header-cell issue">问题</div>
            <div class="header-cell strategy">策略</div>
            <div class="header-cell duration">耗时</div>
            <div class="header-cell status">状态</div>
            <div class="header-cell actions">操作</div>
          </div>
          
          <div class="table-body">
            <div 
              class="table-row"
              v-for="record in filteredHistory"
              :key="record.id"
              :class="record.status"
            >
              <div class="table-cell time">
                <div class="time-info">
                  <div class="time-date">{{ formatDate(record.startTime) }}</div>
                  <div class="time-time">{{ formatTime(record.startTime) }}</div>
                </div>
              </div>
              <div class="table-cell service">
                <div class="service-info">
                  <div class="service-name">{{ record.serviceName }}</div>
                  <div class="service-type">{{ record.serviceType }}</div>
                </div>
              </div>
              <div class="table-cell issue">
                <div class="issue-info">
                  <div class="issue-title">{{ record.issueTitle }}</div>
                  <div class="issue-severity" :class="record.issueSeverity">
                    {{ getIssueSeverityText(record.issueSeverity) }}
                  </div>
                </div>
              </div>
              <div class="table-cell strategy">
                <div class="strategy-info">
                  <div class="strategy-name">{{ record.strategyName }}</div>
                  <div class="strategy-type">{{ getStrategyTypeText(record.strategyType) }}</div>
                </div>
              </div>
              <div class="table-cell duration">
                <div class="duration-info">
                  <div class="duration-value">{{ record.duration }}s</div>
                  <div class="duration-comparison" :class="getDurationComparisonClass(record.durationComparison)">
                    {{ record.durationComparison > 0 ? '+' : '' }}{{ record.durationComparison }}s
                  </div>
                </div>
              </div>
              <div class="table-cell status">
                <span class="status-badge" :class="record.status">
                  <i :class="getStatusIcon(record.status)"></i>
                  {{ getStatusText(record.status) }}
                </span>
              </div>
              <div class="table-cell actions">
                <button class="action-btn" @click="viewRecoveryDetail(record)">
                  <i class="icon-eye"></i>
                  详情
                </button>
                <button 
                  v-if="record.status === 'failed'"
                  class="action-btn retry"
                  @click="retryRecovery(record)"
                >
                  <i class="icon-refresh-cw"></i>
                  重试
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            class="page-btn"
            :disabled="currentPage === 1"
            @click="changePage(currentPage - 1)"
          >
            <i class="icon-chevron-left"></i>
          </button>
          
          <div class="page-numbers">
            <button 
              class="page-number"
              v-for="page in visiblePages"
              :key="page"
              :class="{ active: page === currentPage }"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="page-btn"
            :disabled="currentPage === totalPages"
            @click="changePage(currentPage + 1)"
          >
            <i class="icon-chevron-right"></i>
          </button>
        </div>

        <!-- 空状态 -->
        <EmptyState
          v-if="filteredHistory.length === 0"
          icon="icon-clock"
          title="暂无恢复记录"
          description="还没有执行过自动恢复操作"
          :actions="[
            { text: '运行健康检查', action: runHealthCheck },
            { text: '刷新数据', action: refreshData }
          ]"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 自动恢复页面组件
 * 系统故障自动检测和恢复功能管理
 */
import { ref, computed, onMounted } from 'vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import EmptyState from '@/components/common/EmptyState.vue'

// 响应式数据
const selectedTimeRange = ref('24h')
const selectedStrategy = ref('')
const selectedStatus = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

// 恢复统计数据
const recoveryStats = ref({
  totalRecoveries: 156,
  successRate: 94.2,
  avgRecoveryTime: 45,
  activeRecoveries: 2
})

// 系统健康状态
const systemHealthStatus = ref('healthy') // healthy, warning, critical

// 服务健康度数据
const serviceHealth = ref({
  score: 92,
  services: [
    { name: 'Web服务', status: 'healthy' },
    { name: '数据库', status: 'healthy' },
    { name: 'Redis缓存', status: 'warning' },
    { name: 'API网关', status: 'healthy' },
    { name: '消息队列', status: 'healthy' },
    { name: '文件存储', status: 'critical' }
  ]
})

// 资源监控数据
const resourceMetrics = ref([
  { name: 'CPU', value: 68, threshold: 80 },
  { name: '内存', value: 72, threshold: 85 },
  { name: '磁盘', value: 45, threshold: 90 },
  { name: '网络', value: 34, threshold: 70 }
])

// 故障检测结果
const detectionResults = ref([
  {
    id: 1,
    type: 'performance',
    title: 'API响应时间异常',
    severity: 'warning',
    status: 'detected',
    detectedAt: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: 2,
    type: 'resource',
    title: '内存使用率过高',
    severity: 'critical',
    status: 'recovering',
    detectedAt: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: 3,
    type: 'service',
    title: '数据库连接异常',
    severity: 'high',
    status: 'resolved',
    detectedAt: new Date(Date.now() - 30 * 60 * 1000)
  }
])

// 恢复策略数据
const strategies = ref([
  {
    id: 1,
    name: 'Web服务重启策略',
    type: 'restart',
    status: 'active',
    enabled: true,
    description: '当Web服务响应时间超过阈值时自动重启服务',
    conditions: [
      { id: 1, metric: '响应时间', operator: '>', value: '5000ms' },
      { id: 2, metric: 'CPU使用率', operator: '>', value: '90%' }
    ],
    actions: [
      { id: 1, type: 'restart', description: '重启Web服务' },
      { id: 2, type: 'notify', description: '发送告警通知' }
    ],
    executionCount: 23,
    successRate: 95.7,
    avgTime: 30
  },
  {
    id: 2,
    name: '数据库故障转移',
    type: 'failover',
    status: 'active',
    enabled: true,
    description: '主数据库故障时自动切换到备用数据库',
    conditions: [
      { id: 1, metric: '连接失败率', operator: '>', value: '50%' },
      { id: 2, metric: '响应时间', operator: '>', value: '10000ms' }
    ],
    actions: [
      { id: 1, type: 'failover', description: '切换到备用数据库' },
      { id: 2, type: 'notify', description: '通知运维团队' }
    ],
    executionCount: 8,
    successRate: 100,
    avgTime: 120
  },
  {
    id: 3,
    name: '自动扩容策略',
    type: 'scaling',
    status: 'active',
    enabled: false,
    description: '负载过高时自动增加服务实例',
    conditions: [
      { id: 1, metric: 'CPU使用率', operator: '>', value: '80%' },
      { id: 2, metric: '内存使用率', operator: '>', value: '85%' }
    ],
    actions: [
      { id: 1, type: 'scale', description: '增加2个服务实例' },
      { id: 2, type: 'monitor', description: '监控扩容效果' }
    ],
    executionCount: 15,
    successRate: 86.7,
    avgTime: 180
  }
])

// 恢复历史数据
const recoveryHistory = ref([
  {
    id: 1,
    startTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
    serviceName: 'Web服务',
    serviceType: 'HTTP服务',
    issueTitle: 'API响应超时',
    issueSeverity: 'high',
    strategyName: 'Web服务重启策略',
    strategyType: 'restart',
    duration: 35,
    durationComparison: -5,
    status: 'success'
  },
  {
    id: 2,
    startTime: new Date(Date.now() - 4 * 60 * 60 * 1000),
    serviceName: '数据库',
    serviceType: 'MySQL',
    issueTitle: '连接池耗尽',
    issueSeverity: 'critical',
    strategyName: '数据库故障转移',
    strategyType: 'failover',
    duration: 125,
    durationComparison: 5,
    status: 'success'
  },
  {
    id: 3,
    startTime: new Date(Date.now() - 6 * 60 * 60 * 1000),
    serviceName: 'Redis缓存',
    serviceType: 'Redis',
    issueTitle: '内存不足',
    issueSeverity: 'warning',
    strategyName: '缓存清理策略',
    strategyType: 'cleanup',
    duration: 0,
    durationComparison: 0,
    status: 'failed'
  },
  {
    id: 4,
    startTime: new Date(Date.now() - 8 * 60 * 60 * 1000),
    serviceName: 'API网关',
    serviceType: 'Nginx',
    issueTitle: '负载过高',
    issueSeverity: 'medium',
    strategyName: '自动扩容策略',
    strategyType: 'scaling',
    duration: 185,
    durationComparison: 5,
    status: 'running'
  }
])

// 计算属性
const filteredStrategies = computed(() => {
  let filtered = strategies.value
  
  if (selectedStrategy.value) {
    filtered = filtered.filter(s => s.type === selectedStrategy.value)
  }
  
  return filtered
})

const filteredHistory = computed(() => {
  let filtered = recoveryHistory.value
  
  if (selectedStatus.value) {
    filtered = filtered.filter(h => h.status === selectedStatus.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(h => 
      h.serviceName.toLowerCase().includes(keyword) ||
      h.issueTitle.toLowerCase().includes(keyword) ||
      h.strategyName.toLowerCase().includes(keyword)
    )
  }
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const totalPages = computed(() => {
  let filtered = recoveryHistory.value
  
  if (selectedStatus.value) {
    filtered = filtered.filter(h => h.status === selectedStatus.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(h => 
      h.serviceName.toLowerCase().includes(keyword) ||
      h.issueTitle.toLowerCase().includes(keyword) ||
      h.strategyName.toLowerCase().includes(keyword)
    )
  }
  
  return Math.ceil(filtered.length / pageSize.value)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

/**
 * 获取健康状态图标
 */
const getHealthIcon = (status) => {
  const icons = {
    healthy: 'icon-check-circle',
    warning: 'icon-alert-triangle',
    critical: 'icon-alert-circle'
  }
  return icons[status] || 'icon-help-circle'
}

/**
 * 获取健康状态文本
 */
const getHealthText = (status) => {
  const texts = {
    healthy: '系统正常',
    warning: '需要关注',
    critical: '严重异常'
  }
  return texts[status] || '未知状态'
}

/**
 * 获取健康度等级样式类
 */
const getHealthScoreClass = (score) => {
  if (score >= 90) return 'excellent'
  if (score >= 80) return 'good'
  if (score >= 70) return 'normal'
  if (score >= 60) return 'warning'
  return 'critical'
}

/**
 * 获取服务状态文本
 */
const getServiceStatusText = (status) => {
  const texts = {
    healthy: '正常',
    warning: '警告',
    critical: '异常'
  }
  return texts[status] || '未知'
}

/**
 * 获取指标状态
 */
const getMetricStatus = (value, threshold) => {
  if (value >= threshold * 0.9) return 'critical'
  if (value >= threshold * 0.8) return 'warning'
  return 'normal'
}

/**
 * 获取检测图标
 */
const getDetectionIcon = (type) => {
  const icons = {
    performance: 'icon-zap',
    resource: 'icon-cpu',
    service: 'icon-server',
    network: 'icon-wifi'
  }
  return icons[type] || 'icon-alert-circle'
}

/**
 * 获取检测状态文本
 */
const getDetectionStatusText = (status) => {
  const texts = {
    detected: '已检测',
    recovering: '恢复中',
    resolved: '已解决'
  }
  return texts[status] || status
}

/**
 * 获取策略类型文本
 */
const getStrategyTypeText = (type) => {
  const texts = {
    restart: '服务重启',
    failover: '故障转移',
    scaling: '自动扩容',
    rollback: '版本回滚',
    cleanup: '资源清理'
  }
  return texts[type] || type
}

/**
 * 获取动作图标
 */
const getActionIcon = (type) => {
  const icons = {
    restart: 'icon-refresh-cw',
    failover: 'icon-shuffle',
    scale: 'icon-trending-up',
    rollback: 'icon-rotate-ccw',
    notify: 'icon-bell',
    monitor: 'icon-eye',
    cleanup: 'icon-trash'
  }
  return icons[type] || 'icon-play'
}

/**
 * 获取成功率样式类
 */
const getSuccessRateClass = (rate) => {
  if (rate >= 95) return 'excellent'
  if (rate >= 90) return 'good'
  if (rate >= 80) return 'normal'
  return 'warning'
}

/**
 * 获取问题严重程度文本
 */
const getIssueSeverityText = (severity) => {
  const texts = {
    low: '低',
    medium: '中',
    high: '高',
    critical: '严重',
    warning: '警告'
  }
  return texts[severity] || severity
}

/**
 * 获取状态图标
 */
const getStatusIcon = (status) => {
  const icons = {
    success: 'icon-check',
    failed: 'icon-x',
    running: 'icon-loader'
  }
  return icons[status] || 'icon-help-circle'
}

/**
 * 获取状态文本
 */
const getStatusText = (status) => {
  const texts = {
    success: '成功',
    failed: '失败',
    running: '进行中'
  }
  return texts[status] || status
}

/**
 * 获取耗时对比样式类
 */
const getDurationComparisonClass = (comparison) => {
  if (comparison > 0) return 'slower'
  if (comparison < 0) return 'faster'
  return 'same'
}

/**
 * 格式化时间
 */
const formatTime = (datetime) => {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  }).format(datetime)
}

/**
 * 格式化日期
 */
const formatDate = (datetime) => {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  }).format(datetime)
}

/**
 * 导出恢复日志
 */
const exportRecoveryLog = () => {
  console.log('导出恢复日志')
}

/**
 * 刷新数据
 */
const refreshData = () => {
  console.log('刷新数据')
}

/**
 * 运行健康检查
 */
const runHealthCheck = () => {
  console.log('运行健康检查')
}

/**
 * 运行检测
 */
const runDetection = () => {
  console.log('运行故障检测')
}

/**
 * 新增策略
 */
const addStrategy = () => {
  console.log('新增恢复策略')
}

/**
 * 导入模板
 */
const importTemplate = () => {
  console.log('导入策略模板')
}

/**
 * 切换策略状态
 */
const toggleStrategy = (strategy) => {
  console.log('切换策略状态:', strategy)
}

/**
 * 编辑策略
 */
const editStrategy = (strategy) => {
  console.log('编辑策略:', strategy)
}

/**
 * 删除策略
 */
const deleteStrategy = (strategy) => {
  console.log('删除策略:', strategy)
}

/**
 * 查看恢复详情
 */
const viewRecoveryDetail = (record) => {
  console.log('查看恢复详情:', record)
}

/**
 * 重试恢复
 */
const retryRecovery = (record) => {
  console.log('重试恢复:', record)
}

/**
 * 切换页面
 */
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.auto-recovery {
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

// 恢复概览
.recovery-overview {
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
  
  &.total {
    border-left-color: $primary-color;
    
    .card-icon {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }
  
  &.success {
    border-left-color: $success-color;
    
    .card-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
  
  &.avg-time {
    border-left-color: $info-color;
    
    .card-icon {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }
  }
  
  &.active {
    border-left-color: $warning-color;
    
    .card-icon {
      background: rgba($warning-color, 0.1);
      color: $warning-color;
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

// 系统健康状态
.system-health {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.health-header {
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

.health-controls {
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

.health-status {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-md;
  border-radius: $border-radius-md;
  font-size: 13px;
  font-weight: 500;
  
  &.healthy {
    background: rgba($success-color, 0.1);
    color: $success-color;
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

.health-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: $spacing-lg;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.health-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  overflow: hidden;
}

.card-header {
  padding: $spacing-lg;
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

.health-score {
  font-size: 24px;
  font-weight: 700;
  
  &.excellent {
    color: $success-color;
  }
  
  &.good {
    color: $info-color;
  }
  
  &.normal {
    color: $warning-color;
  }
  
  &.warning {
    color: $danger-color;
  }
  
  &.critical {
    color: $danger-color;
  }
}

.card-content {
  padding: $spacing-lg;
}

// 服务列表
.service-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-sm $spacing-md;
  border-radius: $border-radius-md;
  border: 1px solid $border-color-light;
  
  &.healthy {
    background: rgba($success-color, 0.05);
    border-color: rgba($success-color, 0.2);
  }
  
  &.warning {
    background: rgba($warning-color, 0.05);
    border-color: rgba($warning-color, 0.2);
  }
  
  &.critical {
    background: rgba($danger-color, 0.05);
    border-color: rgba($danger-color, 0.2);
  }
}

.service-info {
  flex: 1;
}

.service-name {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
  margin-bottom: 2px;
}

.service-status {
  font-size: 12px;
  color: $text-color-secondary;
}

.service-indicator {
  display: flex;
  align-items: center;
}

.indicator-dot {
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
}

// 资源监控
.resource-chart {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resource-metrics {
  width: 100%;
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
  font-size: 14px;
  font-weight: 600;
  
  &.normal {
    color: $success-color;
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
  background: $background-color-light;
  border-radius: 3px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  
  &.normal {
    background: $success-color;
  }
  
  &.warning {
    background: $warning-color;
  }
  
  &.critical {
    background: $danger-color;
  }
}

.metric-threshold {
  font-size: 11px;
  color: $text-color-light;
}

// 故障检测
.detection-results {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.detection-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-sm $spacing-md;
  border-radius: $border-radius-md;
  border: 1px solid $border-color-light;
  
  &.warning {
    background: rgba($warning-color, 0.05);
    border-color: rgba($warning-color, 0.2);
  }
  
  &.critical {
    background: rgba($danger-color, 0.05);
    border-color: rgba($danger-color, 0.2);
  }
  
  &.high {
    background: rgba($danger-color, 0.05);
    border-color: rgba($danger-color, 0.2);
  }
}

.detection-icon {
  width: 32px;
  height: 32px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  background: $background-color-light;
  color: $text-color-secondary;
}

.detection-info {
  flex: 1;
}

.detection-title {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
  margin-bottom: 2px;
}

.detection-time {
  font-size: 11px;
  color: $text-color-light;
}

.detection-status {
  .status-badge {
    padding: $spacing-xs $spacing-sm;
    border-radius: $border-radius-sm;
    font-size: 11px;
    font-weight: 500;
    
    &.detected {
      background: rgba($warning-color, 0.1);
      color: $warning-color;
    }
    
    &.recovering {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }
    
    &.resolved {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
}

// 恢复策略
.recovery-strategies {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.strategies-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.strategies-controls {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.strategy-select {
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

.strategies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: $spacing-lg;
}

.strategy-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  border-left: 4px solid;
  
  &.restart {
    border-left-color: $primary-color;
  }
  
  &.failover {
    border-left-color: $warning-color;
  }
  
  &.scaling {
    border-left-color: $info-color;
  }
  
  &.rollback {
    border-left-color: $danger-color;
  }
}

.strategy-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
  gap: $spacing-md;
}

.strategy-info {
  flex: 1;
}

.strategy-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.strategy-type {
  font-size: 12px;
  color: $text-color-secondary;
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  display: inline-block;
}

.strategy-actions {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
}

.strategy-toggle {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
  }
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: $border-color;
  transition: 0.3s;
  border-radius: 20px;
  
  &:before {
    position: absolute;
    content: "";
    height: 14px;
    width: 14px;
    left: 3px;
    bottom: 3px;
    background-color: $white;
    transition: 0.3s;
    border-radius: 50%;
  }
  
  input:checked + & {
    background-color: $primary-color;
  }
  
  input:checked + &:before {
    transform: translateX(20px);
  }
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
  
  &.retry {
    &:hover {
      border-color: $success-color;
      color: $success-color;
    }
  }
}

.strategy-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.strategy-description {
  color: $text-color-secondary;
  line-height: 1.5;
  font-size: 14px;
}

.strategy-conditions {
  .condition-title {
    font-size: 13px;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
}

.condition-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.condition-item {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
  font-size: 12px;
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
}

.condition-metric {
  color: $text-color;
  font-weight: 500;
}

.condition-operator {
  color: $text-color-secondary;
}

.condition-value {
  color: $primary-color;
  font-weight: 500;
}

.strategy-actions-list {
  .actions-title {
    font-size: 13px;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.action-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  color: $text-color-secondary;
}

.action-text {
  color: $text-color;
}

.strategy-stats {
  display: flex;
  gap: $spacing-lg;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
  font-size: 12px;
}

.stat-label {
  color: $text-color-light;
}

.stat-value {
  font-weight: 500;
  color: $text-color;
  
  &.excellent {
    color: $success-color;
  }
  
  &.good {
    color: $info-color;
  }
  
  &.normal {
    color: $warning-color;
  }
  
  &.warning {
    color: $danger-color;
  }
}

// 恢复历史
.recovery-history {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.history-controls {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.status-select {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  font-size: 13px;
  min-width: 100px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  
  .icon-search {
    position: absolute;
    left: $spacing-sm;
    color: $text-color-light;
    font-size: 14px;
  }
}

.search-input {
  padding: $spacing-sm $spacing-sm $spacing-sm 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  font-size: 13px;
  width: 200px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
  
  &::placeholder {
    color: $text-color-light;
  }
}

// 历史表格
.history-table {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-md;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 120px 120px 1fr 120px 100px 100px 120px;
  background: $background-color-light;
  border-bottom: 1px solid $border-color-light;
}

.header-cell {
  padding: $spacing-md;
  font-size: 13px;
  font-weight: 600;
  color: $text-color;
  border-right: 1px solid $border-color-light;
  
  &:last-child {
    border-right: none;
  }
}

.table-body {
  display: flex;
  flex-direction: column;
}

.table-row {
  display: grid;
  grid-template-columns: 120px 120px 1fr 120px 100px 100px 120px;
  border-bottom: 1px solid $border-color-light;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: rgba($primary-color, 0.02);
  }
  
  &:last-child {
    border-bottom: none;
  }
  
  &.success {
    border-left: 3px solid $success-color;
  }
  
  &.failed {
    border-left: 3px solid $danger-color;
  }
  
  &.running {
    border-left: 3px solid $info-color;
  }
}

.table-cell {
  padding: $spacing-md;
  font-size: 13px;
  border-right: 1px solid $border-color-light;
  display: flex;
  align-items: center;
  
  &:last-child {
    border-right: none;
  }
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.time-date {
  font-weight: 500;
  color: $text-color;
}

.time-time {
  color: $text-color-light;
  font-size: 11px;
}

.service-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.service-name {
  font-weight: 500;
  color: $text-color;
}

.service-type {
  color: $text-color-light;
  font-size: 11px;
}

.issue-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.issue-title {
  color: $text-color;
}

.issue-severity {
  font-size: 11px;
  padding: 2px $spacing-xs;
  border-radius: $border-radius-sm;
  font-weight: 500;
  
  &.low {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
  
  &.medium {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.high {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.critical {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.warning {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
}

.strategy-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.strategy-name {
  color: $text-color;
}

.strategy-type {
  color: $text-color-light;
  font-size: 11px;
}

.duration-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.duration-value {
  font-weight: 500;
  color: $text-color;
}

.duration-comparison {
  font-size: 11px;
  
  &.faster {
    color: $success-color;
  }
  
  &.slower {
    color: $danger-color;
  }
  
  &.same {
    color: $text-color-light;
  }
}

.status-badge {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
  
  &.success {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.failed {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.running {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
}

// 分页
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: $spacing-sm;
  margin-top: $spacing-lg;
}

.page-btn {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover:not(:disabled) {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.page-numbers {
  display: flex;
  gap: $spacing-xs;
}

.page-number {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
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

// 按钮样式
.btn {
  padding: $spacing-sm $spacing-md;
  border: none;
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
    color: $white;
    
    &:hover {
      background: darken($primary-color, 5%);
    }
  }
  
  &.btn-outline {
    background: $white;
    color: $text-color;
    border: 1px solid $border-color;
    
    &:hover {
      border-color: $primary-color;
      color: $primary-color;
    }
  }
  
  &.btn-sm {
    padding: $spacing-xs $spacing-sm;
    font-size: 12px;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .health-grid {
    grid-template-columns: 1fr;
  }
  
  .strategies-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .auto-recovery {
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
    grid-template-columns: 1fr;
  }
  
  .health-controls {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .strategies-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .strategies-controls {
    justify-content: flex-start;
  }
  
  .history-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .history-controls {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .search-input {
    width: 100%;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: $spacing-sm;
  }
  
  .header-cell,
  .table-cell {
    padding: $spacing-sm;
    border-right: none;
    border-bottom: 1px solid $border-color-light;
    
    &:last-child {
      border-bottom: none;
    }
  }
  
  .header-cell {
    background: $background-color;
    font-weight: 700;
    
    &:before {
      content: attr(data-label) ': ';
      font-weight: 600;
    }
  }
  
  .table-cell {
    &:before {
      content: attr(data-label) ': ';
      font-weight: 600;
      color: $text-color-secondary;
      margin-right: $spacing-xs;
    }
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .card-value {
    font-size: 24px;
  }
  
  .overview-card {
    padding: $spacing-md;
  }
  
  .card-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
  
  .strategy-card {
    padding: $spacing-md;
  }
  
  .strategy-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .strategy-actions {
    justify-content: flex-start;
  }
  
  .strategy-stats {
    flex-direction: column;
    gap: $spacing-sm;
  }
}
</style>