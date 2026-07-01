<template>
  <div class="bottom-info">
    <div class="info-left">
      <div class="info-item">
        <span class="info-label">布控信息：</span>
        <span class="info-value">{{ deploymentInfo }}</span>
      </div>
      <div class="info-item">
        <span class="info-label">视频质量检测：</span>
        <span class="info-value quality-ok">正常</span>
      </div>
    </div>
    <el-radio-group :model-value="filter" size="small" @update:model-value="emit('update:filter', $event)">
      <el-radio-button value="all">全部</el-radio-button>
      <el-radio-button value="danger">不合规</el-radio-button>
    </el-radio-group>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  deploymentInfo: string
  filter: 'all' | 'danger'
}>()

const emit = defineEmits<{
  (e: 'update:filter', value: 'all' | 'danger'): void
}>()
</script>

<style scoped>
.bottom-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: rgba(0, 10, 30, 0.9);
  border-top: 1px solid rgba(0, 229, 255, 0.1);
}
.info-left {
  display: flex;
  gap: 40px;
}
.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.info-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}
.info-value {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}
.info-value.quality-ok {
  color: #00FF88;
}
</style>