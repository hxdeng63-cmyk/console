<template>
  <div class="linkage-rule">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新建
        </el-button>
      </div>
    </div>

<!-- 表格 -->
    <el-table :data="pagedData" v-loading="loading" border stripe>
      <el-table-column prop="status" label="状态" width="80" align="center">
        <template #default="{ row }">
          <el-switch v-model="row.status" active-color="#36D68A" @change="onStatusChange(row)" />
        </template>
      </el-table-column>
      <el-table-column prop="ruleName" label="联动规则名称" min-width="200" show-overflow-tooltip />
      <el-table-column prop="level" label="预警级别" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getLevelType(row.level)" size="small">{{ row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="algorithm" label="算法" width="120" align="center" />
      <el-table-column prop="event" label="事件" width="120" align="center" />
      <el-table-column prop="compliant" label="是否合规" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.compliant ? 'success' : 'danger'" size="small">
            {{ row.compliant ? '是' : '否' }}
          </el-tag>
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
        :page-sizes="[10, 20, 50, 100]"
        :total="tableData.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联动规则名称" prop="ruleName">
              <el-input v-model="form.ruleName" placeholder="请输入联动规则名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预警级别" prop="level">
              <el-select v-model="form.level" placeholder="请选择" style="width: 100%">
                <el-option label="全部" value="全部" />
                <el-option label="高" value="高" />
                <el-option label="中" value="中" />
                <el-option label="低" value="低" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="算法" prop="algorithm">
              <el-select v-model="form.algorithm" placeholder="请选择算法" style="width: 100%">
                <el-option label="烟火检测" value="烟火检测" />
                <el-option label="入侵检测" value="入侵检测" />
                <el-option label="人脸识别" value="人脸识别" />
                <el-option label="行为分析" value="行为分析" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="事件" prop="event">
              <el-select v-model="form.event" placeholder="请选择" style="width: 100%">
                <el-option label="高温告警" value="高温告警" />
                <el-option label="人员聚集" value="人员聚集" />
                <el-option label="周界入侵" value="周界入侵" />
                <el-option label="设备离线" value="设备离线" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="延迟推送" prop="delayPush">
              <el-switch v-model="form.delayPush" active-color="#36D68A" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否合规" prop="compliant">
              <el-select v-model="form.compliant" placeholder="请选择" style="width: 100%">
                <el-option label="全部" value="" />
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-select v-model="form.unit" placeholder="请选择单位" style="width: 100%">
                <el-option label="隧道所" value="隧道所" />
                <el-option label="分公司" value="分公司" />
                <el-option label="养护中心" value="养护中心" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="设备选择">
          <div class="device-selector">
            <el-input v-model="deviceSearch" placeholder="输入关键字进行过滤" prefix-icon="Search" clearable />
            <div class="device-list">
              <div v-if="filteredDevices.length === 0" class="empty-text">暂无数据</div>
              <el-checkbox-group v-else v-model="form.selectedDevices">
                <el-checkbox v-for="device in filteredDevices" :key="device" :label="device">{{ device }}</el-checkbox>
              </el-checkbox-group>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="推送渠道" prop="pushChannels">
          <div class="push-channels">
            <el-checkbox-group v-model="form.pushChannels">
              <el-checkbox label="钉钉">钉钉</el-checkbox>
              <el-checkbox label="钉钉企业群">钉钉企业群</el-checkbox>
              <el-checkbox label="企业微信">企业微信</el-checkbox>
              <el-checkbox label="系统提示音">系统提示音</el-checkbox>
              <el-checkbox label="API接口推送">API接口推送</el-checkbox>
              <el-checkbox label="摄像机控制">摄像机控制</el-checkbox>
              <el-checkbox label="定制推送渠道">定制推送渠道</el-checkbox>
              <el-checkbox label="Kafka">Kafka</el-checkbox>
              <el-checkbox label="OA推送">OA推送</el-checkbox>
              <el-checkbox label="语音播报">语音播报</el-checkbox>
              <el-checkbox label="声光报警">声光报警</el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editingId ? '保存' : '立即创建' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLinkageRules, createLinkageRule, updateLinkageRule, deleteLinkageRule, enableLinkageRule, disableLinkageRule } from '@/api/linkage-rules'

interface RuleItem {
  id: number
  status: boolean
  ruleName: string
  level: string
  algorithm: string
  event: string
  compliant: boolean
  unit: string
  pushChannels: string[]
  selectedDevices: string[]
}

const loading = ref(false)
const tableData = ref<RuleItem[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const data = await getLinkageRules()
    tableData.value = data.items || data
  } catch (error) {
    console.error('Failed to load linkage rules:', error)
  } finally {
    loading.value = false
  }
})

const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const getLevelType = (level: string) => {
  switch (level) {
    case '高': return 'danger'
    case '中': return 'warning'
    case '低': return 'info'
    default: return 'info'
  }
}

const onStatusChange = async (row: RuleItem) => {
  try {
    if (row.status) {
      await enableLinkageRule(row.id)
    } else {
      await disableLinkageRule(row.id)
    }
    ElMessage.success(`规则 "${row.ruleName}" 已${row.status ? '启用' : '禁用'}`)
  } catch (error: any) {
    row.status = !row.status
    ElMessage.error(error.message || '操作失败')
  }
}

const deviceSearch = ref('')
const allDevices = ['白马寺隧道', '大古城隧道', '老鸦峡1号隧道', '老鸦峡2号隧道', '岘子隧道', '浪塘1号隧道', '浪塘3号隧道', '公哇岭隧道']

const filteredDevices = computed(() => {
  if (!deviceSearch.value) return allDevices
  return allDevices.filter(d => d.includes(deviceSearch.value))
})

const dialogVisible = ref(false)
const dialogTitle = ref('新建联动规则')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = () => ({
  ruleName: '',
  level: '',
  algorithm: '',
  event: '',
  compliant: null as boolean | null,
  delayPush: false,
  unit: '',
  selectedDevices: [] as string[],
  pushChannels: [] as string[]
})

const form = reactive(defaultForm())

const rules = {
  ruleName: [{ required: true, message: '请输入联动规则名称', trigger: 'blur' }],
  level: [{ required: true, message: '请选择预警级别', trigger: 'change' }],
  pushChannels: [{ required: true, message: '请选择推送渠道', trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: RuleItem) => {
  Object.assign(form, defaultForm())
  deviceSearch.value = ''
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑联动规则'
    Object.assign(form, {
      ruleName: row.ruleName,
      level: row.level,
      algorithm: row.algorithm,
      event: row.event,
      compliant: row.compliant,
      delayPush: false,
      unit: row.unit,
      selectedDevices: [...row.selectedDevices],
      pushChannels: [...row.pushChannels]
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新建联动规则'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    if (editingId.value) {
      await updateLinkageRule(editingId.value, form)
      const idx = tableData.value.findIndex(item => item.id === editingId.value)
      if (idx !== -1) {
        Object.assign(tableData.value[idx], form)
      }
      ElMessage.success('编辑成功')
    } else {
      const newRule = await createLinkageRule(form)
      tableData.value.push(newRule)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDelete = (row: RuleItem) => {
  ElMessageBox.confirm(`确定删除联动规则 "${row.ruleName}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteLinkageRule(row.id)
        const idx = tableData.value.findIndex(item => item.id === row.id)
        if (idx !== -1) tableData.value.splice(idx, 1)
        ElMessage.success('删除成功')
      } catch (error: any) {
        ElMessage.error(error.message || '删除失败')
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.linkage-rule {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
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

.push-channels {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

:deep(.el-dialog__body) {
  padding-top: 20px;
}
</style>
