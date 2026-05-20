<template>
  <div class="org-manage">
    <!-- 内容区域 -->
    <div class="org-content">
      <!-- 左侧：组织树 -->
      <div class="org-tree-panel">
        <div class="tree-header">
          <span class="tree-title">组织树形图</span>
          <div class="header-actions">
            <el-button type="default" size="small" @click="onRefresh">
              <el-icon><RefreshRight /></el-icon>
            </el-button>
          </div>
        </div>
        <div class="tree-add">
          <el-button type="primary" size="small" @click="onAddRoot">+ 添加根节点</el-button>
        </div>
<div class="tree-body" v-loading="loading">
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="{ children: 'children', label: 'label' }"
            node-key="id"
            :expand-on-click-node="false"
            :default-expand-all="true"
            @node-click="onNodeClick"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node" :class="{ selected: selectedNode?.id === data.id }">
                <span class="node-label">{{ node.label }}</span>
                <span class="node-actions">
                  <el-button type="text" class="tree-btn" @click.stop="handleAddChild(data)">
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
      <div class="org-detail-panel">
        <div v-if="!selectedNode" class="detail-placeholder">
          <p>选择左侧组织查看详情</p>
        </div>
        <div v-else class="detail-form">
          <h3 class="detail-title">详情</h3>
          <el-form :model="detailForm" label-width="100px">
            <el-form-item label="上级部门">
              <el-input v-model="detailForm.parentName" disabled />
            </el-form-item>
            <el-form-item label="部门名称" required>
              <el-input v-model="detailForm.label" placeholder="请输入部门名称" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input v-model="detailForm.remark" type="textarea" placeholder="请输入备注" :rows="3" />
            </el-form-item>
            <el-form-item label="排序值">
              <el-input-number v-model="detailForm.sortOrder" :min="0" :max="999" />
            </el-form-item>
            <el-form-item label="是否启用">
              <el-switch v-model="detailForm.enabled" />
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
        <el-form-item label="部门名称" prop="label">
          <el-input v-model="form.label" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" placeholder="请输入备注" :rows="3" />
        </el-form-item>
        <el-form-item label="排序值">
          <el-input-number v-model="form.sortOrder" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="form.enabled" />
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { ElTree } from 'element-plus'
import { RefreshRight, Plus, Edit, Delete } from '@element-plus/icons-vue'

interface OrgNode {
  id: number
  label: string
  remark?: string
  sortOrder?: number
  enabled?: boolean
  children?: OrgNode[]
}

const treeRef = ref<InstanceType<typeof ElTree>>()
const loading = ref(false)

// 与 UserManage 对齐的组织数据：公司 -> 部门
const orgTreeData: OrgNode[] = [
  {
    id: 1,
    label: '青海海东分公司',
    remark: '海东地区分公司',
    sortOrder: 1,
    enabled: true,
    children: [
      { id: 11, label: '技术部', remark: '技术研发与支持', sortOrder: 1, enabled: true },
      { id: 12, label: '运维部', remark: '系统运维保障', sortOrder: 2, enabled: true },
      { id: 13, label: '综合部', remark: '行政综合管理', sortOrder: 3, enabled: true }
    ]
  },
  {
    id: 2,
    label: '青海西宁分公司',
    remark: '西宁地区分公司',
    sortOrder: 2,
    enabled: true,
    children: [
      { id: 21, label: '研发部', remark: '产品研发部门', sortOrder: 1, enabled: true },
      { id: 22, label: '测试部', remark: '质量测试部门', sortOrder: 2, enabled: true },
      { id: 23, label: '行政部', remark: '行政人事管理', sortOrder: 3, enabled: true }
    ]
  }
]

const treeData = ref<OrgNode[]>([])

onMounted(async () => {
  loading.value = true
  await new Promise(r => setTimeout(r, 200))
  treeData.value = JSON.parse(JSON.stringify(orgTreeData))
  loading.value = false
})

