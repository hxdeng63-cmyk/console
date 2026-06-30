<template>
  <div class="data-source">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.name" placeholder="请输入数据源名称" style="width: 180px" clearable />
        <el-select v-model="searchForm.accessType" placeholder="请选择接入方式" style="width: 160px" clearable>
          <el-option label="RTMP" value="RTMP" />
          <el-option label="RTSP" value="RTSP" />
          <el-option label="HTTP/HTTPS" value="HTTP/HTTPS" />
        </el-select>
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-wrapper" v-loading="loading">
      <el-table :data="pagedData" border stripe>
        <el-table-column prop="name" label="名称" min-width="160" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === '在线' ? 'success' : row.status === '离线' ? 'danger' : 'info'" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rtspUrl" label="原始流地址" min-width="140" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="mono-text">{{ row.rtspUrl }}</span>
            <el-icon class="copy-icon" @click="copyText(row.rtspUrl)"><DocumentCopy /></el-icon>
          </template>
        </el-table-column>
        <el-table-column prop="pushUrl" label="推流地址" width="90" align="center">
          <template #default="{ row }">
            <el-link type="primary" :underline="false" @click="showMore(row)">查看更多</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="accessType" label="接入方式" width="85" align="center" />
        <el-table-column prop="longitude" label="坐标经度" width="85" align="center" />
        <el-table-column prop="latitude" label="坐标纬度" width="85" align="center" />
        <el-table-column prop="dataSourceType" label="数据源类型" width="90" align="center" />
        <el-table-column prop="region_name" label="区域" width="80" align="center" />
        <el-table-column prop="org_name" label="组织" width="100" align="center">
          <template #default="{ row }">
            <el-link type="primary" :underline="false">{{ row.org_name || row.org }}</el-link>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="100" show-overflow-tooltip />
        <el-table-column prop="memoryUsage" label="内存使用率" width="100" align="center">
          <template #default="{ row }">
            <div class="usage-bar">
              <div class="usage-bar__bg">
                <div class="usage-bar__fill" :style="{ width: row.memoryUsage + '%', background: row.memoryUsage > 80 ? '#FF006E' : row.memoryUsage > 60 ? '#FFAA00' : '#36D68A' }" />
              </div>
              <span class="usage-bar__text">{{ row.memoryUsage }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="diskSize" label="硬盘大小" width="90" align="center" />
        <el-table-column prop="diskUsage" label="硬盘使用率" width="100" align="center">
          <template #default="{ row }">
            <div class="usage-bar">
              <div class="usage-bar__bg">
                <div class="usage-bar__fill" :style="{ width: row.diskUsage + '%', background: row.diskUsage > 80 ? '#FF006E' : row.diskUsage > 60 ? '#FFAA00' : '#36D68A' }" />
              </div>
              <span class="usage-bar__text">{{ row.diskUsage }}%</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="设置" width="150" align="center">
          <template #default="{ row }">
            <el-button class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
            <el-button class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

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

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备" prop="device_id">
              <el-select
                v-model="form.device_id"
                placeholder="请选择设备"
                style="width: 100%"
                filterable
                @change="onDeviceChange"
              >
                <el-option
                  v-for="d in deviceList"
                  :key="d.id"
                  :label="d.name"
                  :value="d.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名称" prop="name">
              <el-input v-model="form.name" placeholder="选择设备后自动生成" readonly />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="接入方式" prop="accessType">
              <el-select v-model="form.accessType" placeholder="请选择" style="width: 100%">
                <el-option label="RTMP" value="RTMP" />
                <el-option label="RTSP" value="RTSP" />
                <el-option label="HTTP/HTTPS" value="HTTP/HTTPS" />
                <el-option label="本地" value="本地" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数据源类型" prop="dataSourceType">
              <el-input v-model="form.dataSourceType" placeholder="请输入数据源类型" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="原始流地址" prop="rtspUrl">
              <el-input v-model="form.rtspUrl" placeholder="请输入原始流地址" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="推流地址" prop="pushUrl">
              <el-input v-model="form.pushUrl" placeholder="请输入推流地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="坐标经度" prop="longitude">
              <el-input v-model="form.longitude" placeholder="请输入经度" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="坐标纬度" prop="latitude">
              <el-input v-model="form.latitude" placeholder="请输入纬度" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="内存使用率(%)" prop="memoryUsage">
              <el-input-number v-model="form.memoryUsage" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="硬盘大小" prop="diskSize">
              <el-select v-model="form.diskSize" style="width: 100%">
                <el-option label="500GB" value="500GB" />
                <el-option label="1TB" value="1TB" />
                <el-option label="2TB" value="2TB" />
                <el-option label="4TB" value="4TB" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="硬盘使用率(%)" prop="diskUsage">
              <el-input-number v-model="form.diskUsage" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="备注" prop="remark">
              <el-input v-model="form.remark" placeholder="请输入备注" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 查看更多弹窗 -->
    <el-dialog
      v-model="moreDialogVisible"
      title="推流地址详情"
      width="600px"
    >
      <div class="url-content">
        <p><strong>推流地址：</strong></p>
        <div class="url-box">
          {{ currentUrl }}
          <el-icon class="copy-icon" @click="copyText(currentUrl)"><DocumentCopy /></el-icon>
        </div>
      </div>
      <template #footer>
        <el-button @click="moreDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getDataSources,
  createDataSource,
  updateDataSource,
  deleteDataSource
} from '@/api/data-sources'
import { getDevices } from '@/api/devices'
import { useRegions } from '@/composables/useRegions'

