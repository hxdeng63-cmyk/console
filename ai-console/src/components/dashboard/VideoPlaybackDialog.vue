<template>
  <el-dialog
    :model-value="modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    title="视频回放"
    width="800px"
    :close-on-click-modal="false"
    class="video-playback-dialog"
  >
    <div class="video-playback-container">
      <video
        v-if="url && !videoError"
        :src="url"
        controls
        autoplay
        style="width: 100%; max-height: 500px;"
        @error="onVideoError"
      />
      <div v-else class="video-playback-empty">暂无视频</div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  modelValue: boolean
  url: string
}>()

defineEmits<{
  (e: 'update:modelValue', v: boolean): void
}>()

const videoError = ref(false)

// 重置 error 状态：每次打开对话框时
watch(() => props.modelValue, (open) => {
  if (open) videoError.value = false
})

function onVideoError() {
  videoError.value = true
}
</script>

<style scoped>
.video-playback-dialog :deep(.el-dialog__body) {
  background: #020B1F;
}
.video-playback-container {
  width: 100%;
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 20, 50, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
}
.video-playback-empty {
  color: rgba(180, 210, 235, 0.6);
  font-size: 13px;
  padding: 60px 0;
}
</style>