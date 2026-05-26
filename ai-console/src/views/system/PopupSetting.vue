<template>
  <div class="popup-setting">
    <div class="setting-layout">
      <!-- 左侧设置区 -->
      <div class="setting-form">
        <div class="form-title">弹窗设置</div>
        <el-form :model="form" label-width="120px">
          <el-form-item label="是否启用弹窗">
            <el-switch
              v-model="form.popupEnabled"
              active-color="#36D68A"
              inactive-color="#303030"
            />
            <span class="switch-text">{{ form.popupEnabled ? '是' : '否' }}</span>
          </el-form-item>
          <el-form-item label="是否启用定时弹窗">
            <el-switch
              v-model="form.timedPopup"
              active-color="#36D68A"
              inactive-color="#303030"
            />
            <span class="switch-text">{{ form.timedPopup ? '是' : '否' }}</span>
          </el-form-item>
          <el-form-item label="弹窗频率(s)">
            <div class="frequency-input">
              <el-input-number
                v-model="form.popupFrequency"
                :min="1"
                :max="3600"
                :step="1"
              />
              <span class="unit">秒</span>
            </div>
          </el-form-item>
          <el-form-item label="事件类型">
            <el-select v-model="form.eventType" placeholder="请选择事件类型" style="width: 100%">
              <el-option label="高温告警" value="high_temp" />
              <el-option label="人员聚集" value="crowd" />
              <el-option label="周界入侵" value="intrusion" />
              <el-option label="设备离线" value="offline" />
            </el-select>
          </el-form-item>
          <el-form-item label="事件限制">
            <el-button type="primary" @click="openLimitDialog">查看</el-button>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="saveSettings">确定</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 右侧事件限制管理弹窗 -->
      <el-dialog
        v-model="limitDialogVisible"
        title="事件限制管理"
        width="700px"
        :close-on-click-modal="false"
      >
        <div class="limit-toolbar">
          <el-button type="primary" @click="openLimitModal('add')">
            <el-icon><Plus /></el-icon>添加新限制
          </el-button>
        </div>

        <el-table :data="pagedLimitData" border stripe v-loading="loading">
          <el-table-column prop="device" label="设备" min-width="150" />
          <el-table-column prop="timeInterval" label="时间间隔(s)" width="120" align="center" />
          <el-table-column prop="responseMode" label="响应方式" width="120" align="center" />
          <el-table-column prop="enabled" label="是否启用" width="100" align="center">
            <template #default="{ row }">
              <el-switch
                v-model="row.enabled"
                active-color="#36D68A"
                inactive-color="#303030"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <el-button link class="action-edit" size="small" @click="openLimitModal('edit', row)">编辑</el-button>
              <el-button link class="action-delete" size="small" @click="handleDeleteLimit(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="limitPage"
            v-model:page-size="limitPageSize"
            :page-sizes="[5, 10, 20, 50]"
            :total="limitList.length"
            layout="total, sizes, prev, pager, next, jumper"
            background
          />
        </div>

        <!-- 添加/编辑限制弹窗 -->
        <el-dialog
          v-model="limitFormVisible"
          :title="limitDialogTitle"
          width="450px"
          append-to-body
          :close-on-click-modal="false"
        >
          <el-form ref="limitFormRef" :model="limitForm" :rules="limitRules" label-width="100px">
            <el-form-item label="设备" prop="device">
              <el-select v-model="limitForm.device" placeholder="请选择设备" style="width: 100%">
                <el-option label="摄像头A" value="摄像头A" />
                <el-option label="摄像头B" value="摄像头B" />
                <el-option label="摄像头C" value="摄像头C" />
              </el-select>
            </el-form-item>
            <el-form-item label="时间间隔(s)" prop="timeInterval">
              <el-input-number
                v-model="limitForm.timeInterval"
                :min="1"
                :max="3600"
                :step="1"
                style="width: 100%"
              />
            </el-form-item>
            <el-form-item label="响应方式" prop="responseMode">
              <el-select v-model="limitForm.responseMode" placeholder="请选择响应方式" style="width: 100%">
                <el-option label="立即弹窗" value="立即弹窗" />
                <el-option label="静默记录" value="静默记录" />
                <el-option label="延迟弹窗" value="延迟弹窗" />
              </el-select>
            </el-form-item>
            <el-form-item label="是否启用">
              <el-switch
                v-model="limitForm.enabled"
                active-color="#36D68A"
                inactive-color="#303030"
              />
            </el-form-item>
          </el-form>

          <template #footer>
            <el-button @click="limitFormVisible = false">取消</el-button>
            <el-button type="primary" @click="handleLimitSubmit">{{ editingLimitId ? '保存' : '确定' }}</el-button>
          </template>
        </el-dialog>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getPopupSettings,
  createPopupSetting,
  updatePopupSetting,
  deletePopupSetting
} from '@/api/popup-settings.js'

const form = reactive({
  popupEnabled: false,
  timedPopup: false,
  popupFrequency: 1,
  eventType: ''
})

