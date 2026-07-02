<template>
  <div class="channel-content">
    <el-select
      :model-value="channel"
      placeholder="选择通道"
      class="channel-select"
      @update:model-value="emit('update:channel', $event)"
    >
      <el-option
        v-for="ch in channels"
        :key="ch.id"
        :label="ch.name"
        :value="ch.id"
      />
    </el-select>
    <el-select
      :model-value="algorithm"
      placeholder="选择识别算法"
      class="channel-select"
      @update:model-value="emit('update:algorithm', $event)"
      @change="emit('change:algorithm', $event)"
    >
      <el-option-group v-for="algo in algorithms" :key="algo.id" :label="algo.name">
        <el-option
          v-for="ev in algo.events"
          :key="`${algo.id}-${ev.name}`"
          :label="getEventTypeDisplayName(ev.name)"
          :value="`${algo.id}:${ev.moduleName}:${ev.name}`"
          :disabled="!ev.moduleName"
        />
      </el-option-group>
    </el-select>
    <el-button class="draw-btn">
      <el-icon><Edit /></el-icon>
      绘制区域
    </el-button>
    <el-button
      class="start-all-btn"
      type="warning"
      :loading="startingAll"
      @click="emit('start-all')"
    >
      <el-icon><VideoPlay /></el-icon>
      开始监测
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { Edit, VideoPlay } from '@element-plus/icons-vue'

interface AlgorithmGroup {
  id: number
  name: string
  events: AlgorithmEvent[]
}

interface AlgorithmEvent {
  name: string
  moduleName: string
}

interface Channel {
  id: string
  name: string
}

defineProps<{
  channels: Channel[]
  algorithms: AlgorithmGroup[]
  channel: string
  algorithm: string
  startingAll: boolean
  getEventTypeDisplayName: (name: string) => string
}>()

const emit = defineEmits<{
  (e: 'update:channel', v: string): void
  (e: 'update:algorithm', v: string): void
  (e: 'change:algorithm', v: string): void
  (e: 'start-all'): void
}>()
</script>

<style scoped>
.channel-content {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.channel-select {
  flex: 1 1 100%;
  min-width: 0;
}

.draw-btn,
.start-all-btn {
  flex: 1;
  min-width: 0;
}

.draw-btn {
  border-color: #00E5FF;
  color: #00E5FF;
}

.draw-btn:hover {
  background: rgba(0, 229, 255, 0.1);
}

.start-all-btn {
  border-color: #ff9f43;
  color: #ff9f43;
  background: transparent;
}

.start-all-btn:hover {
  background: rgba(255, 159, 67, 0.1);
}
</style>