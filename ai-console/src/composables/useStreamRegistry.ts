import { ref } from 'vue'
import { registerDevicesAsync, getRegisterDevicesStatus } from '@/api/stream'
import { withCacheBuster } from '@/utils/streamUrl'

export interface StreamInfo {
  url: string
  sourceType: string
  /** 本地 fallback mp4 路径(HLS 失败时用); backend 从 DB device.name 构造,
   * 不依赖 symlink, 跨机器可移植 */
  deviceFallbackUrl?: string
}

const POLL_INTERVAL_MS = 2000

export function useStreamRegistry() {
  const streamMap = ref<Record<string, StreamInfo>>({})
  const streamRegistering = ref(false)
  const streamLoading = ref(false)
  const streamError = ref(false)
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
            streamError.value = true
          }
          flushPending()
        }
      } catch {
        clearPoll()
        streamRegistering.value = false
        streamLoading.value = false
        streamError.value = true
        flushPending()
      }
    }, POLL_INTERVAL_MS)
  }

  async function registerDeviceStream(rawId: string) {
    if (!rawId) return
    if (streamRegistering.value) {
      pendingRawIds.value.add(rawId)
      return
    }
    streamRegistering.value = true
    streamLoading.value = true
    streamError.value = false
    try {
      const { task_id }: any = await registerDevicesAsync([rawId])
      if (!task_id) throw new Error('未返回任务 ID')
      startPoll(task_id, (status: any) => {
        const item = (status.results || []).find((r: any) => String(r.device_id) === rawId)
        if (!item || !item.success) {
          streamError.value = true
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
    } catch {
      streamRegistering.value = false
      streamLoading.value = false
      streamError.value = true
      flushPending()
    }
  }

  async function registerDeviceStreams(rawIds: string[]) {
    if (rawIds.length === 0 || streamRegistering.value) return
    streamRegistering.value = true
    streamLoading.value = true
    streamError.value = false
    try {
      const { task_id }: any = await registerDevicesAsync(rawIds)
      if (!task_id) throw new Error('未返回任务 ID')
      startPoll(task_id, (status: any) => {
        const results = status.results || []
        const newMap: Record<string, StreamInfo> = {}
        results.forEach((item: any) => {
          const prefixedId = `device-${item.device_id}`
          if (item.success) {
            newMap[prefixedId] = {
              url: withCacheBuster(item.flv_url, item.source_type || ''),
              sourceType: item.source_type || '',
              deviceFallbackUrl: item.device_fallback_url || undefined,
            }
          }
        })
        streamMap.value = newMap
      })
    } catch {
      streamRegistering.value = false
      streamLoading.value = false
      streamError.value = true
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