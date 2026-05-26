<template>
  <div class="gb28181">
    <!-- SIP服务器配置 -->
    <el-card class="sip-card">
      <template #header>
        <div class="card-header">
          <span>SIP 服务器配置</span>
          <el-button type="primary" size="small" @click="handleSaveSip">保存</el-button>
        </div>
      </template>
      <el-form :model="sipForm" label-width="140px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="SIP服务器ID">
              <el-input v-model="sipForm.serverId" placeholder="请输入SIP服务器ID" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="SIP域">
              <el-input v-model="sipForm.realm" placeholder="请输入SIP域" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="SIP密码">
              <el-input v-model="sipForm.password" type="password" placeholder="请输入SIP密码" show-password />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 平台列表 -->
    <el-card class="platform-card" v-loading="platformLoading">
      <template #header>
        <div class="card-header">
          <span>平台列表</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="handleAddPlatform">
              <el-icon><Plus /></el-icon>新增
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="platformPagedData" border stripe>
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="platformNo" label="平台编号" width="150" />
        <el-table-column prop="enabled" label="是否启用" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.enabled ? 'success' : 'info'" size="small">
              {{ row.enabled ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sipIp" label="SIP服务IP" min-width="150" />
        <el-table-column prop="gbDeviceNo" label="设备国标编号" min-width="200" show-overflow-tooltip />
        <el-table-column prop="transport" label="传输方式" width="100" align="center" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link class="action-edit" size="small" @click="openPlatformModal('edit', row)">编辑</el-button>
            <el-button link class="action-delete" size="small" @click="handleDeletePlatform(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="platformPage"
          v-model:page-size="platformPageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="platformList.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <!-- 设备列表 -->
    <el-card class="device-card" v-loading="deviceLoading">
      <template #header>
        <div class="card-header">
          <span>设备列表</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="handleAddAuthId">
              <el-icon><Plus /></el-icon>添加认证ID
            </el-button>
            <el-button type="primary" size="small" @click="handleSyncAll">全部同步至视频源</el-button>
            <el-button type="primary" size="small" @click="handleSyncSelected">选择同步至视频源</el-button>
          </div>
        </div>
      </template>

      <el-table :data="devicePagedData" border stripe @selection-change="onDeviceSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column prop="deviceModel" label="设备型号" width="120" />
        <el-table-column prop="vendor" label="厂商" width="100" />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="deviceId" label="deviceId" min-width="180" show-overflow-tooltip />
        <el-table-column prop="channelId" label="channelId" min-width="180" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP" width="130" />
        <el-table-column prop="syncVideoSource" label="同步视频源" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.syncVideoSource === '是' ? 'success' : 'info'" size="small">
              {{ row.syncVideoSource }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="port" label="端口" width="80" align="center" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button link class="action-edit" size="small" @click="openDeviceModal('edit', row)">编辑</el-button>
            <el-button link class="action-delete" size="small" @click="handleDeleteDevice(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="devicePage"
          v-model:page-size="devicePageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="deviceList.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <!-- 平台新增/编辑弹窗 -->
    <el-dialog
      v-model="platformDialogVisible"
      :title="platformDialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="platformFormRef" :model="platformForm" :rules="platformRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="platformForm.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="平台编号" prop="platformNo">
          <el-input v-model="platformForm.platformNo" placeholder="请输入平台编号" />
        </el-form-item>
        <el-form-item label="是否启用" prop="enabled">
          <el-switch v-model="platformForm.enabled" active-color="#36D68A" />
        </el-form-item>
        <el-form-item label="SIP服务IP" prop="sipIp">
          <el-input v-model="platformForm.sipIp" placeholder="请输入SIP服务IP" />
        </el-form-item>
        <el-form-item label="设备国标编号" prop="gbDeviceNo">
          <el-input v-model="platformForm.gbDeviceNo" placeholder="请输入设备国标编号" />
        </el-form-item>
        <el-form-item label="传输方式" prop="transport">
          <el-select v-model="platformForm.transport" placeholder="请选择" style="width: 100%">
            <el-option label="UDP" value="UDP" />
            <el-option label="TCP" value="TCP" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="platformDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePlatformSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 设备新增/编辑弹窗 -->
    <el-dialog
      v-model="deviceDialogVisible"
      :title="deviceDialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="deviceFormRef" :model="deviceForm" :rules="deviceRules" label-width="100px">
        <el-form-item label="设备型号" prop="deviceModel">
          <el-input v-model="deviceForm.deviceModel" placeholder="请输入设备型号" />
        </el-form-item>
        <el-form-item label="厂商" prop="vendor">
          <el-input v-model="deviceForm.vendor" placeholder="请输入厂商" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="deviceForm.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="deviceId" prop="deviceId">
          <el-input v-model="deviceForm.deviceId" placeholder="请输入deviceId" />
        </el-form-item>
        <el-form-item label="channelId" prop="channelId">
          <el-input v-model="deviceForm.channelId" placeholder="请输入channelId" />
        </el-form-item>
        <el-form-item label="IP" prop="ip">
          <el-input v-model="deviceForm.ip" placeholder="请输入IP地址" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input v-model.number="deviceForm.port" placeholder="请输入端口" type="number" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="deviceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDeviceSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPlatforms,
  createPlatform,
  updatePlatform,
  deletePlatform
} from '@/api/platforms'
import {
  getDevices,
  createDevice,
  updateDevice,
  deleteDevice
} from '@/api/devices'

// Loading states
const platformLoading = ref(false)
const deviceLoading = ref(false)

// SIP配置
const sipForm = reactive({
  serverId: '',
  realm: '',
  password: ''
})

// 平台列表
interface PlatformItem {
  id: number
  name: string
  platformNo: string
  enabled: boolean
  sipIp: string
  gbDeviceNo: string
  transport: string
}

const platformList = ref<PlatformItem[]>([])

const platformPage = ref(1)
const platformPageSize = ref(10)

const platformPagedData = computed(() => {
  const start = (platformPage.value - 1) * platformPageSize.value
  return platformList.value.slice(start, start + platformPageSize.value)
})

// 设备列表
interface DeviceItem {
  id: number
  deviceModel: string
  vendor: string
  name: string
  deviceId: string
  channelId: string
  ip: string
  syncVideoSource: string
  port: number
}

const deviceList = ref<DeviceItem[]>([])

const devicePage = ref(1)
const devicePageSize = ref(10)
const selectedDevices = ref<DeviceItem[]>([])

const devicePagedData = computed(() => {
  const start = (devicePage.value - 1) * devicePageSize.value
  return deviceList.value.slice(start, start + devicePageSize.value)
})

const onDeviceSelectionChange = (rows: DeviceItem[]) => {
  selectedDevices.value = rows
}

// 平台弹窗
const platformDialogVisible = ref(false)
const platformDialogTitle = ref('新增平台')
const platformFormRef = ref()
const editingPlatformId = ref<number | null>(null)

const platformForm = reactive({
  name: '',
  platformNo: '',
  enabled: true,
  sipIp: '',
  gbDeviceNo: '',
  transport: 'UDP'
})

const platformRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  platformNo: [{ required: true, message: '请输入平台编号', trigger: 'blur' }]
}

// 设备弹窗
const deviceDialogVisible = ref(false)
const deviceDialogTitle = ref('新增设备')
const deviceFormRef = ref()
const editingDeviceId = ref<number | null>(null)

const deviceForm = reactive({
  deviceModel: '',
  vendor: '',
  name: '',
  deviceId: '',
  channelId: '',
  ip: '',
  port: 554
})

const deviceRules = {
  deviceModel: [{ required: true, message: '请输入设备型号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  deviceId: [{ required: true, message: '请输入deviceId', trigger: 'blur' }]
}

// Fetch data on mount
const fetchPlatforms = async () => {
  platformLoading.value = true
  try {
    const res = await getPlatforms()
    platformList.value = res.items || res.list || res || []
  } catch (error) {
    // Error already handled by interceptor
  } finally {
    platformLoading.value = false
  }
}

const fetchDevices = async () => {
  deviceLoading.value = true
  try {
    const res = await getDevices()
    deviceList.value = res.items || res.list || res || []
  } catch (error) {
    // Error already handled by interceptor
  } finally {
    deviceLoading.value = false
  }
}

onMounted(() => {
  fetchPlatforms()
  fetchDevices()
})

// 事件处理
const handleSaveSip = () => {
  ElMessage.success('SIP配置已保存')
}

const handleAddPlatform = () => {
  editingPlatformId.value = null
  platformDialogTitle.value = '新增平台'
  Object.assign(platformForm, { name: '', platformNo: '', enabled: true, sipIp: '', gbDeviceNo: '', transport: 'UDP' })
  platformDialogVisible.value = true
}

const openPlatformModal = (type: 'edit', row?: PlatformItem) => {
  if (type === 'edit' && row) {
    editingPlatformId.value = row.id
    platformDialogTitle.value = '编辑平台'
    Object.assign(platformForm, row)
    platformDialogVisible.value = true
  }
}

const handlePlatformSubmit = async () => {
  const valid = await (platformFormRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingPlatformId.value) {
      await updatePlatform(editingPlatformId.value, platformForm)
      ElMessage.success('编辑成功')
    } else {
      await createPlatform(platformForm)
      ElMessage.success('新增成功')
    }
    platformDialogVisible.value = false
    await fetchPlatforms()
  } catch (error) {
    // Error already handled by interceptor
  }
}

const handleDeletePlatform = (row: PlatformItem) => {
  ElMessageBox.confirm('确定删除该平台吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deletePlatform(row.id)
        ElMessage.success('删除成功')
        await fetchPlatforms()
      } catch (error) {
        // Error already handled by interceptor
      }
    })
    .catch(() => {})
}

