/**
 * AIOps测试管理平台 - API服务层
 * 统一管理所有API调用，提供类型安全和错误处理
 */

import axios from 'axios'
import errorHandler from './errorHandler'

/**
 * API客户端配置
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8888/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  paramsSerializer: {
    serialize: (params) => {
      const searchParams = new URLSearchParams()
      for (const [key, value] of Object.entries(params)) {
        if (value !== null && value !== undefined) {
          // 对于数字类型的参数，直接转换为字符串但保持数字格式
          if (typeof value === 'number') {
            searchParams.append(key, value.toString())
          } else {
            searchParams.append(key, String(value))
          }
        }
      }
      return searchParams.toString()
    }
  }
})

/**
 * 请求拦截器
 * 添加认证token和请求日志
 */
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证token（如果存在）
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加请求ID用于追踪
    config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    

    // 请求日志
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
      params: config.params,
      data: config.data
    })
    
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    errorHandler.handleNetworkError(error, {
      title: '请求发送失败',
      message: '无法发送请求到服务器'
    })
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 统一处理响应和错误
 */
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
      status: response.status,
      data: response.data
    })
    return response
  },
  (error) => {
    console.error('[API Response Error]', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      data: error.response?.data
    })
    
    // 构造错误对象用于错误处理服务
    const apiError = {
      status: error.response?.status || 0,
      message: error.response?.data?.message || error.message,
      data: error.response?.data,
      config: error.config
    }
    
    // 使用错误处理服务处理错误
    errorHandler.handleApiError(apiError, {
      onRetry: error.config ? () => {
        // 重试逻辑
        return apiClient.request(error.config)
      } : null
    })
    
    // 处理特定错误状态
    if (error.response?.status === 401) {
      // 清除认证信息并重定向到登录页
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(apiError)
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
          break
        case 403:
          // 禁止访问
          console.error('访问被拒绝')
          break
        case 404:
          // 资源不存在
          console.error('请求的资源不存在')
          break
        case 500:
          // 服务器错误
          console.error('服务器内部错误')
          break
        default:
          console.error(`请求失败: ${status}`, data)
      }
      
      return Promise.reject({
        status,
        message: data?.message || data?.error || '请求失败',
        data: data
      })
    } else if (error.request) {
      // 网络错误
      return Promise.reject({
        status: 0,
        message: '网络连接失败，请检查网络设置',
        data: null
      })
    } else {
      // 其他错误
      return Promise.reject({
        status: -1,
        message: error.message || '未知错误',
        data: null
      })
    }
  }
)

/**
 * 系统API
 */
export const systemAPI = {
  /**
   * 获取系统健康状态
   */
  getHealth: () => apiClient.get('/health'),
  
  /**
   * 获取系统信息
   */
  getSystemInfo: () => apiClient.get('/system/info'),
  
  /**
   * 获取系统统计
   */
  getSystemStats: () => apiClient.get('/system/stats'),
  
  /**
   * 获取API文档
   */
  getApiDocs: () => apiClient.get('/docs'),
  
  /**
   * 获取版本信息
   */
  getVersion: () => apiClient.get('/version'),
}

/**
 * 测试用例API
 */
