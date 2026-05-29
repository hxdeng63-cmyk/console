<template>
  <div class="device-group">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.name" placeholder="请输入设备名称" style="width: 180px" clearable />
        <el-select v-model="searchForm.company" placeholder="请选择公司" style="width: 160px" clearable @change="onCompanyChange">
          <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="searchForm.region" placeholder="请选择大区域" style="width: 140px" clearable @change="onRegionChange">
          <el-option v-for="r in filteredLevel1" :key="r.id" :label="r.name" :value="r.id" />
        </el-select>
        <el-select v-model="searchForm.subRegion" placeholder="请选择小区域" style="width: 140px" clearable>
          <el-option v-for="r in filteredLevel2" :key="r.id" :label="r.name" :value="r.id" />
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
    <el-table :data="filteredTree" row-key="id" :default-expand-all="true" border stripe>
      <el-table-column label="名称" min-width="280">
        <template #default="{ row }">
          <span v-if="row.isCompany" class="node-company">{{ row.name }}</span>
          <span v-else-if="row.isRegion && row.regionLevel === 1" class="node-region-l1">{{ row.name }}</span>
          <span v-else-if="row.isRegion && row.regionLevel === 2" class="node-region-l2">{{ row.name }}</span>
          <span v-else class="node-device">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column label="健康状态" width="120" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.isDevice" :type="row.status === 'active' ? 'success' : 'danger'" size="small">
            {{ row.status === 'active' ? '在线' : '离线' }}
          </el-tag>
          <span v-else-if="row.device_count !== undefined" class="stats-text">设备{{ row.device_count }}台</span>
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.isDevice">{{ row.remark || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
          <template v-if="row.isDevice">
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
        <el-form-item label="所属公司" prop="org_id">
          <el-select v-model="form.org_id" placeholder="请选择公司" style="width: 100%" @change="onFormCompanyChange">
            <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="大区域" prop="region_id_l1">
          <el-select v-model="form.region_id_l1" placeholder="请选择大区域" style="width: 100%" @change="onFormRegionChange">
            <el-option v-for="r in formLevel1" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="小区域" prop="region_id">
          <el-select v-model="form.region_id" placeholder="请选择小区域" style="width: 100%">
            <el-option v-for="r in formLevel2" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="健康状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">在线</el-radio>
            <el-radio value="inactive">离线</el-radio>
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
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRegions } from '@/composables/useRegions'
import { getDeviceGroupTree } from '@/api/device-groups'
import { createDevice, updateDevice, deleteDevice } from '@/api/devices'

interface TreeNode {
  id: number | string
  name: string
  isCompany?: boolean
  isRegion?: boolean
  isDevice?: boolean
  regionLevel?: number
  status?: string
  remark?: string
  device_count?: number
  children?: TreeNode[]
  org_id?: number
  region_id?: number
  device_code?: string
}

const { companies, level1Regions, allRegions, loadRegions } = useRegions()

const rawTree = ref<TreeNode[]>([])
const loading = ref(false)

const searchForm = reactive({
  name: '',
  company: null as number | null,
  region: null as number | null,
  subRegion: null as number | null,
})

onMounted(async () => {
  await loadRegions()
  await fetchTree()
})

async function fetchTree() {
  loading.value = true
  try {
    const data = await getDeviceGroupTree()
    rawTree.value = normalizeTree(data || [])
  } catch (e) {
    console.error('Failed to load device group tree:', e)
    rawTree.value = []
  } finally {
    loading.value = false
  }
}

function normalizeTree(nodes: any[]): TreeNode[] {
  return nodes.map(n => ({
    id: n.id,
    name: n.name,
    isCompany: !!n.isCompany,
    isRegion: !!n.isRegion,
    isDevice: n.level === 'device',
    regionLevel: n.isRegion ? n.level : undefined,
    status: n.status,
    remark: n.remark,
    device_count: n.device_count,
    org_id: n.org_id,
    region_id: n.region_id,
    device_code: n.device_code,
    children: n.children ? normalizeTree(n.children) : [],
  }))
}

const filteredLevel1 = computed(() => {
  if (!searchForm.company) return level1Regions.value
  const org = companies.value.find(c => c.id === searchForm.company)
  if (!org) return level1Regions.value
  return level1Regions.value.filter(r => r.org_id === org.id)
})

