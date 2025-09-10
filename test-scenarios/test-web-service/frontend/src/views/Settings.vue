<!--
  AIOps测试管理平台 - 设置页面
  系统配置和用户设置
-->

<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          系统设置
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          配置系统参数和用户偏好
        </p>
      </div>
    </div>

    <!-- 设置选项卡 -->
    <div class="border-b border-gray-200">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
            'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
          ]"
        >
          {{ tab.name }}
        </button>
      </nav>
    </div>

    <!-- 通用设置 -->
    <div v-if="activeTab === 'general'" class="card">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">通用设置</h3>
        
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700">系统名称</label>
            <input
              v-model="settings.general.systemName"
              type="text"
              class="input-field"
              placeholder="AIOps测试管理平台"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">默认超时时间（秒）</label>
            <input
              v-model.number="settings.general.defaultTimeout"
              type="number"
              class="input-field"
              min="1"
              max="3600"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">最大并发测试数</label>
            <input
              v-model.number="settings.general.maxConcurrentTests"
              type="number"
              class="input-field"
              min="1"
              max="100"
            >
          </div>
          
          <div class="flex items-center">
            <input
              v-model="settings.general.enableNotifications"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label class="ml-2 block text-sm text-gray-900">
              启用通知
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 存储设置 -->
    <div v-if="activeTab === 'storage'" class="card">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">存储设置</h3>
        
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700">数据保留天数</label>
            <input
              v-model.number="settings.storage.retentionDays"
              type="number"
              class="input-field"
              min="1"
              max="365"
            >
            <p class="mt-1 text-sm text-gray-500">测试结果和日志的保留时间</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">最大日志文件大小（MB）</label>
            <input
              v-model.number="settings.storage.maxLogSize"
              type="number"
              class="input-field"
              min="1"
              max="1024"
            >
          </div>
          
          <div class="flex items-center">
            <input
              v-model="settings.storage.enableCompression"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label class="ml-2 block text-sm text-gray-900">
              启用日志压缩
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 安全设置 -->
    <div v-if="activeTab === 'security'" class="card">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">安全设置</h3>
        
        <div class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700">API访问令牌</label>
            <div class="mt-1 flex rounded-md shadow-sm">
              <input
                v-model="settings.security.apiToken"
                :type="showApiToken ? 'text' : 'password'"
                class="input-field rounded-r-none"
                readonly
              >
              <button
                @click="showApiToken = !showApiToken"
                class="relative -ml-px inline-flex items-center space-x-2 rounded-r-md border border-gray-300 bg-gray-50 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100"
              >
                {{ showApiToken ? '隐藏' : '显示' }}
              </button>
            </div>
            <button
              @click="regenerateApiToken"
              class="mt-2 btn-secondary"
            >
              重新生成令牌
            </button>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">会话超时时间（分钟）</label>
            <input
              v-model.number="settings.security.sessionTimeout"
              type="number"
              class="input-field"
              min="5"
              max="1440"
            >
          </div>
          
          <div class="flex items-center">
            <input
              v-model="settings.security.enableAuditLog"
              type="checkbox"
              class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            >
            <label class="ml-2 block text-sm text-gray-900">
              启用审计日志
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="flex justify-end">
      <button
        @click="saveSettings"
        :disabled="saving"
        class="btn-primary"
      >
        {{ saving ? '保存中...' : '保存设置' }}
      </button>
    </div>
  </div>
</template>

<script>
/**
 * 设置页面组件逻辑
 * 负责系统配置和用户设置管理
 */
import { useAppStore } from '../stores'

export default {
  name: 'Settings',
  data() {
    return {
      activeTab: 'general',
      saving: false,
      showApiToken: false,
      tabs: [
        { id: 'general', name: '通用设置' },
        { id: 'storage', name: '存储设置' },
        { id: 'security', name: '安全设置' },
      ],
      settings: {
        general: {
          systemName: 'AIOps测试管理平台',
          defaultTimeout: 300,
          maxConcurrentTests: 10,
          enableNotifications: true,
        },
        storage: {
          retentionDays: 30,
          maxLogSize: 100,
          enableCompression: true,
        },
        security: {
          apiToken: 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
          sessionTimeout: 60,
          enableAuditLog: true,
        },
      },
    }
  },
  
  async mounted() {
    await this.loadSettings()
  },
  
  methods: {
    /**
     * 加载设置
     */
    async loadSettings() {
      try {
        // TODO: 从API加载设置
        console.log('加载设置')
      } catch (error) {
        console.error('加载设置失败:', error)
      }
    },
    
    /**
     * 保存设置
     */
    async saveSettings() {
      this.saving = true
      try {
        // TODO: 保存设置到API
        console.log('保存设置:', this.settings)
        
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        alert('设置保存成功')
      } catch (error) {
        alert('保存设置失败: ' + error.message)
      } finally {
        this.saving = false
      }
    },
    
    /**
     * 重新生成API令牌
     */
    async regenerateApiToken() {
      if (confirm('确定要重新生成API令牌吗？这将使现有令牌失效。')) {
        try {
          // TODO: 调用API重新生成令牌
          const newToken = 'sk-' + Math.random().toString(36).substring(2, 34)
          this.settings.security.apiToken = newToken
          alert('API令牌已重新生成')
        } catch (error) {
          alert('重新生成令牌失败: ' + error.message)
        }
      }
    },
  },
}
</script>