<template>
  <div class="monitoring">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">
          <el-icon><TrendCharts /></el-icon>
          系统监控
        </h1>
        <div class="time-range">
          <el-select v-model="selectedTimeRange" @change="onTimeRangeChange">
            <el-option label="最近1小时" value="1h" />
            <el-option label="最近6小时" value="6h" />
            <el-option label="最近24小时" value="24h" />
            <el-option label="最近7天" value="7d" />
            <el-option label="最近30天" value="30d" />
          </el-select>
        </div>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          :icon="Refresh" 
          :loading="isRefreshing"
          @click="refreshData"
        >
          刷新数据
        </el-button>
        <el-button 
          type="success" 
          :icon="Download"
          @click="exportData"
        >
          导出数据
        </el-button>
      </div>
    </div>

    <!-- 主要内容 -->
    <div class="page-content">
      <!-- 实时指标概览 -->
      <div class="metrics-overview">
        <div class="grid grid-4">
          <div class="metric-card">
            <div class="metric-icon cpu">
              <el-icon><Cpu /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ systemStore.systemMetrics.cpu.usage }}%</div>
              <div class="metric-label">CPU使用率</div>
              <div class="metric-trend" :class="cpuTrend.direction">
                <el-icon v-if="cpuTrend.direction === 'up'"><ArrowUp /></el-icon>
                <el-icon v-else-if="cpuTrend.direction === 'down'"><ArrowDown /></el-icon>
                <el-icon v-else><Minus /></el-icon>
                <span>{{ cpuTrend.value }}%</span>
              </div>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-icon memory">
              <el-icon><Grid /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ systemStore.memoryUsagePercentage }}%</div>
              <div class="metric-label">内存使用率</div>
              <div class="metric-trend" :class="memoryTrend.direction">
                <el-icon v-if="memoryTrend.direction === 'up'"><ArrowUp /></el-icon>
                <el-icon v-else-if="memoryTrend.direction === 'down'"><ArrowDown /></el-icon>
                <el-icon v-else><Minus /></el-icon>
                <span>{{ memoryTrend.value }}%</span>
              </div>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-icon disk">
              <el-icon><Coin /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ systemStore.diskUsagePercentage }}%</div>
              <div class="metric-label">磁盘使用率</div>
              <div class="metric-trend" :class="diskTrend.direction">
                <el-icon v-if="diskTrend.direction === 'up'"><ArrowUp /></el-icon>
                <el-icon v-else-if="diskTrend.direction === 'down'"><ArrowDown /></el-icon>
                <el-icon v-else><Minus /></el-icon>
                <span>{{ diskTrend.value }}%</span>
              </div>
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-icon temperature">
              <el-icon><Sunny /></el-icon>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ averageTemperature }}°C</div>
              <div class="metric-label">平均温度</div>
              <div class="metric-trend" :class="temperatureTrend.direction">
                <el-icon v-if="temperatureTrend.direction === 'up'"><ArrowUp /></el-icon>
                <el-icon v-else-if="temperatureTrend.direction === 'down'"><ArrowDown /></el-icon>
                <el-icon v-else><Minus /></el-icon>
                <span>{{ temperatureTrend.value }}°C</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <div class="grid grid-2">
          <!-- CPU使用率图表 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Cpu /></el-icon>
                CPU使用率趋势
              </span>
            </div>
            <div class="card-content">
              <div ref="cpuChartRef" class="chart-container"></div>
            </div>
          </div>

          <!-- 内存使用率图表 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Grid /></el-icon>
                内存使用率趋势
              </span>
            </div>
            <div class="card-content">
              <div ref="memoryChartRef" class="chart-container"></div>
            </div>
          </div>

          <!-- 磁盘I/O图表 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Coin /></el-icon>
                磁盘I/O趋势
              </span>
            </div>
            <div class="card-content">
              <div ref="diskIOChartRef" class="chart-container"></div>
            </div>
          </div>

          <!-- 网络流量图表 -->
          <div class="dashboard-card">
            <div class="card-header">
              <span class="card-title">
                <el-icon><Connection /></el-icon>
                网络流量趋势
              </span>
            </div>
            <div class="card-content">
              <div ref="networkChartRef" class="chart-container"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 温度监控图表 -->
      <div class="temperature-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><Sunny /></el-icon>
              温度监控
            </span>
          </div>
          <div class="card-content">
            <div ref="temperatureChartRef" class="chart-container large"></div>
          </div>
        </div>
      </div>

      <!-- 系统负载图表 -->
      <div class="load-section">
        <div class="dashboard-card">
          <div class="card-header">
            <span class="card-title">
              <el-icon><DataAnalysis /></el-icon>
              系统负载
            </span>
          </div>
          <div class="card-content">
            <div ref="loadChartRef" class="chart-container large"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 系统监控页面
 * 展示详细的系统性能图表和历史数据
 */
