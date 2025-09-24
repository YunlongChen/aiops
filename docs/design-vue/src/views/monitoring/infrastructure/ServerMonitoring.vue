<!--
  服务器监控页面
  显示服务器详细监控信息和状态
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="server-monitoring">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">服务器监控</h1>
        <p class="page-subtitle">实时监控服务器性能和状态</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="refreshData">
          <i class="icon-refresh-cw"></i>
          刷新
        </button>
        <button class="btn btn-primary" @click="showAddServer">
          <i class="icon-plus"></i>
          添加服务器
        </button>
      </div>
    </div>
    
    <!-- 筛选和搜索 -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="filter-group">
          <label class="filter-label">状态筛选</label>
          <select v-model="statusFilter" class="filter-select">
            <option value="">全部状态</option>
            <option value="online">在线</option>
            <option value="offline">离线</option>
            <option value="warning">警告</option>
            <option value="error">异常</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">环境筛选</label>
          <select v-model="environmentFilter" class="filter-select">
            <option value="">全部环境</option>
            <option value="production">生产环境</option>
            <option value="staging">测试环境</option>
            <option value="development">开发环境</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">搜索</label>
          <div class="search-input">
            <i class="icon-search"></i>
            <input
              type="text"
              v-model="searchQuery"
              placeholder="搜索服务器名称或IP..."
              class="search-field"
            />
          </div>
        </div>
      </div>
    </div>
    
    <!-- 服务器概览统计 -->
    <div class="overview-stats">
      <div class="stat-card" v-for="stat in serverStats" :key="stat.key">
        <div class="stat-icon" :class="stat.iconClass">
          <i :class="stat.icon"></i>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>
    
    <!-- 服务器列表 -->
    <div class="servers-section">
      <div class="section-header">
        <h2 class="section-title">服务器列表</h2>
        <div class="view-controls">
          <button
            class="view-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
          >
            <i class="icon-grid"></i>
          </button>
          <button
            class="view-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            <i class="icon-list"></i>
          </button>
        </div>
      </div>
      
      <!-- 网格视图 -->
      <div v-if="viewMode === 'grid'" class="servers-grid">
        <div
          v-for="server in filteredServers"
          :key="server.id"
          class="server-card"
          @click="showServerDetail(server)"
        >
          <div class="server-header">
            <div class="server-info">
              <h3 class="server-name">{{ server.name }}</h3>
              <p class="server-ip">{{ server.ip }}</p>
            </div>
            <StatusBadge :status="server.status" :animated="true" />
          </div>
          
          <div class="server-metrics">
            <div class="metric-item">
              <div class="metric-label">CPU</div>
              <div class="metric-bar">
                <div
                  class="metric-fill cpu"
                  :style="{ width: server.cpu + '%' }"
                ></div>
              </div>
              <div class="metric-value">{{ server.cpu }}%</div>
            </div>
            
            <div class="metric-item">
              <div class="metric-label">内存</div>
              <div class="metric-bar">
                <div
                  class="metric-fill memory"
                  :style="{ width: server.memory + '%' }"
                ></div>
              </div>
              <div class="metric-value">{{ server.memory }}%</div>
            </div>
            
            <div class="metric-item">
              <div class="metric-label">磁盘</div>
              <div class="metric-bar">
                <div
                  class="metric-fill disk"
                  :style="{ width: server.disk + '%' }"
                ></div>
              </div>
              <div class="metric-value">{{ server.disk }}%</div>
            </div>
          </div>
          
          <div class="server-footer">
            <div class="server-tags">
              <span class="tag" :class="'tag-' + server.environment">
                {{ getEnvironmentLabel(server.environment) }}
              </span>
              <span class="tag tag-gray">{{ server.os }}</span>
            </div>
            <div class="server-uptime">
              运行时间: {{ server.uptime }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- 列表视图 -->
      <div v-else class="servers-table">
        <table class="table">
          <thead>
            <tr>
              <th>服务器</th>
              <th>状态</th>
              <th>CPU</th>
              <th>内存</th>
              <th>磁盘</th>
              <th>网络</th>
              <th>环境</th>
              <th>运行时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="server in filteredServers" :key="server.id">
              <td>
                <div class="server-cell">
                  <div class="server-name">{{ server.name }}</div>
                  <div class="server-ip">{{ server.ip }}</div>
                </div>
              </td>
              <td>
                <StatusBadge :status="server.status" :animated="true" />
              </td>
              <td>
                <div class="metric-cell">
                  <div class="metric-bar-small">
                    <div
                      class="metric-fill-small cpu"
                      :style="{ width: server.cpu + '%' }"
                    ></div>
                  </div>
                  <span class="metric-text">{{ server.cpu }}%</span>
                </div>
              </td>
              <td>
                <div class="metric-cell">
                  <div class="metric-bar-small">
                    <div
                      class="metric-fill-small memory"
                      :style="{ width: server.memory + '%' }"
                    ></div>
                  </div>
                  <span class="metric-text">{{ server.memory }}%</span>
                </div>
              </td>
              <td>
                <div class="metric-cell">
                  <div class="metric-bar-small">
                    <div
                      class="metric-fill-small disk"
                      :style="{ width: server.disk + '%' }"
                    ></div>
                  </div>
                  <span class="metric-text">{{ server.disk }}%</span>
                </div>
              </td>
              <td>
                <div class="network-cell">
                  <div class="network-item">
                    <i class="icon-arrow-down text-success"></i>
                    {{ server.networkIn }} MB/s
                  </div>
                  <div class="network-item">
                    <i class="icon-arrow-up text-primary"></i>
                    {{ server.networkOut }} MB/s
                  </div>
                </div>
              </td>
              <td>
                <span class="tag" :class="'tag-' + server.environment">
                  {{ getEnvironmentLabel(server.environment) }}
                </span>
              </td>
              <td>{{ server.uptime }}</td>
              <td>
                <div class="action-buttons">
                  <button
                    class="btn-icon"
                    @click.stop="showServerDetail(server)"
                    title="查看详情"
                  >
                    <i class="icon-eye"></i>
                  </button>
                  <button
                    class="btn-icon"
                    @click.stop="editServer(server)"
                    title="编辑"
                  >
                    <i class="icon-edit"></i>
                  </button>
                  <button
                    class="btn-icon text-error"
                    @click.stop="deleteServer(server)"
                    title="删除"
                  >
                    <i class="icon-trash-2"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 空状态 -->
      <EmptyState
        v-if="filteredServers.length === 0"
        icon="icon-server"
        title="暂无服务器"
        description="没有找到符合条件的服务器"
        :actions="[
          { id: 'add', title: '添加服务器', icon: 'icon-plus', type: 'primary' },
          { id: 'clear', title: '清除筛选', icon: 'icon-x', type: 'outline' }
        ]"
        @action="handleEmptyAction"
      />
    </div>
  </div>
