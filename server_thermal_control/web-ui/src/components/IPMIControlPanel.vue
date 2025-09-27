<template>
  <div class="ipmi-control-panel">
    <!-- IPMI连接状态 -->
    <div class="connection-status">
      <div class="status-header">
        <h3>IPMI连接状态</h3>
        <el-button 
          :icon="Refresh" 
          size="small" 
          @click="refreshConnection"
          :loading="ipmiStore.connectionStatus.connecting"
        >
          刷新
        </el-button>
      </div>
      <div class="status-info">
        <el-tag 
          :type="ipmiStore.isConnected ? 'success' : 'danger'"
          size="large"
        >
          {{ ipmiStore.isConnected ? '已连接' : '未连接' }}
        </el-tag>
        <span class="host-info">{{ ipmiStore.connectionStatus.host }}:{{ ipmiStore.connectionStatus.port }}</span>
        <span class="last-check" v-if="ipmiStore.connectionStatus.lastCheck">
          最后检查: {{ formatTime(ipmiStore.connectionStatus.lastCheck) }}
        </span>
      </div>
      <div v-if="ipmiStore.connectionStatus.error" class="error-info">
        <el-alert 
          :title="ipmiStore.connectionStatus.error" 
          type="error" 
          :closable="false"
          show-icon
        />
      </div>
    </div>

    <!-- 电源控制 -->
    <div class="power-control">
      <div class="section-header">
        <h3>电源控制</h3>
        <el-tag 
          :type="ipmiStore.isPowerOn ? 'success' : 'info'"
          size="large"
        >
          {{ ipmiStore.isPowerOn ? '开机' : '关机' }}
        </el-tag>
      </div>
      <div class="power-info" v-if="ipmiStore.powerStatus.uptime">
        <span>运行时间: {{ formatUptime(ipmiStore.powerStatus.uptime) }}</span>
      </div>
      <div class="power-buttons">
        <el-button 
          type="success" 
          :icon="VideoPlay"
          @click="handlePowerControl('on')"
          :disabled="!ipmiStore.isConnected || ipmiStore.isPowerOn"
        >
          开机
        </el-button>
        <el-button 
          type="warning" 
          :icon="RefreshRight"
          @click="handlePowerControl('restart')"
          :disabled="!ipmiStore.isConnected || !ipmiStore.isPowerOn"
        >
          重启
        </el-button>
        <el-button 
          type="danger" 
          :icon="VideoPause"
          @click="handlePowerControl('off')"
          :disabled="!ipmiStore.isConnected || !ipmiStore.isPowerOn"
        >
          关机
        </el-button>
        <el-button 
          type="danger" 
          :icon="SwitchButton"
          @click="handlePowerControl('force_off')"
          :disabled="!ipmiStore.isConnected || !ipmiStore.isPowerOn"
          plain
        >
          强制关机
        </el-button>
      </div>
    </div>

    <!-- 远程控制 -->
    <div class="remote-control" v-if="!compact">
      <div class="section-header">
        <h3>远程控制</h3>
      </div>
      <div class="remote-buttons">
        <el-button 
          type="primary" 
          :icon="Monitor"
          @click="handleRemoteControl('console')"
          :disabled="!ipmiStore.isConnected"
        >
          远程控制台
        </el-button>
        <el-button 
          type="primary" 
          :icon="FolderOpened"
          @click="handleRemoteControl('virtual_media')"
          :disabled="!ipmiStore.isConnected"
        >
          虚拟媒体
        </el-button>
        <el-button 
          type="primary" 
          :icon="Setting"
          @click="handleRemoteControl('bios_setup')"
          :disabled="!ipmiStore.isConnected"
        >
          BIOS设置
        </el-button>
      </div>
    </div>

    <!-- 传感器监控 -->
    <div class="sensor-monitoring" v-if="!compact">
      <div class="section-header">
        <h3>传感器监控</h3>
        <el-button 
          :icon="Refresh" 
          size="small" 
          @click="refreshSensors"
        >
          刷新
        </el-button>
      </div>
      
      <!-- 温度传感器 -->
      <div class="sensor-group">
        <h4>温度传感器</h4>
        <div class="sensor-list">
          <div 
            v-for="sensor in ipmiStore.sensorData.temperature" 
            :key="sensor.id"
            class="sensor-item"
          >
            <div class="sensor-info">
              <span class="sensor-name">{{ sensor.name }}</span>
              <el-tag 
                :type="getSensorTagType(sensor.status)" 
                size="small"
              >
                {{ sensor.status }}
              </el-tag>
            </div>
            <div class="sensor-value">
              <span class="value">{{ sensor.value }}{{ sensor.unit }}</span>
              <el-progress 
                :percentage="getSensorPercentage(sensor)" 
                :color="getSensorColor(sensor.status)"
                :show-text="false"
                :stroke-width="6"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 电压传感器 -->
      <div class="sensor-group">
        <h4>电压传感器</h4>
        <div class="sensor-list">
          <div 
            v-for="sensor in ipmiStore.sensorData.voltage" 
            :key="sensor.id"
            class="sensor-item"
          >
            <div class="sensor-info">
              <span class="sensor-name">{{ sensor.name }}</span>
              <el-tag 
                :type="getSensorTagType(sensor.status)" 
                size="small"
              >
                {{ sensor.status }}
              </el-tag>
            </div>
            <div class="sensor-value">
              <span class="value">{{ sensor.value.toFixed(2) }}{{ sensor.unit }}</span>
              <el-progress 
                :percentage="getSensorPercentage(sensor)" 
                :color="getSensorColor(sensor.status)"
                :show-text="false"
                :stroke-width="6"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 风扇传感器 -->
      <div class="sensor-group">
        <h4>风扇传感器</h4>
        <div class="sensor-list">
          <div 
            v-for="sensor in ipmiStore.sensorData.fan" 
            :key="sensor.id"
            class="sensor-item"
          >
            <div class="sensor-info">
              <span class="sensor-name">{{ sensor.name }}</span>
              <el-tag 
                :type="getSensorTagType(sensor.status)" 
                size="small"
              >
                {{ sensor.status }}
              </el-tag>
            </div>
            <div class="sensor-value">
              <span class="value">{{ sensor.value }}{{ sensor.unit }}</span>
              <el-progress 
                :percentage="getSensorPercentage(sensor)" 
                :color="getSensorColor(sensor.status)"
                :show-text="false"
                :stroke-width="6"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 快速操作区域 -->
    <div class="quick-actions" v-if="compact">
      <el-button
        size="small"
        :icon="VideoCamera"
        :disabled="!canControlPower"
        @click="openRemoteConsole"
      >
        控制台
      </el-button>
      
      <el-button
        size="small"
        :icon="Odometer"
        @click="$router.push('/monitoring')"
      >
        传感器
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { 
  Refresh, 
  VideoPlay, 
  VideoPause, 
  RefreshRight, 
  SwitchButton,
  Monitor,
  FolderOpened,
  Setting
} from '@element-plus/icons-vue'
import { useIPMIStore } from '@/stores/ipmi'

