<template>
  <div class="menu-manage">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-button type="primary" @click="openModal('root')">
        <el-icon><Plus /></el-icon>新增根菜单
      </el-button>
      <el-button class="toggle-btn" @click="toggleExpand">
        <el-icon><component :is="expandAll ? ArrowDown : ArrowRight" /></el-icon>
        {{ expandAll ? '折叠全部' : '展开全部' }}
      </el-button>
    </div>

    <!-- 表格 -->
    <el-table
      ref="tableRef"
      :data="tableData"
      v-loading="loading"
      row-key="id"
      :default-expand-all="true"
      border
      stripe
      class="menu-table"
    >
      <el-table-column type="index" label="ID" width="70" align="center" />
      <el-table-column prop="name" label="路由Name" min-width="160" />
      <el-table-column prop="path" label="路由Path" min-width="160" />
      <el-table-column prop="hidden" label="是否隐藏" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.hidden ? 'danger' : 'success'" size="small">
            {{ row.hidden ? '隐藏' : '显示' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="父节点" width="100" align="center">
        <template #default="{ row }">
          <el-tooltip
            v-if="row.parentId && parentTitleMap.get(row.parentId)"
            :content="parentTitleMap.get(row.parentId)"
            placement="top"
          >
            <span class="parent-id">{{ row.parentId }}</span>
          </el-tooltip>
          <span v-else class="parent-id muted">{{ row.parentId ?? 0 }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="sort" label="排序" width="80" align="center" />
      <el-table-column prop="component" label="文件路径" min-width="200" />
      <el-table-column prop="title" label="展示名称" width="130" />
      <el-table-column label="图标" width="140">
        <template #default="{ row }">
          <div class="icon-cell">
            <el-icon v-if="resolveIcon(row.icon)" class="icon-symbol">
              <component :is="resolveIcon(row.icon)" />
            </el-icon>
            <span class="icon-text">{{ row.icon || '-' }}</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="290" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" class="action-add" @click="openModal('child', row)">
            <el-icon><Plus /></el-icon>添加子菜单
          </el-button>
          <el-button class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
          <el-button class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑菜单 Modal -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="680px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="路由name" prop="name">
              <el-input v-model="form.name" placeholder="请输入路由name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="路由path" prop="path">
              <el-input v-model="form.path" placeholder="请输入路由path">
                <template #append>
                  <el-checkbox v-model="form.addParams" @change="onAddParamsChange">添加参数</el-checkbox>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="form.addParams">
          <el-col :span="24">
            <div class="params-section">
              <div class="params-title">
                <span class="required-star">*</span>参数配置
                <el-button type="primary" size="small" @click="addParam">
                  <el-icon><Plus /></el-icon>新增参数
                </el-button>
              </div>
              <el-table :data="form.params" border size="small" class="params-table">
                <el-table-column label="参数类型" width="140">
                  <template #default="{ row }">
                    <el-select v-model="row.type" placeholder="请选择">
                      <el-option label="query" value="query" />
                      <el-option label="params" value="params" />
                    </el-select>
                  </template>
                </el-table-column>
                <el-table-column label="参数key">
                  <template #default="{ row }">
                    <el-input v-model="row.key" placeholder="请输入参数key" />
                  </template>
                </el-table-column>
                <el-table-column label="参数值" width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.value" placeholder="参数值" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="60">
                  <template #default="{ $index }">
                    <el-button type="danger" size="small" @click="removeParam($index)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="是否隐藏" prop="hidden">
              <el-select v-model="form.hidden" placeholder="请选择" style="width: 100%">
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="父节点Id" prop="parentId">
              <el-select v-model="form.parentId" placeholder="请选择" style="width: 100%">
                <el-option label="根节点" :value="0" />
                <el-option
                  v-for="item in parentOptions"
                  :key="item.id"
                  :label="item.title || item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="文件路径" prop="component">
              <el-input v-model="form.component" placeholder="请输入文件路径" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="展示名称" prop="title">
              <el-input v-model="form.title" placeholder="请输入展示名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="图标" prop="icon">
              <el-select v-model="form.icon" placeholder="请选择图标" style="width: 100%" filterable>
                <el-option
                  v-for="key in iconOptionKeys"
                  :key="key"
                  :label="key"
                  :value="key"
                >
                  <span style="display: inline-flex; align-items: center; gap: 8px;">
                    <el-icon><component :is="iconMap[key]" /></el-icon>
                    {{ key }}
                  </span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序" prop="sort">
              <el-input-number v-model="form.sort" :min="0" :max="9999" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row>
          <el-col :span="12">
            <el-form-item label="keepAlive" prop="keepAlive">
              <el-select v-model="form.keepAlive" placeholder="请选择" style="width: 100%">
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="warning-text">
          <el-icon><WarningFilled /></el-icon>
          新增菜单需要在角色管理内配置权限才可使用
        </div>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, markRaw } from 'vue'
import {
  Plus,
  WarningFilled,
  ArrowDown,
  ArrowRight,
  Setting,
  User,
  UserFilled,
  Monitor,
  Connection,
  Tools,
  Box,
  Upload,
  Bell,
  Operation,
  HomeFilled,
  Document,
  Grid,
  DataLine,
  Location,
  Promotion,
  ChatLineSquare,
  QuestionFilled,
  Check,
  Cpu,
  FolderOpened,
  Menu,
  Crop,
  Key,
  OfficeBuilding,
  VideoCamera,
  Refresh,
  Folder,
  PriceTag,
  Delete,
  Coin,
  Aim,
  Files,
  Clock,
  Trophy,
  Star,
  Notebook,
  Avatar
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMenus, createMenu, updateMenu, deleteMenu } from '@/api/menus'

interface MenuItem {
  id: number
  name: string
  path: string
  hidden: boolean
  parentId: number
  sort: number
  component: string
  title: string
  icon: string
  keepAlive: boolean
  children?: MenuItem[]
  params?: Array<{ type: string; key: string; value: string }>
}

const loading = ref(false)
const tableData = ref<MenuItem[]>([])

// Element UI v2 icon name -> @element-plus/icons-vue component
const iconMap: Record<string, any> = markRaw({
  Setting,
  User,
  UserFilled,
  Monitor,
  Connection,
  Tools,
  Box,
  Upload,
  Bell,
  Operation,
  HomeFilled,
  Document,
  Grid,
  DataLine,
  Location,
  Promotion,
  Check,
  Cpu,
  Menu,
  Crop,
  Key,
  Folder,
  Delete,
  Coin,
  Files,
  Clock,
  Trophy,
  Star,
  Notebook,
  Avatar,
  // legacy aliases mapped to Element Plus icons
  'user-solid': UserFilled,
  'user': User,
  's-custom': Avatar,
  's-management': OfficeBuilding,
  's-order': Document,
  's-grid': Grid,
  's-platform': Monitor,
  's-data': DataLine,
  's-location': Location,
  's-connection': Connection,
  's-tools': Tools,
  's-claim': Operation,
  's-promotion': Promotion,
  's-comment': ChatLineSquare,
  's-question': QuestionFilled,
  's-bell': Bell,
  's-check': Check,
  's-chip': Cpu,
  's-upload': Upload,
  's-open': FolderOpened,
  'menu': Menu,
  'document': Document,
  'crop': Crop,
  'key': Key,
  'office-building': OfficeBuilding,
  'monitor': Monitor,
  'video-camera': VideoCamera,
  'refresh': Refresh,
  'setting': Setting,
  'folder': Folder,
  'price-tag': PriceTag,
  'delete': Delete,
  'cpu': Cpu,
  'coin': Coin,
  'coordinate': Aim,
  'files': Files,
  'time': Clock,
  'trophy': Trophy,
  'star-on': Star,
  'notebook-2': Notebook
})

const iconOptionKeys = computed(() =>
  Object.keys(iconMap).filter(k => /^[A-Z]/.test(k))
)

const resolveIcon = (name?: string) => {
  if (!name) return null
  return iconMap[name] || iconMap[name.toLowerCase()] || null
}

onMounted(async () => {
  loading.value = true
  try {
    const data = await getMenus()
    tableData.value = data || []
  } catch (error) {
    console.error('Failed to load menus:', error)
  } finally {
    loading.value = false
  }
})

const parentOptions = computed(() => {
  const result: MenuItem[] = []
  const collect = (items: MenuItem[]) => {
    items.forEach(item => {
      result.push(item)
      if (item.children) collect(item.children)
    })
  }
  collect(tableData.value)
  return result
})

const parentTitleMap = computed(() => {
  const map = new Map<number, string>()
  parentOptions.value.forEach(item => {
    map.set(item.id, item.title || item.name)
  })
  return map
})

const expandAll = ref(true)
const tableRef = ref()
const toggleExpand = () => {
  expandAll.value = !expandAll.value
  const next = expandAll.value
  const walk = (items: MenuItem[]) => {
    items.forEach(item => {
      if (item.children && item.children.length > 0) {
        tableRef.value?.toggleRowExpansion(item, next)
        walk(item.children)
      }
    })
  }
  walk(tableData.value)
}

const dialogVisible = ref(false)
const dialogTitle = ref('新增菜单')
const formRef = ref()

const defaultForm = () => ({
  name: '',
  path: '',
  hidden: false,
  parentId: 0,
  component: '',
  title: '',
  icon: 'Setting',
  sort: 0,
  keepAlive: false,
  addParams: false,
  params: [] as Array<{ type: string; key: string; value: string }>
})

const form = reactive(defaultForm())

const rules = {
  name: [{ required: true, message: '请输入路由name', trigger: 'blur' }],
  path: [{ required: true, message: '请输入路由path', trigger: 'blur' }],
  component: [{ required: true, message: '请输入文件路径', trigger: 'blur' }],
  title: [{ required: true, message: '请输入展示名称', trigger: 'blur' }]
}

const editingId = ref<number | null>(null)

const openModal = (type: 'root' | 'child' | 'edit', row?: MenuItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑菜单'
    Object.assign(form, {
      name: row.name,
      path: row.path,
      hidden: row.hidden,
      parentId: row.parentId,
      component: row.component,
      title: row.title,
      icon: row.icon,
      sort: row.sort,
      keepAlive: row.keepAlive,
      addParams: false,
      params: []
    })
  } else if (type === 'child' && row) {
    editingId.value = null
    dialogTitle.value = '新增子菜单'
    form.parentId = row.id
  } else {
    editingId.value = null
    dialogTitle.value = '新增根菜单'
    form.parentId = 0
  }
  dialogVisible.value = true
}

const onAddParamsChange = (val: boolean) => {
  if (val && form.params.length === 0) {
    addParam()
  }
}

const addParam = () => {
  form.params.push({ type: 'query', key: '', value: '' })
}

const removeParam = (index: number) => {
  form.params.splice(index, 1)
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  try {
    const menuData = {
      name: form.name,
      path: form.path,
      hidden: form.hidden,
      parent_id: form.parentId,
      sort: form.sort,
      component: form.component,
      title: form.title,
      icon: form.icon,
      keep_alive: form.keepAlive
    }

    if (editingId.value) {
      await updateMenu(editingId.value, menuData)
      ElMessage.success('编辑成功')
    } else {
      await createMenu(menuData)
      ElMessage.success('新增成功')
    }
    // 刷新整棵树
    const data = await getMenus()
    tableData.value = data || []
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const handleDelete = (row: MenuItem) => {
  ElMessageBox.confirm('确定删除该菜单吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteMenu(row.id)
        const data = await getMenus()
        tableData.value = data || []
        ElMessage.success('删除成功')
      } catch (error: any) {
        ElMessage.error(error.message || '删除失败')
      }
    })
    .catch(() => {})
}
</script>

<style scoped>
.menu-manage {
  padding: 0;
  height: 100%;
  background: #020B1F;
}

.toolbar {
  margin-bottom: 16px;
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar .el-button {
  background: linear-gradient(135deg, #00E5FF 0%, #00B4D8 100%);
  border: none;
  color: #000;
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 1px;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.35), 0 4px 15px rgba(0, 0, 0, 0.3);
}

.toolbar .el-button:hover {
  box-shadow: 0 0 30px rgba(0, 229, 255, 0.5), 0 6px 20px rgba(0, 0, 0, 0.4);
  transform: translateY(-1px);
}

.toolbar .toggle-btn {
  background: rgba(0, 40, 80, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.35);
  color: #00E5FF;
  box-shadow: none;
}

.toolbar .toggle-btn:hover {
  background: rgba(0, 229, 255, 0.15);
  border-color: #00E5FF;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.25);
}

/* 表格容器 */
.menu-manage :deep(.el-table) {
  margin: 0 20px;
  border-radius: 12px;
  overflow: hidden;
}

/* 表头：去掉过度发光 */
.menu-manage :deep(.el-table th.el-table__cell) {
  background: rgba(0, 25, 55, 0.85) !important;
}

.menu-manage :deep(.el-table th.el-table__cell .cell) {
  color: rgba(255, 255, 255, 0.88) !important;
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 0.4px;
  text-shadow: none !important;
}

/* 图标列单元格 */
.icon-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.85);
}

