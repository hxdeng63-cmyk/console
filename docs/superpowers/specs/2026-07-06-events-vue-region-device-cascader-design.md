# Events.vue 筛选区域/设备下拉改造 — 设计

日期：2026-07-06
范围：单文件改造，零后端改动

## 背景

`/event-manage` (Events.vue) 顶部筛选区：
- **区域** 当前是 `<el-select>` 单层 list（不含大学城南/北大区层级）
- **设备名称** 当前是 `<el-input>` 文本框（自由输入，模糊匹配）

需求：
1. 区域支持大区/小区两级联显示
2. 设备名改为下拉框选择

## 可复用 API（已存在，零后端改动）

| API | 路径 | 用途 |
|---|---|---|
| `GET /regions/tree?org_id=` | `backend/app/api/v1/regions.py:52-74` | 返回大区→小区层级树 |
| `GET /devices?region_id=&org_id=&keyword=` | `backend/app/api/v1/devices.py:13-55` | 按区域/公司筛设备 |
| `getRegionTree({ org_id })` | `ai-console/src/api/regions.ts:8` | 前端 wrapper（已声明未使用） |
| `getDevices({ region_id, ... })` | `ai-console/src/api/devices.js` | 前端 wrapper（已存在） |

后端 `algorithm_events.py` 已支持 `regionName`（自动 `_resolve_region_ids` 展开子）和 `deviceId`（精确过滤）参数，**无需改动**。

## 设计

### 文件改动

仅 `ai-console/src/views/Events.vue` 单文件。

### 1. 顶部 import

```ts
import { getRegionTree } from '@/api/regions'
import { getDevices } from '@/api/devices'  // 路径可能为 .js / .ts，按实际来
```

### 2. searchForm 字段调整（`:329-339`）

```diff
 const searchForm = reactive({
   companyName: '',
-  regionName: '',
+  regionId: null as number | null,    // el-cascader 选中叶子的 region.id
   algorithmName: '',
   eventType: '',
-  deviceName: '',
+  deviceId: null as number | null,    // el-select 选中的 device.id
   isCompliant: '',
   processStatus: '',
   startTime: '',
   endTime: ''
 })
```

### 3. 新增 data（state 区）

```ts
const regionTree = ref<any[]>([])  // 公司下大区→小区树
const regionDevices = ref<any[]>([])  // 当前选中 region 下的设备列表
```

### 4. onCompanyChange 重构（`:530-546`）

```ts
const onCompanyChange = async () => {
  searchForm.regionId = null
  searchForm.deviceId = null
  regionTree.value = []
  regionDevices.value = []
  if (!searchForm.companyName) return
  const company = companies.value.find((c: any) => c.name === searchForm.companyName)
  if (!company) return
  try {
    const res: any = await getRegionTree({ org_id: company.id })
    const data = res.data || res
    regionTree.value = data.items || data || []
  } catch (e) {
    console.error('获取区域树失败:', e)
  }
}
```

### 5. 新增 loadDevicesByRegion

```ts
const loadDevicesByRegion = async (regionId: number | null) => {
  regionDevices.value = []
  if (!regionId) return
  try {
    const res: any = await getDevices({ region_id: regionId, page_size: 100 })
    const data = res.data || res
    regionDevices.value = (data.items || data || []).map((d: any) => ({
      id: d.id,
      name: d.name
    }))
  } catch (e) {
    console.error('获取设备列表失败:', e)
  }
}

// 监听 regionId 变化
watch(() => searchForm.regionId, (newVal) => {
  searchForm.deviceId = null  // 清空设备选择
  loadDevicesByRegion(newVal)
})
```

### 6. 顶部"区域"UI（`:9-11`）替换

```diff
- <el-select v-model="searchForm.regionName" :placeholder="searchForm.companyName ? '区域' : '请先选择公司'" style="width: 120px" clearable :disabled="!searchForm.companyName">
-   <el-option v-for="r in companyRegions" :key="r.id" :label="r.name" :value="r.name" />
- </el-select>
+ <el-cascader
+   v-model="searchForm.regionId"
+   :options="regionTree"
+   :props="{ value: 'id', label: 'name', children: 'children', emitPath: false, checkStrictly: false }"
+   :placeholder="searchForm.companyName ? '区域（大区/小区）' : '请先选择公司'"
+   style="width: 180px"
+   clearable
+   :disabled="!searchForm.companyName"
+ />
```

`emitPath: false` 让 v-model 只绑叶子 region 的 id（不是路径数组），符合 searchForm.regionId 设计。

### 7. 顶部"设备名称"UI（`:28`）替换

```diff
- <el-input v-model="searchForm.deviceName" placeholder="设备名称" style="width: 160px" clearable />
+ <el-select
+   v-model="searchForm.deviceId"
+   placeholder="设备名称"
+   style="width: 180px"
+   clearable
+   filterable
+   :disabled="!searchForm.regionId"
+   no-data-text="请先选择区域"
+ >
+   <el-option v-for="d in regionDevices" :key="d.id" :label="d.name" :value="d.id" />
+ </el-select>
```

`filterable` 允许用户在长列表中搜索；`disabled` 当未选区域时强制要求先选区域。

### 8. handleSearch 序列化（`:362-380`）

```diff
 const handleSearch = async () => {
   currentPage.value = 1
   const params: any = {}
   if (searchForm.companyName) params.companyName = searchForm.companyName
-  if (searchForm.regionName) params.regionName = searchForm.regionName
+  // regionId 直接传给后端（最稳路径）；同时保留 regionName 走 _resolve_region_ids 自动展开子
+  if (searchForm.regionId) {
+    params.regionId = searchForm.regionId
+    // 也传 regionName 让后端 _resolve_region_ids 兜底（双保险）
+    // 找 cascader 当前 label
+  }
   if (searchForm.algorithmName) params.algorithmName = searchForm.algorithmName
   if (searchForm.eventType) params.eventType = searchForm.eventType
-  if (searchForm.deviceName) params.deviceName = searchForm.deviceName
+  if (searchForm.deviceId) params.deviceId = searchForm.deviceId
   ...
 }
```

