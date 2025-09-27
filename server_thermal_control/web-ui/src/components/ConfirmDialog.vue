<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    center
    class="confirm-dialog"
  >
    <div class="confirm-content">
      <!-- 图标 -->
      <div class="confirm-icon">
        <el-icon :size="48" :color="iconColor">
          <component :is="iconComponent" />
        </el-icon>
      </div>
      
      <!-- 消息内容 -->
      <div class="confirm-message">
        <h3>{{ title }}</h3>
        <p v-if="message" class="message-text">{{ message }}</p>
        
        <!-- 详细信息 -->
        <div v-if="details" class="details-section">
          <el-collapse v-model="detailsVisible">
            <el-collapse-item title="查看详细信息" name="details">
              <div class="details-content">
                <div v-for="(value, key) in details" :key="key" class="detail-item">
                  <strong>{{ key }}:</strong> {{ value }}
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
        
        <!-- 危险操作警告 -->
        <el-alert
          v-if="isDangerous"
          title="警告：这是一个危险操作"
          type="error"
          :closable="false"
          show-icon
          class="danger-alert"
        >
          <template #default>
            <p>此操作可能会造成不可逆的影响，请确认您了解操作的后果。</p>
            <ul v-if="risks && risks.length > 0">
              <li v-for="risk in risks" :key="risk">{{ risk }}</li>
            </ul>
          </template>
        </el-alert>
        
        <!-- 确认输入 -->
        <div v-if="requireConfirmText" class="confirm-input">
          <p class="confirm-prompt">
            请输入 <code>{{ confirmText }}</code> 以确认操作：
          </p>
          <el-input
            v-model="inputConfirmText"
            :placeholder="`请输入 ${confirmText}`"
            size="large"
            @keyup.enter="handleConfirm"
          />
        </div>
        
        <!-- 密码确认 -->
        <div v-if="requirePassword" class="password-confirm">
          <p class="confirm-prompt">请输入当前用户密码以确认操作：</p>
          <el-input
            v-model="inputPassword"
            type="password"
            placeholder="请输入密码"
            size="large"
            show-password
            @keyup.enter="handleConfirm"
          />
        </div>
        
        <!-- 倒计时 -->
        <div v-if="countdown > 0" class="countdown">
          <el-progress
            :percentage="countdownPercentage"
            :color="countdownColor"
            :stroke-width="6"
          />
          <p class="countdown-text">
            {{ countdown }} 秒后可以执行操作
          </p>
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="confirm-footer">
        <el-button
          size="large"
          @click="handleCancel"
        >
          {{ cancelText }}
        </el-button>
        <el-button
          :type="confirmButtonType"
          size="large"
          :loading="loading"
          :disabled="!canConfirm"
          @click="handleConfirm"
        >
          {{ loading ? '处理中...' : confirmText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
/**
 * 确认对话框组件
 * 用于危险操作的安全确认
 */
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { 
  Warning, 
  Delete, 
  RefreshRight, 
  SwitchButton, 
  Lock,
  QuestionFilled 
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '确认操作'
  },
  message: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'warning', // warning, error, info, success
    validator: (value) => ['warning', 'error', 'info', 'success'].includes(value)
  },
  operation: {
    type: String,
    default: 'default', // delete, restart, shutdown, reset, etc.
  },
  width: {
    type: String,
    default: '500px'
  },
  confirmText: {
    type: String,
    default: '确认'
  },
  cancelText: {
    type: String,
    default: '取消'
  },
  isDangerous: {
    type: Boolean,
    default: false
  },
  requireConfirmText: {
    type: Boolean,
    default: false
  },
  requirePassword: {
    type: Boolean,
    default: false
  },
  confirmTextValue: {
    type: String,
    default: 'CONFIRM'
  },
  details: {
    type: Object,
    default: null
  },
  risks: {
    type: Array,
    default: () => []
  },
  countdownSeconds: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

// 响应式数据
const inputConfirmText = ref('')
const inputPassword = ref('')
const detailsVisible = ref([])
const countdown = ref(0)
const countdownTimer = ref(null)

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const iconComponent = computed(() => {
  const iconMap = {
    delete: Delete,
    restart: RefreshRight,
    shutdown: SwitchButton,
    reset: RefreshRight,
    lock: Lock,
    warning: Warning,
    error: Warning,
    info: QuestionFilled,
    success: QuestionFilled
  }
  return iconMap[props.operation] || iconMap[props.type] || Warning
})

const iconColor = computed(() => {
  const colorMap = {
    warning: '#E6A23C',
    error: '#F56C6C',
    info: '#409EFF',
    success: '#67C23A'
  }
  return colorMap[props.type] || '#E6A23C'
})

const confirmButtonType = computed(() => {
  if (props.isDangerous || props.type === 'error') {
    return 'danger'
  }
  if (props.type === 'warning') {
    return 'warning'
  }
  return 'primary'
})

const canConfirm = computed(() => {
  // 倒计时未结束
  if (countdown.value > 0) return false
  
  // 需要确认文本
  if (props.requireConfirmText && inputConfirmText.value !== props.confirmTextValue) {
    return false
  }
  
  // 需要密码确认
  if (props.requirePassword && !inputPassword.value.trim()) {
    return false
  }
  
  return true
})

const countdownPercentage = computed(() => {
  if (props.countdownSeconds === 0) return 100
  return ((props.countdownSeconds - countdown.value) / props.countdownSeconds) * 100
})

const countdownColor = computed(() => {
  const percentage = countdownPercentage.value
  if (percentage < 30) return '#F56C6C'
  if (percentage < 70) return '#E6A23C'
  return '#67C23A'
})

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal) {
    resetForm()
    startCountdown()
  } else {
    stopCountdown()
  }
})

