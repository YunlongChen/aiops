<!--
  网络监控页面
  显示网络设备和流量监控信息
  
  @author AI Assistant
  @version 1.0.0
  @date 2025-01-23
-->
<template>
  <div class="network-monitoring">
    <!-- 页面标题和操作 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">网络监控</h1>
        <p class="page-subtitle">实时监控网络设备状态和流量信息</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" @click="refreshData">
          <i class="icon-refresh-cw"></i>
          刷新
        </button>
        <button class="btn btn-primary" @click="showAddDevice">
          <i class="icon-plus"></i>
          添加设备
        </button>
      </div>
    </div>
    
    <!-- 网络概览 -->
    <div class="network-overview">
      <div class="overview-cards">
        <div class="overview-card" v-for="metric in networkMetrics" :key="metric.key">
          <div class="card-icon" :class="metric.iconClass">
            <i :class="metric.icon"></i>
          </div>
          <div class="card-content">
            <div class="card-value">{{ metric.value }}</div>
            <div class="card-label">{{ metric.label }}</div>
            <div class="card-change" :class="metric.changeClass">
              <i :class="metric.changeIcon"></i>
              {{ metric.change }}
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 网络拓扑图 -->
    <div class="topology-section">
      <BaseChart
        title="网络拓扑图"
        subtitle="网络设备连接关系和状态"
        height="400px"
        :loading="topologyLoading"
        :has-data="true"
      >
        <template #header>
          <div class="topology-controls">
            <button class="btn btn-sm btn-outline" @click="resetTopology">
              <i class="icon-refresh-cw"></i>
              重置视图
            </button>
            <button class="btn btn-sm btn-outline" @click="autoLayout">
              <i class="icon-grid"></i>
              自动布局
            </button>
          </div>
        </template>
        <div class="topology-container">
          <!-- 网络拓扑图占位符 -->
          <div class="topology-placeholder">
            <div class="topology-nodes">
              <div
                v-for="node in topologyNodes"
                :key="node.id"
                class="topology-node"
                :class="'node-' + node.type"
                :style="{ left: node.x + 'px', top: node.y + 'px' }"
              >
                <div class="node-icon">
                  <i :class="node.icon"></i>
                </div>
                <div class="node-label">{{ node.name }}</div>
                <StatusBadge :status="node.status" size="small" />
              </div>
            </div>
            <svg class="topology-connections">
              <line
                v-for="connection in topologyConnections"
                :key="connection.id"
                :x1="connection.x1"
                :y1="connection.y1"
                :x2="connection.x2"
                :y2="connection.y2"
                :class="'connection-' + connection.status"
              />
            </svg>
          </div>
        </div>
      </BaseChart>
    </div>
    
    <!-- 流量监控图表 -->
    <div class="traffic-charts">
      <div class="charts-row">
        <div class="chart-container">
          <BaseChart
            title="网络流量趋势"
            subtitle="入站和出站流量变化"
            height="300px"
            :loading="trafficLoading"
            :has-data="trafficData.length > 0"
          >
            <template #header>
              <select v-model="trafficTimeRange" class="time-range-select">
                <option value="1h">最近1小时</option>
                <option value="6h">最近6小时</option>
                <option value="24h">最近24小时</option>
                <option value="7d">最近7天</option>
              </select>
            </template>
            <div class="traffic-chart">
              <div class="traffic-legend">
                <div class="legend-item">
                  <div class="legend-color inbound"></div>
                  <span>入站流量</span>
                </div>
                <div class="legend-item">
                  <div class="legend-color outbound"></div>
                  <span>出站流量</span>
                </div>
              </div>
              <div class="traffic-lines">
                <div class="traffic-line" v-for="(point, index) in trafficData" :key="index">
                  <div class="line-time">{{ point.time }}</div>
                  <div class="line-bars">
                    <div class="bar inbound" :style="{ height: point.inbound + 'px' }"></div>
                    <div class="bar outbound" :style="{ height: point.outbound + 'px' }"></div>
                  </div>
                  <div class="line-values">
                    <div class="value inbound">{{ point.inboundValue }}MB</div>
                    <div class="value outbound">{{ point.outboundValue }}MB</div>
                  </div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>
        
        <div class="chart-container">
          <BaseChart
            title="带宽利用率"
            subtitle="各接口带宽使用情况"
            height="300px"
            :loading="bandwidthLoading"
            :has-data="bandwidthData.length > 0"
          >
            <div class="bandwidth-chart">
              <div class="bandwidth-interfaces">
                <div
                  v-for="networkInterface in bandwidthData"
                  :key="networkInterface.name"
                  class="interface-item"
                >
                  <div class="interface-info">
                    <div class="interface-name">{{ networkInterface.name }}</div>
                    <div class="interface-speed">{{ networkInterface.speed }}</div>
                  </div>
                  <div class="interface-usage">
                    <div class="usage-bar">
                      <div
                        class="usage-fill"
                        :style="{ width: networkInterface.usage + '%' }"
                        :class="getUsageClass(networkInterface.usage)"
                      ></div>
                    </div>
                    <div class="usage-text">{{ networkInterface.usage }}%</div>
                  </div>
                </div>
              </div>
            </div>
          </BaseChart>
        </div>
      </div>
    </div>
    
    <!-- 网络设备列表 -->
    <div class="devices-section">
      <div class="section-header">
        <h2 class="section-title">网络设备</h2>
        <div class="section-filters">
          <select v-model="deviceTypeFilter" class="filter-select">
            <option value="">全部类型</option>
            <option value="router">路由器</option>
            <option value="switch">交换机</option>
            <option value="firewall">防火墙</option>
            <option value="load-balancer">负载均衡</option>
          </select>
          <select v-model="deviceStatusFilter" class="filter-select">
            <option value="">全部状态</option>
            <option value="online">在线</option>
            <option value="offline">离线</option>
            <option value="warning">警告</option>
          </select>
        </div>
      </div>
      
      <div class="devices-grid">
        <div
          v-for="device in filteredDevices"
          :key="device.id"
          class="device-card"
          @click="showDeviceDetail(device)"
        >
          <div class="device-header">
            <div class="device-icon" :class="'icon-' + device.type">
              <i :class="getDeviceIcon(device.type)"></i>
            </div>
            <div class="device-info">
              <h3 class="device-name">{{ device.name }}</h3>
              <p class="device-ip">{{ device.ip }}</p>
              <p class="device-type">{{ getDeviceTypeLabel(device.type) }}</p>
            </div>
            <StatusBadge :status="device.status" :animated="true" />
          </div>
          
          <div class="device-metrics">
            <div class="metric-row">
              <div class="metric-item">
                <div class="metric-label">CPU使用率</div>
                <div class="metric-value">{{ device.cpu }}%</div>
                <div class="metric-bar">
                  <div
                    class="metric-fill"
                    :style="{ width: device.cpu + '%' }"
                    :class="getMetricClass(device.cpu)"
                  ></div>
                </div>
              </div>
            </div>
            
            <div class="metric-row">
              <div class="metric-item">
                <div class="metric-label">内存使用率</div>
                <div class="metric-value">{{ device.memory }}%</div>
                <div class="metric-bar">
                  <div
                    class="metric-fill"
                    :style="{ width: device.memory + '%' }"
                    :class="getMetricClass(device.memory)"
                  ></div>
                </div>
              </div>
            </div>
            
            <div class="metric-row">
              <div class="metric-item">
                <div class="metric-label">连接数</div>
                <div class="metric-value">{{ device.connections }}</div>
              </div>
              <div class="metric-item">
                <div class="metric-label">端口数</div>
                <div class="metric-value">{{ device.ports }}</div>
              </div>
            </div>
          </div>
          
          <div class="device-footer">
            <div class="device-uptime">
              <i class="icon-clock"></i>
              运行时间: {{ device.uptime }}
            </div>
            <div class="device-actions">
              <button class="btn-icon" @click.stop="pingDevice(device)" title="Ping测试">
                <i class="icon-wifi"></i>
              </button>
              <button class="btn-icon" @click.stop="editDevice(device)" title="编辑">
                <i class="icon-edit"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <EmptyState
        v-if="filteredDevices.length === 0"
        icon="icon-wifi"
        title="暂无网络设备"
        description="没有找到符合条件的网络设备"
        :actions="[
          { id: 'add', title: '添加设备', icon: 'icon-plus', type: 'primary' },
          { id: 'clear', title: '清除筛选', icon: 'icon-x', type: 'outline' }
        ]"
        @action="handleEmptyAction"
      />
    </div>
  </div>
