<!--
  预测分析页面
  展示AI预测分析的结果和配置
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="predictive-analysis">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">预测分析</h1>
          <p class="page-description">基于AI算法的智能预测分析与趋势预测</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="exportPrediction">
            <i class="icon-download"></i>
            导出预测
          </button>
          <button class="btn btn-outline" @click="configurePrediction">
            <i class="icon-settings"></i>
            预测配置
          </button>
          <button class="btn btn-primary" @click="runPrediction">
            <i class="icon-trending-up"></i>
            运行预测
          </button>
        </div>
      </div>
    </div>

    <!-- 预测概览 -->
    <div class="prediction-overview">
      <div class="overview-grid">
        <div class="overview-card models">
          <div class="card-icon">
            <i class="icon-cpu"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ predictionStats.models }}</div>
            <div class="card-label">预测模型</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +3个
            </div>
          </div>
        </div>
        <div class="overview-card predictions">
          <div class="card-icon">
            <i class="icon-activity"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ predictionStats.predictions }}</div>
            <div class="card-label">预测任务</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +15%
            </div>
          </div>
        </div>
        <div class="overview-card accuracy">
          <div class="card-icon">
            <i class="icon-target"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ predictionStats.accuracy }}%</div>
            <div class="card-label">预测准确率</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +1.8%
            </div>
          </div>
        </div>
        <div class="overview-card processing">
          <div class="card-icon">
            <i class="icon-clock"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ predictionStats.processing }}</div>
            <div class="card-label">处理中</div>
            <div class="card-status">
              <LoadingSpinner size="small" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预测结果 -->
    <div class="prediction-results">
      <div class="results-header">
        <h2 class="section-title">预测结果</h2>
        <div class="results-controls">
          <div class="prediction-range">
            <select v-model="selectedPredictionRange" class="range-select">
              <option value="1h">未来1小时</option>
              <option value="6h">未来6小时</option>
              <option value="24h">未来24小时</option>
              <option value="7d">未来7天</option>
              <option value="30d">未来30天</option>
            </select>
          </div>
          <div class="metric-selector">
            <select v-model="selectedMetric" class="metric-select">
              <option value="cpu">CPU使用率</option>
              <option value="memory">内存使用率</option>
              <option value="disk">磁盘使用率</option>
              <option value="network">网络流量</option>
              <option value="response_time">响应时间</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 预测图表 -->
      <div class="prediction-charts">
        <div class="main-chart">
          <BaseChart
            :title="getChartTitle()"
            :loading="false"
            :error="false"
            :no-data="false"
          >
            <div class="chart-placeholder">
              <div class="prediction-chart">
                <div class="chart-container">
                  <!-- 历史数据 -->
                  <div class="historical-data">
                    <div class="data-line historical">
                      <div 
                        v-for="(point, index) in historicalData" 
                        :key="index"
                        class="data-point"
                        :style="{ height: point + '%' }"
                      ></div>
                    </div>
                  </div>
                  <!-- 预测数据 -->
                  <div class="predicted-data">
                    <div class="data-line predicted">
                      <div 
                        v-for="(point, index) in predictedData" 
                        :key="index"
                        class="data-point"
                        :style="{ height: point + '%' }"
                      ></div>
                    </div>
                    <!-- 置信区间 -->
                    <div class="confidence-interval">
                      <div 
                        v-for="(interval, index) in confidenceIntervals" 
                        :key="index"
                        class="interval-band"
                        :style="{ 
                          height: (interval.upper - interval.lower) + '%',
                          bottom: interval.lower + '%'
                        }"
                      ></div>
                    </div>
                  </div>
                </div>
                <div class="chart-legend">
                  <div class="legend-item">
                    <span class="legend-color historical"></span>
                    <span class="legend-text">历史数据</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color predicted"></span>
                    <span class="legend-text">预测数据</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color confidence"></span>
                    <span class="legend-text">置信区间</span>
                  </div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>

        <!-- 预测指标 -->
        <div class="prediction-metrics">
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-header">
                <h3 class="metric-title">预测趋势</h3>
                <StatusBadge 
                  :status="getTrendStatus()" 
                  :variant="getTrendVariant()"
                />
              </div>
              <div class="metric-content">
                <div class="trend-indicator">
                  <i :class="getTrendIcon()"></i>
                  <span class="trend-text">{{ getTrendText() }}</span>
                </div>
                <div class="trend-value">{{ getTrendValue() }}</div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-header">
                <h3 class="metric-title">预测置信度</h3>
              </div>
              <div class="metric-content">
                <div class="confidence-bar">
                  <div 
                    class="confidence-fill"
                    :style="{ width: currentPrediction.confidence + '%' }"
                  ></div>
                </div>
                <div class="confidence-value">{{ currentPrediction.confidence }}%</div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-header">
                <h3 class="metric-title">风险评估</h3>
                <StatusBadge 
                  :status="currentPrediction.riskLevel" 
                  :variant="getRiskVariant(currentPrediction.riskLevel)"
                />
              </div>
              <div class="metric-content">
                <div class="risk-description">{{ getRiskDescription() }}</div>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-header">
                <h3 class="metric-title">建议操作</h3>
              </div>
              <div class="metric-content">
                <div class="recommendations">
                  <div 
                    v-for="(recommendation, index) in currentPrediction.recommendations" 
                    :key="index"
                    class="recommendation-item"
                  >
                    <i class="icon-arrow-right"></i>
                    <span>{{ recommendation }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 预测任务 -->
    <div class="prediction-tasks">
      <div class="tasks-header">
        <h2 class="section-title">预测任务</h2>
        <div class="tasks-controls">
          <div class="filter-group">
            <select v-model="selectedTaskStatus" class="filter-select">
              <option value="">全部状态</option>
              <option value="running">运行中</option>
              <option value="completed">已完成</option>
              <option value="failed">失败</option>
              <option value="scheduled">已调度</option>
            </select>
          </div>
          <button class="btn btn-primary btn-sm" @click="createTask">
            <i class="icon-plus"></i>
            新建任务
          </button>
        </div>
      </div>

      <div class="tasks-list">
        <div 
          v-for="task in filteredTasks" 
          :key="task.id"
          class="task-item"
          :class="task.status"
        >
          <div class="task-header">
            <div class="task-info">
              <div class="task-name">{{ task.name }}</div>
              <div class="task-description">{{ task.description }}</div>
            </div>
            <div class="task-status">
              <StatusBadge 
                :status="task.status" 
                :variant="getTaskStatusVariant(task.status)"
              />
            </div>
          </div>
          
          <div class="task-content">
            <div class="task-details">
              <div class="detail-item">
                <span class="detail-label">预测指标:</span>
                <span class="detail-value">{{ task.metric }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">预测范围:</span>
                <span class="detail-value">{{ task.range }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">模型类型:</span>
                <span class="detail-value">{{ task.model }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">创建时间:</span>
                <span class="detail-value">{{ formatTime(task.createdAt) }}</span>
              </div>
            </div>
            
            <div class="task-progress" v-if="task.status === 'running'">
              <div class="progress-bar">
                <div 
                  class="progress-fill"
                  :style="{ width: task.progress + '%' }"
                ></div>
              </div>
              <div class="progress-text">{{ task.progress }}%</div>
            </div>
            
            <div class="task-results" v-if="task.status === 'completed'">
              <div class="result-item">
                <span class="result-label">准确率:</span>
                <span class="result-value">{{ task.accuracy }}%</span>
              </div>
              <div class="result-item">
                <span class="result-label">预测点数:</span>
                <span class="result-value">{{ task.dataPoints }}</span>
              </div>
            </div>
          </div>
          
          <div class="task-actions">
            <button 
              class="action-btn"
              @click="viewTaskDetail(task)"
            >
              <i class="icon-eye"></i>
              查看详情
            </button>
            <button 
              v-if="task.status === 'completed'"
              class="action-btn"
              @click="downloadResults(task)"
            >
              <i class="icon-download"></i>
              下载结果
            </button>
            <button 
              v-if="task.status === 'running'"
              class="action-btn danger"
              @click="stopTask(task)"
            >
              <i class="icon-stop"></i>
              停止任务
            </button>
            <button 
              v-if="task.status === 'failed'"
              class="action-btn"
              @click="retryTask(task)"
            >
              <i class="icon-refresh"></i>
              重试
            </button>
            <button 
              class="action-btn danger"
              @click="deleteTask(task)"
            >
              <i class="icon-trash"></i>
              删除
            </button>
          </div>
        </div>

        <!-- 空状态 -->
        <EmptyState
          v-if="filteredTasks.length === 0"
          icon="icon-trending-up"
          title="暂无预测任务"
          description="创建您的第一个预测任务开始分析"
          :actions="[
            { text: '创建任务', action: createTask }
          ]"
        />
      </div>
    </div>

    <!-- 预测模型 -->
    <div class="prediction-models">
      <div class="models-header">
        <h2 class="section-title">预测模型</h2>
        <button class="btn btn-outline btn-sm" @click="manageModels">
          <i class="icon-settings"></i>
          管理模型
        </button>
      </div>
      
      <div class="models-grid">
        <div 
          v-for="model in predictionModels" 
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
                <span class="metric-label">RMSE</span>
                <span class="metric-value">{{ model.rmse }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">MAE</span>
                <span class="metric-value">{{ model.mae }}</span>
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
            <button class="model-action-btn" @click="trainModel(model)">
              训练
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 预测分析页面组件
 * 展示AI预测分析的结果和配置
 */
import { ref, computed, onMounted } from 'vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

// 响应式数据
const selectedPredictionRange = ref('24h')
const selectedMetric = ref('cpu')
const selectedTaskStatus = ref('')

// 预测统计数据
const predictionStats = ref({
  models: 8,
  predictions: 45,
  accuracy: 92.7,
  processing: 3
})

// 历史数据和预测数据
const historicalData = ref([45, 52, 48, 61, 55, 67, 59, 72, 68, 75])
const predictedData = ref([78, 82, 85, 79, 88, 91, 87, 94, 89, 96])
const confidenceIntervals = ref([
  { lower: 70, upper: 86 },
  { lower: 74, upper: 90 },
  { lower: 77, upper: 93 },
  { lower: 71, upper: 87 },
  { lower: 80, upper: 96 },
  { lower: 83, upper: 99 },
  { lower: 79, upper: 95 },
  { lower: 86, upper: 102 },
  { lower: 81, upper: 97 },
  { lower: 88, upper: 104 }
])

// 当前预测信息
const currentPrediction = ref({
  confidence: 92.7,
  riskLevel: 'medium',
  trend: 'increasing',
  trendValue: '+15.3%',
  recommendations: [
    '建议在未来2小时内增加服务器资源',
    '监控关键服务的响应时间',
    '准备扩容方案以应对流量峰值'
  ]
})

// 预测任务
const predictionTasks = ref([
  {
    id: 1,
    name: 'CPU使用率预测',
    description: '预测未来24小时的CPU使用率趋势',
    metric: 'CPU使用率',
    range: '未来24小时',
    model: 'LSTM神经网络',
    status: 'running',
    progress: 75,
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000)
  },
  {
    id: 2,
    name: '内存使用预测',
    description: '基于历史数据预测内存使用趋势',
    metric: '内存使用率',
    range: '未来7天',
    model: 'ARIMA模型',
    status: 'completed',
    accuracy: 94.2,
    dataPoints: 168,
    createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000)
  },
  {
    id: 3,
    name: '网络流量预测',
    description: '预测网络流量峰值和低谷时段',
    metric: '网络流量',
    range: '未来30天',
    model: 'Prophet模型',
    status: 'failed',
    error: '数据源连接失败',
    createdAt: new Date(Date.now() - 12 * 60 * 60 * 1000)
  },
  {
    id: 4,
    name: '响应时间预测',
    description: '预测应用响应时间变化趋势',
    metric: '响应时间',
    range: '未来6小时',
    model: 'Random Forest',
    status: 'scheduled',
    scheduledAt: new Date(Date.now() + 30 * 60 * 1000),
    createdAt: new Date(Date.now() - 1 * 60 * 60 * 1000)
  }
])

// 预测模型
const predictionModels = ref([
  {
    id: 1,
    name: 'LSTM时序预测',
    type: '深度学习',
    description: '基于长短期记忆网络的时间序列预测模型',
    status: 'active',
    accuracy: 94.2,
    rmse: 0.087,
    mae: 0.065
  },
  {
    id: 2,
    name: 'ARIMA模型',
    type: '统计模型',
    description: '自回归积分滑动平均模型，适用于平稳时间序列',
    status: 'active',
    accuracy: 89.7,
    rmse: 0.124,
    mae: 0.098
  },
  {
    id: 3,
    name: 'Prophet模型',
    type: '时间序列',
    description: 'Facebook开源的时间序列预测模型',
    status: 'active',
    accuracy: 91.3,
    rmse: 0.105,
    mae: 0.082
  },
  {
    id: 4,
    name: 'Random Forest',
    type: '机器学习',
    description: '随机森林回归模型，适用于非线性预测',
    status: 'inactive',
    accuracy: 87.5,
    rmse: 0.142,
    mae: 0.115
  },
  {
    id: 5,
    name: 'XGBoost',
    type: '机器学习',
    description: '梯度提升决策树，高性能预测模型',
    status: 'active',
    accuracy: 92.8,
    rmse: 0.093,
    mae: 0.071
  },
  {
    id: 6,
    name: 'Linear Regression',
    type: '统计模型',
    description: '线性回归模型，适用于线性趋势预测',
    status: 'inactive',
    accuracy: 78.4,
    rmse: 0.198,
    mae: 0.156
  }
])

// 计算属性
const filteredTasks = computed(() => {
  if (!selectedTaskStatus.value) {
    return predictionTasks.value
  }
  return predictionTasks.value.filter(task => task.status === selectedTaskStatus.value)
})

/**
 * 获取图表标题
 */
const getChartTitle = () => {
  const metricNames = {
    cpu: 'CPU使用率',
    memory: '内存使用率',
    disk: '磁盘使用率',
    network: '网络流量',
    response_time: '响应时间'
  }
  const rangeNames = {
    '1h': '未来1小时',
    '6h': '未来6小时',
    '24h': '未来24小时',
    '7d': '未来7天',
    '30d': '未来30天'
  }
  return `${metricNames[selectedMetric.value]} - ${rangeNames[selectedPredictionRange.value]}预测`
}

/**
 * 获取趋势状态
 */
const getTrendStatus = () => {
  return currentPrediction.value.trend
}

/**
 * 获取趋势变体
 */
const getTrendVariant = () => {
  const variants = {
    increasing: 'warning',
    decreasing: 'success',
    stable: 'info'
  }
  return variants[currentPrediction.value.trend] || 'default'
}

/**
 * 获取趋势图标
 */
const getTrendIcon = () => {
  const icons = {
    increasing: 'icon-trending-up',
    decreasing: 'icon-trending-down',
    stable: 'icon-minus'
  }
  return icons[currentPrediction.value.trend] || 'icon-minus'
}

/**
 * 获取趋势文本
 */
const getTrendText = () => {
  const texts = {
    increasing: '上升趋势',
    decreasing: '下降趋势',
    stable: '稳定趋势'
  }
  return texts[currentPrediction.value.trend] || '未知趋势'
}

/**
 * 获取趋势值
 */
const getTrendValue = () => {
  return currentPrediction.value.trendValue
}

/**
 * 获取风险变体
 */
const getRiskVariant = (riskLevel) => {
  const variants = {
    high: 'danger',
    medium: 'warning',
    low: 'success'
  }
  return variants[riskLevel] || 'default'
}

/**
 * 获取风险描述
 */
const getRiskDescription = () => {
  const descriptions = {
    high: '高风险：需要立即采取行动',
    medium: '中等风险：建议密切关注',
    low: '低风险：保持正常监控'
  }
  return descriptions[currentPrediction.value.riskLevel] || '未知风险'
}

/**
 * 获取任务状态变体
 */
const getTaskStatusVariant = (status) => {
  const variants = {
    running: 'info',
    completed: 'success',
    failed: 'danger',
    scheduled: 'warning'
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
 * 运行预测
 */
const runPrediction = () => {
  console.log('运行预测分析')
}

/**
 * 配置预测
 */
const configurePrediction = () => {
  console.log('配置预测参数')
}

/**
 * 导出预测
 */
const exportPrediction = () => {
  console.log('导出预测结果')
}

/**
 * 创建任务
 */
const createTask = () => {
  console.log('创建预测任务')
}

/**
 * 查看任务详情
 */
const viewTaskDetail = (task) => {
  console.log('查看任务详情:', task)
}

/**
 * 下载结果
 */
const downloadResults = (task) => {
  console.log('下载任务结果:', task)
}

/**
 * 停止任务
 */
const stopTask = (task) => {
  console.log('停止任务:', task)
}

/**
 * 重试任务
 */
const retryTask = (task) => {
  console.log('重试任务:', task)
}

/**
 * 删除任务
 */
const deleteTask = (task) => {
  console.log('删除任务:', task)
}

/**
 * 管理模型
 */
const manageModels = () => {
  console.log('管理预测模型')
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

/**
 * 训练模型
 */
const trainModel = (model) => {
  console.log('训练模型:', model)
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.predictive-analysis {
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

// 预测概览
.prediction-overview {
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
  
  &.models {
    border-left-color: $primary-color;
    
    .card-icon {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }
  
  &.predictions {
    border-left-color: $info-color;
    
    .card-icon {
      background: rgba($info-color, 0.1);
      color: $info-color;
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
}

.card-status {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

// 预测结果
.prediction-results {
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

.range-select,
.metric-select {
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

// 预测图表
.prediction-charts {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: $spacing-lg;
  padding: $spacing-lg;
}

.main-chart {
  min-height: 400px;
}

.chart-placeholder {
  height: 350px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.prediction-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-container {
  flex: 1;
  position: relative;
  display: flex;
  margin-bottom: $spacing-md;
}

.historical-data,
.predicted-data {
  flex: 1;
  position: relative;
}

.data-line {
  height: 250px;
  display: flex;
  align-items: end;
  gap: 2px;
  
  &.historical .data-point {
    background: $primary-color;
  }
  
  &.predicted .data-point {
    background: $warning-color;
  }
}

.data-point {
  flex: 1;
  border-radius: 2px 2px 0 0;
  min-height: 10px;
}

.confidence-interval {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 250px;
  display: flex;
  align-items: end;
  gap: 2px;
}

.interval-band {
  flex: 1;
  background: rgba($info-color, 0.2);
  border-radius: 2px;
  position: relative;
}

.chart-legend {
  display: flex;
  justify-content: center;
  gap: $spacing-lg;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  
  &.historical { background: $primary-color; }
  &.predicted { background: $warning-color; }
  &.confidence { background: rgba($info-color, 0.2); }
}

.legend-text {
  font-size: 12px;
  color: $text-color-secondary;
}

// 预测指标
.prediction-metrics {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.metrics-grid {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.metric-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-md;
  padding: $spacing-md;
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
}

.metric-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: $text-color;
}

.metric-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  
  i {
    font-size: 16px;
    color: $warning-color;
  }
}

.trend-text {
  font-size: 13px;
  color: $text-color-secondary;
}

.trend-value {
  font-size: 18px;
  font-weight: 600;
  color: $text-color;
}

.confidence-bar {
  height: 8px;
  background: $background-color-light;
  border-radius: 4px;
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: $success-color;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.confidence-value {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  text-align: center;
}

.risk-description {
  font-size: 13px;
  color: $text-color-secondary;
  line-height: 1.4;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: $spacing-xs;
  font-size: 12px;
  color: $text-color-secondary;
  line-height: 1.4;
  
  i {
    margin-top: 2px;
    color: $primary-color;
    font-size: 10px;
  }
}

// 预测任务
.prediction-tasks {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  margin-bottom: $spacing-xl;
  overflow: hidden;
}

.tasks-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tasks-controls {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.filter-select {
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

.tasks-list {
  padding: $spacing-lg;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.task-item {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: $shadow-sm;
  }
  
  &.running {
    border-left: 4px solid $info-color;
  }
  
  &.completed {
    border-left: 4px solid $success-color;
  }
  
  &.failed {
    border-left: 4px solid $danger-color;
  }
  
  &.scheduled {
    border-left: 4px solid $warning-color;
  }
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
  gap: $spacing-md;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.task-description {
  font-size: 14px;
  color: $text-color-secondary;
  line-height: 1.4;
}

.task-content {
  margin-bottom: $spacing-md;
}

.task-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-sm;
  margin-bottom: $spacing-md;
}

.detail-item {
  display: flex;
  gap: $spacing-xs;
  font-size: 13px;
}

.detail-label {
  color: $text-color-light;
  min-width: 80px;
}

.detail-value {
  color: $text-color;
  font-weight: 500;
}

.task-progress {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: $background-color-light;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: $info-color;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 13px;
  color: $text-color-secondary;
  font-weight: 500;
  min-width: 40px;
}

.task-results {
  display: flex;
  gap: $spacing-lg;
}

.result-item {
  display: flex;
  gap: $spacing-xs;
  font-size: 13px;
}

.result-label {
  color: $text-color-light;
}

.result-value {
  color: $text-color;
  font-weight: 500;
}

.task-actions {
  display: flex;
  gap: $spacing-sm;
  flex-wrap: wrap;
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
  
  &.danger {
    &:hover {
      border-color: $danger-color;
      color: $danger-color;
    }
  }
}

// 预测模型
.prediction-models {
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
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
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
  
  .prediction-charts {
    grid-template-columns: 1fr;
  }
  
  .models-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

@media (max-width: 768px) {
  .predictive-analysis {
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
  
  .task-header {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
  }
  
  .task-details {
    grid-template-columns: 1fr;
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
  
  .results-controls {
    flex-direction: column;
    gap: $spacing-sm;
    
    .range-select,
    .metric-select {
      width: 100%;
    }
  }
  
  .tasks-controls {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-sm;
    
    .filter-select {
      width: 100%;
    }
  }
}
</style>