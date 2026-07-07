import { ref, onMounted, onUnmounted, computed, watch, type Ref } from 'vue'
import flvjs from 'flv.js'
import Hls from 'hls.js'

export type Protocol = 'flv' | 'hls'

// HLS fatal NETWORK_ERROR 时调用。返回新的 m3u8 url 给 hls.js 重新加载。
// 用于处理 traffic-api 的 stream token 失效(403) 或设备未注册(404) 这两类场景。
// 返回 null 表示无可用 url,player 进入 hasError 状态让 VideoStage 显示"无法连接"。
export type RefreshStreamUrl = () => Promise<string | null>

// bbox 元素 — 来自 traffic-api callback（API_SERVICE(5).md L691-704）
// label/score/frame_num/track_id 都可能缺失(track_id 仅跟踪对象有)。
export interface BboxItem {
  label: string
  x: number
  y: number
  w: number
  h: number
  score?: number
  frame_num?: number
  track_id?: number
}

export interface UseVideoPlayerOptions {
  url: string
  protocol: Protocol
  enableDualProtocol?: boolean
  autoStart?: boolean
  onHlsNetworkError?: RefreshStreamUrl
  // 可选：拉新 url 失败时,提供一个本地 MP4 兜底 URL (由 backend 返的 device_fallback_url 传入,
  //       实际形如 /data/monitoring/<device.name>.mp4)
  fallbackUrl?: string
  // 可选：实时事件 ref,触发 bbox 绘制
  realtimeEvent?: Ref<{ event_detail?: Record<string, any> | null } | null>
}

// 不同类别用不同颜色
const BBOX_COLORS: Record<string, string> = {
  car: '#00FF66',
  truck: '#FFAA00',
  bus: '#FF66FF',
  motorcycle: '#00CCFF',
  pedestrian: '#FF3366',
  person_with_vest: '#FFE600',
  vehicle: '#00FF66',
  two_wheeler: '#00CCFF',
}

const BBOX_DEFAULT_COLOR = '#00FF66'

