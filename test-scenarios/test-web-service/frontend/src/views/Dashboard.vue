<!--
  AIOps测试管理平台 - 仪表板页面
  显示系统概览、统计信息和最近的测试运行
-->

<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          仪表板
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          系统概览和运行状态监控
        </p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
            @click="refreshData"
            :disabled="loading"
            class="btn-primary"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg"
               fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">
                测试用例总数
              </dt>
              <dd class="text-lg font-medium text-gray-900">
                {{ stats.totalTestCases || 0 }}
              </dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">
                测试运行总数
              </dt>
              <dd class="text-lg font-medium text-gray-900">
                {{ stats.totalTestRuns || 0 }}
              </dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">
                运行时环境
              </dt>
              <dd class="text-lg font-medium text-gray-900">
                {{ stats.totalRuntimeManagers || 0 }}
              </dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <div class="w-8 h-8 bg-purple-500 rounded-md flex items-center justify-center">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
              </svg>
            </div>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-500 truncate">
                成功率
              </dt>
              <dd class="text-lg font-medium text-gray-900">
                {{ stats.successRate || '0%' }}
              </dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近测试运行 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
          最近测试运行
        </h3>
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
            <tr>
              <th class="table-header">测试用例</th>
              <th class="table-header">状态</th>
              <th class="table-header">运行时</th>
              <th class="table-header">开始时间</th>
              <th class="table-header">持续时间</th>
            </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
            <tr v-for="run in recentTestRuns" :key="run.id">
              <td class="table-cell font-medium">{{ run.test_case_name || '未知' }}</td>
              <td class="table-cell">
                  <span :class="getStatusClass(run.status)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ getStatusText(run.status) }}
                  </span>
              </td>
              <td class="table-cell">{{ run.runtime_type || '未知' }}</td>
              <td class="table-cell">{{ formatDate(run.created_at) }}</td>
              <td class="table-cell">{{ run.duration || '-' }}</td>
            </tr>
            <tr v-if="recentTestRuns.length === 0">
              <td colspan="5" class="table-cell text-center text-gray-500">
                暂无测试运行记录
              </td>
            </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 仪表板页面组件逻辑
 * 负责显示系统统计信息和最近的测试运行
 */
import {useAppStore, useTestCasesStore, useTestRunsStore, useRuntimeManagersStore} from '../stores'
import dayjs from 'dayjs'

export default {
  name: 'Dashboard',
  data() {
    return {
      loading: false,
      stats: {
        totalTestCases: 0,
        totalTestRuns: 0,
        totalRuntimeManagers: 0,
        successRate: '0%',
      },
      recentTestRuns: [],
    }
  },

  async mounted() {
    try {
      await this.loadDashboardData()
    } catch (error) {
      console.error('Dashboard组件挂载失败:', error)
      // 确保页面不会因为数据加载失败而空白
      this.loading = false
    }
  },

  methods: {
    /**
     * 加载仪表板数据
     */
    async loadDashboardData() {
      this.loading = true
      try {
        const appStore = useAppStore()
        const testCasesStore = useTestCasesStore()
        const testRunsStore = useTestRunsStore()
        const runtimeManagersStore = useRuntimeManagersStore()

        // 并行加载所有数据
        await Promise.all([
          testCasesStore.fetchTestCases({limit: 1}),
          testRunsStore.fetchTestRuns({limit: 10}),
          runtimeManagersStore.fetchRuntimeManagers(),
        ])

        // 提取数据（处理响应格式）
        const testCases = Array.isArray(testCasesStore.testCases) ? testCasesStore.testCases : []
        const testRuns = Array.isArray(testRunsStore.testRuns) ? testRunsStore.testRuns : []
        const runtimeManagers = Array.isArray(runtimeManagersStore.runtimeManagers) ? runtimeManagersStore.runtimeManagers : []

        // 更新统计信息
        this.stats.totalTestCases = testCasesStore.pagination?.total || testCases.length || 0
        this.stats.totalTestRuns = testRunsStore.pagination?.total || testRuns.length || 0
        this.stats.totalRuntimeManagers = runtimeManagers.length || 0

        // 计算成功率
        const successfulRuns = testRuns.filter(run => run.status === 'completed' || run.status === 'success').length
        const totalRuns = testRuns.length
        this.stats.successRate = totalRuns > 0 ? `${Math.round((successfulRuns / totalRuns) * 100)}%` : '0%'

        // 设置最近测试运行
        this.recentTestRuns = testRuns
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 10)

      } catch (error) {
        console.error('加载仪表板数据失败:', error)
        // 错误已由API拦截器处理，这里不需要额外处理
      } finally {
        this.loading = false
      }
    },

    /**
     * 刷新数据
     */
    async refreshData() {
      await this.loadDashboardData()
    },

    /**
     * 获取状态样式类
     * @param {string} status - 状态值
     * @returns {string} CSS类名
     */
    getStatusClass(status) {
      const statusClasses = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'running': 'bg-blue-100 text-blue-800',
        'completed': 'bg-green-100 text-green-800',
        'failed': 'bg-red-100 text-red-800',
        'cancelled': 'bg-gray-100 text-gray-800',
      }
      return statusClasses[status] || 'bg-gray-100 text-gray-800'
    },

    /**
     * 获取状态文本
     * @param {string} status - 状态值
     * @returns {string} 状态文本
     */
     getStatusText(status) {
      const statusTexts = {
        'pending': '等待中',
        'running': '运行中',
        'completed': '已完成',
        'failed': '失败',
        'cancelled': '已取消',
      }
      return statusTexts[status] || '未知'
    },

    /**
     * 格式化日期
     * @param {string} date - 日期字符串
     * @returns {string} 格式化后的日期
     */
    formatDate(date) {
      return date ? dayjs(date).format('YYYY-MM-DD HH:mm:ss') : '-'
    },
  },
}
</script>