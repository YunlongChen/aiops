/**
 * API服务工具类
 * 封装HTTP请求和响应处理逻辑
 */
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token（如果有）
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加请求时间戳
    config.metadata = { startTime: new Date() }
    
    return config
  },
  (error) => {
    console.error('请求拦截器错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    // 计算请求耗时
    const endTime = new Date()
    const duration = endTime - response.config.metadata.startTime
    console.log(`API请求耗时: ${duration}ms - ${response.config.url}`)
    
    // 统一处理响应数据
    const { data } = response
    
    // 如果是健康检查接口，直接返回
    if (response.config.url?.includes('/health')) {
      return data
    }
    
    // 处理业务逻辑错误
    if (data.success === false) {
      const errorMessage = data.error || data.message || '请求失败'
      ElMessage.error(errorMessage)
      return Promise.reject(new Error(errorMessage))
    }
    
    return data
  },
  (error) => {
    console.error('API请求失败:', error)
    
    let errorMessage = '网络请求失败'
    
    if (error.response) {
      // 服务器响应了错误状态码
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          errorMessage = data?.message || '请求参数错误'
          break
        case 401:
          errorMessage = '未授权访问，请重新登录'
          // 清除本地认证信息
          localStorage.removeItem('auth_token')
          // 可以在这里跳转到登录页面
          break
        case 403:
          errorMessage = '权限不足'
          break
        case 404:
          errorMessage = '请求的资源不存在'
          break
        case 500:
          errorMessage = '服务器内部错误'
          break
        case 502:
          errorMessage = '网关错误'
          break
        case 503:
          errorMessage = '服务暂时不可用'
          break
        default:
          errorMessage = data?.message || `请求失败 (${status})`
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      errorMessage = '网络连接超时，请检查网络连接'
    } else {
      // 其他错误
      errorMessage = error.message || '未知错误'
    }
    
    // 显示错误消息（排除某些不需要显示的错误）
    if (!error.config?.url?.includes('/health')) {
      ElMessage.error(errorMessage)
    }
    
    return Promise.reject(error)
  }
)

/**
 * API服务类
 */
export class ApiService {
  /**
   * GET请求
   * @param {string} url 请求URL
   * @param {object} params 查询参数
   * @param {object} config 请求配置
   */
  async get(url, params = {}, config = {}) {
    try {
      const response = await api.get(url, { params, ...config })
      return response
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * POST请求
   * @param {string} url 请求URL
   * @param {object} data 请求数据
   * @param {object} config 请求配置
   */
  async post(url, data = {}, config = {}) {
    try {
      const response = await api.post(url, data, config)
      return response
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * PUT请求
   * @param {string} url 请求URL
   * @param {object} data 请求数据
   * @param {object} config 请求配置
   */
  async put(url, data = {}, config = {}) {
    try {
      const response = await api.put(url, data, config)
      return response
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * DELETE请求
   * @param {string} url 请求URL
   * @param {object} config 请求配置
   */
  async delete(url, config = {}) {
    try {
      const response = await api.delete(url, config)
      return response
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 上传文件
   * @param {string} url 上传URL
   * @param {FormData} formData 文件数据
   * @param {function} onProgress 进度回调
   */
  async upload(url, formData, onProgress) {
    try {
      const response = await api.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress) {
            const percentCompleted = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            )
            onProgress(percentCompleted)
          }
        }
      })
      return response
    } catch (error) {
      throw this.handleError(error)
    }
  }

  /**
   * 带确认的危险操作请求
   * @param {string} url 请求URL
   * @param {object} options 选项
   */
  async dangerousAction(url, options = {}) {
    const {
      method = 'POST',
      data = {},
      confirmTitle = '确认操作',
      confirmMessage = '此操作不可撤销，确定要继续吗？',
      confirmButtonText = '确定',
      cancelButtonText = '取消'
    } = options

    try {
      await ElMessageBox.confirm(
        confirmMessage,
        confirmTitle,
        {
          confirmButtonText,
          cancelButtonText,
          type: 'warning',
          dangerouslyUseHTMLString: false
        }
      )

      let response
      switch (method.toUpperCase()) {
        case 'GET':
          response = await this.get(url)
          break
        case 'POST':
          response = await this.post(url, data)
          break
        case 'PUT':
          response = await this.put(url, data)
          break
        case 'DELETE':
          response = await this.delete(url)
          break
        default:
          throw new Error(`不支持的请求方法: ${method}`)
      }

      ElMessage.success('操作成功')
      return response
    } catch (error) {
      if (error === 'cancel') {
        ElMessage.info('操作已取消')
        return null
      }
      throw this.handleError(error)
    }
  }

  /**
   * 错误处理
   * @param {Error} error 错误对象
   */
  handleError(error) {
    console.error('API错误:', error)
    return error
  }
}

// 导出单例实例
export const apiService = new ApiService()

// 导出axios实例（用于特殊情况）
export { api }

// 导出常用的API端点
export const API_ENDPOINTS = {
  // 系统相关
  HEALTH: '/api/v1/health',
  SYSTEM_INFO: '/api/v1/system/info',
  
  // 温度相关
  TEMPERATURE: '/api/v1/temperature',
  TEMPERATURE_HISTORY: '/api/v1/temperature/history',
  
  // 风扇相关
  FANS: '/api/v1/fans',
  FAN_CONTROL: '/api/v1/fans/control',
  
  // IPMI相关
  IPMI_STATUS: '/api/v1/ipmi/status',
  IPMI_POWER: '/api/v1/ipmi/power',
  IPMI_CONSOLE: '/api/v1/ipmi/console',
  
  // 日志相关
  LOGS: '/api/v1/logs',
  
  // 配置相关
  CONFIG: '/api/v1/config',
  
  // 监控相关
  METRICS: '/api/v1/metrics',
  ALERTS: '/api/v1/alerts'
}