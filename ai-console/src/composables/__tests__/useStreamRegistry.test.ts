import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { setStreamMapEntry, _registerDeviceStreamForTest, useStreamRegistry } from '../useStreamRegistry'
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
    const streamError = ref<string | null>(null)
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
    const streamError = ref<string | null>(null)
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

describe('registerDeviceStreams (批量)', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('批量路径: 写入多条 streamMap 条目,保留前置条目,deviceFallbackUrl 归一为 null / 字符串', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't-batch-1' } as any)
    vi.mocked(streamApi.getRegisterDevicesStatus).mockResolvedValue({
      status: 'completed',
      results: [
        { device_id: 11, success: true, flv_url: 'http://x/a.flv', source_type: 'stream', device_fallback_url: '/a.mp4' },
        { device_id: 22, success: true, flv_url: 'http://x/b.flv', source_type: 'local' },
        { device_id: 33, success: true, flv_url: 'http://x/c.flv', source_type: 'stream', device_fallback_url: null },
      ],
    } as any)

    const { streamMap, registerDeviceStreams } = useStreamRegistry()
    // 预置一条,验证批量完成后仍保留
    streamMap.value['device-99'] = { url: 'pre', sourceType: 'stream', deviceFallbackUrl: '/pre.mp4' }

    await registerDeviceStreams(['11', '22', '33'])
    // 触发 setInterval(2s) 一次 → 进入 onCompleted → 写 streamMap
    await vi.advanceTimersByTimeAsync(2100)

    // 后端给了 device_fallback_url → 字符串保留
    expect(streamMap.value['device-11']).toMatchObject({
      sourceType: 'stream',
      deviceFallbackUrl: '/a.mp4',
    })
    // 后端未给 device_fallback_url → 归一为 null(不允许 undefined)
    expect(streamMap.value['device-22'].deviceFallbackUrl).toBeNull()
    expect(streamMap.value['device-33'].deviceFallbackUrl).toBeNull()
    // 前置条目不被批量注册覆盖
    expect(streamMap.value['device-99']).toMatchObject({ url: 'pre', deviceFallbackUrl: '/pre.mp4' })
  })
})

describe('streamError 错误码字符串', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('useStreamRegistry 默认 streamError 为字符串类型(null)', () => {
    const { streamError } = useStreamRegistry()
    // 类型从 boolean 改为 string | null,默认 null
    expect(streamError.value).toBeNull()
  })

  it('批量注册 poll 失败时,streamError 应被设置为错误消息字符串(非 false)', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't-err' } as any)
    vi.mocked(streamApi.getRegisterDevicesStatus).mockResolvedValue({
      status: 'failed',
      results: [],
    } as any)

    const { streamError, registerDeviceStreams } = useStreamRegistry()
    await registerDeviceStreams(['1'])
    await vi.advanceTimersByTimeAsync(2100)

    // 类型为 string | null;失败时必须是 truthy 字符串(包含错误码或关键字)
    expect(typeof streamError.value).toBe('string')
    expect(streamError.value).not.toBe('')
  })

  it('批量注册 poll 抛错时,streamError 也应被设置为字符串', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't-throw' } as any)
    vi.mocked(streamApi.getRegisterDevicesStatus).mockRejectedValue(new Error('500 server error'))

    const { streamError, registerDeviceStreams } = useStreamRegistry()
    await registerDeviceStreams(['1'])
    await vi.advanceTimersByTimeAsync(2100)

    expect(typeof streamError.value).toBe('string')
    expect(streamError.value).not.toBe('')
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
