<!--
  基础设施监控组件
  功能：提供服务器监控、实时性能图表和系统进程监控
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="infrastructure-monitoring">
    <!-- 服务器概览 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>服务器概览</h3>
        <div class="section-actions">
          <button class="btn-icon" @click="addServer" title="添加服务器">
            <i class="fas fa-plus"></i>
          </button>
          <button class="btn-icon" @click="openSettings" title="设置">
            <i class="fas fa-cog"></i>
          </button>
        </div>
      </div>

      <div class="server-grid">
        <div 
          v-for="server in servers" 
          :key="server.id"
          :class="['server-card', server.status]"
        >
          <div class="server-header">
            <div class="server-info">
              <h4>{{ server.name }}</h4>
              <span class="server-ip">{{ server.ip }}</span>
            </div>
            <div class="server-status">
              <span :class="['status-indicator', server.status]"></span>
              <span class="status-text">{{ getStatusText(server.status) }}</span>
            </div>
          </div>
          <div class="server-metrics">
            <div class="metric">
              <span class="metric-label">CPU</span>
              <div class="metric-bar">
                <div 
                  :class="['metric-fill', getMetricLevel(server.cpu)]" 
                  :style="{ width: server.cpu + '%' }"
                ></div>
              </div>
              <span class="metric-value">{{ server.cpu }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">内存</span>
              <div class="metric-bar">
                <div 
                  :class="['metric-fill', getMetricLevel(server.memory)]" 
                  :style="{ width: server.memory + '%' }"
                ></div>
              </div>
              <span class="metric-value">{{ server.memory }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">磁盘</span>
              <div class="metric-bar">
                <div 
                  :class="['metric-fill', getMetricLevel(server.disk)]" 
                  :style="{ width: server.disk + '%' }"
                ></div>
              </div>
              <span class="metric-value">{{ server.disk }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 实时性能图表 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>实时性能监控</h3>
      </div>

      <div class="charts-grid">
        <div class="chart-card">
          <div class="chart-header">
            <h4>CPU使用率</h4>
            <span class="current-value">{{ performanceMetrics.cpu }}%</span>
          </div>
          <div class="chart-content">
            <canvas ref="cpuChart" id="cpu-chart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h4>内存使用率</h4>
            <span class="current-value">{{ performanceMetrics.memory }}%</span>
          </div>
          <div class="chart-content">
            <canvas ref="memoryChart" id="memory-chart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h4>网络流量</h4>
            <span class="current-value">{{ performanceMetrics.network }} MB/s</span>
          </div>
          <div class="chart-content">
            <canvas ref="networkChart" id="network-chart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h4>磁盘I/O</h4>
            <span class="current-value">{{ performanceMetrics.diskIO }} IOPS</span>
          </div>
          <div class="chart-content">
            <canvas ref="diskChart" id="disk-chart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- 系统进程监控 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>系统进程监控</h3>
        <div class="section-actions">
          <input
            type="text"
            v-model="processSearchQuery"
            @input="filterProcesses"
            placeholder="搜索进程..."
            class="search-input"
          />
          <button class="btn-icon" @click="refreshProcesses" title="刷新">
            <i class="fas fa-sync-alt" :class="{ spinning: isRefreshingProcesses }"></i>
          </button>
        </div>
      </div>

      <div class="table-container">
        <table class="monitoring-table">
          <thead>
            <tr>
              <th>进程名称</th>
              <th>PID</th>
              <th>CPU %</th>
              <th>内存 %</th>
              <th>状态</th>
              <th>运行时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="process in filteredProcesses" :key="process.pid">
              <td>
                <div class="process-info">
                  <i :class="process.icon"></i>
                  <span>{{ process.name }}</span>
                </div>
              </td>
              <td>{{ process.pid }}</td>
              <td>
                <span :class="['metric-badge', getMetricLevel(process.cpu)]">
                  {{ process.cpu }}%
                </span>
              </td>
              <td>
                <span :class="['metric-badge', getMetricLevel(process.memory)]">
                  {{ process.memory }}%
                </span>
              </td>
              <td>
                <span :class="['status-badge', process.status]">
                  {{ getProcessStatusText(process.status) }}
                </span>
              </td>
              <td>{{ process.uptime }}</td>
              <td>
                <button 
                  class="btn-icon" 
                  @click="restartProcess(process)"
                  title="重启"
                >
                  <i class="fas fa-redo"></i>
                </button>
                <button 
                  class="btn-icon" 
                  @click="stopProcess(process)"
                  title="停止"
                >
                  <i class="fas fa-stop"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 基础设施监控组件
 * 提供服务器状态、性能图表和进程监控功能
 */
export default {
  name: 'InfrastructureMonitoring',
  props: {
    timeRange: {
      type: String,
      default: '1h'
    },
    isRefreshing: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      // 进程搜索
      processSearchQuery: '',
      isRefreshingProcesses: false,
      // 服务器数据
      servers: [
        {
          id: 1,
          name: 'Web-Server-01',
          ip: '192.168.1.10',
          status: 'healthy',
          cpu: 45,
          memory: 67,
          disk: 32
        },
        {
          id: 2,
          name: 'DB-Server-01',
          ip: '192.168.1.20',
          status: 'warning',
          cpu: 85,
          memory: 78,
          disk: 56
        },
        {
          id: 3,
          name: 'Cache-Server-01',
          ip: '192.168.1.30',
          status: 'healthy',
          cpu: 23,
          memory: 54,
          disk: 18
        },
        {
          id: 4,
          name: 'API-Server-01',
          ip: '192.168.1.40',
          status: 'critical',
          cpu: 95,
          memory: 92,
          disk: 76
        }
      ],
      // 性能指标
      performanceMetrics: {
        cpu: 65,
        memory: 72,
        network: 45,
        diskIO: '1.2K'
      },
      // 进程数据
      processes: [
        {
          pid: 1234,
          name: 'nginx',
          icon: 'fas fa-cog',
          cpu: 12.5,
          memory: 8.2,
          status: 'running',
          uptime: '2天 14小时'
        },
        {
          pid: 5678,
          name: 'mysql',
          icon: 'fas fa-database',
          cpu: 45.8,
          memory: 32.1,
          status: 'running',
          uptime: '5天 8小时'
        },
        {
          pid: 9012,
          name: 'redis-server',
          icon: 'fas fa-memory',
          cpu: 3.2,
          memory: 15.6,
          status: 'running',
          uptime: '1天 22小时'
        },
        {
          pid: 3456,
          name: 'node',
          icon: 'fab fa-node-js',
          cpu: 28.4,
          memory: 22.8,
          status: 'running',
          uptime: '3小时 45分钟'
        }
      ],
      filteredProcesses: []
    }
  },
  methods: {
    /**
     * 获取状态文本
     */
    getStatusText(status) {
      const statusMap = {
        healthy: '正常',
        warning: '警告',
        critical: '严重',
        offline: '离线'
      }
      return statusMap[status] || '未知'
    },
    
    /**
     * 获取指标级别
     */
    getMetricLevel(value) {
      if (value >= 90) return 'critical'
      if (value >= 70) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取进程状态文本
     */
    getProcessStatusText(status) {
      const statusMap = {
        running: '运行中',
        stopped: '已停止',
        sleeping: '休眠',
        zombie: '僵尸进程'
      }
      return statusMap[status] || '未知'
    },
    
    /**
     * 过滤进程
     */
    filterProcesses() {
      if (!this.processSearchQuery) {
        this.filteredProcesses = [...this.processes]
      } else {
        const query = this.processSearchQuery.toLowerCase()
        this.filteredProcesses = this.processes.filter(process =>
          process.name.toLowerCase().includes(query) ||
          process.pid.toString().includes(query)
        )
      }
    },
    
    /**
     * 刷新进程列表
     */
    async refreshProcesses() {
      this.isRefreshingProcesses = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('Processes refreshed')
      } finally {
        this.isRefreshingProcesses = false
      }
    },
    
    /**
     * 重启进程
     */
    restartProcess(process) {
      console.log(`Restarting process: ${process.name} (PID: ${process.pid})`)
      // 这里可以实现具体的重启逻辑
    },
    
    /**
     * 停止进程
     */
    stopProcess(process) {
      console.log(`Stopping process: ${process.name} (PID: ${process.pid})`)
      // 这里可以实现具体的停止逻辑
    },
    
    /**
     * 添加服务器
     */
    addServer() {
      console.log('Adding new server')
      // 这里可以打开添加服务器的弹窗
    },
    
    /**
     * 打开设置
     */
    openSettings() {
      console.log('Opening infrastructure settings')
      // 这里可以打开设置弹窗
    },
    
    /**
     * 初始化图表
     */
    initCharts() {
      // 这里可以使用Chart.js或其他图表库初始化图表
      console.log('Initializing performance charts')
    }
  },
  mounted() {
    // 初始化过滤的进程列表
    this.filterProcesses()
    // 初始化图表
    this.initCharts()
  },
  watch: {
    timeRange() {
      // 时间范围变化时重新加载数据
      console.log(`Time range changed to: ${this.timeRange}`)
      this.initCharts()
    }
  }
}
</script>

<style scoped>
/* 基础设施监控容器 */
.infrastructure-monitoring {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 监控区块样式 */
.monitoring-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 200px;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.btn-icon {
  padding: 6px 8px;
  border: none;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  color: #6c757d;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #e9ecef;
  color: #495057;
}

/* 服务器网格样式 */
.server-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.server-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  border-left: 4px solid #28a745;
}

.server-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.server-card.warning {
  border-left-color: #ffc107;
}

.server-card.critical {
  border-left-color: #dc3545;
}

.server-card.offline {
  border-left-color: #6c757d;
}

.server-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.server-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 16px;
}

.server-ip {
  color: #6c757d;
  font-size: 14px;
  font-family: monospace;
}

.server-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #28a745;
}

