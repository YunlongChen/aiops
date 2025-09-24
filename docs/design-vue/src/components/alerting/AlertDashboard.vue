<!--
  告警仪表板组件
  提供告警概览、活跃告警列表、告警趋势图表等功能
  实现告警系统的核心监控界面
-->
<template>
  <div class="alert-dashboard">
    <!-- 告警统计概览 -->
    <div class="alert-stats">
      <div class="stats-header">
        <h3>告警概览</h3>
        <div class="time-range-selector">
          <select v-model="selectedTimeRange" @change="onTimeRangeChange">
            <option value="1h">最近1小时</option>
            <option value="6h">最近6小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
          </select>
        </div>
      </div>
      
      <div class="stats-grid">
        <div class="stat-card critical">
          <div class="stat-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ alertStats.critical }}</div>
            <div class="stat-label">严重告警</div>
            <div class="stat-trend" :class="{ increase: alertTrends.critical > 0, decrease: alertTrends.critical < 0 }">
              <i :class="alertTrends.critical > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(alertTrends.critical) }}%
            </div>
          </div>
        </div>
        
        <div class="stat-card warning">
          <div class="stat-icon">
            <i class="fas fa-exclamation-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ alertStats.warning }}</div>
            <div class="stat-label">警告告警</div>
            <div class="stat-trend" :class="{ increase: alertTrends.warning > 0, decrease: alertTrends.warning < 0 }">
              <i :class="alertTrends.warning > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(alertTrends.warning) }}%
            </div>
          </div>
        </div>
        
        <div class="stat-card info">
          <div class="stat-icon">
            <i class="fas fa-info-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ alertStats.info }}</div>
            <div class="stat-label">信息告警</div>
            <div class="stat-trend" :class="{ increase: alertTrends.info > 0, decrease: alertTrends.info < 0 }">
              <i :class="alertTrends.info > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(alertTrends.info) }}%
            </div>
          </div>
        </div>
        
        <div class="stat-card resolved">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-number">{{ alertStats.resolved }}</div>
            <div class="stat-label">已解决</div>
            <div class="stat-trend" :class="{ increase: alertTrends.resolved > 0, decrease: alertTrends.resolved < 0 }">
              <i :class="alertTrends.resolved > 0 ? 'fas fa-arrow-up' : 'fas fa-arrow-down'"></i>
              {{ Math.abs(alertTrends.resolved) }}%
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 活跃告警列表 -->
    <div class="active-alerts">
      <div class="alerts-header">
        <h3>活跃告警</h3>
        <div class="alerts-filters">
          <select v-model="selectedLevel" @change="filterAlerts">
            <option value="">所有级别</option>
            <option value="critical">严重</option>
            <option value="warning">警告</option>
            <option value="info">信息</option>
          </select>
          
          <select v-model="selectedSource" @change="filterAlerts">
            <option value="">所有来源</option>
            <option value="infrastructure">基础设施</option>
            <option value="application">应用服务</option>
            <option value="database">数据库</option>
            <option value="network">网络</option>
          </select>
          
          <div class="search-box">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              placeholder="搜索告警..." 
              v-model="searchQuery"
              @input="filterAlerts"
            >
          </div>
        </div>
      </div>
      
      <div class="alerts-table">
        <table>
          <thead>
            <tr>
              <th>级别</th>
              <th>告警名称</th>
              <th>来源</th>
              <th>触发时间</th>
              <th>持续时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="alert in filteredAlerts" :key="alert.id" :class="alert.level">
              <td>
                <span class="alert-level" :class="alert.level">
                  <i :class="getLevelIcon(alert.level)"></i>
                  {{ getLevelText(alert.level) }}
                </span>
              </td>
              <td>
                <div class="alert-name">
                  <span class="name">{{ alert.name }}</span>
                  <span class="description">{{ alert.description }}</span>
                </div>
              </td>
              <td>
                <span class="alert-source">{{ alert.source }}</span>
              </td>
              <td>
                <span class="alert-time">{{ formatTime(alert.triggerTime) }}</span>
              </td>
              <td>
                <span class="alert-duration">{{ formatDuration(alert.duration) }}</span>
              </td>
              <td>
                <span class="alert-status" :class="alert.status">
                  {{ getStatusText(alert.status) }}
                </span>
              </td>
              <td>
                <div class="alert-actions">
                  <button 
                    class="action-btn acknowledge" 
                    @click="acknowledgeAlert(alert.id)"
                    :disabled="alert.status === 'acknowledged'"
                    title="确认告警"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  <button 
                    class="action-btn resolve" 
                    @click="resolveAlert(alert.id)"
                    title="解决告警"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                  <button 
                    class="action-btn details" 
                    @click="viewDetails(alert.id)"
                    title="查看详情"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="filteredAlerts.length === 0" class="no-alerts">
          <i class="fas fa-bell-slash"></i>
          <p>暂无活跃告警</p>
        </div>
      </div>
    </div>

    <!-- 告警趋势图表 -->
    <div class="alert-charts">
      <div class="chart-grid">
        <!-- 告警数量趋势 -->
        <div class="chart-card">
          <div class="chart-header">
            <h4>告警数量趋势</h4>
            <div class="chart-legend">
              <span class="legend-item critical">
                <span class="legend-color"></span>
                严重
              </span>
              <span class="legend-item warning">
                <span class="legend-color"></span>
                警告
              </span>
              <span class="legend-item info">
                <span class="legend-color"></span>
                信息
              </span>
            </div>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-chart-line"></i>
              <p>告警数量趋势图</p>
            </div>
          </div>
        </div>
        
        <!-- 告警级别分布 -->
        <div class="chart-card">
          <div class="chart-header">
            <h4>告警级别分布</h4>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-chart-pie"></i>
              <p>告警级别分布图</p>
            </div>
          </div>
        </div>
        
        <!-- 告警来源分析 -->
        <div class="chart-card">
          <div class="chart-header">
            <h4>告警来源分析</h4>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-chart-bar"></i>
              <p>告警来源分析图</p>
            </div>
          </div>
        </div>
        
        <!-- 平均解决时间 -->
        <div class="chart-card">
          <div class="chart-header">
            <h4>平均解决时间</h4>
          </div>
          <div class="chart-content">
            <div class="chart-placeholder">
              <i class="fas fa-clock"></i>
              <p>平均解决时间统计</p>
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
  name: 'AlertDashboard',
  setup() {
    // 响应式数据
    const selectedTimeRange = ref('24h')
    const selectedLevel = ref('')
    const selectedSource = ref('')
    const searchQuery = ref('')

    // 告警统计数据
    const alertStats = ref({
      critical: 8,
      warning: 23,
      info: 15,
      resolved: 142
    })

    // 告警趋势数据
    const alertTrends = ref({
      critical: 12,
      warning: -5,
      info: 8,
      resolved: 15
    })

    // 活跃告警数据
    const alerts = ref([
      {
        id: 1,
        name: 'CPU使用率过高',
        description: 'web-server-01 CPU使用率超过90%',
        level: 'critical',
        source: '基础设施',
        triggerTime: new Date(Date.now() - 2 * 60 * 60 * 1000),
        duration: 2 * 60 * 60 * 1000,
        status: 'firing'
      },
      {
        id: 2,
        name: '数据库连接失败',
        description: 'MySQL主库连接超时',
        level: 'critical',
        source: '数据库',
        triggerTime: new Date(Date.now() - 1.5 * 60 * 60 * 1000),
        duration: 1.5 * 60 * 60 * 1000,
        status: 'acknowledged'
      },
      {
        id: 3,
        name: '内存使用率高',
        description: 'app-server-02 内存使用率超过85%',
        level: 'warning',
        source: '应用服务',
        triggerTime: new Date(Date.now() - 45 * 60 * 1000),
        duration: 45 * 60 * 1000,
        status: 'firing'
      },
      {
        id: 4,
        name: '磁盘空间不足',
        description: '/var/log 分区使用率超过95%',
        level: 'warning',
        source: '基础设施',
        triggerTime: new Date(Date.now() - 30 * 60 * 1000),
        duration: 30 * 60 * 1000,
        status: 'firing'
      },
      {
        id: 5,
        name: '服务重启',
        description: 'nginx服务异常重启',
        level: 'info',
        source: '应用服务',
        triggerTime: new Date(Date.now() - 15 * 60 * 1000),
        duration: 15 * 60 * 1000,
        status: 'firing'
      }
    ])

    // 过滤后的告警列表
    const filteredAlerts = computed(() => {
      return alerts.value.filter(alert => {
        const matchLevel = !selectedLevel.value || alert.level === selectedLevel.value
        const matchSource = !selectedSource.value || alert.source.includes(selectedSource.value)
        const matchSearch = !searchQuery.value || 
          alert.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
          alert.description.toLowerCase().includes(searchQuery.value.toLowerCase())
        
        return matchLevel && matchSource && matchSearch
      })
    })

    /**
     * 获取告警级别图标
     */
    const getLevelIcon = (level) => {
      const icons = {
        critical: 'fas fa-exclamation-triangle',
        warning: 'fas fa-exclamation-circle',
        info: 'fas fa-info-circle'
      }
      return icons[level] || 'fas fa-bell'
    }

    /**
     * 获取告警级别文本
     */
    const getLevelText = (level) => {
      const texts = {
        critical: '严重',
        warning: '警告',
        info: '信息'
      }
      return texts[level] || level
    }

    /**
     * 获取告警状态文本
     */
    const getStatusText = (status) => {
      const texts = {
        firing: '触发中',
        acknowledged: '已确认',
        resolved: '已解决'
      }
      return texts[status] || status
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
     * 格式化持续时间
     */
    const formatDuration = (duration) => {
      const hours = Math.floor(duration / (60 * 60 * 1000))
      const minutes = Math.floor((duration % (60 * 60 * 1000)) / (60 * 1000))
      
      if (hours > 0) {
        return `${hours}小时${minutes}分钟`
      }
      return `${minutes}分钟`
    }

    /**
     * 时间范围变化处理
     */
    const onTimeRangeChange = () => {
      console.log('时间范围变更:', selectedTimeRange.value)
      // TODO: 根据时间范围重新加载数据
    }

    /**
     * 过滤告警
     */
    const filterAlerts = () => {
      console.log('过滤告警:', {
        level: selectedLevel.value,
        source: selectedSource.value,
        search: searchQuery.value
      })
    }

    /**
     * 确认告警
     */
    const acknowledgeAlert = (alertId) => {
      const alert = alerts.value.find(a => a.id === alertId)
      if (alert) {
        alert.status = 'acknowledged'
        console.log('确认告警:', alertId)
      }
    }

    /**
     * 解决告警
     */
    const resolveAlert = (alertId) => {
      const alertIndex = alerts.value.findIndex(a => a.id === alertId)
      if (alertIndex !== -1) {
        alerts.value.splice(alertIndex, 1)
        console.log('解决告警:', alertId)
      }
    }

    /**
     * 查看告警详情
     */
    const viewDetails = (alertId) => {
      console.log('查看告警详情:', alertId)
      // TODO: 打开告警详情弹窗
    }

    // 生命周期钩子
    onMounted(() => {
      console.log('告警仪表板已加载')
    })

    return {
      selectedTimeRange,
      selectedLevel,
      selectedSource,
      searchQuery,
      alertStats,
      alertTrends,
      alerts,
      filteredAlerts,
      getLevelIcon,
      getLevelText,
      getStatusText,
      formatTime,
      formatDuration,
      onTimeRangeChange,
      filterAlerts,
      acknowledgeAlert,
      resolveAlert,
      viewDetails
    }
  }
}
</script>

