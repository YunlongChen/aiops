<!--
  数据库监控组件
  功能：提供数据库实例监控、查询性能分析和连接池监控
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="database-monitoring">
    <!-- 数据库实例概览 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>数据库实例概览</h3>
        <div class="section-actions">
          <select v-model="selectedDatabase" class="db-selector">
            <option value="all">所有数据库</option>
            <option value="mysql">MySQL</option>
            <option value="postgresql">PostgreSQL</option>
            <option value="redis">Redis</option>
            <option value="mongodb">MongoDB</option>
          </select>
          <button class="btn-icon" @click="refreshDatabases" title="刷新">
            <i class="fas fa-sync-alt" :class="{ spinning: isRefreshingDatabases }"></i>
          </button>
        </div>
      </div>

      <div class="databases-grid">
        <div 
          v-for="database in filteredDatabases" 
          :key="database.id"
          :class="['database-card', database.status]"
        >
          <div class="database-header">
            <div class="database-info">
              <div class="db-name-row">
                <i :class="database.icon"></i>
                <h4>{{ database.name }}</h4>
                <span class="db-type">{{ database.type }}</span>
              </div>
              <span class="db-host">{{ database.host }}:{{ database.port }}</span>
            </div>
            <div class="database-status">
              <span :class="['status-indicator', database.status]"></span>
              <span class="status-text">{{ getStatusText(database.status) }}</span>
            </div>
          </div>
          
          <div class="database-metrics">
            <div class="metric-grid">
              <div class="metric-item">
                <span class="metric-label">连接数</span>
                <span class="metric-value">{{ database.connections }}/{{ database.maxConnections }}</span>
                <div class="metric-bar">
                  <div 
                    :class="['metric-fill', getConnectionLevel(database.connections, database.maxConnections)]" 
                    :style="{ width: (database.connections / database.maxConnections) * 100 + '%' }"
                  ></div>
                </div>
              </div>
              <div class="metric-item">
                <span class="metric-label">QPS</span>
                <span class="metric-value">{{ database.qps }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">响应时间</span>
                <span :class="['metric-value', getResponseTimeLevel(database.responseTime)]">
                  {{ database.responseTime }}ms
                </span>
              </div>
              <div class="metric-item">
                <span class="metric-label">存储使用</span>
                <span class="metric-value">{{ database.storageUsed }}/{{ database.storageTotal }}</span>
                <div class="metric-bar">
                  <div 
                    :class="['metric-fill', getStorageLevel(database.storageUsed, database.storageTotal)]" 
                    :style="{ width: getStoragePercentage(database.storageUsed, database.storageTotal) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="database-actions">
            <button class="btn-small" @click="viewDatabaseDetails(database)">
              详情
            </button>
            <button class="btn-small" @click="viewSlowQueries(database)">
              慢查询
            </button>
            <button class="btn-small" @click="optimizeDatabase(database)">
              优化
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 查询性能分析 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>查询性能分析</h3>
        <div class="section-actions">
          <select v-model="selectedQueryDatabase" class="db-selector">
            <option value="">选择数据库</option>
            <option v-for="db in databases" :key="db.id" :value="db.id">
              {{ db.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="query-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ queryStats.avgResponseTime }}ms</div>
            <div class="stat-label">平均响应时间</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-search"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ queryStats.totalQueries }}</div>
            <div class="stat-label">总查询数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ queryStats.slowQueries }}</div>
            <div class="stat-label">慢查询</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-times-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ queryStats.failedQueries }}</div>
            <div class="stat-label">失败查询</div>
          </div>
        </div>
      </div>

      <div class="query-charts">
        <div class="chart-card">
          <div class="chart-header">
            <h4>查询响应时间趋势</h4>
          </div>
          <div class="chart-content">
            <canvas ref="queryResponseChart" id="query-response-chart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h4>查询类型分布</h4>
          </div>
          <div class="chart-content">
            <canvas ref="queryTypeChart" id="query-type-chart"></canvas>
          </div>
        </div>
      </div>

      <!-- 慢查询列表 -->
      <div class="slow-queries-section">
        <div class="subsection-header">
          <h4>慢查询列表</h4>
          <div class="subsection-actions">
            <input
              type="text"
              v-model="slowQuerySearch"
              @input="filterSlowQueries"
              placeholder="搜索查询..."
              class="search-input"
            />
          </div>
        </div>

        <div class="table-container">
          <table class="monitoring-table">
            <thead>
              <tr>
                <th>查询语句</th>
                <th>数据库</th>
                <th>执行时间</th>
                <th>执行次数</th>
                <th>平均时间</th>
                <th>最后执行</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="query in filteredSlowQueries" :key="query.id">
                <td>
                  <div class="query-text" :title="query.fullQuery">
                    {{ truncateQuery(query.query) }}
                  </div>
                </td>
                <td>{{ query.database }}</td>
                <td>
                  <span :class="['execution-time', getExecutionTimeLevel(query.executionTime)]">
                    {{ query.executionTime }}ms
                  </span>
                </td>
                <td>{{ query.executionCount }}</td>
                <td>{{ query.avgTime }}ms</td>
                <td>{{ query.lastExecution }}</td>
                <td>
                  <button class="btn-icon" @click="explainQuery(query)" title="执行计划">
                    <i class="fas fa-info-circle"></i>
                  </button>
                  <button class="btn-icon" @click="optimizeQuery(query)" title="优化建议">
                    <i class="fas fa-magic"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 连接池监控 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>连接池监控</h3>
      </div>

      <div class="connection-pools">
        <div 
          v-for="pool in connectionPools" 
          :key="pool.id"
          class="pool-card"
        >
          <div class="pool-header">
            <div class="pool-info">
              <h4>{{ pool.name }}</h4>
              <span class="pool-type">{{ pool.type }}</span>
            </div>
            <div class="pool-status">
              <span :class="['status-indicator', pool.status]"></span>
              <span class="status-text">{{ getStatusText(pool.status) }}</span>
            </div>
          </div>

          <div class="pool-metrics">
            <div class="pool-chart">
              <div class="chart-title">连接使用情况</div>
              <div class="connection-chart">
                <div class="connection-bar">
                  <div 
                    class="connection-active" 
                    :style="{ width: (pool.activeConnections / pool.maxConnections) * 100 + '%' }"
                  ></div>
                  <div 
                    class="connection-idle" 
                    :style="{ 
                      width: (pool.idleConnections / pool.maxConnections) * 100 + '%',
                      left: (pool.activeConnections / pool.maxConnections) * 100 + '%'
                    }"
                  ></div>
                </div>
                <div class="connection-legend">
                  <div class="legend-item">
                    <span class="legend-color active"></span>
                    <span class="legend-text">活跃: {{ pool.activeConnections }}</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color idle"></span>
                    <span class="legend-text">空闲: {{ pool.idleConnections }}</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-text">最大: {{ pool.maxConnections }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="pool-stats">
              <div class="stat-row">
                <div class="stat-item">
                  <span class="stat-label">等待连接</span>
                  <span class="stat-value">{{ pool.waitingConnections }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均等待时间</span>
                  <span class="stat-value">{{ pool.avgWaitTime }}ms</span>
                </div>
              </div>
              <div class="stat-row">
                <div class="stat-item">
                  <span class="stat-label">连接超时</span>
                  <span class="stat-value">{{ pool.timeouts }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">连接错误</span>
                  <span class="stat-value">{{ pool.errors }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 数据库监控组件
 * 提供数据库实例、查询性能和连接池监控功能
 */
export default {
  name: 'DatabaseMonitoring',
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
      // 选择器和搜索
      selectedDatabase: 'all',
      selectedQueryDatabase: '',
      slowQuerySearch: '',
      isRefreshingDatabases: false,
      
      // 数据库实例数据
      databases: [
        {
          id: 1,
          name: 'user-db-master',
          type: 'MySQL',
          icon: 'fas fa-database',
          host: '192.168.1.100',
          port: 3306,
          status: 'healthy',
          connections: 45,
          maxConnections: 100,
          qps: 1250,
          responseTime: 12,
          storageUsed: '45GB',
          storageTotal: '100GB'
        },
        {
          id: 2,
          name: 'order-db-slave',
          type: 'MySQL',
          icon: 'fas fa-database',
          host: '192.168.1.101',
          port: 3306,
          status: 'warning',
          connections: 78,
          maxConnections: 100,
          qps: 890,
          responseTime: 45,
          storageUsed: '82GB',
          storageTotal: '100GB'
        },
        {
          id: 3,
          name: 'cache-redis',
          type: 'Redis',
          icon: 'fas fa-memory',
          host: '192.168.1.102',
          port: 6379,
          status: 'healthy',
          connections: 25,
          maxConnections: 50,
          qps: 5600,
          responseTime: 2,
          storageUsed: '2.5GB',
          storageTotal: '8GB'
        },
        {
          id: 4,
          name: 'analytics-mongo',
          type: 'MongoDB',
          icon: 'fas fa-leaf',
          host: '192.168.1.103',
          port: 27017,
          status: 'critical',
          connections: 48,
          maxConnections: 50,
          qps: 320,
          responseTime: 150,
          storageUsed: '180GB',
          storageTotal: '200GB'
        }
      ],
      
      // 查询统计数据
      queryStats: {
        avgResponseTime: 28,
        totalQueries: 125680,
        slowQueries: 45,
        failedQueries: 12
      },
      
      // 慢查询数据
      slowQueries: [
        {
          id: 1,
          query: 'SELECT * FROM orders o JOIN users u ON o.user_id = u.id WHERE o.created_at > ?',
          fullQuery: 'SELECT * FROM orders o JOIN users u ON o.user_id = u.id WHERE o.created_at > ? AND o.status = "pending" ORDER BY o.created_at DESC',
          database: 'order-db',
          executionTime: 2500,
          executionCount: 156,
          avgTime: 2200,
          lastExecution: '2分钟前'
        },
        {
          id: 2,
          query: 'UPDATE user_stats SET login_count = login_count + 1 WHERE user_id = ?',
          fullQuery: 'UPDATE user_stats SET login_count = login_count + 1, last_login = NOW() WHERE user_id = ?',
          database: 'user-db',
          executionTime: 1800,
          executionCount: 89,
          avgTime: 1650,
          lastExecution: '5分钟前'
        },
        {
          id: 3,
          query: 'SELECT COUNT(*) FROM analytics_events WHERE event_date BETWEEN ? AND ?',
          fullQuery: 'SELECT COUNT(*) FROM analytics_events WHERE event_date BETWEEN ? AND ? AND event_type IN ("click", "view", "purchase")',
          database: 'analytics-db',
          executionTime: 3200,
          executionCount: 23,
          avgTime: 2900,
          lastExecution: '10分钟前'
        }
      ],
      
      // 连接池数据
      connectionPools: [
        {
          id: 1,
          name: 'user-db-pool',
          type: 'MySQL',
          status: 'healthy',
          activeConnections: 35,
          idleConnections: 15,
          maxConnections: 100,
          waitingConnections: 2,
          avgWaitTime: 45,
          timeouts: 0,
          errors: 1
        },
        {
          id: 2,
          name: 'order-db-pool',
          type: 'MySQL',
          status: 'warning',
          activeConnections: 68,
          idleConnections: 12,
          maxConnections: 100,
          waitingConnections: 8,
          avgWaitTime: 120,
          timeouts: 3,
          errors: 2
        },
        {
          id: 3,
          name: 'redis-pool',
          type: 'Redis',
          status: 'healthy',
          activeConnections: 18,
          idleConnections: 7,
          maxConnections: 50,
          waitingConnections: 0,
          avgWaitTime: 5,
          timeouts: 0,
          errors: 0
        }
      ],
      
      // 过滤后的数据
      filteredDatabases: [],
      filteredSlowQueries: []
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
        error: '错误',
        offline: '离线'
      }
      return statusMap[status] || '未知'
    },
    
    /**
     * 获取连接级别
     */
    getConnectionLevel(current, max) {
      const percentage = (current / max) * 100
      if (percentage >= 90) return 'critical'
      if (percentage >= 70) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取响应时间级别
     */
    getResponseTimeLevel(time) {
      if (time >= 100) return 'critical'
      if (time >= 50) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取存储级别
     */
    getStorageLevel(used, total) {
      const percentage = this.getStoragePercentage(used, total)
      if (percentage >= 90) return 'critical'
      if (percentage >= 70) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取存储使用百分比
     */
    getStoragePercentage(used, total) {
      const usedNum = parseFloat(used.replace('GB', ''))
      const totalNum = parseFloat(total.replace('GB', ''))
      return (usedNum / totalNum) * 100
    },
    
    /**
     * 获取执行时间级别
     */
    getExecutionTimeLevel(time) {
      if (time >= 2000) return 'critical'
      if (time >= 1000) return 'warning'
      return 'normal'
    },
    
    /**
     * 过滤数据库
     */
    filterDatabases() {
      if (this.selectedDatabase === 'all') {
        this.filteredDatabases = [...this.databases]
      } else {
        this.filteredDatabases = this.databases.filter(db =>
          db.type.toLowerCase() === this.selectedDatabase.toLowerCase()
        )
      }
    },
    
    /**
     * 过滤慢查询
     */
    filterSlowQueries() {
      if (!this.slowQuerySearch) {
        this.filteredSlowQueries = [...this.slowQueries]
      } else {
        const query = this.slowQuerySearch.toLowerCase()
        this.filteredSlowQueries = this.slowQueries.filter(slowQuery =>
          slowQuery.query.toLowerCase().includes(query) ||
          slowQuery.database.toLowerCase().includes(query)
        )
      }
    },
    
    /**
     * 截断查询语句
     */
    truncateQuery(query) {
      return query.length > 60 ? query.substring(0, 60) + '...' : query
    },
    
    /**
     * 刷新数据库
     */
    async refreshDatabases() {
      this.isRefreshingDatabases = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('Databases refreshed')
      } finally {
        this.isRefreshingDatabases = false
      }
    },
    
    /**
     * 查看数据库详情
     */
    viewDatabaseDetails(database) {
      console.log(`Viewing details for database: ${database.name}`)
      // 这里可以打开数据库详情弹窗
    },
    
    /**
     * 查看慢查询
     */
    viewSlowQueries(database) {
      console.log(`Viewing slow queries for database: ${database.name}`)
      // 这里可以打开慢查询详情
    },
    
    /**
     * 优化数据库
     */
    optimizeDatabase(database) {
      console.log(`Optimizing database: ${database.name}`)
      // 这里可以实现数据库优化逻辑
    },
    
    /**
     * 解释查询
     */
    explainQuery(query) {
      console.log(`Explaining query: ${query.query}`)
      // 这里可以显示查询执行计划
    },
    
    /**
     * 优化查询
     */
    optimizeQuery(query) {
      console.log(`Optimizing query: ${query.query}`)
      // 这里可以提供查询优化建议
    },
    
    /**
     * 初始化图表
     */
    initCharts() {
      // 这里可以使用Chart.js或其他图表库初始化图表
      console.log('Initializing database monitoring charts')
    }
  },
  mounted() {
    // 初始化过滤数据
    this.filterDatabases()
    this.filterSlowQueries()
    // 初始化图表
    this.initCharts()
  },
  watch: {
    selectedDatabase() {
      this.filterDatabases()
    },
    timeRange() {
      // 时间范围变化时重新加载数据
      console.log(`Time range changed to: ${this.timeRange}`)
      this.initCharts()
    }
  }
}
</script>

<style scoped>
/* 数据库监控容器 */
.database-monitoring {
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

.db-selector {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
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

.btn-small {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #495057;
  transition: all 0.2s ease;
}

.btn-small:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

/* 数据库网格样式 */
.databases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.database-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  border-left: 4px solid #28a745;
}

.database-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.database-card.warning {
  border-left-color: #ffc107;
}

.database-card.critical {
  border-left-color: #dc3545;
}

.database-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.db-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}

.db-name-row i {
  color: #6c757d;
  width: 16px;
}

.database-info h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.db-type {
  background: #3498db;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.db-host {
  color: #6c757d;
  font-size: 13px;
  font-family: monospace;
}

.database-status {
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

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: #495057;
}

/* 数据库指标样式 */
.database-metrics {
  margin-bottom: 15px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metric-label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.metric-value.warning {
  color: #f39c12;
}

.metric-value.critical {
  color: #e74c3c;
}

.metric-bar {
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
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

.database-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 查询统计样式 */
.query-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #3498db;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

/* 查询图表样式 */
.query-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
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

.chart-content {
  height: 200px;
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

/* 慢查询区块样式 */
.slow-queries-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.subsection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.subsection-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.subsection-actions {
  display: flex;
  gap: 10px;
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

.query-text {
  font-family: monospace;
  font-size: 12px;
  color: #2c3e50;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.execution-time.warning {
  color: #f39c12;
}

.execution-time.critical {
  color: #e74c3c;
}

/* 连接池样式 */
.connection-pools {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.pool-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  background: white;
}

.pool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.pool-info h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
  font-size: 16px;
}

.pool-type {
  background: #6c757d;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.pool-metrics {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 10px;
}

.connection-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.connection-bar {
  height: 20px;
  background: #e9ecef;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.connection-active {
  height: 100%;
  background: #3498db;
  position: absolute;
  left: 0;
  top: 0;
  transition: width 0.3s ease;
}

.connection-idle {
  height: 100%;
  background: #95a5a6;
  position: absolute;
  top: 0;
  transition: width 0.3s ease, left 0.3s ease;
}

.connection-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-color.active {
  background: #3498db;
}

.legend-color.idle {
  background: #95a5a6;
}

.legend-text {
  font-size: 12px;
  color: #6c757d;
}

.pool-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.stat-label {
  font-size: 11px;
  color: #6c757d;
  margin-bottom: 4px;
  text-align: center;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
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
  .databases-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
  
  .connection-pools {
    grid-template-columns: 1fr;
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
  
  .databases-grid {
    grid-template-columns: 1fr;
  }
  
  .query-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .query-charts {
    grid-template-columns: 1fr;
  }
  
  .metric-grid {
    grid-template-columns: 1fr;
  }
  
  .database-actions {
    justify-content: center;
  }
  
  .pool-metrics {
    grid-template-columns: 1fr;
  }
  
  .stat-row {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .database-monitoring {
    gap: 20px;
  }
  
  .monitoring-section {
    padding: 12px;
  }
  
  .section-header h3 {
    font-size: 16px;
  }
  
  .query-stats {
    grid-template-columns: 1fr;
  }
  
  .chart-content {
    height: 150px;
  }
  
  .stat-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>