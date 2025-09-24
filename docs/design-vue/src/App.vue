<!--
  Vue应用根组件 - AIOps智能运维平台
  使用动态路由结构和组件化布局
  
  @author AI Assistant
  @version 2.0.0
  @date 2025-01-24
-->

<template>
  <div id="app">
    <app-layout/>
    <!-- 路由视图 - 动态加载页面组件 -->
  </div>
</template>

<script setup>
/**
 * Vue应用根组件逻辑
 * 处理全局状态和应用初始化
 */

import {onMounted} from 'vue'
import AppLayout from "@components/layout/AppLayout.vue";

/**
 * 组件挂载时的初始化操作
 */
onMounted(() => {
  // 初始化应用配置
  initializeApp()
})

/**
 * 初始化应用配置
 * 设置全局样式和主题
 */
function initializeApp() {
  // 设置应用主题
  document.documentElement.setAttribute('data-theme', 'light')

  // 初始化全局配置
  console.log('AIOps Platform initialized')
}
</script>

<style lang="scss">
/**
 * 全局样式 - 完整迁移原始模板样式
 * 保持与原始设计完全一致的样式规范
 */

@import "@/assets/styles/variables.scss";

/* 全局重置和基础样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-size: 1rem;
  line-height: 1.5;
  color: $text-color-primary;
  background-color: $bg-secondary;
  overflow-x: hidden;
}

#app {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

/* 顶部导航栏 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: $bg-primary;
  border-bottom: 1px solid $border-color-light;
  box-shadow: $shadow-sm;
  z-index: 1000;
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 $spacing-md;
  max-width: 100%;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-weight: 600;
  font-size: 1.125rem;
  color: $primary-color;
}

.nav-brand i {
  font-size: 1.25rem;
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
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-md;
  cursor: pointer;
  transition: all $transition-fast;
  color: $text-color-secondary;
  font-weight: 500;
}

.nav-item a {
  color: inherit;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  width: 100%;
}

.nav-item a:hover,
.nav-item a:focus,
.nav-item a:visited {
  color: inherit;
  text-decoration: none;
}

.nav-item:hover {
  background-color: $bg-tertiary;
  color: $text-color-primary;
}

.nav-item.active {
  background-color: $primary-color;
  color: white;
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
}

.user-info:hover {
  background-color: $bg-tertiary;
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

/* 侧边栏 */
.sidebar {
  position: fixed;
  top: 64px;
  left: 0;
  width: 280px;
  height: calc(100vh - 64px);
  background: $bg-primary;
  border-right: 1px solid $border-color-light;
  overflow-y: auto;
  z-index: 900;
}

.sidebar-header {
  padding: $spacing-md $spacing-md $spacing-sm;
  border-bottom: 1px solid $border-color-light;
}

.sidebar-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: $text-color-primary;
}

.sidebar-menu {
  padding: $spacing-sm;
}

.menu-group {
  margin-bottom: $spacing-md;
}

.menu-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: $text-color-tertiary;
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
}

.menu-item:hover {
  background-color: $bg-tertiary;
  color: $text-color-primary;
}

.menu-item.active {
  background-color: $primary-color;
  color: white;
}

.menu-item i {
  width: 16px;
  text-align: center;
}

/* 主内容区域 */
.main-content {
  margin-top: 64px;
  min-height: calc(100vh - 64px);
  padding: $spacing-md;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: $spacing-md;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.breadcrumb-item {
  color: $text-color-tertiary;
  font-size: 0.875rem;
}

.breadcrumb-item.active {
  color: $text-color-primary;
  font-weight: 600;
  font-size: 1.5rem;
}

.header-actions {
  display: flex;
  gap: $spacing-sm;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-sm;
  border: none;
  border-radius: $border-radius-md;
  font-weight: 500;
  cursor: pointer;
  transition: all $transition-fast;
  text-decoration: none;
}

.btn-primary {
  background-color: $primary-color;
  color: white;
}

.btn-primary:hover {
  background-color: darken($primary-color, 10%);
}

.btn-secondary {
  background-color: $bg-tertiary;
  color: $text-color-primary;
  border: 1px solid $border-color-light;
}

.btn-secondary:hover {
  background-color: $bg-secondary;
  color: $text-color-primary;
}

.page-container {
  background: $bg-primary;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-md;
  border: 1px solid $border-color-light;
  overflow: hidden;
  min-height: 500px;
}

/* 建设中占位样式 */
.construction-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 500px;
  padding: $spacing-lg;
}

.construction-content {
  text-align: center;
  color: $text-color-tertiary;
}

.construction-icon {
  font-size: 4rem;
  margin-bottom: $spacing-md;
  color: $warning-color;
}

.construction-content h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: $spacing-sm;
  color: $text-color-primary;
}

.construction-content p {
  font-size: 1rem;
  color: $text-color-secondary;
}
</style>