<template>
  <div class="event-stats-page">
    <!-- 顶部筛选面板 -->
    <div class="filter-panel">
      <div class="filter-row">
        <el-select v-model="filterForm.org_id" placeholder="选择公司" size="default" clearable @change="onCompanyChange">
          <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="filterForm.region_id" :placeholder="filterForm.org_id ? '选择区域' : '请先选择公司'" size="default" clearable :disabled="!filterForm.org_id">
          <el-option v-for="r in companyRegions" :key="r.id" :label="r.name" :value="r.id" />
        </el-select>
        <el-date-picker v-model="filterForm.startDate" type="date" placeholder="开始日期" size="default" />
        <el-date-picker v-model="filterForm.endDate" type="date" placeholder="结束日期" size="default" />
        <el-button type="primary" @click="handleQuery">查询</el-button>
      </div>
    </div>

    <!-- 三栏仪表板 -->
    <div class="dashboard">
      <!-- 左栏 -->
      <div class="column column-left">
        <!-- 今日上报预警事件数 -->
        <div class="chart-card">
          <div class="card-header">
            <span class="header-icon"></span>
            <span class="card-title">今日上报预警事件数(单位：条)</span>
          </div>
          <div class="card-body">
            <div ref="todayChartRef" class="chart-container"></div>
          </div>
        </div>
        <!-- 交通检测 -->
        <div class="chart-card">
          <div class="card-header">
            <span class="header-icon"></span>
            <span class="card-title">今日交通不合规检测（单位：条）</span>
          </div>
          <div class="card-body">
            <div ref="leftChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 中栏 -->
      <div class="column column-center">
        <!-- 算法场景监控 -->
        <div class="chart-card">
          <div class="card-header">
            <span class="header-icon"></span>
            <span class="card-title">算法(场景)监控</span>
          </div>
          <div class="card-body gauge-area">
            <div ref="gaugeChartRef" class="chart-container gauge-chart"></div>
            <div class="gauge-label">交通检测</div>
          </div>
        </div>
        <!-- 算法子场景 -->
        <div class="chart-card">
          <div class="card-header">
            <span class="header-icon"></span>
            <span class="card-title">算法子场景</span>
          </div>
          <div class="card-body">
            <div ref="centerChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>

      <!-- 右栏 -->
      <div class="column column-right">
        <!-- 算法场景趋势 -->
        <div class="chart-card">
          <div class="card-header">
            <span class="header-icon"></span>
            <span class="card-title">算法(场景)趋势</span>
            <div class="header-controls">
              <el-select v-model="filterForm.algorithmType" size="small">
                <el-option label="交通检测" value="traffic" />
              </el-select>
              <el-select v-model="filterForm.trendDimension" size="small">
                <el-option label="时" value="hour" />
                <el-option label="日" value="day" />
                <el-option label="月" value="month" />
              </el-select>
            </div>
          </div>
          <div class="card-body">
            <div ref="trendChartRef" class="chart-container"></div>
          </div>
        </div>
        <!-- 事件趋势（点击算法子场景切换） -->
        <div class="chart-card">
          <div class="card-header">
            <span class="header-icon"></span>
            <span class="card-title">{{ selectedEventType }}趋势</span>
          </div>
          <div class="card-body">
            <div ref="parkingChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart, PieChart, LineChart, GaugeChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import {
  getTodayStats,
  getViolationStats,
  getAlgorithmSummary,
  getSceneStats,
  getTrendStats,
  getEventTrendStats
} from '@/api/event-stats'
import { useRegions } from '@/composables/useRegions'
import { getRegionsByCompany } from '@/api/company-regions'
import { getEventTypeDisplayName } from '@/utils/eventType'

echarts.use([BarChart, PieChart, LineChart, GaugeChart, GridComponent, TooltipComponent, LegendComponent, DataZoomComponent, CanvasRenderer])

const selectedEventType = ref('异常停车')

const filterForm = reactive({
  org_id: null as number | null,
  region_id: null as number | null,
  startDate: '',
  endDate: '',
  algorithmType: 'traffic',
  trendDimension: 'day',
  event_type_id: null as number | null
})

const { companies, loadRegions, getRegionWithDescendants } = useRegions()

const companyRegions = ref<any[]>([])

const onCompanyChange = async () => {
  filterForm.region_id = null
  companyRegions.value = []
  if (!filterForm.org_id) return
  try {
    const res = await getRegionsByCompany(filterForm.org_id)
    const data = res.data || res
    companyRegions.value = (data.items || []).map((item: any) => ({
      id: item.id,
      name: item.name
    }))
  } catch (e) {
    console.error('获取公司区域失败:', e)
  }
}

