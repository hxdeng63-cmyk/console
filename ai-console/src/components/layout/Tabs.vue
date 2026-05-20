<template>
  <div class="tabs-container">
    <div class="tabs-wrapper">
      <div
        v-for="tab in tabsStore.getValidTabs()"
        :key="tab.path"
        class="tab-item"
        :class="{ active: tab.path === tabsStore.active }"
        @click="switchTab(tab.path)"
      >
        <span class="tab-dot"></span>
        <span class="tab-label">{{ tab.label }}</span>
        <el-icon
          v-if="tabsStore.getValidTabs().length > 1"
          class="tab-close"
          @click.stop="closeTab(tab.path)"
        >
          <Close />
        </el-icon>
      </div>
    </div>
    <el-dropdown trigger="click" @command="handleCommand">
      <el-button text size="small" class="more-btn">
        <el-icon><MoreFilled /></el-icon>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="close-others">关闭其他</el-dropdown-item>
          <el-dropdown-item command="close-all">关闭全部</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Close, MoreFilled } from '@element-plus/icons-vue'
import { useTabsStore } from '@/stores/tabs'

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()

const switchTab = (path: string) => {
  if (!path) return
  tabsStore.saveCurrentToHistory(tabsStore.active)
  tabsStore.setActive(path)
  router.push(path)
}

const closeTab = (path: string) => {
  tabsStore.saveCurrentToHistory(tabsStore.active)
  const result = tabsStore.removeTab(path)
  if (result && result.navigate) {
    tabsStore.setActive(result.activeTab)
    router.push(result.navigate)
  } else if (result && result.activeTab === '' && tabsStore.tabs.value.length === 0) {
    router.push('/')
  }
}

const handleCommand = (cmd: string) => {
  const tabs = tabsStore.tabs.value
  if (!tabs) return
  if (cmd === 'close-others') {
    const keep = tabs.find((t: any) => t.path === tabsStore.active)
    tabs.splice(0, tabs.length)
    if (keep) tabsStore.addTab(keep)
  } else if (cmd === 'close-all') {
    tabs.splice(0, tabs.length)
    tabsStore.active = ''
    router.push('/')
  }
}

watch(
  () => route.path,
  (path) => {
    if (tabsStore.active && tabsStore.active !== path) {
      tabsStore.saveCurrentToHistory(tabsStore.active)
    }
    const lastRecord = route.matched[route.matched.length - 1]
    const fromMeta = (lastRecord?.meta?.title || route.meta?.title) as string | undefined
    const fromPath = path.split('/').filter(Boolean).pop() || path
    const label = fromMeta || fromPath
    tabsStore.addTab({ path, label })
  },
  { immediate: true }
)
</script>

<style scoped>
.tabs-container {
  display: flex;
  align-items: stretch;
  height: 36px;
  padding: 0 8px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.tabs-wrapper {
  display: flex;
  flex: 1;
  overflow-x: auto;
  align-items: stretch;
}

.tabs-wrapper::-webkit-scrollbar {
  height: 0;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 100%;
  padding: 0 12px;
  border-radius: 0;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s, color 0.2s;
  font-size: 13px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: rgba(180, 210, 235, 0.85);
  text-shadow: 0 0 8px rgba(0, 229, 255, 0.15);
  position: relative;
}

.tab-item + .tab-item {
  border-left: 1px solid var(--border-color);
}

.tab-item:hover {
  color: rgba(180, 210, 235, 0.85);
  background: rgba(16, 40, 64, 0.6);
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
}

.tab-item.active {
  background: #102840;
  color: rgba(180, 210, 235, 0.9);
  border-bottom: 2px solid #00E5FF;
}

.tab-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #00E5FF;
  flex-shrink: 0;
}

.tab-item.active .tab-dot {
  background: #00E5FF;
}

.tab-label {
  line-height: 1;
}

.tab-close {
  font-size: 12px;
  opacity: 0;
  margin-left: 2px;
  flex-shrink: 0;
  transition: opacity 0.2s;
}

.tab-item:hover .tab-close,
.tab-item.active .tab-close {
  opacity: 0.7;
}

.tab-close:hover {
  opacity: 1 !important;
}

.more-btn {
  margin-left: 8px;
  align-self: center;
}
</style>
