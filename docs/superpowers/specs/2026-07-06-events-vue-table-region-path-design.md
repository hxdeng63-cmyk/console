# Events.vue 表格/卡片/详情弹窗区域显示大区/小区 — 设计

日期：2026-07-06
范围：单文件改造，零后端改动

## 背景

`/event-manage` 页面 Events.vue 在顶筛改 cascader 之后，表格/卡片/详情弹窗里的"区域"字段还停留在单层显示（只显示叶子 name，如"北区"），无法看出"大学城北 / 北区"这种大区/小区层级。

3 个位置都需要改：
- `Events.vue:83` el-table-column "区域"（表格模式）
- `Events.vue:124-127` 图片卡片"区域名称"
- `Events.vue:174-177` 详情弹窗"区域名称"

## 现状调研

- 后端 `/api/v1/algorithm-events` list 响应只返 `regionName`（string，无 regionId）
  - `algorithm_events.py:158-162` 只输出 `event.report_time.isoformat()` + `region.name`，**没有 regionId 字段**
- 前端 `Events.vue:405` 抓取 `item.region_name || item.regionName` 进 tableData
- 顶筛 `regionTree: ref<any[]>([])` 已是嵌套结构（公司→大区→小区，含 id/name/level/parent_id/children）

## 设计

### 文件改动

仅 `ai-console/src/views/Events.vue` 单文件。

### 1. 新增 computed（按 regionTree 生成 `name → path` map）

```ts
const regionPathMap = computed<Record<string, string>>(() => {
  const map: Record<string, string> = {}
  for (const big of regionTree.value) {
    if (!big) continue
    map[big.name] = big.name  // 选大区时，只显示大区名（无 children）
    for (const small of (big.children || [])) {
      map[small.name] = `${big.name} / ${small.name}`
    }
  }
  return map
})
```

**特点**：
- 纯前端，零后端改动
- 公司切换时 `regionTree` 重载，computed 自动 re-evaluate
- 选大区 → 显示"大学城北"；选小区 → 显示"大学城北 / 北区"
- 未知/历史数据（name 不在 map 中）→ 走 fallback

### 2. 模板改造（3 处）

#### `:83` 表格列（el-table-column）

```diff
- <el-table-column prop="regionName" label="区域" width="80" align="center" />
+ <el-table-column label="区域" min-width="120" align="center">
+   <template #default="{ row }">
+     <span>{{ regionPathMap[row.regionName] || row.regionName }}</span>
+   </template>
+ </el-table-column>
```

`width=80` 改为 `min-width=120`：拼接路径比单字宽，加 `min-width` 防列变形。

#### `:124-127` 图片卡片"区域名称"

```diff
- <span class="label">区域名称：</span>
- <span class="value">{{ item.regionName }}</span>
+ <span class="label">区域名称：</span>
+ <span class="value">{{ regionPathMap[item.regionName] || item.regionName }}</span>
```

#### `:174-177` 详情弹窗"区域名称"

```diff
- <span class="label">区域名称：</span>
- <span class="value">{{ currentRecord?.regionName }}</span>
+ <span class="label">区域名称：</span>
+ <span class="value">{{ regionPathMap[currentRecord?.regionName] || currentRecord?.regionName }}</span>
```

### 数据流

```
用户选公司 → onCompanyChange → GET /regions/tree?org_id=
   ↓
regionTree.value = [{ id, name: '大学城北', children: [{id, name: '北区'}, {id, name: '西区'}] }, ...]
   ↓
computed regionPathMap 自动 derive:
  { '大学城北': '大学城北', '北区': '大学城北 / 北区', '西区': '大学城北 / 西区', ... }
   ↓
表格行 row.regionName='北区' → {{ regionPathMap['北区'] }} → '大学城北 / 北区'
```

### 边界处理

| 场景 | 表现 |
|---|---|
| 公司未选 / regionTree 未加载 | map={}，所有行 fallback 显示 row.regionName（与原行为一致） |
| row.regionName 是 '未知区域'（老数据） | map 无 key，fallback 显示 '未知区域' |
| 选了大区（row.regionName='大学城北'） | map['大学城北']='大学城北'，不显示斜杠 |
| 选了小区（row.regionName='北区'） | map['北区']='大学城北 / 北区' |

### 验证

1. 浏览器 `/event-manage`
2. 选公司"海东公司" → regionTree 加载 → regionPathMap 自动生成
3. 表格"区域"列显示"海东公司 / 大学城北 / 北区"（列表原来显示'西区'，现在变成"大学城北 / 西区"或"大学城南 / 南区"）
4. 切换图片卡片模式，区域名称同样显示大区/小区
5. 点击"详情查看"弹窗，区域名称也是大区/小区
6. 改公司 → regionTree 重载 → map 重新生成 → 显示新公司的大区/小区
7. 重置筛选后表格区域保持大区/小区（因为 regionTree 还在）

### 范围控制

- ✗ 后端零改动
- ✗ 其它视图零影响
- ✗ 不引新 util（computed 内联在 Events.vue）

### 风险

- **低**：纯前端计算，不影响数据源；fallback 处理所有边界
- **中**：表格列宽变化（旧 80 → 120），可能影响其它列布局 — 用 `min-width` 而不是 `width` 缓解

### 测试

- vue-tsc 0 error
- 浏览器视觉：表格/卡片/详情 3 处一致显示 "大区 / 小区" 或 "大区"