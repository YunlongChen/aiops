<!--
  空状态组件
  用于显示无数据或空内容的状态
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="empty-state" :class="[`size-${size}`, { 'centered': centered }]">
    <div class="empty-content">
      <!-- 图标或图片 -->
      <div class="empty-icon" v-if="icon || image">
        <img v-if="image" :src="image" :alt="title" class="empty-image" />
        <i v-else-if="icon" :class="icon" class="empty-icon-svg"></i>
      </div>
      
      <!-- 标题 -->
      <h3 v-if="title" class="empty-title">{{ title }}</h3>
      
      <!-- 描述 -->
      <p v-if="description" class="empty-description">{{ description }}</p>
      
      <!-- 操作按钮 -->
      <div v-if="$slots.actions || actions.length > 0" class="empty-actions">
        <slot name="actions">
          <button
            v-for="action in actions"
            :key="action.id"
            class="empty-action-btn"
            :class="action.type || 'primary'"
            @click="handleAction(action)"
            :disabled="action.disabled"
          >
            <i v-if="action.icon" :class="action.icon"></i>
            {{ action.title }}
          </button>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 空状态组件
 * 提供统一的空状态显示
 */
import { defineProps, defineEmits } from 'vue'

// 组件属性
const props = defineProps({
  // 图标类名
  icon: {
    type: String,
    default: 'icon-inbox'
  },
  // 图片地址
  image: {
    type: String,
    default: ''
  },
  // 标题
  title: {
    type: String,
    default: '暂无数据'
  },
  // 描述
  description: {
    type: String,
    default: '当前没有可显示的内容'
  },
  // 尺寸
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  // 是否居中显示
  centered: {
    type: Boolean,
    default: true
  },
  // 操作按钮
  actions: {
    type: Array,
    default: () => []
  }
})

// 组件事件
const emit = defineEmits(['action'])

/**
 * 处理操作按钮点击
 */
const handleAction = (action) => {
  emit('action', action)
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-xl;
  
  &.centered {
    min-height: 300px;
  }
  
  &.size-small {
    padding: $spacing-lg;
    
    .empty-icon {
      width: 48px;
      height: 48px;
      margin-bottom: $spacing-md;
    }
    
    .empty-title {
      font-size: 16px;
      margin-bottom: $spacing-sm;
    }
    
    .empty-description {
      font-size: 13px;
      margin-bottom: $spacing-md;
    }
  }
  
  &.size-medium {
    .empty-icon {
      width: 64px;
      height: 64px;
      margin-bottom: $spacing-lg;
    }
    
    .empty-title {
      font-size: 18px;
      margin-bottom: $spacing-md;
    }
    
    .empty-description {
      font-size: 14px;
      margin-bottom: $spacing-lg;
    }
  }
  
  &.size-large {
    .empty-icon {
      width: 80px;
      height: 80px;
      margin-bottom: $spacing-xl;
    }
    
    .empty-title {
      font-size: 20px;
      margin-bottom: $spacing-lg;
    }
    
    .empty-description {
      font-size: 16px;
      margin-bottom: $spacing-xl;
    }
  }
}

.empty-content {
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  background: $background-color-light;
  border-radius: 50%;
  
  .empty-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  .empty-icon-svg {
    font-size: 32px;
    color: $text-color-placeholder;
  }
}

.empty-title {
  margin: 0;
  color: $text-color;
  font-weight: 600;
  line-height: 1.4;
}

.empty-description {
  margin: 0;
  color: $text-color-secondary;
  line-height: 1.5;
}

.empty-actions {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-sm;
  justify-content: center;
}

.empty-action-btn {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-sm $spacing-lg;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  background: $white;
  color: $text-color;
  font-size: 14px;
  font-weight: 500;
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
  .empty-state {
    padding: $spacing-lg;
    
    &.size-large {
      .empty-icon {
        width: 64px;
        height: 64px;
      }
      
      .empty-title {
        font-size: 18px;
      }
      
      .empty-description {
        font-size: 14px;
      }
    }
  }
  
  .empty-actions {
    flex-direction: column;
    align-items: stretch;
    
    .empty-action-btn {
      justify-content: center;
    }
  }
}
</style>