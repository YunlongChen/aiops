/**
 * AIOps测试管理平台 - 全局错误处理服务
 * 统一管理应用中的错误处理和用户提示
 */

import { reactive } from 'vue'

/**
 * 错误类型枚举
 */
export const ErrorTypes = {
  NETWORK: 'network',
  API: 'api',
  VALIDATION: 'validation',
  PERMISSION: 'permission',
  UNKNOWN: 'unknown'
}

/**
 * 错误严重级别
 */
export const ErrorSeverity = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
}

/**
 * 全局错误状态
 */
const errorState = reactive({
  errors: [],
  maxErrors: 5 // 最多显示5个错误
})

/**
 * 错误处理服务类
 */
class ErrorHandlerService {
  /**
   * 添加错误
   * @param {Object} error - 错误对象
   * @param {Object} options - 选项
   */
  addError(error, options = {}) {
    const errorInfo = this.parseError(error, options)
    
    // 检查是否已存在相同错误
    const existingError = errorState.errors.find(e => 
      e.message === errorInfo.message && e.type === errorInfo.type
    )
    
    if (existingError) {
      existingError.count = (existingError.count || 1) + 1
      existingError.lastOccurred = new Date()
      return existingError.id
    }
    
    // 添加新错误
    const errorId = this.generateErrorId()
    const newError = {
      id: errorId,
      ...errorInfo,
      count: 1,
      createdAt: new Date(),
      lastOccurred: new Date()
    }
    
    errorState.errors.unshift(newError)
    
    // 限制错误数量
    if (errorState.errors.length > errorState.maxErrors) {
      errorState.errors = errorState.errors.slice(0, errorState.maxErrors)
    }
    
    // 记录到控制台
    this.logError(newError)
    
    return errorId
  }
  
  /**
   * 移除错误
   * @param {string} errorId - 错误ID
   */
  removeError(errorId) {
    const index = errorState.errors.findIndex(e => e.id === errorId)
    if (index !== -1) {
      errorState.errors.splice(index, 1)
    }
  }
  
  /**
   * 清除所有错误
   */
  clearErrors() {
    errorState.errors.length = 0
  }
  
  /**
   * 获取错误列表
   */
  getErrors() {
    return errorState.errors
  }
  
  /**
   * 解析错误对象
   * @param {Error|Object} error - 错误对象
   * @param {Object} options - 选项
   */
  parseError(error, options = {}) {
    let type = ErrorTypes.UNKNOWN
    let severity = ErrorSeverity.MEDIUM
    let title = '操作失败'
    let message = '发生了未知错误'
    let details = null
    let retryable = false
    let onRetry = null
    
    // 解析API错误
    if (error && typeof error === 'object') {
      if (error.status !== undefined) {
        type = ErrorTypes.API
        
        switch (error.status) {
          case 0:
            type = ErrorTypes.NETWORK
            title = '网络连接失败'
            message = error.message || '无法连接到服务器，请检查网络连接'
            severity = ErrorSeverity.HIGH
            retryable = true
            break
            
          case 400:
            type = ErrorTypes.VALIDATION
            title = '请求参数错误'
            message = error.message || '请求参数不正确，请检查输入'
            severity = ErrorSeverity.LOW
            break
            
          case 401:
            type = ErrorTypes.PERMISSION
            title = '身份验证失败'
            message = error.message || '请重新登录'
            severity = ErrorSeverity.HIGH
            break
            
          case 403:
            type = ErrorTypes.PERMISSION
            title = '权限不足'
            message = error.message || '您没有执行此操作的权限'
            severity = ErrorSeverity.MEDIUM
            break
            
          case 404:
            title = '资源不存在'
            message = error.message || '请求的资源不存在'
            severity = ErrorSeverity.LOW
            break
            
          case 429:
            title = '请求过于频繁'
            message = error.message || '请求过于频繁，请稍后再试'
            severity = ErrorSeverity.MEDIUM
            retryable = true
            break
            
          case 500:
          case 502:
          case 503:
          case 504:
            title = '服务器错误'
            message = error.message || '服务器暂时无法处理请求，请稍后再试'
            severity = ErrorSeverity.HIGH
            retryable = true
            break
            
          default:
            title = 'API错误'
            message = error.message || `请求失败 (${error.status})`
            severity = ErrorSeverity.MEDIUM
        }
        
        // 设置详细信息
        if (error.data) {
          details = JSON.stringify(error.data, null, 2)
        }
      } else if (error.message) {
        // JavaScript Error对象
        message = error.message
        details = error.stack
      }
    } else if (typeof error === 'string') {
      message = error
    }
    
    // 应用选项覆盖
    return {
      type: options.type || type,
      severity: options.severity || severity,
      title: options.title || title,
      message: options.message || message,
      details: options.details || details,
      retryable: options.retryable !== undefined ? options.retryable : retryable,
      onRetry: options.onRetry || onRetry,
      autoClose: options.autoClose !== undefined ? options.autoClose : this.getAutoCloseTime(severity)
    }
  }
  
