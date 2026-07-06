/**
 * NOTE: 当前实现继续走 /api/warning-events（event_type=flow/jam 反查）作为 fallback。
 * 后端 Phase 6 新增 /api/realtime/{device_id}/latest 提供一站式聚合；
 * 切换时：fetchStatsData / fetchEventStats / fetchDeploymentData 合并为一次调用。
 * 切换前需先在生产验证新端点的 p95 延迟 < 200ms。
 */
import { ref, watch, type Ref } from 'vue'
import { useIntervalFn } from '@vueuse/core'
import { getList as getWarningEvents } from '@/api/warning-events'
import { getSceneStats } from '@/api/event-stats'
import { deploymentApi } from '@/api/deployment'
import type { AlarmItem } from '@/types/alarm'
import { roadLevelFromJam } from '@/constants/roadLevel'
import { getEventTypeDisplayName } from '@/utils/eventType'
import { formatDateTime } from '@/utils/date'

export interface DashboardData {
  avgSpeed: string
  upTraffic: string
  downTraffic: string
  roadLevel: number
  roadLevelText: string
}

const POLL_EVENT_MS = 3000
const POLL_DASHBOARD_MS = 5000
const LEGEND_COLORS = ['#00FFCC', '#0099FF', '#00EAFF', '#FF9900']

function parseRawChannelId(channelId: string): number {
  if (!channelId) return 0
  const raw = channelId.replace(/^device-/, '')
  const num = Number(raw)
  return Number.isNaN(num) ? 0 : num
}

export function useDashboardPolling(channel: Ref<string>) {
  const alarmList = ref<AlarmItem[]>([])
  const statsData = ref<DashboardData>({
    avgSpeed: '--',
    upTraffic: '--',
    downTraffic: '--',
    roadLevel: 1,
    roadLevelText: '畅通',
  })
  const eventStats = ref<{ total: number; legend: { name: string; value: number; color: string }[] }>({
    total: 0,
    legend: [],
  })
  const deploymentData = ref<any[]>([])
  const dashboardLoading = ref(false)

  async function fetchAlarms(rawId?: number) {
    try {
      const params: any = { page: 1, page_size: 50 }
      if (rawId) params.device_id = rawId
      const res: any = await getWarningEvents(params)
      alarmList.value = (res.items || []).map((item: any) => ({
        id: item.id,
        time: formatDateTime(item.time || item.captureTime),
        type: getEventTypeDisplayName(item.eventType || item.eventTypeName),
        device: item.device || item.cameraName || '',
        deviceName: item.cameraName || item.device || '',
        location: item.location || '',
        eventDetail: item.eventDetail || '',
        level: item.level || 'info',
        handled: item.handled ?? false,
        processStatus: item.status || 'pending',
        isCompliant: item.isCompliant ?? false,
        imageUrl: item.imageUrl || '',
        videoUrl: item.videoUrl || '',
        captureTime: item.captureTime || '',
      }))
    } catch {
      // 静默：api 层已记录
    }
  }

  async function fetchStatsData(rawId: number) {
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
        } catch {/* 解析失败保持默认 */}
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
          const level = roadLevelFromJam(jam.is_jam === true, jam.confidence ?? 0)
          roadLevel = level
          roadLevelText = level === 4 ? '拥堵' : level === 3 ? '缓慢' : '畅通'
        } catch {/* 解析失败保持默认 */}
      }
    } catch {/* api 层已记录 */}
    statsData.value = { avgSpeed: '--', upTraffic, downTraffic, roadLevel, roadLevelText }
  }

  async function fetchEventStats(rawId: number) {
    if (!rawId) return
    try {
      const today = new Date().toLocaleDateString('zh-CN', {
        year: 'numeric', month: '2-digit', day: '2-digit',
      }).replace(/\//g, '-')
      const res: any = await getSceneStats({ device_id: rawId, start_date: today })
      const categories = res.categories || []
      const values = res.values || []
      eventStats.value = {
        total: values.reduce((sum: number, v: number) => sum + (v || 0), 0),
        legend: categories.map((name: string, index: number) => ({
          name,
          value: values[index] || 0,
          color: LEGEND_COLORS[index % LEGEND_COLORS.length],
        })),
      }
    } catch {
      eventStats.value = { total: 0, legend: [] }
    }
  }

  async function fetchDeploymentData(rawId: number) {
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

  async function fetchDashboardData(rawId: number) {
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

  const eventPolling = useIntervalFn(() => {
    const rawId = parseRawChannelId(channel.value)
    if (rawId) void fetchAlarms(rawId)
  }, POLL_EVENT_MS, { immediate: false, immediateCallback: false })

  const dashboardPolling = useIntervalFn(() => {
    const rawId = parseRawChannelId(channel.value)
    if (rawId) void fetchDashboardData(rawId)
  }, POLL_DASHBOARD_MS, { immediate: false, immediateCallback: false })

  watch(channel, (newChannel) => {
    const rawId = parseRawChannelId(newChannel)
    if (!rawId) return
    eventPolling.resume()
    dashboardPolling.resume()
    void fetchAlarms(rawId)
    void fetchDashboardData(rawId)
  }, { immediate: true })

  function pause() {
    eventPolling.pause()
    dashboardPolling.pause()
  }

  function resume() {
    eventPolling.resume()
    dashboardPolling.resume()
  }

  return {
    alarmList,
    statsData,
    eventStats,
    deploymentData,
    dashboardLoading,
    fetchDashboardData,
    fetchAlarms,
    pause,
    resume,
  }
}