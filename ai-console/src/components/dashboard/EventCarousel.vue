<template>
  <div class="bottom-events">
    <div class="events-header">
      <span class="events-title">实时事件抓拍</span>
    </div>
    <div class="events-carousel">
      <div
        v-for="event in events"
        :key="event.id"
        class="event-card clickable"
        @click="emit('alarm-click', event)"
      >
        <div class="event-thumb">
          <img :src="event.imageUrl" :alt="event.type" @error="onImageError" />
          <div class="event-no-image" :style="{ display: event.imageUrl ? 'none' : 'flex' }">无图片</div>
          <div class="event-time">{{ event.time }}</div>
        </div>
        <div class="event-info">
          <div class="event-location">
            {{ event.deviceName || event.device }}
            <template v-if="event.location"> · {{ event.location }}</template>
          </div>
          <div class="event-tags">
            <span
              class="event-status"
              :class="event.isCompliant === true ? 'compliant' : event.isCompliant === false ? 'non-compliant' : 'unknown'"
            >
              {{ formatCompliance(event.isCompliant) }}
            </span>
            <span class="event-process-status">{{ statusText(event.processStatus || '') }}</span>
          </div>
          <div class="event-type">{{ event.type }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AlarmItem } from '@/types/alarm'
import { statusText } from '@/constants/processStatus'
import { formatCompliance } from '@/utils/compliance'

defineProps<{
  events: AlarmItem[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'alarm-click', alarm: AlarmItem): void
}>()

function onImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
  const placeholder = img.nextElementSibling as HTMLElement | null
  if (placeholder) placeholder.style.display = 'flex'
}
</script>

<style scoped>
.bottom-events {
  padding: 12px 20px;
  background: rgba(0, 20, 50, 0.6);
  border-top: 1px solid rgba(0, 229, 255, 0.2);
}
.events-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}
.events-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
}
.events-carousel {
  display: flex;
  gap: 12px;
  overflow-x: auto;
}
.events-carousel::-webkit-scrollbar {
  height: 4px;
}
.events-carousel::-webkit-scrollbar-thumb {
  background: rgba(0, 229, 255, 0.3);
  border-radius: 2px;
}
.event-card {
  flex-shrink: 0;
  width: 140px;
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}
.event-card.clickable {
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.event-card.clickable:hover {
  border-color: #00E5FF;
  box-shadow: 0 0 6px rgba(0, 229, 255, 0.35);
}
.event-thumb {
  position: relative;
  height: 80px;
  overflow: hidden;
}
.event-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.event-no-image {
  position: absolute;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(0, 20, 40, 0.8);
  color: rgba(180, 210, 235, 0.85);
  font-size: 12px;
}
.event-time {
  position: absolute;
  top: 4px;
  right: 4px;
  padding: 1px 6px;
  background: rgba(0, 0, 0, 0.55);
  color: #00E5FF;
  font-size: 10px;
  border-radius: 2px;
  pointer-events: none;
}
.event-info {
  padding: 6px 8px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.event-location {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.event-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.event-status {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 2px;
  white-space: nowrap;
}
.event-status.compliant {
  background: rgba(82, 196, 26, 0.2);
  color: #52C41A;
}
.event-status.non-compliant {
  background: rgba(255, 0, 110, 0.2);
  color: #FF006E;
}
.event-status.unknown {
  background: rgba(120, 130, 150, 0.2);
  color: rgba(180, 210, 235, 0.7);
}
.event-process-status {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 2px;
  background: rgba(0, 153, 255, 0.2);
  color: #0099FF;
  white-space: nowrap;
}
.event-type {
  font-size: 11px;
  color: rgba(180, 210, 235, 0.85);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>