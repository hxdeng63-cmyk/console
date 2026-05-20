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
        <div class="tree-add">
          <el-button type="primary" size="small" @click="onAddCompany">+ 添加公司</el-button>
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
                  <el-button v-if="data.isCompany" type="text" class="tree-btn" @click.stop="handleAddRegion(data)">
                    <el-icon><Plus /></el-icon>
                  </el-button>
                  <el-button type="text" class="tree-btn" @click.stop="handleEdit(data)">
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button type="text" class="tree-btn" @click.stop="handleDelete(data)">
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
        <el-form-item label="类型" prop="type">
          <el-radio-group v-model="form.type" :disabled="isEditing">
            <el-radio label="company">公司</el-radio>
            <el-radio label="region">区域</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="form.type === 'region'" label="所属公司" prop="parentId">
          <el-select v-model="form.parentId" placeholder="请选择所属公司" style="width: 100%">
            <el-option v-for="c in companyList" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item v-if="form.type === 'region'" label="编码">
          <el-input v-model="form.code" placeholder="请输入编码，如 S201" />
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

interface RegionNode {
  id: number
  name: string
  code?: string
  remark?: string
  sortOrder?: number
  deviceCount?: number
  isCompany?: boolean
  isRegion?: boolean
  children?: RegionNode[]
}

// 与 DeviceGroup.vue 数据对齐：海东分公司 / 西宁分公司 → S201 / G213
const regionTreeData: RegionNode[] = [
  {
    id: 1,
    name: '海东分公司',
    isCompany: true,
    remark: '海东地区管辖',
    sortOrder: 1,
    deviceCount: 7,
    children: [
      { id: 11, name: 'S201', isRegion: true, code: 'S201', remark: '省道201沿线', sortOrder: 1, deviceCount: 3 },
      { id: 12, name: 'G213', isRegion: true, code: 'G213', remark: '国道213沿线', sortOrder: 2, deviceCount: 4 }
    ]
  },
  {
    id: 2,
    name: '西宁分公司',
    isCompany: true,
    remark: '西宁地区管辖',
    sortOrder: 2,
    deviceCount: 5,
    children: [
      { id: 21, name: 'S201', isRegion: true, code: 'S201', remark: '省道201沿线', sortOrder: 1, deviceCount: 2 },
      { id: 22, name: 'G213', isRegion: true, code: 'G213', remark: '国道213沿线', sortOrder: 2, deviceCount: 3 }
    ]
  }
]

const treeRef = ref<InstanceType<typeof ElTree>>()
const loading = ref(false)
const treeData = ref<RegionNode[]>([])

onMounted(async () => {
  loading.value = true
  await new Promise(r => setTimeout(r, 200))
  treeData.value = JSON.parse(JSON.stringify(regionTreeData))
  loading.value = false
})

let nextId = 100

