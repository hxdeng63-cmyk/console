<template>
  <div class="header">
    <div class="header-left">
      <el-button text @click="$emit('toggle-sidebar')">
        <el-icon :size="20"><Menu /></el-icon>
      </el-button>
      <Breadcrumb />
    </div>
    <div class="header-right">
      <div class="online-status">
        <span class="status-dot"></span>
        <span class="status-text">1/5 在线</span>
      </div>
      <el-button text @click="openHelp">
        <el-icon :size="18"><QuestionFilled /></el-icon>
      </el-button>
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
            <el-dropdown-item command="more">
              <el-icon><Bell /></el-icon>
              更多信息
              <span class="badge-dot"></span>
            </el-dropdown-item>
            <el-dropdown-item command="profile">
              <el-icon><UserFilled /></el-icon>
              个人中心
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon>
              登出
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Menu, ArrowDown, QuestionFilled, FullScreen, Bell, UserFilled, SwitchButton } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import Breadcrumb from './Breadcrumb.vue'

defineEmits(['toggle-sidebar'])

const router = useRouter()

const openHelp = () => {
  router.push('/console/system/help-center')
}

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
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
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

.badge-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #FF006E;
  margin-left: 4px;
  vertical-align: middle;
}

</style>
