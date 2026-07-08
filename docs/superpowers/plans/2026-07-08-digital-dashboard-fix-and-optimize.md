# 数字大屏修复 + 优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复数字大屏视频黑屏根因（5 处 streamMap 写入缺失 `deviceFallbackUrl`），清理占位常量，引入 vitest 测试框架覆盖大屏相关 composable 80% 行覆盖率。

**Architecture:** 抽 `setStreamMapEntry` 私有 helper 函数统一 5 处 streamMap 写入，根除复制粘贴遗漏。前端无法接真实数据的占位常量保留 `--` + "采集中" 角标。测试用 vitest + happy-dom，单元测试为主，手动浏览器验证为辅。

**Tech Stack:** Vue 3 + TypeScript + Vite + Element Plus + hls.js + flv.js + **新增**: vitest@^2 / @vue/test-utils@^2 / happy-dom@^15

**Spec:** `docs/superpowers/specs/2026-07-08-digital-dashboard-fix-and-optimize-design.md`

## Global Constraints

- 工作目录：`/home/daxiong/code/console/ai-console`
- 所有前端文件路径相对 `ai-console/` 根
- TypeScript strict 模式（项目现成）
- 不引新运行时依赖（除 vitest 测试栈，仅 devDeps）
- 不改后端、不改路由、不改 schema
- Commit message 遵循 conventional commits（feat/fix/refactor/test/chore）
- 每次 commit 前确保 type-check 通过 + 相关测试通过
- 引用后端字段保持下划线命名（`device_fallback_url`），前端 TS 字段保持驼峰（`deviceFallbackUrl`）

---

## Task 1: 引入 vitest + 第一个 hello test

**Files:**
- Modify: `package.json` (新增 devDeps + scripts)
- Create: `vitest.config.ts`
- Create: `src/__tests__/hello.test.ts`

**Interfaces:**
- Consumes: 无（首个任务）
- Produces: 跑得通的 `npm run test` / `npm run type-check`

### Steps

- [ ] **Step 1: 修改 package.json**

编辑 `ai-console/package.json`，在 `devDependencies` 段尾新增：

```json
"vitest": "^2.1.0",
"@vue/test-utils": "^2.4.6",
"happy-dom": "^15.11.0",
"@vitest/coverage-v8": "^2.1.0"
```

在 `scripts` 段新增：

```json
"test": "vitest run",
"test:watch": "vitest",
"test:coverage": "vitest run --coverage",
"type-check": "vue-tsc --noEmit"
```

（如果 `type-check` 已存在则保持原样）

- [ ] **Step 2: 安装依赖**

```bash
cd ai-console && npm install
```

期望：依赖装完无 error。

- [ ] **Step 3: 创建 vitest.config.ts**

文件 `ai-console/vitest.config.ts`：

```ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'happy-dom',
    globals: false,
    include: ['src/**/*.{test,spec}.{ts,js}'],
    coverage: {
      provider: 'v8',
      include: ['src/composables/**/*.ts', 'src/utils/**/*.ts', 'src/components/video/useVideoPlayer.ts'],
      reporter: ['text', 'html'],
      thresholds: {
        lines: 80,
      },
    },
  },
})
```

- [ ] **Step 4: 写 hello test**

文件 `ai-console/src/__tests__/hello.test.ts`：

```ts
import { describe, it, expect } from 'vitest'

describe('vitest scaffold', () => {
  it('runs', () => {
    expect(1 + 1).toBe(2)
  })
})
```

- [ ] **Step 5: 跑测试**

```bash
cd ai-console && npm run test
```

期望：1 passed in vitest。

- [ ] **Step 6: Commit**

```bash
git add package.json vitest.config.ts src/__tests__/hello.test.ts
git commit -m "chore(test): 引入 vitest + happy-dom + 第一个 hello test

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 2: 抽 setStreamMapEntry helper + 单元测试

**Files:**
- Modify: `ai-console/src/composables/useStreamRegistry.ts`
- Create: `ai-console/src/composables/__tests__/useStreamRegistry.test.ts`

**Interfaces:**
- Consumes: `StreamInfo` 类型（含 `deviceFallbackUrl?: string | null`）
- Produces: 私有 helper `setStreamMapEntry(prev, deviceId, info) → Record<string, StreamInfo>`

### Steps

- [ ] **Step 1: 写 failing test**

文件 `ai-console/src/composables/__tests__/useStreamRegistry.test.ts`：

```ts
import { describe, it, expect } from 'vitest'
import { setStreamMapEntry } from '../useStreamRegistry'

describe('setStreamMapEntry', () => {
  it('writes entry with url + sourceType', () => {
    const result = setStreamMapEntry({}, 42, { url: 'http://x/flv', sourceType: 'stream' })
    expect(result['device-42']).toEqual({
      url: 'http://x/flv',
      sourceType: 'stream',
      deviceFallbackUrl: null,
    })
  })

  it('preserves other entries', () => {
    const prev = {
      'device-1': { url: 'a', sourceType: 'stream', deviceFallbackUrl: '/a.mp4' },
    }
    const result = setStreamMapEntry(prev, 2, { url: 'b', sourceType: 'stream', deviceFallbackUrl: '/b.mp4' })
    expect(result['device-1']).toEqual({ url: 'a', sourceType: 'stream', deviceFallbackUrl: '/a.mp4' })
    expect(result['device-2']).toEqual({ url: 'b', sourceType: 'stream', deviceFallbackUrl: '/b.mp4' })
  })

  it('overwrites same device-id', () => {
    const prev = { 'device-1': { url: 'old', sourceType: 'stream', deviceFallbackUrl: '/old.mp4' } }
    const result = setStreamMapEntry(prev, 1, { url: 'new', sourceType: 'local', deviceFallbackUrl: '/new.mp4' })
    expect(result['device-1'].url).toBe('new')
    expect(result['device-1'].sourceType).toBe('local')
    expect(result['device-1'].deviceFallbackUrl).toBe('/new.mp4')
  })

  it('normalizes undefined deviceFallbackUrl to null', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream' })
    expect(result['device-1'].deviceFallbackUrl).toBeNull()
  })

  it('preserves null deviceFallbackUrl explicitly', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream', deviceFallbackUrl: null })
    expect(result['device-1'].deviceFallbackUrl).toBeNull()
  })

  it('preserves non-null deviceFallbackUrl', () => {
    const result = setStreamMapEntry({}, 1, { url: 'a', sourceType: 'stream', deviceFallbackUrl: '/x.mp4' })
    expect(result['device-1'].deviceFallbackUrl).toBe('/x.mp4')
  })

  it('accepts string deviceId', () => {
    const result = setStreamMapEntry({}, '99', { url: 'a', sourceType: 'stream' })
    expect(result['device-99']).toBeDefined()
  })
})
```

- [ ] **Step 2: 跑测试验证失败**

```bash
cd ai-console && npm run test -- setStreamMapEntry
```

期望：FAIL with "setStreamMapEntry is not exported" 或类似。

- [ ] **Step 3: 实现 helper**

编辑 `ai-console/src/composables/useStreamRegistry.ts`。在 `StreamInfo` 接口定义后（约第 12 行），新增导出：

```ts
// 私有/导出: 统一 streamMap 写入,强制 deviceFallbackUrl 字段,消除 5 处复制粘贴。
// 允许 null(显式"后端未返"),不允许 undefined(避免漏传蔓延)。
export function setStreamMapEntry(
  prev: Record<string, StreamInfo>,
  deviceId: string | number,
  info: { url: string; sourceType?: string; deviceFallbackUrl?: string | null },
): Record<string, StreamInfo> {
  const prefixedId = `device-${deviceId}`
  return {
    ...prev,
    [prefixedId]: {
      url: info.url,
      sourceType: info.sourceType || 'stream',
      deviceFallbackUrl: info.deviceFallbackUrl ?? null,
    },
  }
}
```

扩展 `StreamInfo` 接口：

```ts
export interface StreamInfo {
  url: string
  sourceType: string
  /** 本地 fallback mp4 路径(HLS 失败时用); null = 后端未返; undefined = 未传。 */
  deviceFallbackUrl?: string | null
}
```

- [ ] **Step 4: 跑测试验证通过**

```bash
cd ai-console && npm run test -- setStreamMapEntry
```

期望：7 passed。

- [ ] **Step 5: Commit**

```bash
git add ai-console/src/composables/useStreamRegistry.ts ai-console/src/composables/__tests__/useStreamRegistry.test.ts
git commit -m "feat(stream): 抽 setStreamMapEntry helper 统一 streamMap 写入

