<template>
  <div class="role-manage">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.id" placeholder="请输入角色ID" style="width: 140px" clearable />
        <el-input v-model="searchForm.name" placeholder="请输入角色名称" style="width: 140px" clearable />
        <el-select v-model="searchForm.definition" placeholder="请选择角色定义" style="width: 160px" clearable>
          <el-option label="系统管理员" value="系统管理员" />
          <el-option label="普通管理员" value="普通管理员" />
          <el-option label="普通用户" value="普通用户" />
          <el-option label="访客" value="访客" />
        </el-select>
        <el-select v-model="searchForm.inUse" placeholder="是否使用" style="width: 120px" clearable>
          <el-option label="全部" value="" />
          <el-option label="是" value="是" />
          <el-option label="否" value="否" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增角色
        </el-button>
      </div>
</div>

    <!-- 表格 -->
    <el-table :data="pagedData" v-loading="loading" border stripe>
      <el-table-column prop="id" label="角色ID" width="100" />
      <el-table-column prop="name" label="角色名称" min-width="150" />
      <el-table-column prop="definition" label="角色定义" min-width="150" />
      <el-table-column prop="accountInfo" label="账号信息" min-width="130">
        <template #default="{ row }">
          <el-link type="primary" :underline="false" @click="openModal('detail', row)">查看详情</el-link>
        </template>
      </el-table-column>
      <el-table-column prop="inUse" label="是否使用" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.inUse ? 'success' : 'info'" size="small">
            {{ row.inUse ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="usageCount" label="使用数量" width="100" align="center" />
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button class="action-edit" size="small" @click="openModal('permission', row)">设置权限</el-button>
          <el-button class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
          <el-button class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredData.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- 新增/编辑角色弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="角色ID" prop="id">
          <el-input v-model="form.id" placeholder="请输入角色ID" />
        </el-form-item>
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色定义" prop="definition">
          <el-select v-model="form.definition" placeholder="请选择角色定义" style="width: 100%">
            <el-option label="系统管理员" value="系统管理员" />
            <el-option label="普通管理员" value="普通管理员" />
            <el-option label="普通用户" value="普通用户" />
            <el-option label="访客" value="访客" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否使用" prop="inUse">
          <el-select v-model="form.inUse" placeholder="请选择" style="width: 100%">
            <el-option label="是" :value="true" />
            <el-option label="否" :value="false" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 账号详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="账号详情"
      width="500px"
    >
      <el-table :data="accountList" border stripe size="small">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="phone" label="手机号" />
        <el-table-column prop="org" label="组织" />
      </el-table>
    </el-dialog>

    <!-- 设置权限弹窗 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="设置权限"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="permissionForm" label-width="80px">
        <el-form-item label="角色名称">
          <el-input v-model="permissionForm.name" disabled />
        </el-form-item>
        <el-form-item label="权限配置">
          <el-tree
            ref="treeRef"
            :data="permissionTreeData"
            :props="{ label: 'label', children: 'children' }"
            node-key="id"
            show-checkbox
            default-expand-all
            style="background: transparent"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePermissionSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getRoles, createRole, updateRole, deleteRole } from '@/api/roles.js'

interface RoleItem {
  id: string
  name: string
  definition: string
  inUse: boolean
  usageCount: number
  accounts?: { username: string; name: string; phone: string; org: string }[]
}

interface PermissionNode {
  id: string
  label: string
  children?: PermissionNode[]
}

const searchForm = reactive({
  id: '',
  name: '',
  definition: '',
  inUse: ''
})

const loading = ref(false)
const tableData = ref<RoleItem[]>([])

const loadRoles = async () => {
  loading.value = true
  try {
    const data = await getRoles()
    tableData.value = Array.isArray(data) ? data : []
  } catch (err) {
    ElMessage.error('加载角色列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRoles()
})

const currentPage = ref(1)
const pageSize = ref(10)

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    const matchId = !searchForm.id || item.id.includes(searchForm.id)
    const matchName = !searchForm.name || item.name.includes(searchForm.name)
    const matchDef = !searchForm.definition || item.definition === searchForm.definition
    const matchUse = !searchForm.inUse || (searchForm.inUse === '是' ? item.inUse : !item.inUse)
    return matchId && matchName && matchDef && matchUse
  })
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const handleSearch = () => {
  currentPage.value = 1
}

const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const permissionDialogVisible = ref(false)
const dialogTitle = ref('新增角色')
const formRef = ref()
const treeRef = ref()
const editingId = ref<string | null>(null)

const defaultForm = () => ({
  id: '',
  name: '',
  definition: '',
  inUse: true
})

const form = reactive(defaultForm())

const permissionForm = reactive({
  name: ''
})

const accountList = ref<{ username: string; name: string; phone: string; org: string }[]>([])

const permissionTreeData: PermissionNode[] = []

const rules = {
  id: [{ required: true, message: '请输入角色ID', trigger: 'blur' }],
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  definition: [{ required: true, message: '请选择角色定义', trigger: 'change' }],
  inUse: [{ required: true, message: '请选择是否使用', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit' | 'detail' | 'permission', row?: RoleItem) => {
  if (type === 'add') {
    Object.assign(form, defaultForm())
    editingId.value = null
    dialogTitle.value = '新增角色'
    dialogVisible.value = true
  } else if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑角色'
    Object.assign(form, {
      id: row.id,
      name: row.name,
      definition: row.definition,
      inUse: row.inUse
    })
    dialogVisible.value = true
  } else if (type === 'detail' && row) {
    accountList.value = row.accounts || []
    detailDialogVisible.value = true
  } else if (type === 'permission' && row) {
    permissionForm.name = row.name
    permissionDialogVisible.value = true
  }
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingId.value) {
      await updateRole(editingId.value, { ...form })
      ElMessage.success('编辑成功')
    } else {
      await createRole({ ...form, usageCount: 0, accounts: [] })
      ElMessage.success('新增成功')
    }
    await loadRoles()
    dialogVisible.value = false
  } catch (err) {
    // API error already handled by interceptor
  }
}

const handlePermissionSubmit = () => {
  ElMessage.success('权限设置成功')
  permissionDialogVisible.value = false
}

const handleDelete = async (row: RoleItem) => {
  try {
    await ElMessageBox.confirm('确定删除该角色吗？', '提示', { type: 'warning' })
    await deleteRole(row.id)
    ElMessage.success('删除成功')
    await loadRoles()
  } catch (err: any) {
    if (err !== 'cancel') {
      // API error already handled by interceptor
    }
  }
}
</script>

<style scoped>
.role-manage {
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

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 操作按钮 - 设置权限/编辑（青色） */
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