const saveSettings = () => {
  ElMessage.success('设置保存成功')
}

const loading = ref(false)

// 事件限制管理
interface LimitItem {
  id: number
  device: string
  timeInterval: number
  responseMode: string
  enabled: boolean
}

const limitDialogVisible = ref(false)
const limitList = ref<LimitItem[]>([])
const limitPage = ref(1)
const limitPageSize = ref(5)

const pagedLimitData = computed(() => {
  const start = (limitPage.value - 1) * limitPageSize.value
  return limitList.value.slice(start, start + limitPageSize.value)
})

const openLimitDialog = () => {
  limitDialogVisible.value = true
}

const fetchLimitList = async () => {
  loading.value = true
  try {
    const data = await getPopupSettings()
    limitList.value = (data?.items || data || []) as LimitItem[]
  } catch (error) {
    console.error('Failed to load popup settings:', error)
    ElMessage.error('加载事件限制列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchLimitList()
})

const limitFormVisible = ref(false)
const limitDialogTitle = ref('添加限制')
const limitFormRef = ref()
const editingLimitId = ref<number | null>(null)

const limitForm = reactive({
  device: '',
  timeInterval: 1,
  responseMode: '',
  enabled: true
})

const limitRules = {
  device: [{ required: true, message: '请选择设备', trigger: 'change' }],
  timeInterval: [{ required: true, message: '请输入时间间隔', trigger: 'blur' }],
  responseMode: [{ required: true, message: '请选择响应方式', trigger: 'change' }]
}

const openLimitModal = (type: 'add' | 'edit', row?: LimitItem) => {
  if (type === 'edit' && row) {
    editingLimitId.value = row.id
    limitDialogTitle.value = '编辑限制'
    Object.assign(limitForm, {
      device: row.device,
      timeInterval: row.timeInterval,
      responseMode: row.responseMode,
      enabled: row.enabled
    })
  } else {
    editingLimitId.value = null
    limitDialogTitle.value = '添加限制'
    Object.assign(limitForm, {
      device: '',
      timeInterval: 1,
      responseMode: '',
      enabled: true
    })
  }
  limitFormVisible.value = true
}

const handleLimitSubmit = async () => {
  const valid = await (limitFormRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingLimitId.value) {
      await updatePopupSetting(editingLimitId.value, {
        device: limitForm.device,
        time_interval: limitForm.timeInterval,
        response_mode: limitForm.responseMode,
        enabled: limitForm.enabled
      })
      const idx = limitList.value.findIndex(item => item.id === editingLimitId.value)
      if (idx !== -1) {
        Object.assign(limitList.value[idx], {
          device: limitForm.device,
          timeInterval: limitForm.timeInterval,
          responseMode: limitForm.responseMode,
          enabled: limitForm.enabled
        })
      }
      ElMessage.success('编辑成功')
    } else {
      const res = await createPopupSetting({
        device: limitForm.device,
        time_interval: limitForm.timeInterval,
        response_mode: limitForm.responseMode,
        enabled: limitForm.enabled
      })
      limitList.value.push({
        id: res?.id || Date.now(),
        device: limitForm.device,
        timeInterval: limitForm.timeInterval,
        responseMode: limitForm.responseMode,
        enabled: limitForm.enabled
      })
      ElMessage.success('添加成功')
    }
    limitFormVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDeleteLimit = async (row: LimitItem) => {
  try {
    await ElMessageBox.confirm(`确定删除该限制规则吗？`, '提示', { type: 'warning' })
    await deletePopupSetting(row.id)
    const idx = limitList.value.findIndex(item => item.id === row.id)
    if (idx !== -1) limitList.value.splice(idx, 1)
    ElMessage.success('删除成功')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}
</script>

<style scoped>
.popup-setting {
  padding: 20px;
}

.setting-layout {
  display: flex;
  gap: 24px;
}

.setting-form {
  flex: 0 0 400px;
  background: var(--bg-primary);
  border-radius: 4px;
  padding: 24px;
}

.form-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.switch-text {
  margin-left: 12px;
  color: #B0C4D8;
  font-size: 14px;
}

.frequency-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.unit {
  color: #B0C4D8;
  font-size: 14px;
}

.setting-form .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.setting-form .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.limit-toolbar {
  margin-bottom: 16px;
}

.limit-toolbar .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.limit-toolbar .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.action-edit {
  color: #00E5FF;
  background: rgba(0, 229, 255, 0.15);
  border: 1px solid rgba(0, 229, 255, 0.4);
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 600;
  text-shadow: none;
}

.action-edit:hover {
  color: #00FF88;
  background: rgba(0, 229, 255, 0.25);
  border-color: #00E5FF;
}

.action-delete {
  color: #FF006E;
  background: rgba(255, 0, 110, 0.15);
  border: 1px solid rgba(255, 0, 110, 0.4);
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 600;
  text-shadow: none;
}

.action-delete:hover {
  color: #FF4D6D;
  background: rgba(255, 0, 110, 0.25);
  border-color: #FF006E;
}
</style>
