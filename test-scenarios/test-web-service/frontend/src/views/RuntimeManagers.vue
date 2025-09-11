<!--
  AIOps测试管理平台 - 运行时管理器页面
  管理Docker、Kubernetes等运行时环境
-->

<template>
  <div class="space-y-6">
    <!-- 页面标题和操作按钮 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          运行时管理器
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          管理Docker、Kubernetes等运行时环境
        </p>
      </div>
      <div class="mt-4 flex space-x-3 md:mt-0 md:ml-4">
        <button
          @click="showPlatformInfo = true"
          class="btn-secondary"
        >
          平台信息
        </button>
        <button
          @click="showCreateModal = true"
          class="btn-primary"
        >
          添加运行时
        </button>
      </div>
    </div>

    <!-- 平台信息卡片 -->
    <div v-if="platformInfo" class="card">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">平台能力检测</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="bg-gray-50 p-4 rounded-lg">
            <h4 class="font-medium text-gray-900">系统信息</h4>
            <p class="text-sm text-gray-600 mt-1">平台: {{ platformInfo.platform }}</p>
            <p class="text-sm text-gray-600">架构: {{ platformInfo.arch }}</p>
          </div>
          <div v-for="(runtime, type) in platformInfo.runtimes" :key="type" class="bg-gray-50 p-4 rounded-lg">
            <h4 class="font-medium text-gray-900 capitalize">{{ type }}</h4>
            <div class="flex items-center mt-1">
              <span :class="runtime.available ? 'text-green-600' : 'text-red-600'" class="text-sm font-medium">
                {{ runtime.available ? '可用' : '不可用' }}
              </span>
              <button
                v-if="runtime.available"
                @click="showSetupGuide(type)"
                class="ml-2 text-xs text-blue-600 hover:text-blue-800"
              >
                设置指引
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 运行时管理器列表 -->
    <div class="card">
      <div class="px-4 py-5 sm:p-6">
        <div class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th class="table-header">名称</th>
                <th class="table-header">类型</th>
                <th class="table-header">状态</th>
                <th class="table-header">标签</th>
                <th class="table-header">创建时间</th>
                <th class="table-header">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="manager in runtimeManagers" :key="manager.id">
                <td class="table-cell font-medium">{{ manager.name }}</td>
                <td class="table-cell">
                  <span :class="getTypeClass(manager.runtime_type)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ getTypeText(manager.runtime_type) }}
                  </span>
                </td>
                <td class="table-cell">
                  <span :class="getStatusClass(manager.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ getStatusText(manager.status) }}
                  </span>
                </td>
                <td class="table-cell">
                  <div v-if="manager.tags && manager.tags.length > 0" class="flex flex-wrap gap-1">
                    <span
                      v-for="tag in manager.tags"
                      :key="tag"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                    >
                      {{ tag }}
                    </span>
                  </div>
                  <span v-else class="text-gray-400 text-sm">无标签</span>
                </td>
                <td class="table-cell">{{ formatDate(manager.created_at) }}</td>
                <td class="table-cell">
                  <div class="flex space-x-2">
                    <button
                      @click="testConnection(manager.id)"
                      :disabled="testingConnection === manager.id"
                      class="text-blue-600 hover:text-blue-900 text-sm"
                    >
                      {{ testingConnection === manager.id ? '测试中...' : '测试连接' }}
                    </button>
                    <button
                      @click="performHealthCheck(manager.id)"
                      :disabled="healthChecking === manager.id"
                      class="text-green-600 hover:text-green-900 text-sm"
                    >
                      {{ healthChecking === manager.id ? '检查中...' : '健康检查' }}
                    </button>
                    <button
                      @click="editManager(manager)"
                      class="text-indigo-600 hover:text-indigo-900 text-sm"
                    >
                      编辑
                    </button>
                    <button
                      @click="deleteManager(manager.id)"
                      class="text-red-600 hover:text-red-900 text-sm"
                    >
                      删除
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="runtimeManagers.length === 0">
                <td colspan="6" class="table-cell text-center text-gray-500">
                  暂无运行时管理器
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 创建/编辑运行时管理器模态框 -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ editingManager ? '编辑运行时管理器' : '创建运行时管理器' }}
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
                  placeholder="输入运行时管理器名称"
                >
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">类型</label>
                <select v-model="form.runtime_type" required class="input-field">
                  <option value="">选择运行时类型</option>
                  <option value="docker">Docker</option>
                  <option value="kubernetes">Kubernetes</option>
                  <option value="local">本地</option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">标签</label>
                <input
                  v-model="tagsInput"
                  type="text"
                  class="input-field"
                  placeholder="输入标签，用逗号分隔，如：测试环境,生产环境"
                  @input="updateTags"
                >
                <div v-if="form.tags && form.tags.length > 0" class="mt-2 flex flex-wrap gap-2">
                  <span
                    v-for="(tag, index) in form.tags"
                    :key="index"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                  >
                    {{ tag }}
                    <button
                      type="button"
                      @click="removeTag(index)"
                      class="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                </div>
              </div>
              
              <!-- Docker配置 -->
              <div v-if="form.runtime_type === 'docker'" class="space-y-3">
                <h4 class="text-sm font-medium text-gray-700">Docker配置</h4>
                <div>
                  <label class="block text-sm text-gray-600">Docker Host</label>
                  <input
                    v-model="form.config.host"
                    type="text"
                    class="input-field"
                    placeholder="unix:///var/run/docker.sock"
                  >
                </div>
                <div>
                  <label class="block text-sm text-gray-600">API版本</label>
                  <input
                    v-model="form.config.api_version"
                    type="text"
                    class="input-field"
                    placeholder="1.41"
                  >
                </div>
              </div>
              
              <!-- Kubernetes配置 -->
              <div v-if="form.runtime_type === 'kubernetes'" class="space-y-3">
                <h4 class="text-sm font-medium text-gray-700">Kubernetes配置</h4>
                <div>
                  <label class="block text-sm text-gray-600">集群URL</label>
                  <input
                    v-model="form.config.cluster_url"
                    type="text"
                    class="input-field"
                    placeholder="https://kubernetes.default.svc"
                  >
                </div>
                <div>
                  <label class="block text-sm text-gray-600">命名空间</label>
                  <input
                    v-model="form.config.namespace"
                    type="text"
                    class="input-field"
                    placeholder="default"
                  >
                </div>
                <div>
                  <label class="block text-sm text-gray-600">Token</label>
                  <input
                    v-model="form.config.token"
                    type="password"
                    class="input-field"
                    placeholder="Kubernetes访问令牌"
                  >
                </div>
              </div>
              
              <!-- 本地配置 -->
              <div v-if="form.runtime_type === 'local'" class="space-y-3">
                <h4 class="text-sm font-medium text-gray-700">本地配置</h4>
                <div>
                  <label class="block text-sm text-gray-600">工作目录</label>
                  <input
                    v-model="form.config.working_directory"
                    type="text"
                    class="input-field"
                    placeholder="/tmp/test-workspace"
                  >
                </div>
                <div>
                  <label class="block text-sm text-gray-600">环境变量</label>
                  <textarea
                    v-model="form.config.environment_variables"
                    class="input-field"
                    rows="3"
                    placeholder="KEY1=value1\nKEY2=value2"
                  ></textarea>
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
                {{ submitting ? '提交中...' : (editingManager ? '更新' : '创建') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <!-- 设置指引模态框 -->
  <div v-if="showSetupGuideModal" class="modal-overlay">
    <div class="modal-container">
      <div class="modal-content">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            {{ currentGuideType }} 设置指引
          </h3>
          <button @click="closeSetupGuide" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="max-h-96 overflow-y-auto">
          <div v-if="setupGuide" class="prose prose-sm max-w-none">
            <div v-for="(step, index) in setupGuide.steps" :key="index" class="mb-4">
              <h4 class="font-medium text-gray-900">{{ step.title }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ step.description }}</p>
              <div v-if="step.commands && step.commands.length > 0" class="mt-2">
                <div v-for="(command, cmdIndex) in step.commands" :key="cmdIndex" class="bg-gray-100 p-2 rounded text-sm font-mono mb-1">
                  {{ command }}
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex justify-end mt-6">
          <button @click="closeSetupGuide" class="btn-secondary">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- 健康检查结果模态框 -->
  <div v-if="showHealthCheckModal" class="modal-overlay">
    <div class="modal-container">
      <div class="modal-content">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">
            健康检查结果
          </h3>
          <button @click="closeHealthCheck" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div v-if="healthCheckResult">
          <div class="mb-4">
            <div class="flex items-center">
              <span :class="healthCheckResult.healthy ? 'text-green-600' : 'text-red-600'" class="font-medium">
                {{ healthCheckResult.healthy ? '健康' : '不健康' }}
              </span>
            </div>
            <p class="text-sm text-gray-600 mt-1">{{ healthCheckResult.message }}</p>
          </div>
          <div v-if="healthCheckResult.details" class="space-y-3">
            <div v-for="(detail, key) in healthCheckResult.details" :key="key" class="bg-gray-50 p-3 rounded">
              <h4 class="font-medium text-gray-900 capitalize">{{ key.replace('_', ' ') }}</h4>
              <p class="text-sm text-gray-600 mt-1">{{ detail }}</p>
            </div>
          </div>
        </div>
        <div class="flex justify-end mt-6">
          <button @click="closeHealthCheck" class="btn-secondary">
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 运行时管理器页面组件逻辑
 * 负责管理Docker、Kubernetes等运行时环境
 */
import { useRuntimeManagersStore } from '../stores'
import dayjs from 'dayjs'

export default {
  name: 'RuntimeManagers',
  data() {
    return {
      showCreateModal: false,
      editingManager: null,
      submitting: false,
      testingConnection: null,
      healthChecking: null,
      showPlatformInfo: false,
      showSetupGuideModal: false,
      showHealthCheckModal: false,
      platformInfo: null,
      setupGuide: null,
      healthCheckResult: null,
      currentGuideType: '',
      form: {
        name: '',
        runtime_type: '',
        config: {},
        tags: [],
      },
      tagsInput: '',
    }
  },
  
  computed: {
    runtimeManagers() {
      const store = useRuntimeManagersStore()
      return store.runtimeManagers
    },
  },
  
  async mounted() {
    try {
      await this.loadRuntimeManagers()
      await this.loadPlatformInfo()
    } catch (error) {
      console.error('RuntimeManagers组件挂载失败:', error)
      // 确保页面不会因为数据加载失败而空白
    }
  },
  
  methods: {
    /**
     * 加载运行时管理器列表
     */
    async loadRuntimeManagers() {
      try {
        const store = useRuntimeManagersStore()
        await store.fetchRuntimeManagers()
      } catch (error) {
        console.error('加载运行时管理器失败:', error)
      }
    },
    
    /**
     * 测试连接
     * @param {string} id - 运行时管理器ID
     */
    async testConnection(id) {
      this.testingConnection = id
      try {
        const store = useRuntimeManagersStore()
        const result = await store.testConnection(id)
        if (result.success) {
          this.$message.success(`${this.runtimeManagers.find(rm => rm.id === id)?.name || '运行时管理器'} 连接测试成功`);
        } else {
          this.$message.error(`连接测试失败: ${result.message || '未知错误'}`);
        }
      } catch (error) {
        this.$message.error('连接测试失败: ' + (error.message || '网络错误'))
      } finally {
        this.testingConnection = null
      }
    },
    
    /**
     * 编辑运行时管理器
     * @param {Object} manager - 运行时管理器对象
     */
    editManager(manager) {
      this.editingManager = manager
      this.form = {
        name: manager.name,
        runtime_type: manager.runtime_type,
        config: { ...manager.config },
      }
      this.showCreateModal = true
    },
    
    /**
     * 删除运行时管理器
     * @param {string} id - 运行时管理器ID
     */
    async deleteManager(id) {
      if (confirm('确定要删除这个运行时管理器吗？')) {
        try {
          const store = useRuntimeManagersStore()
          await store.deleteRuntimeManager(id)
          await this.loadRuntimeManagers()
        } catch (error) {
          this.$message.error('删除失败: ' + (error.message || '网络错误'))
        }
      }
    },

    /**
     * 加载平台信息
     */
    async loadPlatformInfo() {
      try {
        const store = useRuntimeManagersStore()
        this.platformInfo = await store.getPlatformInfo()
      } catch (error) {
        console.error('加载平台信息失败:', error)
      }
    },

    /**
     * 显示设置指引
     * @param {string} runtimeType - 运行时类型
     */
    async showSetupGuide(runtimeType) {
      try {
        const store = useRuntimeManagersStore()
        this.setupGuide = await store.getSetupGuide(runtimeType)
        this.currentGuideType = runtimeType
        this.showSetupGuideModal = true
      } catch (error) {
        this.$message.error('获取设置指引失败: ' + (error.message || '网络错误'))
      }
    },

    /**
     * 关闭设置指引模态框
     */
    closeSetupGuide() {
      this.showSetupGuideModal = false
      this.setupGuide = null
      this.currentGuideType = ''
    },

    /**
     * 执行健康检查
     * @param {string} id - 运行时管理器ID
     */
    async performHealthCheck(id) {
      this.healthChecking = id
      try {
        const store = useRuntimeManagersStore()
        this.healthCheckResult = await store.healthCheck(id)
        this.showHealthCheckModal = true
      } catch (error) {
        this.$message.error('健康检查失败: ' + (error.message || '网络错误'))
      } finally {
        this.healthChecking = null
      }
    },

    /**
     * 关闭健康检查结果模态框
     */
    closeHealthCheck() {
      this.showHealthCheckModal = false
      this.healthCheckResult = null
    },
    
    /**
     * 提交表单
     */
    async submitForm() {
      this.submitting = true
      try {
        const store = useRuntimeManagersStore()
        
        if (this.editingManager) {
          await store.updateRuntimeManager(this.editingManager.id, this.form)
          this.$message.success('运行时管理器更新成功')
        } else {
          await store.createRuntimeManager(this.form)
          this.$message.success('运行时管理器创建成功')
        }
        
        this.closeModal()
        await this.loadRuntimeManagers()
      } catch (error) {
        this.$message.error('操作失败: ' + (error.message || '网络错误'))
      } finally {
        this.submitting = false
      }
    },
    
    /**
     * 关闭模态框
     */
    closeModal() {
      this.showCreateModal = false
      this.editingManager = null
      this.form = {
        name: '',
        runtime_type: '',
        config: {},
        tags: [],
      }
      this.tagsInput = ''
    },
    
    /**
     * 获取类型样式类
     * @param {string} type - 运行时类型
     * @returns {string} CSS类名
     */
    getTypeClass(type) {
      const typeClasses = {
        'docker': 'bg-blue-100 text-blue-800',
        'kubernetes': 'bg-green-100 text-green-800',
        'local': 'bg-gray-100 text-gray-800',
      }
      return typeClasses[type] || 'bg-gray-100 text-gray-800'
    },
    
    /**
     * 获取类型文本
     * @param {string} type - 运行时类型
     * @returns {string} 类型文本
     */
    getTypeText(type) {
      const typeTexts = {
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        'local': '本地',
      }
      return typeTexts[type] || '未知'
    },
    
    /**
     * 获取状态样式类
     * @param {string} status - 状态值
     * @returns {string} CSS类名
     */
    getStatusClass(status) {
      const statusClasses = {
        'active': 'bg-green-100 text-green-800',
        'inactive': 'bg-red-100 text-red-800',
        'unknown': 'bg-gray-100 text-gray-800',
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
        'unknown': '未知',
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
    
    /**
     * 更新标签
     */
    updateTags() {
      if (this.tagsInput) {
        this.form.tags = this.tagsInput
          .split(',')
          .map(tag => tag.trim())
          .filter(tag => tag.length > 0)
      } else {
        this.form.tags = []
      }
    },
    
    /**
     * 移除标签
     * @param {number} index - 标签索引
     */
    removeTag(index) {
      this.form.tags.splice(index, 1)
      this.tagsInput = this.form.tags.join(', ')
    },
  },
}
</script>