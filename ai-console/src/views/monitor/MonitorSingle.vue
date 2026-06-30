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
          @node-hover="handleNodeHover"
        />
      </div>
    </div>

    <!-- 中间：视频区域 -->
    <div class="center-panel">
      <!-- 视频播放器 -->
      <div class="video-container">
        <div
          v-for="device in streamPoolStore.hlsDevices"
          :key="device.id"
          class="video-wrapper pool-instance"
          :class="{ active: streamPoolStore.visibleDeviceId === device.id }"
        >
          <VideoPlayer
            :ref="(el: any) => setPlayerRef(device.id, el)"
            :url="device.url"
            protocol="hls"
            :auto-start="false"
            :show-overlays="streamPoolStore.visibleDeviceId === device.id"
            :initial-osd-location="device.name"
            :device-id="device.id"
            @canplay="handleVideoCanplay"
          />
        </div>
        <video
          v-show="isNativeVideoVisible && !nativeVideoError"
          ref="nativeVideoRef"
          :src="currentVideoUrl"
          controls
          autoplay
          muted
          @canplay="nativeVideoError = false; handleVideoCanplay()"
          @error="nativeVideoError = true"
          style="width: 100%; height: 100%; object-fit: contain;"
        />

        <div
          v-show="isNativeVideoVisible && nativeVideoError"
          class="video-placeholder"
        >
          <span style="color: #FF006E;">视频文件不存在或暂不可用</span>
        </div>

        <div
          v-show="isFallbackVideoVisible"
          class="video-wrapper"
          style="width: 100%; height: 100%;"
        >
          <VideoPlayer
            ref="fallbackVideoPlayerRef"
            :url="currentVideoUrl"
            protocol="hls"
            :initial-osd-location="currentDevice?.name || ''"
            @canplay="handleVideoCanplay"
          />
        </div>

        <div v-show="!hasVisibleVideo" class="video-placeholder">
          <template v-if="streamLoading">
            <el-icon class="spin" :size="32" color="rgba(232, 244, 255, 0.3)"><Loading /></el-icon>
            <span>正在连接视频流...</span>
          </template>
          <template v-else-if="streamError">
            <span style="color: #FF006E;">无法连接视频流，请检查设备配置</span>
          </template>
          <template v-else>
            <span>请从左侧选择摄像头</span>
          </template>
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
            <img
              v-if="alarm.imageUrl"
              :src="alarm.imageUrl"
              :alt="alarm.type"
              @error="handleImageError"
            />
            <div class="alarm-no-image" :style="{ display: alarm.imageUrl ? 'none' : 'flex' }">无图片</div>
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
          <img
            v-if="selectedAlarm?.imageUrl"
            :src="selectedAlarm.imageUrl"
            alt="事件图片"
            @error="handleImageError"
          />
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
          v-if="alarmVideoUrl && !alarmVideoError"
          :src="alarmVideoUrl"
          controls
          autoplay
          style="width: 100%; max-height: 500px;"
          @error="handleAlarmVideoError"
        />
        <div v-else class="video-playback-empty">暂无视频</div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Search, Loading } from '@element-plus/icons-vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import DeviceTree from '@/components/device-tree/DeviceTree.vue'
import { useStreamPoolStore, type PoolDevice } from '@/stores/streamPool'
import { getDeviceGroupTree } from '@/api/device-groups'
import { getList as getWarningEvents } from '@/api/warning-events'
import { registerDevicesAsync, getRegisterDevicesStatus } from '@/api/stream'
import { getEventTypeDisplayName } from '@/utils/eventType'
import type { DeviceNode } from '@/components/device-tree/useDeviceTree'
import type { ComponentPublicInstance } from 'vue'

const streamPoolStore = useStreamPoolStore()

const searchQuery = ref('')
const currentDevice = ref<DeviceNode | null>(null)
const alarmTypeFilter = ref('all')
const alarmStatusFilter = ref('all')
const deviceTreeData = ref<DeviceNode[]>([])
const warningEvents = ref<any[]>([])
const loadingAlarms = ref(false)
const streamLoading = ref(false)
const streamError = ref(false)
const nativeVideoError = ref(false)
const nativeVideoRef = ref<HTMLVideoElement | null>(null)
const fallbackVideoPlayerRef = ref<ComponentPublicInstance<any> | null>(null)
const playerRefs = ref<Map<string, ComponentPublicInstance>>(new Map())
let refreshTimer: ReturnType<typeof setInterval> | null = null
let streamRegisterPollTimer: ReturnType<typeof setInterval> | null = null

