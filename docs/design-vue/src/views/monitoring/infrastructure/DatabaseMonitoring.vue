<!--
  数据库监控页面
  监控数据库性能指标、连接状态、查询性能等
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="database-monitoring">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">数据库监控</h1>
        <p class="page-description">实时监控数据库性能指标和运行状态</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="refreshData">
          <i class="icon-refresh-cw"></i>
          刷新数据
        </button>
        <button class="btn btn-outline" @click="exportReport">
          <i class="icon-download"></i>
          导出报告
        </button>
        <button class="btn btn-primary" @click="runHealthCheck">
          <i class="icon-activity"></i>
          健康检查
        </button>
      </div>
    </div>

    <!-- 数据库概览 -->
    <div class="overview-section">
      <div class="overview-cards">
        <div class="overview-card">
          <div class="card-icon">
            <i class="icon-database"></i>
          </div>
          <div class="card-content">
            <h3 class="card-title">数据库实例</h3>
            <p class="card-value">{{ overview.totalInstances }}</p>
            <p class="card-description">{{ overview.activeInstances }} 个在线</p>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">
            <i class="icon-users"></i>
          </div>
          <div class="card-content">
            <h3 class="card-title">活跃连接</h3>
            <p class="card-value">{{ overview.activeConnections }}</p>
            <p class="card-description">最大 {{ overview.maxConnections }}</p>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">
            <i class="icon-zap"></i>
          </div>
          <div class="card-content">
            <h3 class="card-title">查询/秒</h3>
            <p class="card-value">{{ overview.queriesPerSecond }}</p>
            <p class="card-description">平均响应时间 {{ overview.avgResponseTime }}ms</p>
          </div>
        </div>
        
        <div class="overview-card">
          <div class="card-icon">
            <i class="icon-hard-drive"></i>
          </div>
          <div class="card-content">
            <h3 class="card-title">存储使用</h3>
            <p class="card-value">{{ overview.storageUsed }}GB</p>
            <p class="card-description">总容量 {{ overview.totalStorage }}GB</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 数据库实例列表 -->
    <div class="instances-section">
      <div class="section-header">
        <h3 class="section-title">数据库实例</h3>
        <div class="section-actions">
          <div class="filter-group">
            <select v-model="selectedType" class="filter-select">
              <option value="">所有类型</option>
              <option value="mysql">MySQL</option>
              <option value="postgresql">PostgreSQL</option>
              <option value="mongodb">MongoDB</option>
              <option value="redis">Redis</option>
            </select>
            <select v-model="selectedStatus" class="filter-select">
              <option value="">所有状态</option>
              <option value="online">在线</option>
              <option value="offline">离线</option>
              <option value="warning">警告</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="instances-grid">
        <div 
          v-for="instance in filteredInstances" 
          :key="instance.id"
          class="instance-card"
          :class="instance.status"
        >
          <div class="instance-header">
            <div class="instance-info">
              <h4 class="instance-name">{{ instance.name }}</h4>
              <p class="instance-type">{{ instance.type }} {{ instance.version }}</p>
            </div>
            <div class="instance-status">
              <span class="status-badge" :class="instance.status">
                {{ getStatusText(instance.status) }}
              </span>
            </div>
          </div>
          
          <div class="instance-metrics">
            <div class="metric-row">
              <div class="metric">
                <span class="metric-label">CPU</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{ width: instance.cpu + '%' }"></div>
                </div>
                <span class="metric-value">{{ instance.cpu }}%</span>
              </div>
            </div>
            
            <div class="metric-row">
              <div class="metric">
                <span class="metric-label">内存</span>
                <div class="metric-bar">
                  <div class="metric-fill" :style="{ width: instance.memory + '%' }"></div>
                </div>
                <span class="metric-value">{{ instance.memory }}%</span>
              </div>
            </div>
            
            <div class="metric-row">
              <div class="metric">
                <span class="metric-label">连接数</span>
                <span class="metric-value">{{ instance.connections }}/{{ instance.maxConnections }}</span>
              </div>
              <div class="metric">
                <span class="metric-label">QPS</span>
                <span class="metric-value">{{ instance.qps }}</span>
              </div>
            </div>
          </div>
          
          <div class="instance-actions">
            <button class="btn btn-sm btn-outline" @click="viewDetails(instance.id)">
              详情
            </button>
            <button class="btn btn-sm btn-outline" @click="viewLogs(instance.id)">
              日志
            </button>
            <button class="btn btn-sm btn-primary" @click="optimizeInstance(instance.id)">
              优化
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 性能图表 -->
    <div class="charts-section">
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">查询性能趋势</h3>
          <div class="card-actions">
            <select v-model="performanceTimeRange" class="time-range-select">
              <option value="1h">最近1小时</option>
              <option value="6h">最近6小时</option>
              <option value="24h">最近24小时</option>
              <option value="7d">最近7天</option>
            </select>
          </div>
        </div>
        <div class="chart-container">
          <div class="chart-placeholder">
            <i class="icon-trending-up"></i>
            <p>查询性能趋势图表</p>
            <small>QPS、响应时间、错误率变化</small>
          </div>
        </div>
      </div>
      
      <div class="chart-card">
        <div class="card-header">
          <h3 class="card-title">资源使用情况</h3>
        </div>
        <div class="chart-container">
          <div class="chart-placeholder">
            <i class="icon-pie-chart"></i>
            <p>资源使用分布</p>
            <small>CPU、内存、存储使用情况</small>
          </div>
        </div>
      </div>
    </div>

    <!-- 慢查询分析 -->
    <div class="slow-queries-section">
      <div class="section-header">
        <h3 class="section-title">慢查询分析</h3>
        <div class="section-actions">
          <input 
            v-model="querySearch" 
            type="text" 
            placeholder="搜索查询..." 
            class="search-input"
          >
        </div>
      </div>
      
      <div class="slow-queries-table">
        <table class="table">
          <thead>
            <tr>
              <th>数据库</th>
              <th>查询语句</th>
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
                <div class="db-info">
                  <span class="db-name">{{ query.database }}</span>
                  <span class="db-type">{{ query.type }}</span>
                </div>
              </td>
              <td>
                <div class="query-text" :title="query.sql">
                  {{ truncateQuery(query.sql) }}
                </div>
              </td>
              <td>
                <span class="execution-time" :class="getTimeClass(query.executionTime)">
                  {{ query.executionTime }}ms
                </span>
              </td>
              <td>{{ query.count }}</td>
              <td>{{ query.avgTime }}ms</td>
              <td>{{ formatTime(query.lastExecution) }}</td>
              <td>
                <div class="table-actions">
                  <button class="btn btn-sm btn-outline" @click="explainQuery(query.id)">
                    分析
                  </button>
                  <button class="btn btn-sm btn-outline" @click="optimizeQuery(query.id)">
                    优化
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 数据库详情弹窗 -->
    <div v-if="showDetailsModal" class="modal-overlay" @click="closeDetailsModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">数据库详情 - {{ selectedInstance?.name }}</h3>
          <button class="modal-close" @click="closeDetailsModal">
            <i class="icon-x"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="tabs">
            <button 
              v-for="tab in detailTabs" 
              :key="tab.key"
              class="tab-button"
              :class="{ active: activeDetailTab === tab.key }"
              @click="activeDetailTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
          
          <div class="tab-content">
            <!-- 基本信息 -->
            <div v-if="activeDetailTab === 'info'" class="tab-panel">
              <div class="info-grid">
                <div class="info-item">
                  <label>实例名称</label>
                  <span>{{ selectedInstance?.name }}</span>
                </div>
                <div class="info-item">
                  <label>数据库类型</label>
                  <span>{{ selectedInstance?.type }} {{ selectedInstance?.version }}</span>
                </div>
                <div class="info-item">
                  <label>主机地址</label>
                  <span>{{ selectedInstance?.host }}:{{ selectedInstance?.port }}</span>
                </div>
                <div class="info-item">
                  <label>运行时间</label>
                  <span>{{ selectedInstance?.uptime }}</span>
                </div>
                <div class="info-item">
                  <label>数据目录</label>
                  <span>{{ selectedInstance?.dataDir }}</span>
                </div>
                <div class="info-item">
                  <label>配置文件</label>
                  <span>{{ selectedInstance?.configFile }}</span>
                </div>
              </div>
            </div>
            
            <!-- 性能指标 -->
            <div v-if="activeDetailTab === 'metrics'" class="tab-panel">
              <div class="metrics-grid">
                <div class="metric-card">
                  <h4>连接统计</h4>
                  <div class="metric-list">
                    <div class="metric-item">
                      <span>当前连接</span>
                      <span>{{ selectedInstance?.connections }}</span>
                    </div>
                    <div class="metric-item">
                      <span>最大连接</span>
                      <span>{{ selectedInstance?.maxConnections }}</span>
                    </div>
                    <div class="metric-item">
                      <span>连接使用率</span>
                      <span>{{ Math.round((selectedInstance?.connections / selectedInstance?.maxConnections) * 100) }}%</span>
                    </div>
                  </div>
                </div>
                
                <div class="metric-card">
                  <h4>查询统计</h4>
                  <div class="metric-list">
                    <div class="metric-item">
                      <span>每秒查询</span>
                      <span>{{ selectedInstance?.qps }}</span>
                    </div>
                    <div class="metric-item">
                      <span>慢查询数</span>
                      <span>{{ selectedInstance?.slowQueries }}</span>
                    </div>
                    <div class="metric-item">
                      <span>平均响应时间</span>
                      <span>{{ selectedInstance?.avgResponseTime }}ms</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 配置信息 -->
            <div v-if="activeDetailTab === 'config'" class="tab-panel">
              <div class="config-list">
                <div v-for="config in selectedInstance?.configs" :key="config.key" class="config-item">
                  <div class="config-key">{{ config.key }}</div>
                  <div class="config-value">{{ config.value }}</div>
                  <div class="config-description">{{ config.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 数据库监控页面
 * 监控数据库性能指标、连接状态、查询性能等
 */
import { ref, computed, onMounted } from 'vue'

// 响应式数据
const selectedType = ref('')
const selectedStatus = ref('')
const querySearch = ref('')
const performanceTimeRange = ref('24h')
const showDetailsModal = ref(false)
const selectedInstance = ref(null)
const activeDetailTab = ref('info')

// 概览数据
const overview = ref({
  totalInstances: 8,
  activeInstances: 7,
  activeConnections: 245,
  maxConnections: 1000,
  queriesPerSecond: 1250,
  avgResponseTime: 45,
  storageUsed: 128,
  totalStorage: 500
})

// 数据库实例数据
const instances = ref([
  {
    id: 1,
    name: 'prod-mysql-01',
    type: 'MySQL',
    version: '8.0.32',
    status: 'online',
    host: '192.168.1.10',
    port: 3306,
    cpu: 65,
    memory: 78,
    connections: 45,
    maxConnections: 200,
    qps: 320,
    slowQueries: 12,
    avgResponseTime: 35,
    uptime: '15天 8小时',
    dataDir: '/var/lib/mysql',
    configFile: '/etc/mysql/my.cnf',
    configs: [
      { key: 'max_connections', value: '200', description: '最大连接数' },
      { key: 'innodb_buffer_pool_size', value: '1G', description: 'InnoDB缓冲池大小' },
      { key: 'query_cache_size', value: '64M', description: '查询缓存大小' }
    ]
  },
  {
    id: 2,
    name: 'prod-postgres-01',
    type: 'PostgreSQL',
    version: '14.7',
    status: 'online',
    host: '192.168.1.11',
    port: 5432,
    cpu: 42,
    memory: 55,
    connections: 28,
    maxConnections: 100,
    qps: 180,
    slowQueries: 3,
    avgResponseTime: 28,
    uptime: '22天 14小时',
    dataDir: '/var/lib/postgresql/14/main',
    configFile: '/etc/postgresql/14/main/postgresql.conf',
    configs: [
      { key: 'max_connections', value: '100', description: '最大连接数' },
      { key: 'shared_buffers', value: '256MB', description: '共享缓冲区' },
      { key: 'work_mem', value: '4MB', description: '工作内存' }
    ]
  },
  {
    id: 3,
    name: 'prod-mongodb-01',
    type: 'MongoDB',
    version: '6.0.4',
    status: 'warning',
    host: '192.168.1.12',
    port: 27017,
    cpu: 85,
    memory: 92,
    connections: 75,
    maxConnections: 100,
    qps: 450,
    slowQueries: 28,
    avgResponseTime: 85,
    uptime: '8天 3小时',
    dataDir: '/var/lib/mongodb',
    configFile: '/etc/mongod.conf',
    configs: [
      { key: 'maxIncomingConnections', value: '100', description: '最大连接数' },
      { key: 'cacheSizeGB', value: '2', description: '缓存大小' },
      { key: 'slowOpThresholdMs', value: '100', description: '慢操作阈值' }
    ]
  },
  {
    id: 4,
    name: 'prod-redis-01',
    type: 'Redis',
    version: '7.0.8',
    status: 'online',
    host: '192.168.1.13',
    port: 6379,
    cpu: 25,
    memory: 35,
    connections: 15,
    maxConnections: 50,
    qps: 2800,
    slowQueries: 0,
    avgResponseTime: 2,
    uptime: '45天 12小时',
    dataDir: '/var/lib/redis',
    configFile: '/etc/redis/redis.conf',
    configs: [
      { key: 'maxclients', value: '50', description: '最大客户端连接数' },
      { key: 'maxmemory', value: '2gb', description: '最大内存使用' },
      { key: 'timeout', value: '300', description: '连接超时时间' }
    ]
  }
])

// 慢查询数据
const slowQueries = ref([
  {
    id: 1,
    database: 'prod-mysql-01',
    type: 'MySQL',
    sql: 'SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE o.created_at > "2024-01-01" ORDER BY o.created_at DESC',
    executionTime: 2500,
    count: 45,
    avgTime: 2200,
    lastExecution: new Date(Date.now() - 10 * 60 * 1000)
  },
  {
    id: 2,
    database: 'prod-postgres-01',
    type: 'PostgreSQL',
    sql: 'SELECT COUNT(*) FROM products p LEFT JOIN categories c ON p.category_id = c.id GROUP BY c.name',
    executionTime: 1800,
    count: 23,
    avgTime: 1650,
    lastExecution: new Date(Date.now() - 25 * 60 * 1000)
  },
  {
    id: 3,
    database: 'prod-mongodb-01',
    type: 'MongoDB',
    sql: 'db.logs.find({timestamp: {$gte: ISODate("2024-01-01")}}).sort({timestamp: -1}).limit(1000)',
    executionTime: 3200,
    count: 67,
    avgTime: 2800,
    lastExecution: new Date(Date.now() - 5 * 60 * 1000)
  }
])

// 详情标签页
const detailTabs = ref([
  { key: 'info', label: '基本信息' },
  { key: 'metrics', label: '性能指标' },
  { key: 'config', label: '配置信息' }
])

// 计算属性
/**
 * 过滤后的数据库实例
 */
const filteredInstances = computed(() => {
  return instances.value.filter(instance => {
    const typeMatch = !selectedType.value || instance.type.toLowerCase().includes(selectedType.value.toLowerCase())
    const statusMatch = !selectedStatus.value || instance.status === selectedStatus.value
    return typeMatch && statusMatch
  })
})

/**
 * 过滤后的慢查询
 */
const filteredSlowQueries = computed(() => {
  return slowQueries.value.filter(query => {
    const searchMatch = !querySearch.value || 
      query.sql.toLowerCase().includes(querySearch.value.toLowerCase()) ||
      query.database.toLowerCase().includes(querySearch.value.toLowerCase())
    return searchMatch
  })
})

/**
 * 获取状态文本
 * @param {string} status - 状态值
 * @returns {string} 状态文本
 */
const getStatusText = (status) => {
  const statusMap = {
    online: '在线',
    offline: '离线',
    warning: '警告',
    error: '错误'
  }
  return statusMap[status] || '未知'
}

/**
 * 获取执行时间样式类
 * @param {number} time - 执行时间
 * @returns {string} 样式类名
 */
const getTimeClass = (time) => {
  if (time > 3000) return 'critical'
  if (time > 1000) return 'warning'
  return 'normal'
}

/**
 * 截断查询语句
 * @param {string} sql - SQL语句
 * @returns {string} 截断后的SQL
 */
const truncateQuery = (sql) => {
  return sql.length > 80 ? sql.substring(0, 80) + '...' : sql
}

/**
 * 格式化时间
 * @param {Date} timestamp - 时间戳
 * @returns {string} 格式化后的时间
 */
const formatTime = (timestamp) => {
  const now = new Date()
  const diff = now - timestamp
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  
  const days = Math.floor(hours / 24)
  return `${days}天前`
}

/**
 * 刷新数据
 */
const refreshData = () => {
  console.log('刷新数据库监控数据')
  // 这里可以调用API刷新数据
}

/**
 * 导出报告
 */
const exportReport = () => {
  console.log('导出数据库监控报告')
  // 这里可以实现报告导出功能
}

/**
 * 运行健康检查
 */
const runHealthCheck = () => {
  console.log('运行数据库健康检查')
  // 这里可以实现健康检查功能
}

/**
 * 查看实例详情
 * @param {number} instanceId - 实例ID
 */
const viewDetails = (instanceId) => {
  selectedInstance.value = instances.value.find(instance => instance.id === instanceId)
  showDetailsModal.value = true
  activeDetailTab.value = 'info'
}

/**
 * 查看实例日志
 * @param {number} instanceId - 实例ID
 */
const viewLogs = (instanceId) => {
  console.log('查看实例日志:', instanceId)
  // 这里可以跳转到日志页面
}

/**
 * 优化实例
 * @param {number} instanceId - 实例ID
 */
const optimizeInstance = (instanceId) => {
  console.log('优化数据库实例:', instanceId)
  // 这里可以实现数据库优化功能
}

/**
 * 分析查询
 * @param {number} queryId - 查询ID
 */
const explainQuery = (queryId) => {
  console.log('分析查询:', queryId)
  // 这里可以实现查询分析功能
}

/**
 * 优化查询
 * @param {number} queryId - 查询ID
 */
const optimizeQuery = (queryId) => {
  console.log('优化查询:', queryId)
  // 这里可以实现查询优化功能
}

/**
 * 关闭详情弹窗
 */
const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedInstance.value = null
}

// 组件挂载时初始化数据
onMounted(() => {
  console.log('DatabaseMonitoring mounted')
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.database-monitoring {
  padding: $spacing-lg;
  max-width: 1400px;
  margin: 0 auto;
}

// 页面头部
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-xl;
  
  .header-content {
    .page-title {
      font-size: 28px;
      font-weight: 700;
      color: $text-color;
      margin: 0 0 $spacing-xs 0;
    }
    
    .page-description {
      color: $text-color-secondary;
      margin: 0;
    }
  }
  
  .header-actions {
    display: flex;
    gap: $spacing-sm;
  }
}

// 概览卡片
.overview-section {
  margin-bottom: $spacing-xl;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: $spacing-lg;
}

.overview-card {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  border: 1px solid $border-color-light;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
  
  .card-icon {
    width: 48px;
    height: 48px;
    border-radius: $border-radius-md;
    background: rgba($primary-color, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    
    i {
      font-size: 24px;
      color: $primary-color;
    }
  }
  
  .card-content {
    flex: 1;
    
    .card-title {
      font-size: 14px;
      color: $text-color-secondary;
      margin: 0 0 $spacing-xs 0;
      font-weight: 500;
    }
    
    .card-value {
      font-size: 24px;
      font-weight: 700;
      color: $text-color;
      margin: 0 0 $spacing-xs 0;
    }
    
    .card-description {
      font-size: 12px;
      color: $text-color-secondary;
      margin: 0;
    }
  }
}

// 实例列表
.instances-section {
  margin-bottom: $spacing-xl;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-lg;
  
  .section-title {
    font-size: 18px;
    font-weight: 600;
    color: $text-color;
    margin: 0;
  }
  
  .section-actions {
    .filter-group {
      display: flex;
      gap: $spacing-sm;
    }
    
    .filter-select {
      padding: $spacing-xs $spacing-sm;
      border: 1px solid $border-color-light;
      border-radius: $border-radius-sm;
      background: $white;
      font-size: 14px;
      min-width: 120px;
    }
  }
}

.instances-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: $spacing-lg;
}

.instance-card {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  border: 1px solid $border-color-light;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: $shadow-sm;
  }
  
  &.online {
    border-left: 4px solid $success-color;
  }
  
  &.warning {
    border-left: 4px solid $warning-color;
  }
  
  &.offline {
    border-left: 4px solid $error-color;
  }
  
  .instance-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: $spacing-md;
    
    .instance-info {
      .instance-name {
        font-size: 16px;
        font-weight: 600;
        color: $text-color;
        margin: 0 0 $spacing-xs 0;
      }
      
      .instance-type {
        font-size: 12px;
        color: $text-color-secondary;
        margin: 0;
      }
    }
  }
  
  .instance-metrics {
    margin-bottom: $spacing-md;
    
    .metric-row {
      margin-bottom: $spacing-sm;
      
      &:last-child {
        margin-bottom: 0;
        display: flex;
        gap: $spacing-lg;
      }
    }
    
    .metric {
      display: flex;
      align-items: center;
      gap: $spacing-sm;
      
      .metric-label {
        font-size: 12px;
        color: $text-color-secondary;
        min-width: 40px;
      }
      
      .metric-bar {
        flex: 1;
        height: 6px;
        background: $background-color-light;
        border-radius: 3px;
        overflow: hidden;
        
        .metric-fill {
          height: 100%;
          background: $primary-color;
          transition: width 0.3s ease;
        }
      }
      
      .metric-value {
        font-size: 12px;
        font-weight: 600;
        color: $text-color;
        min-width: 40px;
        text-align: right;
      }
    }
  }
  
  .instance-actions {
    display: flex;
    gap: $spacing-sm;
    
    .btn {
      flex: 1;
      font-size: 12px;
      padding: $spacing-xs $spacing-sm;
    }
  }
}

