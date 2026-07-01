<template>
  <div v-loading="loading" class="panel-section events-section">
    <div class="section-header">
      <span class="header-bar"></span>
      <span class="section-title">交通事件统计</span>
      <span class="header-line"></span>
    </div>
    <div class="donut-chart-area">
      <div class="donut-chart">
        <div class="donut-circle" :style="donutStyle"></div>
        <div class="donut-center">
          <span class="donut-total">{{ stats.total }}</span>
          <span class="donut-label">交通事件</span>
        </div>
      </div>
      <div class="donut-legend">
        <div class="legend-item" v-for="item in stats.legend" :key="item.name">
          <span class="legend-dot" :style="{ background: item.color }"></span>
          <span class="legend-name">{{ item.name }}</span>
          <span class="legend-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface LegendItem {
  name: string
  value: number
  color: string
}

interface EventStats {
  total: number
  legend: LegendItem[]
}

const props = defineProps<{
  stats: EventStats
  loading?: boolean
}>()

const donutStyle = computed(() => {
  const legend = props.stats.legend
  if (legend.length === 0 || props.stats.total === 0) {
    return { background: 'conic-gradient(rgba(0,229,255,0.2) 0% 100%)' }
  }
  let gradient = ''
  let currentPercent = 0
  legend.forEach((item, index) => {
    const percent = (item.value / props.stats.total) * 100
    gradient += `${item.color} ${currentPercent}% ${currentPercent + percent}%`
    if (index < legend.length - 1) gradient += ', '
    currentPercent += percent
  })
  return { background: `conic-gradient(${gradient})` }
})
</script>

<style scoped>
.donut-chart-area {
  display: flex;
  align-items: center;
  gap: 20px;
}
.donut-chart {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}
.donut-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}
.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
.donut-total {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #00E5FF;
}
.donut-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
}
.donut-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}
.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 4px;
}
.legend-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
}
.legend-value {
  font-weight: bold;
  color: rgba(180, 210, 235, 0.85);
}
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.header-bar {
  width: 3px;
  height: 14px;
  background: #00E5FF;
}
.section-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
}
.header-line {
  flex: 1;
  height: 1px;
  background: repeating-linear-gradient(
    90deg,
    rgba(0, 229, 255, 0.3),
    rgba(0, 229, 255, 0.3) 4px,
    transparent 4px,
    transparent 8px
  );
}
.panel-section {
  background: rgba(0, 20, 50, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  padding: 12px;
  flex-shrink: 0;
}
</style>