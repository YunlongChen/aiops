/**
 * AIOps测试管理平台 - Vue应用主入口文件
 * 负责初始化Vue应用、路由、状态管理和全局配置
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import './style.css'
import { errorHandler } from './services/errorHandler'

// 创建Vue应用实例
const app = createApp(App)

// 配置全局错误处理
app.config.errorHandler = (error, instance, info) => {
  console.error('Vue全局错误:', error)
  console.error('错误信息:', info)
  console.error('组件实例:', instance)
  
  // 使用错误处理服务统一处理
  errorHandler.handleApiError({
    message: error.message || '组件渲染错误',
    stack: error.stack,
    componentInfo: info
  }, {
    title: '页面渲染错误',
    severity: 'high',
    retryable: false
  })
}

// 配置全局警告处理
app.config.warnHandler = (msg, instance, trace) => {
  console.warn('Vue警告:', msg)
  console.warn('组件追踪:', trace)
}

// 使用Pinia状态管理
app.use(createPinia())

// 使用Vue Router
app.use(router)

// 挂载应用
app.mount('#app')