<template>
  <div class="operation-history">
    <!-- 操作栏 -->
    <div class="toolbar">
      <div class="left-area">
        <el-input v-model="filters.operator" placeholder="请输入操作人" style="width: 140px" clearable />
        <el-input v-model="filters.ip" placeholder="请输入IP" style="width: 140px" clearable />
        <el-select v-model="filters.method" placeholder="请求方法" style="width: 120px" clearable>
          <el-option label="GET" value="GET" />
          <el-option label="POST" value="POST" />
          <el-option label="PUT" value="PUT" />
          <el-option label="DELETE" value="DELETE" />
        </el-select>
        <el-input v-model="filters.path" placeholder="请输入路径" style="width: 160px" clearable />
        <el-button type="primary" @click="onQuery">查询</el-button>
      </div>
    </div>

    <!-- 表格 -->
    <el-table :data="pagedData" border stripe>
      <el-table-column prop="operator" label="操作人" width="110" align="center" />
      <el-table-column prop="date" label="日期" width="170" />
      <el-table-column prop="statusCode" label="状态码" width="80" align="center">
        <template #default="{ row }">
          <el-tag :type="row.statusCode === 200 ? 'success' : 'danger'" size="small">{{ row.statusCode }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ip" label="请求IP" width="140" />
      <el-table-column prop="method" label="请求方法" width="90" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.method === 'GET' ? 'primary' : row.method === 'POST' ? 'success' : row.method === 'PUT' ? 'warning' : 'danger'"
            size="small"
            effect="dark"
          >{{ row.method }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="path" label="请求路径" min-width="220" show-overflow-tooltip />
      <el-table-column prop="description" label="描述" min-width="140" show-overflow-tooltip />
      <el-table-column label="操作" width="80" fixed="right" align="center">
        <template #default="{ row }">
          <el-button class="action-detail" size="small" @click="handleDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[5, 10, 20, 50]"
        :total="filteredData.length"
        layout="total, sizes, prev, pager, next, jumper"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'

interface HistoryItem {
  operator: string
  date: string
  statusCode: number
  ip: string
  method: string
  path: string
  description: string
}

const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  operator: '',
  ip: '',
  method: '',
  path: ''
})

