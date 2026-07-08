# 数字大屏修复 + 优化 — 设计

日期：2026-07-08
范围：纯前端修复 + 优化 + 引入 vitest。零后端改动。

## 背景

### 症状（已确认）

数字大屏（`/monitor/wall` 路由，组件 `MonitorWall.vue`）打开后**视频区黑屏**。右栏数据、事件轮播、布控信息等正常。

### 根因链（已通过代码层确认）

```
1. onMounted 默认选第一个设备
   └─ MonitorWall.vue:528 调 registry.registerDeviceStream(rid)  [单条注册]

2. 单条注册路径写 streamMap 时缺失 deviceFallbackUrl 字段
   └─ useStreamRegistry.ts:85-91
      streamMap[device-X] = { url, sourceType }     // 没有 deviceFallbackUrl!

3. 用户进入大屏未选算法 (selectedAlgorithm='')
   └─ useCurrentStream.ts:32-38 hasAlgorithm=false
      → 取 deviceFallbackUrl，但缺失 → fallback = undefined → 返回空串 ''

4. currentVideoUrl = '' → VideoStage 拿到空 url → 黑屏/无法连接提示
```

附带 4 处**同源 bug**（写 streamMap 时丢 deviceFallbackUrl）：
- `MonitorWall.vue:416` `refreshStreamUrlSync`（HLS 致命错误回调）
- `MonitorWall.vue:444` `refreshStreamMap`
- `MonitorWall.vue:474` `selectedChannel` watch
- `MonitorWall.vue:506` `selectedAlgorithm` watch

5 处代码模板完全相同：`{ url: info.flv_url, sourceType: info.source_type || 'stream' }` —— 缺少 `deviceFallbackUrl` 字段。

### 附带占位 bug

| 行 | 占位 | 真实数据源 |
|---|---|---|
| `MonitorWall.vue:67` | `<LevelIndicator :value="6" :max="10">` 能见度等级写死 | 无（API_SERVICE(5).md 无 visibility 字段） |
| `MonitorWall.vue:85` | `<span class="status-tag online">在线</span>` 视频质量检测 | 无（API_SERVICE(5).md 无 video_quality） |
| `useDashboardPolling.ts:163` | `avgSpeed: '--'` 写死 | flow.class_flows 只给车辆计数，不给速度 |
| `MonitorWall.vue:198` | `path.join('-').replace('-', ' ')` 字符串只替第一个 `-` | — |

### 历史 fix 链路脆弱

20 commits 中 7 个 fix(wall)/fix(monitor)，集中在"流协议 + token + 黑屏"。说明该模块流链路一直脆弱，本次修复需要一次性收敛。

## 设计

### 核心修复策略：抽 `setStreamMapEntry` helper

**根除 5 处复制粘贴**：所有 streamMap 写入强制走同一函数，不可能漏 `deviceFallbackUrl`。

```ts
// useStreamRegistry.ts 新增（私有，不 export）
function setStreamMapEntry(
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
      // 允许 null 显式表达"无兜底"；undefined 留给"未传"
      deviceFallbackUrl: info.deviceFallbackUrl ?? null,
    },
  }
}
```

**调用点统一**：5 处全部改用 `setStreamMapEntry`。

`StreamInfo` 接口扩展（`useStreamRegistry.ts:5-11`）：

```ts
export interface StreamInfo {
  url: string
  sourceType: string
  /** 本地 fallback mp4 路径(HLS 失败时用); null = 后端未返; undefined = 未传。 */
  deviceFallbackUrl?: string | null
}
```

### 文件改动清单

#### 1. `ai-console/src/composables/useStreamRegistry.ts`

- 新增 `setStreamMapEntry` 私有函数
- 扩展 `StreamInfo.deviceFallbackUrl` 允许 `string | null | undefined`
- `registerDeviceStream`（单条）line 85-91：改用 `setStreamMapEntry`，传入 `device_fallback_url`
- `registerDeviceStreams`（批量）line 115-119：同样改用 helper（行为等价，但消除模板）

#### 2. `ai-console/src/views/monitor/MonitorWall.vue`