</template>

<script setup>
/**
 * 服务器监控页面组件
 * 显示服务器列表和监控信息
 */
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()

// 响应式数据
const viewMode = ref('grid')
const statusFilter = ref('')
const environmentFilter = ref('')
const searchQuery = ref('')

// 服务器统计数据
const serverStats = reactive([
  {
    key: 'total',
    icon: 'icon-server',
    iconClass: 'stat-icon-blue',
    value: '156',
    label: '总服务器数'
  },
  {
    key: 'online',
    icon: 'icon-check-circle',
    iconClass: 'stat-icon-green',
    value: '142',
    label: '在线服务器'
  },
  {
    key: 'warning',
    icon: 'icon-alert-triangle',
    iconClass: 'stat-icon-orange',
    value: '8',
    label: '警告状态'
  },
  {
    key: 'offline',
    icon: 'icon-x-circle',
    iconClass: 'stat-icon-red',
    value: '6',
    label: '离线服务器'
  }
])

// 模拟服务器数据
const servers = reactive([
  {
    id: 1,
    name: 'web-server-01',
    ip: '192.168.1.10',
    status: 'online',
    cpu: 65,
    memory: 78,
    disk: 45,
    networkIn: 12.5,
    networkOut: 8.3,
    environment: 'production',
    os: 'Ubuntu 20.04',
    uptime: '15天 8小时'
  },
  {
    id: 2,
    name: 'db-server-01',
    ip: '192.168.1.20',
    status: 'warning',
    cpu: 85,
    memory: 92,
    disk: 67,
    networkIn: 25.8,
    networkOut: 15.2,
    environment: 'production',
    os: 'CentOS 8',
    uptime: '32天 12小时'
  },
  {
    id: 3,
    name: 'app-server-01',
    ip: '192.168.1.30',
    status: 'online',
    cpu: 45,
    memory: 56,
    disk: 34,
    networkIn: 8.9,
    networkOut: 6.7,
    environment: 'staging',
    os: 'Ubuntu 22.04',
    uptime: '7天 3小时'
  },
  {
    id: 4,
    name: 'cache-server-01',
    ip: '192.168.1.40',
    status: 'offline',
    cpu: 0,
    memory: 0,
    disk: 0,
    networkIn: 0,
    networkOut: 0,
    environment: 'production',
    os: 'Redis 6.2',
    uptime: '离线'
  },
  {
    id: 5,
    name: 'test-server-01',
    ip: '192.168.1.50',
    status: 'online',
    cpu: 23,
    memory: 34,
    disk: 12,
    networkIn: 2.1,
    networkOut: 1.8,
    environment: 'development',
    os: 'Ubuntu 20.04',
    uptime: '2天 15小时'
  }
])