const filteredLevel2 = computed(() => {
  if (searchForm.region) return allRegions.value.filter(r => r.parent_id === searchForm.region)
  if (searchForm.company) {
    const org = companies.value.find(c => c.id === searchForm.company)
    if (!org) return []
    const l1Ids = level1Regions.value.filter(r => r.org_id === org.id).map(r => r.id)
    return allRegions.value.filter(r => r.level === 2 && l1Ids.includes(r.parent_id!))
  }
  return allRegions.value.filter(r => r.level === 2)
})

function onCompanyChange() {
  searchForm.region = null
  searchForm.subRegion = null
}

function onRegionChange() {
  searchForm.subRegion = null
}

function filterTree(nodes: TreeNode[]): TreeNode[] {
  return nodes.reduce<TreeNode[]>((acc, node) => {
    if (node.isDevice) {
      if (matchesSearch(node)) {
        acc.push({ ...node })
      }
    } else if (node.isCompany) {
      const filteredChildren = filterTree(node.children || [])
      if (filteredChildren.length > 0) {
        acc.push({ ...node, children: filteredChildren })
      }
    } else if (node.isRegion) {
      const filteredChildren = filterTree(node.children || [])
      if (filteredChildren.length > 0 || matchesRegionFilter(node)) {
        acc.push({ ...node, children: filteredChildren })
      }
    }
    return acc
  }, [])
}

function matchesSearch(device: TreeNode): boolean {
  if (searchForm.name && !device.name?.includes(searchForm.name)) return false
  return true
}

function matchesRegionFilter(node: TreeNode): boolean {
  if (searchForm.subRegion && node.id !== searchForm.subRegion) return false
  return true
}

const filteredTree = computed(() => {
  if (!searchForm.name && !searchForm.company && !searchForm.region && !searchForm.subRegion) {
    return rawTree.value
  }
  return filterTree(rawTree.value)
})

const handleSearch = () => {
  // 搜索由 computed filteredTree 自动触发
}

// 弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('新增设备')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  name: '',
  org_id: null as number | null,
  region_id_l1: null as number | null,
  region_id: null as number | null,
  status: 'active' as string,
  remark: '',
})

const form = reactive(defaultForm())

const formLevel1 = computed(() => {
  if (!form.org_id) return []
  return level1Regions.value.filter(r => r.org_id === form.org_id)
})

const formLevel2 = computed(() => {
  if (!form.region_id_l1) return []
  return allRegions.value.filter(r => r.parent_id === form.region_id_l1)
})

function onFormCompanyChange() {
  form.region_id_l1 = null
  form.region_id = null
}

function onFormRegionChange() {
  form.region_id = null
}

const rules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  org_id: [{ required: true, message: '请选择所属公司', trigger: 'change' }],
  region_id_l1: [{ required: true, message: '请选择大区域', trigger: 'change' }],
  region_id: [{ required: true, message: '请选择小区域', trigger: 'change' }],
  status: [{ required: true, message: '请选择健康状态', trigger: 'change' }],
}

const openModal = (type: 'add' | 'edit', row?: TreeNode) => {
  if (type === 'add') {
    Object.assign(form, defaultForm())
    editingId.value = null
    dialogTitle.value = '新增设备'
  } else if (type === 'edit' && row) {
    editingId.value = row.id as number
    dialogTitle.value = '编辑设备'
    const region = allRegions.value.find(r => r.id === row.region_id)
    Object.assign(form, {
      name: row.name,
      org_id: row.org_id,
      region_id_l1: region?.parent_id || null,
      region_id: row.region_id,
      status: row.status,
      remark: row.remark,
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  const payload = {
    name: form.name,
    device_code: `DEV-${Date.now()}`,
    status: form.status,
    remark: form.remark,
    region_id: form.region_id,
    org_id: form.org_id,
  }

  try {
    if (editingId.value) {
      await updateDevice(editingId.value, payload)
      ElMessage.success('编辑成功')
    } else {
      await createDevice(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await fetchTree()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

const handleDelete = (row: TreeNode) => {
  ElMessageBox.confirm(`确定删除设备 "${row.name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteDevice(row.id as number)
        ElMessage.success('删除成功')
        await fetchTree()
      } catch (e: any) {
        ElMessage.error(e?.message || '删除失败')
      }
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

.node-company {
  font-weight: 700;
  font-size: 14px;
  color: #00E5FF;
}

.node-region-l1 {
  font-weight: 600;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  background: rgba(0, 229, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.node-region-l2 {
  font-weight: 500;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.75);
  background: rgba(0, 229, 255, 0.05);
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
