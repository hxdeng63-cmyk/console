<template>
  <div class="events-page">
    <!-- 第一行筛选 -->
    <div class="toolbar">
      <div class="left-area">
        <el-select v-model="searchForm.companyName" placeholder="公司名称" style="width: 130px" clearable>
          <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.name" />
        </el-select>
        <el-select v-model="searchForm.regionName" placeholder="区域" style="width: 100px" clearable>
          <el-option v-for="r in level1Regions" :key="r.id" :label="r.name" :value="r.name" />
        </el-select>
        <el-select v-model="searchForm.algorithmName" placeholder="算法" style="width: 120px" clearable>
          <el-option label="交通算法" value="交通算法" />
        </el-select>
        <el-select v-model="searchForm.eventType" placeholder="事件" style="width: 150px" clearable>
          <el-option v-for="type in eventTypeOptions" :key="type" :label="type" :value="type" />
        </el-select>
        <el-input v-model="searchForm.deviceName" placeholder="设备名称" style="width: 160px" clearable />
      </div>
    </div>

    <!-- 第二行筛选 -->
    <div class="toolbar secondary">
      <div class="left-area">
        <el-select v-model="searchForm.isCompliant" placeholder="是否合规" style="width: 110px" clearable>
          <el-option label="是" value="是" />
          <el-option label="否" value="否" />
        </el-select>
        <el-select v-model="searchForm.processStatus" placeholder="处置状态" style="width: 110px" clearable>
          <el-option label="已处置" value="已处置" />
          <el-option label="未处置" value="未处置" />
          <el-option label="处理中" value="处理中" />
        </el-select>
        <el-date-picker v-model="searchForm.startTime" type="datetime" placeholder="开始时间" style="width: 170px" />
        <el-date-picker v-model="searchForm.endTime" type="datetime" placeholder="结束时间" style="width: 170px" />
      </div>
      <div class="right-area">
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button class="btn-reset" @click="handleReset">重置</el-button>
        <el-button class="btn-export" @click="handleExport">导出</el-button>
      </div>
    </div>

    <!-- 视图切换 -->
    <div class="view-toggle">
      <el-radio-group v-model="viewMode">
        <el-radio-button value="list">列表模式</el-radio-button>
        <el-radio-button value="image">图片卡片模式</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 列表模式表格 -->
    <el-table v-if="viewMode === 'list'" :data="pagedData" border stripe style="width: 100%" v-loading="loading">
      <el-table-column prop="companyName" label="公司名称" width="100" align="center" />
      <el-table-column prop="regionName" label="区域" width="70" align="center" />
      <el-table-column prop="deviceName" label="设备名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="algorithmName" label="算法" width="100" align="center" />
      <el-table-column prop="eventTypeName" label="事件" width="120" align="center">
        <template #default="{ row }">
          <span class="event-type-text">{{ row.eventTypeName }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="processStatus" label="处理状态" width="85" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.processStatus)" size="small">{{ row.processStatus }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="reportTime" label="上报时间" width="160" align="center" />
      <el-table-column label="操作" width="170" fixed="right" align="center">
        <template #default="{ row }">
          <el-button class="action-edit" size="small" @click="handleDetail(row)">详情查看</el-button>
          <el-button class="action-edit" size="small" @click="handleVideo(row)">视频回放</el-button>
        </template>
      </el-table-column>
      <el-table-column label="处置" width="65" fixed="right" align="center">
        <template #default="{ row }">
          <el-button class="action-edit" size="small" @click="openDisposeDialog(row)">处置</el-button>
        </template>
      </el-table-column>
      <el-table-column label="考核" width="95" fixed="right" align="center">
        <template #default="{ row }">
          <el-button class="action-edit" size="small" @click="openPenaltyDialog(row)">开具考核单</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 图片卡片模式 -->
    <div v-else class="image-grid">
      <div v-for="item in pagedData" :key="item.id" class="event-card" @click="handleDetail(item)">
        <div class="card-image">
          <img :src="item.imageUrl" alt="事件图片" />
          <div class="detect-box" :style="item.detectBox"></div>
        </div>
        <div class="card-info">
          <div class="info-item device-name">{{ item.deviceName }}</div>
          <div class="info-row">
            <span class="label">公司名称：</span>
            <span class="value">{{ item.companyName }}</span>
          </div>
          <div class="info-row">
            <span class="label">区域名称：</span>
            <span class="value">{{ item.regionName }}</span>
          </div>
          <div class="info-row">
            <span class="label">事件类型：</span>
            <span class="value event-type">{{ item.eventTypeName }}</span>
          </div>
          <div class="info-row">
            <span class="label">是否合规：</span>
            <span class="value" :class="item.isCompliant === '是' ? 'compliance-yes' : 'compliance-no'">{{ item.isCompliant }}</span>
          </div>
          <div class="info-row capture-time">
            <span class="label">抓拍时间：</span>
            <span class="value">{{ item.reportTime }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="filteredData.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="预警详情" width="900px" :close-on-click-modal="false">
      <div class="detail-container">
        <div class="detail-image">
          <img :src="currentRecord?.imageUrl" alt="事件图片" />
          <div class="detect-box" :style="currentRecord?.detectBox"></div>
        </div>
        <div class="detail-info">
          <div class="info-section">
            <h4>基本信息</h4>
            <div class="info-grid">
              <div class="info-item">
                <span class="label">公司名称：</span>
                <span class="value">{{ currentRecord?.companyName }}</span>
              </div>
              <div class="info-item">
                <span class="label">区域名称：</span>
                <span class="value">{{ currentRecord?.regionName }}</span>
              </div>
              <div class="info-item">
                <span class="label">设备名称：</span>
                <span class="value">{{ currentRecord?.deviceName }}</span>
              </div>
              <div class="info-item">
                <span class="label">算法名称：</span>
                <span class="value">{{ currentRecord?.algorithmName }}</span>
              </div>
              <div class="info-item">
                <span class="label">事件类型：</span>
                <span class="value event-type">{{ currentRecord?.eventTypeName }}</span>
              </div>
              <div class="info-item">
                <span class="label">事件详情：</span>
                <span class="value">{{ currentRecord?.eventDetail }}</span>
              </div>
              <div class="info-item">
                <span class="label">是否合规：</span>
                <span
                  class="value"
                  :class="currentRecord?.isCompliant === '是' ? 'compliance-yes' : 'compliance-no'"
                >{{ currentRecord?.isCompliant }}</span>
              </div>
              <div class="info-item">
                <span class="label">处理状态：</span>
                <el-tag :type="getStatusType(currentRecord?.processStatus || '')" size="small">{{ currentRecord?.processStatus }}</el-tag>
              </div>
              <div class="info-item">
                <span class="label">上报时间：</span>
                <span class="value">{{ currentRecord?.reportTime }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleVideoPlayback">视频回放</el-button>
        <el-button type="primary" @click="openDisposeDialog(currentRecord!)">处置</el-button>
        <el-button type="primary" @click="openPenaltyDialog(currentRecord!)">开具考核单</el-button>
      </template>
    </el-dialog>

    <!-- 导出弹窗 -->
    <el-dialog v-model="exportDialogVisible" title="导出" width="400px" :close-on-click-modal="false">
      <div class="export-options">
        <el-checkbox v-model="exportForm.includeImage">带有图片</el-checkbox>
        <div class="export-format">
          <span>导出格式：</span>
          <el-radio-group v-model="exportForm.format">
            <el-radio value="excel">Excel</el-radio>
            <el-radio value="csv">CSV</el-radio>
          </el-radio-group>
        </div>
      </div>
      <template #footer>
        <el-button @click="exportDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmExport">确定</el-button>
      </template>
    </el-dialog>

    <!-- 处置反馈弹窗 -->
    <el-dialog v-model="disposeDialogVisible" title="处置反馈" width="500px" :close-on-click-modal="false">
      <el-form ref="disposeFormRef" :model="disposeForm" :rules="disposeRules" label-width="100px">
        <el-form-item label="处置人">
          <el-input v-model="disposeForm.disposer" disabled />
        </el-form-item>
        <el-form-item label="处置码" prop="disposeCode">
          <el-input v-model="disposeForm.disposeCode" placeholder="请输入处置码" />
        </el-form-item>
        <el-form-item label="处置照片">
          <div class="upload-area">
            <el-upload action="#" list-type="picture-card" :auto-upload="false" :on-change="handleDisposePhotoChange">
              <el-icon><Plus /></el-icon>
            </el-upload>
          </div>
        </el-form-item>
        <el-form-item label="处置意见" prop="disposeOpinion">
          <el-input v-model="disposeForm.disposeOpinion" type="textarea" placeholder="请输入处置意见" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="disposeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleDisposeSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 开具考核单弹窗 -->
    <el-dialog v-model="penaltyDialogVisible" title="罚单" width="500px" :close-on-click-modal="false">
      <el-form ref="penaltyFormRef" :model="penaltyForm" :rules="penaltyRules" label-width="100px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="penaltyForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="开具人">
          <el-input v-model="penaltyForm.issuer" disabled />
        </el-form-item>
        <el-form-item label="违章单位" prop="violationUnit">
          <el-input v-model="penaltyForm.violationUnit" placeholder="请输入违章单位" />
        </el-form-item>
        <el-form-item label="考核金额" prop="penaltyAmount">
          <el-input-number v-model="penaltyForm.penaltyAmount" :min="0" :max="999999" />
        </el-form-item>
        <el-form-item label="签发单位" prop="issuingUnit">
          <el-input v-model="penaltyForm.issuingUnit" placeholder="请输入签发单位" />
        </el-form-item>
        <el-form-item label="事由" prop="reason">
          <el-input v-model="penaltyForm.reason" type="textarea" placeholder="请输入事由" :rows="3" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="penaltyForm.remark"
            type="textarea"
            placeholder="请输入备注（100字以内）"
            :rows="2"
            :maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="penaltyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePenaltySubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useRegions } from '@/composables/useRegions'

interface EventItem {
  id: number
  companyName: string
  regionName: string
  deviceName: string
  algorithmName: string
  eventTypeName: string
  eventDetail: string
  processStatus: string
  reportTime: string
  isCompliant: string
  imageUrl: string
  videoUrl: string
  detectBox: { top: string; left: string; width: string; height: string }
}

// 16种事件类型
const eventTypeOptions = [
  '疑似事故',
  '作业人员',
  '交通阻塞',
  '异常停车',
  '烟雾',
  '作业车辆识别',
  '非机动车驶入',
  '占用应急车道',
  '逆向行驶',
  '通过卡车数量',
  '通过大客车数量',
  '通过摩托车数量',
  '通过小汽车数量',
  '下行车流量',
  '上行车流量',
  '行人闯入'
]

const searchForm = reactive({
  companyName: '',
  regionName: '',
  algorithmName: '',
  eventType: '',
  deviceName: '',
  isCompliant: '',
  processStatus: '',
  startTime: '',
  endTime: ''
})

const viewMode = ref('list')
const currentPage = ref(1)
const pageSize = ref(10)

const { companies, level1Regions, loadRegions } = useRegions()

const loading = ref(false)

const fetchEvents = async () => {
  loading.value = true
  try {
    const { getAlgorithmEvents } = await import('@/api/algorithm-events')
    const res = await getAlgorithmEvents({ page_size: 100 })
    const data = res.data || res
    tableData.value = data.items || []
  } catch (e) {
    console.error('获取预警事件失败:', e)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRegions()
  fetchEvents()
})

// 详情弹窗
const detailDialogVisible = ref(false)
const currentRecord = ref<EventItem | null>(null)

// 导出弹窗
const exportDialogVisible = ref(false)
const exportForm = reactive({
  includeImage: false,
  format: 'excel'
})

// 处置反馈弹窗
const disposeDialogVisible = ref(false)
const disposeFormRef = ref()
const disposeForm = reactive({
  disposer: 'admin',
  disposeCode: '',
  disposePhotos: [] as string[],
  disposeOpinion: ''
})
const disposeRules = {
  disposeOpinion: [{ required: true, message: '请输入处置意见', trigger: 'blur' }]
}

// 开具考核单弹窗
const penaltyDialogVisible = ref(false)
const penaltyFormRef = ref()
const penaltyForm = reactive({
  title: '',
  issuer: 'admin',
  violationUnit: '',
  penaltyAmount: 1,
  issuingUnit: '',
  reason: '',
  remark: ''
})
const penaltyRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  violationUnit: [{ required: true, message: '请输入违章单位', trigger: 'blur' }],
  penaltyAmount: [{ required: true, message: '请输入考核金额', trigger: 'blur' }],
  issuingUnit: [{ required: true, message: '请输入签发单位', trigger: 'blur' }],
  reason: [{ required: true, message: '请输入事由', trigger: 'blur' }]
}

const tableData = ref<EventItem[]>([])

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    if (searchForm.companyName && item.companyName !== searchForm.companyName) return false
    if (searchForm.regionName && item.regionName !== searchForm.regionName) return false
    if (searchForm.algorithmName && item.algorithmName !== searchForm.algorithmName) return false
    if (searchForm.eventType && item.eventTypeName !== searchForm.eventType) return false
    if (searchForm.deviceName && !item.deviceName.includes(searchForm.deviceName)) return false
    if (searchForm.isCompliant && item.isCompliant !== searchForm.isCompliant) return false
    if (searchForm.processStatus && item.processStatus !== searchForm.processStatus) return false
    return true
  })
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const getStatusType = (status: string) => {
  switch (status) {
    case '已处置':
      return 'success'
    case '处理中':
      return 'warning'
    case '未处置':
      return 'info'
    default:
      return 'info'
  }
}

