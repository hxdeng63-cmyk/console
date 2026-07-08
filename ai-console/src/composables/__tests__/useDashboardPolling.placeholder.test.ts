import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useDashboardPolling } from '../useDashboardPolling'

vi.mock('@/api/warning-events', () => ({
  getList: vi.fn(),
}))
vi.mock('@/api/event-stats', () => ({
  getSceneStats: vi.fn(),
}))
vi.mock('@/api/deployment', () => ({
  deploymentApi: { list: vi.fn() },
}))

import * as warningEvents from '@/api/warning-events'
import * as eventStats from '@/api/event-stats'
import * as deployment from '@/api/deployment'

describe('useDashboardPolling 占位常量', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // 默认: warning 返回空(alarmList), event-stats/deployment 返回空
    vi.mocked(warningEvents.getList).mockResolvedValue({ items: [] } as any)
    vi.mocked(eventStats.getSceneStats).mockResolvedValue({ categories: [], values: [] } as any)
    vi.mocked(deployment.deploymentApi.list).mockResolvedValue({ items: [] } as any)
  })

  it('avgSpeed 从 flow 事件 detail.avg_speed 拉取(无 avg_speed 时保持 --)', async () => {
    // 用 mockImplementation 让 flow 调用返回带 up/down 但无 avg_speed 的项
    vi.mocked(warningEvents.getList).mockImplementation(async (params: any) => {
      if (params?.event_type === 'flow') {
        return { items: [{ eventDetail: JSON.stringify({ up_count: 100, down_count: 50 }) }] } as any
      }
      return { items: [] } as any
    })

    const channel = ref('device-1')
    const { statsData, fetchDashboardData } = useDashboardPolling(channel)
    await fetchDashboardData(1)

    // flow detail 没 avg_speed 字段时,保持 '--'
    expect(statsData.value.avgSpeed).toBe('--')
  })

  it('avgSpeed 从 flow 事件 detail.avg_speed 拉取(有 avg_speed 时取数值)', async () => {
    vi.mocked(warningEvents.getList).mockImplementation(async (params: any) => {
      if (params?.event_type === 'flow') {
        return { items: [{ eventDetail: JSON.stringify({ avg_speed: 60 }) }] } as any
      }
      return { items: [] } as any
    })

    const channel = ref('device-1')
    const { statsData, fetchDashboardData } = useDashboardPolling(channel)
    await fetchDashboardData(1)
    expect(statsData.value.avgSpeed).toBe('60')
  })

  it('visibilityLevel 默认 null(无后端接口)', async () => {
    const channel = ref('device-1')
    const { statsData, fetchDashboardData } = useDashboardPolling(channel)
    await fetchDashboardData(1)
    expect(statsData.value.visibilityLevel).toBeNull()
  })
})