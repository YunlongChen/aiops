<template>
  <div class="system-logs-list">
    <div v-if="displayLogs.length === 0" class="empty-state">
      <el-icon><Document /></el-icon>
      <p>暂无系统日志</p>
    </div>
    
    <div v-else class="logs-container">
      <!-- 日志过滤器 -->
      <div class="logs-filter" v-if="!compact">
        <el-select
          v-model="selectedLevel"
          placeholder="选择日志级别"
          size="small"
          style="width: 120px"
          @change="filterLogs"
        >
          <el-option label="全部" value="" />
          <el-option label="信息" value="info" />
          <el-option label="警告" value="warning" />
          <el-option label="错误" value="error" />
          <el-option label="调试" value="debug" />
        </el-select>
        
        <el-input
          v-model="searchKeyword"
          placeholder="搜索日志内容"
          size="small"
          style="width: 200px"
          :prefix-icon="Search"
          @input="filterLogs"
          clearable
        />
        
        <el-button
          size="small"
          :icon="Refresh"
          @click="refreshLogs"
          :loading="isRefreshing"
        >
          刷新
        </el-button>
      </div>
      
      <!-- 日志列表 -->
      <div class="logs-list">
        <div 
          v-for="log in displayLogs" 
          :key="log.id"
          :class="['log-item', `log-${log.level}`]"
        >
          <div class="log-header">
            <div class="log-meta">
              <span 
                :class="['log-level', `level-${log.level}`]"
              >
                {{ getLevelText(log.level) }}
              </span>
              <span class="log-time">
                {{ formatTime(log.timestamp) }}
              </span>
              <span class="log-source" v-if="log.source">
                {{ log.source }}
              </span>
            </div>
            
            <div class="log-actions" v-if="!compact">
              <el-button
                size="small"
                text
                :icon="CopyDocument"
                @click="copyLog(log)"
              />
            </div>
          </div>
          
          <div class="log-content">
            <p class="log-message">{{ log.message }}</p>
            
            <!-- 详细信息 -->
            <div class="log-details" v-if="log.details && !compact">
              <el-collapse>
                <el-collapse-item title="详细信息">
                  <pre class="log-details-content">{{ log.details }}</pre>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 加载更多 -->
      <div class="load-more" v-if="hasMoreLogs && !compact">
        <el-button
          text
          type="primary"
          @click="loadMoreLogs"
          :loading="isLoadingMore"
        >
          加载更多日志
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 系统日志列表组件
 * 展示系统运行日志和错误信息
 */
import { ref, computed, onMounted } from 'vue'
import { useSystemStore } from '../stores/system'
import { Document, Search, Refresh, CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  compact: {
    type: Boolean,
    default: false
  },
  limit: {
    type: Number,
    default: 10
  }
})

const systemStore = useSystemStore()

// 响应式数据
const selectedLevel = ref('')
const searchKeyword = ref('')
const isRefreshing = ref(false)
const isLoadingMore = ref(false)
const filteredLogs = ref([])

onMounted(() => {
  filterLogs()
})

// 计算属性
const displayLogs = computed(() => {
  const logs = filteredLogs.value.length > 0 ? filteredLogs.value : systemStore.systemLogs
  return props.compact ? logs.slice(0, props.limit) : logs
})

const hasMoreLogs = computed(() => {
  return systemStore.systemLogs.length > displayLogs.value.length
})

/**
 * 过滤日志
 */
