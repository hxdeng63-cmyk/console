<template>
  <div class="device-tree">
    <div class="tree-header">
      <el-input
        v-model="localSearchQuery"
        placeholder="Search devices..."
        clearable
        @input="handleSearch"
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <div class="tree-actions">
        <el-button text @click="expandAll" title="Expand All">
          <el-icon><Expand /></el-icon>
        </el-button>
        <el-button text @click="collapseAll" title="Collapse All">
          <el-icon><Fold /></el-icon>
        </el-button>
      </div>
    </div>

    <div class="tree-content">
      <template v-if="filteredData.length > 0">
        <TreeNode
          v-for="node in filteredData"
          :key="node.id"
          :node="node"
          :expanded-keys="expandedKeys"
          :selected-keys="selectedKeys"
          :checked-keys="checkedKeys"
          :mode="mode"
          :level="0"
          @node-click="handleNodeClick"
          @node-check="handleNodeCheck"
          @toggle-expand="toggleExpand"
        />
      </template>
      <el-empty v-else description="No devices found" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Search, Expand, Fold } from '@element-plus/icons-vue'
import { useDeviceTree, type DeviceNode } from './useDeviceTree'
import TreeNode from './TreeNode.vue'

interface Props {
  data: DeviceNode[]
  mode?: 'radio' | 'checkbox'
  sessionStorageKey?: string
  defaultCheckedKeys?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'radio',
  sessionStorageKey: 'device-tree-state',
  defaultCheckedKeys: () => [],
})

const emit = defineEmits<{
  (e: 'node-click', node: DeviceNode): void
  (e: 'node-check', node: DeviceNode, checked: boolean): void
}>()

const localSearchQuery = ref('')
let debounceTimer: ReturnType<typeof setTimeout> | null = null

const {
  expandedKeys,
  selectedKeys,
  checkedKeys,
  filteredData,
  toggleExpand,
  expandAll,
  collapseAll,
  handleNodeClick: onNodeClick,
  search,
} = useDeviceTree({
  data: props.data,
  mode: props.mode,
  sessionStorageKey: props.sessionStorageKey,
  defaultCheckedKeys: props.defaultCheckedKeys,
})

function handleSearch(value: string) {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }
  debounceTimer = setTimeout(() => {
    search(value)
  }, 300)
}

function handleNodeClick(node: DeviceNode) {
  emit('node-click', node)
  onNodeClick(node)
}

function handleNodeCheck(node: DeviceNode, checked: boolean) {
  // 收集级联节点：当前节点 + 所有子孙节点
  const nodesToUpdate: DeviceNode[] = [node]

  function collectChildren(n: DeviceNode) {
    if (n.children?.length) {
      for (const child of n.children) {
        nodesToUpdate.push(child)
        collectChildren(child)
      }
    }
  }
  collectChildren(node)

  // 批量更新 checkedKeys，只触发一次响应式变更
  const nextChecked = new Set(checkedKeys.value)
  for (const n of nodesToUpdate) {
    if (checked) {
      nextChecked.add(n.id)
    } else {
      nextChecked.delete(n.id)
    }
  }
  checkedKeys.value = nextChecked

  // 逐个 emit 到父组件
  for (const n of nodesToUpdate) {
    emit('node-check', n, checked)
  }
}

watch(
  () => props.data,
  () => {
    localSearchQuery.value = ''
  }
)
</script>

<style scoped>
.device-tree {
  --primary-color: #00E5FF;
  --tech-accent: #00d4ff;
  --online-color: #00FF88;
  --offline-color: #8c8c8c;

  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-card);
  border-radius: 4px;
}

.tree-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  border-bottom: 1px solid rgba(24, 144, 255, 0.2);
}

.search-input {
  flex: 1;
}

.search-input :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(24, 144, 255, 0.3);
  box-shadow: none;
}

.search-input :deep(.el-input__inner) {
  color: rgba(180, 210, 235, 0.85);
}

.search-input :deep(.el-input__inner)::placeholder {
  color: rgba(232, 244, 255, 0.5);
}

.tree-actions {
  display: flex;
  gap: 4px;
}

.tree-actions .el-button {
  color: var(--tech-accent);
}

.tree-actions .el-button:hover {
  color: var(--primary-color);
}

.tree-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.tree-content :deep(.el-empty__description) {
  color: rgba(232, 244, 255, 0.6);
}
</style>
