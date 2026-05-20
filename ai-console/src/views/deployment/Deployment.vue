<template>
  <div class="deployment-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="openModal('add')" class="add-btn">
        <el-icon><Plus /></el-icon>新增
      </el-button>
    </div>

    <!-- 表格 -->
    <div class="table-container">
      <el-table :data="pagedData" border stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="name" label="布控名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="deviceNames" label="布控设备" min-width="250" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="device-link" v-if="row.deviceNamesLink">{{ row.deviceNames }}</span>
            <span v-else>{{ row.deviceNames }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="algorithmId" label="算法" width="100" align="center">
          <template #default="{ row }">
            <span class="algorithm-tag">{{ getAlgorithmName(row.algorithmId) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="创建时间" width="160" />
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <span class="status-label" :class="row.status === 'active' ? 'active' : 'inactive'">
              {{ row.status === 'active' ? '启用' : '禁用' }}
            </span>
            <el-switch
              v-model="row.status"
              :active-value="'active'"
              :inactive-value="'inactive'"
              active-color="#00E5FF"
              inactive-color="rgba(255,255,255,0.2)"
              @change="onStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="algorithmStatus" label="算法分析状态" width="120" align="center">
          <template #default="{ row }">
            <span :class="row.algorithmStatus === 'running' ? 'status-running' : 'status-stopped'">
              {{ row.algorithmStatus === 'running' ? '运行中' : '已停止' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button link style="color: #00E5FF; background: rgba(0, 229, 255, 0.15); border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" size="small" @click="openModal('edit', row)">编辑</el-button>
            <el-button link style="color: #FF006E; background: rgba(255, 0, 110, 0.15); border: 1px solid rgba(255, 0, 110, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <div class="pagination-info">
        <span>共 {{ filteredData.length.toLocaleString() }} 条</span>
      </div>
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="filteredData.length"
        layout="sizes, prev, pager, next"
        background
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
      class="deployment-dialog"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="布控名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入布控名称" />
        </el-form-item>

        <el-form-item label="算法选择" prop="algorithmId">
          <el-select v-model="form.algorithmId" placeholder="请选择算法" style="width: 100%">
            <el-option
              v-for="item in algorithms"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="服务选择">
          <div class="service-selector">
            <el-table
              :data="services"
              border
              size="small"
              @selection-change="handleServiceSelection"
              :row-key="(row: ServiceOption) => row.id"
            >
              <el-table-column type="selection" width="50" />
              <el-table-column prop="name" label="选择服务" />
              <el-table-column prop="address" label="服务地址" />
              <el-table-column prop="labelAddress" label="标注地址" />
            </el-table>
          </div>
        </el-form-item>

        <el-form-item label="设备选择">
          <div class="device-selector">
            <el-input
              v-model="deviceSearch"
              placeholder="输入关键字进行过滤"
              clearable
              size="small"
              style="margin-bottom: 10px;"
            />
            <DeviceTree :data="deviceTreeData" mode="checkbox" @node-check="handleDeviceSelect" />
          </div>
        </el-form-item>

        <el-form-item label="时间计划">
          <div class="time-schedule">
            <div class="schedule-row header-row">
              <span class="day-label">日期</span>
              <span class="time-slots">时间段</span>
              <span class="actions">操作</span>
            </div>
            <div v-for="day in weekDays" :key="day.key" class="schedule-row">
              <span class="day-label">{{ day.label }}</span>
              <div class="time-slots">
                <div v-for="(slot, idx) in form.schedule[day.key]" :key="idx" class="time-slot-item">
                  <el-time-picker
                    v-model="slot.start"
                    format="HH:mm:ss"
                    value-format="HH:mm:ss"
                    placeholder="开始时间"
                    style="width: 130px"
                  />
                  <span class="time-separator">-</span>
                  <el-time-picker
                    v-model="slot.end"
                    format="HH:mm:ss"
                    value-format="HH:mm:ss"
                    placeholder="结束时间"
                    style="width: 130px"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    link
                    @click="removeTimeSlot(day.key, idx)"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <el-button type="primary" size="small" link @click="addTimeSlot(day.key)">
                  <el-icon><Plus /></el-icon>添加
                </el-button>
              </div>
              <div class="actions">
                <el-button type="primary" size="small" link @click="syncTimeSlot(day.key)">
                  <el-icon><Refresh /></el-icon>同步
                </el-button>
              </div>
            </div>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false" class="cancel-btn">取消</el-button>
        <el-button type="primary" @click="handleSubmit" class="submit-btn">{{ editingId ? '保存' : '确定' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Search, Plus, Delete, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import DeviceTree from '@/components/device-tree/DeviceTree.vue'
import { deployments, algorithms, services } from '@/mock/deployment/data'
import { deviceTreeData } from '@/mock/monitor/data'

interface DeploymentItem {
  id: number
  name: string
  deviceIds: number[]
  algorithmId: number
  serviceId: number
  schedule: { [key: number]: Array<{ start: string; end: string }> }
  status: string
  createTime: string
}

interface ServiceOption {
  id: number
  name: string
  address: string
}

const weekDays = [
  { key: 1, label: '周一' },
  { key: 2, label: '周二' },
  { key: 3, label: '周三' },
  { key: 4, label: '周四' },
  { key: 5, label: '周五' },
  { key: 6, label: '周六' },
  { key: 7, label: '周日' }
]

const searchName = ref('')
const deviceSearch = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const filteredData = computed(() => {
  if (!searchName.value) return deployments
  return deployments.filter((item: DeploymentItem) =>
    item.name.toLowerCase().includes(searchName.value.toLowerCase())
  )
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const getAlgorithmName = (id: number) => {
  const algo = algorithms.find((a: { id: number }) => a.id === id)
  return algo?.name || '-'
}

const handleSearch = () => {
  currentPage.value = 1
}

const onStatusChange = (row: DeploymentItem) => {
  ElMessage.success(`布控任务 "${row.name}" 已${row.status === 'active' ? '启用' : '停用'}`)
}

const dialogVisible = ref(false)
const dialogTitle = ref('新建布控')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultSchedule = (): { [key: number]: Array<{ start: string; end: string }> } => ({
  1: [{ start: '00:00:00', end: '23:59:59' }],
  2: [{ start: '00:00:00', end: '23:59:59' }],
  3: [{ start: '00:00:00', end: '23:59:59' }],
  4: [{ start: '00:00:00', end: '23:59:59' }],
  5: [{ start: '00:00:00', end: '23:59:59' }],
  6: [{ start: '00:00:00', end: '23:59:59' }],
  7: []
})

const form: {
  name: string
  algorithmId: number | null
  selectedServices: ServiceOption[]
  selectedDevices: number[]
  schedule: { [key: number]: Array<{ start: string; end: string }> }
} = reactive({
  name: '',
  algorithmId: null,
  selectedServices: [],
  selectedDevices: [],
  schedule: defaultSchedule()
})

const rules = {
  name: [{ required: true, message: '请输入布控名称', trigger: 'blur' }],
  algorithmId: [{ required: true, message: '请选择算法', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: DeploymentItem) => {
  Object.assign(form, {
    name: '',
    algorithmId: null,
    selectedServices: [],
    selectedDevices: [],
    schedule: defaultSchedule()
  })
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑布控'
    const selectedService = services.filter((s: ServiceOption) => s.id === row.serviceId)
    Object.assign(form, {
      name: row.name,
      algorithmId: row.algorithmId,
      selectedServices: selectedService,
      selectedDevices: [...row.deviceIds],
      schedule: JSON.parse(JSON.stringify(row.schedule))
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新建布控'
  }
  dialogVisible.value = true
}

const handleServiceSelection = (selection: ServiceOption[]) => {
  form.selectedServices = selection
  if (selection.length > 0) {
    form.selectedDevices = []
  }
}

const handleDeviceSelect = (node: any, checked: boolean) => {
  if (checked) {
    form.selectedDevices.push(node.id)
  } else {
    const idx = form.selectedDevices.indexOf(node.id)
    if (idx > -1) form.selectedDevices.splice(idx, 1)
  }
}

const addTimeSlot = (day: number) => {
  form.schedule[day].push({ start: '00:00:00', end: '23:59:59' })
}

const removeTimeSlot = (day: number, index: number) => {
  form.schedule[day].splice(index, 1)
}

const syncTimeSlot = (_day: number) => {
  const sourceSlots = form.schedule[1]
  weekDays.forEach(d => {
    if (d.key !== 1) {
      form.schedule[d.key] = JSON.parse(JSON.stringify(sourceSlots))
    }
  })
  ElMessage.success('已同步周一时间到其他日期')
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingId.value) {
    const idx = deployments.findIndex((item: DeploymentItem) => item.id === editingId.value)
    if (idx !== -1) {
      Object.assign(deployments[idx], {
        name: form.name,
        algorithmId: form.algorithmId,
        serviceId: form.selectedServices[0]?.id || 0,
        deviceIds: [...form.selectedDevices],
        schedule: JSON.parse(JSON.stringify(form.schedule))
      })
    }
    ElMessage.success('编辑成功')
  } else {
    deployments.push({
      id: Date.now(),
      name: form.name,
      algorithmId: form.algorithmId!,
      serviceId: form.selectedServices[0]?.id || 0,
      deviceIds: [...form.selectedDevices],
      schedule: JSON.parse(JSON.stringify(form.schedule)),
      status: 'active',
      createTime: new Date().toLocaleString()
    })
    ElMessage.success('创建成功')
  }
  dialogVisible.value = false
}

const handleDelete = (row: DeploymentItem) => {
  ElMessageBox.confirm(`确定删除布控任务 "${row.name}" 吗？`, '提示', { type: 'warning' })
    .then(() => {
      const idx = deployments.findIndex((item: DeploymentItem) => item.id === row.id)
      if (idx !== -1) deployments.splice(idx, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
</script>

<style scoped>
.deployment-page {
  height: 100%;
  background: #020B1F;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 操作栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  flex-shrink: 0;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(0, 40, 70, 0.5) 0%, rgba(0, 20, 40, 0.7) 100%);
  border-radius: 12px;
  border: 1px solid rgba(0, 229, 255, 0.12);
}

.search-area {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  width: 220px;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.25);
  box-shadow: none;
  border-radius: 6px;
}

.search-input :deep(.el-input__inner) {
  color: rgba(180, 210, 235, 0.9);
  font-family: 'Rajdhani', sans-serif;
}

.search-input :deep(.el-input__wrapper:hover) {
  border-color: rgba(0, 229, 255, 0.4);
}

.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: #00E5FF;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
}

.search-btn {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 229, 255, 0.05) 100%) !important;
  border: 1px solid rgba(0, 229, 255, 0.3) !important;
  color: #00E5FF !important;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 1px;
}

.search-btn:hover {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.25) 0%, rgba(0, 229, 255, 0.1) 100%) !important;
  border-color: #00E5FF !important;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.25);
}

.add-btn {
  background: linear-gradient(135deg, #00E5FF 0%, #00B4D8 100%) !important;
  border: none !important;
  color: #000 !important;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.35), 0 4px 15px rgba(0, 0, 0, 0.3) !important;
}

.add-btn:hover {
  box-shadow: 0 0 30px rgba(0, 229, 255, 0.5), 0 6px 20px rgba(0, 0, 0, 0.4) !important;
  transform: translateY(-1px);
}

/* 表格 */
.table-container {
  flex: 1;
  min-height: 0;
  overflow: auto;
  background: linear-gradient(145deg, rgba(0, 30, 60, 0.5) 0%, rgba(0, 15, 40, 0.7) 100%);
  border-radius: 12px;
  border: 1px solid rgba(0, 229, 255, 0.12);
  padding: 12px;
}

:deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(0, 40, 80, 0.5);
  --el-table-row-hover-bg-color: rgba(0, 60, 100, 0.3);
  --el-table-border-color: rgba(0, 229, 255, 0.1);
  --el-table-text-color: rgba(255, 255, 255, 0.85);
  --el-table-header-text-color: #00E5FF;
  font-family: 'Rajdhani', sans-serif;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table th.el-table__cell) {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  text-transform: uppercase;
  background: linear-gradient(180deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 229, 255, 0.08) 100%) !important;
}

:deep(.el-table__body tr:hover > td) {
  background: rgba(0, 229, 255, 0.08) !important;
}

.algorithm-tag {
  font-family: 'Orbitron', sans-serif;
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #00E5FF;
  text-shadow: 0 0 8px rgba(0, 229, 255, 0.4);
}

.status-label {
  font-family: 'Rajdhani', sans-serif;
  font-size: 12px;
  font-weight: 500;
  margin-right: 8px;
}

.status-label.active {
  color: #00FF88;
  text-shadow: 0 0 8px rgba(0, 255, 136, 0.4);
}

.status-label.inactive {
  color: rgba(255, 255, 255, 0.4);
}

.device-link {
  color: #8B5CF6;
  cursor: pointer;
  transition: all 0.3s ease;
}

.device-link:hover {
  color: #A78BFA;
  text-shadow: 0 0 10px rgba(139, 92, 246, 0.5);
}

.status-running {
  font-family: 'Orbitron', sans-serif;
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #00FF88;
  text-shadow: 0 0 8px rgba(0, 255, 136, 0.4);
}

.status-stopped {
  font-family: 'Orbitron', sans-serif;
  font-size: 10px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #FF006E;
  text-shadow: 0 0 8px rgba(255, 0, 110, 0.4);
}

/* 分页 */
.pagination-wrapper {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(0, 40, 70, 0.4) 0%, rgba(0, 20, 40, 0.6) 100%);
  border-radius: 12px;
  border: 1px solid rgba(0, 229, 255, 0.1);
  flex-shrink: 0;
}

.pagination-info {
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 1px;
}

/* 弹窗 */
.service-selector {
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 8px;
  overflow: hidden;
  background: rgba(0, 20, 50, 0.4);
}

.device-selector {
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 8px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(0, 30, 60, 0.5) 0%, rgba(0, 15, 40, 0.7) 100%);
  max-height: 220px;
  overflow-y: auto;
}

.time-schedule {
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 8px;
  background: linear-gradient(135deg, rgba(0, 30, 60, 0.5) 0%, rgba(0, 15, 40, 0.7) 100%);
  overflow: hidden;
}

.schedule-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid rgba(0, 229, 255, 0.1);
}

.schedule-row:last-child {
  border-bottom: none;
}

.header-row {
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 229, 255, 0.05) 100%);
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.day-label {
  width: 80px;
  flex-shrink: 0;
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
}

.time-slots {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.time-slot-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.time-separator {
  color: rgba(0, 229, 255, 0.5);
  font-family: 'Orbitron', sans-serif;
}

.actions {
  width: 80px;
  flex-shrink: 0;
  text-align: center;
}

.cancel-btn {
  background: linear-gradient(135deg, rgba(255, 0, 110, 0.1) 0%, rgba(255, 0, 110, 0.05) 100%) !important;
  border: 1px solid rgba(255, 0, 110, 0.3) !important;
  color: #FF006E !important;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 1px;
}

.cancel-btn:hover {
  background: linear-gradient(135deg, rgba(255, 0, 110, 0.2) 0%, rgba(255, 0, 110, 0.1) 100%) !important;
  box-shadow: 0 0 20px rgba(255, 0, 110, 0.25);
}

.submit-btn {
  background: linear-gradient(135deg, #00E5FF 0%, #00B4D8 100%) !important;
  border: none !important;
  color: #000 !important;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 1px;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.35);
}

.submit-btn:hover {
  box-shadow: 0 0 30px rgba(0, 229, 255, 0.5);
}

:deep(.el-dialog) {
  --el-dialog-bg-color: rgba(0, 20, 50, 0.98);
  border: 1px solid rgba(0, 229, 255, 0.25);
  border-radius: 16px !important;
  box-shadow: 0 0 40px rgba(0, 229, 255, 0.15), 0 20px 60px rgba(0, 0, 0, 0.5) !important;
}

:deep(.el-dialog__title) {
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #00E5FF !important;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
}

:deep(.el-form-item__label) {
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 1px;
  color: rgba(0, 229, 255, 0.9) !important;
}

:deep(.el-input__wrapper) {
  background: rgba(0, 20, 50, 0.8) !important;
  border: 1px solid rgba(0, 229, 255, 0.25) !important;
  box-shadow: none !important;
  border-radius: 6px;
}

:deep(.el-input__inner) {
  color: rgba(180, 210, 235, 0.9);
  font-family: 'Rajdhani', sans-serif;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(0, 229, 255, 0.4) !important;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #00E5FF !important;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.25) !important;
}

:deep(.el-select .el-input__wrapper) {
  background: rgba(0, 20, 50, 0.8) !important;
}

:deep(.el-select-dropdown) {
  background: rgba(0, 20, 50, 0.98) !important;
  border: 1px solid rgba(0, 229, 255, 0.25) !important;
  border-radius: 8px;
}

:deep(.el-select-dropdown__item) {
  font-family: 'Rajdhani', sans-serif;
  color: rgba(255, 255, 255, 0.85);
}

:deep(.el-select-dropdown__item.is-hovering) {
  background: rgba(0, 229, 255, 0.1) !important;
}

:deep(.el-select-dropdown__item.is-selected) {
  background: rgba(0, 229, 255, 0.2) !important;
  color: #00E5FF !important;
}
</style>
