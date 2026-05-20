<template>
  <div class="device-group">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.name" placeholder="请输入设备名称" style="width: 180px" clearable />
        <el-select v-model="searchForm.company" placeholder="请选择公司" style="width: 160px" clearable>
          <el-option label="海东分公司" value="海东分公司" />
          <el-option label="西宁分公司" value="西宁分公司" />
        </el-select>
        <el-select v-model="searchForm.region" placeholder="请选择区域" style="width: 140px" clearable>
          <el-option label="S201" value="S201" />
          <el-option label="G213" value="G213" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增设备
        </el-button>
      </div>
    </div>

    <!-- 树形表格 -->
    <el-table :data="treeData" row-key="id" :default-expand-all="true" border stripe>
      <el-table-column label="名称" min-width="280">
        <template #default="{ row }">
          <span v-if="row.level === 'company'" class="node-company">{{ row.name }}</span>
          <span v-else-if="row.level === 'region'" class="node-region">{{ row.name }}</span>
          <span v-else class="node-device">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="健康状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.level === 'device'" :type="row.status === '在线' ? 'success' : 'danger'" size="small">
            {{ row.status }}
          </el-tag>
          <span v-else-if="row.level === 'region'" class="stats-text">{{ getRegionStats(row) }}</span>
          <span v-else-if="row.level === 'company'" class="stats-text">{{ getCompanyStats(row) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.level === 'device'">{{ row.remark || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
          <template v-if="row.level === 'device'">
            <el-button class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
            <el-button class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" :close-on-click-modal="false">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="设备名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="所属公司" prop="company">
          <el-select v-model="form.company" placeholder="请选择公司" style="width: 100%">
            <el-option label="海东分公司" value="海东分公司" />
            <el-option label="西宁分公司" value="西宁分公司" />
          </el-select>
        </el-form-item>
        <el-form-item label="所属区域" prop="region">
          <el-select v-model="form.region" placeholder="请选择区域" style="width: 100%">
            <el-option label="S201" value="S201" />
            <el-option label="G213" value="G213" />
          </el-select>
        </el-form-item>
        <el-form-item label="健康状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio label="在线">在线</el-radio>
            <el-radio label="离线">离线</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface DeviceItem {
  id: number
  name: string
  status: string
  region: string
  org: string
  remark: string
}

interface TreeNode {
  id: string
  name: string
  level: 'company' | 'region' | 'device'
  children?: TreeNode[]
  status?: string
  remark?: string
  _raw?: DeviceItem
}

// 参照数据源页面数据，按 org + region 分组
const rawData = ref<DeviceItem[]>([
  { id: 1, name: 'S201海东分公司K228+300下行(道路沿线)', status: '在线', region: 'S201', org: '海东分公司', remark: '道路沿线' },
  { id: 2, name: 'S201海东分公司K199+650上行(道路沿线)', status: '在线', region: 'S201', org: '海东分公司', remark: '道路沿线' },
  { id: 3, name: 'G213策磨高速乐化路段K16+250上行', status: '在线', region: 'G213', org: '海东分公司', remark: '隧道入口' },
  { id: 4, name: 'G213策磨高速乐化路段K10+150上行', status: '在线', region: 'G213', org: '海东分公司', remark: '互通立交' },
  { id: 5, name: 'G213策磨高速乐化路段K9+045下行', status: '离线', region: 'G213', org: '海东分公司', remark: '急弯路段' },
  { id: 6, name: 'S201海东分公司K195+700上行(道路沿线)', status: '在线', region: 'S201', org: '海东分公司', remark: '' },
  { id: 7, name: 'G213策磨高速乐化路段K8+150下行', status: '在线', region: 'G213', org: '海东分公司', remark: '' },
  { id: 8, name: 'S201西宁分公司K45+200上行(道路沿线)', status: '在线', region: 'S201', org: '西宁分公司', remark: '' },
  { id: 9, name: 'S201西宁分公司K38+600下行(道路沿线)', status: '在线', region: 'S201', org: '西宁分公司', remark: '' },
  { id: 10, name: 'G213策磨高速西宁段K89+100下行', status: '离线', region: 'G213', org: '西宁分公司', remark: '隧道出口' },
  { id: 11, name: '西宁分公司环城高速K120+500上行', status: '在线', region: 'G213', org: '西宁分公司', remark: '城市入口' },
  { id: 12, name: '西宁分公司环城高速K115+300下行', status: '在线', region: 'G213', org: '西宁分公司', remark: '' },
])

const searchForm = reactive({
  name: '',
  company: '',
  region: ''
})

function buildTree(devices: DeviceItem[]): TreeNode[] {
  const grouped: Record<string, Record<string, DeviceItem[]>> = {}
  devices.forEach(d => {
    if (!grouped[d.org]) grouped[d.org] = {}
    if (!grouped[d.org][d.region]) grouped[d.org][d.region] = []
    grouped[d.org][d.region].push(d)
  })

  return Object.entries(grouped).map(([org, regions], ci) => ({
    id: `c-${ci}`,
    name: org,
    level: 'company' as const,
    children: Object.entries(regions).map(([region, items], ri) => ({
      id: `c-${ci}-r-${ri}`,
      name: region,
      level: 'region' as const,
      children: items.map((d, di) => ({
        id: `c-${ci}-r-${ri}-d-${di}`,
        name: d.name,
        level: 'device' as const,
        status: d.status,
        remark: d.remark,
        _raw: d
      }))
    }))
  }))
}

const treeData = computed(() => {
  let filtered = rawData.value
  if (searchForm.name) {
    filtered = filtered.filter(d => d.name.includes(searchForm.name))
  }
  if (searchForm.company) {
    filtered = filtered.filter(d => d.org === searchForm.company)
  }
  if (searchForm.region) {
    filtered = filtered.filter(d => d.region === searchForm.region)
  }
  return buildTree(filtered)
})

const handleSearch = () => {
  // 搜索由 computed 自动触发
}

function getRegionStats(node: TreeNode): string {
  if (!node.children) return ''
  const online = node.children.filter(c => c.status === '在线').length
  const offline = node.children.filter(c => c.status === '离线').length
  return `在线${online}/离线${offline}`
}

function getCompanyStats(node: TreeNode): string {
  if (!node.children) return ''
  let online = 0, offline = 0
  node.children.forEach(region => {
    region.children?.forEach(d => {
      if (d.status === '在线') online++
      else offline++
    })
  })
  return `在线${online}/离线${offline}`
}

// 弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('新增设备')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  name: '',
  company: '海东分公司',
  region: 'S201',
  status: '在线' as string,
  remark: ''
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  company: [{ required: true, message: '请选择所属公司', trigger: 'change' }],
  region: [{ required: true, message: '请选择所属区域', trigger: 'change' }],
  status: [{ required: true, message: '请选择健康状态', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: TreeNode) => {
  if (type === 'add') {
    Object.assign(form, defaultForm())
    editingId.value = null
    dialogTitle.value = '新增设备'
  } else if (type === 'edit' && row?._raw) {
    editingId.value = row._raw.id
    dialogTitle.value = '编辑设备'
    Object.assign(form, {
      name: row._raw.name,
      company: row._raw.org,
      region: row._raw.region,
      status: row._raw.status,
      remark: row._raw.remark
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingId.value) {
    const idx = rawData.value.findIndex(item => item.id === editingId.value)
    if (idx !== -1) {
      Object.assign(rawData.value[idx], {
        name: form.name,
        org: form.company,
        region: form.region,
        status: form.status,
        remark: form.remark
      })
    }
    ElMessage.success('编辑成功')
  } else {
    rawData.value.push({
      id: Date.now(),
      name: form.name,
      org: form.company,
      region: form.region,
      status: form.status,
      remark: form.remark
    })
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
}

const handleDelete = (row: TreeNode) => {
  if (!row._raw) return
  ElMessageBox.confirm(`确定删除设备 "${row._raw.name}" 吗？`, '提示', { type: 'warning' })
    .then(() => {
      const idx = rawData.value.findIndex(item => item.id === row._raw!.id)
      if (idx !== -1) rawData.value.splice(idx, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
</script>

<style scoped>
.device-group {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.search-area {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.search-area .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.search-area .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.action-area .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.action-area .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

/* 树形节点样式 */
.node-company {
  font-weight: 700;
  font-size: 14px;
  color: #00E5FF;
}

.node-region {
  font-weight: 600;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  background: rgba(0, 229, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.node-device {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
}

.stats-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

/* 操作按钮 - 编辑（青色） */
.action-edit {
  background: rgba(0, 229, 255, 0.15) !important;
  border: 1px solid rgba(0, 229, 255, 0.4) !important;
  color: #00E5FF !important;
  border-radius: 4px;
  padding: 6px 10px !important;
  font-weight: 600;
  text-shadow: none;
  box-shadow: none;
}

.action-edit:hover {
  background: rgba(0, 229, 255, 0.25) !important;
  border-color: #00E5FF !important;
  color: #00FF88 !important;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.3);
}

/* 操作按钮 - 删除（粉红） */
.action-delete {
  background: rgba(255, 0, 110, 0.15) !important;
  border: 1px solid rgba(255, 0, 110, 0.4) !important;
  color: #FF006E !important;
  border-radius: 4px;
  padding: 6px 10px !important;
  font-weight: 600;
  text-shadow: none;
  box-shadow: none;
}

.action-delete:hover {
  background: rgba(255, 0, 110, 0.25) !important;
  border-color: #FF006E !important;
  color: #FF4D6D !important;
  box-shadow: 0 0 12px rgba(255, 0, 110, 0.3);
}
</style>
