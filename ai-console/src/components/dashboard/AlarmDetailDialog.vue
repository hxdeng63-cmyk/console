<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="报警动态详情"
    width="800px"
    :close-on-click-modal="false"
    class="alarm-detail-dialog"
  >
    <div class="detail-container">
      <div class="detail-image">
        <img
          v-if="alarm?.imageUrl"
          :src="alarm.imageUrl"
          alt="事件图片"
          @error="onImageError"
        />
        <div v-else class="detail-no-image">无图片</div>
      </div>
      <div class="detail-info">
        <div class="detail-row">
          <span class="detail-label">事件名称：</span>
          <span class="detail-value">{{ alarm?.type || '-' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">事件类型：</span>
          <span class="detail-value">{{ alarm?.eventDetail || alarm?.type || '-' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">报警位置：</span>
          <span class="detail-value">{{ alarm?.location || '-' }}</span>
        </div>
        <div class="detail-row">
          <span class="detail-label">处理状态：</span>
          <el-tag :type="statusTagType(alarm?.processStatus)" size="small">
            {{ statusText(alarm?.processStatus || '') }}
          </el-tag>
        </div>
        <div class="detail-row">
          <span class="detail-label">合规状态：</span>
          <span
            class="detail-value"
            :class="alarm?.isCompliant === true ? 'text-success' : alarm?.isCompliant === false ? 'text-danger' : 'text-secondary'"
          >
            {{ alarm?.isCompliant === true ? '合规' : alarm?.isCompliant === false ? '不合规' : '未知' }}
          </span>
        </div>
        <div class="detail-row">
          <span class="detail-label">报警时间：</span>
          <span class="detail-value">{{ alarm?.time || '-' }}</span>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">关闭</el-button>
      <el-button type="primary" @click="emit('playback', alarm)">视频回放</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import type { AlarmItem } from '@/types/alarm'
import { statusText, statusTagType } from '@/constants/processStatus'

defineProps<{
  modelValue: boolean
  alarm: AlarmItem | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'playback', alarm: AlarmItem | null): void
}>()

function onImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}
</script>

<style scoped>
.alarm-detail-dialog :deep(.el-dialog__body) {
  background: #020B1F;
  color: rgba(255, 255, 255, 0.85);
}
.detail-container {
  display: flex;
  gap: 16px;
}
.detail-image {
  flex: 1;
  min-width: 0;
  background: rgba(0, 20, 50, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  overflow: hidden;
}
.detail-image img {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}
.detail-no-image {
  color: rgba(180, 210, 235, 0.6);
  font-size: 13px;
}
.detail-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.detail-row {
  display: flex;
  align-items: center;
  font-size: 13px;
  line-height: 1.6;
}
.detail-label {
  flex-shrink: 0;
  width: 88px;
  color: rgba(180, 210, 235, 0.6);
}
.detail-value {
  color: rgba(255, 255, 255, 0.9);
  word-break: break-all;
}
.detail-value.text-success {
  color: #52C41A;
}
.detail-value.text-danger {
  color: #FF006E;
}
.detail-value.text-secondary {
  color: rgba(180, 210, 235, 0.7);
}
</style>