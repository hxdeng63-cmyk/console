<template>
  <div class="video-wrapper">
    <div class="video-container">
      <template v-if="device">
        <MonitoringVideoPlayer
          v-if="isNativeVideo"
          :src="videoUrl"
        />
        <VideoPlayer
          v-else-if="videoUrl"
          :url="videoUrl"
          :protocol="protocol"
          :initial-osd-location="device.name"
        />
        <div v-else-if="loading" class="video-placeholder">
          <span>正在连接视频流...</span>
        </div>
        <div v-else class="video-placeholder">
          <span style="color: #FF006E;">无法连接视频流，请检查设备配置</span>
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
  protocol: string
  loading: boolean
  error: boolean
}>()

const isNativeVideo = isLocalStream(props.sourceType, props.videoUrl)
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