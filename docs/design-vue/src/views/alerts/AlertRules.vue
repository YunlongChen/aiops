<!--
  告警规则管理页面
  提供告警规则的创建、编辑、删除等功能
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="alert-rules">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">告警规则</h1>
          <p class="page-description">配置和管理系统监控告警规则</p>
        </div>
        <div class="header-right">
          <button class="btn btn-outline" @click="importRules">
            <i class="icon-upload"></i>
            导入规则
          </button>
          <button class="btn btn-outline" @click="exportRules">
            <i class="icon-download"></i>
            导出规则
          </button>
          <button class="btn btn-primary" @click="createRule">
            <i class="icon-plus"></i>
            新建规则
          </button>
        </div>
      </div>
    </div>

    <!-- 规则统计 -->
    <div class="rules-stats">
      <div class="stats-grid">
        <div class="stat-card active">
          <div class="stat-icon">
            <i class="icon-play-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ ruleStats.active }}</div>
            <div class="stat-label">启用规则</div>
          </div>
        </div>
        <div class="stat-card inactive">
          <div class="stat-icon">
            <i class="icon-pause-circle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ ruleStats.inactive }}</div>
            <div class="stat-label">禁用规则</div>
          </div>
        </div>
        <div class="stat-card triggered">
          <div class="stat-icon">
            <i class="icon-alert-triangle"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ ruleStats.triggered }}</div>
            <div class="stat-label">已触发</div>
          </div>
        </div>
        <div class="stat-card total">
          <div class="stat-icon">
            <i class="icon-layers"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ ruleStats.total }}</div>
            <div class="stat-label">总规则数</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="filter-row">
        <div class="filter-group">
          <label class="filter-label">规则类型</label>
          <select v-model="selectedType" class="filter-select">
            <option value="">全部类型</option>
            <option value="system">系统监控</option>
            <option value="application">应用监控</option>
            <option value="network">网络监控</option>
            <option value="business">业务监控</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">规则状态</label>
          <select v-model="selectedStatus" class="filter-select">
            <option value="">全部状态</option>
            <option value="active">启用</option>
            <option value="inactive">禁用</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">严重级别</label>
          <select v-model="selectedSeverity" class="filter-select">
            <option value="">全部级别</option>
            <option value="critical">严重</option>
            <option value="warning">警告</option>
            <option value="info">信息</option>
          </select>
        </div>
        <div class="filter-group search-group">
          <div class="search-input">
            <i class="icon-search"></i>
            <input 
              type="text" 
              v-model="searchQuery"
              placeholder="搜索规则名称、描述..."
              @input="handleSearch"
            >
            <button v-if="searchQuery" class="clear-btn" @click="clearSearch">
              <i class="icon-x"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 规则列表 -->
    <div class="rules-list">
      <div class="list-header">
        <div class="list-controls">
          <div class="bulk-actions">
            <input 
              type="checkbox" 
              v-model="selectAll"
              @change="toggleSelectAll"
              class="bulk-checkbox"
            >
            <span class="selected-count" v-if="selectedRules.length > 0">
              已选择 {{ selectedRules.length }} 项
            </span>
          </div>
          <div class="batch-actions" v-if="selectedRules.length > 0">
            <button class="btn btn-sm btn-outline" @click="batchEnable">
              <i class="icon-play"></i>
              批量启用
            </button>
            <button class="btn btn-sm btn-outline" @click="batchDisable">
              <i class="icon-pause"></i>
              批量禁用
            </button>
            <button class="btn btn-sm btn-danger" @click="batchDelete">
              <i class="icon-trash"></i>
              批量删除
            </button>
          </div>
        </div>
      </div>

      <div class="table-container">
        <table class="rules-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <input 
                  type="checkbox" 
                  v-model="selectAll"
                  @change="toggleSelectAll"
                >
              </th>
              <th class="name-col">规则名称</th>
              <th class="type-col">类型</th>
              <th class="condition-col">触发条件</th>
              <th class="severity-col">级别</th>
              <th class="status-col">状态</th>
              <th class="updated-col">更新时间</th>
              <th class="actions-col">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="rule in filteredRules" 
              :key="rule.id"
              class="rule-row"
              :class="{ selected: selectedRules.includes(rule.id) }"
            >
              <td class="checkbox-col">
                <input 
                  type="checkbox" 
                  :value="rule.id"
                  v-model="selectedRules"
                >
              </td>
              <td class="name-col">
                <div class="rule-name">
                  <span class="name-text">{{ rule.name }}</span>
                  <span class="rule-description">{{ rule.description }}</span>
                </div>
              </td>
              <td class="type-col">
                <StatusBadge 
                  :status="rule.type" 
                  :variant="getTypeVariant(rule.type)"
                />
              </td>
              <td class="condition-col">
                <div class="condition-info">
                  <span class="condition-text">{{ rule.condition }}</span>
                  <span class="threshold-text">阈值: {{ rule.threshold }}</span>
                </div>
              </td>
              <td class="severity-col">
                <StatusBadge 
                  :status="rule.severity" 
                  :variant="getSeverityVariant(rule.severity)"
                />
              </td>
              <td class="status-col">
                <div class="status-toggle">
                  <label class="switch">
                    <input 
                      type="checkbox" 
                      :checked="rule.status === 'active'"
                      @change="toggleRuleStatus(rule)"
                    >
                    <span class="slider"></span>
                  </label>
                </div>
              </td>
              <td class="updated-col">
                <div class="time-info">
                  <span class="update-time">{{ formatTime(rule.updatedAt) }}</span>
                  <span class="update-user">{{ rule.updatedBy }}</span>
                </div>
              </td>
              <td class="actions-col">
                <div class="action-buttons">
                  <button 
                    class="action-btn"
                    @click="viewRule(rule)"
                    title="查看详情"
                  >
                    <i class="icon-eye"></i>
                  </button>
                  <button 
                    class="action-btn"
                    @click="editRule(rule)"
                    title="编辑规则"
                  >
                    <i class="icon-edit"></i>
                  </button>
                  <button 
                    class="action-btn"
                    @click="duplicateRule(rule)"
                    title="复制规则"
                  >
                    <i class="icon-copy"></i>
                  </button>
                  <button 
                    class="action-btn danger"
                    @click="deleteRule(rule)"
                    title="删除规则"
                  >
                    <i class="icon-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-if="filteredRules.length === 0"
        icon="icon-alert-circle"
        title="暂无告警规则"
        description="还没有配置任何告警规则，点击新建规则开始配置"
        :actions="[
          { text: '新建规则', action: createRule },
          { text: '导入规则', action: importRules }
        ]"
      />
    </div>

    <!-- 分页 -->
    <div class="pagination" v-if="filteredRules.length > 0">
      <div class="pagination-info">
        显示第 {{ (currentPage - 1) * pageSize + 1 }} - {{ Math.min(currentPage * pageSize, totalRules) }} 条，
        共 {{ totalRules }} 条记录
      </div>
      <div class="pagination-controls">
        <button 
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <i class="icon-chevron-left"></i>
        </button>
        <span class="pagination-pages">
          <button 
            v-for="page in visiblePages" 
            :key="page"
            class="pagination-page"
            :class="{ active: page === currentPage }"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>
        </span>
        <button 
          class="pagination-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          <i class="icon-chevron-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 告警规则管理页面组件
 * 提供告警规则的创建、编辑、删除等功能
 */
