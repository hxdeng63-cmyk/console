<template>
  <div class="algorithm-manage">
    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon"><el-icon :size="28"><Box /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ tableData.length }}</div>
          <div class="stat-label">算法总数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="color: #00FF88"><el-icon :size="28"><Bell /></el-icon></div>
        <div class="stat-info">
          <div class="stat-value">{{ totalEvents }}</div>
          <div class="stat-label">事件类型</div>
        </div>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-input v-model="searchName" placeholder="请输入算法名称" style="width: 200px" clearable />
        <el-button type="primary" @click="handleSearch">查询</el-button>
      </div>
      <div class="action-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新建算法
        </el-button>
      </div>
    </div>

    <!-- 算法卡片列表 -->
    <div class="algorithm-list">
      <div v-for="algo in filteredData" :key="algo.id" class="algo-card">
        <div class="algo-header">
          <div class="algo-title-area">
            <el-icon class="algo-icon" :size="22"><Box /></el-icon>
            <div class="algo-title-info">
              <div class="algo-name">{{ algo.name }}</div>
              <div class="algo-desc">{{ algo.description }}</div>
            </div>
          </div>
          <div class="algo-actions">
            <el-button class="action-edit" size="small" @click="openModal('edit', algo)">编辑</el-button>
            <el-button class="action-delete" size="small" @click="handleDelete(algo)">删除</el-button>
          </div>
        </div>
        <div class="algo-divider" />
        <div class="algo-events">
          <div class="events-header">
            <span class="events-title">
              <el-icon :size="14"><Collection /></el-icon>
              包含事件（{{ algo.events?.length || 0 }}）
            </span>
            <el-button type="primary" size="small" class="btn-add-event" @click="openEventModal('add', algo)">
              <el-icon><Plus /></el-icon>添加事件
            </el-button>
          </div>
          <div v-if="algo.events?.length" class="events-tags">
            <div
              v-for="(ev, idx) in algo.events"
              :key="idx"
              class="event-tag"
            >
              <span class="event-name">{{ ev.name }}</span>
              <span class="event-desc">{{ ev.description }}</span>
              <span class="event-actions">
                <el-icon class="ev-edit" @click.stop="openEventModal('edit', algo, idx)"><Edit /></el-icon>
                <el-icon class="ev-delete" @click.stop="handleDeleteEvent(algo, idx)"><Delete /></el-icon>
              </span>
            </div>
          </div>
          <div v-else class="events-empty">
            <el-icon :size="32"><Collection /></el-icon>
            <span>暂无事件，点击上方按钮添加</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Box, Bell, Collection, Edit, Delete } from '@element-plus/icons-vue'
import { getAlgorithms, deleteAlgorithm, createAlgorithm, updateAlgorithm } from '@/api/algorithms'

interface AlgorithmEvent {
  name: string
  description: string
}

interface Algorithm {
  id: number
  name: string
  description: string
  events?: AlgorithmEvent[]
}

const loading = ref(false)
const tableData = ref<Algorithm[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const res = await getAlgorithms()
    tableData.value = res.data || []
  } catch (e) {
    ElMessage.error('获取算法列表失败')
  } finally {
    loading.value = false
  }
})

const searchName = ref('')

const handleSearch = () => {}

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    return !searchName.value || item.name.includes(searchName.value)
  })
})

const totalEvents = computed(() => {
  return tableData.value.reduce((sum, algo) => sum + (algo.events?.length || 0), 0)
})

// 添加/编辑弹窗
const dialogVisible = ref(false)
const dialogTitle = ref('新建算法')
const formRef = ref()
const editingId = ref<number | null>(null)
const editingTarget = ref<'algorithm' | 'event'>('algorithm')
const editingAlgorithmId = ref<number | null>(null)
const editingEventIndex = ref<number | null>(null)

