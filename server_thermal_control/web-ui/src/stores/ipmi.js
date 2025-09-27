/**
 * IPMI控制相关的状态管理
 * 管理IPMI连接、电源控制、传感器监控等功能
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export const useIPMIStore = defineStore('ipmi', () => {
  // 状态定义
  const connectionStatus = ref({
    connected: false,
    host: '192.168.1.100',
    port: 623,
    username: 'admin',
    lastCheck: null,
    error: null,
    connecting: false
  })

  const powerStatus = ref({
    state: 'on', // on, off, unknown
    lastChanged: null,
    uptime: 0
  })

  const sensorData = ref({
    temperature: [],
    voltage: [],
    fan: [],
    power: [],
    lastUpdate: null
  })

  const systemEventLog = ref({
    events: [],
    totalCount: 0,
    lastUpdate: null
  })

  const remoteControl = ref({
    consoleActive: false,
    virtualMediaMounted: false,
    biosSetupMode: false
  })

  // 计算属性
  const isConnected = computed(() => connectionStatus.value.connected)
  const isPowerOn = computed(() => powerStatus.value.state === 'on')
  const hasWarnings = computed(() => {
    return sensorData.value.temperature.some(sensor => sensor.status === 'warning') ||
           sensorData.value.voltage.some(sensor => sensor.status === 'warning') ||
           sensorData.value.fan.some(sensor => sensor.status === 'warning')
  })

  const hasCritical = computed(() => {
    return sensorData.value.temperature.some(sensor => sensor.status === 'critical') ||
           sensorData.value.voltage.some(sensor => sensor.status === 'critical') ||
           sensorData.value.fan.some(sensor => sensor.status === 'critical')
  })

  // 方法定义

  /**
   * 初始化IPMI连接
   */
  const initializeIPMI = async () => {
    try {
      connectionStatus.value.connecting = true
      await checkConnection()
      if (connectionStatus.value.connected) {
        await Promise.all([
          fetchPowerStatus(),
          fetchSensorData(),
          fetchSystemEventLog()
        ])
      }
    } catch (error) {
      console.error('IPMI初始化失败:', error)
      connectionStatus.value.error = error.message
    } finally {
      connectionStatus.value.connecting = false
    }
  }

  /**
   * 检查IPMI连接状态
   */
  const checkConnection = async () => {
    try {
      // 在实际环境中会调用真实API
      // const response = await api.get('/api/ipmi/status')
      
      // 模拟连接检查
      await new Promise(resolve => setTimeout(resolve, 1000))
      connectionStatus.value.connected = Math.random() > 0.1 // 90%成功率
      connectionStatus.value.lastCheck = new Date()
      connectionStatus.value.error = connectionStatus.value.connected ? null : 'IPMI连接超时'
      
      if (connectionStatus.value.connected) {
        ElMessage.success('IPMI连接成功')
      } else {
        ElMessage.error('IPMI连接失败')
      }
    } catch (error) {
      connectionStatus.value.connected = false
      connectionStatus.value.error = error.message
      ElMessage.error(`IPMI连接检查失败: ${error.message}`)
    }
  }

  /**
   * 获取电源状态
   */
  const fetchPowerStatus = async () => {
    try {
      // 在实际环境中会调用真实API
      // const response = await api.get('/api/ipmi/power/status')
      
      // 模拟电源状态
      powerStatus.value = {
        state: Math.random() > 0.2 ? 'on' : 'off',
        lastChanged: new Date(Date.now() - Math.random() * 86400000),
        uptime: Math.floor(Math.random() * 86400 * 7) // 0-7天
      }
    } catch (error) {
      console.error('获取电源状态失败:', error)
    }
  }

  /**
   * 获取传感器数据
   */
  const fetchSensorData = async () => {
    try {
      // 在实际环境中会调用真实API
      // const response = await api.get('/api/ipmi/sensors')
      
      // 模拟传感器数据
      sensorData.value = {
        temperature: [
          {
            id: 'cpu_temp',
            name: 'CPU温度',
            value: 45 + Math.floor(Math.random() * 20),
            unit: '°C',
            status: 'normal',
            threshold: { warning: 70, critical: 85 }
          },
          {
            id: 'mb_temp',
            name: '主板温度',
            value: 35 + Math.floor(Math.random() * 15),
            unit: '°C',
            status: 'normal',
            threshold: { warning: 60, critical: 75 }
          },
          {
            id: 'ambient_temp',
            name: '环境温度',
            value: 25 + Math.floor(Math.random() * 10),
            unit: '°C',
            status: 'normal',
            threshold: { warning: 40, critical: 50 }
          }
        ],
        voltage: [
          {
            id: 'cpu_vcore',
            name: 'CPU核心电压',
            value: 1.2 + Math.random() * 0.1,
            unit: 'V',
            status: 'normal',
            threshold: { warning: 1.4, critical: 1.5 }
          },
          {
            id: 'mem_voltage',
            name: '内存电压',
            value: 1.35 + Math.random() * 0.05,
            unit: 'V',
            status: 'normal',
            threshold: { warning: 1.5, critical: 1.6 }
          },
          {
            id: 'psu_12v',
            name: '12V电源',
            value: 12.0 + (Math.random() - 0.5) * 0.2,
            unit: 'V',
            status: 'normal',
            threshold: { warning: 11.5, critical: 11.0 }
          }
        ],
        fan: [
          {
            id: 'cpu_fan1',
            name: 'CPU风扇1',
            value: 2000 + Math.floor(Math.random() * 500),
            unit: 'RPM',
            status: 'normal',
            threshold: { warning: 1000, critical: 500 }
          },
          {
            id: 'cpu_fan2',
            name: 'CPU风扇2',
            value: 1800 + Math.floor(Math.random() * 400),
            unit: 'RPM',
            status: 'normal',
            threshold: { warning: 1000, critical: 500 }
          },
          {
            id: 'case_fan',
            name: '机箱风扇',
            value: 1200 + Math.floor(Math.random() * 300),
            unit: 'RPM',
            status: 'normal',
            threshold: { warning: 800, critical: 400 }
          }
        ],
        power: [
          {
            id: 'total_power',
            name: '总功耗',
            value: 150 + Math.floor(Math.random() * 100),
            unit: 'W',
            status: 'normal',
            threshold: { warning: 300, critical: 400 }
          }
        ],
        lastUpdate: new Date()
      }

      // 更新传感器状态
      updateSensorStatus()
    } catch (error) {
      console.error('获取传感器数据失败:', error)
    }
  }

  /**
   * 更新传感器状态
   */
  const updateSensorStatus = () => {
    const updateStatus = (sensors) => {
      sensors.forEach(sensor => {
        if (sensor.value >= sensor.threshold.critical) {
          sensor.status = 'critical'
        } else if (sensor.value >= sensor.threshold.warning) {
          sensor.status = 'warning'
        } else {
          sensor.status = 'normal'
        }
      })
    }

    updateStatus(sensorData.value.temperature)
    updateStatus(sensorData.value.voltage)
    updateStatus(sensorData.value.fan)
    updateStatus(sensorData.value.power)
  }

  /**
   * 获取系统事件日志
   */
  const fetchSystemEventLog = async () => {
    try {
      // 在实际环境中会调用真实API
      // const response = await api.get('/api/ipmi/events')
      
      // 模拟系统事件日志
      const events = [
        {
          id: 1,
          timestamp: new Date(Date.now() - 3600000),
          severity: 'info',
          source: 'System',
          description: '系统启动完成',
          sensorType: 'System Event',
          sensorNumber: 0x01
        },
        {
          id: 2,
          timestamp: new Date(Date.now() - 1800000),
          severity: 'warning',
          source: 'Temperature',
          description: 'CPU温度超过警告阈值',
          sensorType: 'Temperature',
          sensorNumber: 0x02
        },
        {
          id: 3,
          timestamp: new Date(Date.now() - 900000),
          severity: 'info',
          source: 'Fan',
          description: '风扇转速调整',
          sensorType: 'Fan',
          sensorNumber: 0x03
        },
        {
          id: 4,
          timestamp: new Date(Date.now() - 300000),
          severity: 'info',
          source: 'Power',
          description: '电源状态正常',
          sensorType: 'Power Supply',
          sensorNumber: 0x04
        }
      ]

      systemEventLog.value = {
        events,
        totalCount: events.length,
        lastUpdate: new Date()
      }
    } catch (error) {
      console.error('获取系统事件日志失败:', error)
    }
  }

  /**
   * 电源控制操作
   */
  const powerControl = async (action) => {
    try {
      // 确认操作
      const actionMap = {
        'on': '开机',
        'off': '关机',
        'restart': '重启',
        'force_off': '强制关机'
      }

      const confirmMessage = `确定要执行${actionMap[action]}操作吗？`
      await ElMessageBox.confirm(confirmMessage, '确认操作', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      // 在实际环境中会调用真实API
      // const response = await api.post('/api/ipmi/power/control', { action })
      
      // 模拟电源控制
      ElMessage.info(`正在执行${actionMap[action]}操作...`)
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 更新电源状态
      if (action === 'on') {
        powerStatus.value.state = 'on'
      } else if (action === 'off' || action === 'force_off') {
        powerStatus.value.state = 'off'
      } else if (action === 'restart') {
        powerStatus.value.state = 'off'
        setTimeout(() => {
          powerStatus.value.state = 'on'
        }, 3000)
      }
      
      powerStatus.value.lastChanged = new Date()
      ElMessage.success(`${actionMap[action]}操作执行成功`)
      
      // 添加事件日志
      addEventLog({
        severity: 'info',
        source: 'Power',
        description: `执行${actionMap[action]}操作`
      })
    } catch (error) {
      if (error !== 'cancel') {
        console.error('电源控制失败:', error)
        ElMessage.error(`电源控制失败: ${error.message}`)
      }
    }
  }

  /**
   * 远程控制操作
   */
  const remoteControlAction = async (action) => {
    try {
      const actionMap = {
        'console': '远程控制台',
        'virtual_media': '虚拟媒体',
        'bios_setup': 'BIOS设置'
      }

      // 在实际环境中会调用真实API或打开新窗口
      // const response = await api.post('/api/ipmi/remote/control', { action })
      
      ElMessage.info(`正在启动${actionMap[action]}...`)
      
      // 模拟远程控制状态更新
      if (action === 'console') {
        remoteControl.value.consoleActive = true
        // 实际应用中这里会打开远程控制台窗口
        window.open('#', '_blank')
      } else if (action === 'virtual_media') {
        remoteControl.value.virtualMediaMounted = !remoteControl.value.virtualMediaMounted
      } else if (action === 'bios_setup') {
        remoteControl.value.biosSetupMode = true
      }
      
      ElMessage.success(`${actionMap[action]}启动成功`)
    } catch (error) {
      console.error('远程控制失败:', error)
      ElMessage.error(`远程控制失败: ${error.message}`)
    }
  }

  /**
   * 清除系统事件日志
   */
  const clearEventLog = async () => {
    try {
      await ElMessageBox.confirm('确定要清除所有系统事件日志吗？此操作不可恢复。', '确认清除', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })

      // 在实际环境中会调用真实API
      // const response = await api.delete('/api/ipmi/events')
      
      systemEventLog.value.events = []
      systemEventLog.value.totalCount = 0
      systemEventLog.value.lastUpdate = new Date()
      
      ElMessage.success('系统事件日志已清除')
    } catch (error) {
      if (error !== 'cancel') {
        console.error('清除事件日志失败:', error)
        ElMessage.error(`清除事件日志失败: ${error.message}`)
      }
    }
  }

  /**
   * 添加事件日志
   */
  const addEventLog = (event) => {
    const newEvent = {
      id: Date.now(),
      timestamp: new Date(),
      severity: event.severity || 'info',
      source: event.source || 'System',
      description: event.description,
      sensorType: event.sensorType || 'System Event',
      sensorNumber: event.sensorNumber || 0x00
    }
    
    systemEventLog.value.events.unshift(newEvent)
    systemEventLog.value.totalCount++
    systemEventLog.value.lastUpdate = new Date()
    
    // 限制日志数量
    if (systemEventLog.value.events.length > 100) {
      systemEventLog.value.events = systemEventLog.value.events.slice(0, 100)
    }
  }

  /**
   * 刷新所有IPMI数据
   */
  const refreshAllData = async () => {
    if (!connectionStatus.value.connected) {
      ElMessage.warning('IPMI未连接，无法刷新数据')
      return
    }

    try {
      await Promise.all([
        fetchPowerStatus(),
        fetchSensorData(),
        fetchSystemEventLog()
      ])
      ElMessage.success('IPMI数据刷新完成')
    } catch (error) {
      console.error('刷新IPMI数据失败:', error)
      ElMessage.error('刷新IPMI数据失败')
    }
  }

  /**
   * 配置IPMI连接
   */
  const configureConnection = async (config) => {
    try {
      connectionStatus.value.host = config.host
      connectionStatus.value.port = config.port
      connectionStatus.value.username = config.username
      
      // 测试连接
      await checkConnection()
      
      if (connectionStatus.value.connected) {
        ElMessage.success('IPMI配置保存成功')
        return true
      } else {
        ElMessage.error('IPMI连接测试失败')
        return false
      }
    } catch (error) {
      console.error('配置IPMI连接失败:', error)
      ElMessage.error(`配置IPMI连接失败: ${error.message}`)
      return false
    }
  }

  return {
    // 状态
    connectionStatus,
    powerStatus,
    sensorData,
    systemEventLog,
    remoteControl,
    
    // 计算属性
    isConnected,
    isPowerOn,
    hasWarnings,
    hasCritical,
    
    // 方法
    initializeIPMI,
    checkConnection,
    fetchPowerStatus,
    fetchSensorData,
    fetchSystemEventLog,
    powerControl,
    remoteControlAction,
    clearEventLog,
    addEventLog,
    refreshAllData,
    configureConnection
  }
})