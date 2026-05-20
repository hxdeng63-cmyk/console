<template>
  <div class="annotation-page">
    <ThreeColumnLayout>
      <!-- Left Column: Selectors -->
      <template #left>
        <div class="left-panel">
          <div class="panel-section">
            <h4 class="section-title">
              <span class="required-mark">*</span>选择布控
            </h4>
            <el-select v-model="selectedDeployment" placeholder="请选择布控" style="width: 100%" clearable>
              <el-option
                v-for="item in deployments"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </div>

          <div class="panel-section">
            <h4 class="section-title">
              <span class="required-mark">*</span>选择设备
            </h4>
            <el-select v-model="selectedDevice" placeholder="请在选择布控后选择设备" style="width: 100%" clearable>
              <el-option
                v-for="item in devices"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </div>

          <div class="panel-section">
            <div class="button-row">
              <el-button type="primary" size="small" @click="handleQuery" class="query-btn">查询</el-button>
            </div>
          </div>

          <div class="panel-section">
            <h4 class="section-title">操作</h4>
            <div class="button-group-vertical">
              <el-button type="primary" size="small" @click="handleCaptureFrame" class="action-btn">
                <el-icon><Camera /></el-icon>抽帧
              </el-button>
              <el-button type="primary" size="small" @click="handleImportBg" class="action-btn">
                <el-icon><Upload /></el-icon>导入
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete" class="action-btn">
                <el-icon><Delete /></el-icon>删除
              </el-button>
              <el-button type="primary" size="small" @click="handleUpdateBg" class="action-btn">
                <el-icon><Refresh /></el-icon>更新底图
              </el-button>
            </div>
          </div>
        </div>
      </template>

      <!-- Middle Column: Video + Canvas -->
      <template #middle>
        <div class="video-container" ref="videoContainerRef">
          <VideoPlayer
            ref="videoPlayerRef"
            url=""
            protocol="hls"
            :enable-dual-protocol="false"
          />
          <canvas
            ref="annotationCanvasRef"
            class="annotation-canvas"
            @mousedown="startDraw"
            @mousemove="draw"
            @mouseup="endDraw"
            @mouseleave="endDraw"
          ></canvas>
        </div>
      </template>

      <!-- Right Column: Config Panel -->
      <template #right>
        <div class="right-panel">
          <el-tabs v-model="activeTab" class="config-tabs">
            <!-- Tab1: 选择标签 -->
            <el-tab-pane label="选择标签" name="tags">
              <div class="tab-content">
                <div class="tag-section">
                  <div class="section-header">
                    <h4 class="section-title">选择标签</h4>
                    <el-button link size="small" style="color: #00E5FF; background: rgba(0, 229, 255, 0.15); border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" @click="openTagManage" class="create-tag-btn">创建标签</el-button>
                  </div>
                  <div class="tag-options">
                    <el-radio-group v-model="selectedTagType" size="small">
                      <el-radio-button value="monitoring">监测区域</el-radio-button>
                      <el-radio-button value="forbidden">非监测区域</el-radio-button>
                    </el-radio-group>
                  </div>
                </div>

                <div class="preset-section">
                  <h4 class="section-title">预置点信息</h4>
                  <el-form :model="presetForm" label-width="80px" size="small">
                    <el-form-item label="名称">
                      <el-input v-model="presetForm.name" placeholder="请输入名称" />
                    </el-form-item>
                    <el-form-item label="编号">
                      <el-select v-model="presetForm.code" placeholder="请选择" style="width: 100%">
                        <el-option label="1" value="1" />
                        <el-option label="2" value="2" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="监控时间">
                      <div class="time-range">
                        <el-time-picker
                          v-model="presetForm.timeRange.start"
                          format="HH:mm:ss"
                          value-format="HH:mm:ss"
                          placeholder="开始时间"
                          style="width: 100px"
                        />
                        <span class="time-separator">-</span>
                        <el-time-picker
                          v-model="presetForm.timeRange.end"
                          format="HH:mm:ss"
                          value-format="HH:mm:ss"
                          placeholder="结束时间"
                          style="width: 100px"
                        />
                        <el-button type="primary" size="small" link @click="addTimeRange" class="add-time-btn">
                          <el-icon><Plus /></el-icon>
                        </el-button>
                      </div>
                    </el-form-item>
                  </el-form>
                </div>

                <div class="auto-preset-section">
                  <h4 class="section-title">自动获取预置点</h4>
                  <div class="preset-controls">
                    <el-button type="primary" size="small" @click="handleGetPreset" class="query-preset-btn">查询</el-button>
                    <div class="preset-inputs">
                      <el-input-number v-model="presetForm.p" :min="0" :max="360" size="small" controls-position="right" />
                      <el-input-number v-model="presetForm.t" :min="0" :max="90" size="small" controls-position="right" />
                      <el-input-number v-model="presetForm.z" :min="1" :max="20" size="small" controls-position="right" />
                    </div>
                  </div>
                </div>

                <div class="annotation-list-section">
                  <h4 class="section-title">标注列表</h4>
                  <el-table :data="filteredAnnotations" border size="small" max-height="200">
                    <el-table-column prop="type" label="标签" width="80">
                      <template #default="{ row }">
                        <el-tag :type="row.type === 'monitoring' ? 'success' : 'danger'" size="small">
                          {{ row.type === 'monitoring' ? '监测' : '非监测' }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="createTime" label="时间" />
                    <el-table-column label="编辑" width="80">
                      <template #default="{ row }">
                        <el-button link size="small" style="color: #00E5FF; background: rgba(0, 229, 255, 0.15); border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" @click="editAnnotation(row)">编辑</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>

                <div class="save-section">
                  <el-button type="primary" size="small" @click="saveAnnotation" class="save-btn">保存标注信息</el-button>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </template>
    </ThreeColumnLayout>

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
import { Camera, Upload, Delete, Refresh, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ThreeColumnLayout from '@/components/layout/ThreeColumnLayout.vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import { annotations, presets, tags } from '@/mock/deployment/annotation'
import { deployments } from '@/mock/deployment/data'

interface Annotation {
  id: number
  deploymentId: number
  deviceId: string
  type: string
  polygon: number[][]
  createTime: string
}

interface Preset {
  id: number
  deviceId: string
  name: string
  p: number
  t: number
  z: number
  timeRange: { start: string; end: string }
}

interface Tag {
  id: number
  name: string
  type: string
}

const selectedDeployment = ref<number | null>(null)
const selectedDevice = ref<string | null>(null)
const activeTab = ref('tags')
const selectedTagType = ref('monitoring')
const tagDialogVisible = ref(false)

const videoPlayerRef = ref<InstanceType<typeof VideoPlayer> | null>(null)
const videoContainerRef = ref<HTMLDivElement | null>(null)
const annotationCanvasRef = ref<HTMLCanvasElement | null>(null)

const isDrawing = ref(false)
const currentPolygon = ref<number[][]>([])

// Mock devices - in real app would come from API
const devices = ref([
  { id: 'dev-1', name: '摄像头-01' },
  { id: 'dev-2', name: '摄像头-02' },
  { id: 'dev-3', name: '摄像头-03' },
  { id: 'dev-4', name: '摄像头-04' }
])

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
  return annotations.filter(a => {
    const deploymentMatch = !selectedDeployment.value || a.deploymentId === selectedDeployment.value
    const deviceMatch = !selectedDevice.value || a.deviceId === selectedDevice.value
    return deploymentMatch && deviceMatch
  })
})

