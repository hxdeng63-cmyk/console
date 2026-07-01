import { ref, onUnmounted } from 'vue'
import { deploymentApi } from '@/api/deployment'

const POLL_STOP_MS = 1000
const MAX_STOP_ATTEMPTS = 30

export interface StopPollResult {
  /** 404/410/网络抖动超时 → resolved；其他 stopStatus 失败 → rejected */
  outcome: 'stopped' | 'gone' | 'timeout'
}

export function useStopPoll() {
  const stopping = ref(false)
  let timer: number | null = null
  let attempts = 0
  let currentResolve: ((r: StopPollResult) => void) | null = null

  function clearTimer() {
    if (timer !== null) {
      window.clearInterval(timer)
      timer = null
    }
  }

  function stop() {
    clearTimer()
    attempts = 0
    currentResolve = null
    stopping.value = false
  }

  function pollOnce(deploymentId: number, taskId: string) {
    attempts += 1
    void (async () => {
      try {
        const s: any = await deploymentApi.stopStatus(deploymentId, taskId)
        if (s.status === 'completed') {
          currentResolve?.({ outcome: 'stopped' })
          stop()
          return
        }
        if (s.status === 'failed') {
          currentResolve?.({ outcome: 'timeout' })
          stop()
          return
        }
      } catch {
        // 单次轮询失败继续，由 attempts 兜底
      }
      if (attempts >= MAX_STOP_ATTEMPTS) {
        currentResolve?.({ outcome: 'timeout' })
        stop()
      }
    })()
  }

  function startStopPoll(deploymentId: number, taskId: string): Promise<StopPollResult> {
    stop()
    stopping.value = true
    return new Promise<StopPollResult>((resolve) => {
      currentResolve = resolve
      timer = window.setInterval(() => pollOnce(deploymentId, taskId), POLL_STOP_MS)
    })
  }

  onUnmounted(stop)

  return {
    stopping,
    startStopPoll,
    stop,
  }
}
