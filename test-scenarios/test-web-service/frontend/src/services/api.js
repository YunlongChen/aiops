/**
 * AIOps测试管理平台 - API服务层
 * 统一管理所有API调用，提供类型安全和错误处理
 */

import axios from 'axios'

/**
 * API客户端配置
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3030/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

/**
 * 请求拦截器
 * 添加认证token和请求日志
 */
api.interceptors.request.use(
  (config) => {
    // 添加认证token（如果存在）
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 请求日志
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data)
    
    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

/**
 * 响应拦截器
 * 统一处理响应和错误
 */
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, response.data)
    return response.data
  },
  (error) => {
    console.error('[API Response Error]', error)
    
    // 统一错误处理
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
  getHealth: () => api.get('/health'),
  
  /**
   * 获取系统信息
   */
  getSystemInfo: () => api.get('/system/info'),
  
  /**
   * 获取系统统计
   */
  getSystemStats: () => api.get('/system/stats'),
  
  /**
   * 获取API文档
   */
  getApiDocs: () => api.get('/docs'),
  
  /**
   * 获取版本信息
   */
  getVersion: () => api.get('/version'),
}

/**
 * 测试用例API
 */
export const testCasesAPI = {
  /**
   * 获取测试用例列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => api.get('/test-cases', { params }),
  
  /**
   * 获取单个测试用例
   * @param {string} id - 测试用例ID
   */
  get: (id) => api.get(`/test-cases/${id}`),
  
  /**
   * 创建测试用例
   * @param {Object} data - 测试用例数据
   */
  create: (data) => api.post('/test-cases', data),
  
  /**
   * 更新测试用例
   * @param {string} id - 测试用例ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => api.put(`/test-cases/${id}`, data),
  
  /**
   * 删除测试用例
   * @param {string} id - 测试用例ID
   */
  delete: (id) => api.delete(`/test-cases/${id}`),
  
  /**
   * 运行测试用例
   * @param {string} id - 测试用例ID
   * @param {Object} params - 运行参数
   */
  run: (id, params = {}) => api.post(`/test-cases/${id}/run`, params),
  
  /**
   * 批量导入测试用例
   * @param {FormData} formData - 文件数据
   */
  import: (formData) => api.post('/test-cases/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  
  /**
   * 导出测试用例
   * @param {Array} ids - 测试用例ID列表
   */
  export: (ids) => api.post('/test-cases/export', { ids }, {
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
  list: (params = {}) => api.get('/test-runs', { params }),
  
  /**
   * 获取单个测试运行
   * @param {string} id - 测试运行ID
   */
  get: (id) => api.get(`/test-runs/${id}`),
  
  /**
   * 创建测试运行
   * @param {Object} data - 测试运行数据
   */
  create: (data) => api.post('/test-runs', data),
  
  /**
   * 更新测试运行
   * @param {string} id - 测试运行ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => api.put(`/test-runs/${id}`, data),
  
  /**
   * 开始测试运行
   * @param {string} id - 测试运行ID
   */
  start: (id) => api.post(`/test-runs/${id}/start`),
  
  /**
   * 停止测试运行
   * @param {string} id - 测试运行ID
   */
  stop: (id) => api.post(`/test-runs/${id}/stop`),
  
  /**
   * 获取测试日志
   * @param {string} id - 测试运行ID
   * @param {Object} params - 查询参数
   */
  getLogs: (id, params = {}) => api.get(`/test-runs/${id}/logs`, { params }),
  
  /**
   * 获取测试统计
   * @param {Object} params - 查询参数
   */
  getStats: (params = {}) => api.get('/test-runs/stats', { params }),
  
  /**
   * 重新运行测试
   * @param {string} id - 测试运行ID
   */
  rerun: (id) => api.post(`/test-runs/${id}/rerun`),
}

/**
 * 运行时管理器API
 */
export const runtimeManagersAPI = {
  /**
   * 获取运行时管理器列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => api.get('/runtime-managers', { params }),
  
  /**
   * 获取单个运行时管理器
   * @param {string} id - 运行时管理器ID
   */
  get: (id) => api.get(`/runtime-managers/${id}`),
  
  /**
   * 创建运行时管理器
   * @param {Object} data - 运行时管理器数据
   */
  create: (data) => api.post('/runtime-managers', data),
  
  /**
   * 更新运行时管理器
   * @param {string} id - 运行时管理器ID
   * @param {Object} data - 更新数据
   */
  update: (id, data) => api.put(`/runtime-managers/${id}`, data),
  
  /**
   * 删除运行时管理器
   * @param {string} id - 运行时管理器ID
   */
  delete: (id) => api.delete(`/runtime-managers/${id}`),
  
  /**
   * 测试连接
   * @param {string} id - 运行时管理器ID
   */
  testConnection: (id) => api.post(`/runtime-managers/${id}/test`),
  
  /**
   * 心跳检测
   * @param {string} id - 运行时管理器ID
   */
  heartbeat: (id) => api.post(`/runtime-managers/${id}/heartbeat`),
  
  /**
   * 获取运行时信息
   * @param {string} id - 运行时管理器ID
   */
  getInfo: (id) => api.get(`/runtime-managers/${id}/info`),
  
  /**
   * 获取运行时资源使用情况
   * @param {string} id - 运行时管理器ID
   */
  getResources: (id) => api.get(`/runtime-managers/${id}/resources`),
  
  /**
   * 获取平台信息
   * 检测当前平台支持的运行时类型和能力
   */
  getPlatformInfo: () => api.get('/runtime-managers/platform-info'),
  
  /**
   * 获取设置指引
   * @param {string} runtimeType - 运行时类型 (local|docker|kubernetes)
   */
  getSetupGuide: (runtimeType) => api.get(`/runtime-managers/setup-guide/${runtimeType}`),
  
  /**
   * 执行健康检查
   * @param {string} id - 运行时管理器ID
   */
  healthCheck: (id) => api.post(`/runtime-managers/${id}/health-check`),
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
  login: (credentials) => api.post('/auth/login', credentials),
  
  /**
   * 用户登出
   */
  logout: () => api.post('/auth/logout'),
  
  /**
   * 刷新令牌
   */
  refreshToken: () => api.post('/auth/refresh'),
  
  /**
   * 获取当前用户信息
   */
  getCurrentUser: () => api.get('/auth/me'),
  
  // 用户管理
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => api.get('/users', { params }),
  
  /**
   * 创建用户
   * @param {Object} data - 用户数据 {username, email, password, full_name}
   */
  create: (data) => api.post('/users', data),
  
  /**
   * 获取用户详情
   * @param {string} id - 用户ID
   */
  get: (id) => api.get(`/users/${id}`),
  
  /**
   * 更新用户
   * @param {string} id - 用户ID
   * @param {Object} data - 用户数据
   */
  update: (id, data) => api.put(`/users/${id}`, data),
  
  /**
   * 删除用户
   * @param {string} id - 用户ID
   */
  delete: (id) => api.delete(`/users/${id}`),
  
  // 密码管理
  /**
   * 修改密码
   * @param {Object} data - 密码数据 {old_password, new_password}
   */
  changePassword: (data) => api.post('/users/change-password', data),
  
  /**
   * 重置用户密码
   * @param {string} id - 用户ID
   */
  resetPassword: (id) => api.post(`/users/${id}/reset-password`),
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
  upload: (formData, onProgress) => api.post('/files/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: onProgress
  }),
  
  /**
   * 下载文件
   * @param {string} id - 文件ID
   */
  download: (id) => api.get(`/files/${id}/download`, {
    responseType: 'blob'
  }),
  
  /**
   * 删除文件
   * @param {string} id - 文件ID
   */
  delete: (id) => api.delete(`/files/${id}`),
  
  /**
   * 获取文件列表
   * @param {Object} params - 查询参数
   */
  list: (params = {}) => api.get('/files', { params }),
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
  list: (params) => api.get('/settings', { params }),
  
  /**
   * 根据分类获取设置
   * @param {string} category - 设置分类
   */
  getByCategory: (category) => api.get(`/settings/category/${category}`),
  
  /**
   * 获取单个设置
   * @param {string} key - 设置键
   */
  get: (key) => api.get(`/settings/${key}`),
  
  /**
   * 更新设置
   * @param {string} key - 设置键
   * @param {Object} data - 设置数据 {value, description}
   */
  update: (key, data) => api.put(`/settings/${key}`, data),
  
  /**
   * 批量更新设置
   * @param {Object} settings - 设置对象 {key: value}
   */
  batchUpdate: (settings) => api.put('/settings/batch', { settings }),
  
  /**
   * 重置设置为默认值
   * @param {string} key - 设置键
   */
  reset: (key) => api.post(`/settings/${key}/reset`),
  
  // 系统配置
  /**
   * 获取系统配置概览
   */
  getSystemConfig: () => api.get('/settings/config'),
  
  // 用户偏好
  /**
   * 获取用户偏好设置
   */
  getUserPreferences: () => api.get('/preferences'),
  
  /**
   * 更新用户偏好设置
   * @param {Object} preference - 偏好设置 {key, value}
   */
  updateUserPreference: (preference) => api.put('/preferences', preference),
}

export default api
export { api }