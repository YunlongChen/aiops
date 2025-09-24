<!--
  策略管理页面
  自愈系统策略配置和管理
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="policy-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">策略管理</h1>
          <p class="page-description">自愈系统策略配置和智能管理</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="importPolicies">
            <i class="icon-upload"></i>
            导入策略
          </button>
          <button class="btn btn-outline" @click="exportPolicies">
            <i class="icon-download"></i>
            导出策略
          </button>
          <button class="btn btn-primary" @click="createPolicy">
            <i class="icon-plus"></i>
            新建策略
          </button>
        </div>
      </div>
    </div>

    <!-- 策略概览 -->
    <div class="policy-overview">
      <div class="overview-grid">
        <div class="overview-card total">
          <div class="card-icon">
            <i class="icon-layers"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ policyStats.totalPolicies }}</div>
            <div class="card-label">总策略数</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +3个本周
            </div>
          </div>
        </div>
        <div class="overview-card active">
          <div class="card-icon">
            <i class="icon-play-circle"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ policyStats.activePolicies }}</div>
            <div class="card-label">启用中</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +2个
            </div>
          </div>
        </div>
        <div class="overview-card success-rate">
          <div class="card-icon">
            <i class="icon-target"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ policyStats.successRate }}%</div>
            <div class="card-label">成功率</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +1.2%
            </div>
          </div>
        </div>
        <div class="overview-card executions">
          <div class="card-icon">
            <i class="icon-zap"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ policyStats.totalExecutions }}</div>
            <div class="card-label">执行次数</div>
            <div class="card-trend positive">
              <i class="icon-trending-up"></i>
              +45次今日
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="filter-content">
        <div class="filter-left">
          <select v-model="selectedCategory" class="filter-select">
            <option value="">全部分类</option>
            <option value="performance">性能优化</option>
            <option value="availability">可用性保障</option>
            <option value="security">安全防护</option>
            <option value="resource">资源管理</option>
          </select>
          <select v-model="selectedStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="active">启用</option>
            <option value="inactive">禁用</option>
            <option value="draft">草稿</option>
          </select>
          <select v-model="selectedPriority" class="filter-select">
            <option value="">全部优先级</option>
            <option value="high">高</option>
            <option value="medium">中</option>
            <option value="low">低</option>
          </select>
        </div>
        <div class="filter-right">
          <div class="search-box">
            <i class="icon-search"></i>
            <input 
              type="text" 
              v-model="searchKeyword"
              placeholder="搜索策略名称、描述..."
              class="search-input"
            >
          </div>
          <div class="view-toggle">
            <button 
              class="toggle-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
            >
              <i class="icon-grid"></i>
            </button>
            <button 
              class="toggle-btn"
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
            >
              <i class="icon-list"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 策略列表 -->
    <div class="policy-list">
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="policy-grid">
        <div 
          class="policy-card"
          v-for="policy in filteredPolicies"
          :key="policy.id"
          :class="[policy.category, policy.status]"
        >
          <div class="card-header">
            <div class="policy-info">
              <div class="policy-name">{{ policy.name }}</div>
              <div class="policy-category">{{ getCategoryText(policy.category) }}</div>
            </div>
            <div class="policy-actions">
              <label class="policy-toggle">
                <input 
                  type="checkbox" 
                  v-model="policy.enabled"
                  @change="togglePolicy(policy)"
                >
                <span class="toggle-slider"></span>
              </label>
              <div class="action-dropdown">
                <button class="action-btn" @click="toggleDropdown(policy.id)">
                  <i class="icon-more-vertical"></i>
                </button>
                <div class="dropdown-menu" v-show="activeDropdown === policy.id">
                  <button class="dropdown-item" @click="editPolicy(policy)">
                    <i class="icon-edit"></i>
                    编辑
                  </button>
                  <button class="dropdown-item" @click="duplicatePolicy(policy)">
                    <i class="icon-copy"></i>
                    复制
                  </button>
                  <button class="dropdown-item" @click="exportPolicy(policy)">
                    <i class="icon-download"></i>
                    导出
                  </button>
                  <button class="dropdown-item danger" @click="deletePolicy(policy)">
                    <i class="icon-trash"></i>
                    删除
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card-content">
            <div class="policy-description">{{ policy.description }}</div>
            
            <div class="policy-priority">
              <span class="priority-label">优先级:</span>
              <span class="priority-badge" :class="policy.priority">
                {{ getPriorityText(policy.priority) }}
              </span>
            </div>
            
            <div class="policy-conditions">
              <div class="conditions-title">触发条件 ({{ policy.conditions.length }})</div>
              <div class="conditions-preview">
                <div 
                  class="condition-tag"
                  v-for="condition in policy.conditions.slice(0, 3)"
                  :key="condition.id"
                >
                  {{ condition.metric }} {{ condition.operator }} {{ condition.value }}
                </div>
                <div v-if="policy.conditions.length > 3" class="condition-more">
                  +{{ policy.conditions.length - 3 }}个
                </div>
              </div>
            </div>
            
            <div class="policy-actions-list">
              <div class="actions-title">执行动作 ({{ policy.actions.length }})</div>
              <div class="actions-preview">
                <div 
                  class="action-tag"
                  v-for="action in policy.actions.slice(0, 2)"
                  :key="action.id"
                >
                  <i :class="getActionIcon(action.type)"></i>
                  {{ action.name }}
                </div>
                <div v-if="policy.actions.length > 2" class="action-more">
                  +{{ policy.actions.length - 2 }}个
                </div>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <div class="policy-stats">
              <div class="stat-item">
                <span class="stat-value">{{ policy.executionCount }}</span>
                <span class="stat-label">执行次数</span>
              </div>
              <div class="stat-item">
                <span class="stat-value" :class="getSuccessRateClass(policy.successRate)">
                  {{ policy.successRate }}%
                </span>
                <span class="stat-label">成功率</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ formatTime(policy.lastExecuted) }}</span>
                <span class="stat-label">最后执行</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-if="viewMode === 'list'" class="policy-table">
        <div class="table-header">
          <div class="header-cell name">策略名称</div>
          <div class="header-cell category">分类</div>
          <div class="header-cell priority">优先级</div>
          <div class="header-cell conditions">条件</div>
          <div class="header-cell actions">动作</div>
          <div class="header-cell stats">统计</div>
          <div class="header-cell status">状态</div>
          <div class="header-cell operations">操作</div>
        </div>
        
        <div class="table-body">
          <div 
            class="table-row"
            v-for="policy in filteredPolicies"
            :key="policy.id"
            :class="[policy.status, policy.priority]"
          >
            <div class="table-cell name">
              <div class="policy-info">
                <div class="policy-name">{{ policy.name }}</div>
                <div class="policy-description">{{ policy.description }}</div>
              </div>
            </div>
            <div class="table-cell category">
              <span class="category-badge" :class="policy.category">
                {{ getCategoryText(policy.category) }}
              </span>
            </div>
            <div class="table-cell priority">
              <span class="priority-badge" :class="policy.priority">
                {{ getPriorityText(policy.priority) }}
              </span>
            </div>
            <div class="table-cell conditions">
              <div class="conditions-count">{{ policy.conditions.length }}个条件</div>
              <div class="conditions-preview">
                {{ policy.conditions.map(c => `${c.metric}${c.operator}${c.value}`).join(', ') }}
              </div>
            </div>
            <div class="table-cell actions">
              <div class="actions-count">{{ policy.actions.length }}个动作</div>
              <div class="actions-preview">
                {{ policy.actions.map(a => a.name).join(', ') }}
              </div>
            </div>
            <div class="table-cell stats">
              <div class="stats-grid">
                <div class="stat-item">
                  <span class="stat-label">执行:</span>
                  <span class="stat-value">{{ policy.executionCount }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">成功率:</span>
                  <span class="stat-value" :class="getSuccessRateClass(policy.successRate)">
                    {{ policy.successRate }}%
                  </span>
                </div>
              </div>
            </div>
            <div class="table-cell status">
              <label class="policy-toggle">
                <input 
                  type="checkbox" 
                  v-model="policy.enabled"
                  @change="togglePolicy(policy)"
                >
                <span class="toggle-slider"></span>
              </label>
            </div>
            <div class="table-cell operations">
              <div class="operation-buttons">
                <button class="operation-btn" @click="editPolicy(policy)">
                  <i class="icon-edit"></i>
                </button>
                <button class="operation-btn" @click="duplicatePolicy(policy)">
                  <i class="icon-copy"></i>
                </button>
                <button class="operation-btn danger" @click="deletePolicy(policy)">
                  <i class="icon-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-if="filteredPolicies.length === 0"
        icon="icon-layers"
        title="暂无策略"
        description="还没有创建任何自愈策略"
        :actions="[
          { text: '新建策略', action: createPolicy },
          { text: '导入策略', action: importPolicies }
        ]"
      />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="totalPages > 1">
      <button 
        class="page-btn"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        <i class="icon-chevron-left"></i>
      </button>
      
      <div class="page-numbers">
        <button 
          class="page-number"
          v-for="page in visiblePages"
          :key="page"
          :class="{ active: page === currentPage }"
          @click="changePage(page)"
        >
          {{ page }}
        </button>
      </div>
      
      <button 
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        <i class="icon-chevron-right"></i>
      </button>
    </div>

    <!-- 策略编辑弹窗 -->
    <div class="modal-overlay" v-if="showEditModal" @click="closeEditModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ editingPolicy.id ? '编辑策略' : '新建策略' }}</h3>
          <button class="modal-close" @click="closeEditModal">
            <i class="icon-x"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="form-section">
            <div class="section-title">基本信息</div>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">策略名称</label>
                <input 
                  type="text" 
                  v-model="editingPolicy.name"
                  class="form-input"
                  placeholder="请输入策略名称"
                >
              </div>
              <div class="form-group">
                <label class="form-label">分类</label>
                <select v-model="editingPolicy.category" class="form-select">
                  <option value="performance">性能优化</option>
                  <option value="availability">可用性保障</option>
                  <option value="security">安全防护</option>
                  <option value="resource">资源管理</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">优先级</label>
                <select v-model="editingPolicy.priority" class="form-select">
                  <option value="high">高</option>
                  <option value="medium">中</option>
                  <option value="low">低</option>
                </select>
              </div>
              <div class="form-group full-width">
                <label class="form-label">描述</label>
                <textarea 
                  v-model="editingPolicy.description"
                  class="form-textarea"
                  placeholder="请输入策略描述"
                  rows="3"
                ></textarea>
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <div class="section-title">触发条件</div>
            <div class="conditions-editor">
              <div 
                class="condition-item"
                v-for="(condition, index) in editingPolicy.conditions"
                :key="condition.id"
              >
                <select v-model="condition.metric" class="condition-select">
                  <option value="cpu">CPU使用率</option>
                  <option value="memory">内存使用率</option>
                  <option value="disk">磁盘使用率</option>
                  <option value="response_time">响应时间</option>
                  <option value="error_rate">错误率</option>
                </select>
                <select v-model="condition.operator" class="condition-select">
                  <option value=">">大于</option>
                  <option value="<">小于</option>
                  <option value=">=">大于等于</option>
                  <option value="<=">小于等于</option>
                  <option value="==">等于</option>
                </select>
                <input 
                  type="text" 
                  v-model="condition.value"
                  class="condition-input"
                  placeholder="阈值"
                >
                <button 
                  class="condition-remove"
                  @click="removeCondition(index)"
                  v-if="editingPolicy.conditions.length > 1"
                >
                  <i class="icon-x"></i>
                </button>
              </div>
              <button class="add-condition" @click="addCondition">
                <i class="icon-plus"></i>
                添加条件
              </button>
            </div>
          </div>
          
          <div class="form-section">
            <div class="section-title">执行动作</div>
            <div class="actions-editor">
              <div 
                class="action-item"
                v-for="(action, index) in editingPolicy.actions"
                :key="action.id"
              >
                <select v-model="action.type" class="action-select">
                  <option value="restart">重启服务</option>
                  <option value="scale">自动扩容</option>
                  <option value="failover">故障转移</option>
                  <option value="notify">发送通知</option>
                  <option value="rollback">版本回滚</option>
                </select>
                <input 
                  type="text" 
                  v-model="action.name"
                  class="action-input"
                  placeholder="动作名称"
                >
                <textarea 
                  v-model="action.config"
                  class="action-config"
                  placeholder="配置参数 (JSON格式)"
                  rows="2"
                ></textarea>
                <button 
                  class="action-remove"
                  @click="removeAction(index)"
                  v-if="editingPolicy.actions.length > 1"
                >
                  <i class="icon-x"></i>
                </button>
              </div>
              <button class="add-action" @click="addAction">
                <i class="icon-plus"></i>
                添加动作
              </button>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="closeEditModal">取消</button>
          <button class="btn btn-primary" @click="savePolicy">保存策略</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 策略管理页面组件
 * 自愈系统策略配置和管理
 */