</template>

<script setup>
/**
 * 网络监控页面组件
 * 显示网络设备和流量监控信息
 */
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import BaseChart from '@/components/charts/BaseChart.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const router = useRouter()

// 响应式数据
const topologyLoading = ref(false)
const trafficLoading = ref(false)
const bandwidthLoading = ref(false)
const trafficTimeRange = ref('24h')
const deviceTypeFilter = ref('')
const deviceStatusFilter = ref('')

// 网络指标
const networkMetrics = reactive([
  {
    key: 'devices',
    icon: 'icon-wifi',
    iconClass: 'card-icon-blue',
    value: '24',
    label: '网络设备',
    change: '+2',
    changeClass: 'card-change-up',
    changeIcon: 'icon-trending-up'
  },
  {
    key: 'bandwidth',
    icon: 'icon-activity',
    iconClass: 'card-icon-green',
    value: '1.2GB/s',
    label: '总带宽',
    change: '+15%',
    changeClass: 'card-change-up',
    changeIcon: 'icon-trending-up'
  },
  {
    key: 'connections',
    icon: 'icon-link',
    iconClass: 'card-icon-purple',
    value: '1,856',
    label: '活跃连接',
    change: '-5%',
    changeClass: 'card-change-down',
    changeIcon: 'icon-trending-down'
  },
  {
    key: 'latency',
    icon: 'icon-zap',
    iconClass: 'card-icon-orange',
    value: '12ms',
    label: '平均延迟',
    change: '+2ms',
    changeClass: 'card-change-up',
    changeIcon: 'icon-trending-up'
  }
])

