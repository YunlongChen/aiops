<!--
  面包屑导航组件
  显示当前页面的导航路径
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="app-breadcrumb" v-if="breadcrumbs.length > 0">
    <div class="breadcrumb-container">
      <nav class="breadcrumb-nav">
        <ol class="breadcrumb-list">
          <li 
            v-for="(item, index) in breadcrumbs" 
            :key="index"
            class="breadcrumb-item"
            :class="{ 'active': index === breadcrumbs.length - 1 }"
          >
            <router-link 
              v-if="item.path && index < breadcrumbs.length - 1"
              :to="item.path"
              class="breadcrumb-link"
            >
              <i v-if="item.icon" :class="item.icon" class="breadcrumb-icon"></i>
              {{ item.title }}
            </router-link>
            <span v-else class="breadcrumb-text">
              <i v-if="item.icon" :class="item.icon" class="breadcrumb-icon"></i>
              {{ item.title }}
            </span>
            <i 
              v-if="index < breadcrumbs.length - 1" 
              class="breadcrumb-separator icon-chevron-right"
            ></i>
          </li>
        </ol>
      </nav>
      
      <!-- 页面操作按钮 -->
      <div class="breadcrumb-actions" v-if="pageActions.length > 0">
        <button
          v-for="action in pageActions"
          :key="action.id"
          class="action-btn"
          :class="action.type || 'default'"
          @click="handleAction(action)"
          :disabled="action.disabled"
        >
          <i v-if="action.icon" :class="action.icon"></i>
          {{ action.title }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 面包屑导航组件
 * 根据当前路由自动生成面包屑导航
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

// 使用路由
const route = useRoute()
const router = useRouter()

// 路由到面包屑的映射配置
const routeBreadcrumbMap = {
  '/': [
    { title: '首页', icon: 'icon-home', path: '/' }
  ],
  '/dashboard': [
    { title: '仪表板', icon: 'icon-home', path: '/' }
  ],
  '/monitoring/infrastructure/servers': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '监控中心', icon: 'icon-monitor' },
    { title: '服务器监控', icon: 'icon-server' }
  ],
  '/monitoring/network': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '监控中心', icon: 'icon-monitor' },
    { title: '网络监控', icon: 'icon-network' }
  ],
  '/monitoring/application': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '监控中心', icon: 'icon-monitor' },
    { title: '应用监控', icon: 'icon-app' }
  ],
  '/monitoring/database': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '监控中心', icon: 'icon-monitor' },
    { title: '数据库监控', icon: 'icon-database' }
  ],
  '/ai-engine': [
    { title: 'AI引擎', icon: 'icon-monitor' },
  ],
  '/alerting/dashboard': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '告警管理', icon: 'icon-alert-triangle' },
  ],
  '/alerting/rules': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '告警管理', icon: 'icon-alert-triangle' },
    { title: '告警规则', icon: 'icon-rule' }
  ],
  '/alerting/history': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '告警管理', icon: 'icon-alert-triangle' },
    { title: '告警历史', icon: 'icon-history' }
  ],
  '/alerting/notifications': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '告警管理', icon: 'icon-alert-triangle' },
    { title: '通知配置', icon: 'icon-bell' }
  ],
  '/ai-engine/anomaly-detection': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: 'AI引擎', icon: 'icon-cpu' },
    { title: '异常检测', icon: 'icon-search' }
  ],
  '/ai-engine/predictive-analysis': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: 'AI引擎', icon: 'icon-cpu' },
    { title: '预测分析', icon: 'icon-trending-up' }
  ],
  '/ai-engine/intelligent-diagnosis': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: 'AI引擎', icon: 'icon-cpu' },
    { title: '智能诊断', icon: 'icon-activity' }
  ],
  '/self-healing/auto-recovery': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '自愈系统', icon: 'icon-shield' },
    { title: '自动恢复', icon: 'icon-refresh-cw' }
  ],
  '/self-healing/recovery-policies': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '自愈系统', icon: 'icon-shield' },
    { title: '恢复策略', icon: 'icon-file-text' }
  ],
  '/self-healing/recovery-history': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '自愈系统', icon: 'icon-shield' },
    { title: '恢复历史', icon: 'icon-clock' }
  ],
  '/settings': [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: '系统设置', icon: 'icon-settings' }
  ]
}

// 计算面包屑
const breadcrumbs = computed(() => {
  const currentPath = route.path
  return routeBreadcrumbMap[currentPath] || [
    { title: '首页', icon: 'icon-home', path: '/' },
    { title: currentPath, icon: 'icon-help-circle' }
  ]
})

