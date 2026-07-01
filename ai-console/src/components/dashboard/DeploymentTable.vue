<template>
  <div v-loading="loading" class="panel-section deployment-section">
    <div class="section-header">
      <span class="header-bar"></span>
      <span class="section-title">布控信息</span>
      <span class="header-line"></span>
    </div>
    <el-table :data="data" size="small" class="deployment-table" border>
      <el-table-column prop="name" label="布控方案名称" min-width="130" show-overflow-tooltip />
      <el-table-column prop="algorithm" label="算法名称" width="95" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="70" align="center">
        <template #default="{ row }">
          <span class="status-tag" :class="row.statusClass">{{ row.status }}</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
interface DeploymentRow {
  name: string
  algorithm: string
  status: string
  statusClass: string
}

defineProps<{
  data: DeploymentRow[]
  loading?: boolean
}>()
</script>

<style scoped>
.deployment-table {
  background: transparent;
}
.deployment-table :deep(.el-table__header th) {
  background: rgba(0, 229, 255, 0.1);
  color: rgba(180, 210, 235, 0.85);
  font-size: 11px;
  border-color: rgba(0, 229, 255, 0.15);
}
.deployment-table :deep(.el-table__body td) {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  font-size: 11px;
  border-color: rgba(0, 229, 255, 0.1);
}
.deployment-table :deep(.el-table__row:hover td) {
  background: rgba(0, 229, 255, 0.06);
}
.status-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
}
.status-tag.online {
  background: rgba(82, 196, 26, 0.2);
  color: #00FF88;
}
.status-tag.offline {
  background: rgba(120, 130, 150, 0.2);
  color: rgba(180, 210, 235, 0.7);
}
.status-tag.warning {
  background: rgba(255, 0, 110, 0.2);
  color: #FF006E;
}
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.header-bar {
  width: 3px;
  height: 14px;
  background: #00E5FF;
}
.section-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
}
.header-line {
  flex: 1;
  height: 1px;
  background: repeating-linear-gradient(
    90deg,
    rgba(0, 229, 255, 0.3),
    rgba(0, 229, 255, 0.3) 4px,
    transparent 4px,
    transparent 8px
  );
}
.panel-section {
  background: rgba(0, 20, 50, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  padding: 12px;
  flex-shrink: 0;
}
</style>