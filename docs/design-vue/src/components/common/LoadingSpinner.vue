<!--
  加载动画组件
  提供统一的加载状态显示
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="loading-spinner" :class="{ 'overlay': overlay, [`size-${size}`]: true }">
    <div class="spinner-container">
      <div class="spinner" :class="type">
        <div v-if="type === 'dots'" class="dot" v-for="i in 3" :key="i"></div>
        <div v-else-if="type === 'pulse'" class="pulse"></div>
        <div v-else-if="type === 'ring'" class="ring">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
        <div v-else class="default-spinner"></div>
      </div>
      <div v-if="text" class="loading-text">{{ text }}</div>
    </div>
  </div>
</template>

<script setup>
/**
 * 加载动画组件
 * 支持多种动画类型和尺寸
 */
import { defineProps } from 'vue'

// 组件属性
const props = defineProps({
  // 动画类型
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'dots', 'pulse', 'ring'].includes(value)
  },
  // 尺寸
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 加载文本
  text: {
    type: String,
    default: ''
  },
  // 是否显示遮罩层
  overlay: {
    type: Boolean,
    default: false
  }
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.8);
    z-index: 9999;
    backdrop-filter: blur(2px);
  }
  
  &.size-small {
    .spinner {
      width: 20px;
      height: 20px;
    }
    
    .loading-text {
      font-size: 12px;
      margin-top: $spacing-xs;
    }
  }
  
  &.size-medium {
    .spinner {
      width: 32px;
      height: 32px;
    }
    
    .loading-text {
      font-size: 14px;
      margin-top: $spacing-sm;
    }
  }
  
  &.size-large {
    .spinner {
      width: 48px;
      height: 48px;
    }
    
    .loading-text {
      font-size: 16px;
      margin-top: $spacing-md;
    }
  }
}

.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.spinner {
  position: relative;
  
  // 默认旋转动画
  &.default .default-spinner {
    width: 100%;
    height: 100%;
    border: 3px solid $border-color-light;
    border-top: 3px solid $primary-color;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  // 点状动画
  &.dots {
    display: flex;
    gap: 4px;
    
    .dot {
      width: 6px;
      height: 6px;
      background: $primary-color;
      border-radius: 50%;
      animation: dots 1.4s ease-in-out infinite both;
      
      &:nth-child(1) { animation-delay: -0.32s; }
      &:nth-child(2) { animation-delay: -0.16s; }
      &:nth-child(3) { animation-delay: 0s; }
    }
  }
  
  // 脉冲动画
  &.pulse .pulse {
    width: 100%;
    height: 100%;
    background: $primary-color;
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }
  
  // 环形动画
  &.ring {
    display: inline-block;
    position: relative;
    
    div {
      box-sizing: border-box;
      display: block;
      position: absolute;
      width: 100%;
      height: 100%;
      border: 3px solid $primary-color;
      border-radius: 50%;
      animation: ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
      border-color: $primary-color transparent transparent transparent;
      
      &:nth-child(1) { animation-delay: -0.45s; }
      &:nth-child(2) { animation-delay: -0.3s; }
      &:nth-child(3) { animation-delay: -0.15s; }
    }
  }
}

.loading-text {
  color: $text-color-secondary;
  font-weight: 500;
  text-align: center;
}

// 动画定义
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes dots {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes pulse {
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 0;
  }
}

@keyframes ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>