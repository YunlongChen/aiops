/**
 * AIOps测试管理平台 - 状态管理
 * 使用Pinia管理应用的全局状态
 */

import { defineStore } from 'pinia'
import axios from 'axios'

/**
 * API客户端配置
 * 设置基础URL和请求拦截器
 */
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证token等
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

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
        this.setLoading(true)
        this.setError(null)
        const response = await api.get('/system/info')
        this.systemInfo = response.data
      } catch (error) {
        this.setError('获取系统信息失败')
        throw error
      } finally {
        this.setLoading(false)
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
        const response = await api.get('/test-cases', { params })
        this.testCases = response.data
        this.pagination = response.pagination
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
        const response = await api.post('/test-cases', testCase)
        this.testCases.unshift(response.data)
        return response.data
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
        const response = await api.get('/test-runs', { params })
        this.testRuns = response.data
        this.pagination = response.pagination
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
        const response = await api.post('/test-runs', testRunData)
        this.testRuns.unshift(response.data)
        return response.data
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
        const response = await api.get('/runtime-managers')
        this.runtimeManagers = response.data
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
        const response = await api.post('/runtime-managers', runtimeManager)
        this.runtimeManagers.push(response.data)
        return response.data
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
        const response = await api.post(`/runtime-managers/${id}/test`)
        return response.data
      } catch (error) {
        console.error('测试连接失败:', error)
        throw error
      }
    },
  },
})

export { api }