  /**
   * 生成错误ID
   */
  generateErrorId() {
    return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  /**
   * 记录错误到控制台
   * @param {Object} errorInfo - 错误信息
   */
  logError(errorInfo) {
    const logLevel = this.getLogLevel(errorInfo.severity)
    const logMessage = `[${errorInfo.type.toUpperCase()}] ${errorInfo.title}: ${errorInfo.message}`
    
    console[logLevel](logMessage, {
      error: errorInfo,
      timestamp: errorInfo.createdAt
    })
  }
  
  /**
   * 获取日志级别
   * @param {string} severity - 严重级别
   */
  getLogLevel(severity) {
    switch (severity) {
      case ErrorSeverity.LOW:
        return 'info'
      case ErrorSeverity.MEDIUM:
        return 'warn'
      case ErrorSeverity.HIGH:
      case ErrorSeverity.CRITICAL:
        return 'error'
      default:
        return 'log'
    }
  }
  
  /**
   * 获取自动关闭时间
   * @param {string} severity - 严重级别
   */
  getAutoCloseTime(severity) {
    switch (severity) {
      case ErrorSeverity.LOW:
        return 3000
      case ErrorSeverity.MEDIUM:
        return 5000
      case ErrorSeverity.HIGH:
        return 8000
      case ErrorSeverity.CRITICAL:
        return 0 // 不自动关闭
      default:
        return 5000
    }
  }
  
  /**
   * 处理API错误的便捷方法
   * @param {Object} error - API错误
   * @param {Object} options - 选项
   */
  handleApiError(error, options = {}) {
    return this.addError(error, {
      type: ErrorTypes.API,
      ...options
    })
  }
  
  /**
   * 处理网络错误的便捷方法
   * @param {Object} error - 网络错误
   * @param {Object} options - 选项
   */
  handleNetworkError(error, options = {}) {
    return this.addError(error, {
      type: ErrorTypes.NETWORK,
      retryable: true,
      ...options
    })
  }
  
  /**
   * 处理验证错误的便捷方法
   * @param {string} message - 错误消息
   * @param {Object} options - 选项
   */
  handleValidationError(message, options = {}) {
    return this.addError({ message }, {
      type: ErrorTypes.VALIDATION,
      title: '输入验证失败',
      severity: ErrorSeverity.LOW,
      ...options
    })
  }
  
  /**
   * 显示成功消息
   * @param {string} message - 成功消息
   * @param {Object} options - 选项
   */
  showSuccess(message, options = {}) {
    return this.addError({ message }, {
      type: 'success',
      title: '操作成功',
      severity: ErrorSeverity.LOW,
      autoClose: 3000,
      ...options
    })
  }
  
  /**
   * 显示信息消息
   * @param {string} message - 信息消息
   * @param {Object} options - 选项
   */
  showInfo(message, options = {}) {
    return this.addError({ message }, {
      type: 'info',
      title: '提示',
      severity: ErrorSeverity.LOW,
      autoClose: 4000,
      ...options
    })
  }
  
  /**
   * 显示警告消息
   * @param {string} message - 警告消息
   * @param {Object} options - 选项
   */
  showWarning(message, options = {}) {
    return this.addError({ message }, {
      type: 'warning',
      title: '警告',
      severity: ErrorSeverity.MEDIUM,
      autoClose: 6000,
      ...options
    })
  }
}

// 创建全局实例
const errorHandler = new ErrorHandlerService()

// 导出服务实例和状态
export { errorHandler, errorState }
export default errorHandler