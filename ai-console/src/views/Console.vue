<template>
  <div class="console-wrapper">
    <Sidebar :collapsed="sidebarCollapsed" />
    <div class="console-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="console-header">
        <div class="header-left">
          <el-button text @click="sidebarCollapsed = !sidebarCollapsed">
            <el-icon :size="20"><Menu /></el-icon>
          </el-button>
          <Breadcrumb />
        </div>
        <div class="header-right">
          <div class="online-status">
            <span class="status-dot"></span>
            <span class="status-text">1/5 在线</span>
          </div>
          <el-button text @click="toggleFullscreen">
            <el-icon :size="18"><FullScreen /></el-icon>
          </el-button>
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" src="/admin.jpg" />
              <span class="username">admin</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><UserFilled /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="logout" divided>
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      <Tabs />
      <div class="console-tabs">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, ArrowDown, FullScreen, UserFilled, SwitchButton } from '@element-plus/icons-vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Breadcrumb from '@/components/layout/Breadcrumb.vue'
import Tabs from '@/components/layout/Tabs.vue'

const router = useRouter()
const sidebarCollapsed = ref(false)

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const handleCommand = (cmd: string) => {
  if (cmd === 'profile') {
    router.push('/console/profile')
  } else if (cmd === 'logout') {
    router.push('/login')
  }
}
</script>

<style scoped>
.console-wrapper {
  display: flex;
  width: 100%;
  height: 100vh;
  background: var(--bg-primary);
}

.console-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 200px;
  transition: margin-left 0.3s;
  overflow: hidden;
  min-width: 0;
}

.console-main.sidebar-collapsed {
  margin-left: 64px;
}

.console-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px 8px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.online-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00E5FF;
}

.status-text {
  color: var(--text-secondary);
  font-size: 13px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.user-info:hover {
  background: var(--el-menu-hover-bg-color);
}

.username {
  color: var(--text-primary);
  font-size: 14px;
}

.console-tabs {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-primary);
}

</style>
