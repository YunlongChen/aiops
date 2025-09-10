<!--
  AIOps测试管理平台 - 测试脚本页面
  管理多语言测试脚本的创建、编辑和执行
-->

<template>
  <div class="space-y-6">
    <!-- 页面标题和操作按钮 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          测试脚本
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          管理和执行多语言测试脚本
        </p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
          @click="showCreateModal = true"
          class="btn-primary"
        >
          创建测试脚本
        </button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">搜索</label>
            <input
              v-model="searchQuery"
              type="text"
              class="input-field"
              placeholder="搜索脚本名称或描述"
            >
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">语言</label>
            <select v-model="languageFilter" class="input-field">
              <option value="">所有语言</option>
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
            <label class="block text-sm font-medium text-gray-700">测试用例</label>
            <select v-model="testCaseFilter" class="input-field">
              <option value="">所有测试用例</option>
              <option v-for="testCase in testCases" :key="testCase.id" :value="testCase.id">
                {{ testCase.name }}
              </option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              @click="loadTestScripts"
              class="btn-secondary w-full"
            >
              搜索
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试脚本列表 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">名称</th>
                <th class="table-header">语言</th>
                <th class="table-header">测试用例</th>
                <th class="table-header">描述</th>
                <th class="table-header">创建时间</th>
                <th class="table-header">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="script in testScripts" :key="script.id">
                <td class="table-cell font-medium">{{ script.name }}</td>
                <td class="table-cell">
                  <span :class="getLanguageClass(script.language)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ script.language.toUpperCase() }}
                  </span>
                </td>
                <td class="table-cell">{{ getTestCaseName(script.test_case_id) }}</td>
                <td class="table-cell">{{ script.description || '-' }}</td>
                <td class="table-cell">{{ formatDate(script.created_at) }}</td>
                <td class="table-cell">
                  <div class="flex space-x-2">
                    <button
                      @click="executeScript(script)"
                      class="text-green-600 hover:text-green-900 text-sm"
                    >
                      执行
                    </button>
                    <button
                      @click="editScript(script)"
                      class="text-indigo-600 hover:text-indigo-900 text-sm"
                    >
                      编辑
                    </button>
                    <button
                      @click="deleteScript(script.id)"
                      class="text-red-600 hover:text-red-900 text-sm"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="testScripts.length === 0">
                <td colspan="6" class="table-cell text-center text-gray-500">
                  暂无测试脚本
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

    <!-- 创建/编辑测试脚本模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ editingScript ? '编辑测试脚本' : '创建测试脚本' }}
          </h3>
          <form @submit.prevent="submitForm">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- 左侧：基本信息 -->
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">脚本名称 *</label>
                  <input
                    v-model="form.name"
                    type="text"
                    required
                    class="input-field"
                    placeholder="输入脚本名称"
                  >
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">测试用例 *</label>
                  <select
                    v-model="form.test_case_id"
                    class="input-field"
                    required
                  >
                    <option value="">请选择测试用例</option>
                    <option v-for="testCase in testCases" :key="testCase.id" :value="testCase.id">
                      {{ testCase.name }}
                    </option>
                  </select>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">脚本语言 *</label>
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
                  <label class="block text-sm font-medium text-gray-700">描述</label>
                  <textarea
                    v-model="form.description"
                    class="input-field"
                    rows="3"
                    placeholder="输入脚本描述"
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
                
                <div class="grid grid-cols-2 gap-4">
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
                  <div>
                    <label class="block text-sm font-medium text-gray-700">重试次数</label>
                    <input
                      v-model.number="form.retry_count"
                      type="number"
                      class="input-field"
                      placeholder="默认0次"
                      min="0"
                      max="10"
                    >
                  </div>
                </div>
              </div>
              
              <!-- 右侧：脚本内容 -->
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">脚本内容 *</label>
                  <textarea
                    v-model="form.script_content"
                    class="input-field font-mono text-sm"
                    rows="15"
                    required
                    :placeholder="getScriptPlaceholder()"
                  ></textarea>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">环境变量</label>
                  <textarea
                    v-model="environmentVarsText"
                    class="input-field font-mono text-sm"
                    rows="4"
                    placeholder="KEY1=value1\nKEY2=value2"
                  ></textarea>
                  <p class="text-xs text-gray-500 mt-1">每行一个环境变量，格式：KEY=value</p>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700">依赖包</label>
                  <textarea
                    v-model="dependenciesText"
                    class="input-field font-mono text-sm"
                    rows="3"
                    placeholder="requests\nnumpy\npandas"
                  ></textarea>
                  <p class="text-xs text-gray-500 mt-1">每行一个依赖包名称</p>
                </div>
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
                {{ submitting ? '提交中...' : (editingScript ? '更新' : '创建') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 执行结果模态框 -->
    <div v-if="showExecutionModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            脚本执行结果 - {{ executingScript?.name }}
          </h3>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">执行状态</label>
                <span :class="getExecutionStatusClass(executionResult?.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                  {{ getExecutionStatusText(executionResult?.status) }}
                </span>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">执行时间</label>
                <span class="text-sm text-gray-900">{{ executionResult?.execution_time_ms }}ms</span>
              </div>
            </div>
            
            <div v-if="executionResult?.stdout">
              <label class="block text-sm font-medium text-gray-700">标准输出</label>
              <pre class="bg-gray-100 p-3 rounded-md text-sm font-mono whitespace-pre-wrap">{{ executionResult.stdout }}</pre>
            </div>
            
            <div v-if="executionResult?.stderr">
              <label class="block text-sm font-medium text-gray-700">错误输出</label>
              <pre class="bg-red-50 p-3 rounded-md text-sm font-mono whitespace-pre-wrap text-red-700">{{ executionResult.stderr }}</pre>
            </div>
            
            <div v-if="executionResult?.exit_code !== undefined">
              <label class="block text-sm font-medium text-gray-700">退出码</label>
              <span class="text-sm" :class="executionResult.exit_code === 0 ? 'text-green-600' : 'text-red-600'">
                {{ executionResult.exit_code }}
              </span>
            </div>
          </div>
          
          <div class="flex justify-end mt-6">
            <button
              @click="closeExecutionModal"
              class="btn-secondary"
            >
              关闭
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 测试脚本页面组件逻辑
 * 负责管理多语言测试脚本的创建、编辑和执行
 */
import { testScriptsAPI, testCasesAPI } from '../services/api'
import dayjs from 'dayjs'

export default {
  name: 'TestScripts',
  data() {
    return {
      searchQuery: '',
      languageFilter: '',
      testCaseFilter: '',
      showCreateModal: false,
      showExecutionModal: false,
      editingScript: null,
      executingScript: null,
      executionResult: null,
      submitting: false,
      testScripts: [],
      testCases: [],
      pagination: {
        page: 1,
        limit: 10,
        total: 0,
      },
      form: {
        test_case_id: '',
        name: '',
        description: '',
        language: '',
        script_content: '',
        docker_image: '',
        timeout_seconds: 30,
        retry_count: 0,
      },
      environmentVarsText: '',
      dependenciesText: '',
    }
  },
  
  computed: {
    totalPages() {
      return Math.ceil(this.pagination.total / this.pagination.limit)
    },
  },
  
  async mounted() {
    await this.loadTestCases()
    await this.loadTestScripts()
  },
  
  methods: {
    /**
     * 获取脚本占位符文本
     */
    getScriptPlaceholder() {
      const placeholders = {
        python: 'print("Hello, World!")\n# 编写你的Python测试脚本\n# 可以使用 sys.argv 获取输入参数\n# 使用 print() 输出结果',
        javascript: 'console.log("Hello, World!");\n// 编写你的JavaScript测试脚本\n// 可以使用 process.argv 获取输入参数\n// 使用 console.log() 输出结果',
        shell: 'echo "Hello, World!"\n# 编写你的Shell测试脚本\n# 可以使用 $1, $2 等获取输入参数\n# 使用 echo 输出结果',
        go: 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n    // 编写你的Go测试脚本\n}',
        rust: 'fn main() {\n    println!("Hello, World!");\n    // 编写你的Rust测试脚本\n}',
        java: 'public class TestScript {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n        // 编写你的Java测试脚本\n    }\n}',
        docker: '# Docker命令或Dockerfile内容\necho "Hello, World!"\n# 或者编写Dockerfile:\n# FROM python:3.9-slim\n# COPY . /app\n# WORKDIR /app\n# RUN pip install -r requirements.txt\n# CMD ["python", "script.py"]'
      }
      return placeholders[this.form.language] || '输入测试脚本内容'
    },

    /**
     * 加载测试用例列表
     */
    async loadTestCases() {
      try {
        const response = await testCasesAPI.list({ limit: 1000 })
        this.testCases = response.data.test_cases || []
      } catch (error) {
        console.error('加载测试用例失败:', error)
      }
    },

    /**
     * 加载测试脚本列表
     */
    async loadTestScripts() {
      try {
        const params = {
          page: this.pagination.page,
          page_size: this.pagination.limit,
        }
        
        if (this.searchQuery) {
          params.search = this.searchQuery
        }
        
        if (this.languageFilter) {
          params.language = this.languageFilter
        }
        
        if (this.testCaseFilter) {
          params.test_case_id = this.testCaseFilter
        }
        
        const response = await testScriptsAPI.list(params)
        this.testScripts = response.data.scripts || []
        this.pagination.total = response.data.total || 0
      } catch (error) {
        console.error('加载测试脚本失败:', error)
        this.testScripts = []
      }
    },
    
    /**
     * 获取测试用例名称
     */
    getTestCaseName(testCaseId) {
      const testCase = this.testCases.find(tc => tc.id === testCaseId)
      return testCase ? testCase.name : '-'
    },
    
    /**
     * 获取语言样式类
     */
    getLanguageClass(language) {
      const classes = {
        python: 'bg-blue-100 text-blue-800',
        javascript: 'bg-yellow-100 text-yellow-800',
        shell: 'bg-gray-100 text-gray-800',
        go: 'bg-cyan-100 text-cyan-800',
        rust: 'bg-orange-100 text-orange-800',
        java: 'bg-red-100 text-red-800',
        docker: 'bg-purple-100 text-purple-800',
      }
      return classes[language] || 'bg-gray-100 text-gray-800'
    },
    
    /**
     * 获取执行状态样式类
     */
    getExecutionStatusClass(status) {
      const classes = {
        success: 'bg-green-100 text-green-800',
        failed: 'bg-red-100 text-red-800',
        timeout: 'bg-yellow-100 text-yellow-800',
        error: 'bg-red-100 text-red-800',
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    },
    
    /**
     * 获取执行状态文本
     */
    getExecutionStatusText(status) {
      const texts = {
        success: '成功',
        failed: '失败',
        timeout: '超时',
        error: '错误',
      }
      return texts[status] || '未知'
    },
    
    /**
     * 格式化日期
     */
    formatDate(dateString) {
      if (!dateString) return '-'
      return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
    },
    
    /**
     * 上一页
     */
    async previousPage() {
      if (this.pagination.page > 1) {
        this.pagination.page--
        await this.loadTestScripts()
      }
    },
    
    /**
     * 下一页
     */
    async nextPage() {
      if (this.pagination.page < this.totalPages) {
        this.pagination.page++
        await this.loadTestScripts()
      }
    },
    
    /**
     * 编辑脚本
     */
    editScript(script) {
      this.editingScript = script
      this.form = {
        test_case_id: script.test_case_id,
        name: script.name,
        description: script.description || '',
        language: script.language,
        script_content: script.script_content,
        docker_image: script.docker_image || '',
        timeout_seconds: script.timeout_seconds || 30,
        retry_count: script.retry_count || 0,
      }
      
      // 处理环境变量
      if (script.environment_vars) {
        this.environmentVarsText = Object.entries(script.environment_vars)
          .map(([key, value]) => `${key}=${value}`)
          .join('\n')
      } else {
        this.environmentVarsText = ''
      }
      
      // 处理依赖包
      if (script.dependencies) {
        this.dependenciesText = script.dependencies.join('\n')
      } else {
        this.dependenciesText = ''
      }
      
      this.showCreateModal = true
    },
    
    /**
     * 删除脚本
     */
    async deleteScript(id) {
      if (confirm('确定要删除这个测试脚本吗？')) {
        try {
          await testScriptsAPI.delete(id)
          await this.loadTestScripts()
        } catch (error) {
          alert('删除失败: ' + error.message)
        }
      }
    },
    
    /**
     * 执行脚本
     */
    async executeScript(script) {
      this.executingScript = script
      this.executionResult = null
      this.showExecutionModal = true
      
      try {
        const response = await testScriptsAPI.execute(script.id)
        this.executionResult = response.data.execution_result
      } catch (error) {
        this.executionResult = {
          status: 'error',
          stderr: error.message,
          execution_time_ms: 0,
          exit_code: -1
        }
      }
    },
    
    /**
     * 提交表单
     */
    async submitForm() {
      this.submitting = true
      try {
        // 处理环境变量
        const environmentVars = {}
        if (this.environmentVarsText.trim()) {
          this.environmentVarsText.split('\n').forEach(line => {
            const [key, ...valueParts] = line.split('=')
            if (key && valueParts.length > 0) {
              environmentVars[key.trim()] = valueParts.join('=').trim()
            }
          })
        }
        
        // 处理依赖包
        const dependencies = this.dependenciesText.trim() 
          ? this.dependenciesText.split('\n').map(dep => dep.trim()).filter(dep => dep)
          : []
        
        const formData = {
          ...this.form,
          environment_vars: Object.keys(environmentVars).length > 0 ? environmentVars : null,
          dependencies: dependencies.length > 0 ? dependencies : null,
        }
        
        if (this.editingScript) {
          await testScriptsAPI.update(this.editingScript.id, formData)
        } else {
          await testScriptsAPI.create(formData)
        }
        
        this.closeModal()
        await this.loadTestScripts()
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
      this.editingScript = null
      this.form = {
        test_case_id: '',
        name: '',
        description: '',
        language: '',
        script_content: '',
        docker_image: '',
        timeout_seconds: 30,
        retry_count: 0,
      }
      this.environmentVarsText = ''
      this.dependenciesText = ''
    },
    
    /**
     * 关闭执行结果模态框
     */
    closeExecutionModal() {
      this.showExecutionModal = false
      this.executingScript = null
      this.executionResult = null
    },
  },
}
</script>

<style scoped>
/* 组件特定样式 */
.table-header {
  @apply px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider;
}

.table-cell {
  @apply px-6 py-4 whitespace-nowrap text-sm text-gray-900;
}

.btn-primary {
  @apply inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500;
}

.btn-secondary {
  @apply inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500;
}

.input-field {
  @apply mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm;
}

.card {
  @apply bg-white overflow-hidden shadow rounded-lg;
}
</style>