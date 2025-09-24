<!--
  异常检测页面
  展示AI异常检测的结果和配置
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="anomaly-detection">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">异常检测</h1>
          <p class="page-description">基于AI算法的智能异常检测与分析</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="exportReport">
            <i class="icon-download"></i>
            导出报告
          </button>
          <button class="btn btn-outline" @click="configureDetection">
            <i class="icon-settings"></i>
            检测配置
          </button>
          <button class="btn btn-primary" @click="runDetection">
            <i class="icon-play"></i>
            运行检测
          </button>
        </div>
      </div>
    </div>

    <!-- 检测概览 -->
    <div class="detection-overview">
      <div class="overview-grid">
        <div class="overview-card total">
          <div class="card-icon">
            <i class="icon-activity"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ detectionStats.total }}</div>
            <div class="card-label">检测项目</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +12%
            </div>
          </div>
        </div>
        <div class="overview-card anomalies">
          <div class="card-icon">
            <i class="icon-alert-triangle"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ detectionStats.anomalies }}</div>
            <div class="card-label">发现异常</div>
            <div class="card-trend negative">
              <i class="icon-trending-down"></i>
              -8%
            </div>
          </div>
        </div>
        <div class="overview-card accuracy">
          <div class="card-icon">
            <i class="icon-target"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ detectionStats.accuracy }}%</div>
            <div class="card-label">检测准确率</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +2.5%
            </div>
          </div>
        </div>
        <div class="overview-card processing">
          <div class="card-icon">
            <i class="icon-cpu"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ detectionStats.processing }}</div>
            <div class="card-label">处理中</div>
            <div class="card-status">
              <LoadingSpinner size="small" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 检测结果 -->
    <div class="detection-results">
      <div class="results-header">
        <h2 class="section-title">检测结果</h2>
        <div class="results-controls">
          <div class="time-range">
            <select v-model="selectedTimeRange" class="time-select">
              <option value="1h">最近1小时</option>
              <option value="6h">最近6小时</option>
              <option value="24h">最近24小时</option>
              <option value="7d">最近7天</option>
            </select>
          </div>
          <div class="view-toggle">
            <button 
              class="toggle-btn"
              :class="{ active: viewMode === 'chart' }"
              @click="viewMode = 'chart'"
            >
              <i class="icon-bar-chart"></i>
              图表视图
            </button>
            <button 
              class="toggle-btn"
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
            >
              <i class="icon-list"></i>
              列表视图
            </button>
          </div>
        </div>
      </div>

      <!-- 图表视图 -->
      <div v-if="viewMode === 'chart'" class="chart-view">
        <div class="charts-grid">
          <div class="chart-container">
            <BaseChart
              title="异常检测趋势"
              :loading="false"
              :error="false"
              :no-data="false"
            >
              <div class="chart-placeholder">
                <div class="chart-content">
                  <div class="trend-chart">
                    <div class="chart-line">
                      <div class="line-segment normal"></div>
                      <div class="line-segment anomaly"></div>
                      <div class="line-segment normal"></div>
                      <div class="line-segment warning"></div>
                      <div class="line-segment normal"></div>
                    </div>
                    <div class="chart-labels">
                      <span>00:00</span>
                      <span>06:00</span>
                      <span>12:00</span>
                      <span>18:00</span>
                      <span>24:00</span>
                    </div>
                  </div>
                </div>
              </div>
            </BaseChart>
          </div>
          <div class="chart-container">
            <BaseChart
              title="异常类型分布"
              :loading="false"
              :error="false"
              :no-data="false"
            >
              <div class="chart-placeholder">
                <div class="pie-chart">
                  <div class="pie-segment cpu" style="--percentage: 35%"></div>
                  <div class="pie-segment memory" style="--percentage: 25%"></div>
                  <div class="pie-segment network" style="--percentage: 20%"></div>
                  <div class="pie-segment disk" style="--percentage: 20%"></div>
                </div>
                <div class="pie-legend">
                  <div class="legend-item">
                    <span class="legend-color cpu"></span>
                    <span class="legend-text">CPU异常 (35%)</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color memory"></span>
                    <span class="legend-text">内存异常 (25%)</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color network"></span>
                    <span class="legend-text">网络异常 (20%)</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color disk"></span>
                    <span class="legend-text">磁盘异常 (20%)</span>
                  </div>
                </div>
              </div>
            </BaseChart>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="list-view">
        <div class="anomaly-list">
          <div class="list-filters">
            <div class="filter-group">
              <select v-model="selectedSeverity" class="filter-select">
                <option value="">全部级别</option>
                <option value="high">高风险</option>
                <option value="medium">中风险</option>
                <option value="low">低风险</option>
              </select>
            </div>
            <div class="filter-group">
              <select v-model="selectedType" class="filter-select">
                <option value="">全部类型</option>
                <option value="cpu">CPU异常</option>
                <option value="memory">内存异常</option>
                <option value="network">网络异常</option>
                <option value="disk">磁盘异常</option>
              </select>
            </div>
            <div class="filter-group search-group">
              <div class="search-input">
                <i class="icon-search"></i>
                <input 
                  type="text" 
                  v-model="searchQuery"
                  placeholder="搜索异常描述..."
                >
              </div>
            </div>
          </div>

          <div class="anomaly-items">
            <div 
              v-for="anomaly in filteredAnomalies" 
              :key="anomaly.id"
              class="anomaly-item"
              :class="anomaly.severity"
            >
              <div class="anomaly-header">
                <div class="anomaly-info">
                  <div class="anomaly-title">{{ anomaly.title }}</div>
                  <div class="anomaly-time">{{ formatTime(anomaly.detectedAt) }}</div>
                </div>
                <div class="anomaly-badges">
                  <StatusBadge 
                    :status="anomaly.severity" 
                    :variant="getSeverityVariant(anomaly.severity)"
                  />
                  <StatusBadge 
                    :status="anomaly.type" 
                    :variant="getTypeVariant(anomaly.type)"
                  />
                </div>
              </div>
              <div class="anomaly-content">
                <div class="anomaly-description">{{ anomaly.description }}</div>
                <div class="anomaly-metrics">
                  <div class="metric-item">
                    <span class="metric-label">置信度:</span>
                    <span class="metric-value">{{ anomaly.confidence }}%</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">影响范围:</span>
                    <span class="metric-value">{{ anomaly.impact }}</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">数据源:</span>
                    <span class="metric-value">{{ anomaly.source }}</span>
                  </div>
                </div>
              </div>
              <div class="anomaly-actions">
                <button class="action-btn" @click="viewAnomalyDetail(anomaly)">
                  <i class="icon-eye"></i>
                  查看详情
                </button>
                <button class="action-btn" @click="acknowledgeAnomaly(anomaly)">
                  <i class="icon-check"></i>
                  确认异常
                </button>
                <button class="action-btn" @click="ignoreAnomaly(anomaly)">
                  <i class="icon-x"></i>
                  忽略
                </button>
              </div>
            </div>
          </div>

          <!-- 空状态 -->
          <EmptyState
            v-if="filteredAnomalies.length === 0"
            icon="icon-search"
            title="未发现异常"
            description="在当前时间范围内未检测到任何异常"
            :actions="[
              { text: '重新检测', action: runDetection },
              { text: '调整配置', action: configureDetection }
            ]"
          />
        </div>
      </div>
    </div>

    <!-- 检测模型 -->
    <div class="detection-models">
      <div class="models-header">
        <h2 class="section-title">检测模型</h2>
        <button class="btn btn-outline btn-sm" @click="manageModels">
          <i class="icon-settings"></i>
          管理模型
        </button>
      </div>
      <div class="models-grid">
        <div 
          v-for="model in detectionModels" 
          :key="model.id"
          class="model-card"
          :class="{ active: model.status === 'active' }"
        >
          <div class="model-header">
            <div class="model-info">
              <div class="model-name">{{ model.name }}</div>
              <div class="model-type">{{ model.type }}</div>
            </div>
            <div class="model-status">
              <StatusBadge 
                :status="model.status" 
                :variant="model.status === 'active' ? 'success' : 'default'"
              />
            </div>
          </div>
          <div class="model-content">
            <div class="model-description">{{ model.description }}</div>
            <div class="model-metrics">
              <div class="metric">
                <span class="metric-label">准确率</span>
                <span class="metric-value">{{ model.accuracy }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">召回率</span>
                <span class="metric-value">{{ model.recall }}%</span>
              </div>
              <div class="metric">
                <span class="metric-label">F1分数</span>
                <span class="metric-value">{{ model.f1Score }}</span>
              </div>
            </div>
          </div>
          <div class="model-actions">
            <button 
              class="model-action-btn"
              @click="toggleModel(model)"
              :class="{ active: model.status === 'active' }"
            >
              {{ model.status === 'active' ? '停用' : '启用' }}
            </button>
            <button class="model-action-btn" @click="configureModel(model)">
              配置
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 异常检测页面组件
 * 展示AI异常检测的结果和配置
 */
import { ref, computed, onMounted } from 'vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

// 响应式数据
const selectedTimeRange = ref('24h')
const viewMode = ref('chart')
const selectedSeverity = ref('')
const selectedType = ref('')
const searchQuery = ref('')

// 检测统计数据
const detectionStats = ref({
  total: 156,
  anomalies: 23,
  accuracy: 94.2,
  processing: 8
})

// 异常数据
const anomalies = ref([
  {
    id: 1,
    title: 'CPU使用率异常峰值',
    description: '服务器web-01的CPU使用率在过去30分钟内出现异常峰值，超出正常范围3个标准差',
    severity: 'high',
    type: 'cpu',
    confidence: 95.8,
    impact: '单台服务器',
    source: 'web-01',
    detectedAt: new Date(Date.now() - 30 * 60 * 1000)
  },
  {
    id: 2,
    title: '内存泄漏检测',
    description: '应用服务器app-02检测到潜在的内存泄漏模式，内存使用量持续增长',
    severity: 'medium',
    type: 'memory',
    confidence: 87.3,
    impact: '应用服务',
    source: 'app-02',
    detectedAt: new Date(Date.now() - 2 * 60 * 60 * 1000)
  },
  {
    id: 3,
    title: '网络延迟异常',
    description: '网络设备switch-01出现间歇性延迟异常，可能影响数据传输',
    severity: 'medium',
    type: 'network',
    confidence: 78.9,
    impact: '网络连接',
    source: 'switch-01',
    detectedAt: new Date(Date.now() - 4 * 60 * 60 * 1000)
  },
  {
    id: 4,
    title: '磁盘IO异常',
    description: '数据库服务器db-01的磁盘IO模式异常，可能存在性能瓶颈',
    severity: 'low',
    type: 'disk',
    confidence: 72.1,
    impact: '数据库性能',
    source: 'db-01',
    detectedAt: new Date(Date.now() - 6 * 60 * 60 * 1000)
  },
  {
    id: 5,
    title: '业务指标异常',
    description: '订单处理量出现异常下降，可能存在系统问题',
    severity: 'high',
    type: 'business',
    confidence: 91.2,
    impact: '业务流程',
    source: 'order-service',
    detectedAt: new Date(Date.now() - 8 * 60 * 60 * 1000)
  }
])

// 检测模型
const detectionModels = ref([
  {
    id: 1,
    name: 'LSTM时序异常检测',
    type: '深度学习',
    description: '基于长短期记忆网络的时间序列异常检测模型',
    status: 'active',
    accuracy: 94.2,
    recall: 89.7,
    f1Score: 0.918
  },
  {
    id: 2,
    name: 'Isolation Forest',
    description: '基于孤立森林算法的无监督异常检测',
    type: '机器学习',
    status: 'active',
    accuracy: 87.5,
    recall: 92.1,
    f1Score: 0.897
  },
  {
    id: 3,
    name: 'One-Class SVM',
    type: '机器学习',
    description: '单类支持向量机异常检测模型',
    status: 'inactive',
    accuracy: 82.3,
    recall: 85.6,
    f1Score: 0.839
  },
  {
    id: 4,
    name: '统计阈值检测',
    type: '统计方法',
    description: '基于统计阈值的传统异常检测方法',
    status: 'active',
    accuracy: 76.8,
    recall: 88.9,
    f1Score: 0.824
  }
])

// 计算属性
const filteredAnomalies = computed(() => {
  let filtered = anomalies.value

  // 级别筛选
  if (selectedSeverity.value) {
    filtered = filtered.filter(anomaly => anomaly.severity === selectedSeverity.value)
  }

  // 类型筛选
  if (selectedType.value) {
    filtered = filtered.filter(anomaly => anomaly.type === selectedType.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(anomaly => 
      anomaly.title.toLowerCase().includes(query) ||
      anomaly.description.toLowerCase().includes(query)
    )
  }

  return filtered.sort((a, b) => b.detectedAt - a.detectedAt)
})

/**
 * 获取严重级别对应的变体
 */
const getSeverityVariant = (severity) => {
  const variants = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return variants[severity] || 'default'
}

/**
 * 获取类型对应的变体
 */
const getTypeVariant = (type) => {
  const variants = {
    cpu: 'primary',
    memory: 'success',
    network: 'info',
    disk: 'warning',
    business: 'danger'
  }
  return variants[type] || 'default'
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
 * 运行检测
 */
const runDetection = () => {
  console.log('运行异常检测')
}

/**
 * 配置检测
 */
const configureDetection = () => {
  console.log('配置异常检测')
}

/**
 * 导出报告
 */
const exportReport = () => {
  console.log('导出异常检测报告')
}

/**
 * 查看异常详情
 */
const viewAnomalyDetail = (anomaly) => {
  console.log('查看异常详情:', anomaly)
}

/**
 * 确认异常
 */
const acknowledgeAnomaly = (anomaly) => {
  console.log('确认异常:', anomaly)
}

/**
 * 忽略异常
 */
const ignoreAnomaly = (anomaly) => {
  console.log('忽略异常:', anomaly)
}

/**
 * 管理模型
 */
const manageModels = () => {
  console.log('管理检测模型')
}

/**
 * 切换模型状态
 */
const toggleModel = (model) => {
  model.status = model.status === 'active' ? 'inactive' : 'active'
  console.log('切换模型状态:', model)
}

/**
 * 配置模型
 */
const configureModel = (model) => {
  console.log('配置模型:', model)
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.anomaly-detection {
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

// 检测概览
.detection-overview {
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
  
  &.anomalies {
    border-left-color: $danger-color;
    
    .card-icon {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }
  }
  
  &.accuracy {
    border-left-color: $success-color;
    
    .card-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
  
  &.processing {
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

.card-status {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

// 检测结果
.detection-results {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  margin-bottom: $spacing-xl;
  overflow: hidden;
}

.results-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-lg;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: $text-color;
}

.results-controls {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.time-select {
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

.view-toggle {
  display: flex;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  overflow: hidden;
}

.toggle-btn {
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

// 图表视图
.chart-view {
  padding: $spacing-lg;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: $spacing-lg;
}

.chart-container {
  min-height: 300px;
}

.chart-placeholder {
  height: 250px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-content {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.trend-chart {
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.chart-line {
  height: 150px;
  display: flex;
  align-items: end;
  gap: 2px;
}

.line-segment {
  flex: 1;
  border-radius: 2px 2px 0 0;
  
  &.normal {
    height: 60%;
    background: $success-color;
  }
  
  &.anomaly {
    height: 90%;
    background: $danger-color;
  }
  
  &.warning {
    height: 75%;
    background: $warning-color;
  }
}

.chart-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: $text-color-light;
  margin-top: $spacing-sm;
}

.pie-chart {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: conic-gradient(
    $danger-color 0% 35%,
    $warning-color 35% 60%,
    $info-color 60% 80%,
    $success-color 80% 100%
  );
  margin: 0 auto $spacing-lg;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  
  &.cpu { background: $danger-color; }
  &.memory { background: $warning-color; }
  &.network { background: $info-color; }
  &.disk { background: $success-color; }
}

.legend-text {
  font-size: 12px;
  color: $text-color-secondary;
}

// 列表视图
.list-view {
  padding: $spacing-lg;
}

.list-filters {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-lg;
  flex-wrap: wrap;
}

.filter-group {
  &.search-group {
    flex: 1;
    min-width: 200px;
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
}

.anomaly-items {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.anomaly-item {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  transition: all 0.2s ease;
  border-left: 4px solid;
  
  &:hover {
    box-shadow: $shadow-sm;
  }
  
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

.anomaly-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
  gap: $spacing-md;
}

.anomaly-info {
  flex: 1;
}

.anomaly-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.anomaly-time {
  font-size: 13px;
  color: $text-color-secondary;
}

.anomaly-badges {
  display: flex;
  gap: $spacing-sm;
}

.anomaly-content {
  margin-bottom: $spacing-md;
}

.anomaly-description {
  color: $text-color-secondary;
  line-height: 1.5;
  margin-bottom: $spacing-md;
}

.anomaly-metrics {
  display: flex;
  gap: $spacing-lg;
  flex-wrap: wrap;
}

.metric-item {
  display: flex;
  gap: $spacing-xs;
  font-size: 13px;
}

.metric-label {
  color: $text-color-light;
}

.metric-value {
  color: $text-color;
  font-weight: 500;
}

.anomaly-actions {
  display: flex;
  gap: $spacing-sm;
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
}

// 检测模型
.detection-models {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.models-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.models-grid {
  padding: $spacing-lg;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: $spacing-lg;
}

.model-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: $shadow-sm;
  }
  
  &.active {
    border-color: $success-color;
    background: rgba($success-color, 0.02);
  }
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
}

.model-info {
  flex: 1;
}

.model-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.model-type {
  font-size: 13px;
  color: $text-color-secondary;
}

.model-content {
  margin-bottom: $spacing-md;
}

.model-description {
  color: $text-color-secondary;
  line-height: 1.5;
  margin-bottom: $spacing-md;
  font-size: 14px;
}

.model-metrics {
  display: flex;
  justify-content: space-between;
  gap: $spacing-md;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 12px;
  color: $text-color-light;
  margin-bottom: $spacing-xs;
}

.metric-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.model-actions {
  display: flex;
  gap: $spacing-sm;
}

.model-action-btn {
  flex: 1;
  padding: $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.active {
    background: $success-color;
    border-color: $success-color;
    color: $white;
    
    &:hover {
      background: darken($success-color, 5%);
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .anomaly-detection {
    padding: $spacing-md;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: flex-end;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .results-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .results-controls {
    justify-content: space-between;
  }
  
  .list-filters {
    flex-direction: column;
  }
  
  .filter-group {
    &.search-group {
      min-width: auto;
    }
  }
  
  .anomaly-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .anomaly-badges {
    justify-content: flex-start;
  }
  
  .anomaly-metrics {
    flex-direction: column;
    gap: $spacing-sm;
  }
  
  .models-grid {
    grid-template-columns: 1fr;
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
  
  .card-value {
    font-size: 24px;
  }
  
  .view-toggle {
    width: 100%;
    
    .toggle-btn {
      flex: 1;
      justify-content: center;
    }
  }
}
</style>