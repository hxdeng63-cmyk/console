# EventStats「算法子场景」中文化 — 设计

日期：2026-07-06
范围：单文件、最小改动

## 背景

`http://localhost:10073/event-stats` 中栏第二张卡片「算法子场景」（`EventStats.vue:57-66`），
x 轴直接渲染后端返回的英文 code（`jam` / `flow` / `vest` …），对运营/客户不友好。

## 现有可复用方法

`ai-console/src/utils/eventType.ts` 已暴露：

```ts
export const EVENT_TYPE_NAME_MAP: Record<string, string> = {
  jam: '交通阻塞', anomaly: '异常停车', flow: '流量统计',
  reverse: '逆向行驶', pedestrian: '行人闯入',
  accident: '疑似事故', vest: '反光衣检测'
}

export function getEventTypeDisplayName(name: string | undefined | null): string
```

未命中回退原值，空值返回 `'-'`。已被 7+ 视图复用（MonitorWall、MonitorSingle、FileAnalysis、Events.vue、LinkageRule 等），
最近 commit `9dd9e54 fix(wall): 报警事件类型中文化` 就是它的应用先例。

## 目标

仅「算法子场景」卡 x 轴柱状图显示中文，不改其他卡片。

## 非目标

- 不改后端 `EventType.name` / 不加 `name_cn` 列
- 不引入 vue-i18n
- 不中文化左栏「交通不合规检测」柱状图（同根因但用户明确选择不在本次范围）
- 不中文化「今日上报预警事件数」

## 设计

文件：`ai-console/src/views/event-stats/EventStats.vue`（757 行，唯一目标）

### 编辑 1 — import

在 `:121` 附近 import 区加：

```ts
import { getEventTypeDisplayName } from '@/utils/eventType'
```

### 编辑 2 — xAxis data wrap

`:382`：

```diff
-      data: sceneStats.value.categories,
+      data: sceneStats.value.categories.map(getEventTypeDisplayName),
```

### 编辑 3 — click handler 用 dataIndex 反查

`:408-414`：

```diff
   centerChart.on('click', (params: any) => {
-    if (params.name) {
-      selectedEventType.value = params.name
-      const item = sceneStats.value.items.find((i: { id: number; name: string; value: number }) => i.name === params.name)
-      filterForm.event_type_id = item?.id || null
+    if (typeof params.dataIndex === 'number') {
+      const item = sceneStats.value.items[params.dataIndex]
+      if (item) {
+        selectedEventType.value = getEventTypeDisplayName(item.name)
+        filterForm.event_type_id = item.id
+        fetchEventTrend().then(() => updateParkingChart())
+      }
     }
-    fetchEventTrend().then(() => updateParkingChart())
   })
```

**为什么换 `dataIndex`**：xAxis 改中文后 `params.name` 是中文，`items[i].name` 仍是英文 code，`===` 必失配 → `filterForm.event_type_id = null` → 趋势图查不到数据。
`params.dataIndex` 是 ECharts 给的下标，与 `sceneStats.value.items` 数组下标同源（后端 `/event-stats/scenes` 同序返回），可直接索引。

**为什么 wrap `selectedEventType`**：当前默认 `'异常停车'` 已是中文；click 后被 `params.name`（英文）覆盖会回到英文状态。统一 wrap 后顶部「X 趋势」标题（`:95`）始终中文。

## 数据流

```
EventType.name (EN, DB)         ← 不变
   ↓
/event-stats/scenes (backend)   ← 不变
   ↓
sceneStats.{categories,items}   ← 不变（仍是 EN code 数组）
   ↓
categories.map(getEventTypeDisplayName)  ← 编辑 2：UI 层映射
   ↓
ECharts xAxis 中文渲染           ← 编辑 2：可观察效果

click → params.dataIndex → items[dataIndex] → id 走原通路（filterForm.event_type_id）
```

后端通路、id/筛选参数、查询逻辑零变化。

## 错误处理

- `dataIndex` 越界：`items[dataIndex]` 为 `undefined`，内层 `if (item)` 守卫跳过 — 不写 `filterForm.event_type_id`，趋势图保持上次结果
- `dataIndex` 不是 number（罕见）：外层 `typeof === 'number'` 守卫跳过
- 字典未命中：`getEventTypeDisplayName` 回退原值，UI 仍显示英文 code（不报错）

## 验证

1. 启动前端 dev：`http://localhost:10073/event-stats`
2. 视觉确认：中栏第二张卡片 x 轴显示 `交通阻塞 / 异常停车 / 流量统计 / 逆向行驶 / 行人闯入 / 疑似事故 / 反光衣检测`
3. 点击任一柱子：右下方卡片标题从 `异常停车趋势` 切换为对应中文，`/event-stats/event-trend` 接口仍按 id 查询（DevTools Network 验证 `event_type_id` 为数字）
4. 趋势图正常渲染数据

## 风险

低。改动局限于 UI 渲染层；id/筛选/value 不变；后端零改动；数据库零迁移。

## 参考

- 字典：`ai-console/src/utils/eventType.ts:8-21`
- 应用先例 commit：`9dd9e54 fix(wall): 报警事件类型中文化`（改 `useDashboardPolling.ts:14,59`）
- 另一先例 commit：`80708b2 feat: 事件类型中文显示、实时监控修复及后端部署同步`