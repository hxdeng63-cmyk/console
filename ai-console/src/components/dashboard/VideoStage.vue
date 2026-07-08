<template>
  <div class="video-wrapper">
    <!-- 状态灯 -->
    <div class="status-light" :class="statusLightClass" data-test="status-light"></div>

    <div class="video-container">
      <!-- 错误优先覆盖 -->
      <div v-if="error" class="overlay error" data-test="error">
        <div class="error-text">{{ error }}</div>
        <button class="retry-btn" @click="handleRetry" data-test="retry-btn">重试</button>
      </div>

      <!-- 加载覆盖 -->
      <div v-else-if="loading" class="overlay loading" data-test="loading">
        正在加载 ({{ protocolText }})...
      </div>

      <!-- 正常视频流 -->
      <template v-else-if="device">
        <MonitoringVideoPlayer
          v-if="isNativeVideo"
          :src="videoUrl"
        />
        <VideoPlayer
          v-else-if="videoUrl"
          :url="videoUrl"
          :protocol="protocol"
          :initial-osd-location="device.name"
          :refresh-stream-url="refreshStreamUrl"
          :fallback-url="fallbackUrl"
          :realtime-event="realtimeEvent"
          @hls-network-error="emit('hls-network-error')"
        />
        <div v-else class="video-placeholder">
          <span>正在连接视频流...</span>
        </div>
      </template>
      <div v-else class="video-placeholder">
        <span>等待选择设备...</span>
      </div>

      <div class="video-corner top-left"></div>
      <div class="video-corner top-right"></div>
      <div class="video-corner bottom-left"></div>
      <div class="video-corner bottom-right"></div>
    </div>
    <div class="video-footer">
      <div class="footer-line"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Ref } from 'vue'
import MonitoringVideoPlayer from '@/components/monitor/MonitoringVideoPlayer.vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import { isLocalStream } from '@/utils/streamUrl'

interface Device {
  id: string
  name: string
}

const props = defineProps<{
  device: Device | null
  videoUrl: string
  sourceType: string
  protocol: 'flv' | 'hls'
  loading: boolean
  error: string
  refreshStreamUrl?: () => Promise<string | null>
  // HLS 多次失败时回退到此 URL（由 backend stream API 返的 device_fallback_url 传入,
  //       实际形如 /data/monitoring/<device.name>.mp4）
  fallbackUrl?: string
  // 实时事件 ref（来自 useRealtimeSocket），用于在视频上画 bbox
  realtimeEvent?: Ref<{ event_detail?: Record<string, any> | null } | null>
}>()

const isNativeVideo = computed(() => isLocalStream(props.sourceType, props.videoUrl))

const protocolText = computed(() => props.protocol.toUpperCase())

const statusLightClass = computed(() => {
  if (props.error) return 'error'
  if (props.loading) return 'loading'
  return 'online'
})

function handleRetry() {
  // 通知父组件触发刷新
  void props.refreshStreamUrl?.()
}

const emit = defineEmits<{
  (e: 'hls-network-error'): void
}>()
</script>

<style scoped>
.video-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000;
  border: 1px solid #00E5FF;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}
.video-container {
  flex: 1;
  position: relative;
  background: #000;
}
.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 229, 255, 0.4);
  font-size: 18px;
}
.status-light {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  z-index: 20;
  pointer-events: none;
}
.status-light.online { background: #00FF88; box-shadow: 0 0 8px #00FF88; }
.status-light.loading { background: #FFAA00; box-shadow: 0 0 8px #FFAA00; }
.status-light.error { background: #FF006E; box-shadow: 0 0 8px #FF006E; }
.overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  z-index: 10;
  gap: 16px;
}
.error-text { font-size: 16px; }
.retry-btn {
  padding: 8px 24px;
  background: #00E5FF;
  color: #000;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}
.retry-btn:hover { background: #00BFFF; }
.video-corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border-color: #00E5FF;
  border-style: solid;
  pointer-events: none;
}
.video-corner.top-left {
  top: 0;
  left: 0;
  border-width: 3px 0 0 3px;
}
.video-corner.top-right {
  top: 0;
  right: 0;
  border-width: 3px 3px 0 0;
}
.video-corner.bottom-left {
  bottom: 0;
  left: 0;
  border-width: 0 0 3px 3px;
}
.video-corner.bottom-right {
  bottom: 0;
  right: 0;
  border-width: 0 3px 3px 0;
}
.video-footer {
  height: 6px;
  background: linear-gradient(90deg, #00E5FF, #0099FF, #00E5FF);
  padding: 0 20px;
}
.footer-line {
  height: 100%;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 10px,
    rgba(0, 0, 0, 0.5) 10px,
    rgba(0, 0, 0, 0.5) 20px
  );
}
</style>