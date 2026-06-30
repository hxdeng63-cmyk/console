<template>
  <div class="monitor-wall">
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧视频区域 -->
      <div class="video-area">
        <div class="video-wrapper">
          <!-- 视频播放器 -->
          <div class="video-container">
            <template v-if="currentDevice">
              <MonitoringVideoPlayer
                v-if="isNativeVideo"
                :src="currentVideoUrl"
              />
              <VideoPlayer
                v-else-if="currentVideoUrl"
                :url="currentVideoUrl"
                :protocol="currentProtocol"
                :initial-osd-location="currentDevice.name"
              />
              <div v-else-if="streamLoading" class="video-placeholder">
                <span>正在连接视频流...</span>
              </div>
              <div v-else class="video-placeholder">
                <span style="color: #FF006E;">无法连接视频流，请检查设备配置</span>
              </div>
            </template>
            <div v-else class="video-placeholder">
              <span>等待选择设备...</span>
            </div>

            <!-- 视频装饰角 -->
            <div class="video-corner top-left"></div>
            <div class="video-corner top-right"></div>
            <div class="video-corner bottom-left"></div>
            <div class="video-corner bottom-right"></div>
          </div>

          <!-- 视频底部装饰 -->
          <div class="video-footer">
            <div class="footer-line"></div>
          </div>
        </div>
      </div>

      <!-- 右侧数据面板 -->
      <div class="right-panel">
        <!-- 预览通道 -->
        <div class="panel-section channel-section">
          <div class="section-header">
            <span class="section-title">预览通道</span>
          </div>
          <div class="channel-content">
            <el-select v-model="selectedChannel" placeholder="选择通道" class="channel-select">
              <el-option
                v-for="ch in channels"
                :key="ch.id"
                :label="ch.name"
                :value="ch.id"
              />
            </el-select>
            <el-select
              v-model="selectedAlgorithm"
              placeholder="选择识别算法"
              class="channel-select"
              @change="handleAlgorithmChange"
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
              class="restart-btn"
              type="warning"
              :loading="restarting"
              @click="handleRestartAll"
            >
              <el-icon><Refresh /></el-icon>
              重新监测
            </el-button>
          </div>
        </div>

        <!-- 实时交通参数 -->
        <div v-loading="dashboardLoading" class="panel-section traffic-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">实时交通参数</span>
            <span class="header-line"></span>
          </div>
          <div class="traffic-grid">
            <div class="traffic-item">
              <div class="traffic-value primary">{{ statsData.avgSpeed }}</div>
              <div class="traffic-label">平均速度 (km/h)</div>
            </div>
            <div class="traffic-item">
              <div class="traffic-value">{{ statsData.upTraffic }}</div>
              <div class="traffic-label">上行车流量</div>
            </div>
            <div class="traffic-item">
              <div class="traffic-value">{{ statsData.downTraffic }}</div>
              <div class="traffic-label">下行车流量</div>
            </div>
          </div>
        </div>

        <!-- 交通事件统计 -->
        <div v-loading="dashboardLoading" class="panel-section events-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">交通事件统计</span>
            <span class="header-line"></span>
          </div>
          <div class="donut-chart-area">
            <div class="donut-chart">
              <div class="donut-circle" :style="donutStyle"></div>
              <div class="donut-center">
                <span class="donut-total">{{ eventStats.total }}</span>
                <span class="donut-label">交通事件</span>
              </div>
            </div>
            <div class="donut-legend">
              <div class="legend-item" v-for="item in eventStats.legend" :key="item.name">
                <span class="legend-dot" :style="{ background: item.color }"></span>
                <span class="legend-name">{{ item.name }}</span>
                <span class="legend-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 等级指标 -->
        <div class="panel-section level-section">
          <div class="level-item">
            <div class="level-header">
              <span class="level-label">道理通行等级</span>
            </div>
            <div class="level-bar">
              <div class="level-gradient"></div>
              <div class="level-marker" :style="{ left: roadLevelPosition }"></div>
            </div>
            <div class="level-scale">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
            <div class="level-status" :class="'level-' + statsData.roadLevel">{{ statsData.roadLevelText }}</div>
          </div>
          <div class="level-item">
            <div class="level-header">
              <span class="level-label">能见度等级</span>
            </div>
            <div class="level-bar">
              <div class="level-gradient visibility"></div>
              <div class="level-marker" :style="{ left: visibilityPosition }"></div>
            </div>
            <div class="level-scale">
              <span>0</span>
              <span>2</span>
              <span>4</span>
              <span>6</span>
              <span>8</span>
              <span>10</span>
            </div>
          </div>
        </div>

        <!-- 布控信息 -->
        <div v-loading="dashboardLoading" class="panel-section deployment-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">布控信息</span>
            <span class="header-line"></span>
          </div>
          <el-table :data="deploymentData" size="small" class="deployment-table" border>
            <el-table-column prop="name" label="布控方案名称" min-width="130" show-overflow-tooltip />
            <el-table-column prop="algorithm" label="算法名称" width="95" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="70" align="center">
              <template #default="{ row }">
                <span class="status-tag" :class="row.statusClass">{{ row.status }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 视频质量检测 -->
        <div class="panel-section quality-section">
          <span class="quality-label">视频质量检测</span>
          <span class="status-tag online">在线</span>
        </div>
      </div>
    </div>

    <!-- 底部实时事件抓拍 -->
    <div class="bottom-events">
      <div class="events-header">
        <span class="events-title">实时事件抓拍</span>
      </div>
      <div class="events-carousel">
        <div
          v-for="event in filteredEvents"
          :key="event.id"
          class="event-card"
        >
          <div class="event-thumb">
            <img :src="event.imageUrl" :alt="event.type" @error="handleImageError" />
            <div class="event-no-image" :style="{ display: event.imageUrl ? 'none' : 'flex' }">无图片</div>
          </div>
          <div class="event-label">
            <span class="event-type">{{ event.type }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部信息栏 -->
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
      <el-radio-group v-model="eventFilter" size="small">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="danger">不合规</el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { Edit, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import MonitoringVideoPlayer from '@/components/monitor/MonitoringVideoPlayer.vue'
import { getDevices } from '@/api/devices'
import { getList as getWarningEvents } from '@/api/warning-events'
import { getSceneStats } from '@/api/event-stats'
import { deploymentApi } from '@/api/deployment'
import { registerDevicesAsync, getRegisterDevicesStatus } from '@/api/stream'
import { getEventTypeDisplayName } from '@/utils/eventType'
import type { DeviceNode } from '@/components/device-tree/useDeviceTree'

const selectedChannel = ref('')
const selectedAlgorithm = ref('')
const eventFilter = ref('all')

interface StreamInfo {
  url: string
  sourceType: string
}

interface AlgorithmOption {
  id: number
  name: string
  events: {
    name: string
    description?: string
    moduleName?: string
  }[]
}

const streamMap = ref<Record<string, StreamInfo>>({})
const streamLoading = ref(false)
const streamError = ref(false)
const streamRegistering = ref(false)
const streamRegisterPollTimer = ref<number | null>(null)

const dashboardLoading = ref(false)
const algorithms = ref<AlgorithmOption[]>([])
const deploymentData = ref<any[]>([])
const alarmList = ref<any[]>([])

const eventPollTimer = ref<number | null>(null)
const dashboardRefreshTimer = ref<number | null>(null)
const startStatusTimer = ref<number | null>(null)

const deploymentInfo = computed(() => {
  const totalDevices = deviceTreeData.value.reduce((sum, org) => {
    return sum + (org.children?.reduce((s, group) => s + (group.children?.length || 0), 0) || 0)
  }, 0)
  const firstOrg = deviceTreeData.value[0]
  return firstOrg ? `${firstOrg.name}(${totalDevices}路)` : '暂无设备'
})

const deviceTreeData = ref<DeviceNode[]>([])

const fetchDeviceTree = async () => {
  try {
    const res: any = await getDevices({ page: 1, page_size: 100 })
    const devices = res.items || []
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

const parseRawChannelId = (channelId: string): number => {
  if (!channelId) return 0
  const raw = channelId.replace(/^device-/, '')
  const num = Number(raw)
  return Number.isNaN(num) ? 0 : num
}

const fetchAlgorithms = async () => {
  try {
    const res: any = await deploymentApi.listAlgorithms({ page: 1, page_size: 100 })
    algorithms.value = (res.items || []).map((a: any) => ({
      id: a.id,
      name: a.name,
      events: (a.events || []).map((e: any) => ({
        name: e.name,
        description: e.description,
        moduleName: e.module_name,
      })),
    }))
  } catch {
    ElMessage.error('加载算法列表失败')
  }
}

const handleAlgorithmChange = async (value: string) => {
  if (!value || !selectedChannel.value) return
  const parts = value.split(':')
  if (parts.length < 3 || !parts[1]) {
    ElMessage.warning('该算法模块不可运行')
    return
  }
  const [algorithmIdStr, moduleName, eventName] = parts
  const algorithmId = Number(algorithmIdStr)
  const rawId = parseRawChannelId(selectedChannel.value)
  if (!rawId || !algorithmId || !moduleName || !eventName) return

  try {
    const existing: any = await deploymentApi.list({
      device_id: rawId,
      module_name: moduleName,
      page: 1,
      page_size: 1,
    })
    const item = existing.items?.[0]

    let deploymentId: number
    if (item) {
      deploymentId = item.id
      if (item.algorithm_status === 'running') {
        ElMessage.info('该算法已在运行')
        return
      }
    } else {
      const created: any = await deploymentApi.create({
        name: `${moduleName}_${rawId}`,
        algorithm_id: algorithmId,
        device_ids: [rawId],
        module_name: moduleName,
        status: 'active',
        algorithm_status: 'stopped',
      })
      deploymentId = created.id
    }

    const startRes: any = await deploymentApi.start(deploymentId, {
      module_name: moduleName,
      video_path: 'auto',
    })
    pollStartStatus(deploymentId, startRes.task_id, moduleName)
    ElMessage.success('识别任务已启动')
  } catch (error: any) {
    ElMessage.error('启动识别失败：' + (error?.message || '未知错误'))
  }
}

const pollStartStatus = (
  deploymentId: number,
  taskId: string,
  moduleName: string,
  maxAttempts = 30,
) => {
  if (startStatusTimer.value) {
    window.clearInterval(startStatusTimer.value)
    startStatusTimer.value = null
  }
  let attempts = 0
  startStatusTimer.value = window.setInterval(async () => {
    attempts += 1
    try {
      const res: any = await deploymentApi.startStatus(deploymentId, taskId)
      if (res.status === 'success') {
        clearStartStatusTimer()
        ElMessage.success(`${moduleName} 识别已就绪`)
        const rawId = parseRawChannelId(selectedChannel.value)
        if (rawId) {
          fetchDashboardData(rawId)
          fetchAlarms(rawId)
        }
        return
      }
      if (res.status === 'failed') {
        clearStartStatusTimer()
        ElMessage.error(`${moduleName} 启动失败：${res.error || '未知错误'}`)
        return
      }
      if (attempts >= maxAttempts) {
        clearStartStatusTimer()
        ElMessage.warning(`${moduleName} 启动状态获取超时`)
      }
    } catch {
      // 继续轮询直到超时
    }
  }, 2000)
}

const clearStartStatusTimer = () => {
  if (startStatusTimer.value) {
    window.clearInterval(startStatusTimer.value)
    startStatusTimer.value = null
  }
}

const clearEventPollTimer = () => {
  if (eventPollTimer.value) {
    window.clearInterval(eventPollTimer.value)
    eventPollTimer.value = null
  }
}

const clearDashboardRefreshTimer = () => {
  if (dashboardRefreshTimer.value) {
    window.clearInterval(dashboardRefreshTimer.value)
    dashboardRefreshTimer.value = null
  }
}

const restartEventPolling = (rawId: number) => {
  clearEventPollTimer()
  if (!rawId) return
  fetchAlarms(rawId)
  eventPollTimer.value = window.setInterval(() => fetchAlarms(rawId), 3000)
}

const restartDashboardPolling = (rawId: number) => {
  clearDashboardRefreshTimer()
  if (!rawId) return
  fetchDashboardData(rawId)
  dashboardRefreshTimer.value = window.setInterval(() => fetchDashboardData(rawId), 5000)
}

const fetchDashboardData = async (rawId: number) => {
  if (!rawId) return
  dashboardLoading.value = true
  try {
    await Promise.all([
      fetchStatsData(rawId),
      fetchEventStats(rawId),
      fetchDeploymentData(rawId),
    ])
  } finally {
    dashboardLoading.value = false
  }
}

const fetchStatsData = async (rawId: number) => {
  if (!rawId) return
  let upTraffic = '--'
  let downTraffic = '--'
  let roadLevel = 1
  let roadLevelText = '畅通'

  try {
    const flowRes: any = await getWarningEvents({
      device_id: rawId,
      event_type: 'flow',
      page: 1,
      page_size: 1,
    })
    const flowItem = (flowRes.items || [])[0]
    if (flowItem?.eventDetail) {
      try {
        const flow = JSON.parse(flowItem.eventDetail)
        if (flow.up_count !== undefined) upTraffic = String(flow.up_count)
        if (flow.down_count !== undefined) downTraffic = String(flow.down_count)
      } catch {
        // 解析失败时保持默认值
      }
    }

    const jamRes: any = await getWarningEvents({
      device_id: rawId,
      event_type: 'jam',
      page: 1,
      page_size: 1,
    })
    const jamItem = (jamRes.items || [])[0]
    if (jamItem?.eventDetail) {
      try {
        const jam = JSON.parse(jamItem.eventDetail)
        if (jam.is_jam === true) {
          roadLevel = 4
          roadLevelText = '拥堵'
        } else if (jam.confidence > 0.5) {
          roadLevel = 3
          roadLevelText = '缓慢'
        }
      } catch {
        // 解析失败时保持默认值
      }
    }
  } catch {
    // 已在 api 层提示
  }

  statsData.value = {
    avgSpeed: '--',
    upTraffic,
    downTraffic,
    roadLevel,
    roadLevelText,
  }
}

const LEGEND_COLORS = ['#00FFCC', '#0099FF', '#00EAFF', '#FF9900']

const fetchEventStats = async (rawId: number) => {
  if (!rawId) return
  try {
    const today = new Date().toISOString().split('T')[0]
    const res: any = await getSceneStats({ device_id: rawId, start_date: today })
    const categories = res.categories || []
    const values = res.values || []
    const legend = categories.map((name: string, index: number) => ({
      name: getEventTypeDisplayName(name),
      value: values[index] || 0,
      color: LEGEND_COLORS[index % LEGEND_COLORS.length],
    }))
    eventStats.value = {
      total: values.reduce((sum: number, v: number) => sum + (v || 0), 0),
      legend,
    }
  } catch {
    eventStats.value = { total: 0, legend: [] }
  }
}

const fetchDeploymentData = async (rawId: number) => {
  if (!rawId) return
  try {
    const res: any = await deploymentApi.list({ device_id: rawId, page: 1, page_size: 100 })
    const items = res.items || []
    deploymentData.value = items.map((item: any) => {
      const status = item.algorithm_status || item.status || 'stopped'
      const statusMap: Record<string, { text: string; cls: string }> = {
        running: { text: '运行中', cls: 'online' },
        stopped: { text: '已停止', cls: 'offline' },
        failed: { text: '失败', cls: 'warning' },
        completed: { text: '已完成', cls: 'online' },
        active: { text: '运行中', cls: 'online' },
      }
      const mapped = statusMap[status] || { text: status, cls: 'offline' }
      return {
        name: item.name || '未知方案',
        algorithm: item.module_name || '未知算法',
        status: mapped.text,
        statusClass: mapped.cls,
      }
    })
  } catch {
    deploymentData.value = []
  }
}

const fetchAlarms = async (rawId?: number) => {
  try {
    const params: any = { page: 1, page_size: 50 }
    if (rawId) params.device_id = rawId
    const res: any = await getWarningEvents(params)
    const items = res.items || []
    alarmList.value = items.map((item: any) => ({
      id: item.id,
      time: item.time || item.captureTime?.split(' ')[1] || '00:00:00',
      type: getEventTypeDisplayName(item.eventType || item.eventTypeName) || '未知',
      device: item.device || '',
      location: item.location || '',
      level: item.level || 'info',
      handled: item.handled ?? false,
      isCompliant: item.isCompliant ?? true,
      imageUrl: item.imageUrl || '',
      captureTime: item.captureTime || '',
    }))
  } catch {
    alarmList.value = []
  }
}

function handleImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
  const placeholder = img.nextElementSibling as HTMLElement | null
  if (placeholder) placeholder.style.display = 'flex'
}

const restarting = ref(false)
const restartPollTimer = ref<number | null>(null)

const clearRestartPoll = () => {
  if (restartPollTimer.value !== null) {
    clearInterval(restartPollTimer.value)
    restartPollTimer.value = null
  }
}

const handleRestartAll = async () => {
  if (restarting.value) return
  clearRestartPoll()

  try {
    restarting.value = true
    const { task_id }: any = await deploymentApi.restartAll()
    if (!task_id) {
      throw new Error('未返回任务 ID')
    }

    ElMessage.info('重新监测任务已启动，正在轮询进度…')

    restartPollTimer.value = window.setInterval(async () => {
      try {
        const status: any = await deploymentApi.getRestartAllStatus(task_id)
        const {
          status: taskStatus,
          restarted = 0,
          failed = 0,
          skipped = 0,
          error,
        } = status

        if (taskStatus === 'completed') {
          clearRestartPoll()
          restarting.value = false
          ElMessage.success(
            `重新监测完成：已重启 ${restarted} 个，失败 ${failed} 个，跳过 ${skipped} 个`
          )
        } else if (taskStatus === 'failed') {
          clearRestartPoll()
          restarting.value = false
          ElMessage.error('重新监测失败：' + (error || '未知错误'))
        }
      } catch (pollError: any) {
        clearRestartPoll()
        restarting.value = false
        ElMessage.error('轮询任务进度失败：' + (pollError?.message || '未知错误'))
      }
    }, 2000)
  } catch (error: any) {
    restarting.value = false
    ElMessage.error('重新监测失败：' + (error?.message || '未知错误'))
  }
}

function isDirectVideoUrl(url: string): boolean {
  return /\.(mp4|webm|ogg|mov)(\?.*)?$/i.test(url)
}

function isLocalStream(sourceType: string, url: string): boolean {
  return sourceType === 'local' || isDirectVideoUrl(url)
}

function withCacheBuster(url: string, sourceType: string): string {
  if (sourceType !== 'local') return url
  if (!url) return url
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}_t=${Date.now()}`
}

const clearStreamRegisterPoll = () => {
  if (streamRegisterPollTimer.value !== null) {
    clearInterval(streamRegisterPollTimer.value)
    streamRegisterPollTimer.value = null
  }
}

const startStreamRegisterPoll = (taskId: string, onCompleted: (status: any) => void) => {
  clearStreamRegisterPoll()
  streamRegisterPollTimer.value = window.setInterval(async () => {
    try {
      const status: any = await getRegisterDevicesStatus(taskId)
      if (status.status === 'completed' || status.status === 'failed') {
        clearStreamRegisterPoll()
        streamRegistering.value = false
        streamLoading.value = false
        if (status.status === 'completed') {
          onCompleted(status)
        } else {
          console.error('Stream registration task failed:', status.error || status.errors)
          streamError.value = true
        }
      }
    } catch (pollError: any) {
      clearStreamRegisterPoll()
      streamRegistering.value = false
      streamLoading.value = false
      console.error('Stream register poll failed:', pollError)
    }
  }, 2000)
}

async function registerDeviceStream(rawId: string) {
  if (!rawId || streamRegistering.value) return

  streamRegistering.value = true
  streamLoading.value = true
  streamError.value = false

  try {
    const { task_id }: any = await registerDevicesAsync([rawId])
    if (!task_id) {
      throw new Error('未返回任务 ID')
    }

    startStreamRegisterPoll(task_id, (status: any) => {
      const item = (status.results || []).find((r: any) => String(r.device_id) === rawId)
      if (!item || !item.success) {
        console.warn(`[MonitorWall] Device ${rawId} stream registration failed:`, item?.error)
        return
      }

      const prefixedId = `device-${item.device_id}`
      const sourceType = item.source_type || ''
      streamMap.value = {
        ...streamMap.value,
        [prefixedId]: {
          url: withCacheBuster(item.flv_url, sourceType),
          sourceType,
        },
      }
    })
  } catch (error) {
    streamRegistering.value = false
    streamLoading.value = false
    console.error(`Failed to register stream for device ${rawId}:`, error)
  }
}

async function registerDeviceStreams() {
  if (channels.value.length === 0 || streamRegistering.value) return

  const rawIds = channels.value.map(ch => ch.id.replace(/^device-/, '')).filter(id => id !== '')
  if (rawIds.length === 0) return

  streamRegistering.value = true
  streamLoading.value = true
  streamError.value = false

  try {
    const { task_id }: any = await registerDevicesAsync(rawIds)
    if (!task_id) {
      throw new Error('未返回任务 ID')
    }

    startStreamRegisterPoll(task_id, (status: any) => {
      const results = status.results || []
      const newMap: Record<string, StreamInfo> = {}

      results.forEach((item: any) => {
        const prefixedId = `device-${item.device_id}`
        if (item.success) {
          newMap[prefixedId] = {
            url: withCacheBuster(item.flv_url, item.source_type || ''),
            sourceType: item.source_type || '',
          }
        } else {
          console.warn(`[MonitorWall] Device ${item.device_id} stream registration failed:`, item.error)
        }
      })

      streamMap.value = newMap
    })
  } catch (error) {
    streamRegistering.value = false
    streamLoading.value = false
    streamError.value = true
    console.error('Failed to register device streams:', error)
  }
}

onMounted(() => {
  fetchDeviceTree().then(() => {
    registerDeviceStreams()
    if (selectedChannel.value) {
      const rawId = parseRawChannelId(selectedChannel.value)
      fetchDashboardData(rawId)
      restartEventPolling(rawId)
      restartDashboardPolling(rawId)
    }
  })
  fetchAlgorithms()
  fetchAlarms()
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

const stopSelectedChannelWatch = watch(selectedChannel, (newChannel) => {
  if (!newChannel) return
  const rawId = newChannel.replace(/^device-/, '')
  if (!rawId) return
  registerDeviceStream(rawId)
  const rawNum = parseRawChannelId(newChannel)
  fetchDashboardData(rawNum)
  restartEventPolling(rawNum)
  restartDashboardPolling(rawNum)
})

function handleVisibilityChange() {
  const rawId = parseRawChannelId(selectedChannel.value)
  if (document.hidden) {
    clearEventPollTimer()
    clearDashboardRefreshTimer()
    clearStartStatusTimer()
  } else if (rawId) {
    fetchAlarms(rawId)
    fetchDashboardData(rawId)
    restartEventPolling(rawId)
    restartDashboardPolling(rawId)
  }
}

onUnmounted(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  stopSelectedChannelWatch()
  clearRestartPoll()
  clearStreamRegisterPoll()
  clearEventPollTimer()
  clearDashboardRefreshTimer()
  clearStartStatusTimer()
})

// 通道列表
const channels = computed(() => {
  const result: any[] = []
  deviceTreeData.value.forEach(org => {
    if (org.children) {
      org.children.forEach(group => {
        if (group.children) {
          group.children.forEach(device => {
            result.push({
              id: device.id,
              name: `${org.name} ${device.name}`
            })
          })
        }
      })
    }
  })
  return result
})

// 当前选中的设备
const currentDevice = computed(() => {
  return channels.value.find(ch => ch.id === selectedChannel.value)
})

// 视频URL
const currentVideoUrl = computed(() => {
  if (!currentDevice.value) return ''
  return streamMap.value[currentDevice.value.id]?.url || ''
})

// 当前视频源类型
const currentSourceType = computed(() => {
  if (!currentDevice.value) return ''
  return streamMap.value[currentDevice.value.id]?.sourceType || ''
})

// 当前视频协议
const currentProtocol = computed(() => {
  const url = currentVideoUrl.value
  if (!url) return 'flv'
  if (url.toLowerCase().endsWith('.m3u8')) return 'hls'
  return 'flv'
})

// 是否使用原生视频播放本地文件
const isNativeVideo = computed(() => {
  return isLocalStream(currentSourceType.value, currentVideoUrl.value)
})

// 统计数据
const statsData = ref({
  avgSpeed: '--',
  upTraffic: '--',
  downTraffic: '--',
  roadLevel: 1,
  roadLevelText: '畅通'
})

// 事件统计
const eventStats = ref({
  total: 0,
  legend: [] as { name: string; value: number; color: string }[],
})

// 饼图样式
const donutStyle = computed(() => {
  const legend = eventStats.value.legend
  if (legend.length === 0 || eventStats.value.total === 0) {
    return { background: 'conic-gradient(rgba(0,229,255,0.2) 0% 100%)' }
  }
  let gradient = ''
  let currentPercent = 0
  legend.forEach((item, index) => {
    const percent = (item.value / eventStats.value.total) * 100
    gradient += `${item.color} ${currentPercent}% ${currentPercent + percent}%`
    if (index < legend.length - 1) gradient += ', '
    currentPercent += percent
  })
  return {
    background: `conic-gradient(${gradient})`
  }
})

// 能见度
const visibilityPosition = computed(() => {
  return '65%'
})

// 道路等级位置
const roadLevelPosition = computed(() => {
  const level = statsData.value.roadLevel
  return `${(level - 1) * 25}%`
})

// 过滤后的事件
const filteredEvents = computed(() => {
  const events = alarmList.value.slice(0, 8)
  if (eventFilter.value === 'all') {
    return events
  }
  return events.filter(e => !e.isCompliant)
})
</script>

<style scoped>
.monitor-wall {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #000510;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  min-height: 0;
  padding: 15px;
  gap: 15px;
}

/* 左侧视频区域 */
.video-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

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

/* 视频装饰角 */
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

/* 右侧面板 */
.right-panel {
  width: 400px;
  min-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 6px;
}

.right-panel::-webkit-scrollbar {
  width: 6px;
}

.right-panel::-webkit-scrollbar-track {
  background: rgba(0, 229, 255, 0.05);
  border-radius: 3px;
}

.right-panel::-webkit-scrollbar-thumb {
  background: rgba(0, 229, 255, 0.45);
  border-radius: 3px;
}

.right-panel::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 229, 255, 0.7);
}

.panel-section {
  background: rgba(0, 20, 50, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  padding: 12px;
  flex-shrink: 0;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.header-bar {
  width: 3px;
  height: 14px;
  background: #00E5FF;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
}

.header-line {
  flex: 1;
  height: 1px;
  background: repeating-linear-gradient(
    90deg,
    rgba(0, 229, 255, 0.3),
    rgba(0, 229, 255, 0.3) 4px,
    transparent 4px,
    transparent 8px
  );
}

/* 预览通道 */
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
.restart-btn {
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

.restart-btn {
  border-color: #ff9f43;
  color: #ff9f43;
  background: transparent;
}

.restart-btn:hover {
  background: rgba(255, 159, 67, 0.1);
}

/* 实时交通参数 */
.traffic-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.traffic-item {
  text-align: center;
}

.traffic-value {
  font-size: 28px;
  font-weight: bold;
  color: rgba(180, 210, 235, 0.85);
  margin-bottom: 4px;
}

.traffic-value.primary {
  color: #00E5FF;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.traffic-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

/* 事件统计 */
.donut-chart-area {
  display: flex;
  align-items: center;
  gap: 20px;
}

.donut-chart {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.donut-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.donut-total {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #00E5FF;
}

.donut-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
}

.donut-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
}

.legend-value {
  font-weight: bold;
  color: rgba(180, 210, 235, 0.85);
}

/* 等级指标 */
.level-item {
  margin-bottom: 12px;
}

.level-item:last-child {
  margin-bottom: 0;
}

.level-header {
  margin-bottom: 6px;
}

.level-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.level-bar {
  position: relative;
  height: 8px;
  background: linear-gradient(90deg, #00FF88, #FFB800, #FF006E);
  border-radius: 4px;
  margin-bottom: 4px;
}

.level-gradient {
  width: 100%;
  height: 100%;
  border-radius: 4px;
}

.level-marker {
  position: absolute;
  top: -4px;
  width: 4px;
  height: 16px;
  background: rgba(180, 210, 235, 0.85);
  border-radius: 2px;
  transform: translateX(-50%);
}

.level-scale {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.level-status {
  text-align: center;
  font-size: 12px;
  margin-top: 4px;
  padding: 2px 8px;
  border-radius: 2px;
  display: inline-block;
}

.level-status.level-1 {
  background: rgba(82, 196, 26, 0.2);
  color: #00FF88;
}

.level-status.level-2 {
  background: rgba(255, 170, 0, 0.2);
  color: #FFB800;
}

/* 布控信息 */
.deployment-table {
  background: transparent;
}

.deployment-table :deep(.el-table__header th) {
  background: rgba(0, 229, 255, 0.1);
  color: rgba(180, 210, 235, 0.85);
  font-size: 11px;
  border-color: rgba(0, 229, 255, 0.15);
}

.deployment-table :deep(.el-table__body td) {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  font-size: 11px;
  border-color: rgba(0, 229, 255, 0.1);
}

.deployment-table :deep(.el-table__row:hover td) {
  background: rgba(0, 229, 255, 0.06);
}

.status-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
}

.status-tag.online {
  background: rgba(82, 196, 26, 0.2);
  color: #00FF88;
}

.status-tag.offline {
  background: rgba(120, 130, 150, 0.2);
  color: rgba(180, 210, 235, 0.7);
}

.status-tag.warning {
  background: rgba(255, 0, 110, 0.2);
  color: #FF006E;
}

/* 视频质量检测 */
.quality-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.quality-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* 底部事件抓拍 */
.bottom-events {
  padding: 12px 20px;
  background: rgba(0, 20, 50, 0.6);
  border-top: 1px solid rgba(0, 229, 255, 0.2);
}

.events-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.events-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
}

/* radio-button 深色主题适配 */
.events-header :deep(.el-radio-button__inner) {
  background: rgba(0, 21, 41, 0.8);
  border-color: rgba(0, 229, 255, 0.3);
  color: rgba(200, 230, 255, 0.85);
  font-size: 12px;
  padding: 4px 12px;
}

.events-header :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
  box-shadow: none;
}

.events-carousel {
  display: flex;
  gap: 12px;
  overflow-x: auto;
}

.events-carousel::-webkit-scrollbar {
  height: 4px;
}

.events-carousel::-webkit-scrollbar-thumb {
  background: rgba(0, 229, 255, 0.3);
  border-radius: 2px;
}

.event-card {
  flex-shrink: 0;
  width: 140px;
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.event-thumb {
  position: relative;
  height: 80px;
  overflow: hidden;
}

.event-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.event-no-image {
  position: absolute;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(0, 20, 40, 0.8);
  color: rgba(180, 210, 235, 0.85);
  font-size: 12px;
}

.event-label {
  padding: 6px 8px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.1), transparent);
  clip-path: polygon(0 0, 100% 0, 100% 70%, 80% 100%, 0 100%);
}

.event-type {
  font-size: 11px;
  color: rgba(180, 210, 235, 0.85);
}

/* 底部信息栏 */
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