// 设备流元数据缓存（包含所有设备，用于原生视频播放）
const deviceStreamMap = ref<Record<string, CachedStreamInfo>>({})

// 延迟测量
const switchStartTime = ref<number>(0)
const switchDeviceId = ref<string>('')
const hasMeasuredLatency = ref(false)

function handleVideoCanplay() {
  if (hasMeasuredLatency.value || !switchStartTime.value) return
  hasMeasuredLatency.value = true
  const latency = performance.now() - switchStartTime.value
  console.log(`[HotConnection] Device ${switchDeviceId.value} switch latency: ${Math.round(latency)}ms`)
}
const detailDialogVisible = ref(false)
const selectedAlarm = ref<any>(null)
const videoDialogVisible = ref(false)
const alarmVideoError = ref(false)

const handleAlarmVideoError = () => {
  alarmVideoError.value = true
}

interface CachedStreamInfo {
  url: string
  type: 'local' | 'stream'
  sourceType: string
  rtspUrl?: string
  streamName?: string
  cachedAt: number
}

function setPlayerRef(deviceId: string, el: any) {
  if (el) {
    playerRefs.value.set(deviceId, el as ComponentPublicInstance)
  }
}

function isDirectVideoUrl(url: string): boolean {
  return /\.(mp4|webm|ogg|mov)(\?.*)?$/i.test(url)
}

function mapStreamType(sourceType: string, url: string): 'stream' | 'local' {
  // 'local' means "use native <video> player"
  // 'stream' means "use hls.js/flv.js player"
  if (sourceType === 'local') return 'local'
  if (isDirectVideoUrl(url)) return 'local'
  return 'stream'
}

function flattenDevices(nodes: DeviceNode[]): DeviceNode[] {
  const result: DeviceNode[] = []
  for (const node of nodes) {
    if (node.type === 'device') {
      result.push(node)
    }
    if (node.children) {
      result.push(...flattenDevices(node.children))
    }
  }
  return result
}

const alarmVideoUrl = computed(() => {
  return selectedAlarm.value?.videoUrl || ''
})

function handleVideoPlayback() {
  alarmVideoError.value = false
  videoDialogVisible.value = true
}

// Convert /device-groups/tree response to DeviceNode format
const convertTreeData = (nodes: any[]): DeviceNode[] => {
  return nodes.map((node: any) => {
    const isDevice = node.level === 'device' || node.device_code !== undefined
    const converted: DeviceNode = {
      id: String(node.id),
      name: node.name,
      type: isDevice ? 'device' : 'org',
      online: node.status === 'active' || node.status === 'online',
      children: node.children ? convertTreeData(node.children) : undefined,
      level: node.level,
      deviceCode: node.device_code,
    }
    return converted
  })
}

const currentVideoUrl = computed(() => {
  if (!currentDevice.value) return ''
  return deviceStreamMap.value[currentDevice.value.id]?.url || ''
})

const currentStreamType = computed(() => {
  if (!currentDevice.value) return 'stream'
  return deviceStreamMap.value[currentDevice.value.id]?.type || 'stream'
})

const isPoolVideoVisible = computed(() => !!streamPoolStore.visibleDeviceId)

const isNativeVideoVisible = computed(() => {
  return !!currentDevice.value && !!currentVideoUrl.value && currentStreamType.value !== 'stream'
})

const isFallbackVideoVisible = computed(() => {
  return !streamPoolStore.enableHotPool && !!currentDevice.value && !!currentVideoUrl.value && currentStreamType.value === 'stream' && !isDirectVideoUrl(currentVideoUrl.value)
})

const hasVisibleVideo = computed(() => isPoolVideoVisible.value || isNativeVideoVisible.value || isFallbackVideoVisible.value)

