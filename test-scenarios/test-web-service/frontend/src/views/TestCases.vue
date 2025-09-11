<!--
  AIOps测试管理平台 - 测试用例页面
  管理和查看测试用例，集成列表、编辑器和详情组件
-->

<template>
  <div class="test-cases-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <svg class="title-icon" viewBox="0 0 24 24">
              <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke="currentColor" stroke-width="2" fill="none"/>
            </svg>
            测试用例管理
          </h1>
          <p class="page-description">创建、编辑和管理自动化测试用例</p>
        </div>
        <div class="header-actions">
          <button 
            class="btn btn-primary"
            @click="showCreateForm"
            :disabled="loading"
          >
            <svg viewBox="0 0 24 24">
              <path d="M12 4v16m8-8H4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
            新建测试用例
          </button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 测试用例列表视图 -->
      <div v-if="currentView === 'list'" class="list-view">
        <TestCaseList
          :test-cases="testCases"
          :loading="loading"
          :pagination="pagination"
          @edit="showEditForm"
          @view="showDetail"
          @delete="handleDelete"
          @run="handleRun"
          @page-change="handlePageChange"
          @search="handleSearch"
          @filter="handleFilter"
        />
      </div>

      <!-- 测试用例编辑器视图 -->
      <div v-else-if="currentView === 'editor'" class="editor-view">
        <TestCaseEditor
          :test-case="selectedTestCase"
          :is-editing="isEditing"
          @save="handleSave"
          @cancel="showList"
        />
      </div>

      <!-- 测试用例详情视图 -->
      <div v-else-if="currentView === 'detail'" class="detail-view">
        <TestCaseDetail
          :test-case="selectedTestCase"
          :run-history="runHistory"
          :loading-history="loadingHistory"
          @back="showList"
          @edit="showEditForm"
          @run="handleRun"
          @refresh-history="loadRunHistory"
        />
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
                <label class="block text-sm font-medium text-gray-700">脚本语言</label>
                <select
                  v-model="form.language"
                  class="input-field"
                  required
                >
                  <option value="">请选择脚本语言</option>
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="shell">Shell</option>
                  <option value="go">Go</option>
                  <option value="rust">Rust</option>
                  <option value="java">Java</option>
                  <option value="docker">Docker</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">测试脚本</label>
                <textarea
                  v-model="form.script_content"
                  class="input-field font-mono text-sm"
                  rows="8"
                  :placeholder="getScriptPlaceholder()"
                ></textarea>
              </div>
              
              <div v-if="form.language === 'docker'">
                <label class="block text-sm font-medium text-gray-700">Docker镜像</label>
                <input
                  v-model="form.docker_image"
                  type="text"
                  class="input-field"
                  placeholder="例如: python:3.9-slim"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">超时时间（秒）</label>
                <input
                  v-model.number="form.timeout_seconds"
                  type="number"
                  class="input-field"
                  placeholder="默认30秒"
                  min="1"
                  max="3600"
                >
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
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useTestCasesStore } from '../stores'
import TestCaseList from '../components/TestCaseList.vue'
import TestCaseEditor from '../components/TestCaseEditor.vue'
import TestCaseDetail from '../components/TestCaseDetail.vue'
import dayjs from 'dayjs'

