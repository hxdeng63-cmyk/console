<template>
  <div class="monitor-wall">
    <div class="main-content">
      <div class="video-area">
        <VideoStage
          :device="currentDevice"
          :video-url="currentVideoUrl"
          :source-type="currentSourceType"
          :protocol="currentProtocol"
          :loading="registry.streamLoading.value"
          :error="registry.streamError.value"
          :refresh-stream-url="refreshStreamUrlSync"
          @hls-network-error="refreshStreamOnNetworkError"
        />
      </div>

      <div class="right-panel">
        <div class="panel-section channel-section">
          <div class="section-header">
            <span class="section-title">预览通道</span>
          </div>
          <ChannelSelector
            :channels="channels"
            :algorithms="algorithms"
            :channel="selectedChannel"
            :algorithm="selectedAlgorithm"
            :monitoring="monitoring"
            :starting-all="tasks.startingAll.value"
            :get-event-type-display-name="getEventTypeDisplayName"
            @update:channel="selectedChannel = $event"
            @update:algorithm="selectedAlgorithm = $event"
            @start-all="handleStartAll"
          />
        </div>

        <div class="panel-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">实时交通参数</span>
            <span class="header-line"></span>
          </div>
          <TrafficMetrics :data="dashboard.statsData.value" :loading="dashboard.dashboardLoading.value" />
        </div>

        <div class="panel-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">交通事件统计</span>
            <span class="header-line"></span>
          </div>
          <EventDonutChart :stats="dashboard.eventStats.value" :loading="dashboard.dashboardLoading.value" />
        </div>

        <div class="panel-section level-section">
          <LevelIndicator
            label="道理通行等级"
            :value="dashboard.statsData.value.roadLevel"
            :max="5"
            :scale-labels="['1', '2', '3', '4', '5']"
            :status-text="dashboard.statsData.value.roadLevelText"
            :status-class="`level-${dashboard.statsData.value.roadLevel}`"
          />
          <LevelIndicator
            label="能见度等级"
            :value="6"
            :max="10"
            :scale-labels="['0', '2', '4', '6', '8', '10']"
            gradient-class="visibility"
          />
        </div>

        <div class="panel-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">布控信息</span>
            <span class="header-line"></span>
          </div>
          <DeploymentTable :data="dashboard.deploymentData.value" :loading="dashboard.dashboardLoading.value" />
        </div>

        <div class="panel-section quality-section">
          <span class="quality-label">视频质量检测</span>
          <span class="status-tag online">在线</span>
        </div>
      </div>
    </div>

    <EventCarousel :events="filteredEvents" @alarm-click="handleAlarmClick" />
    <BottomInfoBar :deployment-info="deploymentInfo" :filter="eventFilter" @update:filter="eventFilter = $event" />
    <AlarmDetailDialog v-model="detailDialogVisible" :alarm="selectedAlarm" @playback="handleVideoPlayback" />
    <VideoPlaybackDialog v-model="videoDialogVisible" :url="selectedAlarm?.videoUrl || ''" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useStreamRegistry } from '@/composables/useStreamRegistry'
import { useDashboardPolling } from '@/composables/useDashboardPolling'
import { useTaskPolling } from '@/composables/useTaskPolling'
import { useStopPoll } from '@/composables/useStopPoll'
import { useVisibilityResume } from '@/composables/useVisibilityResume'
import { useCurrentStream } from '@/composables/useCurrentStream'
import { getEventTypeDisplayName } from '@/utils/eventType'
import { getDeviceGroupTree } from '@/api/device-groups'
import { deploymentApi } from '@/api/deployment'
import { getDeviceFlvUrl } from '@/api/stream'
import VideoStage from '@/components/dashboard/VideoStage.vue'
import ChannelSelector from '@/components/dashboard/ChannelSelector.vue'
import TrafficMetrics from '@/components/dashboard/TrafficMetrics.vue'
import EventDonutChart from '@/components/dashboard/EventDonutChart.vue'
import LevelIndicator from '@/components/dashboard/LevelIndicator.vue'
import DeploymentTable from '@/components/dashboard/DeploymentTable.vue'
import EventCarousel from '@/components/dashboard/EventCarousel.vue'
import BottomInfoBar from '@/components/dashboard/BottomInfoBar.vue'
import AlarmDetailDialog from '@/components/dashboard/AlarmDetailDialog.vue'
import VideoPlaybackDialog from '@/components/dashboard/VideoPlaybackDialog.vue'
import type { AlarmItem } from '@/types/alarm'
import type { DeviceNode } from '@/components/device-tree/useDeviceTree'

