<template>
  <div class="tree-container">
    <div class="tree-toolbar">
      <el-button type="primary" size="small" @click="$emit('refresh')">
        刷新
      </el-button>
      <el-button type="primary" size="small" @click="$emit('add')">
        + 添加根节点
      </el-button>
    </div>
    <el-tree
      :data="data"
      :props="{ children: 'children', label: 'label' }"
      node-key="id"
      default-expand-all
      class="org-tree"
    >
      <template #default="{ node, data }">
        <span class="tree-node">
          <span class="node-label">{{ node.label }}</span>
          <span class="node-actions">
            <el-button link class="edit-btn" size="small" @click.stop="$emit('edit', data)">编辑</el-button>
            <el-button link class="delete-btn" size="small" @click.stop="$emit('delete', data)">删除</el-button>
            <el-button link class="add-btn" size="small" @click.stop="$emit('addChild', data)">+添加子节点</el-button>
          </span>
        </span>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  data: any[]
}>()

defineEmits<{
  refresh: []
  add: []
  edit: [data: any]
  delete: [data: any]
  addChild: [data: any]
}>()
</script>

<style scoped>
.tree-container {
  padding: 16px;
}
.tree-toolbar {
  margin-bottom: 16px;
  display: flex;
  gap: 8px;
}
.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 8px;
}
.node-label {
  flex: 1;
}
.node-actions {
  display: flex;
  gap: 8px;
}
.org-tree {
  background: transparent;
}
.edit-btn {
  color: #4a9eff;
}
.edit-btn:hover {
  color: #6bb3ff;
}
.delete-btn {
  color: #ff6b8a;
}
.delete-btn:hover {
  color: #ff8fa3;
}
.add-btn {
  color: #4a9eff;
}
.add-btn:hover {
  color: #6bb3ff;
}
</style>
