<template>
  <div class="video-setting">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left-actions">
        <span class="total-label">录像设置</span>
        <el-switch
          v-model="masterSwitch"
          active-color="#36D68A"
          inactive-color="#303030"
        />
        <span class="switch-label">{{ masterSwitch ? '已启用' : '已禁用' }}</span>
      </div>
      <el-button type="primary" @click="openModal('add')">
        <el-icon><Plus /></el-icon>新增规则
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe>
      <el-table-column prop="ruleName" label="规则名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="events" label="事件" min-width="300">
        <template #default="{ row }">
          <el-tag
            v-for="event in row.events"
            :key="event"
            size="small"
            style="margin-right: 4px;"
          >
            {{ event }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch
            v-model="row.status"
            active-color="#36D68A"
            inactive-color="#303030"
            @change="onStatusChange(row)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button link style="color: #00E5FF; background: rgba(0, 229, 255, 0.15); border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" size="small" @click="openModal('edit', row)">编辑</el-button>
          <el-button link style="color: #FF006E; background: rgba(255, 0, 110, 0.15); border: 1px solid rgba(255, 0, 110, 0.4); border-radius: 4px; padding: 2px 8px; font-weight: 600; text-shadow: none;" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="tableData.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="550px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="规则名称" prop="ruleName">
          <el-input v-model="form.ruleName" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="设备选择" prop="device">
          <div class="device-selector">
            <el-input v-model="deviceSearch" placeholder="输入关键字进行过滤" prefix-icon="Search" clearable />
            <div class="device-list">
              <div v-if="filteredDevices.length === 0" class="empty-text">暂无数据</div>
              <el-radio-group v-else v-model="form.device">
                <el-radio v-for="device in filteredDevices" :key="device" :value="device">{{ device }}</el-radio>
              </el-radio-group>
            </div>
          </div>
        </el-form-item>
        <el-form-item label="事件选择" prop="events">
          <div class="event-selector">
            <el-checkbox-group v-model="form.events">
              <el-checkbox value="疑似事故">疑似事故</el-checkbox>
              <el-checkbox value="作业人员">作业人员</el-checkbox>
              <el-checkbox value="交通阻塞">交通阻塞</el-checkbox>
              <el-checkbox value="异常停车">异常停车</el-checkbox>
              <el-checkbox value="烟雾">烟雾</el-checkbox>
              <el-checkbox value="作业车辆识别">作业车辆识别</el-checkbox>
              <el-checkbox value="非机动车驶入">非机动车驶入</el-checkbox>
              <el-checkbox value="占用应急车道">占用应急车道</el-checkbox>
              <el-checkbox value="逆向行驶">逆向行驶</el-checkbox>
              <el-checkbox value="通过卡车数量">通过卡车数量</el-checkbox>
              <el-checkbox value="通过大客车数量">通过大客车数量</el-checkbox>
              <el-checkbox value="通过摩托车数量">通过摩托车数量</el-checkbox>
              <el-checkbox value="通过小汽车数量">通过小汽车数量</el-checkbox>
              <el-checkbox value="下行车流量">下行车流量</el-checkbox>
              <el-checkbox value="上行车流量">上行车流量</el-checkbox>
              <el-checkbox value="行人闯入">行人闯入</el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>
        <el-form-item label="时长设置">
          <div class="duration-selector">
            <el-input-number v-model="form.recordDuration" :min="6" :max="30" :step="2" />
            <span class="duration-unit">秒</span>
          </div>
          <div class="duration-note">
            注：时长范围6-30秒，步进值为2秒，每次录像最大3MB
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editingId ? '保存' : '确定' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface RecordRule {
  id: number
  ruleName: string
  device: string
  events: string[]
  recordDuration: number
  status: boolean
}

const tableData = ref<RecordRule[]>([])

const masterSwitch = ref(true)
const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const onStatusChange = (row: RecordRule) => {
  ElMessage.success(`规则 "${row.ruleName}" 已${row.status ? '启用' : '禁用'}`)
}

const deviceSearch = ref('')
const allDevices = ['摄像头A', '摄像头B', '摄像头C', '摄像头D', '摄像头E']

const filteredDevices = computed(() => {
  if (!deviceSearch.value) return allDevices
  return allDevices.filter(d => d.includes(deviceSearch.value))
})

const dialogVisible = ref(false)
const dialogTitle = ref('添加录像设置')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  ruleName: '',
  device: '',
  events: [] as string[],
  recordDuration: 6
})

const form = reactive(defaultForm())

const rules = {
  ruleName: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  device: [{ required: true, message: '请选择设备', trigger: 'change' }],
  events: [{ required: true, message: '请选择事件', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: RecordRule) => {
  Object.assign(form, defaultForm())
  deviceSearch.value = ''
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '修改录像设置'
    Object.assign(form, {
      ruleName: row.ruleName,
      device: row.device,
      events: [...row.events],
      recordDuration: row.recordDuration
    })
  } else {
    editingId.value = null
    dialogTitle.value = '添加录像设置'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  if (editingId.value) {
    const idx = tableData.value.findIndex(item => item.id === editingId.value)
    if (idx !== -1) {
      Object.assign(tableData.value[idx], {
        ruleName: form.ruleName,
        device: form.device,
        events: [...form.events],
        recordDuration: form.recordDuration
      })
    }
    ElMessage.success('修改成功')
  } else {
    tableData.value.push({
      id: Date.now(),
      ruleName: form.ruleName,
      device: form.device,
      events: [...form.events],
      recordDuration: form.recordDuration,
      status: true
    })
    ElMessage.success('添加成功')
  }
  dialogVisible.value = false
}

const handleDelete = (row: RecordRule) => {
  ElMessageBox.confirm(`确定删除录像规则 "${row.ruleName}" 吗？`, '提示', { type: 'warning' })
    .then(() => {
      const idx = tableData.value.findIndex(item => item.id === row.id)
      if (idx !== -1) tableData.value.splice(idx, 1)
      ElMessage.success('删除成功')
    })
    .catch(() => {})
}
</script>

<style scoped>
.video-setting {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.left-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-label {
  font-size: 16px;
  font-weight: 500;
  margin-right: 8px;
}

.switch-label {
  font-size: 14px;
  color: #B0C4D8;
}

.toolbar .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.toolbar .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.device-selector {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
}

.device-list {
  margin-top: 12px;
  max-height: 150px;
  overflow-y: auto;
}

.empty-text {
  color: #B0C4D8;
  text-align: center;
  padding: 20px;
}

.event-selector {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  max-height: 180px;
  overflow-y: auto;
}

.event-selector :deep(.el-checkbox) {
  margin-right: 16px;
  margin-bottom: 8px;
}

.duration-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.duration-unit {
  color: #B0C4D8;
  font-size: 14px;
}

.duration-note {
  margin-top: 8px;
  font-size: 12px;
  color: #00E5FF;
  line-height: 1.4;
}

:deep(.el-dialog__body) {
  padding-top: 20px;
}
</style>
