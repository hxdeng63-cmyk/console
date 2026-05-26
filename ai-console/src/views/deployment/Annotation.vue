<template>
  <div class="annotation-page">
    <!-- 顶部工具栏 -->
    <div class="top-toolbar">
      <div class="toolbar-left">
        <div class="selector-item">
          <span class="required-mark">*</span>
          <span class="selector-label">选择布控</span>
          <el-select v-model="selectedDeployment" placeholder="请选择布控" style="width: 180px" clearable>
            <el-option v-for="item in deployments" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </div>
        <div class="selector-item">
          <span class="required-mark">*</span>
          <span class="selector-label">选择设备</span>
          <el-select v-model="selectedDevice" placeholder="请在选择布控后选择设备" style="width: 260px" clearable>
            <el-option v-for="item in availableDevices" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </div>
        <el-button type="primary" class="query-btn" @click="handleQuery">
          <el-icon><Search /></el-icon>查询
        </el-button>
      </div>
      <div class="toolbar-right">
        <el-button class="action-btn" @click="handleCaptureFrame">
          <el-icon><Camera /></el-icon>抽帧
        </el-button>
        <el-button class="action-btn" @click="handleImportBg">
          <el-icon><Upload /></el-icon>导入
        </el-button>
        <el-button class="action-btn danger" @click="handleDelete">
          <el-icon><Delete /></el-icon>删除
        </el-button>
        <el-button class="action-btn" @click="handleUpdateBg">
          <el-icon><Refresh /></el-icon>更新底图
        </el-button>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="main-content">
      <!-- 左侧画布 -->
      <div class="canvas-area" ref="videoContainerRef">
        <VideoPlayer ref="videoPlayerRef" url="" protocol="hls" :enable-dual-protocol="false" />
        <canvas ref="annotationCanvasRef" class="annotation-canvas" @mousedown="startDraw" @mousemove="draw"
          @mouseup="endDraw" @mouseleave="endDraw"></canvas>
      </div>

      <!-- 右侧配置面板 -->
      <div class="config-panel">
        <!-- 选择标签 -->
        <div class="panel-section">
          <div class="section-header">
            <h4 class="section-title">选择标签</h4>
            <el-button link size="small" class="create-tag-btn" @click="openTagManage">创建标签</el-button>
          </div>
          <div class="tag-type-selector">
            <el-radio-group v-model="selectedTagType">
              <el-radio value="monitoring">监测区域</el-radio>
              <el-radio value="forbidden">非监测区</el-radio>
            </el-radio-group>
          </div>
        </div>

        <!-- 预置点信息 -->
        <div class="panel-section">
          <h4 class="section-title">预置点信息</h4>
          <el-form :model="presetForm" label-width="90px" size="small" class="compact-form">
            <el-form-item label="预置点名称：">
              <el-input v-model="presetForm.name" placeholder="请输入名称" />
            </el-form-item>
            <el-form-item label="预置点编号：">
              <el-select v-model="presetForm.code" placeholder="请选择" style="width: 100%">
                <el-option label="1" value="1" />
                <el-option label="2" value="2" />
                <el-option label="3" value="3" />
                <el-option label="4" value="4" />
              </el-select>
            </el-form-item>
            <el-form-item label="监控时间段：">
              <div class="time-range">
                <el-time-picker v-model="presetForm.timeRange.start" format="HH:mm:ss" value-format="HH:mm:ss"
                  placeholder="开始时间" style="width: 110px" />
                <span class="time-separator">-</span>
                <el-time-picker v-model="presetForm.timeRange.end" format="HH:mm:ss" value-format="HH:mm:ss"
                  placeholder="结束时间" style="width: 110px" />
                <el-button type="primary" size="small" link class="add-time-btn" @click="addTimeRange">
                  <el-icon>
                    <Plus />
                  </el-icon>
                </el-button>
              </div>
            </el-form-item>
          </el-form>
        </div>

        <!-- 自动获取预置点 -->
        <div class="panel-section">
          <h4 class="section-title">自动获取预置点</h4>
          <div class="preset-controls">
            <el-button type="primary" size="small" class="query-preset-btn" @click="handleGetPreset">查询</el-button>
            <div class="preset-inputs">
              <span class="preset-label">P:</span>
              <el-input-number v-model="presetForm.p" :min="0" :max="360" size="small" controls-position="right" />
              <span class="preset-label">T:</span>
              <el-input-number v-model="presetForm.t" :min="0" :max="90" size="small" controls-position="right" />
              <span class="preset-label">Z:</span>
              <el-input-number v-model="presetForm.z" :min="1" :max="20" size="small" controls-position="right" />
            </div>
          </div>
        </div>

        <!-- 标注列表 -->
        <div class="panel-section">
          <h4 class="section-title">标注列表</h4>
          <el-table :data="filteredAnnotations" border size="small" max-height="180" class="annotation-table">
            <el-table-column prop="type" label="标签" width="80" align="center">
              <template #default="{ row }">
                <el-tag :type="row.type === 'monitoring' ? 'success' : 'danger'" size="small">
                  {{ row.type === 'monitoring' ? '监测' : '非监测' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="时间" min-width="120" show-overflow-tooltip />
            <el-table-column label="编辑" width="70" align="center">
              <template #default="{ row }">
                <el-button link size="small" class="action-edit" @click="editAnnotation(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 保存按钮 -->
        <div class="save-section">
          <el-button type="primary" size="small" class="save-btn" @click="saveAnnotation">保存标注信息</el-button>
        </div>
      </div>
    </div>

    <!-- 标签管理弹窗 -->
    <el-dialog v-model="tagDialogVisible" title="标签管理" width="400px" class="tag-dialog">
      <el-form :model="tagForm" label-width="80px">
        <el-form-item label="标签名称" required>
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签类型" required>
          <el-input v-model="tagForm.typeValue" placeholder="请输入标签类型,只能输入数字" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="tagDialogVisible = false" class="cancel-btn">取消</el-button>
        <el-button type="primary" @click="handleAddTag" class="submit-btn">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { Camera, Upload, Delete, Refresh, Plus, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import { getDevices } from '@/api/devices'
import { getDeployments } from '@/api/deployments'
import { getAnnotations, createAnnotation } from '@/api/annotations'

interface Annotation {
  id: number
  deploymentId: number
  deviceId: number
  type: string
  polygon: number[][]
  createTime: string
}


const selectedDeployment = ref<number | null>(null)
const selectedDevice = ref<number | null>(null)
const selectedTagType = ref('monitoring')
const tagDialogVisible = ref(false)

const videoPlayerRef = ref<InstanceType<typeof VideoPlayer> | null>(null)
const videoContainerRef = ref<HTMLDivElement | null>(null)
const annotationCanvasRef = ref<HTMLCanvasElement | null>(null)

const isDrawing = ref(false)
const currentPolygon = ref<number[][]>([])

// 设备数据
const allDevices = ref<any[]>([])

// 布控数据
const deployments = ref<any[]>([])

// 标注数据
const annotations = ref<any[]>([])

// 标签数据（本地维护，后端无API）
const tags = ref<any[]>([
  { id: 1, name: '重点区域', type: 'number' },
  { id: 2, name: '禁行区域', type: 'number' },
  { id: 3, name: '施工区域', type: 'number' },
  { id: 4, name: '分流区域', type: 'number' }
])

// 获取设备列表
const fetchDevices = async () => {
  try {
    const res: any = await getDevices({ page: 1, page_size: 100 })
    allDevices.value = res.items || []
  } catch {
    ElMessage.error('获取设备列表失败')
  }
}

// 获取布控列表
const fetchDeployments = async () => {
  try {
    const res: any = await getDeployments({ page: 1, page_size: 100 })
    deployments.value = res.items || []
  } catch {
    ElMessage.error('获取布控列表失败')
  }
}

// 获取标注列表
const fetchAnnotations = async () => {
  try {
    const res: any = await getAnnotations({ page: 1, page_size: 100 })
    annotations.value = res.items || []
  } catch {
    ElMessage.error('获取标注列表失败')
  }
}

// 根据选择的布控过滤可用设备（后端暂无布控-设备关联，显示全部设备）
const availableDevices = computed(() => {
  if (!selectedDeployment.value) return []
  return allDevices.value
})

const tagForm = reactive({
  name: '',
  typeValue: ''
})

const presetForm = reactive({
  name: '',
  code: '',
  p: 0,
  t: 0,
  z: 1,
  timeRange: {
    start: '00:00:00',
    end: '23:59:59'
  }
})

const filteredAnnotations = computed(() => {
  return annotations.value.filter((a: any) => {
    const deploymentMatch = !selectedDeployment.value || a.deployment_id === selectedDeployment.value
    const deviceMatch = !selectedDevice.value || a.device_id === selectedDevice.value
    return deploymentMatch && deviceMatch
  })
})

const handleCaptureFrame = () => {
  ElMessage.success('抽帧成功')
}

const handleImportBg = () => {
  ElMessage.info('导入功能')
}

const handleQuery = () => {
  if (!selectedDeployment.value) {
    ElMessage.warning('请选择布控')
    return
  }
  ElMessage.success('查询成功')
}

const handleDelete = () => {
  ElMessage.info('删除功能')
}

const handleUpdateBg = () => {
  ElMessage.info('更新底图功能')
}

const startDraw = (e: MouseEvent) => {
  if (!annotationCanvasRef.value) return
  isDrawing.value = true
  const rect = annotationCanvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  currentPolygon.value = [[x, y]]
}

const draw = (e: MouseEvent) => {
  if (!isDrawing.value || !annotationCanvasRef.value) return
  const rect = annotationCanvasRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  currentPolygon.value.push([x, y])
  renderCanvas()
}

const endDraw = () => {
  isDrawing.value = false
}

const renderCanvas = () => {
  if (!annotationCanvasRef.value) return
  const canvas = annotationCanvasRef.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  ctx.clearRect(0, 0, canvas.width, canvas.height)

  if (currentPolygon.value.length > 1) {
    ctx.beginPath()
    ctx.moveTo(currentPolygon.value[0][0], currentPolygon.value[0][1])
    currentPolygon.value.forEach(point => {
      ctx.lineTo(point[0], point[1])
    })
    ctx.closePath()
    ctx.strokeStyle = '#00E5FF'
    ctx.lineWidth = 2
    ctx.stroke()
    ctx.fillStyle = 'rgba(0, 229, 255, 0.2)'
    ctx.fill()
  }
}

const clearCanvas = () => {
  currentPolygon.value = []
  if (annotationCanvasRef.value) {
    const ctx = annotationCanvasRef.value.getContext('2d')
    if (ctx) {
      ctx.clearRect(0, 0, annotationCanvasRef.value.width, annotationCanvasRef.value.height)
    }
  }
}

const saveAnnotation = async () => {
  if (currentPolygon.value.length < 3) {
    ElMessage.warning('请绘制至少3个点形成区域')
    return
  }
  if (!selectedDeployment.value || !selectedDevice.value) {
    ElMessage.warning('请选择布控任务和设备')
    return
  }
  try {
    await createAnnotation({
      deployment_id: selectedDeployment.value,
      device_id: selectedDevice.value,
      type: selectedTagType.value,
      polygon_json: [...currentPolygon.value],
      name: presetForm.name || null
    })
    clearCanvas()
    ElMessage.success('标注保存成功')
    fetchAnnotations()
  } catch (error: any) {
    ElMessage.error(error.message || '保存失败')
  }
}

const handleAddTag = () => {
  if (!tagForm.name) {
    ElMessage.warning('请输入标签名称')
    return
  }
  if (!tagForm.typeValue) {
    ElMessage.warning('请输入标签类型')
    return
  }
  tags.value.push({
    id: Date.now(),
    name: tagForm.name,
    type: tagForm.typeValue
  })
  tagForm.name = ''
  tagForm.typeValue = ''
  ElMessage.success('标签添加成功')
}

const handleGetPreset = () => {
  ElMessage.info('获取预置点')
}

const addTimeRange = () => {
  ElMessage.info('添加时间段')
}

const openTagManage = () => {
  tagDialogVisible.value = true
}

const editAnnotation = (_row: Annotation) => {
  ElMessage.info('编辑标注')
}

onMounted(() => {
  if (annotationCanvasRef.value && videoContainerRef.value) {
    annotationCanvasRef.value.width = videoContainerRef.value.clientWidth
    annotationCanvasRef.value.height = videoContainerRef.value.clientHeight
  }
  fetchDevices()
  fetchDeployments()
  fetchAnnotations()
})

watch([selectedDeployment, selectedDevice], () => {
  renderCanvas()
})
</script>

<style scoped>
.annotation-page {
  width: 100%;
  height: 100%;
  background: #020B1F;
  padding: 15px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 顶部工具栏 */
.top-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(145deg, rgba(0, 40, 70, 0.6) 0%, rgba(0, 20, 40, 0.8) 100%);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 8px;
  backdrop-filter: blur(16px) saturate(160%);
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.selector-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.selector-label {
  font-size: 13px;
  color: rgba(180, 210, 235, 0.9);
  white-space: nowrap;
}

.required-mark {
  color: #FF006E;
}

.query-btn {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

.query-btn:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.toolbar-right {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: rgba(0, 30, 60, 0.6);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.action-btn:hover {
  background: rgba(0, 229, 255, 0.2);
  border-color: #00E5FF;
}

.action-btn.danger {
  border-color: rgba(255, 77, 106, 0.4);
  color: #FF4D6D;
}

.action-btn.danger:hover {
  background: rgba(255, 0, 110, 0.2);
  border-color: #FF006E;
  color: #FF006E;
}

/* 主体区域 */
.main-content {
  display: flex;
  flex: 1;
  gap: 12px;
  min-height: 0;
}

/* 左侧画布 */
.canvas-area {
  position: relative;
  flex: 1;
  min-width: 0;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(0, 229, 255, 0.2);
}

.annotation-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: auto;
  cursor: crosshair;
}

/* 右侧配置面板 */
.config-panel {
  width: 340px;
  flex-shrink: 0;
  padding: 16px;
  overflow-y: auto;
  background: linear-gradient(145deg, rgba(0, 50, 80, 0.5) 0%, rgba(0, 25, 50, 0.75) 100%);
  border: 1px solid rgba(0, 229, 255, 0.18);
  border-radius: 8px;
  backdrop-filter: blur(18px) saturate(170%);
}

.panel-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(0, 229, 255, 0.9);
  margin: 0;
  padding-left: 8px;
  border-left: 3px solid #00E5FF;
}

.create-tag-btn {
  color: #00E5FF;
}

.tag-type-selector {
  margin-top: 8px;
}

.compact-form :deep(.el-form-item) {
  margin-bottom: 10px;
}

.compact-form :deep(.el-form-item__label) {
  color: rgba(180, 210, 235, 0.8);
  font-size: 12px;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 6px;
}

.time-separator {
  color: rgba(255, 255, 255, 0.5);
}

.add-time-btn {
  color: #00E5FF;
}

.preset-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.query-preset-btn {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

.query-preset-btn:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.preset-inputs {
  display: flex;
  align-items: center;
  gap: 6px;
}

.preset-label {
  font-size: 12px;
  color: rgba(180, 210, 235, 0.7);
}

.save-section {
  margin-top: 12px;
}

.save-btn {
  width: 100%;
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

.save-btn:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

/* 操作按钮 - 编辑（青色） */
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

/* 弹窗 */
.tag-dialog :deep(.el-dialog) {
  --el-dialog-bg-color: rgba(0, 20, 50, 0.95);
  border: 1px solid rgba(0, 229, 255, 0.3);
}

.tag-dialog :deep(.el-dialog__title) {
  color: rgba(180, 210, 235, 0.9);
}

.tag-dialog :deep(.el-form-item__label) {
  color: rgba(255, 255, 255, 0.8);
}

.tag-dialog :deep(.el-input__wrapper) {
  background: rgba(0, 30, 60, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.3);
  box-shadow: none;
}

.tag-dialog :deep(.el-input__inner) {
  color: rgba(180, 210, 235, 0.9);
}

.tag-dialog .cancel-btn {
  background: rgba(0, 30, 60, 0.6);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.tag-dialog .submit-btn {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

/* Element Plus 覆盖 */
:deep(.el-input__wrapper) {
  background: rgba(0, 30, 60, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.3);
  box-shadow: none;
}

:deep(.el-input__inner) {
  color: rgba(180, 210, 235, 0.9);
}

:deep(.el-select .el-input__wrapper) {
  background: rgba(0, 30, 60, 0.6);
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #00E5FF;
}

:deep(.el-radio__input.is-checked .el-radio__inner) {
  background: #00E5FF;
  border-color: #00E5FF;
}

:deep(.el-radio__label) {
  color: rgba(180, 210, 235, 0.8);
}

:deep(.el-table) {
  --el-table-bg-color: rgba(0, 20, 50, 0.4);
  --el-table-tr-bg-color: rgba(0, 30, 60, 0.4);
  --el-table-header-bg-color: rgba(0, 40, 80, 0.6);
  --el-table-row-hover-bg-color: rgba(0, 60, 100, 0.4);
  --el-table-border-color: rgba(0, 229, 255, 0.2);
  --el-table-text-color: rgba(180, 210, 235, 0.9);
  --el-table-header-text-color: rgba(180, 210, 235, 0.9);
}

.annotation-table :deep(.el-table__cell) {
  padding: 4px 0;
}
</style>