const handleAddAuthId = () => {
  ElMessage.info('添加认证ID')
}

const handleSyncAll = () => {
  ElMessage.success('全部同步至视频源')
}

const handleSyncSelected = () => {
  if (selectedDevices.value.length === 0) {
    ElMessage.warning('请先选择设备')
    return
  }
  ElMessage.success(`已同步 ${selectedDevices.value.length} 个设备至视频源`)
}

const openDeviceModal = (type: 'edit', row?: DeviceItem) => {
  if (type === 'edit' && row) {
    editingDeviceId.value = row.id
    deviceDialogTitle.value = '编辑设备'
    Object.assign(deviceForm, row)
    deviceDialogVisible.value = true
  }
}

const handleDeviceSubmit = async () => {
  const valid = await (deviceFormRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingDeviceId.value) {
      await updateDevice(editingDeviceId.value, deviceForm)
      ElMessage.success('编辑成功')
    } else {
      await createDevice({ ...deviceForm, syncVideoSource: '否' })
      ElMessage.success('新增成功')
    }
    deviceDialogVisible.value = false
    await fetchDevices()
  } catch (error) {
    // Error already handled by interceptor
  }
}

const handleDeleteDevice = (row: DeviceItem) => {
  ElMessageBox.confirm('确定删除该设备吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteDevice(row.id)
        ElMessage.success('删除成功')
        await fetchDevices()
      } catch (error) {
        // Error already handled by interceptor
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.gb28181 {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-actions .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

:deep(.el-card__header) {
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.02);
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