const handleSearch = () => {
  currentPage.value = 1
  ElMessage.success('查询成功')
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    ;(searchForm as any)[key] = ''
  })
  currentPage.value = 1
  ElMessage.success('重置成功')
}

const handleExport = () => {
  exportDialogVisible.value = true
}

const confirmExport = () => {
  ElMessage.success(`导出成功，格式：${exportForm.format}${exportForm.includeImage ? '（带图片）' : ''}`)
  exportDialogVisible.value = false
}

const handleDetail = (row: EventItem) => {
  currentRecord.value = row
  detailDialogVisible.value = true
}

const handleVideo = (row: EventItem) => {
  ElMessage.info(`视频回放: ${row.deviceName}`)
}

const handleVideoPlayback = () => {
  if (currentRecord.value) {
    ElMessage.info(`视频回放: ${currentRecord.value.deviceName}`)
  }
}

// 处置相关
const openDisposeDialog = (row: EventItem) => {
  currentRecord.value = row
  disposeForm.disposer = 'admin'
  disposeForm.disposeCode = ''
  disposeForm.disposePhotos = []
  disposeForm.disposeOpinion = ''
  disposeDialogVisible.value = true
}

const handleDisposePhotoChange = (file: any) => {
  disposeForm.disposePhotos.push(file.url)
}

