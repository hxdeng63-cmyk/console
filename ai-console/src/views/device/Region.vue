<template>
  <div class="region-manage">
    <div class="region-content">
      <!-- 左侧：区域树 -->
      <div class="region-tree-panel">
        <div class="tree-header">
          <span class="tree-title">区域树形图</span>
          <div class="header-actions">
            <el-button type="default" size="small" @click="onRefresh">
              <el-icon><RefreshRight /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="tree-body" v-loading="loading">
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="{ children: 'children', label: 'name' }"
            node-key="id"
            :expand-on-click-node="false"
            :default-expand-all="true"
            @node-click="onNodeClick"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node" :class="{ selected: selectedNode?.id === data.id }">
                <span class="node-label">
                  <el-icon v-if="data.isCompany" class="node-icon"><OfficeBuilding /></el-icon>
                  <el-icon v-else class="node-icon"><Location /></el-icon>
                  <span>{{ node.label }}</span>
                  <span v-if="data.deviceCount !== undefined" class="device-count">({{ data.deviceCount }}台)</span>
                </span>
                <span class="node-actions">
                  <el-button v-if="!data.isRegion || data.level === 1" link class="tree-btn" @click.stop="handleAdd(data)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button link class="tree-btn" @click.stop="handleEdit(data)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button link class="tree-btn" @click.stop="handleDelete(data)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </span>
              </span>
            </template>
          </el-tree>
        </div>
      </div>

      <!-- 右侧：详情 -->
      <div class="region-detail-panel">
        <div v-if="!selectedNode" class="detail-placeholder">
          <p>选择左侧区域查看详情</p>
        </div>
        <div v-else class="detail-form">
          <h3 class="detail-title">详情</h3>
          <el-form :model="detailForm" label-width="100px">
            <el-form-item label="类型">
              <el-input :model-value="detailForm.typeText" disabled />
            </el-form-item>
            <el-form-item v-if="detailForm.parentName" label="上级">
              <el-input v-model="detailForm.parentName" disabled />
            </el-form-item>
            <el-form-item label="名称" required>
              <el-input v-model="detailForm.name" placeholder="请输入名称" />
            </el-form-item>
            <el-form-item v-if="!detailForm.isCompany" label="编码">
              <el-input v-model="detailForm.code" placeholder="请输入编码" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="detailForm.remark" type="textarea" placeholder="请输入备注" :rows="3" />
            </el-form-item>
            <el-form-item label="排序值">
              <el-input-number v-model="detailForm.sortOrder" :min="0" :max="999" />
            </el-form-item>
          </el-form>
          <div class="detail-footer">
            <el-button @click="selectedNode = null">取消</el-button>
            <el-button type="primary" @click="handleSave">确定</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="编码">
          <el-input v-model="form.code" placeholder="请输入编码，如 S201" />
        </el-form-item>
        <el-form-item label="所属公司" prop="orgId">
          <el-select v-model="form.orgId" placeholder="请选择所属公司" style="width: 100%">
            <el-option v-for="c in companyList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="上级区域">
          <el-select v-model="form.parentId" placeholder="不选则为一级区域" clearable style="width: 100%">
            <el-option v-for="r in level1RegionList" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" :rows="3" />
        </el-form-item>
        <el-form-item label="排序值">
          <el-input-number v-model="form.sortOrder" :min="0" :max="999" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ElTree } from 'element-plus'
import {
  RefreshRight,
  Plus,
  Edit,
  Delete,
  OfficeBuilding,
  Location
} from '@element-plus/icons-vue'
import { getFullRegionTree, createRegion, updateRegion, deleteRegion } from '@/api/regions'

interface RegionNode {
  id: number
  name: string
  code?: string
  remark?: string
  sortOrder?: number
  deviceCount?: number
  isCompany?: boolean
  isRegion?: boolean
  level?: number
  orgId?: number
  parentId?: number
  children?: RegionNode[]
}

const treeRef = ref<InstanceType<typeof ElTree>>()
const loading = ref(false)
const treeData = ref<RegionNode[]>([])

const sumDevices = (nodes: RegionNode[]): number => {
  return nodes.reduce((sum, n) => sum + (n.deviceCount || 0), 0)
}

const mapApiNode = (node: any): RegionNode => {
  const children = node.children?.map(mapApiNode)
  const mapped: RegionNode = {
    id: node.id,
    name: node.name,
    code: node.code,
    remark: node.remark,
    sortOrder: node.sort,
    deviceCount: node.device_count ?? 0,
    isCompany: node.isCompany,
    isRegion: node.isRegion,
    level: node.level,
    orgId: node.org_id,
    parentId: node.parent_id,
    children
  }
  if (node.isCompany && children) {
    mapped.deviceCount = sumDevices(children)
  }
  return mapped
}

const loadTreeData = async () => {
  loading.value = true
  try {
    const res = await getFullRegionTree()
    treeData.value = (res || []).map(mapApiNode)
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '加载区域数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTreeData()
})

const selectedNode = ref<RegionNode | null>(null)
const detailForm = reactive({
  typeText: '',
  isCompany: false,
  parentName: '',
  name: '',
  code: '',
  remark: '',
  sortOrder: 0,
  orgId: undefined as number | undefined
})

const dialogVisible = ref(false)
const dialogTitle = ref('添加区域')
const formRef = ref()
const editingNode = ref<RegionNode | null>(null)
const isEditing = ref(false)