// 计算属性
const filteredServers = computed(() => {
  let filtered = servers
  
  // 状态筛选
  if (statusFilter.value) {
    filtered = filtered.filter(server => server.status === statusFilter.value)
  }
  
  // 环境筛选
  if (environmentFilter.value) {
    filtered = filtered.filter(server => server.environment === environmentFilter.value)
  }
  
  // 搜索筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(server =>
      server.name.toLowerCase().includes(query) ||
      server.ip.includes(query)
    )
  }
  
  return filtered
})

/**
 * 获取环境标签
 */
const getEnvironmentLabel = (env) => {
  const labels = {
    production: '生产',
    staging: '测试',
    development: '开发'
  }
  return labels[env] || env
}

/**
 * 刷新数据
 */
const refreshData = async () => {
  try {
    // 模拟API调用
    console.log('刷新服务器数据...')
    
    // 模拟数据更新
    servers.forEach(server => {
      if (server.status !== 'offline') {
        server.cpu = Math.floor(Math.random() * 100)
        server.memory = Math.floor(Math.random() * 100)
        server.disk = Math.floor(Math.random() * 100)
        server.networkIn = Math.floor(Math.random() * 50 * 100) / 100
        server.networkOut = Math.floor(Math.random() * 30 * 100) / 100
      }
    })
  } catch (error) {
    console.error('刷新数据失败:', error)
  }
}

/**
 * 显示添加服务器对话框
 */
const showAddServer = () => {
  console.log('显示添加服务器对话框')
  // TODO: 实现添加服务器功能
}

/**
 * 显示服务器详情
 */
const showServerDetail = (server) => {
  console.log('显示服务器详情:', server.name)
  // TODO: 跳转到服务器详情页面
  router.push(`/monitoring/infrastructure/servers/${server.id}`)
}

/**
 * 编辑服务器
 */
const editServer = (server) => {
  console.log('编辑服务器:', server.name)
  // TODO: 实现编辑服务器功能
}

/**
 * 删除服务器
 */
const deleteServer = (server) => {
  console.log('删除服务器:', server.name)
  // TODO: 实现删除服务器功能
}

/**
 * 处理空状态操作
 */
const handleEmptyAction = (action) => {
  switch (action.id) {
    case 'add':
      showAddServer()
      break
    case 'clear':
      statusFilter.value = ''
      environmentFilter.value = ''
      searchQuery.value = ''
      break
  }
}

