<!--
  正在建设中页面
  用于未实现功能的占位页面
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="under-construction">
    <div class="construction-container">
      <!-- 图标区域 -->
      <div class="construction-icon">
        <div class="icon-wrapper">
          <i class="icon-tool"></i>
          <div class="construction-dots">
            <span class="dot dot-1"></span>
            <span class="dot dot-2"></span>
            <span class="dot dot-3"></span>
          </div>
        </div>
      </div>
      
      <!-- 内容区域 -->
      <div class="construction-content">
        <h1 class="construction-title">{{ title || '功能建设中' }}</h1>
        <p class="construction-description">
          {{ description || '该功能正在紧张开发中，敬请期待！' }}
        </p>
        
        <!-- 进度条 -->
        <div class="construction-progress">
          <div class="progress-label">开发进度</div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: progress + '%' }"
            ></div>
          </div>
          <div class="progress-text">{{ progress }}%</div>
        </div>
        
        <!-- 预计完成时间 -->
        <div class="construction-timeline" v-if="estimatedDate">
          <div class="timeline-item">
            <i class="icon-calendar"></i>
            <span>预计完成时间：{{ estimatedDate }}</span>
          </div>
        </div>
        
        <!-- 功能特性预览 -->
        <div class="construction-features" v-if="features && features.length > 0">
          <h3 class="features-title">即将推出的功能</h3>
          <div class="features-list">
            <div 
              v-for="(feature, index) in features" 
              :key="index"
              class="feature-item"
            >
              <i class="icon-check-circle"></i>
              <span>{{ feature }}</span>
            </div>
          </div>
        </div>
        
        <!-- 操作按钮 -->
        <div class="construction-actions">
          <button class="btn btn-primary" @click="goBack">
            <i class="icon-arrow-left"></i>
            返回上一页
          </button>
          <button class="btn btn-outline" @click="goHome">
            <i class="icon-home"></i>
            返回首页
          </button>
        </div>
        
        <!-- 联系信息 -->
        <div class="construction-contact">
          <p class="contact-text">
            如有疑问或建议，请联系我们：
            <a href="mailto:support@aiops.com" class="contact-link">
              support@aiops.com
            </a>
          </p>
        </div>
      </div>
    </div>
    
    <!-- 背景装饰 -->
    <div class="construction-bg">
      <div class="bg-shape shape-1"></div>
      <div class="bg-shape shape-2"></div>
      <div class="bg-shape shape-3"></div>
    </div>
  </div>
</template>

<script setup>
/**
 * 正在建设中页面组件
 * 用于未实现功能的占位页面
 */
import { defineProps } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 组件属性
const props = defineProps({
  title: {
    type: String,
    default: '功能建设中'
  },
  description: {
    type: String,
    default: '该功能正在紧张开发中，敬请期待！'
  },
  progress: {
    type: Number,
    default: 65,
    validator: (value) => value >= 0 && value <= 100
  },
  estimatedDate: {
    type: String,
    default: '2025年3月'
  },
  features: {
    type: Array,
    default: () => [
      '直观的用户界面设计',
      '实时数据监控和分析',
      '智能告警和通知系统',
      '完善的权限管理机制',
      '丰富的数据可视化图表'
    ]
  }
})

/**
 * 返回上一页
 */
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}

/**
 * 返回首页
 */
