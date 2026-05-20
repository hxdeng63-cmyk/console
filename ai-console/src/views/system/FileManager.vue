<template>
  <div class="file-manager">
    <!-- 搜索栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchForm.companyName" placeholder="公司名称" style="width: 160px" clearable />
        <el-input v-model="searchForm.regionName" placeholder="区域" style="width: 140px" clearable />
        <el-select v-model="searchForm.fileType" placeholder="文件类型" style="width: 120px" clearable>
          <el-option label="视频" value="视频" />
          <el-option label="图片" value="图片" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>搜索
        </el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="expandAll">
          <el-icon><ArrowDown /></el-icon>展开全部
        </el-button>
        <el-button type="primary" @click="collapseAll">
          <el-icon><ArrowUp /></el-icon>折叠全部
        </el-button>
      </div>
    </div>

    <!-- 树形表格 -->
    <el-table
      ref="tableRef"
      :data="filteredTreeData"
      row-key="id"
      border
      stripe
      :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      :default-expand-all="true"
      v-loading="loading"
    >
      <!-- 层级列：公司 / 区域 / 文件 -->
      <el-table-column label="文件层级" min-width="280">
        <template #default="{ row }">
          <div class="tree-node-content">
            <el-icon v-if="row.isCompany" :size="16" class="node-icon company-icon"><OfficeBuilding /></el-icon>
            <el-icon v-else-if="row.isRegion" :size="16" class="node-icon region-icon"><MapLocation /></el-icon>
            <el-icon v-else-if="row.fileType === '视频'" :size="16" class="node-icon video-icon"><VideoCamera /></el-icon>
            <el-icon v-else :size="16" class="node-icon image-icon"><Picture /></el-icon>
            <span class="node-name" :class="{ 'company-name': row.isCompany, 'region-name': row.isRegion }">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>

      <!-- 在线预览列 -->
      <el-table-column label="在线预览" width="180" align="center">
        <template #default="{ row }">
          <template v-if="row.isFile">
            <div v-if="row.fileType === '图片'" class="preview-wrapper" @click="openImagePreview(row)">
              <img :src="row.previewUrl" class="preview-thumb" />
              <div class="preview-overlay">
                <el-icon :size="20"><ZoomIn /></el-icon>
              </div>
            </div>
            <div v-else class="preview-wrapper video" @click="openVideoPreview(row)">
              <img :src="row.previewUrl" class="preview-thumb" />
              <div class="preview-overlay">
                <el-icon :size="24"><VideoPlay /></el-icon>
              </div>
            </div>
          </template>
          <span v-else class="node-placeholder">—</span>
        </template>
      </el-table-column>

      <!-- 文件路径列 -->
      <el-table-column label="文件路径" min-width="280">
        <template #default="{ row }">
          <span v-if="row.isFile" class="file-path">{{ row.filePath }}</span>
          <span v-else class="node-placeholder">—</span>
        </template>
      </el-table-column>

      <!-- 操作列 -->
      <el-table-column label="操作" width="160" fixed="right" align="center">
        <template #default="{ row }">
          <template v-if="row.isFile">
            <el-button class="action-edit" size="small" @click="handleExport(row)">导出</el-button>
            <el-button class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
          <span v-else class="node-placeholder">—</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- 图片预览 -->
    <el-image-viewer
      v-if="imagePreviewVisible"
      :url-list="[currentPreviewUrl]"
      @close="imagePreviewVisible = false"
    />

    <!-- 视频预览弹窗 -->
    <el-dialog
      v-model="videoDialogVisible"
      title="视频预览"
      width="700px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div class="video-player-wrapper">
        <video
          :src="currentVideoUrl"
          controls
          class="video-player"
          preload="metadata"
        />
      </div>
      <template #footer>
        <el-button @click="videoDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search, ArrowDown, ArrowUp,
  OfficeBuilding, MapLocation, VideoCamera, Picture,
  ZoomIn, VideoPlay
} from '@element-plus/icons-vue'

interface FileNode {
  id: number
  name: string
  isCompany?: boolean
  isRegion?: boolean
  isFile?: boolean
  fileType?: '视频' | '图片'
  previewUrl?: string
  filePath?: string
  children?: FileNode[]
}