const filterLogs = () => {
  let logs = [...systemStore.systemLogs]
  
  // 按级别过滤
  if (selectedLevel.value) {
    logs = logs.filter(log => log.level === selectedLevel.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    logs = logs.filter(log => 
      log.message.toLowerCase().includes(keyword) ||
      (log.source && log.source.toLowerCase().includes(keyword))
    )
  }
  
  filteredLogs.value = logs
}

/**
 * 刷新日志
 */
const refreshLogs = async () => {
  isRefreshing.value = true
  try {
    await systemStore.fetchSystemLogs()
    filterLogs()
    ElMessage.success('日志刷新成功')
  } catch (error) {
    console.error('刷新日志失败:', error)
    ElMessage.error('刷新日志失败')
  } finally {
    isRefreshing.value = false
  }
}

/**
 * 加载更多日志
 */
const loadMoreLogs = async () => {
  isLoadingMore.value = true
  try {
    await systemStore.fetchMoreLogs()
    filterLogs()
  } catch (error) {
    console.error('加载更多日志失败:', error)
    ElMessage.error('加载更多日志失败')
  } finally {
    isLoadingMore.value = false
  }
}

/**
 * 复制日志内容
 * @param {Object} log 日志对象
 */
const copyLog = async (log) => {
  try {
    const logText = `[${formatTime(log.timestamp)}] [${getLevelText(log.level)}] ${log.source ? `[${log.source}] ` : ''}${log.message}`
    await navigator.clipboard.writeText(logText)
    ElMessage.success('日志内容已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

/**
 * 格式化时间
 * @param {Date} timestamp 时间戳
 */
const formatTime = (timestamp) => {
  if (!timestamp) return '未知时间'
  
  const date = new Date(timestamp)
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

/**
 * 获取日志级别文本
 * @param {string} level 日志级别
 */
const getLevelText = (level) => {
  switch (level) {
    case 'info':
      return '信息'
    case 'warning':
      return '警告'
    case 'error':
      return '错误'
    case 'debug':
      return '调试'
    default:
      return '未知'
  }
}
</script>

<style lang="scss" scoped>
.system-logs-list {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  color: var(--el-text-color-secondary);
  flex: 1;

  .el-icon {
    font-size: 48px;
    margin-bottom: var(--spacing-md);
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}

.logs-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.logs-filter {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--el-bg-color-page);
  border-bottom: 1px solid var(--el-border-color-lighter);
  flex-wrap: wrap;
}

.logs-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.log-item {
  padding: var(--spacing-md);
  background: var(--el-bg-color);
  border-left: 4px solid var(--el-border-color);
  border-radius: var(--border-radius);
  transition: all 0.3s ease;

  &:hover {
    box-shadow: var(--shadow-light);
  }

  &.log-info {
    border-left-color: var(--el-color-info);
  }

  &.log-warning {
    border-left-color: var(--el-color-warning);
  }

  &.log-error {
    border-left-color: var(--el-color-danger);
  }

  &.log-debug {
    border-left-color: var(--el-color-success);
  }
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.log-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.log-level {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;

  &.level-info {
    background: var(--el-color-info-light-9);
    color: var(--el-color-info);
  }

  &.level-warning {
    background: var(--el-color-warning-light-9);
    color: var(--el-color-warning);
  }

  &.level-error {
    background: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
  }

  &.level-debug {
    background: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }
}

.log-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.log-source {
  font-size: 12px;
  color: var(--el-text-color-regular);
  background: var(--el-bg-color-page);
  padding: 2px 6px;
  border-radius: 4px;
}

.log-content {
  .log-message {
    margin: 0;
    line-height: 1.5;
    color: var(--el-text-color-primary);
  }

  .log-details {
    margin-top: var(--spacing-sm);

    .log-details-content {
      background: var(--el-bg-color-page);
      padding: var(--spacing-sm);
      border-radius: var(--border-radius);
      font-size: 12px;
      line-height: 1.4;
      overflow-x: auto;
      margin: 0;
    }
  }
}

.load-more {
  text-align: center;
  padding: var(--spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
}

// 响应式设计
@media (max-width: 768px) {
  .logs-filter {
    flex-direction: column;
    gap: var(--spacing-sm);

    .el-select,
    .el-input {
      width: 100% !important;
    }
  }

  .log-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }

  .log-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }
}
</style>