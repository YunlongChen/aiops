<!--
  AIOps测试管理平台 - 404页面
  页面未找到错误页面
-->

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8 text-center">
      <!-- 404图标 -->
      <div>
        <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.467-.881-6.08-2.33M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      </div>
      
      <!-- 错误信息 -->
      <div>
        <h1 class="text-6xl font-bold text-gray-900">404</h1>
        <h2 class="mt-2 text-3xl font-bold text-gray-900">页面未找到</h2>
        <p class="mt-2 text-sm text-gray-600">
          抱歉，您访问的页面不存在或已被移动。
        </p>
      </div>
      
      <!-- 操作按钮 -->
      <div class="space-y-4">
        <div class="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            @click="goBack"
            class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            返回上页
          </button>
          
          <router-link
            to="/"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="-ml-1 mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            回到首页
          </router-link>
        </div>
        
        <!-- 常用链接 -->
        <div class="border-t border-gray-200 pt-4">
          <p class="text-sm text-gray-500 mb-3">您可能想要访问：</p>
          <div class="flex flex-wrap justify-center gap-2">
            <router-link
              to="/"
              class="text-blue-600 hover:text-blue-800 text-sm underline"
            >
              仪表板
            </router-link>
            <span class="text-gray-300">|</span>
            <router-link
              to="/test-cases"
              class="text-blue-600 hover:text-blue-800 text-sm underline"
            >
              测试用例
            </router-link>
            <span class="text-gray-300">|</span>
            <router-link
              to="/test-runs"
              class="text-blue-600 hover:text-blue-800 text-sm underline"
            >
              测试运行
            </router-link>
            <span class="text-gray-300">|</span>
            <router-link
              to="/runtime-managers"
              class="text-blue-600 hover:text-blue-800 text-sm underline"
            >
              运行时管理
            </router-link>
          </div>
        </div>
      </div>
      
      <!-- 帮助信息 -->
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-blue-800">
              需要帮助？
            </h3>
            <div class="mt-2 text-sm text-blue-700">
              <p>
                如果您认为这是一个错误，请检查URL是否正确，或联系系统管理员。
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 404页面组件逻辑
 * 处理页面未找到的情况
 */
export default {
  name: 'NotFound',
  
  methods: {
    /**
     * 返回上一页
     */
    goBack() {
      // 如果有历史记录，返回上一页
      if (window.history.length > 1) {
        this.$router.go(-1)
      } else {
        // 否则跳转到首页
        this.$router.push('/')
      }
    },
  },
  
  /**
   * 组件挂载时设置页面标题
   */
  mounted() {
    document.title = '页面未找到 - AIOps测试管理平台'
  },
}
</script>

<style scoped>
/* 404页面特定样式 */
.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>