<template>
  <div class="events-page">
    <!-- 第一行筛选 -->
    <div class="toolbar">
      <div class="left-area">
        <el-select v-model="searchForm.companyName" placeholder="公司名称" style="width: 130px" clearable @change="onCompanyChange">
          <el-option v-for="c in companies" :key="c.id" :label="c.name" :value="c.name" />
        </el-select>
        <el-cascader
          v-model="searchForm.regionId"
          :options="regionTree"
          :props="{ value: 'id', label: 'name', children: 'children', emitPath: false }"
          :placeholder="searchForm.companyName ? '区域（大区/小区）' : '请先选择公司'"
          style="width: 180px"
          clearable
          :disabled="!searchForm.companyName"
        />
        <el-select v-model="searchForm.algorithmName" placeholder="算法" style="width: 180px" clearable>
          <el-option
            v-for="algo in algorithmOptions"
            :key="algo.value"
            :label="algo.label"
            :value="algo.value"
          />
        </el-select>
        <el-select v-model="searchForm.eventType" placeholder="事件" style="width: 150px" clearable>
          <el-option
            v-for="type in eventTypeOptions"
            :key="type.value"
            :label="type.label"
            :value="type.value"
          />
        </el-select>
        <el-select
          v-model="searchForm.deviceId"
          placeholder="设备名称"
          style="width: 180px"
          clearable
          filterable
          :disabled="!searchForm.regionId"
          no-data-text="请先选择区域"
        >
          <el-option v-for="d in regionDevices" :key="d.id" :label="d.name" :value="d.id" />
        </el-select>
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

    <!-- 内容区域 -->
    <div class="content-wrapper">
      <!-- 列表模式表格 -->
      <el-table v-if="viewMode === 'list'" :data="pagedData" border stripe v-loading="loading">
      <el-table-column prop="companyName" label="公司名称" width="100" align="center" />
      <el-table-column label="区域" min-width="120" align="center">
        <template #default="{ row }">
          <span>{{ regionPathMap[row.regionName] || row.regionName }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="deviceName" label="设备名称" min-width="180" show-overflow-tooltip />
      <el-table-column prop="algorithmName" label="算法" width="100" align="center" />
      <el-table-column prop="eventTypeName" label="事件" width="110" align="center">
        <template #default="{ row }">
          <span class="event-type-text">{{ row.eventTypeName }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="processStatus" label="处理状态" width="85" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.processStatus)" size="small">{{ row.processStatus }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="上报时间" width="180" align="center">
        <template #default="{ row }">
          <span class="value">{{ formatDateTime(row.reportTime) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right" align="center">
        <template #default="{ row }">
          <el-button class="action-edit" size="small" @click="handleDetail(row)">详情查看</el-button>
          <el-button class="action-edit" size="small" @click="handleVideo(row)">视频回放</el-button>
          <el-button class="action-edit" size="small" @click="openDisposeDialog(row)">处置</el-button>
          <el-button class="action-edit" size="small" @click="openPenaltyDialog(row)">开具考核单</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 图片卡片模式 -->
    <div v-else class="image-grid">
      <div v-for="item in pagedData" :key="item.id" class="event-card" @click="handleDetail(item)">
        <div class="card-image">
          <img :src="item.imageUrl" alt="事件图片" @error="handleImageError" />
          <div class="image-placeholder" :style="{ display: item.imageUrl ? 'none' : 'flex' }">暂无图片</div>
        </div>
        <div class="card-info">
          <div class="info-item device-name">{{ item.deviceName }}</div>
          <div class="info-row">
            <span class="label">公司名称：</span>
            <span class="value">{{ item.companyName }}</span>
          </div>
          <div class="info-row">
            <span class="label">区域名称：</span>
            <span class="value">{{ regionPathMap[item.regionName] || item.regionName }}</span>
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
            <span class="value">{{ formatDateTime(item.reportTime) }}</span>
          </div>
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
        :total="totalCount"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="fetchEvents"
        @size-change="() => { currentPage = 1; fetchEvents() }"
      />
    </div>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailDialogVisible" title="预警详情" width="900px" :close-on-click-modal="false">
      <div class="detail-container">
        <div class="detail-image">
          <img :src="currentRecord?.imageUrl" alt="事件图片" @error="handleImageError" />
          <div class="image-placeholder" :style="{ display: currentRecord?.imageUrl ? 'none' : 'flex' }">暂无图片</div>
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
                <span class="value">{{ regionPathMap[currentRecord?.regionName] || currentRecord?.regionName }}</span>
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
                <span class="value">{{ formatDateTime(currentRecord?.reportTime) }}</span>
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

    <!-- 视频回放弹窗 -->
    <el-dialog v-model="videoDialogVisible" title="视频回放" width="800px" :close-on-click-modal="false">
      <div class="video-container">
        <video v-if="currentVideoUrl && !videoError" :src="currentVideoUrl" controls style="width: 100%; max-height: 500px;" @error="handleVideoError" />
        <div v-else style="text-align: center; padding: 40px; color: #999;">暂无视频</div>
      </div>
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
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { getDeviceGroupTree } from '@/api/device-groups'
import { getRegionTree, getFullRegionTree } from '@/api/regions'
import { getDevices } from '@/api/devices'
import { getAlgorithms } from '@/api/algorithms'
import { getEventTypes } from '@/api/event-types'
import { getEventTypeDisplayName } from '@/utils/eventType'
import { formatDateTime } from '@/utils/date'

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
}

// 事件类型选项，从后端 /event-types 动态加载
const eventTypeOptions = ref<{ label: string; value: string }[]>([])

const trafficAlgorithm = ref<any>(null)
const algorithmOptions = ref<{ label: string; value: string }[]>([])

const searchForm = reactive({
  companyName: '',
  regionId: null as number | null,
  regionName: '',
  algorithmName: '',
  eventType: '',
  deviceId: null as number | null,
  isCompliant: '',
  processStatus: '',
  startTime: '',
  endTime: ''
})

const regionTree = ref<any[]>([])  // cascader 用的单公司大区/小区树
const fullRegionTree = ref<any[]>([])  // 全公司区域树（公司→大区→小区），用于 regionPathMap
const regionDevices = ref<any[]>([])

const loadFullRegionTree = async () => {
  try {
    const res: any = await getFullRegionTree()
    fullRegionTree.value = Array.isArray(res) ? res : (res.data || [])
  } catch (e) {
    console.error('加载全公司区域树失败:', e)
  }
}

// regionName → '大区 / 小区' 路径映射。表格/卡片/详情用，避免每行单独 walk 整棵树
const regionPathMap = computed<Record<string, string>>(() => {
  const map: Record<string, string> = {}
  // fullRegionTree 是 [公司 → 大区 → 小区] 嵌套，跳过公司层
  for (const company of fullRegionTree.value) {
    if (!company) continue
    for (const big of (company.children || [])) {
      if (!big) continue
      map[big.name] = big.name
      for (const small of (big.children || [])) {
        map[small.name] = `${big.name} / ${small.name}`
      }
    }
  }
  return map
})

const viewMode = ref('list')
const currentPage = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)

const companies = ref<any[]>([])

function flattenTree(nodes: any[]): any[] {
  const result: any[] = []
  for (const node of nodes) {
    result.push(node)
    if (node.children?.length) {
      result.push(...flattenTree(node.children))
    }
  }
  return result
}

const loading = ref(false)

const fetchEvents = async () => {
  loading.value = true
  try {
    const { getAlgorithmEvents } = await import('@/api/algorithm-events')
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    if (searchForm.companyName) params.companyName = searchForm.companyName
    if (searchForm.regionName) params.regionName = searchForm.regionName
    if (searchForm.algorithmName) params.algorithmName = searchForm.algorithmName
    if (searchForm.eventType) params.eventType = searchForm.eventType
    if (searchForm.deviceId) params.deviceId = searchForm.deviceId
    if (searchForm.isCompliant) params.isCompliant = searchForm.isCompliant
    if (searchForm.processStatus) params.processStatus = searchForm.processStatus
    if (searchForm.startTime) params.startTime = new Date(searchForm.startTime).toISOString()
    if (searchForm.endTime) params.endTime = new Date(searchForm.endTime).toISOString()

    const res = await getAlgorithmEvents(params)
    const data = res.data || res
    tableData.value = (data.items || []).map((item: any) => ({
      id: item.id,
      companyName: item.company_name || item.companyName || '',
      regionName: item.region_name || item.regionName || '',
      deviceName: item.device_name || item.device?.name || item.deviceName || '',
      algorithmName: item.algorithm_name || item.algorithmName || '',
      eventTypeName: getEventTypeDisplayName(
        item.event_type_name || item.event_type?.name || item.eventTypeName || item.event_detail || ''
      ),
      eventDetail: item.event_detail || item.eventDetail || '',
      processStatus: item.process_status || item.processStatus || '未处置',
      reportTime: item.report_time || item.reportTime || item.created_at || '',
      isCompliant: item.is_compliant !== undefined ? (item.is_compliant ? '是' : '否') : (item.isCompliant || '否'),
      imageUrl: item.image_url || item.imageUrl || '',
      videoUrl: item.video_url || item.videoUrl || ''
    }))
    totalCount.value = data.total || 0
  } catch (e) {
    console.error('获取预警事件失败:', e)
  } finally {
    loading.value = false
  }
}

const loadTreeData = async () => {
  try {
    const res = await getDeviceGroupTree()
    const tree = res.data || res || []
    const flat = flattenTree(tree)
    companies.value = flat.filter((n: any) => n.isCompany)
  } catch (e) {
    console.error('获取设备组树失败:', e)
  }
}

const loadAlgorithms = async () => {
  try {
    const res = await getAlgorithms({ page_size: 100 })
    const data = res.data || res
    const items = data.items || data || []
    algorithmOptions.value = items
      .filter((a: any) => a.name === 'traffic')
      .map((a: any) => ({ label: a.description || a.name, value: a.name }))

    trafficAlgorithm.value = items.find((a: any) => a.name === 'traffic')
    if (trafficAlgorithm.value) {
      searchForm.algorithmName = trafficAlgorithm.value.name
      await loadEventTypes(trafficAlgorithm.value.id)
    }
  } catch (e) {
    console.error('加载算法列表失败:', e)
  }
}

const loadEventTypes = async (algorithmId: number) => {
  try {
    const res = await getEventTypes({ algorithm_id: algorithmId, page_size: 100 })
    const data = res.data || res
    const items = data.items || data || []
    eventTypeOptions.value = items.map((item: any) => ({
      label: item.description || getEventTypeDisplayName(item.name),
      value: item.name,
    }))
  } catch (e) {
    console.error('加载事件类型失败:', e)
  }
}

onMounted(() => {
  loadTreeData()
  loadFullRegionTree()  // 加载全公司区域树，让表格未选公司时也能显示路径
  loadAlgorithms().then(() => fetchEvents())
})

// 详情弹窗
const detailDialogVisible = ref(false)
const currentRecord = ref<EventItem | null>(null)

// 视频回放弹窗
const videoDialogVisible = ref(false)
const currentVideoUrl = ref('')
const videoError = ref(false)

const handleVideoError = () => {
  videoError.value = true
}

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

const pagedData = computed(() => tableData.value)

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
  fetchEvents()
}

