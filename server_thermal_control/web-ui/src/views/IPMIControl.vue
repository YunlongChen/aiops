<template>
  <div class="ipmi-control-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1>IPMI控制</h1>
        <p>服务器远程管理和监控</p>
      </div>
      <div class="header-actions">
        <el-button 
          :icon="Refresh" 
          @click="refreshData"
          :loading="refreshing"
        >
          刷新数据
        </el-button>
        <PermissionGuard permissions="ipmi:configure">
          <el-button 
            :icon="Setting" 
            @click="showConfigDialog = true"
          >
            IPMI配置
          </el-button>
        </PermissionGuard>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="page-content">
      <!-- 电源控制区域 -->
      <div class="power-control-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><SwitchButton /></el-icon>
              电源控制
            </span>
            <div class="power-status">
              <span 
                :class="['power-indicator', systemStore.serverStatus.powerState === 'on' ? 'on' : 'off']"
              >
                {{ systemStore.serverStatus.powerState === 'on' ? '开机' : '关机' }}
              </span>
            </div>
          </div>
          <div class="card-content">
            <div class="power-buttons">
              <PermissionGuard permissions="ipmi:power_control">
                <el-button
                  type="success"
                  size="large"
                  :icon="VideoPlay"
                  :disabled="!systemStore.ipmiConnection.isConnected || systemStore.serverStatus.powerState === 'on'"
                  :loading="powerOperationLoading === 'on'"
                  @click="handlePowerOperation('on')"
                >
                  开机
                </el-button>
                <el-button
                  type="warning"
                  size="large"
                  :icon="RefreshRight"
                  :disabled="!systemStore.ipmiConnection.isConnected || systemStore.serverStatus.powerState === 'off'"
                  :loading="powerOperationLoading === 'restart'"
                  @click="handlePowerOperation('restart')"
                >
                  重启
                </el-button>
                <el-button
                  type="info"
                  size="large"
                  :icon="SwitchButton"
                  :disabled="!systemStore.ipmiConnection.isConnected || systemStore.serverStatus.powerState === 'off'"
                  :loading="powerOperationLoading === 'shutdown'"
                  @click="handlePowerOperation('shutdown')"
                >
                  关机
                </el-button>
                <el-button
                  type="danger"
                  size="large"
                  :icon="Close"
                  :disabled="!systemStore.ipmiConnection.isConnected || systemStore.serverStatus.powerState === 'off'"
                  :loading="powerOperationLoading === 'force_off'"
                  @click="handlePowerOperation('force_off')"
                >
                  强制关机
                </el-button>
              </PermissionGuard>
            </div>
          </div>
        </div>
      </div>

      <!-- 远程控制区域 -->
      <div class="remote-control-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Monitor /></el-icon>
              远程控制
            </span>
          </div>
          <div class="card-content">
            <div class="remote-buttons">
              <PermissionGuard permissions="ipmi:remote_control">
                <el-button
                  type="primary"
                  size="large"
                  :icon="Monitor"
                  :disabled="!systemStore.ipmiConnection.isConnected"
                  @click="openRemoteConsole"
                >
                  远程控制台
                </el-button>
                <el-button
                  type="primary"
                  size="large"
                  :icon="FolderOpened"
                  :disabled="!systemStore.ipmiConnection.isConnected"
                  @click="openVirtualMedia"
                >
                  虚拟媒体
                </el-button>
                <el-button
                  type="primary"
                  size="large"
                  :icon="Setting"
                  :disabled="!systemStore.ipmiConnection.isConnected"
                  @click="openBIOSSetup"
                >
                  BIOS设置
                </el-button>
              </PermissionGuard>
            </div>
          </div>
        </div>
      </div>

      <!-- 传感器监控区域 -->
      <div class="sensor-monitoring-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><DataAnalysis /></el-icon>
              传感器监控
            </span>
          </div>
          <div class="card-content">
            <div class="sensor-grid">
              <!-- 温度传感器 -->
              <div class="sensor-group">
                <h4 class="sensor-group-title">温度传感器</h4>
                <div class="sensor-list">
                  <div 
                    v-for="sensor in temperatureSensors" 
                    :key="sensor.name"
                    class="sensor-item"
                  >
                    <div class="sensor-info">
                      <span class="sensor-name">{{ sensor.name }}</span>
                      <span 
                        :class="['sensor-status', getSensorStatusClass(sensor.status)]"
                      >
                        {{ sensor.status }}
                      </span>
                    </div>
                    <div class="sensor-value">
                      <span class="value">{{ sensor.value }}°C</span>
                      <el-progress
                        :percentage="getSensorPercentage(sensor.value, sensor.max)"
                        :color="getSensorColor(sensor.value, sensor.warning, sensor.critical)"
                        :show-text="false"
                        :stroke-width="4"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- 风扇传感器 -->
              <div class="sensor-group">
                <h4 class="sensor-group-title">风扇传感器</h4>
                <div class="sensor-list">
                  <div 
                    v-for="sensor in fanSensors" 
                    :key="sensor.name"
                    class="sensor-item"
                  >
                    <div class="sensor-info">
                      <span class="sensor-name">{{ sensor.name }}</span>
                      <span 
                        :class="['sensor-status', getSensorStatusClass(sensor.status)]"
                      >
                        {{ sensor.status }}
                      </span>
                    </div>
                    <div class="sensor-value">
                      <span class="value">{{ sensor.value }} RPM</span>
                      <el-progress
                        :percentage="getSensorPercentage(sensor.value, sensor.max)"
                        :color="getSensorColor(sensor.value, sensor.warning, sensor.critical)"
                        :show-text="false"
                        :stroke-width="4"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <!-- 电压传感器 -->
              <div class="sensor-group">
                <h4 class="sensor-group-title">电压传感器</h4>
                <div class="sensor-list">
                  <div 
                    v-for="sensor in voltageSensors" 
                    :key="sensor.name"
                    class="sensor-item"
                  >
                    <div class="sensor-info">
                      <span class="sensor-name">{{ sensor.name }}</span>
                      <span 
                        :class="['sensor-status', getSensorStatusClass(sensor.status)]"
                      >
                        {{ sensor.status }}
                      </span>
                    </div>
                    <div class="sensor-value">
                      <span class="value">{{ sensor.value }}V</span>
                      <el-progress
                        :percentage="getSensorPercentage(sensor.value, sensor.max)"
                        :color="getSensorColor(sensor.value, sensor.warning, sensor.critical)"
                        :show-text="false"
                        :stroke-width="4"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统事件日志 -->
      <div class="system-events-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Document /></el-icon>
              系统事件日志
            </span>
            <div class="card-actions">
              <PermissionGuard permissions="ipmi:view_logs">
                <el-button 
                  size="small" 
                  :icon="Refresh"
                  @click="refreshSystemEvents"
                >
                  刷新
                </el-button>
              </PermissionGuard>
              <PermissionGuard permissions="ipmi:manage_logs">
                <el-button 
                  size="small" 
                  :icon="Delete"
                  type="danger"
                  @click="clearSystemEvents"
                >
                  清空日志
                </el-button>
              </PermissionGuard>
            </div>
          </div>
          <div class="card-content">
            <div class="events-list" v-if="ipmiStore.eventLogs.length > 0">
              <div 
                v-for="event in ipmiStore.eventLogs" 
                :key="event.id"
                :class="['event-item', `event-${event.level}`]"
              >
                <div class="event-time">{{ formatTime(event.timestamp) }}</div>
                <div class="event-level">{{ event.level.toUpperCase() }}</div>
                <div class="event-message">{{ event.message }}</div>
              </div>
            </div>
            <div v-else class="empty-state">
              <el-icon><Document /></el-icon>
              <span>暂无系统事件</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- 确认对话框 -->
    <ConfirmDialog
      v-model="showConfirmDialog"
      v-bind="confirmDialogProps"
      @confirm="handleConfirmDialogConfirm"
      @cancel="handleConfirmDialogCancel"
    />
  </div>