let nextId = 100

const selectedNode = ref<OrgNode | null>(null)
const detailForm = reactive({
  parentName: '',
  label: '',
  remark: '',
  sortOrder: 0,
  enabled: true
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增根节点')
const formRef = ref()
const editingNode = ref<OrgNode | null>(null)
const isChildNode = ref(false)

const form = reactive({
  label: '',
  remark: '',
  sortOrder: 0,
  enabled: true
})

const rules = {
  label: [{ required: true, message: '请输入部门名称', trigger: 'blur' }]
}

const onNodeClick = (data: OrgNode) => {
  selectedNode.value = data
  detailForm.parentName = getParentName(data.id) || '无'
  detailForm.label = data.label
  detailForm.remark = data.remark || ''
  detailForm.sortOrder = data.sortOrder || 0
  detailForm.enabled = data.enabled !== false
}

const getParentName = (nodeId: number): string | null => {
  for (const node of treeData.value) {
    if (node.children?.some(child => child.id === nodeId)) {
      return node.label
    }
  }
  return null
}

const onRefresh = async () => {
  loading.value = true
  await new Promise(r => setTimeout(r, 200))
  treeData.value = JSON.parse(JSON.stringify(orgTreeData))
  loading.value = false
  ElMessage.success('刷新成功')
}

const onAddRoot = () => {
  editingNode.value = null
  isChildNode.value = false
  dialogTitle.value = '新增根节点'
  form.label = ''
  form.remark = ''
  form.sortOrder = 0
  form.enabled = true
  dialogVisible.value = true
}

const handleAddChild = (data: OrgNode) => {
  editingNode.value = data
  isChildNode.value = true
  dialogTitle.value = '新增子节点'
  form.label = ''
  form.remark = ''
  form.sortOrder = 0
  form.enabled = true
  dialogVisible.value = true
}

const handleEdit = (data: OrgNode) => {
  editingNode.value = data
  isChildNode.value = false
  dialogTitle.value = '编辑节点'
  form.label = data.label
  form.remark = data.remark || ''
  form.sortOrder = data.sortOrder || 0
  form.enabled = data.enabled !== false
  dialogVisible.value = true
}

const handleDelete = (data: OrgNode) => {
  ElMessageBox.confirm(`确定删除部门 "${data.label}" 吗？`, '提示', { type: 'warning' })
    .then(() => {
      const removeNode = (nodes: OrgNode[], id: number): boolean => {
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

  if (isChildNode.value && editingNode.value) {
    // 添加子节点
    const addChild = (nodes: OrgNode[]): boolean => {
      for (const node of nodes) {
        if (node.id === editingNode.value!.id) {
          if (!node.children) node.children = []
          node.children.push({
            id: nextId++,
            label: form.label,
            remark: form.remark,
            sortOrder: form.sortOrder,
            enabled: form.enabled
          })
          return true
        }
        if (node.children && addChild(node.children)) return true
      }
      return false
    }
    addChild(treeData.value)
    ElMessage.success('添加成功')
  } else {
    // 添加根节点
    treeData.value.push({
      id: nextId++,
      label: form.label,
      remark: form.remark,
      sortOrder: form.sortOrder,
      enabled: form.enabled
    })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
}

const handleSave = async () => {
  if (selectedNode.value) {
    selectedNode.value.label = detailForm.label
    selectedNode.value.remark = detailForm.remark
    selectedNode.value.sortOrder = detailForm.sortOrder
    selectedNode.value.enabled = detailForm.enabled
    ElMessage.success('保存成功')
  }
}
</script>

<style scoped>
.org-manage {
  padding: 20px;
  height: 100%;
}

.org-content {
  display: flex;
  gap: 20px;
  height: calc(100vh - 140px);
}

.org-tree-panel {
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
  color: var(--text-primary);
  font-size: 14px;
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
.org-detail-panel {
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
