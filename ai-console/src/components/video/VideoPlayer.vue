<template>
  <div class="video-player" :class="{ fullscreen: isFullscreen }">
    <div class="video-container">
      <video
        ref="videoRef"
        class="video-element"
        playsinline
        :muted="!showOverlays"
        @canplay="onCanplay"
      ></video>

      <canvas ref="canvasRef" class="video-canvas"></canvas>

      <div class="osd-overlay" v-if="showOverlays && (osdText || osdLocation)">
        <span class="osd-location">{{ osdLocation }}</span>
        <span class="osd-timestamp">{{ currentTime }}</span>
        <span class="osd-text">{{ osdText }}</span>
      </div>

      <div class="bandwidth-display" v-if="showOverlays && bandwidth > 0">
        <span class="bandwidth-value">{{ formatBandwidth(bandwidth) }}</span>
      </div>

      <div class="loading-overlay" v-if="isLoading">
        <div class="loading-spinner"></div>
      </div>

      <div class="error-overlay" v-if="hasError">
        <div class="error-content">
          <span class="error-icon">!</span>
          <span class="error-message">{{ errorMessage }}</span>
          <button class="retry-button" @click="retry">Retry</button>
        </div>
      </div>

      <div class="controls-overlay" v-if="showOverlays && !isLoading && !hasError">
        <button
          v-if="showProtocolToggle"
          class="control-button protocol-toggle"
          @click="toggleProtocol"
          :title="`Switch to ${currentProtocol === 'flv' ? 'HLS' : 'FLV'}`"
        >
          {{ currentProtocol.toUpperCase() }}
        </button>

        <button
          class="control-button fullscreen-toggle"
          @click="toggleFullscreen"
          :title="isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'"
        >
          <svg v-if="!isFullscreen" viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" width="20" height="20">
            <path fill="currentColor" d="M5 16h3v3h2v-5H5v2zm3-8H5v2h5V5H8v3zm6 11h2v-3h3v-2h-5v5zm2-11V5h-2v5h5V8h-3z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useVideoPlayer, type Protocol } from './useVideoPlayer'
import { useStreamPoolStore } from '@/stores/streamPool'

interface Props {
  url: string
  protocol: Protocol
  enableDualProtocol?: boolean
  initialOsdText?: string
  initialOsdLocation?: string
  autoStart?: boolean
  showOverlays?: boolean
  deviceId?: string
}

const props = withDefaults(defineProps<Props>(), {
  protocol: 'flv',
  enableDualProtocol: false,
  initialOsdText: '',
  initialOsdLocation: '',
  autoStart: true,
  showOverlays: true,
})

const emit = defineEmits<{
  (e: 'canvas-ref', ref: HTMLCanvasElement | null): void
  (e: 'canplay'): void
}>()

const streamPoolStore = useStreamPoolStore()
const currentTime = ref('')
const retryTimer = ref<number | null>(null)

const {
  videoRef,
  canvasRef,
  isLoading,
  hasError,
  errorMessage,
  isFullscreen,
  bandwidth,
  osdText,
  osdLocation,
  currentProtocol,
  showProtocolToggle,
  toggleProtocol,
  retry,
  toggleFullscreen,
  updateOsd,
  switchUrl,
  pauseBuffering,
  resumeBuffering,
  start,
  stopBackgroundActivity,
  resumeBackgroundActivity,
  setProtocol,
} = useVideoPlayer({
  url: props.url,
  protocol: props.protocol,
  enableDualProtocol: props.enableDualProtocol,
  autoStart: props.autoStart,
})

watch([() => props.initialOsdText, () => props.initialOsdLocation], () => {
  updateOsd(props.initialOsdText, props.initialOsdLocation)
})

watch(() => props.url, (newUrl) => {
  if (newUrl && props.autoStart !== false) {
    switchUrl(newUrl)
  }
})

// protocol prop 变化时必须让 player 按新协议重建 — useVideoPlayer 内部 currentProtocol
// 只在初始化时取了一次,父组件 protocol 变化(典型: 选算法后 useCurrentStream 把
// protocol 从 flv 翻 hls)不会被自动感知。setProtocol 内部同步 currentProtocol + loadMedia。
watch(() => props.protocol, (newProto) => {
  if (newProto) setProtocol(newProto)
})

watch(canvasRef, (el) => {
  emit('canvas-ref', el)
})

watch(canvasRef, (el) => {
  if (el && videoRef.value) {
    const video = videoRef.value
    const canvas = el
    canvas.width = video.clientWidth || 800
    canvas.height = video.clientHeight || 450
  }
})