// 定时更新数据
let updateTimer = null
const startDataUpdate = () => {
  updateTimer = setInterval(() => {
    refreshData()
  }, 30000) // 30秒更新一次
}

const stopDataUpdate = () => {
  if (updateTimer) {
    clearInterval(updateTimer)
    updateTimer = null
  }
}

// 生命周期
onMounted(() => {
  startDataUpdate()
})

onUnmounted(() => {
  stopDataUpdate()
})
</script>

<style lang="scss" scoped>
@import '@/assets/styles/variables.scss';

.server-monitoring {
  padding: $spacing-lg;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: $spacing-xl;
}

.header-content {
  flex: 1;
}

.page-title {
  margin: 0 0 $spacing-xs 0;
  font-size: 28px;
  font-weight: 700;
  color: $text-color;
}

.page-subtitle {
  margin: 0;
  font-size: 16px;
  color: $text-color-secondary;
}

.header-actions {
  display: flex;
  gap: $spacing-sm;
}

// 筛选区域
.filters-section {
  margin-bottom: $spacing-xl;
  padding: $spacing-lg;
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
}

.filters-row {
  display: flex;
  gap: $spacing-lg;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.filter-label {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
}

.filter-select {
  padding: $spacing-sm $spacing-md;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  font-size: 14px;
  background: $white;
  color: $text-color;
  min-width: 150px;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.search-input {
  position: relative;
  
  .icon-search {
    position: absolute;
    left: $spacing-sm;
    top: 50%;
    transform: translateY(-50%);
    color: $text-color-light;
    font-size: 16px;
  }
  
  .search-field {
    padding: $spacing-sm $spacing-md $spacing-sm 36px;
    border: 1px solid $border-color;
    border-radius: $border-radius;
    font-size: 14px;
    background: $white;
    color: $text-color;
    min-width: 250px;
    
    &:focus {
      outline: none;
      border-color: $primary-color;
    }
    
    &::placeholder {
      color: $text-color-light;
    }
  }
}

// 概览统计
.overview-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
  margin-bottom: $spacing-xl;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: $spacing-lg;
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: $border-radius;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $spacing-md;
  
  i {
    font-size: 20px;
    color: $white;
  }
  
  &.stat-icon-blue {
    background: $primary-color;
  }
  
  &.stat-icon-green {
    background: $success-color;
  }
  
  &.stat-icon-orange {
    background: $warning-color;
  }
  
  &.stat-icon-red {
    background: $error-color;
  }
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
  font-size: 14px;
  color: $text-color-secondary;
}

// 服务器列表区域
.servers-section {
  background: $white;
  border-radius: $border-radius-lg;
  border: 1px solid $border-color-light;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-lg;
  border-bottom: 1px solid $border-color-light;
  background: $background-light;
}

.section-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: $text-color;
}

.view-controls {
  display: flex;
  gap: $spacing-xs;
}

.view-btn {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  background: $white;
  color: $text-color-light;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    color: $primary-color;
    border-color: $primary-color;
  }
  
  &.active {
    background: $primary-color;
    color: $white;
    border-color: $primary-color;
  }
}

// 网格视图
.servers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: $spacing-lg;
  padding: $spacing-lg;
}

.server-card {
  border: 1px solid $border-color-light;
  border-radius: $border-radius-lg;
  padding: $spacing-lg;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
    border-color: $primary-color;
  }
}

.server-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: $spacing-md;
}

.server-info {
  flex: 1;
}

