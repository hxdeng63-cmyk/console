<template>
  <div class="file-analysis-page">
    <ThreeColumnLayout>
      <template #left>
        <div class="left-panel">
          <div class="panel-header">
            <h4 class="panel-title">设备列表</h4>
          </div>
          <div class="filter-row">
            <el-select v-model="selectedRoad" placeholder="道路" size="small" class="filter-select">
              <el-option label="道路" value="road" />
              <el-option label="G213" value="G213" />
            </el-select>
            <el-select v-model="selectedSection" placeholder="G213" size="small" class="filter-select">
              <el-option label="G213" value="G213" />
              <el-option label="川大高速" value="chuan" />
            </el-select>
          </div>
          <el-input
            v-model="searchText"
            placeholder="输入关键字进行过滤"
            size="small"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <DeviceTree
            :data="deviceTreeData"
            mode="radio"
            @node-click="handleDeviceClick"
          />
          <div v-if="selectedDevice" class="file-list">
            <div class="file-list-header">
              <span>录像文件</span>
            </div>
            <el-table
              :data="videoFileList"
              size="small"
              @row-click="handleFileClick"
              style="width: 100%"
            >
              <el-table-column prop="fileName" label="文件名称" show-overflow-tooltip />
              <el-table-column prop="startTime" label="开始时间" width="140" />
              <el-table-column prop="duration" label="时长(秒)" width="80" />
            </el-table>
          </div>
        </div>
      </template>

      <template #middle>
        <div class="middle-panel">
          <div class="video-section">
            <VideoPlayer
              v-if="currentFile"
              url=""
              protocol="hls"
            />
            <div v-else class="video-placeholder">
              <span>请选择设备和文件进行播放</span>
            </div>
          </div>
          <div v-if="currentFile" class="timeline-section">
            <span class="time-label">{{ currentFile.startTime }}</span>
            <el-slider v-model="playProgress" :show-tooltip="false" />
            <span class="time-label">{{ formatDuration(currentFile.duration) }}</span>
          </div>
          <div v-if="currentFile" class="controls-section">
            <el-button-group>
              <el-button @click="togglePlay">
                {{ isPlaying ? '暂停' : '播放' }}
              </el-button>
              <el-button @click="toggleFullscreen">
                全屏
              </el-button>
            </el-button-group>
          </div>
        </div>
      </template>

      <template #right>
        <div class="right-panel">
          <div class="panel-header">
            <h4 class="panel-title">报警动态</h4>
          </div>
          <div class="filter-row">
            <el-select v-model="selectedAlarmType" placeholder="全部" size="small" class="filter-select">
              <el-option label="全部" value="all" />
              <el-option label="不合规" value="violation" />
            </el-select>
            <el-select v-model="selectedAlarmLevel" placeholder="不合规" size="small" class="filter-select">
              <el-option label="不合规" value="violation" />
              <el-option label="全部" value="all" />
            </el-select>
          </div>
          <div v-if="alarmLoading" class="alarm-loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>加载中...</span>
          </div>
          <AlarmPanel v-else :alarms="alarmList" @alarm-click="handleAlarmClick" />
        </div>
      </template>
    </ThreeColumnLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import ThreeColumnLayout from '@/components/layout/ThreeColumnLayout.vue'
import DeviceTree from '@/components/device-tree/DeviceTree.vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import AlarmPanel from '@/components/monitor/AlarmPanel.vue'
import { getDevices } from '@/api/devices'
import { getList as getWarningEvents } from '@/api/warning-events'
import request from '@/api/index.js'
import type { DeviceNode } from '@/components/device-tree/useDeviceTree'

interface VideoFile {
  id: number
  fileName: string
  startTime: string
  duration: number
}

const selectedDevice = ref<DeviceNode | null>(null)
const currentFile = ref<VideoFile | null>(null)
const playProgress = ref(0)
const isPlaying = ref(false)
const searchText = ref('')
const selectedRoad = ref('road')
const selectedSection = ref('G213')
const selectedAlarmType = ref('all')
const selectedAlarmLevel = ref('violation')

// 设备树数据（从API获取）
const deviceTreeData = ref<DeviceNode[]>([])

// 报警列表（从API获取）
const alarmList = ref<any[]>([])
const alarmLoading = ref(false)

