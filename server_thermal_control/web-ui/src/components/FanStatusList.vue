<template>
  <div class="fan-status-list">
    <div v-if="systemStore.fanStatus.fans.length === 0" class="empty-state">
      <el-icon><WindPower /></el-icon>
      <p>暂无风扇数据</p>
    </div>
    
    <div v-else class="fan-list">
      <div 
        v-for="fan in displayFans" 
        :key="fan.id"
        class="fan-item"
      >
        <div class="fan-info">
          <div class="fan-header">
            <span class="fan-name">{{ fan.name }}</span>
            <span 
              :class="['fan-status', getFanStatusClass(fan.status)]"
            >
              {{ getFanStatusText(fan.status) }}
            </span>
          </div>
          
          <div class="fan-metrics">
            <div class="metric">
              <span class="metric-label">转速</span>
              <span class="metric-value">
                {{ fan.rpm }} 
                <span class="metric-unit">RPM</span>
              </span>
            </div>
            
            <div class="metric">
              <span class="metric-label">占空比</span>
              <span class="metric-value">
                {{ fan.dutyCycle }}
                <span class="metric-unit">%</span>
              </span>
            </div>
            
            <div class="metric" v-if="!compact">
              <span class="metric-label">目标转速</span>
              <span class="metric-value">
                {{ fan.targetRpm }}
                <span class="metric-unit">RPM</span>
              </span>
            </div>
          </div>
        </div>
        
        <!-- 风扇转速进度条 -->
        <div class="fan-progress" v-if="!compact">
          <el-progress
            :percentage="getFanSpeedPercentage(fan)"
            :color="getFanProgressColor(fan)"
            :show-text="false"
            :stroke-width="6"
          />
        </div>
        
        <!-- 风扇控制按钮 -->
        <div class="fan-controls" v-if="!compact && canControlFan">
          <el-button-group size="small">
            <el-button 
              :icon="Minus"
              @click="adjustFanSpeed(fan.id, -10)"
              :disabled="fan.dutyCycle <= 10"
            />
            <el-button 
              :icon="Plus"
              @click="adjustFanSpeed(fan.id, 10)"
              :disabled="fan.dutyCycle >= 100"
            />
          </el-button-group>
        </div>
      </div>
    </div>
    
    <!-- 查看更多按钮 -->
    <div v-if="compact && systemStore.fanStatus.fans.length > maxDisplayCount" class="view-more">
      <el-button 
        text 
        type="primary" 
        @click="$router.push('/monitoring')"
      >
        查看全部 {{ systemStore.fanData.length }} 个风扇
      </el-button>
    </div>
  </div>
</template>

<script setup>
/**
 * 风扇状态列表组件
 * 展示风扇运行状态和控制功能
 */
import { computed } from 'vue'
import { useSystemStore } from '@/stores/system'
import { WindPower, Plus, Minus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  compact: {
    type: Boolean,
    default: false
  },
  maxDisplayCount: {
    type: Number,
    default: 3
  }
})

const systemStore = useSystemStore()


// 计算属性
const displayFans = computed(() => {
  const fans = systemStore.fanStatus.fans
  return props.compact ? fans.slice(0, props.maxDisplayCount) : fans
})

const canControlFan = computed(() => {
  return systemStore.ipmiStatus.connected && systemStore.serverStatus.isOnline
})

/**
 * 获取风扇状态样式类
 * @param {string} status 风扇状态
 */
const getFanStatusClass = (status) => {
  switch (status) {
    case 'normal':
      return 'success'
    case 'warning':
      return 'warning'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

/**
 * 获取风扇状态文本
 * @param {string} status 风扇状态
 */
const getFanStatusText = (status) => {
  switch (status) {
    case 'normal':
      return '正常'
    case 'warning':
      return '警告'
    case 'error':
      return '故障'
    default:
      return '未知'
  }
}

/**
 * 获取风扇转速百分比
 * @param {Object} fan 风扇对象
 */
const getFanSpeedPercentage = (fan) => {
  const maxRpm = fan.maxRpm || 3000 // 默认最大转速
  return Math.min((fan.rpm / maxRpm) * 100, 100)
}

/**
 * 获取风扇进度条颜色
 * @param {Object} fan 风扇对象
 */
const getFanProgressColor = (fan) => {
  const percentage = getFanSpeedPercentage(fan)
  if (percentage < 30) return '#67C23A'
  if (percentage < 70) return '#E6A23C'
  return '#F56C6C'
}

/**
 * 调整风扇转速
 * @param {string} fanId 风扇ID
 * @param {number} adjustment 调整值
 */
const adjustFanSpeed = async (fanId, adjustment) => {
  try {
    await ElMessageBox.confirm(
      `确定要调整风扇转速吗？这可能会影响系统散热效果。`,
      '风扇控制确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 调用API调整风扇转速
    await systemStore.adjustFanSpeed(fanId, adjustment)
    
    ElMessage.success('风扇转速调整成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('调整风扇转速失败:', error)
      ElMessage.error('调整风扇转速失败')
    }
  }
}
</script>

<style lang="scss" scoped>
.fan-status-list {
  width: 100%;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  color: var(--el-text-color-secondary);

  .el-icon {
    font-size: 48px;
    margin-bottom: var(--spacing-md);
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}

.fan-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.fan-item {
  padding: var(--spacing-md);
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-lighter);
  border-radius: var(--border-radius);
  transition: all 0.3s ease;

  &:hover {
    border-color: var(--el-border-color);
    box-shadow: var(--shadow-light);
  }
}

.fan-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.fan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .fan-name {
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .fan-status {
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;

    &.success {
      background: var(--el-color-success-light-9);
      color: var(--el-color-success);
    }

    &.warning {
      background: var(--el-color-warning-light-9);
      color: var(--el-color-warning);
    }

    &.danger {
      background: var(--el-color-danger-light-9);
      color: var(--el-color-danger);
    }

    &.info {
      background: var(--el-color-info-light-9);
      color: var(--el-color-info);
    }
  }
}

.fan-metrics {
  display: flex;
  gap: var(--spacing-lg);

  .metric {
    display: flex;
    flex-direction: column;
    gap: 2px;

    .metric-label {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    .metric-value {
      font-size: 14px;
      font-weight: 600;
      color: var(--el-text-color-primary);

      .metric-unit {
        font-size: 12px;
        font-weight: normal;
        color: var(--el-text-color-secondary);
      }
    }
  }
}

.fan-progress {
  margin-top: var(--spacing-sm);
}

.fan-controls {
  margin-top: var(--spacing-sm);
  display: flex;
  justify-content: flex-end;
}

.view-more {
  text-align: center;
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: var(--spacing-md);
}

// 响应式设计
@media (max-width: 768px) {
  .fan-metrics {
    flex-wrap: wrap;
    gap: var(--spacing-md);

    .metric {
      min-width: 80px;
    }
  }

  .fan-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }
}
</style>