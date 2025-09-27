<template>
  <div class="system-logs">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Document /></el-icon>
          系统日志
        </h1>
        <div class="log-stats">
          <span class="stat-item">
            总计: {{ totalLogs }}
          </span>
          <span class="stat-item">
            错误: {{ errorCount }}
          </span>
          <span class="stat-item">
            警告: {{ warningCount }}
          </span>
        </div>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          :icon="Refresh" 
          :loading="isRefreshing"
          @click="refreshLogs"
        >
          刷新日志
        </el-button>
        <el-button 
          type="success" 
          :icon="Download"
          @click="exportLogs"
        >
          导出日志
        </el-button>
        <el-button 
          type="danger" 
          :icon="Delete"
          @click="clearLogs"
        >
          清空日志
        </el-button>
      </div>
    </div>

    <!-- 过滤器 -->
    <div class="filters-section">
      <div class="dashboard-card">
        <div class="card-content">
          <div class="filters-grid">
            <!-- 日志级别过滤 -->
            <div class="filter-group">
              <label class="filter-label">日志级别</label>
              <el-select 
                v-model="filters.level" 
                placeholder="选择级别"
                clearable
                @change="applyFilters"
              >
                <el-option label="全部" value="" />
                <el-option label="错误" value="error" />
                <el-option label="警告" value="warning" />
                <el-option label="信息" value="info" />
                <el-option label="调试" value="debug" />
              </el-select>
            </div>

            <!-- 日志来源过滤 -->
            <div class="filter-group">
              <label class="filter-label">日志来源</label>
              <el-select 
                v-model="filters.source" 
                placeholder="选择来源"
                clearable
                @change="applyFilters"
              >
                <el-option label="全部" value="" />
                <el-option label="系统" value="system" />
                <el-option label="应用" value="application" />
                <el-option label="安全" value="security" />
                <el-option label="网络" value="network" />
                <el-option label="硬件" value="hardware" />
              </el-select>
            </div>

            <!-- 时间范围过滤 -->
            <div class="filter-group">
              <label class="filter-label">时间范围</label>
              <el-date-picker
                v-model="filters.dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                @change="applyFilters"
              />
            </div>

            <!-- 关键词搜索 -->
            <div class="filter-group">
              <label class="filter-label">关键词搜索</label>
              <el-input
                v-model="filters.keyword"
                placeholder="输入关键词搜索"
                :prefix-icon="Search"
                clearable
                @input="debounceSearch"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 日志列表 -->
    <div class="logs-section">
      <div class="dashboard-card">
        <div class="card-header">
          <span class="card-title">
            <el-icon><List /></el-icon>
            日志记录 ({{ filteredLogs.length }})
          </span>
          <div class="card-actions">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              @change="toggleAutoRefresh"
            />
          </div>
        </div>
        <div class="card-content">
          <div class="logs-container" ref="logsContainer">
            <div 
              v-for="log in paginatedLogs" 
              :key="log.id"
              :class="['log-item', `log-${log.level}`]"
            >
              <div class="log-header">
                <div class="log-meta">
                  <span class="log-time">{{ formatTime(log.timestamp) }}</span>
                  <span :class="['log-level', `level-${log.level}`]">
                    {{ log.level.toUpperCase() }}
                  </span>
                  <span class="log-source">{{ log.source }}</span>
                </div>
                <div class="log-actions">
                  <el-button 
                    size="small" 
                    text 
                    :icon="CopyDocument"
                    @click="copyLog(log)"
                  >
                    复制
                  </el-button>
                  <el-button 
                    size="small" 
                    text 
                    :icon="View"
                    @click="viewLogDetails(log)"
                  >
                    详情
                  </el-button>
                </div>
              </div>
              <div class="log-message">{{ log.message }}</div>
              <div class="log-details" v-if="log.details">
                <pre>{{ log.details }}</pre>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="filteredLogs.length === 0" class="empty-state">
              <el-icon><Document /></el-icon>
              <span>暂无日志记录</span>
            </div>

            <!-- 加载状态 -->
            <div v-if="isLoading" class="loading-state">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
          </div>

          <!-- 分页 -->
          <div class="pagination-section" v-if="filteredLogs.length > 0">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[20, 50, 100, 200]"
              :total="filteredLogs.length"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="logDetailVisible"
      title="日志详情"
      width="60%"
      :before-close="closeLogDetail"
    >
      <div v-if="selectedLog" class="log-detail-content">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">时间:</span>
              <span class="detail-value">{{ formatTime(selectedLog.timestamp) }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">级别:</span>
              <span :class="['detail-value', 'level-badge', `level-${selectedLog.level}`]">
                {{ selectedLog.level.toUpperCase() }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">来源:</span>
              <span class="detail-value">{{ selectedLog.source }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">ID:</span>
              <span class="detail-value">{{ selectedLog.id }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h4>消息内容</h4>
          <div class="message-content">{{ selectedLog.message }}</div>
        </div>

        <div class="detail-section" v-if="selectedLog.details">
          <h4>详细信息</h4>
          <pre class="details-content">{{ selectedLog.details }}</pre>
        </div>

        <div class="detail-section" v-if="selectedLog.stackTrace">
          <h4>堆栈跟踪</h4>
          <pre class="stack-trace">{{ selectedLog.stackTrace }}</pre>
        </div>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeLogDetail">关闭</el-button>
          <el-button type="primary" @click="copyLog(selectedLog)">复制日志</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 系统日志页面
 * 提供日志查看、过滤、搜索和导出功能
 */
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Document, Refresh, Download, Delete, Search, List, 
  CopyDocument, View, Loading 
} from '@element-plus/icons-vue'

const isRefreshing = ref(false)
const isLoading = ref(false)
const autoRefresh = ref(false)
const logDetailVisible = ref(false)
const selectedLog = ref(null)
const logsContainer = ref(null)

// 分页
const currentPage = ref(1)
const pageSize = ref(50)

// 过滤器
const filters = reactive({
  level: '',
  source: '',
  dateRange: null,
  keyword: ''
})

// 模拟日志数据
const logs = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 300000),
    level: 'error',
    source: 'system',
    message: '磁盘空间不足，剩余空间低于10%',
    details: 'Disk usage: 92%\nAvailable space: 2.1GB\nMount point: /var/log',
    stackTrace: null
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 600000),
    level: 'warning',
    source: 'hardware',
    message: 'CPU温度过高，当前温度85°C',
    details: 'CPU Temperature: 85°C\nThreshold: 80°C\nFan Speed: 3200 RPM',
    stackTrace: null
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 900000),
    level: 'info',
    source: 'application',
    message: '服务器热控制系统启动成功',
    details: 'Service: server_thermal_control\nVersion: 1.0.0\nPID: 12345',
    stackTrace: null
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 1200000),
    level: 'debug',
    source: 'network',
    message: 'IPMI连接建立成功',
    details: 'Host: 192.168.1.100\nPort: 623\nProtocol: IPMI v2.0',
    stackTrace: null
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 1500000),
    level: 'error',
    source: 'security',
    message: '登录失败，用户名或密码错误',
    details: 'Username: admin\nIP: 192.168.1.50\nAttempts: 3',
    stackTrace: 'SecurityException: Invalid credentials\n  at auth.validate(auth.rs:45)\n  at login.handler(login.rs:23)'
  }
])

