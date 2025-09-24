<!--
  仪表板主页面组件
  功能：显示系统概览、性能监控、性能分析和日志查看等功能
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="dashboard-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>
        <i class="fas fa-tachometer-alt"></i>
        仪表板
      </h1>
    </div>

    <!-- 子页面标签导航 -->
    <div class="subtabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['subtab', { active: activeTab === tab.id }]"
        @click="switchTab(tab.id)"
      >
        <i :class="tab.icon"></i>
        {{ tab.name }}
      </div>
    </div>

    <!-- 子页面内容 -->
    <div class="subtab-container">
      <!-- 系统概览 -->
      <SystemOverview v-if="activeTab === 'overview'" />
      
      <!-- 性能监控 -->
      <PerformanceMonitoring v-if="activeTab === 'monitoring'" />
      
      <!-- 性能分析 -->
      <PerformanceAnalysis v-if="activeTab === 'analysis'" />
      
      <!-- 日志查看 -->
      <LogViewer v-if="activeTab === 'logs'" />
    </div>
  </div>
</template>

<script>
/**
 * 仪表板主页面组件
 * 管理仪表板的标签切换和子组件显示
 */
import SystemOverview from './components/SystemOverview.vue'
import PerformanceMonitoring from './components/PerformanceMonitoring.vue'
import PerformanceAnalysis from './components/PerformanceAnalysis.vue'
import LogViewer from './components/LogViewer.vue'

export default {
  name: 'DashboardView',
  components: {
    SystemOverview,
    PerformanceMonitoring,
    PerformanceAnalysis,
    LogViewer
  },
  data() {
    return {
      // 当前激活的标签页
      activeTab: 'overview',
      // 标签页配置
      tabs: [
        {
          id: 'overview',
          name: '系统概览',
          icon: 'fas fa-chart-pie'
        },
        {
          id: 'monitoring',
          name: '性能监控',
          icon: 'fas fa-chart-line'
        },
        {
          id: 'analysis',
          name: '性能分析',
          icon: 'fas fa-analytics'
        },
        {
          id: 'logs',
          name: '日志查看',
          icon: 'fas fa-file-alt'
        }
      ]
    }
  },
  methods: {
    /**
     * 切换标签页
     * @param {string} tabId - 标签页ID
     */
    switchTab(tabId) {
      this.activeTab = tabId
    }
  },
  mounted() {
    // 组件挂载后的初始化操作
    console.log('Dashboard view mounted')
  }
}
</script>

<style scoped>
/* 仪表板容器样式 */
.dashboard-container {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

/* 页面标题样式 */
.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
}

.page-header h1 i {
  color: #3498db;
}

/* 子标签导航样式 */
.subtabs {
  display: flex;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  overflow: hidden;
}

.subtab {
  flex: 1;
  padding: 15px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-right: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
  color: #6c757d;
}

.subtab:last-child {
  border-right: none;
}

.subtab:hover {
  background: #f8f9fa;
  color: #495057;
}

.subtab.active {
  background: #3498db;
  color: white;
}

.subtab.active:hover {
  background: #2980b9;
}

/* 子页面容器样式 */
.subtab-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .subtabs {
    flex-direction: column;
  }
  
  .subtab {
    border-right: none;
    border-bottom: 1px solid #e9ecef;
  }
  
  .subtab:last-child {
    border-bottom: none;
  }
}
</style>