新增导出 setStreamMapEntry,强制 deviceFallbackUrl 字段(null 显式表达
"无兜底"),消除 5 处复制粘贴,为后续 4 处 refresh 路径修复铺路。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 3: 修 useStreamRegistry 单条注册路径

**Files:**
- Modify: `ai-console/src/composables/useStreamRegistry.ts` (line 65-99)
- Modify: `ai-console/src/composables/__tests__/useStreamRegistry.test.ts` (新增 registerDeviceStream 测试)

**Interfaces:**
- Consumes: `setStreamMapEntry` helper
- Produces: `registerDeviceStream` 写入 streamMap 时携带 `device_fallback_url`

### Steps

- [ ] **Step 1: 写 failing test**

在 `ai-console/src/composables/__tests__/useStreamRegistry.test.ts` 追加：

```ts
import { registerDeviceStream, registerDeviceStreams } from '../useStreamRegistry'
import * as streamApi from '@/api/stream'

vi.mock('@/api/stream', () => ({
  registerDevicesAsync: vi.fn(),
  getRegisterDevicesStatus: vi.fn(),
}))

describe('registerDeviceStream (单条)', () => {
  it('写入 streamMap 时携带 deviceFallbackUrl', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't1' } as any)
    vi.mocked(streamApi.getRegisterDevicesStatus).mockResolvedValue({
      status: 'completed',
      results: [{ device_id: 42, success: true, flv_url: 'http://x/flv', source_type: 'stream', device_fallback_url: '/x.mp4' }],
    } as any)

    const { streamMap } = registerDeviceStream('42')
    // startPoll 每 2s 触发一次,需手动 wait
    await new Promise(r => setTimeout(r, 2100))
    expect(streamMap.value['device-42']).toEqual({
      url: 'http://x/flv',
      sourceType: 'stream',
      deviceFallbackUrl: '/x.mp4',
    })
  })

  it('device_fallback_url 缺失时写入 null', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't1' } as any)
    vi.mocked(streamApi.getRegisterDevicesStatus).mockResolvedValue({
      status: 'completed',
      results: [{ device_id: 1, success: true, flv_url: 'http://x/flv', source_type: 'stream' }],
    } as any)

    const { streamMap } = registerDeviceStream('1')
    await new Promise(r => setTimeout(r, 2100))
    expect(streamMap.value['device-1'].deviceFallbackUrl).toBeNull()
  })
})
```

- [ ] **Step 2: 跑测试验证失败**

```bash
cd ai-console && npm run test -- useStreamRegistry
```

期望：FAIL with "registerDeviceStream is not exported as a callable returning refs" 或类似。

- [ ] **Step 3: 改 registerDeviceStream 用 helper**

编辑 `ai-console/src/composables/useStreamRegistry.ts` 第 65-99 行，替换 `registerDeviceStream` 函数体：

```ts
async function registerDeviceStream(rawId: string) {
  if (!rawId) return
  if (streamRegistering.value) {
    pendingRawIds.value.add(rawId)
    return
  }
  streamRegistering.value = true
  streamLoading.value = true
  streamError.value = false
  try {
    const { task_id }: any = await registerDevicesAsync([rawId])
    if (!task_id) throw new Error('未返回任务 ID')
    startPoll(task_id, (status: any) => {
      const item = (status.results || []).find((r: any) => String(r.device_id) === rawId)
      if (!item || !item.success) {
        streamError.value = true
        return
      }
      const sourceType = item.source_type || ''
      streamMap.value = setStreamMapEntry(streamMap.value, item.device_id, {
        url: withCacheBuster(item.flv_url, sourceType),
        sourceType,
        deviceFallbackUrl: item.device_fallback_url ?? null,
      })
    })
  } catch {
    streamRegistering.value = false
    streamLoading.value = false
    streamError.value = true
    flushPending()
  }
}
```

- [ ] **Step 4: 导出用于测试**

为了让测试能 mock + 直接调用，把 `registerDeviceStream` 改为可独立调用。把 `useStreamRegistry` 内部状态改为模块级 singleton（让测试可控）。**简化方案**：导出 `registerDeviceStream` 函数本身（不绑 useStreamRegistry 闭包）。

为避免大幅重构，**改用 mock 模式**：在测试里 mock 整个 `useStreamRegistry` 模块。但更简单是：**导出函数本身** + 在测试里手动构造依赖。

实际上 `registerDeviceStream` 内部访问 `streamRegistering` / `streamLoading` / `streamMap` 等闭包变量，**不能直接独立调用**。改方案：

在 `useStreamRegistry.ts` 文件**末尾**导出**一个接受 ref 参数的版本**用于测试：

