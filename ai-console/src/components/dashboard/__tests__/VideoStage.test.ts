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
})