// Reactive state for API data
const todayStats = ref({ total: 0, items: [] as { name: string; value: number }[] })
const violationStats = ref([] as { name: string; value: number }[])
const algoSummary = ref({ total: 0, max: 0 })
const sceneStats = ref({ items: [] as { id: number; name: string; value: number }[], categories: [] as string[], values: [] as number[] })
const trendData = ref<{ time: string; value: number }[]>([])
const eventTrendData = ref<{ time: string; value: number }[]>([])

const todayChartRef = ref<HTMLDivElement>()
const leftChartRef = ref<HTMLDivElement>()
const gaugeChartRef = ref<HTMLDivElement>()
const centerChartRef = ref<HTMLDivElement>()
const trendChartRef = ref<HTMLDivElement>()
const parkingChartRef = ref<HTMLDivElement>()

let todayChart: echarts.ECharts | null = null
let leftChart: echarts.ECharts | null = null
let gaugeChart: echarts.ECharts | null = null
let centerChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let parkingChart: echarts.ECharts | null = null

const chartColors = {
  primary: '#00E5FF',
  secondary: '#007BFF',
  background: '#020B1F',
  cardBg: 'rgba(0, 30, 60, 0.6)',
  border: 'rgba(0, 229, 255, 0.2)',
  textPrimary: '#FFFFFF',
  textSecondary: '#8AAFC8',
  gridLine: 'rgba(0, 229, 255, 0.1)'
}

const buildBaseParams = () => {
  const regionIds = filterForm.region_id ? getRegionWithDescendants(filterForm.region_id) : undefined
  return {
    org_id: filterForm.org_id || undefined,
    region_ids: regionIds,
    start_date: filterForm.startDate || undefined,
    end_date: filterForm.endDate || undefined
  }
}

const fetchTodayStats = async () => {
  try {
    const data = await getTodayStats(buildBaseParams())
    todayStats.value = data
  } catch (error) {
    console.error('Failed to fetch today stats:', error)
    todayStats.value = { total: 0, items: [] }
  }
}

const fetchViolationStats = async () => {
  try {
    const data = await getViolationStats(buildBaseParams())
    violationStats.value = data.items || []
  } catch (error) {
    console.error('Failed to fetch violation stats:', error)
    violationStats.value = []
  }
}

const fetchAlgorithmSummary = async () => {
  try {
    const data = await getAlgorithmSummary(buildBaseParams())
    algoSummary.value = data
  } catch (error) {
    console.error('Failed to fetch algorithm summary:', error)
    algoSummary.value = { total: 0, max: 0 }
  }
}

const fetchSceneStats = async () => {
  try {
    const data = await getSceneStats(buildBaseParams())
    sceneStats.value = data
  } catch (error) {
    console.error('Failed to fetch scene stats:', error)
    sceneStats.value = { items: [], categories: [], values: [] }
  }
}

const fetchTrendData = async () => {
  try {
    const data = await getTrendStats({
      ...buildBaseParams(),
      dimension: filterForm.trendDimension
    })
    trendData.value = data.trend || []
  } catch (error) {
    console.error('Failed to fetch trend data:', error)
    trendData.value = []
  }
}

const fetchEventTrend = async () => {
  try {
    const data = await getEventTrendStats({
      ...buildBaseParams(),
      dimension: filterForm.trendDimension,
      event_type_id: filterForm.event_type_id || undefined
    })
    eventTrendData.value = data.trend || []
  } catch (error) {
    console.error('Failed to fetch event trend:', error)
    eventTrendData.value = []
  }
}

