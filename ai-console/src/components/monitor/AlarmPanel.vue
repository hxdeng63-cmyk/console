<template>
  <div class="alarm-panel">
    <div class="alarm-list" ref="listRef">
      <TransitionGroup name="alarm">
        <div
          v-for="alarm in filteredAlarms"
          :key="alarm.id"
          class="alarm-item"
          :class="{ 'is-new': alarm.isNew }"
        >
          <div class="alarm-main">
            <div class="alarm-header">
              <span class="device-name">{{ alarm.deviceName }}</span>
              <span class="compliant-tag" :class="alarm.compliant ? 'compliant' : 'violation'">
                {{ alarm.compliant ? '合规' : '不合规' }}
              </span>
            </div>
            <div class="alarm-body">
              <span class="event-type">{{ alarm.eventType }}</span>
              <span class="capture-time">{{ alarm.captureTime }}</span>
            </div>
          </div>
        </div>
      </TransitionGroup>

      <el-empty v-if="filteredAlarms.length === 0" description="暂无数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElEmpty } from 'element-plus'

export interface AlarmItem {
  id: string
  deviceName: string
  eventType: string
  compliant: boolean
  captureTime: string
  isNew?: boolean
}

interface Props {
  alarms: AlarmItem[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'alarm-click', alarm: AlarmItem): void
}>()

const listRef = ref<HTMLElement | null>(null)

const filteredAlarms = computed(() => {
  return props.alarms
})

function handleAlarmClick(alarm: AlarmItem) {
  emit('alarm-click', alarm)
}

onMounted(() => {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = 0
    }
  })
})
</script>

<style scoped>
.alarm-panel {
  --primary-color: #00E5FF;
  --tech-accent: #00E5FF;
  --compliant-color: #00FF88;
  --violation-color: #FF006E;
  --bg-card: linear-gradient(145deg, rgba(0, 50, 80, 0.5) 0%, rgba(0, 25, 50, 0.75) 100%);

  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-card);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 229, 255, 0.18);
  backdrop-filter: blur(18px) saturate(170%);
}

.alarm-list {
  flex: 1;
  overflow-y: auto;
  max-height: 100%;
  padding: 8px;
}

.alarm-item {
  background: linear-gradient(135deg, rgba(0, 20, 50, 0.7) 0%, rgba(0, 10, 30, 0.85) 100%);
  border: 1px solid rgba(0, 229, 255, 0.12);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.alarm-item:hover {
  border-color: rgba(0, 229, 255, 0.4);
  background: linear-gradient(135deg, rgba(0, 40, 80, 0.6) 0%, rgba(0, 20, 50, 0.8) 100%);
  box-shadow: 0 4px 25px rgba(0, 229, 255, 0.15);
  transform: translateX(4px);
}

.alarm-item.is-new {
  animation: alarmHighlight 2s ease-out;
  border-color: var(--tech-accent);
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
}

@keyframes alarmHighlight {
  0% {
    background: rgba(0, 229, 255, 0.25);
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 229, 255, 0.4);
  }
  100% {
    background: rgba(0, 20, 50, 0.7);
    transform: translateY(0);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  }
}

.alarm-main {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alarm-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.device-name {
  font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
  font-size: 13px;
  font-weight: 600;
  color: rgba(180, 210, 235, 0.85);
  letter-spacing: 0.5px;
}

.compliant-tag {
  font-family: 'Orbitron', sans-serif;
  font-size: 10px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 500;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.compliant-tag.compliant {
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 255, 136, 0.1) 100%);
  color: var(--compliant-color);
  border: 1px solid rgba(0, 255, 136, 0.4);
  box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
}

.compliant-tag.violation {
  background: linear-gradient(135deg, rgba(255, 0, 110, 0.2) 0%, rgba(255, 0, 110, 0.1) 100%);
  color: var(--violation-color);
  border: 1px solid rgba(255, 0, 110, 0.4);
  box-shadow: 0 0 10px rgba(255, 0, 110, 0.2);
  animation: violation-pulse 2s ease-in-out infinite;
}

@keyframes violation-pulse {
  0%, 100% { box-shadow: 0 0 8px rgba(255, 0, 110, 0.2); }
  50% { box-shadow: 0 0 15px rgba(255, 0, 110, 0.4); }
}

.alarm-body {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.event-type {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  color: var(--tech-accent);
  letter-spacing: 1px;
  text-transform: uppercase;
  text-shadow: 0 0 8px rgba(0, 229, 255, 0.4);
}

.capture-time {
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.5px;
}

/* Transition animations */
.alarm-enter-active {
  animation: fadeIn 0.4s ease-out, slideDown 0.4s ease-out;
}

.alarm-leave-active {
  animation: fadeOut 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideDown {
  from {
    transform: translateY(-8px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* Scrollbar styling */
.alarm-list::-webkit-scrollbar {
  width: 4px;
}

.alarm-list::-webkit-scrollbar-track {
  background: rgba(0, 20, 50, 0.5);
  border-radius: 2px;
}

.alarm-list::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #00E5FF, #00FF88);
  border-radius: 2px;
  box-shadow: 0 0 6px rgba(0, 229, 255, 0.5);
}

.alarm-list::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #00FF88, #00E5FF);
}

:deep(.el-empty__description) {
  color: rgba(0, 229, 255, 0.6);
  font-family: 'Rajdhani', sans-serif;
}
</style>
