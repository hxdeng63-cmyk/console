<template>
  <div class="tree-node" :style="{ paddingLeft: `${level * 12}px` }">
    <div
      class="node-content"
      :class="{
        selected: selectedKeys.has(node.id),
        checked: checkedKeys.has(node.id),
      }"
      @click="handleClick"
    >
      <span
        v-if="node.children?.length"
        class="expand-icon"
        :class="{ expanded: expandedKeys.has(node.id) }"
        @click.stop="handleToggle"
      >
        <el-icon><ArrowRight /></el-icon>
      </span>
      <span v-else class="expand-placeholder"></span>

      <span v-if="mode === 'radio'" class="radio-select">
        <el-radio
          :model-value="selectedKeys.has(node.id)"
          @click.stop
          @change="handleRadioChange"
        >&nbsp;</el-radio>
      </span>
      <span v-else-if="mode === 'checkbox'" class="checkbox-select">
        <el-checkbox
          v-model="isChecked"
          @click.stop
        >&nbsp;</el-checkbox>
      </span>

      <span class="status-dot" :class="{ online: node.online, offline: !node.online }"></span>

      <span class="node-icon">
        <el-icon v-if="node.type === 'org'"><OfficeBuilding /></el-icon>
        <el-icon v-else-if="node.type === 'road'"><Guide /></el-icon>
        <el-icon v-else><Monitor /></el-icon>
      </span>

      <span class="node-name">{{ node.name }}</span>
    </div>

    <div v-if="expandedKeys.has(node.id) && node.children?.length" class="node-children">
      <TreeNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :expanded-keys="expandedKeys"
        :selected-keys="selectedKeys"
        :checked-keys="checkedKeys"
        :mode="mode"
        :level="level + 1"
        @node-click="$emit('node-click', $event)"
        @node-check="(...args) => $emit('node-check', ...args)"
        @toggle-expand="$emit('toggle-expand', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowRight, OfficeBuilding, Guide, Monitor } from '@element-plus/icons-vue'
import type { DeviceNode } from './useDeviceTree'

interface Props {
  node: DeviceNode
  expandedKeys: Set<string>
  selectedKeys: Set<string>
  checkedKeys: Set<string>
  mode: 'radio' | 'checkbox'
  level: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'node-click', node: DeviceNode): void
  (e: 'node-check', node: DeviceNode, checked: boolean): void
  (e: 'toggle-expand', key: string): void
}>()

function handleClick() {
  emit('node-click', props.node)
}

function handleToggle() {
  emit('toggle-expand', props.node.id)
}

function handleRadioChange() {
  emit('node-click', props.node)
}

const isChecked = computed({
  get: () => props.checkedKeys.has(props.node.id),
  set: (val: boolean) => {
    emit('node-check', props.node, val)
  },
})
</script>

<style scoped>
.tree-node {
  user-select: none;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.node-content:hover {
  background: rgba(24, 144, 255, 0.1);
}

.node-content.selected {
  background: rgba(24, 144, 255, 0.2);
}

.node-content.checked {
  background: rgba(24, 144, 255, 0.15);
}

.expand-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  color: #00d4ff;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(90deg);
}

.expand-placeholder {
  width: 16px;
}

.radio-select,
.checkbox-select {
  display: flex;
  align-items: center;
}

.radio-select :deep(.el-radio__label) {
  display: none;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-dot.online {
  background: #00FF88;
  box-shadow: 0 0 6px #00FF88;
}

.status-dot.offline {
  background: #8c8c8c;
}

.node-icon {
  display: flex;
  align-items: center;
  color: #00d4ff;
}

.node-name {
  color: rgba(180, 210, 235, 0.85);
  font-size: 13px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-children {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