// 拓扑节点数据
const topologyNodes = reactive([
  { id: 1, name: 'Core-Router', type: 'router', status: 'online', icon: 'icon-router', x: 200, y: 50 },
  { id: 2, name: 'Switch-01', type: 'switch', status: 'online', icon: 'icon-layers', x: 100, y: 150 },
  { id: 3, name: 'Switch-02', type: 'switch', status: 'warning', icon: 'icon-layers', x: 300, y: 150 },
  { id: 4, name: 'Firewall', type: 'firewall', status: 'online', icon: 'icon-shield', x: 200, y: 250 },
  { id: 5, name: 'LoadBalancer', type: 'load-balancer', status: 'online', icon: 'icon-shuffle', x: 50, y: 250 },
  { id: 6, name: 'Server-01', type: 'server', status: 'online', icon: 'icon-server', x: 150, y: 350 },
  { id: 7, name: 'Server-02', type: 'server', status: 'offline', icon: 'icon-server', x: 250, y: 350 }
])

// 拓扑连接数据
const topologyConnections = reactive([
  { id: 1, x1: 200, y1: 80, x2: 130, y2: 150, status: 'online' },
  { id: 2, x1: 200, y1: 80, x2: 270, y2: 150, status: 'warning' },
  { id: 3, x1: 130, y1: 180, x2: 80, y2: 250, status: 'online' },
  { id: 4, x1: 200, y1: 220, x2: 200, y2: 280, status: 'online' },
  { id: 5, x1: 80, y1: 280, x2: 150, y2: 350, status: 'online' },
  { id: 6, x1: 200, y1: 280, x2: 250, y2: 350, status: 'offline' }
])

// 流量数据
const trafficData = reactive([
  { time: '00:00', inbound: 80, outbound: 60, inboundValue: 120, outboundValue: 90 },
  { time: '04:00', inbound: 45, outbound: 35, inboundValue: 68, outboundValue: 52 },
  { time: '08:00', inbound: 120, outbound: 95, inboundValue: 180, outboundValue: 142 },
  { time: '12:00', inbound: 100, outbound: 80, inboundValue: 150, outboundValue: 120 },
  { time: '16:00', inbound: 85, outbound: 70, inboundValue: 128, outboundValue: 105 },
  { time: '20:00', inbound: 65, outbound: 50, inboundValue: 98, outboundValue: 75 }
])

