import { ref, type Ref } from 'vue'
import { registerDevicesAsync, getRegisterDevicesStatus } from '@/api/stream'
import { withCacheBuster } from '@/utils/streamUrl'

export interface StreamInfo {
  url: string
  sourceType: string
  /** 本地 fallback mp4 路径(HLS 失败时用); null = 后端未返; undefined = 未传。 */
  deviceFallbackUrl?: string | null
}

const POLL_INTERVAL_MS = 2000

// 私有/导出: 统一 streamMap 写入,强制 deviceFallbackUrl 字段,消除 5 处复制粘贴。
// 允许 null(显式"后端未返"),不允许 undefined(避免漏传蔓延)。
export function setStreamMapEntry(
  prev: Record<string, StreamInfo>,
  deviceId: string | number,
  info: { url: string; sourceType?: string; deviceFallbackUrl?: string | null },
): Record<string, StreamInfo> {
  const prefixedId = `device-${deviceId}`
  return {
    ...prev,
    [prefixedId]: {
      url: info.url,
      sourceType: info.sourceType || 'stream',
      deviceFallbackUrl: info.deviceFallbackUrl ?? null,
    },
  }
}

export function useStreamRegistry() {
  const streamMap = ref<Record<string, StreamInfo>>({})
  const streamRegistering = ref(false)
  const streamLoading = ref(false)
  const streamError = ref<string | null>(null)
  const pendingRawIds = ref<Set<string>>(new Set())
  const pollTimer = ref<number | null>(null)

  function clearPoll() {
    if (pollTimer.value !== null) {
      clearInterval(pollTimer.value)
      pollTimer.value = null
    }
  }

  function flushPending() {
    if (pendingRawIds.value.size === 0) return
    if (streamRegistering.value) return
    const [nextId] = pendingRawIds.value
    if (!nextId) return
    pendingRawIds.value.delete(nextId)
    void registerDeviceStream(nextId)
  }

  function startPoll(taskId: string, onCompleted: (status: any) => void) {
    clearPoll()
    pollTimer.value = window.setInterval(async () => {
      try {
        const status: any = await getRegisterDevicesStatus(taskId)
        if (status.status === 'completed' || status.status === 'failed') {
          clearPoll()
          streamRegistering.value = false
          streamLoading.value = false
          if (status.status === 'completed') {
            onCompleted(status)
          } else {
            streamError.value = `注册失败:${status.error || status.status}`
          }
          flushPending()
        }
      } catch (err: any) {
        clearPoll()
        streamRegistering.value = false
        streamLoading.value = false
        streamError.value = err?.message ? `轮询异常:${err.message}` : '轮询异常'
        flushPending()
      }
    }, POLL_INTERVAL_MS)
  }

  async function registerDeviceStream(rawId: string) {
    return _registerDeviceStreamForTest(rawId, {
      streamMap,
      streamRegistering,
      streamLoading,
      streamError,
      pendingRawIds,
      clearPoll,
      startPoll,
      flushPending,
    })
  }

  async function registerDeviceStreams(rawIds: string[]) {
    if (rawIds.length === 0 || streamRegistering.value) return
    streamRegistering.value = true
    streamLoading.value = true
    streamError.value = null
    try {
      const { task_id }: any = await registerDevicesAsync(rawIds)
      if (!task_id) throw new Error('未返回任务 ID')
      startPoll(task_id, (status: any) => {
        const results = status.results || []
        let next = streamMap.value
        results.forEach((item: any) => {
          if (!item.success) return
          next = setStreamMapEntry(next, item.device_id, {
            url: withCacheBuster(item.flv_url, item.source_type || ''),
            sourceType: item.source_type || '',
            deviceFallbackUrl: item.device_fallback_url ?? null,
          })
        })
        streamMap.value = next
      })
    } catch (err: any) {
      streamRegistering.value = false
      streamLoading.value = false
      streamError.value = err?.message ? `批量注册失败:${err.message}` : '批量注册失败'
      flushPending()
    }
  }

  function dispose() {
    clearPoll()
  }

  return {
    streamMap,
    streamRegistering,
    streamLoading,
    streamError,
    registerDeviceStream,
    registerDeviceStreams,
    dispose,
  }
}

// 测试 helper: 接受外部 ref,便于直接调用 registerDeviceStream 逻辑
export async function _registerDeviceStreamForTest(
  rawId: string,
  stateRefs: {
    streamMap: Ref<Record<string, StreamInfo>>
    streamRegistering: Ref<boolean>
    streamLoading: Ref<boolean>
    streamError: Ref<string | null>
    pendingRawIds: Ref<Set<string>>
    clearPoll: () => void
    startPoll: (taskId: string, cb: (s: any) => void) => void
    flushPending: () => void
  },
) {
  if (!rawId) return
  if (stateRefs.streamRegistering.value) {
    stateRefs.pendingRawIds.value.add(rawId)
    return
  }
  stateRefs.streamRegistering.value = true
  stateRefs.streamLoading.value = true
  stateRefs.streamError.value = null
  try {
    const { task_id }: any = await registerDevicesAsync([rawId])
    if (!task_id) throw new Error('未返回任务 ID')
    stateRefs.startPoll(task_id, (status: any) => {
      const item = (status.results || []).find((r: any) => String(r.device_id) === rawId)
      if (!item || !item.success) {
        stateRefs.streamError.value = item?.error
          ? `设备流注册失败:${item.error}`
          : '设备流注册失败'
        return
      }
      const sourceType = item.source_type || ''
      stateRefs.streamMap.value = setStreamMapEntry(stateRefs.streamMap.value, item.device_id, {
        url: withCacheBuster(item.flv_url, sourceType),
        sourceType,
        deviceFallbackUrl: item.device_fallback_url ?? null,
      })
    })
  } catch (err: any) {
    stateRefs.streamRegistering.value = false
    stateRefs.streamLoading.value = false
    stateRefs.streamError.value = err?.message ? `设备流注册失败:${err.message}` : '设备流注册失败'
    stateRefs.flushPending()
  }
}