.icon-symbol {
  color: #00E5FF;
  font-size: 16px;
}

.icon-text {
  font-family: 'JetBrains Mono', 'Source Code Pro', monospace;
  font-size: 12px;
  color: rgba(180, 210, 235, 0.85);
}

/* 父节点ID 单元格 */
.parent-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 12px;
  color: #00E5FF;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(0, 229, 255, 0.08);
  border: 1px solid rgba(0, 229, 255, 0.2);
}

.parent-id.muted {
  color: rgba(180, 210, 235, 0.5);
  background: rgba(255, 255, 255, 0.03);
  border-color: rgba(255, 255, 255, 0.08);
}

/* 操作按钮 - 添加子菜单（蓝色实心） */
.action-add {
  padding: 6px 10px !important;
}

/* 操作按钮 - 编辑（青色） */
.action-edit {
  background: rgba(0, 229, 255, 0.15) !important;
  border: 1px solid rgba(0, 229, 255, 0.4) !important;
  color: #00E5FF !important;
  border-radius: 4px;
  padding: 6px 10px !important;
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
  padding: 6px 10px !important;
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

/* 参数区域 */
.params-section {
  background: linear-gradient(135deg, rgba(0, 30, 60, 0.5) 0%, rgba(0, 15, 40, 0.7) 100%);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 8px;
  padding: 16px;
}

.params-title {
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.required-star {
  color: #FF006E;
  font-size: 16px;
  font-weight: bold;
}

.params-table {
  margin-top: 0;
}

.params-table :deep(.el-table) {
  border-radius: 6px;
}

/* 警告文字 */
.warning-text {
  margin-top: 16px;
  padding: 12px 16px;
  background: linear-gradient(135deg, rgba(255, 0, 110, 0.1) 0%, rgba(255, 0, 110, 0.05) 100%);
  border: 1px solid rgba(255, 0, 110, 0.25);
  border-radius: 8px;
  color: #FF006E;
  font-family: 'Rajdhani', sans-serif;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
  text-shadow: 0 0 8px rgba(255, 0, 110, 0.3);
}

/* 弹窗按钮 */
.menu-manage :deep(.el-dialog__footer .el-button) {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  letter-spacing: 1px;
}

.menu-manage :deep(.el-dialog__footer .el-button:not(.el-button--primary)) {
  background: rgba(0, 30, 60, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.3);
  color: #00E5FF;
}

.menu-manage :deep(.el-dialog__footer .el-button:not(.el-button--primary):hover) {
  background: rgba(0, 229, 255, 0.15);
  border-color: #00E5FF;
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
}

.menu-manage :deep(.el-dialog__footer .el-button--primary) {
  background: linear-gradient(135deg, #00E5FF 0%, #00B4D8 100%);
  border: none;
  color: #000;
  font-weight: 600;
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.35);
}

.menu-manage :deep(.el-dialog__footer .el-button--primary:hover) {
  box-shadow: 0 0 30px rgba(0, 229, 255, 0.5);
}
</style>