interface AlgorithmEvent {
  name: string
  description?: string
  moduleName: string
}
interface AlgorithmGroup {
  id: number
  name: string
  events: AlgorithmEvent[]
}

const selectedChannel = ref('')
const selectedAlgorithm = ref('')
const monitoring = ref(false)
const eventFilter = ref<'all' | 'danger'>('all')
const detailDialogVisible = ref(false)
const videoDialogVisible = ref(false)
const selectedAlarm = ref<AlarmItem | null>(null)
const deviceTreeData = ref<DeviceNode[]>([])
const channels = ref<{ id: string; name: string }[]>([])

const registry = useStreamRegistry()
const dashboard = useDashboardPolling(selectedChannel)
const tasks = useTaskPolling()
const stopPoll = useStopPoll()


const { currentDevice, currentVideoUrl, currentSourceType, currentProtocol } =
  useCurrentStream(selectedChannel, channels, registry.streamMap, selectedAlgorithm)

const algorithms = ref<AlgorithmGroup[]>([])
const filteredEvents = computed(() => {
  const events = dashboard.alarmList.value.slice(0, 8)
  return eventFilter.value === 'all' ? events : events.filter(e => e.isCompliant === false)
})
const deploymentInfo = computed(() => {
  const total = deviceTreeData.value.reduce(
    (s, o) => s + (o.children?.reduce((a, g) => a + (g.children?.length || 0), 0) || 0), 0,
  )
  const first = deviceTreeData.value[0]
  return first ? `${first.name}(${total}路)` : '暂无设备'
})

function handleAlarmClick(alarm: AlarmItem) {
  selectedAlarm.value = alarm
  detailDialogVisible.value = true
}
function handleVideoPlayback() {
  if (!selectedAlarm.value?.videoUrl) { ElMessage.warning('该事件暂无可回放视频'); return }
  videoDialogVisible.value = true
}
function parseRawChannelId(channelId: string): number {
  if (!channelId) return 0
  const n = Number(channelId.replace(/^device-/, ''))
  return Number.isNaN(n) ? 0 : n
}

async function fetchDeviceTree() {
  try {
    const tree: any[] = await getDeviceGroupTree()
    const byCompany = new Map<string, any[]>()
    const channelList: { id: string; name: string }[] = []
    function collect(nodes: any[], path: string[]) {
      for (const n of nodes || []) {
        if (n.level === 'device') {
          const id = `device-${n.id}`
          const prefix = path.join('-').replace('-', ' ')  // "海东公司-大学城北-北区" → "海东公司 大学城北-北区"
          channelList.push({ id, name: `${prefix}-${n.name}` })
          const companyName = path[0] || ''
          if (!byCompany.has(companyName)) byCompany.set(companyName, [])
          byCompany.get(companyName)!.push({
            id,
            name: n.name,
            type: 'camera' as const,
            online: n.status === 'active',
            ip: '',
          })
        } else {
          collect(n.children || [], [...path, n.name])
        }
      }
    }
    collect(tree, [])
    deviceTreeData.value = Array.from(byCompany, ([orgName, cams]) => ({
      id: `org-${orgName}`,
      name: orgName,
      type: 'org' as const,
      online: true,
      children: [{
        id: `group-${orgName}`,
        name: orgName,
        type: 'group' as const,
        online: true,
        children: cams,
      }],
    }))
    channels.value = channelList
    // 默认选第一个设备，触发 useDashboardPolling watch 把右栏 polling 跑起来。
    if (!selectedChannel.value && channelList.length) {
      selectedChannel.value = channelList[0].id
    }
  } catch { ElMessage.error('获取设备列表失败') }
}

async function fetchAlgorithms() {
  try {
    const res: any = await deploymentApi.listAlgorithms({ page: 1, page_size: 100 })
    algorithms.value = (res.items || []).map((a: any) => ({
      id: a.id, name: a.name,
      events: (a.events || []).map((e: any) => ({ name: e.name, description: e.description, moduleName: e.module_name || '' })),
    }))
  } catch { ElMessage.error('加载算法列表失败') }
}

async function stopExisting(deploymentId: number, existing?: any): Promise<boolean> {
  try {
    const stopRes: any = await deploymentApi.stop(deploymentId)
    if (!stopRes?.task_id) return true
    const r = await stopPoll.startStopPoll(deploymentId, stopRes.task_id)
    return r.outcome !== 'timeout'
  } catch (err: any) {
    const s = err?.response?.status
    if (s === 404 || s === 410) {
      // traffic-api 端 404：任务已结束，但 DB 里 deployment 状态可能仍卡在
      // running/pending/stopping。必须主动重置，否则 ensureDeploymentId 会
      // 看到旧状态再次调 stop → 死循环。{ ...existing } 展开保留 device_ids
      // 等必填字段，避免后端 PUT 删除 device 关联。
      if (existing) {
        try { await deploymentApi.update(deploymentId, { ...existing, algorithm_status: 'stopped' }) } catch {}
      }
      return true
    }
    ElMessage.error('停止旧任务失败，已阻断启动：' + (err?.response?.data?.detail || err?.message || '未知错误'))
    return false
  }
}