// 图表区域
.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.chart-card {
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  overflow: hidden;
  
  .card-header {
    padding: $spacing-lg;
    border-bottom: 1px solid $border-color-light;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: $text-color;
      margin: 0;
    }
  }
  
  .chart-container {
    padding: $spacing-lg;
    height: 300px;
    
    .chart-placeholder {
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: $text-color-secondary;
      
      i {
        font-size: 48px;
        margin-bottom: $spacing-md;
        opacity: 0.5;
      }
      
      p {
        font-size: 16px;
        margin: 0 0 $spacing-xs 0;
      }
      
      small {
        font-size: 12px;
        opacity: 0.7;
      }
    }
  }
}

.time-range-select {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color-light;
  border-radius: $border-radius-sm;
  background: $white;
  font-size: 12px;
}

// 慢查询分析
.slow-queries-section {
  margin-bottom: $spacing-xl;
  
  .section-actions {
    .search-input {
      padding: $spacing-xs $spacing-sm;
      border: 1px solid $border-color-light;
      border-radius: $border-radius-sm;
      font-size: 14px;
      width: 250px;
    }
  }
}

.slow-queries-table {
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  overflow: hidden;
  
  .table {
    width: 100%;
    border-collapse: collapse;
    
    th {
      background: $background-color-light;
      padding: $spacing-md;
      text-align: left;
      font-weight: 600;
      color: $text-color;
      border-bottom: 1px solid $border-color-light;
      font-size: 14px;
    }
    
    td {
      padding: $spacing-md;
      border-bottom: 1px solid $border-color-light;
      font-size: 13px;
      
      &:last-child {
        border-bottom: none;
      }
    }
    
    tr:last-child td {
      border-bottom: none;
    }
  }
  
  .db-info {
    .db-name {
      display: block;
      font-weight: 600;
      color: $text-color;
    }
    
    .db-type {
      font-size: 11px;
      color: $text-color-secondary;
    }
  }
  
  .query-text {
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: $text-color;
    max-width: 300px;
    word-break: break-all;
  }
  
  .execution-time {
    font-weight: 600;
    
    &.normal {
      color: $success-color;
    }
    
    &.warning {
      color: $warning-color;
    }
    
    &.critical {
      color: $error-color;
    }
  }
  
  .table-actions {
    display: flex;
    gap: $spacing-xs;
    
    .btn {
      font-size: 11px;
      padding: 4px 8px;
    }
  }
}

