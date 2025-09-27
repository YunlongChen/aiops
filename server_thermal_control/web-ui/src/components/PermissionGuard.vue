<template>
  <div v-if="hasPermission" class="permission-guard">
    <slot />
  </div>
  <div v-else-if="showFallback" class="permission-denied">
    <slot name="fallback">
      <el-empty
        :image-size="80"
        description="您没有权限访问此功能"
      >
        <template #image>
          <el-icon size="80" color="#C0C4CC">
            <Lock />
          </el-icon>
        </template>
        <el-button
          v-if="showLoginButton"
          type="primary"
          @click="handleLogin"
        >
          登录
        </el-button>
      </el-empty>
    </slot>
  </div>
</template>

<script setup>
/**
 * 权限守卫组件
 * 用于控制组件和功能的访问权限
 */
import { computed } from 'vue'
import { Lock } from '@element-plus/icons-vue'
import { useSecurityStore } from '@/stores/security'

const securityStore = useSecurityStore()

// Props
const props = defineProps({
  // 所需权限列表
  permissions: {
    type: [String, Array],
    default: null
  },
  // 所需角色列表
  roles: {
    type: [String, Array],
    default: null
  },
  // 权限检查模式：'all' 需要所有权限，'any' 需要任一权限
  mode: {
    type: String,
    default: 'any',
    validator: (value) => ['all', 'any'].includes(value)
  },
  // 是否显示无权限时的后备内容
  showFallback: {
    type: Boolean,
    default: true
  },
  // 是否显示登录按钮（当用户未登录时）
  showLoginButton: {
    type: Boolean,
    default: true
  },
  // 是否需要登录
  requireAuth: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['permission-denied', 'login-required'])

// 计算属性
const hasPermission = computed(() => {
  // 如果不需要认证，直接通过
  if (!props.requireAuth) {
    return true
  }
  
  // 检查是否已登录
  if (!securityStore.isAuthenticated) {
    emit('login-required')
    return false
  }
  
  // 检查角色权限
  if (props.roles) {
    const requiredRoles = Array.isArray(props.roles) ? props.roles : [props.roles]
    const hasRole = requiredRoles.some(role => securityStore.hasRole(role))
    
    if (!hasRole) {
      emit('permission-denied', { type: 'role', required: requiredRoles })
      return false
    }
  }
  
  // 检查具体权限
  if (props.permissions) {
    const requiredPermissions = Array.isArray(props.permissions) 
      ? props.permissions 
      : [props.permissions]
    
    let hasRequiredPermissions = false
    
    if (props.mode === 'all') {
      // 需要所有权限
      hasRequiredPermissions = requiredPermissions.every(permission => 
        securityStore.hasPermission(permission)
      )
    } else {
      // 需要任一权限
      hasRequiredPermissions = requiredPermissions.some(permission => 
        securityStore.hasPermission(permission)
      )
    }
    
    if (!hasRequiredPermissions) {
      emit('permission-denied', { 
        type: 'permission', 
        required: requiredPermissions,
        mode: props.mode
      })
      return false
    }
  }
  
  return true
})

/**
 * 处理登录
 */
const handleLogin = () => {
  securityStore.showLoginDialog()
}
</script>

<style lang="scss" scoped>
.permission-guard {
  // 权限通过时的容器样式
}

.permission-denied {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  padding: 20px;
  
  .el-empty {
    .el-button {
      margin-top: 16px;
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .permission-denied {
    min-height: 150px;
    padding: 10px;
  }
}
</style>