import { ref, computed, onMounted } from 'vue'
import EmptyState from '@/components/common/EmptyState.vue'

// 响应式数据
const selectedCategory = ref('')
const selectedStatus = ref('')
const selectedPriority = ref('')
const searchKeyword = ref('')
const viewMode = ref('grid')
const currentPage = ref(1)
const pageSize = ref(12)
const activeDropdown = ref(null)
const showEditModal = ref(false)

// 策略统计数据
const policyStats = ref({
  totalPolicies: 24,
  activePolicies: 18,
  successRate: 92.5,
  totalExecutions: 1247
})

// 编辑中的策略
const editingPolicy = ref({
  id: null,
  name: '',
  category: 'performance',
  priority: 'medium',
  description: '',
  conditions: [
    { id: 1, metric: 'cpu', operator: '>', value: '80' }
  ],
  actions: [
    { id: 1, type: 'restart', name: '重启服务', config: '{}' }
  ]
})

// 策略数据
const policies = ref([
  {
    id: 1,
    name: 'CPU过载自动重启',
    category: 'performance',
    priority: 'high',
    status: 'active',
    enabled: true,
    description: '当CPU使用率持续超过80%时自动重启相关服务',
    conditions: [
      { id: 1, metric: 'CPU使用率', operator: '>', value: '80%' },
      { id: 2, metric: '持续时间', operator: '>', value: '5分钟' }
    ],
    actions: [
      { id: 1, type: 'restart', name: '重启Web服务' },
      { id: 2, type: 'notify', name: '发送告警通知' }
    ],
    executionCount: 23,
    successRate: 95.7,
    lastExecuted: new Date(Date.now() - 2 * 60 * 60 * 1000)
  },
  {
    id: 2,
    name: '内存泄漏检测清理',
    category: 'resource',
    priority: 'high',
    status: 'active',
    enabled: true,
    description: '检测内存泄漏并自动清理无用进程',
    conditions: [
      { id: 1, metric: '内存使用率', operator: '>', value: '90%' },
      { id: 2, metric: '内存增长率', operator: '>', value: '10%/min' }
    ],
    actions: [
      { id: 1, type: 'cleanup', name: '清理内存' },
      { id: 2, type: 'restart', name: '重启应用' },
      { id: 3, type: 'notify', name: '通知运维' }
    ],
    executionCount: 15,
    successRate: 86.7,
    lastExecuted: new Date(Date.now() - 4 * 60 * 60 * 1000)
  },
  {
    id: 3,
    name: '数据库连接池优化',
    category: 'availability',
    priority: 'medium',
    status: 'active',
    enabled: true,
    description: '自动调整数据库连接池大小以优化性能',
    conditions: [
      { id: 1, metric: '连接池使用率', operator: '>', value: '85%' },
      { id: 2, metric: '等待连接数', operator: '>', value: '10' }
    ],
    actions: [
      { id: 1, type: 'scale', name: '扩展连接池' },
      { id: 2, type: 'monitor', name: '监控效果' }
    ],
    executionCount: 8,
    successRate: 100,
    lastExecuted: new Date(Date.now() - 6 * 60 * 60 * 1000)
  },
  {
    id: 4,
    name: '安全威胁自动阻断',
    category: 'security',
    priority: 'high',
    status: 'active',
    enabled: false,
    description: '检测到安全威胁时自动阻断可疑IP',
    conditions: [
      { id: 1, metric: '异常请求率', operator: '>', value: '50/min' },
      { id: 2, metric: '威胁等级', operator: '>=', value: '中' }
    ],
    actions: [
      { id: 1, type: 'block', name: '阻断IP' },
      { id: 2, type: 'notify', name: '安全告警' },
      { id: 3, type: 'log', name: '记录日志' }
    ],
    executionCount: 42,
    successRate: 98.1,
    lastExecuted: new Date(Date.now() - 1 * 60 * 60 * 1000)
  },
  {
    id: 5,
    name: '磁盘空间清理',
    category: 'resource',
    priority: 'medium',
    status: 'active',
    enabled: true,
    description: '磁盘空间不足时自动清理临时文件和日志',
    conditions: [
      { id: 1, metric: '磁盘使用率', operator: '>', value: '85%' }
    ],
    actions: [
      { id: 1, type: 'cleanup', name: '清理临时文件' },
      { id: 2, type: 'archive', name: '归档旧日志' }
    ],
    executionCount: 12,
    successRate: 91.7,
    lastExecuted: new Date(Date.now() - 8 * 60 * 60 * 1000)
  },
  {
    id: 6,
    name: '服务健康检查',
    category: 'availability',
    priority: 'low',
    status: 'draft',
    enabled: false,
    description: '定期检查服务健康状态并自动恢复异常服务',
    conditions: [
      { id: 1, metric: '服务响应时间', operator: '>', value: '5000ms' },
      { id: 2, metric: '错误率', operator: '>', value: '5%' }
    ],
    actions: [
      { id: 1, type: 'restart', name: '重启服务' },
      { id: 2, type: 'failover', name: '切换备用' }
    ],
    executionCount: 0,
    successRate: 0,
    lastExecuted: null
  }
])

