<template>
  <div class="user-manage">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.name" placeholder="请输入用户姓名" style="width: 140px" clearable />
        <el-input v-model="searchForm.username" placeholder="请输入用户名" style="width: 130px" clearable />
        <el-input v-model="searchForm.phone" placeholder="请输入手机号" style="width: 140px" clearable />
        <el-select v-model="searchForm.role" placeholder="请选择用户角色" style="width: 140px" clearable>
          <el-option label="管理员" value="admin" />
          <el-option label="普通用户" value="user" />
          <el-option label="访客" value="guest" />
        </el-select>
        <el-select v-model="searchForm.status" placeholder="账号状态" style="width: 110px" clearable>
          <el-option label="全部" value="" />
          <el-option label="正常" value="正常" />
          <el-option label="停用" value="停用" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新建用户
        </el-button>
        <el-button class="toggle-btn" @click="toggleExpand">
          <el-icon><component :is="expandAll ? ArrowDown : ArrowRight" /></el-icon>
          {{ expandAll ? '折叠全部' : '展开全部' }}
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      ref="tableRef"
      :data="filteredTreeData"
      row-key="id"
      :default-expand-all="true"
      border
      stripe
      style="width: 100%"
    >
      <el-table-column label="名称" min-width="220">
        <template #default="{ row }">
          <div v-if="row.isCompany" class="company-cell">
            <el-icon class="node-icon company-icon"><OfficeBuilding /></el-icon>
            <span class="company-name">{{ row.name }}</span>
          </div>
          <div v-else-if="row.isDept" class="dept-cell">
            <el-icon class="node-icon dept-icon"><FolderOpened /></el-icon>
            <span class="dept-name">{{ row.name }}</span>
          </div>
          <div v-else class="user-cell">
            <el-avatar v-if="row.avatar" :size="32" :src="row.avatar" class="user-avatar" />
            <div class="user-info">
              <span class="user-name">{{ row.name }}</span>
              <span class="user-username">{{ row.username }}</span>
            </div>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="120" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.isCompany" class="type-tag company-tag" size="small">公司</el-tag>
          <el-tag v-else-if="row.isDept" class="type-tag dept-tag" size="small">部门</el-tag>
          <span v-else class="role-text">{{ roleLabel(row.role) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="phone" label="手机号" width="140">
        <template #default="{ row }">
          <span v-if="!row.isCompany && !row.isDept">{{ row.phone }}</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="!row.isCompany && !row.isDept" :type="row.status === '正常' ? 'success' : 'danger'" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="340" fixed="right">
        <template #default="{ row }">
          <template v-if="!row.isCompany && !row.isDept">
            <el-button class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
            <el-button class="action-edit" size="small" @click="openModal('detail', row)">详情</el-button>
            <el-button class="action-edit" size="small" @click="openModal('password', row)">改密</el-button>
            <el-button class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑用户弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="用户姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入用户姓名" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="工号" prop="employeeId">
          <el-input v-model="form.employeeId" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="组织" prop="org">
          <el-input v-model="form.org" placeholder="请输入组织" />
        </el-form-item>
        <el-form-item label="用户角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择用户角色" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
            <el-option label="访客" value="guest" />
          </el-select>
        </el-form-item>
        <el-form-item label="账号状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择账号状态" style="width: 100%">
            <el-option label="正常" value="正常" />
            <el-option label="停用" value="停用" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="用户详情"
      width="500px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{ detailData.username }}</el-descriptions-item>
        <el-descriptions-item label="用户姓名">{{ detailData.name }}</el-descriptions-item>
        <el-descriptions-item label="工号">{{ detailData.employeeId }}</el-descriptions-item>
        <el-descriptions-item label="手机号">{{ detailData.phone }}</el-descriptions-item>
        <el-descriptions-item label="组织">{{ detailData.org }}</el-descriptions-item>
        <el-descriptions-item label="用户角色">
          <el-tag :type="detailData.role === 'admin' ? 'danger' : detailData.role === 'user' ? 'success' : 'info'" size="small">
            {{ roleLabel(detailData.role) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="账号状态">
          <el-tag :type="detailData.status === '正常' ? 'success' : 'danger'" size="small">
            {{ detailData.status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码弹窗 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="修改密码"
      width="400px"
      :close-on-click-modal="false"
    >
      <el-form ref="passwordFormRef" :model="passwordForm" :rules="passwordRules" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="passwordForm.username" disabled />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请确认新密码" show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePasswordSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Plus, ArrowDown, ArrowRight, OfficeBuilding, FolderOpened } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface UserItem {
  id: string
  avatar?: string
  username: string
  name: string
  employeeId: string
  phone: string
  org: string
  role: string
  status: string
  isCompany?: boolean
  isDept?: boolean
  isUser?: boolean
  children?: any[]
}

const roleLabel = (role: string) => {
  const map: Record<string, string> = { admin: '管理员', user: '普通用户', guest: '访客' }
  return map[role] || role
}

const expandAll = ref(true)
const tableRef = ref()

const toggleExpand = () => {
  expandAll.value = !expandAll.value
  const next = expandAll.value
  const walk = (items: any[]) => {
    items.forEach(item => {
      if (item.children && item.children.length > 0) {
        tableRef.value?.toggleRowExpansion(item, next)
        walk(item.children)
      }
    })
  }
  walk(filteredTreeData.value)
}

// 模拟 2 个公司
const treeData = ref<UserItem[]>([
  {
    id: 'company-1',
    name: '青海海东分公司',
    org: '青海海东分公司',
    role: '',
    status: '正常',
    username: '',
    employeeId: '',
    phone: '',
    isCompany: true,
    children: [
      {
        id: 'dept-1-1',
        name: '技术部',
        org: '青海海东分公司/技术部',
        role: '',
        status: '正常',
        username: '',
        employeeId: '',
        phone: '',
        isDept: true,
        children: [
          { id: 'user-001', avatar: 'https://i.pravatar.cc/100?img=2', username: 'zhangwei', name: '张伟', employeeId: 'HD001', phone: '13800138002', org: '青海海东分公司/技术部', role: 'admin', status: '正常', isUser: true },
          { id: 'user-002', avatar: 'https://i.pravatar.cc/100?img=3', username: 'wangli', name: '王丽', employeeId: 'HD002', phone: '13800138003', org: '青海海东分公司/技术部', role: 'user', status: '正常', isUser: true },
        ]
      },
      {
        id: 'dept-1-2',
        name: '运维部',
        org: '青海海东分公司/运维部',
        role: '',
        status: '正常',
        username: '',
        employeeId: '',
        phone: '',
        isDept: true,
        children: [
          { id: 'user-003', avatar: 'https://i.pravatar.cc/100?img=4', username: 'zhaoming', name: '赵明', employeeId: 'HD003', phone: '13800138004', org: '青海海东分公司/运维部', role: 'user', status: '正常', isUser: true },
          { id: 'user-004', avatar: 'https://i.pravatar.cc/100?img=5', username: 'sunlei', name: '孙磊', employeeId: 'HD004', phone: '13800138005', org: '青海海东分公司/运维部', role: 'admin', status: '正常', isUser: true },
        ]
      },
      {
        id: 'dept-1-3',
        name: '综合部',
        org: '青海海东分公司/综合部',
        role: '',
        status: '正常',
        username: '',
        employeeId: '',
        phone: '',
        isDept: true,
        children: [
          { id: 'user-005', avatar: 'https://i.pravatar.cc/100?img=1', username: 'admin', name: '系统管理员', employeeId: 'HD005', phone: '13800138001', org: '青海海东分公司/综合部', role: 'admin', status: '正常', isUser: true },
        ]
      }
    ]
  },
  {
    id: 'company-2',
    name: '青海西宁分公司',
    org: '青海西宁分公司',
    role: '',
    status: '正常',
    username: '',
    employeeId: '',
    phone: '',
    isCompany: true,
    children: [
      {
        id: 'dept-2-1',
        name: '研发部',
        org: '青海西宁分公司/研发部',
        role: '',
        status: '正常',
        username: '',
        employeeId: '',
        phone: '',
        isDept: true,
        children: [
          { id: 'user-006', avatar: 'https://i.pravatar.cc/100?img=6', username: 'liuyang', name: '刘洋', employeeId: 'XN001', phone: '13800138006', org: '青海西宁分公司/研发部', role: 'user', status: '正常', isUser: true },
          { id: 'user-007', avatar: 'https://i.pravatar.cc/100?img=8', username: 'wuqiang', name: '吴强', employeeId: 'XN002', phone: '13800138008', org: '青海西宁分公司/研发部', role: 'admin', status: '正常', isUser: true },
        ]
      },
      {
        id: 'dept-2-2',
        name: '测试部',
        org: '青海西宁分公司/测试部',
        role: '',
        status: '正常',
        username: '',
        employeeId: '',
        phone: '',
        isDept: true,
        children: [
          { id: 'user-008', avatar: 'https://i.pravatar.cc/100?img=9', username: 'zhengxia', name: '郑霞', employeeId: 'XN003', phone: '13800138009', org: '青海西宁分公司/测试部', role: 'user', status: '正常', isUser: true },
        ]
      },
      {
        id: 'dept-2-3',
        name: '行政部',
        org: '青海西宁分公司/行政部',
        role: '',
        status: '正常',
        username: '',
        employeeId: '',
        phone: '',
        isDept: true,
        children: [
          { id: 'user-009', avatar: 'https://i.pravatar.cc/100?img=10', username: 'wanghong', name: '王红', employeeId: 'XN004', phone: '13800138010', org: '青海西宁分公司/行政部', role: 'user', status: '正常', isUser: true },
        ]
      }
    ]
  }
])

const searchForm = reactive({
  name: '',
  username: '',
  phone: '',
  role: '',
  status: ''
})

const handleSearch = () => {}

// 深度过滤树：如果节点的子孙中有匹配的用户，则保留该节点
const filterTree = (nodes: UserItem[]): UserItem[] => {
  return nodes.reduce<UserItem[]>((acc, node) => {
    if (node.isUser) {
      const matchName = !searchForm.name || node.name.includes(searchForm.name)
      const matchUsername = !searchForm.username || node.username.includes(searchForm.username)
      const matchPhone = !searchForm.phone || node.phone.includes(searchForm.phone)
      const matchRole = !searchForm.role || node.role === searchForm.role
      const matchStatus = !searchForm.status || node.status === searchForm.status
      if (matchName && matchUsername && matchPhone && matchRole && matchStatus) {
        acc.push(node)
      }
      return acc
    }
    if (node.children && node.children.length > 0) {
      const filteredChildren = filterTree(node.children)
      if (filteredChildren.length > 0) {
        acc.push({ ...node, children: filteredChildren })
      }
    }
    return acc
  }, [])
}

const filteredTreeData = computed(() => filterTree(treeData.value))

// 收集所有用户节点（用于新增/编辑时查找）
const allUsers = computed(() => {
  const users: UserItem[] = []
  const walk = (nodes: UserItem[]) => {
    nodes.forEach(node => {
      if (node.isUser) users.push(node)
      if (node.children) walk(node.children)
    })
  }
  walk(treeData.value)
  return users
})

const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const dialogTitle = ref('新建用户')
const formRef = ref()
const passwordFormRef = ref()
const editingId = ref<string | null>(null)

const defaultForm = () => ({
  username: '',
  name: '',
  employeeId: '',
  phone: '',
  org: '',
  role: 'user',
  status: '正常'
})

const form = reactive(defaultForm())

const detailData = reactive({
  username: '',
  name: '',
  employeeId: '',
  phone: '',
  org: '',
  role: '',
  status: ''
})

const passwordForm = reactive({
  id: null as string | null,
  username: '',
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (_rule: any, value: string, callback: any) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  name: [{ required: true, message: '请输入用户姓名', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  role: [{ required: true, message: '请选择用户角色', trigger: 'change' }],
  status: [{ required: true, message: '请选择账号状态', trigger: 'change' }]
}

const passwordRules = {
  newPassword: [{ required: true, message: '请输入新密码', trigger: 'blur' }],
  confirmPassword: [{ required: true, message: '请确认新密码', trigger: 'blur' }, { validator: validateConfirmPassword, trigger: 'blur' }]
}

const openModal = (type: 'add' | 'edit' | 'detail' | 'password', row?: UserItem) => {
  if (type === 'add') {
    Object.assign(form, defaultForm())
    editingId.value = null
    dialogTitle.value = '新建用户'
    dialogVisible.value = true
  } else if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑用户'
    Object.assign(form, {
      username: row.username,
      name: row.name,
      employeeId: row.employeeId,
      phone: row.phone,
      org: row.org,
      role: row.role,
      status: row.status
    })
    dialogVisible.value = true
  } else if (type === 'detail' && row) {
    Object.assign(detailData, row)
    detailDialogVisible.value = true
  } else if (type === 'password' && row) {
    passwordForm.id = row.id
    passwordForm.username = row.username
    passwordForm.newPassword = ''
    passwordForm.confirmPassword = ''
    passwordDialogVisible.value = true
  }
}

// 在树中递归查找并更新用户
const updateUserInTree = (nodes: UserItem[], id: string, data: Record<string, string>): boolean => {
  for (const node of nodes) {
    if (node.isUser && node.id === id) {
      Object.assign(node, data)
      return true
    }
    if (node.children && updateUserInTree(node.children, id, data)) return true
  }
  return false
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingId.value) {
    updateUserInTree(treeData.value, editingId.value, { ...form })
    ElMessage.success('编辑成功')
  } else {
    // 新增用户添加到第一个公司的第一个部门
    const company = treeData.value[0]
    if (company?.children?.[0]) {
      company.children[0].children!.push({
        id: 'user-' + Date.now(),
        avatar: '',
        username: form.username,
        name: form.name,
        employeeId: form.employeeId,
        phone: form.phone,
        org: form.org || company.children[0].org,
        role: form.role,
        status: form.status,
        isUser: true
      })
    }
    ElMessage.success('新建成功')
  }
  dialogVisible.value = false
}

const handlePasswordSubmit = async () => {
  const valid = await (passwordFormRef.value as any).validate().catch(() => false)
  if (!valid) return
  ElMessage.success('密码修改成功')
  passwordDialogVisible.value = false
}

// 从树中递归删除用户
const deleteUserInTree = (nodes: UserItem[], id: string): boolean => {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].isUser && nodes[i].id === id) {
      nodes.splice(i, 1)
      return true
    }
    if (nodes[i].children && deleteUserInTree(nodes[i].children!, id)) return true
  }
  return false
}

const handleDelete = (row: UserItem) => {
  ElMessageBox.confirm('确定删除该用户吗？', '提示', { type: 'warning' })
    .then(() => {
      deleteUserInTree(treeData.value, row.id)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
</script>

<style scoped>
.user-manage {
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
  gap: 10px;
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

.action-area {
  display: flex;
  gap: 12px;
  align-items: center;
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

.action-area .toggle-btn {
  background: rgba(0, 40, 80, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.35);
  color: #00E5FF;
}

.action-area .toggle-btn:hover {
  background: rgba(0, 229, 255, 0.15);
  border-color: #00E5FF;
}

/* 公司节点 */
.company-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.company-icon {
  color: #00E5FF;
  font-size: 18px;
}

.company-name {
  font-weight: 700;
  font-size: 14px;
  color: #fff;
}

/* 部门节点 */
.dept-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 8px;
}

.dept-icon {
  color: #00FF88;
  font-size: 16px;
}

.dept-name {
  font-weight: 600;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

/* 用户节点 */
.user-cell {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-left: 8px;
}

.user-avatar {
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.user-username {
  font-size: 11px;
  color: rgba(180, 210, 235, 0.6);
}

.role-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.75);
}

/* 类型标签 */
.type-tag.company-tag {
  background: rgba(0, 229, 255, 0.12);
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: #00B4D8;
}

.type-tag.dept-tag {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid rgba(0, 255, 136, 0.25);
  color: #00CC6A;
}

/* 操作按钮 - 编辑/详情/改密（青色） */
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