</template>

<script setup>
/**
 * IPMI控制页面
 * 提供服务器远程管理和监控功能，集成权限控制和安全确认
 */
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useSystemStore } from '../stores/system'
import { useIPMIStore } from '@/stores/ipmi'
import { useSecurityStore } from '@/stores/security'
import PermissionGuard from '@/components/PermissionGuard.vue'
import ConfirmDialog from '@/components/ConfirmDialog.vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { 
  Setting, Refresh, Connection, SwitchButton, VideoPlay, 
  RefreshRight, Close, Monitor, FolderOpened, DataAnalysis,
  Document, Delete, Sunny
} from '@element-plus/icons-vue'

const systemStore = useSystemStore()
const ipmiStore = useIPMIStore()
const securityStore = useSecurityStore()

// 响应式数据
const showConfigDialog = ref(false)
const showConfirmDialog = ref(false)
const confirmDialogProps = ref({})
const pendingOperation = ref(null)
const refreshing = ref(false)
const powerOperationLoading = ref('')

// 传感器数据
const temperatureSensors = ref([
  { name: 'CPU温度', value: 45, max: 100, warning: 70, critical: 85, status: 'normal' },
  { name: 'GPU温度', value: 52, max: 100, warning: 80, critical: 90, status: 'normal' },
  { name: '主板温度', value: 38, max: 100, warning: 60, critical: 75, status: 'normal' },
  { name: '内存温度', value: 42, max: 100, warning: 65, critical: 80, status: 'normal' }
])

