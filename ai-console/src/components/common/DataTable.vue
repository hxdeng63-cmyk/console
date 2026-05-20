<template>
  <div class="data-table">
    <el-table
      :data="data"
      :columns="columns"
      v-loading="loading"
      stripe
      border
      style="width: 100%"
    >
      <el-table-column
        v-for="col in columns"
        :key="col.prop"
        :prop="col.prop"
        :label="col.label"
        :width="col.width"
        :formatter="col.formatter"
      >
        <template v-if="col.slot" #default="scope">
          <slot :name="col.prop" :row="scope.row" />
        </template>
      </el-table-column>
    </el-table>
    <slot name="pagination" />
  </div>
</template>

<script setup lang="ts">
interface Column {
  prop: string
  label: string
  width?: string | number
  formatter?: (row: any, column: any, cellValue: any) => string
  slot?: boolean
}

defineProps<{
  columns: Column[]
  data: any[]
  loading?: boolean
}>()
</script>

<style scoped>
.data-table {
  width: 100%;
}
</style>
