<!--
  模型训练组件
  提供AI模型训练任务的管理和监控功能
  包含训练任务统计、训练任务列表、训练配置等功能
-->
<template>
  <div class="model-training">
    <!-- 训练任务统计 -->
    <div class="ai-section">
      <div class="section-header">
        <h3>训练任务管理</h3>
        <button class="btn btn-primary" @click="newTrainingTask">
          <i class="fas fa-plus"></i>
          新建训练任务
        </button>
      </div>
      
      <div class="training-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-play"></i>
          </div>
          <div class="stat-info">
            <h4>运行中</h4>
            <span class="stat-value">{{ trainingStats.running }}</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-check"></i>
          </div>
          <div class="stat-info">
            <h4>已完成</h4>
            <span class="stat-value">{{ trainingStats.completed }}</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-pause"></i>
          </div>
          <div class="stat-info">
            <h4>已暂停</h4>
            <span class="stat-value">{{ trainingStats.paused }}</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-times"></i>
          </div>
          <div class="stat-info">
            <h4>失败</h4>
            <span class="stat-value">{{ trainingStats.failed }}</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-info">
            <h4>队列中</h4>
            <span class="stat-value">{{ trainingStats.queued }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 训练任务列表 -->
    <div class="ai-section">
      <div class="section-header">
        <h3>训练任务列表</h3>
        <div class="section-actions">
          <div class="filter-group">
            <select class="filter-select" v-model="filters.status">
              <option value="">所有状态</option>
              <option value="running">运行中</option>
              <option value="completed">已完成</option>
              <option value="paused">已暂停</option>
              <option value="failed">失败</option>
              <option value="queued">队列中</option>
            </select>
            <select class="filter-select" v-model="filters.type">
              <option value="">所有类型</option>
              <option value="anomaly">异常检测</option>
              <option value="prediction">性能预测</option>
              <option value="classification">分类模型</option>
              <option value="regression">回归模型</option>
            </select>
          </div>
          <input 
            type="text" 
            placeholder="搜索训练任务..." 
            class="search-input" 
            v-model="searchQuery"
          >
        </div>
      </div>
      
      <div class="training-list">
        <div 
          v-for="task in filteredTasks" 
          :key="task.id"
          class="training-card" 
          :class="task.status"
        >
          <div class="training-header">
            <div class="training-info">
              <h4>{{ task.name }}</h4>
              <div class="training-meta">
                <span class="training-type">{{ getModelTypeText(task.type) }}</span>
                <span class="training-time">{{ task.createdAt }}</span>
              </div>
            </div>
            <div class="training-status">
              <span class="status-indicator" :class="task.status"></span>
              <span class="status-text">{{ getStatusText(task.status) }}</span>
            </div>
          </div>
          
          <!-- 运行中的任务显示进度 -->
          <div v-if="task.status === 'running'" class="training-progress">
            <div class="progress-info">
              <span>训练进度</span>
              <span>{{ task.progress }}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
            </div>
            <div class="progress-details">
              <div class="progress-item">
                <span class="label">Epoch:</span>
                <span class="value">{{ task.currentEpoch }}/{{ task.totalEpochs }}</span>
              </div>
              <div class="progress-item">
                <span class="label">损失:</span>
                <span class="value">{{ task.currentLoss }}</span>
              </div>
              <div class="progress-item">
                <span class="label">准确率:</span>
                <span class="value">{{ task.currentAccuracy }}%</span>
              </div>
              <div class="progress-item">
                <span class="label">剩余时间:</span>
                <span class="value">{{ task.remainingTime }}</span>
              </div>
            </div>
          </div>
          
          <!-- 其他状态的任务显示基本信息 -->
          <div v-else class="training-details">
            <div class="detail-row">
              <span class="detail-label">数据集:</span>
              <span class="detail-value">{{ task.dataset }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">算法:</span>
              <span class="detail-value">{{ task.algorithm }}</span>
            </div>
            <div v-if="task.status === 'completed'" class="detail-row">
              <span class="detail-label">最终准确率:</span>
              <span class="detail-value">{{ task.finalAccuracy }}%</span>
            </div>
            <div v-if="task.status === 'completed'" class="detail-row">
              <span class="detail-label">训练时长:</span>
              <span class="detail-value">{{ task.duration }}</span>
            </div>
            <div v-if="task.status === 'failed'" class="detail-row">
              <span class="detail-label">失败原因:</span>
              <span class="detail-value error">{{ task.errorMessage }}</span>
            </div>
          </div>
          
          <div class="training-actions">
            <button class="btn-icon" @click="viewTask(task)" title="查看详情">
              <i class="fas fa-eye"></i>
            </button>
            <button 
              v-if="task.status === 'running'" 
              class="btn-icon" 
              @click="viewLogs(task)" 
              title="查看日志"
            >
              <i class="fas fa-file-alt"></i>
            </button>
            <button 
              v-if="task.status === 'running'" 
              class="btn-icon" 
              @click="pauseTask(task)" 
              title="暂停"
            >
              <i class="fas fa-pause"></i>
            </button>
            <button 
              v-if="task.status === 'paused'" 
              class="btn-icon" 
              @click="resumeTask(task)" 
              title="继续"
            >
              <i class="fas fa-play"></i>
            </button>
            <button 
              v-if="['running', 'paused', 'queued'].includes(task.status)" 
              class="btn-icon" 
              @click="stopTask(task)" 
              title="停止"
            >
              <i class="fas fa-stop"></i>
            </button>
            <button 
              v-if="['completed', 'failed'].includes(task.status)" 
              class="btn-icon" 
              @click="retryTask(task)" 
              title="重新训练"
            >
              <i class="fas fa-redo"></i>
            </button>
            <button 
              v-if="['completed', 'failed'].includes(task.status)" 
              class="btn-icon" 
              @click="deleteTask(task)" 
              title="删除"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 训练资源监控 -->
    <div class="ai-section">
      <div class="section-header">
        <h3>训练资源监控</h3>
      </div>
      
      <div class="resource-grid">
        <div class="resource-card">
          <div class="resource-header">
            <h4>GPU使用率</h4>
            <span class="resource-value">{{ resourceUsage.gpu }}%</span>
          </div>
          <div class="resource-bar">
            <div class="resource-fill" :style="{ width: resourceUsage.gpu + '%' }"></div>
          </div>
        </div>
        
        <div class="resource-card">
          <div class="resource-header">
            <h4>内存使用</h4>
            <span class="resource-value">{{ resourceUsage.memory }}%</span>
          </div>
          <div class="resource-bar">
            <div class="resource-fill" :style="{ width: resourceUsage.memory + '%' }"></div>
          </div>
        </div>
        
        <div class="resource-card">
          <div class="resource-header">
            <h4>CPU使用率</h4>
            <span class="resource-value">{{ resourceUsage.cpu }}%</span>
          </div>
          <div class="resource-bar">
            <div class="resource-fill" :style="{ width: resourceUsage.cpu + '%' }"></div>
          </div>
        </div>
        
        <div class="resource-card">
          <div class="resource-header">
            <h4>磁盘I/O</h4>
            <span class="resource-value">{{ resourceUsage.disk }}%</span>
          </div>
          <div class="resource-bar">
            <div class="resource-fill" :style="{ width: resourceUsage.disk + '%' }"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'ModelTraining',
  setup() {
    // 响应式数据
    const searchQuery = ref('')
    const filters = ref({
      status: '',
      type: ''
    })

    // 训练统计
    const trainingStats = ref({
      running: 3,
      completed: 15,
      paused: 1,
      failed: 2,
      queued: 4
    })

    // 资源使用情况
    const resourceUsage = ref({
      gpu: 75,
      memory: 68,
      cpu: 45,
      disk: 32
    })

    // 训练任务列表
    const trainingTasks = ref([
      {
        id: 1,
        name: 'CPU异常检测模型训练',
        type: 'anomaly',
        status: 'running',
        progress: 67,
        currentEpoch: 67,
        totalEpochs: 100,
        currentLoss: 0.0234,
        currentAccuracy: 94.2,
        remainingTime: '45分钟',
        dataset: 'CPU监控数据集',
        algorithm: 'LSTM',
        createdAt: '2小时前'
      },
      {
        id: 2,
        name: '内存预测模型训练',
        type: 'prediction',
        status: 'completed',
        dataset: '内存使用数据集',
        algorithm: 'Random Forest',
        finalAccuracy: 92.8,
        duration: '3小时15分钟',
        createdAt: '1天前'
      },
      {
        id: 3,
        name: '网络流量分类训练',
        type: 'classification',
        status: 'paused',
        progress: 45,
        dataset: '网络流量数据集',
        algorithm: 'CNN',
        createdAt: '6小时前'
      },
      {
        id: 4,
        name: '磁盘容量预测训练',
        type: 'regression',
        status: 'failed',
        dataset: '磁盘使用数据集',
        algorithm: 'Linear Regression',
        errorMessage: '数据预处理失败',
        createdAt: '2天前'
      },
      {
        id: 5,
        name: '服务器性能预测训练',
        type: 'prediction',
        status: 'queued',
        dataset: '服务器性能数据集',
        algorithm: 'XGBoost',
        createdAt: '30分钟前'
      }
    ])

    /**
     * 过滤后的训练任务列表
     */
    const filteredTasks = computed(() => {
      return trainingTasks.value.filter(task => {
        const matchesSearch = task.name.toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesStatus = !filters.value.status || task.status === filters.value.status
        const matchesType = !filters.value.type || task.type === filters.value.type
        
        return matchesSearch && matchesStatus && matchesType
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
        'running': '运行中',
        'completed': '已完成',
        'paused': '已暂停',
        'failed': '失败',
        'queued': '队列中'
      }
      return statusMap[status] || status
    }

    /**
     * 新建训练任务
     */
    const newTrainingTask = () => {
      console.log('新建训练任务')
      // TODO: 实现新建训练任务逻辑
    }

    /**
     * 查看任务详情
     */
    const viewTask = (task) => {
      console.log('查看任务详情:', task.name)
      // TODO: 实现查看任务详情逻辑
    }

    /**
     * 查看训练日志
     */
    const viewLogs = (task) => {
      console.log('查看训练日志:', task.name)
      // TODO: 实现查看训练日志逻辑
    }

    /**
     * 暂停训练任务
     */
    const pauseTask = (task) => {
      console.log('暂停训练任务:', task.name)
      task.status = 'paused'
    }

    /**
     * 继续训练任务
     */
    const resumeTask = (task) => {
      console.log('继续训练任务:', task.name)
      task.status = 'running'
    }

    /**
     * 停止训练任务
     */
    const stopTask = (task) => {
      console.log('停止训练任务:', task.name)
      task.status = 'failed'
      task.errorMessage = '用户手动停止'
    }

    /**
     * 重新训练
     */
    const retryTask = (task) => {
      console.log('重新训练:', task.name)
      task.status = 'queued'
    }

    /**
     * 删除训练任务
     */
    const deleteTask = (task) => {
      if (confirm(`确定要删除训练任务 "${task.name}" 吗？`)) {
        const index = trainingTasks.value.findIndex(t => t.id === task.id)
        if (index > -1) {
          trainingTasks.value.splice(index, 1)
        }
      }
    }

    // 生命周期钩子
    onMounted(() => {
      console.log('模型训练组件已加载')
    })

    return {
      searchQuery,
      filters,
      trainingStats,
      resourceUsage,
      trainingTasks,
      filteredTasks,
      getModelTypeText,
      getStatusText,
      newTrainingTask,
      viewTask,
      viewLogs,
      pauseTask,
      resumeTask,
      stopTask,
      retryTask,
      deleteTask
    }
  }
}
</script>

<style scoped>
.model-training {
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

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
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

/* 训练统计 */
.training-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3b82f6;
  color: white;
  border-radius: 6px;
  font-size: 16px;
}

.stat-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

/* 训练任务列表 */
.training-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.training-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;
}

.training-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.training-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.training-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.training-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.training-type {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
}

.training-time {
  font-size: 12px;
  color: #9ca3af;
}

.training-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.running {
  background: #10b981;
}

.status-indicator.completed {
  background: #3b82f6;
}

.status-indicator.paused {
  background: #f59e0b;
}

.status-indicator.failed {
  background: #ef4444;
}

.status-indicator.queued {
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
  font-weight: 500;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: #10b981;
  transition: width 0.3s;
}

.progress-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.progress-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.progress-item .label {
  color: #6b7280;
}

.progress-item .value {
  color: #1f2937;
  font-weight: 500;
}

/* 训练详情 */
.training-details {
  margin-bottom: 16px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.detail-label {
  color: #6b7280;
}

.detail-value {
  color: #1f2937;
  font-weight: 500;
}

.detail-value.error {
  color: #ef4444;
}

/* 训练操作 */
.training-actions {
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

/* 资源监控 */
.resource-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.resource-card {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.resource-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.resource-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.resource-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.resource-bar {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  background: #3b82f6;
  transition: width 0.3s;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .model-training {
    padding: 16px;
  }

  .ai-section {
    padding: 16px;
  }

  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
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

  .training-stats {
    grid-template-columns: 1fr;
  }

  .training-header {
    flex-direction: column;
    gap: 12px;
  }

  .progress-details {
    grid-template-columns: 1fr;
  }

  .resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>