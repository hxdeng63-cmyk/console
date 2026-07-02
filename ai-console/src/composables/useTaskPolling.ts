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
          // traffic-api 状态机：上一个 task 刚 completed 但 active slot 还没释放
          // → ai-console 后端透传 409 → task 标 failed + error 含"状态冲突"
          // 自动 sleep + 重新调 start（让 ai-console 后端拿到新 task_id）后重试轮询
          if (/状态冲突/.test(String(res.error || '')) && startAttempts < MAX_TASK_ATTEMPTS) {
            await new Promise(r => setTimeout(r, 2000))
            try {
              const restart = await deploymentApi.start(startArgs!.deploymentId, {
                module_name: startArgs!.moduleName,
                video_path: 'auto',
                stream_map: { [String(startArgs!.deploymentId)]: String(startArgs!.deploymentId) },
                config: { callback_url: '', push_interval: 1.0 },
              })
              if (restart?.task_id) {
                startArgs!.taskId = restart.task_id
                startAttempts = 0
                return  // 继续轮询
              }
            } catch { /* 落到下面正常错误处理 */ }
          }
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