import { ref, computed, onMounted } from 'vue'
import StatusBadge from '@components/common/StatusBadge.vue'
import EmptyState from '@components/common/EmptyState.vue'

// 响应式数据
const selectedType = ref('')
const selectedStatus = ref('')
const selectedSeverity = ref('')
const searchQuery = ref('')
const selectAll = ref(false)
const selectedRules = ref([])
const currentPage = ref(1)
const pageSize = ref(20)

// 规则统计数据
const ruleStats = ref({
  active: 24,
  inactive: 8,
  triggered: 5,
  total: 32
})

// 模拟规则数据
const rules = ref([
  {
    id: 1,
    name: 'CPU使用率告警',
    description: '当CPU使用率超过80%时触发告警',
    type: 'system',
    condition: 'cpu_usage > 80%',
    threshold: '80%',
    severity: 'warning',
    status: 'active',
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    updatedBy: '管理员'
  },
  {
    id: 2,
    name: '内存使用率告警',
    description: '当内存使用率超过90%时触发严重告警',
    type: 'system',
    condition: 'memory_usage > 90%',
    threshold: '90%',
    severity: 'critical',
    status: 'active',
    updatedAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    updatedBy: '运维团队'
  },
  {
    id: 3,
    name: '磁盘空间告警',
    description: '当磁盘使用率超过85%时触发告警',
    type: 'system',
    condition: 'disk_usage > 85%',
    threshold: '85%',
    severity: 'warning',
    status: 'active',
    updatedAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    updatedBy: '系统管理员'
  },
  {
    id: 4,
    name: '应用响应时间告警',
    description: '当应用响应时间超过2秒时触发告警',
    type: 'application',
    condition: 'response_time > 2s',
    threshold: '2秒',
    severity: 'warning',
    status: 'active',
    updatedAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
    updatedBy: '开发团队'
  },
  {
    id: 5,
    name: '网络连接数告警',
    description: '当网络连接数超过1000时触发告警',
    type: 'network',
    condition: 'connection_count > 1000',
    threshold: '1000',
    severity: 'info',
    status: 'inactive',
    updatedAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
    updatedBy: '网络管理员'
  },
  {
    id: 6,
    name: '业务订单量告警',
    description: '当订单量低于正常水平时触发告警',
    type: 'business',
    condition: 'order_count < 100/hour',
    threshold: '100/小时',
    severity: 'critical',
    status: 'active',
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    updatedBy: '业务团队'
  }
])