export const testCasesAPI = {
  /**
   * 获取测试用例列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => apiClient.get('/test-cases', { params }),
  
  /**
   * 获取单个测试用例
   * @param {string} id - 测试用例ID
   */
  get: (id) => apiClient.get(`/test-cases/${id}`),
  
  /**
   * 创建测试用例
   * @param {Object} data - 测试用例数据
   */
  create: (data) => apiClient.post('/test-cases', data),
  
  /**
   * 更新测试用例
   * @param {string} id - 测试用例ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => apiClient.put(`/test-cases/${id}`, data),
  
  /**
   * 删除测试用例
   * @param {string} id - 测试用例ID
   */
  delete: (id) => apiClient.delete(`/test-cases/${id}`),
  
  /**
   * 运行测试用例
   * @param {string} id - 测试用例ID
   * @param {Object} params - 运行参数
   */
  run: (id, params = {}) => apiClient.post(`/test-cases/${id}/run`, params),
  
  /**
   * 批量导入测试用例
   * @param {FormData} formData - 文件数据
   */
  import: (formData) => apiClient.post('/test-cases/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  /**
   * 导出测试用例
   * @param {Array} ids - 测试用例ID列表
   */
  export: (ids) => apiClient.post('/test-cases/export', { ids }, {
    responseType: 'blob'
  }),
}

/**
 * 测试运行API
 */
export const testRunsAPI = {
  /**
   * 获取测试运行列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => apiClient.get('/test-runs', { params }),
  
  /**
   * 获取测试运行详情
   * @param {string} id - 测试运行ID
   */
  get: (id) => apiClient.get(`/test-runs/${id}`),
  
  /**
   * 取消测试运行
   * @param {string} id - 测试运行ID
   */
  cancel: (id) => apiClient.post(`/test-runs/${id}/cancel`),
  
  /**
   * 重新运行测试
   * @param {string} testCaseId - 测试用例ID
   * @param {string} runtimeManagerId - 运行时管理器ID
   */
  rerun: (testCaseId, runtimeManagerId) => apiClient.post('/test-runs/rerun', {
    test_case_id: testCaseId,
    runtime_manager_id: runtimeManagerId
  }),
  
  /**
   * 创建测试运行
   * @param {Object} data - 测试运行数据
   */
  create: (data) => apiClient.post('/test-runs', data),
  
  /**
   * 更新测试运行
   * @param {string} id - 测试运行ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => apiClient.put(`/test-runs/${id}`, data),
  
  /**
   * 开始测试运行
   * @param {string} id - 测试运行ID
   */
  start: (id) => apiClient.post(`/test-runs/${id}/start`),
  
  /**
   * 停止测试运行
   * @param {string} id - 测试运行ID
   */
  stop: (id) => apiClient.post(`/test-runs/${id}/stop`),
  
  /**
   * 获取测试日志
   * @param {string} id - 测试运行ID
   * @param {Object} params - 查询参数
   */
  getLogs: (id, params = {}) => apiClient.get(`/test-runs/${id}/logs`, { params }),
  
  /**
   * 获取测试统计
   * @param {Object} params - 查询参数
   */
  getStats: (params = {}) => apiClient.get('/test-runs/stats', { params }),
  
  /**
   * 重新运行测试
   * @param {string} id - 测试运行ID
   */
  rerun: (id) => apiClient.post(`/test-runs/${id}/rerun`),
}

/**
 * 测试脚本API
 */
export const testScriptsAPI = {
  /**
   * 获取测试脚本列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => apiClient.get('/test-scripts', { params }),
  
  /**
   * 获取单个测试脚本
   * @param {string} id - 测试脚本ID
   */
  get: (id) => apiClient.get(`/test-scripts/${id}`),
  
  /**
   * 创建测试脚本
   * @param {Object} data - 测试脚本数据
   */
  create: (data) => apiClient.post('/test-scripts', data),
  
  /**
   * 更新测试脚本
   * @param {string} id - 测试脚本ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => apiClient.put(`/test-scripts/${id}`, data),
  
  /**
   * 删除测试脚本
   * @param {string} id - 测试脚本ID
   */
  delete: (id) => apiClient.delete(`/test-scripts/${id}`),
  
  /**
   * 执行测试脚本
   * @param {string} id - 测试脚本ID
   * @param {Object} params - 执行参数
   */
  execute: (id, params = {}) => apiClient.post(`/test-scripts/${id}/execute`, params),
  
  /**
   * 批量执行测试脚本
   * @param {Object} data - 批量执行数据
   */
  batchExecute: (data) => apiClient.post('/test-scripts/batch-execute', data),
  
  /**
   * 获取支持的编程语言列表
   */
  getSupportedLanguages: () => apiClient.get('/test-scripts/languages'),
  
  /**
   * 验证测试脚本
   * @param {Object} data - 脚本数据
   */
  validate: (data) => apiClient.post('/test-scripts/validate', data),
}

/**
 * 运行时管理器API
 */
export const runtimeManagersAPI = {
  /**
   * 获取运行时管理器列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => apiClient.get('/runtime-managers', { params }),
  
  /**
   * 获取单个运行时管理器
   * @param {string} id - 运行时管理器ID
   */
  get: (id) => apiClient.get(`/runtime-managers/${id}`),
  
  /**
   * 创建运行时管理器
   * @param {Object} data - 运行时管理器数据
   */
  create: (data) => apiClient.post('/runtime-managers', data),
  
  /**
   * 更新运行时管理器
   * @param {string} id - 运行时管理器ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => apiClient.put(`/runtime-managers/${id}`, data),
  
  /**
   * 删除运行时管理器
   * @param {string} id - 运行时管理器ID
   */
  delete: (id) => apiClient.delete(`/runtime-managers/${id}`),
  
  /**
   * 测试连接
   * @param {string} id - 运行时管理器ID
   */
  testConnection: (id) => apiClient.post(`/runtime-managers/${id}/test`),
  
  /**
   * 心跳检测
   * @param {string} id - 运行时管理器ID
   */
  heartbeat: (id) => apiClient.post(`/runtime-managers/${id}/heartbeat`),
  
  /**
   * 获取运行时信息
   * @param {string} id - 运行时管理器ID
   */
  getInfo: (id) => apiClient.get(`/runtime-managers/${id}/info`),
  
  /**
   * 获取运行时资源使用情况
   * @param {string} id - 运行时管理器ID
   */
  getResources: (id) => apiClient.get(`/runtime-managers/${id}/resources`),
  
  /**
   * 获取平台信息
   * 检测当前平台支持的运行时类型和能力
   */
  getPlatformInfo: () => apiClient.get('/runtime-managers/platform-info'),
  
  /**
   * 获取设置指引
   * @param {string} runtimeType - 运行时类型 (local|docker|kubernetes)
   */
  getSetupGuide: (runtimeType) => apiClient.get(`/runtime-managers/setup-guide/${runtimeType}`),
  
  /**
   * 执行健康检查
   * @param {string} id - 运行时管理器ID
   */
  healthCheck: (id) => apiClient.post(`/runtime-managers/${id}/health-check`),
}

/**
 * 用户管理API
 */
export const usersAPI = {
  // 认证相关
  /**
   * 用户登录
   * @param {Object} credentials - 登录凭据 {username, password}
   */
  login: (credentials) => apiClient.post('/auth/login', credentials),
  
  /**
   * 用户登出
   */
  logout: () => apiClient.post('/auth/logout'),
  
  /**
   * 刷新令牌
   */
  refreshToken: () => apiClient.post('/auth/refresh'),
  
  /**
   * 获取当前用户信息
   */
  getCurrentUser: () => apiClient.get('/auth/me'),
  
  // 用户管理
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => apiClient.get('/users', { params }),
  
  /**
   * 创建用户
   * @param {Object} data - 用户数据 {username, email, password, full_name}
   */
  create: (data) => apiClient.post('/users', data),
  
  /**
   * 获取用户详情
   * @param {string} id - 用户ID
   */
  get: (id) => apiClient.get(`/users/${id}`),
  
  /**
   * 更新用户
   * @param {string} id - 用户ID
   * @param {Object} data - 用户数据
   */
  update: (id, data) => apiClient.put(`/users/${id}`, data),
  
  /**
   * 删除用户
   * @param {string} id - 用户ID
   */
  delete: (id) => apiClient.delete(`/users/${id}`),
  
  // 密码管理
  /**
   * 修改密码
   * @param {Object} data - 密码数据 {old_password, new_password}
   */
  changePassword: (data) => apiClient.post('/users/change-password', data),
  
  /**
   * 重置用户密码
   * @param {string} id - 用户ID
   */
  resetPassword: (id) => apiClient.post(`/users/${id}/reset-password`),
}

/**
 * 文件管理API
 */
export const filesAPI = {
  /**
   * 上传文件
   * @param {FormData} formData - 文件数据
   * @param {Function} onProgress - 进度回调
   */
  upload: (formData, onProgress) => apiClient.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
  }),
  
  /**
   * 下载文件
   * @param {string} id - 文件ID
   */
  download: (id) => apiClient.get(`/files/${id}/download`, {
    responseType: 'blob'
  }),
  
  /**
   * 删除文件
   * @param {string} id - 文件ID
   */
  delete: (id) => apiClient.delete(`/files/${id}`),
  
  /**
   * 获取文件列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => apiClient.get('/files', { params }),
}

/**
 * 设置API
 */
