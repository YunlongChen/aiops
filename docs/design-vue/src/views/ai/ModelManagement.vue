<!--
  模型管理页面
  管理AI模型的训练、部署和监控
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="model-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">模型管理</h1>
          <p class="page-description">AI模型的训练、部署和生命周期管理</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="importModel">
            <i class="icon-upload"></i>
            导入模型
          </button>
          <button class="btn btn-outline" @click="exportModel">
            <i class="icon-download"></i>
            导出模型
          </button>
          <button class="btn btn-primary" @click="createModel">
            <i class="icon-plus"></i>
            新建模型
          </button>
        </div>
      </div>
    </div>

    <!-- 模型概览 -->
    <div class="model-overview">
      <div class="overview-grid">
        <div class="overview-card total">
          <div class="card-icon">
            <i class="icon-layers"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ modelStats.total }}</div>
            <div class="card-label">总模型数</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +5个
            </div>
          </div>
        </div>
        <div class="overview-card active">
          <div class="card-icon">
            <i class="icon-play"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ modelStats.active }}</div>
            <div class="card-label">运行中</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +2个
            </div>
          </div>
        </div>
        <div class="overview-card training">
          <div class="card-icon">
            <i class="icon-refresh"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ modelStats.training }}</div>
            <div class="card-label">训练中</div>
            <div class="card-status">
              <LoadingSpinner size="small" />
            </div>
          </div>
        </div>
        <div class="overview-card accuracy">
          <div class="card-icon">
            <i class="icon-target"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ modelStats.avgAccuracy }}%</div>
            <div class="card-label">平均准确率</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +2.1%
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="model-filters">
      <div class="filters-content">
        <div class="filter-group">
          <select v-model="selectedCategory" class="filter-select">
            <option value="">全部类型</option>
            <option value="anomaly">异常检测</option>
            <option value="prediction">预测分析</option>
            <option value="classification">分类模型</option>
            <option value="regression">回归模型</option>
            <option value="clustering">聚类模型</option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="selectedStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="active">运行中</option>
            <option value="inactive">已停用</option>
            <option value="training">训练中</option>
            <option value="failed">训练失败</option>
            <option value="draft">草稿</option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="selectedFramework" class="filter-select">
            <option value="">全部框架</option>
            <option value="tensorflow">TensorFlow</option>
            <option value="pytorch">PyTorch</option>
            <option value="sklearn">Scikit-learn</option>
            <option value="xgboost">XGBoost</option>
            <option value="lightgbm">LightGBM</option>
          </select>
        </div>
        <div class="filter-group search-group">
          <div class="search-input">
            <i class="icon-search"></i>
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="搜索模型名称或描述..."
            >
          </div>
        </div>
        <div class="filter-group">
          <div class="view-toggle">
            <button 
              class="toggle-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <i class="icon-grid"></i>
              网格视图
            </button>
            <button 
              class="toggle-btn"
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
            >
              <i class="icon-list"></i>
              列表视图
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型列表 -->
    <div class="model-list">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="grid-view">
        <div class="models-grid">
          <div 
            v-for="model in filteredModels" 
            :key="model.id"
            class="model-card"
            :class="[model.status, model.category]"
          >
            <div class="model-header">
              <div class="model-info">
                <div class="model-name">{{ model.name }}</div>
                <div class="model-version">v{{ model.version }}</div>
              </div>
              <div class="model-status">
                <StatusBadge 
                  :status="model.status" 
                  :variant="getStatusVariant(model.status)"
                />
              </div>
            </div>
            
            <div class="model-content">
              <div class="model-description">{{ model.description }}</div>
              <div class="model-details">
                <div class="detail-item">
                  <span class="detail-label">类型:</span>
                  <span class="detail-value">{{ getCategoryName(model.category) }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">框架:</span>
                  <span class="detail-value">{{ model.framework }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">创建时间:</span>
                  <span class="detail-value">{{ formatDate(model.createdAt) }}</span>
                </div>
              </div>
              
              <div class="model-metrics" v-if="model.status === 'active'">
                <div class="metric">
                  <span class="metric-label">准确率</span>
                  <span class="metric-value">{{ model.accuracy }}%</span>
                </div>
                <div class="metric">
                  <span class="metric-label">延迟</span>
                  <span class="metric-value">{{ model.latency }}ms</span>
                </div>
                <div class="metric">
                  <span class="metric-label">吞吐量</span>
                  <span class="metric-value">{{ model.throughput }}/s</span>
                </div>
              </div>
              
              <div class="training-progress" v-if="model.status === 'training'">
                <div class="progress-info">
                  <span class="progress-label">训练进度</span>
                  <span class="progress-percentage">{{ model.trainingProgress }}%</span>
                </div>
                <div class="progress-bar">
                  <div 
                    class="progress-fill"
                    :style="{ width: model.trainingProgress + '%' }"
                  ></div>
                </div>
                <div class="progress-details">
                  <span class="progress-epoch">Epoch {{ model.currentEpoch }}/{{ model.totalEpochs }}</span>
                  <span class="progress-loss">Loss: {{ model.currentLoss }}</span>
                </div>
              </div>
            </div>
            
            <div class="model-actions">
              <button 
                v-if="model.status === 'active'"
                class="action-btn primary"
                @click="viewModelDetail(model)"
              >
                <i class="icon-eye"></i>
                查看详情
              </button>
              <button 
                v-if="model.status === 'active'"
                class="action-btn"
                @click="stopModel(model)"
              >
                <i class="icon-pause"></i>
                停用
              </button>
              <button 
                v-if="model.status === 'inactive'"
                class="action-btn success"
                @click="startModel(model)"
              >
                <i class="icon-play"></i>
                启用
              </button>
              <button 
                v-if="model.status !== 'training'"
                class="action-btn"
                @click="trainModel(model)"
              >
                <i class="icon-refresh"></i>
                重新训练
              </button>
              <button 
                v-if="model.status === 'training'"
                class="action-btn danger"
                @click="stopTraining(model)"
              >
                <i class="icon-stop"></i>
                停止训练
              </button>
              <button 
                class="action-btn"
                @click="cloneModel(model)"
              >
                <i class="icon-copy"></i>
                克隆
              </button>
              <button 
                class="action-btn danger"
                @click="deleteModel(model)"
              >
                <i class="icon-trash"></i>
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="list-view">
        <div class="list-table">
          <div class="table-header">
            <div class="header-cell name">模型名称</div>
            <div class="header-cell type">类型</div>
            <div class="header-cell framework">框架</div>
            <div class="header-cell status">状态</div>
            <div class="header-cell metrics">性能指标</div>
            <div class="header-cell updated">更新时间</div>
            <div class="header-cell actions">操作</div>
          </div>
          
          <div class="table-body">
            <div 
              v-for="model in filteredModels" 
              :key="model.id"
              class="table-row"
              :class="model.status"
            >
              <div class="table-cell name">
                <div class="model-info">
                  <div class="model-name">{{ model.name }}</div>
                  <div class="model-version">v{{ model.version }}</div>
                </div>
              </div>
              <div class="table-cell type">
                <span class="type-badge" :class="model.category">
                  {{ getCategoryName(model.category) }}
                </span>
              </div>
              <div class="table-cell framework">
                <span class="framework-badge">{{ model.framework }}</span>
              </div>
              <div class="table-cell status">
                <StatusBadge 
                  :status="model.status" 
                  :variant="getStatusVariant(model.status)"
                />
              </div>
              <div class="table-cell metrics">
                <div v-if="model.status === 'active'" class="metrics-info">
                  <div class="metric-item">
                    <span class="metric-label">准确率:</span>
                    <span class="metric-value">{{ model.accuracy }}%</span>
                  </div>
                  <div class="metric-item">
                    <span class="metric-label">延迟:</span>
                    <span class="metric-value">{{ model.latency }}ms</span>
                  </div>
                </div>
                <div v-else-if="model.status === 'training'" class="training-info">
                  <div class="training-progress-mini">
                    <div class="progress-bar-mini">
                      <div 
                        class="progress-fill-mini"
                        :style="{ width: model.trainingProgress + '%' }"
                      ></div>
                    </div>
                    <span class="progress-text-mini">{{ model.trainingProgress }}%</span>
                  </div>
                </div>
                <span v-else class="no-metrics">-</span>
              </div>
              <div class="table-cell updated">
                {{ formatTime(model.updatedAt) }}
              </div>
              <div class="table-cell actions">
                <div class="action-buttons">
                  <button 
                    class="action-btn-mini"
                    @click="viewModelDetail(model)"
                    title="查看详情"
                  >
                    <i class="icon-eye"></i>
                  </button>
                  <button 
                    v-if="model.status === 'active'"
                    class="action-btn-mini"
                    @click="stopModel(model)"
                    title="停用"
                  >
                    <i class="icon-pause"></i>
                  </button>
                  <button 
                    v-if="model.status === 'inactive'"
                    class="action-btn-mini success"
                    @click="startModel(model)"
                    title="启用"
                  >
                    <i class="icon-play"></i>
                  </button>
                  <button 
                    class="action-btn-mini"
                    @click="trainModel(model)"
                    title="训练"
                  >
                    <i class="icon-refresh"></i>
                  </button>
                  <button 
                    class="action-btn-mini danger"
                    @click="deleteModel(model)"
                    title="删除"
                  >
                    <i class="icon-trash"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-if="filteredModels.length === 0"
        icon="icon-layers"
        title="暂无模型"
        description="创建您的第一个AI模型开始智能运维"
        :actions="[
          { text: '新建模型', action: createModel },
          { text: '导入模型', action: importModel }
        ]"
      />
    </div>

    <!-- 模型详情弹窗 -->
    <div v-if="showModelDetail" class="model-detail-modal" @click="closeModelDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ selectedModel?.name }} 详情</h3>
          <button class="modal-close" @click="closeModelDetail">
            <i class="icon-x"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="detail-tabs">
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'overview' }"
              @click="activeTab = 'overview'"
            >
              概览
            </button>
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'metrics' }"
              @click="activeTab = 'metrics'"
            >
              性能指标
            </button>
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'config' }"
              @click="activeTab = 'config'"
            >
              配置信息
            </button>
            <button 
              class="tab-btn"
              :class="{ active: activeTab === 'logs' }"
              @click="activeTab = 'logs'"
            >
              训练日志
            </button>
          </div>
          
          <div class="tab-content">
            <!-- 概览标签页 -->
            <div v-if="activeTab === 'overview'" class="tab-panel">
              <div class="overview-info">
                <div class="info-group">
                  <h4 class="group-title">基本信息</h4>
                  <div class="info-items">
                    <div class="info-item">
                      <span class="info-label">模型名称:</span>
                      <span class="info-value">{{ selectedModel?.name }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">版本:</span>
                      <span class="info-value">v{{ selectedModel?.version }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">类型:</span>
                      <span class="info-value">{{ getCategoryName(selectedModel?.category) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">框架:</span>
                      <span class="info-value">{{ selectedModel?.framework }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">状态:</span>
                      <StatusBadge 
                        :status="selectedModel?.status" 
                        :variant="getStatusVariant(selectedModel?.status)"
                      />
                    </div>
                  </div>
                </div>
                
                <div class="info-group">
                  <h4 class="group-title">描述信息</h4>
                  <p class="model-description-full">{{ selectedModel?.description }}</p>
                </div>
                
                <div class="info-group">
                  <h4 class="group-title">时间信息</h4>
                  <div class="info-items">
                    <div class="info-item">
                      <span class="info-label">创建时间:</span>
                      <span class="info-value">{{ formatDateTime(selectedModel?.createdAt) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">更新时间:</span>
                      <span class="info-value">{{ formatDateTime(selectedModel?.updatedAt) }}</span>
                    </div>
                    <div class="info-item">
                      <span class="info-label">最后训练:</span>
                      <span class="info-value">{{ formatDateTime(selectedModel?.lastTrainedAt) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 性能指标标签页 -->
            <div v-if="activeTab === 'metrics'" class="tab-panel">
              <div class="metrics-content">
                <div class="metrics-grid">
                  <div class="metric-card">
                    <div class="metric-header">
                      <h4 class="metric-title">准确率</h4>
                    </div>
                    <div class="metric-value-large">{{ selectedModel?.accuracy }}%</div>
                    <div class="metric-trend positive">
                      <i class="icon-trending-up"></i>
                      +2.3% 较上次训练
                    </div>
                  </div>
                  
                  <div class="metric-card">
                    <div class="metric-header">
                      <h4 class="metric-title">响应延迟</h4>
                    </div>
                    <div class="metric-value-large">{{ selectedModel?.latency }}ms</div>
                    <div class="metric-trend negative">
                      <i class="icon-trending-down"></i>
                      -5ms 较上次部署
                    </div>
                  </div>
                  
                  <div class="metric-card">
                    <div class="metric-header">
                      <h4 class="metric-title">吞吐量</h4>
                    </div>
                    <div class="metric-value-large">{{ selectedModel?.throughput }}/s</div>
                    <div class="metric-trend positive">
                      <i class="icon-trending-up"></i>
                      +15% 较上次部署
                    </div>
                  </div>
                  
                  <div class="metric-card">
                    <div class="metric-header">
                      <h4 class="metric-title">内存使用</h4>
                    </div>
                    <div class="metric-value-large">{{ selectedModel?.memoryUsage }}MB</div>
                    <div class="metric-trend stable">
                      <i class="icon-minus"></i>
                      稳定
                    </div>
                  </div>
                </div>
                
                <div class="performance-chart">
                  <BaseChart
                    title="性能趋势"
                    :loading="false"
                    :error="false"
                    :no-data="false"
                  >
                    <div class="chart-placeholder">
                      <div class="performance-trend">
                        <div class="trend-line">
                          <div class="line-point" v-for="i in 10" :key="i" :style="{ height: (Math.random() * 60 + 20) + '%' }"></div>
                        </div>
                        <div class="trend-labels">
                          <span>1天前</span>
                          <span>现在</span>
                        </div>
                      </div>
                    </div>
                  </BaseChart>
                </div>
              </div>
            </div>
            
            <!-- 配置信息标签页 -->
            <div v-if="activeTab === 'config'" class="tab-panel">
              <div class="config-content">
                <div class="config-section">
                  <h4 class="section-title">模型参数</h4>
                  <div class="config-items">
                    <div class="config-item">
                      <span class="config-label">学习率:</span>
                      <span class="config-value">0.001</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">批次大小:</span>
                      <span class="config-value">32</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">训练轮数:</span>
                      <span class="config-value">100</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">优化器:</span>
                      <span class="config-value">Adam</span>
                    </div>
                  </div>
                </div>
                
                <div class="config-section">
                  <h4 class="section-title">网络结构</h4>
                  <div class="config-items">
                    <div class="config-item">
                      <span class="config-label">输入层:</span>
                      <span class="config-value">64 neurons</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">隐藏层:</span>
                      <span class="config-value">3 layers (128, 64, 32)</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">输出层:</span>
                      <span class="config-value">1 neuron</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">激活函数:</span>
                      <span class="config-value">ReLU</span>
                    </div>
                  </div>
                </div>
                
                <div class="config-section">
                  <h4 class="section-title">数据配置</h4>
                  <div class="config-items">
                    <div class="config-item">
                      <span class="config-label">训练集大小:</span>
                      <span class="config-value">10,000 samples</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">验证集大小:</span>
                      <span class="config-value">2,000 samples</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">测试集大小:</span>
                      <span class="config-value">2,000 samples</span>
                    </div>
                    <div class="config-item">
                      <span class="config-label">特征数量:</span>
                      <span class="config-value">64</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 训练日志标签页 -->
            <div v-if="activeTab === 'logs'" class="tab-panel">
              <div class="logs-content">
                <div class="logs-header">
                  <h4 class="logs-title">训练日志</h4>
                  <button class="btn btn-outline btn-sm" @click="refreshLogs">
                    <i class="icon-refresh"></i>
                    刷新
                  </button>
                </div>
                <div class="logs-list">
                  <div class="log-item" v-for="log in trainingLogs" :key="log.id">
                    <div class="log-time">{{ formatTime(log.timestamp) }}</div>
                    <div class="log-level" :class="log.level">{{ log.level.toUpperCase() }}</div>
                    <div class="log-message">{{ log.message }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeModelDetail">关闭</button>
          <button class="btn btn-primary" @click="editModel(selectedModel)">编辑模型</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 模型管理页面组件
 * 管理AI模型的训练、部署和监控
 */
import { ref, computed, onMounted } from 'vue'
import BaseChart from '@/components/charts/BaseChart.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

// 响应式数据
const selectedCategory = ref('')
const selectedStatus = ref('')
const selectedFramework = ref('')
const searchQuery = ref('')
const viewMode = ref('grid')
const showModelDetail = ref(false)
const selectedModel = ref(null)
const activeTab = ref('overview')

// 模型统计数据
const modelStats = ref({
  total: 24,
  active: 8,
  training: 3,
  avgAccuracy: 91.5
})

// 模型数据
const models = ref([
  {
    id: 1,
    name: 'CPU异常检测模型',
    version: '2.1.0',
    description: '基于LSTM的CPU使用率异常检测模型，能够识别异常峰值和异常模式',
    category: 'anomaly',
    framework: 'TensorFlow',
    status: 'active',
    accuracy: 94.2,
    latency: 15,
    throughput: 1200,
    memoryUsage: 256,
    createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    lastTrainedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
  },
  {
    id: 2,
    name: '内存使用预测模型',
    version: '1.5.2',
    description: '基于时间序列的内存使用率预测模型，支持未来24小时预测',
    category: 'prediction',
    framework: 'PyTorch',
    status: 'training',
    trainingProgress: 75,
    currentEpoch: 75,
    totalEpochs: 100,
    currentLoss: 0.0234,
    createdAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    lastTrainedAt: new Date(Date.now() - 1 * 60 * 60 * 1000)
  },
  {
    id: 3,
    name: '网络流量分类模型',
    version: '3.0.1',
    description: '基于随机森林的网络流量分类模型，识别正常和异常流量模式',
    category: 'classification',
    framework: 'Scikit-learn',
    status: 'active',
    accuracy: 89.7,
    latency: 8,
    throughput: 2500,
    memoryUsage: 128,
    createdAt: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    lastTrainedAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000)
  },
  {
    id: 4,
    name: '响应时间回归模型',
    version: '1.2.0',
    description: '基于XGBoost的应用响应时间预测模型，支持负载预测',
    category: 'regression',
    framework: 'XGBoost',
    status: 'inactive',
    accuracy: 87.3,
    latency: 12,
    throughput: 1800,
    memoryUsage: 192,
    createdAt: new Date(Date.now() - 60 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    lastTrainedAt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000)
  },
  {
    id: 5,
    name: '服务器聚类模型',
    version: '2.0.0',
    description: '基于K-means的服务器性能聚类模型，用于资源优化分组',
    category: 'clustering',
    framework: 'Scikit-learn',
    status: 'active',
    accuracy: 92.1,
    latency: 20,
    throughput: 800,
    memoryUsage: 320,
    createdAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    lastTrainedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000)
  },
  {
    id: 6,
    name: '磁盘故障预测模型',
    version: '1.8.1',
    description: '基于深度学习的磁盘故障预测模型，提前预警硬件故障',
    category: 'prediction',
    framework: 'TensorFlow',
    status: 'failed',
    error: '训练数据不足',
    createdAt: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    lastTrainedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000)
  }
])

// 训练日志数据
const trainingLogs = ref([
  {
    id: 1,
    timestamp: new Date(Date.now() - 5 * 60 * 1000),
    level: 'info',
    message: 'Epoch 75/100 - loss: 0.0234 - accuracy: 0.9542 - val_loss: 0.0267 - val_accuracy: 0.9489'
  },
  {
    id: 2,
    timestamp: new Date(Date.now() - 10 * 60 * 1000),
    level: 'info',
    message: 'Epoch 74/100 - loss: 0.0241 - accuracy: 0.9538 - val_loss: 0.0271 - val_accuracy: 0.9485'
  },
  {
    id: 3,
    timestamp: new Date(Date.now() - 15 * 60 * 1000),
    level: 'warning',
    message: 'Learning rate reduced to 0.0005 due to plateau in validation loss'
  },
  {
    id: 4,
    timestamp: new Date(Date.now() - 20 * 60 * 1000),
    level: 'info',
    message: 'Epoch 73/100 - loss: 0.0248 - accuracy: 0.9534 - val_loss: 0.0275 - val_accuracy: 0.9481'
  },
  {
    id: 5,
    timestamp: new Date(Date.now() - 25 * 60 * 1000),
    level: 'error',
    message: 'GPU memory usage high: 7.2GB/8GB. Consider reducing batch size.'
  }
])

// 计算属性
const filteredModels = computed(() => {
  let filtered = models.value

  // 类型筛选
  if (selectedCategory.value) {
    filtered = filtered.filter(model => model.category === selectedCategory.value)
  }

  // 状态筛选
  if (selectedStatus.value) {
    filtered = filtered.filter(model => model.status === selectedStatus.value)
  }

  // 框架筛选
  if (selectedFramework.value) {
    filtered = filtered.filter(model => model.framework === selectedFramework.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(model => 
      model.name.toLowerCase().includes(query) ||
      model.description.toLowerCase().includes(query)
    )
  }

  return filtered.sort((a, b) => b.updatedAt - a.updatedAt)
})

/**
 * 获取类型名称
 */
const getCategoryName = (category) => {
  const names = {
    anomaly: '异常检测',
    prediction: '预测分析',
    classification: '分类模型',
    regression: '回归模型',
    clustering: '聚类模型'
  }
  return names[category] || category
}

/**
 * 获取状态变体
 */
const getStatusVariant = (status) => {
  const variants = {
    active: 'success',
    inactive: 'default',
    training: 'info',
    failed: 'danger',
    draft: 'warning'
  }
  return variants[status] || 'default'
}

/**
 * 格式化日期
 */
const formatDate = (date) => {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  }).format(date)
}

/**
 * 格式化时间
 */
const formatTime = (time) => {
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(time)
}

/**
 * 格式化日期时间
 */
const formatDateTime = (datetime) => {
  return new Intl.DateTimeFormat('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(datetime)
}

/**
 * 创建模型
 */
const createModel = () => {
  console.log('创建新模型')
}

/**
 * 导入模型
 */
const importModel = () => {
  console.log('导入模型')
}

/**
 * 导出模型
 */
const exportModel = () => {
  console.log('导出模型')
}

/**
 * 查看模型详情
 */
const viewModelDetail = (model) => {
  selectedModel.value = model
  showModelDetail.value = true
  activeTab.value = 'overview'
}

/**
 * 关闭模型详情
 */
const closeModelDetail = () => {
  showModelDetail.value = false
  selectedModel.value = null
}

/**
 * 启动模型
 */
const startModel = (model) => {
  model.status = 'active'
  console.log('启动模型:', model)
}

/**
 * 停用模型
 */
const stopModel = (model) => {
  model.status = 'inactive'
  console.log('停用模型:', model)
}

/**
 * 训练模型
 */
const trainModel = (model) => {
  model.status = 'training'
  model.trainingProgress = 0
  console.log('训练模型:', model)
}

/**
 * 停止训练
 */
const stopTraining = (model) => {
  model.status = 'inactive'
  console.log('停止训练:', model)
}

/**
 * 克隆模型
 */
const cloneModel = (model) => {
  console.log('克隆模型:', model)
}

/**
 * 删除模型
 */
const deleteModel = (model) => {
  console.log('删除模型:', model)
}

/**
 * 编辑模型
 */
const editModel = (model) => {
  console.log('编辑模型:', model)
}

/**
 * 刷新日志
 */
const refreshLogs = () => {
  console.log('刷新训练日志')
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.model-management {
  padding: $spacing-lg;
  background: $background-color;
  min-height: 100vh;
}

// 页面头部
.page-header {
  margin-bottom: $spacing-xl;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: $spacing-lg;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 $spacing-xs 0;
  font-size: 28px;
  font-weight: 700;
  color: $text-color;
}

.page-description {
  margin: 0;
  color: $text-color-secondary;
  font-size: 15px;
}

.header-right {
  display: flex;
  gap: $spacing-md;
}

// 模型概览
.model-overview {
  margin-bottom: $spacing-xl;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
}

.overview-card {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  border-left: 4px solid;
  
  &.total {
    border-left-color: $primary-color;
    
    .card-icon {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }
  
  &.active {
    border-left-color: $success-color;
    
    .card-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
  
  &.training {
    border-left-color: $info-color;
    
    .card-icon {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }
  }
  
  &.accuracy {
    border-left-color: $warning-color;
    
    .card-icon {
      background: rgba($warning-color, 0.1);
      color: $warning-color;
    }
  }
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 700;
  color: $text-color;
  line-height: 1;
  margin-bottom: $spacing-xs;
}

.card-label {
  font-size: 14px;
  color: $text-color-secondary;
  margin-bottom: $spacing-xs;
}

.card-trend {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  font-weight: 500;
  
  &.positive {
    color: $success-color;
  }
  
  &.negative {
    color: $danger-color;
  }
}

.card-status {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

// 筛选和搜索
.model-filters {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.filters-content {
  display: flex;
  gap: $spacing-md;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  &.search-group {
    flex: 1;
    min-width: 200px;
  }
}

.filter-select {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  font-size: 13px;
  min-width: 120px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.search-input {
  position: relative;
  display: flex;
  align-items: center;
  
  i {
    position: absolute;
    left: $spacing-md;
    color: $text-color-light;
    font-size: 14px;
  }
  
  input {
    width: 100%;
    padding: $spacing-sm $spacing-md $spacing-sm 36px;
    border: 1px solid $border-color;
    border-radius: $border-radius-md;
    font-size: 13px;
    
    &:focus {
      outline: none;
      border-color: $primary-color;
    }
    
    &::placeholder {
      color: $text-color-light;
    }
  }
}

.view-toggle {
  display: flex;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  overflow: hidden;
}

.toggle-btn {
  padding: $spacing-sm $spacing-md;
  border: none;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  
  &:hover {
    background: $background-color-light;
  }
  
  &.active {
    background: $primary-color;
    color: $white;
  }
}

// 模型列表
.model-list {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

// 网格视图
.grid-view {
  padding: $spacing-lg;
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: $spacing-lg;
}

.model-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  transition: all 0.2s ease;
  border-left: 4px solid;
  
  &:hover {
    box-shadow: $shadow-sm;
  }
  
  &.active {
    border-left-color: $success-color;
  }
  
  &.inactive {
    border-left-color: $text-color-light;
  }
  
  &.training {
    border-left-color: $info-color;
  }
  
  &.failed {
    border-left-color: $danger-color;
  }
  
  &.draft {
    border-left-color: $warning-color;
  }
}

.model-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: $spacing-md;
  gap: $spacing-md;
}

.model-info {
  flex: 1;
}

.model-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.model-version {
  font-size: 13px;
  color: $text-color-secondary;
}

.model-content {
  margin-bottom: $spacing-md;
}

.model-description {
  color: $text-color-secondary;
  line-height: 1.5;
  margin-bottom: $spacing-md;
  font-size: 14px;
}

.model-details {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  margin-bottom: $spacing-md;
}

.detail-item {
  display: flex;
  gap: $spacing-xs;
  font-size: 13px;
}

.detail-label {
  color: $text-color-light;
  min-width: 80px;
}

.detail-value {
  color: $text-color;
  font-weight: 500;
}

.model-metrics {
  display: flex;
  justify-content: space-between;
  gap: $spacing-md;
  padding: $spacing-md;
  background: $background-color-light;
  border-radius: $border-radius-md;
}

.metric {
  text-align: center;
}

.metric-label {
  display: block;
  font-size: 12px;
  color: $text-color-light;
  margin-bottom: $spacing-xs;
}

.metric-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.training-progress {
  padding: $spacing-md;
  background: rgba($info-color, 0.05);
  border-radius: $border-radius-md;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-sm;
}

.progress-label {
  font-size: 13px;
  color: $text-color-secondary;
}

.progress-percentage {
  font-size: 13px;
  font-weight: 600;
  color: $info-color;
}

.progress-bar {
  height: 8px;
  background: $background-color-light;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: $spacing-sm;
}

.progress-fill {
  height: 100%;
  background: $info-color;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-details {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: $text-color-light;
}

.model-actions {
  display: flex;
  gap: $spacing-xs;
  flex-wrap: wrap;
}

.action-btn {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.primary {
    background: $primary-color;
    border-color: $primary-color;
    color: $white;
    
    &:hover {
      background: darken($primary-color, 5%);
    }
  }
  
  &.success {
    &:hover {
      border-color: $success-color;
      color: $success-color;
    }
  }
  
  &.danger {
    &:hover {
      border-color: $danger-color;
      color: $danger-color;
    }
  }
}

// 列表视图
.list-view {
  overflow-x: auto;
}

.list-table {
  min-width: 1000px;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1.5fr 1fr 1.5fr;
  gap: $spacing-md;
  padding: $spacing-md $spacing-lg;
  background: $background-color-light;
  border-bottom: 1px solid $border-color-light;
  font-weight: 600;
  color: $text-color;
  font-size: 13px;
}

.table-body {
  display: flex;
  flex-direction: column;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr 1.5fr 1fr 1.5fr;
  gap: $spacing-md;
  padding: $spacing-md $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  transition: all 0.2s ease;
  
  &:hover {
    background: $background-color-light;
  }
  
  &.active {
    border-left: 4px solid $success-color;
  }
  
  &.training {
    border-left: 4px solid $info-color;
  }
  
  &.failed {
    border-left: 4px solid $danger-color;
  }
}

.table-cell {
  display: flex;
  align-items: center;
  font-size: 13px;
  
  &.name {
    flex-direction: column;
    align-items: flex-start;
  }
}

.type-badge {
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
  
  &.anomaly {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.prediction {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.classification {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
  
  &.regression {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.clustering {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
  }
}

.framework-badge {
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  font-size: 11px;
  color: $text-color-secondary;
}

.metrics-info {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.metric-item {
  display: flex;
  gap: $spacing-xs;
  font-size: 11px;
}

.training-info {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.training-progress-mini {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.progress-bar-mini {
  width: 60px;
  height: 4px;
  background: $background-color-light;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill-mini {
  height: 100%;
  background: $info-color;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text-mini {
  font-size: 11px;
  color: $info-color;
  font-weight: 500;
}

.no-metrics {
  color: $text-color-light;
}

.action-buttons {
  display: flex;
  gap: $spacing-xs;
}

.action-btn-mini {
  width: 28px;
  height: 28px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.success {
    &:hover {
      border-color: $success-color;
      color: $success-color;
    }
  }
  
  &.danger {
    &:hover {
      border-color: $danger-color;
      color: $danger-color;
    }
  }
}

// 模型详情弹窗
.model-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: $spacing-lg;
}

.modal-content {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-lg;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: $text-color;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: $text-color-light;
  cursor: pointer;
  border-radius: $border-radius-sm;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  
  &:hover {
    background: $background-color-light;
    color: $text-color;
  }
}

.modal-body {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.detail-tabs {
  display: flex;
  border-bottom: 1px solid $border-color-light;
  padding: 0 $spacing-lg;
}

.tab-btn {
  padding: $spacing-md $spacing-lg;
  border: none;
  background: none;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  border-bottom: 2px solid transparent;
  
  &:hover {
    color: $text-color;
  }
  
  &.active {
    color: $primary-color;
    border-bottom-color: $primary-color;
  }
}

.tab-content {
  flex: 1;
  overflow-y: auto;
}

.tab-panel {
  padding: $spacing-lg;
}

// 概览标签页
.overview-info {
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.info-group {
  .group-title {
    margin: 0 0 $spacing-md 0;
    font-size: 16px;
    font-weight: 600;
    color: $text-color;
  }
}

.info-items {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.info-item {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.info-label {
  color: $text-color-light;
  min-width: 100px;
  font-size: 14px;
}

.info-value {
  color: $text-color;
  font-weight: 500;
  font-size: 14px;
}

.model-description-full {
  color: $text-color-secondary;
  line-height: 1.6;
  margin: 0;
}

// 性能指标标签页
.metrics-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-lg;
}

.metric-card {
  padding: $spacing-lg;
  background: $background-color-light;
  border-radius: $border-radius-lg;
  text-align: center;
}

.metric-header {
  margin-bottom: $spacing-md;
  
  .metric-title {
    margin: 0;
    font-size: 14px;
    color: $text-color-light;
    font-weight: 500;
  }
}

.metric-value-large {
  font-size: 32px;
  font-weight: 700;
  color: $text-color;
  margin-bottom: $spacing-sm;
}

.metric-trend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  font-size: 12px;
  font-weight: 500;
  
  &.positive {
    color: $success-color;
  }
  
  &.negative {
    color: $danger-color;
  }
  
  &.stable {
    color: $text-color-light;
  }
}

.performance-chart {
  margin-top: $spacing-lg;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.performance-trend {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.trend-line {
  display: flex;
  align-items: end;
  gap: 4px;
  height: 80px;
  margin-bottom: $spacing-md;
}

.line-point {
  width: 8px;
  background: $primary-color;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
  
  &:hover {
    background: darken($primary-color, 10%);
  }
}

.trend-labels {
  display: flex;
  justify-content: space-between;
  width: 100%;
  font-size: 12px;
  color: $text-color-light;
}

// 配置信息标签页
.config-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.config-section {
  .section-title {
    margin: 0 0 $spacing-md 0;
    font-size: 16px;
    font-weight: 600;
    color: $text-color;
  }
}

.config-items {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-md;
}

.config-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-sm $spacing-md;
  background: $background-color-light;
  border-radius: $border-radius-md;
}

.config-label {
  color: $text-color-light;
  font-size: 14px;
}

.config-value {
  color: $text-color;
  font-weight: 500;
  font-size: 14px;
}

// 训练日志标签页
.logs-content {
  display: flex;
  flex-direction: column;
  height: 400px;
}

.logs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $spacing-md;
  
  .logs-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: $text-color;
  }
}

.logs-list {
  flex: 1;
  overflow-y: auto;
  border: 1px solid $border-color-light;
  border-radius: $border-radius-md;
  background: $background-color-dark;
}

.log-item {
  display: flex;
  gap: $spacing-md;
  padding: $spacing-sm $spacing-md;
  border-bottom: 1px solid rgba($border-color-light, 0.5);
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  
  &:last-child {
    border-bottom: none;
  }
}

.log-time {
  color: $text-color-light;
  min-width: 80px;
}

.log-level {
  min-width: 60px;
  font-weight: 600;
  text-transform: uppercase;
  
  &.info {
    color: $info-color;
  }
  
  &.warning {
    color: $warning-color;
  }
  
  &.error {
    color: $danger-color;
  }
}

.log-message {
  flex: 1;
  color: $text-color;
  word-break: break-all;
}

.modal-footer {
  padding: $spacing-lg;
  border-top: 1px solid $border-color-light;
  display: flex;
  justify-content: flex-end;
  gap: $spacing-md;
}

// 响应式设计
@media (max-width: 1200px) {
  .models-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .model-management {
    padding: $spacing-md;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: flex-start;
  }
  
  .filters-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    &.search-group {
      min-width: auto;
    }
  }
  
  .models-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .model-card {
    padding: $spacing-md;
  }
  
  .model-actions {
    justify-content: center;
  }
  
  .modal-content {
    margin: $spacing-md;
    max-height: calc(100vh - #{$spacing-md * 2});
  }
  
  .metrics-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  }
  
  .config-items {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .card-content {
    text-align: center;
  }
  
  .card-value {
    font-size: 24px;
  }
  
  .model-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .model-metrics {
    flex-direction: column;
    gap: $spacing-sm;
  }
  
  .metric {
    text-align: left;
  }
  
  .action-btn {
    flex: 1;
    justify-content: center;
  }
  
  .modal-header {
    padding: $spacing-md;
  }
  
  .tab-panel {
    padding: $spacing-md;
  }
  
  .modal-footer {
    padding: $spacing-md;
  }
}
</style>