// 静态树形数据
const rawTreeData: FileNode[] = [
  {
    id: 1,
    name: '青海海东分公司',
    isCompany: true,
    children: [
      {
        id: 11,
        name: '城东区',
        isRegion: true,
        children: [
          {
            id: 111,
            name: '事故录像_20240518.mp4',
            isFile: true,
            fileType: '视频',
            previewUrl: 'https://picsum.photos/seed/video111/320/180',
            filePath: '/video/hd/事故录像_20240518.mp4'
          },
          {
            id: 112,
            name: '拥堵录像_20240519.mp4',
            isFile: true,
            fileType: '视频',
            previewUrl: 'https://picsum.photos/seed/video112/320/180',
            filePath: '/video/hd/拥堵录像_20240519.mp4'
          },
          {
            id: 113,
            name: '抓拍_001.jpg',
            isFile: true,
            fileType: '图片',
            previewUrl: 'https://picsum.photos/seed/img113/320/180',
            filePath: '/img/hd/抓拍_001.jpg'
          }
        ]
      },
      {
        id: 12,
        name: '平安区',
        isRegion: true,
        children: [
          {
            id: 121,
            name: '逆行检测_001.mp4',
            isFile: true,
            fileType: '视频',
            previewUrl: 'https://picsum.photos/seed/video121/320/180',
            filePath: '/video/hd/逆行检测_001.mp4'
          },
          {
            id: 122,
            name: '违停抓拍_003.jpg',
            isFile: true,
            fileType: '图片',
            previewUrl: 'https://picsum.photos/seed/img122/320/180',
            filePath: '/img/hd/违停抓拍_003.jpg'
          }
        ]
      },
      {
        id: 13,
        name: '乐都区',
        isRegion: true,
        children: [
          {
            id: 131,
            name: '行人闯入_002.mp4',
            isFile: true,
            fileType: '视频',
            previewUrl: 'https://picsum.photos/seed/video131/320/180',
            filePath: '/video/hd/行人闯入_002.mp4'
          }
        ]
      }
    ]
  },
  {
    id: 2,
    name: '青海西宁分公司',
    isCompany: true,
    children: [
      {
        id: 21,
        name: '城西区',
        isRegion: true,
        children: [
          {
            id: 211,
            name: '烟雾检测_001.mp4',
            isFile: true,
            fileType: '视频',
            previewUrl: 'https://picsum.photos/seed/video211/320/180',
            filePath: '/video/xn/烟雾检测_001.mp4'
          },
          {
            id: 212,
            name: '异常停车_005.jpg',
            isFile: true,
            fileType: '图片',
            previewUrl: 'https://picsum.photos/seed/img212/320/180',
            filePath: '/img/xn/异常停车_005.jpg'
          }
        ]
      },
      {
        id: 22,
        name: '城中区',
        isRegion: true,
        children: [
          {
            id: 221,
            name: '上行车流量_001.mp4',
            isFile: true,
            fileType: '视频',
            previewUrl: 'https://picsum.photos/seed/video221/320/180',
            filePath: '/video/xn/上行车流量_001.mp4'
          },
          {
            id: 222,
            name: '作业人员_002.jpg',
            isFile: true,
            fileType: '图片',
            previewUrl: 'https://picsum.photos/seed/img222/320/180',
            filePath: '/img/xn/作业人员_002.jpg'
          },
          {
            id: 223,
            name: '交通阻塞_003.mp4',
            isFile: true,
            fileType: '视频',
            previewUrl: 'https://picsum.photos/seed/video223/320/180',
            filePath: '/video/xn/交通阻塞_003.mp4'
          }
        ]
      }
    ]
  }
]

const treeData = ref<FileNode[]>([])
const loading = ref(false)
const tableRef = ref()

onMounted(async () => {
  loading.value = true
  await new Promise(r => setTimeout(r, 200))
  treeData.value = JSON.parse(JSON.stringify(rawTreeData))
  loading.value = false
})

// 搜索
const searchForm = ref({
  companyName: '',
  regionName: '',
  fileType: ''
})

const handleSearch = () => {
  // el-table 树形不支持内置过滤，通过重新赋值触发
  const filtered = filterTree(rawTreeData, searchForm.value)
  treeData.value = JSON.parse(JSON.stringify(filtered))
}

