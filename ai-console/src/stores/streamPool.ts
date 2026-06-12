import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface HlsDevice {
  id: string
  name: string
  url: string
  streamName?: string
  status: 'idle' | 'buffering' | 'ready' | 'error'
  retryCount: number
  lastAccessed: number
}

export interface StreamPoolState {
  hlsDevices: HlsDevice[]
  visibleDeviceId: string | null
  isReleasing: boolean
  releaseTimer: number | null
  enableHotPool: boolean
  hotPoolMaxSize: number
}

export interface PoolDevice {
  id: string
  name: string
  url: string
  sourceType: string
  streamName?: string
}

function isHlsDevice(device: PoolDevice): boolean {
  if (device.sourceType === 'stream') return true
  if (device.url && device.url.toLowerCase().endsWith('.m3u8')) return true
  return false
}

export const useStreamPoolStore = defineStore('streamPool', () => {
  // State
  const hlsDevices = ref<HlsDevice[]>([])
  const visibleDeviceId = ref<string | null>(null)
  const isReleasing = ref(false)
  const releaseTimer = ref<number | null>(null)
  const enableHotPool = ref(true)
  const hotPoolMaxSize = ref(10)

  // Getters
  const visibleDevice = computed<HlsDevice | null>(() => {
    if (!visibleDeviceId.value) return null
    return hlsDevices.value.find(d => d.id === visibleDeviceId.value) || null
  })

  const needsRelease = computed(() => isReleasing.value && releaseTimer.value !== null)

  // Actions
  function initPool(devices: PoolDevice[]) {
    // Filter to only HLS-capable devices
    const hlsList = devices.filter(isHlsDevice).map((device): HlsDevice => ({
      id: device.id,
      name: device.name,
      url: device.url,
      streamName: device.streamName,
      status: 'idle',
      retryCount: 0,
      lastAccessed: Date.now(),
    }))

    // Apply soft cap if exceeded using LRU eviction
    if (hlsList.length > hotPoolMaxSize.value) {
      const sorted = [...hlsList].sort((a, b) => b.lastAccessed - a.lastAccessed)
      console.warn(
        `[StreamPool] Device count (${hlsList.length}) exceeds hot pool max size (${hotPoolMaxSize.value}). ` +
        `LRU downgrade: only the most recently used ${hotPoolMaxSize.value} devices will be kept in the hot pool.`
      )
      hlsDevices.value = sorted.slice(0, hotPoolMaxSize.value)
    } else {
      hlsDevices.value = hlsList
    }

    visibleDeviceId.value = null
    isReleasing.value = false
    if (releaseTimer.value !== null) {
      window.clearTimeout(releaseTimer.value)
      releaseTimer.value = null
    }
  }

  function setVisible(deviceId: string | null) {
    visibleDeviceId.value = deviceId
    if (deviceId) {
      const device = hlsDevices.value.find(d => d.id === deviceId)
      if (device) {
        device.lastAccessed = Date.now()
      }
    }
  }

  function setDeviceStatus(deviceId: string, status: HlsDevice['status']) {
    const device = hlsDevices.value.find(d => d.id === deviceId)
    if (device) {
      device.status = status
    }
  }

  function scheduleRelease(delayMs: number) {
    isReleasing.value = true
    if (releaseTimer.value !== null) {
      window.clearTimeout(releaseTimer.value)
    }
    releaseTimer.value = window.setTimeout(() => {
      destroyPool()
    }, delayMs)
  }

  function cancelRelease() {
    if (releaseTimer.value !== null) {
      window.clearTimeout(releaseTimer.value)
      releaseTimer.value = null
    }
    isReleasing.value = false
  }

  function destroyPool() {
    hlsDevices.value = []
    visibleDeviceId.value = null
    isReleasing.value = false
    if (releaseTimer.value !== null) {
      window.clearTimeout(releaseTimer.value)
      releaseTimer.value = null
    }
  }

  function incrementRetry(deviceId: string) {
    const device = hlsDevices.value.find(d => d.id === deviceId)
    if (device) {
      device.retryCount += 1
    }
  }

  function resetRetry(deviceId: string) {
    const device = hlsDevices.value.find(d => d.id === deviceId)
    if (device) {
      device.retryCount = 0
    }
  }

  return {
    // State
    hlsDevices,
    visibleDeviceId,
    isReleasing,
    releaseTimer,
    enableHotPool,
    hotPoolMaxSize,
    // Getters
    visibleDevice,
    needsRelease,
    // Actions
    initPool,
    setVisible,
    setDeviceStatus,
    scheduleRelease,
    cancelRelease,
    destroyPool,
    incrementRetry,
    resetRetry,
  }
})
