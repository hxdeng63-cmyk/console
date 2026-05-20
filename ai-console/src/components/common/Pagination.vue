<template>
  <div class="pagination-wrapper">
    <span class="total-text">共 {{ total }} 条</span>
    <el-select
      :model-value="pageSize"
      @update:model-value="$emit('update:pageSize', $event)"
      class="page-size-select"
      size="small"
    >
      <el-option :value="10" label="10条/页" />
      <el-option :value="20" label="20条/页" />
      <el-option :value="50" label="50条/页" />
    </el-select>
    <el-pagination
      :current-page="page"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      @update:current-page="$emit('update:page', $event)"
    />
    <el-input
      :model-value="page"
      @update:model-value="$emit('update:page', $event)"
      class="page-jump-input"
      size="small"
      placeholder="页码"
      type="number"
      :min="1"
      :max="Math.ceil(total / pageSize)"
      @keyup.enter="$emit('update:page', parseInt(($event.target as HTMLInputElement).value))"
    />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  total: number
  page: number
  pageSize: number
}>()

defineEmits<{
  'update:page': [page: number]
  'update:pageSize': [pageSize: number]
}>()
</script>

<style scoped>
.pagination-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-end;
  padding: 12px 0;
}
.total-text {
  color: #8AAFC8;
  font-size: 13px;
}
.page-size-select {
  width: 100px;
}
.page-jump-input {
  width: 80px;
}
</style>
