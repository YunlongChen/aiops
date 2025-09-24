<!--
  网络监控组件
  功能：提供网络设备监控、流量分析和网络拓扑监控
  作者：AI Assistant
  创建时间：2025-01-23
-->
<template>
  <div class="network-monitoring">
    <!-- 网络设备概览 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>网络设备概览</h3>
        <div class="section-actions">
          <select v-model="selectedDeviceType" class="device-selector">
            <option value="all">所有设备</option>
            <option value="router">路由器</option>
            <option value="switch">交换机</option>
            <option value="firewall">防火墙</option>
            <option value="load-balancer">负载均衡器</option>
          </select>
          <button class="btn-icon" @click="refreshDevices" title="刷新">
            <i class="fas fa-sync-alt" :class="{ spinning: isRefreshingDevices }"></i>
          </button>
          <button class="btn-icon" @click="showTopology" title="网络拓扑">
            <i class="fas fa-project-diagram"></i>
          </button>
        </div>
      </div>

      <div class="devices-grid">
        <div 
          v-for="device in filteredDevices" 
          :key="device.id"
          :class="['device-card', device.status]"
        >
          <div class="device-header">
            <div class="device-info">
              <div class="device-name-row">
                <i :class="device.icon"></i>
                <h4>{{ device.name }}</h4>
                <span class="device-type">{{ device.type }}</span>
              </div>
              <span class="device-ip">{{ device.ip }}</span>
            </div>
            <div class="device-status">
              <span :class="['status-indicator', device.status]"></span>
              <span class="status-text">{{ getStatusText(device.status) }}</span>
            </div>
          </div>
          
          <div class="device-metrics">
            <div class="metric-grid">
              <div class="metric-item">
                <span class="metric-label">CPU使用率</span>
                <span class="metric-value">{{ device.cpuUsage }}%</span>
                <div class="metric-bar">
                  <div 
                    :class="['metric-fill', getCpuLevel(device.cpuUsage)]" 
                    :style="{ width: device.cpuUsage + '%' }"
                  ></div>
                </div>
              </div>
              <div class="metric-item">
                <span class="metric-label">内存使用率</span>
                <span class="metric-value">{{ device.memoryUsage }}%</span>
                <div class="metric-bar">
                  <div 
                    :class="['metric-fill', getMemoryLevel(device.memoryUsage)]" 
                    :style="{ width: device.memoryUsage + '%' }"
                  ></div>
                </div>
              </div>
              <div class="metric-item">
                <span class="metric-label">端口利用率</span>
                <span class="metric-value">{{ device.portUtilization }}%</span>
                <div class="metric-bar">
                  <div 
                    :class="['metric-fill', getPortLevel(device.portUtilization)]" 
                    :style="{ width: device.portUtilization + '%' }"
                  ></div>
                </div>
              </div>
              <div class="metric-item">
                <span class="metric-label">运行时间</span>
                <span class="metric-value">{{ device.uptime }}</span>
              </div>
            </div>
          </div>
          
          <div class="device-actions">
            <button class="btn-small" @click="viewDeviceDetails(device)">
              详情
            </button>
            <button class="btn-small" @click="viewPortStatus(device)">
              端口状态
            </button>
            <button class="btn-small" @click="configureDevice(device)">
              配置
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 网络流量分析 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>网络流量分析</h3>
        <div class="section-actions">
          <select v-model="selectedInterface" class="interface-selector">
            <option value="all">所有接口</option>
            <option v-for="interface in networkInterfaces" :key="interface.id" :value="interface.id">
              {{ interface.name }}
            </option>
          </select>
        </div>
      </div>

      <div class="traffic-stats">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-arrow-down"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ trafficStats.inbound }}</div>
            <div class="stat-label">入站流量</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-arrow-up"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ trafficStats.outbound }}</div>
            <div class="stat-label">出站流量</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-exchange-alt"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ trafficStats.total }}</div>
            <div class="stat-label">总流量</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-tachometer-alt"></i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ trafficStats.bandwidth }}</div>
            <div class="stat-label">带宽利用率</div>
          </div>
        </div>
      </div>

      <div class="traffic-charts">
        <div class="chart-card">
          <div class="chart-header">
            <h4>流量趋势</h4>
            <div class="chart-actions">
              <select v-model="trafficTimeRange" class="time-selector">
                <option value="1h">1小时</option>
                <option value="6h">6小时</option>
                <option value="24h">24小时</option>
                <option value="7d">7天</option>
              </select>
            </div>
          </div>
          <div class="chart-content">
            <canvas ref="trafficTrendChart" id="traffic-trend-chart"></canvas>
          </div>
        </div>

        <div class="chart-card">
          <div class="chart-header">
            <h4>协议分布</h4>
          </div>
          <div class="chart-content">
            <canvas ref="protocolChart" id="protocol-chart"></canvas>
          </div>
        </div>
      </div>

      <!-- 接口状态列表 -->
      <div class="interfaces-section">
        <div class="subsection-header">
          <h4>网络接口状态</h4>
          <div class="subsection-actions">
            <input
              type="text"
              v-model="interfaceSearch"
              @input="filterInterfaces"
              placeholder="搜索接口..."
              class="search-input"
            />
          </div>
        </div>

        <div class="table-container">
          <table class="monitoring-table">
            <thead>
              <tr>
                <th>接口名称</th>
                <th>设备</th>
                <th>状态</th>
                <th>速率</th>
                <th>入站流量</th>
                <th>出站流量</th>
                <th>错误包</th>
                <th>丢包率</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="interface in filteredInterfaces" :key="interface.id">
                <td>
                  <div class="interface-name">
                    <i :class="interface.icon"></i>
                    {{ interface.name }}
                  </div>
                </td>
                <td>{{ interface.device }}</td>
                <td>
                  <span :class="['interface-status', interface.status]">
                    {{ getStatusText(interface.status) }}
                  </span>
                </td>
                <td>{{ interface.speed }}</td>
                <td>{{ interface.inTraffic }}</td>
                <td>{{ interface.outTraffic }}</td>
                <td>
                  <span :class="['error-count', getErrorLevel(interface.errors)]">
                    {{ interface.errors }}
                  </span>
                </td>
                <td>
                  <span :class="['packet-loss', getPacketLossLevel(interface.packetLoss)]">
                    {{ interface.packetLoss }}%
                  </span>
                </td>
                <td>
                  <button class="btn-icon" @click="viewInterfaceDetails(interface)" title="详情">
                    <i class="fas fa-info-circle"></i>
                  </button>
                  <button class="btn-icon" @click="resetInterface(interface)" title="重置">
                    <i class="fas fa-redo"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 网络拓扑监控 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>网络拓扑监控</h3>
        <div class="section-actions">
          <button class="btn-icon" @click="refreshTopology" title="刷新拓扑">
            <i class="fas fa-sync-alt" :class="{ spinning: isRefreshingTopology }"></i>
          </button>
          <button class="btn-icon" @click="exportTopology" title="导出拓扑">
            <i class="fas fa-download"></i>
          </button>
        </div>
      </div>

      <div class="topology-container">
        <div class="topology-sidebar">
          <div class="topology-legend">
            <h5>设备类型</h5>
            <div class="legend-items">
              <div class="legend-item">
                <i class="fas fa-router legend-icon router"></i>
                <span>路由器</span>
              </div>
              <div class="legend-item">
                <i class="fas fa-network-wired legend-icon switch"></i>
                <span>交换机</span>
              </div>
              <div class="legend-item">
                <i class="fas fa-shield-alt legend-icon firewall"></i>
                <span>防火墙</span>
              </div>
              <div class="legend-item">
                <i class="fas fa-server legend-icon server"></i>
                <span>服务器</span>
              </div>
            </div>
          </div>

          <div class="topology-stats">
            <h5>拓扑统计</h5>
            <div class="stat-items">
              <div class="stat-item">
                <span class="stat-label">设备总数</span>
                <span class="stat-value">{{ topologyStats.totalDevices }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">连接数</span>
                <span class="stat-value">{{ topologyStats.totalConnections }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">在线设备</span>
                <span class="stat-value">{{ topologyStats.onlineDevices }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">离线设备</span>
                <span class="stat-value">{{ topologyStats.offlineDevices }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="topology-canvas">
          <div class="topology-view" ref="topologyView">
            <!-- 这里可以集成网络拓扑图库，如D3.js、vis.js等 -->
            <div class="topology-placeholder">
              <i class="fas fa-project-diagram"></i>
              <p>网络拓扑图</p>
              <p class="placeholder-text">点击刷新按钮加载拓扑图</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 网络告警 -->
    <div class="monitoring-section">
      <div class="section-header">
        <h3>网络告警</h3>
        <div class="section-actions">
          <select v-model="alertSeverity" class="severity-selector">
            <option value="all">所有级别</option>
            <option value="critical">严重</option>
            <option value="warning">警告</option>
            <option value="info">信息</option>
          </select>
        </div>
      </div>

      <div class="alerts-list">
        <div 
          v-for="alert in filteredAlerts" 
          :key="alert.id"
          :class="['alert-item', alert.severity]"
        >
          <div class="alert-icon">
            <i :class="getAlertIcon(alert.severity)"></i>
          </div>
          <div class="alert-content">
            <div class="alert-title">{{ alert.title }}</div>
            <div class="alert-description">{{ alert.description }}</div>
            <div class="alert-meta">
              <span class="alert-device">{{ alert.device }}</span>
              <span class="alert-time">{{ alert.time }}</span>
            </div>
          </div>
          <div class="alert-actions">
            <button class="btn-small" @click="acknowledgeAlert(alert)">
              确认
            </button>
            <button class="btn-small" @click="resolveAlert(alert)">
              解决
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * 网络监控组件
 * 提供网络设备、流量分析和拓扑监控功能
 */
export default {
  name: 'NetworkMonitoring',
  props: {
    timeRange: {
      type: String,
      default: '1h'
    },
    isRefreshing: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      // 选择器和搜索
      selectedDeviceType: 'all',
      selectedInterface: 'all',
      interfaceSearch: '',
      alertSeverity: 'all',
      trafficTimeRange: '1h',
      isRefreshingDevices: false,
      isRefreshingTopology: false,
      
      // 网络设备数据
      networkDevices: [
        {
          id: 1,
          name: 'Core-Router-01',
          type: '路由器',
          icon: 'fas fa-router',
          ip: '192.168.1.1',
          status: 'healthy',
          cpuUsage: 25,
          memoryUsage: 45,
          portUtilization: 60,
          uptime: '45天'
        },
        {
          id: 2,
          name: 'Access-Switch-01',
          type: '交换机',
          icon: 'fas fa-network-wired',
          ip: '192.168.1.10',
          status: 'warning',
          cpuUsage: 78,
          memoryUsage: 82,
          portUtilization: 85,
          uptime: '30天'
        },
        {
          id: 3,
          name: 'Firewall-01',
          type: '防火墙',
          icon: 'fas fa-shield-alt',
          ip: '192.168.1.254',
          status: 'healthy',
          cpuUsage: 35,
          memoryUsage: 55,
          portUtilization: 40,
          uptime: '60天'
        },
        {
          id: 4,
          name: 'LoadBalancer-01',
          type: '负载均衡器',
          icon: 'fas fa-balance-scale',
          ip: '192.168.1.100',
          status: 'critical',
          cpuUsage: 95,
          memoryUsage: 90,
          portUtilization: 95,
          uptime: '15天'
        }
      ],
      
      // 网络接口数据
      networkInterfaces: [
        {
          id: 1,
          name: 'GigabitEthernet0/0/1',
          device: 'Core-Router-01',
          icon: 'fas fa-ethernet',
          status: 'healthy',
          speed: '1Gbps',
          inTraffic: '450Mbps',
          outTraffic: '320Mbps',
          errors: 0,
          packetLoss: 0.1
        },
        {
          id: 2,
          name: 'FastEthernet0/1',
          device: 'Access-Switch-01',
          icon: 'fas fa-ethernet',
          status: 'warning',
          speed: '100Mbps',
          inTraffic: '85Mbps',
          outTraffic: '78Mbps',
          errors: 15,
          packetLoss: 2.5
        },
        {
          id: 3,
          name: 'TenGigabitEthernet0/0/1',
          device: 'Core-Router-01',
          icon: 'fas fa-ethernet',
          status: 'healthy',
          speed: '10Gbps',
          inTraffic: '2.5Gbps',
          outTraffic: '1.8Gbps',
          errors: 2,
          packetLoss: 0.05
        },
        {
          id: 4,
          name: 'Management0/0',
          device: 'Firewall-01',
          icon: 'fas fa-ethernet',
          status: 'healthy',
          speed: '1Gbps',
          inTraffic: '120Mbps',
          outTraffic: '95Mbps',
          errors: 0,
          packetLoss: 0
        }
      ],
      
      // 流量统计数据
      trafficStats: {
        inbound: '2.8Gbps',
        outbound: '2.1Gbps',
        total: '4.9Gbps',
        bandwidth: '65%'
      },
      
      // 拓扑统计数据
      topologyStats: {
        totalDevices: 24,
        totalConnections: 48,
        onlineDevices: 22,
        offlineDevices: 2
      },
      
      // 网络告警数据
      networkAlerts: [
        {
          id: 1,
          severity: 'critical',
          title: '负载均衡器CPU使用率过高',
          description: 'LoadBalancer-01的CPU使用率达到95%，可能影响服务性能',
          device: 'LoadBalancer-01',
          time: '2分钟前'
        },
        {
          id: 2,
          severity: 'warning',
          title: '交换机端口利用率告警',
          description: 'Access-Switch-01的端口利用率超过80%阈值',
          device: 'Access-Switch-01',
          time: '5分钟前'
        },
        {
          id: 3,
          severity: 'warning',
          title: '网络接口丢包率异常',
          description: 'FastEthernet0/1接口丢包率达到2.5%',
          device: 'Access-Switch-01',
          time: '8分钟前'
        },
        {
          id: 4,
          severity: 'info',
          title: '设备重启完成',
          description: 'Core-Router-01重启完成，所有服务正常',
          device: 'Core-Router-01',
          time: '15分钟前'
        }
      ],
      
      // 过滤后的数据
      filteredDevices: [],
      filteredInterfaces: [],
      filteredAlerts: []
    }
  },
  methods: {
    /**
     * 获取状态文本
     */
    getStatusText(status) {
      const statusMap = {
        healthy: '正常',
        warning: '警告',
        critical: '严重',
        error: '错误',
        offline: '离线'
      }
      return statusMap[status] || '未知'
    },
    
    /**
     * 获取CPU级别
     */
    getCpuLevel(usage) {
      if (usage >= 90) return 'critical'
      if (usage >= 70) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取内存级别
     */
    getMemoryLevel(usage) {
      if (usage >= 90) return 'critical'
      if (usage >= 70) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取端口级别
     */
    getPortLevel(usage) {
      if (usage >= 90) return 'critical'
      if (usage >= 70) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取错误级别
     */
    getErrorLevel(errors) {
      if (errors >= 10) return 'critical'
      if (errors >= 5) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取丢包率级别
     */
    getPacketLossLevel(loss) {
      if (loss >= 2) return 'critical'
      if (loss >= 1) return 'warning'
      return 'normal'
    },
    
    /**
     * 获取告警图标
     */
    getAlertIcon(severity) {
      const iconMap = {
        critical: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
      }
      return iconMap[severity] || 'fas fa-bell'
    },
    
    /**
     * 过滤设备
     */
    filterDevices() {
      if (this.selectedDeviceType === 'all') {
        this.filteredDevices = [...this.networkDevices]
      } else {
        this.filteredDevices = this.networkDevices.filter(device => {
          const typeMap = {
            'router': '路由器',
            'switch': '交换机',
            'firewall': '防火墙',
            'load-balancer': '负载均衡器'
          }
          return device.type === typeMap[this.selectedDeviceType]
        })
      }
    },
    
    /**
     * 过滤接口
     */
    filterInterfaces() {
      let filtered = [...this.networkInterfaces]
      
      if (this.selectedInterface !== 'all') {
        filtered = filtered.filter(interface => interface.id === this.selectedInterface)
      }
      
      if (this.interfaceSearch) {
        const query = this.interfaceSearch.toLowerCase()
        filtered = filtered.filter(interface =>
          interface.name.toLowerCase().includes(query) ||
          interface.device.toLowerCase().includes(query)
        )
      }
      
      this.filteredInterfaces = filtered
    },
    
    /**
     * 过滤告警
     */
    filterAlerts() {
      if (this.alertSeverity === 'all') {
        this.filteredAlerts = [...this.networkAlerts]
      } else {
        this.filteredAlerts = this.networkAlerts.filter(alert =>
          alert.severity === this.alertSeverity
        )
      }
    },
    
    /**
     * 刷新设备
     */
    async refreshDevices() {
      this.isRefreshingDevices = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1000))
        console.log('Network devices refreshed')
      } finally {
        this.isRefreshingDevices = false
      }
    },
    
    /**
     * 刷新拓扑
     */
    async refreshTopology() {
      this.isRefreshingTopology = true
      try {
        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 1500))
        console.log('Network topology refreshed')
      } finally {
        this.isRefreshingTopology = false
      }
    },
    
    /**
     * 显示拓扑
     */
    showTopology() {
      console.log('Showing network topology')
      // 这里可以打开拓扑图弹窗
    },
    
    /**
     * 导出拓扑
     */
    exportTopology() {
      console.log('Exporting network topology')
      // 这里可以实现拓扑图导出功能
    },
    
    /**
     * 查看设备详情
     */
    viewDeviceDetails(device) {
      console.log(`Viewing details for device: ${device.name}`)
      // 这里可以打开设备详情弹窗
    },
    
    /**
     * 查看端口状态
     */
    viewPortStatus(device) {
      console.log(`Viewing port status for device: ${device.name}`)
      // 这里可以显示端口状态详情
    },
    
    /**
     * 配置设备
     */
    configureDevice(device) {
      console.log(`Configuring device: ${device.name}`)
      // 这里可以打开设备配置界面
    },
    
    /**
     * 查看接口详情
     */
    viewInterfaceDetails(interface) {
      console.log(`Viewing details for interface: ${interface.name}`)
      // 这里可以显示接口详细信息
    },
    
    /**
     * 重置接口
     */
    resetInterface(interface) {
      console.log(`Resetting interface: ${interface.name}`)
      // 这里可以实现接口重置功能
    },
    
    /**
     * 确认告警
     */
    acknowledgeAlert(alert) {
      console.log(`Acknowledging alert: ${alert.title}`)
      // 这里可以实现告警确认功能
    },
    
    /**
     * 解决告警
     */
    resolveAlert(alert) {
      console.log(`Resolving alert: ${alert.title}`)
      // 这里可以实现告警解决功能
    },
    
    /**
     * 初始化图表
     */
    initCharts() {
      // 这里可以使用Chart.js或其他图表库初始化图表
      console.log('Initializing network monitoring charts')
    }
  },
  mounted() {
    // 初始化过滤数据
    this.filterDevices()
    this.filterInterfaces()
    this.filterAlerts()
    // 初始化图表
    this.initCharts()
  },
  watch: {
    selectedDeviceType() {
      this.filterDevices()
    },
    selectedInterface() {
      this.filterInterfaces()
    },
    alertSeverity() {
      this.filterAlerts()
    },
    trafficTimeRange() {
      // 时间范围变化时重新加载图表
      console.log(`Traffic time range changed to: ${this.trafficTimeRange}`)
      this.initCharts()
    },
    timeRange() {
      // 时间范围变化时重新加载数据
      console.log(`Time range changed to: ${this.timeRange}`)
      this.initCharts()
    }
  }
}
</script>

<style scoped>
/* 网络监控容器 */
.network-monitoring {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 监控区块样式 */
.monitoring-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.section-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.section-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.device-selector,
.interface-selector,
.severity-selector,
.time-selector {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
}

.search-input {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  width: 200px;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.btn-icon {
  padding: 6px 8px;
  border: none;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  color: #6c757d;
  transition: all 0.2s ease;
}

.btn-icon:hover {
  background: #e9ecef;
  color: #495057;
}

.btn-small {
  padding: 4px 8px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #495057;
  transition: all 0.2s ease;
}

.btn-small:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

/* 设备网格样式 */
.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.device-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
  border-left: 4px solid #28a745;
}

.device-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.device-card.warning {
  border-left-color: #ffc107;
}

.device-card.critical {
  border-left-color: #dc3545;
}

.device-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.device-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}

.device-name-row i {
  color: #6c757d;
  width: 16px;
}

.device-info h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.device-type {
  background: #3498db;
  color: white;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.device-ip {
  color: #6c757d;
  font-size: 13px;
  font-family: monospace;
}

.device-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #28a745;
}

.status-indicator.warning {
  background: #ffc107;
}

.status-indicator.critical {
  background: #dc3545;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: #495057;
}

/* 设备指标样式 */
.device-metrics {
  margin-bottom: 15px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.metric-label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.metric-bar {
  height: 4px;
  background: #e9ecef;
  border-radius: 2px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: #28a745;
  transition: width 0.3s ease;
}

.metric-fill.warning {
  background: #ffc107;
}

.metric-fill.critical {
  background: #dc3545;
}

.device-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 流量统计样式 */
.traffic-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #3498db;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 2px;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

/* 流量图表样式 */
.traffic-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 15px;
  background: white;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-header h4 {
  margin: 0;
  font-size: 14px;
  color: #2c3e50;
}

.chart-content {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  border-radius: 4px;
  color: #6c757d;
}

.chart-content canvas {
  max-width: 100%;
  max-height: 100%;
}

/* 接口区块样式 */
.interfaces-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.subsection-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.subsection-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.subsection-actions {
  display: flex;
  gap: 10px;
}

/* 表格样式 */
.table-container {
  overflow-x: auto;
}

.monitoring-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.monitoring-table th,
.monitoring-table td {
  padding: 12px 8px;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.monitoring-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  font-size: 12px;
  text-transform: uppercase;
}

.monitoring-table tr:hover {
  background: #f8f9fa;
}

.interface-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: monospace;
  font-size: 13px;
}

.interface-name i {
  color: #6c757d;
  width: 14px;
}

.interface-status.healthy {
  color: #28a745;
}

.interface-status.warning {
  color: #ffc107;
}

.interface-status.critical {
  color: #dc3545;
}

.error-count.warning {
  color: #f39c12;
}

.error-count.critical {
  color: #e74c3c;
}

.packet-loss.warning {
  color: #f39c12;
}

.packet-loss.critical {
  color: #e74c3c;
}

/* 拓扑容器样式 */
.topology-container {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
  min-height: 400px;
}

.topology-sidebar {
  background: #f8f9fa;
  border-radius: 6px;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.topology-legend h5,
.topology-stats h5 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 600;
}

.legend-items,
.stat-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #495057;
}

.legend-icon {
  width: 16px;
  text-align: center;
}

.legend-icon.router {
  color: #3498db;
}

.legend-icon.switch {
  color: #2ecc71;
}

.legend-icon.firewall {
  color: #e74c3c;
}

.legend-icon.server {
  color: #9b59b6;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.stat-label {
  color: #6c757d;
}

.stat-value {
  font-weight: 600;
  color: #2c3e50;
}

.topology-canvas {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  background: white;
  position: relative;
}

.topology-view {
  width: 100%;
  height: 100%;
  min-height: 400px;
}

.topology-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6c757d;
}

