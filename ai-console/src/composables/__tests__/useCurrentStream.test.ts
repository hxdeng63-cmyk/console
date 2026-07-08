import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { useCurrentStream } from '../useCurrentStream'

function setup(channelId: string, fallback: string | null | undefined, hasAlgo: boolean) {
  const channel = ref(channelId)
  const channels = ref([{ id: channelId, name: 'dev' }])
  const streamMap = ref<Record<string, any>>({
    [channelId]: fallback === undefined ? { url: 'http://x/flv', sourceType: 'stream' }
                : { url: 'http://x/flv', sourceType: 'stream', deviceFallbackUrl: fallback },
  })
  const algorithm = ref(hasAlgo ? 'algo:1' : '')
  return useCurrentStream(channel, channels, streamMap, algorithm)
}

describe('useCurrentStream 6 象限', () => {
  it('hasAlgorithm=false + fallback=string -> 用 fallback', () => {
    const r = setup('device-1', '/x.mp4', false)
    expect(r.currentVideoUrl.value).toBe('/x.mp4')
    expect(r.currentSourceType.value).toBe('local')
  })

  it('hasAlgorithm=false + fallback=null -> 空串 + 占位', () => {
    const r = setup('device-1', null, false)
    expect(r.currentVideoUrl.value).toBe('')
    expect(r.currentSourceType.value).toBe('local')
  })

  it('hasAlgorithm=false + fallback=undefined(字段缺失) -> 空串', () => {
    const r = setup('device-1', undefined, false)
    expect(r.currentVideoUrl.value).toBe('')
  })

  it('hasAlgorithm=true + fallback=string -> 用 url (HLS)', () => {
    const r = setup('device-1', '/x.mp4', true)
    expect(r.currentVideoUrl.value).toBe('http://x/flv')
    expect(r.currentSourceType.value).toBe('stream')
  })

  it('hasAlgorithm=true + fallback=null -> 用 url (HLS 仍能播)', () => {
    const r = setup('device-1', null, true)
    expect(r.currentVideoUrl.value).toBe('http://x/flv')
  })

  it('hasAlgorithm=true + fallback=undefined -> 用 url', () => {
    const r = setup('device-1', undefined, true)
    expect(r.currentVideoUrl.value).toBe('http://x/flv')
  })

  it('currentProtocol 空 url 时回退 flv', () => {
    const r = setup('device-1', null, false)
    expect(r.currentVideoUrl.value).toBe('')
    expect(r.currentProtocol.value).toBe('flv')
  })

  it('currentProtocol m3u8 时识别 hls', () => {
    const channel = ref('device-1')
    const channels = ref([{ id: 'device-1', name: 'd' }])
    const streamMap = ref<Record<string, any>>({
      'device-1': { url: 'http://x/stream.m3u8', sourceType: 'stream' },
    })
    const r = useCurrentStream(channel, channels, streamMap, ref('algo'))
    expect(r.currentProtocol.value).toBe('hls')
  })

  it('currentProtocol flv 时识别 flv', () => {
    const channel = ref('device-1')
    const channels = ref([{ id: 'device-1', name: 'd' }])
    const streamMap = ref<Record<string, any>>({
      'device-1': { url: 'http://x/stream.flv', sourceType: 'stream' },
    })
    const r = useCurrentStream(channel, channels, streamMap, ref('algo'))
    expect(r.currentProtocol.value).toBe('flv')
  })
})
