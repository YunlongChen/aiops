<!--
  模型库组件
  提供AI模型的查看、管理和监控功能
  包含AI引擎状态概览、模型列表、模型性能监控等功能
-->
<template>
  <div class="model-library">
    <!-- AI引擎状态概览 -->
    <div class="ai-section">
      <div class="section-header">
        <h3>AI引擎状态</h3>
      </div>
      
      <div class="status-grid">
        <div class="status-card">
          <div class="status-icon">
            <i class="fas fa-brain"></i>
          </div>
          <div class="status-info">
            <h4>活跃模型</h4>
            <span class="status-value">{{ engineStatus.activeModels }}</span>
            <span class="status-change" :class="{ positive: engineStatus.activeModelsChange > 0, negative: engineStatus.activeModelsChange < 0 }">
              {{ engineStatus.activeModelsChange > 0 ? '+' : '' }}{{ engineStatus.activeModelsChange }}
            </span>
          </div>
        </div>
        
        <div class="status-card">
          <div class="status-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="status-info">
            <h4>预测准确率</h4>
            <span class="status-value">{{ engineStatus.accuracy }}%</span>
            <span class="status-change" :class="{ positive: engineStatus.accuracyChange > 0, negative: engineStatus.accuracyChange < 0 }">
              {{ engineStatus.accuracyChange > 0 ? '+' : '' }}{{ engineStatus.accuracyChange }}%
            </span>
          </div>
        </div>
        
        <div class="status-card">
          <div class="status-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="status-info">
            <h4>平均响应时间</h4>
            <span class="status-value">{{ engineStatus.responseTime }}ms</span>
            <span class="status-change" :class="{ positive: engineStatus.responseTimeChange < 0, negative: engineStatus.responseTimeChange > 0 }">
              {{ engineStatus.responseTimeChange > 0 ? '+' : '' }}{{ engineStatus.responseTimeChange }}ms
            </span>
          </div>
        </div>
        
        <div class="status-card">
          <div class="status-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="status-info">
            <h4>异常检测率</h4>
            <span class="status-value">{{ engineStatus.detectionRate }}%</span>
            <span class="status-change" :class="{ positive: engineStatus.detectionRateChange > 0, negative: engineStatus.detectionRateChange < 0 }">
              {{ engineStatus.detectionRateChange > 0 ? '+' : '' }}{{ engineStatus.detectionRateChange }}%
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型列表 -->
    <div class="ai-section">
      <div class="section-header">
        <h3>模型列表</h3>
        <div class="section-actions">
          <div class="filter-group">
            <select class="filter-select" v-model="filters.type">
              <option value="">所有类型</option>
              <option value="anomaly">异常检测</option>
              <option value="prediction">性能预测</option>
              <option value="classification">分类模型</option>
              <option value="regression">回归模型</option>
            </select>
            <select class="filter-select" v-model="filters.status">
              <option value="">所有状态</option>
              <option value="active">运行中</option>
              <option value="training">训练中</option>
              <option value="stopped">已停止</option>
            </select>
          </div>
          <input 
            type="text" 
            placeholder="搜索模型..." 
            class="search-input" 
            v-model="searchQuery"
          >
        </div>
      </div>
      
      <div class="models-grid">
        <div 
          v-for="model in filteredModels" 
          :key="model.id"
          class="model-card" 
          :class="model.status"
        >
          <div class="model-header">
            <div class="model-info">
              <h4>{{ model.name }}</h4>
              <span class="model-type">{{ getModelTypeText(model.type) }}</span>
            </div>
            <div class="model-status">
              <span class="status-indicator" :class="model.status"></span>
              <span class="status-text">{{ getStatusText(model.status) }}</span>
            </div>
          </div>
          
          <!-- 训练进度（仅训练中的模型显示） -->
          <div v-if="model.status === 'training'" class="training-progress">
            <div class="progress-info">
              <span>训练进度</span>
              <span>{{ model.progress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: model.progress + '%' }"></div>
            </div>
            <div class="progress-details">
              <span>Epoch {{ model.currentEpoch }}/{{ model.totalEpochs }}</span>
              <span>预计剩余: {{ model.remainingTime }}</span>
            </div>
          </div>
          
          <!-- 模型指标（非训练中的模型显示） -->
          <div v-else class="model-metrics">
            <div class="metric-row">
              <span class="metric-label">准确率</span>
              <span class="metric-value">{{ model.accuracy }}%</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">训练时间</span>
              <span class="metric-value">{{ model.trainingTime }}</span>
            </div>
            <div class="metric-row">
              <span class="metric-label">最后更新</span>
              <span class="metric-value">{{ model.lastUpdate }}</span>
            </div>
          </div>
          
          <div class="model-actions">
            <button class="btn-icon" @click="viewModel(model)" title="查看详情">
              <i class="fas fa-eye"></i>
            </button>
            <button 
              v-if="model.status === 'training'" 
              class="btn-icon" 
              @click="viewTrainingLog(model)" 
              title="查看训练日志"
            >
              <i class="fas fa-file-alt"></i>
            </button>
            <button 
              v-if="model.status !== 'training'" 
              class="btn-icon" 
              @click="editModel(model)" 
              title="编辑"
            >
              <i class="fas fa-edit"></i>
            </button>
            <button 
              v-if="model.status === 'active'" 
              class="btn-icon" 
              @click="retrainModel(model)" 
              title="重新训练"
            >
              <i class="fas fa-redo"></i>
            </button>
            <button 
              v-if="model.status === 'training'" 
              class="btn-icon" 
              @click="pauseTraining(model)" 
              title="暂停训练"
            >
              <i class="fas fa-pause"></i>
            </button>
            <button 
              v-if="model.status === 'stopped'" 
              class="btn-icon" 
              @click="startModel(model)" 
              title="启动"
            >
              <i class="fas fa-play"></i>
            </button>
            <button 
              v-if="['active', 'training'].includes(model.status)" 
              class="btn-icon" 
              @click="stopModel(model)" 
              title="停止"
            >
              <i class="fas fa-stop"></i>
            </button>
            <button 
              v-if="model.status === 'stopped'" 
              class="btn-icon" 
              @click="deleteModel(model)" 
              title="删除"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型性能图表 -->
    <div class="ai-section">
      <div class="section-header">
        <h3>模型性能监控</h3>
      </div>
      
      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <h4>模型准确率趋势</h4>
            <span class="current-value">{{ engineStatus.accuracy }}%</span>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-chart-line"></i>
              <span>准确率趋势图</span>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">
            <h4>预测响应时间</h4>
            <span class="current-value">{{ engineStatus.responseTime }}ms</span>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-clock"></i>
              <span>响应时间图</span>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">
            <h4>模型使用频率</h4>
            <span class="current-value">1.2K/h</span>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-chart-bar"></i>
              <span>使用频率图</span>
            </div>
          </div>
        </div>
        
        <div class="chart-card">
          <div class="chart-header">
            <h4>异常检测统计</h4>
            <span class="current-value">23</span>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-exclamation-triangle"></i>
              <span>异常统计图</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ModelLibrary',
  setup() {
    // 响应式数据
    const searchQuery = ref('')
    const filters = ref({
      type: '',
      status: ''
    })

    // AI引擎状态
    const engineStatus = ref({
      activeModels: 12,
      activeModelsChange: 2,
      accuracy: 94.2,
      accuracyChange: 1.5,
      responseTime: 125,
      responseTimeChange: 15,
      detectionRate: 98.7,
      detectionRateChange: 0.3
    })

    // 模型列表
    const models = ref([
      {
        id: 1,
        name: 'CPU异常检测模型',
        type: 'anomaly',
        status: 'active',
        accuracy: 96.5,
        trainingTime: '2小时',
        lastUpdate: '2小时前'
      },
      {
        id: 2,
        name: '内存使用预测模型',
        type: 'prediction',
        status: 'training',
        progress: 67,
        currentEpoch: 67,
        totalEpochs: 100,
        remainingTime: '45分钟'
      },
      {
        id: 3,
        name: '网络流量分类模型',
        type: 'classification',
        status: 'active',
        accuracy: 92.8,
        trainingTime: '4小时',
        lastUpdate: '1天前'
      },
      {
        id: 4,
        name: '磁盘容量预测模型',
        type: 'regression',
        status: 'stopped',
        accuracy: 89.2,
        trainingTime: '3小时',
        lastUpdate: '3天前'
      }
    ])

    /**
     * 过滤后的模型列表
     */
    const filteredModels = computed(() => {
      return models.value.filter(model => {
        const matchesSearch = model.name.toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesType = !filters.value.type || model.type === filters.value.type
        const matchesStatus = !filters.value.status || model.status === filters.value.status
        
        return matchesSearch && matchesType && matchesStatus
      })
    })

    /**
     * 获取模型类型文本
     */
    const getModelTypeText = (type) => {
      const typeMap = {
        'anomaly': '异常检测',
        'prediction': '性能预测',
        'classification': '分类模型',
        'regression': '回归模型'
      }
      return typeMap[type] || type
    }

    /**
     * 获取状态文本
     */
    const getStatusText = (status) => {
      const statusMap = {
        'active': '运行中',
        'training': '训练中',
        'stopped': '已停止'
      }
      return statusMap[status] || status
    }

    /**
     * 查看模型详情
     */
    const viewModel = (model) => {
      console.log('查看模型详情:', model.name)
      // TODO: 实现查看模型详情逻辑
    }

    /**
     * 查看训练日志
     */
    const viewTrainingLog = (model) => {
      console.log('查看训练日志:', model.name)
      // TODO: 实现查看训练日志逻辑
    }

    /**
     * 编辑模型
     */
    const editModel = (model) => {
      console.log('编辑模型:', model.name)
      // TODO: 实现编辑模型逻辑
    }

    /**
     * 重新训练模型
     */
    const retrainModel = (model) => {
      console.log('重新训练模型:', model.name)
      // TODO: 实现重新训练模型逻辑
    }

    /**
     * 暂停训练
     */
    const pauseTraining = (model) => {
      console.log('暂停训练:', model.name)
      // TODO: 实现暂停训练逻辑
    }

    /**
     * 启动模型
     */
    const startModel = (model) => {
      console.log('启动模型:', model.name)
      model.status = 'active'
    }

    /**
     * 停止模型
     */
    const stopModel = (model) => {
      console.log('停止模型:', model.name)
      model.status = 'stopped'
    }

    /**
     * 删除模型
     */
    const deleteModel = (model) => {
      if (confirm(`确定要删除模型 "${model.name}" 吗？`)) {
        const index = models.value.findIndex(m => m.id === model.id)
        if (index > -1) {
          models.value.splice(index, 1)
        }
      }
    }

    // 生命周期钩子
    onMounted(() => {
      console.log('模型库组件已加载')
    })

    return {
      searchQuery,
      filters,
      engineStatus,
      models,
      filteredModels,
      getModelTypeText,
      getStatusText,
      viewModel,
      viewTrainingLog,
      editModel,
      retrainModel,
      pauseTraining,
      startModel,
      stopModel,
      deleteModel
    }
  }
}
</script>