/**
 * 开始倒计时
 */
const startCountdown = () => {
  if (props.countdownSeconds > 0) {
    countdown.value = props.countdownSeconds
    countdownTimer.value = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        stopCountdown()
      }
    }, 1000)
  }
}

/**
 * 停止倒计时
 */
const stopCountdown = () => {
  if (countdownTimer.value) {
    clearInterval(countdownTimer.value)
    countdownTimer.value = null
  }
  countdown.value = 0
}

/**
 * 重置表单
 */
const resetForm = () => {
  inputConfirmText.value = ''
  inputPassword.value = ''
  detailsVisible.value = []
}

/**
 * 处理确认
 */
const handleConfirm = () => {
  if (!canConfirm.value) return
  
  emit('confirm', {
    confirmText: inputConfirmText.value,
    password: inputPassword.value
  })
}

/**
 * 处理取消
 */
const handleCancel = () => {
  visible.value = false
  emit('cancel')
}

// 生命周期
onMounted(() => {
  // 组件挂载时的初始化
})

onUnmounted(() => {
  stopCountdown()
})
</script>

<style lang="scss" scoped>
.confirm-dialog {
  .confirm-content {
    text-align: center;
    padding: 20px 0;
    
    .confirm-icon {
      margin-bottom: 20px;
    }
    
    .confirm-message {
      h3 {
        margin: 0 0 16px 0;
        color: var(--el-text-color-primary);
        font-size: 20px;
        font-weight: 600;
      }
      
      .message-text {
        margin: 0 0 20px 0;
        color: var(--el-text-color-regular);
        font-size: 14px;
        line-height: 1.6;
      }
      
      .details-section {
        margin: 20px 0;
        text-align: left;
        
        .details-content {
          .detail-item {
            padding: 4px 0;
            font-size: 14px;
            
            strong {
              color: var(--el-text-color-primary);
              margin-right: 8px;
            }
          }
        }
      }
      
      .danger-alert {
        margin: 20px 0;
        text-align: left;
        
        ul {
          margin: 8px 0 0 0;
          padding-left: 20px;
          
          li {
            margin: 4px 0;
            font-size: 13px;
          }
        }
      }
      
      .confirm-input,
      .password-confirm {
        margin: 20px 0;
        text-align: left;
        
        .confirm-prompt {
          margin: 0 0 12px 0;
          color: var(--el-text-color-regular);
          font-size: 14px;
          
          code {
            background: var(--el-fill-color-light);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: var(--el-color-danger);
            font-weight: 600;
          }
        }
      }
      
      .countdown {
        margin: 20px 0;
        
        .countdown-text {
          margin: 12px 0 0 0;
          color: var(--el-text-color-regular);
          font-size: 14px;
        }
      }
    }
  }
  
  .confirm-footer {
    display: flex;
    justify-content: center;
    gap: 16px;
    padding: 0 20px 20px 20px;
    
    .el-button {
      min-width: 100px;
    }
  }
}

// 深色主题适配
.dark {
  .confirm-dialog {
    .confirm-content {
      .confirm-message {
        h3 {
          color: var(--el-text-color-primary);
        }
        
        .message-text {
          color: var(--el-text-color-regular);
        }
        
        .confirm-prompt {
          color: var(--el-text-color-regular);
          
          code {
            background: var(--el-fill-color-dark);
            color: var(--el-color-danger);
          }
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .confirm-dialog {
    .confirm-content {
      padding: 10px 0;
      
      .confirm-message {
        h3 {
          font-size: 18px;
        }
      }
    }
    
    .confirm-footer {
      flex-direction: column;
      
      .el-button {
        width: 100%;
      }
    }
  }
}
</style>