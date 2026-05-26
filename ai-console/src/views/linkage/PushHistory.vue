<template>
  <div class="push-history">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.operator" placeholder="请输入操作人" style="width: 140px" clearable />
        <el-select v-model="searchForm.sendStatus" placeholder="发送状态" style="width: 120px" clearable>
          <el-option label="全部" value="" />
          <el-option label="完成" value="完成" />
          <el-option label="失败" value="失败" />
        </el-select>
        <el-select v-model="searchForm.pushChannel" placeholder="推送渠道" style="width: 140px" clearable>
          <el-option label="全部" value="" />
          <el-option label="钉钉" value="钉钉" />
          <el-option label="企业微信" value="企业微信" />
          <el-option label="短信" value="短信" />
          <el-option label="API接口" value="API接口" />
        </el-select>
        <el-date-picker
          v-model="searchForm.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 240px"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" v-loading="loading" border stripe>
      <el-table-column prop="ruleName" label="联动规则名称" min-width="150" show-overflow-tooltip />
      <el-table-column prop="operator" label="操作人" width="100" align="center" />
      <el-table-column prop="pushChannel" label="推送渠道" width="120" align="center" />
      <el-table-column prop="count" label="数量" width="80" align="center" />
      <el-table-column prop="sendStatus" label="发送状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.sendStatus === '完成' ? 'success' : 'danger'" size="small">
            {{ row.sendStatus }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="detail" label="结果描述" min-width="300" show-overflow-tooltip />
      <el-table-column prop="sendDate" label="发送日期" width="160" align="center" />
      <el-table-column label="操作" width="100" fixed="right">
        <template #default="{ row }">
          <el-button link class="action-edit" size="small" @click="handleView(row)">查看</el-button>
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

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="推送详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="联动规则名称">{{ currentRecord.ruleName }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentRecord.operator }}</el-descriptions-item>
        <el-descriptions-item label="推送渠道">{{ currentRecord.pushChannel }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ currentRecord.count }}</el-descriptions-item>
        <el-descriptions-item label="发送状态">
          <el-tag :type="currentRecord.sendStatus === '完成' ? 'success' : 'danger'" size="small">
            {{ currentRecord.sendStatus }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发送日期">{{ currentRecord.sendDate }}</el-descriptions-item>
        <el-descriptions-item label="结果描述" :span="2">{{ currentRecord.detail }}</el-descriptions-item>
      </el-descriptions>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { getLinkageHistories } from '@/api/linkage-histories'

interface PushRecord {
  id: number
  ruleName: string
  operator: string
  pushChannel: string
  count: number
  sendStatus: string
  detail: string
  sendDate: string
}

const searchForm = reactive({
  operator: '',
  sendStatus: '',
  pushChannel: '',
  dateRange: null as any
})

const loading = ref(false)
const tableData = ref<PushRecord[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const data = await getLinkageHistories()
    tableData.value = data.items || data
  } catch (error) {
    console.error('Failed to load linkage histories:', error)
  } finally {
    loading.value = false
  }
})

const currentPage = ref(1)
const pageSize = ref(10)

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    const matchOperator = !searchForm.operator || item.operator.includes(searchForm.operator)
    const matchStatus = !searchForm.sendStatus || item.sendStatus === searchForm.sendStatus
    const matchChannel = !searchForm.pushChannel || item.pushChannel === searchForm.pushChannel
    return matchOperator && matchStatus && matchChannel
  })
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const handleSearch = () => {
  currentPage.value = 1
}

const detailDialogVisible = ref(false)
const currentRecord = ref<PushRecord>({
  id: 0,
  ruleName: '',
  operator: '',
  pushChannel: '',
  count: 0,
  sendStatus: '',
  detail: '',
  sendDate: ''
})

const handleView = (row: PushRecord) => {
  currentRecord.value = { ...row }
  detailDialogVisible.value = true
}
</script>

<style scoped>
.push-history {
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
</style>