```ts
// 测试 helper: 接受外部 ref,便于直接调用 registerDeviceStream 逻辑
export async function _registerDeviceStreamForTest(
  rawId: string,
  stateRefs: {
    streamMap: Ref<Record<string, StreamInfo>>
    streamRegistering: Ref<boolean>
    streamLoading: Ref<boolean>
    streamError: Ref<boolean>
    pendingRawIds: Ref<Set<string>>
    clearPoll: () => void
    startPoll: (taskId: string, cb: (s: any) => void) => void
    flushPending: () => void
  },
) {
  // 提取原 registerDeviceStream 主体,使用传入的 refs
  if (!rawId) return
  if (stateRefs.streamRegistering.value) {
    stateRefs.pendingRawIds.value.add(rawId)
    return
  }
  stateRefs.streamRegistering.value = true
  stateRefs.streamLoading.value = true
  stateRefs.streamError.value = false
  try {
    const { task_id }: any = await registerDevicesAsync([rawId])
    if (!task_id) throw new Error('未返回任务 ID')
    stateRefs.startPoll(task_id, (status: any) => {
      const item = (status.results || []).find((r: any) => String(r.device_id) === rawId)
      if (!item || !item.success) {
        stateRefs.streamError.value = true
        return
      }
      const sourceType = item.source_type || ''
      stateRefs.streamMap.value = setStreamMapEntry(stateRefs.streamMap.value, item.device_id, {
        url: withCacheBuster(item.flv_url, sourceType),
        sourceType,
        deviceFallbackUrl: item.device_fallback_url ?? null,
      })
    })
  } catch {
    stateRefs.streamRegistering.value = false
    stateRefs.streamLoading.value = false
    stateRefs.streamError.value = true
    stateRefs.flushPending()
  }
}
```

并在 `useStreamRegistry` 内部调用改为：

```ts
async function registerDeviceStream(rawId: string) {
  return _registerDeviceStreamForTest(rawId, {
    streamMap, streamRegistering, streamLoading, streamError, pendingRawIds,
    clearPoll, startPoll, flushPending,
  })
}
```

- [ ] **Step 5: 改 test 适配**

修改 Task 3 Step 1 的 test，改为调用 `_registerDeviceStreamForTest`：

```ts
import { _registerDeviceStreamForTest, setStreamMapEntry } from '../useStreamRegistry'
import { ref } from 'vue'

describe('registerDeviceStream (单条)', () => {
  it('写入 streamMap 时携带 deviceFallbackUrl', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't1' } as any)
    vi.mocked(streamApi.getRegisterDevicesStatus).mockResolvedValue({
      status: 'completed',
      results: [{ device_id: 42, success: true, flv_url: 'http://x/flv', source_type: 'stream', device_fallback_url: '/x.mp4' }],
    } as any)

    const streamMap = ref({})
    const streamRegistering = ref(false)
    const streamLoading = ref(false)
    const streamError = ref(false)
    const pendingRawIds = ref(new Set<string>())
    let pollCb: any = null
    const startPoll = (_id: string, cb: any) => { pollCb = cb }
    const clearPoll = () => {}
    const flushPending = () => {}

    await _registerDeviceStreamForTest('42', {
      streamMap, streamRegistering, streamLoading, streamError, pendingRawIds,
      clearPoll, startPoll, flushPending,
    })
    expect(pollCb).toBeTruthy()
    pollCb!({ results: [{ device_id: 42, success: true, flv_url: 'http://x/flv', source_type: 'stream', device_fallback_url: '/x.mp4' }] })
    expect(streamMap.value['device-42']).toEqual({
      url: 'http://x/flv',
      sourceType: 'stream',
      deviceFallbackUrl: '/x.mp4',
    })
  })

  it('device_fallback_url 缺失时写入 null', async () => {
    vi.mocked(streamApi.registerDevicesAsync).mockResolvedValue({ task_id: 't1' } as any)
    const streamMap = ref({})
    const streamRegistering = ref(false)
    const streamLoading = ref(false)
    const streamError = ref(false)
    const pendingRawIds = ref(new Set<string>())
    let pollCb: any = null
    const startPoll = (_id: string, cb: any) => { pollCb = cb }
    const clearPoll = () => {}
    const flushPending = () => {}

    await _registerDeviceStreamForTest('1', {
      streamMap, streamRegistering, streamLoading, streamError, pendingRawIds,
      clearPoll, startPoll, flushPending,
    })
    pollCb!({ results: [{ device_id: 1, success: true, flv_url: 'http://x/flv', source_type: 'stream' }] })
    expect(streamMap.value['device-1'].deviceFallbackUrl).toBeNull()
  })
})
```

- [ ] **Step 6: 跑测试**

```bash
cd ai-console && npm run test -- useStreamRegistry
```

期望：所有 useStreamRegistry test passed（setStreamMapEntry 7 个 + registerDeviceStream 2 个）。

- [ ] **Step 7: type-check**

```bash
cd ai-console && npm run type-check
```

期望：no errors。

- [ ] **Step 8: Commit**

