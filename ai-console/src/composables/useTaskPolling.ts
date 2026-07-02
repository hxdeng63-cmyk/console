import { ref, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { deploymentApi } from '@/api/deployment'

const POLL_TASK_MS = 2000
const MAX_TASK_ATTEMPTS = 30

export interface StartPollArgs {
  deploymentId: number
  taskId: string
  moduleName: string
  onSuccess?: (deploymentId: number, taskId: string, moduleName: string) => void
}

export interface StartAllPollArgs {
  taskId: string
  onCompleted: (summary: { started: number; failed: number; skipped: number }) => void
  onFailed: (error: string) => void
}

export function useTaskPolling() {
  const startingAll = ref(false)

  let startTimer: number | null = null
  let startAttempts = 0
  let startArgs: StartPollArgs | null = null

  let startAllTimer: number | null = null
  let startAllErrorReported = false
  let startAllArgs: StartAllPollArgs | null = null

  function clearStartTimer() {
    if (startTimer !== null) {
      window.clearInterval(startTimer)
      startTimer = null
    }
  }

  function clearStartAllTimer() {
    if (startAllTimer !== null) {
      window.clearInterval(startAllTimer)
      startAllTimer = null
    }
  }

  function pollStart() {
    if (!startArgs) return
    startAttempts += 1
    void (async () => {
      try {
        const res: any = await deploymentApi.startStatus(startArgs!.deploymentId, startArgs!.taskId)
        if (res.status === 'success') {
          ElMessage.success(`${startArgs!.moduleName} 识别已就绪`)
          startArgs!.onSuccess?.(startArgs!.deploymentId, startArgs!.taskId, startArgs!.moduleName)
          stopStartPoll()
          return
        }
        if (res.status === 'failed') {
          ElMessage.error(`${startArgs!.moduleName} 启动失败：${res.error || '未知错误'}`)
          stopStartPoll()
          return
        }
        if (startAttempts >= MAX_TASK_ATTEMPTS) {
          ElMessage.warning(`${startArgs!.moduleName} 启动状态获取超时`)
          stopStartPoll()
        }
      } catch {
        if (startAttempts >= MAX_TASK_ATTEMPTS) {
          ElMessage.warning(`${startArgs!.moduleName} 启动状态获取超时`)
          stopStartPoll()
        }
      }
    })()
  }

  function pollStartAll() {
    if (!startAllArgs) return
    void (async () => {
      try {
        const status: any = await deploymentApi.getStartAllStatus(startAllArgs!.taskId)
        const { status: taskStatus, started = 0, failed = 0, skipped = 0, error } = status
        if (taskStatus === 'completed') {
          ElMessage.success(`开始监测完成：已启动 ${started} 个，失败 ${failed} 个，跳过 ${skipped} 个`)
          startAllArgs!.onCompleted({ started, failed, skipped })
          stopStartAllPoll()
        } else if (taskStatus === 'failed') {
          ElMessage.error('开始监测失败：' + (error || '未知错误'))
          startAllArgs!.onFailed(error || '未知错误')
          stopStartAllPoll()
        }
      } catch (pollError: any) {
        if (!startAllErrorReported) {
          startAllErrorReported = true
          ElMessage.error('轮询任务进度失败：' + (pollError?.message || '未知错误'))
        }
        stopStartAllPoll()
      }
    })()
  }

  function startStartPoll(args: StartPollArgs) {
    stopStartPoll()
    startAttempts = 0
    startArgs = args
    startTimer = window.setInterval(pollStart, POLL_TASK_MS)
  }

  function stopStartPoll() {
    clearStartTimer()
    startArgs = null
  }

  function startStartAllPoll(args: StartAllPollArgs) {
    stopStartAllPoll()
    startingAll.value = true
    startAllErrorReported = false
    startAllArgs = args
    startAllTimer = window.setInterval(pollStartAll, POLL_TASK_MS)
  }

  function stopStartAllPoll() {
    clearStartAllTimer()
    startAllArgs = null
    startingAll.value = false
  }

  function dispose() {
    stopStartPoll()
    stopStartAllPoll()
  }

  onUnmounted(dispose)

  return {
    startingAll,
    startStartPoll,
    stopStartPoll,
    startStartAllPoll,
    stopStartAllPoll,
    dispose,
  }
}