**注意**：后端 `algorithm_events.py:list_algorithm_events` **目前没有 `regionId: int` 参数**！需要确认后端是否接受 regionId。

实际上根据 agent 报告，后端只接受 `companyName`、`regionName`、`deviceId`、`algorithmName`、`eventType`、`isCompliant`、`processStatus`、`startTime`、`endTime`。**没有 `regionId: int` 参数**。

那么两种选择：
- **A. 传 regionName**：cascader 绑 label（区域 name），后端 `_resolve_region_ids` 自动展开子
- **B. 后端加 regionId 参数**：1 行改动

考虑到改动最小，**选 A**：保持 regionName 传 name 路径。后端兼容。searchForm.regionId 只用于前端状态，不发给后端。

修正设计：

```diff
 // cascader 绑 value 而不是 id
-  v-model="searchForm.regionId"
+  v-model="searchForm.regionName"  // 存 cascader 最后一级 name（传给后端做解析）

 // 内部仍需 regionId 用于 loadDevicesByRegion（设备查询）
 const selectedRegionId = computed(() => {
   // walk regionTree to find node with name === searchForm.regionName
   // 简化：cascader 配 emitPath: false 时 v-model 是 leaf node 对象本身
 })
```

但 cascader 的 `emitPath: false` + `value: 'id'` 时，v-model 拿到的就是 id。所以可以：

```ts
// cascader 用 v-model="regionId"（id），handleSearch 时通过 regionTree 找到对应 name，传给后端
```

或更简单：用 cascader 的 `emitPath: true` + `value: 'id'`，v-model 就是 [大区id, 小区id] 数组，后端其实不支持。

最干净的方案：

```ts
// cascader 配置：
:props="{ value: 'id', label: 'name', children: 'children', emitPath: false }"
v-model="selectedRegion"  // 单个 id

// 同时维护一个 regionName 用于传给后端
const selectedRegion = ref<number | null>(null)
const selectedRegionName = ref<string>('')

// cascader @change 回调：拿到 { value: id, labelText: ['大学城北', '北区'] } 之类
@change="(val) => handleRegionChange(val)"

function handleRegionChange(id: number) {
  searchForm.regionId = id
  // walk regionTree to find name
  selectedRegionName.value = findNameInTree(regionTree.value, id) || ''
  loadDevicesByRegion(id)
}

// handleSearch:
if (selectedRegionName.value) params.regionName = selectedRegionName.value
```

或者更简单：用 cascader 的 `value: 'name'` 配置，v-model 直接拿 name。但 cascader 默认 v-model 是数组（路径），emitPath: false 时是叶子值。

**最终方案**：
```ts
// cascader 配置：
:props="{ value: 'name', label: 'name', children: 'children', emitPath: false }"
v-model="searchForm.regionName"  // 直接存 region name（叶子）

// 同时为设备加载，需要 id：
const onRegionChange = (name: string | null) => {
  // walk regionTree to find id by name
  searchForm.regionId = findIdByName(regionTree.value, name)
  loadDevicesByRegion(searchForm.regionId)
}
```

这样 searchForm.regionName 保留 string 类型（向后兼容），新增 regionId 用于设备查询。

**简化**：用 el-cascader 自带的 `@change` 事件拿 cascader 节点，然后从节点对象取 id。

### 9. handleReset

```diff
 const handleReset = () => {
   Object.assign(searchForm, {
     companyName: '',
-    regionName: '',
+    regionId: null,
-    deviceName: '',
+    deviceId: null,
     ...
   })
+  regionDevices.value = []
+  // cascader 通过 v-model 自动清空
 }
```

## 数据流

```
后端
  ├── GET /regions/tree?org_id=X  → 大区→小区 树 (regions.py:52)
  └── GET /devices?region_id=Y    → 设备列表    (devices.py:13)

Events.vue
  companyName  onCompanyChange
       │
       ▼
  regionTree (ref)  ←  /regions/tree?org_id=
       │
       ▼ el-cascader v-model (叶子 name)
  searchForm.regionName (string)
       │
       ▼ @change
  onRegionChange → walk tree → searchForm.regionId (number)
       │
       ▼ watch regionId
  loadDevicesByRegion → GET /devices?region_id=
       │
       ▼
  regionDevices (ref)
       │
       ▼ el-select v-model
  searchForm.deviceId (number)
       │
       ▼ handleSearch
  GET /algorithm-events?companyName=X&regionName=Y&deviceId=Z&...
```

## 不在范围

- 后端 `algorithm_events.py` 不动（用 regionName 路径，`_resolve_region_ids` 兼容）
- 其它视图（MonitorSingle/Wall 等）零影响
- el-input 改 el-select 不引入新依赖

## 验证

1. 浏览器 `/event-manage`
2. 选公司 → 区域 cascader 显示大区→小区两级（如"海东公司"→"大学城北"→"北区"）
3. 选具体区域 → 设备 select 自动加载该区域下设备
4. 选设备 → 查询 → 列表筛选生效
5. 改公司 → 区域 cascader 清空，设备 select 清空
6. 清空 → 重置 → 全部还原

## 风险

- 中等：searchForm regionName 改 storage 形式（保留 string），新增 regionId/deviceId 字段需小心现有引用
- 后端零改动

## 范围控制

- ✗ 不改后端
- ✗ 不改其它视图
- ✗ 不新建 util（直接调 @/api/regions 和 @/api/devices）
- ✗ 不引入新依赖