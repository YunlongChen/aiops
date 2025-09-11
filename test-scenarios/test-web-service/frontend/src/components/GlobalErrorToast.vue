<template>
  <!-- 全局错误提示容器 -->
  <div class="error-toast-container">
    <transition-group name="toast" tag="div">
      <div
        v-for="error in visibleErrors"
        :key="error.id"
        :class="[
          'error-toast',
          `error-toast--${error.type}`,
          `error-toast--${error.severity}`
        ]"
        @click="handleToastClick(error)"
      >
        <!-- 错误图标 -->
        <div class="error-toast__icon">
          <svg v-if="error.type === 'success'" class="icon" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" fill="currentColor"/>
          </svg>
          <svg v-else-if="error.type === 'info'" class="icon" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="currentColor"/>
          </svg>
          <svg v-else-if="error.type === 'warning'" class="icon" viewBox="0 0 24 24">
            <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z" fill="currentColor"/>
          </svg>
          <svg v-else class="icon" viewBox="0 0 24 24">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" fill="currentColor"/>
          </svg>
        </div>
        
        <!-- 错误内容 -->
        <div class="error-toast__content">
          <div class="error-toast__title">
            {{ error.title }}
            <span v-if="error.count > 1" class="error-toast__count">
              ({{ error.count }})
            </span>
          </div>
          <div class="error-toast__message">{{ error.message }}</div>
          
          <!-- 详细信息（可展开） -->
          <div v-if="error.details && expandedErrors.has(error.id)" class="error-toast__details">
            <pre>{{ error.details }}</pre>
          </div>
          
          <!-- 操作按钮 -->
          <div v-if="error.retryable || error.details" class="error-toast__actions">
            <button
              v-if="error.retryable"
              class="error-toast__action error-toast__action--retry"
              @click.stop="handleRetry(error)"
            >
              重试
            </button>
            <button
              v-if="error.details"
              class="error-toast__action error-toast__action--details"
              @click.stop="toggleDetails(error.id)"
            >
              {{ expandedErrors.has(error.id) ? '隐藏详情' : '查看详情' }}
            </button>
          </div>
        </div>
        
        <!-- 关闭按钮 -->
        <button
          class="error-toast__close"
          @click.stop="closeError(error.id)"
          title="关闭"
        >
          <svg class="icon" viewBox="0 0 24 24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" fill="currentColor"/>
          </svg>
        </button>
        
        <!-- 自动关闭进度条 -->
        <div
          v-if="error.autoClose > 0"
          class="error-toast__progress"
          :style="{ animationDuration: `${error.autoClose}ms` }"
        ></div>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { errorHandler, errorState } from '@/services/errorHandler'

export default {
  name: 'GlobalErrorToast',
  
  setup() {
    const expandedErrors = ref(new Set())
    const autoCloseTimers = ref(new Map())
    
    /**
     * 可见的错误列表
     */
    const visibleErrors = computed(() => {
      return errorState.errors.slice(0, 5) // 最多显示5个
    })
    
    /**
     * 处理点击提示框
     * @param {Object} error - 错误对象
     */
    const handleToastClick = (error) => {
      // 点击时暂停自动关闭
      if (autoCloseTimers.value.has(error.id)) {
        clearTimeout(autoCloseTimers.value.get(error.id))
        autoCloseTimers.value.delete(error.id)
      }
    }
    
    /**
     * 关闭错误
     * @param {string} errorId - 错误ID
     */
    const closeError = (errorId) => {
      errorHandler.removeError(errorId)
      expandedErrors.value.delete(errorId)
      
      if (autoCloseTimers.value.has(errorId)) {
        clearTimeout(autoCloseTimers.value.get(errorId))
        autoCloseTimers.value.delete(errorId)
      }
    }
    
    /**
     * 处理重试
     * @param {Object} error - 错误对象
     */
    const handleRetry = (error) => {
      if (error.onRetry && typeof error.onRetry === 'function') {
        try {
          error.onRetry()
          closeError(error.id)
        } catch (retryError) {
          console.error('重试失败:', retryError)
        }
      }
    }
    
    /**
     * 切换详情显示
     * @param {string} errorId - 错误ID
     */
    const toggleDetails = (errorId) => {
      if (expandedErrors.value.has(errorId)) {
        expandedErrors.value.delete(errorId)
      } else {
        expandedErrors.value.add(errorId)
      }
    }
    
    /**
     * 设置自动关闭定时器
     * @param {Object} error - 错误对象
     */
    const setAutoCloseTimer = (error) => {
      if (error.autoClose > 0) {
        const timer = setTimeout(() => {
          closeError(error.id)
        }, error.autoClose)
        
        autoCloseTimers.value.set(error.id, timer)
      }
    }
    
    /**
     * 监听错误变化
     */
    const watchErrors = () => {
      // 为新错误设置自动关闭定时器
      visibleErrors.value.forEach(error => {
        if (!autoCloseTimers.value.has(error.id)) {
          setAutoCloseTimer(error)
        }
      })
      
      // 清理已删除错误的定时器
      const currentErrorIds = new Set(visibleErrors.value.map(e => e.id))
      autoCloseTimers.value.forEach((timer, errorId) => {
        if (!currentErrorIds.has(errorId)) {
          clearTimeout(timer)
          autoCloseTimers.value.delete(errorId)
          expandedErrors.value.delete(errorId)
        }
      })
    }
    
    onMounted(() => {
      // 初始化现有错误的定时器
      watchErrors()
      
      // 监听错误状态变化
      const observer = new MutationObserver(watchErrors)
      // 这里简化处理，实际应该使用Vue的响应式系统
      setInterval(watchErrors, 1000)
    })
    
    onUnmounted(() => {
      // 清理所有定时器
      autoCloseTimers.value.forEach(timer => clearTimeout(timer))
      autoCloseTimers.value.clear()
    })
    
    return {
      visibleErrors,
      expandedErrors,
      handleToastClick,
      closeError,
      handleRetry,
      toggleDetails
    }
  }
}
</script>