const fanSensors = ref([
  { name: 'CPU风扇', value: 2400, max: 4000, warning: 1000, critical: 500, status: 'normal' },
  { name: '系统风扇1', value: 1800, max: 3000, warning: 800, critical: 400, status: 'normal' },
  { name: '系统风扇2', value: 1950, max: 3000, warning: 800, critical: 400, status: 'normal' }
])

const voltageSensors = ref([
  { name: '+12V', value: 12.1, max: 13.2, warning: 11.4, critical: 10.8, status: 'normal' },
  { name: '+5V', value: 5.02, max: 5.5, warning: 4.75, critical: 4.5, status: 'normal' },
  { name: '+3.3V', value: 3.31, max: 3.63, warning: 3.14, critical: 2.97, status: 'normal' }
])

const systemEvents = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 300000),
    level: 'info',
    message: '系统启动完成'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 600000),
    level: 'warning',
    message: 'CPU温度达到警告阈值'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 900000),
    level: 'error',
    message: '风扇转速异常'
  }
])

let refreshTimer = null

onMounted(() => {
  refreshData()
  
  // 设置自动刷新
  refreshTimer = setInterval(() => {
    if (!isRefreshing.value) {
      refreshData(true)
    }
  }, 15000) // 15秒刷新一次
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
    refreshing.value = true
  }
  
  try {
    await Promise.all([
      systemStore.fetchIPMIStatus(),
      systemStore.fetchSystemStatus(),
      refreshSensorData()
    ])
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    if (!silent) {
      refreshing.value = false
    }
  }
}

/**
 * 连接IPMI
 */
const openRemoteConsole = () => {
  handleRemoteControl('console')
}

const openVirtualMedia = () => {
  handleRemoteControl('virtual_media')
}

const openBIOSSetup = () => {
  handleRemoteControl('bios')
}

/**
 * 处理电源操作
 * @param {string} operation 操作类型
 */
const handlePowerOperation = async (operation) => {
  // 检查权限
  if (!securityStore.hasPermission('ipmi:power_control')) {
    ElMessage.error('您没有权限执行此操作')
    return
  }
  
  // 危险操作需要确认
  const dangerousOps = ['force_off', 'restart']
  const isDangerous = dangerousOps.includes(operation)
  
  if (isDangerous || securityStore.securitySettings.confirmDangerousOperations) {
    const operationNames = {
      'on': '开机',
      'restart': '重启服务器',
      'shutdown': '关机',
      'force_off': '强制关机'
    }
    
    const risks = {
      'restart': ['可能导致正在运行的服务中断', '未保存的数据可能丢失'],
      'force_off': ['可能导致数据损坏', '正在运行的进程将被强制终止', '文件系统可能出现错误']
    }
    
    confirmDialogProps.value = {
      title: `确认${operationNames[operation]}`,
      message: `您确定要${operationNames[operation]}吗？`,
      type: isDangerous ? 'error' : 'warning',
      operation: operation,
      isDangerous,
      requireConfirmText: isDangerous,
      confirmTextValue: 'CONFIRM',
      risks: risks[operation] || [],
      countdownSeconds: isDangerous ? 5 : 0
    }
    
    pendingOperation.value = { type: 'power', operation }
    showConfirmDialog.value = true
    return
  }
  
  // 直接执行操作
  await executePowerOperation(operation)
}

/**
 * 执行电源操作
 * @param {string} operation 操作类型
 */
