<!--
  AI引擎主页面组件
  提供AI模型管理、训练、部署和预测分析功能
  包含模型库、模型训练、模型部署、异常检测、容量规划、性能预测、决策规则、自动化策略、知识库、智能洞察、优化建议等功能模块
-->
<template>
  <div class="ai-engine-view">
    <!-- 内容头部 -->
    <div class="content-header">
      <div class="breadcrumb">
        <span class="breadcrumb-item">AI引擎</span>
        <i class="fas fa-chevron-right"></i>
        <span class="breadcrumb-item active">{{ getCurrentTabName() }}</span>
      </div>
      
      <div class="header-actions">
        <button class="btn btn-secondary" @click="refreshData">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': isRefreshing }"></i>
          刷新
        </button>
        <button class="btn btn-primary" @click="createModel" v-if="activeTab === 'models'">
          <i class="fas fa-plus"></i>
          创建模型
        </button>
        <button class="btn btn-primary" @click="newTrainingTask" v-if="activeTab === 'training'">
          <i class="fas fa-plus"></i>
          新建训练任务
        </button>
      </div>
    </div>

    <!-- AI引擎内容容器 -->
    <div class="ai-engine-container">
      <!-- 子标签页导航 -->
      <div class="sub-tabs">
        <div class="tab-group">
          <div class="tab-group-title">模型管理</div>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'models' }"
            @click="setActiveTab('models')"
          >
            <i class="fas fa-database"></i>
            模型库
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'training' }"
            @click="setActiveTab('training')"
          >
            <i class="fas fa-graduation-cap"></i>
            模型训练
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'deployment' }"
            @click="setActiveTab('deployment')"
          >
            <i class="fas fa-rocket"></i>
            模型部署
          </button>
        </div>

        <div class="tab-group">
          <div class="tab-group-title">预测分析</div>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'anomaly-detection' }"
            @click="setActiveTab('anomaly-detection')"
          >
            <i class="fas fa-search"></i>
            异常检测
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'capacity-planning' }"
            @click="setActiveTab('capacity-planning')"
          >
            <i class="fas fa-chart-area"></i>
            容量规划
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'performance-prediction' }"
            @click="setActiveTab('performance-prediction')"
          >
            <i class="fas fa-crystal-ball"></i>
            性能预测
          </button>
        </div>

        <div class="tab-group">
          <div class="tab-group-title">决策引擎</div>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'decision-rules' }"
            @click="setActiveTab('decision-rules')"
          >
            <i class="fas fa-sitemap"></i>
            决策规则
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'automation-policies' }"
            @click="setActiveTab('automation-policies')"
          >
            <i class="fas fa-cogs"></i>
            自动化策略
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'knowledge-base' }"
            @click="setActiveTab('knowledge-base')"
          >
            <i class="fas fa-book"></i>
            知识库
          </button>
        </div>

        <div class="tab-group">
          <div class="tab-group-title">AI洞察</div>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'insights' }"
            @click="setActiveTab('insights')"
          >
            <i class="fas fa-lightbulb"></i>
            智能洞察
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'recommendations' }"
            @click="setActiveTab('recommendations')"
          >
            <i class="fas fa-thumbs-up"></i>
            优化建议
          </button>
        </div>
      </div>

      <!-- 动态内容区域 -->
      <div class="tab-content">
        <!-- 模型库 -->
        <ModelLibrary v-if="activeTab === 'models'" />
        
        <!-- 模型训练 -->
        <ModelTraining v-if="activeTab === 'training'" />
        
        <!-- 模型部署 -->
        <div v-else-if="activeTab === 'deployment'" class="deployment-content">
          <div class="deployment-header">
            <h3>模型部署管理</h3>
            <p>管理已部署的AI模型实例</p>
          </div>
          <div class="deployment-grid">
            <div class="deployment-card" v-for="deployment in deployments" :key="deployment.id">
              <div class="deployment-status" :class="deployment.status">
                <i :class="deployment.statusIcon"></i>
                {{ deployment.statusText }}
              </div>
              <h4>{{ deployment.name }}</h4>
              <p>{{ deployment.description }}</p>
              <div class="deployment-metrics">
                <div class="metric">
                  <span class="label">CPU使用率:</span>
                  <span class="value">{{ deployment.cpuUsage }}%</span>
                </div>
                <div class="metric">
                  <span class="label">内存使用:</span>
                  <span class="value">{{ deployment.memoryUsage }}%</span>
                </div>
                <div class="metric">
                  <span class="label">请求数:</span>
                  <span class="value">{{ deployment.requests }}/min</span>
                </div>
              </div>
              <div class="deployment-actions">
                <button class="btn btn-sm btn-secondary">监控</button>
                <button class="btn btn-sm btn-primary">配置</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 异常检测 -->
        <div v-else-if="activeTab === 'anomaly-detection'" class="anomaly-detection-content">
          <div class="detection-header">
            <h3>异常检测</h3>
            <p>基于AI算法的系统异常检测和分析</p>
          </div>
          <div class="detection-dashboard">
            <div class="detection-stats">
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-exclamation-triangle"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ anomalyStats.total }}</div>
                  <div class="stat-label">检测到异常</div>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-shield-alt"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ anomalyStats.resolved }}</div>
                  <div class="stat-label">已处理异常</div>
                </div>
              </div>
              <div class="stat-card">
                <div class="stat-icon">
                  <i class="fas fa-clock"></i>
                </div>
                <div class="stat-content">
                  <div class="stat-value">{{ anomalyStats.pending }}</div>
                  <div class="stat-label">待处理异常</div>
                </div>
              </div>
            </div>
            <div class="detection-chart">
              <h4>异常检测趋势</h4>
              <div class="chart-placeholder">
                <i class="fas fa-chart-line"></i>
                <p>异常检测趋势图表</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 容量规划 -->
        <div v-else-if="activeTab === 'capacity-planning'" class="capacity-planning-content">
          <div class="planning-header">
            <h3>容量规划</h3>
            <p>基于历史数据和趋势预测的容量规划建议</p>
          </div>
          <div class="planning-dashboard">
            <div class="resource-forecast">
              <h4>资源预测</h4>
              <div class="forecast-grid">
                <div class="forecast-item">
                  <div class="forecast-icon">
                    <i class="fas fa-microchip"></i>
                  </div>
                  <div class="forecast-content">
                    <div class="forecast-title">CPU容量</div>
                    <div class="forecast-current">当前: 65%</div>
                    <div class="forecast-predicted">预测: 85% (30天后)</div>
                    <div class="forecast-recommendation">建议: 增加2个CPU核心</div>
                  </div>
                </div>
                <div class="forecast-item">
                  <div class="forecast-icon">
                    <i class="fas fa-memory"></i>
                  </div>
                  <div class="forecast-content">
                    <div class="forecast-title">内存容量</div>
                    <div class="forecast-current">当前: 72%</div>
                    <div class="forecast-predicted">预测: 90% (30天后)</div>
                    <div class="forecast-recommendation">建议: 增加8GB内存</div>
                  </div>
                </div>
                <div class="forecast-item">
                  <div class="forecast-icon">
                    <i class="fas fa-hdd"></i>
                  </div>
                  <div class="forecast-content">
                    <div class="forecast-title">存储容量</div>
                    <div class="forecast-current">当前: 58%</div>
                    <div class="forecast-predicted">预测: 75% (30天后)</div>
                    <div class="forecast-recommendation">建议: 增加500GB存储</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 性能预测 -->
        <div v-else-if="activeTab === 'performance-prediction'" class="performance-prediction-content">
          <div class="prediction-header">
            <h3>性能预测</h3>
            <p>基于机器学习的系统性能预测和优化建议</p>
          </div>
          <div class="prediction-dashboard">
            <div class="prediction-metrics">
              <div class="metric-card">
                <h4>响应时间预测</h4>
                <div class="metric-chart">
                  <div class="chart-placeholder">
                    <i class="fas fa-stopwatch"></i>
                    <p>响应时间趋势预测</p>
                  </div>
                </div>
              </div>
              <div class="metric-card">
                <h4>吞吐量预测</h4>
                <div class="metric-chart">
                  <div class="chart-placeholder">
                    <i class="fas fa-tachometer-alt"></i>
                    <p>系统吞吐量预测</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 决策规则 -->
        <div v-else-if="activeTab === 'decision-rules'" class="decision-rules-content">
          <div class="rules-header">
            <h3>决策规则管理</h3>
            <p>配置和管理AI决策引擎的规则</p>
          </div>
          <div class="rules-list">
            <div class="rule-item" v-for="rule in decisionRules" :key="rule.id">
              <div class="rule-status" :class="rule.status">
                <i :class="rule.statusIcon"></i>
              </div>
              <div class="rule-content">
                <h4>{{ rule.name }}</h4>
                <p>{{ rule.description }}</p>
                <div class="rule-conditions">
                  <span class="condition" v-for="condition in rule.conditions" :key="condition">
                    {{ condition }}
                  </span>
                </div>
              </div>
              <div class="rule-actions">
                <button class="btn btn-sm btn-secondary">编辑</button>
                <button class="btn btn-sm btn-danger">删除</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 自动化策略 -->
        <div v-else-if="activeTab === 'automation-policies'" class="automation-policies-content">
          <div class="policies-header">
            <h3>自动化策略</h3>
            <p>配置系统自动化运维策略</p>
          </div>
          <div class="policies-grid">
            <div class="policy-card" v-for="policy in automationPolicies" :key="policy.id">
              <div class="policy-header">
                <h4>{{ policy.name }}</h4>
                <div class="policy-toggle">
                  <input type="checkbox" :checked="policy.enabled" />
                  <span class="toggle-slider"></span>
                </div>
              </div>
              <p>{{ policy.description }}</p>
              <div class="policy-triggers">
                <div class="trigger" v-for="trigger in policy.triggers" :key="trigger">
                  <i class="fas fa-bolt"></i>
                  {{ trigger }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 知识库 -->
        <div v-else-if="activeTab === 'knowledge-base'" class="knowledge-base-content">
          <div class="knowledge-header">
            <h3>AI知识库</h3>
            <p>系统运维知识和最佳实践库</p>
          </div>
          <div class="knowledge-categories">
            <div class="category-card" v-for="category in knowledgeCategories" :key="category.id">
              <div class="category-icon">
                <i :class="category.icon"></i>
              </div>
              <h4>{{ category.name }}</h4>
              <p>{{ category.description }}</p>
              <div class="category-stats">
                <span>{{ category.articleCount }} 篇文章</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 智能洞察 -->
        <div v-else-if="activeTab === 'insights'" class="insights-content">
          <div class="insights-header">
            <h3>智能洞察</h3>
            <p>AI分析生成的系统洞察和发现</p>
          </div>
          <div class="insights-list">
            <div class="insight-item" v-for="insight in intelligentInsights" :key="insight.id">
              <div class="insight-priority" :class="insight.priority">
                <i :class="insight.priorityIcon"></i>
              </div>
              <div class="insight-content">
                <h4>{{ insight.title }}</h4>
                <p>{{ insight.description }}</p>
                <div class="insight-tags">
                  <span class="tag" v-for="tag in insight.tags" :key="tag">{{ tag }}</span>
                </div>
                <div class="insight-time">{{ insight.createdAt }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 优化建议 -->
        <div v-else-if="activeTab === 'recommendations'" class="recommendations-content">
          <div class="recommendations-header">
            <h3>优化建议</h3>
            <p>AI生成的系统优化建议和改进方案</p>
          </div>
          <div class="recommendations-list">
            <div class="recommendation-item" v-for="recommendation in optimizationRecommendations" :key="recommendation.id">
              <div class="recommendation-impact" :class="recommendation.impact">
                <span>{{ recommendation.impactText }}</span>
              </div>
              <div class="recommendation-content">
                <h4>{{ recommendation.title }}</h4>
                <p>{{ recommendation.description }}</p>
                <div class="recommendation-benefits">
                  <div class="benefit" v-for="benefit in recommendation.benefits" :key="benefit">
                    <i class="fas fa-check"></i>
                    {{ benefit }}
                  </div>
                </div>
              </div>
              <div class="recommendation-actions">
                <button class="btn btn-sm btn-primary">应用建议</button>
                <button class="btn btn-sm btn-secondary">查看详情</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import ModelLibrary from '@/components/ai-engine/ModelLibrary.vue'
import ModelTraining from '@/components/ai-engine/ModelTraining.vue'

export default {
  name: 'AiEngineView',
  components: {
    ModelLibrary,
    ModelTraining
  },
  setup() {
    // 响应式数据
    const activeTab = ref('models')
    const isRefreshing = ref(false)
    const autoRefreshInterval = ref(null)

    // 模型部署数据
    const deployments = ref([
      {
        id: 1,
        name: '异常检测模型 v2.1',
        description: '基于LSTM的系统异常检测模型',
        status: 'running',
        statusText: '运行中',
        statusIcon: 'fas fa-play-circle',
        cpuUsage: 45,
        memoryUsage: 62,
        requests: 1250
      },
      {
        id: 2,
        name: '容量预测模型 v1.3',
        description: '资源容量预测和规划模型',
        status: 'stopped',
        statusText: '已停止',
        statusIcon: 'fas fa-stop-circle',
        cpuUsage: 0,
        memoryUsage: 0,
        requests: 0
      }
    ])

    // 异常检测统计数据
    const anomalyStats = ref({
      total: 127,
      resolved: 98,
      pending: 29
    })

    // 决策规则数据
    const decisionRules = ref([
      {
        id: 1,
        name: 'CPU使用率告警规则',
        description: '当CPU使用率超过80%时触发告警',
        status: 'active',
        statusIcon: 'fas fa-check-circle',
        conditions: ['CPU > 80%', '持续时间 > 5分钟']
      },
      {
        id: 2,
        name: '内存泄漏检测规则',
        description: '检测应用程序内存泄漏模式',
        status: 'inactive',
        statusIcon: 'fas fa-pause-circle',
        conditions: ['内存增长率 > 10%/小时', '持续时间 > 2小时']
      }
    ])

    // 自动化策略数据
    const automationPolicies = ref([
      {
        id: 1,
        name: '自动扩容策略',
        description: '根据负载自动调整资源配置',
        enabled: true,
        triggers: ['CPU使用率 > 75%', '内存使用率 > 80%']
      },
      {
        id: 2,
        name: '故障自愈策略',
        description: '自动重启失败的服务实例',
        enabled: false,
        triggers: ['服务健康检查失败', '响应时间超时']
      }
    ])

    // 知识库分类数据
    const knowledgeCategories = ref([
      {
        id: 1,
        name: '系统监控',
        description: '系统监控相关知识和最佳实践',
        icon: 'fas fa-chart-line',
        articleCount: 45
      },
      {
        id: 2,
        name: '故障排查',
        description: '常见故障的诊断和解决方案',
        icon: 'fas fa-tools',
        articleCount: 32
      },
      {
        id: 3,
        name: '性能优化',
        description: '系统性能优化技巧和方法',
        icon: 'fas fa-rocket',
        articleCount: 28
      }
    ])

    // 智能洞察数据
    const intelligentInsights = ref([
      {
        id: 1,
        title: '数据库连接池配置异常',
        description: '检测到数据库连接池配置可能导致性能瓶颈',
        priority: 'high',
        priorityIcon: 'fas fa-exclamation-triangle',
        tags: ['数据库', '性能', '配置'],
        createdAt: '2小时前'
      },
      {
        id: 2,
        title: '磁盘空间使用趋势异常',
        description: '磁盘空间增长速度超出预期，建议检查日志清理策略',
        priority: 'medium',
        priorityIcon: 'fas fa-info-circle',
        tags: ['存储', '趋势分析'],
        createdAt: '4小时前'
      }
    ])

    // 优化建议数据
    const optimizationRecommendations = ref([
      {
        id: 1,
        title: '优化数据库查询性能',
        description: '通过添加索引和优化查询语句提升数据库性能',
        impact: 'high',
        impactText: '高影响',
        benefits: ['查询速度提升40%', '减少CPU使用率15%', '改善用户体验']
      },
      {
        id: 2,
        title: '调整JVM内存配置',
        description: '根据应用负载特征调整JVM堆内存配置',
        impact: 'medium',
        impactText: '中等影响',
        benefits: ['减少GC频率', '提升应用稳定性', '优化内存使用']
      }
    ])

    // 标签页名称映射
    const tabNames = {
      'models': '模型库',
      'training': '模型训练',
      'deployment': '模型部署',
      'anomaly-detection': '异常检测',
      'capacity-planning': '容量规划',
      'performance-prediction': '性能预测',
      'decision-rules': '决策规则',
      'automation-policies': '自动化策略',
      'knowledge-base': '知识库',
      'insights': '智能洞察',
      'recommendations': '优化建议'
    }

    /**
     * 获取当前标签页名称
     */
    const getCurrentTabName = () => {
      return tabNames[activeTab.value] || '未知'
    }

    /**
     * 设置活跃标签页
     */
    const setActiveTab = (tab) => {
      activeTab.value = tab
    }

    /**
     * 刷新数据
     */
    const refreshData = async () => {
      isRefreshing.value = true
      try {
        // 模拟刷新延迟
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('AI引擎数据已刷新')
      } catch (error) {
        console.error('刷新失败:', error)
      } finally {
        isRefreshing.value = false
      }
    }

    /**
     * 创建模型
     */
    const createModel = () => {
      console.log('创建新模型')
      // TODO: 实现创建模型逻辑
    }

    /**
     * 新建训练任务
     */
    const newTrainingTask = () => {
      console.log('新建训练任务')
      // TODO: 实现新建训练任务逻辑
    }

    /**
     * 启动自动刷新
     */
    const startAutoRefresh = () => {
      autoRefreshInterval.value = setInterval(() => {
        if (!isRefreshing.value) {
          refreshData()
        }
      }, 30000) // 30秒自动刷新
    }

    /**
     * 停止自动刷新
     */
    const stopAutoRefresh = () => {
      if (autoRefreshInterval.value) {
        clearInterval(autoRefreshInterval.value)
        autoRefreshInterval.value = null
      }
    }

    // 生命周期钩子
    onMounted(() => {
      startAutoRefresh()
    })

    onUnmounted(() => {
      stopAutoRefresh()
    })

    return {
      activeTab,
      isRefreshing,
      deployments,
      anomalyStats,
      decisionRules,
      automationPolicies,
      knowledgeCategories,
      intelligentInsights,
      optimizationRecommendations,
      getCurrentTabName,
      setActiveTab,
      refreshData,
      createModel,
      newTrainingTask
    }
  }
}
</script>

<style scoped>
.ai-engine-view {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #6b7280;
}

.breadcrumb-item.active {
  color: #1f2937;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.ai-engine-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sub-tabs {
  display: flex;
  gap: 24px;
  padding: 16px 20px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  overflow-x: auto;
}

.tab-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: fit-content;
}

.tab-group-title {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: none;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.tab-btn.active {
  background: #dbeafe;
  color: #1d4ed8;
}

.tab-content {
  flex: 1;
  overflow: auto;
}

.fa-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .header-actions {
    justify-content: center;
  }

  .sub-tabs {
    flex-direction: column;
    gap: 16px;
  }

  .tab-group {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .tab-btn {
    flex: 1;
    justify-content: center;
    min-width: 120px;
  }
}
</style>