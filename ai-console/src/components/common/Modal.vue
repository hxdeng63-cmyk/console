<template>
  <el-dialog
    :model-value="visible"
    :title="title"
    width="600px"
    @close="$emit('close')"
    class="dark-modal"
    :close-on-click-modal="false"
  >
    <slot />
    <template #footer>
      <slot name="footer">
        <el-button @click="$emit('close')">取消</el-button>
        <el-button type="primary" @click="$emit('confirm')">确定</el-button>
      </slot>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  title: string
}>()

defineEmits<{
  close: []
  confirm: []
}>()
</script>

<style scoped>
.dark-modal :deep(.el-dialog) {
  background: #1a1a2e;
  border: 1px solid #2a2a4a;
}
.dark-modal :deep(.el-dialog__header) {
  border-bottom: 1px solid #2a2a4a;
}
.dark-modal :deep(.el-dialog__title) {
  color: #e0e0e0;
}
.dark-modal :deep(.el-dialog__body) {
  color: #c0c0c0;
}
.dark-modal :deep(.el-dialog__footer) {
  border-top: 1px solid #2a2a4a;
}
</style>
