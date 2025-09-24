<!--
  应用侧边栏组件
  包含快速导航菜单和功能分组
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3>快速导航</h3>
    </div>

    <div class="sidebar-menu">
      <!-- 操作类别 -->
        <!-- 监控概览 -->
      <div class="menu-group" v-for="group in groupsItems" :key="group.id">
        <div class="menu-title">{{group.name}}</div>
        <div
            v-for="item in group.items"
            :key="item.id"
            class="menu-item"
            :class="{ active: activeSubpage === item.id }"
            @click="setActiveSubpage(item.id)"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
/**
 * 应用侧边栏组件
 * 提供快速导航和功能分组
 */
import {ref} from 'vue'

// 当前激活的子页面
const activeSubpage = ref('system-overview')

// 监控概览菜单项
const monitoringItems = [
  {id: 'system-overview', label: '系统概览', icon: 'fas fa-server'},
  {id: 'infrastructure', label: '基础设施', icon: 'fas fa-network-wired'},
  {id: 'applications', label: '应用服务', icon: 'fas fa-cube'},
  {id: 'databases', label: '数据库', icon: 'fas fa-database'}
]

// AI分析菜单项
const aiAnalysisItems = [
  {id: 'anomaly-detection', label: '异常检测', icon: 'fas fa-search'},
  {id: 'prediction', label: '预测分析', icon: 'fas fa-search'},
  {id: 'model-management', label: '模型管理', icon: 'fas fa-cogs'}
]

// 运维管理菜单项
const operationItems = [
  {id: 'alert-rules', label: '告警规则', icon: 'fas fa-exclamation-triangle', path: '/alerting'},
  {id: 'automation', label: '自动化脚本', icon: 'fas fa-robot', path: '/self-healing'},
  {id: 'logs', label: '日志分析', icon: 'fas fa-file-alt', path: '/logs'},
  {id: 'settings', label: '系统设置', icon: 'fas fa-cog', path: '/settings'}
]

const groupsItems = [
  {
    id: 'system-overview',
    name: "监控概览",
    items: monitoringItems
  },
  {
    id: 'ai-analysis',
    name: "AI分析",
    items: aiAnalysisItems
  },
  {
    id: 'operation',
    name: "运维管理",
    items: operationItems
  }
]

/**
 * 设置激活的子页面
 */
const setActiveSubpage = (subpageId) => {
  activeSubpage.value = subpageId
  // TODO: 触发子页面切换事件
  console.log('切换到子页面:', subpageId)
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 64px;
  left: 0;
  width: 280px;
  height: calc(100vh - 64px);
  background: $bg-primary;
  border-right: 1px solid $border-color;
  overflow-y: auto;
  z-index: 900;
}

.sidebar-header {
  padding: $spacing-lg $spacing-lg $spacing-md;
  border-bottom: 1px solid $border-color;

  h3 {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $text-color-primary;
  }
}

.sidebar-menu {
  padding: $spacing-md;
}

.menu-group {
  margin-bottom: $spacing-lg;
}

.menu-title {
  font-size: $font-size-sm;
  font-weight: 600;
  color: $text-color-secondary;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: $spacing-sm;
  padding: 0 $spacing-sm;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-sm;
  border-radius: $border-radius-md;
  cursor: pointer;
  transition: all $transition-fast;
  color: $text-color-secondary;
  margin-bottom: $spacing-xs;

  &:hover {
    background-color: $bg-secondary;
    color: $text-color-primary;
  }

  &.active {
    background-color: $primary-light;
    color: white;
  }

  i {
    width: 16px;
    text-align: center;
  }
}

// 自定义滚动条样式
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: $bg-secondary;
}

.sidebar::-webkit-scrollbar-thumb {
  background: $border-color;
  border-radius: 3px;

  &:hover {
    background: $text-color-secondary;
  }
}
</style>