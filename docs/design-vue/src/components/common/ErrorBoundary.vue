<!--
  错误边界组件
  用于捕获和处理组件加载错误
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-24
-->

<template>
  <div class="error-boundary">
    <div v-if="hasError" class="error-container">
      <div class="error-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      <h3 class="error-title">{{ errorTitle }}</h3>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <button class="btn btn-primary" @click="retry">
          <i class="fas fa-redo"></i>
          重试
        </button>
        <button class="btn btn-secondary" @click="goBack">
          <i class="fas fa-arrow-left"></i>
          返回
        </button>
      </div>
      <details v-if="showDetails && errorDetails" class="error-details">
        <summary>错误详情</summary>
        <pre>{{ errorDetails }}</pre>
      </details>
    </div>
    <slot v-else></slot>
  </div>
</template>

<script>
/**
 * 错误边界组件
 * 提供组件级别的错误捕获和处理
 */
export default {
  name: 'ErrorBoundary',
  props: {
    /**
     * 错误标题
     */
    errorTitle: {
      type: String,
      default: '页面加载失败'
    },
    /**
     * 错误消息
     */
    errorMessage: {
      type: String,
      default: '抱歉，页面加载时出现了问题。请稍后重试。'
    },
    /**
     * 是否显示错误详情
     */
    showDetails: {
      type: Boolean,
      default: false
    },
    /**
     * 自定义重试函数
     */
    onRetry: {
      type: Function,
      default: null
    }
  },
  data() {
    return {
      hasError: false,
      errorDetails: null
    }
  },
  methods: {
    /**
     * 捕获错误
     * @param {Error} error - 错误对象
     */
    captureError(error) {
      this.hasError = true
      this.errorDetails = error.stack || error.message
      console.error('ErrorBoundary caught an error:', error)
      
      // 发送错误报告（可选）
      this.reportError(error)
    },
    
    /**
     * 重试操作
     */
    retry() {
      if (this.onRetry) {
        this.onRetry()
      } else {
        // 默认重试：重新加载当前路由
        this.$router.go(0)
      }
      this.hasError = false
      this.errorDetails = null
    },
    
    /**
     * 返回上一页
     */
    goBack() {
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        this.$router.push('/')
      }
    },
    
    /**
     * 报告错误（可扩展）
     * @param {Error} error - 错误对象
     */
    reportError(error) {
      // 这里可以集成错误监控服务
      // 例如：Sentry, LogRocket 等
      if (process.env.NODE_ENV === 'production') {
        // 生产环境下发送错误报告
        console.log('Error reported:', error)
      }
    }
  },
  errorCaptured(error, instance, info) {
    // Vue 3 错误捕获钩子
    this.captureError(error)
    return false // 阻止错误继续传播
  }
}
</script>

<style lang="scss" scoped>
.error-boundary {
  width: 100%;
  height: 100%;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
  min-height: 400px;
}

.error-icon {
  font-size: 64px;
  color: #f56565;
  margin-bottom: 20px;
}

.error-title {
  font-size: 24px;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 12px;
}

.error-message {
  font-size: 16px;
  color: #718096;
  margin-bottom: 30px;
  max-width: 500px;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    transform: translateY(-1px);
  }
  
  &.btn-primary {
    background-color: #4299e1;
    color: white;
    
    &:hover {
      background-color: #3182ce;
    }
  }
  
  &.btn-secondary {
    background-color: #e2e8f0;
    color: #4a5568;
    
    &:hover {
      background-color: #cbd5e0;
    }
  }
}

.error-details {
  margin-top: 20px;
  text-align: left;
  max-width: 600px;
  
  summary {
    cursor: pointer;
    font-weight: 500;
    color: #4a5568;
    margin-bottom: 10px;
  }
  
  pre {
    background-color: #f7fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 12px;
    font-size: 12px;
    color: #2d3748;
    overflow-x: auto;
    white-space: pre-wrap;
  }
}

// 暗色主题适配
@media (prefers-color-scheme: dark) {
  .error-title {
    color: #f7fafc;
  }
  
  .error-message {
    color: #a0aec0;
  }
  
  .btn-secondary {
    background-color: #4a5568;
    color: #f7fafc;
    
    &:hover {
      background-color: #2d3748;
    }
  }
  
  .error-details {
    summary {
      color: #a0aec0;
    }
    
    pre {
      background-color: #2d3748;
      border-color: #4a5568;
      color: #f7fafc;
    }
  }
}
</style>