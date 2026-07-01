import { computed, type Ref } from 'vue'
import type { StreamInfo } from './useStreamRegistry'
import { pathOnly } from '@/utils/streamUrl'

export interface ChannelItem {
  id: string
  name: string
}

export function useCurrentStream(
  channel: Ref<string>,
  channels: Ref<ChannelItem[]>,
  streamMap: Ref<Record<string, StreamInfo>>,
) {
  const currentDevice = computed(() => {
    return channels.value.find(ch => ch.id === channel.value) || null
  })

  const currentVideoUrl = computed(() => {
    if (!currentDevice.value) return ''
    return streamMap.value[currentDevice.value.id]?.url || ''
  })

  const currentSourceType = computed(() => {
    if (!currentDevice.value) return ''
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