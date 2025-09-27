<template>
  <div class="dashboard">
    <!-- 页面头部 -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Monitor /></el-icon>
          服务器热控制系统
        </h1>
        <div class="system-status">
          <span 
            :class="['status-indicator', systemStore.serverStatus.isOnline ? 'online' : 'offline']"
          >
            {{ systemStore.serverStatus.isOnline ? '在线' : '离线' }}
          </span>
          <span class="last-update">
            最后更新: {{ formatTime(systemStore.serverStatus.lastUpdate) }}
          </span>
        </div>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          :icon="Refresh" 
          :loading="isRefreshing"
          @click="refreshData"
        >
          刷新数据
        </el-button>
        <el-button 
          type="info" 
          :icon="Setting" 
          @click="$router.push('/settings')"
        >
          设置
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="dashboard-content">
      <!-- 系统概览卡片 -->
      <div class="overview-section">
        <div class="grid grid-4">
          <!-- 系统健康状态 -->
          <div class="metric-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><CircleCheck /></el-icon>
                系统健康
              </span>
            </div>
            <div class="card-content">
              <div 
                :class="['metric-value', systemStore.isSystemHealthy ? 'success' : 'danger']"
              >
                {{ systemStore.isSystemHealthy ? '正常' : '异常' }}
              </div>
              <div class="metric-label">整体状态</div>
            </div>
          </div>

          <!-- CPU使用率 -->
          <div class="metric-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Cpu /></el-icon>
                CPU使用率
              </span>
            </div>
            <div class="card-content">
              <div 
                :class="['metric-value', getCpuStatusClass(systemStore.systemMetrics.cpu.usage)]"
              >
                {{ systemStore.systemMetrics.cpu.usage }}
                <span class="metric-unit">%</span>
              </div>
              <div class="metric-label">{{ systemStore.systemInfo.cpuCores }} 核心</div>
            </div>
          </div>

          <!-- 内存使用率 -->
          <div class="metric-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Grid /></el-icon>
                内存使用率
              </span>
            </div>
            <div class="card-content">
              <div 
                :class="['metric-value', getMemoryStatusClass(systemStore.memoryUsagePercentage)]"
              >
                {{ systemStore.memoryUsagePercentage }}
                <span class="metric-unit">%</span>
              </div>
              <div class="metric-label">{{ formatBytes(systemStore.systemMetrics.memory.total) }}</div>
            </div>
          </div>

          <!-- 磁盘使用率 -->
          <div class="metric-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Coin /></el-icon>
                磁盘使用率
              </span>
            </div>
            <div class="card-content">
              <div 
                :class="['metric-value', getDiskStatusClass(systemStore.diskUsagePercentage)]"
              >
                {{ systemStore.diskUsagePercentage }}
                <span class="metric-unit">%</span>
              </div>
              <div class="metric-label">{{ formatBytes(systemStore.systemMetrics.disk.total) }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 详细监控区域 -->
      <div class="monitoring-section">
        <div class="grid grid-2">
          <!-- 温度监控 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Sunny /></el-icon>
                温度监控
              </span>
              <el-button 
                size="small" 
                text 
                @click="$router.push('/monitoring')"
              >
                查看详情
              </el-button>
            </div>
            <div class="card-content">
              <TemperatureChart :height="200" />
            </div>
          </div>

          <!-- 风扇状态 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><WindPower /></el-icon>
                风扇状态
              </span>
              <el-button 
                size="small" 
                text 
                @click="$router.push('/monitoring')"
              >
                查看详情
              </el-button>
            </div>
            <div class="card-content">
              <FanStatusList :compact="true" />
            </div>
          </div>
        </div>
      </div>

      <!-- IPMI控制区域 -->
      <div class="control-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Setting /></el-icon>
              IPMI控制面板
            </span>
            <div class="ipmi-status">
              <span 
                :class="['status-indicator', systemStore.ipmiStatus.connected ? 'online' : 'offline']"
              >
                {{ systemStore.ipmiStatus.connected ? 'IPMI已连接' : 'IPMI未连接' }}
              </span>
            </div>
          </div>
          <div class="card-content">
            <IPMIControlPanel :compact="true" />
          </div>
        </div>
      </div>

      <!-- 系统日志预览 -->
      <div class="logs-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Document /></el-icon>
              系统日志
            </span>
            <el-button 
              size="small" 
              text 
              @click="$router.push('/logs')"
            >
              查看全部
            </el-button>
          </div>
          <div class="card-content">
            <SystemLogsList :limit="5" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 主仪表板页面
 * 展示系统整体状态和关键指标
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '../stores/system'
import { 
  Monitor, Refresh, Setting, CircleCheck, Cpu, 
  Grid, Coin, Sunny, WindPower, Document 
} from '@element-plus/icons-vue'

// 导入组件
import TemperatureChart from '../components/TemperatureChart.vue'
import FanStatusList from '../components/FanStatusList.vue'
import IPMIControlPanel from '../components/IPMIControlPanel.vue'
import SystemLogsList from '../components/SystemLogsList.vue'

const systemStore = useSystemStore()
const isRefreshing = ref(false)
let refreshTimer = null

onMounted(() => {
  // 初始化数据
  refreshData()
  
  // 设置自动刷新
  refreshTimer = setInterval(() => {
    if (!isRefreshing.value) {
      refreshData(true) // 静默刷新
    }
  }, 30000) // 30秒刷新一次
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

/**
 * 刷新数据
 * @param {boolean} silent 是否静默刷新
 */
const refreshData = async (silent = false) => {
  if (!silent) {
    isRefreshing.value = true
  }
  
  try {
    await systemStore.refreshAllData()
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    if (!silent) {
      isRefreshing.value = false
    }
  }
}

/**
 * 格式化时间
 * @param {Date} date 时间对象
 */
const formatTime = (date) => {
  if (!date) return '未知'
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date)
}

/**
 * 格式化字节数
 * @param {number} bytes 字节数
 */
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 获取CPU状态样式类
 * @param {number} usage CPU使用率
 */
const getCpuStatusClass = (usage) => {
  if (usage < 50) return 'success'
  if (usage < 80) return 'warning'
  return 'danger'
}

/**
 * 获取内存状态样式类
 * @param {number} usage 内存使用率
 */
const getMemoryStatusClass = (usage) => {
  if (usage < 70) return 'success'
  if (usage < 90) return 'warning'
  return 'danger'
}

/**
 * 获取磁盘状态样式类
 * @param {number} usage 磁盘使用率
 */
const getDiskStatusClass = (usage) => {
  if (usage < 80) return 'success'
  if (usage < 95) return 'warning'
  return 'danger'
}
</script>

<style lang="scss" scoped>
.dashboard {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color-page);
}

.dashboard-header {
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

    .system-status {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      font-size: 14px;

      .last-update {
        color: var(--el-text-color-secondary);
      }
    }
  }

  .header-right {
    display: flex;
    gap: var(--spacing-sm);
  }
}

.dashboard-content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.overview-section {
  .metric-card {
    min-height: 140px;
    
    .card-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100px;
    }
  }
}

.monitoring-section,
.control-section,
.logs-section {
  .dashboard-card {
    min-height: 300px;
  }
}

.ipmi-status {
  font-size: 14px;
}

// 响应式设计
@media (max-width: 1200px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);

    .header-right {
      align-self: flex-end;
    }
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    padding: var(--spacing-md);

    .header-left .page-title {
      font-size: 20px;
    }

    .header-right {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .dashboard-content {
    padding: var(--spacing-md);
  }

  .overview-section .metric-card {
    min-height: 120px;
    
    .card-content {
      height: 80px;
    }
  }
}
</style>