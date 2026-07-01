<template>
  <div v-loading="loading" class="panel-section traffic-section">
    <div class="section-header">
      <span class="header-bar"></span>
      <span class="section-title">实时交通参数</span>
      <span class="header-line"></span>
    </div>
    <div class="traffic-grid">
      <div class="traffic-item">
        <div class="traffic-value primary">{{ data.avgSpeed }}</div>
        <div class="traffic-label">平均速度 (km/h)</div>
      </div>
      <div class="traffic-item">
        <div class="traffic-value">{{ data.upTraffic }}</div>
        <div class="traffic-label">上行车流量</div>
      </div>
      <div class="traffic-item">
        <div class="traffic-value">{{ data.downTraffic }}</div>
        <div class="traffic-label">下行车流量</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface TrafficData {
  avgSpeed: string | number
  upTraffic: string | number
  downTraffic: string | number
}

defineProps<{
  data: TrafficData
  loading?: boolean
}>()
</script>

<style scoped>
.traffic-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}
.traffic-item {
  text-align: center;
}
.traffic-value {
  font-size: 28px;
  font-weight: bold;
  color: rgba(180, 210, 235, 0.85);
  margin-bottom: 4px;
}
.traffic-value.primary {
  color: #00E5FF;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}
.traffic-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
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