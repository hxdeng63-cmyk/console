<template>
  <div class="tree-node">
    <div
      class="node-row"
      :class="{
        'is-selected': isSelected,
        'is-file': isFile,
        'is-folder': !isFile,
      }"
      :style="{ paddingLeft: `${level * 16 + 8}px` }"
      @click="handleClick"
    >
      <span v-if="hasChildren" class="expand-icon" :class="{ expanded: isExpanded }" @click.stop="toggleExpand">
        <el-icon><ArrowRight /></el-icon>
      </span>
      <span v-else class="expand-spacer"></span>

      <el-icon class="node-icon" :class="iconClass">
        <component :is="nodeIcon" />
      </el-icon>

      <span class="node-name" :title="node.name">{{ node.isEventType ? getEventTypeDisplayName(node.name) : node.name }}</span>

      <span v-if="isFile" class="file-type-tag" :class="fileTypeClass">
        {{ detectedFileType }}
      </span>
    </div>

    <div v-if="hasChildren && isExpanded" class="node-children">
      <FileAnalysisTreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :level="level + 1"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  OfficeBuilding,
  MapLocation,
  Calendar,
  Folder,
  VideoCamera,
  Picture,
  ArrowRight
} from '@element-plus/icons-vue'
import { detectFileType } from '@/utils/fileType.ts'
import { getEventTypeDisplayName } from '@/utils/eventType'

interface FileNode {
  id: number | string
  name: string
  isCompany?: boolean
  isRegion?: boolean
  isEventType?: boolean
  isFolder?: boolean
  isFile?: boolean
  fileType?: '视频' | '图片'
  eventType?: string
  previewUrl?: string
  filePath?: string
  children?: FileNode[]
}

interface Props {
  node: FileNode
  level?: number
  selectedId?: number | string | null
}

const props = withDefaults(defineProps<Props>(), {
  level: 0,
  selectedId: null,
})

const emit = defineEmits<{
  (e: 'select', node: FileNode): void
}>()

const isExpanded = ref(true)

const isFile = computed(() => Boolean(props.node.isFile))
const hasChildren = computed(() => Boolean(props.node.children && props.node.children.length > 0))
const isSelected = computed(() => props.selectedId !== null && props.selectedId === props.node.id)

const detectedFileType = computed(() => {
  return detectFileType(props.node.name || '', props.node.fileType || '图片')
})

const nodeIcon = computed(() => {
  if (props.node.isCompany) return OfficeBuilding
  if (props.node.isRegion) return MapLocation
  if (props.node.isEventType) return Calendar
  if (props.node.isFolder) return Folder
  if (detectedFileType.value === '视频') return VideoCamera
  return Picture
})

const iconClass = computed(() => {
  if (props.node.isCompany) return 'company-icon'
  if (props.node.isRegion) return 'region-icon'
  if (props.node.isEventType) return 'event-icon'
  if (props.node.isFolder) return 'folder-icon'
  if (detectedFileType.value === '视频') return 'video-icon'
  return 'image-icon'
})

const fileTypeClass = computed(() => {
  return detectedFileType.value === '视频' ? 'video-tag' : 'image-tag'
})

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const handleClick = () => {
  if (isFile.value) {
    emit('select', props.node)
  } else if (hasChildren.value) {
    toggleExpand()
  }
}
</script>

<style scoped>
.tree-node {
  font-size: 13px;
  user-select: none;
}

.node-row {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding-right: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.node-row:hover {
  background: rgba(0, 229, 255, 0.08);
}

.node-row.is-selected {
  background: rgba(0, 229, 255, 0.18);
  box-shadow: inset 2px 0 0 #00E5FF;
}

.node-row.is-file {
  cursor: pointer;
}

.node-row.is-folder {
  cursor: pointer;
}

.expand-icon,
.expand-spacer {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: rgba(0, 229, 255, 0.6);
}

.expand-icon {
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.node-icon {
  flex-shrink: 0;
  font-size: 15px;
}

.company-icon {
  color: #00E5FF;
}

.region-icon {
  color: #00FF88;
}

.event-icon {
  color: #F59E0B;
}

.folder-icon {
  color: #60A5FA;
}

.video-icon {
  color: #FFAA00;
}

.image-icon {
  color: #A855F7;
}

.node-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(220, 240, 255, 0.95);
}

.file-type-tag {
  flex-shrink: 0;
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 3px;
  border: 1px solid;
}

.video-tag {
  color: #FFAA00;
  border-color: rgba(255, 170, 0, 0.4);
  background: rgba(255, 170, 0, 0.1);
}

.image-tag {
  color: #A855F7;
  border-color: rgba(168, 85, 247, 0.4);
  background: rgba(168, 85, 247, 0.1);
}

.node-children {
  margin-top: 2px;
}
</style>