const onCompanyChange = async () => {
  searchForm.regionId = null
  searchForm.regionName = ''
  searchForm.deviceId = null
  regionTree.value = []
  regionDevices.value = []
  if (!searchForm.companyName) return
  const company = companies.value.find((c: any) => c.name === searchForm.companyName)
  if (!company) return
  try {
    const res: any = await getRegionTree({ org_id: company.id })
    // 后端 /regions/tree 直接返回 roots 数组（已按 parent_id 构建好嵌套）
    const data = res.data || res
    regionTree.value = Array.isArray(data) ? data : (data.items || [])
  } catch (e) {
    console.error('获取区域树失败:', e)
  }
}

const loadDevicesByRegion = async (regionId: number | null) => {
  regionDevices.value = []
  if (!regionId) return
  try {
    const res: any = await getDevices({ region_id: regionId, page_size: 100 })
    const data = res.data || res
    regionDevices.value = (data.items || []).map((d: any) => ({ id: d.id, name: d.name }))
  } catch (e) {
    console.error('获取设备列表失败:', e)
  }
}

// cascader 选了具体 region 后，刷新设备下拉 + 同步 regionName（供后端 _resolve_region_ids）
watch(() => searchForm.regionId, (newId) => {
  searchForm.deviceId = null
  loadDevicesByRegion(newId)
  // walk regionTree 找 name
  let name = ''
  const walk = (nodes: any[]): boolean => {
    for (const n of nodes) {
      if (n.id === newId) { name = n.name; return true }
      if (n.children && walk(n.children)) return true
    }
    return false
  }
  walk(regionTree.value)
  searchForm.regionName = name
})

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    ;(searchForm as any)[key] = (typeof (searchForm as any)[key] === 'number') ? null : ''
  })
  regionTree.value = []
  regionDevices.value = []
  currentPage.value = 1
  if (trafficAlgorithm.value) {
    searchForm.algorithmName = trafficAlgorithm.value.name
  }
  fetchEvents()
  ElMessage.success('重置成功')
}

