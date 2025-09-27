<template>
  <div class="temperature-chart">
    <div 
      ref="chartRef" 
      :style="{ height: height + 'px' }"
      class="chart-container"
    ></div>
    
    <!-- 温度统计信息 -->
    <div class="temperature-stats" v-if="!compact">
      <div class="stat-item">
        <span class="stat-label">当前温度</span>
        <span :class="['stat-value', getTemperatureClass(currentTemp)]">
          {{ currentTemp }}°C
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最高温度</span>
        <span :class="['stat-value', getTemperatureClass(maxTemp)]">
          {{ maxTemp }}°C
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">平均温度</span>
        <span :class="['stat-value', getTemperatureClass(avgTemp)]">
          {{ avgTemp }}°C
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 温度监控图表组件
 * 使用ECharts展示实时温度数据
 */
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import { useSystemStore } from '../stores/system'
import * as echarts from 'echarts'

const props = defineProps({
  height: {
    type: Number,
    default: 300
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const systemStore = useSystemStore()
const chartRef = ref(null)
let chart = null

// 计算属性
const currentTemp = computed(() => {
  const temps = systemStore.temperatureData
  console.log("温度传感器列表",temps.sensors);
  return temps.sensors.length === 0 ? 0 : Math.round(temps.sensors[temps.sensors.length - 1].value);
})

const maxTemp = computed(() => {
  const temps = systemStore.temperatureData
  if (temps.sensors.length === 0) return 0
  return Math.round(Math.max(...temps.sensors.map(t => Math.max(t.cpu, t.gpu, t.motherboard))))
})

const avgTemp = computed(() => {
  const temps = systemStore.temperatureData
  if (temps.sensors.length === 0) return 0
  const sum = temps.sensors.reduce((acc, t) => acc + t.cpu + t.gpu + t.motherboard, 0)
  return Math.round(sum / (temps.sensors.length * 3))
})

onMounted(() => {
  initChart()
  updateChart()
})

onUnmounted(() => {
  if (chart) {
    chart.dispose()
  }
})

// 监听温度数据变化
watch(() => systemStore.temperatureData, () => {
  updateChart()
}, { deep: true })

/**
 * 初始化图表
 */
const initChart = () => {
  if (!chartRef.value) return
  
  chart = echarts.init(chartRef.value)
  
  const option = {
    title: {
      text: props.compact ? '' : '温度监控',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        let result = `${params[0].axisValue}<br/>`
        params.forEach(param => {
          result += `${param.seriesName}: ${param.value}°C<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['CPU', 'GPU', '主板'],
      bottom: props.compact ? 5 : 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: props.compact ? '15%' : '20%',
      top: props.compact ? '10%' : '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [],
      axisLabel: {
        formatter: (value) => {
          const date = new Date(value)
          return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '温度 (°C)',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}°C'
      }
    },
    series: [
      {
        name: 'CPU',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          opacity: 0.1
        }
      },
      {
        name: 'GPU',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#67C23A'
        },
        areaStyle: {
          opacity: 0.1
        }
      },
      {
        name: '主板',
        type: 'line',
        smooth: true,
        data: [],
        itemStyle: {
          color: '#E6A23C'
        },
        areaStyle: {
          opacity: 0.1
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  // 响应式调整
  window.addEventListener('resize', () => {
    chart?.resize()
  })
}

/**
 * 更新图表数据
 */
const updateChart = () => {
  if (!chart) return
  
  const temperatureData = systemStore.temperatureData
  const timeLabels = temperatureData.sensors.map(item => item.timestamp)
  const cpuData = temperatureData.sensors.map(item => item.cpu)
  const gpuData = temperatureData.sensors.map(item => item.gpu)
  const motherboardData = temperatureData.sensors.map(item => item.motherboard)
  
  chart.setOption({
    xAxis: {
      data: timeLabels
    },
    series: [
      { data: cpuData },
      { data: gpuData },
      { data: motherboardData }
    ]
  })
}

/**
 * 获取温度状态样式类
 * @param {number} temp 温度值
 */
const getTemperatureClass = (temp) => {
  if (temp < 60) return 'success'
  if (temp < 80) return 'warning'
  return 'danger'
}
</script>

<style lang="scss" scoped>
.temperature-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
}

.temperature-stats {
  display: flex;
  justify-content: space-around;
  padding: var(--spacing-md) 0;
  border-top: 1px solid var(--el-border-color-lighter);
  margin-top: var(--spacing-md);

  .stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-xs);

    .stat-label {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    .stat-value {
      font-size: 18px;
      font-weight: 600;

      &.success {
        color: var(--el-color-success);
      }

      &.warning {
        color: var(--el-color-warning);
      }

      &.danger {
        color: var(--el-color-danger);
      }
    }
  }
}

@media (max-width: 768px) {
  .temperature-stats {
    .stat-item .stat-value {
      font-size: 16px;
    }
  }
}
</style>