const fetchAlarms = async () => {
  alarmLoading.value = true
  try {
    const res: any = await getWarningEvents({ page: 1, page_size: 50 })
    const items = res.items || []
    alarmList.value = items.map((item: any) => ({
      id: item.id,
      time: item.time || item.captureTime?.split(' ')[1] || '00:00:00',
      type: item.type || '未知',
      device: item.device || '',
      location: item.location || '',
      level: item.level || 'info',
      handled: item.handled ?? false,
      isCompliant: item.isCompliant ?? true,
      imageUrl: item.imageUrl || '',
      captureTime: item.captureTime || ''
    }))
  } catch (error) {
    console.error('Failed to load alarms:', error)
    alarmList.value = []
  } finally {
    alarmLoading.value = false
  }
}

// 获取设备列表并构建树
const fetchDeviceTree = async () => {
  try {
    const res: any = await getDevices({ page: 1, page_size: 100 })
    const devices = res.items || []
    // 构建设备树结构
    const grouped: Record<string, Record<string, any[]>> = {}
    devices.forEach((d: any) => {
      const org = d.org_name || d.org || '未知组织'
      const region = d.region_name || d.region || '未知区域'
      if (!grouped[org]) grouped[org] = {}
      if (!grouped[org][region]) grouped[org][region] = []
      grouped[org][region].push({
        id: `device-${d.id}`,
        name: d.name,
        type: 'camera' as const,
        online: d.status === 'active',
        ip: ''
      })
    })

    deviceTreeData.value = Object.entries(grouped).map(([orgName, regions]) => ({
      id: `org-${orgName}`,
      name: orgName,
      type: 'org' as const,
      online: true,
      children: Object.entries(regions).map(([regionName, cameras]) => ({
        id: `group-${regionName}`,
        name: regionName,
        type: 'group' as const,
        online: true,
        children: cameras
      }))
    }))
  } catch {
    console.error('获取设备列表失败')
  }
}

onMounted(() => {
  fetchDeviceTree()
  fetchAlarms()
})

const videoFileList = ref<VideoFile[]>([])

const fetchVideoFiles = async (deviceId: number) => {
  try {
    const res: any = await request.get('/file-records', { params: { device_id: deviceId, page: 1, page_size: 50 } })
    const items = res.items || []
    videoFileList.value = items.map((item: any) => ({
      id: item.id,
      fileName: item.file_name,
      startTime: item.created_at ? new Date(item.created_at).toLocaleString() : '-',
      duration: item.duration_seconds || 0
    }))
  } catch (error) {
    console.error('Failed to fetch video files:', error)
    videoFileList.value = []
  }
}

function handleDeviceClick(node: DeviceNode) {
  if (node.type === 'camera') {
    selectedDevice.value = node
    currentFile.value = null
    const rawId = node.id.replace('device-', '')
    const deviceId = parseInt(rawId, 10)
    if (!isNaN(deviceId)) {
      fetchVideoFiles(deviceId)
    }
  }
}

function handleFileClick(row: VideoFile) {
  currentFile.value = row
  playProgress.value = 0
  isPlaying.value = false
}

function togglePlay() {
  isPlaying.value = !isPlaying.value
}

function toggleFullscreen() {
  // Trigger fullscreen on video player
}

function formatDuration(seconds: number): string {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

function handleAlarmClick(alarm: any) {
  console.log('Alarm clicked:', alarm)
}
</script>

<style scoped>
.file-analysis-page {
  height: 100%;
  background: #020B1F;
  padding: 0;
}

.left-panel,
.right-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
}

.panel-header {
  padding: 10px 12px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.08) 0%, rgba(0, 229, 255, 0.03) 100%);
  border-radius: 8px;
  border: 1px solid rgba(0, 229, 255, 0.15);
}

.panel-title {
  font-family: 'Orbitron', 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 2px;
  text-transform: uppercase;
  background: linear-gradient(90deg, #00E5FF, #00FF88);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.filter-row {
  display: flex;
  gap: 8px;
  padding: 0 4px;
}

.filter-select {
  flex: 1;
}

.filter-select :deep(.el-input__wrapper) {
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.3);
  box-shadow: none;
  border-radius: 6px;
}

