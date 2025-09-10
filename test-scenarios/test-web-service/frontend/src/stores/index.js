/**
 * AIOps测试管理平台 - 状态管理
 * 使用Pinia管理应用的全局状态
 */

import { defineStore } from 'pinia'
import { 
  systemAPI, 
  testCasesAPI, 
  testRunsAPI, 
  runtimeManagersAPI,
  usersAPI,
  settingsAPI
} from '../services/api.js'

/**
 * 主应用状态store
 * 管理全局应用状态和通用数据
 */
export const useAppStore = defineStore('app', {
  state: () => ({
    loading: false,
    error: null,
    systemInfo: null,
  }),
  
  getters: {
    isLoading: (state) => state.loading,
    hasError: (state) => !!state.error,
  },
  
  actions: {
    /**
     * 设置加载状态
     * @param {boolean} loading - 加载状态
     */
    setLoading(loading) {
      this.loading = loading
    },
    
    /**
     * 设置错误信息
     * @param {string|null} error - 错误信息
     */
    setError(error) {
      this.error = error
    },
    
    /**
     * 获取系统信息
     */
    async fetchSystemInfo() {
      try {
        this.loading = true
        const response = await systemAPI.getSystemInfo()
        this.systemInfo = response
      } catch (error) {
        this.setError(error.message)
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 获取系统统计
     */
    async fetchSystemStats() {
      try {
        return await systemAPI.getSystemStats()
      } catch (error) {
        this.setError(error.message)
        throw error
      }
    },
    
    // 用户管理相关actions
    /**
     * 用户登录
     * @param {Object} credentials - 登录凭据
     */
    async login(credentials) {
      try {
        const response = await usersAPI.login(credentials)
        const loginData = response.data || response
        this.currentUser = loginData.user
        this.isAuthenticated = true
        // 存储token到localStorage
        if (loginData.token) {
          localStorage.setItem('auth_token', loginData.token)
        }
        return loginData
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },
    
    /**
     * 用户登出
     */
    async logout() {
      try {
        await usersAPI.logout()
        this.currentUser = null
        this.isAuthenticated = false
        localStorage.removeItem('auth_token')
      } catch (error) {
        console.error('登出失败:', error)
        // 即使API调用失败，也要清除本地状态
        this.currentUser = null
        this.isAuthenticated = false
        localStorage.removeItem('auth_token')
      }
    },
    
    /**
      * 获取当前用户信息
      */
     async fetchCurrentUser() {
       try {
         const response = await usersAPI.getCurrentUser()
         this.currentUser = response.data || response
         this.isAuthenticated = true
       } catch (error) {
         console.error('获取当前用户信息失败:', error)
         this.currentUser = null
         this.isAuthenticated = false
       }
     },
     
     /**
      * 获取用户列表
      * @param {Object} params - 查询参数
      */
     async fetchUsers(params = {}) {
       try {
         const response = await usersAPI.list(params)
         this.users = response.data || response
         this.usersPagination = response.pagination || { total: (response.data || response).length || 0 }
       } catch (error) {
         console.error('获取用户列表失败:', error)
         throw error
       }
     },
     
     // 设置管理相关actions
     /**
      * 获取设置列表
      * @param {Object} params - 查询参数
      */
     async fetchSettings(params = {}) {
       try {
         const response = await settingsAPI.list(params)
         this.settings = response.data || response
         this.settingsPagination = response.pagination || { total: (response.data || response).length || 0 }
       } catch (error) {
         console.error('获取设置列表失败:', error)
         throw error
       }
     },
     
     /**
      * 获取系统配置
      */
     async fetchSystemConfig() {
       try {
         const response = await settingsAPI.getSystemConfig()
         this.systemConfig = response.data || response
       } catch (error) {
         console.error('获取系统配置失败:', error)
         throw error
       }
     },
     
     /**
      * 获取用户偏好设置
      */
     async fetchUserPreferences() {
       try {
         const response = await settingsAPI.getUserPreferences()
         this.userPreferences = response.data || response
       } catch (error) {
         console.error('获取用户偏好设置失败:', error)
         throw error
       }
     },
   },
 })

/**
 * 测试用例状态store
 * 管理测试用例相关的状态和操作
 */
export const useTestCasesStore = defineStore('testCases', {
  state: () => ({
    testCases: [],
    currentTestCase: null,
    pagination: {
      page: 1,
      limit: 10,
      total: 0,
    },
  }),
  
  getters: {
    totalPages: (state) => Math.ceil(state.pagination.total / state.pagination.limit),
  },
  
  actions: {
    /**
     * 获取测试用例列表
     * @param {Object} params - 查询参数
     */
    async fetchTestCases(params = {}) {
      try {
        const response = await testCasesAPI.list(params)
        this.testCases = response.data || response
        this.pagination = response.pagination || { total: response.length || 0 }
      } catch (error) {
        console.error('获取测试用例失败:', error)
        throw error
      }
    },
    
    /**
     * 创建测试用例
     * @param {Object} testCase - 测试用例数据
     */
    async createTestCase(testCase) {
      try {
        const response = await testCasesAPI.create(testCase)
        this.testCases.unshift(response.data || response)
        return response.data || response
      } catch (error) {
        console.error('创建测试用例失败:', error)
        throw error
      }
    },
  },
})

/**
 * 测试运行状态store
 * 管理测试运行相关的状态和操作
 */
export const useTestRunsStore = defineStore('testRuns', {
  state: () => ({
    testRuns: [],
    currentTestRun: null,
    pagination: {
      page: 1,
      limit: 10,
      total: 0,
    },
  }),
  
  actions: {
    /**
     * 获取测试运行列表
     * @param {Object} params - 查询参数
     */
    async fetchTestRuns(params = {}) {
      try {
        const response = await testRunsAPI.list(params)
        this.testRuns = response.data || response
        this.pagination = response.pagination || { total: response.length || 0 }
      } catch (error) {
        console.error('获取测试运行失败:', error)
        throw error
      }
    },
    
    /**
     * 执行测试
     * @param {Object} testRunData - 测试运行数据
     */
    async executeTest(testRunData) {
      try {
        const response = await testRunsAPI.create(testRunData)
        this.testRuns.unshift(response.data || response)
        return response.data || response
      } catch (error) {
        console.error('执行测试失败:', error)
        throw error
      }
    },
  },
})

/**
 * 运行时管理器状态store
 * 管理运行时环境相关的状态和操作
 */
export const useRuntimeManagersStore = defineStore('runtimeManagers', {
  state: () => ({
    runtimeManagers: [],
    currentRuntimeManager: null,
  }),
  
  actions: {
    /**
     * 获取运行时管理器列表
     */
    async fetchRuntimeManagers() {
      try {
        const response = await runtimeManagersAPI.list()
        this.runtimeManagers = response.data || response
      } catch (error) {
        console.error('获取运行时管理器失败:', error)
        throw error
      }
    },
    
    /**
     * 创建运行时管理器
     * @param {Object} runtimeManager - 运行时管理器数据
     */
    async createRuntimeManager(runtimeManager) {
      try {
        const response = await runtimeManagersAPI.create(runtimeManager)
        this.runtimeManagers.push(response.data || response)
        return response.data || response
      } catch (error) {
        console.error('创建运行时管理器失败:', error)
        throw error
      }
    },
    
    /**
     * 测试运行时管理器连接
     * @param {string} id - 运行时管理器ID
     */
    async testConnection(id) {
      try {
        const response = await runtimeManagersAPI.test(id)
        return response.data || response
      } catch (error) {
        console.error('测试连接失败:', error)
        throw error
      }
    },

    /**
     * 更新运行时管理器
     * @param {string} id - 运行时管理器ID
     * @param {Object} runtimeManager - 运行时管理器数据
     */
    async updateRuntimeManager(id, runtimeManager) {
      try {
        const response = await runtimeManagersAPI.update(id, runtimeManager)
        const index = this.runtimeManagers.findIndex(rm => rm.id === id)
        if (index !== -1) {
          this.runtimeManagers[index] = response.data || response
        }
        return response.data || response
      } catch (error) {
        console.error('更新运行时管理器失败:', error)
        throw error
      }
    },

    /**
     * 删除运行时管理器
     * @param {string} id - 运行时管理器ID
     */
    async deleteRuntimeManager(id) {
      try {
        await runtimeManagersAPI.delete(id)
        this.runtimeManagers = this.runtimeManagers.filter(rm => rm.id !== id)
      } catch (error) {
        console.error('删除运行时管理器失败:', error)
        throw error
      }
    },

    /**
     * 获取平台信息
     */
    async getPlatformInfo() {
      try {
        const response = await runtimeManagersAPI.getPlatformInfo()
        return response.data || response
      } catch (error) {
        console.error('获取平台信息失败:', error)
        throw error
      }
    },

    /**
     * 获取设置指引
     * @param {string} runtimeType - 运行时类型
     */
    async getSetupGuide(runtimeType) {
      try {
        const response = await runtimeManagersAPI.getSetupGuide(runtimeType)
        return response.data || response
      } catch (error) {
        console.error('获取设置指引失败:', error)
        throw error
      }
    },

    /**
     * 执行健康检查
     * @param {string} id - 运行时管理器ID
     */
    async healthCheck(id) {
      try {
        const response = await runtimeManagersAPI.healthCheck(id)
        return response.data || response
      } catch (error) {
        console.error('健康检查失败:', error)
        throw error
      }
    },
  },
})

/**
 * 用户管理状态store
 * 管理用户相关的状态和操作
 */
export const useUsersStore = defineStore('users', {
  state: () => ({
    users: [],
    currentUser: null,
    isAuthenticated: false,
    pagination: {
      page: 1,
      limit: 10,
      total: 0,
    },
  }),
  
  getters: {
    totalPages: (state) => Math.ceil(state.pagination.total / state.pagination.limit),
  },
  
  actions: {
    /**
     * 获取用户列表
     * @param {Object} params - 查询参数
     */
    async fetchUsers(params = {}) {
      try {
        const response = await usersAPI.list(params)
        this.users = response.data || response
        this.pagination = response.pagination || { total: response.length || 0 }
      } catch (error) {
        console.error('获取用户列表失败:', error)
        throw error
      }
    },
    
    /**
     * 创建用户
     * @param {Object} user - 用户数据
     */
    async createUser(user) {
      try {
        const response = await usersAPI.create(user)
        this.users.unshift(response.data || response)
        return response.data || response
      } catch (error) {
        console.error('创建用户失败:', error)
        throw error
      }
    },
    
    /**
     * 更新用户
     * @param {string} id - 用户ID
     * @param {Object} user - 用户数据
     */
    async updateUser(id, user) {
      try {
        const response = await usersAPI.update(id, user)
        const index = this.users.findIndex(u => u.id === id)
        if (index !== -1) {
          this.users[index] = response.data || response
        }
        return response.data || response
      } catch (error) {
        console.error('更新用户失败:', error)
        throw error
      }
    },
    
    /**
     * 删除用户
     * @param {string} id - 用户ID
     */
    async deleteUser(id) {
      try {
        await usersAPI.delete(id)
        this.users = this.users.filter(u => u.id !== id)
      } catch (error) {
        console.error('删除用户失败:', error)
        throw error
      }
    },
    
    /**
     * 设置当前用户
     * @param {Object} user - 用户信息
     */
    setCurrentUser(user) {
      this.currentUser = user
      this.isAuthenticated = !!user
    },
  },
})

/**
 * 设置管理状态store
 * 管理系统设置相关的状态和操作
 */
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: [],
    systemConfig: null,
    userPreferences: [],
    pagination: {
      page: 1,
      limit: 10,
      total: 0,
    },
  }),
  
  getters: {
    totalPages: (state) => Math.ceil(state.pagination.total / state.pagination.limit),
  },
  
  actions: {
    /**
     * 获取设置列表
     * @param {Object} params - 查询参数
     */
    async fetchSettings(params = {}) {
      try {
        const response = await settingsAPI.list(params)
        this.settings = response.data || response
        this.pagination = response.pagination || { total: response.length || 0 }
      } catch (error) {
        console.error('获取设置列表失败:', error)
        throw error
      }
    },
    
    /**
     * 获取系统配置
     */
    async fetchSystemConfig() {
      try {
        const response = await settingsAPI.getSystemConfig()
        this.systemConfig = response.data || response
      } catch (error) {
        console.error('获取系统配置失败:', error)
        throw error
      }
    },
    
    /**
     * 更新系统配置
     * @param {Object} config - 配置数据
     */
    async updateSystemConfig(config) {
      try {
        const response = await settingsAPI.updateSystemConfig(config)
        this.systemConfig = response.data || response
        return response.data || response
      } catch (error) {
        console.error('更新系统配置失败:', error)
        throw error
      }
    },
    
    /**
     * 获取用户偏好设置
     * @param {string} userId - 用户ID
     */
    async fetchUserPreferences(userId) {
      try {
        const response = await settingsAPI.getUserPreferences(userId)
        this.userPreferences = response.data || response
      } catch (error) {
        console.error('获取用户偏好设置失败:', error)
        throw error
      }
    },
    
    /**
     * 更新用户偏好设置
     * @param {string} userId - 用户ID
     * @param {Object} preferences - 偏好设置数据
     */
    async updateUserPreferences(userId, preferences) {
      try {
        const response = await settingsAPI.updateUserPreferences(userId, preferences)
        this.userPreferences = response.data || response
        return response.data || response
      } catch (error) {
        console.error('更新用户偏好设置失败:', error)
        throw error
      }
    },
  },
})