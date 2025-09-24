<!--
  状态徽章组件
  用于显示各种状态信息
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <span 
    class="status-badge" 
    :class="[
      `status-${status}`,
      `size-${size}`,
      { 'with-icon': showIcon, 'dot': variant === 'dot' }
    ]"
  >
    <i v-if="showIcon && icon" :class="icon" class="status-icon"></i>
    <span v-if="variant !== 'dot'" class="status-text">{{ text }}</span>
  </span>
</template>

<script setup>
/**
 * 状态徽章组件
 * 支持多种状态类型和显示样式
 */
import { computed, defineProps } from 'vue'

// 组件属性
const props = defineProps({
  // 状态类型
  status: {
    type: String,
    default: 'default',
    validator: (value) => [
      'default', 'primary', 'success', 'warning', 'danger', 'info',
      'online', 'offline', 'running', 'stopped', 'pending', 'error'
    ].includes(value)
  },
  // 显示文本
  text: {
    type: String,
    default: ''
  },
  // 图标
  icon: {
    type: String,
    default: ''
  },
  // 是否显示图标
  showIcon: {
    type: Boolean,
    default: false
  },
  // 尺寸
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 变体样式
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'dot'].includes(value)
  }
})

// 计算默认图标
const defaultIcon = computed(() => {
  const iconMap = {
    success: 'icon-check-circle',
    warning: 'icon-alert-triangle',
    danger: 'icon-x-circle',
    error: 'icon-x-circle',
    info: 'icon-info',
    online: 'icon-wifi',
    offline: 'icon-wifi-off',
    running: 'icon-play-circle',
    stopped: 'icon-stop-circle',
    pending: 'icon-clock'
  }
  return iconMap[props.status] || 'icon-circle'
})

// 实际使用的图标
const actualIcon = computed(() => props.icon || defaultIcon.value)
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  font-weight: 500;
  line-height: 1.2;
  white-space: nowrap;
  
  // 尺寸变体
  &.size-small {
    padding: 1px 6px;
    font-size: 11px;
    border-radius: 8px;
    
    .status-icon {
      font-size: 10px;
    }
    
    &.dot {
      width: 6px;
      height: 6px;
      padding: 0;
      border-radius: 50%;
    }
  }
  
  &.size-medium {
    padding: 2px 8px;
    font-size: 12px;
    
    .status-icon {
      font-size: 12px;
    }
    
    &.dot {
      width: 8px;
      height: 8px;
      padding: 0;
      border-radius: 50%;
    }
  }
  
  &.size-large {
    padding: 4px 12px;
    font-size: 14px;
    border-radius: 16px;
    
    .status-icon {
      font-size: 14px;
    }
    
    &.dot {
      width: 10px;
      height: 10px;
      padding: 0;
      border-radius: 50%;
    }
  }
  
  // 状态颜色
  &.status-default {
    background: $background-light;
    color: $text-color-secondary;
    border: 1px solid $border-color;
  }
  
  &.status-primary {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
    border: 1px solid rgba($primary-color, 0.2);
    
    &.dot {
      background: $primary-color;
      border-color: $primary-color;
    }
  }
  
  &.status-success,
  &.status-online,
  &.status-running {
    background: rgba($success-color, 0.1);
    color: $success-color;
    border: 1px solid rgba($success-color, 0.2);
    
    &.dot {
      background: $success-color;
      border-color: $success-color;
    }
  }
  
  &.status-warning,
  &.status-pending {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
    border: 1px solid rgba($warning-color, 0.2);
    
    &.dot {
      background: $warning-color;
      border-color: $warning-color;
    }
  }
  
  &.status-danger,
  &.status-error,
  &.status-offline,
  &.status-stopped {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
    border: 1px solid rgba($danger-color, 0.2);
    
    &.dot {
      background: $danger-color;
      border-color: $danger-color;
    }
  }
  
  &.status-info {
    background: rgba($info-color, 0.1);
    color: $info-color;
    border: 1px solid rgba($info-color, 0.2);
    
    &.dot {
      background: $info-color;
      border-color: $info-color;
    }
  }
}

.status-icon {
  flex-shrink: 0;
}

.status-text {
  flex-shrink: 0;
}

// 点状变体的特殊样式
.status-badge.dot {
  min-width: auto;
  border-radius: 50%;
  
  .status-icon,
  .status-text {
    display: none;
  }
}

// 动画效果（可选）
.status-badge {
  transition: all 0.2s ease;
  
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
}

// 脉冲动画（用于在线状态等）
.status-badge.status-online.dot,
.status-badge.status-running.dot {
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 50%;
    background: currentColor;
    opacity: 0.3;
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 0.3;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.1;
  }
  100% {
    transform: scale(1);
    opacity: 0.3;
  }
}
</style>