// 计算属性
const filteredRules = computed(() => {
  let filtered = rules.value

  // 类型筛选
  if (selectedType.value) {
    filtered = filtered.filter(rule => rule.type === selectedType.value)
  }

  // 状态筛选
  if (selectedStatus.value) {
    filtered = filtered.filter(rule => rule.status === selectedStatus.value)
  }

  // 级别筛选
  if (selectedSeverity.value) {
    filtered = filtered.filter(rule => rule.severity === selectedSeverity.value)
  }

  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(rule => 
      rule.name.toLowerCase().includes(query) ||
      rule.description.toLowerCase().includes(query)
    )
  }

  return filtered
})

const totalRules = computed(() => filteredRules.value.length)
const totalPages = computed(() => Math.ceil(totalRules.value / pageSize.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

/**
 * 获取类型对应的变体
 */
const getTypeVariant = (type) => {
  const variants = {
    system: 'primary',
    application: 'success',
    network: 'info',
    business: 'warning'
  }
  return variants[type] || 'default'
}

/**
 * 获取严重级别对应的变体
 */
const getSeverityVariant = (severity) => {
  const variants = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return variants[severity] || 'default'
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
 * 处理搜索
 */
const handleSearch = () => {
  currentPage.value = 1
}

/**
 * 清除搜索
 */
const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
}

/**
 * 切换全选
 */
const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedRules.value = filteredRules.value.map(rule => rule.id)
  } else {
    selectedRules.value = []
  }
}

/**
 * 跳转到指定页面
 */
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

/**
 * 切换规则状态
 */
const toggleRuleStatus = (rule) => {
  rule.status = rule.status === 'active' ? 'inactive' : 'active'
  rule.updatedAt = new Date()
  console.log('切换规则状态:', rule)
}

/**
 * 创建规则
 */