let refreshTimer = null
let searchTimer = null

onMounted(() => {
  generateMoreLogs()
  refreshLogs()
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
})

// 计算属性
const totalLogs = computed(() => logs.value.length)
const errorCount = computed(() => logs.value.filter(log => log.level === 'error').length)
const warningCount = computed(() => logs.value.filter(log => log.level === 'warning').length)

const filteredLogs = computed(() => {
  let result = logs.value

  // 级别过滤
  if (filters.level) {
    result = result.filter(log => log.level === filters.level)
  }

  // 来源过滤
  if (filters.source) {
    result = result.filter(log => log.source === filters.source)
  }

  // 时间范围过滤
  if (filters.dateRange && filters.dateRange.length === 2) {
    const [startTime, endTime] = filters.dateRange
    result = result.filter(log => {
      const logTime = log.timestamp.getTime()
      return logTime >= new Date(startTime).getTime() && logTime <= new Date(endTime).getTime()
    })
  }

  // 关键词搜索
  if (filters.keyword) {
    const keyword = filters.keyword.toLowerCase()
    result = result.filter(log => 
      log.message.toLowerCase().includes(keyword) ||
      (log.details && log.details.toLowerCase().includes(keyword))
    )
  }

  // 按时间倒序排列
  return result.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
})

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredLogs.value.slice(start, end)
})

/**
 * 生成更多模拟日志数据
 */
