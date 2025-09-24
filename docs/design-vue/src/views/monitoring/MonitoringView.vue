<!--
  监控中心主页面
  功能：提供基础设施、应用、数据库和网络监控功能
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="monitoring-view">
    <!-- 内容头部 -->
    <div class="content-header">
      <div class="breadcrumb">
        <span class="breadcrumb-item">监控中心</span>
        <i class="fas fa-chevron-right"></i>
        <span class="breadcrumb-item active">{{ currentTabName }}</span>
      </div>

      <div class="header-actions">
        <div class="time-selector">
          <select v-model="selectedTimeRange" @change="handleTimeRangeChange" class="time-range">
            <option value="5m">最近5分钟</option>
            <option value="15m">最近15分钟</option>
            <option value="1h">最近1小时</option>
            <option value="6h">最近6小时</option>
            <option value="24h">最近24小时</option>
            <option value="7d">最近7天</option>
          </select>
        </div>
        <button class="btn btn-secondary" @click="refreshData" :disabled="isRefreshing">
          <i class="fas fa-sync-alt" :class="{ spinning: isRefreshing }"></i>
          刷新
        </button>
        <button class="btn btn-primary" @click="exportReport">
          <i class="fas fa-download"></i>
          导出报告
        </button>
      </div>
    </div>

    <!-- 监控内容容器 -->
    <div class="monitoring-container">
      <!-- 子标签页导航 -->
      <div class="sub-tabs">
        <div 
          v-for="tab in subTabs" 
          :key="tab.id"
          :class="['sub-tab', { active: activeSubTab === tab.id }]"
          @click="switchSubTab(tab.id)"
        >
          <i :class="tab.icon"></i>
          {{ tab.name }}
        </div>
      </div>

      <!-- 基础设施监控 -->
      <div v-if="activeSubTab === 'infrastructure'" class="subtab-content active">
        <InfrastructureMonitoring 
          :time-range="selectedTimeRange"
          :is-refreshing="isRefreshing"
          @refresh="refreshData"
        />
      </div>

      <!-- 应用监控 -->
      <div v-if="activeSubTab === 'applications'" class="subtab-content active">
        <ApplicationMonitoring 
          :time-range="selectedTimeRange"
          :is-refreshing="isRefreshing"
          @refresh="refreshData"
        />
      </div>

      <!-- 数据库监控 -->
      <div v-if="activeSubTab === 'databases'" class="subtab-content active">
        <DatabaseMonitoring 
          :time-range="selectedTimeRange"
          :is-refreshing="isRefreshing"
          @refresh="refreshData"
        />
      </div>

      <!-- 网络监控 -->
      <div v-if="activeSubTab === 'network'" class="subtab-content active">
        <NetworkMonitoring 
          :time-range="selectedTimeRange"
          :is-refreshing="isRefreshing"
          @refresh="refreshData"
        />
      </div>
    </div>
  </div>
</template>

<script>
import InfrastructureMonitoring from './components/InfrastructureMonitoring.vue'
import ApplicationMonitoring from './components/ApplicationMonitoring.vue'
import DatabaseMonitoring from './components/DatabaseMonitoring.vue'
import NetworkMonitoring from './components/NetworkMonitoring.vue'

/**
 * 监控中心主页面组件
 * 管理各种监控子页面的切换和数据刷新
 */
