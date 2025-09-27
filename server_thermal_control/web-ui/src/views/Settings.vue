<template>
  <div class="settings">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><Setting /></el-icon>
          系统设置
        </h1>
        <p class="page-description">配置系统参数和用户偏好</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          :icon="Check"
          :loading="isSaving"
          @click="saveAllSettings"
        >
          保存所有设置
        </el-button>
        <el-button 
          :icon="RefreshLeft"
          @click="resetAllSettings"
        >
          重置设置
        </el-button>
      </div>
    </div>

    <!-- 设置内容 -->
    <div class="settings-content">
      <div class="settings-grid">
        <!-- 系统配置 -->
        <div class="settings-section">
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Monitor /></el-icon>
                系统配置
              </span>
            </div>
            <div class="card-content">
              <div class="setting-group">
                <div class="setting-item">
                  <div class="setting-label">
                    <span>数据刷新间隔</span>
                    <el-tooltip content="设置系统数据自动刷新的时间间隔">
                      <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                  <el-select v-model="settings.system.refreshInterval" @change="onSettingChange">
                    <el-option label="5秒" :value="5000" />
                    <el-option label="10秒" :value="10000" />
                    <el-option label="30秒" :value="30000" />
                    <el-option label="1分钟" :value="60000" />
                    <el-option label="5分钟" :value="300000" />
                  </el-select>
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>温度单位</span>
                    <el-tooltip content="选择温度显示单位">
                      <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                  <el-radio-group v-model="settings.system.temperatureUnit" @change="onSettingChange">
                    <el-radio label="celsius">摄氏度 (°C)</el-radio>
                    <el-radio label="fahrenheit">华氏度 (°F)</el-radio>
                  </el-radio-group>
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>启用声音提醒</span>
                    <el-tooltip content="系统异常时播放提醒声音">
                      <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                  <el-switch 
                    v-model="settings.system.enableSound" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>启用桌面通知</span>
                    <el-tooltip content="系统异常时显示桌面通知">
                      <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                  <el-switch 
                    v-model="settings.system.enableNotification" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>数据保留天数</span>
                    <el-tooltip content="历史数据保留的天数">
                      <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </div>
                  <el-input-number
                    v-model="settings.system.dataRetentionDays"
                    :min="1"
                    :max="365"
                    @change="onSettingChange"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 监控阈值 -->
        <div class="settings-section">
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Warning /></el-icon>
                监控阈值
              </span>
            </div>
            <div class="card-content">
              <div class="setting-group">
                <div class="setting-item">
                  <div class="setting-label">
                    <span>CPU使用率警告阈值 (%)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.cpuWarning"
                    :min="50"
                    :max="95"
                    show-input
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>CPU使用率危险阈值 (%)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.cpuDanger"
                    :min="70"
                    :max="100"
                    show-input
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>内存使用率警告阈值 (%)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.memoryWarning"
                    :min="50"
                    :max="95"
                    show-input
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>内存使用率危险阈值 (%)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.memoryDanger"
                    :min="70"
                    :max="100"
                    show-input
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>磁盘使用率警告阈值 (%)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.diskWarning"
                    :min="50"
                    :max="95"
                    show-input
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>磁盘使用率危险阈值 (%)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.diskDanger"
                    :min="70"
                    :max="100"
                    show-input
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>温度警告阈值 (°C)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.temperatureWarning"
                    :min="60"
                    :max="90"
                    show-input
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>温度危险阈值 (°C)</span>
                  </div>
                  <el-slider
                    v-model="settings.thresholds.temperatureDanger"
                    :min="70"
                    :max="100"
                    show-input
                    @change="onSettingChange"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- IPMI配置 -->
        <div class="settings-section">
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Connection /></el-icon>
                IPMI配置
              </span>
            </div>
            <div class="card-content">
              <div class="setting-group">
                <div class="setting-item">
                  <div class="setting-label">
                    <span>IPMI主机地址</span>
                  </div>
                  <el-input
                    v-model="settings.ipmi.host"
                    placeholder="192.168.1.100"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>IPMI端口</span>
                  </div>
                  <el-input-number
                    v-model="settings.ipmi.port"
                    :min="1"
                    :max="65535"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>用户名</span>
                  </div>
                  <el-input
                    v-model="settings.ipmi.username"
                    placeholder="admin"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>密码</span>
                  </div>
                  <el-input
                    v-model="settings.ipmi.password"
                    type="password"
                    show-password
                    placeholder="请输入密码"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>连接超时 (秒)</span>
                  </div>
                  <el-input-number
                    v-model="settings.ipmi.timeout"
                    :min="5"
                    :max="60"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>启用SSL</span>
                  </div>
                  <el-switch 
                    v-model="settings.ipmi.enableSSL" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-actions">
                  <el-button 
                    type="primary" 
                    :icon="Connection"
                    :loading="isTestingConnection"
                    @click="testIPMIConnection"
                  >
                    测试连接
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 界面设置 -->
        <div class="settings-section">
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Brush /></el-icon>
                界面设置
              </span>
            </div>
            <div class="card-content">
              <div class="setting-group">
                <div class="setting-item">
                  <div class="setting-label">
                    <span>主题模式</span>
                  </div>
                  <el-radio-group v-model="settings.ui.theme" @change="onThemeChange">
                    <el-radio label="light">浅色主题</el-radio>
                    <el-radio label="dark">深色主题</el-radio>
                    <el-radio label="auto">跟随系统</el-radio>
                  </el-radio-group>
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>语言</span>
                  </div>
                  <el-select v-model="settings.ui.language" @change="onSettingChange">
                    <el-option label="简体中文" value="zh-CN" />
                    <el-option label="English" value="en-US" />
                    <el-option label="日本語" value="ja-JP" />
                  </el-select>
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>侧边栏折叠</span>
                  </div>
                  <el-switch 
                    v-model="settings.ui.sidebarCollapsed" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>显示动画效果</span>
                  </div>
                  <el-switch 
                    v-model="settings.ui.enableAnimations" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>图表刷新频率</span>
                  </div>
                  <el-select v-model="settings.ui.chartRefreshRate" @change="onSettingChange">
                    <el-option label="实时" :value="1000" />
                    <el-option label="2秒" :value="2000" />
                    <el-option label="5秒" :value="5000" />
                    <el-option label="10秒" :value="10000" />
                  </el-select>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 安全设置 -->
        <div class="settings-section">
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Lock /></el-icon>
                安全设置
              </span>
            </div>
            <div class="card-content">
              <div class="setting-group">
                <div class="setting-item">
                  <div class="setting-label">
                    <span>会话超时 (分钟)</span>
                  </div>
                  <el-input-number
                    v-model="settings.security.sessionTimeout"
                    :min="5"
                    :max="480"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>启用双因素认证</span>
                  </div>
                  <el-switch 
                    v-model="settings.security.enableTwoFactor" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>危险操作确认</span>
                  </div>
                  <el-switch 
                    v-model="settings.security.requireConfirmation" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>登录失败锁定次数</span>
                  </div>
                  <el-input-number
                    v-model="settings.security.maxLoginAttempts"
                    :min="3"
                    :max="10"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>IP白名单</span>
                  </div>
                  <el-input
                    v-model="settings.security.ipWhitelist"
                    type="textarea"
                    :rows="3"
                    placeholder="每行一个IP地址或CIDR网段"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-actions">
                  <el-button 
                    type="warning" 
                    :icon="Key"
                    @click="changePassword"
                  >
                    修改密码
                  </el-button>
                  <el-button 
                    type="danger" 
                    :icon="SwitchButton"
                    @click="logoutAllSessions"
                  >
                    注销所有会话
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 备份与恢复 -->
        <div class="settings-section">
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><FolderOpened /></el-icon>
                备份与恢复
              </span>
            </div>
            <div class="card-content">
              <div class="setting-group">
                <div class="setting-item">
                  <div class="setting-label">
                    <span>自动备份</span>
                  </div>
                  <el-switch 
                    v-model="settings.backup.enableAutoBackup" 
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>备份频率</span>
                  </div>
                  <el-select v-model="settings.backup.frequency" @change="onSettingChange">
                    <el-option label="每天" value="daily" />
                    <el-option label="每周" value="weekly" />
                    <el-option label="每月" value="monthly" />
                  </el-select>
                </div>

                <div class="setting-item">
                  <div class="setting-label">
                    <span>备份保留数量</span>
                  </div>
                  <el-input-number
                    v-model="settings.backup.retentionCount"
                    :min="1"
                    :max="30"
                    @change="onSettingChange"
                  />
                </div>

                <div class="setting-actions">
                  <el-button 
                    type="primary" 
                    :icon="Download"
                    :loading="isBackingUp"
                    @click="createBackup"
                  >
                    立即备份
                  </el-button>
                  <el-button 
                    type="success" 
                    :icon="Upload"
                    @click="restoreBackup"
                  >
                    恢复备份
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="100px"
      >
        <el-form-item label="当前密码" prop="currentPassword">
          <el-input
            v-model="passwordForm.currentPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="passwordForm.newPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="passwordForm.confirmPassword"
            type="password"
            show-password
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="passwordDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            :loading="isChangingPassword"
            @click="submitPasswordChange"
          >
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 系统设置页面
 * 提供系统配置、监控阈值、IPMI配置、界面设置、安全设置等功能
 */
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Setting, Check, RefreshLeft, Monitor, Warning, Connection, 
  Brush, Lock, FolderOpened, QuestionFilled, Key, SwitchButton,
  Download, Upload
} from '@element-plus/icons-vue'