const form = reactive({
  orgId: undefined as number | undefined,
  parentId: undefined as number | undefined,
  name: '',
  code: '',
  remark: '',
  sortOrder: 0
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const companyList = computed(() => treeData.value.filter(n => n.isCompany))

const level1RegionList = computed(() => {
  const regions: RegionNode[] = []
  const collect = (nodes: RegionNode[]) => {
    for (const node of nodes) {
      if (node.isRegion && node.level === 1) regions.push(node)
      if (node.children) collect(node.children)
    }
  }
  collect(treeData.value)
  return regions
})

const getParentName = (nodeId: number, nodes: RegionNode[] = treeData.value): string | null => {
  for (const node of nodes) {
    if (node.children?.some(child => child.id === nodeId)) return node.name
    if (node.children) {
      const found = getParentName(nodeId, node.children)
      if (found) return found
    }
  }
  return null
}

const onNodeClick = (data: RegionNode) => {
  selectedNode.value = data
  detailForm.isCompany = !!data.isCompany
  detailForm.typeText = data.isCompany ? '公司' : '区域'
  detailForm.parentName = getParentName(data.id) || ''
  detailForm.name = data.name
  detailForm.code = data.code || ''
  detailForm.remark = data.remark || ''
  detailForm.sortOrder = data.sortOrder || 0
  detailForm.orgId = data.orgId
}

const onRefresh = () => {
  loadTreeData()
  ElMessage.success('刷新成功')
}

const handleAdd = (data: RegionNode) => {
  editingNode.value = null
  isEditing.value = false
  dialogTitle.value = data.isCompany ? '添加区域' : '添加子区域'
  if (data.isCompany) {
    form.orgId = data.id
    form.parentId = undefined
  } else {
    form.orgId = data.orgId
    form.parentId = data.id
  }
  form.name = ''
  form.code = ''
  form.remark = ''
  form.sortOrder = 0
  dialogVisible.value = true
}

const handleEdit = (data: RegionNode) => {
  if (data.isCompany) {
    ElMessage.warning('公司信息请在组织架构管理中修改')
    return
  }
  editingNode.value = data
  isEditing.value = true
  dialogTitle.value = '编辑区域'
  form.name = data.name
  form.code = data.code || ''
  form.remark = data.remark || ''
  form.sortOrder = data.sortOrder || 0
  form.orgId = data.orgId
  form.parentId = data.parentId
  dialogVisible.value = true
}

const handleDelete = async (data: RegionNode) => {
  if (data.isCompany) {
    ElMessage.warning('公司请在组织架构管理中删除')
    return
  }
  const warnText = data.children?.length ? `，其下 ${data.children.length} 个子区域将一并被处理` : ''
  try {
    await ElMessageBox.confirm(`确定删除区域 "${data.name}" 吗？${warnText}`, '提示', { type: 'warning' })
    await deleteRegion(data.id)
    ElMessage.success('删除成功')
    await loadTreeData()
    if (selectedNode.value?.id === data.id) selectedNode.value = null
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '删除失败')
    }
  }
}

const handleConfirm = async () => {
  const valid = await (formRef.value as any)?.validate().catch(() => false)
  if (!valid) return
  if (!form.parentId && !form.orgId) {
    ElMessage.error('一级区域必须选择所属公司')
    return
  }
  const payload = {
    name: form.name,
    code: form.code || null,
    remark: form.remark || null,
    sort: form.sortOrder,
    org_id: form.orgId || null,
    parent_id: form.parentId || null
  }
  try {
    if (isEditing.value && editingNode.value) {
      await updateRegion(editingNode.value.id, payload)
      ElMessage.success('保存成功')
    } else {
      await createRegion(payload)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await loadTreeData()
    selectedNode.value = null
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

const handleSave = async () => {
  if (!selectedNode.value) return
  if (selectedNode.value.isCompany) {
    ElMessage.warning('公司信息请在组织架构管理中修改')
    return
  }
  const payload = {
    name: detailForm.name,
    code: detailForm.code || null,
    remark: detailForm.remark || null,
    sort: detailForm.sortOrder,
    org_id: selectedNode.value.orgId || null,
    parent_id: selectedNode.value.parentId || null
  }
  try {
    await updateRegion(selectedNode.value.id, payload)
    ElMessage.success('保存成功')
    await loadTreeData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  }
}
</script>

<style scoped>
.region-manage {
  padding: 20px;
  height: 100%;
}

.region-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
}

.region-tree-panel {
  width: 400px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.tree-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tree-title {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
}

.header-actions :deep(.el-button) {
  padding: 4px 8px;
}

.tree-body {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.tree-body :deep(.el-tree) {
  background: transparent;
}

.tree-body :deep(.el-tree-node__content) {
  height: 36px;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  padding: 0 8px;
  height: 36px;
  border-radius: 4px;
}

.custom-tree-node:hover {
  background: rgba(255, 255, 255, 0.05);
}

.custom-tree-node.selected {
  background: rgba(24, 144, 255, 0.15);
}

.node-label {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-primary);
  font-size: 14px;
}

.node-icon {
  color: #00E5FF;
  font-size: 14px;
}

.device-count {
  color: var(--text-secondary);
  font-size: 12px;
  margin-left: 4px;
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.custom-tree-node:hover .node-actions {
  opacity: 1;
}

.tree-btn {
  padding: 4px;
  color: #00E5FF;
}

.tree-btn:hover {
  color: #00E5FF;
  background: transparent;
}

/* 右侧详情面板 */
.region-detail-panel {
  flex: 1;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.detail-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.detail-form {
  padding: 20px;
}

.detail-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: var(--text-primary);
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.detail-footer {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.detail-footer .el-button:first-child {
  background: transparent;
  border-color: var(--border-color);
  color: var(--text-primary);
}

.detail-footer .el-button:last-child {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}
</style>