const createRule = () => {
  console.log('创建规则')
}

/**
 * 查看规则详情
 */
const viewRule = (rule) => {
  console.log('查看规则详情:', rule)
}

/**
 * 编辑规则
 */
const editRule = (rule) => {
  console.log('编辑规则:', rule)
}

/**
 * 复制规则
 */
const duplicateRule = (rule) => {
  const newRule = {
    ...rule,
    id: Date.now(),
    name: rule.name + ' (副本)',
    status: 'inactive',
    updatedAt: new Date(),
    updatedBy: '当前用户'
  }
  rules.value.unshift(newRule)
  console.log('复制规则:', newRule)
}

/**
 * 删除规则
 */
const deleteRule = (rule) => {
  if (confirm('确定要删除这个规则吗？')) {
    const index = rules.value.findIndex(r => r.id === rule.id)
    if (index > -1) {
      rules.value.splice(index, 1)
    }
  }
}

/**
 * 导入规则
 */
const importRules = () => {
  console.log('导入规则')
}

/**
 * 导出规则
 */
const exportRules = () => {
  console.log('导出规则')
}

/**
 * 批量启用
 */
const batchEnable = () => {
  selectedRules.value.forEach(id => {
    const rule = rules.value.find(r => r.id === id)
    if (rule) {
      rule.status = 'active'
      rule.updatedAt = new Date()
    }
  })
  selectedRules.value = []
  selectAll.value = false
}

/**
 * 批量禁用
 */
const batchDisable = () => {
  selectedRules.value.forEach(id => {
    const rule = rules.value.find(r => r.id === id)
    if (rule) {
      rule.status = 'inactive'
      rule.updatedAt = new Date()
    }
  })
  selectedRules.value = []
  selectAll.value = false
}

/**
 * 批量删除
 */
