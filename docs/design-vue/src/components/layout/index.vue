<!--
  主布局组件
  包含侧边栏导航和主内容区域
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <i class="icon-activity"></i>
          <span v-show="!sidebarCollapsed" class="logo-text">AIOps</span>
        </div>
        <button 
          class="collapse-btn" 
          @click="toggleSidebar"
          :title="sidebarCollapsed ? '展开菜单' : '收起菜单'"
        >
          <i :class="sidebarCollapsed ? 'icon-chevron-right' : 'icon-chevron-left'"></i>
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <ul class="nav-list">
          <li class="nav-item">
            <router-link to="/" class="nav-link" exact-active-class="active">
              <i class="icon-home"></i>
              <span v-show="!sidebarCollapsed" class="nav-text">系统概览</span>
            </router-link>
          </li>
          
          <li class="nav-item">
            <div class="nav-group">
              <div class="nav-group-title">
                <i class="icon-monitor"></i>
                <span v-show="!sidebarCollapsed" class="nav-text">监控中心</span>
              </div>
              <ul class="nav-sublist" v-show="!sidebarCollapsed">
                <li class="nav-subitem">
                  <router-link to="/monitoring/metrics" class="nav-link" active-class="active">
                    <span class="nav-text">指标监控</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/monitoring/logs" class="nav-link" active-class="active">
                    <span class="nav-text">日志分析</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/monitoring/performance" class="nav-link" active-class="active">
                    <span class="nav-text">性能监控</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/monitoring/infrastructure" class="nav-link" active-class="active">
                    <span class="nav-text">基础设施</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          
          <li class="nav-item">
            <div class="nav-group">
              <div class="nav-group-title">
                <i class="icon-alert-triangle"></i>
                <span v-show="!sidebarCollapsed" class="nav-text">告警管理</span>
              </div>
              <ul class="nav-sublist" v-show="!sidebarCollapsed">
                <li class="nav-subitem">
                  <router-link to="/alerts/dashboard" class="nav-link" active-class="active">
                    <span class="nav-text">告警仪表板</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/alerts/rules" class="nav-link" active-class="active">
                    <span class="nav-text">告警规则</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/alerts/history" class="nav-link" active-class="active">
                    <span class="nav-text">告警历史</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          
          <li class="nav-item">
            <div class="nav-group">
              <div class="nav-group-title">
                <i class="icon-cpu"></i>
                <span v-show="!sidebarCollapsed" class="nav-text">AI引擎</span>
              </div>
              <ul class="nav-sublist" v-show="!sidebarCollapsed">
                <li class="nav-subitem">
                  <router-link to="/ai/anomaly-detection" class="nav-link" active-class="active">
                    <span class="nav-text">异常检测</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/ai/predictive-analysis" class="nav-link" active-class="active">
                    <span class="nav-text">预测分析</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/ai/model-management" class="nav-link" active-class="active">
                    <span class="nav-text">模型管理</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/ai/intelligent-optimization" class="nav-link" active-class="active">
                    <span class="nav-text">智能优化</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
          
          <li class="nav-item">
            <div class="nav-group">
              <div class="nav-group-title">
                <i class="icon-shield"></i>
                <span v-show="!sidebarCollapsed" class="nav-text">自愈系统</span>
              </div>
              <ul class="nav-sublist" v-show="!sidebarCollapsed">
                <li class="nav-subitem">
                  <router-link to="/self-healing/auto-recovery" class="nav-link" active-class="active">
                    <span class="nav-text">自动恢复</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/self-healing/policy-management" class="nav-link" active-class="active">
                    <span class="nav-text">策略管理</span>
                  </router-link>
                </li>
                <li class="nav-subitem">
                  <router-link to="/self-healing/health-monitoring" class="nav-link" active-class="active">
                    <span class="nav-text">健康监控</span>
                  </router-link>
                </li>
              </ul>
            </div>
          </li>
        </ul>
      </nav>
    </aside>
    
    <!-- 主内容区域 -->
    <main class="main-content" :class="{ expanded: sidebarCollapsed }">
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
/**
 * 主布局组件
 * 包含侧边栏导航和主内容区域
 */
import { ref } from 'vue'

// 响应式数据
const sidebarCollapsed = ref(false)

/**
 * 切换侧边栏展开/收起状态
 */
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.layout {
  display: flex;
  height: 100vh;
  background: $bg-primary;
}

// 侧边栏
.sidebar {
  width: 260px;
  background: $white;
  border-right: 1px solid $border-color-light;
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 100;
  
  &.collapsed {
    width: 64px;
  }
}
</style>

.sidebar-header {
  height: 64px;
  padding: 0 $spacing-md;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  color: $primary-color;
  font-weight: 700;
  font-size: 18px;
  
  i {
    font-size: 24px;
  }
}

.logo-text {
  transition: opacity 0.3s ease;
}

.collapse-btn {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color-light;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: $spacing-md 0;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-bottom: $spacing-xs;
}

.nav-group {
  padding: 0 $spacing-md;
}

.nav-group-title {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm 0;
  color: $text-color-secondary;
  font-size: 13px;
  font-weight: 500;
  border-bottom: 1px solid $border-color-light;
  margin-bottom: $spacing-xs;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-md;
  color: $text-color-secondary;
  text-decoration: none;
  transition: all 0.2s ease;
  border-radius: $border-radius-sm;
  margin: 0 $spacing-xs;
  
  &:hover {
    background: $background-color-light;
    color: $text-color;
  }
  
  &.active {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
    font-weight: 500;
  }
  
  i {
    font-size: 16px;
    width: 16px;
    text-align: center;
  }
}

.nav-text {
  font-size: 14px;
  transition: opacity 0.3s ease;
}

.nav-sublist {
  list-style: none;
  margin: 0;
  padding: 0;
  margin-left: $spacing-lg;
}

.nav-subitem {
  margin-bottom: 2px;
}

.nav-sublist .nav-link {
  padding: $spacing-xs $spacing-sm;
  font-size: 13px;
  
  .nav-text {
    font-size: 13px;
  }
}

// 主内容区域
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: margin-left 0.3s ease;
  
  &.expanded {
    margin-left: 0;
  }
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  background: $background-color;
}

// 响应式设计
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    
    &:not(.collapsed) {
      transform: translateX(0);
    }
  }
  
  .main-content {
    margin-left: 0;
    width: 100%;
  }
  
  .nav-group-title,
  .nav-sublist {
    display: block;
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 280px;
  }
  
  .sidebar-header {
    padding: 0 $spacing-sm;
  }
  
  .nav-group {
    padding: 0 $spacing-sm;
  }
  
  .nav-link {
    margin: 0 $spacing-xs;
    padding: $spacing-sm;
  }
}