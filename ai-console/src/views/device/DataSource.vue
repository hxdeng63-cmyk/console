<template>
  <div class="data-source">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.name" placeholder="请输入数据源名称" style="width: 180px" clearable />
        <el-select v-model="searchForm.accessType" placeholder="请选择接入方式" style="width: 160px" clearable>
          <el-option label="本地" value="本地" />
          <el-option label="远程" value="远程" />
          <el-option label="RTSP" value="RTSP" />
          <el-option label="GB28181" value="GB28181" />
          <el-option label="ONVIF" value="ONVIF" />
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
    <div class="table-wrapper">
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
        <el-table-column prop="region" label="区域" width="80" align="center" />
        <el-table-column prop="org" label="组织" width="100" align="center">
          <template #default="{ row }">
            <el-link type="primary" :underline="false">{{ row.org }}</el-link>
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
            <el-form-item label="名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入数据源名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="接入方式" prop="accessType">
              <el-select v-model="form.accessType" placeholder="请选择" style="width: 100%">
                <el-option label="本地" value="本地" />
                <el-option label="远程" value="远程" />
                <el-option label="RTSP" value="RTSP" />
                <el-option label="GB28181" value="GB28181" />
                <el-option label="ONVIF" value="ONVIF" />
              </el-select>
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
          <el-col :span="12">
            <el-form-item label="数据源类型" prop="dataSourceType">
              <el-input v-model="form.dataSourceType" placeholder="请输入数据源类型" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域" prop="region">
              <el-input v-model="form.region" placeholder="请输入区域" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="组织" prop="org">
              <el-input v-model="form.org" placeholder="请输入组织" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设备" prop="device">
              <el-input v-model="form.device" placeholder="请输入设备" />
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
import { ref, computed, reactive } from 'vue'
import { Plus, DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

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
  setting: string
  remark: string
  memoryUsage: number
  diskSize: string
  diskUsage: number
}

const searchForm = reactive({
  name: '',
  accessType: ''
})

