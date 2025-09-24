<!--
  应用主布局组件
  包含顶部导航栏、侧边栏和主内容区域
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="app-layout">
    <!-- 顶部导航栏 -->
    <AppHeader/>
    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 内容头部 -->
      <div class="content-header">
        <!-- 面包屑导航 -->
        <AppBreadcrumb/>

        <!-- 页面操作按钮 -->
        <div class="page-actions">
          <button class="btn btn-secondary">
            <i class="fas fa-download"></i>
            导出数据
          </button>
          <button class="btn btn-primary">
            <i class="fas fa-plus"></i>
            新建项目
          </button>
        </div>
      </div>

      <!-- 页面内容 -->
      <div class="page-content">
        <router-view/>
      </div>
    </main>
  </div>
</template>

<script setup>
/**
 * 应用主布局组件
 * 提供整体页面布局结构
 */
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import AppBreadcrumb from './AppBreadcrumb.vue'
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.app-layout {
  min-height: 100vh;
  background: $bg-secondary;
}

/* 主内容区域 */
.main-content {
  margin-left: 280px;
  margin-top: 64px;
  min-height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
}

/* 内容头部 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg $spacing-xl;
  background: $bg-primary;
  border-bottom: 1px solid $border-color;
  min-height: 72px;
}

/* 页面操作按钮 */
.page-actions {
  display: flex;
  gap: $spacing-sm;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-md;
  border: none;
  border-radius: $border-radius-md;
  font-size: $font-size-sm;
  font-weight: 500;
  cursor: pointer;
  transition: all $transition-fast;
  text-decoration: none;

  &.btn-primary {
    background: $primary-color;
    color: white;

    &:hover {
      background: $primary-dark;
    }
  }

  &.btn-secondary {
    background: $bg-secondary;
    color: $text-color-primary;
    border: 1px solid $border-color;

    &:hover {
      background: $neutral-100;
      border-color: $neutral-300;
    }
  }

  i {
    font-size: 14px;
  }
}

/* 页面内容 */
.page-content {
  flex: 1;
  padding: $spacing-xl;
  overflow-y: auto;
}

// 响应式设计
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }

  .content-header {
    padding: $spacing-md;
    flex-direction: column;
    gap: $spacing-md;
    align-items: stretch;
  }

  .page-actions {
    justify-content: center;
  }

  .page-content {
    padding: $spacing-xs;
  }
}
</style>