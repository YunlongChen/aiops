<!--
  AIOps测试管理平台 - 根组件
  提供应用的整体布局结构和路由视图
-->

<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <h1 class="text-xl font-bold text-gray-900">AIOps 测试管理平台</h1>
            </div>
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <router-link
                v-for="item in navigation"
                :key="item.name"
                :to="item.href"
                class="inline-flex items-center px-1 pt-1 text-sm font-medium transition-colors duration-200"
                :class="[
                  $route.path === item.href
                    ? 'border-b-2 border-primary-500 text-gray-900'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                ]"
              >
                {{ item.name }}
              </router-link>
            </div>
          </div>
          <div class="flex items-center">
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-500">系统状态:</span>
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                运行中
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <router-view />
    </main>
  </div>
</template>

<script>
/**
 * 根组件逻辑
 * 管理全局导航和布局状态
 */
export default {
  name: 'App',
  data() {
    return {
      // 导航菜单配置
      navigation: [
        { name: '仪表板', href: '/' },
        { name: '测试用例', href: '/test-cases' },
        { name: '测试脚本', href: '/test-scripts' },
        { name: '测试运行', href: '/test-runs' },
        { name: '运行时管理', href: '/runtime-managers' },
        { name: '系统设置', href: '/settings' },
      ],
    }
  },
}
</script>

<style scoped>
/* 组件特定样式 */
.router-link-active {
  @apply border-b-2 border-primary-500 text-gray-900;
}
</style>