<template>
  <div class="global-header">
    <!-- 左侧：Logo + 系统名称 -->
    <div class="header-left">
      <div class="logo-area">
        <img :src="'/data/head-portrait/admin.jpg'" alt="logo" class="logo-img" />
        <span class="system-name">交通智能分析系统</span>
      </div>
    </div>

    <!-- 中间：Tab 导航 -->
    <div class="header-tabs">
      <div
        v-for="tab in tabs"
        :key="tab.path"
        :class="['tab-item', { active: activeTab === tab.path }]"
        @click="handleTabClick(tab)"
      >
        <span class="tab-icon" v-if="tab.icon">
          <component :is="tab.icon" />
        </span>
        <span class="tab-label">{{ tab.label }}</span>
        <span class="tab-badge" v-if="tab.badge">{{ tab.badge }}</span>
      </div>
    </div>

    <!-- 右侧：状态 + 用户 -->
    <div class="header-right">
      <div class="online-status">
        <span class="status-dot"></span>
        <span class="status-text">{{ onlineCount }} 在线</span>
      </div>
      <el-button text @click="toggleFullscreen">
        <el-icon :size="18"><FullScreen /></el-icon>
      </el-button>
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="28" :src="'/data/head-portrait/admin.jpg'" />
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
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowDown, FullScreen, UserFilled, SwitchButton, Monitor, DataLine, List, Setting, FolderOpened, Grid } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const onlineCount = ref(5)

interface Tab {
  label: string
  path: string
  icon?: any
  badge?: string
  children?: Tab[]
}

const tabs: Tab[] = [
  { label: '实时监控', path: '/monitor', icon: Monitor },
  { label: '数字大屏', path: '/monitor/wall', icon: Monitor },
  { label: '事件统计', path: '/event-stats', icon: DataLine },
  { label: '事件管理', path: '/event-manage', icon: List },
  { label: '布控管理', path: '/deployment', icon: Setting },
  { label: '文件分析', path: '/file-analysis', icon: FolderOpened },
  { label: '控制台', path: '/console', icon: Grid }
]

// 根据当前路由确定激活的 Tab
const activeTab = computed(() => {
  const path = route.path
  // 精确匹配 /monitor 或以 /monitor/ 开头的路径
  if (path === '/monitor' || path.startsWith('/monitor/')) {
    return path
  }
  // 检查是否是其他 Tab 的子路由
  for (const tab of tabs) {
    if (tab.path === path || path.startsWith(tab.path + '/')) {
      return tab.path
    }
  }
  // 默认选中第一个 Tab
  return tabs[0].path
})

function handleTabClick(tab: Tab) {
  router.push(tab.path)
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
.global-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 52px;
  padding: 0 20px;
  background: linear-gradient(180deg, rgba(0, 30, 60, 0.95) 0%, rgba(0, 15, 40, 0.9) 100%);
  border-bottom: 1px solid rgba(0, 229, 255, 0.15);
  position: relative;
  z-index: 1000;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.global-header::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.4), rgba(0, 255, 136, 0.3), transparent);
}

/* 左侧 Logo 区 */
.header-left {
  display: flex;
  align-items: center;
  min-width: 260px;
}

.logo-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-img {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid rgba(0, 229, 255, 0.4);
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
}

.system-name {
  font-family: 'Orbitron', 'Rajdhani', sans-serif;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 2px;
  text-transform: uppercase;
  background: linear-gradient(90deg, #00E5FF, #00FF88);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
  text-shadow: 0 0 20px rgba(0, 229, 255, 0.3);
}

/* 中间 Tab 导航 */
.header-tabs {
  display: flex;
  align-items: center;
  gap: 4px;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  cursor: pointer;
  color: rgba(180, 210, 235, 0.85);
  font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 1px;
  border-radius: 6px;
  transition: all 0.3s ease;
  position: relative;
  white-space: nowrap;
  border: 1px solid transparent;
}

.tab-item:hover {
  color: #00E5FF;
  background: rgba(0, 229, 255, 0.08);
  border-color: rgba(0, 229, 255, 0.15);
}

.tab-item.active {
  color: #00E5FF;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 229, 255, 0.05) 100%);
  border-color: rgba(0, 229, 255, 0.25);
  box-shadow: 0 0 20px rgba(0, 229, 255, 0.15), inset 0 0 15px rgba(0, 229, 255, 0.05);
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 50%;
  height: 2px;
  background: linear-gradient(90deg, #00E5FF, #00FF88);
  border-radius: 2px 2px 0 0;
  box-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.tab-icon {
  display: flex;
  align-items: center;
  font-size: 14px;
}

.tab-label {
  font-weight: 600;
}

.tab-badge {
  background: linear-gradient(135deg, #FF006E, #FF4D6D);
  color: #000;
  font-family: 'Orbitron', sans-serif;
  font-size: 9px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 16px;
  text-align: center;
  box-shadow: 0 0 8px rgba(255, 0, 110, 0.4);
}

/* 右侧状态区 */
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 220px;
  justify-content: flex-end;
}

.online-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  background: linear-gradient(135deg, rgba(0, 255, 136, 0.1) 0%, rgba(0, 255, 136, 0.05) 100%);
  border: 1px solid rgba(0, 255, 136, 0.25);
  border-radius: 16px;
  box-shadow: 0 0 15px rgba(0, 255, 136, 0.1);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #00FF88;
  box-shadow: 0 0 10px #00FF88, 0 0 20px #00FF88;
  animation: status-pulse 2s ease-in-out infinite;
}

@keyframes status-pulse {
  0%, 100% { box-shadow: 0 0 8px #00FF88, 0 0 16px #00FF88; }
  50% { box-shadow: 0 0 12px #00FF88, 0 0 24px #00FF88; }
}

.status-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 1px;
  color: #00FF88;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.08) 0%, rgba(0, 229, 255, 0.02) 100%);
}

.user-info:hover {
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.15) 0%, rgba(0, 229, 255, 0.08) 100%);
  border-color: rgba(0, 229, 255, 0.25);
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.15);
}

.username {
  font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
  color: rgba(180, 210, 235, 0.9);
  font-size: 13px;
  font-weight: 500;
}
</style>