async function ensureDeploymentId(rawId: number, algorithmId: number, moduleName: string): Promise<number | null> {
  const existing: any = await deploymentApi.list({ device_id: rawId, module_name: moduleName, page: 1, page_size: 1 })
  const item = existing.items?.[0]
  if (item) {
    if (['running', 'pending', 'stopping'].includes(item.algorithm_status)) {
      if (!(await stopExisting(item.id, item))) return null
    }
    return item.id
  }
  const created: any = await deploymentApi.create({
    name: `${moduleName}_${rawId}`, algorithm_id: algorithmId, device_ids: [rawId],
    module_name: moduleName, status: 'active', algorithm_status: 'stopped',
  })
  return created.id
}

// 启动当前选中通道 + 选中算法。只在"开始监测"按钮点击时调用(选下拉不再触发)。
// onSuccess 回调里调 getDeviceFlvUrl 刷 streamMap —— 这是修黑屏的关键:
// traffic-api /start 完成后 HLS 推理流 m3u8 才就绪,register 占位 url 已失效。
async function startSelectedAlgorithm(): Promise<void> {
  if (tasks.startingAll.value) return
  if (!selectedChannel.value) { ElMessage.warning('请先选择预览通道'); return }
  if (!selectedAlgorithm.value) { ElMessage.warning('请先选择识别算法'); return }
  const parts = selectedAlgorithm.value.split(':')
  if (parts.length < 3 || !parts[1]) { ElMessage.warning('该算法模块不可运行'); return }
  const [aId, moduleName, eventName] = parts
  const algorithmId = Number(aId)
  const rawId = parseRawChannelId(selectedChannel.value)
  if (!rawId || !algorithmId || !moduleName || !eventName) return
  try {
    const deploymentId = await ensureDeploymentId(rawId, algorithmId, moduleName)
    if (!deploymentId) return
    const startPayload = {
      module_name: moduleName, video_path: 'auto',
      stream_map: { [String(rawId)]: String(rawId) },
      config: { callback_url: (import.meta.env.VITE_TRAFFIC_CALLBACK_URL as string) || '', push_interval: 1.0 },
    }
    let startRes: any
    const MAX_START_ATTEMPTS = 3
    for (let attempt = 1; attempt <= MAX_START_ATTEMPTS; attempt += 1) {
      try {
        startRes = await deploymentApi.start(deploymentId, startPayload)
        break
      } catch (startErr: any) {
        // traffic-api 状态机：上一个 task completed 后短暂（数秒）未释放 slot
        // → 409 状态冲突。最多重试 3 次，每次 sleep 2s。
        const status = startErr?.response?.status
        if (status === 409 && attempt < MAX_START_ATTEMPTS) {
          await new Promise(r => setTimeout(r, 2000))
          continue
        }
        throw startErr
      }
    }
    tasks.startStartPoll({
      deploymentId, taskId: startRes.task_id, moduleName,
      onSuccess: () => {
        const rid = parseRawChannelId(selectedChannel.value)
        if (!rid) return
        void dashboard.fetchDashboardData(rid)
        void dashboard.fetchAlarms(rid)
        // 算法 start success 后,traffic-api 的 HLS 推理流 m3u8 才就绪。
        // 此时 register 时拿到的占位 flv_url(token 已轮换)已失效,必须重新拉一次
        // 覆盖 streamMap,否则 useCurrentStream 拿旧 url → 403 → 黑屏。
        void (async () => {
          try {
            const info: any = await getDeviceFlvUrl(rid)
            if (!info?.flv_url) return
            registry.streamMap.value = {
              ...registry.streamMap.value,
              [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type || 'stream' },
            }
          } catch (err) {
            console.warn('[MonitorWall] 启动后刷新 flv_url 失败', err)
          }
        })()
        monitoring.value = true
      },
    })
    ElMessage.success('识别任务已启动')
  } catch (error: any) {
    ElMessage.error('启动识别失败：' + (error?.message || '未知错误'))
  }
}