interface DataSourceItem {
  id: number
  name: string
  status: string
  rtspUrl: string
  pushUrl: string
  accessType: string
  longitude: string
  latitude: string
  dataSourceType: string
  region: string
  org: string
  device: string
  remark: string
  memoryUsage: number
  diskSize: string
  diskUsage: number
  device_id?: number
  region_id?: number
  org_id?: number
  device_name?: string
  region_name?: string
  org_name?: string
}

interface DeviceItem {
  id: number
  name: string
  region_id?: number
  org_id?: number
  region_name?: string
  org_name?: string
}

const searchForm = reactive({
  name: '',
  accessType: ''
})

const { allRegions, loadRegions } = useRegions()

const tableData = ref<DataSourceItem[]>([])
const deviceList = ref<DeviceItem[]>([])
const loading = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    const matchName = !searchForm.name || item.name.includes(searchForm.name)
    const matchAccess = !searchForm.accessType || item.accessType === searchForm.accessType
    return matchName && matchAccess
  })
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const handleSearch = () => {
  currentPage.value = 1
}

const copyText = (text: string) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制')
}

const showMore = (row: DataSourceItem) => {
  currentUrl.value = row.pushUrl
  moreDialogVisible.value = true
}

const currentUrl = ref('')
const moreDialogVisible = ref(false)

const dialogVisible = ref(false)
const dialogTitle = ref('新增数据源')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  name: '',
  status: '在线',
  rtspUrl: '',
  pushUrl: '',
  accessType: 'RTMP',
  longitude: '',
  latitude: '',
  dataSourceType: '',
  region: '',
  org: '',
  device: '',
  setting: '-',
  remark: '',
  memoryUsage: 0,
  diskSize: '1TB',
  diskUsage: 0,
  device_id: null as number | null,
  region_id: null as number | null,
  org_id: null as number | null,
})

const form = reactive(defaultForm())

const rules = {
  device_id: [{ required: true, message: '请选择设备', trigger: 'change' }],
  name: [{ required: true, message: '名称自动生成', trigger: 'blur' }],
  accessType: [{ required: true, message: '请选择接入方式', trigger: 'change' }]
}

function onDeviceChange(deviceId: number) {
  const device = deviceList.value.find(d => d.id === deviceId)
  if (!device) return

  // 自动填充名称：大区域-小区域-设备名称
  const region = allRegions.value.find(r => r.id === device.region_id)
  const parentRegion = region?.parent_id ? allRegions.value.find(r => r.id === region.parent_id) : null
  const parts = [parentRegion?.name, region?.name, device.name].filter(Boolean)
  form.name = parts.join('-')

  // 自动填充区域和组织
  form.device_id = deviceId
  form.region_id = device.region_id || null
  form.org_id = device.org_id || null
}