// 带宽数据
const bandwidthData = reactive([
  { name: 'eth0', speed: '1Gbps', usage: 75 },
  { name: 'eth1', speed: '1Gbps', usage: 45 },
  { name: 'eth2', speed: '10Gbps', usage: 85 },
  { name: 'eth3', speed: '10Gbps', usage: 30 },
  { name: 'bond0', speed: '20Gbps', usage: 60 }
])

// 网络设备数据
const devices = reactive([
  {
    id: 1,
    name: 'Core-Router-01',
    ip: '192.168.1.1',
    type: 'router',
    status: 'online',
    cpu: 45,
    memory: 62,
    connections: 1856,
    ports: 48,
    uptime: '45天 12小时'
  },
  {
    id: 2,
    name: 'Switch-Main-01',
    ip: '192.168.1.10',
    type: 'switch',
    status: 'warning',
    cpu: 78,
    memory: 85,
    connections: 324,
    ports: 24,
    uptime: '23天 8小时'
  },
  {
    id: 3,
    name: 'Firewall-01',
    ip: '192.168.1.100',
    type: 'firewall',
    status: 'online',
    cpu: 35,
    memory: 55,
    connections: 2156,
    ports: 8,
    uptime: '67天 15小时'
  },
  {
    id: 4,
    name: 'LoadBalancer-01',
    ip: '192.168.1.200',
    type: 'load-balancer',
    status: 'online',
    cpu: 52,
    memory: 68,
    connections: 892,
    ports: 16,
    uptime: '12天 6小时'
  }
])

// 计算属性
const filteredDevices = computed(() => {
  let filtered = devices
  
  if (deviceTypeFilter.value) {
    filtered = filtered.filter(device => device.type === deviceTypeFilter.value)
  }
  
  if (deviceStatusFilter.value) {
    filtered = filtered.filter(device => device.status === deviceStatusFilter.value)
  }
  
  return filtered
})

/**
 * 获取设备类型标签
 */
const getDeviceTypeLabel = (type) => {
  const labels = {
    router: '路由器',
    switch: '交换机',
    firewall: '防火墙',
    'load-balancer': '负载均衡'
  }
  return labels[type] || type
}

/**
 * 获取设备图标
 */
const getDeviceIcon = (type) => {
  const icons = {
    router: 'icon-router',
    switch: 'icon-layers',
    firewall: 'icon-shield',
    'load-balancer': 'icon-shuffle'
  }
  return icons[type] || 'icon-wifi'
}

/**
 * 获取使用率样式类
 */
const getUsageClass = (usage) => {
  if (usage >= 80) return 'usage-high'
  if (usage >= 60) return 'usage-medium'
  return 'usage-low'
}

/**
 * 获取指标样式类
 */
const getMetricClass = (value) => {
  if (value >= 80) return 'metric-high'
  if (value >= 60) return 'metric-medium'
  return 'metric-low'
}

/**
 * 刷新数据
 */
const refreshData = async () => {
  try {
    console.log('刷新网络监控数据...')
    // 模拟数据更新
    devices.forEach(device => {
      if (device.status !== 'offline') {
        device.cpu = Math.floor(Math.random() * 100)
        device.memory = Math.floor(Math.random() * 100)
        device.connections = Math.floor(Math.random() * 3000)
      }
    })
  } catch (error) {
    console.error('刷新数据失败:', error)
  }
}

/**
 * 显示添加设备对话框
 */
const showAddDevice = () => {
  console.log('显示添加设备对话框')
  // TODO: 实现添加设备功能
}

/**
 * 重置拓扑图
 */
const resetTopology = () => {
  console.log('重置拓扑图视图')
  // TODO: 实现拓扑图重置功能
}

/**
 * 自动布局
 */
const autoLayout = () => {
  console.log('自动布局拓扑图')
  // TODO: 实现自动布局功能
}

/**
 * 显示设备详情
 */
const showDeviceDetail = (device) => {
  console.log('显示设备详情:', device.name)
  // TODO: 跳转到设备详情页面
}

