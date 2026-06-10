<template>
  <div class="monitor-single">
    <!-- 左侧：设备列表 -->
    <div class="left-panel">
      <div class="panel-header">
        <span class="panel-title">设备列表</span>
      </div>
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="请输入关键字进行过滤"
          size="small"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="device-tree-container">
        <DeviceTree
          :data="filteredDeviceTree"
          mode="radio"
          @node-click="handleDeviceClick"
        />
      </div>
    </div>

    <!-- 中间：视频区域 -->
    <div class="center-panel">
      <!-- 视频播放器 -->
      <div class="video-container">
        <template v-if="currentDevice && currentVideoUrl">
          <VideoPlayer
            v-if="currentStreamType === 'stream'"
            :url="currentVideoUrl"
            protocol="hls"
            :initial-osd-location="currentDevice?.name || ''"
          />
          <video
            v-else
            :src="currentVideoUrl"
            controls
            autoplay
            muted
            style="width: 100%; height: 100%; object-fit: contain;"
          />
        </template>
        <div v-else-if="streamLoading" class="video-placeholder">
          <el-icon class="spin" :size="32" color="rgba(232, 244, 255, 0.3)"><Loading /></el-icon>
          <span>正在连接视频流...</span>
        </div>
        <div v-else-if="streamError" class="video-placeholder">
          <span style="color: #FF006E;">无法连接视频流，请检查设备配置</span>
        </div>
        <div v-else class="video-placeholder">
          <span>请从左侧选择摄像头</span>
        </div>
      </div>
    </div>

    <!-- 右侧：报警动态 -->
    <div class="right-panel">
      <div class="panel-header">
        <span class="panel-title">报警动态</span>
      </div>
      <div class="alarm-filters">
        <el-select v-model="alarmTypeFilter" size="small" placeholder="全部">
          <el-option label="全部" value="all" />
          <el-option label="不合规" value="danger" />
        </el-select>
        <el-select v-model="alarmStatusFilter" size="small" placeholder="全部">
          <el-option label="全部" value="all" />
          <el-option label="合规" value="compliant" />
          <el-option label="不合规" value="non-compliant" />
        </el-select>
      </div>
      <div class="alarm-list-container">
        <div v-if="loadingAlarms" class="alarm-empty">
          <el-icon class="spin" :size="24" color="var(--text-secondary)"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        <div v-else-if="filteredAlarms.length === 0" class="alarm-empty">
          <span>暂无预警事件</span>
        </div>
        <div
          v-for="alarm in filteredAlarms"
          :key="alarm.id"
          class="alarm-card"
          @click="handleAlarmClick(alarm)"
        >
          <div class="alarm-thumbnail">
            <img v-if="alarm.imageUrl" :src="alarm.imageUrl" :alt="alarm.type" />
            <div v-else class="alarm-no-image">无图片</div>
            <div class="alarm-detection-box"></div>
            <div class="alarm-time">{{ alarm.time }}</div>
          </div>
          <div class="alarm-info">
            <div class="alarm-location">{{ alarm.deviceName }} {{ alarm.location ? '· ' + alarm.location : '' }}</div>
            <div class="alarm-tags">
              <span class="alarm-status" :class="alarm.isCompliant === true ? 'compliant' : alarm.isCompliant === false ? 'non-compliant' : 'unknown'">
                {{ alarm.isCompliant === true ? '合规' : alarm.isCompliant === false ? '不合规' : '未知' }}
              </span>
              <span class="alarm-process-status">{{ statusText(alarm.processStatus) }}</span>
            </div>
            <div class="alarm-type">{{ alarm.type }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 报警详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="报警动态详情"
      width="800px"
      :close-on-click-modal="false"
      class="alarm-detail-dialog"
    >
      <div class="detail-container">
        <div class="detail-image">
          <img v-if="selectedAlarm?.imageUrl" :src="selectedAlarm.imageUrl" alt="事件图片" />
          <div v-else class="detail-no-image">无图片</div>
        </div>
        <div class="detail-info">
          <div class="detail-row">
            <span class="detail-label">事件名称：</span>
            <span class="detail-value">{{ selectedAlarm?.type || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">事件类型：</span>
            <span class="detail-value">{{ selectedAlarm?.eventDetail || selectedAlarm?.type || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">报警位置：</span>
            <span class="detail-value">{{ selectedAlarm?.location || '-' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">处理状态：</span>
            <el-tag :type="statusTagType(selectedAlarm?.processStatus)" size="small">
              {{ statusText(selectedAlarm?.processStatus || '') }}
            </el-tag>
          </div>
          <div class="detail-row">
            <span class="detail-label">合规状态：</span>
            <span
              class="detail-value"
              :class="selectedAlarm?.isCompliant === true ? 'text-success' : selectedAlarm?.isCompliant === false ? 'text-danger' : 'text-secondary'"
            >
              {{ selectedAlarm?.isCompliant === true ? '合规' : selectedAlarm?.isCompliant === false ? '不合规' : '未知' }}
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">报警时间：</span>
            <span class="detail-value">{{ selectedAlarm?.time || '-' }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleVideoPlayback">视频回放</el-button>
      </template>
    </el-dialog>

    <!-- 视频回放弹窗 -->
    <el-dialog
      v-model="videoDialogVisible"
      title="视频回放"
      width="800px"
      :close-on-click-modal="false"
      class="video-playback-dialog"
    >
      <div class="video-playback-container">
        <video
          v-if="alarmVideoUrl"
          :src="alarmVideoUrl"
          controls
          autoplay
          style="width: 100%; max-height: 500px;"
        />
        <div v-else class="video-playback-empty">暂无视频</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import DeviceTree from '@/components/device-tree/DeviceTree.vue'
import { getDeviceGroupTree } from '@/api/device-groups'
import { getList as getWarningEvents } from '@/api/warning-events'
import type { DeviceNode } from '@/components/device-tree/useDeviceTree'

const searchQuery = ref('')
const currentDevice = ref<DeviceNode | null>(null)
const alarmTypeFilter = ref('all')
const alarmStatusFilter = ref('all')
const deviceTreeData = ref<DeviceNode[]>([])
const warningEvents = ref<any[]>([])
const loadingAlarms = ref(false)
const deviceStreamMap = ref<Record<string, string>>({})
const deviceStreamType = ref<Record<string, 'local' | 'stream'>>({})
const streamLoading = ref(false)
const streamError = ref(false)
let refreshTimer: ReturnType<typeof setInterval> | null = null
const detailDialogVisible = ref(false)
const selectedAlarm = ref<any>(null)
const videoDialogVisible = ref(false)

const alarmVideoUrl = computed(() => {
  return selectedAlarm.value?.videoUrl || ''
})

function handleVideoPlayback() {
  videoDialogVisible.value = true
}

// Convert /device-groups/tree response to DeviceNode format
const convertTreeData = (nodes: any[]): DeviceNode[] => {
  return nodes.map((node: any) => {
    const converted: DeviceNode = {
      id: String(node.id),
      name: node.name,
      type: node.level === 'device' ? 'device' : 'org',
      online: node.status === 'active' || node.status === 'online',
      children: node.children ? convertTreeData(node.children) : undefined,
      level: node.level,
    }
    return converted
  })
}

const currentVideoUrl = computed(() => {
  if (!currentDevice.value) return ''
  return deviceStreamMap.value[currentDevice.value.id] || ''
})

const currentStreamType = computed(() => {
  if (!currentDevice.value) return 'stream'
  return deviceStreamType.value[currentDevice.value.id] || 'stream'
})

const fetchWarningEvents = async () => {
  loadingAlarms.value = true
  try {
    const res: any = await getWarningEvents({ page: 1, page_size: 10, sort: '-created_at' })
    const items = res.items || []
    warningEvents.value = items.map((item: any) => ({
      id: item.id,
      time: item.time || '',
      type: item.eventType || item.eventDetail || '未知事件',
      eventDetail: item.eventDetail || '',
      deviceName: item.cameraName || '',
      location: item.location || '',
      processStatus: item.status || 'pending',
      imageUrl: item.imageUrl || '',
      videoUrl: item.videoUrl || '',
      isCompliant: item.isCompliant,
      level: item.level || 'low',
    }))
  } catch (error) {
    console.error('Failed to fetch warning events:', error)
    warningEvents.value = []
  } finally {
    loadingAlarms.value = false
  }
}

const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(() => {
    fetchWarningEvents()
  }, 30000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(async () => {
  try {
    const res = await getDeviceGroupTree() as any
    const tree = res || []
    deviceTreeData.value = convertTreeData(tree)
  } catch (error) {
    console.error('Failed to load device tree:', error)
    deviceTreeData.value = []
  }
  await fetchWarningEvents()
  startAutoRefresh()
})

watch(deviceTreeData, async (tree) => {
  if (tree.length > 0 && !currentDevice.value) {
    const firstDevice = findFirstDevice(tree)
    if (firstDevice) {
      currentDevice.value = firstDevice
      await switchDeviceStream(firstDevice)
    }
  }
}, { once: true })

onUnmounted(() => {
  stopAutoRefresh()
})

const filteredDeviceTree = computed(() => {
  if (!searchQuery.value) return deviceTreeData.value
  const query = searchQuery.value.toLowerCase()

  function filterNodes(nodes: any[]): any[] {
    return nodes.reduce((acc: any[], node) => {
      const matches = node.name?.toLowerCase().includes(query)
      const children = node.children ? filterNodes(node.children) : []
      if (matches || children.length > 0) {
        acc.push({
          ...node,
          children: children.length > 0 ? children : node.children
        })
      }
      return acc
    }, [])
  }

  return filterNodes(deviceTreeData.value)
})

const filteredAlarms = computed<any[]>(() => {
  let result = warningEvents.value
  if (alarmTypeFilter.value !== 'all') {
    result = result.filter((a) => (alarmTypeFilter.value === 'danger' ? !a.isCompliant : a.isCompliant))
  }
  if (alarmStatusFilter.value !== 'all') {
    result = result.filter((a) =>
      alarmStatusFilter.value === 'compliant'
        ? a.isCompliant === true
        : a.isCompliant === false
    )
  }
  return result
})

interface StreamInfo {
  url: string
  type: 'local' | 'stream'
}

async function getDeviceStreamInfo(deviceId: string): Promise<StreamInfo | null> {
  try {
    const res = await fetch(`/api/v1/stream/device/${deviceId}/flv`)
    if (!res.ok) return null
    const data = await res.json()
    const mappedType = data.source_type === 'http' || data.source_type === 'stream' ? 'stream' : 'local'
    return { url: data.flv_url, type: mappedType }
  } catch {
    return null
  }
}

async function switchDeviceStream(device: DeviceNode) {
  streamLoading.value = true
  streamError.value = false
  const info = await getDeviceStreamInfo(device.id)
  if (info) {
    deviceStreamMap.value = { ...deviceStreamMap.value, [device.id]: info.url }
    deviceStreamType.value = { ...deviceStreamType.value, [device.id]: info.type }
  } else {
    streamError.value = true
  }
  streamLoading.value = false
}

async function handleDeviceClick(node: DeviceNode) {
  if (node.type === 'device') {
    currentDevice.value = node
    if (!deviceStreamMap.value[node.id]) {
      await switchDeviceStream(node)
    }
  }
}

function findFirstDevice(nodes: DeviceNode[]): DeviceNode | null {
  for (const node of nodes) {
    if (node.type === 'device') return node
    if (node.children) {
      const found = findFirstDevice(node.children)
      if (found) return found
    }
  }
  return null
}

function handleAlarmClick(alarm: any) {
  selectedAlarm.value = alarm
  detailDialogVisible.value = true
}

function statusText(status: string) {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    resolved: '已解决',
    ignored: '已忽略',
  }
  return map[status] || status
}

function statusTagType(status: string): string {
  const map: Record<string, string> = {
    pending: 'warning',
    processing: 'primary',
    resolved: 'success',
    ignored: 'info',
  }
  return map[status] || ''
}
</script>

<style scoped>
.monitor-single {
  display: flex;
  flex: 1;
  min-height: 0;
  background: var(--bg-primary);
}

/* 左侧面板 */
.left-panel {
  width: 350px;
  min-width: 350px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.panel-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.search-box {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.device-tree-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

/* 中间面板 */
.center-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.video-container {
  flex: 1;
  position: relative;
  background: #000;
  overflow: hidden;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(232, 244, 255, 0.3);
  font-size: 16px;
}

/* 右侧面板 */
.right-panel {
  width: 300px;
  min-width: 300px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.alarm-filters {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.alarm-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.alarm-card {
  background: rgba(0, 30, 60, 0.6);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  margin-bottom: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
}

.alarm-card:hover {
  border-color: var(--primary-color);
}

.alarm-thumbnail {
  position: relative;
  height: 100px;
  overflow: hidden;
}

.alarm-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.alarm-detection-box {
  position: absolute;
  top: 20%;
  left: 20%;
  width: 60%;
  height: 50%;
  border: 2px solid #FF006E;
  border-radius: 2px;
  pointer-events: none;
}

.alarm-time {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(0, 0, 0, 0.5);
  padding: 2px 6px;
  border-radius: 2px;
}

.alarm-info {
  padding: 10px;
}

.alarm-location {
  font-size: 12px;
  color: var(--text-primary);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alarm-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 4px;
}

.alarm-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
}

.alarm-status.compliant {
  background: rgba(54, 214, 138, 0.2);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success);
}

.alarm-status.non-compliant {
  background: rgba(255, 77, 106, 0.2);
  color: var(--el-color-danger);
  border: 1px solid var(--el-color-danger);
}

.alarm-status.unknown {
  background: rgba(128, 128, 128, 0.2);
  color: var(--text-secondary);
  border: 1px solid var(--text-secondary);
}

.alarm-type {
  font-size: 11px;
  color: var(--text-secondary);
}

.alarm-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: var(--text-secondary);
  font-size: 13px;
  gap: 8px;
}

.alarm-no-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 20, 40, 0.6);
  color: var(--text-secondary);
  font-size: 12px;
}

.alarm-process-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
  background: rgba(0, 100, 180, 0.2);
  color: var(--primary-color);
  border: 1px solid var(--primary-color);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 报警详情弹窗 */
:deep(.alarm-detail-dialog .el-dialog__header) {
  margin-right: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

:deep(.alarm-detail-dialog .el-dialog__title) {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
}

:deep(.alarm-detail-dialog .el-dialog__body) {
  padding: 20px;
}

.detail-container {
  display: flex;
  gap: 20px;
}

.detail-image {
  flex: 1;
  min-width: 0;
  height: 320px;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.detail-no-image {
  color: var(--text-secondary);
  font-size: 14px;
}

.detail-info {
  width: 280px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-label {
  color: var(--text-secondary);
  font-size: 13px;
  white-space: nowrap;
}

.detail-value {
  color: var(--text-primary);
  font-size: 13px;
  word-break: break-all;
}

.text-success {
  color: var(--el-color-success);
}

.text-danger {
  color: var(--el-color-danger);
}

.text-secondary {
  color: var(--text-secondary);
}

/* 视频回放弹窗 */
:deep(.video-playback-dialog .el-dialog__header) {
  margin-right: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

:deep(.video-playback-dialog .el-dialog__title) {
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
}

:deep(.video-playback-dialog .el-dialog__body) {
  padding: 0;
  background: #000;
}

.video-playback-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}

.video-playback-empty {
  padding: 40px;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
