<template>
  <div class="file-analysis-page">
    <ThreeColumnLayout left-width="300px" right-width="320px">
      <!-- 左侧：文件树 -->
      <template #left>
        <div class="side-panel tree-panel">
          <div class="panel-header">
            <span class="header-bar"></span>
            <span class="panel-title">文件层级</span>
          </div>

          <div class="stats-row">
            <div class="stat-card">
              <span class="stat-value">{{ stats.total }}</span>
              <span class="stat-label">文件总数</span>
            </div>
            <div class="stat-card video-card">
              <span class="stat-value">{{ stats.video }}</span>
              <span class="stat-label">视频</span>
            </div>
            <div class="stat-card image-card">
              <span class="stat-value">{{ stats.image }}</span>
              <span class="stat-label">图片</span>
            </div>
          </div>

          <div class="filter-row">
            <el-select
              v-model="selectedEventType"
              placeholder="全部事件类型"
              size="small"
              clearable
              class="event-type-filter"
            >
              <el-option
                v-for="et in eventTypes"
                :key="et.id"
                :label="et.description || getEventTypeDisplayName(et.name)"
                :value="et.name"
              />
            </el-select>
          </div>

          <div class="search-box">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索文件 / 公司 / 区域 / 事件"
              size="small"
              clearable
              class="tree-search"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <div class="tree-content">
            <div v-if="loading" class="tree-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
            <div v-else-if="filteredTree.length === 0" class="tree-empty">
              暂无文件数据
            </div>
            <FileAnalysisTreeNode
              v-else
              v-for="node in filteredTree"
              :key="node.id"
              :node="node"
              :selected-id="selectedFile?.id"
              @select="handleSelect"
            />
          </div>
        </div>
      </template>

      <!-- 中间：预览区 -->
      <template #middle>
        <div class="preview-panel">
          <div v-if="!selectedFile" class="preview-placeholder">
            <div class="placeholder-icon"></div>
            <span>请选择文件进行预览</span>
          </div>

          <div v-else class="crt-screen">
            <div class="crt-corners">
              <div class="crt-corner top-left"></div>
              <div class="crt-corner top-right"></div>
              <div class="crt-corner bottom-left"></div>
              <div class="crt-corner bottom-right"></div>
            </div>
            <div class="crt-scanlines"></div>

            <img
              v-if="selectedFileType === '图片'"
              :src="selectedFile.previewUrl"
              :alt="selectedFile.name"
              class="preview-media preview-image"
              @click="openImagePreview"
              @error="handlePreviewError"
            />

            <video
              v-else-if="selectedFileType === '视频'"
              :src="selectedFile.previewUrl"
              controls
              class="preview-media preview-video"
              preload="metadata"
            />

            <div v-else class="preview-unsupported">
              不支持的文件类型
            </div>
          </div>
        </div>
      </template>

      <!-- 右侧：详情 -->
      <template #right>
        <div class="side-panel detail-panel">
          <div class="panel-header">
            <span class="header-bar"></span>
            <span class="panel-title">文件详情</span>
          </div>

          <div v-if="!selectedFile" class="detail-content">
            <div class="detail-placeholder">请选择文件查看详情</div>
          </div>

          <div v-else class="detail-content">
            <div class="detail-card">
              <div class="detail-item">
                <span class="detail-label">文件名称</span>
                <span class="detail-value file-name">{{ selectedFile.name }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">事件类型</span>
                <span class="detail-value">{{ selectedFile.eventType ? getEventTypeDisplayName(selectedFile.eventType) : '-' }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">文件类型</span>
                <span class="detail-value">
                  <span class="type-badge" :class="selectedFileType === '视频' ? 'video-badge' : 'image-badge'">
                    {{ selectedFileType }}
                  </span>
                </span>
              </div>

              <div class="detail-item detail-path">
                <span class="detail-label">文件路径</span>
                <span class="detail-value path-value">{{ selectedFile.filePath || '-' }}</span>
              </div>
            </div>

            <div class="detail-actions">
              <el-button class="action-export" @click="handleExport">
                <el-icon><Download /></el-icon>
                导出
              </el-button>
              <el-button class="action-delete" @click="handleDelete">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </div>
      </template>
    </ThreeColumnLayout>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="imagePreviewVisible"
      :url-list="[selectedFile?.previewUrl || '']"
      @close="imagePreviewVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  Search,
  Loading,
  Download,
  Delete
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import ThreeColumnLayout from '@/components/layout/ThreeColumnLayout.vue'
import { getFileTree, downloadFile, deleteFile } from '@/api/files.js'
import { getEventTypes } from '@/api/event-types.js'
import { detectFileType } from '@/utils/fileType.ts'
import { getEventTypeDisplayName } from '@/utils/eventType'
import FileAnalysisTreeNode from './FileAnalysisTreeNode.vue'

interface EventType {
  id: number | string
  name: string
  description?: string
}

interface FileNode {
  id: number | string
  name: string
  isCompany?: boolean
  isRegion?: boolean
  isEventType?: boolean
  isFile?: boolean
  fileType?: '视频' | '图片'
  eventType?: string
  previewUrl?: string
  filePath?: string
  children?: FileNode[]
}

const loading = ref(false)
const treeData = ref<FileNode[]>([])
const searchKeyword = ref('')
const selectedFile = ref<FileNode | null>(null)
const imagePreviewVisible = ref(false)
const eventTypes = ref<EventType[]>([])
const selectedEventType = ref<string>('')

const selectedFileType = computed(() => {
  if (!selectedFile.value) return ''
  return detectFileType(selectedFile.value.name || '', selectedFile.value.fileType || '图片')
})

const fetchTree = async () => {
  loading.value = true
  try {
    const data = await getFileTree()
    treeData.value = data || []
  } catch (error) {
    ElMessage.error('加载文件树失败')
    treeData.value = []
  } finally {
    loading.value = false
  }
}

const fetchEventTypes = async () => {
  try {
    const data = await getEventTypes({ page_size: 100 })
    const items = data?.items || data || []
    eventTypes.value = Array.isArray(items) ? items : []
  } catch (error) {
    eventTypes.value = []
  }
}

onMounted(() => {
  fetchTree()
  fetchEventTypes()
})

function nodeMatches(node: FileNode, lowerKeyword: string): boolean {
  const nameMatch = node.name?.toLowerCase().includes(lowerKeyword)
  const eventMatch = node.eventType?.toLowerCase().includes(lowerKeyword)
  return Boolean(nameMatch || eventMatch)
}

function filterByEventType(nodes: FileNode[], eventTypeName: string): FileNode[] {
  if (!eventTypeName) return nodes

  return nodes.reduce<FileNode[]>((result, node) => {
    if (node.isEventType) {
      if (node.name === eventTypeName || node.eventType === eventTypeName) {
        result.push({
          ...node,
          children: node.children ? [...node.children] : undefined,
        })
      }
      return result
    }

    if (!node.children) return result

    const filteredChildren = filterByEventType(node.children, eventTypeName)
    if (filteredChildren.length > 0) {
      result.push({ ...node, children: filteredChildren })
    }
    return result
  }, [])
}

function filterTree(nodes: FileNode[], keyword: string): FileNode[] {
  const trimmedKeyword = keyword.trim()
  if (!trimmedKeyword) return nodes

  const lowerKeyword = trimmedKeyword.toLowerCase()

  return nodes.reduce<FileNode[]>((result, node) => {
    const filteredChildren = node.children
      ? filterTree(node.children, keyword)
      : undefined
    const hasMatchingChild = filteredChildren && filteredChildren.length > 0

    if (nodeMatches(node, lowerKeyword) || hasMatchingChild) {
      result.push({ ...node, children: filteredChildren })
    }
    return result
  }, [])
}

const treeFilteredByEvent = computed(() => {
  return filterByEventType(treeData.value, selectedEventType.value)
})

const filteredTree = computed(() => {
  return filterTree(treeFilteredByEvent.value, searchKeyword.value)
})

const stats = computed(() => {
  const counts = { total: 0, video: 0, image: 0 }
  function walk(nodes: FileNode[]) {
    for (const node of nodes) {
      if (node.isFile) {
        counts.total++
        const type = detectFileType(node.name || '', node.fileType || '图片')
        if (type === '视频') counts.video++
        else if (type === '图片') counts.image++
      } else if (node.children) {
        walk(node.children)
      }
    }
  }
  walk(filteredTree.value)
  return counts
})

const handleSelect = (node: FileNode) => {
  if (!node.isFile) return
  selectedFile.value = node
}

const openImagePreview = () => {
  imagePreviewVisible.value = true
}

const handleExport = async () => {
  if (!selectedFile.value) return
  try {
    await downloadFile(Number(selectedFile.value.id), selectedFile.value.name)
    ElMessage.success('导出已开始')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const handleDelete = () => {
  if (!selectedFile.value) return
  const file = selectedFile.value
  ElMessageBox.confirm(`确定删除文件 "${file.name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteFile(Number(file.id))
        ElMessage.success('删除成功')
        selectedFile.value = null
        await fetchTree()
      } catch (error) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

const handlePreviewError = () => {
  ElMessage.error('预览图加载失败')
}
</script>

<style scoped>
.file-analysis-page {
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.side-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  gap: 12px;
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.header-bar {
  width: 3px;
  height: 14px;
  background: #00E5FF;
  border-radius: 2px;
}

.panel-title {
  font-family: 'Orbitron', 'Rajdhani', sans-serif;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  color: rgba(180, 210, 235, 0.9);
}

.stats-row {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.stat-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 4px;
  background: rgba(0, 20, 50, 0.5);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 6px;
}

.stat-value {
  font-family: 'Orbitron', 'Rajdhani', sans-serif;
  font-size: 16px;
  font-weight: 700;
  color: #00E5FF;
  line-height: 1;
}

.video-card .stat-value {
  color: #FFAA00;
}

.image-card .stat-value {
  color: #A855F7;
}

.stat-label {
  font-size: 10px;
  color: rgba(180, 210, 235, 0.6);
}

.filter-row {
  flex-shrink: 0;
}

.event-type-filter {
  width: 100%;
}

.event-type-filter :deep(.el-input__wrapper) {
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.3);
  box-shadow: none;
  border-radius: 6px;
}

.event-type-filter :deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.85);
}

.event-type-filter :deep(.el-select-dropdown) {
  background: rgba(0, 15, 40, 0.95);
  border: 1px solid rgba(0, 229, 255, 0.25);
}

.search-box {
  flex-shrink: 0;
}

.tree-search :deep(.el-input__wrapper) {
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.3);
  box-shadow: none;
  border-radius: 6px;
}

.tree-search :deep(.el-input__inner) {
  color: rgba(255, 255, 255, 0.85);
}

.tree-search :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.tree-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.tree-loading,
.tree-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 120px;
  color: rgba(0, 229, 255, 0.5);
  font-size: 13px;
}

.detail-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.detail-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(0, 229, 255, 0.5);
  font-size: 13px;
}

.preview-panel {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.preview-placeholder {
  width: 100%;
  max-width: 720px;
  aspect-ratio: 16 / 9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background:
    radial-gradient(ellipse at center, rgba(0, 229, 255, 0.05) 0%, transparent 70%),
    rgba(0, 10, 25, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 12px;
  color: rgba(0, 229, 255, 0.6);
  font-family: 'Orbitron', 'Rajdhani', sans-serif;
  font-size: 14px;
  letter-spacing: 2px;
}

.placeholder-icon {
  width: 60px;
  height: 60px;
  border: 2px solid rgba(0, 229, 255, 0.3);
  border-radius: 50%;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.2), inset 0 0 20px rgba(0, 229, 255, 0.1);
  animation: glow-pulse 2s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% {
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.3), inset 0 0 15px rgba(0, 229, 255, 0.1);
    transform: scale(1);
  }
  50% {
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.5), inset 0 0 25px rgba(0, 229, 255, 0.2);
    transform: scale(1.05);
  }
}

/* CRT 监控屏幕效果 */
.crt-screen {
  position: relative;
  width: 100%;
  max-width: 900px;
  aspect-ratio: 16 / 9;
  background: #000;
  border: 1px solid rgba(0, 229, 255, 0.25);
  border-radius: 12px;
  overflow: hidden;
  box-shadow:
    0 0 40px rgba(0, 229, 255, 0.1),
    inset 0 0 80px rgba(0, 0, 0, 0.6);
}

.crt-corners {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 3;
}

.crt-corner {
  position: absolute;
  width: 24px;
  height: 24px;
  border-color: #00E5FF;
  border-style: solid;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.5);
}

.crt-corner.top-left {
  top: 12px;
  left: 12px;
  border-width: 3px 0 0 3px;
}

.crt-corner.top-right {
  top: 12px;
  right: 12px;
  border-width: 3px 3px 0 0;
}

.crt-corner.bottom-left {
  bottom: 12px;
  left: 12px;
  border-width: 0 0 3px 3px;
}

.crt-corner.bottom-right {
  bottom: 12px;
  right: 12px;
  border-width: 0 3px 3px 0;
}

.crt-scanlines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 2;
  background: repeating-linear-gradient(
    0deg,
    rgba(0, 0, 0, 0.15),
    rgba(0, 0, 0, 0.15) 1px,
    transparent 1px,
    transparent 3px
  );
  opacity: 0.35;
}

.preview-media {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

.preview-image {
  cursor: zoom-in;
}

.preview-unsupported {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 229, 255, 0.5);
  font-size: 14px;
}

/* 详情面板 */
.detail-card {
  background: rgba(0, 20, 50, 0.4);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 8px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-size: 11px;
  color: rgba(180, 210, 235, 0.6);
  font-family: 'Orbitron', 'Rajdhani', sans-serif;
  letter-spacing: 1px;
}

.detail-value {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  word-break: break-all;
}

.file-name {
  font-weight: 600;
  color: #00E5FF;
}

.path-value {
  font-family: monospace;
  font-size: 11px;
  color: rgba(180, 210, 235, 0.75);
  line-height: 1.5;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  width: fit-content;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 3px;
  border: 1px solid;
}

.video-badge {
  color: #FFAA00;
  border-color: rgba(255, 170, 0, 0.4);
  background: rgba(255, 170, 0, 0.1);
}

.image-badge {
  color: #A855F7;
  border-color: rgba(168, 85, 247, 0.4);
  background: rgba(168, 85, 247, 0.1);
}

.detail-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}

.action-export {
  flex: 1;
  background: rgba(0, 229, 255, 0.12) !important;
  border: 1px solid rgba(0, 229, 255, 0.35) !important;
  color: #00E5FF !important;
}

.action-export:hover {
  background: rgba(0, 229, 255, 0.22) !important;
  border-color: #00E5FF !important;
}

.action-delete {
  flex: 1;
  background: rgba(255, 0, 110, 0.12) !important;
  border: 1px solid rgba(255, 0, 110, 0.35) !important;
  color: #FF006E !important;
}

.action-delete:hover {
  background: rgba(255, 0, 110, 0.22) !important;
  border-color: #FF006E !important;
}

.tree-content::-webkit-scrollbar,
.detail-content::-webkit-scrollbar {
  width: 4px;
}

.tree-content::-webkit-scrollbar-thumb,
.detail-content::-webkit-scrollbar-thumb {
  background: rgba(0, 229, 255, 0.3);
  border-radius: 2px;
}
</style>