const isSaving = ref(false)
const isTestingConnection = ref(false)
const isBackingUp = ref(false)
const isChangingPassword = ref(false)
const passwordDialogVisible = ref(false)
const passwordFormRef = ref(null)

// 设置数据
const settings = reactive({
  system: {
    refreshInterval: 10000,
    temperatureUnit: 'celsius',
    enableSound: true,
    enableNotification: true,
    dataRetentionDays: 30
  },
  thresholds: {
    cpuWarning: 80,
    cpuDanger: 90,
    memoryWarning: 85,
    memoryDanger: 95,
    diskWarning: 80,
    diskDanger: 90,
    temperatureWarning: 75,
    temperatureDanger: 85
  },
  ipmi: {
    host: '192.168.1.100',
    port: 623,
    username: 'admin',
    password: '',
    timeout: 30,
    enableSSL: false
  },
  ui: {
    theme: 'light',
    language: 'zh-CN',
    sidebarCollapsed: false,
    enableAnimations: true,
    chartRefreshRate: 2000
  },
  security: {
    sessionTimeout: 60,
    enableTwoFactor: false,
    requireConfirmation: true,
    maxLoginAttempts: 5,
    ipWhitelist: ''
  },
  backup: {
    enableAutoBackup: true,
    frequency: 'daily',
    retentionCount: 7
  }
})