import { ref, reactive, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useSystemStore } from '../stores/system'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { 
  TrendCharts, Refresh, Download, Cpu, Grid, 
  Coin, Sunny, Connection, DataAnalysis,
  ArrowUp, ArrowDown, Minus
} from '@element-plus/icons-vue'

const systemStore = useSystemStore()
const isRefreshing = ref(false)
const selectedTimeRange = ref('1h')

// 图表引用
const cpuChartRef = ref(null)
const memoryChartRef = ref(null)
const diskIOChartRef = ref(null)
const networkChartRef = ref(null)
const temperatureChartRef = ref(null)
const loadChartRef = ref(null)

// 图表实例
let cpuChart = null
let memoryChart = null
let diskIOChart = null
let networkChart = null
let temperatureChart = null
let loadChart = null

// 历史数据
const historicalData = reactive({
  cpu: [],
  memory: [],
  diskIO: [],
  network: [],
  temperature: [],
  load: []
})

// 趋势数据
const cpuTrend = ref({ direction: 'stable', value: 0 })
const memoryTrend = ref({ direction: 'stable', value: 0 })
const diskTrend = ref({ direction: 'stable', value: 0 })
const temperatureTrend = ref({ direction: 'stable', value: 0 })

// 计算平均温度
const averageTemperature = computed(() => {
  const temps = systemStore.temperatureData.sensors
  if (!temps || temps.length === 0) return 0
  
  const sum = temps.reduce((acc, temp) => acc + temp.current, 0)
  return Math.round(sum / temps.length)
})

let refreshTimer = null

onMounted(async () => {
  await nextTick()
  initCharts()
  await refreshData()
  
  // 设置自动刷新
  refreshTimer = setInterval(() => {
    if (!isRefreshing.value) {
      refreshData(true)
    }
  }, 30000) // 30秒刷新一次
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  
  // 销毁图表实例
  destroyCharts()
  
  window.removeEventListener('resize', handleResize)
})

/**
 * 初始化所有图表
 */
const initCharts = () => {
  initCpuChart()
  initMemoryChart()
  initDiskIOChart()
  initNetworkChart()
  initTemperatureChart()
  initLoadChart()
}

/**
 * 初始化CPU图表
 */
const initCpuChart = () => {
  if (!cpuChartRef.value) return
  
  cpuChart = echarts.init(cpuChartRef.value)
  
  const option = {
    title: {
      show: false
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>CPU使用率: {c}%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: 'CPU使用率',
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
        ])
      },
      lineStyle: {
        color: '#409EFF'
      },
      data: []
    }]
  }
  
  cpuChart.setOption(option)
}

/**
 * 初始化内存图表
 */
const initMemoryChart = () => {
  if (!memoryChartRef.value) return
  
  memoryChart = echarts.init(memoryChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>内存使用率: {c}%'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [{
      name: '内存使用率',
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
          { offset: 1, color: 'rgba(103, 194, 58, 0.1)' }
        ])
      },
      lineStyle: {
        color: '#67C23A'
      },
      data: []
    }]
  }
  
  memoryChart.setOption(option)
}

/**
 * 初始化磁盘I/O图表
 */
const initDiskIOChart = () => {
  if (!diskIOChartRef.value) return
  
  diskIOChart = echarts.init(diskIOChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += param.seriesName + ': ' + formatBytes(param.value) + '/s<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['读取', '写入']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: function(value) {
          return formatBytes(value) + '/s'
        }
      }
    },
    series: [
      {
        name: '读取',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#E6A23C' },
        data: []
      },
      {
        name: '写入',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#F56C6C' },
        data: []
      }
    ]
  }
  
  diskIOChart.setOption(option)
}