/**
 * Ping设备
 */
const pingDevice = (device) => {
  console.log('Ping设备:', device.name)
  // TODO: 实现Ping测试功能
}

/**
 * 编辑设备
 */
const editDevice = (device) => {
  console.log('编辑设备:', device.name)
  // TODO: 实现编辑设备功能
}

/**
 * 处理空状态操作
 */
const handleEmptyAction = (action) => {
  switch (action.id) {
    case 'add':
      showAddDevice()
      break
    case 'clear':
      deviceTypeFilter.value = ''
      deviceStatusFilter.value = ''
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

.network-monitoring {
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

// 网络概览
.network-overview {
  margin-bottom: $spacing-xl;
}

.overview-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: $spacing-lg;
}

.overview-card {
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

.card-icon {
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
  
  &.card-icon-blue {
    background: $primary-color;
  }
  
  &.card-icon-green {
    background: $success-color;
  }
  
  &.card-icon-purple {
    background: #8b5cf6;
  }
  
  &.card-icon-orange {
    background: $warning-color;
  }
}

.card-content {
  flex: 1;
}

.card-value {
  font-size: 24px;
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

.card-change {
  display: flex;
  align-items: center;
  font-size: 13px;
  font-weight: 500;
  
  i {
    margin-right: $spacing-xs;
  }
  
  &.card-change-up {
    color: $success-color;
  }
  
  &.card-change-down {
    color: $error-color;
  }
}

// 拓扑图
.topology-section {
  margin-bottom: $spacing-xl;
}

.topology-controls {
  display: flex;
  gap: $spacing-sm;
}

.topology-container {
  height: 350px;
  position: relative;
  overflow: hidden;
}

.topology-placeholder {
  width: 100%;
  height: 100%;
  position: relative;
  background: $background-light;
  border-radius: $border-radius;
}

.topology-nodes {
  position: relative;
  width: 100%;
  height: 100%;
}

.topology-node {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: scale(1.1);
  }
}

.node-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $white;
  border: 2px solid $primary-color;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  
  i {
    font-size: 16px;
    color: $primary-color;
  }
}

.node-label {
  font-size: 12px;
  font-weight: 500;
  color: $text-color;
  text-align: center;
  background: $white;
  padding: $spacing-xs;
  border-radius: $border-radius;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.topology-connections {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  
  line {
    stroke-width: 2;
    
    &.connection-online {
      stroke: $success-color;
    }
    
    &.connection-warning {
      stroke: $warning-color;
    }
    
    &.connection-offline {
      stroke: $error-color;
      stroke-dasharray: 5,5;
    }
  }
}

// 流量图表
.traffic-charts {
  margin-bottom: $spacing-xl;
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: $spacing-lg;
}

.chart-container {
  min-height: 350px;
}

.time-range-select {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  font-size: 13px;
  background: $white;
  color: $text-color;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.traffic-chart {
  padding: $spacing-lg;
  height: 250px;
}

.traffic-legend {
  display: flex;
  gap: $spacing-lg;
  margin-bottom: $spacing-lg;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 13px;
  color: $text-color-secondary;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  
  &.inbound {
    background: $primary-color;
  }
  
  &.outbound {
    background: $success-color;
  }
}

.traffic-lines {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 150px;
  gap: $spacing-sm;
}

.traffic-line {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  height: 100%;
}

.line-time {
  font-size: 12px;
  color: $text-color-secondary;
  margin-bottom: $spacing-xs;
}

.line-bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  flex: 1;
  width: 30px;
}

.bar {
  width: 12px;
  border-radius: 2px 2px 0 0;
  min-height: 2px;
  
  &.inbound {
    background: linear-gradient(to top, $primary-color, lighten($primary-color, 20%));
  }
  
  &.outbound {
    background: linear-gradient(to top, $success-color, lighten($success-color, 20%));
  }
}

.line-values {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: $spacing-xs;
  
  .value {
    font-size: 10px;
    text-align: center;
    
    &.inbound {
      color: $primary-color;
    }
    
    &.outbound {
      color: $success-color;
    }
  }
}

.bandwidth-chart {
  padding: $spacing-lg;
  height: 250px;
}

.bandwidth-interfaces {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
  height: 100%;
  justify-content: center;
}

.interface-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
}

.interface-info {
  min-width: 100px;
}

.interface-name {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
  font-family: monospace;
}

.interface-speed {
  font-size: 12px;
  color: $text-color-secondary;
}

.interface-usage {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  flex: 1;
}

.usage-bar {
  flex: 1;
  height: 8px;
  background: $border-color-light;
  border-radius: 4px;
  overflow: hidden;
}

.usage-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
  
  &.usage-low {
    background: $success-color;
  }
  
  &.usage-medium {
    background: $warning-color;
  }
  
  &.usage-high {
    background: $error-color;
  }
}

.usage-text {
  font-size: 13px;
  font-weight: 500;
  color: $text-color;
  min-width: 35px;
  text-align: right;
}

// 设备列表
.devices-section {
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

.section-filters {
  display: flex;
  gap: $spacing-sm;
}

.filter-select {
  padding: $spacing-xs $spacing-sm;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  font-size: 13px;
  background: $white;
  color: $text-color;
  
  &:focus {
    outline: none;
    border-color: $primary-color;
  }
}

.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: $spacing-lg;
  padding: $spacing-lg;
}

.device-card {
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

.device-header {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  margin-bottom: $spacing-md;
}

.device-icon {
  width: 50px;
  height: 50px;
  border-radius: $border-radius;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $background-light;
  border: 1px solid $border-color-light;
  
  i {
    font-size: 20px;
    color: $primary-color;
  }
  
  &.icon-router i {
    color: $primary-color;
  }
  
  &.icon-switch i {
    color: $success-color;
  }
  
  &.icon-firewall i {
    color: $error-color;
  }
  
  &.icon-load-balancer i {
    color: $warning-color;
  }
}

.device-info {
  flex: 1;
}

.device-name {
  margin: 0 0 $spacing-xs 0;
  font-size: 16px;
  font-weight: 600;
  color: $text-color;
}

.device-ip {
  margin: 0 0 $spacing-xs 0;
  font-size: 14px;
  color: $text-color-secondary;
  font-family: monospace;
}

.device-type {
  margin: 0;
  font-size: 13px;
  color: $text-color-light;
}

.device-metrics {
  margin-bottom: $spacing-md;
}

.metric-row {
  display: flex;
  gap: $spacing-md;
  margin-bottom: $spacing-sm;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.metric-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: $spacing-xs;
}

.metric-label {
  font-size: 13px;
  color: $text-color-secondary;
}

.metric-value {
  font-size: 14px;
  font-weight: 500;
  color: $text-color;
}

.metric-bar {
  height: 4px;
  background: $border-color-light;
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s ease;
  
  &.metric-low {
    background: $success-color;
  }
  
  &.metric-medium {
    background: $warning-color;
  }
  
  &.metric-high {
    background: $error-color;
  }
}

.device-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.device-uptime {
  display: flex;
  align-items: center;
  gap: $spacing-xs;
  font-size: 12px;
  color: $text-color-secondary;
  
  i {
    font-size: 12px;
  }
}

.device-actions {
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
}

// 响应式设计
@media (max-width: 1200px) {
  .charts-row {
    grid-template-columns: 1fr;
  }
  
  .devices-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

@media (max-width: 768px) {
  .network-monitoring {
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
  
  .overview-cards {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: $spacing-md;
  }
  
  .overview-card {
    padding: $spacing-md;
  }
  
  .devices-grid {
    grid-template-columns: 1fr;
    gap: $spacing-md;
    padding: $spacing-md;
  }
  
  .device-card {
    padding: $spacing-md;
  }
  
  .section-header {
    flex-direction: column;
    gap: $spacing-md;
    align-items: flex-start;
    
    .section-filters {
      width: 100%;
      justify-content: flex-end;
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
  
  .card-value {
    font-size: 20px;
  }
  
  .device-header {
    flex-direction: column;
    align-items: flex-start;
    gap: $spacing-sm;
  }
  
  .device-icon {
    width: 40px;
    height: 40px;
    
    i {
      font-size: 16px;
    }
  }
}
</style>