- Line 416（`refreshStreamUrlSync`）：改用 `setStreamMapEntry`，**传入 `deviceFallbackUrl: info.device_fallback_url ?? null`**
- Line 444（`refreshStreamMap`）：同上
- Line 474（`selectedChannel` watch）：同上
- Line 506（`selectedAlgorithm` watch）：同上
- Line 198（`parseRawChannelId` / device tree 收集）：`.replace('-', ' ')` → `.replaceAll('-', ' ')`
- Line 67（`<LevelIndicator :value="6" :max="10">`）：改 `:value="visibilityLevel"` 接 `useDashboardPolling` 新增字段；fallback 为 `null` 时显示 `--` + "采集中" 角标
- Line 85（视频质量检测 "在线"）：改为基于 `useVideoPlayer` 的 `hasError`/`errorMessage` + WS 连接状态推断：`hasError ? '异常' : '在线'`；增加 `warning` / `offline` 状态样式（CSS 已有 `.status-tag.offline` `.status-tag.warning` 占位）

#### 3. `ai-console/src/composables/useDashboardPolling.ts`

- Line 163 `statsData` 默认值扩展 `visibilityLevel: null`
- 新增 `fetchVisibility` 占位实现：`try` traffic-api `GET /api/visibility?device_id=` 推断；无接口则保持 `null`
- `avgSpeed` 计算：若 traffic-api `GET /api/flow` 返回 speed 字段则使用；否则保持 `'--'`

#### 4. `ai-console/src/components/dashboard/VideoStage.vue`

- 加状态灯（右上角小圆点，颜色映射：HLS 连接中/FLV 连接中/MP4 fallback/错误）
- 错误提示区增加：状态码（如 `403` / `404` / `NETWORK`）+ 当前协议文字（HLS/FLV/MP4）+ 重试按钮（已有 retry()，暴露给 UI）
- loading 时显示"正在加载 ({protocol})..."

#### 5. 测试

引入 `vitest`：
- `package.json` 新增 devDeps: `vitest@^2`，`@vue/test-utils@^2`，`happy-dom@^15`
- `vitest.config.ts` 新建（happy-dom 环境 + `@/` alias）
- `npm run test` script

#### 6. 测试文件

按 C2 范围（大屏相关所有 composable 80% 行覆盖）：

| 测试文件 | 覆盖目标 |
|---|---|
| `useStreamRegistry.test.ts` | `setStreamMapEntry`、`registerDeviceStream`/`registerDeviceStreams` 写入 streamMap 必带 `deviceFallbackUrl`（null/undefined 处理）、404 清理 |
| `useCurrentStream.test.ts` | `hasAlgorithm=true/false` × `deviceFallbackUrl` 有/无/null 六象限（4 种业务路径）；`currentProtocol` 空串 fallback |
| `useVideoPlayer.test.ts` | `setProtocol`、`switchUrl`、`initNativeFallback` 调用路径；HLS 错误计数（3 次后切 fallback） |
| `useDashboardPolling.test.ts` | `avgSpeed` 拉取路径（mock fetch 成功 / 失败 / 无字段）；`visibilityLevel` 拉取 |
| `useTaskPolling.test.ts` | start/stop poll 状态机 |
| `useStopPoll.test.ts` | start/poll 状态机 |
| `useVisibilityResume.test.ts` | document 可见性变化时 pause/resume |
| `utils/streamUrl.test.ts` | `isLocalStream`、`withCacheBuster`、`pathOnly` |
| `utils/eventType.test.ts` | `getEventTypeDisplayName` 中英文映射 |

## 数据流

