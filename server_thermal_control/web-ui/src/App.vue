<template>
  <div id="app">
    <router-view />
    
    <!-- 登录对话框 -->
    <LoginDialog
      v-model="securityStore.showLogin"
      @login-success="handleLoginSuccess"
    />
  </div>
</template>

<script setup>
/**
 * 主应用组件
 * 集成系统初始化、安全管理和全局组件
 */
import { onMounted } from 'vue'
import { useSystemStore } from '@/stores/system'
import { useSecurityStore } from '@/stores/security'
import LoginDialog from '@/components/LoginDialog.vue'
import { ElMessage } from 'element-plus'

const systemStore = useSystemStore()
const securityStore = useSecurityStore()

onMounted(() => {
  // 初始化安全管理
  securityStore.initializeSecurity()
  
  // 初始化系统数据
  systemStore.initializeSystem()
  
  // 设置定期检查会话状态
  setInterval(checkSessionStatus, 60000) // 每分钟检查一次
})

/**
 * 检查会话状态
 */
const checkSessionStatus = () => {
  // 如果启用了会话超时检查
  if (securityStore.securitySettings.sessionTimeout > 0) {
    // 设置定期检查
    setInterval(() => {
      if (securityStore.isAuthenticated && securityStore.isSessionExpired()) {
        ElMessage.warning('会话已过期，请重新登录')
        securityStore.logout()
      }
    }, 60000) // 每分钟检查一次
  }
}

/**
 * 处理登录成功
 */
const handleLoginSuccess = () => {
  ElMessage.success(`欢迎回来，${securityStore.currentUser?.username}！`)
  
  // 记录登录日志
  securityStore.logOperation('user_login', '用户登录成功', {
    username: securityStore.currentUser?.username,
    role: securityStore.currentUser?.role,
    loginTime: new Date().toISOString()
  })
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

/* 全局样式 */
.permission-required {
  opacity: 0.6;
  pointer-events: none;
}

.danger-operation {
  border: 2px solid var(--el-color-danger);
  border-radius: 4px;
}

/* 安全提示样式 */
.security-notice {
  background: var(--el-color-warning-light-9);
  border: 1px solid var(--el-color-warning);
  border-radius: 4px;
  padding: 12px;
  margin: 16px 0;
  
  .notice-title {
    font-weight: 600;
    color: var(--el-color-warning);
    margin-bottom: 8px;
  }
  
  .notice-content {
    color: var(--el-text-color-regular);
    font-size: 14px;
    line-height: 1.5;
  }
}

/* 深色主题适配 */
.dark {
  .security-notice {
    background: var(--el-color-warning-dark-2);
    border-color: var(--el-color-warning);
    
    .notice-title {
      color: var(--el-color-warning-light-3);
    }
    
    .notice-content {
      color: var(--el-text-color-regular);
    }
  }
}
</style>