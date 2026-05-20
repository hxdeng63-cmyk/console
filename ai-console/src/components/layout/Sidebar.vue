<template>
  <div class="sidebar" :class="{ collapsed }">
    <div class="sidebar-header">
      <div class="logo">
        <span v-if="!collapsed">AI Console</span>
        <span v-else class="logo-icon">AI</span>
      </div>
      <el-button text class="home-btn" @click="goHome" title="返回主页">
        <el-icon :size="18"><HomeFilled /></el-icon>
      </el-button>
    </div>

    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      :collapse="collapsed"
      :collapse-transition="false"
      background-color="var(--bg-primary)"
      text-color="var(--el-menu-item-text-color)"
    >
      <!-- 有子菜单的模块 -->
      <el-sub-menu v-for="module in modulesWithChildren" :key="module.name" :index="module.name">
        <template #title>
          <el-icon><component :is="module.icon" /></el-icon>
          <span>{{ module.label }}</span>
        </template>
        <template v-if="module.children && module.children.length > 0">
          <template v-for="item in module.children" :key="item.path || item.name">
            <!-- 二级菜单（带三级子菜单） -->
            <el-sub-menu v-if="item.children && item.children.length > 0" :index="item.name || item.path">
              <template #title>{{ item.label }}</template>
              <el-menu-item
                v-for="child in item.children"
                :key="child.path"
                :index="child.path"
                @click="navigate(child.path)"
              >
                {{ child.label }}
              </el-menu-item>
            </el-sub-menu>
            <!-- 二级菜单（无子菜单） -->
            <el-menu-item v-else-if="item.path" :index="item.path" @click="navigate(item.path)">
              {{ item.label }}
            </el-menu-item>
          </template>
        </template>
      </el-sub-menu>
      <!-- 无子菜单的顶级模块（如 data-clean） -->
      <el-menu-item
        v-for="module in modulesWithoutChildren"
        :key="module.name"
        :index="module.path"
        @click="navigate(module.path)"
      >
        <el-icon><component :is="module.icon" /></el-icon>
        <span>{{ module.label }}</span>
      </el-menu-item>
    </el-menu>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  Setting,
  User,
  Monitor,
  Connection,
  Tools,
  Box,
  Upload,
  Bell,
  Operation,
  HomeFilled
} from '@element-plus/icons-vue'

defineProps<{ collapsed: boolean }>()

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

const modulesWithChildren = computed(() => modules.filter(m => m.children && m.children.length > 0))
const modulesWithoutChildren = computed(() =>
  modules
    .filter(m => !m.children || m.children.length === 0)
    .map(m => ({
      name: m.name,
      label: m.label,
      icon: m.icon,
      path: (m as any).path || ''
    }))
)

const modules = [
  {
    name: 'super-admin',
    label: '超级管理员',
    icon: Setting,
    children: [
      { label: '菜单管理', path: '/console/super-admin/menu-manage' },
      { label: '资源管理', path: '/console/super-admin/resource-manage' },
      { label: '微服务', path: '/console/super-admin/microservice' },
      { label: 'UI定制', path: '/console/super-admin/ui-customize' },
      { label: '授权文件', path: '/console/super-admin/license-file' }
    ]
  },
  {
    name: 'user-center',
    label: '用户中心',
    icon: User,
    children: [
      { label: '用户管理', path: '/console/user-center/user-manage' },
      { label: '组织管理', path: '/console/user-center/org-manage' },
      { label: '角色管理', path: '/console/user-center/role-manage' },
      { label: '操作历史', path: '/console/user-center/operation-history' }
    ]
  },
  {
    name: 'device',
    label: '设备管理',
    icon: Monitor,
    children: [
      { label: '数据源', path: '/console/device/data-source' },
      { label: '设备组管理', path: '/console/device/device-group' },
      { label: '区域', path: '/console/device/region' },
      {
        name: 'device-access',
        label: '设备接入管理',
        children: [
          { label: '平台列表', path: '/console/device/device-access/platform-list' },
          { label: 'GB28181', path: '/console/device/device-access/gb28181' },
          { label: 'ONVIF', path: '/console/device/device-access/onvif' }
        ]
      }
    ]
  },
  {
    name: 'linkage',
    label: '智能联动',
    icon: Connection,
    children: [
      { label: '发送通知', path: '/console/linkage/send-notify' },
      { label: '联动规则', path: '/console/linkage/linkage-rule' },
      { label: '推送历史', path: '/console/linkage/push-history' }
    ]
  },
  {
    name: 'system',
    label: '系统设置',
    icon: Tools,
    children: [
      { label: '录像设置', path: '/console/system/video-setting' },
      { label: '文件管理', path: '/console/system/file-manager' },
      { label: '帮助中心', path: '/console/system/help-center' },
      { label: '弹窗设置', path: '/console/system/popup-setting' },
      { label: '处置标签管理', path: '/console/system/dispose-tag' }
    ]
  },
  {
    name: 'data-clean',
    label: '数据清理',
    icon: Operation,
    path: '/console/data-clean',
    children: []
  },
  {
    name: 'algorithm',
    label: '算法管理',
    icon: Box,
    children: [
      { label: '算法管理', path: '/console/algorithm/algorithm-manage' }
    ]
  },
  {
    name: 'firmware',
    label: '固件中心',
    icon: Upload,
    children: [{ label: '固件中心', path: '/console/firmware' }]
  },
  {
    name: 'events',
    label: '预警事件',
    icon: Bell,
    children: [{ label: '预警事件', path: '/console/events' }]
  }
]

const navigate = (path: string) => {
  router.push(path)
}

const goHome = () => {
  router.push('/monitor/single')
}
</script>

<style scoped>
.sidebar {
  position: fixed;
  left: 0;
  top: 0;
  width: 200px;
  height: 100vh;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  z-index: 100;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 12px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  font-size: 16px;
  font-weight: bold;
  color: var(--primary-color);
  white-space: nowrap;
}

.logo-icon {
  font-size: 14px;
}

.home-btn {
  padding: 4px;
  color: #00E5FF;
}

.home-btn:hover {
  background: rgba(0, 229, 255, 0.1) !important;
}

.home-icon {
  font-size: 18px;
  line-height: 1;
  filter: grayscale(0.3);
  transition: filter 0.2s;
}

.home-btn:hover .home-icon {
  filter: grayscale(0) drop-shadow(0 0 6px rgba(0, 229, 255, 0.5));
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  border-right: none;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 200px;
}

.sidebar-menu :deep(.el-menu-item) {
  color: rgba(180, 210, 235, 0.8) !important;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  color: #00E5FF !important;
  background: rgba(0, 229, 255, 0.1) !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: rgba(0, 229, 255, 0.15) !important;
  border-left: 3px solid #00E5FF;
  padding-left: calc(var(--el-menu-icon-width) + 20px - 3px);
  color: #00E5FF !important;
}
</style>