/**
 * 初始化网络图表
 */
const initNetworkChart = () => {
  if (!networkChartRef.value) return
  
  networkChart = echarts.init(networkChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += param.seriesName + ': ' + formatBytes(param.value) + '/s<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['上传', '下载']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: function(value) {
          return formatBytes(value) + '/s'
        }
      }
    },
    series: [
      {
        name: '上传',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#909399' },
        data: []
      },
      {
        name: '下载',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#409EFF' },
        data: []
      }
    ]
  }
  
  networkChart.setOption(option)
}

/**
 * 初始化温度图表
 */
const initTemperatureChart = () => {
  if (!temperatureChartRef.value) return
  
  temperatureChart = echarts.init(temperatureChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += param.seriesName + ': ' + param.value + '°C<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['CPU温度', 'GPU温度', '主板温度']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}°C'
      }
    },
    series: [
      {
        name: 'CPU温度',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#F56C6C' },
        data: []
      },
      {
        name: 'GPU温度',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#E6A23C' },
        data: []
      },
      {
        name: '主板温度',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#67C23A' },
        data: []
      }
    ]
  }
  
  temperatureChart.setOption(option)
}

/**
 * 初始化系统负载图表
 */
const initLoadChart = () => {
  if (!loadChartRef.value) return
  
  loadChart = echarts.init(loadChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        let result = params[0].name + '<br/>'
        params.forEach(param => {
          result += param.seriesName + ': ' + param.value + '<br/>'
        })
        return result
      }
    },
    legend: {
      data: ['1分钟', '5分钟', '15分钟']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '1分钟',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#409EFF' },
        data: []
      },
      {
        name: '5分钟',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#67C23A' },
        data: []
      },
      {
        name: '15分钟',
        type: 'line',
        smooth: true,
        lineStyle: { color: '#E6A23C' },
        data: []
      }
    ]
  }
  
  loadChart.setOption(option)
}

/**
 * 销毁所有图表
 */
const destroyCharts = () => {
  if (cpuChart) {
    cpuChart.dispose()
    cpuChart = null
  }
  if (memoryChart) {
    memoryChart.dispose()
    memoryChart = null
  }
  if (diskIOChart) {
    diskIOChart.dispose()
    diskIOChart = null
  }
  if (networkChart) {
    networkChart.dispose()
    networkChart = null
  }
  if (temperatureChart) {
    temperatureChart.dispose()
    temperatureChart = null
  }
  if (loadChart) {
    loadChart.dispose()
    loadChart = null
  }
}

/**
 * 处理窗口大小变化
 */
const handleResize = () => {
  if (cpuChart) cpuChart.resize()
  if (memoryChart) memoryChart.resize()
  if (diskIOChart) diskIOChart.resize()
  if (networkChart) networkChart.resize()
  if (temperatureChart) temperatureChart.resize()
  if (loadChart) loadChart.resize()
}

/**
 * 刷新数据
 * @param {boolean} silent 是否静默刷新
 */
const refreshData = async (silent = false) => {
  if (!silent) {
    isRefreshing.value = true
  }
  
  try {
    await Promise.all([
      systemStore.fetchSystemMetrics(),
      systemStore.fetchTemperatureData(),
      generateHistoricalData()
    ])
    
    updateCharts()
    updateTrends()
    
  } catch (error) {
    console.error('刷新数据失败:', error)
  } finally {
    if (!silent) {
      isRefreshing.value = false
    }
  }
}

/**
 * 生成历史数据（模拟）
 */
