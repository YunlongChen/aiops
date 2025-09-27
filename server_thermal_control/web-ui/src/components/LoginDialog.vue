<template>
  <el-dialog
    v-model="visible"
    title="用户登录"
    width="400px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    center
  >
    <div class="login-form">
      <div class="login-header">
        <el-icon class="login-icon" size="48">
          <User />
        </el-icon>
        <h2>服务器热控管理系统</h2>
        <p>请登录以继续使用</p>
      </div>
      
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        size="large"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="loginForm.username"
            :prefix-icon="User"
            placeholder="请输入用户名"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            :prefix-icon="Lock"
            placeholder="请输入密码"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item v-if="securityStore.securitySettings.twoFactorEnabled">
          <el-input
            v-model="loginForm.twoFactorCode"
            :prefix-icon="Key"
            placeholder="请输入双因素认证码"
            maxlength="6"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <el-form-item>
          <el-checkbox v-model="loginForm.rememberMe">
            记住我
          </el-checkbox>
        </el-form-item>
      </el-form>
      
      <!-- 账户锁定提示 -->
      <el-alert
        v-if="securityStore.isAccountLocked"
        :title="`账户已被锁定，请在 ${securityStore.lockTimeRemaining} 分钟后重试`"
        type="error"
        :closable="false"
        show-icon
        class="lock-alert"
      />
      
      <!-- 登录提示信息 -->
      <div class="login-tips">
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="默认账户信息" name="accounts">
            <div class="account-info">
              <div class="account-item">
                <strong>管理员:</strong> admin / admin123
                <el-tag size="small" type="danger">完全权限</el-tag>
              </div>
              <div class="account-item">
                <strong>操作员:</strong> operator / operator123
                <el-tag size="small" type="warning">操作权限</el-tag>
              </div>
              <div class="account-item">
                <strong>观察者:</strong> viewer / viewer123
                <el-tag size="small" type="info">只读权限</el-tag>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
    
    <template #footer>
      <div class="login-footer">
        <el-button
          type="primary"
          size="large"
          :loading="loginLoading"
          :disabled="securityStore.isAccountLocked"
          @click="handleLogin"
          style="width: 100%"
        >
          {{ loginLoading ? '登录中...' : '登录' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
/**
 * 登录对话框组件
 * 提供用户认证界面和安全验证
 */
import { ref, reactive, computed, watch } from 'vue'
import { User, Lock, Key } from '@element-plus/icons-vue'
import { useSecurityStore } from '@/stores/security'

const securityStore = useSecurityStore()

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'login-success'])

// 响应式数据
const loginFormRef = ref()
const loginLoading = ref(false)
const activeCollapse = ref([])

const loginForm = reactive({
  username: '',
  password: '',
  twoFactorCode: '',
  rememberMe: false
})

// 表单验证规则
const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ]
}

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 监听对话框显示状态
watch(visible, (newVal) => {
  if (newVal) {
    // 重置表单
    resetForm()
  }
})

/**
 * 处理登录
 */
const handleLogin = async () => {
  try {
    // 验证表单
    const valid = await loginFormRef.value?.validate()
    if (!valid) return
    
    loginLoading.value = true
    
    // 执行登录
    const success = await securityStore.login({
      username: loginForm.username,
      password: loginForm.password,
      twoFactorCode: loginForm.twoFactorCode,
      rememberMe: loginForm.rememberMe
    })
    
    if (success) {
      // 登录成功
      visible.value = false
      emit('login-success')
    }
    
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
    loginLoading.value = false
  }
}

/**
 * 重置表单
 */
const resetForm = () => {
  loginForm.username = ''
  loginForm.password = ''
  loginForm.twoFactorCode = ''
  loginForm.rememberMe = false
  
  // 清除验证错误
  loginFormRef.value?.clearValidate()
}

/**
 * 快速填充账户信息
 */
const fillAccount = (username, password) => {
  loginForm.username = username
  loginForm.password = password
}

// 暴露方法给父组件
defineExpose({
  fillAccount,
  resetForm
})
</script>

<style lang="scss" scoped>
.login-form {
  padding: 20px 0;
  
  .login-header {
    text-align: center;
    margin-bottom: 30px;
    
    .login-icon {
      color: var(--el-color-primary);
      margin-bottom: 16px;
    }
    
    h2 {
      margin: 0 0 8px 0;
      color: var(--el-text-color-primary);
      font-size: 24px;
      font-weight: 600;
    }
    
    p {
      margin: 0;
      color: var(--el-text-color-regular);
      font-size: 14px;
    }
  }
  
  .lock-alert {
    margin-bottom: 20px;
  }
  
  .login-tips {
    margin-top: 20px;
    
    .account-info {
      .account-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid var(--el-border-color-lighter);
        
        &:last-child {
          border-bottom: none;
        }
        
        strong {
          color: var(--el-text-color-primary);
        }
      }
    }
  }
}

.login-footer {
  padding: 0 20px 20px 20px;
}

// 深色主题适配
.dark {
  .login-form {
    .login-header {
      h2 {
        color: var(--el-text-color-primary);
      }
      
      p {
        color: var(--el-text-color-regular);
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .login-form {
    padding: 10px 0;
    
    .login-header {
      margin-bottom: 20px;
      
      h2 {
        font-size: 20px;
      }
    }
  }
}
</style>