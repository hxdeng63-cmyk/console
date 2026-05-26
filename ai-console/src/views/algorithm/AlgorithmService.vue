<template>
  <div class="algorithm-service">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left-area">
        <el-button type="primary" @click="openAddModal">添加服务</el-button>
      </div>
     
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" v-loading="loading" border stripe>
      <el-table-column prop="serviceId" label="算法ID" width="100" align="center" />
      <el-table-column prop="serviceName" label="算法名称" min-width="120" show-overflow-tooltip />
      <el-table-column prop="serviceAddress" label="算法服务" min-width="280" show-overflow-tooltip />
      <el-table-column prop="algorithmConfig" label="算法设置" min-width="150" show-overflow-tooltip />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link class="action-edit" size="small" @click="openEditModal(row)">编辑</el-button>
          <el-button link class="action-edit" size="small" @click="openAddressModal(row)">算法地址管理</el-button>
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

    <!-- 添加/编辑服务弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="算法选择" prop="serviceName">
          <el-select v-model="form.serviceName" placeholder="请选择算法服务" style="width: 100%">
            <el-option label="目标检测" value="目标检测" />
            <el-option label="行为分析" value="行为分析" />
            <el-option label="烟火检测" value="烟火检测" />
          </el-select>
        </el-form-item>
        <el-form-item label="算法设置">
          <div class="config-list">
            <div v-for="(item, index) in form.configs" :key="index" class="config-item">
              <el-input v-model="item.key" placeholder="key" style="width: 150px" />
              <el-input v-model="item.value" placeholder="value" style="width: 150px" />
              <el-button type="danger" link @click="removeConfig(index)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
            <el-button link class="action-edit" @click="addConfig">
              <el-icon><Plus /></el-icon>添加设置
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editingId ? '保存' : '确定' }}</el-button>
      </template>
    </el-dialog>

    <!-- 算法地址管理弹窗 -->
    <el-dialog
      v-model="addressDialogVisible"
      title="服务地址管理"
      width="650px"
      :close-on-click-modal="false"
    >
      <div class="address-toolbar">
        <el-button type="primary" @click="openAddressAddModal">新增</el-button>
      </div>

      <el-table :data="addressList" border stripe>
        <el-table-column prop="serviceUrl" label="服务地址" min-width="250" show-overflow-tooltip />
        <el-table-column prop="annotationUrl" label="标注地址" min-width="250" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link class="action-edit" size="small" @click="openAddressEditModal(row)">编辑</el-button>
            <el-button link class="action-delete" size="small" @click="handleDeleteAddress(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 新增/编辑地址弹窗 -->
      <el-dialog
        v-model="addressFormVisible"
        :title="addressDialogTitle"
        width="450px"
        append-to-body
        :close-on-click-modal="false"
      >
        <el-form ref="addressFormRef" :model="addressForm" :rules="addressRules" label-width="90px">
          <el-form-item label="服务地址" prop="serviceUrl">
            <el-input v-model="addressForm.serviceUrl" placeholder="请输入服务地址" />
          </el-form-item>
          <el-form-item label="标注地址" prop="annotationUrl">
            <el-input v-model="addressForm.annotationUrl" placeholder="请输入标注地址" />
          </el-form-item>
        </el-form>

        <template #footer>
          <el-button @click="addressFormVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddressSubmit">{{ editingAddressId ? '保存' : '确定' }}</el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAlgorithmServices, createAlgorithmService, updateAlgorithmService } from '@/api/algorithm-services'

interface ServiceItem {
  id: number
  serviceId: string
  serviceName: string
  serviceAddress: string
  algorithmConfig: string
}

interface AddressItem {
  id: number
  serviceUrl: string
  annotationUrl: string
}

interface ConfigItem {
  key: string
  value: string
}