const selectedNode = ref<RegionNode | null>(null)
const detailForm = reactive({
  typeText: '',
  isCompany: false,
  parentName: '',
  name: '',
  code: '',
  remark: '',
  sortOrder: 0
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增公司')
const formRef = ref()
const editingNode = ref<RegionNode | null>(null)
const isEditing = ref(false)

const form = reactive({
  type: 'company' as 'company' | 'region',
  parentId: undefined as number | undefined,
  name: '',
  code: '',
  remark: '',
  sortOrder: 0
})

const rules = {
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  parentId: [{ required: true, message: '请选择所属公司', trigger: 'change' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const companyList = computed(() => {
  return treeData.value.filter(n => n.isCompany)
})

const onNodeClick = (data: RegionNode) => {
  selectedNode.value = data
  detailForm.isCompany = !!data.isCompany
  detailForm.typeText = data.isCompany ? '公司' : '区域'
  detailForm.parentName = getParentName(data.id) || ''
  detailForm.name = data.name
  detailForm.code = data.code || ''
  detailForm.remark = data.remark || ''
  detailForm.sortOrder = data.sortOrder || 0
}

const getParentName = (nodeId: number): string | null => {
  for (const node of treeData.value) {
    if (node.children?.some(child => child.id === nodeId)) {
      return node.name
    }
  }
  return null
}

const onRefresh = async () => {
  loading.value = true
  await new Promise(r => setTimeout(r, 200))
  treeData.value = JSON.parse(JSON.stringify(regionTreeData))
  loading.value = false
  ElMessage.success('刷新成功')
}

const onAddCompany = () => {
  editingNode.value = null
  isEditing.value = false
  dialogTitle.value = '新增公司'
  form.type = 'company'
  form.parentId = undefined
  form.name = ''
  form.code = ''
  form.remark = ''
  form.sortOrder = 0
  dialogVisible.value = true
}

const handleAddRegion = (data: RegionNode) => {
  editingNode.value = null
  isEditing.value = false
  dialogTitle.value = '新增区域'
  form.type = 'region'
  form.parentId = data.id
  form.name = ''
  form.code = ''
  form.remark = ''
  form.sortOrder = 0
  dialogVisible.value = true
}

const handleEdit = (data: RegionNode) => {
  editingNode.value = data
  isEditing.value = true
  dialogTitle.value = data.isCompany ? '编辑公司' : '编辑区域'
  form.type = data.isCompany ? 'company' : 'region'
  if (!data.isCompany) {
    const parent = treeData.value.find(n => n.children?.some(c => c.id === data.id))
    form.parentId = parent?.id
  }
  form.name = data.name
  form.code = data.code || ''
  form.remark = data.remark || ''
  form.sortOrder = data.sortOrder || 0
  dialogVisible.value = true
}

const handleDelete = (data: RegionNode) => {
  const typeText = data.isCompany ? '公司' : '区域'
  const warnText = data.isCompany && data.children?.length
    ? `，旗下 ${data.children.length} 个区域将一并删除`
    : ''
  ElMessageBox.confirm(`确定删除${typeText} "${data.name}" 吗？${warnText}`, '提示', { type: 'warning' })
    .then(() => {
      const removeNode = (nodes: RegionNode[], id: number): boolean => {
        const index = nodes.findIndex(n => n.id === id)
        if (index !== -1) {
          nodes.splice(index, 1)
          return true
        }
        for (const node of nodes) {
          if (node.children && removeNode(node.children, id)) {
            return true
          }
        }
        return false
      }
      removeNode(treeData.value, data.id)
      if (selectedNode.value?.id === data.id) {
        selectedNode.value = null
      }
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}

const handleConfirm = async () => {
  const valid = await (formRef.value as any)?.validate().catch(() => false)
  if (!valid) return

  if (form.type === 'region' && form.parentId) {
    // 添加/编辑区域
    const targetCompany = treeData.value.find(n => n.id === form.parentId)
    if (!targetCompany) {
      ElMessage.error('所属公司不存在')
      return
    }
    if (!targetCompany.children) targetCompany.children = []

    if (editingNode.value) {
      // 编辑：如果换了公司，需要移动
      const oldParent = treeData.value.find(n => n.children?.some(c => c.id === editingNode.value!.id))
      if (oldParent && oldParent.id !== form.parentId) {
        // 从旧公司移除
        const idx = oldParent.children!.findIndex(c => c.id === editingNode.value!.id)
        if (idx !== -1) oldParent.children!.splice(idx, 1)
        // 添加到新公司
        targetCompany.children.push({
          id: editingNode.value.id,
          name: form.name,
          isRegion: true,
          code: form.code,
          remark: form.remark,
          sortOrder: form.sortOrder,
          deviceCount: editingNode.value.deviceCount || 0
        })
      } else {
        // 同一家公司内更新
        const child = targetCompany.children.find(c => c.id === editingNode.value!.id)
        if (child) {
          child.name = form.name
          child.code = form.code
          child.remark = form.remark
          child.sortOrder = form.sortOrder
        }
      }
      ElMessage.success('保存成功')
    } else {
      // 新增区域
      targetCompany.children.push({
        id: nextId++,
        name: form.name,
        isRegion: true,
        code: form.code,
        remark: form.remark,
        sortOrder: form.sortOrder,
        deviceCount: 0
      })
      // 更新公司设备数统计（简化：新增区域默认0台）
      ElMessage.success('添加成功')
    }
  } else {
    // 添加/编辑公司
    if (editingNode.value) {
      editingNode.value.name = form.name
      editingNode.value.remark = form.remark
      editingNode.value.sortOrder = form.sortOrder
      ElMessage.success('保存成功')
    } else {
      treeData.value.push({
        id: nextId++,
        name: form.name,
        isCompany: true,
        remark: form.remark,
        sortOrder: form.sortOrder,
        deviceCount: 0,
        children: []
      })
      ElMessage.success('添加成功')
    }
  }
  dialogVisible.value = false
}

const handleSave = async () => {
  if (selectedNode.value) {
    selectedNode.value.name = detailForm.name
    if (!selectedNode.value.isCompany) {
      selectedNode.value.code = detailForm.code
    }
    selectedNode.value.remark = detailForm.remark
    selectedNode.value.sortOrder = detailForm.sortOrder
    ElMessage.success('保存成功')
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

.tree-add {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.tree-add :deep(.el-button) {
  width: 100%;
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
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