const generateMoreLogs = () => {
  const levels = ['error', 'warning', 'info', 'debug']
  const sources = ['system', 'application', 'security', 'network', 'hardware']
  const messages = [
    '系统启动完成',
    '内存使用率过高',
    '网络连接异常',
    '用户登录成功',
    '配置文件更新',
    '服务重启',
    '磁盘I/O错误',
    '温度传感器异常',
    '风扇转速调整',
    'IPMI命令执行'
  ]

  for (let i = 6; i <= 100; i++) {
    const level = levels[Math.floor(Math.random() * levels.length)]
    const source = sources[Math.floor(Math.random() * sources.length)]
    const message = messages[Math.floor(Math.random() * messages.length)]
    
    logs.value.push({
      id: i,
      timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
      level,
      source,
      message: `${message} - ${i}`,
      details: level === 'error' ? `Error details for log ${i}` : null,
      stackTrace: level === 'error' && Math.random() > 0.5 ? `Stack trace for error ${i}` : null
    })
  }
}

/**
 * 刷新日志
 */
const refreshLogs = async () => {
  isRefreshing.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 这里应该从API获取最新日志
    ElMessage.success('日志已刷新')
    
  } catch (error) {
    ElMessage.error('刷新日志失败: ' + error.message)
  } finally {
    isRefreshing.value = false
  }
}

/**
 * 应用过滤器
 */
const applyFilters = () => {
  currentPage.value = 1
}

/**
 * 防抖搜索
 */
const debounceSearch = () => {
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  
  searchTimer = setTimeout(() => {
    applyFilters()
  }, 500)
}

/**
 * 切换自动刷新
 */
const toggleAutoRefresh = (enabled) => {
  if (enabled) {
    refreshTimer = setInterval(() => {
      if (!isRefreshing.value) {
        refreshLogs()
      }
    }, 30000) // 30秒刷新一次
  } else {
    if (refreshTimer) {
      clearInterval(refreshTimer)
      refreshTimer = null
    }
  }
}

/**
 * 复制日志
 * @param {Object} log 日志对象
 */
const copyLog = async (log) => {
  const logText = `[${formatTime(log.timestamp)}] [${log.level.toUpperCase()}] [${log.source}] ${log.message}`
  
  try {
    await navigator.clipboard.writeText(logText)
    ElMessage.success('日志已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

/**
 * 查看日志详情
 * @param {Object} log 日志对象
 */
const viewLogDetails = (log) => {
  selectedLog.value = log
  logDetailVisible.value = true
}

/**
 * 关闭日志详情
 */
const closeLogDetail = () => {
  logDetailVisible.value = false
  selectedLog.value = null
}

/**
 * 导出日志
 */
const exportLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要导出当前筛选的日志吗？',
      '确认导出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 生成CSV内容
    const csvContent = generateCSV(filteredLogs.value)
    
    // 创建下载链接
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `system_logs_${new Date().toISOString().slice(0, 10)}.csv`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('日志导出成功')
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('导出失败: ' + error.message)
    }
  }
}

/**
 * 生成CSV内容
 * @param {Array} logs 日志数组
 */
const generateCSV = (logs) => {
  const headers = ['时间', '级别', '来源', '消息', '详情']
  const csvRows = [headers.join(',')]
  
  logs.forEach(log => {
    const row = [
      formatTime(log.timestamp),
      log.level.toUpperCase(),
      log.source,
      `"${log.message.replace(/"/g, '""')}"`,
      `"${(log.details || '').replace(/"/g, '""')}"`
    ]
    csvRows.push(row.join(','))
  })
  
  return csvRows.join('\n')
}

/**
 * 清空日志
 */
const clearLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有日志吗？此操作不可恢复！',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    logs.value = []
    ElMessage.success('日志已清空')
    
  } catch (error) {
    // 用户取消操作
  }
}

/**
 * 分页大小变化
 */
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
}

/**
 * 当前页变化
 */
const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
  
  // 滚动到顶部
  nextTick(() => {
    if (logsContainer.value) {
      logsContainer.value.scrollTop = 0
    }
  })
}

/**
 * 格式化时间
 * @param {Date} date 日期对象
 */
const formatTime = (date) => {
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style lang="scss" scoped>
.system-logs {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color-page);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  box-shadow: var(--shadow-light);

  .header-left {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      margin: 0;
    }

    .log-stats {
      display: flex;
      gap: var(--spacing-md);
      font-size: 14px;

      .stat-item {
        color: var(--el-text-color-secondary);
      }
    }
  }

  .header-right {
    display: flex;
    gap: var(--spacing-sm);
  }
}

