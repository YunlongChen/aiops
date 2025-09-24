<!--
  建设中页面组件
  显示系统正在建设中的提示信息
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="construction-page">
    <!-- 建设中图标 -->
    <div class="construction-icon">
      <i class="fas fa-hard-hat"></i>
    </div>
    
    <!-- 主标题 -->
    <h1 class="construction-title">系统建设中</h1>
    
    <!-- 副标题 -->
    <p class="construction-subtitle">
      我们正在努力完善这个功能，敬请期待！
    </p>
    
    <!-- 进度指示器 -->
    <div class="progress-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <span class="progress-text">{{ progress }}% 完成</span>
    </div>
    
    <!-- 预计完成时间 -->
    <div class="completion-info">
      <i class="fas fa-calendar-alt"></i>
      <span>预计完成时间：{{ estimatedCompletion }}</span>
    </div>
    
    <!-- 功能特性预览 -->
    <div class="features-preview">
      <h3>即将推出的功能</h3>
      <div class="features-grid">
        <div 
          v-for="feature in upcomingFeatures" 
          :key="feature.id"
          class="feature-card"
        >
          <div class="feature-icon">
            <i :class="feature.icon"></i>
          </div>
          <h4>{{ feature.title }}</h4>
          <p>{{ feature.description }}</p>
        </div>
      </div>
    </div>
    
    <!-- 联系信息 -->
    <div class="contact-info">
      <p>如有疑问，请联系我们：</p>
      <div class="contact-methods">
        <a href="mailto:support@aiops.com" class="contact-link">
          <i class="fas fa-envelope"></i>
          support@aiops.com
        </a>
        <a href="tel:400-123-4567" class="contact-link">
          <i class="fas fa-phone"></i>
          400-123-4567
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 建设中页面组件
 * 提供友好的建设中提示界面
 */
import { ref, onMounted, onUnmounted } from 'vue'

// 响应式数据
const progress = ref(65)
const estimatedCompletion = ref('2025年2月15日')

// 即将推出的功能
const upcomingFeatures = ref([
  {
    id: 1,
    title: '智能监控',
    description: '基于AI的系统监控和异常检测',
    icon: 'fas fa-brain'
  },
  {
    id: 2,
    title: '自动化运维',
    description: '智能化的运维操作和故障自愈',
    icon: 'fas fa-robot'
  },
  {
    id: 3,
    title: '数据分析',
    description: '深度数据分析和可视化报表',
    icon: 'fas fa-chart-line'
  },
  {
    id: 4,
    title: '告警管理',
    description: '智能告警规则和通知系统',
    icon: 'fas fa-bell'
  }
])

// 进度条动画
let progressInterval = null

/**
 * 启动进度条动画
 */
const startProgressAnimation = () => {
  progressInterval = setInterval(() => {
    if (progress.value < 100) {
      progress.value += Math.random() * 2
      if (progress.value > 100) {
        progress.value = 100
      }
    } else {
      // 重置进度
      setTimeout(() => {
        progress.value = 65
      }, 2000)
    }
  }, 3000)
}

/**
 * 停止进度条动画
 */
const stopProgressAnimation = () => {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

// 生命周期钩子
onMounted(() => {
  startProgressAnimation()
})

onUnmounted(() => {
  stopProgressAnimation()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.construction-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: $spacing-2xl;
  text-align: center;
}

/* 建设中图标 */
.construction-icon {
  margin-bottom: $spacing-xl;
  
  i {
    font-size: 4rem;
    color: $warning-color;
    animation: bounce 2s infinite;
  }
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

/* 标题样式 */
.construction-title {
  font-size: $font-size-3xl;
  font-weight: $font-weight-bold;
  color: $text-color-primary;
  margin-bottom: $spacing-md;
}

.construction-subtitle {
  font-size: $font-size-lg;
  color: $text-color-secondary;
  margin-bottom: $spacing-2xl;
  max-width: 500px;
}

/* 进度指示器 */
.progress-container {
  width: 100%;
  max-width: 400px;
  margin-bottom: $spacing-xl;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: $neutral-200;
  border-radius: $border-radius-full;
  overflow: hidden;
  margin-bottom: $spacing-sm;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, $primary-color, $primary-light);
  border-radius: $border-radius-full;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: $font-size-sm;
  color: $text-color-secondary;
  font-weight: $font-weight-medium;
}

/* 完成时间信息 */
.completion-info {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-2xl;
  padding: $spacing-md $spacing-lg;
  background: $bg-tertiary;
  border-radius: $border-radius-lg;
  color: $text-color-secondary;
  
  i {
    color: $info-color;
  }
}

/* 功能特性预览 */
.features-preview {
  width: 100%;
  max-width: 800px;
  margin-bottom: $spacing-2xl;
  
  h3 {
    font-size: $font-size-xl;
    font-weight: $font-weight-semibold;
    color: $text-color-primary;
    margin-bottom: $spacing-lg;
  }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-lg;
}

.feature-card {
  padding: $spacing-lg;
  background: $bg-primary;
  border: 1px solid $border-color;
  border-radius: $border-radius-lg;
  transition: all $transition-fast;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: $shadow-md;
    border-color: $primary-light;
  }
}

.feature-icon {
  margin-bottom: $spacing-md;
  
  i {
    font-size: 2rem;
    color: $primary-color;
  }
}

.feature-card h4 {
  font-size: $font-size-lg;
  font-weight: $font-weight-semibold;
  color: $text-color-primary;
  margin-bottom: $spacing-sm;
}

.feature-card p {
  font-size: $font-size-sm;
  color: $text-color-secondary;
  line-height: $line-height-relaxed;
}

/* 联系信息 */
.contact-info {
  text-align: center;
  
  p {
    font-size: $font-size-base;
    color: $text-color-secondary;
    margin-bottom: $spacing-md;
  }
}

.contact-methods {
  display: flex;
  gap: $spacing-lg;
  justify-content: center;
  flex-wrap: wrap;
}

.contact-link {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-sm $spacing-md;
  color: $primary-color;
  text-decoration: none;
  border: 1px solid $primary-color;
  border-radius: $border-radius-md;
  transition: all $transition-fast;
  
  &:hover {
    background: $primary-color;
    color: white;
  }
  
  i {
    font-size: $font-size-sm;
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .construction-page {
    padding: $spacing-lg;
  }
  
  .construction-title {
    font-size: $font-size-2xl;
  }
  
  .construction-subtitle {
    font-size: $font-size-base;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .contact-methods {
    flex-direction: column;
    align-items: center;
  }
}
</style>