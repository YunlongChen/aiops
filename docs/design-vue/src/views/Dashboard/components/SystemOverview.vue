<!--
  系统概览组件
  功能：显示系统状态、关键指标图表和最近事件
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="system-overview">
    <!-- 系统状态卡片 -->
    <div class="status-cards">
      <div 
        v-for="card in statusCards" 
        :key="card.id"
        :class="['status-card', card.type]"
      >
        <div class="card-icon">
          <i :class="card.icon"></i>
        </div>
        <div class="card-content">
          <div class="card-title">{{ card.title }}</div>
          <div class="card-value">{{ card.value }}</div>
          <div class="card-description">{{ card.description }}</div>
        </div>
      </div>
    </div>

    <!-- 关键指标图表 -->
    <div class="charts-section">
      <div class="chart-card">
        <div class="chart-header">
          <h3>系统性能趋势</h3>
          <div class="chart-controls">
            <select v-model="performanceTimeRange" @change="updatePerformanceChart">
              <option value="1h">最近1小时</option>
              <option value="6h">最近6小时</option>
              <option value="24h">最近24小时</option>
              <option value="7d">最近7天</option>
            </select>
          </div>
        </div>
        <div class="chart-content">
          <canvas ref="performanceChart" id="performance-chart"></canvas>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>资源使用率</h3>
          <div class="refresh-btn" @click="refreshResourceChart">
            <i class="fas fa-sync-alt"></i>
          </div>
        </div>
        <div class="chart-content">
          <canvas ref="resourceChart" id="resource-chart"></canvas>
        </div>
      </div>
    </div>

    <!-- 最近事件和告警 -->
    <div class="events-section">
      <div class="events-card">
        <div class="card-header">
          <h3>最近告警</h3>
          <a href="#" class="view-all" @click="viewAllAlerts">查看全部</a>
        </div>
        <div class="table-content">
          <table class="data-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>级别</th>
                <th>告警内容</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="alert in recentAlerts" :key="alert.id">
                <td>{{ alert.time }}</td>
                <td>
                  <span :class="['level', alert.level]">{{ alert.levelText }}</span>
                </td>
                <td>{{ alert.content }}</td>
                <td>
                  <span :class="['status', alert.status]">{{ alert.statusText }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="events-card">
        <div class="card-header">
          <h3>自愈操作记录</h3>
          <a href="#" class="view-all" @click="viewAllHealingRecords">查看全部</a>
        </div>
        <div class="table-content">
          <table class="data-table">
            <thead>
              <tr>
                <th>时间</th>
                <th>触发事件</th>
                <th>执行操作</th>
                <th>结果</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in healingRecords" :key="record.id">
                <td>{{ record.time }}</td>
                <td>{{ record.trigger }}</td>
                <td>{{ record.action }}</td>
                <td>
                  <span :class="['status', record.result]">{{ record.resultText }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 系统概览组件
 * 显示系统状态卡片、性能图表和最近事件
 */
export default {
  name: 'SystemOverview',
  data() {
    return {
      // 性能图表时间范围
      performanceTimeRange: '24h',
      // 系统状态卡片数据
      statusCards: [
        {
          id: 1,
          type: 'healthy',
          icon: 'fas fa-check-circle',
          title: '系统健康',
          value: '98.5%',
          description: '所有服务正常运行'
        },
        {
          id: 2,
          type: 'warning',
          icon: 'fas fa-exclamation-triangle',
          title: '告警数量',
          value: '3',
          description: '需要关注的告警'
        },
        {
          id: 3,
          type: 'info',
          icon: 'fas fa-info-circle',
          title: '活跃连接',
          value: '1,234',
          description: '当前活跃用户连接'
        },
        {
          id: 4,
          type: 'success',
          icon: 'fas fa-magic',
          title: '自愈成功率',
          value: '95.2%',
          description: '自动修复成功率'
        }
      ],
      // 最近告警数据
      recentAlerts: [
        {
          id: 1,
          time: '14:35',
          level: 'critical',
          levelText: '严重',
          content: '数据库连接池耗尽',
          status: 'active',
          statusText: '处理中'
        },
        {
          id: 2,
          time: '13:22',
          level: 'warning',
          levelText: '警告',
          content: 'CPU使用率超过80%',
          status: 'resolved',
          statusText: '已解决'
        },
        {
          id: 3,
          time: '12:15',
          level: 'info',
          levelText: '信息',
          content: '定时备份任务完成',
          status: 'resolved',
          statusText: '已完成'
        }
      ],
      // 自愈操作记录
      healingRecords: [
        {
          id: 1,
          time: '14:30',
          trigger: '数据库连接异常',
          action: '重启连接池',
          result: 'success',
          resultText: '成功'
        },
        {
          id: 2,
          time: '13:45',
          trigger: '磁盘空间不足',
          action: '清理临时文件',
          result: 'success',
          resultText: '成功'
        },
        {
          id: 3,
          time: '12:20',
          trigger: '服务响应超时',
          action: '重启服务实例',
          result: 'success',
          resultText: '成功'
        }
      ]
    }
  },
  methods: {
    /**
     * 更新性能图表
     */
    updatePerformanceChart() {
      // 这里应该根据时间范围更新图表数据
      console.log('Updating performance chart for:', this.performanceTimeRange)
    },
    
    /**
     * 刷新资源图表
     */
    refreshResourceChart() {
      console.log('Refreshing resource chart')
    },
    
    /**
     * 查看全部告警
     */
    viewAllAlerts() {
      this.$router.push('/alerting')
    },
    
    /**
     * 查看全部自愈记录
     */
    viewAllHealingRecords() {
      this.$router.push('/self-healing')
    }
  },
  mounted() {
    // 初始化图表
    this.initCharts()
  },
  methods: {
    /**
     * 初始化图表
     */
    initCharts() {
      // 这里可以使用Chart.js或其他图表库初始化图表
      console.log('Initializing charts')
    }
  }
}
</script>

<style scoped>
/* 系统概览容器 */
.system-overview {
  padding: 20px;
}

/* 状态卡片样式 */
.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.status-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.status-card:hover {
  transform: translateY(-2px);
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.status-card.healthy .card-icon {
  background: #d4edda;
  color: #155724;
}

.status-card.warning .card-icon {
  background: #fff3cd;
  color: #856404;
}

.status-card.info .card-icon {
  background: #d1ecf1;
  color: #0c5460;
}

.status-card.success .card-icon {
  background: #d4edda;
  color: #155724;
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 14px;
  color: #6c757d;
  margin-bottom: 5px;
}

.card-value {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.card-description {
  font-size: 12px;
  color: #6c757d;
}

/* 图表区域样式 */
.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chart-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.chart-controls select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.refresh-btn {
  cursor: pointer;
  padding: 5px;
  color: #6c757d;
  transition: color 0.2s ease;
}

.refresh-btn:hover {
  color: #3498db;
}

.chart-content {
  padding: 20px;
  height: 300px;
}

.chart-content canvas {
  width: 100% !important;
  height: 100% !important;
}

/* 事件区域样式 */
.events-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.events-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-header {
  padding: 20px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.view-all {
  color: #3498db;
  text-decoration: none;
  font-size: 12px;
  transition: color 0.2s ease;
}

.view-all:hover {
  color: #2980b9;
}

/* 表格样式 */
.table-content {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 12px;
  text-transform: uppercase;
}

.data-table td {
  font-size: 14px;
  color: #495057;
}

/* 状态标签样式 */
.level, .status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
}

.level.critical {
  background: #f8d7da;
  color: #721c24;
}

.level.warning {
  background: #fff3cd;
  color: #856404;
}

.level.info {
  background: #d1ecf1;
  color: #0c5460;
}

.status.active {
  background: #fff3cd;
  color: #856404;
}

.status.resolved {
  background: #d4edda;
  color: #155724;
}

.status.success {
  background: #d4edda;
  color: #155724;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .system-overview {
    padding: 15px;
  }
  
  .status-cards {
    grid-template-columns: 1fr;
  }
  
  .events-section {
    grid-template-columns: 1fr;
  }
  
  .chart-content {
    height: 250px;
  }
}
</style>