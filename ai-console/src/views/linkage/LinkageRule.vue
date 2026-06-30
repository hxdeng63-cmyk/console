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
      <el-table-column prop="algorithm" label="算法" width="120" align="center">
        <template #default="{ row }">
          <span>{{ row.algorithm }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="event" label="事件" width="120" align="center">
        <template #default="{ row }">
          <span>{{ row.event }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="compliant" label="是否合规" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.compliantType" size="small">{{ row.compliantText }}</el-tag>
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
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="120px">
        <el-form-item label="联动规则名称" prop="ruleName">
          <el-input v-model="form.ruleName" placeholder="请输入联动规则名称" />
        </el-form-item>

        <el-form-item label="预警级别" prop="level">
          <el-select v-model="form.level" placeholder="请选择" style="width: 100%">
            <el-option label="高" value="高" />
            <el-option label="中" value="中" />
            <el-option label="低" value="低" />
          </el-select>
        </el-form-item>

        <el-form-item label="算法" prop="algorithmId">
          <el-select v-model="form.algorithmId" placeholder="请选择算法" style="width: 100%">
            <el-option
              v-for="algo in algorithmOptions"
              :key="algo.id"
              :label="algo.name"
              :value="algo.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="事件" prop="eventTypeId">
          <el-select v-model="form.eventTypeId" placeholder="请选择事件" style="width: 100%">
            <el-option
              v-for="ev in eventTypeOptions"
              :key="ev.id"
              :label="ev.name"
              :value="ev.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="延迟推送" prop="delayPush">
          <el-switch v-model="form.delayPush" active-color="#36D68A" />
        </el-form-item>

        <el-form-item label="是否合规" prop="isCompliant">
          <el-select v-model="form.isCompliant" placeholder="请选择" style="width: 100%" clearable>
            <el-option label="全部" :value="null" />
            <el-option label="是" value="true" />
            <el-option label="否" value="false" />
          </el-select>
        </el-form-item>

        <el-form-item label="单位" prop="unit">
          <div class="unit-selector">
            <el-input v-model="form.unit" placeholder="请选择单位" readonly style="flex: 1" />
            <el-button type="primary" size="small" @click="orgDialogVisible = true">选择单位</el-button>
          </div>
        </el-form-item>

        <el-form-item label="设备选择" prop="selectedDeviceIds">
          <el-tree
            ref="deviceTreeRef"
            :data="deviceTreeData"
            :props="{ children: 'children', label: 'name' }"
            node-key="treeKey"
            show-checkbox
            default-expand-all
            class="device-tree"
          />
        </el-form-item>

        <el-form-item label="事件限制">
          <div class="event-limit-row">
            <span class="event-limit-label">事件限制</span>
            <el-button type="primary" link size="small" @click="eventLimitDialogVisible = true">查看</el-button>
          </div>
        </el-form-item>

        <el-form-item label="推送渠道" prop="pushChannels">
          <div class="push-channels">
            <el-checkbox
              v-for="ch in form.pushChannels"
              :key="ch.name"
              v-model="ch.enabled"
              @change="formRef?.validateField('pushChannels')"
            >
              {{ ch.name }}
            </el-checkbox>
          </div>
          <div v-for="ch in enabledPushChannels" :key="ch.name" class="channel-config-card">
            <div class="channel-config-title">{{ ch.name }} 配置</div>
            <!-- 钉钉 -->
            <template v-if="ch.name === '钉钉'">
              <el-form-item label="appKey"><el-input v-model="ch.config.appKey" /></el-form-item>
              <el-form-item label="appSecret"><el-input v-model="ch.config.appSecret" /></el-form-item>
              <el-form-item label="agentId"><el-input v-model="ch.config.agentId" /></el-form-item>
              <el-form-item label="target"><el-input v-model="ch.config.target" /></el-form-item>
              <el-form-item label="content"><el-input v-model="ch.config.content" type="textarea" /></el-form-item>
            </template>
            <!-- 企业微信 -->
            <template v-else-if="ch.name === '企业微信'">
              <el-form-item label="corpId"><el-input v-model="ch.config.corpId" /></el-form-item>
              <el-form-item label="agentId"><el-input v-model="ch.config.agentId" /></el-form-item>
              <el-form-item label="secret"><el-input v-model="ch.config.secret" /></el-form-item>
              <el-form-item label="target"><el-input v-model="ch.config.target" /></el-form-item>
              <el-form-item label="content"><el-input v-model="ch.config.content" type="textarea" /></el-form-item>
            </template>
            <!-- 系统提示音 -->
            <template v-else-if="ch.name === '系统提示音'">
              <el-form-item label="audioFile"><el-input v-model="ch.config.audioFile" /></el-form-item>
              <el-form-item label="volume">
                <el-slider v-model="ch.config.volume" :min="0" :max="100" show-input />
              </el-form-item>
              <el-form-item label="loop"><el-switch v-model="ch.config.loop" /></el-form-item>
            </template>
            <!-- 其他渠道 -->
            <template v-else>
              <el-form-item label="webhookUrl"><el-input v-model="ch.config.webhookUrl" /></el-form-item>
              <el-form-item label="target"><el-input v-model="ch.config.target" /></el-form-item>
              <el-form-item label="content"><el-input v-model="ch.config.content" type="textarea" /></el-form-item>
            </template>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">{{ editingId ? '保存' : '立即创建' }}</el-button>
      </template>
    </el-dialog>

    <!-- 事件限制弹窗 -->
    <el-dialog v-model="eventLimitDialogVisible" title="事件限制" width="500px" :close-on-click-modal="false">
      <p>事件限制配置功能即将上线，敬请期待。</p>
      <template #footer>
        <el-button @click="eventLimitDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 单位选择弹窗 -->
    <el-dialog v-model="orgDialogVisible" title="选择单位" width="400px" :close-on-click-modal="false">
      <el-tree
        ref="orgTreeRef"
        :data="orgTreeData"
        :props="{ children: 'children', label: 'label' }"
        node-key="id"
        highlight-current
        default-expand-all
        @node-click="onOrgNodeClick"
      />
      <template #footer>
        <el-button @click="orgDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmOrgSelect">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getLinkageRules,
  createLinkageRule,
  updateLinkageRule,
  deleteLinkageRule,
  enableLinkageRule,
  disableLinkageRule
} from '@/api/linkage-rules'
import { getAlgorithms } from '@/api/algorithms'
import { getEventTypes } from '@/api/event-types'
import { getDeviceGroupTree } from '@/api/device-groups'
import { getOrganizationTree } from '@/api/organizations'
import { getEventTypeDisplayName } from '@/utils/eventType'

interface PushChannelConfig {
  name: string
  enabled: boolean
  config: Record<string, any>
}

interface FormState {
  ruleName: string
  level: string
  algorithmId: number | null
  eventTypeId: number | null
  delayPush: boolean
  isCompliant: string | null
  unit: string
  selectedDeviceIds: number[]
  pushChannels: PushChannelConfig[]
}

interface TableItem {
  id: number
  status: boolean
  ruleName: string
  level: string
  algorithm: string
  event: string
  compliantType: string
  compliantText: string
  unit: string
  pushChannels: PushChannelConfig[]
  selectedDeviceIds: number[]
  rawAlgorithmId: number | null
  rawEventTypeId: number | null
  rawIsCompliant: string | null
  rawDelayPush: number
  rawLevel: number
}

const ALL_CHANNEL_NAMES = [
  '钉钉',
  '钉钉企业群',
  '企业微信',
  '系统提示音',
  'API接口推送',
  '摄像机控制',
  '定制推送渠道',
  'Kafka',
  'OA推送',
  '语音播报',
  '声光报警'
]

function getDefaultConfig(name: string): Record<string, any> {
  if (name === '钉钉') {
    return { appKey: '', appSecret: '', agentId: '', target: '', content: '' }
  }
  if (name === '企业微信') {
    return { corpId: '', agentId: '', secret: '', target: '', content: '' }
  }
  if (name === '系统提示音') {
    return { audioFile: '', volume: 50, loop: false }
  }
  return { webhookUrl: '', target: '', content: '' }
}

function normalizePushChannels(channels: any): PushChannelConfig[] {
  if (!Array.isArray(channels) || channels.length === 0) {
    return ALL_CHANNEL_NAMES.map(name => ({ name, enabled: false, config: getDefaultConfig(name) }))
  }
  if (typeof channels[0] === 'string') {
    const oldNames = channels as string[]
    return ALL_CHANNEL_NAMES.map(name => ({
      name,
      enabled: oldNames.includes(name),
      config: getDefaultConfig(name)
    }))
  }
  const existing = new Map((channels as PushChannelConfig[]).map(c => [c.name, c]))
  return ALL_CHANNEL_NAMES.map(name => existing.get(name) || { name, enabled: false, config: getDefaultConfig(name) })
}

const loading = ref(false)
const tableData = ref<TableItem[]>([])
const algoNameMap = ref<Map<number, string>>(new Map())
const eventNameMap = ref<Map<number, string>>(new Map())
const algorithmOptions = ref<{ id: number; name: string }[]>([])
const eventTypeOptions = ref<{ id: number; name: string }[]>([])
const deviceTreeData = ref<any[]>([])
const orgTreeData = ref<any[]>([])
const orgDialogVisible = ref(false)
const deviceTreeRef = ref<any>(null)
const orgTreeRef = ref<any>(null)
const selectedOrgNode = ref<any>(null)

function preprocessDeviceTree(nodes: any[]): any[] {
  return nodes.map(node => ({
    ...node,
    treeKey: `${node.level}-${node.id}`,
    children: node.children ? preprocessDeviceTree(node.children) : []
  }))
}

function getDeviceIdsFromTree(checkedNodes: any[]): number[] {
  return checkedNodes
    .filter(node => node.level === 'device')
    .map(node => node.id)
}

function mapLevel(level: number): string {
  if (level >= 4) return '高'
  if (level >= 3) return '中'
  return '低'
}

const isActive = (status: string): boolean => status === 'active'

function getCompliantDisplay(isCompliant: string | null): { text: string; type: string } {
  if (isCompliant === 'true') return { text: '是', type: 'success' }
  if (isCompliant === 'false') return { text: '否', type: 'danger' }
  return { text: '全部', type: 'info' }
}

function mapLinkageRuleItem(item: any): TableItem {
  const compliantDisplay = getCompliantDisplay(item.is_compliant)
  return {
    id: item.id,
    status: isActive(item.status),
    ruleName: item.rule_name || '',
    level: mapLevel(item.level),
    algorithm: algoNameMap.value.get(item.algorithm_id) || String(item.algorithm_id || ''),
    event: eventNameMap.value.get(item.event_type_id) || String(item.event_type_id || ''),
    compliantType: compliantDisplay.type,
    compliantText: compliantDisplay.text,
    unit: item.unit || '',
    pushChannels: normalizePushChannels(item.push_channels),
    selectedDeviceIds: item.selected_devices || [],
    rawAlgorithmId: item.algorithm_id,
    rawEventTypeId: item.event_type_id,
    rawIsCompliant: item.is_compliant,
    rawDelayPush: item.delay_push,
    rawLevel: item.level
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const [linkageData, algoData, eventData, deviceTree, orgTree] = await Promise.all([
      getLinkageRules(),
      getAlgorithms(),
      getEventTypes(),
      getDeviceGroupTree(),
      getOrganizationTree()
    ])

    const aList = algoData.items || algoData || []
    const aMap = new Map<number, string>()
    for (const algo of aList) {
      aMap.set(algo.id, algo.name)
    }
    algoNameMap.value = aMap
    algorithmOptions.value = aList.map((a: any) => ({ id: a.id, name: a.name }))

    const eList = eventData.items || eventData || []
    const eMap = new Map<number, string>()
    for (const ev of eList) {
      eMap.set(ev.id, ev.description || getEventTypeDisplayName(ev.name))
    }
    eventNameMap.value = eMap
    eventTypeOptions.value = eList.map((e: any) => ({ id: e.id, name: e.description || getEventTypeDisplayName(e.name) }))

    deviceTreeData.value = preprocessDeviceTree(deviceTree || [])
    orgTreeData.value = orgTree || []

    const rawRules = linkageData.items || linkageData || []
    tableData.value = rawRules.map(mapLinkageRuleItem)
  } catch {
    ElMessage.error('加载联动规则数据失败')
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

function getLevelType(level: string): string {
  switch (level) {
    case '高': return 'danger'
    case '中': return 'warning'
    case '低': return 'info'
    default: return 'info'
  }
}

const onStatusChange = async (row: TableItem) => {
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

const dialogVisible = ref(false)
const eventLimitDialogVisible = ref(false)
const dialogTitle = ref('新建联动规则')
const formRef = ref()
const editingId = ref<number | null>(null)

const defaultForm = (): FormState => ({
  ruleName: '',
  level: '',
  algorithmId: null,
  eventTypeId: null,
  delayPush: false,
  isCompliant: null,
  unit: '',
  selectedDeviceIds: [],
  pushChannels: ALL_CHANNEL_NAMES.map(name => ({ name, enabled: false, config: getDefaultConfig(name) }))
})

const form = reactive<FormState>(defaultForm())

const enabledPushChannels = computed(() => form.pushChannels.filter(ch => ch.enabled))

const rules = {
  ruleName: [{ required: true, message: '请输入联动规则名称', trigger: 'blur' }],
  level: [{ required: true, message: '请选择预警级别', trigger: 'change' }],
  pushChannels: [{ required: true, validator: (_rule: any, _value: any, callback: any) => {
    const hasEnabled = form.pushChannels.some(ch => ch.enabled)
    if (!hasEnabled) {
      callback(new Error('请选择至少一个推送渠道'))
    } else {
      callback()
    }
  }, trigger: 'change' }]
}

const openModal = (type: 'add' | 'edit', row?: TableItem) => {
  Object.assign(form, defaultForm())
  selectedOrgNode.value = null
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑联动规则'

    const algorithmId = row.rawAlgorithmId
    const eventTypeId = row.rawEventTypeId

    Object.assign(form, {
      ruleName: row.ruleName,
      level: row.level,
      algorithmId,
      eventTypeId,
      delayPush: row.rawDelayPush === 1,
      isCompliant: row.rawIsCompliant,
      unit: row.unit,
      selectedDeviceIds: [...row.selectedDeviceIds],
      pushChannels: normalizePushChannels(row.pushChannels)
    })

    // 回显设备树选中状态
    setTimeout(() => {
      if (deviceTreeRef.value) {
        const treeKeys = row.selectedDeviceIds.map((id: number) => `device-${id}`)
        deviceTreeRef.value.setCheckedKeys(treeKeys)
      }
    }, 0)
  } else {
    editingId.value = null
    dialogTitle.value = '新建联动规则'
    setTimeout(() => {
      if (deviceTreeRef.value) {
        deviceTreeRef.value.setCheckedKeys([])
      }
    }, 0)
  }
  dialogVisible.value = true
}

const onOrgNodeClick = (node: any) => {
  selectedOrgNode.value = node
}

const confirmOrgSelect = () => {
  if (selectedOrgNode.value) {
    form.unit = selectedOrgNode.value.label || selectedOrgNode.value.name || ''
  }
  orgDialogVisible.value = false
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  const levelMap: Record<string, number> = { '高': 4, '中': 3, '低': 2 }

  // 从设备树提取选中的设备ID
  let selectedDeviceIds: number[] = []
  if (deviceTreeRef.value) {
    const checkedNodes = deviceTreeRef.value.getCheckedNodes(false, false)
    selectedDeviceIds = getDeviceIdsFromTree(checkedNodes)
  }

  const payload = {
    rule_name: form.ruleName,
    level: levelMap[form.level] ?? 2,
    algorithm_id: form.algorithmId,
    event_type_id: form.eventTypeId,
    delay_push: form.delayPush ? 1 : 0,
    is_compliant: form.isCompliant,
    unit: form.unit,
    selected_devices: selectedDeviceIds,
    push_channels: form.pushChannels.map(ch => ({
      name: ch.name,
      enabled: ch.enabled,
      config: ch.config
    }))
  }

  try {
    if (editingId.value) {
      await updateLinkageRule(editingId.value, payload)
      const linkageData = await getLinkageRules()
      const rawRules = linkageData.items || linkageData || []
      tableData.value = rawRules.map(mapLinkageRuleItem)
      ElMessage.success('编辑成功')
    } else {
      const newRule = await createLinkageRule(payload)
      tableData.value.push(mapLinkageRuleItem(newRule))
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDelete = (row: TableItem) => {
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

.unit-selector {
  display: flex;
  gap: 8px;
  align-items: center;
}

.device-tree {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  max-height: 280px;
  overflow-y: auto;
}

.push-channels {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.channel-config-card {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 12px;
  margin-top: 12px;
  background: rgba(255, 255, 255, 0.02);
}

.channel-config-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #00E5FF;
}

.event-limit-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.event-limit-label {
  color: #B0C4D8;
}

:deep(.el-dialog__body) {
  padding-top: 20px;
}
</style>
