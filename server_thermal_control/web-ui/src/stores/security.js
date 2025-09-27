/**
 * 安全管理 Store
 * 处理用户认证、权限控制和安全确认
 */
import { defineStore } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'

export const useSecurityStore = defineStore('security', {
  state: () => ({
    // 用户信息
    user: {
      id: null,
      username: '',
      role: 'guest', // admin, operator, viewer, guest
      permissions: [],
      isAuthenticated: false,
      lastLogin: null,
      sessionTimeout: 30 * 60 * 1000, // 30分钟
      sessionExpiry: null
    },
    
    // 安全设置
    securitySettings: {
      requireConfirmation: true,
      dangerousOperationConfirm: true,
      sessionTimeout: 30,
      maxLoginAttempts: 5,
      lockoutDuration: 15,
      twoFactorEnabled: false,
      ipWhitelist: [],
      passwordPolicy: {
        minLength: 8,
        requireUppercase: true,
        requireLowercase: true,
        requireNumbers: true,
        requireSpecialChars: true
      }
    },
    
    // 登录尝试记录
    loginAttempts: {
      count: 0,
      lastAttempt: null,
      isLocked: false,
      lockExpiry: null
    },
    
    // 操作日志
    operationLogs: [],
    
    // 权限定义
    permissions: {
      // 系统监控权限
      'system.view': '查看系统状态',
      'system.metrics': '查看系统指标',
      
      // IPMI控制权限
      'ipmi.view': '查看IPMI状态',
      'ipmi.power': '电源控制',
      'ipmi.remote': '远程控制',
      'ipmi.config': 'IPMI配置',
      
      // 系统管理权限
      'admin.users': '用户管理',
      'admin.settings': '系统设置',
      'admin.logs': '日志管理',
      'admin.backup': '备份恢复',
      
      // 危险操作权限
      'dangerous.power_off': '强制关机',
      'dangerous.reset': '系统重置',
      'dangerous.clear_logs': '清空日志',
      'dangerous.factory_reset': '恢复出厂设置'
    },
    
    // 角色权限映射
    rolePermissions: {
      admin: [
        'system.view', 'system.metrics',
        'ipmi.view', 'ipmi.power', 'ipmi.remote', 'ipmi.config',
        'admin.users', 'admin.settings', 'admin.logs', 'admin.backup',
        'dangerous.power_off', 'dangerous.reset', 'dangerous.clear_logs', 'dangerous.factory_reset'
      ],
      operator: [
        'system.view', 'system.metrics',
        'ipmi.view', 'ipmi.power', 'ipmi.remote',
        'dangerous.power_off', 'dangerous.reset'
      ],
      viewer: [
        'system.view', 'system.metrics',
        'ipmi.view'
      ],
      guest: []
    }
  }),

  getters: {
    /**
     * 检查用户是否已认证
     */
    isAuthenticated: (state) => state.user.isAuthenticated,
    
    /**
     * 获取用户角色
     */
    userRole: (state) => state.user.role,
    
    /**
     * 获取用户权限列表
     */
    userPermissions: (state) => {
      if (!state.user.isAuthenticated) return []
      return state.rolePermissions[state.user.role] || []
    },
    
    /**
     * 检查会话是否过期
     */
    isSessionExpired: (state) => {
      if (!state.user.sessionExpiry) return false
      return Date.now() > state.user.sessionExpiry
    },
    
    /**
     * 检查是否被锁定
     */
    isAccountLocked: (state) => {
      if (!state.loginAttempts.isLocked) return false
      if (!state.loginAttempts.lockExpiry) return false
      return Date.now() < state.loginAttempts.lockExpiry
    },
    
    /**
     * 获取剩余锁定时间（分钟）
     */
    lockTimeRemaining: (state) => {
      if (!state.loginAttempts.lockExpiry) return 0
      const remaining = state.loginAttempts.lockExpiry - Date.now()
      return Math.max(0, Math.ceil(remaining / 60000))
    }
  },

  actions: {
    /**
     * 初始化安全模块
     */
    async initializeSecurity() {
      try {
        // 从本地存储恢复用户会话
        this.restoreSession()
        
        // 检查会话是否过期
        if (this.isSessionExpired) {
          await this.logout()
        }
        
        // 初始化模拟数据
        this.initializeMockData()
        
        console.log('安全模块初始化完成')
      } catch (error) {
        console.error('安全模块初始化失败:', error)
      }
    },
    
    /**
     * 用户登录
     */
    async login(credentials) {
      try {
        // 检查账户是否被锁定
        if (this.isAccountLocked) {
          throw new Error(`账户已被锁定，请在 ${this.lockTimeRemaining} 分钟后重试`)
        }
        
        // 模拟登录验证
        const success = await this.validateCredentials(credentials)
        
        if (success) {
          // 登录成功
          this.user.id = 1
          this.user.username = credentials.username
          this.user.role = this.determineUserRole(credentials.username)
          this.user.isAuthenticated = true
          this.user.lastLogin = new Date()
          this.user.sessionExpiry = Date.now() + this.user.sessionTimeout
          
          // 重置登录尝试
          this.resetLoginAttempts()
          
          // 保存会话
          this.saveSession()
          
          // 记录操作日志
          this.logOperation('用户登录', 'info', `用户 ${credentials.username} 登录成功`)
          
          ElMessage.success('登录成功')
          return true
        } else {
          // 登录失败
          this.recordFailedLogin()
          throw new Error('用户名或密码错误')
        }
      } catch (error) {
        ElMessage.error(error.message)
        throw error
      }
    },
    
    /**
     * 用户登出
     */
    async logout() {
      try {
        const username = this.user.username
        
        // 清除用户信息
        this.user = {
          id: null,
          username: '',
          role: 'guest',
          permissions: [],
          isAuthenticated: false,
          lastLogin: null,
          sessionTimeout: 30 * 60 * 1000,
          sessionExpiry: null
        }
        
        // 清除本地存储
        localStorage.removeItem('user_session')
        
        // 记录操作日志
        if (username) {
          this.logOperation('用户登出', 'info', `用户 ${username} 登出`)
        }
        
        ElMessage.success('已安全登出')
      } catch (error) {
        console.error('登出失败:', error)
      }
    },
    
    /**
     * 检查权限
     */
    hasPermission(permission) {
      if (!this.isAuthenticated) return false
      return this.userPermissions.includes(permission)
    },
    
    /**
     * 检查多个权限（需要全部满足）
     */
    hasAllPermissions(permissions) {
      return permissions.every(permission => this.hasPermission(permission))
    },
    
    /**
     * 检查多个权限（满足任一即可）
     */
    hasAnyPermission(permissions) {
      return permissions.some(permission => this.hasPermission(permission))
    },
    
    /**
     * 安全确认对话框
     */
    async confirmOperation(operation, options = {}) {
      try {
        const {
          title = '确认操作',
          message = `确定要执行 ${operation} 操作吗？`,
          type = 'warning',
          requirePassword = false,
          isDangerous = false
        } = options
        
        // 检查是否需要确认
        if (!this.securitySettings.requireConfirmation && !isDangerous) {
          return true
        }
        
        // 危险操作需要额外确认
        if (isDangerous && this.securitySettings.dangerousOperationConfirm) {
          const confirmText = `确认执行 ${operation}`
          const { value } = await ElMessageBox.prompt(
            `${message}\n\n请输入 "${confirmText}" 来确认此危险操作：`,
            title,
            {
              confirmButtonText: '确认执行',
              cancelButtonText: '取消',
              inputPattern: new RegExp(`^${confirmText}$`),
              inputErrorMessage: '输入的确认文本不正确',
              type: 'error'
            }
          )
          
          if (value !== confirmText) {
            throw new Error('确认文本不匹配')
          }
        } else {
          // 普通确认
          await ElMessageBox.confirm(message, title, {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type
          })
        }
        
        // 需要密码确认
        if (requirePassword) {
          const { value: password } = await ElMessageBox.prompt(
            '请输入当前用户密码以确认操作：',
            '密码确认',
            {
              confirmButtonText: '确认',
              cancelButtonText: '取消',
              inputType: 'password'
            }
          )
          
          // 验证密码（这里简化处理）
          if (!password || password.length < 6) {
            throw new Error('密码验证失败')
          }
        }
        
        // 记录操作日志
        this.logOperation('安全确认', 'info', `用户确认执行操作: ${operation}`)
        
        return true
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error(error.message || '操作确认失败')
          this.logOperation('安全确认', 'warning', `用户取消或确认失败: ${operation}`)
        }
        return false
      }
    },
    
    /**
     * 更新安全设置
     */
    async updateSecuritySettings(settings) {
      try {
        Object.assign(this.securitySettings, settings)
        
        // 保存到本地存储
        localStorage.setItem('security_settings', JSON.stringify(this.securitySettings))
        
        // 记录操作日志
        this.logOperation('安全设置', 'info', '更新安全设置')
        
        ElMessage.success('安全设置已更新')
      } catch (error) {
        console.error('更新安全设置失败:', error)
        ElMessage.error('更新安全设置失败')
      }
    },
    
    /**
     * 记录操作日志
     */
    logOperation(category, level, message, details = null) {
      const log = {
        id: Date.now(),
        timestamp: new Date(),
        category,
        level,
        message,
        details,
        user: this.user.username || 'anonymous',
        ip: '127.0.0.1' // 实际应用中从请求获取
      }
      
      this.operationLogs.unshift(log)
      
      // 保持日志数量在合理范围内
      if (this.operationLogs.length > 1000) {
        this.operationLogs = this.operationLogs.slice(0, 1000)
      }
    },
    
    /**
     * 清空操作日志
     */
    async clearOperationLogs() {
      try {
        const confirmed = await this.confirmOperation('清空操作日志', {
          message: '确定要清空所有操作日志吗？此操作不可恢复。',
          isDangerous: true
        })
        
        if (confirmed) {
          this.operationLogs = []
          ElMessage.success('操作日志已清空')
        }
      } catch (error) {
        console.error('清空操作日志失败:', error)
      }
    },
    
    /**
     * 验证凭据（模拟）
     */
    async validateCredentials(credentials) {
      // 模拟网络延迟
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // 简单的模拟验证
      const validUsers = {
        'admin': 'admin123',
        'operator': 'operator123',
        'viewer': 'viewer123'
      }
      
      return validUsers[credentials.username] === credentials.password
    },
    
    /**
     * 确定用户角色
     */
    determineUserRole(username) {
      const roleMap = {
        'admin': 'admin',
        'operator': 'operator',
        'viewer': 'viewer'
      }
      return roleMap[username] || 'guest'
    },
    
    /**
     * 记录失败的登录尝试
     */
    recordFailedLogin() {
      this.loginAttempts.count++
      this.loginAttempts.lastAttempt = new Date()
      
      // 检查是否需要锁定账户
      if (this.loginAttempts.count >= this.securitySettings.maxLoginAttempts) {
        this.loginAttempts.isLocked = true
        this.loginAttempts.lockExpiry = Date.now() + (this.securitySettings.lockoutDuration * 60 * 1000)
        
        this.logOperation('安全事件', 'warning', 
          `账户因多次登录失败被锁定 ${this.securitySettings.lockoutDuration} 分钟`)
      }
    },
    
    /**
     * 重置登录尝试
     */
    resetLoginAttempts() {
      this.loginAttempts = {
        count: 0,
        lastAttempt: null,
        isLocked: false,
        lockExpiry: null
      }
    },
    
    /**
     * 保存会话到本地存储
     */
    saveSession() {
      const sessionData = {
        user: this.user,
        timestamp: Date.now()
      }
      localStorage.setItem('user_session', JSON.stringify(sessionData))
    },
    
    /**
     * 从本地存储恢复会话
     */
    restoreSession() {
      try {
        const sessionData = localStorage.getItem('user_session')
        if (sessionData) {
          const parsed = JSON.parse(sessionData)
          if (parsed.user && parsed.timestamp) {
            // 检查会话是否在有效期内
            const sessionAge = Date.now() - parsed.timestamp
            if (sessionAge < this.user.sessionTimeout) {
              this.user = { ...this.user, ...parsed.user }
            }
          }
        }
      } catch (error) {
        console.error('恢复会话失败:', error)
        localStorage.removeItem('user_session')
      }
    },
    
    /**
     * 初始化模拟数据
     */
    initializeMockData() {
      // 从本地存储恢复安全设置
      try {
        const savedSettings = localStorage.getItem('security_settings')
        if (savedSettings) {
          const parsed = JSON.parse(savedSettings)
          Object.assign(this.securitySettings, parsed)
        }
      } catch (error) {
        console.error('恢复安全设置失败:', error)
      }
      
      // 添加一些示例操作日志
      if (this.operationLogs.length === 0) {
        this.operationLogs = [
          {
            id: 1,
            timestamp: new Date(Date.now() - 300000),
            category: '系统启动',
            level: 'info',
            message: '系统启动完成',
            user: 'system',
            ip: '127.0.0.1'
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 600000),
            category: '用户登录',
            level: 'info',
            message: '用户登录成功',
            user: 'admin',
            ip: '192.168.1.100'
          }
        ]
      }
    }
  }
})