<style scoped>
.alert-dashboard {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
  overflow-y: auto;
}

/* 告警统计概览 */
.alert-stats {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stats-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stats-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.time-range-selector select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 8px;
  border-left: 4px solid;
}

.stat-card.critical {
  background: #fef2f2;
  border-left-color: #dc2626;
}

.stat-card.warning {
  background: #fffbeb;
  border-left-color: #d97706;
}

.stat-card.info {
  background: #eff6ff;
  border-left-color: #2563eb;
}

.stat-card.resolved {
  background: #f0fdf4;
  border-left-color: #16a34a;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-card.critical .stat-icon {
  background: #dc2626;
  color: white;
}

.stat-card.warning .stat-icon {
  background: #d97706;
  color: white;
}

.stat-card.info .stat-icon {
  background: #2563eb;
  color: white;
}

.stat-card.resolved .stat-icon {
  background: #16a34a;
  color: white;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin: 4px 0;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend.increase {
  color: #dc2626;
}

.stat-trend.decrease {
  color: #16a34a;
}

/* 活跃告警列表 */
.active-alerts {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  flex: 1;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 16px;
}

.alerts-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.alerts-filters {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.alerts-filters select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box i {
  position: absolute;
  left: 12px;
  color: #9ca3af;
  font-size: 14px;
}

.search-box input {
  padding: 6px 12px 6px 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  width: 200px;
}

.alerts-table {
  overflow-x: auto;
}

.alerts-table table {
  width: 100%;
  border-collapse: collapse;
}

.alerts-table th,
.alerts-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.alerts-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.alert-level {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.alert-level.critical {
  background: #fef2f2;
  color: #dc2626;
}

.alert-level.warning {
  background: #fffbeb;
  color: #d97706;
}

.alert-level.info {
  background: #eff6ff;
  color: #2563eb;
}

.alert-name .name {
  display: block;
  font-weight: 500;
  color: #1f2937;
}

.alert-name .description {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.alert-source {
  color: #6b7280;
  font-size: 14px;
}

.alert-time,
.alert-duration {
  color: #6b7280;
  font-size: 14px;
}

.alert-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.alert-status.firing {
  background: #fef2f2;
  color: #dc2626;
}

.alert-status.acknowledged {
  background: #fffbeb;
  color: #d97706;
}

.alert-status.resolved {
  background: #f0fdf4;
  color: #16a34a;
}

.alert-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.2s;
}

.action-btn.acknowledge {
  background: #fffbeb;
  color: #d97706;
}

.action-btn.acknowledge:hover:not(:disabled) {
  background: #fef3c7;
}

.action-btn.resolve {
  background: #fef2f2;
  color: #dc2626;
}

.action-btn.resolve:hover {
  background: #fecaca;
}

.action-btn.details {
  background: #eff6ff;
  color: #2563eb;
}

.action-btn.details:hover {
  background: #dbeafe;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.no-alerts {
  text-align: center;
  padding: 40px;
  color: #9ca3af;
}

.no-alerts i {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 告警趋势图表 */
.alert-charts {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.chart-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.chart-header {
  padding: 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.chart-legend {
  display: flex;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-item.critical .legend-color {
  background: #dc2626;
}

.legend-item.warning .legend-color {
  background: #d97706;
}

.legend-item.info .legend-color {
  background: #2563eb;
}

.chart-content {
  padding: 24px;
  height: 200px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
}

.chart-placeholder i {
  font-size: 48px;
  margin-bottom: 12px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .alert-dashboard {
    padding: 16px;
  }

  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
  }

  .alerts-header {
    flex-direction: column;
    align-items: stretch;
  }

  .alerts-filters {
    justify-content: space-between;
  }

  .chart-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .alert-dashboard {
    padding: 12px;
    gap: 16px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 16px;
  }

  .alerts-filters {
    flex-direction: column;
    gap: 8px;
  }

  .search-box input {
    width: 100%;
  }

  .alerts-table {
    font-size: 14px;
  }

  .alerts-table th,
  .alerts-table td {
    padding: 8px;
  }

  .alert-actions {
    flex-direction: column;
    gap: 4px;
  }
}
</style>