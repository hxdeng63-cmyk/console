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
        // 实际接口(ai-console 后端转发 traffic-api task status)返回的 status 是 'completed' / 'failed' / 'running',
        // 不是单 deployment start 调用方曾约定的 'success'。与 pollStartAll 同源。
        // 这里把 'success' 和 'completed' 都视为"就绪"以兼容老后端。
        if (res.status === 'completed' || res.status === 'success') {
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
              // stream_map 的 key 必须是 device_id（traffic-api / _resolve_stream_id_and_device 都按 primary_device.id 查找）；
              // 之前误写 deploymentId → 触发 "stream_map missing entry for device N"。
              // 取一次 deployment 详情拿 device_ids[0]；取不到时 fallback 用 deploymentId。
              let deviceKey: number = startArgs!.deploymentId
              try {
                const dep: any = await deploymentApi.get(startArgs!.deploymentId)
                const ids: number[] = Array.isArray(dep?.device_ids) ? dep.device_ids : []
                if (ids.length > 0 && typeof ids[0] === 'number') deviceKey = ids[0]
              } catch { /* 拉不到就 fallback */ }
              const restart = await deploymentApi.start(startArgs!.deploymentId, {
                module_name: startArgs!.moduleName,
                video_path: 'auto',
                stream_map: { [String(deviceKey)]: String(deviceKey) },
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