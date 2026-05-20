<template>
  <div class="platform-list">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.vendor" placeholder="请输入租户厂商" style="width: 140px" clearable />
        <el-input v-model="searchForm.tenantName" placeholder="请输入租户名称" style="width: 160px" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button type="primary" @click="handleRefresh">刷新</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增
        </el-button>
      </div>
</div>

    <!-- 表格 -->
    <el-table :data="pagedData" v-loading="loading" border stripe>
      <el-table-column prop="vendor" label="租户厂商" width="120" />
      <el-table-column prop="tenantName" label="租户名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="host" label="Host" min-width="180" show-overflow-tooltip />
      <el-table-column prop="port" label="Port" width="80" align="center" />
      <el-table-column prop="appKey" label="AppKey" min-width="150" show-overflow-tooltip />
      <el-table-column prop="appSecret" label="AppSecret" min-width="150" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="secret-text">{{ row.showSecret ? row.appSecret : '********' }}</span>
          <el-button link style="color: #00E5FF; text-shadow: 0 0 10px rgba(0, 229, 255, 0.8); font-weight: 700; margin-left: 8px;" size="small" @click="row.showSecret = !row.showSecret">
            {{ row.showSecret ? '隐藏' : '显示' }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="apiVersion" label="Api版本" width="100" align="center" />
      <el-table-column prop="platformVersion" label="平台版本" width="120" align="center" />
      <el-table-column prop="defaultProtocol" label="默认协议" width="100" align="center" />
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
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="租户厂商" prop="vendor">
              <el-input v-model="form.vendor" placeholder="请输入租户厂商" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="租户名称" prop="tenantName">
              <el-input v-model="form.tenantName" placeholder="请输入租户名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Host" prop="host">
              <el-input v-model="form.host" placeholder="请输入Host" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="Port" prop="port">
              <el-input v-model.number="form.port" placeholder="请输入端口" type="number" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="AppKey" prop="appKey">
              <el-input v-model="form.appKey" placeholder="请输入AppKey" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="AppSecret" prop="appSecret">
              <el-input v-model="form.appSecret" placeholder="请输入AppSecret" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="Api版本" prop="apiVersion">
              <el-select v-model="form.apiVersion" placeholder="请选择" style="width: 100%">
                <el-option label="v2" value="v2" />
                <el-option label="v3" value="v3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="平台版本" prop="platformVersion">
              <el-input v-model="form.platformVersion" placeholder="请输入平台版本" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="默认协议" prop="defaultProtocol">
              <el-select v-model="form.defaultProtocol" placeholder="请选择" style="width: 100%">
                <el-option label="HTTPS" value="HTTPS" />
                <el-option label="HTTP" value="HTTP" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
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
import { getPlatforms, createPlatform, updatePlatform, deletePlatform } from '@/api/platforms'

interface PlatformItem {
  id: number
  vendor: string
  tenantName: string
  host: string
  port: number
  appKey: string
  appSecret: string
  showSecret: boolean
  apiVersion: string
  platformVersion: string
  defaultProtocol: string
}

const searchForm = reactive({
  vendor: '',
  tenantName: ''
})

const loading = ref(false)
const tableData = ref<PlatformItem[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const data = await getPlatforms()
    tableData.value = data.items || data
  } catch (error) {
    console.error('Failed to load platforms:', error)
  } finally {
    loading.value = false
  }
})

const currentPage = ref(1)
const pageSize = ref(10)

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    const matchVendor = !searchForm.vendor || item.vendor.includes(searchForm.vendor)
    const matchName = !searchForm.tenantName || item.tenantName.includes(searchForm.tenantName)
    return matchVendor && matchName
  })
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const handleSearch = () => {
  currentPage.value = 1
}

const handleRefresh = () => {
  ElMessage.success('刷新成功')
}

const dialogVisible = ref(false)
const dialogTitle = ref('新增平台')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  vendor: '',
  tenantName: '',
  host: '',
  port: 8080,
  appKey: '',
  appSecret: '',
  apiVersion: 'v2',
  platformVersion: '',
  defaultProtocol: 'HTTPS'
})

const form = reactive(defaultForm())

const rules = {
  vendor: [{ required: true, message: '请输入租户厂商', trigger: 'blur' }],
  tenantName: [{ required: true, message: '请输入租户名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入Host', trigger: 'blur' }],
  port: [{ required: true, message: '请输入端口', trigger: 'blur' }],
  appKey: [{ required: true, message: '请输入AppKey', trigger: 'blur' }]
}

const openModal = (type: 'add' | 'edit', row?: PlatformItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑平台'
    Object.assign(form, {
      vendor: row.vendor,
      tenantName: row.tenantName,
      host: row.host,
      port: row.port,
      appKey: row.appKey,
      appSecret: row.appSecret,
      apiVersion: row.apiVersion,
      platformVersion: row.platformVersion,
      defaultProtocol: row.defaultProtocol
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新增平台'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingId.value) {
      await updatePlatform(editingId.value, form)
      const idx = tableData.value.findIndex(item => item.id === editingId.value)
      if (idx !== -1) {
        tableData.value[idx] = { ...tableData.value[idx], ...form, id: editingId.value, showSecret: false }
      }
      ElMessage.success('编辑成功')
    } else {
      const newPlatform = await createPlatform(form)
      tableData.value.push({ ...newPlatform, showSecret: false })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDelete = (row: PlatformItem) => {
  ElMessageBox.confirm('确定删除该平台吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deletePlatform(row.id)
        const idx = tableData.value.findIndex(item => item.id === row.id)
        if (idx !== -1) tableData.value.splice(idx, 1)
        ElMessage.success('删除成功')
      } catch (error: any) {
        ElMessage.error(error.message || '删除失败')
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.platform-list {
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

.secret-text {
  font-family: monospace;
  font-size: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
