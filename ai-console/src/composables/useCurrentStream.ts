import { computed, type Ref } from 'vue'
import type { StreamInfo } from './useStreamRegistry'
import { pathOnly } from '@/utils/streamUrl'

export interface ChannelItem {
  id: string
  name: string
}

function rawIdFromChannel(id: string): number {
  if (!id) return 0
  const n = Number(id.replace(/^device-/, ''))
  return Number.isNaN(n) ? 0 : n
}

export function useCurrentStream(
  channel: Ref<string>,
  channels: Ref<ChannelItem[]>,
  streamMap: Ref<Record<string, StreamInfo>>,
  selectedAlgorithm?: Ref<string>,
) {
  const currentDevice = computed(() => {
    return channels.value.find(ch => ch.id === channel.value) || null
  })

  // 有算法 → traffic-api 推理后 m3u8（HLS，带 bbox）；无算法 → 走 backend stream API 返的
  // device_fallback_url (用 device.name 构造, e.g. /data/monitoring/西区-设备1.mp4)
  const hasAlgorithm = computed(() => Boolean(selectedAlgorithm?.value))

  const currentVideoUrl = computed(() => {
    if (!currentDevice.value) return ''
    if (!hasAlgorithm.value) {
      const fallback = streamMap.value[currentDevice.value.id]?.deviceFallbackUrl
      if (fallback) return fallback
      // 兜底: backend API 没返 fallback_url 时, 用空字符串 (前端渲染占位)
      // 旧硬编码 /data/monitoring/device_${rid}.mp4 已删 (物理文件不存在)
      return ''
    }
    return streamMap.value[currentDevice.value.id]?.url || ''
  })

  const currentSourceType = computed(() => {
    if (!currentDevice.value) return ''
    if (!hasAlgorithm.value) return 'local'
    return streamMap.value[currentDevice.value.id]?.sourceType || ''
  })

  const currentProtocol = computed(() => {
    const url = currentVideoUrl.value
    if (!url) return 'flv'
    return pathOnly(url).toLowerCase().endsWith('.m3u8') ? 'hls' : 'flv'
  })

  return {
    currentDevice,
    currentVideoUrl,
    currentSourceType,
    currentProtocol,
  }
}