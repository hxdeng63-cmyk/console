import { ref, onMounted, onUnmounted, computed } from 'vue'
import flvjs from 'flv.js'
import Hls from 'hls.js'

export type Protocol = 'flv' | 'hls'

export interface UseVideoPlayerOptions {
  url: string
  protocol: Protocol
  enableDualProtocol?: boolean
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
      errorMessage.value = 'FLV playback error'
      isLoading.value = false
    })

    flvPlayer.on(flvjs.Events.STATISTICS_INFO, (info) => {
      if (info.speed) {
        bandwidth.value = info.speed
      }
    })
  }

  function initHls() {
    if (!videoRef.value) return

    if (hlsInstance) {
      hlsInstance.destroy()
    }

    const url = getHlsUrl()

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
            errorMessage.value = 'HLS playback error'
            isLoading.value = false
          }
        }
      })

      hlsInstance.on(Hls.Events.MANIFEST_PARSED, () => {
        videoRef.value?.play()
      })

      hlsInstance.on(Hls.Events.FRAG_LOADED, (_event, data) => {
        const bitrate = data.frag.duration > 0 ? (data.loaded * 8) / data.frag.duration : 0
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
          const stats = flvPlayer.getStats()
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
    loadMedia()

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
  }
}
