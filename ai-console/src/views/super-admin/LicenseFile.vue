<template>
  <div class="license-file">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.fileCode" placeholder="请输入文件代号" style="width: 200px" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="handleUpload">
          <el-icon><Upload /></el-icon>上传
        </el-button>
        <el-button type="primary" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" v-loading="loading" border stripe>
      <el-table-column prop="fileId" label="文件ID" min-width="200" show-overflow-tooltip />
      <el-table-column prop="validity" label="有效期" min-width="200" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
          <el-button link class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
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

    <!-- 上传弹窗 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="文件上传"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="uploadFormRef" :model="uploadForm" label-width="80px">
        <el-form-item label="文件">
          <el-upload
            class="license-upload"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".lic,.license,.json"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持 .lic, .license, .json 格式文件</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUploadSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑文件"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="editFormRef" :model="editForm" label-width="80px">
        <el-form-item label="文件ID">
          <el-input v-model="editForm.fileId" disabled />
        </el-form-item>
        <el-form-item label="有效期">
          <el-input v-model="editForm.validity" placeholder="请输入有效期" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Upload, Refresh, UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLicenses, uploadLicense, deleteLicense } from '@/api/licenses'

interface LicenseItem {
  id: number
  fileId: string
  validity: string
}

const searchForm = reactive({
  fileCode: ''
})

const loading = ref(false)
const tableData = ref<LicenseItem[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const data = await getLicenses()
    tableData.value = data.items || data
  } catch (error) {
    console.error('Failed to load licenses:', error)
  } finally {
    loading.value = false
  }
})

const currentPage = ref(1)
const pageSize = ref(10)

const filteredData = computed(() => {
  if (!searchForm.fileCode) return tableData.value
  return tableData.value.filter(item =>
    item.fileId.toLowerCase().includes(searchForm.fileCode.toLowerCase())
  )
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const handleSearch = () => {
  currentPage.value = 1
}

const handleRefresh = async () => {
  loading.value = true
  try {
    const data = await getLicenses()
    tableData.value = data.items || data
    ElMessage.success('刷新成功')
  } catch (error: any) {
    ElMessage.error(error.message || '刷新失败')
  } finally {
    loading.value = false
  }
}

const uploadDialogVisible = ref(false)
const uploadFormRef = ref()
const uploadForm = reactive({
  file: ''
})

const handleUpload = () => {
  uploadDialogVisible.value = true
}

const handleUploadSubmit = async () => {
  try {
    await uploadLicense(uploadForm)
    ElMessage.success('上传成功')
    uploadDialogVisible.value = false
    const data = await getLicenses()
    tableData.value = data.items || data
  } catch (error: any) {
    ElMessage.error(error.message || '上传失败')
  }
}

const editDialogVisible = ref(false)
const editFormRef = ref()
const editingId = ref<number | null>(null)
const editForm = reactive({
  fileId: '',
  validity: ''
})

const openModal = (type: 'edit', row?: LicenseItem) => {
  if (type === 'edit' && row) {
    editingId.value = row.id
    editForm.fileId = row.fileId
    editForm.validity = row.validity
    editDialogVisible.value = true
  }
}

const handleEditSubmit = () => {
  if (!editForm.validity) {
    ElMessage.warning('请输入有效期')
    return
  }
  const idx = tableData.value.findIndex(item => item.id === editingId.value)
  if (idx !== -1) {
    tableData.value[idx].validity = editForm.validity
  }
  ElMessage.success('编辑成功')
  editDialogVisible.value = false
}

const handleDelete = (row: LicenseItem) => {
  ElMessageBox.confirm('确定删除该文件吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteLicense(row.id)
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
.license-file {
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

.action-edit {
  color: #00E5FF;
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.4);
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 600;
  text-shadow: none;
}

.action-edit:hover {
  color: #00FF88;
  background: rgba(0, 229, 255, 0.25);
  border-color: #00E5FF;
}

.action-delete {
  color: #FF006E;
  background: rgba(255, 0, 110, 0.15);
  border: 1px solid rgba(255, 0, 110, 0.4);
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 600;
  text-shadow: none;
}

.action-delete:hover {
  color: #FF4D6D;
  background: rgba(255, 0, 110, 0.25);
  border-color: #FF006E;
}

/* 链接按钮 - 高对比度样式 */
.license-file :deep(.el-button--primary.link) {
  background: transparent;
  border: none;
  padding: 4px 8px;
}

.license-file :deep(.el-button.link[style*="color: #00E5FF"]) {
  color: #00E5FF !important;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.license-file :deep(.el-button.link[style*="color: #00E5FF"]:hover) {
  color: #00FF88 !important;
  text-shadow: 0 0 15px rgba(0, 255, 136, 0.6);
}

.license-file :deep(.el-button.link[style*="color: #FF006E"]) {
  color: #FF006E !important;
  text-shadow: 0 0 10px rgba(255, 0, 110, 0.4);
}

.license-file :deep(.el-button.link[style*="color: #FF006E"]:hover) {
  color: #FF4D6D !important;
  text-shadow: 0 0 15px rgba(255, 0, 110, 0.6);
}

.license-upload {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>
