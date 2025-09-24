<!--
  基础图表组件
  提供统一的图表容器和基础功能
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="base-chart" :class="{ 'loading': loading }">
    <!-- 图表标题 -->
    <div v-if="title || $slots.header" class="chart-header">
      <div class="chart-title-section">
        <h3 v-if="title" class="chart-title">{{ title }}</h3>
        <p v-if="subtitle" class="chart-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.header" class="chart-actions">
        <slot name="header"></slot>
      </div>
    </div>
    
    <!-- 图表内容 -->
    <div class="chart-content" :style="{ height: height }">
      <!-- 加载状态 -->
      <div v-if="loading" class="chart-loading">
        <LoadingSpinner :size="loadingSize" :text="loadingText" />
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="chart-error">
        <EmptyState
          icon="icon-alert-triangle"
          title="图表加载失败"
          :description="error"
          :actions="[{ id: 'retry', title: '重试', icon: 'icon-refresh-cw', type: 'primary' }]"
          @action="handleRetry"
        />
      </div>
      
      <!-- 无数据状态 -->
      <div v-else-if="!hasData" class="chart-empty">
        <EmptyState
          icon="icon-bar-chart"
          title="暂无数据"
          description="当前时间范围内没有可显示的数据"
          :actions="emptyActions"
          @action="handleEmptyAction"
        />
      </div>
      
      <!-- 图表主体 -->
      <div v-else class="chart-body" ref="chartContainer">
        <slot></slot>
      </div>
    </div>
    
    <!-- 图表底部 -->
    <div v-if="$slots.footer" class="chart-footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script setup>
/**
 * 基础图表组件
 * 提供图表的通用功能和状态管理
 */
import { ref, computed, defineProps, defineEmits, onMounted, onUnmounted } from 'vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import EmptyState from '@/components/common/EmptyState.vue'

// 组件属性
const props = defineProps({
  // 图表标题
  title: {
    type: String,
    default: ''
  },
  // 图表副标题
  subtitle: {
    type: String,
    default: ''
  },
  // 图表高度
  height: {
    type: String,
    default: '300px'
  },
  // 加载状态
  loading: {
    type: Boolean,
    default: false
  },
  // 加载文本
  loadingText: {
    type: String,
    default: '加载中...'
  },
  // 加载动画尺寸
  loadingSize: {
    type: String,
    default: 'medium'
  },
  // 错误信息
  error: {
    type: String,
    default: ''
  },
  // 是否有数据
  hasData: {
    type: Boolean,
    default: true
  },
  // 空状态操作按钮
  emptyActions: {
    type: Array,
    default: () => []
  },
  // 是否自动调整大小
  autoResize: {
    type: Boolean,
    default: true
  }
})

// 组件事件
const emit = defineEmits(['retry', 'empty-action', 'resize'])

// 响应式数据
const chartContainer = ref(null)
const resizeObserver = ref(null)

// 计算属性
const containerStyle = computed(() => ({
  height: props.height
}))

/**
 * 处理重试
 */
const handleRetry = () => {
  emit('retry')
}

/**
 * 处理空状态操作
 */
const handleEmptyAction = (action) => {
  emit('empty-action', action)
}

/**
 * 处理容器大小变化
 */
const handleResize = (entries) => {
  if (entries && entries.length > 0) {
    const { width, height } = entries[0].contentRect
    emit('resize', { width, height })
  }
}

/**
 * 初始化大小监听
 */
const initResizeObserver = () => {
  if (props.autoResize && chartContainer.value && window.ResizeObserver) {
    resizeObserver.value = new ResizeObserver(handleResize)
    resizeObserver.value.observe(chartContainer.value)
  }
}

/**
 * 销毁大小监听
 */
const destroyResizeObserver = () => {
  if (resizeObserver.value) {
    resizeObserver.value.disconnect()
    resizeObserver.value = null
  }
}

// 生命周期
onMounted(() => {
  initResizeObserver()
})

onUnmounted(() => {
  destroyResizeObserver()
})

// 暴露方法给父组件
defineExpose({
  chartContainer,
  initResizeObserver,
  destroyResizeObserver
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.base-chart {
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  overflow: hidden;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
  
  &.loading {
    pointer-events: none;
  }
}

.chart-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  background: $background-color-light;
}

.chart-title-section {
  flex: 1;
  min-width: 0;
}

.chart-title {
  margin: 0 0 $spacing-xs 0;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  line-height: 1.4;
}

.chart-subtitle {
  margin: 0;
  font-size: 13px;
  color: $text-color-secondary;
  line-height: 1.4;
}

.chart-actions {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-left: $spacing-lg;
}

.chart-content {
  position: relative;
  min-height: 200px;
}

.chart-loading,
.chart-error,
.chart-empty {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-loading {
  background: rgba(255, 255, 255, 0.8);
  z-index: 10;
}

.chart-body {
  width: 100%;
  height: 100%;
  padding: $spacing-lg;
}

.chart-footer {
  padding: $spacing-md $spacing-lg;
  border-top: 1px solid $border-color-light;
  background: $background-color-light;
  font-size: 13px;
  color: $text-color-secondary;
}

// 响应式设计
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: $spacing-md;
    
    .chart-actions {
      margin-left: 0;
      width: 100%;
      justify-content: flex-end;
    }
  }
  
  .chart-body {
    padding: $spacing-md;
  }
  
  .chart-title {
    font-size: 15px;
  }
  
  .chart-subtitle {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .chart-header {
    padding: $spacing-md;
  }
  
  .chart-body {
    padding: $spacing-sm;
  }
  
  .chart-footer {
    padding: $spacing-sm $spacing-md;
  }
}
</style>