<style scoped>
.error-toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  max-width: 400px;
  pointer-events: none;
}

.error-toast {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  margin-bottom: 12px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  cursor: pointer;
  pointer-events: auto;
  position: relative;
  overflow: hidden;
  border-left: 4px solid #e5e7eb;
  transition: all 0.3s ease;
}

.error-toast:hover {
  transform: translateX(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

/* 错误类型样式 */
.error-toast--success {
  border-left-color: #10b981;
}

.error-toast--info {
  border-left-color: #3b82f6;
}

.error-toast--warning {
  border-left-color: #f59e0b;
}

.error-toast--network,
.error-toast--api,
.error-toast--validation,
.error-toast--permission,
.error-toast--unknown {
  border-left-color: #ef4444;
}

/* 严重级别样式 */
.error-toast--critical {
  background: #fef2f2;
  border-left-color: #dc2626;
}

.error-toast--high {
  background: #fefbf2;
  border-left-color: #f59e0b;
}

/* 图标样式 */
.error-toast__icon {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  margin-top: 2px;
}

.error-toast--success .error-toast__icon {
  color: #10b981;
}

.error-toast--info .error-toast__icon {
  color: #3b82f6;
}

.error-toast--warning .error-toast__icon {
  color: #f59e0b;
}

.error-toast--network .error-toast__icon,
.error-toast--api .error-toast__icon,
.error-toast--validation .error-toast__icon,
.error-toast--permission .error-toast__icon,
.error-toast--unknown .error-toast__icon {
  color: #ef4444;
}

.icon {
  width: 100%;
  height: 100%;
}

/* 内容样式 */
.error-toast__content {
  flex: 1;
  min-width: 0;
}

.error-toast__title {
  font-weight: 600;
  font-size: 14px;
  color: #111827;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-toast__count {
  background: #ef4444;
  color: white;
  font-size: 12px;
  font-weight: 500;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.error-toast__message {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
  margin-bottom: 8px;
}

.error-toast__details {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  padding: 8px;
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.error-toast__details pre {
  font-size: 11px;
  color: #374151;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

/* 操作按钮 */
.error-toast__actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.error-toast__action {
  background: none;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.error-toast__action:hover {
  background: #f3f4f6;
}

.error-toast__action--retry {
  color: #3b82f6;
  border-color: #3b82f6;
}

.error-toast__action--retry:hover {
  background: #eff6ff;
}

.error-toast__action--details {
  color: #6b7280;
}

/* 关闭按钮 */
.error-toast__close {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.error-toast__close:hover {
  background: #f3f4f6;
  color: #6b7280;
}

/* 进度条 */
.error-toast__progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: #3b82f6;
  width: 100%;
  transform-origin: left;
  animation: progress-shrink linear;
}

@keyframes progress-shrink {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

/* 动画效果 */
.toast-enter-active {
  transition: all 0.3s ease;
}

.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .error-toast-container {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .error-toast {
    padding: 12px;
  }
  
  .error-toast__title {
    font-size: 13px;
  }
  
  .error-toast__message {
    font-size: 12px;
  }
}
</style>