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

export interface RestartPollArgs {
  taskId: string
  onCompleted: (summary: { restarted: number; failed: number; skipped: number }) => void
  onFailed: (error: string) => void
}

export function useTaskPolling() {
  const restarting = ref(false)

  let startTimer: number | null = null
  let startAttempts = 0
  let startArgs: StartPollArgs | null = null

  let restartTimer: number | null = null
  let restartErrorReported = false
  let restartArgs: RestartPollArgs | null = null

  function clearStartTimer() {
    if (startTimer !== null) {
      window.clearInterval(startTimer)
      startTimer = null
    }
  }

  function clearRestartTimer() {
    if (restartTimer !== null) {
      window.clearInterval(restartTimer)
      restartTimer = null
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

  function pollRestart() {
    if (!restartArgs) return
    void (async () => {
      try {
        const status: any = await deploymentApi.getRestartAllStatus(restartArgs!.taskId)
        const { status: taskStatus, restarted = 0, failed = 0, skipped = 0, error } = status
        if (taskStatus === 'completed') {
          ElMessage.success(`重新监测完成：已重启 ${restarted} 个，失败 ${failed} 个，跳过 ${skipped} 个`)
          restartArgs!.onCompleted({ restarted, failed, skipped })
          stopRestartPoll()
        } else if (taskStatus === 'failed') {
          ElMessage.error('重新监测失败：' + (error || '未知错误'))
          restartArgs!.onFailed(error || '未知错误')
          stopRestartPoll()
        }
      } catch (pollError: any) {
        if (!restartErrorReported) {
          restartErrorReported = true
          ElMessage.error('轮询任务进度失败：' + (pollError?.message || '未知错误'))
        }
        stopRestartPoll()
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

  function startRestartPoll(args: RestartPollArgs) {
    stopRestartPoll()
    restarting.value = true
    restartErrorReported = false
    restartArgs = args
    restartTimer = window.setInterval(pollRestart, POLL_TASK_MS)
  }

  function stopRestartPoll() {
    clearRestartTimer()
    restartArgs = null
    restarting.value = false
  }

  function dispose() {
    stopStartPoll()
    stopRestartPoll()
  }

  onUnmounted(dispose)

  return {
    restarting,
    startStartPoll,
    stopStartPoll,
    startRestartPoll,
    stopRestartPoll,
    dispose,
  }
}