function formatBandwidth(bps: number): string {
  if (bps < 1024) {
    return `${bps.toFixed(0)} bps`
  } else if (bps < 1024 * 1024) {
    return `${(bps / 1024).toFixed(1)} Kbps`
  } else {
    return `${(bps / (1024 * 1024)).toFixed(2)} Mbps`
  }
}

function scheduleAutoRetry() {
  if (!props.deviceId) return
  streamPoolStore.setDeviceStatus(props.deviceId, 'error')
  streamPoolStore.incrementRetry(props.deviceId)
  const device = streamPoolStore.hlsDevices.find(d => d.id === props.deviceId)
  const retryCount = device?.retryCount || 0
  if (retryCount > 5) return
  const delay = Math.min(1000 * Math.pow(2, retryCount - 1), 10000)
  retryTimer.value = window.setTimeout(() => {
    if (!props.deviceId) return
    streamPoolStore.setDeviceStatus(props.deviceId, 'buffering')
    retry()
  }, delay)
}

function markDeviceReady() {
  if (!props.deviceId) return
  streamPoolStore.setDeviceStatus(props.deviceId, 'ready')
  streamPoolStore.resetRetry(props.deviceId)
  if (retryTimer.value !== null) {
    window.clearTimeout(retryTimer.value)
    retryTimer.value = null
  }
}

watch(hasError, (err) => {
  if (err) {
    scheduleAutoRetry()
  }
})

function onCanplay() {
  markDeviceReady()
  emit('canplay')
}

function updateTimestamp() {
  if (videoRef.value) {
    const now = new Date()
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')
    currentTime.value = `${hours}:${minutes}:${seconds}`
  }
}

let timestampInterval: ReturnType<typeof setInterval> | null = null

function startTimestampInterval() {
  if (timestampInterval) return
  updateTimestamp()
  timestampInterval = setInterval(updateTimestamp, 1000)
}

function stopTimestampInterval() {
  if (timestampInterval) {
    clearInterval(timestampInterval)
    timestampInterval = null
  }
}

watch(() => props.showOverlays, (enabled) => {
  if (enabled !== false) {
    startTimestampInterval()
  } else {
    stopTimestampInterval()
  }
})

onMounted(() => {
  if (props.showOverlays !== false) {
    startTimestampInterval()
  }
})

onUnmounted(() => {
  stopTimestampInterval()
})

defineExpose({
  videoRef,
  canvasRef,
  updateOsd,
  toggleFullscreen,
  retry,
  toggleProtocol,
  pauseBuffering,
  resumeBuffering,
  start,
  stopBackgroundActivity,
  resumeBackgroundActivity,
})
</script>

<style scoped>
.video-player {
  --primary-color: #00E5FF;
  --tech-accent: #00d4ff;
  --bg-overlay: rgba(0, 0, 0, 0.6);

  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}

.video-player.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999;
  border-radius: 0;
}

.video-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.video-element {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.video-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.osd-overlay {
  position: absolute;
  top: 10px;
  left: 10px;
  right: 10px;
  display: flex;
  gap: 16px;
  color: var(--tech-accent);
  font-size: 12px;
  font-family: 'Courier New', monospace;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.8);
  pointer-events: none;
}

.osd-location,
.osd-timestamp,
.osd-text {
  background: rgba(0, 0, 0, 0.5);
  padding: 4px 8px;
  border-radius: 2px;
}

.bandwidth-display {
  position: absolute;
  bottom: 10px;
  right: 10px;
  background: rgba(0, 0, 0, 0.6);
  color: var(--primary-color);
  padding: 4px 8px;
  border-radius: 2px;
  font-size: 11px;
  font-family: 'Courier New', monospace;
  border: 1px solid var(--primary-color);
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-overlay);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(24, 144, 255, 0.2);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-overlay);
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #FF006E;
}

.error-icon {
  width: 48px;
  height: 48px;
  border: 3px solid #FF006E;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
}

.error-message {
  font-size: 14px;
}

.retry-button {
  background: var(--primary-color);
  color: #000;
  border: none;
  padding: 8px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.retry-button:hover {
  background: #00B4D8;
}

.controls-overlay {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.video-container:hover .controls-overlay {
  opacity: 1;
}

.control-button {
  background: rgba(0, 0, 0, 0.6);
  border: 1px solid var(--primary-color);
  color: var(--tech-accent);
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.control-button:hover {
  background: var(--primary-color);
  color: #000;
}

.protocol-toggle {
  font-size: 11px;
  font-weight: bold;
  font-family: 'Courier New', monospace;
}
</style>