const handleExport = () => {
  exportDialogVisible.value = true
}

const confirmExport = () => {
  ElMessage.success(`导出成功，格式：${exportForm.format}${exportForm.includeImage ? '（带图片）' : ''}`)
  exportDialogVisible.value = false
}

const handleImageError = (e: Event) => {
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
  const placeholder = img.nextElementSibling as HTMLElement | null
  if (placeholder) placeholder.style.display = 'flex'
}

const handleDetail = (row: EventItem) => {
  currentRecord.value = row
  detailDialogVisible.value = true
}

const handleVideo = (row: EventItem) => {
  currentRecord.value = row
  currentVideoUrl.value = row.videoUrl || ''
  videoError.value = false
  videoDialogVisible.value = true
}

const handleVideoPlayback = () => {
  if (currentRecord.value) {
    currentVideoUrl.value = currentRecord.value.videoUrl || ''
    videoError.value = false
    videoDialogVisible.value = true
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
  min-width: 1200px;
  display: flex;
  flex-direction: column;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  flex-shrink: 0;
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
  flex-shrink: 0;
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

.content-wrapper {
  flex: 1;
  min-height: 0;
  overflow: auto;
}

.content-wrapper :deep(.el-table) {
  min-width: 1100px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
  flex-shrink: 0;
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

.card-image img,
.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  position: absolute;
  inset: 0;
  display: none;
  align-items: center;
  justify-content: center;
  background: rgba(0, 20, 40, 0.6);
  color: var(--text-secondary);
  font-size: 14px;
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
