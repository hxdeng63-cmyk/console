import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { ref } from 'vue'
import VideoStage from '../VideoStage.vue'

// Mock useVideoPlayer composable — VideoStage may consume its exports
// (hasError / errorMessage / currentProtocol / retry) when wired up.
vi.mock('@/components/video/useVideoPlayer', () => ({
  useVideoPlayer: () => ({
    videoRef: ref(null),
    canvasRef: ref(null),
    isLoading: ref(false),
    hasError: ref(true),
    errorMessage: ref('HTTP 403: Invalid stream token'),
    currentProtocol: ref('hls'),
    isFullscreen: ref(false),
    bandwidth: ref(0),
    retry: vi.fn(),
  }),
}))

describe('VideoStage', () => {
  it('有错误时显示错误码 + 重试按钮', () => {
    const wrapper = mount(VideoStage, {
      props: {
        device: null,
        videoUrl: 'http://x/flv',
        sourceType: 'stream',
        protocol: 'hls',
        loading: false,
        error: 'HTTP 403: Invalid stream token',
        refreshStreamUrl: vi.fn(),
        fallbackUrl: '',
        realtimeEvent: ref(null),
      },
    })
    expect(wrapper.text()).toContain('403')
    expect(wrapper.find('[data-test="retry-btn"]').exists()).toBe(true)
  })

  it('无错误时显示状态灯', async () => {
    // 使用 vi.doMock 工厂替换 useVideoPlayer 返回值
    vi.doMock('@/components/video/useVideoPlayer', () => ({
      useVideoPlayer: () => ({
        videoRef: ref(null),
        canvasRef: ref(null),
        isLoading: ref(false),
        hasError: ref(false),
        errorMessage: ref(''),
        currentProtocol: ref('hls'),
        isFullscreen: ref(false),
        bandwidth: ref(0),
        retry: vi.fn(),
      }),
    }))
    const { mount: mount2 } = await import('@vue/test-utils')
    const VideoStage2 = (await import('../VideoStage.vue')).default
    const wrapper = mount2(VideoStage2, {
      props: {
        device: null,
        videoUrl: 'http://x/flv',
        sourceType: 'stream',
        protocol: 'hls',
        loading: false,
        error: '',
        refreshStreamUrl: vi.fn(),
        fallbackUrl: '',
        realtimeEvent: ref(null),
      },
    })
    expect(wrapper.find('[data-test="status-light"]').exists()).toBe(true)
  })

  it('loading 时显示"正在加载" + 协议文字', () => {
    const wrapper = mount(VideoStage, {
      props: {
        device: null,
        videoUrl: '',
        sourceType: 'stream',
        protocol: 'flv',
        loading: true,
        error: '',
        refreshStreamUrl: vi.fn(),
        fallbackUrl: '',
        realtimeEvent: ref(null),
      },
    })
    expect(wrapper.text()).toContain('正在加载')
    expect(wrapper.text()).toContain('FLV')
  })

  it('device=null + 无错误 + 无 loading 时,状态灯应显示 idle (灰色),而非 online', () => {
    // 不再使用 vi.doMock — 直接 mount,默认 useVideoPlayer.hasError=true;
    // 我们只关心状态灯和 placeholder 文字,不进入 useVideoPlayer 分支。
    const wrapper = mount(VideoStage, {
      props: {
        device: null,
        videoUrl: 'http://x/flv',
        sourceType: 'stream',
        protocol: 'hls',
        loading: false,
        error: '',
        refreshStreamUrl: vi.fn(),
        fallbackUrl: '',
        realtimeEvent: ref(null),
      },
    })
    const light = wrapper.find('[data-test="status-light"]')
    expect(light.exists()).toBe(true)
    // 状态灯不应呈现 green online
    expect(light.classes()).not.toContain('online')
    // 应当有 idle(灰色)类
    expect(light.classes()).toContain('idle')
    // 同时 placeholder 应显示"等待选择设备..."
    expect(wrapper.text()).toContain('等待选择设备')
  })
})