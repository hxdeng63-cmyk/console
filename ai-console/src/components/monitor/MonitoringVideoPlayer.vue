<template>
  <div class="monitoring-video-player">
    <video
      v-if="src"
      ref="videoRef"
      class="video-element"
      :src="src"
      controls
      loop
      autoplay
      muted
      @error="handleError"
      @loadedmetadata="handleLoaded"
    />
    <div v-if="error" class="error-overlay">
      <el-icon :size="48" color="rgba(255, 0, 110, 0.6)"><VideoPlay /></el-icon>
      <p>{{ error }}</p>
    </div>
    <div v-else-if="loading" class="loading-overlay">
      <el-icon class="spin" :size="32" color="#00E5FF"><Loading /></el-icon>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { VideoPlay, Loading } from '@element-plus/icons-vue'

interface Props {
  src: string
}

const props = defineProps<Props>()

const videoRef = ref<HTMLVideoElement | null>(null)
const error = ref('')
const loading = ref(true)

watch(
  () => props.src,
  () => {
    error.value = ''
    loading.value = true
  }
)

function handleError() {
  loading.value = false
  error.value = '视频加载失败，文件不存在或格式不支持'
}

function handleLoaded() {
  loading.value = false
  error.value = ''
  videoRef.value?.play().catch(() => {})
}
</script>

<style scoped>
.monitoring-video-player {
  width: 100%;
  height: 100%;
  position: relative;
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.error-overlay,
.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(232, 244, 255, 0.6);
  font-size: 14px;
}

.error-overlay {
  background: rgba(0, 0, 0, 0.7);
}

.loading-overlay {
  background: rgba(0, 0, 0, 0.5);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
