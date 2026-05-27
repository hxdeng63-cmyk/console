<template>
  <div class="ui-customize">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="search-area">
        <el-button type="primary" @click="openModal('add')">
          <el-icon><Plus /></el-icon>新增
        </el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe>
      <el-table-column prop="platform" label="平台名称" min-width="200" />
      <el-table-column prop="id" label="ID" width="300" show-overflow-tooltip />
      <el-table-column prop="menu" label="菜单" min-width="300" show-overflow-tooltip />
      <el-table-column prop="theme" label="主题" width="100" align="center">
        <template #default="{ row }">
          <span>{{ row.theme }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button class="action-edit" size="small" @click="openModal('edit', row)">编辑</el-button>
          <el-button class="action-delete" size="small" @click="handleDelete(row)">删除</el-button>
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

    <!-- 新增/编辑 Modal -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="平台名称" prop="platform">
          <el-input v-model="form.platform" placeholder="请输入平台名称" />
        </el-form-item>

        <el-form-item label="平台商标" prop="logo">
          <el-select v-model="form.logo" placeholder="请选择平台商标" style="width: 60%">
            <el-option label="交通智能分析" value="traffic" />
            <el-option label="通用平台" value="generic" />
            <el-option label="监控平台" value="monitor" />
          </el-select>
          <el-button type="primary" style="margin-left: 12px">上传商标</el-button>
        </el-form-item>

        <el-form-item label="展示模块" prop="modules">
          <div class="modules-grid">
            <el-checkbox-group v-model="form.modules">
              <el-checkbox value="实时监控flv/vlc">实时监控flv/vlc</el-checkbox>
              <el-checkbox value="实时监控图片流">实时监控图片流</el-checkbox>
              <el-checkbox value="实时监控hls">实时监控hls</el-checkbox>
              <el-checkbox value="实时监控HK1.5+">实时监控HK1.5+</el-checkbox>
              <el-checkbox value="实时监控HK1.3">实时监控HK1.3</el-checkbox>
              <el-checkbox value="实时监控交通flv">实时监控交通flv</el-checkbox>
              <el-checkbox value="实时监控交通vlc">实时监控交通vlc</el-checkbox>
              <el-checkbox value="事件统计">事件统计</el-checkbox>
              <el-checkbox value="事件管理">事件管理</el-checkbox>
              <el-checkbox value="布控管理">布控管理</el-checkbox>
              <el-checkbox value="人脸管理">人脸管理</el-checkbox>
              <el-checkbox value="文件分析">文件分析</el-checkbox>
              <el-checkbox value="控制台">控制台</el-checkbox>
            </el-checkbox-group>
          </div>
        </el-form-item>

        <el-form-item label="主题" prop="theme">
          <el-radio-group v-model="form.theme">
            <el-radio value="黑色">黑色</el-radio>
            <el-radio value="白色">白色</el-radio>
          </el-radio-group>
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
import { ref, computed, reactive, onMounted } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getUIThemes,
  createUITheme,
  updateUITheme,
  deleteUITheme
} from '@/api/ui-themes'

interface PlatformItem {
  id: string
  platform: string
  logo: string
  modules: string[]
  menu: string
  theme: string
  is_active?: boolean
  raw?: any
}

const tableData = ref<PlatformItem[]>([])
const loading = ref(false)

const currentPage = ref(1)
const pageSize = ref(10)

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增')
const formRef = ref()
const editingId = ref<string | null>(null)

const defaultForm = () => ({
  platform: '',
  logo: '',
  modules: [] as string[],
  theme: '黑色'
})

const form = reactive(defaultForm())

const rules = {
  platform: [{ required: true, message: '请输入平台名称', trigger: 'blur' }],
  logo: [{ required: true, message: '请选择平台商标', trigger: 'change' }],
  modules: [{ required: true, message: '请选择展示模块', trigger: 'change' }],
  theme: [{ required: true, message: '请选择主题', trigger: 'change' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await getUIThemes({ pageNo: 1, pageSize: 100 })
    const items = res.items || res.list || []
    tableData.value = items.map((item: any) => ({
      id: String(item.id),
      platform: item.name,
      logo: extractLogoKey(item.logo_url),
      modules: [],
      menu: `${item.platform || 'web'} | ${item.is_active ? '已激活' : '未激活'}`,
      theme: item.theme_color === '#303133' || item.theme_color === '#000000' ? '黑色' : '白色',
      is_active: item.is_active,
      raw: item
    }))
  } catch (error) {
    console.error('加载 UI 主题失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const extractLogoKey = (url?: string) => {
  if (!url) return ''
  const m = url.match(/logo-(.+)\.png/)
  return m ? m[1] : ''
}

const buildLogoUrl = (key: string) => `/logo-${key}.png`

const openModal = (type: 'add' | 'edit', row?: PlatformItem) => {
  Object.assign(form, defaultForm())
  if (type === 'edit' && row) {
    editingId.value = row.id
    dialogTitle.value = '编辑'
    Object.assign(form, {
      platform: row.platform,
      logo: row.logo,
      modules: [...row.modules],
      theme: row.theme
    })
  } else {
    editingId.value = null
    dialogTitle.value = '新增'
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await (formRef.value as any).validate().catch(() => false)
  if (!valid) return

  const payload = {
    name: form.platform,
    platform: 'web',
    theme_color: form.theme === '黑色' ? '#303133' : '#FFFFFF',
    logo_url: buildLogoUrl(form.logo),
    is_active: false
  }

  try {
    if (editingId.value) {
      const row = tableData.value.find(item => item.id === editingId.value)
      await updateUITheme(Number(editingId.value), { ...payload, is_active: row?.is_active ?? false })
      ElMessage.success('编辑成功')
    } else {
      await createUITheme(payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    await loadData()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

const handleDelete = (row: PlatformItem) => {
  ElMessageBox.confirm('确定删除该平台配置吗？', '提示', { type: 'warning' })
    .then(async () => {
      try {
        await deleteUITheme(Number(row.id))
        ElMessage.success('删除成功')
        await loadData()
      } catch (error) {
        console.error('删除失败:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

onMounted(loadData)
</script>

<style scoped>
.ui-customize {
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

.modules-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 4px;
}
</style>