.filters-section {
  padding: 0 var(--spacing-lg);
  margin-top: var(--spacing-lg);

  .filters-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-md);
    align-items: end;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);

    .filter-label {
      font-size: 14px;
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
  }
}

.logs-section {
  flex: 1;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;

  .dashboard-card {
    flex: 1;
    display: flex;
    flex-direction: column;

    .card-content {
      flex: 1;
      display: flex;
      flex-direction: column;
    }
  }
}

.logs-container {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.log-item {
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  border-left: 4px solid;
  background: var(--el-bg-color-page);

  &.log-error {
    border-left-color: var(--el-color-danger);
    background: var(--el-color-danger-light-9);
  }

  &.log-warning {
    border-left-color: var(--el-color-warning);
    background: var(--el-color-warning-light-9);
  }

  &.log-info {
    border-left-color: var(--el-color-info);
    background: var(--el-color-info-light-9);
  }

  &.log-debug {
    border-left-color: var(--el-color-success);
    background: var(--el-color-success-light-9);
  }

  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);

    .log-meta {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);

      .log-time {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        font-family: monospace;
      }

      .log-level {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;

        &.level-error {
          background: var(--el-color-danger);
          color: white;
        }

        &.level-warning {
          background: var(--el-color-warning);
          color: white;
        }

        &.level-info {
          background: var(--el-color-info);
          color: white;
        }

        &.level-debug {
          background: var(--el-color-success);
          color: white;
        }
      }

      .log-source {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        background: var(--el-bg-color);
        padding: 2px 6px;
        border-radius: 4px;
      }
    }

    .log-actions {
      display: flex;
      gap: var(--spacing-xs);
    }
  }

  .log-message {
    font-size: 14px;
    color: var(--el-text-color-primary);
    line-height: 1.5;
    margin-bottom: var(--spacing-sm);
  }

  .log-details {
    background: var(--el-bg-color);
    padding: var(--spacing-sm);
    border-radius: 4px;
    border: 1px solid var(--el-border-color-lighter);

    pre {
      margin: 0;
      font-size: 12px;
      color: var(--el-text-color-secondary);
      white-space: pre-wrap;
      word-break: break-all;
    }
  }
}

.pagination-section {
  display: flex;
  justify-content: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
}

.log-detail-content {
  .detail-section {
    margin-bottom: var(--spacing-lg);

    h4 {
      margin: 0 0 var(--spacing-md) 0;
      color: var(--el-text-color-primary);
      font-size: 16px;
      font-weight: 600;
    }

    .detail-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--spacing-md);
    }

    .detail-item {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);

      .detail-label {
        font-weight: 500;
        color: var(--el-text-color-secondary);
        min-width: 60px;
      }

      .detail-value {
        color: var(--el-text-color-primary);

        &.level-badge {
          padding: 2px 8px;
          border-radius: 12px;
          font-size: 11px;
          font-weight: 600;
          color: white;

          &.level-error {
            background: var(--el-color-danger);
          }

          &.level-warning {
            background: var(--el-color-warning);
          }

          &.level-info {
            background: var(--el-color-info);
          }

          &.level-debug {
            background: var(--el-color-success);
          }
        }
      }
    }

    .message-content {
      padding: var(--spacing-md);
      background: var(--el-bg-color-page);
      border-radius: var(--border-radius);
      border: 1px solid var(--el-border-color-lighter);
      font-size: 14px;
      line-height: 1.6;
    }

    .details-content,
    .stack-trace {
      background: var(--el-bg-color-page);
      padding: var(--spacing-md);
      border-radius: var(--border-radius);
      border: 1px solid var(--el-border-color-lighter);
      font-size: 12px;
      color: var(--el-text-color-secondary);
      white-space: pre-wrap;
      word-break: break-all;
      max-height: 300px;
      overflow-y: auto;
      margin: 0;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);

    .header-right {
      align-self: flex-end;
    }
  }

  .filters-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: var(--spacing-md);

    .header-left .page-title {
      font-size: 20px;
    }

    .header-right {
      width: 100%;
      display: flex;
      justify-content: flex-end;
      flex-wrap: wrap;
      gap: var(--spacing-sm);
    }
  }

  .filters-section,
  .logs-section {
    padding: var(--spacing-md);
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .log-item {
    .log-header {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-sm);

      .log-meta {
        flex-wrap: wrap;
      }
    }
  }

  .detail-grid {
    grid-template-columns: 1fr !important;
  }
}
</style>