export default {
  name: 'TestCases',
  components: {
    TestCaseList,
    TestCaseEditor,
    TestCaseDetail
  },
  setup() {
    const store = useTestCasesStore()
    
    // 错误处理和成功提示函数
    const handleError = (error, message) => {
      console.error(error)
      ElMessage.error(message || '操作失败')
    }
    
    const showSuccess = (message) => {
      ElMessage.success(message)
    }
    
    // 响应式数据
    const currentView = ref('list') // 'list', 'editor', 'detail'
    const selectedTestCase = ref(null)
    const isEditing = ref(false)
    const loading = ref(false)
    const loadingHistory = ref(false)
    const runHistory = ref([])
    const showCreateModal = ref(false)
    const editingTestCase = ref(null)
    const submitting = ref(false)
    const form = ref({
      name: '',
      description: '',
      language: '',
      script_content: '',
      docker_image: '',
      timeout_seconds: 30,
      status: 'active'
    })
    
    // 计算属性
    const testCases = computed(() => store.testCases)
    const pagination = computed(() => store.pagination)
    
    // 视图切换方法
    const showList = () => {
      currentView.value = 'list'
      selectedTestCase.value = null
      isEditing.value = false
    }
    
    const showCreateForm = () => {
      showCreateModal.value = true
      editingTestCase.value = null
      form.value = {
        name: '',
        description: '',
        language: '',
        script_content: '',
        docker_image: '',
        timeout_seconds: 30,
        status: 'active'
      }
    }
    
    const showEditForm = (testCase) => {
      currentView.value = 'editor'
      selectedTestCase.value = testCase
      isEditing.value = true
    }
    
    // 关闭模态框
    const closeModal = () => {
      showCreateModal.value = false
      editingTestCase.value = null
      form.value = {
        name: '',
        description: '',
        language: '',
        script_content: '',
        docker_image: '',
        timeout_seconds: 30,
        status: 'active'
      }
    }
    
    // 提交表单
    const submitForm = async () => {
      if (!form.value.name || !form.value.language || !form.value.script_content) {
        ElMessage.error('请填写必填字段')
        return
      }

      submitting.value = true
      try {
        if (editingTestCase.value) {
          await store.updateTestCase(editingTestCase.value.id, form.value)
          showSuccess('测试用例更新成功')
        } else {
          await store.createTestCase(form.value)
          showSuccess('测试用例创建成功')
        }
        closeModal()
        await loadTestCases()
      } catch (error) {
        handleError(error, editingTestCase.value ? '更新测试用例失败' : '创建测试用例失败')
      } finally {
        submitting.value = false
      }
    }
    
    // 获取脚本占位符
    const getScriptPlaceholder = () => {
      const placeholders = {
        python: 'def test_function():\n    # 编写你的Python测试代码\n    assert True',
        javascript: 'function test() {\n    // 编写你的JavaScript测试代码\n    console.log("测试通过");\n}',
        shell: '#!/bin/bash\n# 编写你的Shell脚本\necho "测试通过"',
        go: 'package main\n\nimport "fmt"\n\nfunc main() {\n    // 编写你的Go测试代码\n    fmt.Println("测试通过")\n}',
        rust: 'fn main() {\n    // 编写你的Rust测试代码\n    println!("测试通过");\n}',
        java: 'public class Test {\n    public static void main(String[] args) {\n        // 编写你的Java测试代码\n        System.out.println("测试通过");\n    }\n}',
        docker: '# Dockerfile内容或docker命令\nFROM alpine:latest\nRUN echo "测试通过"'
      }
      return placeholders[form.value.language] || '请输入测试脚本内容'
    }
    
    const showDetail = (testCase) => {
      currentView.value = 'detail'
      selectedTestCase.value = testCase
      loadRunHistory(testCase.id)
    }
    
    // 数据加载方法
    const loadTestCases = async (params = {}) => {
      loading.value = true
      try {
        await store.fetchTestCases(params)
      } catch (error) {
        handleError(error, '加载测试用例失败')
      } finally {
        loading.value = false
      }
    }
    
    const loadRunHistory = async (testCaseId) => {
      loadingHistory.value = true
      try {
        // TODO: 实现获取运行历史的API调用
        runHistory.value = []
      } catch (error) {
        handleError(error, '加载运行历史失败')
      } finally {
        loadingHistory.value = false
      }
    }
    
    // 事件处理方法
    const handleSave = async (testCaseData) => {
      try {
        if (isEditing.value) {
          await store.updateTestCase(selectedTestCase.value.id, testCaseData)
          showSuccess('测试用例更新成功')
        } else {
          await store.createTestCase(testCaseData)
          showSuccess('测试用例创建成功')
        }
        showList()
        await loadTestCases()
      } catch (error) {
        handleError(error, isEditing.value ? '更新测试用例失败' : '创建测试用例失败')
      }
    }
    
    const handleDelete = async (testCase) => {
      try {
        await store.deleteTestCase(testCase.id)
        showSuccess('测试用例删除成功')
        await loadTestCases()
      } catch (error) {
        handleError(error, '删除测试用例失败')
      }
    }
    
    const handleRun = async (testCase) => {
      try {
        // TODO: 实现运行测试用例的API调用
        showSuccess(`测试用例 "${testCase.name}" 已开始运行`)
      } catch (error) {
        handleError(error, '运行测试用例失败')
      }
    }
    
    const handlePageChange = (page) => {
      loadTestCases({ page })
    }
    
    const handleSearch = (query) => {
      loadTestCases({ search: query, page: 1 })
    }
    
    const handleFilter = (filters) => {
      loadTestCases({ ...filters, page: 1 })
    }
    
    /**
     * 获取状态样式类
     * @param {string} status - 状态值
     * @returns {string} CSS类名
     */
    const getStatusClass = (status) => {
      const statusClasses = {
        'active': 'bg-green-100 text-green-800',
        'inactive': 'bg-gray-100 text-gray-800',
        'pending': 'bg-yellow-100 text-yellow-800',
        'running': 'bg-blue-100 text-blue-800',
        'completed': 'bg-green-100 text-green-800',
        'failed': 'bg-red-100 text-red-800',
        'cancelled': 'bg-gray-100 text-gray-800',
      }
      return statusClasses[status] || 'bg-gray-100 text-gray-800'
    }
    
    // 生命周期
    onMounted(async () => {
      try {
        await loadTestCases()
      } catch (error) {
        console.error('TestCases组件挂载失败:', error)
        handleError(error, '加载测试用例失败')
        // 确保页面不会因为数据加载失败而空白
        loading.value = false
      }
    })
    
    return {
      // 响应式数据
      currentView,
      selectedTestCase,
      isEditing,
      loading,
      loadingHistory,
      runHistory,
      showCreateModal,
      editingTestCase,
      submitting,
      form,
      
      // 计算属性
      testCases,
      pagination,
      
      // 方法
      showList,
      showCreateForm,
      showEditForm,
      showDetail,
      closeModal,
      submitForm,
      getScriptPlaceholder,
      loadTestCases,
      loadRunHistory,
      handleSave,
      handleDelete,
      handleRun,
      handlePageChange,
      handleSearch,
      handleFilter,
      getStatusClass
    }
  }
 }
 </script>
 
 <style scoped>
 /* 测试用例视图样式 */
 .test-cases-view {
   min-height: 100vh;
   background-color: #f8fafc;
 }
 
 .page-header {
   background: white;
   border-bottom: 1px solid #e2e8f0;
   padding: 1.5rem 0;
   margin-bottom: 2rem;
 }
 
 .header-content {
   max-width: 1200px;
   margin: 0 auto;
   padding: 0 1rem;
   display: flex;
   justify-content: space-between;
   align-items: center;
 }
 
 .header-left {
   flex: 1;
 }
 
 .page-title {
   display: flex;
   align-items: center;
   gap: 0.75rem;
   font-size: 1.875rem;
   font-weight: 700;
   color: #1a202c;
   margin: 0;
 }
 
 .title-icon {
   width: 2rem;
   height: 2rem;
   color: #3182ce;
 }
 
 .page-description {
   margin: 0.5rem 0 0 0;
   color: #718096;
   font-size: 1rem;
 }
 
 .header-actions {
   display: flex;
   gap: 1rem;
 }
 
 .btn {
   display: inline-flex;
   align-items: center;
   gap: 0.5rem;
   padding: 0.75rem 1.5rem;
   border-radius: 0.5rem;
   font-weight: 500;
   text-decoration: none;
   transition: all 0.2s;
   border: none;
   cursor: pointer;
   font-size: 0.875rem;
 }
 
 .btn svg {
   width: 1rem;
   height: 1rem;
 }
 
 .btn-primary {
   background-color: #3182ce;
   color: white;
 }
 
 .btn-primary:hover:not(:disabled) {
   background-color: #2c5aa0;
   transform: translateY(-1px);
 }
 
 .btn:disabled {
   opacity: 0.6;
   cursor: not-allowed;
 }
 
 .main-content {
   max-width: 1200px;
   margin: 0 auto;
   padding: 0 1rem;
 }
 
 .list-view,
 .editor-view,
 .detail-view {
   background: white;
   border-radius: 0.75rem;
   box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
   overflow: hidden;
 }
 
 /* 响应式设计 */
 @media (max-width: 768px) {
   .header-content {
     flex-direction: column;
     gap: 1rem;
     align-items: stretch;
   }
   
   .header-actions {
     justify-content: center;
   }
   
   .page-title {
     font-size: 1.5rem;
     justify-content: center;
   }
   
   .page-description {
     text-align: center;
   }
 }
 </style>