// 状态徽章
.status-badge {
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  font-size: 12px;
  font-weight: 500;
  
  &.online {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.warning {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.offline {
    background: rgba($error-color, 0.1);
    color: $error-color;
  }
}

// 弹窗样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: $white;
  border-radius: $border-radius-lg;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .modal-title {
    font-size: 18px;
    font-weight: 600;
    color: $text-color;
    margin: 0;
  }
  
  .modal-close {
    width: 32px;
    height: 32px;
    border: none;
    background: none;
    color: $text-color-secondary;
    cursor: pointer;
    border-radius: $border-radius-sm;
    
    &:hover {
      background: $background-color-light;
    }
  }
}

.modal-body {
  flex: 1;
  overflow-y: auto;
}

.tabs {
  display: flex;
  border-bottom: 1px solid $border-color-light;
  
  .tab-button {
    padding: $spacing-md $spacing-lg;
    border: none;
    background: none;
    color: $text-color-secondary;
    cursor: pointer;
    font-size: 14px;
    border-bottom: 2px solid transparent;
    
    &:hover {
      color: $text-color;
    }
    
    &.active {
      color: $primary-color;
      border-bottom-color: $primary-color;
    }
  }
}

.tab-content {
  padding: $spacing-lg;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-md;
  
  .info-item {
    display: flex;
    flex-direction: column;
    gap: $spacing-xs;
    
    label {
      font-size: 12px;
      color: $text-color-secondary;
      font-weight: 500;
    }
    
    span {
      font-size: 14px;
      color: $text-color;
    }
  }
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: $spacing-lg;
}

.metric-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-md;
  padding: $spacing-md;
  
  h4 {
    font-size: 14px;
    font-weight: 600;
    color: $text-color;
    margin: 0 0 $spacing-md 0;
  }
  
  .metric-list {
    .metric-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-xs 0;
      border-bottom: 1px solid $border-color-light;
      
      &:last-child {
        border-bottom: none;
      }
      
      span:first-child {
        font-size: 13px;
        color: $text-color-secondary;
      }
      
      span:last-child {
        font-size: 13px;
        font-weight: 600;
        color: $text-color;
      }
    }
  }
}