export const settingsAPI = {
  // 设置管理
  /**
   * 获取设置列表
   * @param {Object} params - 查询参数
   */
  list: (params) => apiClient.get('/settings', { params }),
  
  /**
   * 根据分类获取设置
   * @param {string} category - 设置分类
   */
  getByCategory: (category) => apiClient.get(`/settings/category/${category}`),
  
  /**
   * 获取单个设置
   * @param {string} key - 设置键
   */
  get: (key) => apiClient.get(`/settings/${key}`),
  
  /**
   * 更新设置
   * @param {string} key - 设置键
   * @param {Object} data - 设置数据 {value, description}
   */
  update: (key, data) => apiClient.put(`/settings/${key}`, data),
  
  /**
   * 批量更新设置
   * @param {Object} settings - 设置对象 {key: value}
   */
  batchUpdate: (settings) => apiClient.put('/settings/batch', { settings }),
  
  /**
   * 重置设置为默认值
   * @param {string} key - 设置键
   */
  reset: (key) => apiClient.post(`/settings/${key}/reset`),
  
  // 系统配置
  /**
   * 获取系统配置概览
   */
  getSystemConfig: () => apiClient.get('/settings/config'),
  
  /**
   * 更新系统配置
   * @param {Object} config - 系统配置对象
   */
  updateSystemConfig: (config) => apiClient.put('/settings/config', config),
  
  /**
   * 重新生成API令牌
   */
  regenerateApiToken: () => apiClient.post('/settings/api-token/regenerate'),
  
  // 用户偏好
  /**
   * 获取用户偏好设置
   */
  getUserPreferences: () => apiClient.get('/preferences'),
  
  /**
   * 更新用户偏好设置
   * @param {Object} preference - 偏好设置 {key, value}
   */
  updateUserPreference: (preference) => apiClient.put('/preferences', preference),
}

export default apiClient
export { apiClient }