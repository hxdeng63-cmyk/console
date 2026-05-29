<template>
  <div class="pt-weight-file">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.keyword" placeholder="请输入权重文件名称" style="width: 200px" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增权重文件
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="name" label="名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="file_path" label="文件路径" min-width="250" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="mono-text">{{ row.file_path }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
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
        :total="total"
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
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入权重文件名称" />
        </el-form-item>
        <el-form-item label="文件路径" prop="file_path">
          <el-input v-model="form.file_path" placeholder="请输入文件路径，如 models/traffic_v1.pt" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
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
import {
  getPTWeightFiles,
  createPTWeightFile,
  updatePTWeightFile,
  deletePTWeightFile
} from '@/api/pt-weight-files'

interface PTWeightFileItem {
  id: number
  name: string
  file_path: string
  description: string
}

const searchForm = reactive({
  keyword: ''
})

const tableData = ref<PTWeightFileItem[]>([])
const loading = ref(false)
const total = ref(0)

const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const handleSearch = () => {
  currentPage.value = 1
  fetchData()
}

const dialogVisible = ref(false)
const dialogTitle = ref('新增权重文件')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  name: '',
  file_path: '',
  description: ''
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  file_path: [{ required: true, message: '请输入文件路径', trigger: 'blur' }]
}

const openModal = (type: 'add' | 'edit', row?: PTWeightFileItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑权重文件'
    Object.assign(form, {
      name: row.name,
      file_path: row.file_path,
      description: row.description
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新增权重文件'
  }
  dialogVisible.value = true
}

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchForm.keyword) params.keyword = searchForm.keyword

    const res = await getPTWeightFiles(params)
    const data = res.data || res
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (err) {
    ElMessage.error('获取权重文件列表失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingId.value) {
      await updatePTWeightFile(editingId.value, form)
      ElMessage.success('编辑成功')
    } else {
      await createPTWeightFile(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await fetchData()
  } catch (err) {
    ElMessage.error(editingId.value ? '编辑失败' : '新增失败')
  }
}

const handleDelete = (row: PTWeightFileItem) => {
  ElMessageBox.confirm('确定删除该权重文件吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deletePTWeightFile(row.id)
        ElMessage.success('删除成功')
        await fetchData()
      } catch (err) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.pt-weight-file {
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

.mono-text {
  font-family: monospace;
  font-size: 12px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
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