.status-indicator.warning {
  background: #ffc107;
}

.status-indicator.critical {
  background: #dc3545;
}

.status-indicator.offline {
  background: #6c757d;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: #495057;
}

/* 服务器指标样式 */
.server-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-label {
  width: 40px;
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.metric-bar {
  flex: 1;
  height: 6px;
  background: #e9ecef;
  border-radius: 3px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: #28a745;
  transition: width 0.3s ease;
}

.metric-fill.warning {
  background: #ffc107;
}

.metric-fill.critical {
  background: #dc3545;
}

.metric-value {
  width: 35px;
  text-align: right;
  font-size: 12px;
  font-weight: 600;
  color: #495057;
}

/* 图表网格样式 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.chart-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  background: white;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-header h4 {
  margin: 0;
  font-size: 14px;
  color: #2c3e50;
}

.current-value {
  font-size: 16px;
  font-weight: 600;
  color: #3498db;
}

.chart-content {
  height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 4px;
  color: #6c757d;
}

.chart-content canvas {
  max-width: 100%;
  max-height: 100%;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
}

.monitoring-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.monitoring-table th,
.monitoring-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.monitoring-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 12px;
  text-transform: uppercase;
}

.monitoring-table tr:hover {
  background: #f8f9fa;
}

.process-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.process-info i {
  color: #6c757d;
  width: 16px;
}

.metric-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.metric-badge.normal {
  background: #d4edda;
  color: #155724;
}

.metric-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.metric-badge.critical {
  background: #f8d7da;
  color: #721c24;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.running {
  background: #d4edda;
  color: #155724;
}

.status-badge.stopped {
  background: #f8d7da;
  color: #721c24;
}

.status-badge.sleeping {
  background: #fff3cd;
  color: #856404;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .server-grid {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
  
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}

@media (max-width: 768px) {
  .monitoring-section {
    padding: 15px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .section-actions {
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
  
  .server-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .server-header {
    flex-direction: column;
    gap: 10px;
  }
  
  .metric {
    flex-direction: column;
    align-items: stretch;
    gap: 5px;
  }
  
  .metric-label {
    width: auto;
  }
  
  .metric-value {
    width: auto;
    text-align: left;
  }
}

@media (max-width: 480px) {
  .infrastructure-monitoring {
    gap: 20px;
  }
  
  .monitoring-section {
    padding: 12px;
  }
  
  .section-header h3 {
    font-size: 16px;
  }
  
  .chart-content {
    height: 120px;
  }
}
</style>