.topology-placeholder i {
  font-size: 48px;
  margin-bottom: 15px;
}

.topology-placeholder p {
  margin: 5px 0;
  font-size: 16px;
  font-weight: 500;
}

.placeholder-text {
  font-size: 14px !important;
  color: #adb5bd !important;
}

/* 告警列表样式 */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #17a2b8;
  background: #f8f9fa;
}

.alert-item.critical {
  border-left-color: #dc3545;
  background: #f8d7da;
}

.alert-item.warning {
  border-left-color: #ffc107;
  background: #fff3cd;
}

.alert-item.info {
  border-left-color: #17a2b8;
  background: #d1ecf1;
}

.alert-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: white;
  font-size: 12px;
}

.alert-item.critical .alert-icon {
  background: #dc3545;
}

.alert-item.warning .alert-icon {
  background: #ffc107;
}

.alert-item.info .alert-icon {
  background: #17a2b8;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 5px;
}

.alert-description {
  font-size: 14px;
  color: #495057;
  margin-bottom: 5px;
}

.alert-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #6c757d;
}

.alert-actions {
  display: flex;
  gap: 8px;
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
  .devices-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
  
  .topology-container {
    grid-template-columns: 1fr;
  }
  
  .topology-sidebar {
    order: 2;
  }
}

@media (max-width: 768px) {
  .monitoring-section {
    padding: 15px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .section-actions {
    justify-content: center;
  }
  
  .search-input {
    width: 100%;
  }
  
  .devices-grid {
    grid-template-columns: 1fr;
  }
  
  .traffic-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .traffic-charts {
    grid-template-columns: 1fr;
  }
  
  .metric-grid {
    grid-template-columns: 1fr;
  }
  
  .device-actions {
    justify-content: center;
  }
  
  .topology-container {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .alert-item {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .alert-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .network-monitoring {
    gap: 20px;
  }
  
  .monitoring-section {
    padding: 12px;
  }
  
  .section-header h3 {
    font-size: 16px;
  }
  
  .traffic-stats {
    grid-template-columns: 1fr;
  }
  
  .chart-content {
    height: 150px;
  }
  
  .stat-card {
    flex-direction: column;
    text-align: center;
  }
  
  .topology-sidebar {
    padding: 12px;
  }
  
  .topology-view {
    min-height: 300px;
  }
}
</style>