const goHome = () => {
  router.push('/')
}
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.under-construction {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-lg;
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.construction-container {
  max-width: 600px;
  width: 100%;
  text-align: center;
  position: relative;
  z-index: 2;
}

// 图标区域
.construction-icon {
  margin-bottom: $spacing-xl;
}

.icon-wrapper {
  position: relative;
  display: inline-block;
}

.icon-wrapper > i {
  font-size: 80px;
  color: $white;
  opacity: 0.9;
  animation: bounce 2s infinite;
}

.construction-dots {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $white;
  opacity: 0.7;
  animation: pulse 1.5s infinite;
  
  &.dot-1 {
    animation-delay: 0s;
  }
  
  &.dot-2 {
    animation-delay: 0.5s;
  }
  
  &.dot-3 {
    animation-delay: 1s;
  }
}

// 内容区域
.construction-content {
  background: $white;
  border-radius: $border-radius-xl;
  padding: $spacing-xl;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.construction-title {
  margin: 0 0 $spacing-md 0;
  font-size: 32px;
  font-weight: 700;
  color: $text-color;
  background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.construction-description {
  margin: 0 0 $spacing-xl 0;
  font-size: 16px;
  color: $text-color-secondary;
  line-height: 1.6;
}

// 进度条
.construction-progress {
  margin-bottom: $spacing-xl;
}

.progress-label {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
  margin-bottom: $spacing-sm;
  text-align: left;
}

.progress-bar {
  height: 8px;
  background: $border-color-light;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: $spacing-xs;
  position: relative;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 4px;
  transition: width 0.8s ease;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
    animation: shimmer 2s infinite;
  }
}

.progress-text {
  font-size: 13px;
  font-weight: 500;
  color: $text-color-secondary;
  text-align: right;
}

// 时间线
.construction-timeline {
  margin-bottom: $spacing-xl;
}

.timeline-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  font-size: 14px;
  color: $text-color-secondary;
  
  i {
    color: $primary-color;
  }
}

// 功能特性
.construction-features {
  margin-bottom: $spacing-xl;
  text-align: left;
}

.features-title {
  margin: 0 0 $spacing-md 0;
  font-size: 18px;
  font-weight: 600;
  color: $text-color;
  text-align: center;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: 14px;
  color: $text-color-secondary;
  
  i {
    color: $success-color;
    font-size: 16px;
  }
}

// 操作按钮
.construction-actions {
  display: flex;
  gap: $spacing-md;
  justify-content: center;
  margin-bottom: $spacing-lg;
}

// 联系信息
.construction-contact {
  padding-top: $spacing-lg;
  border-top: 1px solid $border-color-light;
}

.contact-text {
  margin: 0;
  font-size: 13px;
  color: $text-color-light;
}

.contact-link {
  color: $primary-color;
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
    text-decoration: underline;
  }
}

// 背景装饰
.construction-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
  
  &.shape-1 {
    width: 200px;
    height: 200px;
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }
  
  &.shape-2 {
    width: 150px;
    height: 150px;
    top: 60%;
    right: 15%;
    animation-delay: 2s;
  }
  
  &.shape-3 {
    width: 100px;
    height: 100px;
    bottom: 20%;
    left: 20%;
    animation-delay: 4s;
  }
}

// 动画
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

@keyframes pulse {
  0%, 100% {
    opacity: 0.7;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  33% {
    transform: translateY(-20px) rotate(120deg);
  }
  66% {
    transform: translateY(10px) rotate(240deg);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .under-construction {
    padding: $spacing-md;
  }
  
  .construction-content {
    padding: $spacing-lg;
  }
  
  .construction-title {
    font-size: 28px;
  }
  
  .construction-description {
    font-size: 15px;
  }
  
  .icon-wrapper > i {
    font-size: 60px;
  }
  
  .construction-actions {
    flex-direction: column;
    align-items: center;
    
    .btn {
      width: 100%;
      max-width: 200px;
    }
  }
}

@media (max-width: 480px) {
  .construction-title {
    font-size: 24px;
  }
  
  .construction-description {
    font-size: 14px;
  }
  
  .icon-wrapper > i {
    font-size: 50px;
  }
  
  .construction-content {
    padding: $spacing-md;
  }
  
  .bg-shape {
    &.shape-1 {
      width: 120px;
      height: 120px;
    }
    
    &.shape-2 {
      width: 80px;
      height: 80px;
    }
    
    &.shape-3 {
      width: 60px;
      height: 60px;
    }
  }
}
</style>