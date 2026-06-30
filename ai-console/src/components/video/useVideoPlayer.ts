import { ref, onMounted, onUnmounted, computed } from 'vue'
import flvjs from 'flv.js'
import Hls from 'hls.js'

export type Protocol = 'flv' | 'hls'

export interface UseVideoPlayerOptions {
  url: string
  protocol: Protocol
  enableDualProtocol?: boolean
  autoStart?: boolean
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
      enableWorker: true,
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
        manifestLoadingRetryDelay: 1000,
        levelLoadingRetryDelay: 1000,
        fragLoadingRetryDelay: 1000,
        manifestLoadingMaxRetry: 10,
        levelLoadingMaxRetry: 10,
        fragLoadingMaxRetry: 10,
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
            hlsInstance?.startLoad()
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
  }
}