<style scoped>
.model-library {
  padding: 20px;
  background: #f9fafb;
  min-height: 100%;
}

.ai-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.section-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-group {
  display: flex;
  gap: 8px;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  width: 200px;
}

/* 状态网格 */
.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.status-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  font-size: 20px;
}

.status-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.status-value {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin-right: 8px;
}

.status-change {
  font-size: 14px;
  font-weight: 500;
}

.status-change.positive {
  color: #10b981;
}

.status-change.negative {
  color: #ef4444;
}

/* 模型网格 */
.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.model-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;
}

.model-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.model-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.model-type {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
}

.model-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.active {
  background: #10b981;
}

.status-indicator.training {
  background: #f59e0b;
}

.status-indicator.stopped {
  background: #6b7280;
}

.status-text {
  font-size: 12px;
  color: #6b7280;
}

/* 训练进度 */
.training-progress {
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
  color: #374151;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
}

/* 模型指标 */
.model-metrics {
  margin-bottom: 16px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.metric-label {
  color: #6b7280;
}

.metric-value {
  color: #1f2937;
  font-weight: 500;
}

/* 模型操作 */
.model-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #e5e7eb;
  color: #374151;
}

/* 图表网格 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.current-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.chart-content {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #9ca3af;
}

.chart-placeholder i {
  font-size: 32px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .model-library {
    padding: 16px;
  }

  .ai-section {
    padding: 16px;
  }

  .section-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .filter-group {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }

  .models-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>