function extractBboxes(eventDetail: Record<string, any> | null | undefined): BboxItem[] {
  if (!eventDetail) return []
  const out: BboxItem[] = []
  const keys = ['jam', 'anomaly', 'flow', 'reverse', 'pedestrian', 'accident', 'parking_violation', 'vest']
  for (const k of keys) {
    const arr = eventDetail[k]?.bbox
    if (Array.isArray(arr)) {
      for (const item of arr) {
        if (
          item &&
          typeof item.x === 'number' &&
          typeof item.y === 'number' &&
          typeof item.w === 'number' &&
          typeof item.h === 'number'
        ) {
          out.push({
            label: String(item.label || 'object'),
            x: item.x,
            y: item.y,
            w: item.w,
            h: item.h,
            score: typeof item.score === 'number' ? item.score : undefined,
            frame_num: typeof item.frame_num === 'number' ? item.frame_num : undefined,
            track_id: typeof item.track_id === 'number' ? item.track_id : undefined,
          })
        }
      }
    }
  }
  return out
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
  let hlsErrorCount = 0
  let currentRealtimeEvent: Ref<{ event_detail?: Record<string, any> | null } | null> | null = null

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
        lowLatencyMode: true,
        // 给 traffic-api 启动慢一点缓冲,避免冷启时被误判为 fatal。
        // 失败 3 次后才走 fatal NETWORK_ERROR → refresh,避免单次抖动就拉新 url。
        manifestLoadingRetryDelay: 1000,
        levelLoadingRetryDelay: 1000,
        fragLoadingRetryDelay: 1000,
        manifestLoadingMaxRetry: 3,
        levelLoadingMaxRetry: 3,
        fragLoadingMaxRetry: 3,
        maxBufferLength: 6,
        maxMaxBufferLength: 10,
        liveSyncDurationCount: 3,
        initialLiveManifestSize: 2,
        // LL-HLS 配置
        backBufferLength: 0,
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
            hlsErrorCount += 1
            const refresh = options.onHlsNetworkError
            if (hlsInstance) {
              try {
                hlsInstance.stopLoad()
                hlsInstance.destroy()
              } catch { /* ignore */ }
              hlsInstance = null
            }
            if (refresh) {
              void refresh().then((newUrl) => {
                if (newUrl) {
                  hlsErrorCount = 0
                  initHls(newUrl)
                } else {
                  // 拉新 url 失败 —— 计数,3 次后切到本地兜底
                  if (hlsErrorCount >= 3 && options.fallbackUrl) {
                    console.warn('HLS refresh failed 3 times, falling back to local MP4')
                    currentProtocol.value = 'flv'
                    initNativeFallback(options.fallbackUrl)
                  } else {
                    console.error('HLS fatal NETWORK_ERROR: no refresh url available', data)
                    hasError.value = true
                    errorMessage.value = '无法连接到视频流服务器'
                    isLoading.value = false
                  }
                }
              })
            } else {
              // 没有 refresh 回调：尝试 hls.js 自带恢复（startLoad）。
              // hlsInstance 可能已在上面被置 null,这里用类型断言避免 TS 收紧到 never。
              ;(hlsInstance as any)?.startLoad?.()
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

  // HLS 多次失败后,直接用 <video src=mp4> 播放本地素材,作为最后兜底。
  // 不走 flvjs/hlsjs,因为本地文件浏览器原生支持最好。
  function initNativeFallback(url: string) {
    if (hlsInstance) {
      try {
        hlsInstance.destroy()
      } catch { /* ignore */ }
      hlsInstance = null
    }
    if (flvPlayer) {
      try {
        flvPlayer.destroy()
      } catch { /* ignore */ }
      flvPlayer = null
    }
    if (!videoRef.value) return
    setUrl(url)
    videoRef.value.src = url
    videoRef.value.load()
    videoRef.value.play().catch(() => {
      // Auto-play may be blocked
    })
    isLoading.value = false
    hasError.value = false
    errorMessage.value = ''
  }

  function start() {
    loadMedia()
  }

  // 绘制 bbox 到 canvas —— 由 realtimeEvent watcher 触发。
  // 每次新事件到达时全量重画(不增量),因为 HLS 帧可能跳变,全量重画最简单可靠。
  function drawBboxes(bboxes: BboxItem[]) {
    if (!canvasRef.value) return
    const canvas = canvasRef.value
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const W = canvas.width
    const H = canvas.height
    if (W === 0 || H === 0) return
    ctx.clearRect(0, 0, W, H)
    for (const b of bboxes) {
      // 防御性范围检查
      if (b.x < 0 || b.y < 0 || b.w <= 0 || b.h <= 0) continue
      if (b.x + b.w > 1.001 || b.y + b.h > 1.001) continue
      const color = BBOX_COLORS[b.label] || BBOX_DEFAULT_COLOR
      const x = b.x * W
      const y = b.y * H
      const w = b.w * W
      const h = b.h * H
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.strokeRect(x, y, w, h)
      // label 背景条
      const label = `${b.label}${typeof b.score === 'number' ? ` ${(b.score * 100).toFixed(0)}%` : ''}`
      ctx.font = '12px sans-serif'
      const textWidth = ctx.measureText(label).width + 8
      ctx.fillStyle = color
      ctx.fillRect(x, Math.max(0, y - 16), textWidth, 16)
      ctx.fillStyle = '#000'
      ctx.fillText(label, x + 4, Math.max(12, y - 4))
    }
  }

  function clearCanvas() {
    if (!canvasRef.value) return
    const ctx = canvasRef.value.getContext('2d')
    if (ctx) ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height)
  }

  // 父组件传入 realtimeEvent 时启用 watcher：每次新事件触发 bbox 重绘。
  // 不传则保持纯播放器,不引入对 useRealtimeSocket 的耦合。
  function setRealtimeEvent(ref: Ref<{ event_detail?: Record<string, any> | null } | null> | undefined) {
    if (currentRealtimeEvent) {
      currentRealtimeEvent = null
    }
    if (ref) {
      currentRealtimeEvent = ref
      watch(
        ref,
        (event) => {
          if (!event) {
            clearCanvas()
            return
          }
          const bboxes = extractBboxes(event.event_detail)
          if (bboxes.length > 0) {
            drawBboxes(bboxes)
          } else {
            clearCanvas()
          }
        },
        { immediate: true }
      )
    }
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
    // WS-1 黑屏兜底
    initNativeFallback,
    // WS-3 bbox 渲染
    drawBboxes,
    clearCanvas,
    setRealtimeEvent,
  }
}
