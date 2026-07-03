import { ref, onMounted, onUnmounted, computed } from 'vue'
import flvjs from 'flv.js'
import Hls from 'hls.js'

export type Protocol = 'flv' | 'hls'

// HLS fatal NETWORK_ERROR 时调用。返回新的 m3u8 url 给 hls.js 重新加载。
// 用于处理 traffic-api 的 stream token 失效(403) 或设备未注册(404) 这两类场景。
// 返回 null 表示无可用 url,player 进入 hasError 状态让 VideoStage 显示"无法连接"。
export type RefreshStreamUrl = () => Promise<string | null>

export interface UseVideoPlayerOptions {
  url: string
  protocol: Protocol
  enableDualProtocol?: boolean
  autoStart?: boolean
  onHlsNetworkError?: RefreshStreamUrl
}

export function useVideoPlayer(options: UseVideoPlayerOptions) {
  const videoRef = ref<HTMLVideoElement | null>(null)
  const canvasRef = ref<HTMLCanvasElement | null>(null)
  const isLoading = ref(true)
  const hasError = ref(false)
  const errorMessage = ref('')
  const isFullscreen = ref(false)
  const bandwidth = ref(0)
  const osdText = ref('')
  const osdLocation = ref('')
  const currentProtocol = ref<Protocol>(options.protocol)
  const showProtocolToggle = ref(false)
  const currentUrl = ref(options.url)

  let flvPlayer: flvjs.Player | null = null
  let hlsInstance: Hls | null = null
  let bandwidthInterval: ReturnType<typeof setInterval> | null = null

  const dualProtocolSupported = computed(() => options.enableDualProtocol ?? false)

  function getFlvUrl() {
    if (currentProtocol.value === 'flv' && currentUrl.value) {
      return currentUrl.value
    }
    return currentUrl.value.replace(/\.(m3u8|mpd)/i, '.flv')
  }

  function getHlsUrl() {
    if (currentProtocol.value === 'hls' && currentUrl.value) {
      return currentUrl.value
    }
    return currentUrl.value.replace(/\.flv$/i, '.m3u8')
  }

  function setUrl(url: string) {
    currentUrl.value = url
  }

  function initFlv() {
    if (!videoRef.value || !flvjs.isSupported()) return

    if (flvPlayer) {
      flvPlayer.destroy()
    }

    const url = getFlvUrl()
    flvPlayer = flvjs.createPlayer({
      type: 'flv',
      url,
    }, {
      enableWorker: false,
      enableStashBuffer: false,
      stashInitialSize: 128,
    })

    flvPlayer.attachMediaElement(videoRef.value)
    flvPlayer.load()
    flvPlayer.play()

    flvPlayer.on(flvjs.Events.ERROR, (_err, errType) => {
      console.error('FLV error:', errType)
      hasError.value = true
      errorMessage.value = '无法连接到视频流服务器'
      isLoading.value = false
    })

    flvPlayer.on(flvjs.Events.STATISTICS_INFO, (info) => {
      if (info.speed) {
        bandwidth.value = info.speed
      }
    })
  }

  function initHls(urlOverride?: string) {
    if (!videoRef.value) return

    if (hlsInstance) {
      hlsInstance.destroy()
      hlsInstance = null
    }

    const url = urlOverride || getHlsUrl()

    if (Hls.isSupported()) {
      hlsInstance = new Hls({
        enableWorker: true,
        lowLatencyMode: false,
        // 降到 1 次重试:traffic-api stream token 失效时(403)如果一直 retry 同一个死 url,
        // 用户会看到 10 次 403 闪现(~10s 黑屏)才走到 fatal NETWORK_ERROR → refresh。
        // 失败立即放弃,让 fatal NETWORK_ERROR 回调尽快触发 onHlsNetworkError 拉新 url。
        manifestLoadingRetryDelay: 500,
        levelLoadingRetryDelay: 500,
        fragLoadingRetryDelay: 500,
        manifestLoadingMaxRetry: 1,
        levelLoadingMaxRetry: 1,
        fragLoadingMaxRetry: 1,
        maxBufferLength: 10,
        maxMaxBufferLength: 15,
        liveSyncDurationCount: 2,
        initialLiveManifestSize: 2,
        xhrSetup: (xhr, url) => {
          try {
            if (new URL(url, window.location.href).origin === window.location.origin) {
              xhr.withCredentials = true
            }
          } catch {
            // Unparseable URL: leave default credentials mode to avoid CORS issues
          }
        },
      })

      hlsInstance.loadSource(url)
      hlsInstance.attachMedia(videoRef.value)

      hlsInstance.on(Hls.Events.ERROR, (_event, data) => {
        if (data.fatal) {
          if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
            // 立刻 stopLoad + destroy 死 url 的 hlsInstance,避免它在 refresh 期间继续 retry。
            // 然后让父组件通过回调拉新 url,createNewHlsInstance() 整体重建 player。
            const refresh = options.onHlsNetworkError
            if (refresh) {
              if (hlsInstance) {
                try {
                  hlsInstance.stopLoad()
                  hlsInstance.destroy()
                } catch { /* ignore */ }
                hlsInstance = null
              }
              void refresh().then((newUrl) => {
                if (newUrl) {
                  initHls(newUrl)
                } else {
                  console.error('HLS fatal NETWORK_ERROR: no refresh url available', data)
                  hasError.value = true
                  errorMessage.value = '无法连接到视频流服务器'
                  isLoading.value = false
                }
              })
            } else {
              hlsInstance?.startLoad()
            }
          } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
            hlsInstance?.recoverMediaError()
          } else {
            console.error('HLS fatal error:', data)
            hasError.value = true
            errorMessage.value = '无法连接到视频流服务器'
            isLoading.value = false
          }
        }
      })

      hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
        videoRef.value?.play()
      })

      hlsInstance.on(Hls.Events.FRAG_LOADED, (_event, data) => {
        const loaded = (data as any).stats?.loaded ?? (data as any).loaded ?? 0
        const bitrate = data.frag.duration > 0 ? (loaded * 8) / data.frag.duration : 0
        if (bitrate > 0) {
          bandwidth.value = bitrate / 1024
        }
      })
    } else if (videoRef.value.canPlayType('application/vnd.apple.mpegurl')) {
      videoRef.value.src = url
      videoRef.value.play()
    }
  }

  function loadMedia() {
    setBandwidthDisplay(false)
    isLoading.value = true
    hasError.value = false
    errorMessage.value = ''

    if (currentProtocol.value === 'flv') {
      initFlv()
    } else {
      initHls()
    }

    isLoading.value = false
  }

  function start() {
    loadMedia()
  }

  function stopBackgroundActivity() {
    if (currentProtocol.value === 'hls' && hlsInstance) {
      if (typeof (hlsInstance as any).pauseBuffering === 'function') {
        ;(hlsInstance as any).pauseBuffering()
      }
    }
    if (videoRef.value) {
      videoRef.value.pause()
    }
  }

  function resumeBackgroundActivity() {
    resumeBuffering()
    if (currentProtocol.value === 'hls' && hlsInstance) {
      // 直播流 segment 轮换很快，后台 pause 后 level details 可能已过期；
      // 重新加载 manifest，让 hls.js 同步到当前直播边缘，避免请求已删除的旧 segment。
      if (typeof hlsInstance.loadSource === 'function') {
        hlsInstance.loadSource(getHlsUrl())
      }
    }
    if (videoRef.value) {
      videoRef.value.play().catch(() => {
        // Auto-play may be blocked; caller can retry manually
      })
    }
  }

  function switchUrl(url: string) {
    if (!url || !videoRef.value) return
    setBandwidthDisplay(false)
    setUrl(url)

    // 跳过直接视频文件（mp4/webm/ogg/mov）—— 这些应由原生 <video> 播放
    const isDirectVideo = /\.(mp4|webm|ogg|mov)(\?.*)?$/i.test(url)
    if (isDirectVideo) return

    if (currentProtocol.value === 'flv') {
      // flv.js 不支持 URL 切换，必须销毁重建
      if (flvPlayer) {
        flvPlayer.destroy()
        flvPlayer = null
      }
      initFlv()
    } else {
      // hls.js 支持 loadSource() 复用实例
      if (hlsInstance) {
        hlsInstance.loadSource(getHlsUrl())
      } else {
        initHls(getHlsUrl())
      }
    }
  }

  function pauseBuffering() {
    stopBackgroundActivity()
  }

  function resumeBuffering() {
    if (hlsInstance && currentProtocol.value === 'hls' && typeof (hlsInstance as any).resumeBuffering === 'function') {
      ;(hlsInstance as any).resumeBuffering()
    }
  }

  function toggleProtocol() {
    if (!dualProtocolSupported.value) return
    currentProtocol.value = currentProtocol.value === 'flv' ? 'hls' : 'flv'
    showProtocolToggle.value = true
    loadMedia()
  }

  function retry() {
    hasError.value = false
    loadMedia()
  }

  // 父组件 protocol prop 变化时同步内部 currentProtocol 并按新协议重建 player。
  // 之前 currentProtocol 只在初始化时从 options.protocol 取一次,父组件 protocol 切换
  // 不会被感知,导致 switchUrl 仍走旧协议分支(典型: flv → hls 时仍 initFlv 吃 .m3u8 → 黑屏)。
  function setProtocol(p: Protocol) {
    if (currentProtocol.value !== p) {
      currentProtocol.value = p
      loadMedia()
    }
  }

  function toggleFullscreen() {
    const container = videoRef.value?.parentElement
    if (!container) return

    if (!document.fullscreenElement) {
      container.requestFullscreen?.()
      isFullscreen.value = true
    } else {
      document.exitFullscreen?.()
      isFullscreen.value = false
    }
  }

  function updateOsd(text: string, location: string) {
    osdText.value = text
    osdLocation.value = location
  }

  function setBandwidthDisplay(enabled: boolean) {
    if (enabled) {
      bandwidthInterval = setInterval(() => {
        if (flvPlayer) {
          const stats = (flvPlayer as any).getStats?.()
          if (stats?.speed) {
            bandwidth.value = stats.speed
          }
        }
      }, 1000)
    } else if (bandwidthInterval) {
      clearInterval(bandwidthInterval)
      bandwidthInterval = null
    }
  }

  onMounted(() => {
    if (options.autoStart !== false) {
      loadMedia()
    }

    document.addEventListener('fullscreenchange', () => {
      isFullscreen.value = !!document.fullscreenElement
    })
  })

  onUnmounted(() => {
    flvPlayer?.destroy()
    hlsInstance?.destroy()
    if (bandwidthInterval) {
      clearInterval(bandwidthInterval)
    }
  })

  return {
    videoRef,
    canvasRef,
    isLoading,
    hasError,
    errorMessage,
    isFullscreen,
    bandwidth,
    osdText,
    osdLocation,
    currentProtocol,
    showProtocolToggle,
    dualProtocolSupported,
    toggleProtocol,
    retry,
    toggleFullscreen,
    updateOsd,
    setBandwidthDisplay,
    loadMedia,
    setUrl,
    switchUrl,
    pauseBuffering,
    resumeBuffering,
    start,
    stopBackgroundActivity,
    resumeBackgroundActivity,
    setProtocol,
  }
}