// 停止当前选中通道 + 选中算法的监测。
async function stopSelectedAlgorithm(): Promise<void> {
  if (!monitoring.value) return
  if (!selectedAlgorithm.value) { monitoring.value = false; return }
  const parts = selectedAlgorithm.value.split(':')
  if (parts.length < 3 || !parts[1]) { monitoring.value = false; return }
  const [, moduleName] = parts
  const rawId = parseRawChannelId(selectedChannel.value)
  if (!rawId || !moduleName) { monitoring.value = false; return }
  try {
    const existing: any = await deploymentApi.list({ device_id: rawId, module_name: moduleName, page: 1, page_size: 1 })
    const item = existing.items?.[0]
    if (!item) { monitoring.value = false; return }
    if (item.algorithm_status === 'stopped') { monitoring.value = false; return }
    const stopRes: any = await deploymentApi.stop(item.id)
    if (!stopRes?.task_id) { monitoring.value = false; return }
    const r = await stopPoll.startStopPoll(item.id, stopRes.task_id)
    if (r.outcome === 'timeout') {
      ElMessage.warning('停止任务超时,请稍后再试')
    }
  } catch (err: any) {
    const s = err?.response?.status
    if (s !== 404 && s !== 410) {
      ElMessage.error('停止监测失败：' + (err?.response?.data?.detail || err?.message || '未知错误'))
    }
  } finally {
    monitoring.value = false
  }
}

async function handleStartAll() {
  if (monitoring.value) {
    await stopSelectedAlgorithm()
  } else {
    await startSelectedAlgorithm()
  }
}

useVisibilityResume(() => dashboard.pause(), () => dashboard.resume())

// HLS 致命网络错误(403 token 失效 / 404 设备未注册)回调:
// 重新拉一次 flv_url 覆盖 streamMap → useCurrentStream 重新算 url → VideoPlayer url watch
// 触发 switchUrl → 加载新 url。如果新拉仍是 404,清掉 streamMap 让 VideoStage 显示提示。
async function refreshStreamOnNetworkError() {
  await refreshStreamMap()
}

// 同步版本: HLS fatal NETWORK_ERROR 时 useVideoPlayer 会 await 这个返回值,
// 必须返回**新 url**给 hlsInstance.loadSource(newUrl)。不能走 emit + 异步更新 streamMap 的反应链,
// 因为反应链有时间差,等不到新 url 就放弃了。
async function refreshStreamUrlSync(): Promise<string | null> {
  const rid = parseRawChannelId(selectedChannel.value)
  if (!rid) return null
  try {
    const info: any = await getDeviceFlvUrl(rid)
    if (info?.flv_url) {
      registry.streamMap.value = {
        ...registry.streamMap.value,
        [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type || 'stream' },
      }
      return info.flv_url
    }
    return null
  } catch (err: any) {
    console.warn('[MonitorWall] refreshStreamUrlSync 失败', err)
    if (err?.response?.status === 404) {
      const key = `device-${rid}`
      if (registry.streamMap.value[key]) {
        const next = { ...registry.streamMap.value }
        delete next[key]
        registry.streamMap.value = next
      }
    }
    return null
  }
}

async function refreshStreamMap() {
  if (!selectedChannel.value) return
  const rid = parseRawChannelId(selectedChannel.value)
  if (!rid) return
  try {
    const info: any = await getDeviceFlvUrl(rid)
    if (!info?.flv_url) return
    registry.streamMap.value = {
      ...registry.streamMap.value,
      [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type || 'stream' },
    }
  } catch (err: any) {
    console.warn('[MonitorWall] 网络错误回调刷新 streamMap 失败', err)
    if (err?.response?.status === 404) {
      const key = `device-${rid}`
      if (registry.streamMap.value[key]) {
        const next = { ...registry.streamMap.value }
        delete next[key]
        registry.streamMap.value = next
      }
    }
  }
}

// traffic-api 每次 /stream/devices/register 都会**轮换 stream token**，
// 批量注册时拿到的 flv_url 在用户真正点开设备时已失效（403 Invalid stream token）。
// 每次 selectedChannel 变化 → 立刻向 traffic-api 现拉一次最新 flv_url 覆盖 streamMap。
//
// 404 同样清理 streamMap 条目（见下方 selectedAlgorithm watch 的注释）。
import { watch as vueWatch } from 'vue'
vueWatch(() => selectedChannel.value, async (rawId) => {
  if (!rawId) return
  const rid = parseRawChannelId(rawId)
  if (!rid) return
  try {
    const info: any = await getDeviceFlvUrl(rid)
    if (!info?.flv_url) return
    registry.streamMap.value = {
      ...registry.streamMap.value,
      [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type || 'stream' },
    }
  } catch (err: any) {
    console.warn('[MonitorWall] 拉取最新 flv_url 失败', err)
    if (err?.response?.status === 404) {
      const key = `device-${rid}`
      if (registry.streamMap.value[key]) {
        const next = { ...registry.streamMap.value }
        delete next[key]
        registry.streamMap.value = next
      }
    }
  }
})

