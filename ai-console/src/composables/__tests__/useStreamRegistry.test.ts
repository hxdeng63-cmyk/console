import { describe, it, expect, vi } from 'vitest'
import { ref } from 'vue'
import { setStreamMapEntry, _registerDeviceStreamForTest } from '../useStreamRegistry'
import * as streamApi from '@/api/stream'

vi.mock('@/api/stream', () => ({
  registerDevicesAsync: vi.fn(),
  getRegisterDevicesStatus: vi.fn(),
}))

describe('registerDeviceStream (单条)', () => {
  it('写入 streamMap 时携带 deviceFallbackUrl', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't1' } as any)

    const streamMap = ref<Record<string, any>>({})
    const streamRegistering = ref(false)
    const streamLoading = ref(false)
    const streamError = ref(false)
    const pendingRawIds = ref<Set<string>>(new Set())
    let pollCb: any = null
    const startPoll = (_id: string, cb: any) => { pollCb = cb }
    const clearPoll = () => {}
    const flushPending = () => {}

    await _registerDeviceStreamForTest('42', {
      streamMap,
      streamRegistering,
      streamLoading,
      streamError,
      pendingRawIds,
      clearPoll,
      startPoll,
      flushPending,
    })
    expect(pollCb).toBeTruthy()
    pollCb!({
      results: [
        {
          device_id: 42,
          success: true,
          flv_url: 'http://x/flv',
          source_type: 'stream',
          device_fallback_url: '/x.mp4',
        },
      ],
    })
    expect(streamMap.value['device-42']).toMatchObject({
      url: expect.stringMatching(/^http:\/\/x\/flv\?_t=\d+$/),
      sourceType: 'stream',
      deviceFallbackUrl: '/x.mp4',
    })
  })

  it('device_fallback_url 缺失时写入 null', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't1' } as any)

    const streamMap = ref<Record<string, any>>({})
    const streamRegistering = ref(false)
    const streamLoading = ref(false)
    const streamError = ref(false)
    const pendingRawIds = ref<Set<string>>(new Set())
    let pollCb: any = null
    const startPoll = (_id: string, cb: any) => { pollCb = cb }
    const clearPoll = () => {}
    const flushPending = () => {}

    await _registerDeviceStreamForTest('1', {
      streamMap,
      streamRegistering,
      streamLoading,
      streamError,
      pendingRawIds,
      clearPoll,
      startPoll,
      flushPending,
    })
    pollCb!({
      results: [
        { device_id: 1, success: true, flv_url: 'http://x/flv', source_type: 'stream' },
      ],
    })
    expect(streamMap.value['device-1'].deviceFallbackUrl).toBeNull()
  })
})

describe('setStreamMapEntry', () => {
  it('writes entry with url + sourceType', () => {
    const result = setStreamMapEntry({}, 42, { url: 'http://x/flv', sourceType: 'stream' })
    expect(result['device-42']).toEqual({
      url: 'http://x/flv',
      sourceType: 'stream',
      deviceFallbackUrl: null,
    })
  })

  it('preserves other entries', () => {
    const prev = {
      'device-1': { url: 'a', sourceType: 'stream', deviceFallbackUrl: '/a.mp4' },
    }
    const result = setStreamMapEntry(prev, 2, { url: 'b', sourceType: 'stream', deviceFallbackUrl: '/b.mp4' })
    expect(result['device-1']).toEqual({ url: 'a', sourceType: 'stream', deviceFallbackUrl: '/a.mp4' })
    expect(result['device-2']).toEqual({ url: 'b', sourceType: 'stream', deviceFallbackUrl: '/b.mp4' })
  })

  it('overwrites same device-id', () => {
    const prev = { 'device-1': { url: 'old', sourceType: 'stream', deviceFallbackUrl: '/old.mp4' } }
    const result = setStreamMapEntry(prev, 1, { url: 'new', sourceType: 'local', deviceFallbackUrl: '/new.mp4' })
    expect(result['device-1'].url).toBe('new')
    expect(result['device-1'].sourceType).toBe('local')
    expect(result['device-1'].deviceFallbackUrl).toBe('/new.mp4')
  })

  it('normalizes undefined deviceFallbackUrl to null', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream' })
    expect(result['device-1'].deviceFallbackUrl).toBeNull()
  })

  it('preserves null deviceFallbackUrl explicitly', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream', deviceFallbackUrl: null })
    expect(result['device-1'].deviceFallbackUrl).toBeNull()
  })

  it('preserves non-null deviceFallbackUrl', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream', deviceFallbackUrl: '/x.mp4' })
    expect(result['device-1'].deviceFallbackUrl).toBe('/x.mp4')
  })

  it('accepts string deviceId', () => {
    const result = setStreamMapEntry({}, '99', { url: 'a', sourceType: 'stream' })
    expect(result['device-99']).toBeDefined()
  })
})
