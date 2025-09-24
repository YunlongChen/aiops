<!--
  自愈系统仪表板组件
  提供自愈统计概览、活跃修复任务、最近修复历史等功能
-->
<template>
  <div class="healing-dashboard">
    <!-- 自愈统计概览 -->
    <div class="healing-section">
      <div class="section-header">
        <h3>自愈统计</h3>
        <div class="time-range-selector">
          <select v-model="selectedTimeRange" @change="onTimeRangeChange">
            <option value="1h">最近1小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
          </select>
        </div>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card success">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-info">
            <h4>成功修复</h4>
            <span class="stat-value">{{ stats.success }}</span>
            <span class="stat-change positive">+{{ stats.successChange }}</span>
          </div>
        </div>
        
        <div class="stat-card running">
          <div class="stat-icon">
            <i class="fas fa-cog fa-spin"></i>
          </div>
          <div class="stat-info">
            <h4>正在修复</h4>
            <span class="stat-value">{{ stats.running }}</span>
            <span class="stat-change neutral">{{ stats.runningChange }}</span>
          </div>
        </div>
        
        <div class="stat-card failed">
          <div class="stat-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="stat-info">
            <h4>修复失败</h4>
            <span class="stat-value">{{ stats.failed }}</span>
            <span class="stat-change negative">+{{ stats.failedChange }}</span>
          </div>
        </div>
        
        <div class="stat-card rate">
          <div class="stat-icon">
            <i class="fas fa-percentage"></i>
          </div>
          <div class="stat-info">
            <h4>成功率</h4>
            <span class="stat-value">{{ stats.successRate }}%</span>
            <span class="stat-change positive">+{{ stats.rateChange }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 活跃修复任务 -->
    <div class="healing-section">
      <div class="section-header">
        <h3>活跃修复任务</h3>
        <div class="section-actions">
          <button class="btn btn-secondary btn-sm" @click="pauseAllTasks">
            <i class="fas fa-pause"></i>
            暂停全部
          </button>
        </div>
      </div>
      
      <div class="active-tasks">
        <div 
          v-for="task in activeTasks" 
          :key="task.id"
          :class="['task-card', task.status]"
        >
          <div class="task-header">
            <div class="task-info">
              <h4>{{ task.title }}</h4>
              <span class="task-id">{{ task.id }}</span>
            </div>
            <div class="task-status">
              <span :class="['status-badge', task.status]">
                <i :class="getStatusIcon(task.status)"></i>
                {{ getStatusText(task.status) }}
              </span>
            </div>
          </div>
          
          <div class="task-details">
            <div class="detail-item">
              <span class="label">目标服务器:</span>
              <span class="value">{{ task.target }}</span>
            </div>
            <div class="detail-item">
              <span class="label">触发条件:</span>
              <span class="value">{{ task.condition }}</span>
            </div>
            <div class="detail-item">
              <span class="label">修复脚本:</span>
              <span class="value">{{ task.script }}</span>
            </div>
            <div class="detail-item">
              <span class="label">{{ task.status === 'pending' ? '预计开始' : '开始时间' }}:</span>
              <span class="value">{{ task.startTime }}</span>
            </div>
          </div>
          
          <div v-if="task.status === 'running'" class="task-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: task.progress + '%' }"></div>
            </div>
            <span class="progress-text">{{ task.progress }}% - {{ task.progressText }}</span>
          </div>
          
          <div class="task-actions">
            <button 
              v-if="task.status === 'running'"
              class="btn btn-secondary btn-sm"
              @click="pauseTask(task.id)"
            >
              <i class="fas fa-pause"></i>
              暂停
            </button>
            <button 
              v-if="task.status === 'pending'"
              class="btn btn-primary btn-sm"
              @click="executeTask(task.id)"
            >
              <i class="fas fa-play"></i>
              立即执行
            </button>
            <button 
              v-if="task.status !== 'pending'"
              class="btn btn-danger btn-sm"
              @click="stopTask(task.id)"
            >
              <i class="fas fa-stop"></i>
              {{ task.status === 'pending' ? '取消' : '停止' }}
            </button>
            <button class="btn btn-info btn-sm" @click="viewTaskDetails(task.id)">
              <i class="fas fa-eye"></i>
              详情
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近修复历史 -->
    <div class="healing-section">
      <div class="section-header">
        <h3>最近修复历史</h3>
        <div class="section-actions">
          <button class="btn btn-secondary btn-sm" @click="viewAllHistory">
            <i class="fas fa-list"></i>
            查看全部
          </button>
        </div>
      </div>
      
      <div class="history-table">
        <table>
          <thead>
            <tr>
              <th>任务ID</th>
              <th>问题描述</th>
              <th>修复方式</th>
              <th>执行时间</th>
              <th>耗时</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="record in historyRecords" 
              :key="record.id"
              :class="['history-row', record.status]"
            >
              <td>
                <span class="task-id">{{ record.id }}</span>
              </td>
              <td>
                <div class="problem-info">
                  <div class="problem-title">{{ record.problem }}</div>
                  <div class="problem-target">{{ record.target }}</div>
                </div>
              </td>
              <td>
                <span class="script-name">{{ record.script }}</span>
              </td>
              <td>{{ record.executeTime }}</td>
              <td>
                <span class="duration">{{ record.duration }}</span>
              </td>
              <td>
                <span :class="['status-badge', record.status]">
                  <i :class="getStatusIcon(record.status)"></i>
                  {{ getStatusText(record.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-icon" @click="viewLog(record.id)" title="查看日志">
                    <i class="fas fa-file-alt"></i>
                  </button>
                  <button class="btn-icon" @click="reExecute(record.id)" title="重新执行">
                    <i class="fas fa-redo"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'HealingDashboard',
  emits: ['refresh'],
  setup(props, { emit }) {
    // 响应式数据
    const selectedTimeRange = ref('24h')
    const stats = ref({
      success: 47,
      successChange: 8,
      running: 3,
      runningChange: 0,
      failed: 2,
      failedChange: 1,
      successRate: 94,
      rateChange: 2
    })

    const activeTasks = ref([
      {
        id: '#HEAL-001',
        title: 'CPU使用率过高自动修复',
        status: 'running',
        target: 'web-server-01',
        condition: 'CPU > 90% 持续5分钟',
        script: 'restart-high-cpu-processes.sh',
        startTime: '2024-01-15 14:35:20',
        progress: 65,
        progressText: '正在重启高CPU进程'
      },
      {
        id: '#HEAL-002',
        title: '数据库连接池清理',
        status: 'running',
        target: 'mysql-primary',
        condition: '连接数 > 80% 持续3分钟',
        script: 'cleanup-db-connections.py',
        startTime: '2024-01-15 14:32:15',
        progress: 40,
        progressText: '正在清理空闲连接'
      },
      {
        id: '#HEAL-003',
        title: '磁盘空间清理',
        status: 'pending',
        target: 'log-server-01',
        condition: '磁盘使用率 > 85%',
        script: 'cleanup-old-logs.sh',
        startTime: '2024-01-15 14:40:00'
      }
    ])

    const historyRecords = ref([
      {
        id: '#HEAL-098',
        problem: '内存使用率过高',
        target: 'app-server-02',
        script: 'restart-memory-intensive-services.sh',
        executeTime: '2024-01-15 14:20:30',
        duration: '2分30秒',
        status: 'success'
      },
      {
        id: '#HEAL-097',
        problem: 'Nginx服务异常',
        target: 'web-server-03',
        script: 'restart-nginx-service.sh',
        executeTime: '2024-01-15 14:15:45',
        duration: '1分15秒',
        status: 'success'
      },
      {
        id: '#HEAL-096',
        problem: '磁盘I/O异常',
        target: 'db-server-01',
        script: 'optimize-disk-io.sh',
        executeTime: '2024-01-15 14:10:20',
        duration: '5分45秒',
        status: 'failed'
      }
    ])

    // 方法
    /**
     * 获取状态图标
     * @param {string} status - 状态
     * @returns {string} 图标类名
     */
    const getStatusIcon = (status) => {
      switch (status) {
        case 'running':
          return 'fas fa-cog fa-spin'
        case 'pending':
          return 'fas fa-clock'
        case 'success':
          return 'fas fa-check-circle'
        case 'failed':
          return 'fas fa-times-circle'
        default:
          return 'fas fa-question-circle'
      }
    }

    /**
     * 获取状态文本
     * @param {string} status - 状态
     * @returns {string} 状态文本
     */
    const getStatusText = (status) => {
      switch (status) {
        case 'running':
          return '执行中'
        case 'pending':
          return '等待中'
        case 'success':
          return '成功'
        case 'failed':
          return '失败'
        default:
          return '未知'
      }
    }

    /**
     * 时间范围变更处理
     */
    const onTimeRangeChange = () => {
      console.log('时间范围变更:', selectedTimeRange.value)
      loadStats()
    }

    /**
     * 加载统计数据
     */
    const loadStats = async () => {
      try {
        // 模拟API调用
        console.log('加载自愈统计数据...')
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    }

    /**
     * 暂停所有任务
     */
    const pauseAllTasks = () => {
      console.log('暂停所有活跃任务')
    }

    /**
     * 暂停任务
     * @param {string} taskId - 任务ID
     */
    const pauseTask = (taskId) => {
      console.log('暂停任务:', taskId)
    }

    /**
     * 执行任务
     * @param {string} taskId - 任务ID
     */
    const executeTask = (taskId) => {
      console.log('立即执行任务:', taskId)
    }

    /**
     * 停止任务
     * @param {string} taskId - 任务ID
     */
    const stopTask = (taskId) => {
      console.log('停止任务:', taskId)
    }

    /**
     * 查看任务详情
     * @param {string} taskId - 任务ID
     */
    const viewTaskDetails = (taskId) => {
      console.log('查看任务详情:', taskId)
    }

    /**
     * 查看全部历史
     */
    const viewAllHistory = () => {
      console.log('查看全部修复历史')
    }

    /**
     * 查看日志
     * @param {string} recordId - 记录ID
     */
    const viewLog = (recordId) => {
      console.log('查看日志:', recordId)
    }

    /**
     * 重新执行
     * @param {string} recordId - 记录ID
     */
    const reExecute = (recordId) => {
      console.log('重新执行:', recordId)
    }

    // 生命周期
    onMounted(() => {
      loadStats()
    })

    return {
      selectedTimeRange,
      stats,
      activeTasks,
      historyRecords,
      getStatusIcon,
      getStatusText,
      onTimeRangeChange,
      pauseAllTasks,
      pauseTask,
      executeTask,
      stopTask,
      viewTaskDetails,
      viewAllHistory,
      viewLog,
      reExecute
    }
  }
}
</script>

<style scoped>
.healing-dashboard {
  padding: 20px;
}

.healing-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.time-range-selector select {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  color: #666;
}

.section-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.3s ease;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 11px;
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-primary {
  background: #1890ff;
  color: white;
}

.btn-primary:hover {
  background: #40a9ff;
}

.btn-danger {
  background: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background: #ff7875;
}

.btn-info {
  background: #13c2c2;
  color: white;
}

.btn-info:hover {
  background: #36cfc9;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-card.success .stat-icon {
  background: #f6ffed;
  color: #52c41a;
}

.stat-card.running .stat-icon {
  background: #e6f7ff;
  color: #1890ff;
}

.stat-card.failed .stat-icon {
  background: #fff2f0;
  color: #ff4d4f;
}

.stat-card.rate .stat-icon {
  background: #f9f0ff;
  color: #722ed1;
}

.stat-info h4 {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 14px;
  font-weight: normal;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-right: 8px;
}

.stat-change {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.stat-change.positive {
  background: #f6ffed;
  color: #52c41a;
}

.stat-change.negative {
  background: #fff2f0;
  color: #ff4d4f;
}

.stat-change.neutral {
  background: #f0f0f0;
  color: #666;
}

/* 活跃任务 */
.active-tasks {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-left: 4px solid #d9d9d9;
}

.task-card.running {
  border-left-color: #1890ff;
}

.task-card.pending {
  border-left-color: #faad14;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.task-info h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 16px;
}

.task-id {
  color: #666;
  font-size: 12px;
  font-family: monospace;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-badge.running {
  background: #e6f7ff;
  color: #1890ff;
}

.status-badge.pending {
  background: #fff7e6;
  color: #faad14;
}

.status-badge.success {
  background: #f6ffed;
  color: #52c41a;
}

.status-badge.failed {
  background: #fff2f0;
  color: #ff4d4f;
}

.task-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-item .label {
  font-size: 12px;
  color: #666;
}

.detail-item .value {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.task-progress {
  margin-bottom: 15px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 5px;
}

.progress-fill {
  height: 100%;
  background: #1890ff;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
}

.task-actions {
  display: flex;
  gap: 8px;
}

/* 历史记录表格 */
.history-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  background: #fafafa;
  padding: 12px;
  text-align: left;
  font-weight: 500;
  color: #666;
  font-size: 13px;
  border-bottom: 1px solid #f0f0f0;
}

.history-table td {
  padding: 12px;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.history-row:hover {
  background: #fafafa;
}

.problem-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.problem-title {
  color: #333;
  font-weight: 500;
}

.problem-target {
  color: #666;
  font-size: 12px;
}

.script-name {
  font-family: monospace;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 12px;
}

.duration {
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.btn-icon {
  width: 28px;
  height: 28px;
  border: none;
  background: #f0f0f0;
  color: #666;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.btn-icon:hover {
  background: #e0e0e0;
  color: #1890ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .healing-dashboard {
    padding: 10px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .task-details {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .history-table {
    overflow-x: auto;
  }
}
</style>