const executePowerOperation = async (operation) => {
  const operationNames = {
    on: '开机',
    restart: '重启',
    shutdown: '关机',
    force_off: '强制关机'
  }
  
  const operationName = operationNames[operation]
  
  try {
    powerOperationLoading.value = operation
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success(`${operationName}操作已执行`)
    
    // 记录操作日志
    securityStore.logOperation('ipmi_power_control', `执行电源操作: ${operationName}`, {
      operation,
      timestamp: new Date().toISOString()
    })
    
    // 刷新服务器状态
    await systemStore.fetchSystemStatus()
    
  } catch (error) {
    ElMessage.error(`${operationName}操作失败: ${error.message}`)
  } finally {
    powerOperationLoading.value = ''
  }
}

/**
 * 处理远程控制操作
 */
const handleRemoteControl = async (type) => {
  // 检查权限
  if (!securityStore.hasPermission('ipmi:remote_control')) {
    ElMessage.error('您没有权限执行此操作')
    return
  }
  
  try {
    await ipmiStore.performRemoteControl(type)
    
    const typeNames = {
      'console': '远程控制台',
      'virtual_media': '虚拟媒体',
      'bios': 'BIOS设置'
    }
    
    ElMessage.success(`${typeNames[type]}已启动`)
    
    // 记录操作日志
    securityStore.logOperation('ipmi_remote_control', `启动远程控制: ${typeNames[type]}`, {
      type,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    ElMessage.error(`操作失败: ${error.message}`)
  }
}

/**
 * 处理清空日志操作
 */
const handleClearLogs = async () => {
  // 检查权限
  if (!securityStore.hasPermission('ipmi:manage_logs')) {
    ElMessage.error('您没有权限执行此操作')
    return
  }
  
  // 需要确认
  confirmDialogProps.value = {
    title: '确认清空系统事件日志',
    message: '此操作将清空所有系统事件日志，无法恢复。',
    type: 'warning',
    operation: 'clear_logs',
    isDangerous: true,
    requireConfirmText: true,
    confirmTextValue: 'CLEAR',
    risks: ['所有历史事件记录将被永久删除', '可能影响故障排查和审计'],
    countdownSeconds: 3
  }
  
  pendingOperation.value = { type: 'clear_logs' }
  showConfirmDialog.value = true
}

/**
 * 执行清空日志操作
 */
const executeClearLogs = async () => {
  try {
    await ipmiStore.clearEventLogs()
    ElMessage.success('系统事件日志已清空')
    
    // 记录操作日志
    securityStore.logOperation('ipmi_clear_logs', '清空系统事件日志', {
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    ElMessage.error(`清空日志失败: ${error.message}`)
  }
}

/**
 * 刷新传感器数据
 */
const refreshSensorData = async () => {
  // 模拟传感器数据更新
  temperatureSensors.value.forEach(sensor => {
    sensor.value = Math.max(30, sensor.value + (Math.random() - 0.5) * 4)
    sensor.status = getSensorStatus(sensor.value, sensor.warning, sensor.critical)
  })
  
  fanSensors.value.forEach(sensor => {
    sensor.value = Math.max(500, sensor.value + (Math.random() - 0.5) * 200)
    sensor.status = getSensorStatus(sensor.value, sensor.warning, sensor.critical, true)
  })
  
  voltageSensors.value.forEach(sensor => {
    sensor.value = Math.max(0, sensor.value + (Math.random() - 0.5) * 0.1)
    sensor.status = getSensorStatus(sensor.value, sensor.warning, sensor.critical)
  })
}

/**
 * 获取传感器状态
 * @param {number} value 当前值
 * @param {number} warning 警告阈值
 * @param {number} critical 严重阈值
 * @param {boolean} reverse 是否反向判断（风扇等）
 */
const getSensorStatus = (value, warning, critical, reverse = false) => {
  if (reverse) {
    if (value <= critical) return 'critical'
    if (value <= warning) return 'warning'
    return 'normal'
  } else {
    if (value >= critical) return 'critical'
    if (value >= warning) return 'warning'
    return 'normal'
  }
}

/**
 * 获取传感器状态样式类
 * @param {string} status 状态
 */
const getSensorStatusClass = (status) => {
  return {
    normal: 'normal',
    warning: 'warning',
    critical: 'critical'
  }[status] || 'normal'
}

/**
 * 获取传感器百分比
 * @param {number} value 当前值
 * @param {number} max 最大值
 */
const getSensorPercentage = (value, max) => {
  return Math.min(100, (value / max) * 100)
}

/**
 * 获取传感器颜色
 * @param {number} value 当前值
 * @param {number} warning 警告阈值
 * @param {number} critical 严重阈值
 */
const getSensorColor = (value, warning, critical) => {
  if (value >= critical) return '#F56C6C'
  if (value >= warning) return '#E6A23C'
  return '#67C23A'
}

/**
 * 刷新数据
 */
const refreshAllData = async () => {
  try {
    refreshing.value = true
    await ipmiStore.refreshAllData()
    ElMessage.success('数据已刷新')
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.message}`)
  } finally {
    refreshing.value = false
  }
}

/**
 * 刷新事件日志
 */
const refreshEventLogs = async () => {
  try {
    await ipmiStore.fetchEventLogs()
    ElMessage.success('事件日志已刷新')
  } catch (error) {
    ElMessage.error(`刷新失败: ${error.message}`)
  }
}

/**
 * 刷新系统事件
 */
const refreshSystemEvents = async () => {
  await refreshEventLogs()
}

/**
 * 清空系统事件
 */
const clearSystemEvents = async () => {
  handleClearLogs()
}

/**
 * 处理确认对话框确认
 */
const handleConfirmDialogConfirm = async (data) => {
  showConfirmDialog.value = false
  
  if (!pendingOperation.value) return
  
  try {
    const { type, operation } = pendingOperation.value
    
    switch (type) {
      case 'power':
        await executePowerOperation(operation)
        break
      case 'clear_logs':
        await executeClearLogs()
        break
      default:
        console.warn('未知的操作类型:', type)
    }
  } catch (error) {
    ElMessage.error(`操作失败: ${error.message}`)
  } finally {
    pendingOperation.value = null
  }
}

/**
 * 处理确认对话框取消
 */
const handleConfirmDialogCancel = () => {
  showConfirmDialog.value = false
  pendingOperation.value = null
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
.ipmi-control {
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

    .connection-status {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);
      font-size: 14px;

      .connection-info {
        color: var(--el-text-color-secondary);
      }
    }
  }

  .header-right {
    display: flex;
    gap: var(--spacing-sm);
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

.power-buttons {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.remote-buttons {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.power-indicator {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 600;

  &.on {
    background: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }

  &.off {
    background: var(--el-color-info-light-9);
    color: var(--el-color-info);
  }
}

.sensor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

.sensor-group {
  .sensor-group-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 0 0 var(--spacing-md) 0;
    padding-bottom: var(--spacing-sm);
    border-bottom: 2px solid var(--el-color-primary);
  }
}

.sensor-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.sensor-item {
  padding: var(--spacing-md);
  background: var(--el-bg-color-page);
  border-radius: var(--border-radius);
  border: 1px solid var(--el-border-color-lighter);

  .sensor-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);

    .sensor-name {
      font-weight: 500;
      color: var(--el-text-color-primary);
    }

    .sensor-status {
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;

      &.normal {
        background: var(--el-color-success-light-9);
        color: var(--el-color-success);
      }

      &.warning {
        background: var(--el-color-warning-light-9);
        color: var(--el-color-warning);
      }

      &.critical {
        background: var(--el-color-danger-light-9);
        color: var(--el-color-danger);
      }
    }
  }

  .sensor-value {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);

    .value {
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
    }
  }
}

.events-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.event-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius);
  border-left: 4px solid;

  &.event-info {
    border-left-color: var(--el-color-info);
    background: var(--el-color-info-light-9);
  }

  &.event-warning {
    border-left-color: var(--el-color-warning);
    background: var(--el-color-warning-light-9);
  }

  &.event-error {
    border-left-color: var(--el-color-danger);
    background: var(--el-color-danger-light-9);
  }

  .event-time {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    white-space: nowrap;
    min-width: 140px;
  }

  .event-level {
    font-size: 12px;
    font-weight: 600;
    min-width: 60px;
  }

  .event-message {
    flex: 1;
    font-size: 14px;
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

  .sensor-grid {
    grid-template-columns: 1fr;
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

  .page-content {
    padding: var(--spacing-md);
  }

  .power-buttons,
  .remote-buttons {
    flex-direction: column;

    .el-button {
      width: 100%;
    }
  }

  .event-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);

    .event-time,
    .event-level {
      min-width: auto;
    }
  }
}
</style>