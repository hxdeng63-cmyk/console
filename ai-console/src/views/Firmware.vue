<template>
  <div class="firmware-center">
    <!-- 版本信息卡片 -->
    <div class="version-cards">
      <div class="version-card current">
        <div class="card-label">当前版本</div>
        <div class="card-version">{{ currentVersion.version }}</div>
        <div class="card-date">{{ currentVersion.date }} 发布</div>
      </div>
      <div class="version-arrow">
        <el-icon :size="28"><Right /></el-icon>
      </div>
      <div class="version-card latest">
        <div class="card-label">最新版本</div>
        <div class="card-version">{{ latestVersion.version }}</div>
        <div class="card-date">{{ latestVersion.date }} 发布</div>
      </div>
      <div class="version-arrow">
        <el-icon :size="28"><Right /></el-icon>
      </div>
      <div class="version-card status" :class="{ outdated: hasUpdate }">
        <div class="card-label">更新状态</div>
        <div class="card-version">{{ hasUpdate ? '有更新' : '已最新' }}</div>
        <div class="card-date">{{ hasUpdate ? `${updateCount}个版本待更新` : '当前已是最新版本' }}</div>
      </div>
    </div>

    <!-- 更新操作区 -->
    <div class="update-action">
      <el-button
        type="primary"
        size="large"
        :disabled="!hasUpdate || loading"
        :loading="loading"
        @click="openUpdateDialog"
      >
        <el-icon><Download /></el-icon>
        {{ hasUpdate ? '立即更新' : '已是最新版本' }}
      </el-button>
    </div>

    <!-- 更新日志 -->
    <div class="changelog-section">
      <div class="section-title">更新日志</div>
      <el-timeline>
        <el-timeline-item
          v-for="log in updateLogs"
          :key="log.version"
          :type="log.type"
          :color="log.color"
        >
          <div class="log-header">
            <span class="log-version">{{ log.version }}</span>
            <span class="log-date">{{ log.date }}</span>
            <el-tag v-if="log.isCurrent" type="success" size="small">当前</el-tag>
            <el-tag v-if="log.isLatest" type="warning" size="small">最新</el-tag>
          </div>
          <ul class="log-items">
            <li v-for="(item, idx) in log.items" :key="idx" :class="item.type">
              <span class="item-badge">{{ item.type === 'add' ? '新增' : item.type === 'optimize' ? '优化' : '修复' }}</span>
              {{ item.text }}
            </li>
          </ul>
        </el-timeline-item>
      </el-timeline>
    </div>

    <!-- 历史更新记录 -->
    <div class="history-section">
      <div class="section-title">历史更新记录</div>
      <el-table :data="historyRecords" border stripe style="width: 100%">
        <el-table-column prop="version" label="版本号" width="120" align="center" />
        <el-table-column prop="date" label="发布时间" width="120" align="center" />
        <el-table-column prop="updateType" label="更新类型" width="160" align="center">
          <template #default="{ row }">
            <el-tag :type="row.typeTag" size="small">{{ row.updateType }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.statusTag" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="更新说明" min-width="300" show-overflow-tooltip />
      </el-table>
    </div>

    <!-- 更新确认弹窗 -->
    <el-dialog
      v-model="updateDialogVisible"
      title="系统更新确认"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="update-confirm-content">
        <div class="confirm-icon">⚠️</div>
        <div class="confirm-title">即将更新系统版本</div>
        <div class="version-compare">
          <div class="compare-item">
            <span class="compare-label">当前版本</span>
            <span class="compare-value old">{{ currentVersion.version }}</span>
          </div>
          <div class="compare-arrow">→</div>
          <div class="compare-item">
            <span class="compare-label">目标版本</span>
            <span class="compare-value new">{{ latestVersion.version }}</span>
          </div>
        </div>

        <div class="update-preview">
          <div class="preview-title">更新内容预览</div>
          <ul>
            <li v-for="(item, idx) in latestLogItems" :key="idx">
              {{ item.type === 'add' ? '新增' : item.type === 'optimize' ? '优化' : '修复' }}: {{ item.text }}
            </li>
          </ul>
        </div>

        <div class="update-warning">
          更新期间系统可能短暂不可用，建议在业务低峰期执行。
        </div>
      </div>

      <template #footer>
        <el-button @click="updateDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="updating" @click="handleUpdate">确认更新</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Right, Download } from '@element-plus/icons-vue'
import { getFirmwares } from '@/api/firmwares.js'

interface LogItem {
  type: 'add' | 'optimize' | 'fix'
  text: string
}

interface UpdateLog {
  version: string
  date: string
  items: LogItem[]
  isCurrent?: boolean
  isLatest?: boolean
  type?: string
  color?: string
}

const loading = ref(false)

// 当前版本（写死）
const currentVersion = ref({
  version: 'v2.3.1',
  date: '2024-04-15'
})

// 全部版本历史（从新到旧）
const allVersions = ref<{
  version: string
  date: string
  updateType: string
  typeTag: string
  status: string
  statusTag: string
  description: string
  items?: { type: 'add' | 'optimize' | 'fix'; text: string }[]
}[]>([])

const fetchFirmwares = async () => {
  loading.value = true
  try {
    const res: any = await getFirmwares({ page: 1, page_size: 100 })
    const items = res?.items || res || []
    allVersions.value = items.map((item: any) => ({
      version: item.version || item.name || '',
      date: item.release_date || item.date || '',
      updateType: item.update_type || '功能更新',
      typeTag: item.type_tag || 'success',
      status: item.status || '已更新',
      statusTag: item.status_tag || 'info',
      description: item.description || '',
      items: item.items || []
    }))
  } catch (error) {
    console.error('Failed to load firmwares:', error)
    ElMessage.error('加载固件版本失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchFirmwares()
})

// 最新版本
const latestVersion = computed(() => allVersions.value[0] || { version: '', date: '' })

// 是否有更新
const hasUpdate = computed(() => latestVersion.value.version !== currentVersion.value.version)

// 待更新数量
const updateCount = computed(() => {
  const currentIdx = allVersions.value.findIndex(v => v.version === currentVersion.value.version)
  if (currentIdx === -1) return 0
  return currentIdx
})

// 更新日志（时间线）
const updateLogs = computed(() => {
  const logs: UpdateLog[] = allVersions.value.map((v, index) => ({
    version: v.version,
    date: v.date,
    isLatest: index === 0,
    isCurrent: v.version === currentVersion.value.version,
    type: index === 0 ? 'primary' : v.version === currentVersion.value.version ? 'success' : '',
    color: index === 0 ? '#00E5FF' : v.version === currentVersion.value.version ? '#00FF88' : '#909399',
    items: v.items || []
  }))
  return logs
})

// 最新版本的日志项（用于弹窗预览）
const latestLogItems = computed(() => updateLogs.value[0]?.items || [])

// 历史记录表格数据
const historyRecords = computed(() => allVersions.value)

// 更新弹窗
const updateDialogVisible = ref(false)
const updating = ref(false)

const openUpdateDialog = () => {
  updateDialogVisible.value = true
}

const handleUpdate = async () => {
  updating.value = true
  await new Promise(r => setTimeout(r, 2000))
  updating.value = false
  updateDialogVisible.value = false
  // 更新当前版本
  currentVersion.value = { ...latestVersion.value }
  ElMessage.success('系统更新成功，当前版本已更新至 ' + latestVersion.value.version)
}
</script>

<style scoped>
.firmware-center {
  padding: 20px;
}

/* 版本卡片 */
.version-cards {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 24px;
}

.version-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 24px 32px;
  text-align: center;
  min-width: 180px;
}

.version-card.current {
  border-color: #00FF88;
  background: rgba(0, 255, 136, 0.05);
}

.version-card.latest {
  border-color: #00E5FF;
  background: rgba(0, 229, 255, 0.05);
}

.version-card.status {
  border-color: rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.02);
}