const filteredPresets = computed(() => {
  return presets.filter(p => !selectedDevice.value || p.deviceId === selectedDevice.value)
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

const handleReset = () => {
  selectedDeployment.value = null
  selectedDevice.value = null
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

  // Draw current polygon
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

const saveAnnotation = () => {
  if (currentPolygon.value.length < 3) {
    ElMessage.warning('请绘制至少3个点形成区域')
    return
  }
  if (!selectedDeployment.value || !selectedDevice.value) {
    ElMessage.warning('请选择布控任务和设备')
    return
  }
  annotations.push({
    id: Date.now(),
    deploymentId: selectedDeployment.value,
    deviceId: selectedDevice.value,
    type: selectedTagType.value,
    polygon: [...currentPolygon.value],
    createTime: new Date().toLocaleString()
  })
  clearCanvas()
  ElMessage.success('标注保存成功')
}

const deleteAnnotation = (row: Annotation) => {
  const idx = annotations.findIndex(a => a.id === row.id)
  if (idx !== -1) annotations.splice(idx, 1)
  ElMessage.success('删除成功')
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
  tags.push({
    id: Date.now(),
    name: tagForm.name,
    type: tagForm.typeValue
  })
  tagForm.name = ''
  tagForm.typeValue = ''
  ElMessage.success('标签添加成功')
}

const deleteTag = (row: Tag) => {
  const idx = tags.findIndex(t => t.id === row.id)
  if (idx !== -1) tags.splice(idx, 1)
  ElMessage.success('删除成功')
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

const editAnnotation = (row: Annotation) => {
  ElMessage.info('编辑标注')
}

const handleSavePreset = () => {
  if (!selectedDevice.value) {
    ElMessage.warning('请先选择设备')
    return
  }
  presets.push({
    id: Date.now(),
    deviceId: selectedDevice.value,
    name: `预置点${presets.length + 1}`,
    p: presetForm.p,
    t: presetForm.t,
    z: presetForm.z,
    timeRange: { ...presetForm.timeRange }
  })
  ElMessage.success('预置点保存成功')
}

const deletePreset = (row: Preset) => {
  const idx = presets.findIndex(p => p.id === row.id)
  if (idx !== -1) presets.splice(idx, 1)
  ElMessage.success('删除成功')
}

onMounted(() => {
  if (annotationCanvasRef.value && videoContainerRef.value) {
    annotationCanvasRef.value.width = videoContainerRef.value.clientWidth
    annotationCanvasRef.value.height = videoContainerRef.value.clientHeight
  }
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
}

.left-panel {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}

.panel-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(0, 229, 255, 0.9);
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #00E5FF;
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.button-group-vertical {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.button-row {
  display: flex;
  gap: 8px;
}

.required-mark {
  color: #FF006E;
  margin-right: 4px;
}

.query-btn {
  flex: 1;
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

.reset-btn {
  flex: 1;
  background: rgba(0, 30, 60, 0.6);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.tag-section,
.preset-section,
.auto-preset-section,
.annotation-list-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-header .section-title {
  margin-bottom: 0;
}

.create-tag-btn {
  color: #00E5FF;
}

.tag-options {
  margin-top: 12px;
}

.time-range {
  display: flex;
  align-items: center;
  gap: 8px;
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
  gap: 12px;
  margin-top: 12px;
}

.query-preset-btn {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

.preset-inputs {
  display: flex;
  gap: 8px;
}

.save-section {
  margin-top: 20px;
}

.save-section .save-btn {
  width: 100%;
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

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

.action-btn {
  width: 100%;
  background: rgba(0, 30, 60, 0.6);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.action-btn:hover {
  background: rgba(0, 229, 255, 0.2);
  border-color: #00E5FF;
}

.video-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #000;
  border-radius: 4px;
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

.right-panel {
  height: 100%;
  padding: 16px;
  overflow-y: auto;
}

.config-tabs {
  height: 100%;
}

.config-tabs :deep(.el-tabs__header) {
  margin-bottom: 0;
}

.config-tabs :deep(.el-tabs__nav-wrap::after) {
  background: rgba(0, 229, 255, 0.2);
}

.config-tabs :deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.6);
}

.config-tabs :deep(.el-tabs__item.is-active) {
  color: #00E5FF;
}

.config-tabs :deep(.el-tabs__active-bar) {
  background: #00E5FF;
}

.config-tabs :deep(.el-tabs__content) {
  height: calc(100% - 40px);
  overflow-y: auto;
}

.tab-content {
  padding: 12px 0;
}

.type-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.toggle-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.canvas-controls {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.clear-btn {
  background: rgba(0, 30, 60, 0.6);
  border-color: rgba(255, 77, 106, 0.5);
  color: #FF006E;
}

.clear-btn:hover {
  background: rgba(255, 77, 106, 0.2);
  border-color: #FF006E;
}

.save-btn {
  background: rgba(0, 229, 255, 0.2);
  border-color: #00E5FF;
  color: #00E5FF;
}

.save-btn:hover {
  background: rgba(0, 229, 255, 0.3);
}

.annotation-list,
.tag-list,
.preset-list {
  margin-top: 16px;
}

.list-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(0, 229, 255, 0.9);
  margin-bottom: 8px;
}

.tag-form,
.preset-form {
  padding: 12px;
  background: rgba(0, 30, 60, 0.3);
  border-radius: 4px;
  border: 1px solid rgba(0, 229, 255, 0.1);
}

.add-tag-btn,
.get-preset-btn {
  background: rgba(0, 229, 255, 0.2);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.add-tag-btn:hover,
.get-preset-btn:hover {
  background: rgba(0, 229, 255, 0.3);
}

.save-preset-btn {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}

.save-preset-btn:hover {
  background: #00b8d4;
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

:deep(.el-radio-button__inner) {
  background: rgba(0, 30, 60, 0.6);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #000;
}
</style>
