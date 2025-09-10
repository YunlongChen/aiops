<!--
  AIOps测试管理平台 - 测试用例页面
  管理和查看测试用例
-->

<template>
  <div class="space-y-6">
    <!-- 页面标题和操作按钮 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          测试用例
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          管理和查看所有测试用例
        </p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
          @click="showCreateModal = true"
          class="btn-primary"
        >
          创建测试用例
        </button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label class="block text-sm font-medium text-gray-700">搜索</label>
            <input
              v-model="searchQuery"
              type="text"
              class="input-field"
              placeholder="搜索测试用例名称或描述"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">状态</label>
            <select v-model="statusFilter" class="input-field">
              <option value="">所有状态</option>
              <option value="active">活跃</option>
              <option value="inactive">不活跃</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="loadTestCases"
              class="btn-secondary w-full"
            >
              搜索
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试用例列表 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">名称</th>
                <th class="table-header">描述</th>
                <th class="table-header">状态</th>
                <th class="table-header">创建时间</th>
                <th class="table-header">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="testCase in testCases" :key="testCase.id">
                <td class="table-cell font-medium">{{ testCase.name }}</td>
                <td class="table-cell">{{ testCase.description || '-' }}</td>
                <td class="table-cell">
                  <span :class="getStatusClass(testCase.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ getStatusText(testCase.status) }}
                  </span>
                </td>
                <td class="table-cell">{{ formatDate(testCase.created_at) }}</td>
                <td class="table-cell">
                  <div class="flex space-x-2">
                    <button
                      @click="runTest(testCase)"
                      class="text-green-600 hover:text-green-900 text-sm"
                    >
                      运行
                    </button>
                    <button
                      @click="editTestCase(testCase)"
                      class="text-indigo-600 hover:text-indigo-900 text-sm"
                    >
                      编辑
                    </button>
                    <button
                      @click="deleteTestCase(testCase.id)"
                      class="text-red-600 hover:text-red-900 text-sm"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="testCases.length === 0">
                <td colspan="5" class="table-cell text-center text-gray-500">
                  暂无测试用例
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

    <!-- 创建/编辑测试用例模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ editingTestCase ? '编辑测试用例' : '创建测试用例' }}
          </h3>
          <form @submit.prevent="submitForm">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">名称</label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  class="input-field"
                  placeholder="输入测试用例名称"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">描述</label>
                <textarea
                  v-model="form.description"
                  class="input-field"
                  rows="3"
                  placeholder="输入测试用例描述"
                ></textarea>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">测试脚本</label>
                <textarea
                  v-model="form.script_content"
                  class="input-field font-mono text-sm"
                  rows="8"
                  placeholder="输入测试脚本内容"
                ></textarea>
              </div>
            </div>
            
            <div class="flex justify-end space-x-3 mt-6">
              <button
                type="button"
                @click="closeModal"
                class="btn-secondary"
              >
                取消
              </button>
              <button
                type="submit"
                :disabled="submitting"
                class="btn-primary"
              >
                {{ submitting ? '提交中...' : (editingTestCase ? '更新' : '创建') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 测试用例页面组件逻辑
 * 负责管理和查看测试用例
 */
import { useTestCasesStore } from '../stores'
import dayjs from 'dayjs'

export default {
  name: 'TestCases',
  data() {
    return {
      searchQuery: '',
      statusFilter: '',
      showCreateModal: false,
      editingTestCase: null,
      submitting: false,
      form: {
        name: '',
        description: '',
        script_content: '',
      },
    }
  },
  
  computed: {
    testCases() {
      const store = useTestCasesStore()
      return store.testCases
    },
    
    pagination() {
      const store = useTestCasesStore()
      return store.pagination
    },
    
    totalPages() {
      const store = useTestCasesStore()
      return store.totalPages
    },
  },
  
  async mounted() {
    await this.loadTestCases()
  },
  
  methods: {
    /**
     * 加载测试用例列表
     */
    async loadTestCases() {
      try {
        const store = useTestCasesStore()
        const params = {
          page: this.pagination.page,
          limit: this.pagination.limit,
        }
        
        if (this.searchQuery) {
          params.search = this.searchQuery
        }
        
        if (this.statusFilter) {
          params.status = this.statusFilter
        }
        
        await store.fetchTestCases(params)
      } catch (error) {
        console.error('加载测试用例失败:', error)
      }
    },
    
    /**
     * 运行测试
     * @param {Object} testCase - 测试用例对象
     */
    async runTest(testCase) {
      try {
        // TODO: 实现运行测试的逻辑
        console.log('运行测试:', testCase)
        alert('测试已开始运行，请在测试运行页面查看结果')
      } catch (error) {
        alert('运行测试失败: ' + error.message)
      }
    },
    
    /**
     * 编辑测试用例
     * @param {Object} testCase - 测试用例对象
     */
    editTestCase(testCase) {
      this.editingTestCase = testCase
      this.form = {
        name: testCase.name,
        description: testCase.description || '',
        script_content: testCase.script_content || '',
      }
      this.showCreateModal = true
    },
    
    /**
     * 删除测试用例
     * @param {string} id - 测试用例ID
     */
    async deleteTestCase(id) {
      if (confirm('确定要删除这个测试用例吗？')) {
        try {
          // TODO: 实现删除API调用
          console.log('删除测试用例:', id)
          await this.loadTestCases()
        } catch (error) {
          alert('删除失败: ' + error.message)
        }
      }
    },
    
    /**
     * 提交表单
     */
    async submitForm() {
      this.submitting = true
      try {
        const store = useTestCasesStore()
        
        if (this.editingTestCase) {
          // TODO: 实现更新API调用
          console.log('更新测试用例:', this.form)
        } else {
          await store.createTestCase(this.form)
        }
        
        this.closeModal()
        await this.loadTestCases()
      } catch (error) {
        alert('操作失败: ' + error.message)
      } finally {
        this.submitting = false
      }
    },
    
    /**
     * 关闭模态框
     */
    closeModal() {
      this.showCreateModal = false
      this.editingTestCase = null
      this.form = {
        name: '',
        description: '',
        script_content: '',
      }
    },
    
    /**
     * 上一页
     */
    async previousPage() {
      if (this.pagination.page > 1) {
        const store = useTestCasesStore()
        store.pagination.page--
        await this.loadTestCases()
      }
    },
    
    /**
     * 下一页
     */
    async nextPage() {
      if (this.pagination.page < this.totalPages) {
        const store = useTestCasesStore()
        store.pagination.page++
        await this.loadTestCases()
      }
    },
    
    /**
     * 获取状态样式类
     * @param {string} status - 状态值
     * @returns {string} CSS类名
     */
    getStatusClass(status) {
      const statusClasses = {
        'active': 'bg-green-100 text-green-800',
        'inactive': 'bg-gray-100 text-gray-800',
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
        'active': '活跃',
        'inactive': '不活跃',
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