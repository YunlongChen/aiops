<!--
  智能优化页面
  基于AI的系统性能优化建议和自动化优化
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="intelligent-optimization">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">智能优化</h1>
          <p class="page-description">基于AI的系统性能分析和智能优化建议</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="exportReport">
            <i class="icon-download"></i>
            导出报告
          </button>
          <button class="btn btn-outline" @click="refreshAnalysis">
            <i class="icon-refresh"></i>
            刷新分析
          </button>
          <button class="btn btn-primary" @click="runOptimization">
            <i class="icon-zap"></i>
            运行优化
          </button>
        </div>
      </div>
    </div>

    <!-- 优化概览 -->
    <div class="optimization-overview">
      <div class="overview-grid">
        <div class="overview-card total">
          <div class="card-icon">
            <i class="icon-target"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ optimizationStats.totalSuggestions }}</div>
            <div class="card-label">优化建议</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +8个新建议
            </div>
          </div>
        </div>
        <div class="overview-card implemented">
          <div class="card-icon">
            <i class="icon-check-circle"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ optimizationStats.implemented }}</div>
            <div class="card-label">已实施</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +3个
            </div>
          </div>
        </div>
        <div class="overview-card potential-savings">
          <div class="card-icon">
            <i class="icon-dollar-sign"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ optimizationStats.potentialSavings }}%</div>
            <div class="card-label">潜在节省</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +5.2%
            </div>
          </div>
        </div>
        <div class="overview-card performance-gain">
          <div class="card-icon">
            <i class="icon-trending-up"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ optimizationStats.performanceGain }}%</div>
            <div class="card-label">性能提升</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +12.3%
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 优化分析 -->
    <div class="optimization-analysis">
      <div class="analysis-header">
        <h2 class="section-title">系统分析</h2>
        <div class="analysis-controls">
          <select v-model="selectedTimeRange" class="time-range-select">
            <option value="1h">最近1小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
          </select>
          <button class="btn btn-outline btn-sm" @click="runAnalysis">
            <i class="icon-play"></i>
            运行分析
          </button>
        </div>
      </div>

      <div class="analysis-content">
        <div class="analysis-grid">
          <!-- 系统健康度 -->
          <div class="analysis-card health-score">
            <div class="card-header">
              <h3 class="card-title">系统健康度</h3>
              <div class="health-score-value" :class="getHealthScoreClass(systemHealth.score)">
                {{ systemHealth.score }}
              </div>
            </div>
            <div class="card-content">
              <div class="health-indicators">
                <div class="indicator" v-for="indicator in systemHealth.indicators" :key="indicator.name">
                  <div class="indicator-info">
                    <span class="indicator-name">{{ indicator.name }}</span>
                    <span class="indicator-value" :class="indicator.status">{{ indicator.value }}</span>
                  </div>
                  <div class="indicator-bar">
                    <div 
                      class="indicator-fill"
                      :class="indicator.status"
                      :style="{ width: indicator.percentage + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 资源使用分析 -->
          <div class="analysis-card resource-analysis">
            <div class="card-header">
              <h3 class="card-title">资源使用分析</h3>
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
                        <span class="metric-value" :class="metric.status">{{ metric.current }}%</span>
                      </div>
                      <div class="metric-bar">
                        <div 
                          class="metric-fill"
                          :class="metric.status"
                          :style="{ width: metric.current + '%' }"
                        ></div>
                      </div>
                      <div class="metric-info">
                        <span class="metric-trend" :class="metric.trend">
                          <i :class="getTrendIcon(metric.trend)"></i>
                          {{ metric.change }}%
                        </span>
                        <span class="metric-threshold">阈值: {{ metric.threshold }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </BaseChart>
            </div>
          </div>

          <!-- 性能瓶颈分析 -->
          <div class="analysis-card bottleneck-analysis">
            <div class="card-header">
              <h3 class="card-title">性能瓶颈分析</h3>
            </div>
            <div class="card-content">
              <div class="bottleneck-list">
                <div 
                  class="bottleneck-item"
                  v-for="bottleneck in performanceBottlenecks"
                  :key="bottleneck.id"
                  :class="bottleneck.severity"
                >
                  <div class="bottleneck-icon">
                    <i :class="getBottleneckIcon(bottleneck.type)"></i>
                  </div>
                  <div class="bottleneck-info">
                    <div class="bottleneck-title">{{ bottleneck.title }}</div>
                    <div class="bottleneck-description">{{ bottleneck.description }}</div>
                    <div class="bottleneck-impact">
                      <span class="impact-label">影响程度:</span>
                      <span class="impact-value" :class="bottleneck.severity">{{ bottleneck.impact }}</span>
                    </div>
                  </div>
                  <div class="bottleneck-actions">
                    <button class="action-btn" @click="viewBottleneckDetail(bottleneck)">
                      <i class="icon-eye"></i>
                      详情
                    </button>
                    <button class="action-btn primary" @click="optimizeBottleneck(bottleneck)">
                      <i class="icon-zap"></i>
                      优化
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 优化建议 -->
    <div class="optimization-suggestions">
      <div class="suggestions-header">
        <h2 class="section-title">优化建议</h2>
        <div class="suggestions-controls">
          <select v-model="selectedCategory" class="category-select">
            <option value="">全部类型</option>
            <option value="performance">性能优化</option>
            <option value="resource">资源优化</option>
            <option value="cost">成本优化</option>
            <option value="security">安全优化</option>
            <option value="reliability">可靠性优化</option>
          </select>
          <select v-model="selectedPriority" class="priority-select">
            <option value="">全部优先级</option>
            <option value="high">高优先级</option>
            <option value="medium">中优先级</option>
            <option value="low">低优先级</option>
          </select>
        </div>
      </div>

      <div class="suggestions-content">
        <div class="suggestions-list">
          <div 
            class="suggestion-card"
            v-for="suggestion in filteredSuggestions"
            :key="suggestion.id"
            :class="[suggestion.priority, suggestion.status]"
          >
            <div class="suggestion-header">
              <div class="suggestion-info">
                <div class="suggestion-title">{{ suggestion.title }}</div>
                <div class="suggestion-meta">
                  <span class="suggestion-category" :class="suggestion.category">
                    {{ getCategoryName(suggestion.category) }}
                  </span>
                  <span class="suggestion-priority" :class="suggestion.priority">
                    {{ getPriorityName(suggestion.priority) }}
                  </span>
                  <span class="suggestion-status" :class="suggestion.status">
                    {{ getStatusName(suggestion.status) }}
                  </span>
                </div>
              </div>
              <div class="suggestion-actions">
                <button 
                  v-if="suggestion.status === 'pending'"
                  class="action-btn success"
                  @click="implementSuggestion(suggestion)"
                >
                  <i class="icon-play"></i>
                  实施
                </button>
                <button 
                  v-if="suggestion.status === 'pending'"
                  class="action-btn"
                  @click="dismissSuggestion(suggestion)"
                >
                  <i class="icon-x"></i>
                  忽略
                </button>
                <button 
                  class="action-btn"
                  @click="viewSuggestionDetail(suggestion)"
                >
                  <i class="icon-eye"></i>
                  详情
                </button>
              </div>
            </div>
            
            <div class="suggestion-content">
              <div class="suggestion-description">{{ suggestion.description }}</div>
              
              <div class="suggestion-benefits">
                <div class="benefit-item" v-for="benefit in suggestion.benefits" :key="benefit.type">
                  <div class="benefit-icon">
                    <i :class="getBenefitIcon(benefit.type)"></i>
                  </div>
                  <div class="benefit-info">
                    <span class="benefit-label">{{ benefit.label }}</span>
                    <span class="benefit-value" :class="benefit.type">{{ benefit.value }}</span>
                  </div>
                </div>
              </div>
              
              <div class="suggestion-implementation" v-if="suggestion.status === 'pending'">
                <div class="implementation-info">
                  <div class="info-item">
                    <span class="info-label">预计时间:</span>
                    <span class="info-value">{{ suggestion.estimatedTime }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">复杂度:</span>
                    <span class="info-value" :class="suggestion.complexity">{{ getComplexityName(suggestion.complexity) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">风险等级:</span>
                    <span class="info-value" :class="suggestion.risk">{{ getRiskName(suggestion.risk) }}</span>
                  </div>
                </div>
              </div>
              
              <div class="suggestion-progress" v-if="suggestion.status === 'implementing'">
                <div class="progress-info">
                  <span class="progress-label">实施进度</span>
                  <span class="progress-percentage">{{ suggestion.progress }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill"
                    :style="{ width: suggestion.progress + '%' }"
                  ></div>
                </div>
                <div class="progress-status">{{ suggestion.progressStatus }}</div>
              </div>
              
              <div class="suggestion-result" v-if="suggestion.status === 'completed'">
                <div class="result-info">
                  <div class="result-item">
                    <span class="result-label">实施时间:</span>
                    <span class="result-value">{{ formatDateTime(suggestion.completedAt) }}</span>
                  </div>
                  <div class="result-item">
                    <span class="result-label">实际效果:</span>
                    <span class="result-value positive">{{ suggestion.actualBenefit }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <EmptyState
          v-if="filteredSuggestions.length === 0"
          icon="icon-lightbulb"
          title="暂无优化建议"
          description="系统运行良好，暂时没有发现需要优化的地方"
          :actions="[
            { text: '运行分析', action: runAnalysis },
            { text: '刷新数据', action: refreshAnalysis }
          ]"
        />
      </div>
    </div>

    <!-- 自动优化设置 -->
    <div class="auto-optimization">
      <div class="auto-header">
        <h2 class="section-title">自动优化设置</h2>
        <div class="auto-toggle">
          <label class="toggle-switch">
            <input type="checkbox" v-model="autoOptimizationEnabled">
            <span class="toggle-slider"></span>
          </label>
          <span class="toggle-label">启用自动优化</span>
        </div>
      </div>

      <div class="auto-content" v-if="autoOptimizationEnabled">
        <div class="auto-settings">
          <div class="setting-group">
            <h3 class="group-title">优化策略</h3>
            <div class="strategy-options">
              <label class="strategy-option" v-for="strategy in optimizationStrategies" :key="strategy.id">
                <input 
                  type="checkbox" 
                  v-model="selectedStrategies"
                  :value="strategy.id"
                >
                <div class="option-content">
                  <div class="option-title">{{ strategy.title }}</div>
                  <div class="option-description">{{ strategy.description }}</div>
                </div>
              </label>
            </div>
          </div>
          
          <div class="setting-group">
            <h3 class="group-title">执行条件</h3>
            <div class="condition-settings">
              <div class="condition-item">
                <label class="condition-label">CPU使用率超过</label>
                <input 
                  type="number" 
                  v-model="autoConditions.cpuThreshold"
                  class="condition-input"
                  min="0" 
                  max="100"
                >
                <span class="condition-unit">%</span>
              </div>
              <div class="condition-item">
                <label class="condition-label">内存使用率超过</label>
                <input 
                  type="number" 
                  v-model="autoConditions.memoryThreshold"
                  class="condition-input"
                  min="0" 
                  max="100"
                >
                <span class="condition-unit">%</span>
              </div>
              <div class="condition-item">
                <label class="condition-label">响应时间超过</label>
                <input 
                  type="number" 
                  v-model="autoConditions.responseTimeThreshold"
                  class="condition-input"
                  min="0"
                >
                <span class="condition-unit">ms</span>
              </div>
            </div>
          </div>
          
          <div class="setting-group">
            <h3 class="group-title">执行时间</h3>
            <div class="schedule-settings">
              <div class="schedule-item">
                <label class="schedule-label">
                  <input 
                    type="radio" 
                    v-model="autoSchedule.type"
                    value="immediate"
                  >
                  立即执行
                </label>
              </div>
              <div class="schedule-item">
                <label class="schedule-label">
                  <input 
                    type="radio" 
                    v-model="autoSchedule.type"
                    value="scheduled"
                  >
                  定时执行
                </label>
                <select 
                  v-if="autoSchedule.type === 'scheduled'"
                  v-model="autoSchedule.time"
                  class="schedule-select"
                >
                  <option value="02:00">凌晨2点</option>
                  <option value="03:00">凌晨3点</option>
                  <option value="04:00">凌晨4点</option>
                  <option value="05:00">凌晨5点</option>
                </select>
              </div>
              <div class="schedule-item">
                <label class="schedule-label">
                  <input 
                    type="radio" 
                    v-model="autoSchedule.type"
                    value="maintenance"
                  >
                  维护窗口执行
                </label>
              </div>
            </div>
          </div>
        </div>
        
        <div class="auto-actions">
          <button class="btn btn-outline" @click="resetAutoSettings">重置设置</button>
          <button class="btn btn-primary" @click="saveAutoSettings">保存设置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 智能优化页面组件
 * 基于AI的系统性能优化建议和自动化优化
 */
import { ref, computed, onMounted } from 'vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import EmptyState from '@/components/common/EmptyState.vue'

// 响应式数据
const selectedTimeRange = ref('24h')
const selectedCategory = ref('')
const selectedPriority = ref('')
const autoOptimizationEnabled = ref(false)
const selectedStrategies = ref([])

// 优化统计数据
const optimizationStats = ref({
  totalSuggestions: 24,
  implemented: 8,
  potentialSavings: 23.5,
  performanceGain: 18.7
})

// 系统健康度数据
const systemHealth = ref({
  score: 85,
  indicators: [
    { name: 'CPU性能', value: '良好', percentage: 85, status: 'good' },
    { name: '内存使用', value: '正常', percentage: 72, status: 'normal' },
    { name: '磁盘I/O', value: '优秀', percentage: 92, status: 'excellent' },
    { name: '网络延迟', value: '正常', percentage: 78, status: 'normal' },
    { name: '服务可用性', value: '优秀', percentage: 98, status: 'excellent' }
  ]
})

// 资源使用指标
const resourceMetrics = ref([
  { name: 'CPU', current: 68, threshold: 80, trend: 'up', change: 5.2, status: 'normal' },
  { name: '内存', current: 72, threshold: 85, trend: 'stable', change: 0.8, status: 'normal' },
  { name: '磁盘', current: 45, threshold: 90, trend: 'down', change: -2.1, status: 'good' },
  { name: '网络', current: 34, threshold: 70, trend: 'up', change: 8.5, status: 'good' }
])

// 性能瓶颈数据
const performanceBottlenecks = ref([
  {
    id: 1,
    type: 'cpu',
    title: 'CPU使用率过高',
    description: '服务器CPU使用率持续超过70%，影响系统响应速度',
    severity: 'high',
    impact: '高'
  },
  {
    id: 2,
    type: 'memory',
    title: '内存碎片化严重',
    description: '系统内存碎片化程度较高，可能导致内存分配效率降低',
    severity: 'medium',
    impact: '中'
  },
  {
    id: 3,
    type: 'disk',
    title: '磁盘I/O瓶颈',
    description: '数据库查询频繁，磁盘I/O成为性能瓶颈',
    severity: 'medium',
    impact: '中'
  },
  {
    id: 4,
    type: 'network',
    title: '网络带宽不足',
    description: '高峰期网络带宽使用率接近上限',
    severity: 'low',
    impact: '低'
  }
])

// 优化建议数据
const suggestions = ref([
  {
    id: 1,
    title: '启用CPU缓存优化',
    description: '通过调整CPU缓存策略，提高处理器效率，减少计算延迟',
    category: 'performance',
    priority: 'high',
    status: 'pending',
    benefits: [
      { type: 'performance', label: '性能提升', value: '+15%' },
      { type: 'cost', label: '成本节省', value: '$120/月' }
    ],
    estimatedTime: '2小时',
    complexity: 'medium',
    risk: 'low'
  },
  {
    id: 2,
    title: '优化数据库查询',
    description: '分析慢查询并添加适当索引，优化数据库性能',
    category: 'performance',
    priority: 'high',
    status: 'implementing',
    progress: 65,
    progressStatus: '正在添加索引...',
    benefits: [
      { type: 'performance', label: '查询速度', value: '+40%' },
      { type: 'resource', label: '资源节省', value: '+25%' }
    ]
  },
  {
    id: 3,
    title: '调整内存分配策略',
    description: '优化JVM内存配置，减少垃圾回收频率',
    category: 'resource',
    priority: 'medium',
    status: 'completed',
    completedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    actualBenefit: '内存使用率降低18%',
    benefits: [
      { type: 'resource', label: '内存优化', value: '+20%' },
      { type: 'performance', label: '响应时间', value: '-12%' }
    ]
  },
  {
    id: 4,
    title: '启用负载均衡优化',
    description: '调整负载均衡算法，提高请求分发效率',
    category: 'performance',
    priority: 'medium',
    status: 'pending',
    benefits: [
      { type: 'performance', label: '吞吐量', value: '+30%' },
      { type: 'reliability', label: '可用性', value: '+5%' }
    ],
    estimatedTime: '4小时',
    complexity: 'high',
    risk: 'medium'
  },
  {
    id: 5,
    title: '压缩静态资源',
    description: '启用Gzip压缩，减少网络传输数据量',
    category: 'cost',
    priority: 'low',
    status: 'pending',
    benefits: [
      { type: 'cost', label: '带宽节省', value: '$80/月' },
      { type: 'performance', label: '加载速度', value: '+25%' }
    ],
    estimatedTime: '1小时',
    complexity: 'low',
    risk: 'low'
  }
])

// 自动优化策略
const optimizationStrategies = ref([
  {
    id: 'auto-scaling',
    title: '自动扩缩容',
    description: '根据负载自动调整资源配置'
  },
  {
    id: 'cache-optimization',
    title: '缓存优化',
    description: '自动调整缓存策略和配置'
  },
  {
    id: 'query-optimization',
    title: '查询优化',
    description: '自动优化数据库查询性能'
  },
  {
    id: 'resource-cleanup',
    title: '资源清理',
    description: '自动清理无用资源和临时文件'
  }
])

// 自动优化条件
const autoConditions = ref({
  cpuThreshold: 80,
  memoryThreshold: 85,
  responseTimeThreshold: 1000
})

// 自动优化调度
const autoSchedule = ref({
  type: 'scheduled',
  time: '03:00'
})

// 计算属性
const filteredSuggestions = computed(() => {
  let filtered = suggestions.value

  if (selectedCategory.value) {
    filtered = filtered.filter(s => s.category === selectedCategory.value)
  }

  if (selectedPriority.value) {
    filtered = filtered.filter(s => s.priority === selectedPriority.value)
  }

  return filtered.sort((a, b) => {
    const priorityOrder = { high: 3, medium: 2, low: 1 }
    return priorityOrder[b.priority] - priorityOrder[a.priority]
  })
})

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
 * 获取趋势图标
 */
const getTrendIcon = (trend) => {
  const icons = {
    up: 'icon-trending-up',
    down: 'icon-trending-down',
    stable: 'icon-minus'
  }
  return icons[trend] || 'icon-minus'
}

/**
 * 获取瓶颈图标
 */
const getBottleneckIcon = (type) => {
  const icons = {
    cpu: 'icon-cpu',
    memory: 'icon-memory',
    disk: 'icon-hard-drive',
    network: 'icon-wifi'
  }
  return icons[type] || 'icon-alert-circle'
}

/**
 * 获取类型名称
 */
const getCategoryName = (category) => {
  const names = {
    performance: '性能优化',
    resource: '资源优化',
    cost: '成本优化',
    security: '安全优化',
    reliability: '可靠性优化'
  }
  return names[category] || category
}

/**
 * 获取优先级名称
 */
const getPriorityName = (priority) => {
  const names = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  }
  return names[priority] || priority
}

/**
 * 获取状态名称
 */
const getStatusName = (status) => {
  const names = {
    pending: '待实施',
    implementing: '实施中',
    completed: '已完成',
    dismissed: '已忽略'
  }
  return names[status] || status
}

/**
 * 获取复杂度名称
 */
const getComplexityName = (complexity) => {
  const names = {
    low: '简单',
    medium: '中等',
    high: '复杂'
  }
  return names[complexity] || complexity
}

/**
 * 获取风险等级名称
 */
const getRiskName = (risk) => {
  const names = {
    low: '低风险',
    medium: '中风险',
    high: '高风险'
  }
  return names[risk] || risk
}

/**
 * 获取收益图标
 */
const getBenefitIcon = (type) => {
  const icons = {
    performance: 'icon-zap',
    cost: 'icon-dollar-sign',
    resource: 'icon-cpu',
    reliability: 'icon-shield'
  }
  return icons[type] || 'icon-trending-up'
}

/**
 * 格式化日期时间
 */
const formatDateTime = (datetime) => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(datetime)
}

/**
 * 导出报告
 */
const exportReport = () => {
  console.log('导出优化报告')
}

/**
 * 刷新分析
 */
const refreshAnalysis = () => {
  console.log('刷新分析数据')
}

/**
 * 运行优化
 */
const runOptimization = () => {
  console.log('运行智能优化')
}

/**
 * 运行分析
 */
const runAnalysis = () => {
  console.log('运行系统分析')
}

/**
 * 查看瓶颈详情
 */
const viewBottleneckDetail = (bottleneck) => {
  console.log('查看瓶颈详情:', bottleneck)
}

/**
 * 优化瓶颈
 */
const optimizeBottleneck = (bottleneck) => {
  console.log('优化瓶颈:', bottleneck)
}

/**
 * 实施建议
 */
const implementSuggestion = (suggestion) => {
  suggestion.status = 'implementing'
  suggestion.progress = 0
  console.log('实施优化建议:', suggestion)
}

/**
 * 忽略建议
 */
const dismissSuggestion = (suggestion) => {
  suggestion.status = 'dismissed'
  console.log('忽略优化建议:', suggestion)
}

/**
 * 查看建议详情
 */
const viewSuggestionDetail = (suggestion) => {
  console.log('查看建议详情:', suggestion)
}

/**
 * 重置自动设置
 */
const resetAutoSettings = () => {
  selectedStrategies.value = []
  autoConditions.value = {
    cpuThreshold: 80,
    memoryThreshold: 85,
    responseTimeThreshold: 1000
  }
  autoSchedule.value = {
    type: 'scheduled',
    time: '03:00'
  }
}

/**
 * 保存自动设置
 */
const saveAutoSettings = () => {
  console.log('保存自动优化设置')
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.intelligent-optimization {
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

// 优化概览
.optimization-overview {
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
  
  &.implemented {
    border-left-color: $success-color;
    
    .card-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
  
  &.potential-savings {
    border-left-color: $warning-color;
    
    .card-icon {
      background: rgba($warning-color, 0.1);
      color: $warning-color;
    }
  }
  
  &.performance-gain {
    border-left-color: $info-color;
    
    .card-icon {
      background: rgba($info-color, 0.1);
      color: $info-color;
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
}

// 优化分析
.optimization-analysis {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.analysis-header {
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

.analysis-controls {
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

.analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-lg;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.analysis-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  overflow: hidden;
  
  &.health-score {
    grid-row: span 2;
    
    @media (max-width: 1200px) {
      grid-row: span 1;
    }
  }
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

.health-score-value {
  font-size: 32px;
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

.health-indicators {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.indicator {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.indicator-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.indicator-name {
  font-size: 14px;
  color: $text-color;
}

.indicator-value {
  font-size: 13px;
  font-weight: 500;
  
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

.indicator-bar {
  height: 6px;
  background: $background-color-light;
  border-radius: 3px;
  overflow: hidden;
}

.indicator-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  
  &.excellent {
    background: $success-color;
  }
  
  &.good {
    background: $info-color;
  }
  
  &.normal {
    background: $warning-color;
  }
  
  &.warning {
    background: $danger-color;
  }
}

// 资源分析
.resource-chart {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resource-metrics {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
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
  font-size: 14px;
  color: $text-color;
  font-weight: 500;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  
  &.good {
    color: $success-color;
  }
  
  &.normal {
    color: $warning-color;
  }
  
  &.warning {
    color: $danger-color;
  }
}

.metric-bar {
  height: 8px;
  background: $background-color-light;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
  
  &.good {
    background: $success-color;
  }
  
  &.normal {
    background: $warning-color;
  }
  
  &.warning {
    background: $danger-color;
  }
}

.metric-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-weight: 500;
  
  &.up {
    color: $danger-color;
  }
  
  &.down {
    color: $success-color;
  }
  
  &.stable {
    color: $text-color-light;
  }
}

.metric-threshold {
  color: $text-color-light;
}

// 瓶颈分析
.bottleneck-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.bottleneck-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-md;
  border: 1px solid $border-color-light;
  border-radius: $border-radius-md;
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

.bottleneck-icon {
  width: 40px;
  height: 40px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  background: $background-color-light;
  color: $text-color-secondary;
}

.bottleneck-info {
  flex: 1;
}

.bottleneck-title {
  font-size: 14px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.bottleneck-description {
  font-size: 13px;
  color: $text-color-secondary;
  line-height: 1.4;
  margin-bottom: $spacing-xs;
}

.bottleneck-impact {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
  font-size: 12px;
}

.impact-label {
  color: $text-color-light;
}

.impact-value {
  font-weight: 500;
  
  &.high {
    color: $danger-color;
  }
  
  &.medium {
    color: $warning-color;
  }
  
  &.low {
    color: $info-color;
  }
}

.bottleneck-actions {
  display: flex;
  gap: $spacing-xs;
}

.action-btn {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  
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
    }
  }
  
  &.success {
    &:hover {
      border-color: $success-color;
      color: $success-color;
    }
  }
}

// 优化建议
.optimization-suggestions {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.suggestions-controls {
  display: flex;
  gap: $spacing-md;
}

.category-select,
.priority-select {
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

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.suggestion-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
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
  
  &.completed {
    background: rgba($success-color, 0.02);
    border-left-color: $success-color;
  }
  
  &.implementing {
    background: rgba($info-color, 0.02);
    border-left-color: $info-color;
  }
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
  gap: $spacing-md;
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

.suggestion-meta {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
}

.suggestion-category,
.suggestion-priority,
.suggestion-status {
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
}

.suggestion-category {
  &.performance {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
  }
  
  &.resource {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.cost {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.security {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.reliability {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
}

.suggestion-priority {
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

.suggestion-status {
  &.pending {
    background: rgba($text-color-light, 0.1);
    color: $text-color-light;
  }
  
  &.implementing {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
  
  &.completed {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.dismissed {
    background: rgba($text-color-light, 0.1);
    color: $text-color-light;
  }
}

.suggestion-actions {
  display: flex;
  gap: $spacing-xs;
}

.suggestion-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.suggestion-description {
  color: $text-color-secondary;
  line-height: 1.5;
  font-size: 14px;
}

.suggestion-benefits {
  display: flex;
  gap: $spacing-md;
  flex-wrap: wrap;
}

.benefit-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-md;
  background: $background-color-light;
  border-radius: $border-radius-md;
}

.benefit-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: $text-color-secondary;
}

.benefit-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.benefit-label {
  font-size: 11px;
  color: $text-color-light;
}

.benefit-value {
  font-size: 13px;
  font-weight: 600;
  
  &.performance {
    color: $primary-color;
  }
  
  &.cost {
    color: $warning-color;
  }
  
  &.resource {
    color: $success-color;
  }
  
  &.reliability {
    color: $info-color;
  }
}

.suggestion-implementation {
  padding: $spacing-md;
  background: rgba($info-color, 0.05);
  border-radius: $border-radius-md;
}

.implementation-info {
  display: flex;
  gap: $spacing-lg;
  flex-wrap: wrap;
}

.info-item {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
  font-size: 13px;
}

.info-label {
  color: $text-color-light;
}

.info-value {
  font-weight: 500;
  color: $text-color;
  
  &.low {
    color: $success-color;
  }
  
  &.medium {
    color: $warning-color;
  }
  
  &.high {
    color: $danger-color;
  }
}

.suggestion-progress {
  padding: $spacing-md;
  background: rgba($info-color, 0.05);
  border-radius: $border-radius-md;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
}

.progress-label {
  font-size: 13px;
  color: $text-color-secondary;
}

.progress-percentage {
  font-size: 13px;
  font-weight: 600;
  color: $info-color;
}

.progress-bar {
  height: 8px;
  background: $background-color-light;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: $spacing-sm;
}

.progress-fill {
  height: 100%;
  background: $info-color;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-status {
  font-size: 12px;
  color: $text-color-light;
}

.suggestion-result {
  padding: $spacing-md;
  background: rgba($success-color, 0.05);
  border-radius: $border-radius-md;
}

.result-info {
  display: flex;
  gap: $spacing-lg;
  flex-wrap: wrap;
}

.result-item {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
  font-size: 13px;
}

.result-label {
  color: $text-color-light;
}

.result-value {
  font-weight: 500;
  color: $text-color;
  
  &.positive {
    color: $success-color;
  }
}

// 自动优化设置
.auto-optimization {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
}

.auto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
}

.auto-toggle {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  
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
  border-radius: 24px;
  
  &:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
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
    transform: translateX(24px);
  }
}

.toggle-label {
  font-size: 14px;
  color: $text-color;
}

.auto-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.auto-settings {
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.setting-group {
  .group-title {
    margin: 0 0 $spacing-md 0;
    font-size: 16px;
    font-weight: 600;
    color: $text-color;
  }
}

.strategy-options {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.strategy-option {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  padding: $spacing-md;
  border: 1px solid $border-color-light;
  border-radius: $border-radius-md;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: $primary-color;
    background: rgba($primary-color, 0.02);
  }
  
  input {
    margin-top: 2px;
  }
}

.option-content {
  flex: 1;
}

.option-title {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.option-description {
  font-size: 13px;
  color: $text-color-secondary;
  line-height: 1.4;
}

.condition-settings {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.condition-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.condition-label {
  min-width: 120px;
  font-size: 14px;
  color: $text-color;
}

.condition-input {
  width: 80px;
  padding: $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  text-align: center;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.condition-unit {
  font-size: 14px;
  color: $text-color-light;
}

.schedule-settings {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.schedule-label {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: 14px;
  color: $text-color;
  cursor: pointer;
}

.schedule-select {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color;
  font-size: 13px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.auto-actions {
  display: flex;
  justify-content: flex-end;
  gap: $spacing-md;
}

// 响应式设计
@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .intelligent-optimization {
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
  
  .overview-card {
    flex-direction: column;
    text-align: center;
    gap: $spacing-sm;
  }
  
  .analysis-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .suggestions-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .suggestions-controls {
    flex-direction: column;
  }
  
  .suggestion-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .suggestion-actions {
    justify-content: flex-start;
  }
  
  .suggestion-benefits {
    flex-direction: column;
  }
  
  .implementation-info,
  .result-info {
    flex-direction: column;
    gap: $spacing-sm;
  }
  
  .auto-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .condition-item,
  .schedule-item {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-xs;
  }
  
  .condition-label,
  .schedule-label {
    min-width: auto;
  }
  
  .auto-actions {
    justify-content: stretch;
    
    .btn {
      flex: 1;
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
  
  .health-score-value {
    font-size: 28px;
  }
  
  .bottleneck-item {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .bottleneck-actions {
    justify-content: flex-start;
  }
  
  .strategy-option {
    flex-direction: column;
    gap: $spacing-sm;
  }
}
</style>