// 计算属性
const filteredPolicies = computed(() => {
  let filtered = policies.value
  
  if (selectedCategory.value) {
    filtered = filtered.filter(p => p.category === selectedCategory.value)
  }
  
  if (selectedStatus.value) {
    if (selectedStatus.value === 'active') {
      filtered = filtered.filter(p => p.enabled)
    } else if (selectedStatus.value === 'inactive') {
      filtered = filtered.filter(p => !p.enabled)
    } else {
      filtered = filtered.filter(p => p.status === selectedStatus.value)
    }
  }
  
  if (selectedPriority.value) {
    filtered = filtered.filter(p => p.priority === selectedPriority.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(keyword) ||
      p.description.toLowerCase().includes(keyword)
    )
  }
  
  // 分页
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filtered.slice(start, end)
})

const totalPages = computed(() => {
  let filtered = policies.value
  
  if (selectedCategory.value) {
    filtered = filtered.filter(p => p.category === selectedCategory.value)
  }
  
  if (selectedStatus.value) {
    if (selectedStatus.value === 'active') {
      filtered = filtered.filter(p => p.enabled)
    } else if (selectedStatus.value === 'inactive') {
      filtered = filtered.filter(p => !p.enabled)
    } else {
      filtered = filtered.filter(p => p.status === selectedStatus.value)
    }
  }
  
  if (selectedPriority.value) {
    filtered = filtered.filter(p => p.priority === selectedPriority.value)
  }
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(keyword) ||
      p.description.toLowerCase().includes(keyword)
    )
  }
  
  return Math.ceil(filtered.length / pageSize.value)
})

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) {
        pages.push(i)
      }
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) {
        pages.push(i)
      }
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