const initTodayChart = () => {
  if (!todayChartRef.value) return
  todayChart = echarts.init(todayChartRef.value)
  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', top: '10%', bottom: '10%' },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: chartColors.border } },
      splitLine: { lineStyle: { color: chartColors.gridLine } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    yAxis: {
      type: 'category',
      data: ['今日上报预警事件数'],
      axisLine: { lineStyle: { color: chartColors.border } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 11 }
    },
    series: [{
      type: 'bar',
      data: [{ value: todayStats.value.total, itemStyle: { color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#007BFF' }, { offset: 1, color: '#00E5FF' }]) } }],
      barWidth: 20,
      label: { show: true, position: 'right', color: chartColors.primary, fontSize: 14, fontWeight: 'bold' }
    }]
  }
  todayChart.setOption(option)
}

const initLeftChart = () => {
  if (!leftChartRef.value) return
  leftChart = echarts.init(leftChartRef.value)
  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', top: '10%', bottom: '10%' },
    xAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: chartColors.border } },
      splitLine: { lineStyle: { color: chartColors.gridLine } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    yAxis: {
      type: 'category',
      data: violationStats.value.map((d: { name: string; value: number }) => d.name),
      axisLine: { lineStyle: { color: chartColors.border } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    series: [{
      type: 'bar',
      data: violationStats.value.map((d: { name: string; value: number }) => ({ value: d.value, itemStyle: { color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [{ offset: 0, color: '#007BFF' }, { offset: 1, color: '#00E5FF' }]) } })),
      barWidth: 12,
      label: { show: true, position: 'right', color: chartColors.primary, fontSize: 11 }
    }]
  }
  leftChart.setOption(option)
}

const initGaugeChart = () => {
  if (!gaugeChartRef.value) return
  gaugeChart = echarts.init(gaugeChartRef.value)
  const option = {
    backgroundColor: 'transparent',
    series: [{
      type: 'gauge',
      startAngle: 200,
      endAngle: -20,
      radius: '90%',
      center: ['50%', '60%'],
      progress: {
        show: true,
        width: 18,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#007BFF' },
            { offset: 1, color: '#00E5FF' }
          ])
        }
      },
      axisLine: {
        lineStyle: { width: 18, color: [[1, 'rgba(0, 229, 255, 0.15)']] }
      },
      axisTick: { show: false },
      splitLine: { show: false },
      axisLabel: { show: false },
      pointer: { show: false },
      anchor: { show: false },
      title: { show: false },
      detail: { show: false },
      data: [{ value: algoSummary.value.total, name: '事件总数' }],
      max: algoSummary.value.max || 100
    }],
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => `<div style="font-size:12px;color:#666;margin-bottom:4px">${params.name}</div><div style="display:flex;align-items:center;gap:6px"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#007BFF"></span><span style="font-size:14px;font-weight:600;color:#333">${params.value}</span></div>`,
      backgroundColor: '#fff',
      borderColor: '#e0e0e0',
      borderWidth: 1,
      padding: [8, 12],
      textStyle: { color: '#333' },
      extraCssText: 'box-shadow:0 2px 8px rgba(0,0,0,0.15);border-radius:4px;'
    }
  }
  gaugeChart.setOption(option)
}

const initCenterChart = () => {
  if (!centerChartRef.value) return
  centerChart = echarts.init(centerChartRef.value)
  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '3%', top: '15%', bottom: '15%' },
    xAxis: {
      type: 'category',
      data: sceneStats.value.categories.map(getEventTypeDisplayName),
      axisLine: { lineStyle: { color: chartColors.border } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: chartColors.border } },
      splitLine: { lineStyle: { color: chartColors.gridLine } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    series: [{
      type: 'bar',
      data: sceneStats.value.values,
      barWidth: '50%',
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#00E5FF' },
          { offset: 1, color: '#007BFF' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }
  centerChart.setOption(option)

  // 点击柱子切换右下方趋势图
  centerChart.on('click', (params: any) => {
    if (typeof params.dataIndex === 'number') {
      const item = sceneStats.value.items[params.dataIndex]
      if (item) {
        selectedEventType.value = getEventTypeDisplayName(item.name)
        filterForm.event_type_id = item.id
        fetchEventTrend().then(() => updateParkingChart())
      }
    }
  })
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const times = trendData.value.map((d: { time: string }) => d.time)
  const values = trendData.value.map((d: { time: string; value: number }) => d.value)
  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '3%', top: '10%', bottom: '22%' },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLine: { lineStyle: { color: chartColors.border } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: chartColors.border } },
      splitLine: { lineStyle: { color: chartColors.gridLine } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    dataZoom: [{
      type: 'slider',
      show: true,
      start: 0,
      end: 100,
      height: 14,
      bottom: 4,
      borderColor: 'rgba(0,229,255,0.15)',
      fillerColor: 'rgba(0,229,255,0.15)',
      backgroundColor: 'rgba(0,30,60,0.3)',
      handleStyle: { color: '#00E5FF', borderColor: '#00E5FF' },
      textStyle: { color: '#8AAFC8', fontSize: 10 },
      dataBackground: {
        lineStyle: { color: 'rgba(0,229,255,0.3)', width: 1 },
        areaStyle: { color: 'rgba(0,229,255,0.05)' }
      },
      selectedDataBackground: {
        lineStyle: { color: '#00E5FF', width: 1 },
        areaStyle: { color: 'rgba(0,229,255,0.15)' }
      }
    }],
    series: [{
      type: 'line',
      data: values,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 229, 255, 0.3)' },
          { offset: 1, color: 'rgba(0, 229, 255, 0.02)' }
        ])
      },
      lineStyle: { width: 2, color: chartColors.primary },
      itemStyle: { color: chartColors.primary },
      smooth: true
    }]
  }
  trendChart.setOption(option)
}

const initParkingChart = () => {
  if (!parkingChartRef.value) return
  parkingChart = echarts.init(parkingChartRef.value)
  updateParkingChart()
}