// 与用户管理组织关联的 mock 数据 — 海东分公司 / 西宁分公司
const tableData = ref<DataSourceItem[]>([
  { id: 1,  name: 'S201海东分公司K228+300下行(道路沿线)',   status: '在线', rtspUrl: 'rtsp://admin:admin12345@63.81.10.1:554/stream1',  pushUrl: 'rtsp://172.17.0.1:8554/live/0a68f0f6a3564c46934041a82d24bb37', accessType: '本地', longitude: '102.1041', latitude: '36.5012', dataSourceType: '设备',     region: 'S201', org: '海东分公司', device: '摄像头A01', setting: '-', remark: '-', memoryUsage: 45, diskSize: '1TB',   diskUsage: 62 },
  { id: 2,  name: 'S201海东分公司K199+650上行(道路沿线)',   status: '在线', rtspUrl: 'rtsp://admin:admin12345@63.81.10.2:554/stream1',  pushUrl: 'rtsp://172.17.0.1:8554/live/656ce5c19d7942b1b7b397948ca9b2ed', accessType: '本地', longitude: '102.0856', latitude: '36.4834', dataSourceType: '设备',     region: 'S201', org: '海东分公司', device: '摄像头A02', setting: '-', remark: '-', memoryUsage: 52, diskSize: '1TB',   diskUsage: 58 },
  { id: 3,  name: 'G213策磨高速乐化路段K16+250上行',        status: '在线', rtspUrl: 'rtsp://admin:LHGL2022..@63.86.10.3:554/stream1', pushUrl: 'rtsp://172.17.0.1:8554/live/6ab4192028584f138327e13bf69f8b45', accessType: '本地', longitude: '102.2031', latitude: '36.5610', dataSourceType: '数据源',   region: 'G213', org: '海东分公司', device: '雷达R01',  setting: '-', remark: '隧道入口', memoryUsage: 72, diskSize: '2TB',   diskUsage: 45 },
  { id: 4,  name: 'G213策磨高速乐化路段K10+150上行',        status: '在线', rtspUrl: 'rtsp://admin:LHGL2022..@63.86.10.4:554/stream1', pushUrl: 'rtsp://172.17.0.1:8554/live/5954002036b2402ea5e9b7d815753a66', accessType: 'RTSP',  longitude: '102.1654', latitude: '36.5448', dataSourceType: '数据源',   region: 'G213', org: '海东分公司', device: '雷达R02',  setting: '-', remark: '互通立交', memoryUsage: 68, diskSize: '2TB',   diskUsage: 41 },
  { id: 5,  name: 'G213策磨高速乐化路段K9+045下行',         status: '离线', rtspUrl: 'rtsp://admin:LHGL2022..@63.86.10.5:554/stream1', pushUrl: 'rtsp://172.17.0.1:8554/live/ad9349b5ddc8404ea562526037c287dc', accessType: 'RTSP',  longitude: '102.1523', latitude: '36.5380', dataSourceType: '数据源',   region: 'G213', org: '海东分公司', device: '雷达R03',  setting: '-', remark: '急弯路段', memoryUsage: 91, diskSize: '500GB', diskUsage: 88 },
  { id: 6,  name: 'S201海东分公司K195+700上行(道路沿线)',   status: '在线', rtspUrl: 'rtsp://admin:admin12345@63.81.10.6:554/stream1',  pushUrl: 'rtsp://172.17.0.1:8554/live/ab9fe5bd7cfd43cf85805bbf89aa40b2', accessType: '本地', longitude: '102.0612', latitude: '36.4710', dataSourceType: '设备',     region: 'S201', org: '海东分公司', device: '摄像头A03', setting: '-', remark: '-', memoryUsage: 38, diskSize: '1TB',   diskUsage: 55 },
  { id: 7,  name: 'G213策磨高速乐化路段K8+150下行',         status: '在线', rtspUrl: 'rtsp://admin:LHGL2022..@63.86.10.7:554/stream1', pushUrl: 'rtsp://172.17.0.1:8554/live/df0a0cd5999c46f79c64fe559fa54c12', accessType: 'RTSP',  longitude: '102.1398', latitude: '36.5324', dataSourceType: '数据源',   region: 'G213', org: '海东分公司', device: '雷达R04',  setting: '-', remark: '-', memoryUsage: 55, diskSize: '2TB',   diskUsage: 35 },
  { id: 8,  name: 'S201西宁分公司K45+200上行(道路沿线)',     status: '在线', rtspUrl: 'rtsp://admin:xn12345@63.82.20.1:554/stream1',    pushUrl: 'rtsp://172.17.0.1:8554/live/c8a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5', accessType: '本地', longitude: '101.7742', latitude: '36.6215', dataSourceType: '设备',     region: 'S201', org: '西宁分公司', device: '摄像头B01', setting: '-', remark: '-', memoryUsage: 60, diskSize: '1TB',   diskUsage: 72 },
  { id: 9,  name: 'S201西宁分公司K38+600下行(道路沿线)',     status: '在线', rtspUrl: 'rtsp://admin:xn12345@63.82.20.2:554/stream1',    pushUrl: 'rtsp://172.17.0.1:8554/live/d5c4b3a2f1e0987654321098abcdef01', accessType: '本地', longitude: '101.6251', latitude: '36.5830', dataSourceType: '设备',     region: 'S201', org: '西宁分公司', device: '摄像头B02', setting: '-', remark: '-', memoryUsage: 42, diskSize: '1TB',   diskUsage: 51 },
  { id: 10, name: 'G213策磨高速西宁段K89+100下行',          status: '离线', rtspUrl: 'rtsp://admin:xn213@63.86.20.3:554/stream1',      pushUrl: 'rtsp://172.17.0.1:8554/live/f1e2d3c4b5a69788756453a2b1c0d9e8', accessType: 'RTSP',  longitude: '101.8912', latitude: '36.6500', dataSourceType: '数据源',   region: 'G213', org: '西宁分公司', device: '雷达R05',  setting: '-', remark: '隧道出口', memoryUsage: 85, diskSize: '500GB', diskUsage: 93 },
  { id: 11, name: '西宁分公司环城高速K120+500上行',          status: '在线', rtspUrl: 'rtsp://admin:xncity@63.82.20.4:554/stream1',     pushUrl: 'rtsp://172.17.0.1:8554/live/a1b2c3d4e5f6789012345678abcdef01', accessType: 'GB28181', longitude: '101.7520', latitude: '36.6088', dataSourceType: '数据源',   region: 'G213', org: '西宁分公司', device: '球机D01',  setting: '-', remark: '城市入口', memoryUsage: 33, diskSize: '4TB',   diskUsage: 28 },
  { id: 12, name: '西宁分公司环城高速K115+300下行',          status: '在线', rtspUrl: 'rtsp://admin:xncity@63.82.20.5:554/stream1',     pushUrl: 'rtsp://172.17.0.1:8554/live/0123456789abcdef0123456789abcdef', accessType: 'ONVIF',  longitude: '101.6813', latitude: '36.5892', dataSourceType: '数据源',   region: 'G213', org: '西宁分公司', device: '球机D02',  setting: '-', remark: '-', memoryUsage: 28, diskSize: '4TB',   diskUsage: 22 },
])

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
  accessType: '本地',
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
  diskUsage: 0
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入数据源名称', trigger: 'blur' }],
  accessType: [{ required: true, message: '请选择接入方式', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: DataSourceItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑数据源'
    Object.assign(form, row)
  } else {
    editingId.value = null
    dialogTitle.value = '新增数据源'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingId.value) {
    const idx = tableData.value.findIndex(item => item.id === editingId.value)
    if (idx !== -1) Object.assign(tableData.value[idx], form)
    ElMessage.success('编辑成功')
  } else {
    tableData.value.push({ id: Date.now(), ...form })
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
}

const handleDelete = (row: DataSourceItem) => {
  ElMessageBox.confirm('确定删除该数据源吗？', '提示', { type: 'warning' })
    .then(() => {
      const idx = tableData.value.findIndex(item => item.id === row.id)
      if (idx !== -1) tableData.value.splice(idx, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
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

/* 使用率进度条 */
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