const defaultForm = () => ({
  name: '',
  description: ''
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

const openModal = (type: 'add' | 'edit', row?: Algorithm) => {
  editingTarget.value = 'algorithm'
  editingAlgorithmId.value = null
  editingEventIndex.value = null
  if (type === 'add') {
    Object.assign(form, defaultForm())
    editingId.value = null
    dialogTitle.value = '新建算法'
  } else if (row) {
    editingId.value = row.id
    dialogTitle.value = '编辑算法'
    Object.assign(form, {
      name: row.name,
      description: row.description
    })
  }
  dialogVisible.value = true
}

const openEventModal = (type: 'add' | 'edit', algorithm: Algorithm, eventIndex?: number) => {
  editingTarget.value = 'event'
  editingAlgorithmId.value = algorithm.id
  editingEventIndex.value = eventIndex ?? null
  if (type === 'add') {
    Object.assign(form, defaultForm())
    dialogTitle.value = '添加事件'
  } else if (eventIndex !== undefined) {
    const ev = algorithm.events![eventIndex]
    dialogTitle.value = '编辑事件'
    Object.assign(form, {
      name: ev.name,
      description: ev.description
    })
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any)?.validate().catch(() => false)
  if (!valid) return

  if (editingTarget.value === 'event' && editingAlgorithmId.value !== null) {
    const algo = tableData.value.find(item => item.id === editingAlgorithmId.value)
    if (!algo) return
    if (!algo.events) algo.events = []
    if (editingEventIndex.value !== null) {
      algo.events[editingEventIndex.value] = { name: form.name, description: form.description }
      ElMessage.success('编辑成功')
    } else {
      algo.events.push({ name: form.name, description: form.description })
      ElMessage.success('添加成功')
    }
  } else {
    try {
      if (editingId.value) {
        await updateAlgorithm(editingId.value, {
          name: form.name,
          description: form.description
        })
        const idx = tableData.value.findIndex(item => item.id === editingId.value)
        if (idx !== -1) {
          tableData.value[idx].name = form.name
          tableData.value[idx].description = form.description
        }
        ElMessage.success('编辑成功')
      } else {
        const res = await createAlgorithm({
          name: form.name,
          description: form.description
        })
        tableData.value.push(res.data)
        ElMessage.success('新建成功')
      }
      dialogVisible.value = false
    } catch (e) {
      ElMessage.error('操作失败')
    }
  }
}

const handleDeleteEvent = (algorithm: Algorithm, eventIndex: number) => {
  ElMessageBox.confirm(`确定删除事件 "${algorithm.events![eventIndex].name}" 吗？`, '提示', { type: 'warning' })
    .then(() => {
      algorithm.events!.splice(eventIndex, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}

const handleDelete = async (row: Algorithm) => {
  try {
    await ElMessageBox.confirm(`确定删除算法 "${row.name}" 吗？`, '提示', { type: 'warning' })
    await deleteAlgorithm(row.id)
    const idx = tableData.value.findIndex(item => item.id === row.id)
    if (idx !== -1) tableData.value.splice(idx, 1)
    ElMessage.success('删除成功')
  } catch (e) {
    // user cancelled or API error
  }
}
</script>

<style scoped>
.algorithm-manage {
  padding: 20px;
}

/* 统计卡片 */
.stat-cards {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 180px;
}

.stat-icon {
  color: #00E5FF;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* 操作栏 */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.search-area {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-area .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.search-area .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.action-area {
  display: flex;
  gap: 12px;
  align-items: center;
}

.action-area .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.action-area .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

/* 算法卡片列表 */
.algorithm-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.algo-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
}

.algo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
}

.algo-title-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.algo-icon {
  color: #00E5FF;
  flex-shrink: 0;
}

.algo-title-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.algo-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.algo-desc {
  font-size: 13px;
  color: var(--text-secondary);
}

.algo-actions {
  display: flex;
  gap: 8px;
}

.algo-divider {
  height: 1px;
  background: var(--border-color);
  margin: 0 20px;
}

/* 事件区域 */
.algo-events {
  padding: 14px 20px 18px;
}

.events-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.events-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.events-title .el-icon {
  color: #00E5FF;
}

.btn-add-event {
  background: rgba(0, 229, 255, 0.1);
  border-color: rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.btn-add-event:hover {
  background: rgba(0, 229, 255, 0.2);
  border-color: #00E5FF;
}

/* 事件标签 */
.events-tags {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 10px;
}

.event-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(0, 229, 255, 0.06);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 6px;
  padding: 8px 12px;
  transition: all 0.2s;
  min-width: 0;
}

.event-tag:hover {
  background: rgba(0, 229, 255, 0.12);
  border-color: rgba(0, 229, 255, 0.4);
  box-shadow: 0 0 8px rgba(0, 229, 255, 0.1);
}

.event-name {
  font-size: 13px;
  font-weight: 600;
  color: #00E5FF;
  white-space: nowrap;
  flex-shrink: 0;
}

.event-desc {
  font-size: 12px;
  color: rgba(180, 210, 235, 0.65);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  min-width: 0;
}

.event-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}

.event-tag:hover .event-actions {
  opacity: 1;
}

.ev-edit {
  color: #00E5FF;
  cursor: pointer;
  font-size: 14px;
  padding: 2px;
  transition: color 0.2s;
}

.ev-edit:hover {
  color: #00FF88;
}

.ev-delete {
  color: #FF006E;
  cursor: pointer;
  font-size: 14px;
  padding: 2px;
  transition: color 0.2s;
}

.ev-delete:hover {
  color: #FF4D6D;
}

/* 空状态 */
.events-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 24px;
  color: var(--text-secondary);
  font-size: 13px;
}

.events-empty .el-icon {
  color: rgba(0, 229, 255, 0.2);
}

/* 操作按钮 - 编辑（青色） */
.action-edit {
  background: rgba(0, 229, 255, 0.15) !important;
  border: 1px solid rgba(0, 229, 255, 0.4) !important;
  color: #00E5FF !important;
  border-radius: 4px;
  padding: 6px 14px !important;
  font-weight: 600;
  text-shadow: none;
  box-shadow: none;
}

.action-edit:hover {
  background: rgba(0, 229, 255, 0.25) !important;
  border-color: #00E5FF !important;
  color: #00FF88 !important;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.3);
}

/* 操作按钮 - 删除（粉红） */
.action-delete {
  background: rgba(255, 0, 110, 0.15) !important;
  border: 1px solid rgba(255, 0, 110, 0.4) !important;
  color: #FF006E !important;
  border-radius: 4px;
  padding: 6px 14px !important;
  font-weight: 600;
  text-shadow: none;
  box-shadow: none;
}

.action-delete:hover {
  background: rgba(255, 0, 110, 0.25) !important;
  border-color: #FF006E !important;
  color: #FF4D6D !important;
  box-shadow: 0 0 12px rgba(255, 0, 110, 0.3);
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
