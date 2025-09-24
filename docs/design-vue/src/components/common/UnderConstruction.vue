<!--
  通用"建设中"组件
  用于显示尚未完成开发的页面占位内容
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="under-construction">
    <div class="construction-container">
      <!-- 图标区域 -->
      <div class="construction-icon">
        <i class="fas fa-hard-hat"></i>
      </div>
      
      <!-- 主要内容 -->
      <div class="construction-content">
        <h2 class="construction-title">{{ title || '页面建设中' }}</h2>
        <p class="construction-description">
          {{ description || '该功能正在紧张开发中，敬请期待！' }}
        </p>
        
        <!-- 进度指示器 -->
        <div class="construction-progress" v-if="showProgress">
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
          </div>
          <span class="progress-text">{{ progress }}% 完成</span>
        </div>
        
        <!-- 预计完成时间 -->
        <div class="construction-eta" v-if="eta">
          <i class="fas fa-clock"></i>
          <span>预计完成时间：{{ eta }}</span>
        </div>
        
        <!-- 操作按钮 -->
        <div class="construction-actions" v-if="showActions">
          <button class="btn btn-primary" @click="goBack">
            <i class="fas fa-arrow-left"></i>
            返回上一页
          </button>
          <button class="btn btn-secondary" @click="goHome">
            <i class="fas fa-home"></i>
            返回首页
          </button>
        </div>
      </div>
      
      <!-- 装饰元素 -->
      <div class="construction-decoration">
        <div class="cone cone-1"></div>
        <div class="cone cone-2"></div>
        <div class="cone cone-3"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 建设中组件的脚本逻辑
 */
import { useRouter } from 'vue-router'

// 定义组件属性
const props = defineProps({
  // 页面标题
  title: {
    type: String,
    default: '页面建设中'
  },
  // 描述信息
  description: {
    type: String,
    default: '该功能正在紧张开发中，敬请期待！'
  },
  // 是否显示进度条
  showProgress: {
    type: Boolean,
    default: false
  },
  // 进度百分比
  progress: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  // 预计完成时间
  eta: {
    type: String,
    default: ''
  },
  // 是否显示操作按钮
  showActions: {
    type: Boolean,
    default: true
  }
})

const router = useRouter()

/**
 * 返回上一页
 */
const goBack = () => {
  router.go(-1)
}

/**
 * 返回首页
 */
const goHome = () => {
  router.push('/')
}
</script>

<style lang="scss" scoped>
.under-construction {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  
  .construction-container {
    position: relative;
    text-align: center;
    max-width: 600px;
    padding: 3rem;
    background: white;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    
    .construction-icon {
      margin-bottom: 2rem;
      
      i {
        font-size: 4rem;
        color: #ff9800;
        animation: bounce 2s infinite;
      }
    }
    
    .construction-content {
      .construction-title {
        font-size: 2rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
      }
      
      .construction-description {
        font-size: 1.1rem;
        color: #7f8c8d;
        margin-bottom: 2rem;
        line-height: 1.6;
      }
      
      .construction-progress {
        margin-bottom: 2rem;
        
        .progress-bar {
          width: 100%;
          height: 8px;
          background: #ecf0f1;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 0.5rem;
          
          .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 4px;
            transition: width 0.3s ease;
            animation: shimmer 2s infinite;
          }
        }
        
        .progress-text {
          font-size: 0.9rem;
          color: #7f8c8d;
          font-weight: 500;
        }
      }
      
      .construction-eta {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 2rem;
        color: #7f8c8d;
        font-size: 0.95rem;
        
        i {
          color: #3498db;
        }
      }
      
      .construction-actions {
        display: flex;
        gap: 1rem;
        justify-content: center;
        flex-wrap: wrap;
        
        .btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-size: 0.95rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          gap: 0.5rem;
          
          &.btn-primary {
            background: #3498db;
            color: white;
            
            &:hover {
              background: #2980b9;
              transform: translateY(-2px);
            }
          }
          
          &.btn-secondary {
            background: #95a5a6;
            color: white;
            
            &:hover {
              background: #7f8c8d;
              transform: translateY(-2px);
            }
          }
        }
      }
    }
    
    .construction-decoration {
      position: absolute;
      top: -20px;
      right: -20px;
      
      .cone {
        position: absolute;
        width: 0;
        height: 0;
        
        &.cone-1 {
          border-left: 15px solid transparent;
          border-right: 15px solid transparent;
          border-bottom: 25px solid #ff9800;
          top: 0;
          right: 0;
          animation: float 3s ease-in-out infinite;
        }
        
        &.cone-2 {
          border-left: 10px solid transparent;
          border-right: 10px solid transparent;
          border-bottom: 18px solid #f39c12;
          top: 30px;
          right: 40px;
          animation: float 3s ease-in-out infinite 0.5s;
        }
        
        &.cone-3 {
          border-left: 8px solid transparent;
          border-right: 8px solid transparent;
          border-bottom: 14px solid #e67e22;
          top: 60px;
          right: 20px;
          animation: float 3s ease-in-out infinite 1s;
        }
      }
    }
  }
}

// 动画效果
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

@keyframes shimmer {
  0% {
    background-position: -200px 0;
  }
  100% {
    background-position: calc(200px + 100%) 0;
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .under-construction {
    padding: 1rem;
    
    .construction-container {
      padding: 2rem 1.5rem;
      
      .construction-content {
        .construction-title {
          font-size: 1.5rem;
        }
        
        .construction-description {
          font-size: 1rem;
        }
        
        .construction-actions {
          flex-direction: column;
          
          .btn {
            width: 100%;
            justify-content: center;
          }
        }
      }
    }
  }
}
</style>