const openModal = (type: 'add' | 'edit', row?: DataSourceItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑数据源'
    Object.assign(form, {
      name: row.name,
      status: row.status,
      rtspUrl: row.rtspUrl,
      pushUrl: row.pushUrl,
      accessType: row.accessType,
      longitude: row.longitude,
      latitude: row.latitude,
      dataSourceType: row.dataSourceType,
      region: row.region,
      org: row.org,
      device: row.device,
      remark: row.remark,
      memoryUsage: row.memoryUsage,
      diskSize: row.diskSize,
      diskUsage: row.diskUsage,
      device_id: row.device_id || null,
      region_id: row.region_id || null,
      org_id: row.org_id || null,
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新增数据源'
  }
  dialogVisible.value = true
}

function mapItem(item: any): DataSourceItem {
  return {
    id: item.id,
    name: item.name,
    status: item.status,
    rtspUrl: item.rtsp_url || '',
    pushUrl: item.push_url || '',
    accessType: item.access_type || '',
    longitude: item.longitude || '',
    latitude: item.latitude || '',
    dataSourceType: item.data_source_type || '',
    region: item.region || '',
    org: item.org || '',
    device: item.device || '',
    remark: item.remark || '',
    memoryUsage: item.memory_usage || 0,
    diskSize: item.disk_size || '',
    diskUsage: item.disk_usage || 0,
    device_id: item.device_id,
    region_id: item.region_id,
    org_id: item.org_id,
    device_name: item.device_name,
    region_name: item.region_name,
    org_name: item.org_name,
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getDataSources()
    const items = res.data?.items || res.items || []
    tableData.value = items.map(mapItem)
  } catch (err) {
    ElMessage.error('获取数据源列表失败')
  } finally {
    loading.value = false
  }
}

const fetchDevices = async () => {
  try {
    const res = await getDevices({ page_size: 100 })
    deviceList.value = res.data?.items || res.items || []
  } catch (err) {
    console.error('获取设备列表失败:', err)
  }
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  const payload = {
    name: form.name,
    status: form.status,
    rtsp_url: form.rtspUrl,
    push_url: form.pushUrl,
    access_type: form.accessType,
    longitude: form.longitude,
    latitude: form.latitude,
    data_source_type: form.dataSourceType,
    region: form.region,
    org: form.org,
    device: form.device,
    remark: form.remark,
    memory_usage: form.memoryUsage,
    disk_size: form.diskSize,
    disk_usage: form.diskUsage,
    device_id: form.device_id,
    region_id: form.region_id,
    org_id: form.org_id,
  }

  try {
    if (editingId.value) {
      await updateDataSource(editingId.value, payload)
      ElMessage.success('编辑成功')
    } else {
      await createDataSource(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await fetchData()
  } catch (err) {
    ElMessage.error(editingId.value ? '编辑失败' : '新增失败')
  }
}

const handleDelete = (row: DataSourceItem) => {
  ElMessageBox.confirm('确定删除该数据源吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteDataSource(row.id)
        ElMessage.success('删除成功')
        await fetchData()
      } catch (err) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

onMounted(() => {
  loadRegions()
  fetchData()
  fetchDevices()
})
</script>

<style scoped>
.data-source {
  padding: 20px;
}

.table-wrapper .el-table {
  min-width: 1900px;
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

.copy-icon {
  margin-left: 8px;
  cursor: pointer;
  color: #00E5FF;
  vertical-align: middle;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.url-content {
  padding: 10px 0;
}

.url-box {
  background: rgba(255, 255, 255, 0.05);
  padding: 12px;
  border-radius: 4px;
  font-family: monospace;
  word-break: break-all;
  display: flex;
  align-items: center;
  gap: 8px;
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

.usage-bar {
  display: flex;
  align-items: center;
  gap: 6px;
}

.usage-bar__bg {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}

.usage-bar__fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.4s ease;
}

.usage-bar__text {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: rgba(255, 255, 255, 0.7);
  min-width: 32px;
  text-align: right;
}
</style>