// 树形过滤
function filterTree(nodes: FileNode[], criteria: { companyName: string; regionName: string; fileType: string }): FileNode[] {
  const result: FileNode[] = []
  for (const node of nodes) {
    if (node.isCompany && criteria.companyName && !node.name.includes(criteria.companyName)) {
      // 公司名不匹配，跳过整个公司
      continue
    }
    const cloned = { ...node, children: node.children ? [...node.children] : undefined }
    if (cloned.children) {
      cloned.children = filterTree(cloned.children, criteria)
    }
    // 区域过滤
    if (node.isRegion && criteria.regionName && !node.name.includes(criteria.regionName)) {
      // 如果区域不匹配但有子文件匹配公司/类型，保留
      if (!cloned.children || cloned.children.length === 0) continue
    }
    // 文件类型过滤
    if (node.isFile && criteria.fileType && node.fileType !== criteria.fileType) {
      continue
    }
    result.push(cloned)
  }
  return result
}

const filteredTreeData = computed(() => treeData.value)

// 展开/折叠
const expandAll = () => {
  tableRef.value?.toggleRowExpansion?.(treeData.value, true)
  // 递归展开所有节点
  const expand = (nodes: FileNode[]) => {
    nodes.forEach(node => {
      tableRef.value?.toggleRowExpansion?.(node, true)
      if (node.children) expand(node.children)
    })
  }
  expand(treeData.value)
}

const collapseAll = () => {
  const collapse = (nodes: FileNode[]) => {
    nodes.forEach(node => {
      tableRef.value?.toggleRowExpansion?.(node, false)
      if (node.children) collapse(node.children)
    })
  }
  collapse(treeData.value)
}

// 预览
const imagePreviewVisible = ref(false)
const currentPreviewUrl = ref('')

const openImagePreview = (row: FileNode) => {
  currentPreviewUrl.value = row.previewUrl || ''
  imagePreviewVisible.value = true
}

const videoDialogVisible = ref(false)
const currentVideoUrl = ref('')

const openVideoPreview = (row: FileNode) => {
  currentVideoUrl.value = row.previewUrl || ''
  videoDialogVisible.value = true
}

// 操作
const handleExport = (row: FileNode) => {
  ElMessage.success(`开始导出文件：${row.name}`)
}

const handleDelete = (row: FileNode) => {
  ElMessageBox.confirm(`确定删除文件 "${row.name}" 吗？`, '提示', { type: 'warning' })
    .then(() => {
      deleteNode(treeData.value, row.id)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}

function deleteNode(nodes: FileNode[], targetId: number): boolean {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].id === targetId) {
      nodes.splice(i, 1)
      return true
    }
    if (nodes[i].children) {
      if (deleteNode(nodes[i].children!, targetId)) {
        // 如果区域下没有文件了，移除区域
        if (nodes[i].isRegion && nodes[i].children!.length === 0) {
          nodes.splice(i, 1)
        }
        return true
      }
    }
  }
  return false
}
</script>

<style scoped>
.file-manager {
  padding: 20px;
}

/* 工具栏 */
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
  gap: 10px;
  align-items: center;
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

.action-area {
  display: flex;
  gap: 10px;
}

.action-area .el-button {
  background: rgba(0, 229, 255, 0.1);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.action-area .el-button:hover {
  background: rgba(0, 229, 255, 0.2);
  border-color: #00E5FF;
}

/* 树节点 */
.tree-node-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-icon {
  flex-shrink: 0;
}

.company-icon {
  color: #00E5FF;
}

.region-icon {
  color: #00FF88;
}

.video-icon {
  color: #FFAA00;
}

.image-icon {
  color: #A855F7;
}

.node-name {
  font-size: 14px;
  color: var(--text-primary);
}

.company-name {
  font-weight: 700;
  font-size: 15px;
}

.region-name {
  font-weight: 600;
  color: var(--text-secondary);
}

.node-placeholder {
  color: var(--text-secondary);
  opacity: 0.4;
}

.file-path {
  font-size: 13px;
  color: var(--text-secondary);
  font-family: monospace;
}

/* 预览 */
.preview-wrapper {
  position: relative;
  width: 120px;
  height: 68px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  margin: 0 auto;
}

.preview-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.preview-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  opacity: 0;
  transition: opacity 0.2s;
  color: #fff;
}

.preview-wrapper:hover .preview-overlay {
  opacity: 1;
}

.preview-wrapper.video .preview-overlay {
  opacity: 1;
  background: rgba(0, 0, 0, 0.2);
}

/* 视频播放器 */
.video-player-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-player {
  width: 100%;
  max-height: 400px;
}

/* 操作按钮 */
.action-edit {
  background: rgba(0, 229, 255, 0.15) !important;
  border: 1px solid rgba(0, 229, 255, 0.4) !important;
  color: #00E5FF !important;
  border-radius: 4px;
  padding: 6px 14px !important;
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
  padding: 6px 14px !important;
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