.config-list {
  .config-item {
    padding: $spacing-md;
    border: 1px solid $border-color-light;
    border-radius: $border-radius-md;
    margin-bottom: $spacing-md;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .config-key {
      font-size: 14px;
      font-weight: 600;
      color: $text-color;
      margin-bottom: $spacing-xs;
    }
    
    .config-value {
      font-size: 13px;
      color: $primary-color;
      font-family: 'Courier New', monospace;
      margin-bottom: $spacing-xs;
    }
    
    .config-description {
      font-size: 12px;
      color: $text-color-secondary;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .charts-section {
    grid-template-columns: 1fr;
  }
  
  .instances-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (max-width: 768px) {
  .database-monitoring {
    padding: $spacing-md;
  }
  
  .page-header {
    flex-direction: column;
    gap: $spacing-md;
    align-items: stretch;
    
    .header-actions {
      justify-content: flex-end;
    }
  }
  
  .overview-cards {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }
  
  .overview-card {
    padding: $spacing-md;
  }
  
  .instances-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
  }
  
  .instance-card {
    padding: $spacing-md;
  }
  
  .section-header {
    flex-direction: column;
    gap: $spacing-sm;
    align-items: stretch;
    
    .section-actions {
      .filter-group {
        justify-content: flex-end;
      }
    }
  }
  
  .slow-queries-table {
    overflow-x: auto;
    
    .table {
      min-width: 800px;
    }
  }
  
  .modal-content {
    width: 95%;
    margin: $spacing-md;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .database-monitoring {
    padding: $spacing-sm;
  }
  
  .page-header {
    .header-content {
      .page-title {
        font-size: 24px;
      }
    }
    
    .header-actions {
      flex-direction: column;
      gap: $spacing-xs;
    }
  }
  
  .overview-card {
    flex-direction: column;
    text-align: center;
    gap: $spacing-sm;
  }
  
  .instance-card {
    .instance-actions {
      flex-direction: column;
    }
  }
  
  .section-actions {
    .search-input {
      width: 100%;
    }
  }
}
</style>