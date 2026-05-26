<template>
  <div class="microservice">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增微服务
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe v-loading="loading">
      <el-table-column prop="code" label="服务编码" width="200" />
      <el-table-column prop="name" label="服务名称" min-width="200" />
      <el-table-column label="操作" width="150" fixed="right">
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

    <!-- 新增/编辑微服务 Modal -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="服务编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入服务编码" />
        </el-form-item>
        <el-form-item label="服务名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入服务名称" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getMicroservices,
  createMicroservice,
  updateMicroservice,
  deleteMicroservice
} from '@/api/microservices'

interface ServiceItem {
  id: number
  code: string
  name: string
}

const tableData = ref<ServiceItem[]>([])
const total = ref(0)
const loading = ref(false)
const submitLoading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMicroservices({
      pageNo: currentPage.value,
      pageSize: pageSize.value
    })
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('Failed to fetch microservices:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})

watch([currentPage, pageSize], () => {
  fetchData()
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增微服务')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  code: '',
  name: ''
})

const form = reactive(defaultForm())

const rules = {
  code: [{ required: true, message: '请输入服务编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入服务名称', trigger: 'blur' }]
}

const openModal = (type: 'add' | 'edit', row?: ServiceItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑微服务'
    Object.assign(form, {
      code: row.code,
      name: row.name
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新增微服务'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (editingId.value) {
      await updateMicroservice(editingId.value, {
        code: form.code,
        name: form.name
      })
      ElMessage.success('编辑成功')
    } else {
      await createMicroservice({
        code: form.code,
        name: form.name
      })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('Submit failed:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row: ServiceItem) => {
  ElMessageBox.confirm('确定删除该微服务吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteMicroservice(row.id)
        ElMessage.success('删除成功')
        fetchData()
      } catch (error) {
        console.error('Delete failed:', error)
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.microservice {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.toolbar .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 操作按钮 - 编辑（青色） */
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