// 修改密码表单
const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 密码验证规则
const passwordRules = {
  currentPassword: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度不能少于8位', trigger: 'blur' },
    { 
      pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      message: '密码必须包含大小写字母、数字和特殊字符',
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

onMounted(() => {
  loadSettings()
})

/**
 * 加载设置
 */
const loadSettings = async () => {
  try {
    // 从localStorage加载设置
    const savedSettings = localStorage.getItem('system_settings')
    if (savedSettings) {
      const parsed = JSON.parse(savedSettings)
      Object.assign(settings, parsed)
    }
    
    // 应用主题设置
    applyTheme(settings.ui.theme)
    
  } catch (error) {
    ElMessage.error('加载设置失败: ' + error.message)
  }
}

/**
 * 设置变更处理
 */
const onSettingChange = () => {
  // 自动保存到localStorage
  localStorage.setItem('system_settings', JSON.stringify(settings))
}

/**
 * 主题变更处理
 */
const onThemeChange = (theme) => {
  applyTheme(theme)
  onSettingChange()
}

/**
 * 应用主题
 * @param {string} theme 主题名称
 */
const applyTheme = (theme) => {
  const html = document.documentElement
  
  if (theme === 'dark') {
    html.classList.add('dark')
  } else if (theme === 'light') {
    html.classList.remove('dark')
  } else if (theme === 'auto') {
    // 跟随系统主题
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    if (prefersDark) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }
}

/**
 * 保存所有设置
 */
const saveAllSettings = async () => {
  isSaving.value = true
  
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // 保存到localStorage
    localStorage.setItem('system_settings', JSON.stringify(settings))
    
    ElMessage.success('设置保存成功')
    
  } catch (error) {
    ElMessage.error('保存设置失败: ' + error.message)
  } finally {
    isSaving.value = false
  }
}

/**
 * 重置所有设置
 */
const resetAllSettings = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重置所有设置吗？此操作将恢复默认配置！',
      '确认重置',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 重置为默认值
    Object.assign(settings, {
      system: {
        refreshInterval: 10000,
        temperatureUnit: 'celsius',
        enableSound: true,
        enableNotification: true,
        dataRetentionDays: 30
      },
      thresholds: {
        cpuWarning: 80,
        cpuDanger: 90,
        memoryWarning: 85,
        memoryDanger: 95,
        diskWarning: 80,
        diskDanger: 90,
        temperatureWarning: 75,
        temperatureDanger: 85
      },
      ipmi: {
        host: '192.168.1.100',
        port: 623,
        username: 'admin',
        password: '',
        timeout: 30,
        enableSSL: false
      },
      ui: {
        theme: 'light',
        language: 'zh-CN',
        sidebarCollapsed: false,
        enableAnimations: true,
        chartRefreshRate: 2000
      },
      security: {
        sessionTimeout: 60,
        enableTwoFactor: false,
        requireConfirmation: true,
        maxLoginAttempts: 5,
        ipWhitelist: ''
      },
      backup: {
        enableAutoBackup: true,
        frequency: 'daily',
        retentionCount: 7
      }
    })
    
    // 应用主题
    applyTheme(settings.ui.theme)
    
    // 保存到localStorage
    localStorage.setItem('system_settings', JSON.stringify(settings))
    
    ElMessage.success('设置已重置')
    
  } catch (error) {
    // 用户取消操作
  }
}