// 选算法本身不启动监测（"开始监测" 按钮才启动），但 hasAlgorithm 翻 true 后
// useCurrentStream 会立刻读 streamMap.url — 那个 url 可能是 register 时拿的过期 token (403)。
// 所以 selectedAlgorithm 变非空时也必须**立刻**拉一次最新 flv_url 覆盖 streamMap。
//
// 404 含义（后端 `/stream/device/{id}/flv`）：该设备在 traffic-api 端没有流注册，
// 此时不要保留旧的(可能失效的) url，否则 VideoStage 会用死 url 喂 hls.js → 持续 404 → 黑屏。
// 直接 delete 该 device 的 streamMap 条目 → useCurrentStream 返回 '' → VideoStage 显示"无法连接"。
vueWatch(() => selectedAlgorithm.value, async (val) => {
  if (!val) return
  if (!selectedChannel.value) return
  const rid = parseRawChannelId(selectedChannel.value)
  if (!rid) return
  try {
    const info: any = await getDeviceFlvUrl(rid)
    if (!info?.flv_url) return
    registry.streamMap.value = {
      ...registry.streamMap.value,
      [`device-${rid}`]: { url: info.flv_url, sourceType: info.source_type || 'stream' },
    }
  } catch (err: any) {
    console.warn('[MonitorWall] 选算法后拉取最新 flv_url 失败', err)
    if (err?.response?.status === 404) {
      const key = `device-${rid}`
      if (registry.streamMap.value[key]) {
        const next = { ...registry.streamMap.value }
        delete next[key]
        registry.streamMap.value = next
      }
    }
  }
})

onMounted(() => {
  void fetchDeviceTree().then(() => {
    const rawIds = channels.value.map(c => c.id.replace(/^device-/, '')).filter(id => id !== '')
    if (rawIds.length) void registry.registerDeviceStreams(rawIds)
    if (selectedChannel.value) {
      const rid = parseRawChannelId(selectedChannel.value)
      if (rid) {
        registry.registerDeviceStream(rid.toString())
        // 默认设备拉一次右栏数据，不等 3s/5s 轮询。
        void dashboard.fetchAlarms(rid)
        void dashboard.fetchDashboardData(rid)
      }
    }
  })
  void fetchAlgorithms()
})
</script>

<style scoped>
.monitor-wall { display: flex; flex-direction: column; height: 100%; background: #000510; }
.main-content { display: flex; flex: 1; min-height: 0; padding: 15px; gap: 15px; }
.video-area { flex: 1; display: flex; flex-direction: column; }
.right-panel {
  width: 400px; min-width: 400px; display: flex; flex-direction: column; gap: 12px;
  height: 100%; overflow-y: auto; overflow-x: hidden; padding-right: 6px;
}
.right-panel::-webkit-scrollbar { width: 6px; }
.right-panel::-webkit-scrollbar-track { background: rgba(0, 229, 255, 0.05); border-radius: 3px; }
.right-panel::-webkit-scrollbar-thumb { background: rgba(0, 229, 255, 0.45); border-radius: 3px; }
.right-panel::-webkit-scrollbar-thumb:hover { background: rgba(0, 229, 255, 0.7); }
.panel-section {
  background: rgba(0, 20, 50, 0.6); border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px; padding: 12px; flex-shrink: 0;
}
.section-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.header-bar { width: 3px; height: 14px; background: #00E5FF; }
.section-title { font-size: 13px; font-weight: 500; color: rgba(180, 210, 235, 0.85); }
.header-line {
  flex: 1; height: 1px; background: repeating-linear-gradient(90deg,
    rgba(0, 229, 255, 0.3), rgba(0, 229, 255, 0.3) 4px, transparent 4px, transparent 8px);
}
.channel-section .section-header { margin-bottom: 0; }
.level-section { display: flex; flex-direction: column; gap: 12px; }
.quality-section { display: flex; align-items: center; justify-content: space-between; }
.quality-label { font-size: 12px; color: rgba(255, 255, 255, 0.7); }
.status-tag { font-size: 10px; padding: 2px 6px; border-radius: 2px; }
.status-tag.online { background: rgba(82, 196, 26, 0.2); color: #00FF88; }
.status-tag.offline { background: rgba(120, 130, 150, 0.2); color: rgba(180, 210, 235, 0.7); }
.status-tag.warning { background: rgba(255, 0, 110, 0.2); color: #FF006E; }
</style>