.version-card.status.outdated {
  border-color: #FFAA00;
  background: rgba(255, 170, 0, 0.05);
}

.card-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.card-version {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.version-card.current .card-version {
  color: #00FF88;
}

.version-card.latest .card-version {
  color: #00E5FF;
}

.version-card.status.outdated .card-version {
  color: #FFAA00;
}

.version-card.status:not(.outdated) .card-version {
  color: #00FF88;
}

.card-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.version-arrow {
  color: var(--text-secondary);
  display: flex;
  align-items: center;
}

/* 更新操作 */
.update-action {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.update-action .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
  padding: 12px 48px;
  font-size: 16px;
  font-weight: 600;
}

.update-action .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.update-action .el-button.is-disabled {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
}

/* 区域标题 */
.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

/* 更新日志 */
.changelog-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.changelog-section :deep(.el-timeline-item__node) {
  background-color: transparent;
  border: 2px solid var(--el-timeline-node-color);
}

.changelog-section :deep(.el-timeline-item__tail) {
  border-left-color: var(--border-color);
}

.log-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.log-version {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
}

.log-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.log-items {
  list-style: none;
  padding: 0;
  margin: 0;
}

.log-items li {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 2;
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-badge {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.log-items li.add .item-badge {
  background: rgba(0, 255, 136, 0.15);
  color: #00FF88;
}

.log-items li.optimize .item-badge {
  background: rgba(0, 229, 255, 0.15);
  color: #00E5FF;
}

.log-items li.fix .item-badge {
  background: rgba(255, 170, 0, 0.15);
  color: #FFAA00;
}

/* 历史记录 */
.history-section {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 20px;
}

/* 更新确认弹窗 */
.update-confirm-content {
  text-align: center;
  padding: 10px 0;
}

.confirm-icon {
  font-size: 40px;
  margin-bottom: 8px;
}

.confirm-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.version-compare {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  margin-bottom: 24px;
}

.compare-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.compare-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.compare-value {
  font-size: 20px;
  font-weight: 700;
  padding: 8px 20px;
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.compare-value.old {
  color: var(--text-secondary);
  background: rgba(255, 255, 255, 0.03);
}

.compare-value.new {
  color: #00E5FF;
  background: rgba(0, 229, 255, 0.08);
  border-color: #00E5FF;
}

.compare-arrow {
  font-size: 24px;
  color: #00E5FF;
  font-weight: 700;
}

.update-preview {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  text-align: left;
  margin-bottom: 16px;
}

.preview-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
}

.update-preview ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.update-preview li {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 2;
}

.update-warning {
  font-size: 12px;
  color: #FFAA00;
  background: rgba(255, 170, 0, 0.08);
  border: 1px solid rgba(255, 170, 0, 0.2);
  border-radius: 6px;
  padding: 10px 16px;
}

:deep(.el-dialog__footer .el-button--primary) {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

:deep(.el-dialog__footer .el-button--primary:hover) {
  background: #00B4D8;
  border-color: #00B4D8;
}
</style>
