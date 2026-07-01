<template>
  <div class="panel-section level-section">
    <div class="level-item">
      <div class="level-header">
        <span class="level-label">{{ label }}</span>
      </div>
      <div class="level-bar">
        <div class="level-gradient" :class="gradientClass"></div>
        <div class="level-marker" :style="{ left: position }"></div>
      </div>
      <div class="level-scale">
        <span v-for="s in scaleLabels" :key="s">{{ s }}</span>
      </div>
      <div v-if="statusText" class="level-status" :class="statusClass">{{ statusText }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  label: string
  value: number
  max: number
  scaleLabels: string[]
  statusText?: string
  statusClass?: string
  gradientClass?: string
}>()

const position = computed(() => {
  const clamped = Math.max(0, Math.min(props.value, props.max))
  return `${((clamped - 1) / (props.max - 1)) * 100}%`
})
</script>

<style scoped>
.level-item {
  margin-bottom: 12px;
}
.level-item:last-child {
  margin-bottom: 0;
}
.level-header {
  margin-bottom: 6px;
}
.level-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}
.level-bar {
  position: relative;
  height: 8px;
  background: linear-gradient(90deg, #00FF88, #FFB800, #FF006E);
  border-radius: 4px;
  margin-bottom: 4px;
}
.level-gradient {
  width: 100%;
  height: 100%;
  border-radius: 4px;
}
.level-gradient.visibility {
  background: linear-gradient(90deg, #FF006E, #FFB800, #00FF88);
}
.level-marker {
  position: absolute;
  top: -4px;
  width: 4px;
  height: 16px;
  background: rgba(180, 210, 235, 0.85);
  border-radius: 2px;
  transform: translateX(-50%);
}
.level-scale {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}
.level-status {
  text-align: center;
  font-size: 12px;
  margin-top: 4px;
  padding: 2px 8px;
  border-radius: 2px;
  display: inline-block;
}
.level-status.level-1 {
  background: rgba(82, 196, 26, 0.2);
  color: #00FF88;
}
.level-status.level-2 {
  background: rgba(255, 170, 0, 0.2);
  color: #FFB800;
}
.level-status.level-3 {
  background: rgba(255, 100, 0, 0.2);
  color: #FF6E00;
}
.level-status.level-4 {
  background: rgba(255, 0, 110, 0.2);
  color: #FF006E;
}
.level-status.level-5 {
  background: rgba(180, 0, 80, 0.3);
  color: #FF5599;
}
.panel-section {
  background: rgba(0, 20, 50, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  padding: 12px;
  flex-shrink: 0;
}
</style>