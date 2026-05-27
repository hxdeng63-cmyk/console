<template>
  <div class="operation-history">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left-area">
        <el-input v-model="filters.operator" placeholder="请输入操作人" style="width: 140px" clearable />
        <el-input v-model="filters.ip" placeholder="请输入IP" style="width: 140px" clearable />
        <el-select v-model="filters.method" placeholder="请求方法" style="width: 120px" clearable>
          <el-option label="GET" value="GET" />
          <el-option label="POST" value="POST" />
          <el-option label="PUT" value="PUT" />
          <el-option label="DELETE" value="DELETE" />
        </el-select>
        <el-input v-model="filters.path" placeholder="请输入路径" style="width: 160px" clearable />
        <el-button type="primary" @click="onQuery">查询</el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" border stripe v-loading="loading">
      <el-table-column prop="real_name" label="操作人" width="130" align="center">
        <template #default="{ row }">
          {{ row.real_name || row.operator || '自动记录的请求' }}
        </template>
      </el-table-column>
      <el-table-column prop="date" label="日期" width="170" />
      <el-table-column prop="status_code" label="状态码" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status_code === 200 ? 'success' : 'danger'" size="small">{{ row.status_code }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ip" label="请求IP" width="140" />
      <el-table-column prop="method" label="请求方法" width="90" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.method === 'GET' ? 'primary' : row.method === 'POST' ? 'success' : row.method === 'PUT' ? 'warning' : 'danger'"
            size="small"
            effect="dark"
          >{{ row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="请求路径" min-width="220" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="140" show-overflow-tooltip />
      <el-table-column label="操作" width="80" fixed="right" align="center">
        <template #default="{ row }">
          <el-button class="action-detail" size="small" @click="handleDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @size-change="onQuery"
        @current-change="onQuery"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getOperationLogs } from '@/api/operation-logs.js'

interface HistoryItem {
  id: number
  operator: string
  date: string
  status_code: number
  ip: string
  method: string
  path: string
  description: string
}

const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const tableData = ref<HistoryItem[]>([])

const filters = reactive({
  operator: '',
  ip: '',
  method: '',
  path: ''
})

const fetchData = async () => {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (filters.operator) params.operator = filters.operator
    if (filters.ip) params.ip = filters.ip
    if (filters.method) params.method = filters.method
    if (filters.path) params.path = filters.path

    const res = await getOperationLogs(params)
    tableData.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error('获取操作日志失败')
  } finally {
    loading.value = false
  }
}

const onQuery = () => {
  currentPage.value = 1
  fetchData()
}

const handleDetail = (row: HistoryItem) => {
  ElMessage.info(`${row.operator} - ${row.description}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.operation-history {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.left-area {
  display: flex;
  gap: 12px;
  align-items: center;
}

.left-area .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.left-area .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 详情按钮 */
.action-detail {
  background: rgba(0, 229, 255, 0.15) !important;
  border: 1px solid rgba(0, 229, 255, 0.4) !important;
  color: #00E5FF !important;
  border-radius: 4px;
  padding: 6px 10px !important;
  font-weight: 600;
  text-shadow: none;
  box-shadow: none;
}

.action-detail:hover {
  background: rgba(0, 229, 255, 0.25) !important;
  border-color: #00E5FF !important;
  color: #00FF88 !important;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.3);
}
</style>