.server-name {
  margin: 0 0 $spacing-xs 0;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.server-ip {
  margin: 0;
  font-size: 14px;
  color: $text-color-secondary;
  font-family: monospace;
}

.server-metrics {
  margin-bottom: $spacing-md;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-sm;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.metric-label {
  font-size: 13px;
  color: $text-color-secondary;
  min-width: 40px;
}

.metric-bar {
  flex: 1;
  height: 6px;
  background: $border-color-light;
  border-radius: 3px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
  
  &.cpu {
    background: linear-gradient(90deg, $primary-color, lighten($primary-color, 20%));
  }
  
  &.memory {
    background: linear-gradient(90deg, $success-color, lighten($success-color, 20%));
  }
  
  &.disk {
    background: linear-gradient(90deg, $warning-color, lighten($warning-color, 20%));
  }
}

.metric-value {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
  min-width: 35px;
  text-align: right;
}

.server-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.server-tags {
  display: flex;
  gap: $spacing-xs;
}

.tag {
  padding: $spacing-xs $spacing-sm;
  border-radius: $border-radius;
  font-size: 12px;
  font-weight: 500;
  
  &.tag-production {
    background: rgba($error-color, 0.1);
    color: $error-color;
  }
  
  &.tag-staging {
    background: rgba($warning-color, 0.1);
    color: $warning-color;
  }
  
  &.tag-development {
    background: rgba($success-color, 0.1);
    color: $success-color;
  }
  
  &.tag-gray {
    background: rgba($text-color-light, 0.1);
    color: $text-color-light;
  }
}

.server-uptime {
  font-size: 12px;
  color: $text-color-secondary;
}

// 列表视图
.servers-table {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
  
  th {
    padding: $spacing-md $spacing-lg;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    color: $text-color;
    border-bottom: 1px solid $border-color-light;
    background: $background-light;
  }
  
  td {
    padding: $spacing-md $spacing-lg;
    border-bottom: 1px solid $border-color-light;
    vertical-align: middle;
  }
  
  tr:hover {
    background: $background-light;
  }
}

.server-cell {
  .server-name {
    font-size: 14px;
    font-weight: 500;
    color: $text-color;
    margin-bottom: $spacing-xs;
  }
  
  .server-ip {
    font-size: 13px;
    color: $text-color-secondary;
    font-family: monospace;
  }
}

.metric-cell {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
}

.metric-bar-small {
  width: 60px;
  height: 4px;
  background: $border-color-light;
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill-small {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
  
  &.cpu {
    background: $primary-color;
  }
  
  &.memory {
    background: $success-color;
  }
  
  &.disk {
    background: $warning-color;
  }
}

.metric-text {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
  min-width: 35px;
}

.network-cell {
  font-size: 13px;
  
  .network-item {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    margin-bottom: $spacing-xs;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    i {
      font-size: 12px;
    }
  }
}

.action-buttons {
  display: flex;
  gap: $spacing-xs;
}

.btn-icon {
  padding: $spacing-xs;
  border: none;
  background: none;
  color: $text-color-light;
  cursor: pointer;
  border-radius: $border-radius;
  transition: all 0.3s ease;
  
  &:hover {
    background: $background-light;
    color: $text-color;
  }
  
  &.text-error:hover {
    color: $error-color;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .servers-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .server-monitoring {
    padding: $spacing-md;
  }
  
  .page-header {
    flex-direction: column;
    gap: $spacing-md;
    
    .header-actions {
      width: 100%;
      justify-content: flex-end;
    }
  }
  
  .filters-row {
    flex-direction: column;
    gap: $spacing-md;
    
    .filter-group {
      width: 100%;
    }
    
    .filter-select,
    .search-field {
      width: 100%;
      min-width: auto;
    }
  }
  
  .overview-stats {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: $spacing-md;
  }
  
  .servers-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
    padding: $spacing-md;
  }
  
  .server-card {
    padding: $spacing-md;
  }
  
  .servers-table {
    font-size: 13px;
    
    th,
    td {
      padding: $spacing-sm;
    }
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .page-subtitle {
    font-size: 14px;
  }
  
  .stat-card {
    padding: $spacing-md;
  }
  
  .stat-icon {
    width: 40px;
    height: 40px;
    margin-right: $spacing-sm;
    
    i {
      font-size: 16px;
    }
  }
  
  .stat-value {
    font-size: 20px;
  }
}
</style>