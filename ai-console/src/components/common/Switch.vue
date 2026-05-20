<template>
  <el-switch
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    active-color="#00E5FF"
    inactive-color="#444"
  />
</template>

<script setup lang="ts">
defineProps<{
  modelValue: boolean
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>