// 与用户管理、资源管理数据关联的操作历史
const tableData = ref<HistoryItem[]>([
  // ===== 用户管理相关操作 =====
  { operator: '系统管理员', date: '2026-05-15 08:30:12', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/users', description: '新建用户 张伟' },
  { operator: '系统管理员', date: '2026-05-15 08:35:44', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/users', description: '新建用户 王丽' },
  { operator: '系统管理员', date: '2026-05-15 08:40:18', statusCode: 200, ip: '192.168.1.1', method: 'PUT', path: '/api/users/zhangwei', description: '编辑用户 张伟 信息' },
  { operator: '系统管理员', date: '2026-05-15 09:00:05', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/users', description: '新建用户 王红' },
  { operator: '张伟', date: '2026-05-15 09:15:33', statusCode: 200, ip: '192.168.1.100', method: 'PUT', path: '/api/users/zhangwei', description: '修改个人密码' },
  { operator: '系统管理员', date: '2026-05-15 09:30:22', statusCode: 200, ip: '192.168.1.1', method: 'DELETE', path: '/api/users/wanghong', description: '删除用户 王红' },
  { operator: '系统管理员', date: '2026-05-15 09:45:10', statusCode: 200, ip: '192.168.1.1', method: 'PUT', path: '/api/users/sunlei', description: '重置用户 孙磊 密码' },
  { operator: '系统管理员', date: '2026-05-15 10:00:00', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/roles', description: '新增角色 普通用户' },
  { operator: '系统管理员', date: '2026-05-15 10:05:30', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/roles', description: '新增角色 隧道所' },
  { operator: '系统管理员', date: '2026-05-15 10:10:45', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/roles', description: '新增角色 系统管理员' },
  { operator: '系统管理员', date: '2026-05-15 10:20:18', statusCode: 200, ip: '192.168.1.1', method: 'PUT', path: '/api/roles/0723/permissions', description: '设置 普通用户 角色权限' },
  { operator: '系统管理员', date: '2026-05-15 10:25:55', statusCode: 200, ip: '192.168.1.1', method: 'DELETE', path: '/api/roles/1', description: '删除角色 隧道所' },

  // ===== 资源管理相关操作 =====
  { operator: '张伟', date: '2026-05-15 10:30:10', statusCode: 200, ip: '192.168.1.100', method: 'GET', path: '/api/resources?serviceCode=011', description: '查询固件服务资源列表' },
  { operator: '张伟', date: '2026-05-15 10:32:45', statusCode: 200, ip: '192.168.1.100', method: 'POST', path: '/api/resources', description: '新增资源 Firmware' },
  { operator: '王丽', date: '2026-05-15 10:40:22', statusCode: 200, ip: '192.168.1.101', method: 'GET', path: '/api/resources?resourceGroup=Upgrade', description: '查询升级策略资源' },
  { operator: '王丽', date: '2026-05-15 10:45:08', statusCode: 200, ip: '192.168.1.101', method: 'PUT', path: '/api/resources/upgrade-strategy-1', description: '编辑升级策略资源' },
  { operator: '孙磊', date: '2026-05-15 11:00:33', statusCode: 200, ip: '192.168.1.103', method: 'GET', path: '/api/resources?method=DELETE', description: '查询所有删除类资源' },
  { operator: '孙磊', date: '2026-05-15 11:05:19', statusCode: 200, ip: '192.168.1.103', method: 'DELETE', path: '/api/resources/device-version-3', description: '删除设备版本资源' },
  { operator: '赵明', date: '2026-05-15 11:15:42', statusCode: 200, ip: '192.168.1.102', method: 'GET', path: '/api/resources?serviceCode=007', description: '查询设备接入资源' },
  { operator: '赵明', date: '2026-05-15 11:20:55', statusCode: 403, ip: '192.168.1.102', method: 'DELETE', path: '/api/resources/firmware-1', description: '无权限删除固件资源' },
  { operator: '系统管理员', date: '2026-05-15 11:30:10', statusCode: 200, ip: '192.168.1.1', method: 'PUT', path: '/api/resources/firmware-1', description: '修改固件资源信息' },
  { operator: '系统管理员', date: '2026-05-15 11:35:00', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/resources', description: '新增 DeviceVersion 资源' },

  // ===== 菜单管理相关 =====
  { operator: '系统管理员', date: '2026-05-15 13:00:05', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/menus', description: '新增菜单 用户管理' },
  { operator: '系统管理员', date: '2026-05-15 13:10:32', statusCode: 200, ip: '192.168.1.1', method: 'PUT', path: '/api/menus/menu-manage', description: '编辑菜单 菜单管理' },
  { operator: '吴强', date: '2026-05-15 14:00:18', statusCode: 200, ip: '192.168.1.106', method: 'GET', path: '/api/resources?serviceCode=005', description: '查询算法服务资源' },
  { operator: '吴强', date: '2026-05-15 14:05:44', statusCode: 200, ip: '192.168.1.106', method: 'POST', path: '/api/resources', description: '新增算法服务资源' },
  { operator: '刘洋', date: '2026-05-15 14:15:30', statusCode: 200, ip: '192.168.1.105', method: 'GET', path: '/api/users?role=user', description: '查询普通用户列表' },
  { operator: '刘洋', date: '2026-05-15 14:20:12', statusCode: 200, ip: '192.168.1.105', method: 'PUT', path: '/api/users/wangli', description: '编辑用户 王丽 角色信息' },
  { operator: '郑霞', date: '2026-05-15 14:30:00', statusCode: 200, ip: '192.168.1.107', method: 'GET', path: '/api/resources?resourceGroup=Firmware', description: '查询固件分组资源' },
  { operator: '郑霞', date: '2026-05-15 14:35:22', statusCode: 404, ip: '192.168.1.107', method: 'GET', path: '/api/resources/nonexistent', description: '请求不存在的资源路径' },
  { operator: '系统管理员', date: '2026-05-15 15:00:00', statusCode: 200, ip: '192.168.1.1', method: 'POST', path: '/api/microservices', description: '新增微服务 交通应用' },
  { operator: '系统管理员', date: '2026-05-15 15:10:15', statusCode: 200, ip: '192.168.1.1', method: 'PUT', path: '/api/microservices/004', description: '修改微服务 交通应用→模型应用' },
  { operator: '系统管理员', date: '2026-05-15 15:15:40', statusCode: 200, ip: '192.168.1.1', method: 'DELETE', path: '/api/microservices/006', description: '删除微服务 加油站应用' },
  { operator: '王红', date: '2026-05-15 16:00:08', statusCode: 200, ip: '192.168.1.108', method: 'GET', path: '/api/users?org=西宁', description: '查询西宁分公司用户' },
  { operator: '系统管理员', date: '2026-05-15 16:30:00', statusCode: 200, ip: '192.168.1.1', method: 'PUT', path: '/api/users/admin', description: '修改管理员账户信息' },
  { operator: '系统管理员', date: '2026-05-15 17:00:00', statusCode: 200, ip: '192.168.1.1', method: 'GET', path: '/api/operation-logs', description: '查看操作历史日志' },
])

const filteredData = computed(() => {
  return tableData.value.filter(item => {
    if (filters.operator && !item.operator.includes(filters.operator)) return false
    if (filters.ip && !item.ip.includes(filters.ip)) return false
    if (filters.method && item.method !== filters.method) return false
    if (filters.path && !item.path.includes(filters.path)) return false
    return true
  })
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const onQuery = () => {
  currentPage.value = 1
}

const handleDetail = (row: HistoryItem) => {
  ElMessage.info(`${row.operator} - ${row.description}`)
}
</script>

<style scoped>
.operation-history {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.left-area {
  display: flex;
  gap: 12px;
  align-items: center;
}

.left-area .el-button {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
}

.left-area .el-button:hover {
  background: #00B4D8;
  border-color: #00B4D8;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

/* 详情按钮 */
.action-detail {
  background: rgba(0, 229, 255, 0.15) !important;
  border: 1px solid rgba(0, 229, 255, 0.4) !important;
  color: #00E5FF !important;
  border-radius: 4px;
  padding: 6px 10px !important;
  font-weight: 600;
  text-shadow: none;
  box-shadow: none;
}

.action-detail:hover {
  background: rgba(0, 229, 255, 0.25) !important;
  border-color: #00E5FF !important;
  color: #00FF88 !important;
  box-shadow: 0 0 12px rgba(0, 229, 255, 0.3);
}
</style>
