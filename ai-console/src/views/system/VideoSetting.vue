<template>
  <div class="video-setting">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left-actions">
        <span class="total-label">录像设置</span>
      </div>
      <el-button type="primary" @click="openModal('add')">
        <el-icon><Plus /></el-icon>新增规则
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe v-loading="loading">
      <el-table-column prop="org_name" label="规则名称（公司）" min-width="200" show-overflow-tooltip />
      <el-table-column label="事件" min-width="300">
        <template #default="{ row }">
          <el-tag
            v-for="eventId in row.event_types"
            :key="eventId"
            size="small"
            style="margin-right: 4px;"
          >
            {{ getEventName(eventId) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="record_duration_seconds" label="录像时长" width="100" align="center">
        <template #default="{ row }">
          {{ row.record_duration_seconds }}秒
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
        :total="total"
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
        <el-form-item label="公司" prop="org_id">
          <el-select v-model="form.org_id" placeholder="请选择公司" style="width: 100%">
            <el-option
              v-for="org in orgList"
              :key="org.id"
              :label="org.name"
              :value="org.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="事件选择" prop="event_types">
          <div class="event-selector">
            <el-checkbox-group v-model="form.event_types">
              <el-checkbox
                v-for="et in eventTypeList"
                :key="et.id"
                :value="et.id"
              >
                {{ et.name }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>
        <el-form-item label="时长设置">
          <div class="duration-selector">
            <el-input-number v-model="form.record_duration_seconds" :min="6" :max="60" :step="2" />
            <span class="duration-unit">秒</span>
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
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getVideoSettings,
  createVideoSetting,
  updateVideoSetting,
  deleteVideoSetting,
  toggleVideoSettingStatus
} from '@/api/video-settings'
import { getEventTypes } from '@/api/event-types'
import { getOrgs } from '@/api/orgs'

interface VideoSettingItem {
  id: number
  org_id: number
  org_name: string
  event_types: number[]
  record_duration_seconds: number
  status: boolean
}

interface EventTypeItem {
  id: number
  name: string
}

interface OrgItem {
  id: number
  name: string
}

const tableData = ref<VideoSettingItem[]>([])
const eventTypeList = ref<EventTypeItem[]>([])
const orgList = ref<OrgItem[]>([])
const loading = ref(false)
const total = ref(0)

const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const getEventName = (eventId: number) => {
  const et = eventTypeList.value.find(e => e.id === eventId)
  return et ? et.name : `事件${eventId}`
}

const onStatusChange = async (row: VideoSettingItem) => {
  try {
    await toggleVideoSettingStatus(row.id)
    ElMessage.success(`规则 "${row.org_name}" 已${row.status ? '启用' : '禁用'}`)
  } catch (e) {
    row.status = !row.status
    ElMessage.error('状态更新失败')
  }
}

const dialogVisible = ref(false)
const dialogTitle = ref('添加录像设置')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  org_id: null as number | null,
  event_types: [] as number[],
  record_duration_seconds: 10
})

const form = reactive(defaultForm())

const rules = {
  org_id: [{ required: true, message: '请选择公司', trigger: 'change' }],
  event_types: [{ required: true, message: '请选择事件', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: VideoSettingItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '修改录像设置'
    Object.assign(form, {
      org_id: row.org_id,
      event_types: [...row.event_types],
      record_duration_seconds: row.record_duration_seconds
    })
  } else {
    editingId.value = null
    dialogTitle.value = '添加录像设置'
  }
  dialogVisible.value = true
}

const fetchData = async () => {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    const res = await getVideoSettings(params)
    const data = res.data || res
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    ElMessage.error('获取录像设置失败')
  } finally {
    loading.value = false
  }
}

const fetchEventTypes = async () => {
  try {
    const res = await getEventTypes({ page_size: 100 })
    const data = res.data || res
    eventTypeList.value = data.items || []
  } catch (e) {
    console.error('获取事件类型失败:', e)
  }
}

const fetchOrgs = async () => {
  try {
    const res = await getOrgs({ page_size: 100 })
    const data = res.data || res
    orgList.value = (data.items || []).filter((o: any) => o.level === 1)
  } catch (e) {
    console.error('获取公司列表失败:', e)
  }
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  const payload = {
    org_id: form.org_id!,
    event_types: form.event_types,
    record_duration_seconds: form.record_duration_seconds,
    status: true
  }

  try {
    if (editingId.value) {
      await updateVideoSetting(editingId.value, payload)
      ElMessage.success('编辑成功')
    } else {
      await createVideoSetting(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e?.message || '操作失败')
  }
}

const handleDelete = (row: VideoSettingItem) => {
  ElMessageBox.confirm(`确定删除 "${row.org_name}" 的录像规则吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteVideoSetting(row.id)
        ElMessage.success('删除成功')
        await fetchData()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

onMounted(() => {
  fetchData()
  fetchEventTypes()
  fetchOrgs()
})
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
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.event-selector {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 8px;
}

.event-selector .el-checkbox {
  display: block;
  margin-bottom: 4px;
}

.duration-selector {
  display: flex;
  align-items: center;
  gap: 8px;
}

.duration-unit {
  color: rgba(255, 255, 255, 0.6);
}
</style>