// 页面操作按钮（根据不同页面显示不同的操作）
const pageActions = computed(() => {
  const currentPath = route.path
  
  // 根据不同页面返回不同的操作按钮
  switch (currentPath) {
    case '/monitoring/server':
      return [
        { id: 'refresh', title: '刷新', icon: 'icon-refresh-cw', type: 'default' },
        { id: 'export', title: '导出', icon: 'icon-download', type: 'default' }
      ]
    case '/alerting/rules':
      return [
        { id: 'add-rule', title: '新增规则', icon: 'icon-plus', type: 'primary' },
        { id: 'import', title: '导入', icon: 'icon-upload', type: 'default' }
      ]
    case '/settings':
      return [
        { id: 'save', title: '保存', icon: 'icon-save', type: 'primary' },
        { id: 'reset', title: '重置', icon: 'icon-rotate-ccw', type: 'default' }
      ]
    default:
      return []
  }
})

/**
 * 处理操作按钮点击
 */
const handleAction = (action) => {
  console.log('执行操作:', action.id)
  // TODO: 根据不同的操作执行相应的功能
  switch (action.id) {
    case 'refresh':
      // 刷新页面数据
      break
    case 'export':
      // 导出数据
      break
    case 'add-rule':
      // 新增告警规则
      break
    case 'import':
      // 导入数据
      break
    case 'save':
      // 保存设置
      break
    case 'reset':
      // 重置设置
      break
    default:
      console.log('未知操作:', action.id)
  }
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.app-breadcrumb {
  background: $white;
  border-bottom: 1px solid $border-color-light;
  padding: $spacing-md $spacing-lg;
}

.breadcrumb-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 100%;
}

.breadcrumb-nav {
  flex: 1;
  min-width: 0;
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  margin: 0;
  padding: 0;
  list-style: none;
  flex-wrap: wrap;
  gap: $spacing-xs;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  
  &:not(:last-child) {
    margin-right: $spacing-sm;
  }
  
  &.active {
    .breadcrumb-text {
      color: $text-color;
      font-weight: 500;
    }
  }
}

.breadcrumb-link {
  display: flex;
  align-items: center;
  color: $text-color-secondary;
  text-decoration: none;
  font-size: 14px;
  transition: color 0.3s ease;
  
  &:hover {
    color: $primary-color;
  }
}

.breadcrumb-text {
  display: flex;
  align-items: center;
  color: $text-color-secondary;
  font-size: 14px;
}

.breadcrumb-icon {
  font-size: 14px;
  margin-right: $spacing-xs;
}

.breadcrumb-separator {
  font-size: 12px;
  color: $text-color-placeholder;
  margin: 0 $spacing-sm;
}

.breadcrumb-actions {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-left: $spacing-lg;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  background: $white;
  color: $text-color;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover:not(:disabled) {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.primary {
    background: $primary-color;
    border-color: $primary-color;
    color: $white;
    
    &:hover:not(:disabled) {
      background: darken($primary-color, 10%);
      border-color: darken($primary-color, 10%);
    }
  }
  
  &.success {
    background: $success-color;
    border-color: $success-color;
    color: $white;
    
    &:hover:not(:disabled) {
      background: darken($success-color, 10%);
      border-color: darken($success-color, 10%);
    }
  }
  
  &.warning {
    background: $warning-color;
    border-color: $warning-color;
    color: $white;
    
    &:hover:not(:disabled) {
      background: darken($warning-color, 10%);
      border-color: darken($warning-color, 10%);
    }
  }
  
  &.danger {
    background: $danger-color;
    border-color: $danger-color;
    color: $white;
    
    &:hover:not(:disabled) {
      background: darken($danger-color, 10%);
      border-color: darken($danger-color, 10%);
    }
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  i {
    font-size: 14px;
  }
}

// 响应式设计
@media (max-width: 768px) {
  .breadcrumb-container {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-md;
  }
  
  .breadcrumb-actions {
    margin-left: 0;
    width: 100%;
    justify-content: flex-end;
  }
  
  .breadcrumb-list {
    font-size: 13px;
  }
  
  .action-btn {
    padding: $spacing-xs $spacing-sm;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .breadcrumb-actions {
    flex-wrap: wrap;
  }
  
  .action-btn {
    flex: 1;
    min-width: 80px;
    justify-content: center;
  }
}
</style>