```
onMounted → fetchDeviceTree() → 默认 selectedChannel
  ├─ registerDeviceStreams(rawIds)        [批量] → setStreamMapEntry(..., deviceFallbackUrl) ✓
  └─ registerDeviceStream(rid.toString())  [单条] → setStreamMapEntry(..., deviceFallbackUrl) ✓ [修]

selectedChannel/selectedAlgorithm 变化
  → getDeviceFlvUrl(rid) → setStreamMapEntry(prev, rid, info) ✓ [统一 4 处]

HLS NETWORK_ERROR → refreshStreamUrlSync() → setStreamMapEntry ✓

算法启动成功 → onSuccess → setStreamMapEntry ✓

useCurrentStream.currentVideoUrl:
  hasAlgorithm=false → deviceFallbackUrl 有则用；null → 空串（VideoStage 显示"暂无预览"）
  hasAlgorithm=true  → streamMap.url（HLS/FLV）
```

## 错误处理

| 场景 | 行为 |
|---|---|
| 后端无 `device_fallback_url` | `null`（显式），VideoStage 显示"暂无预览"占位 |
| HLS 3 次失败 + 有 fallback | 切 `initNativeFallback`（已有行为） |
| HLS 3 次失败 + 无 fallback | VideoStage 显示"无可用流，请检查设备" + 重试按钮（已有 retry） |
| 单条注册失败 | 该设备 streamError=true，**不影响其他设备** |
| 404 设备未注册 | streamMap 删条目（已有行为） |
| VideoStage 加载协议显示 | `loading + "{protocol}"`（如 "正在加载 (HLS)..."） |

## 测试策略

- **单元测试**（vitest）：9 个测试文件，目标 80% 行覆盖（聚焦大屏相关 composable + utils）
- **手动验证**：浏览器 DevTools 跑一遍：
  - F5 刷新 → 视频区应在 1-2s 内出画面
  - 切换通道 → 新视频加载
  - 选算法 → 启动监测 → 视频流切换 HLS，bbox 出现
  - 模拟 token 失效（手动删 streamMap）→ 看到 fallback mp4
  - 404 设备 → VideoStage 显示错误提示 + 重试按钮可点
  - console.warn 不应再出现 "[MonitorWall] 拉取最新 flv_url 失败"

不写 e2e（项目无 playwright runner）。

## 验收

```bash
# 1. 类型 + 单测
cd ai-console && npm run type-check && npm run test
# 期望: 9 个测试文件全过，覆盖率 ≥80% (大屏相关 composable)

# 2. 浏览器 DevTools 手动
# - 打开 http://localhost:10073/monitor/wall
# - 默认视频 ≤2s 出画面（mp4 兜底）
# - 选算法 + 开始监测 → HLS 流，bbox 出现
# - 切换通道 → 视频重载 ≤1s
# - 模拟 streamMap 失效 → fallback mp4 自动接管
# - console 无 [MonitorWall] 警告
```

## 范围之外

- ❌ 后端 API 变更（visibility / avg_speed / video_quality 字段 → spec 的 Follow-ups）
- ❌ 新功能（地图/AI 概览/设备健康度面板等 → 用户选 B 范围）
- ❌ 大屏布局重构
- ❌ 引新外部依赖（除 vitest 测试栈）
- ❌ `MonitorSingle.vue`（共用 composable 但本次聚焦 MonitorWall；后续可复用 helper）

## 风险

| 风险 | 缓解 |
|---|---|
| `setStreamMapEntry` 是新建辅助函数 | 行为完全等价现有 5 处 spread，单元测试覆盖关键路径 |
| B8 `.replaceAll` 字符串变化 | grep 所有 `parseRawChannelId` 消费的 `name` 字段验证显示效果 |
| vitest 是新引入 | 仅 devDeps，不影响生产 bundle；package.json scripts 新增 `test` / `test:coverage` |
| 80% 覆盖率是承诺 | 范围限定大屏相关 composable，避免对整个 src/ 的过度承诺 |
| visibility/quality 真正接口不存在 | 占位 + "采集中" 角标，不阻塞本次交付 |

## Follow-ups（不在本次 spec）

1. 后端补 `visibility` / `video_quality` 接口，前端从占位切真实
2. `MonitorSingle.vue` 同步应用 `setStreamMapEntry` helper
3. 大屏新功能：设备健康度面板 / TOP 拥堵路段 / 异常事件地理分布
4. e2e 测试（playwright）
5. WS 重连策略（断线后自动重连 + 状态灯联动）