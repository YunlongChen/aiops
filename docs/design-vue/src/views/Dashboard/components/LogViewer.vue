<!--
  日志查看组件
  功能：提供日志搜索、过滤、查看和导出功能
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="log-viewer">
    <!-- 日志工具栏 -->
    <div class="logs-toolbar">
      <div class="search-section">
        <div class="search-input">
          <i class="fas fa-search"></i>
          <input 
            type="text" 
            v-model="searchQuery"
            @input="handleSearch"
            placeholder="搜索日志内容..."
          >
          <button 
            v-if="searchQuery" 
            class="clear-search"
            @click="clearSearch"
          >
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="log-filters">
          <select v-model="selectedLogLevel" @change="applyFilters" class="log-level">
            <option value="all">全部级别</option>
            <option value="error">错误</option>
            <option value="warning">警告</option>
            <option value="info">信息</option>
            <option value="debug">调试</option>
          </select>
          <select v-model="selectedLogSource" @change="applyFilters" class="log-source">
            <option value="all">全部来源</option>
            <option value="web">Web服务</option>
            <option value="api">API服务</option>
            <option value="database">数据库</option>
            <option value="system">系统</option>
            <option value="cache">缓存服务</option>
          </select>
          <div class="time-range-filter">
            <input 
              type="datetime-local" 
              v-model="startTime"
              @change="applyFilters"
              class="time-input"
            >
            <span>至</span>
            <input 
              type="datetime-local" 
              v-model="endTime"
              @change="applyFilters"
              class="time-input"
            >
          </div>
        </div>
      </div>
      <div class="toolbar-actions">
        <button class="btn btn-secondary" @click="exportLogs">
          <i class="fas fa-download"></i>
          导出日志
        </button>
        <button class="btn btn-primary" @click="refreshLogs">
          <i class="fas fa-sync-alt" :class="{ spinning: isRefreshing }"></i>
          刷新
        </button>
        <button class="btn btn-info" @click="toggleAutoRefresh">
          <i :class="autoRefresh ? 'fas fa-pause' : 'fas fa-play'"></i>
          {{ autoRefresh ? '暂停' : '自动' }}刷新
        </button>
      </div>
    </div>
    
    <!-- 日志统计信息 -->
    <div class="logs-stats">
      <div class="stat-item">
        <span class="stat-label">总计:</span>
        <span class="stat-value">{{ totalLogs }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">错误:</span>
        <span class="stat-value error">{{ errorCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">警告:</span>
        <span class="stat-value warning">{{ warningCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">信息:</span>
        <span class="stat-value info">{{ infoCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">调试:</span>
        <span class="stat-value debug">{{ debugCount }}</span>
      </div>
    </div>
    
    <!-- 日志内容 -->
    <div class="logs-content" ref="logsContainer">
      <div class="logs-header">
        <div class="header-controls">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="showTimestamp"
              @change="updateLogDisplay"
            >
            显示时间戳
          </label>
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="showSource"
              @change="updateLogDisplay"
            >
            显示来源
          </label>
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              v-model="wrapLines"
              @change="updateLogDisplay"
            >
            自动换行
          </label>
        </div>
        <div class="view-controls">
          <button 
            :class="['view-btn', { active: viewMode === 'table' }]"
            @click="setViewMode('table')"
          >
            <i class="fas fa-table"></i>
            表格视图
          </button>
          <button 
            :class="['view-btn', { active: viewMode === 'raw' }]"
            @click="setViewMode('raw')"
          >
            <i class="fas fa-align-left"></i>
            原始视图
          </button>
        </div>
      </div>
      
      <!-- 表格视图 -->
      <div v-if="viewMode === 'table'" class="table-view">
        <table class="logs-table">
          <thead>
            <tr>
              <th v-if="showTimestamp" class="time-column">时间</th>
              <th class="level-column">级别</th>
              <th v-if="showSource" class="source-column">来源</th>
              <th class="message-column">消息</th>
              <th class="actions-column">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="log in paginatedLogs" 
              :key="log.id"
              :class="['log-entry', log.level]"
            >
              <td v-if="showTimestamp" class="log-time">{{ formatTime(log.timestamp) }}</td>
              <td class="log-level">
                <span :class="['level-badge', log.level]">{{ log.level.toUpperCase() }}</span>
              </td>
              <td v-if="showSource" class="log-source">{{ log.source }}</td>
              <td class="log-message" :class="{ wrapped: wrapLines }">
                <span v-html="highlightSearch(log.message)"></span>
              </td>
              <td class="log-actions">
                <button class="action-btn" @click="viewLogDetails(log)" title="查看详情">
                  <i class="fas fa-eye"></i>
                </button>
                <button class="action-btn" @click="copyLogMessage(log)" title="复制消息">
                  <i class="fas fa-copy"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 原始视图 -->
      <div v-if="viewMode === 'raw'" class="raw-view">
        <pre class="raw-logs" :class="{ wrapped: wrapLines }">{{ rawLogsText }}</pre>
      </div>
      
      <!-- 空状态 -->
      <div v-if="filteredLogs.length === 0" class="empty-logs">
        <i class="fas fa-file-alt"></i>
        <h3>暂无日志数据</h3>
        <p>当前筛选条件下没有找到匹配的日志记录</p>
      </div>
    </div>
    
    <!-- 分页控件 -->
    <div class="logs-pagination" v-if="filteredLogs.length > 0">
      <div class="pagination-info">
        <span>显示 {{ startIndex + 1 }}-{{ endIndex }} 条，共 {{ filteredLogs.length }} 条记录</span>
        <select v-model="pageSize" @change="updatePagination" class="page-size-selector">
          <option value="25">25条/页</option>
          <option value="50">50条/页</option>
          <option value="100">100条/页</option>
          <option value="200">200条/页</option>
        </select>
      </div>
      <div class="pagination-controls">
        <button 
          class="btn btn-secondary"
          :disabled="currentPage === 1"
          @click="goToPage(1)"
        >
          首页
        </button>
        <button 
          class="btn btn-secondary"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          上一页
        </button>
        <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
        <button 
          class="btn btn-secondary"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          下一页
        </button>
        <button 
          class="btn btn-secondary"
          :disabled="currentPage === totalPages"
          @click="goToPage(totalPages)"
        >
          末页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 日志查看组件
 * 提供完整的日志查看、搜索、过滤和导出功能
 */
export default {
  name: 'LogViewer',
  data() {
    return {
      // 搜索和过滤
      searchQuery: '',
      selectedLogLevel: 'all',
      selectedLogSource: 'all',
      startTime: '',
      endTime: '',
      // 显示选项
      showTimestamp: true,
      showSource: true,
      wrapLines: false,
      viewMode: 'table', // 'table' 或 'raw'
      // 刷新控制
      isRefreshing: false,
      autoRefresh: false,
      refreshInterval: null,
      // 分页
      currentPage: 1,
      pageSize: 50,
      // 日志数据
      logs: [
        {
          id: 1,
          timestamp: '2025-01-23T14:32:15.123Z',
          level: 'error',
          source: 'database',
          message: 'Connection pool exhausted: Unable to acquire connection from pool after 30 seconds timeout'
        },
        {
          id: 2,
          timestamp: '2025-01-23T14:28:42.456Z',
          level: 'warning',
          source: 'web',
          message: 'Response time exceeded threshold: 2.5s > 2.0s for endpoint /api/users'
        },
        {
          id: 3,
          timestamp: '2025-01-23T14:25:33.789Z',
          level: 'info',
          source: 'api',
          message: 'User authentication successful: user_id=12345, session_id=abc123'
        },
        {
          id: 4,
          timestamp: '2025-01-23T14:22:18.012Z',
          level: 'info',
          source: 'system',
          message: 'Scheduled backup completed successfully: backup_id=backup_20250123_142218'
        },
        {
          id: 5,
          timestamp: '2025-01-23T14:20:05.345Z',
          level: 'debug',
          source: 'cache',
          message: 'Cache miss for key: user_profile_12345, fetching from database'
        },
        {
          id: 6,
          timestamp: '2025-01-23T14:18:30.678Z',
          level: 'error',
          source: 'api',
          message: 'Invalid request payload: missing required field "email" in user registration'
        },
        {
          id: 7,
          timestamp: '2025-01-23T14:15:22.901Z',
          level: 'warning',
          source: 'system',
          message: 'Disk usage warning: /var/log partition is 85% full (8.5GB/10GB)'
        },
        {
          id: 8,
          timestamp: '2025-01-23T14:12:45.234Z',
          level: 'info',
          source: 'web',
          message: 'New user session started: IP=192.168.1.100, User-Agent=Mozilla/5.0'
        }
      ]
    }
  },
  computed: {
    /**
     * 过滤后的日志
     */
    filteredLogs() {
      let filtered = this.logs
      
      // 按级别过滤
      if (this.selectedLogLevel !== 'all') {
        filtered = filtered.filter(log => log.level === this.selectedLogLevel)
      }
      
      // 按来源过滤
      if (this.selectedLogSource !== 'all') {
        filtered = filtered.filter(log => log.source === this.selectedLogSource)
      }
      
      // 按搜索关键词过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(log => 
          log.message.toLowerCase().includes(query) ||
          log.source.toLowerCase().includes(query)
        )
      }
      
      // 按时间范围过滤
      if (this.startTime) {
        const startDate = new Date(this.startTime)
        filtered = filtered.filter(log => new Date(log.timestamp) >= startDate)
      }
      
      if (this.endTime) {
        const endDate = new Date(this.endTime)
        filtered = filtered.filter(log => new Date(log.timestamp) <= endDate)
      }
      
      return filtered.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    },
    
    /**
     * 分页后的日志
     */
    paginatedLogs() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredLogs.slice(start, end)
    },
    
    /**
     * 总页数
     */
    totalPages() {
      return Math.ceil(this.filteredLogs.length / this.pageSize)
    },
    
    /**
     * 开始索引
     */
    startIndex() {
      return (this.currentPage - 1) * this.pageSize
    },
    
    /**
     * 结束索引
     */
    endIndex() {
      return Math.min(this.startIndex + this.pageSize, this.filteredLogs.length)
    },
    
    /**
     * 原始日志文本
     */
    rawLogsText() {
      return this.paginatedLogs.map(log => {
        let line = ''
        if (this.showTimestamp) {
          line += `[${this.formatTime(log.timestamp)}] `
        }
        line += `${log.level.toUpperCase()}`
        if (this.showSource) {
          line += ` [${log.source}]`
        }
        line += `: ${log.message}`
        return line
      }).join('\n')
    },
    
    // 统计信息
    totalLogs() {
      return this.filteredLogs.length
    },
    
    errorCount() {
      return this.filteredLogs.filter(log => log.level === 'error').length
    },
    
    warningCount() {
      return this.filteredLogs.filter(log => log.level === 'warning').length
    },
    
    infoCount() {
      return this.filteredLogs.filter(log => log.level === 'info').length
    },
    
    debugCount() {
      return this.filteredLogs.filter(log => log.level === 'debug').length
    }
  },
  methods: {
    /**
     * 处理搜索
     */
    handleSearch() {
      this.currentPage = 1
      this.applyFilters()
    },
    
    /**
     * 清除搜索
     */
    clearSearch() {
      this.searchQuery = ''
      this.handleSearch()
    },
    
    /**
     * 应用过滤器
     */
    applyFilters() {
      this.currentPage = 1
    },
    
    /**
     * 刷新日志
     */
    async refreshLogs() {
      this.isRefreshing = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('Logs refreshed')
      } finally {
        this.isRefreshing = false
      }
    },
    
    /**
     * 切换自动刷新
     */
    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh
      
      if (this.autoRefresh) {
        this.refreshInterval = setInterval(() => {
          this.refreshLogs()
        }, 10000) // 每10秒刷新一次
      } else {
        if (this.refreshInterval) {
          clearInterval(this.refreshInterval)
          this.refreshInterval = null
        }
      }
    },
    
    /**
     * 导出日志
     */
    exportLogs() {
      const csvContent = this.filteredLogs.map(log => {
        return [
          this.formatTime(log.timestamp),
          log.level,
          log.source,
          `"${log.message.replace(/"/g, '""')}"`
        ].join(',')
      }).join('\n')
      
      const header = 'Timestamp,Level,Source,Message\n'
      const blob = new Blob([header + csvContent], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `logs_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.csv`
      a.click()
      URL.revokeObjectURL(url)
    },
    
    /**
     * 设置视图模式
     */
    setViewMode(mode) {
      this.viewMode = mode
    },
    
    /**
     * 更新日志显示
     */
    updateLogDisplay() {
      // 触发重新渲染
      this.$forceUpdate()
    },
    
    /**
     * 跳转到指定页面
     */
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    },
    
    /**
     * 更新分页
     */
    updatePagination() {
      this.currentPage = 1
    },
    
    /**
     * 格式化时间
     */
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    /**
     * 高亮搜索关键词
     */
    highlightSearch(text) {
      if (!this.searchQuery) return text
      
      const regex = new RegExp(`(${this.searchQuery})`, 'gi')
      return text.replace(regex, '<mark>$1</mark>')
    },
    
    /**
     * 查看日志详情
     */
    viewLogDetails(log) {
      console.log('Viewing log details:', log)
      // 这里可以打开详情弹窗
    },
    
    /**
     * 复制日志消息
     */
    copyLogMessage(log) {
      navigator.clipboard.writeText(log.message).then(() => {
        console.log('Log message copied to clipboard')
      })
    }
  },
  beforeUnmount() {
    // 清理定时器
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval)
    }
  }
}
</script>

