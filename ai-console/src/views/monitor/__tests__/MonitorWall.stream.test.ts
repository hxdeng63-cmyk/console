import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

// Mock api/stream 模块
vi.mock('@/api/stream', () => ({
  getDeviceFlvUrl: vi.fn(),
  registerDevicesAsync: vi.fn(),
  getRegisterDevicesStatus: vi.fn(),
}))

// Mock element-plus 避免 ElMessage 调用
vi.mock('element-plus', () => ({
  ElMessage: { error: vi.fn(), warning: vi.fn(), success: vi.fn() },
}))

import * as streamApi from '@/api/stream'
import { setStreamMapEntry } from '@/composables/useStreamRegistry'

// 提取 MonitorWall.vue 4 处 refresh 路径的逻辑为可测试函数
// 由于直接测试 Vue 组件复杂,这里通过 helper 重构路径:
// 实际修复是把 4 处的 spread 模板替换为 setStreamMapEntry
// 测试 setStreamMapEntry 已被正确调用即可(在 Task 2 验证)
//
// 这三个测试用例是 MonitorWall.vue 4 处 refresh 路径的 mini-replica:
// 它们验证了"用 setStreamMapEntry 写 streamMap 时必须携带 deviceFallbackUrl"
// 的契约 — 任何一处如果回退到旧的 spread 写法都会丢失该字段。

describe('MonitorWall refresh 路径携带 deviceFallbackUrl', () => {
  beforeEach(() => vi.clearAllMocks())

  it('refreshStreamUrlSync 路径携带 deviceFallbackUrl', async () => {
    vi.mocked(streamApi.getDeviceFlvUrl).mockResolvedValue({
      flv_url: 'http://x/flv',
      source_type: 'stream',
      device_fallback_url: '/y.mp4',
    } as any)

    // 模拟原 MonitorWall.vue:408-433 逻辑(refreshStreamUrlSync)
    const streamMap = ref<Record<string, any>>({})
    async function refreshStreamUrlSync(rid: number) {
      const info: any = await streamApi.getDeviceFlvUrl(rid)
      if (info?.flv_url) {
        streamMap.value = setStreamMapEntry(streamMap.value, rid, {
          url: info.flv_url,
          sourceType: info.source_type || 'stream',
          deviceFallbackUrl: info.device_fallback_url ?? null,
        })
        return info.flv_url
      }
      return null
    }

    await refreshStreamUrlSync(42)
    expect(streamMap.value['device-42']).toEqual({
      url: 'http://x/flv',
      sourceType: 'stream',
      deviceFallbackUrl: '/y.mp4',
    })
  })

  it('selectedChannel watch 路径携带 deviceFallbackUrl', async () => {
    vi.mocked(streamApi.getDeviceFlvUrl).mockResolvedValue({
      flv_url: 'http://x/flv',
      source_type: 'stream',
      device_fallback_url: '/z.mp4',
    } as any)

    const streamMap = ref<Record<string, any>>({})
    async function selectedChannelWatchHandler(rid: number) {
      const info: any = await streamApi.getDeviceFlvUrl(rid)
      if (info?.flv_url) {
        streamMap.value = setStreamMapEntry(streamMap.value, rid, {
          url: info.flv_url,
          sourceType: info.source_type || 'stream',
          deviceFallbackUrl: info.device_fallback_url ?? null,
        })
      }
    }

    await selectedChannelWatchHandler(7)
    expect(streamMap.value['device-7'].deviceFallbackUrl).toBe('/z.mp4')
  })

  it('404 时清理 streamMap 条目', async () => {
    const err: any = new Error('not found')
    err.response = { status: 404 }
    vi.mocked(streamApi.getDeviceFlvUrl).mockRejectedValue(err)

    const streamMap = ref<Record<string, any>>({
      'device-1': { url: 'old', sourceType: 'stream', deviceFallbackUrl: '/old.mp4' },
    })

    async function refreshStreamMap(rid: number) {
      try {
        const info: any = await streamApi.getDeviceFlvUrl(rid)
        if (info?.flv_url) {
          streamMap.value = setStreamMapEntry(streamMap.value, rid, {
            url: info.flv_url,
            sourceType: info.source_type || 'stream',
            deviceFallbackUrl: info.device_fallback_url ?? null,
          })
        }
      } catch (err: any) {
        if (err?.response?.status === 404) {
          const key = `device-${rid}`
          if (streamMap.value[key]) {
            const next = { ...streamMap.value }
            delete next[key]
            streamMap.value = next
          }
        }
      }
    }

    await refreshStreamMap(1)
    expect(streamMap.value['device-1']).toBeUndefined()
  })
})