const updateParkingChart = () => {
  if (!parkingChart) return
  const times = eventTrendData.value.length > 0 ? eventTrendData.value.map((d: { time: string }) => d.time) : []
  const values = eventTrendData.value.length > 0 ? eventTrendData.value.map((d: { value: number }) => d.value) : []
  const option = {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '3%', top: '10%', bottom: '22%' },
    xAxis: {
      type: 'category',
      data: times,
      boundaryGap: false,
      axisLine: { lineStyle: { color: chartColors.border } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: chartColors.border } },
      splitLine: { lineStyle: { color: chartColors.gridLine } },
      axisLabel: { color: chartColors.textSecondary, fontSize: 10 }
    },
    dataZoom: [{
      type: 'slider',
      show: true,
      start: 0,
      end: 100,
      height: 14,
      bottom: 4,
      borderColor: 'rgba(0,229,255,0.15)',
      fillerColor: 'rgba(0,229,255,0.15)',
      backgroundColor: 'rgba(0,30,60,0.3)',
      handleStyle: { color: '#00E5FF', borderColor: '#00E5FF' },
      textStyle: { color: '#8AAFC8', fontSize: 10 },
      dataBackground: {
        lineStyle: { color: 'rgba(0,229,255,0.3)', width: 1 },
        areaStyle: { color: 'rgba(0,229,255,0.05)' }
      },
      selectedDataBackground: {
        lineStyle: { color: '#00E5FF', width: 1 },
        areaStyle: { color: 'rgba(0,229,255,0.15)' }
      }
    }],
    series: [{
      type: 'line',
      data: values,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(0, 229, 255, 0.4)' },
          { offset: 1, color: 'rgba(0, 229, 255, 0.02)' }
        ])
      },
      lineStyle: { width: 2, color: chartColors.primary },
      itemStyle: { color: chartColors.primary },
      smooth: true
    }]
  }
  parkingChart.setOption(option, true)
}

const handleQuery = async () => {
  await Promise.all([
    fetchTodayStats(),
    fetchViolationStats(),
    fetchAlgorithmSummary(),
    fetchSceneStats(),
    fetchTrendData(),
    fetchEventTrend()
  ])
  initTodayChart()
  initLeftChart()
  initGaugeChart()
  initCenterChart()
  initTrendChart()
  initParkingChart()
}

const resizeCharts = () => {
  todayChart?.resize()
  leftChart?.resize()
  gaugeChart?.resize()
  centerChart?.resize()
  trendChart?.resize()
  parkingChart?.resize()
}

onMounted(async () => {
  await loadRegions()
  await Promise.all([
    fetchTodayStats(),
    fetchViolationStats(),
    fetchAlgorithmSummary(),
    fetchSceneStats(),
    fetchTrendData(),
    fetchEventTrend()
  ])
  initTodayChart()
  initLeftChart()
  initGaugeChart()
  initCenterChart()
  initTrendChart()
  initParkingChart()
  window.addEventListener('resize', resizeCharts)
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  todayChart?.dispose()
  leftChart?.dispose()
  gaugeChart?.dispose()
  centerChart?.dispose()
  trendChart?.dispose()
  parkingChart?.dispose()
})
</script>

<style scoped>
.event-stats-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #020B1F;
  padding: 15px;
}

/* 筛选面板 */
.filter-panel {
  background: rgba(0, 30, 60, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  padding: 12px 16px;
  margin-bottom: 15px;
  flex-shrink: 0;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* 仪表板 */
.dashboard {
  flex: 1;
  display: flex;
  gap: 15px;
  min-height: 0;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 15px;
  min-height: 0;
}

.column-left {
  flex: 2.8;
}

.column-center {
  flex: 3.6;
}

.column-right {
  flex: 3.6;
}

/* 卡片 */
.chart-card {
  background: rgba(0, 30, 60, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  padding: 12px 15px;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.chart-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #00E5FF, transparent);
}

.column-left .chart-card:first-child {
  flex: 0 0 auto;
}

.column-left .chart-card:last-child {
  flex: 1;
  min-height: 0;
}

.column-center .chart-card:first-child {
  flex: 0 0 200px;
}

.column-center .chart-card:last-child {
  flex: 1;
  min-height: 0;
}

.column-right .chart-card {
  flex: 1;
  min-height: 0;
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-shrink: 0;
}

.header-icon {
  width: 12px;
  height: 12px;
  background: #00E5FF;
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
  flex-shrink: 0;
}

.card-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
  white-space: nowrap;
}

.header-controls {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

/* 卡片内容 */
.card-body {
  flex: 1;
  min-height: 0;
  position: relative;
}

.chart-container {
  width: 100%;
  height: 100%;
  min-height: 120px;
}

.gauge-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.gauge-chart {
  width: 80%;
  height: 150px;
}

.gauge-label {
  font-size: 12px;
  color: #00E5FF;
  margin-top: 8px;
}
</style>
