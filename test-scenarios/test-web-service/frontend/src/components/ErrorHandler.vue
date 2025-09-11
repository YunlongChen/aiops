<!--
  AIOps测试管理平台 - 错误处理组件
  统一处理和显示API错误信息
-->

<template>
  <!-- 全局错误提示 -->
  <div
    v-if="visible"
    class="fixed top-4 right-4 z-50 max-w-md w-full bg-white shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5 overflow-hidden"
  >
    <div class="p-4">
      <div class="flex items-start">
        <div class="flex-shrink-0">
          <svg
            v-if="type === 'error'"
            class="h-6 w-6 text-red-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else-if="type === 'warning'"
            class="h-6 w-6 text-yellow-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
          <svg
            v-else-if="type === 'success'"
            class="h-6 w-6 text-green-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <svg
            v-else
            class="h-6 w-6 text-blue-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="ml-3 w-0 flex-1 pt-0.5">
          <p class="text-sm font-medium text-gray-900">{{ title }}</p>
          <p class="mt-1 text-sm text-gray-500">{{ message }}</p>
          <div v-if="details" class="mt-2">
            <button
              @click="showDetails = !showDetails"
              class="text-sm text-indigo-600 hover:text-indigo-500"
            >
              {{ showDetails ? '隐藏详情' : '显示详情' }}
            </button>
            <div v-if="showDetails" class="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
              <pre class="whitespace-pre-wrap">{{ details }}</pre>
            </div>
          </div>
          <div v-if="retryable" class="mt-3">
            <button
              @click="retry"
              :disabled="retrying"
              class="text-sm bg-indigo-600 text-white px-3 py-1 rounded hover:bg-indigo-700 disabled:opacity-50"
            >
              {{ retrying ? '重试中...' : '重试' }}
            </button>
          </div>
        </div>
        <div class="ml-4 flex-shrink-0 flex">
          <button
            @click="close"
            class="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <span class="sr-only">关闭</span>
            <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 错误处理组件
 * 提供统一的错误显示和处理机制
 */
export default {
  name: 'ErrorHandler',
  props: {
    /**
     * 错误类型
     */
    type: {
      type: String,
      default: 'error',
      validator: (value) => ['error', 'warning', 'success', 'info'].includes(value)
    },
    /**
     * 错误标题
     */
    title: {
      type: String,
      required: true
    },
    /**
     * 错误消息
     */
    message: {
      type: String,
      required: true
    },
    /**
     * 错误详情
     */
    details: {
      type: String,
      default: null
    },
    /**
     * 是否可重试
     */
    retryable: {
      type: Boolean,
      default: false
    },
    /**
     * 重试回调函数
     */
    onRetry: {
      type: Function,
      default: null
    },
    /**
     * 自动关闭时间（毫秒）
     */
    autoClose: {
      type: Number,
      default: 5000
    }
  },
  
  data() {
    return {
      visible: true,
      showDetails: false,
      retrying: false,
      autoCloseTimer: null
    }
  },
  
  mounted() {
    // 设置自动关闭
    if (this.autoClose > 0) {
      this.autoCloseTimer = setTimeout(() => {
        this.close()
      }, this.autoClose)
    }
  },
  
  beforeUnmount() {
    if (this.autoCloseTimer) {
      clearTimeout(this.autoCloseTimer)
    }
  },
  
  methods: {
    /**
     * 关闭错误提示
     */
    close() {
      this.visible = false
      this.$emit('close')
    },
    
    /**
     * 重试操作
     */
    async retry() {
      if (!this.onRetry || this.retrying) return
      
      this.retrying = true
      try {
        await this.onRetry()
        this.close()
      } catch (error) {
        console.error('重试失败:', error)
      } finally {
        this.retrying = false
      }
    }
  }
}
</script>