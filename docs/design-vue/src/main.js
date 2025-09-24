/**
 * Vue应用主入口文件
 * 配置Vue应用实例、路由、状态管理和全局组件
 * 
 * @author AI Assistant
 * @version 1.1.0
 * @date 2025-01-24
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// 导入全局样式
import '@/assets/styles/main.scss'

// 导入图标库
import '@/assets/fonts/fontawesome-all.min.css'
import '@/assets/fonts/inter.css'

// 导入全局组件
import LoadingSpinner from '@/components/Common/LoadingSpinner.vue'
import ErrorBoundary from '@/components/Common/ErrorBoundary.vue'

// 创建Vue应用实例
const app = createApp(App)

// 注册全局组件
app.component('LoadingSpinner', LoadingSpinner)
app.component('ErrorBoundary', ErrorBoundary)

// 使用Pinia状态管理
app.use(createPinia())

// 使用Vue Router
app.use(router)

// 全局错误处理
app.config.errorHandler = (error, instance, info) => {
  console.error('Global error:', error)
  console.error('Error info:', info)
  
  // 在生产环境中，可以将错误发送到监控服务
  if (process.env.NODE_ENV === 'production') {
    // 发送错误报告到监控服务
    // reportError(error, instance, info)
  }
}

// 全局警告处理
app.config.warnHandler = (msg, instance, trace) => {
  console.warn('Global warning:', msg)
  console.warn('Warning trace:', trace)
}

// 性能监控（开发环境）
if (process.env.NODE_ENV === 'development') {
  app.config.performance = true
}

// 挂载应用
app.mount('#app')