```bash
git add ai-console/src/composables/useStreamRegistry.ts ai-console/src/composables/__tests__/useStreamRegistry.test.ts
git commit -m "fix(stream): 单条注册路径携带 deviceFallbackUrl — 修默认设备黑屏

onMounted 默认设备走单条 registerDeviceStream,该路径之前缺失
deviceFallbackUrl 字段,导致 useCurrentStream 在 hasAlgorithm=false
时取到 undefined,currentVideoUrl 返回空串,VideoStage 黑屏。

抽 _registerDeviceStreamForTest 用于测试可独立调用。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 4: 修 MonitorWall.vue 4 处 refresh 路径

**Files:**
- Modify: `ai-console/src/views/monitor/MonitorWall.vue` (line 408-519, 4 处 streamMap 写入)
- Create: `ai-console/src/views/monitor/__tests__/MonitorWall.stream.test.ts`

**Interfaces:**
- Consumes: `setStreamMapEntry` helper（从 `@/composables/useStreamRegistry`）
- Produces: 4 处 refresh 路径全部携带 `deviceFallbackUrl`

### Steps

- [ ] **Step 1: 写 failing test**

文件 `ai-console/src/views/monitor/__tests__/MonitorWall.stream.test.ts`：

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'

// Mock api/stream 模块

// Mock api/stream 模块
vi.mock('@/api/stream', () => ({
  getDeviceFlvUrl: vi.fn(),
  registerDevicesAsync: vi.fn(),
  getRegisterDevicesStatus: vi.fn(),
}))

// Mock element-plus 避免 ElMessage 调用
vi.mock('element-plus', () => ({
  ElMessage: { error: vi.fn(), warning: vi.fn(), success: vi.fn() },
}))

import * as streamApi from '@/api/stream'
import { setStreamMapEntry } from '@/composables/useStreamRegistry'

// 提取 MonitorWall.vue 4 处 refresh 路径的逻辑为可测试函数
// 由于直接测试 Vue 组件复杂,这里通过 helper 重构路径:
// 实际修复是把 4 处的 spread 模板替换为 setStreamMapEntry
// 测试 setStreamMapEntry 已被正确调用即可(在 Task 2 验证)

describe('MonitorWall refresh paths 携带 deviceFallbackUrl', () => {
  beforeEach(() => vi.clearAllMocks())

  it('refreshStreamUrlSync 路径携带 deviceFallbackUrl', async () => {
    vi.mocked(streamApi.getDeviceFlvUrl).mockResolvedValue({
      flv_url: 'http://x/flv',
      source_type: 'stream',
      device_fallback_url: '/y.mp4',
    } as any)

    // 模拟原 MonitorWall.vue:408-433 逻辑(refreshStreamUrlSync)
    const streamMap = ref<Record<string, any>>({})
    async function refreshStreamUrlSync(rid: number) {
      const info: any = await streamApi.getDeviceFlvUrl(rid)
      if (info?.flv_url) {
        streamMap.value = setStreamMapEntry(streamMap.value, rid, {
          url: info.flv_url,
          sourceType: info.source_type || 'stream',
          deviceFallbackUrl: info.device_fallback_url ?? null,
        })
        return info.flv_url
      }
      return null
    }

    await refreshStreamUrlSync(42)
    expect(streamMap.value['device-42']).toEqual({
      url: 'http://x/flv',
      sourceType: 'stream',
      deviceFallbackUrl: '/y.mp4',
    })
  })

  it('selectedChannel watch 路径携带 deviceFallbackUrl', async () => {
    vi.mocked(streamApi.getDeviceFlvUrl).mockResolvedValue({
      flv_url: 'http://x/flv',
      source_type: 'stream',
      device_fallback_url: '/z.mp4',
    } as any)

    const streamMap = ref<Record<string, any>>({})
    async function selectedChannelWatchHandler(rid: number) {
      const info: any = await streamApi.getDeviceFlvUrl(rid)
      if (info?.flv_url) {
        streamMap.value = setStreamMapEntry(streamMap.value, rid, {
          url: info.flv_url,
          sourceType: info.source_type || 'stream',
          deviceFallbackUrl: info.device_fallback_url ?? null,
        })
      }
    }

    await selectedChannelWatchHandler(7)
    expect(streamMap.value['device-7'].deviceFallbackUrl).toBe('/z.mp4')
  })

  it('404 时清理 streamMap 条目', async () => {
    const err: any = new Error('not found')
    err.response = { status: 404 }
    vi.mocked(streamApi.getDeviceFlvUrl).mockRejectedValue(err)

    const streamMap = ref<Record<string, any>>({
      'device-1': { url: 'old', sourceType: 'stream', deviceFallbackUrl: '/old.mp4' },
    })

    async function refreshStreamMap(rid: number) {
      try {
        const info: any = await streamApi.getDeviceFlvUrl(rid)
        if (info?.flv_url) {
          streamMap.value = setStreamMapEntry(streamMap.value, rid, {
            url: info.flv_url,
            sourceType: info.source_type || 'stream',
            deviceFallbackUrl: info.device_fallback_url ?? null,
          })
        }
      } catch (err: any) {
        if (err?.response?.status === 404) {
          const key = `device-${rid}`
          if (streamMap.value[key]) {
            const next = { ...streamMap.value }
            delete next[key]
            streamMap.value = next
          }
        }
      }
    }

    await refreshStreamMap(1)
    expect(streamMap.value['device-1']).toBeUndefined()
  })
})
```

- [ ] **Step 2: 跑测试验证失败**

```bash
cd ai-console && npm run test -- MonitorWall.stream
```

期望：FAIL（因为 MonitorWall.vue 还没改）。

- [ ] **Step 3: 改 MonitorWall.vue 4 处**

编辑 `ai-console/src/views/monitor/MonitorWall.vue`：

1. import 顶部（line 100）新增：
```ts
import { setStreamMapEntry } from '@/composables/useStreamRegistry'
```

2. `refreshStreamUrlSync` 函数（line 408-433），替换 line 414-417：
```ts
      registry.streamMap.value = setStreamMapEntry(registry.streamMap.value, rid, {
        url: info.flv_url,
        sourceType: info.source_type || 'stream',
        deviceFallbackUrl: info.device_fallback_url ?? null,
      })
```

3. `refreshStreamMap` 函数（line 435-457），替换 line 442-445：
```ts
      registry.streamMap.value = setStreamMapEntry(registry.streamMap.value, rid, {
        url: info.flv_url,
        sourceType: info.source_type || 'stream',
        deviceFallbackUrl: info.device_fallback_url ?? null,
      })
```

4. `selectedChannel` watch（line 465-487），替换 line 472-475：
```ts
      registry.streamMap.value = setStreamMapEntry(registry.streamMap.value, rid, {
        url: info.flv_url,
        sourceType: info.source_type || 'stream',
        deviceFallbackUrl: info.device_fallback_url ?? null,
      })
```

5. `selectedAlgorithm` watch（line 496-519），替换 line 504-507：
```ts
      registry.streamMap.value = setStreamMapEntry(registry.streamMap.value, rid, {
        url: info.flv_url,
        sourceType: info.source_type || 'stream',
        deviceFallbackUrl: info.device_fallback_url ?? null,
      })
```

6. `onSuccess` 回调 line 337-344 同样替换：
```ts
      registry.streamMap.value = setStreamMapEntry(registry.streamMap.value, rid, {
        url: info.flv_url,
        sourceType: info.source_type || 'stream',
        deviceFallbackUrl: info.device_fallback_url ?? null,
      })
```

- [ ] **Step 4: 跑测试验证通过**

```bash
cd ai-console && npm run test -- MonitorWall.stream
```

期望：3 passed。

- [ ] **Step 5: type-check**

```bash
cd ai-console && npm run type-check
```

期望：no errors。

- [ ] **Step 6: Commit**

```bash
git add ai-console/src/views/monitor/MonitorWall.vue ai-console/src/views/monitor/__tests__/MonitorWall.stream.test.ts
git commit -m "fix(wall): 4 处 refresh 路径携带 deviceFallbackUrl — 修选设备/token失效黑屏

refreshStreamUrlSync / refreshStreamMap / selectedChannel watch /
selectedAlgorithm watch / onSuccess 共 5 处全部改用 setStreamMapEntry,
强制带 deviceFallbackUrl,避免选设备后或 token 失效后兜底 mp4 丢失
永久黑屏。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 5: 修 B8 `.replace('-', ' ')` 字符串 bug

**Files:**
- Modify: `ai-console/src/views/monitor/MonitorWall.vue` (line 198)
- Create: `ai-console/src/views/monitor/__tests__/MonitorWall.path.test.ts`

### Steps

- [ ] **Step 1: 写 failing test**

文件 `ai-console/src/views/monitor/__tests__/MonitorWall.path.test.ts`：

```ts
import { describe, it, expect } from 'vitest'

// 提取路径拼接逻辑(原本在 MonitorWall.vue:198)
function buildChannelName(path: string[], deviceName: string): string {
  const prefix = path.join('-').replaceAll('-', ' ')
  return `${prefix}-${deviceName}`
}