const props = defineProps({
  compact: {
    type: Boolean,
    default: false
  }
})

const ipmiStore = useIPMIStore()

let refreshTimer = null

/**
 * 组件挂载时初始化
 */
onMounted(async () => {
  await ipmiStore.initializeIPMI()
  
  // 设置定时刷新
  refreshTimer = setInterval(() => {
    if (ipmiStore.isConnected) {
      ipmiStore.fetchSensorData()
    }
  }, 30000) // 30秒刷新一次
})

/**
 * 组件卸载时清理
 */
onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})

/**
 * 刷新IPMI连接
 */
const refreshConnection = async () => {
  await ipmiStore.checkConnection()
  if (ipmiStore.isConnected) {
    await ipmiStore.refreshAllData()
  }
}

/**
 * 刷新传感器数据
 */
const refreshSensors = async () => {
  await ipmiStore.fetchSensorData()
}

/**
 * 处理电源控制
 */
const handlePowerControl = async (action) => {
  await ipmiStore.powerControl(action)
}

/**
 * 处理远程控制
 */
const handleRemoteControl = async (action) => {
  await ipmiStore.remoteControlAction(action)
}

/**
 * 格式化时间
 */
const formatTime = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString()
}

/**
 * 格式化运行时间
 */
const formatUptime = (seconds) => {
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
 * 获取传感器标签类型
 */
const getSensorTagType = (status) => {
  switch (status) {
    case 'normal': return 'success'
    case 'warning': return 'warning'
    case 'critical': return 'danger'
    default: return 'info'
  }
}

/**
 * 获取传感器颜色
 */
const getSensorColor = (status) => {
  switch (status) {
    case 'normal': return '#67c23a'
    case 'warning': return '#e6a23c'
    case 'critical': return '#f56c6c'
    default: return '#909399'
  }
}

/**
 * 获取传感器百分比
 */
const getSensorPercentage = (sensor) => {
  if (sensor.unit === '°C') {
    // 温度传感器：基于阈值计算百分比
    return Math.min(100, (sensor.value / sensor.threshold.critical) * 100)
  } else if (sensor.unit === 'V') {
    // 电压传感器：基于标准值计算百分比
    const nominal = sensor.id.includes('12v') ? 12 : sensor.id.includes('cpu') ? 1.2 : 1.35
    return Math.min(100, (sensor.value / nominal) * 100)
  } else if (sensor.unit === 'RPM') {
    // 风扇传感器：基于最大转速计算百分比
    return Math.min(100, (sensor.value / 3000) * 100)
  } else if (sensor.unit === 'W') {
    // 功率传感器：基于阈值计算百分比
    return Math.min(100, (sensor.value / sensor.threshold.warning) * 100)
  }
  return 0
}
</script>

<style lang="scss" scoped>
.ipmi-control-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.connection-status {
  padding: var(--spacing-md);
  background: var(--el-bg-color-page);
  border-radius: var(--border-radius);
  border: 1px solid var(--el-border-color-lighter);

  .status-header {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
  }

  .status-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .status-info {
      font-size: 14px;
      color: var(--el-text-color-secondary);
    }
  }
}

.section-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 600;
  margin-bottom: var(--spacing-md);
  color: var(--el-text-color-primary);
}

.power-controls {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);

  .force-power-btn {
    align-self: flex-start;
  }
}

.remote-controls {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.sensor-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-md);
}

.sensor-item {
  padding: var(--spacing-md);
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: var(--border-radius);
  text-align: center;

  .sensor-name {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: var(--spacing-xs);
  }

  .sensor-value {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: var(--spacing-xs);

    &.success {
      color: var(--el-color-success);
    }

    &.warning {
      color: var(--el-color-warning);
    }

    &.danger {
      color: var(--el-color-danger);
    }
  }

  .sensor-status {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}

.quick-actions {
  display: flex;
  gap: var(--spacing-sm);
  justify-content: center;
}

// 响应式设计
@media (max-width: 768px) {
  .power-controls {
    .el-button-group {
      display: flex;
      flex-direction: column;

      .el-button {
        border-radius: var(--border-radius) !important;
        margin-bottom: var(--spacing-xs);
      }
    }
  }

  .remote-controls {
    flex-direction: column;
  }

  .sensor-grid {
    grid-template-columns: 1fr;
  }
}
</style>