<!--
  AIOps测试管理平台 - 测试运行页面
  查看测试运行历史和结果
-->

<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          测试运行
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          查看测试运行历史和结果
        </p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
          @click="loadTestRuns"
          class="btn-secondary mr-3"
        >
          刷新
        </button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">状态</label>
            <select v-model="statusFilter" class="input-field">
              <option value="">所有状态</option>
              <option value="pending">等待中</option>
              <option value="running">运行中</option>
              <option value="completed">已完成</option>
              <option value="failed">失败</option>
              <option value="cancelled">已取消</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">运行时类型</label>
            <select v-model="runtimeFilter" class="input-field">
              <option value="">所有类型</option>
              <option value="docker">Docker</option>
              <option value="kubernetes">Kubernetes</option>
              <option value="local">本地</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">开始日期</label>
            <input
              v-model="startDateFilter"
              type="date"
              class="input-field"
            >
          </div>
          <div class="flex items-end">
            <button
              @click="loadTestRuns"
              class="btn-secondary w-full"
            >
              筛选
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试运行列表 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">ID</th>
                <th class="table-header">测试用例</th>
                <th class="table-header">状态</th>
                <th class="table-header">运行时</th>
                <th class="table-header">开始时间</th>
                <th class="table-header">持续时间</th>
                <th class="table-header">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="run in testRuns" :key="run.id">
                <td class="table-cell font-mono text-sm">{{ run.id.substring(0, 8) }}</td>
                <td class="table-cell font-medium">{{ run.test_case_name || '未知' }}</td>
                <td class="table-cell">
                  <span :class="getStatusClass(run.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ getStatusText(run.status) }}
                  </span>
                </td>
                <td class="table-cell">
                  <span :class="getRuntimeClass(run.runtime_type)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ getRuntimeText(run.runtime_type) }}
                  </span>
                </td>
                <td class="table-cell">{{ formatDate(run.created_at) }}</td>
                <td class="table-cell">{{ run.duration || '-' }}</td>
                <td class="table-cell">
                  <div class="flex space-x-2">
                    <button
                      @click="viewDetails(run)"
                      class="text-blue-600 hover:text-blue-900 text-sm"
                    >
                      详情
                    </button>
                    <button
                      v-if="run.status === 'running'"
                      @click="cancelRun(run.id)"
                      class="text-red-600 hover:text-red-900 text-sm"
                    >
                      取消
                    </button>
                    <button
                      v-if="['completed', 'failed'].includes(run.status)"
                      @click="rerunTest(run)"
                      class="text-green-600 hover:text-green-900 text-sm"
                    >
                      重新运行
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="testRuns.length === 0">
                <td colspan="7" class="table-cell text-center text-gray-500">
                  暂无测试运行记录
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- 分页 -->
        <div v-if="pagination.total > 0" class="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 mt-4">
          <div class="flex flex-1 justify-between sm:hidden">
            <button
              @click="previousPage"
              :disabled="pagination.page <= 1"
              class="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              上一页
            </button>
            <button
              @click="nextPage"
              :disabled="pagination.page >= totalPages"
              class="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              下一页
            </button>
          </div>
          <div class="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示第 {{ (pagination.page - 1) * pagination.limit + 1 }} 到 {{ Math.min(pagination.page * pagination.limit, pagination.total) }} 条，共 {{ pagination.total }} 条记录
              </p>
            </div>
            <div>
              <nav class="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                <button
                  @click="previousPage"
                  :disabled="pagination.page <= 1"
                  class="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0"
                >
                  上一页
                </button>
                <button
                  @click="nextPage"
                  :disabled="pagination.page >= totalPages"
                  class="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0"
                >
                  下一页
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试运行详情模态框 -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              测试运行详情
            </h3>
            <button
              @click="closeDetailsModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div v-if="selectedRun" class="space-y-6">
            <!-- 基本信息 -->
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">运行ID</label>
                <p class="mt-1 text-sm text-gray-900 font-mono">{{ selectedRun.id }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">测试用例</label>
                <p class="mt-1 text-sm text-gray-900">{{ selectedRun.test_case_name || '未知' }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">状态</label>
                <span :class="getStatusClass(selectedRun.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full mt-1">
                  {{ getStatusText(selectedRun.status) }}
                </span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">运行时类型</label>
                <span :class="getRuntimeClass(selectedRun.runtime_type)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full mt-1">
                  {{ getRuntimeText(selectedRun.runtime_type) }}
                </span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">开始时间</label>
                <p class="mt-1 text-sm text-gray-900">{{ formatDate(selectedRun.created_at) }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">持续时间</label>
                <p class="mt-1 text-sm text-gray-900">{{ selectedRun.duration || '-' }}</p>
              </div>
            </div>
            
            <!-- 输出日志 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">输出日志</label>
              <div class="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm max-h-96 overflow-y-auto">
                <pre>{{ selectedRun.output || '暂无输出日志' }}</pre>
              </div>
            </div>
            
            <!-- 错误信息 -->
            <div v-if="selectedRun.error_message">
              <label class="block text-sm font-medium text-gray-700 mb-2">错误信息</label>
              <div class="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
                <pre>{{ selectedRun.error_message }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 测试运行页面组件逻辑
 * 负责查看测试运行历史和结果
 */
import { useTestRunsStore } from '../stores'
import dayjs from 'dayjs'

export default {
  name: 'TestRuns',
  data() {
    return {
      statusFilter: '',
      runtimeFilter: '',
      startDateFilter: '',
      showDetailsModal: false,
      selectedRun: null,
    }
  },
  
  computed: {
    testRuns() {
      const store = useTestRunsStore()
      return store.testRuns
    },
    
    pagination() {
      const store = useTestRunsStore()
      return store.pagination
    },
    
    totalPages() {
      const store = useTestRunsStore()
      return Math.ceil(store.pagination.total / store.pagination.limit)
    },
  },
  
  async mounted() {
    await this.loadTestRuns()
  },
  
  methods: {
    /**
     * 加载测试运行列表
     */
    async loadTestRuns() {
      try {
        const store = useTestRunsStore()
        const params = {
          page: this.pagination.page,
          limit: this.pagination.limit,
        }
        
        if (this.statusFilter) {
          params.status = this.statusFilter
        }
        
        if (this.runtimeFilter) {
          params.runtime_type = this.runtimeFilter
        }
        
        if (this.startDateFilter) {
          params.start_date = this.startDateFilter
        }
        
        await store.fetchTestRuns(params)
      } catch (error) {
        console.error('加载测试运行失败:', error)
      }
    },
    
    /**
     * 查看详情
     * @param {Object} run - 测试运行对象
     */
    viewDetails(run) {
      this.selectedRun = run
      this.showDetailsModal = true
    },
    
    /**
     * 关闭详情模态框
     */
    closeDetailsModal() {
      this.showDetailsModal = false
      this.selectedRun = null
    },
    
    /**
     * 取消运行
     * @param {string} id - 测试运行ID
     */
    async cancelRun(id) {
      if (confirm('确定要取消这个测试运行吗？')) {
        try {
          // TODO: 实现取消运行API调用
          console.log('取消测试运行:', id)
          await this.loadTestRuns()
        } catch (error) {
          alert('取消失败: ' + error.message)
        }
      }
    },
    
    /**
     * 重新运行测试
     * @param {Object} run - 测试运行对象
     */
    async rerunTest(run) {
      try {
        // TODO: 实现重新运行测试的逻辑
        console.log('重新运行测试:', run)
        alert('测试已开始重新运行')
        await this.loadTestRuns()
      } catch (error) {
        alert('重新运行失败: ' + error.message)
      }
    },
    
    /**
     * 上一页
     */
    async previousPage() {
      if (this.pagination.page > 1) {
        const store = useTestRunsStore()
        store.pagination.page--
        await this.loadTestRuns()
      }
    },
    
    /**
     * 下一页
     */
    async nextPage() {
      if (this.pagination.page < this.totalPages) {
        const store = useTestRunsStore()
        store.pagination.page++
        await this.loadTestRuns()
      }
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
     * 获取运行时样式类
     * @param {string} type - 运行时类型
     * @returns {string} CSS类名
     */
    getRuntimeClass(type) {
      const typeClasses = {
        'docker': 'bg-blue-100 text-blue-800',
        'kubernetes': 'bg-green-100 text-green-800',
        'local': 'bg-gray-100 text-gray-800',
      }
      return typeClasses[type] || 'bg-gray-100 text-gray-800'
    },
    
    /**
     * 获取运行时文本
     * @param {string} type - 运行时类型
     * @returns {string} 运行时文本
     */
    getRuntimeText(type) {
      const typeTexts = {
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'local': '本地',
      }
      return typeTexts[type] || '未知'
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