const handleDisposeSubmit = async () => {
  const valid = await (disposeFormRef.value as any).validate().catch(() => false)
  if (!valid) return
  ElMessage.success('处置成功')
  disposeDialogVisible.value = false
}

// 考核单相关
const openPenaltyDialog = (row: EventItem) => {
  currentRecord.value = row
  penaltyForm.title = `关于${row.eventTypeName}的考核`
  penaltyForm.issuer = 'admin'
  penaltyForm.violationUnit = row.companyName
  penaltyForm.penaltyAmount = 1
  penaltyForm.issuingUnit = ''
  penaltyForm.reason = `${row.deviceName}发生${row.eventTypeName}事件`
  penaltyForm.remark = ''
  penaltyDialogVisible.value = true
}

const handlePenaltySubmit = async () => {
  const valid = await (penaltyFormRef.value as any).validate().catch(() => false)
  if (!valid) return
  ElMessage.success('考核单已开具')
  penaltyDialogVisible.value = false
}
</script>

<style scoped>
.events-page {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.toolbar.secondary {
  margin-bottom: 16px;
}

.left-area {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.right-area {
  display: flex;
  gap: 10px;
  align-items: center;
}

.right-area .el-button--primary {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.right-area .el-button--primary:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.btn-reset {
  background: transparent;
  border-color: #00E5FF;
  color: #00E5FF;
}

.btn-reset:hover {
  background: rgba(0, 229, 255, 0.1);
}

.btn-export {
  background: #36D68A;
  border-color: #36D68A;
  color: #001a2e;
}

.btn-export:hover {
  background: #00FF88;
  border-color: #00FF88;
}

.view-toggle {
  margin-bottom: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 事件类型文字 */
.event-type-text {
  color: #FFAA00;
  font-weight: 600;
  font-size: 13px;
}

/* 操作按钮 - 青色 */
.action-edit {
  background: rgba(0, 229, 255, 0.15) !important;
  border: 1px solid rgba(0, 229, 255, 0.4) !important;
  color: #00E5FF !important;
  border-radius: 4px;
  padding: 4px 8px !important;
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

/* 图片卡片模式 */
.image-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 0;
}

.event-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.card-image {
  position: relative;
  width: 100%;
  height: 160px;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detect-box {
  position: absolute;
  border: 2px solid #FF006E;
  border-radius: 2px;
  pointer-events: none;
}

.card-info {
  padding: 12px;
}

.card-info .device-name {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text-primary);
}

.info-row {
  display: flex;
  font-size: 12px;
  margin-bottom: 4px;
}

.info-row .label {
  flex-shrink: 0;
  color: var(--text-secondary);
}

.info-row .value {
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-row .event-type {
  color: #FFAA00;
  font-weight: 600;
}

.compliance-yes {
  color: #00FF88 !important;
}

.compliance-no {
  color: #FF006E !important;
}

.capture-time {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--border-color);
}

/* 详情弹窗 */
.detail-container {
  display: flex;
  gap: 20px;
}

.detail-image {
  position: relative;
  width: 400px;
  height: 300px;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-info {
  flex: 1;
}

.info-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--text-primary);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.info-item {
  font-size: 14px;
}

.info-item .label {
  display: inline-block;
  min-width: 80px;
  color: var(--text-secondary);
}

.info-item .value {
  color: var(--text-primary);
}

.info-item .event-type {
  color: #FFAA00;
  font-weight: 600;
}

/* 导出弹窗 */
.export-options {
  padding: 10px 0;
}

.export-format {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 处置反馈弹窗 */
.upload-area {
  width: 100%;
}

/* 考核单弹窗 */
:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-dialog__footer .el-button--primary) {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

:deep(.el-dialog__footer .el-button--primary:hover) {
  background: #00B4D8;
  border-color: #00B4D8;
}
</style>