.filter-select :deep(.el-input__inner) {
  color: #001a2e;
}

.filter-select :deep(.el-input__wrapper:hover) {
  border-color: rgba(0, 229, 255, 0.5);
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.15);
}

.search-input {
  margin: 0 4px;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.3);
  box-shadow: none;
  border-radius: 6px;
}

.search-input :deep(.el-input__inner) {
  color: #001a2e;
}

.search-input :deep(.el-input__wrapper:focus-within) {
  border-color: #00E5FF;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.25);
}

.file-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: linear-gradient(145deg, rgba(0, 30, 60, 0.5) 0%, rgba(0, 15, 40, 0.7) 100%);
  border-radius: 8px;
  border: 1px solid rgba(0, 229, 255, 0.12);
}

.file-list-header {
  padding: 10px 12px;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #00E5FF;
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.1), transparent);
  border-bottom: 1px solid rgba(0, 229, 255, 0.15);
}

.file-list :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(0, 40, 80, 0.4);
  --el-table-row-hover-bg-color: rgba(0, 60, 100, 0.4);
  --el-table-border-color: rgba(0, 229, 255, 0.1);
  --el-table-text-color: rgba(255, 255, 255, 0.85);
  --el-table-header-text-color: #00E5FF;
  background: transparent;
  font-family: 'Rajdhani', sans-serif;
}

.file-list :deep(.el-table th.el-table__cell) {
  font-family: 'Orbitron', sans-serif;
  font-size: 10px;
  letter-spacing: 1px;
}

.file-list :deep(.el-table__body-wrapper) {
  background: transparent;
}

.middle-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 12px;
  gap: 12px;
}

.video-section {
  flex: 1;
  min-height: 0;
  background: linear-gradient(145deg, rgba(0, 0, 0, 0.8) 0%, rgba(0, 10, 30, 0.9) 100%);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(0, 229, 255, 0.2);
  box-shadow:
    0 4px 30px rgba(0, 0, 0, 0.5),
    inset 0 0 60px rgba(0, 229, 255, 0.02);
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 16px;
  color: rgba(0, 229, 255, 0.6);
  font-family: 'Orbitron', 'Rajdhani', sans-serif;
  font-size: 14px;
  letter-spacing: 2px;
  background:
    radial-gradient(ellipse at center, rgba(0, 229, 255, 0.05) 0%, transparent 70%);
}

.video-placeholder::before {
  content: '';
  width: 60px;
  height: 60px;
  border: 2px solid rgba(0, 229, 255, 0.3);
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.2), inset 0 0 20px rgba(0, 229, 255, 0.1);
  animation: glow-pulse 2s ease-in-out infinite;
}

.timeline-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(0, 40, 70, 0.5) 0%, rgba(0, 20, 40, 0.7) 100%);
  border-radius: 8px;
  border: 1px solid rgba(0, 229, 255, 0.15);
}

.time-label {
  font-size: 12px;
  color: #00E5FF;
  font-family: 'Share Tech Mono', 'Courier New', monospace;
  letter-spacing: 1px;
  white-space: nowrap;
  text-shadow: 0 0 8px rgba(0, 229, 255, 0.5);
}

.timeline-section :deep(.el-slider) {
  flex: 1;
}

.timeline-section :deep(.el-slider__runway) {
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 3px;
}

.timeline-section :deep(.el-slider__bar) {
  background: linear-gradient(90deg, #00E5FF, #00FF88);
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.timeline-section :deep(.el-slider__button) {
  border-color: #00E5FF;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.controls-section {
  display: flex;
  justify-content: center;
  padding: 8px 0;
  gap: 12px;
}

.controls-section :deep(.el-button-group .el-button) {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 229, 255, 0.05) 100%);
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: #00E5FF;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 1px;
}

.controls-section :deep(.el-button-group .el-button:hover) {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.25) 0%, rgba(0, 229, 255, 0.1) 100%);
  border-color: #00E5FF;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.3);
}

@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.3), inset 0 0 15px rgba(0, 229, 255, 0.1);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.5), inset 0 0 25px rgba(0, 229, 255, 0.2);
    transform: scale(1.05);
  }
}

.alarm-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px 0;
  color: rgba(0, 229, 255, 0.6);
  font-size: 13px;
}
</style>
