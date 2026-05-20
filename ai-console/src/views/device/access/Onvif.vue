<template>
  <div class="onvif">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.ip" placeholder="请输入IP地址" style="width: 160px" clearable />
        <el-select v-model="searchForm.vendor" placeholder="请选择厂商" style="width: 140px" clearable>
          <el-option label="海康威视" value="海康威视" />
          <el-option label="大华" value="大华" />
          <el-option label="宇视" value="宇视" />
          <el-option label="华为" value="华为" />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索设备</el-button>
        <el-button type="primary" @click="handleRefresh">刷新</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>添加数据源
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe @selection-change="onSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="ip" label="IP" min-width="180" />
      <el-table-column prop="vendor" label="厂商" width="150" />
      <el-table-column prop="model" label="型号" min-width="180" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === '在线' ? 'success' : 'danger'" size="small">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link style="color: #00E5FF; background: rgba(0, 229, 255, 0.15); border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" size="small" @click="openModal('edit', row)">编辑</el-button>
          <el-button link style="color: #FF006E; background: rgba(255, 0, 110, 0.15); border: 1px solid rgba(255, 0, 110, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" size="small" @click="handleDelete(row)">删除</el-button>
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

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="IP" prop="ip">
          <el-input v-model="form.ip" placeholder="请输入IP地址" />
        </el-form-item>
        <el-form-item label="厂商" prop="vendor">
          <el-select v-model="form.vendor" placeholder="请选择厂商" style="width: 100%">
            <el-option label="海康威视" value="海康威视" />
            <el-option label="大华" value="大华" />
            <el-option label="宇视" value="宇视" />
            <el-option label="华为" value="华为" />
          </el-select>
        </el-form-item>
        <el-form-item label="型号" prop="model">
          <el-input v-model="form.model" placeholder="请输入型号" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input v-model.number="form.port" placeholder="请输入端口" type="number" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
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

interface OnvifDevice {
  id: number
  ip: string
  vendor: string
  model: string
  port: number
  username: string
  password: string
  status: string
}

const searchForm = reactive({
  ip: '',
  vendor: ''
})

const tableData = ref<OnvifDevice[]>([
  { id: 1, ip: '192.168.1.200', vendor: '海康威视', model: 'DS-2CD3T86F', port: 554, username: 'admin', password: 'admin123', status: '在线' },
  { id: 2, ip: '192.168.1.201', vendor: '大华', model: 'DH-IPC-HFW', port: 554, username: 'admin', password: 'admin123', status: '在线' },
  { id: 3, ip: '192.168.1.202', vendor: '宇视', model: 'IPC-S314', port: 554, username: 'admin', password: 'admin123', status: '离线' },
])

const currentPage = ref(1)
const pageSize = ref(10)
const selectedRows = ref<OnvifDevice[]>([])

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    const matchIp = !searchForm.ip || item.ip.includes(searchForm.ip)
    const matchVendor = !searchForm.vendor || item.vendor === searchForm.vendor
    return matchIp && matchVendor
  })
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const onSelectionChange = (rows: OnvifDevice[]) => {
  selectedRows.value = rows
}

const handleSearch = () => {
  currentPage.value = 1
  ElMessage.success('正在搜索ONVIF设备...')
}

const handleRefresh = () => {
  ElMessage.success('刷新成功')
}

const dialogVisible = ref(false)
const dialogTitle = ref('添加数据源')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  ip: '',
  vendor: '',
  model: '',
  port: 554,
  username: '',
  password: ''
})

const form = reactive(defaultForm())

const rules = {
  ip: [{ required: true, message: '请输入IP地址', trigger: 'blur' }],
  vendor: [{ required: true, message: '请选择厂商', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: OnvifDevice) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑数据源'
    Object.assign(form, {
      ip: row.ip,
      vendor: row.vendor,
      model: row.model,
      port: row.port,
      username: row.username,
      password: row.password
    })
  } else {
    editingId.value = null
    dialogTitle.value = '添加数据源'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingId.value) {
    const idx = tableData.value.findIndex(item => item.id === editingId.value)
    if (idx !== -1) {
      tableData.value[idx] = { ...tableData.value[idx], ...form, id: editingId.value }
    }
    ElMessage.success('编辑成功')
  } else {
    tableData.value.push({ id: Date.now(), ...form, status: '在线' })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
}

const handleDelete = (row: OnvifDevice) => {
  ElMessageBox.confirm('确定删除该数据源吗？', '提示', { type: 'warning' })
    .then(() => {
      const idx = tableData.value.findIndex(item => item.id === row.id)
      if (idx !== -1) tableData.value.splice(idx, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
</script>

<style scoped>
.onvif {
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
</style>