<style scoped>
/* 日志查看器容器 */
.log-viewer {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 工具栏样式 */
.logs-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e9ecef;
}

.search-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input i {
  position: absolute;
  left: 12px;
  color: #6c757d;
}

.search-input input {
  width: 100%;
  padding: 10px 12px 10px 35px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.clear-search {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 4px;
}

.log-filters {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}

.log-level,
.log-source {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.time-range-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.time-input {
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.toolbar-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

/* 统计信息样式 */
.logs-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.stat-label {
  color: #6c757d;
}

.stat-value {
  font-weight: 600;
  color: #2c3e50;
}

.stat-value.error {
  color: #dc3545;
}

.stat-value.warning {
  color: #ffc107;
}

.stat-value.info {
  color: #17a2b8;
}

.stat-value.debug {
  color: #6c757d;
}

/* 日志内容样式 */
.logs-content {
  margin-bottom: 20px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e9ecef;
}

.header-controls {
  display: flex;
  gap: 15px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  cursor: pointer;
}

.view-controls {
  display: flex;
  gap: 5px;
}

.view-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s ease;
}

.view-btn:hover {
  background: #f8f9fa;
}

.view-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

/* 表格视图样式 */
.table-view {
  overflow-x: auto;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.logs-table th,
.logs-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.logs-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 12px;
  text-transform: uppercase;
  position: sticky;
  top: 0;
  z-index: 10;
}

.time-column {
  width: 180px;
}

.level-column {
  width: 80px;
}

.source-column {
  width: 100px;
}

.actions-column {
  width: 80px;
}

.log-entry {
  transition: background-color 0.2s ease;
}

.log-entry:hover {
  background: #f8f9fa;
}

.log-entry.error {
  border-left: 3px solid #dc3545;
}

.log-entry.warning {
  border-left: 3px solid #ffc107;
}

.log-entry.info {
  border-left: 3px solid #17a2b8;
}

.log-entry.debug {
  border-left: 3px solid #6c757d;
}

.log-time {
  font-family: monospace;
  color: #6c757d;
  font-size: 12px;
}

.level-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.level-badge.error {
  background: #f8d7da;
  color: #721c24;
}

.level-badge.warning {
  background: #fff3cd;
  color: #856404;
}

.level-badge.info {
  background: #d1ecf1;
  color: #0c5460;
}

.level-badge.debug {
  background: #f8f9fa;
  color: #6c757d;
}

.log-source {
  font-weight: 500;
  color: #495057;
}

.log-message {
  font-family: monospace;
  color: #2c3e50;
  line-height: 1.4;
}

.log-message.wrapped {
  white-space: pre-wrap;
  word-break: break-word;
}

.log-message mark {
  background: #fff3cd;
  padding: 1px 2px;
  border-radius: 2px;
}

.log-actions {
  display: flex;
  gap: 5px;
}

.action-btn {
  padding: 4px 6px;
  border: none;
  background: #f8f9fa;
  border-radius: 3px;
  cursor: pointer;
  color: #6c757d;
  font-size: 12px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #e9ecef;
  color: #495057;
}

/* 原始视图样式 */
.raw-view {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
  max-height: 600px;
  overflow: auto;
}

.raw-logs {
  font-family: monospace;
  font-size: 13px;
  line-height: 1.4;
  color: #2c3e50;
  margin: 0;
  white-space: pre;
}

.raw-logs.wrapped {
  white-space: pre-wrap;
  word-break: break-word;
}

/* 空状态样式 */
.empty-logs {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.empty-logs i {
  font-size: 48px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-logs h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
}

.empty-logs p {
  margin: 0;
  font-size: 14px;
}

/* 分页样式 */
.logs-pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 14px;
  color: #6c757d;
}

.page-size-selector {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-info {
  font-size: 14px;
  color: #6c757d;
  margin: 0 10px;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.btn-info {
  background: #17a2b8;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #138496;
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
  .logs-toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .log-viewer {
    padding: 15px;
  }
  
  .log-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .time-range-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .logs-stats {
    flex-direction: column;
    gap: 10px;
  }
  
  .logs-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-controls {
    flex-direction: column;
  }
  
  .logs-pagination {
    flex-direction: column;
    gap: 15px;
  }
  
  .pagination-controls {
    justify-content: center;
  }
}
</style>