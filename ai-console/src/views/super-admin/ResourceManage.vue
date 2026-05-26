<template>
  <div class="resource-manage">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.resource" placeholder="请输入资源" style="width: 160px" clearable />
        <el-input v-model="searchForm.resourceGroup" placeholder="请输入分组" style="width: 160px" clearable />
        <el-select v-model="searchForm.serviceCode" placeholder="请选择微服务" style="width: 160px" clearable>
          <el-option label="011 固件服务" value="011" />
          <el-option label="007 设备接入" value="007" />
          <el-option label="001 用户服务" value="001" />
          <el-option label="002 菜单服务" value="002" />
          <el-option label="003 系统设置" value="003" />
          <el-option label="004 联动服务" value="004" />
          <el-option label="005 算法服务" value="005" />
          <el-option label="006 预警服务" value="006" />
          <el-option label="008 数据清理" value="008" />
          <el-option label="009 监控服务" value="009" />
          <el-option label="010 事件统计" value="010" />
          <el-option label="012 部署服务" value="012" />
          <el-option label="013 数据看板" value="013" />
          <el-option label="014 日志审计" value="014" />
          <el-option label="015 任务调度" value="015" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增资源
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
      :data="tableData"
      v-loading="loading"
      row-key="id"
      :default-expand-all="true"
      border
      stripe
      style="width: 100%"
    >
      <el-table-column prop="resource" label="资源" min-width="160" sortable show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.isParent" style="font-weight: 600;">{{ row.resource }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="serviceCode" label="微服务" width="100" sortable>
        <template #default="{ row }">
          <span v-if="row.isParent">{{ row.serviceCode }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="resourceGroup" label="分组" width="120" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.isParent">{{ row.resourceGroup }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="简介" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="!row.isParent">{{ row.description }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="hidden" label="隐藏" width="80" align="center">
        <template #default="{ row }">
          <el-tag v-if="!row.isParent" :type="row.hidden ? 'danger' : 'success'" size="small">
            {{ row.hidden ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="请求" width="160">
        <template #default="{ row }">
          <div v-if="!row.isParent" class="method-tag-wrapper">
            <el-tag v-if="row.method === 'DELETE'" type="danger" size="small" effect="dark">DELETE</el-tag>
            <el-tag v-else-if="row.method === 'PUT'" type="warning" size="small" effect="dark">PUT</el-tag>
            <el-tag v-else-if="row.method === 'GET'" type="primary" size="small" effect="dark">GET</el-tag>
            <el-tag v-else-if="row.method === 'POST'" type="success" size="small" effect="dark">POST</el-tag>
            <span class="method-desc">{{ methodLabel(row.method) }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <template v-if="!row.isParent">
            <el-button link class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
            <el-button link class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
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

    <!-- 新增/编辑资源 Modal -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="680px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="资源" prop="resource">
              <el-input v-model="form.resource" placeholder="请输入资源" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分组" prop="resourceGroup">
              <el-input v-model="form.resourceGroup" placeholder="请输入分组" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="请求" prop="method">
              <el-select v-model="form.method" placeholder="请选择" style="width: 100%">
                <el-option label="POST" value="POST" />
                <el-option label="GET" value="GET" />
                <el-option label="PUT" value="PUT" />
                <el-option label="DELETE" value="DELETE" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="微服务" prop="serviceCode">
              <el-select v-model="form.serviceCode" placeholder="请选择" style="width: 100%">
                <el-option label="011 固件服务" value="011" />
                <el-option label="007 设备接入" value="007" />
                <el-option label="001 用户服务" value="001" />
                <el-option label="002 菜单服务" value="002" />
                <el-option label="003 系统设置" value="003" />
                <el-option label="004 联动服务" value="004" />
                <el-option label="005 算法服务" value="005" />
                <el-option label="006 预警服务" value="006" />
                <el-option label="008 数据清理" value="008" />
                <el-option label="009 监控服务" value="009" />
                <el-option label="010 事件统计" value="010" />
                <el-option label="012 部署服务" value="012" />
                <el-option label="013 数据看板" value="013" />
                <el-option label="014 日志审计" value="014" />
                <el-option label="015 任务调度" value="015" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="隐藏" prop="hidden">
              <el-select v-model="form.hidden" placeholder="请选择" style="width: 100%">
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="简介" prop="description">
              <el-input v-model="form.description" placeholder="请输入简介" />
            </el-form-item>
          </el-col>
        </el-row>

        <div class="warning-text">
          <el-icon><WarningFilled /></el-icon>
          新增资源需要在角色管理内配置权限才可使用
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { Plus, WarningFilled, ArrowDown, ArrowRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getResources, createResource, updateResource, deleteResource } from '@/api/resources'

interface ResourceItem {
  id: string
  resource: string
  serviceCode: string
  resourceGroup: string
  description: string
  hidden: boolean
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  createdAt: string
  updatedAt: string
}

const searchForm = reactive({
  resource: '',
  resourceGroup: '',
  serviceCode: ''
})

const loading = ref(false)
const tableData = ref<any[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const tableRef = ref()
const expandAll = ref(true)

const methodLabel = (method: string) => {
  const map: Record<string, string> = { GET: '查看', POST: '创建', PUT: '更新', DELETE: '删除' }
  return map[method] || method
}

const allExpandableIds = (items: any[]) => {
  const ids: string[] = []
  const walk = (list: any[]) => {
    list.forEach(item => {
      if (item.children && item.children.length > 0) {
        ids.push(item.id)
        walk(item.children)
      }
    })
  }
  walk(items)
  return ids
}

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
  walk(tableData.value)
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getResources({
      pageNo: currentPage.value,
      pageSize: pageSize.value,
      ...searchForm
    })
    const items = res.items || []
    total.value = res.total || 0

    // Group by resourceGroup to build tree structure
    const groupMap = new Map<string, any>()
    items.forEach((item: any) => {
      const group = item.resourceGroup || item.resource_group || '默认分组'
      if (!groupMap.has(group)) {
        groupMap.set(group, {
          id: `group-${group}`,
          resource: group,
          resourceGroup: group,
          serviceCode: item.serviceCode || item.service_code || '',
          description: '',
          hidden: false,
          method: '',
          isParent: true,
          children: []
        })
      }
      groupMap.get(group).children.push({
        ...item,
        isParent: false
      })
    })

    tableData.value = Array.from(groupMap.values())
  } catch (error) {
    console.error('Failed to load resources:', error)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
watch([currentPage, pageSize], loadData)

const handleSearch = () => {
  currentPage.value = 1
  loadData()
}

const dialogVisible = ref(false)
const dialogTitle = ref('新增资源')
const formRef = ref()
const editingId = ref<string | null>(null)

const defaultForm = () => ({
  resource: '',
  resourceGroup: '',
  method: 'GET' as 'GET' | 'POST' | 'PUT' | 'DELETE',
  serviceCode: '',
  hidden: false,
  description: ''
})

const form = reactive(defaultForm())

const rules = {
  resource: [{ required: true, message: '请输入资源', trigger: 'blur' }],
  resourceGroup: [{ required: true, message: '请输入分组', trigger: 'blur' }],
  method: [{ required: true, message: '请选择请求', trigger: 'change' }],
  serviceCode: [{ required: true, message: '请选择微服务', trigger: 'change' }],
  hidden: [{ required: true, message: '请选择隐藏', trigger: 'change' }],
  description: [{ required: true, message: '请输入简介', trigger: 'blur' }]
}

const openModal = (type: 'add' | 'edit', row?: ResourceItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑资源'
    Object.assign(form, {
      resource: row.resource,
      resourceGroup: row.resourceGroup,
      method: row.method,
      serviceCode: row.serviceCode,
      hidden: row.hidden,
      description: row.description
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新增资源'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingId.value) {
      await updateResource(editingId.value, form)
      ElMessage.success('编辑成功')
    } else {
      await createResource(form)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDelete = (row: ResourceItem) => {
  ElMessageBox.confirm('确定删除该资源吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteResource(row.id)
        ElMessage.success('删除成功')
        loadData()
      } catch (error: any) {
        ElMessage.error(error.message || '删除失败')
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.resource-manage {
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

.action-area .toggle-btn {
  background: rgba(0, 40, 80, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.35);
  color: #00E5FF;
}

.action-area .toggle-btn:hover {
  background: rgba(0, 229, 255, 0.15);
  border-color: #00E5FF;
}

.method-tag-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.method-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.action-edit {
  color: #00E5FF !important;
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.4);
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 600;
}

.action-delete {
  color: #FF006E !important;
  background: rgba(255, 0, 110, 0.15);
  border: 1px solid rgba(255, 0, 110, 0.4);
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 600;
}

.warning-text {
  margin-top: 16px;
  padding: 10px 12px;
  background: rgba(245, 108, 108, 0.1);
  border: 1px solid rgba(245, 108, 108, 0.3);
  border-radius: 4px;
  color: #FF006E;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
}
</style>
