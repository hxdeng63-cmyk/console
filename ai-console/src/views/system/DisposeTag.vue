<template>
  <div class="dispose-tag">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left-area">
        
      </div>
      <el-button type="primary" @click="openModal('add')">
        <el-icon><Plus /></el-icon>新增
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe>
      <el-table-column prop="tagName" label="标签名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="tagLevel" label="标签等级" width="150" align="center">
        <template #default="{ row }">
          <el-tag :type="getLevelType(row.tagLevel)" size="small">{{ row.tagLevel }}</el-tag>
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
        :page-sizes="[5, 10, 20, 50]"
        :total="tableData.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="450px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="标签名称" prop="tagName">
          <el-input v-model="form.tagName" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签等级" prop="tagLevel">
          <el-select v-model="form.tagLevel" placeholder="请选择标签等级" style="width: 100%">
            <el-option label="一级" value="一级" />
            <el-option label="二级" value="二级" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editingId ? '保存' : '确定' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface TagItem {
  id: number
  tagName: string
  tagLevel: string
}

const tableData = ref<TagItem[]>([
  { id: 1, tagName: '高温告警', tagLevel: '一级' },
  { id: 2, tagName: '人员聚集', tagLevel: '二级' },
  { id: 3, tagName: '设备离线', tagLevel: '二级' },
  { id: 4, tagName: '周界入侵', tagLevel: '一级' },
])

const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const getLevelType = (level: string) => {
  const map: Record<string, string> = {
    '一级': 'danger',
    '二级': 'warning'
  }
  return map[level] || 'info'
}

const dialogVisible = ref(false)
const dialogTitle = ref('添加标签')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  tagName: '',
  tagLevel: ''
})

const form = reactive(defaultForm())

const rules = {
  tagName: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  tagLevel: [{ required: true, message: '请选择标签等级', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: TagItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑标签'
    Object.assign(form, {
      tagName: row.tagName,
      tagLevel: row.tagLevel
    })
  } else {
    editingId.value = null
    dialogTitle.value = '添加标签'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingId.value) {
    const idx = tableData.value.findIndex(item => item.id === editingId.value)
    if (idx !== -1) {
      Object.assign(tableData.value[idx], {
        tagName: form.tagName,
        tagLevel: form.tagLevel
      })
    }
    ElMessage.success('编辑成功')
  } else {
    tableData.value.push({
      id: Date.now(),
      tagName: form.tagName,
      tagLevel: form.tagLevel
    })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
}

const handleDelete = (row: TagItem) => {
  ElMessageBox.confirm(`确定删除标签 "${row.tagName}" 吗？`, '提示', { type: 'warning' })
    .then(() => {
      const idx = tableData.value.findIndex(item => item.id === row.id)
      if (idx !== -1) tableData.value.splice(idx, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
</script>

<style scoped>
.dispose-tag {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.left-area .el-button {
  color: #00E5FF;
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
</style>