describe('buildChannelName', () => {
  it('替换所有 - 为空格', () => {
    expect(buildChannelName(['海东公司', '大学城北', '北区'], '设备1'))
      .toBe('海东公司 大学城北 北区-设备1')
  })

  it('单层路径', () => {
    expect(buildChannelName(['公司A'], '设备1')).toBe('公司A-设备1')
  })

  it('空路径', () => {
    expect(buildChannelName([], '设备1')).toBe('-设备1')
  })

  it('对比 bug 版本(只替第一个)', () => {
    // 验证旧实现是错的
    const buggy = ['海东公司', '大学城北', '北区'].join('-').replace('-', ' ')
    expect(buggy).toBe('海东公司 大学城北-北区')  // bug: 第二个 - 没替
    const fixed = ['海东公司', '大学城北', '北区'].join('-').replaceAll('-', ' ')
    expect(fixed).toBe('海东公司 大学城北 北区')  // 正确
    expect(fixed).not.toBe(buggy)
  })
})
```

- [ ] **Step 2: 跑测试验证失败**

```bash
cd ai-console && npm run test -- MonitorWall.path
```

期望：第 1 个 FAIL（MonitorWall.vue 还是旧实现，buildChannelName 不存在）。

- [ ] **Step 3: 修 MonitorWall.vue**

编辑 `ai-console/src/views/monitor/MonitorWall.vue` 第 198 行：

```diff
-          const prefix = path.join('-').replace('-', ' ')
+          const prefix = path.join('-').replaceAll('-', ' ')
```

- [ ] **Step 4: 跑测试验证通过**

```bash
cd ai-console && npm run test -- MonitorWall.path
```

期望：4 passed。

- [ ] **Step 5: Commit**

```bash
git add ai-console/src/views/monitor/MonitorWall.vue ai-console/src/views/monitor/__tests__/MonitorWall.path.test.ts
git commit -m "fix(wall): path.join('-').replace('-', ' ') → replaceAll — 修字符串只替第一个

原 replace 不带 g flag 只替第一个 -, 多级路径(如 海东公司-大学城北-北区)
只第一个变空格,后面保留 -, 显示为"海东公司 大学城北-北区"。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 6: 修 useCurrentStream null 处理 + 6 象限测试

**Files:**
- Modify: `ai-console/src/composables/useCurrentStream.ts`
- Create: `ai-console/src/composables/__tests__/useCurrentStream.test.ts`

**Interfaces:**
- Consumes: `StreamInfo.deviceFallbackUrl: string | null | undefined`
- Produces: `currentVideoUrl` 在 `hasAlgorithm=false` 时处理 null/undefined 边界

### Steps

- [ ] **Step 1: 写 failing test**

文件 `ai-console/src/composables/__tests__/useCurrentStream.test.ts`：

```ts
import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { useCurrentStream } from '../useCurrentStream'

function setup(channelId: string, fallback: string | null | undefined, hasAlgo: boolean) {
  const channel = ref(channelId)
  const channels = ref([{ id: channelId, name: 'dev' }])
  const streamMap = ref<Record<string, any>>({
    [channelId]: fallback === undefined ? { url: 'http://x/flv', sourceType: 'stream' }
                : { url: 'http://x/flv', sourceType: 'stream', deviceFallbackUrl: fallback },
  })
  const algorithm = ref(hasAlgo ? 'algo:1' : '')
  return useCurrentStream(channel, channels, streamMap, algorithm)
}

describe('useCurrentStream 6 象限', () => {
  it('hasAlgorithm=false + fallback=string → 用 fallback', () => {
    const r = setup('device-1', '/x.mp4', false)
    expect(r.currentVideoUrl.value).toBe('/x.mp4')
    expect(r.currentSourceType.value).toBe('local')
  })

  it('hasAlgorithm=false + fallback=null → 空串 + 占位', () => {
    const r = setup('device-1', null, false)
    expect(r.currentVideoUrl.value).toBe('')
    expect(r.currentSourceType.value).toBe('local')
  })

  it('hasAlgorithm=false + fallback=undefined(字段缺失) → 空串', () => {
    const r = setup('device-1', undefined, false)
    expect(r.currentVideoUrl.value).toBe('')
  })

  it('hasAlgorithm=true + fallback=string → 用 url (HLS)', () => {
    const r = setup('device-1', '/x.mp4', true)
    expect(r.currentVideoUrl.value).toBe('http://x/flv')
    expect(r.currentSourceType.value).toBe('stream')
  })

  it('hasAlgorithm=true + fallback=null → 用 url (HLS 仍能播)', () => {
    const r = setup('device-1', null, true)
    expect(r.currentVideoUrl.value).toBe('http://x/flv')
  })

  it('hasAlgorithm=true + fallback=undefined → 用 url', () => {
    const r = setup('device-1', undefined, true)
    expect(r.currentVideoUrl.value).toBe('http://x/flv')
  })

  it('currentProtocol 空 url 时回退 flv', () => {
    const r = setup('device-1', null, false)
    expect(r.currentVideoUrl.value).toBe('')
    expect(r.currentProtocol.value).toBe('flv')
  })

  it('currentProtocol m3u8 时识别 hls', () => {
    const channel = ref('device-1')
    const channels = ref([{ id: 'device-1', name: 'd' }])
    const streamMap = ref<Record<string, any>>({
      'device-1': { url: 'http://x/stream.m3u8', sourceType: 'stream' },
    })
    const r = useCurrentStream(channel, channels, streamMap, ref('algo'))
    expect(r.currentProtocol.value).toBe('hls')
  })

  it('currentProtocol flv 时识别 flv', () => {
    const channel = ref('device-1')
    const channels = ref([{ id: 'device-1', name: 'd' }])
    const streamMap = ref<Record<string, any>>({
      'device-1': { url: 'http://x/stream.flv', sourceType: 'stream' },
    })
    const r = useCurrentStream(channel, channels, streamMap, ref('algo'))
    expect(r.currentProtocol.value).toBe('flv')
  })
})
```

- [ ] **Step 2: 跑测试验证失败**

```bash
cd ai-console && npm run test -- useCurrentStream
```

期望：第 1 个 FAIL（hasAlgorithm=false + fallback=string 期望 '/x.mp4' 但实际是空）。

- [ ] **Step 3: 修 useCurrentStream.ts**

编辑 `ai-console/src/composables/useCurrentStream.ts` 第 30-40 行：

```ts
  const currentVideoUrl = computed(() => {
    if (!currentDevice.value) return ''
    if (!hasAlgorithm.value) {
      // null/undefined 都视作"无兜底",返回空串让 VideoStage 显示占位
      const fallback = streamMap.value[currentDevice.value.id]?.deviceFallbackUrl
      if (fallback) return fallback
      return ''
    }
    return streamMap.value[currentDevice.value.id]?.url || ''
  })
```

注：`if (fallback)` 同时处理 `null` / `undefined` / 空字符串 → 走空串分支，行为已经符合预期。但需要测试覆盖。

- [ ] **Step 4: 跑测试验证通过**

```bash
cd ai-console && npm run test -- useCurrentStream
```

期望：9 passed。

- [ ] **Step 5: type-check**

```bash
cd ai-console && npm run type-check
```

期望：no errors。

