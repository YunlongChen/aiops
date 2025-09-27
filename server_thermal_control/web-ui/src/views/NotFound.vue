<template>
  <div class="not-found">
    <div class="not-found-container">
      <!-- 404图标 -->
      <div class="error-icon">
        <el-icon><WarningFilled /></el-icon>
      </div>

      <!-- 错误信息 -->
      <div class="error-content">
        <h1 class="error-code">404</h1>
        <h2 class="error-title">页面未找到</h2>
        <p class="error-description">
          抱歉，您访问的页面不存在或已被移除。
        </p>
      </div>

      <!-- 操作按钮 -->
      <div class="error-actions">
        <el-button 
          type="primary" 
          size="large"
          :icon="HomeFilled"
          @click="goHome"
        >
          返回首页
        </el-button>
        <el-button 
          size="large"
          :icon="ArrowLeft"
          @click="goBack"
        >
          返回上页
        </el-button>
      </div>

      <!-- 建议链接 -->
      <div class="suggested-links">
        <h3>您可能想要访问：</h3>
        <div class="links-grid">
          <router-link to="/dashboard" class="link-item">
            <el-icon><Monitor /></el-icon>
            <span>系统仪表板</span>
          </router-link>
          <router-link to="/server-status" class="link-item">
            <el-icon><Setting /></el-icon>
            <span>服务器状态</span>
          </router-link>
          <router-link to="/ipmi-control" class="link-item">
            <el-icon><Connection /></el-icon>
            <span>IPMI控制</span>
          </router-link>
          <router-link to="/monitoring" class="link-item">
            <el-icon><TrendCharts /></el-icon>
            <span>系统监控</span>
          </router-link>
        </div>
      </div>
    </div>

    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
    </div>
  </div>
</template>

<script setup>
/**
 * 404页面组件
 * 当用户访问不存在的页面时显示
 */
import { useRouter } from 'vue-router'
import { 
  WarningFilled, HomeFilled, ArrowLeft, Monitor, 
  Setting, Connection, TrendCharts 
} from '@element-plus/icons-vue'

const router = useRouter()

/**
 * 返回首页
 */
const goHome = () => {
  router.push('/dashboard')
}

/**
 * 返回上一页
 */
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/dashboard')
  }
}
</script>

<style lang="scss" scoped>
.not-found {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--el-bg-color-page) 0%, var(--el-bg-color) 100%);
  position: relative;
  overflow: hidden;
}

.not-found-container {
  text-align: center;
  max-width: 600px;
  padding: var(--spacing-xl);
  position: relative;
  z-index: 2;
}

.error-icon {
  margin-bottom: var(--spacing-xl);

  .el-icon {
    font-size: 120px;
    color: var(--el-color-warning);
    animation: bounce 2s infinite;
  }
}

.error-content {
  margin-bottom: var(--spacing-xl);

  .error-code {
    font-size: 120px;
    font-weight: 900;
    color: var(--el-color-primary);
    margin: 0;
    line-height: 1;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  }

  .error-title {
    font-size: 32px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: var(--spacing-md) 0;
  }

  .error-description {
    font-size: 16px;
    color: var(--el-text-color-secondary);
    line-height: 1.6;
    margin: 0;
  }
}

.error-actions {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  margin-bottom: var(--spacing-xl);
}

.suggested-links {
  h3 {
    font-size: 18px;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin: 0 0 var(--spacing-md) 0;
  }

  .links-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }

  .link-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    background: var(--el-bg-color);
    border: 1px solid var(--el-border-color);
    border-radius: var(--border-radius);
    color: var(--el-text-color-primary);
    text-decoration: none;
    transition: all 0.3s ease;

    &:hover {
      background: var(--el-color-primary-light-9);
      border-color: var(--el-color-primary);
      color: var(--el-color-primary);
      transform: translateY(-2px);
      box-shadow: var(--shadow-base);
    }

    .el-icon {
      font-size: 20px;
    }

    span {
      font-weight: 500;
    }
  }
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, var(--el-color-primary-light-7), var(--el-color-primary-light-9));
  opacity: 0.1;
  animation: float 6s ease-in-out infinite;

  &.circle-1 {
    width: 200px;
    height: 200px;
    top: 10%;
    left: 10%;
    animation-delay: 0s;
  }

  &.circle-2 {
    width: 150px;
    height: 150px;
    top: 60%;
    right: 15%;
    animation-delay: 2s;
  }

  &.circle-3 {
    width: 100px;
    height: 100px;
    bottom: 20%;
    left: 20%;
    animation-delay: 4s;
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

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .not-found-container {
    padding: var(--spacing-lg);
  }

  .error-icon .el-icon {
    font-size: 80px;
  }

  .error-content {
    .error-code {
      font-size: 80px;
    }

    .error-title {
      font-size: 24px;
    }

    .error-description {
      font-size: 14px;
    }
  }

  .error-actions {
    flex-direction: column;
    align-items: center;

    .el-button {
      width: 200px;
    }
  }

  .suggested-links {
    .links-grid {
      grid-template-columns: 1fr;
    }
  }

  .decoration-circle {
    &.circle-1 {
      width: 120px;
      height: 120px;
    }

    &.circle-2 {
      width: 80px;
      height: 80px;
    }

    &.circle-3 {
      width: 60px;
      height: 60px;
    }
  }
}

@media (max-width: 480px) {
  .error-content {
    .error-code {
      font-size: 60px;
    }

    .error-title {
      font-size: 20px;
    }
  }

  .suggested-links .link-item {
    padding: var(--spacing-sm);
    font-size: 14px;

    .el-icon {
      font-size: 16px;
    }
  }
}
</style>