<!--
  应用顶部导航栏组件
  包含品牌标识、导航菜单和用户信息
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <nav class="navbar">
    <div class="nav-container">
      <!-- 品牌标识 -->
      <div class="nav-brand">
        <i class="fas fa-robot"></i>
        <span>AIOps Platform</span>
      </div>

      <!-- 导航菜单 -->
      <div class="nav-menu">
        <router-link
            v-for="item in navigationItems"
            :key="item.name"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.name === item.name }"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </router-link>
      </div>

      <!-- 用户信息 -->
      <div class="nav-user">
        <div class="user-info">
          <img src="@/assets/images/user-avatar.svg" alt="用户头像" class="user-avatar">
          <span class="user-name">管理员</span>
          <i class="fas fa-chevron-down"></i>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
/**
 * 应用顶部导航栏组件
 * 提供主要的导航功能和用户信息显示
 */
import {computed} from 'vue'
import {useRoute} from 'vue-router'

const route = useRoute()

// 导航菜单项
const navigationItems = [
  {name: 'dashboard', path: '/', label: '仪表板', icon: 'fas fa-tachometer-alt'},
  {name: 'monitoring', path: '/monitoring', label: '监控中心', icon: 'fas fa-chart-line'},
  {name: 'ai-engine', path: '/ai-engine', label: 'AI引擎', icon: 'fas fa-brain'},
  {name: 'alerting', path: '/alerting', label: '告警管理', icon: 'fas fa-bell'},
  {name: 'self-healing', path: '/self-healing', label: '自愈系统', icon: 'fas fa-magic'},
  {name: 'settings', path: '/settings', label: '系统设置', icon: 'fas fa-cog'}
]
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

/* 顶部导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: $bg-primary;
  border-bottom: 1px solid $border-color;
  box-shadow: $shadow-light;
  z-index: 1000;
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 $spacing-lg;
  max-width: 100%;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-weight: 600;
  font-size: $font-size-lg;
  color: $primary-color;

  i {
    font-size: $font-size-xl;
  }
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-md;
  border-radius: $border-radius-md;
  cursor: pointer;
  transition: all $transition-fast;
  color: $text-color-secondary;
  font-weight: 500;
  text-decoration: none;

  &:hover {
    background-color: $bg-secondary;
    color: $text-color-primary;
  }

  &.active {
    background-color: $primary-color;
    color: white;
  }

  i {
    width: 16px;
    text-align: center;
  }
}

.nav-user {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-md;
  cursor: pointer;
  transition: background-color $transition-fast;

  &:hover {
    background-color: $bg-secondary;
  }
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
}

.user-name {
  font-weight: 500;
  color: $text-color-primary;
}
</style>