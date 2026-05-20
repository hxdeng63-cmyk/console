<template>
  <div class="help-container">
    <el-card class="info-card">
      <div class="info-content">
        <div class="info-row">
          <span class="label">系统名称:</span>
          <span class="value">AI智能分析平台</span>
        </div>
        <div class="info-row">
          <span class="label">版本:</span>
          <span class="value">Copyright©2023 v2.0.2 aio</span>
        </div>
        <div class="info-row">
          <span class="label">公司:</span>
          <span class="value">联通数字科技有限公司</span>
        </div>
        <div class="info-row">
          <el-button type="primary" @click="downloadManual">用户手册</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'

const downloadManual = () => ElMessage.success('正在下载用户手册...')
</script>

<style scoped>
.help-container {
  padding: 24px;
  display: flex;
  justify-content: center;
}
.info-card {
  width: 100%;
  max-width: 500px;
  background: #1a1a2e;
  border: 1px solid #333;
}
.info-content {
  padding: 20px;
}
.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}
.label {
  color: #888;
  margin-right: 12px;
  font-size: 14px;
}
.value {
  color: rgba(180, 210, 235, 0.85);
  font-size: 14px;
}

.info-row .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.info-row .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}
</style>