export default {
  name: 'MonitoringView',
  components: {
    InfrastructureMonitoring,
    ApplicationMonitoring,
    DatabaseMonitoring,
    NetworkMonitoring
  },
  data() {
    return {
      // 当前活动的子标签页
      activeSubTab: 'infrastructure',
      // 选中的时间范围
      selectedTimeRange: '1h',
      // 刷新状态
      isRefreshing: false,
      // 自动刷新定时器
      autoRefreshTimer: null,
      // 子标签页配置
      subTabs: [
        {
          id: 'infrastructure',
          name: '基础设施',
          icon: 'fas fa-server'
        },
        {
          id: 'applications',
          name: '应用监控',
          icon: 'fas fa-cube'
        },
        {
          id: 'databases',
          name: '数据库',
          icon: 'fas fa-database'
        },
        {
          id: 'network',
          name: '网络监控',
          icon: 'fas fa-network-wired'
        }
      ]
    }
  },
  computed: {
    /**
     * 当前标签页名称
     */
    currentTabName() {
      const tab = this.subTabs.find(t => t.id === this.activeSubTab)
      return tab ? tab.name : '基础设施监控'
    }
  },
  methods: {
    /**
     * 切换子标签页
     */
    switchSubTab(tabId) {
      if (this.activeSubTab !== tabId) {
        this.activeSubTab = tabId
        this.refreshData()
      }
    },
    
    /**
     * 处理时间范围变化
     */
    handleTimeRangeChange() {
      this.refreshData()
    },
    
    /**
     * 刷新数据
     */
    async refreshData() {
      if (this.isRefreshing) return
      
      this.isRefreshing = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1500))
        console.log(`Refreshing ${this.activeSubTab} monitoring data for ${this.selectedTimeRange}`)
      } catch (error) {
        console.error('Failed to refresh monitoring data:', error)
      } finally {
        this.isRefreshing = false
      }
    },
    
    /**
     * 导出报告
     */
    exportReport() {
      console.log(`Exporting ${this.activeSubTab} monitoring report for ${this.selectedTimeRange}`)
      // 这里可以实现具体的导出逻辑
    },
    
    /**
     * 启动自动刷新
     */
    startAutoRefresh() {
      this.stopAutoRefresh()
      this.autoRefreshTimer = setInterval(() => {
        this.refreshData()
      }, 30000) // 每30秒刷新一次
    },
    
    /**
     * 停止自动刷新
     */
    stopAutoRefresh() {
      if (this.autoRefreshTimer) {
        clearInterval(this.autoRefreshTimer)
        this.autoRefreshTimer = null
      }
    }
  },
  mounted() {
    // 初始化数据
    this.refreshData()
    // 启动自动刷新
    this.startAutoRefresh()
  },
  beforeUnmount() {
    // 清理定时器
    this.stopAutoRefresh()
  }
}
</script>

<style scoped>
/* 监控视图容器 */
.monitoring-view {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

/* 内容头部样式 */
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.breadcrumb-item {
  color: #6c757d;
}

.breadcrumb-item.active {
  color: #2c3e50;
  font-weight: 600;
}

.breadcrumb i {
  color: #6c757d;
  font-size: 12px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.time-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.time-selector select:focus {
  outline: none;
  border-color: #3498db;
}

/* 监控容器样式 */
.monitoring-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* 子标签页导航样式 */
.sub-tabs {
  display: flex;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.sub-tab {
  flex: 1;
  padding: 15px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 500;
  color: #6c757d;
}

.sub-tab:hover {
  background: #e9ecef;
  color: #495057;
}

.sub-tab.active {
  background: white;
  color: #3498db;
  border-bottom-color: #3498db;
}

.sub-tab i {
  font-size: 16px;
}

/* 子标签页内容样式 */
.subtab-content {
  padding: 30px;
  min-height: 600px;
}

.subtab-content.active {
  display: block;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-header {
    flex-direction: column;
    gap: 20px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .monitoring-view {
    padding: 15px;
  }
  
  .content-header {
    padding: 15px;
  }
  
  .sub-tabs {
    flex-direction: column;
  }
  
  .sub-tab {
    justify-content: flex-start;
    text-align: left;
  }
  
  .subtab-content {
    padding: 20px;
  }
  
  .header-actions {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .breadcrumb {
    font-size: 14px;
  }
  
  .sub-tab {
    padding: 12px 15px;
    font-size: 14px;
  }
  
  .subtab-content {
    padding: 15px;
  }
}
</style>