/**
 * 测试IPMI连接
 */
const testIPMIConnection = async () => {
  isTestingConnection.value = true
  
  try {
    // 模拟连接测试
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 随机成功或失败
    if (Math.random() > 0.3) {
      ElMessage.success('IPMI连接测试成功')
    } else {
      throw new Error('连接超时或认证失败')
    }
    
  } catch (error) {
    ElMessage.error('IPMI连接测试失败: ' + error.message)
  } finally {
    isTestingConnection.value = false
  }
}

/**
 * 修改密码
 */
const changePassword = () => {
  passwordForm.currentPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordDialogVisible.value = true
}

/**
 * 提交密码修改
 */
const submitPasswordChange = async () => {
  try {
    await passwordFormRef.value.validate()
    
    isChangingPassword.value = true
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('密码修改成功')
    passwordDialogVisible.value = false
    
  } catch (error) {
    if (error !== false) {
      ElMessage.error('密码修改失败: ' + error.message)
    }
  } finally {
    isChangingPassword.value = false
  }
}

/**
 * 注销所有会话
 */
const logoutAllSessions = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要注销所有会话吗？这将强制所有用户重新登录！',
      '确认注销',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    ElMessage.success('所有会话已注销')
    
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('注销失败: ' + error.message)
    }
  }
}

/**
 * 创建备份
 */
const createBackup = async () => {
  isBackingUp.value = true
  
  try {
    // 模拟备份过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // 生成备份文件
    const backupData = {
      timestamp: new Date().toISOString(),
      settings: settings,
      version: '1.0.0'
    }
    
    const blob = new Blob([JSON.stringify(backupData, null, 2)], { 
      type: 'application/json' 
    })
    
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    
    link.setAttribute('href', url)
    link.setAttribute('download', `system_backup_${new Date().toISOString().slice(0, 10)}.json`)
    link.style.visibility = 'hidden'
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    ElMessage.success('备份创建成功')
    
  } catch (error) {
    ElMessage.error('创建备份失败: ' + error.message)
  } finally {
    isBackingUp.value = false
  }
}

/**
 * 恢复备份
 */
const restoreBackup = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  
  input.onchange = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    try {
      const text = await file.text()
      const backupData = JSON.parse(text)
      
      if (!backupData.settings) {
        throw new Error('无效的备份文件格式')
      }
      
      await ElMessageBox.confirm(
        '确定要恢复备份吗？当前设置将被覆盖！',
        '确认恢复',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      // 恢复设置
      Object.assign(settings, backupData.settings)
      
      // 应用主题
      applyTheme(settings.ui.theme)
      
      // 保存到localStorage
      localStorage.setItem('system_settings', JSON.stringify(settings))
      
      ElMessage.success('备份恢复成功')
      
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('恢复备份失败: ' + error.message)
      }
    }
  }
  
  input.click()
}
</script>

<style lang="scss" scoped>
.settings {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color-page);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  box-shadow: var(--shadow-light);

  .header-left {
    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      margin: 0 0 var(--spacing-xs) 0;
    }

    .page-description {
      color: var(--el-text-color-secondary);
      margin: 0;
    }
  }

  .header-right {
    display: flex;
    gap: var(--spacing-sm);
  }
}

.settings-content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: var(--spacing-lg);
}

.settings-section {
  .dashboard-card {
    height: fit-content;
  }
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);

  .setting-label {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    font-weight: 500;
    color: var(--el-text-color-primary);

    .el-icon {
      color: var(--el-text-color-secondary);
      cursor: help;
    }
  }
}

.setting-actions {
  display: flex;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: var(--spacing-md);
}

// 响应式设计
@media (max-width: 1200px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);

    .header-right {
      align-self: flex-end;
    }
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: var(--spacing-md);

    .header-left .page-title {
      font-size: 20px;
    }

    .header-right {
      width: 100%;
      justify-content: flex-end;
    }
  }

  .settings-content {
    padding: var(--spacing-md);
  }

  .settings-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }

  .setting-actions {
    flex-direction: column;
  }
}
</style>