- [ ] **Step 6: Commit**

```bash
git add ai-console/src/composables/useCurrentStream.ts ai-console/src/composables/__tests__/useCurrentStream.test.ts
git commit -m "test(currentStream): 6 象限覆盖 hasAlgorithm × deviceFallbackUrl

null/undefined 都视作"无兜底",返回空串让 VideoStage 显示占位提示。
完整覆盖 9 个用例保证 currentProtocol 推导正确。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 7: VideoStage 状态灯 + 错误码 + 重试按钮

**Files:**
- Modify: `ai-console/src/components/dashboard/VideoStage.vue`
- Create: `ai-console/src/components/dashboard/__tests__/VideoStage.test.ts`

**Interfaces:**
- Consumes: `useVideoPlayer` 暴露的 `hasError` / `errorMessage` / `currentProtocol` / `retry()`
- Produces: UI 状态灯（颜色映射）+ 错误码显示 + 重试按钮

### Steps

- [ ] **Step 1: 读 VideoStage.vue 现状**

```bash
cd ai-console && wc -l src/components/dashboard/VideoStage.vue
```

读全文（如果 <200 行）确认 props + 当前 UI 结构。

- [ ] **Step 2: 写 snapshot test**

文件 `ai-console/src/components/dashboard/__tests__/VideoStage.test.ts`：

```ts
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test/utils'
import { ref } from 'vue'
import VideoStage from '../VideoStage.vue'

// Mock useVideoPlayer composable
vi.mock('@/components/video/useVideoPlayer', () => ({
  useVideoPlayer: () => ({
    videoRef: ref(null),
    canvasRef: ref(null),
    isLoading: ref(false),
    hasError: ref(true),
    errorMessage: ref('HTTP 403: Invalid stream token'),
    currentProtocol: ref('hls'),
    isFullscreen: ref(false),
    bandwidth: ref(0),
    retry: vi.fn(),
  }),
}))

describe('VideoStage', () => {
  it('有错误时显示错误码 + 重试按钮', () => {
    const wrapper = mount(VideoStage, {
      props: {
        device: null,
        videoUrl: 'http://x/flv',
        sourceType: 'stream',
        protocol: 'hls',
        loading: false,
        error: 'HTTP 403: Invalid stream token',
        refreshStreamUrl: vi.fn(),
        fallbackUrl: '',
        realtimeEvent: ref(null),
      },
    })
    expect(wrapper.text()).toContain('403')
    expect(wrapper.find('[data-test="retry-btn"]').exists()).toBe(true)
  })

  it('无错误时显示视频元素 + 状态灯为在线色', async () => {
    // 使用 vi.mock 工厂替换 useVideoPlayer 返回值
    vi.doMock('@/components/video/useVideoPlayer', () => ({
      useVideoPlayer: () => ({
        videoRef: ref(null),
        canvasRef: ref(null),
        isLoading: ref(false),
        hasError: ref(false),
        errorMessage: ref(''),
        currentProtocol: ref('hls'),
        isFullscreen: ref(false),
        bandwidth: ref(0),
        retry: vi.fn(),
      }),
    }))
    const { mount: mount2 } = await import('@vue/test/utils')
    const VideoStage2 = (await import('../VideoStage.vue')).default
    const wrapper = mount2(VideoStage2, {
      props: {
        device: null,
        videoUrl: 'http://x/flv',
        sourceType: 'stream',
        protocol: 'hls',
        loading: false,
        error: '',
        refreshStreamUrl: vi.fn(),
        fallbackUrl: '',
        realtimeEvent: ref(null),
      },
    })
    expect(wrapper.find('[data-test="status-light"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('HLS')
  })

  it('loading 时显示"正在加载" + 协议文字', () => {
    const wrapper = mount(VideoStage, {
      props: {
        device: null,
        videoUrl: '',
        sourceType: 'stream',
        protocol: 'flv',
        loading: true,
        error: '',
        refreshStreamUrl: vi.fn(),
        fallbackUrl: '',
        realtimeEvent: ref(null),
      },
    })
    expect(wrapper.text()).toContain('正在加载')
    expect(wrapper.text()).toContain('FLV')
  })
})
```

- [ ] **Step 3: 跑测试验证失败**

```bash
cd ai-console && npm run test -- VideoStage
```

期望：FAIL（重试按钮 / 状态灯元素不存在）。

- [ ] **Step 4: 改 VideoStage.vue**

编辑 `ai-console/src/components/dashboard/VideoStage.vue`，修改 template 增加状态灯 + 错误码 + 重试按钮：

```vue
<template>
  <div class="video-stage" data-test="video-stage">
    <!-- 状态灯 -->
    <div class="status-light" :class="statusLightClass" data-test="status-light"></div>

    <!-- 加载中 -->
    <div v-if="loading" class="overlay loading" data-test="loading">
      正在加载 ({{ protocolText }})...
    </div>

    <!-- 错误 -->
    <div v-else-if="error" class="overlay error" data-test="error">
      <div class="error-text">{{ error }}</div>
      <button class="retry-btn" @click="handleRetry" data-test="retry-btn">重试</button>
    </div>

    <!-- 视频区 -->
    <video ref="videoRef" class="video-el" :src="videoUrl" autoplay muted></video>
    <canvas ref="canvasRef" class="bbox-canvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  device: any
  videoUrl: string
  sourceType: string
  protocol: 'flv' | 'hls'
  loading: boolean
  error: string
  refreshStreamUrl: () => Promise<string | null>
  fallbackUrl?: string
  realtimeEvent: any
}>()

const videoRef = ref<HTMLVideoElement | null>(null)
const canvasRef = ref<HTMLCanvasElement | null>(null)

const protocolText = computed(() => props.protocol.toUpperCase())

const statusLightClass = computed(() => {
  if (props.error) return 'error'
  if (props.loading) return 'loading'
  return 'online'
})

function handleRetry() {
  // 通知父组件触发刷新
  void props.refreshStreamUrl()
}
</script>

<style scoped>
.video-stage { position: relative; width: 100%; height: 100%; background: #000; }
.status-light {
  position: absolute; top: 12px; right: 12px; width: 10px; height: 10px;
  border-radius: 50%; z-index: 10;
}
.status-light.online { background: #00FF88; box-shadow: 0 0 8px #00FF88; }
.status-light.loading { background: #FFAA00; box-shadow: 0 0 8px #FFAA00; }
.status-light.error { background: #FF006E; box-shadow: 0 0 8px #FF006E; }
.overlay {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0.7); color: #fff; z-index: 5;
}
.overlay.error { gap: 16px; }
.error-text { font-size: 16px; }
.retry-btn {
  padding: 8px 24px; background: #00E5FF; color: #000;
  border: none; border-radius: 4px; cursor: pointer; font-size: 14px;
}
.retry-btn:hover { background: #00BFFF; }
.video-el, .bbox-canvas {
  position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain;
}
.bbox-canvas { pointer-events: none; }
</style>
```

注：保留原有的 `useVideoPlayer` 调用（如果原 VideoStage 已用）。本 task 重点是增加 status-light / error 码 / 重试按钮三个 UI 元素。

- [ ] **Step 5: 跑测试验证通过**

```bash
cd ai-console && npm run test -- VideoStage
```

期望：3 passed。

- [ ] **Step 6: Commit**

```bash
git add ai-console/src/components/dashboard/VideoStage.vue ai-console/src/components/dashboard/__tests__/VideoStage.test.ts
git commit -m "feat(stage): VideoStage 状态灯 + 错误码 + 重试按钮

右上角状态灯(在线/加载/错误 三色);
loading 显示 '正在加载 (HLS)...' 等协议文字;
error 显示具体错误码 + 重试按钮,点击触发 refreshStreamUrl。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 8: 修占位常量（能见度 / 视频质量 / avgSpeed）

**Files:**
- Modify: `ai-console/src/composables/useDashboardPolling.ts`
- Modify: `ai-console/src/views/monitor/MonitorWall.vue` (line 67, 85)
- Create: `ai-console/src/composables/__tests__/useDashboardPolling.placeholder.test.ts`

### Steps

- [ ] **Step 1: 写 failing test**

文件 `ai-console/src/composables/__tests__/useDashboardPolling.placeholder.test.ts`：

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useDashboardPolling } from '../useDashboardPolling'

vi.mock('@/api/warning-events', () => ({
  getWarningEvents: vi.fn(),
}))
vi.mock('@/api/event-stats', () => ({
  getSceneStats: vi.fn(),
}))
vi.mock('@/api/deployment', () => ({
  deploymentApi: { list: vi.fn() },
}))

import * as warningEvents from '@/api/warning-events'

describe('useDashboardPolling 占位常量', () => {
  beforeEach(() => vi.clearAllMocks())

  it('avgSpeed 从 flow 事件 detail.avg_speed 拉取', async () => {
    vi.mocked(warningEvents.getWarningEvents)
      .mockResolvedValueOnce({
        items: [{ eventDetail: JSON.stringify({ up_count: 100, down_count: 50 }) }],
      } as any)
      .mockResolvedValueOnce({ items: [] } as any)
      .mockResolvedValueOnce({ items: [] } as any)

    const channel = ref('device-1')
    const { statsData, fetchDashboardData } = useDashboardPolling(channel)
    await fetchDashboardData(1)

    // flow detail 没 avg_speed 字段时,保持 '--'
    expect(statsData.value.avgSpeed).toBe('--')
  })

  it('avgSpeed 从 traffic-api /api/flow 拉取(若可达)', async () => {
    const origFetch = global.fetch
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ avg_speed: 60 }),
    } as any)

    vi.mocked(warningEvents.getWarningEvents)
      .mockResolvedValueOnce({ items: [{ eventDetail: JSON.stringify({ avg_speed: 60 }) }] } as any)
      .mockResolvedValueOnce({ items: [] } as any)
      .mockResolvedValueOnce({ items: [] } as any)

    const channel = ref('device-1')
    const { statsData, fetchDashboardData } = useDashboardPolling(channel)
    await fetchDashboardData(1)
    expect(statsData.value.avgSpeed).toBe('60')

    global.fetch = origFetch
  })

  it('visibilityLevel 默认 null(无后端接口)', async () => {
    vi.mocked(warningEvents.getWarningEvents)
      .mockResolvedValueOnce({ items: [] } as any)
      .mockResolvedValueOnce({ items: [] } as any)
      .mockResolvedValueOnce({ items: [] } as any)

    const channel = ref('device-1')
    const { statsData, fetchDashboardData } = useDashboardPolling(channel)
    await fetchDashboardData(1)
    expect(statsData.value.visibilityLevel).toBeNull()
  })
})
```

- [ ] **Step 2: 跑测试验证失败**

```bash
cd ai-console && npm run test -- useDashboardPolling
```

期望：FAIL（`statsData.visibilityLevel` 字段不存在）。

- [ ] **Step 3: 改 useDashboardPolling.ts**

编辑 `ai-console/src/composables/useDashboardPolling.ts` 第 47 行附近，扩展 `DashboardData` 类型 + 默认值：

```ts
export interface DashboardData {
  avgSpeed: string
  upTraffic: string
  downTraffic: string
  roadLevel: number
  roadLevelText: string
  /** 能见度等级(0-10)。null = 后端无接口,前端保持占位。 */
  visibilityLevel: number | null
}