const batchDelete = () => {
  if (confirm(`确定要删除选中的 ${selectedRules.value.length} 个规则吗？`)) {
    rules.value = rules.value.filter(rule => !selectedRules.value.includes(rule.id))
    selectedRules.value = []
    selectAll.value = false
  }
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style lang="scss" scoped>
@import '@assets/styles/variables';

.alert-rules {
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

// 规则统计
.rules-stats {
  margin-bottom: $spacing-xl;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: $spacing-lg;
}

.stat-card {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  box-shadow: $shadow-sm;
  display: flex;
  align-items: center;
  gap: $spacing-md;
  border-left: 4px solid;
  
  &.active {
    border-left-color: $success-color;
    
    .stat-icon {
      background: rgba($success-color, 0.1);
      color: $success-color;
    }
  }
  
  &.inactive {
    border-left-color: $text-color-light;
    
    .stat-icon {
      background: rgba($text-color-light, 0.1);
      color: $text-color-light;
    }
  }
  
  &.triggered {
    border-left-color: $danger-color;
    
    .stat-icon {
      background: rgba($danger-color, 0.1);
      color: $danger-color;
    }
  }
  
  &.total {
    border-left-color: $primary-color;
    
    .stat-icon {
      background: rgba($primary-color, 0.1);
      color: $primary-color;
    }
  }
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: $border-radius-md;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: $text-color;
  line-height: 1;
  margin-bottom: $spacing-xs;
}

.stat-label {
  font-size: 13px;
  color: $text-color-secondary;
}

// 筛选区域
.filter-section {
  background: $white;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  margin-bottom: $spacing-lg;
  box-shadow: $shadow-sm;
}

.filter-row {
  display: flex;
  gap: $spacing-lg;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
  
  &.search-group {
    flex: 1;
    min-width: 200px;
  }
}

.filter-label {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
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
  
  .clear-btn {
    position: absolute;
    right: $spacing-sm;
    width: 20px;
    height: 20px;
    border: none;
    background: $text-color-light;
    color: $white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 10px;
    
    &:hover {
      background: $text-color-secondary;
    }
  }
}

// 规则列表
.rules-list {
  background: $white;
  border-radius: $border-radius-lg;
  box-shadow: $shadow-sm;
  overflow: hidden;
}

.list-header {
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
}

.list-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: $spacing-lg;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.bulk-checkbox {
  margin: 0;
}

.selected-count {
  font-size: 13px;
  color: $text-color-secondary;
}

.batch-actions {
  display: flex;
  gap: $spacing-sm;
}

// 表格
.table-container {
  overflow-x: auto;
}

.rules-table {
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: $spacing-md;
    text-align: left;
    border-bottom: 1px solid $border-color-light;
  }
  
  th {
    background: $background-color-light;
    font-weight: 600;
    color: $text-color;
    font-size: 13px;
  }
  
  .checkbox-col {
    width: 40px;
  }
  
  .name-col {
    min-width: 250px;
  }
  
  .type-col {
    width: 100px;
  }
  
  .condition-col {
    min-width: 200px;
  }
  
  .severity-col {
    width: 80px;
  }
  
  .status-col {
    width: 80px;
  }
  
  .updated-col {
    width: 120px;
  }
  
  .actions-col {
    width: 140px;
  }
}

.rule-row {
  transition: background-color 0.2s ease;
  
  &:hover {
    background: $background-color-light;
  }
  
  &.selected {
    background: rgba($primary-color, 0.05);
  }
}

.rule-name {
  .name-text {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .rule-description {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
    line-height: 1.4;
  }
}

.condition-info {
  .condition-text {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
    font-family: monospace;
    font-size: 12px;
  }
  
  .threshold-text {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
  }
}

.status-toggle {
  .switch {
    position: relative;
    display: inline-block;
    width: 44px;
    height: 24px;
    
    input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: $border-color;
      transition: 0.3s;
      border-radius: 24px;
      
      &:before {
        position: absolute;
        content: "";
        height: 18px;
        width: 18px;
        left: 3px;
        bottom: 3px;
        background-color: $white;
        transition: 0.3s;
        border-radius: 50%;
      }
    }
    
    input:checked + .slider {
      background-color: $success-color;
    }
    
    input:checked + .slider:before {
      transform: translateX(20px);
    }
  }
}

.time-info {
  .update-time {
    display: block;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .update-user {
    display: block;
    font-size: 12px;
    color: $text-color-secondary;
  }
}

.action-buttons {
  display: flex;
  gap: $spacing-xs;
}

.action-btn {
  width: 28px;
  height: 28px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 12px;
  
  &:hover {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &.danger:hover {
    border-color: $danger-color;
    color: $danger-color;
  }
}

// 分页
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: $spacing-lg;
  background: $white;
  border-radius: $border-radius-lg;
  margin-top: $spacing-lg;
  box-shadow: $shadow-sm;
}

.pagination-info {
  font-size: 13px;
  color: $text-color-secondary;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover:not(:disabled) {
    border-color: $primary-color;
    color: $primary-color;
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.pagination-pages {
  display: flex;
  gap: $spacing-xs;
}

.pagination-page {
  width: 32px;
  height: 32px;
  border: 1px solid $border-color;
  border-radius: $border-radius-sm;
  background: $white;
  color: $text-color-secondary;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
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

// 响应式设计
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .alert-rules {
    padding: $spacing-md;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-right {
    justify-content: flex-end;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    &.search-group {
      min-width: auto;
    }
  }
  
  .list-controls {
    flex-direction: column;
    align-items: stretch;
    gap: $spacing-md;
  }
  
  .batch-actions {
    justify-content: center;
  }
  
  .table-container {
    font-size: 12px;
    
    th, td {
      padding: $spacing-sm;
    }
  }
  
  .pagination {
    flex-direction: column;
    gap: $spacing-md;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .header-right {
    flex-direction: column;
    gap: $spacing-sm;
    
    .btn {
      width: 100%;
    }
  }
}
</style>