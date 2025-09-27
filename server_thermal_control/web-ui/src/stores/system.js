/**
 * 系统状态管理Store
 * 管理服务器状态、IPMI连接状态和实时数据
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { apiService } from '../utils/api'

export const useSystemStore = defineStore('system', () => {
  // 系统基本信息
  const systemInfo = ref({
    serviceName: '',
    version: '',
    uptime: '',
    cpuCores: 0,
    timestamp: null
  })

  // 服务器状态
  const serverStatus = ref({
    isOnline: false,
    lastUpdate: null,
    connectionStatus: 'disconnected' // connected, disconnected, connecting
  })

  // 系统资源使用情况
  const systemMetrics = ref({
    cpu: {
      usage: 0,
      temperature: 0,
      cores: []
    },
    memory: {
      total: 0,
      used: 0,
      available: 0,
      percentage: 0
    },
    disk: {
      total: 0,
      used: 0,
      available: 0,
      percentage: 0
    },
    network: {
      bytesIn: 0,
      bytesOut: 0,
      packetsIn: 0,
      packetsOut: 0
    }
  })

  // 温度传感器数据
  const temperatureData = ref({
    sensors: [],
    lastUpdate: null,
    status: 'unknown' // normal, warning, critical, unknown
  })

  // 风扇状态
  const fanStatus = ref({
    fans: [],
    lastUpdate: null,
    overallStatus: 'unknown'
  })

  // IPMI连接状态
  const ipmiStatus = ref({
    connected: false,
    lastCheck: null,
    error: null
  })

  // 系统日志
  const systemLogs = ref([])

  // 计算属性
  const isSystemHealthy = computed(() => {
    return serverStatus.value.isOnline && 
           temperatureData.value.status !== 'critical' &&
           fanStatus.value.overallStatus !== 'error'
  })

  const memoryUsagePercentage = computed(() => {
    const { total, used } = systemMetrics.value.memory
    return total > 0 ? Math.round((used / total) * 100) : 0
  })

  const diskUsagePercentage = computed(() => {
    const { total, used } = systemMetrics.value.disk
    return total > 0 ? Math.round((used / total) * 100) : 0
  })

  // 方法
  const initializeSystem = async () => {
    try {
      // 使用模拟数据进行初始化，避免API请求错误
      loadMockData()
      serverStatus.value.isOnline = true
      serverStatus.value.lastUpdate = new Date()
      serverStatus.value.connectionStatus = 'connected'
    } catch (error) {
      console.error('系统初始化失败:', error)
    }
  }

  const loadMockData = () => {
    // 模拟系统信息
    systemInfo.value = {
      serviceName: 'Server Monitor',
      version: '1.0.0',
      uptime: '7 days, 12 hours',
      cpuCores: 8,
      timestamp: new Date()
    }

    // 模拟系统指标数据
    systemMetrics.value = {
      cpu: {
        usage: Math.floor(Math.random() * 30) + 20, // 20-50%
        temperature: Math.floor(Math.random() * 15) + 45, // 45-60°C
        cores: Array.from({ length: 8 }, (_, i) => ({
          id: i,
          usage: Math.floor(Math.random() * 40) + 10 // 10-50%
        }))
      },
      memory: {
        total: 32 * 1024 * 1024 * 1024, // 32GB
        used: Math.floor(Math.random() * 10 * 1024 * 1024 * 1024) + 10 * 1024 * 1024 * 1024, // 10-20GB
        available: 0,
        percentage: 0
      },
      disk: {
        total: 1024 * 1024 * 1024 * 1024, // 1TB
        used: Math.floor(Math.random() * 300 * 1024 * 1024 * 1024) + 200 * 1024 * 1024 * 1024, // 200-500GB
        available: 0,
        percentage: 0
      },
      network: {
        bytesIn: Math.floor(Math.random() * 1000000) + 500000,
        bytesOut: Math.floor(Math.random() * 800000) + 300000,
        packetsIn: Math.floor(Math.random() * 10000) + 5000,
        packetsOut: Math.floor(Math.random() * 8000) + 3000
      }
    }

    // 计算可用空间和使用百分比
    systemMetrics.value.memory.available = systemMetrics.value.memory.total - systemMetrics.value.memory.used
    systemMetrics.value.disk.available = systemMetrics.value.disk.total - systemMetrics.value.disk.used

    // 模拟温度数据
    temperatureData.value = {
      sensors: [
        { name: 'CPU', value: 45 + Math.floor(Math.random() * 15), unit: '°C', status: 'normal' },
        { name: 'GPU', value: 50 + Math.floor(Math.random() * 20), unit: '°C', status: 'normal' },
        { name: 'Motherboard', value: 35 + Math.floor(Math.random() * 10), unit: '°C', status: 'normal' }
      ],
      lastUpdate: new Date(),
      status: 'normal'
    }

    // 模拟风扇状态
    fanStatus.value = {
      fans: [
        { id: 'fan1', name: 'CPU风扇1', rpm: 2000 + Math.floor(Math.random() * 500), status: 'normal' },
        { id: 'fan2', name: 'CPU风扇2', rpm: 1800 + Math.floor(Math.random() * 400), status: 'normal' },
        { id: 'fan3', name: '机箱风扇', rpm: 1200 + Math.floor(Math.random() * 300), status: 'normal' }
      ],
      lastUpdate: new Date(),
      overallStatus: 'normal'
    }

    // 模拟IPMI状态
    ipmiStatus.value = {
      connected: true,
      lastCheck: new Date(),
      error: null
    }
  }

  const fetchSystemInfo = async () => {
    try {
      // 在实际环境中会调用真实API，现在使用模拟数据
      // const response = await apiService.get('/api/v1/system/info')
      loadMockData()
      serverStatus.value.isOnline = true
      serverStatus.value.lastUpdate = new Date()
    } catch (error) {
      console.error('获取系统信息失败:', error)
      serverStatus.value.isOnline = false
    }
  }

  const fetchSystemMetrics = async () => {
    try {
      // 更新模拟数据以模拟实时变化
      updateMockMetrics()
    } catch (error) {
      console.error('获取系统指标失败:', error)
    }
  }

  const updateMockMetrics = () => {
    // 模拟CPU使用率变化
    if (systemMetrics.value.cpu) {
      systemMetrics.value.cpu.usage = Math.max(10, Math.min(80, 
        systemMetrics.value.cpu.usage + (Math.random() - 0.5) * 10))
      systemMetrics.value.cpu.temperature = Math.max(35, Math.min(75, 
        systemMetrics.value.cpu.temperature + (Math.random() - 0.5) * 5))
    }

    // 模拟内存使用变化
    if (systemMetrics.value.memory) {
      const variation = (Math.random() - 0.5) * 2 * 1024 * 1024 * 1024 // ±2GB
      systemMetrics.value.memory.used = Math.max(
        5 * 1024 * 1024 * 1024, 
        Math.min(25 * 1024 * 1024 * 1024, systemMetrics.value.memory.used + variation)
      )
      systemMetrics.value.memory.available = systemMetrics.value.memory.total - systemMetrics.value.memory.used
    }

    // 模拟网络流量变化
    if (systemMetrics.value.network) {
      systemMetrics.value.network.bytesIn += Math.floor(Math.random() * 100000)
      systemMetrics.value.network.bytesOut += Math.floor(Math.random() * 80000)
      systemMetrics.value.network.packetsIn += Math.floor(Math.random() * 1000)
      systemMetrics.value.network.packetsOut += Math.floor(Math.random() * 800)
    }
  }

  const fetchTemperatureData = async () => {
    try {
      // 在实际环境中会调用真实API，现在使用模拟数据
      // const response = await apiService.get('/api/v1/temperature')
      
      // 模拟温度数据变化
      temperatureData.value.sensors.forEach(sensor => {
        sensor.value = Math.max(30, Math.min(80, 
          sensor.value + (Math.random() - 0.5) * 3))
        sensor.status = sensor.value > 70 ? 'warning' : sensor.value > 75 ? 'critical' : 'normal'
      })
      temperatureData.value.lastUpdate = new Date()
      
      // 更新整体状态
      const hasWarning = temperatureData.value.sensors.some(s => s.status === 'warning')
      const hasCritical = temperatureData.value.sensors.some(s => s.status === 'critical')
      temperatureData.value.status = hasCritical ? 'critical' : hasWarning ? 'warning' : 'normal'
    } catch (error) {
      console.error('获取温度数据失败:', error)
      temperatureData.value.status = 'unknown'
    }
  }

  const fetchFanStatus = async () => {
    try {
      // 在实际环境中会调用真实API，现在使用模拟数据
      // const response = await apiService.get('/api/v1/fans')
      
      // 模拟风扇状态变化
      fanStatus.value.fans.forEach(fan => {
        fan.rpm = Math.max(800, Math.min(3000, 
          fan.rpm + (Math.random() - 0.5) * 100))
        fan.status = fan.rpm < 1000 ? 'warning' : 'normal'
      })
      fanStatus.value.lastUpdate = new Date()
      
      // 更新整体状态
      const hasError = fanStatus.value.fans.some(f => f.status === 'error')
      const hasWarning = fanStatus.value.fans.some(f => f.status === 'warning')
      fanStatus.value.overallStatus = hasError ? 'error' : hasWarning ? 'warning' : 'normal'
    } catch (error) {
      console.error('获取风扇状态失败:', error)
      fanStatus.value.overallStatus = 'unknown'
    }
  }

  const checkServerHealth = async () => {
    try {
      // 在实际环境中会调用真实API，现在使用模拟数据
      // const response = await apiService.get('/api/v1/health')
      
      // 模拟健康检查
      serverStatus.value.isOnline = true
      serverStatus.value.lastUpdate = new Date()
      serverStatus.value.connectionStatus = 'connected'
    } catch (error) {
      console.error('健康检查失败:', error)
      serverStatus.value.isOnline = false
      serverStatus.value.connectionStatus = 'disconnected'
    }
  }

  const checkIPMIStatus = async () => {
    try {
      // 在实际环境中会调用真实API，现在使用模拟数据
      // const response = await apiService.get('/api/v1/ipmi/status')
      
      // 模拟IPMI连接状态（大部分时间保持连接）
      ipmiStatus.value.connected = Math.random() > 0.1 // 90%概率连接成功
      ipmiStatus.value.lastCheck = new Date()
      ipmiStatus.value.error = ipmiStatus.value.connected ? null : 'IPMI连接超时'
    } catch (error) {
      console.error('IPMI状态检查失败:', error)
      ipmiStatus.value.connected = false
      ipmiStatus.value.error = error.message
    }
  }

  const refreshAllData = async () => {
    serverStatus.value.connectionStatus = 'connecting'
    try {
      // 使用模拟数据刷新，避免API请求错误
      await Promise.all([
        fetchSystemInfo(),
        fetchSystemMetrics(),
        fetchTemperatureData(),
        fetchFanStatus(),
        checkIPMIStatus()
      ])
      serverStatus.value.connectionStatus = 'connected'
      
      // 添加系统日志
      addSystemLog({
        level: 'info',
        source: 'system',
        message: '数据刷新完成'
      })
    } catch (error) {
      console.error('刷新数据失败:', error)
      serverStatus.value.connectionStatus = 'disconnected'
      
      // 添加错误日志
      addSystemLog({
        level: 'error',
        source: 'system',
        message: `数据刷新失败: ${error.message}`
      })
    }
  }

  const addSystemLog = (log) => {
    systemLogs.value.unshift({
      id: Date.now(),
      timestamp: new Date(),
      ...log
    })
    
    // 限制日志数量
    if (systemLogs.value.length > 1000) {
      systemLogs.value = systemLogs.value.slice(0, 1000)
    }
  }

  return {
    // 状态
    systemInfo,
    serverStatus,
    systemMetrics,
    temperatureData,
    fanStatus,
    ipmiStatus,
    systemLogs,
    
    // 计算属性
    isSystemHealthy,
    memoryUsagePercentage,
    diskUsagePercentage,
    
    // 方法
    initializeSystem,
    loadMockData,
    updateMockMetrics,
    fetchSystemInfo,
    fetchSystemMetrics,
    fetchTemperatureData,
    fetchFanStatus,
    checkServerHealth,
    checkIPMIStatus,
    refreshAllData,
    addSystemLog
  }
})