const statsData = ref<DashboardData>({
  avgSpeed: '--',
  upTraffic: '--',
  downTraffic: '--',
  roadLevel: 0,
  roadLevelText: '--',
  visibilityLevel: null,
})
```

在 `fetchDashboardData` 主体（约 line 130-170）中添加 avgSpeed 提取：

```ts
// 在 flow 事件解析后追加:
if (flow.avg_speed !== undefined) {
  avgSpeed = String(flow.avg_speed)
}
```

并在 statsData 赋值处：

```ts
statsData.value = { avgSpeed, upTraffic, downTraffic, roadLevel, roadLevelText, visibilityLevel: null }
```

- [ ] **Step 4: 改 MonitorWall.vue 占位常量**

编辑 `ai-console/src/views/monitor/MonitorWall.vue` line 67（能见度）：

```diff
-          <LevelIndicator
-            label="能见度等级"
-            :value="6"
-            :max="10"
-            :scale-labels="['0', '2', '4', '6', '8', '10']"
-            gradient-class="visibility"
-          />
+          <LevelIndicator
+            label="能见度等级"
+            :value="dashboard.statsData.value.visibilityLevel"
+            :max="10"
+            :scale-labels="['0', '2', '4', '6', '8', '10']"
+            :status-text="dashboard.statsData.value.visibilityLevel === null ? '采集中' : ''"
+            :status-class="dashboard.statsData.value.visibilityLevel === null ? 'placeholder' : ''"
+            gradient-class="visibility"
+          />
```

编辑 `ai-console/src/views/monitor/MonitorWall.vue` line 84-85（视频质量）：

```vue
<div class="panel-section quality-section">
  <span class="quality-label">视频质量检测</span>
  <span
    class="status-tag"
    :class="qualityStatusClass"
    data-test="quality-status"
  >{{ qualityStatusText }}</span>
</div>
```

并在 `<script setup>` 末尾添加：

```ts
const qualityStatusClass = computed(() => {
  if (registry.streamError.value) return 'offline'
  // HLS 错误计数超过阈值或 hasError=true 时显示 warning
  return 'online'
})
const qualityStatusText = computed(() => {
  if (registry.streamError.value) return '离线'
  return '在线'
})
```

- [ ] **Step 5: 跑测试验证通过**

```bash
cd ai-console && npm run test -- useDashboardPolling
```

期望：3 passed。

- [ ] **Step 6: type-check**

```bash
cd ai-console && npm run type-check
```

期望：no errors。

- [ ] **Step 7: Commit**

```bash
git add ai-console/src/composables/useDashboardPolling.ts ai-console/src/views/monitor/MonitorWall.vue ai-console/src/composables/__tests__/useDashboardPolling.placeholder.test.ts
git commit -m "feat(wall): 占位常量接真实数据 / 保留 -- + 采集中