const generateHistoricalData = async () => {
  const now = new Date()
  const points = getDataPoints()
  
  // 生成时间标签
  const timeLabels = []
  for (let i = points - 1; i >= 0; i--) {
    const time = new Date(now.getTime() - i * getTimeInterval())
    timeLabels.push(formatTimeLabel(time))
  }
  
  // 生成CPU数据
  historicalData.cpu = timeLabels.map(() => ({
    time: timeLabels[historicalData.cpu.length] || '',
    value: Math.random() * 80 + 10
  }))
  
  // 生成内存数据
  historicalData.memory = timeLabels.map(() => ({
    time: timeLabels[historicalData.memory.length] || '',
    value: Math.random() * 60 + 20
  }))
  
  // 生成磁盘I/O数据
  historicalData.diskIO = timeLabels.map(() => ({
    time: timeLabels[historicalData.diskIO.length] || '',
    read: Math.random() * 100 * 1024 * 1024,
    write: Math.random() * 50 * 1024 * 1024
  }))
  
  // 生成网络数据
  historicalData.network = timeLabels.map(() => ({
    time: timeLabels[historicalData.network.length] || '',
    upload: Math.random() * 10 * 1024 * 1024,
    download: Math.random() * 50 * 1024 * 1024
  }))
  
  // 生成温度数据
  historicalData.temperature = timeLabels.map(() => ({
    time: timeLabels[historicalData.temperature.length] || '',
    cpu: Math.random() * 30 + 40,
    gpu: Math.random() * 35 + 45,
    motherboard: Math.random() * 20 + 30
  }))
  
  // 生成负载数据
  historicalData.load = timeLabels.map(() => ({
    time: timeLabels[historicalData.load.length] || '',
    load1: Math.random() * 2,
    load5: Math.random() * 1.5,
    load15: Math.random() * 1
  }))
}

/**
 * 更新所有图表
 */
const updateCharts = () => {
  updateCpuChart()
  updateMemoryChart()
  updateDiskIOChart()
  updateNetworkChart()
  updateTemperatureChart()
  updateLoadChart()
}

/**
 * 更新CPU图表
 */
const updateCpuChart = () => {
  if (!cpuChart) return
  
  const option = {
    xAxis: {
      data: historicalData.cpu.map(item => item.time)
    },
    series: [{
      data: historicalData.cpu.map(item => item.value.toFixed(1))
    }]
  }
  
  cpuChart.setOption(option)
}

/**
 * 更新内存图表
 */
const updateMemoryChart = () => {
  if (!memoryChart) return
  
  const option = {
    xAxis: {
      data: historicalData.memory.map(item => item.time)
    },
    series: [{
      data: historicalData.memory.map(item => item.value.toFixed(1))
    }]
  }
  
  memoryChart.setOption(option)
}

/**
 * 更新磁盘I/O图表
 */
const updateDiskIOChart = () => {
  if (!diskIOChart) return
  
  const option = {
    xAxis: {
      data: historicalData.diskIO.map(item => item.time)
    },
    series: [
      {
        data: historicalData.diskIO.map(item => item.read)
      },
      {
        data: historicalData.diskIO.map(item => item.write)
      }
    ]
  }
  
  diskIOChart.setOption(option)
}

/**
 * 更新网络图表
 */
const updateNetworkChart = () => {
  if (!networkChart) return
  
  const option = {
    xAxis: {
      data: historicalData.network.map(item => item.time)
    },
    series: [
      {
        data: historicalData.network.map(item => item.upload)
      },
      {
        data: historicalData.network.map(item => item.download)
      }
    ]
  }
  
  networkChart.setOption(option)
}

/**
 * 更新温度图表
 */
const updateTemperatureChart = () => {
  if (!temperatureChart) return
  
  const option = {
    xAxis: {
      data: historicalData.temperature.map(item => item.time)
    },
    series: [
      {
        data: historicalData.temperature.map(item => item.cpu.toFixed(1))
      },
      {
        data: historicalData.temperature.map(item => item.gpu.toFixed(1))
      },
      {
        data: historicalData.temperature.map(item => item.motherboard.toFixed(1))
      }
    ]
  }
  
  temperatureChart.setOption(option)
}

/**
 * 更新负载图表
 */
const updateLoadChart = () => {
  if (!loadChart) return
  
  const option = {
    xAxis: {
      data: historicalData.load.map(item => item.time)
    },
    series: [
      {
        data: historicalData.load.map(item => item.load1.toFixed(2))
      },
      {
        data: historicalData.load.map(item => item.load5.toFixed(2))
      },
      {
        data: historicalData.load.map(item => item.load15.toFixed(2))
      }
    ]
  }
  
  loadChart.setOption(option)
}