/**
 * 获取分类文本
 */
const getCategoryText = (category) => {
  const texts = {
    performance: '性能优化',
    availability: '可用性保障',
    security: '安全防护',
    resource: '资源管理'
  }
  return texts[category] || category
}

/**
 * 获取优先级文本
 */
const getPriorityText = (priority) => {
  const texts = {
    high: '高',
    medium: '中',
    low: '低'
  }
  return texts[priority] || priority
}

/**
 * 获取动作图标
 */
const getActionIcon = (type) => {
  const icons = {
    restart: 'icon-refresh-cw',
    scale: 'icon-trending-up',
    failover: 'icon-shuffle',
    notify: 'icon-bell',
    rollback: 'icon-rotate-ccw',
    cleanup: 'icon-trash',
    block: 'icon-shield',
    archive: 'icon-archive',
    monitor: 'icon-eye',
    log: 'icon-file-text'
  }
  return icons[type] || 'icon-play'
}

/**
 * 获取成功率样式类
 */
const getSuccessRateClass = (rate) => {
  if (rate >= 95) return 'excellent'
  if (rate >= 90) return 'good'
  if (rate >= 80) return 'normal'
  return 'warning'
}

/**
 * 格式化时间
 */
const formatTime = (datetime) => {
  if (!datetime) return '从未'
  
  const now = new Date()
  const diff = now - datetime
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

/**
 * 切换下拉菜单
 */
const toggleDropdown = (policyId) => {
  activeDropdown.value = activeDropdown.value === policyId ? null : policyId
}

/**
 * 切换策略状态
 */
const togglePolicy = (policy) => {
  console.log('切换策略状态:', policy)
}

/**
 * 编辑策略
 */
const editPolicy = (policy) => {
  editingPolicy.value = { ...policy }
  showEditModal.value = true
  activeDropdown.value = null
}

/**
 * 复制策略
 */
const duplicatePolicy = (policy) => {
  console.log('复制策略:', policy)
  activeDropdown.value = null
}

/**
 * 导出策略
 */
const exportPolicy = (policy) => {
  console.log('导出策略:', policy)
  activeDropdown.value = null
}

/**
 * 删除策略
 */
const deletePolicy = (policy) => {
  console.log('删除策略:', policy)
  activeDropdown.value = null
}

/**
 * 创建策略
 */
const createPolicy = () => {
  editingPolicy.value = {
    id: null,
    name: '',
    category: 'performance',
    priority: 'medium',
    description: '',
    conditions: [
      { id: 1, metric: 'cpu', operator: '>', value: '80' }
    ],
    actions: [
      { id: 1, type: 'restart', name: '重启服务', config: '{}' }
    ]
  }
  showEditModal.value = true
}

/**
 * 导入策略
 */
const importPolicies = () => {
  console.log('导入策略')
}

/**
 * 导出策略
 */
const exportPolicies = () => {
  console.log('导出策略')
}

/**
 * 关闭编辑弹窗
 */
const closeEditModal = () => {
  showEditModal.value = false
  editingPolicy.value = {
    id: null,
    name: '',
    category: 'performance',
    priority: 'medium',
    description: '',
    conditions: [
      { id: 1, metric: 'cpu', operator: '>', value: '80' }
    ],
    actions: [
      { id: 1, type: 'restart', name: '重启服务', config: '{}' }
    ]
  }
}

/**
 * 保存策略
 */
const savePolicy = () => {
  console.log('保存策略:', editingPolicy.value)
  closeEditModal()
}

/**
 * 添加条件
 */
const addCondition = () => {
  const newId = Math.max(...editingPolicy.value.conditions.map(c => c.id)) + 1
  editingPolicy.value.conditions.push({
    id: newId,
    metric: 'cpu',
    operator: '>',
    value: '80'
  })
}

/**
 * 移除条件
 */
const removeCondition = (index) => {
  editingPolicy.value.conditions.splice(index, 1)
}

/**
 * 添加动作
 */
const addAction = () => {
  const newId = Math.max(...editingPolicy.value.actions.map(a => a.id)) + 1
  editingPolicy.value.actions.push({
    id: newId,
    type: 'restart',
    name: '重启服务',
    config: '{}'
  })
}

/**
 * 移除动作
 */
const removeAction = (index) => {
  editingPolicy.value.actions.splice(index, 1)
}

/**
 * 切换页面
 */
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.policy-management {
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

// 策略概览
.policy-overview {
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
  
  &.success-rate {
    border-left-color: $info-color;
    
    .card-icon {
      background: rgba($info-color, 0.1);
      color: $info-color;
    }
  }
  
  &.executions {
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
  
  &.neutral {
    color: $text-color-light;
  }
}

// 筛选区域
.filter-section {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  padding: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.filter-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-lg;
}

.filter-left {
  display: flex;
  gap: $spacing-md;
  flex: 1;
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

.filter-right {
  display: flex;
  gap: $spacing-md;
  align-items: center;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  
  .icon-search {
    position: absolute;
    left: $spacing-sm;
    color: $text-color-light;
    font-size: 14px;
  }
}

.search-input {
  padding: $spacing-sm $spacing-sm $spacing-sm 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  font-size: 13px;
  width: 250px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
  
  &::placeholder {
    color: $text-color-light;
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
  
  &:hover {
    background: $background-color-light;
  }
  
  &.active {
    background: $primary-color;
    color: $white;
  }
}

// 策略列表
.policy-list {
  margin-bottom: $spacing-xl;
}

// 网格视图
.policy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: $spacing-lg;
}

.policy-card {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
  border-left: 4px solid;
  transition: all 0.2s ease;
  
  &:hover {
    box-shadow: $shadow-md;
    transform: translateY(-2px);
  }
  
  &.performance {
    border-left-color: $primary-color;
  }
  
  &.availability {
    border-left-color: $success-color;
  }
  
  &.security {
    border-left-color: $danger-color;
  }
  
  &.resource {
    border-left-color: $warning-color;
  }
}

.card-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: $spacing-md;
}

.policy-info {
  flex: 1;
}

.policy-name {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-xs;
}

.policy-category {
  font-size: 12px;
  color: $text-color-secondary;
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  display: inline-block;
}

.policy-actions {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
}

.policy-toggle {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 20px;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
  }
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: $border-color;
  transition: 0.3s;
  border-radius: 20px;
  
  &:before {
    position: absolute;
    content: "";
    height: 14px;
    width: 14px;
    left: 3px;
    bottom: 3px;
    background-color: $white;
    transition: 0.3s;
    border-radius: 50%;
  }
  
  input:checked + & {
    background-color: $primary-color;
  }
  
  input:checked + &:before {
    transform: translateX(20px);
  }
}

.action-dropdown {
  position: relative;
}

.action-btn {
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
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: $white;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  box-shadow: $shadow-md;
  z-index: 10;
  min-width: 120px;
  padding: $spacing-xs 0;
}

.dropdown-item {
  width: 100%;
  padding: $spacing-sm $spacing-md;
  border: none;
  background: none;
  color: $text-color;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 13px;
  
  &:hover {
    background: $background-color-light;
  }
  
  &.danger {
    color: $danger-color;
    
    &:hover {
      background: rgba($danger-color, 0.1);
    }
  }
}

.card-content {
  padding: $spacing-lg;
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.policy-description {
  color: $text-color-secondary;
  line-height: 1.5;
  font-size: 14px;
}

.policy-priority {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
}

.priority-label {
  font-size: 13px;
  color: $text-color-light;
}

.priority-badge {
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
  
  &.high {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.medium {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.low {
    background: rgba($info-color, 0.1);
    color: $info-color;
  }
}

.policy-conditions {
  .conditions-title {
    font-size: 13px;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
}

.conditions-preview {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
}

.condition-tag {
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  font-size: 11px;
  color: $text-color-secondary;
}

.condition-more {
  padding: $spacing-xs $spacing-sm;
  background: rgba($primary-color, 0.1);
  color: $primary-color;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
}

.policy-actions-list {
  .actions-title {
    font-size: 13px;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
}

.actions-preview {
  display: flex;
  flex-wrap: wrap;
  gap: $spacing-xs;
}

.action-tag {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  padding: $spacing-xs $spacing-sm;
  background: $background-color-light;
  border-radius: $border-radius-sm;
  font-size: 11px;
  color: $text-color-secondary;
}

.action-more {
  padding: $spacing-xs $spacing-sm;
  background: rgba($primary-color, 0.1);
  color: $primary-color;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
}

.card-footer {
  padding: $spacing-lg;
  border-top: 1px solid $border-color-light;
  background: $background-color-light;
}

.policy-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  
  &.excellent {
    color: $success-color;
  }
  
  &.good {
    color: $info-color;
  }
  
  &.normal {
    color: $warning-color;
  }
  
  &.warning {
    color: $danger-color;
  }
}

.stat-label {
  font-size: 11px;
  color: $text-color-light;
}

// 列表视图
.policy-table {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr 1fr 1fr 1fr;
  background: $background-color-light;
  border-bottom: 1px solid $border-color-light;
}

.header-cell {
  padding: $spacing-md;
  font-size: 13px;
  font-weight: 600;
  color: $text-color;
  border-right: 1px solid $border-color-light;
  
  &:last-child {
    border-right: none;
  }
}

.table-body {
  display: flex;
  flex-direction: column;
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr 1.5fr 1fr 1fr 1fr;
  border-bottom: 1px solid $border-color-light;
  transition: background-color 0.2s ease;
  
  &:hover {
    background: rgba($primary-color, 0.02);
  }
  
  &:last-child {
    border-bottom: none;
  }
  
  &.high {
    border-left: 3px solid $danger-color;
  }
  
  &.medium {
    border-left: 3px solid $warning-color;
  }
  
  &.low {
    border-left: 3px solid $info-color;
  }
}

.table-cell {
  padding: $spacing-md;
  font-size: 13px;
  border-right: 1px solid $border-color-light;
  display: flex;
  align-items: center;
  
  &:last-child {
    border-right: none;
  }
  
  &.name {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-xs;
  }
}

.policy-info {
  .policy-name {
    font-weight: 500;
    color: $text-color;
    margin-bottom: 2px;
  }
  
  .policy-description {
    color: $text-color-light;
    font-size: 11px;
    line-height: 1.3;
  }
}

.category-badge {
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius-sm;
  font-size: 11px;
  font-weight: 500;
  
  &.performance {
    background: rgba($primary-color, 0.1);
    color: $primary-color;
  }
  
  &.availability {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.security {
    background: rgba($danger-color, 0.1);
    color: $danger-color;
  }
  
  &.resource {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
}

.conditions-count,
.actions-count {
  font-weight: 500;
  color: $text-color;
  margin-bottom: 2px;
}

.conditions-preview,
.actions-preview {
  color: $text-color-light;
  font-size: 11px;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stats-grid {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.stat-item {
  display: flex;
  gap: $spacing-xs;
  align-items: center;
  font-size: 11px;
}

.stat-label {
  color: $text-color-light;
}

.stat-value {
  font-weight: 500;
  color: $text-color;
}

.operation-buttons {
  display: flex;
  gap: $spacing-xs;
}

.operation-btn {
  width: 24px;
  height: 24px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.danger {
    &:hover {
      border-color: $danger-color;
      color: $danger-color;
    }
  }
}

// 分页
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: $spacing-sm;
  margin-top: $spacing-lg;
}

.page-btn {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover:not(:disabled) {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.page-numbers {
  display: flex;
  gap: $spacing-xs;
}

.page-number {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.active {
    background: $primary-color;
    border-color: $primary-color;
    color: $white;
  }
}

// 弹窗样式
.modal-overlay {
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
  overflow: hidden;
  display: flex;
  flex-direction: column;
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
  font-size: 18px;
  font-weight: 600;
  color: $text-color;
}

.modal-close {
  width: 32px;
  height: 32px;
  border: none;
  background: none;
  color: $text-color-secondary;
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
  padding: $spacing-lg;
  overflow-y: auto;
  flex: 1;
}

-section {
  margin-bottom: $spacing-xl;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
  margin-bottom: $spacing-md;
  padding-bottom: $spacing-sm;
  border-bottom: 1px solid $border-color-light;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-md;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  
  &.full-width {
    grid-column: 1 / -1;
  }
}

.form-label {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
}

.form-input,
.form-select,
.form-textarea {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius-md;
  background: $white;
  color: $text-color;
  font-size: 13px;
  transition: border-color 0.2s ease;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.conditions-editor,
.actions-editor {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.condition-item,
.action-item {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: $spacing-sm;
  align-items: start;
  padding: $spacing-md;
  background: $background-color-light;
  border-radius: $border-radius-md;
  border: 1px solid $border-color-light;
}

.action-item {
  grid-template-columns: 1fr 1fr 2fr auto;
}

.condition-select,
.condition-input,
.action-select,
.action-input {
  padding: $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color;
  font-size: 12px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.action-config {
  grid-column: 1 / -2;
  margin-top: $spacing-sm;
  padding: $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color;
  font-size: 12px;
  resize: vertical;
  min-height: 60px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.condition-remove,
.action-remove {
  width: 24px;
  height: 24px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: $danger-color;
    color: $danger-color;
  }
}

.add-condition,
.add-action {
  padding: $spacing-sm $spacing-md;
  border: 1px dashed $border-color;
  border-radius: $border-radius-md;
  background: none;
  color: $text-color-secondary;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  font-size: 13px;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
    background: rgba($primary-color, 0.02);
  }
}

.modal-footer {
  padding: $spacing-lg;
  border-top: 1px solid $border-color-light;
  display: flex;
  justify-content: flex-end;
  gap: $spacing-md;
}

// 按钮样式
.btn {
  padding: $spacing-sm $spacing-md;
  border: 1px solid;
  border-radius: $border-radius-md;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  text-decoration: none;
  
  &.btn-primary {
    background: $primary-color;
    border-color: $primary-color;
    color: $white;
    
    &:hover {
      background: darken($primary-color, 5%);
      border-color: darken($primary-color, 5%);
    }
  }
  
  &.btn-outline {
    background: $white;
    border-color: $border-color;
    color: $text-color;
    
    &:hover {
      border-color: $primary-color;
      color: $primary-color;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .policy-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
  
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
}

@media (max-width: 768px) {
  .policy-management {
    padding: $spacing-md;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .header-right {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
  
  .overview-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: $spacing-md;
  }
  
  .overview-card {
    padding: $spacing-md;
    flex-direction: column;
    text-align: center;
    gap: $spacing-sm;
  }
  
  .card-icon {
    width: 48px;
    height: 48px;
    font-size: 20px;
  }
  
  .card-value {
    font-size: 24px;
  }
  
  .filter-content {
    flex-direction: column;
    gap: $spacing-md;
  }
  
  .filter-left {
    flex-wrap: wrap;
  }
  
  .filter-right {
    justify-content: space-between;
  }
  
  .search-input {
    width: 200px;
  }
  
  .policy-grid {
    grid-template-columns: 1fr;
  }
  
  .policy-table {
    overflow-x: auto;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 200px 100px 80px 150px 150px 100px 80px 100px;
    min-width: 860px;
  }
  
  .modal-overlay {
    padding: $spacing-md;
  }
  
  .modal-content {
    max-width: none;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .condition-item,
  .action-item {
    grid-template-columns: 1fr;
    gap: $spacing-sm;
  }
  
  .action-config {
    grid-column: 1;
    margin-top: $spacing-sm;
  }
}

@media (max-width: 480px) {
  .policy-management {
    padding: $spacing-sm;
  }
  
  .page-title {
    font-size: 24px;
  }
  
  .header-right {
    gap: $spacing-sm;
  }
  
  .btn {
    padding: $spacing-xs $spacing-sm;
    font-size: 12px;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .overview-card {
    padding: $spacing-sm;
  }
  
  .card-value {
    font-size: 20px;
  }
  
  .filter-left {
    gap: $spacing-sm;
  }
  
  .filter-select {
    min-width: 100px;
    font-size: 12px;
  }
  
  .search-input {
    width: 150px;
    font-size: 12px;
  }
  
  .policy-card {
    margin-bottom: $spacing-md;
  }
  
  .card-header,
  .card-content,
  .card-footer {
    padding: $spacing-md;
  }
  
  .policy-name {
    font-size: 14px;
  }
  
  .policy-description {
    font-size: 12px;
  }
  
  .modal-header,
  .modal-body,
  .modal-footer {
    padding: $spacing-md;
  }
  
  .modal-title {
    font-size: 16px;
  }
}
</style>