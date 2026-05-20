<template>
  <div class="chart-card" ref="cardRef">
    <div v-if="title" class="chart-header">
      <h4 class="chart-title">{{ title }}</h4>
    </div>

    <div class="chart-body" :style="{ height: height }">
      <div v-if="loading" class="chart-loading">
        <div class="loading-spinner"></div>
      </div>

      <div v-else-if="isEmpty" class="chart-empty">
        <slot name="empty">
          <el-empty description="No Data" />
        </slot>
      </div>

      <div v-else ref="chartRef" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { techTheme } from './themes/techTheme'
import type { EChartsOption } from 'echarts'

interface Props {
  title?: string
  height?: string
  option?: EChartsOption
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  height: '300px',
  loading: false,
})

const cardRef = ref<HTMLElement | null>(null)
const chartRef = ref<HTMLElement | null>(null)
const isEmpty = ref(false)

let chartInstance: echarts.ECharts | null = null
let resizeObserver: ResizeObserver | null = null

function initChart() {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption(techTheme as EChartsOption)

  if (props.option) {
    chartInstance.setOption(props.option)
  }

  isEmpty.value = checkEmpty(props.option)
}

function checkEmpty(option?: EChartsOption): boolean {
  if (!option) return true

  const series = option.series
  if (!series) return true

  if (Array.isArray(series)) {
    if (series.length === 0) return true
    return series.every((s: any) => {
      const data = s.data
      if (!data) return true
      if (Array.isArray(data) && data.length === 0) return true
      return false
    })
  }

  return false
}

function updateChart() {
  if (!chartInstance) return

  if (props.option) {
    chartInstance.setOption(props.option, true)
  }

  isEmpty.value = checkEmpty(props.option)
}

function resizeChart() {
  if (chartInstance) {
    chartInstance.resize()
  }
}

watch(
  () => props.option,
  () => {
    updateChart()
  },
  { deep: true }
)

watch(
  () => props.loading,
  (val) => {
    if (!val && chartInstance) {
      nextTick(() => {
        resizeChart()
      })
    }
  }
)

onMounted(() => {
  nextTick(() => {
    initChart()

    if (cardRef.value) {
      resizeObserver = new ResizeObserver(() => {
        resizeChart()
      })
      resizeObserver.observe(cardRef.value)
    }
  })
})

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  if (chartInstance) {
    chartInstance.dispose()
  }
})

defineExpose({
  chartInstance,
  resizeChart,
  updateChart,
})
</script>

<style scoped>
.chart-card {
  --primary-color: #00E5FF;
  --tech-accent: #00d4ff;
  --bg-card: rgba(10, 20, 40, 0.8);

  background: var(--bg-card);
  border: 1px solid rgba(24, 144, 255, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.chart-header {
  padding: 12px 16px;
  border-bottom: 1px solid rgba(24, 144, 255, 0.15);
}

.chart-title {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: rgba(180, 210, 235, 0.85);
}

.chart-body {
  position: relative;
  width: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.chart-loading,
.chart-empty {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(24, 144, 255, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

:deep(.el-empty__description) {
  color: rgba(232, 244, 255, 0.6);
}
</style>
