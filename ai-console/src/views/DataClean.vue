<template>
  <div class="data-clean">
    <!-- 配置区 -->
    <el-card class="config-card">
      <el-form :model="form" label-width="120px">
        <!-- 提示信息 -->
        <el-alert type="info" :closable="false" class="info-alert">
          <template #title>
            <ul class="info-list">
              <li>定时清理任务将在每天凌晨进行，执行时扫描全表数据，分批执行</li>
              <li>历史保留时长：即数据截止时间，清理时将删除此时间之前的数据</li>
              <li>未勾选的类型数据将永久保存，不会被清理</li>
            </ul>
          </template>
        </el-alert>

        <!-- 执行策略 + 执行时间 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="执行策略">
              <el-radio-group v-model="form.strategy">
                <el-radio value="immediate">立即执行</el-radio>
                <el-radio value="scheduled">定时执行</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="执行时间" v-if="form.strategy === 'scheduled'">
              <el-time-picker
                v-model="form.executeTime"
                format="HH:mm"
                value-format="HH:mm"
                placeholder="选择时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 预警事件 + 视频文件独立行 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="预警事件保留">
              <el-checkbox v-model="form.alertEnabled" />
              <el-input-number
                v-model="form.alertDays"
                :min="1"
                :max="365"
                :disabled="!form.alertEnabled"
                controls-position="right"
                style="width: 120px; margin-left: 8px"
              />
              <span class="unit">天</span>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="视频文件保留">
              <el-checkbox v-model="form.videoEnabled" />
              <el-input-number
                v-model="form.videoDays"
                :min="1"
                :max="365"
                :disabled="!form.videoEnabled"
                controls-position="right"
                style="width: 120px; margin-left: 8px"
              />
              <span class="unit">天</span>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 按钮 -->
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">提交执行</el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 清理记录列表 -->
    <el-card class="table-card">
      <template #header>
        <span>清理记录</span>
      </template>
      <el-table :data="pagedData" stripe border>
        <el-table-column prop="type" label="类型" width="150" />
        <el-table-column prop="cutoffTime" label="数据保存截止时间" width="200" />
        <el-table-column prop="status" label="状态" width="150">
          <template #default="{ row }">
            <el-tag :type="row.status === '成功' ? 'success' : row.status === '执行中' ? 'warning' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :status="row.status === '成功' ? 'success' : undefined"
            />
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="cleanRecords.length"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getCleanRecords } from '@/api/cleanRecords'

interface CleanRecord {
  type: string
  cutoffTime: string
  status: string
  progress: number
}

const form = ref({
  strategy: 'scheduled',
  executeTime: '02:00',
  alertEnabled: true,
  alertDays: 90,
  videoEnabled: true,
  videoDays: 60,
})

const cleanRecords = ref<CleanRecord[]>([])
const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return cleanRecords.value.slice(start, start + pageSize.value)
})

const fetchCleanRecords = async () => {
  try {
    const res: any = await getCleanRecords({ page: 1, page_size: 100 })
    const items = res.items || []
    cleanRecords.value = items.map((item: any) => ({
      type: item.type || item.recordType || item.record_type || '-',
      cutoffTime: item.cutoffTime || item.cutoff_time || item.createdAt || item.created_at || '-',
      status: item.status || (item.progress === 100 ? '成功' : item.progress > 0 ? '执行中' : '待执行'),
      progress: Number(item.progress ?? item.progressPercent ?? item.progress_percent ?? 0)
    }))
  } catch (error) {
    console.error('Failed to load clean records:', error)
    cleanRecords.value = []
  }
}

onMounted(() => {
  fetchCleanRecords()
})

const handleSubmit = () => {
  console.log('submit', form.value)
}

const handleCancel = () => {
  form.value = {
    strategy: 'scheduled',
    executeTime: '02:00',
    alertEnabled: true,
    alertDays: 90,
    videoEnabled: true,
    videoDays: 60,
  }
}
</script>

<style scoped>
.data-clean {
  padding: 20px;
}

.config-card {
  margin-bottom: 20px;
}

.info-alert {
  margin-bottom: 20px;
  background: rgba(24, 144, 255, 0.1);
  border: 1px solid rgba(24, 144, 255, 0.3);
}

:deep(.el-alert__title) {
  font-size: 13px;
  line-height: 1.8;
}

.info-list {
  margin: 0;
  padding-left: 20px;
  color: var(--text-secondary);
}

.info-list li {
  line-height: 1.8;
}

.unit {
  margin-left: 8px;
  color: var(--text-secondary);
}

.table-card {
  margin-bottom: 20px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