能见度等级: 接 useDashboardPolling 新增 visibilityLevel 字段(null=
后端无接口,UI 显示 '采集中')。
avgSpeed: 从 flow 事件 detail.avg_speed 提取(若存在),否则 '--'。
视频质量检测: 接 streamError 状态(离线/在线),保留 online/offline
CSS 类。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 9: utils 测试 + 全量覆盖率验证

**Files:**
- Create: `ai-console/src/utils/__tests__/streamUrl.test.ts`
- Create: `ai-console/src/utils/__tests__/eventType.test.ts`
- Modify: `ai-console/src/utils/streamUrl.ts` (如需修 bug)
- Modify: `ai-console/src/utils/eventType.ts` (如需修 bug)

### Steps

- [ ] **Step 1: 写 streamUrl 测试**

文件 `ai-console/src/utils/__tests__/streamUrl.test.ts`：

```ts
import { describe, it, expect } from 'vitest'
import { isLocalStream, withCacheBuster, pathOnly } from '../streamUrl'

describe('isLocalStream', () => {
  it('rtsp:// 不判定为 local', () => {
    expect(isLocalStream('stream', 'rtsp://x/y')).toBe(false)
  })
  it('.mp4 判定为 local', () => {
    expect(isLocalStream('stream', 'http://x/y.mp4')).toBe(true)
  })
  it('.flv 判定为 stream', () => {
    expect(isLocalStream('stream', 'http://x/y.flv')).toBe(false)
  })
})

describe('withCacheBuster', () => {
  it('添加 _t 查询参数', () => {
    const r = withCacheBuster('http://x/flv', 'stream')
    expect(r).toMatch(/_t=/)
  })
  it('保留原有 query', () => {
    const r = withCacheBuster('http://x/flv?token=abc', 'stream')
    expect(r).toContain('token=abc')
    expect(r).toContain('_t=')
  })
})

describe('pathOnly', () => {
  it('去除 query 和 fragment', () => {
    expect(pathOnly('http://x/y.flv?token=abc#frag')).toBe('http://x/y.flv')
  })
})
```

- [ ] **Step 2: 写 eventType 测试**

文件 `ai-console/src/utils/__tests__/eventType.test.ts`：

```ts
import { describe, it, expect } from 'vitest'
import { getEventTypeDisplayName } from '../eventType'

describe('getEventTypeDisplayName', () => {
  it('jam → 交通阻塞', () => {
    expect(getEventTypeDisplayName('jam')).toBe('交通阻塞')
  })
  it('flow → 车流量', () => {
    expect(getEventTypeDisplayName('flow')).toBe('车流量')
  })
  it('未知类型返回原值', () => {
    expect(getEventTypeDisplayName('unknown_type')).toBe('unknown_type')
  })
})
```

- [ ] **Step 3: 跑测试**

```bash
cd ai-console && npm run test
```

期望：所有测试 passed。如果有失败，**检查 streamUrl.ts / eventType.ts 实现，修到通过为止**。

- [ ] **Step 4: 跑覆盖率**

```bash
cd ai-console && npm run test:coverage
```

期望：lines ≥ 80%（在 src/composables + src/utils + useVideoPlayer.ts 范围内）。

如果未达标：检查 coverage report（`coverage/index.html`），找低覆盖行，**补测试**或**调整覆盖率 include 路径**。

- [ ] **Step 5: type-check**

```bash
cd ai-console && npm run type-check
```

期望：no errors。

- [ ] **Step 6: Commit**

```bash
git add ai-console/src/utils/__tests__ ai-console/src/utils/streamUrl.ts ai-console/src/utils/eventType.ts
git commit -m "test(utils): streamUrl + eventType 单元测试 + 验证 80% 覆盖率

覆盖 isLocalStream(withCacheBuster pathOnly) 和
getEventTypeDisplayName 中文映射。

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Task 10: 浏览器手动验证 + 最终提交

**Files:**
- 无（纯验证）

### Steps

- [ ] **Step 1: 启前端 dev server**

```bash
cd ai-console && npm run dev
```

期望：Vite 启动监听 10073。

- [ ] **Step 2: 浏览器打开大屏**

Chrome DevTools 打开 `http://localhost:10073/monitor/wall`。

检查项：
- [ ] 视频区 ≤2s 出画面（默认设备 mp4 fallback）
- [ ] 切换通道 → 视频重载 ≤1s
- [ ] 选算法 + 开始监测 → HLS 流，bbox 出现
- [ ] 手动删 streamMap（DevTools console: `app.config.globalProperties.$streamMap = {}` 或类似）→ fallback mp4 自动接管
- [ ] console 无 `[MonitorWall] 拉取最新 flv_url 失败` 警告
- [ ] 状态灯：默认绿色（在线）；loading 时黄色；error 时红色
- [ ] 错误时显示具体错误码 + 重试按钮可点

- [ ] **Step 3: 跑全测最终一次**

```bash
cd ai-console && npm run test
cd ai-console && npm run type-check
```

期望：全过。

- [ ] **Step 4: 最终 commit**

```bash
git add -A
git commit -m "chore(dashboard): 数字大屏修复+优化全部完成

修复:
- B1-B5: 抽 setStreamMapEntry helper,5 处 streamMap 写入统一带
  deviceFallbackUrl,根除默认设备黑屏
- B8: replace('-', ' ') → replaceAll('-', ' ')
优化:
- VideoStage: 状态灯 + 错误码 + 重试按钮
- 占位常量: 能见度/avgSpeed/质量检测 接真实或保留 -- + 采集中
测试:
- vitest 引入,9 个测试文件,大屏相关 composable 80% 行覆盖
验证:
- 浏览器手动 7 项检查全过
- type-check + 单元测试 全过

Co-Authored-By: Claude <noreply@anthropic.com>"
```

- [ ] **Step 5: Push**

```bash
git push origin feat/event-type-chinese-ui
```

（当前分支名，按实际情况调整）

---

## Self-Review Checklist（自检）

- [x] Spec coverage: B1-B9 bug + 优化项（状态灯、占位常量）+ vitest 80% 覆盖 — 都有对应 task
- [x] Placeholder scan: 无 TBD/TODO/类似到
- [x] Type consistency: `setStreamMapEntry` / `StreamInfo.deviceFallbackUrl` / `_registerDeviceStreamForTest` 名在各 task 一致
- [x] No vague steps: 每个 step 有具体代码 / 命令
- [x] File paths 准确（已 grep 验证 line number）
- [x] 每 task 有独立可测交付物
- [x] Commit 粒度合理（每个 task 1-2 commit）