const loading = ref(false)
const tableData = ref<ServiceItem[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const data = await getAlgorithmServices()
    tableData.value = data.items || data
  } catch (error) {
    console.error('Failed to load algorithm services:', error)
  } finally {
    loading.value = false
  }
})

const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

// 添加/编辑服务弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('添加服务')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  serviceName: '',
  configs: [] as ConfigItem[]
})

const form = reactive(defaultForm())

const rules = {
  serviceName: [{ required: true, message: '请选择算法服务', trigger: 'change' }]
}

const addConfig = () => {
  form.configs.push({ key: '', value: '' })
}

const removeConfig = (index: number) => {
  form.configs.splice(index, 1)
}

const openAddModal = () => {
  Object.assign(form, defaultForm())
  editingId.value = null
  dialogTitle.value = '添加服务'
  dialogVisible.value = true
}

const openEditModal = (row: ServiceItem) => {
  editingId.value = row.id
  dialogTitle.value = '编辑服务'
  Object.assign(form, {
    serviceName: row.serviceName,
    configs: []
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingId.value) {
      await updateAlgorithmService(editingId.value, {
        serviceName: form.serviceName,
        configs: form.configs
      })
      const idx = tableData.value.findIndex(item => item.id === editingId.value)
      if (idx !== -1) {
        tableData.value[idx].serviceName = form.serviceName
      }
      ElMessage.success('编辑成功')
    } else {
      const newService = await createAlgorithmService({
        serviceName: form.serviceName,
        configs: form.configs
      })
      tableData.value.push(newService)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

// 算法地址管理弹窗
const addressDialogVisible = ref(false)
const addressList = ref<AddressItem[]>([])
const currentServiceId = ref<number | null>(null)

const openAddressModal = (row: ServiceItem) => {
  currentServiceId.value = row.id
  addressList.value = []
  addressDialogVisible.value = true
}

const addressFormVisible = ref(false)
const addressDialogTitle = ref('新增地址')
const addressFormRef = ref()
const editingAddressId = ref<number | null>(null)

const addressForm = reactive({
  serviceUrl: '',
  annotationUrl: ''
})

const addressRules = {
  serviceUrl: [{ required: true, message: '请输入服务地址', trigger: 'blur' }],
  annotationUrl: [{ required: true, message: '请输入标注地址', trigger: 'blur' }]
}

const openAddressAddModal = () => {
  addressForm.serviceUrl = ''
  addressForm.annotationUrl = ''
  editingAddressId.value = null
  addressDialogTitle.value = '新增地址'
  addressFormVisible.value = true
}

const openAddressEditModal = (row: AddressItem) => {
  editingAddressId.value = row.id
  addressDialogTitle.value = '编辑地址'
  addressForm.serviceUrl = row.serviceUrl
  addressForm.annotationUrl = row.annotationUrl
  addressFormVisible.value = true
}

const handleAddressSubmit = async () => {
  const valid = await (addressFormRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingAddressId.value) {
    const idx = addressList.value.findIndex(item => item.id === editingAddressId.value)
    if (idx !== -1) {
      addressList.value[idx].serviceUrl = addressForm.serviceUrl
      addressList.value[idx].annotationUrl = addressForm.annotationUrl
    }
    ElMessage.success('编辑成功')
  } else {
    addressList.value.push({
      id: Date.now(),
      serviceUrl: addressForm.serviceUrl,
      annotationUrl: addressForm.annotationUrl
    })
    ElMessage.success('添加成功')
  }
  addressFormVisible.value = false
}

const handleDeleteAddress = (row: AddressItem) => {
  ElMessageBox.confirm('确定删除该地址吗？', '提示', { type: 'warning' })
    .then(() => {
      const idx = addressList.value.findIndex(item => item.id === row.id)
      if (idx !== -1) addressList.value.splice(idx, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
</script>

<style scoped>
.algorithm-service {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.address-toolbar {
  margin-bottom: 12px;
}

.address-toolbar .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: 8px;
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
</style>