/**
 * 更新趋势数据
 */
const updateTrends = () => {
  // 模拟趋势计算
  cpuTrend.value = { direction: 'up', value: 2.3 }
  memoryTrend.value = { direction: 'down', value: 1.1 }
  diskTrend.value = { direction: 'stable', value: 0.2 }
  temperatureTrend.value = { direction: 'up', value: 1.5 }
}

/**
 * 时间范围变化处理
 */
const onTimeRangeChange = () => {
  refreshData()
}

/**
 * 导出数据
 */
const exportData = () => {
  ElMessage.success('数据导出功能开发中...')
}

/**
 * 获取数据点数量
 */
const getDataPoints = () => {
  const pointsMap = {
    '1h': 60,
    '6h': 72,
    '24h': 96,
    '7d': 168,
    '30d': 720
  }
  return pointsMap[selectedTimeRange.value] || 60
}

/**
 * 获取时间间隔（毫秒）
 */
const getTimeInterval = () => {
  const intervalMap = {
    '1h': 60 * 1000,
    '6h': 5 * 60 * 1000,
    '24h': 15 * 60 * 1000,
    '7d': 60 * 60 * 1000,
    '30d': 10 * 60 * 60 * 1000
  }
  return intervalMap[selectedTimeRange.value] || 60 * 1000
}

/**
 * 格式化时间标签
 * @param {Date} date 日期对象
 */
const formatTimeLabel = (date) => {
  if (selectedTimeRange.value === '7d' || selectedTimeRange.value === '30d') {
    return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
  } else {
    return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }
}

/**
 * 格式化字节数
 * @param {number} bytes 字节数
 */
const formatBytes = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>

<style lang="scss" scoped>
.monitoring {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: var(--el-bg-color-page);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color);
  box-shadow: var(--shadow-light);

  .header-left {
    display: flex;
    align-items: center;
    gap: var(--spacing-lg);

    .page-title {
      font-size: 24px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      margin: 0;
    }
  }

  .header-right {
    display: flex;
    gap: var(--spacing-sm);
  }
}

.page-content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.metrics-overview {
  .metric-card {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    background: var(--el-bg-color);
    border-radius: var(--border-radius);
    box-shadow: var(--shadow-light);
    border: 1px solid var(--el-border-color-lighter);

    .metric-icon {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      color: white;

      &.cpu {
        background: linear-gradient(135deg, #409EFF, #66B1FF);
      }

      &.memory {
        background: linear-gradient(135deg, #67C23A, #85CE61);
      }

      &.disk {
        background: linear-gradient(135deg, #E6A23C, #EEBC6C);
      }

      &.temperature {
        background: linear-gradient(135deg, #F56C6C, #F78989);
      }
    }

    .metric-content {
      flex: 1;

      .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--el-text-color-primary);
        line-height: 1;
        margin-bottom: 4px;
      }

      .metric-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin-bottom: 8px;
      }

      .metric-trend {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        font-weight: 500;

        &.up {
          color: var(--el-color-danger);
        }

        &.down {
          color: var(--el-color-success);
        }

        &.stable {
          color: var(--el-text-color-secondary);
        }
      }
    }
  }
}

.chart-container {
  width: 100%;
  height: 300px;

  &.large {
    height: 400px;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);

    .header-left {
      flex-direction: column;
      align-items: flex-start;
      gap: var(--spacing-sm);
    }

    .header-right {
      align-self: flex-end;
    }
  }

  .grid-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .grid-2 {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: var(--spacing-md);

    .header-left .page-title {
      font-size: 20px;
    }

    .header-right {
      width: 100%;
      display: flex;
      justify-content: flex-end;
      flex-wrap: wrap;
      gap: var(--spacing-sm);
    }
  }

  .page-content {
    padding: var(--spacing-md);
  }

  .grid-4 {
    grid-template-columns: 1fr;
  }

  .metric-card {
    .metric-icon {
      width: 50px;
      height: 50px;
      font-size: 20px;
    }

    .metric-content .metric-value {
      font-size: 24px;
    }
  }

  .chart-container {
    height: 250px;

    &.large {
      height: 300px;
    }
  }
}
</style>