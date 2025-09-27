<template>
  <div class="server-status">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Monitor /></el-icon>
          服务器状态
        </h1>
        <div class="status-summary">
          <span 
            :class="['status-indicator', systemStore.serverStatus.isOnline ? 'online' : 'offline']"
          >
            {{ systemStore.serverStatus.isOnline ? '在线' : '离线' }}
          </span>
          <span class="uptime">
            运行时间: {{ formatUptime(systemStore.serverStatus.uptime) }}
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
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="page-content">
      <!-- 系统信息卡片 -->
      <div class="system-info-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><InfoFilled /></el-icon>
              系统信息
            </span>
          </div>
          <div class="card-content">
            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">主机名</span>
                <span class="info-value">{{ systemStore.systemInfo.hostname || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">操作系统</span>
                <span class="info-value">{{ systemStore.systemInfo.os || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">CPU型号</span>
                <span class="info-value">{{ systemStore.systemInfo.cpuModel || '未知' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">CPU核心数</span>
                <span class="info-value">{{ systemStore.systemInfo.cpuCores || 0 }} 核心</span>
              </div>
              <div class="info-item">
                <span class="info-label">总内存</span>
                <span class="info-value">{{ formatBytes(systemStore.systemMetrics.memory.total) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">总磁盘</span>
                <span class="info-value">{{ formatBytes(systemStore.systemMetrics.disk.total) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 资源使用情况 -->
      <div class="resource-section">
        <div class="grid grid-3">
          <!-- CPU使用率 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Cpu /></el-icon>
                CPU使用率
              </span>
            </div>
            <div class="card-content">
              <div class="resource-chart">
                <el-progress
                  type="circle"
                  :percentage="systemStore.systemMetrics.cpu.usage"
                  :color="getCpuProgressColor(systemStore.systemMetrics.cpu.usage)"
                  :width="120"
                  :stroke-width="8"
                >
                  <template #default="{ percentage }">
                    <span class="progress-text">{{ percentage }}%</span>
                  </template>
                </el-progress>
              </div>
              <div class="resource-details">
                <div class="detail-item">
                  <span class="detail-label">用户态</span>
                  <span class="detail-value">{{ systemStore.systemMetrics.cpu.user }}%</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">系统态</span>
                  <span class="detail-value">{{ systemStore.systemMetrics.cpu.system }}%</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">空闲</span>
                  <span class="detail-value">{{ systemStore.systemMetrics.cpu.idle }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 内存使用率 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Grid /></el-icon>
                内存使用率
              </span>
            </div>
            <div class="card-content">
              <div class="resource-chart">
                <el-progress
                  type="circle"
                  :percentage="systemStore.memoryUsagePercentage"
                  :color="getMemoryProgressColor(systemStore.memoryUsagePercentage)"
                  :width="120"
                  :stroke-width="8"
                >
                  <template #default="{ percentage }">
                    <span class="progress-text">{{ percentage }}%</span>
                  </template>
                </el-progress>
              </div>
              <div class="resource-details">
                <div class="detail-item">
                  <span class="detail-label">已使用</span>
                  <span class="detail-value">{{ formatBytes(systemStore.systemMetrics.memory.used) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">可用</span>
                  <span class="detail-value">{{ formatBytes(systemStore.systemMetrics.memory.available) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">缓存</span>
                  <span class="detail-value">{{ formatBytes(systemStore.systemMetrics.memory.cached) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 磁盘使用率 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Coin /></el-icon>
                磁盘使用率
              </span>
            </div>
            <div class="card-content">
              <div class="resource-chart">
                <el-progress
                  type="circle"
                  :percentage="systemStore.diskUsagePercentage"
                  :color="getDiskProgressColor(systemStore.diskUsagePercentage)"
                  :width="120"
                  :stroke-width="8"
                >
                  <template #default="{ percentage }">
                    <span class="progress-text">{{ percentage }}%</span>
                  </template>
                </el-progress>
              </div>
              <div class="resource-details">
                <div class="detail-item">
                  <span class="detail-label">已使用</span>
                  <span class="detail-value">{{ formatBytes(systemStore.systemMetrics.disk.used) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">可用</span>
                  <span class="detail-value">{{ formatBytes(systemStore.systemMetrics.disk.available) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">I/O读取</span>
                  <span class="detail-value">{{ formatBytes(systemStore.systemMetrics.disk.readBytes) }}/s</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 网络状态 -->
      <div class="network-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Connection /></el-icon>
              网络状态
            </span>
          </div>
          <div class="card-content">
            <div class="network-grid">
              <div class="network-item">
                <div class="network-header">
                  <span class="network-name">{{ systemStore.systemMetrics.network.interface || 'eth0' }}</span>
                  <span 
                    :class="['network-status', systemStore.systemMetrics.network.isUp ? 'online' : 'offline']"
                  >
                    {{ systemStore.systemMetrics.network.isUp ? '已连接' : '未连接' }}
                  </span>
                </div>
                <div class="network-metrics">
                  <div class="metric-row">
                    <div class="metric">
                      <span class="metric-label">上传速度</span>
                      <span class="metric-value">{{ formatBytes(systemStore.systemMetrics.network.uploadSpeed) }}/s</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">下载速度</span>
                      <span class="metric-value">{{ formatBytes(systemStore.systemMetrics.network.downloadSpeed) }}/s</span>
                    </div>
                  </div>
                  <div class="metric-row">
                    <div class="metric">
                      <span class="metric-label">总上传</span>
                      <span class="metric-value">{{ formatBytes(systemStore.systemMetrics.network.totalUploaded) }}</span>
                    </div>
                    <div class="metric">
                      <span class="metric-label">总下载</span>
                      <span class="metric-value">{{ formatBytes(systemStore.systemMetrics.network.totalDownloaded) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 进程信息 -->
      <div class="process-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><List /></el-icon>
              进程信息
            </span>
          </div>
          <div class="card-content">
            <div class="process-stats">
              <div class="stat-item">
                <span class="stat-label">总进程数</span>
                <span class="stat-value">{{ systemStore.systemMetrics.processes.total || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">运行中</span>
                <span class="stat-value">{{ systemStore.systemMetrics.processes.running || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">休眠中</span>
                <span class="stat-value">{{ systemStore.systemMetrics.processes.sleeping || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">僵尸进程</span>
                <span class="stat-value">{{ systemStore.systemMetrics.processes.zombie || 0 }}</span>
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
 * 服务器状态详情页面
 * 展示详细的服务器硬件和系统信息
 */
import { ref, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '../stores/system'
import { 
  Monitor, Refresh, InfoFilled, Cpu, Grid, 
  Coin, Connection, List 
} from '@element-plus/icons-vue'

const systemStore = useSystemStore()
const isRefreshing = ref(false)
let refreshTimer = null

onMounted(() => {
  refreshData()
  
  // 设置自动刷新
  refreshTimer = setInterval(() => {
    if (!isRefreshing.value) {
      refreshData(true)
    }
  }, 10000) // 10秒刷新一次
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
    await Promise.all([
      systemStore.fetchSystemInfo(),
      systemStore.fetchSystemMetrics(),
      systemStore.fetchSystemStatus()
    ])
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    if (!silent) {
      isRefreshing.value = false
    }
  }
}

/**
 * 格式化运行时间
 * @param {number} seconds 秒数
 */
const formatUptime = (seconds) => {
  if (!seconds) return '未知'
  
  const days = Math.floor(seconds / 86400)
  const hours = Math.floor((seconds % 86400) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (days > 0) {
    return `${days}天 ${hours}小时 ${minutes}分钟`
  } else if (hours > 0) {
    return `${hours}小时 ${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
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
 * 获取CPU进度条颜色
 * @param {number} usage CPU使用率
 */
const getCpuProgressColor = (usage) => {
  if (usage < 50) return '#67C23A'
  if (usage < 80) return '#E6A23C'
  return '#F56C6C'
}

/**
 * 获取内存进度条颜色
 * @param {number} usage 内存使用率
 */
const getMemoryProgressColor = (usage) => {
  if (usage < 70) return '#67C23A'
  if (usage < 90) return '#E6A23C'
  return '#F56C6C'
}

/**
 * 获取磁盘进度条颜色
 * @param {number} usage 磁盘使用率
 */
const getDiskProgressColor = (usage) => {
  if (usage < 80) return '#67C23A'
  if (usage < 95) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style lang="scss" scoped>
.server-status {
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

    .status-summary {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      font-size: 14px;

      .uptime {
        color: var(--el-text-color-secondary);
      }
    }
  }
}

.page-content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) 0;
  border-bottom: 1px solid var(--el-border-color-lighter);

  &:last-child {
    border-bottom: none;
  }

  .info-label {
    color: var(--el-text-color-secondary);
    font-size: 14px;
  }

  .info-value {
    color: var(--el-text-color-primary);
    font-weight: 500;
  }
}

.resource-chart {
  display: flex;
  justify-content: center;
  margin-bottom: var(--spacing-md);

  .progress-text {
    font-size: 16px;
    font-weight: 600;
  }
}

.resource-details {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .detail-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .detail-value {
    font-size: 12px;
    color: var(--el-text-color-primary);
    font-weight: 500;
  }
}

.network-grid {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.network-item {
  padding: var(--spacing-md);
  background: var(--el-bg-color-page);
  border-radius: var(--border-radius);
  border: 1px solid var(--el-border-color-lighter);
}

.network-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);

  .network-name {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .network-status {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;

    &.online {
      background: var(--el-color-success-light-9);
      color: var(--el-color-success);
    }

    &.offline {
      background: var(--el-color-danger-light-9);
      color: var(--el-color-danger);
    }
  }
}

.network-metrics {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.metric-row {
  display: flex;
  gap: var(--spacing-lg);
}

.metric {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;

  .metric-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .metric-value {
    font-size: 14px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
}

.process-stats {
  display: flex;
  justify-content: space-around;
  gap: var(--spacing-md);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);

  .stat-label {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }

  .stat-value {
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
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
    }
  }

  .page-content {
    padding: var(--spacing-md);
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .metric-row {
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .process-stats {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>