const fetchWarningEvents = async () => {
  loadingAlarms.value = true
  try {
    const res: any = await getWarningEvents({ page: 1, page_size: 10, sort: '-created_at' })
    const items = res.items || []
    warningEvents.value = items.map((item: any) => ({
      id: item.id,
      time: item.time || '',
      type: item.eventType ? getEventTypeDisplayName(item.eventType) : (item.eventDetail || '未知事件'),
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

  const tree = deviceTreeData.value
  const allDevices = flattenDevices(tree)
  if (allDevices.length === 0) return

  if (streamPoolStore.enableHotPool) {
    await initStreamPool(allDevices)
  } else if (!currentDevice.value) {
    const firstDevice = allDevices[0]
    currentDevice.value = firstDevice
    await switchDeviceStream(firstDevice)
  }
})

async function initStreamPool(allDevices: DeviceNode[]) {
  if (allDevices.length === 0) return

  // 复用现有热池（30s 内返回）
  if (streamPoolStore.hlsDevices.length > 0) {
    streamPoolStore.cancelRelease()
    startPoolPlayers()
    if (!currentDevice.value) {
      const firstDevice = allDevices.find(d => streamPoolStore.hlsDevices.some(pd => pd.id === d.id)) || allDevices[0]
      currentDevice.value = firstDevice
      if (streamPoolStore.hlsDevices.some(d => d.id === firstDevice.id)) {
        streamPoolStore.setVisible(firstDevice.id)
      }
    }
    return
  }

  // 批量获取所有设备流地址（异步任务 + 轮询）
  try {
    const { task_id }: any = await registerDevicesAsync(allDevices.map(d => d.id))
    if (!task_id) {
      console.error('Failed to register device streams: no task_id')
      return
    }

    startStreamRegisterPoll(task_id, (status: any) => {
      const results = status.results || []
      const newMap: Record<string, CachedStreamInfo> = {}
      const poolDevices: PoolDevice[] = []

      results.forEach((item: any) => {
        const deviceId = String(item.device_id)
        const device = allDevices.find(d => d.id === deviceId)
        if (!item.success) {
          console.warn(`[StreamPool] Device ${deviceId} registration failed:`, item.error)
          return
        }

        const info: CachedStreamInfo = {
          url: item.flv_url,
          type: mapStreamType(item.source_type, item.flv_url),
          sourceType: item.source_type,
          rtspUrl: item.rtsp_url,
          streamName: item.stream_name,
          cachedAt: Date.now(),
        }
        newMap[deviceId] = info

        poolDevices.push({
          id: deviceId,
          name: device?.name || deviceId,
          url: item.flv_url,
          sourceType: item.source_type,
          streamName: item.stream_name,
        })
      })

      deviceStreamMap.value = newMap
      streamPoolStore.initPool(poolDevices)

      // 延迟启动后台实例，避免并发 burst
      startPoolPlayers()

      // 默认选中第一个设备
      const firstDevice = allDevices[0]
      if (firstDevice) {
        currentDevice.value = firstDevice
        if (streamPoolStore.hlsDevices.some(d => d.id === firstDevice.id)) {
          streamPoolStore.setVisible(firstDevice.id)
        }
      }
    })
  } catch (error) {
    console.error('Failed to init stream pool:', error)
  }
}

const clearStreamRegisterPoll = () => {
  if (streamRegisterPollTimer) {
    clearInterval(streamRegisterPollTimer)
    streamRegisterPollTimer = null
  }
}

const startStreamRegisterPoll = (taskId: string, onCompleted: (status: any) => void) => {
  clearStreamRegisterPoll()
  streamRegisterPollTimer = window.setInterval(async () => {
    try {
      const status: any = await getRegisterDevicesStatus(taskId)
      if (status.status === 'completed' || status.status === 'failed') {
        clearStreamRegisterPoll()
        if (status.status === 'completed') {
          onCompleted(status)
        } else {
          console.error('Stream registration task failed:', status.error || status.errors)
        }
      }
    } catch (pollError: any) {
      clearStreamRegisterPoll()
      console.error('Stream register poll failed:', pollError)
    }
  }, 2000)
}

function startPoolPlayers() {
  streamPoolStore.hlsDevices.forEach((device, index) => {
    setTimeout(() => {
      const player = playerRefs.value.get(device.id)
      if (player && typeof (player as any).start === 'function') {
        ;(player as any).start()
      }
    }, index * 200)
  })
}

onUnmounted(() => {
  stopAutoRefresh()
  clearStreamRegisterPoll()
  streamPoolStore.scheduleRelease(30000)
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

async function handleDeviceClick(node: DeviceNode) {
  if (node.type !== 'device') return

  streamError.value = false
  nativeVideoError.value = false
  hasMeasuredLatency.value = false

  if (streamPoolStore.enableHotPool) {
    await handleHotPoolClick(node)
  } else {
    await handleFallbackClick(node)
  }
}

async function handleHotPoolClick(node: DeviceNode) {
  const isPoolDevice = streamPoolStore.hlsDevices.some(d => d.id === node.id)

  if (isPoolDevice) {
    const prevId = streamPoolStore.visibleDeviceId
    if (prevId && prevId !== node.id) {
      const prevPlayer = playerRefs.value.get(prevId)
      if (prevPlayer && typeof (prevPlayer as any).stopBackgroundActivity === 'function') {
        ;(prevPlayer as any).stopBackgroundActivity()
      }
    }

    if (fallbackVideoPlayerRef.value) {
      const player = fallbackVideoPlayerRef.value as any
      if (typeof player.pauseBuffering === 'function') {
        player.pauseBuffering()
      }
    }
    if (nativeVideoRef.value) {
      nativeVideoRef.value.pause()
    }

    switchStartTime.value = performance.now()
    switchDeviceId.value = node.id
    hasMeasuredLatency.value = false

    currentDevice.value = node
    streamPoolStore.setVisible(node.id)

    const player = playerRefs.value.get(node.id)
    if (player && typeof (player as any).resumeBackgroundActivity === 'function') {
      ;(player as any).resumeBackgroundActivity()
    }
  } else {
    // 暂停当前热池实例
    const prevId = streamPoolStore.visibleDeviceId
    if (prevId) {
      const prevPlayer = playerRefs.value.get(prevId)
      if (prevPlayer && typeof (prevPlayer as any).stopBackgroundActivity === 'function') {
        ;(prevPlayer as any).stopBackgroundActivity()
      }
      streamPoolStore.setVisible(null)
    }

    if (nativeVideoRef.value) {
      nativeVideoRef.value.pause()
    }

    switchStartTime.value = performance.now()
    switchDeviceId.value = node.id
    hasMeasuredLatency.value = false

    currentDevice.value = node
    const info = deviceStreamMap.value[node.id]
    if (!info) {
      streamError.value = true
    }
  }
}

async function handleFallbackClick(node: DeviceNode) {
  streamLoading.value = true

  if (fallbackVideoPlayerRef.value) {
    const player = fallbackVideoPlayerRef.value as any
    if (typeof player.pauseBuffering === 'function') {
      player.pauseBuffering()
    }
  }
  if (nativeVideoRef.value) {
    nativeVideoRef.value.pause()
  }

  switchStartTime.value = performance.now()
  switchDeviceId.value = node.id
  hasMeasuredLatency.value = false

  currentDevice.value = node
  const info = await getDeviceStreamInfo(node.id)
  if (!info) {
    streamError.value = true
  }
  streamLoading.value = false
}

async function getDeviceStreamInfo(deviceId: string): Promise<CachedStreamInfo | null> {
  const cached = deviceStreamMap.value[deviceId]
  if (cached) {
    return cached
  }

  try {
    const res = await fetch(`/api/v1/stream/device/${deviceId}/flv`)
    if (!res.ok) return null
    const data = await res.json()
    const info: CachedStreamInfo = {
      url: data.flv_url,
      type: mapStreamType(data.source_type, data.flv_url),
      sourceType: data.source_type || '',
      rtspUrl: data.rtsp_url,
      streamName: data.stream_name,
      cachedAt: Date.now(),
    }
    deviceStreamMap.value = { ...deviceStreamMap.value, [deviceId]: info }
    return info
  } catch {
    return null
  }
}

async function switchDeviceStream(device: DeviceNode) {
  streamLoading.value = true
  streamError.value = false
  const info = await getDeviceStreamInfo(device.id)
  if (!info) {
    streamError.value = true
  }
  streamLoading.value = false
}

function handleNodeHover(_node: DeviceNode) {
  // 全热连接模式下，hover 预加载已被页面级热池取代
}

function handleAlarmClick(alarm: any) {
  selectedAlarm.value = alarm
  alarmVideoError.value = false
  detailDialogVisible.value = true
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
  const placeholder = img.nextElementSibling as HTMLElement | null
  if (placeholder) placeholder.style.display = 'flex'
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

.video-wrapper {
  width: 100%;
  height: 100%;
}

.video-wrapper.pool-instance {
  position: absolute;
  top: 0;
  left: 0;
  z-index: 1;
}

.video-wrapper.pool-instance.active {
  z-index: 10;
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
