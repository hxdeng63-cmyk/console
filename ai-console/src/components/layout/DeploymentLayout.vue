<template>
  <div class="layout-container">
    <GlobalHeader class="full-header" />
    <div class="layout-body">
      <div class="layout-sidebar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          :collapse="false"
          :collapse-transition="false"
          background-color="transparent"
          text-color="rgba(180, 210, 235, 0.85)"
          active-text-color="#00E5FF"
        >
          <el-menu-item index="/deployment" @click="navigate('/deployment')">
            <span>布控管理</span>
          </el-menu-item>
          <el-menu-item index="/deployment/annotation" @click="navigate('/deployment/annotation')">
            <span>标注管理</span>
          </el-menu-item>
        </el-menu>
      </div>
      <div class="layout-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import GlobalHeader from '@/components/layout/GlobalHeader.vue'

const router = useRouter()
const route = useRoute()

const activeMenu = computed(() => route.path)

const navigate = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.layout-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  background: #020B1F;
}

.full-header {
  width: 100%;
  flex-shrink: 0;
}

.layout-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.layout-sidebar {
  width: 180px;
  background: linear-gradient(180deg, rgba(0, 30, 60, 0.6) 0%, rgba(0, 15, 40, 0.8) 100%);
  border-right: 1px solid rgba(0, 229, 255, 0.12);
  flex-shrink: 0;
  overflow-y: auto;
  backdrop-filter: blur(10px);
  position: relative;
}

.layout-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(180deg, rgba(0, 229, 255, 0.3) 0%, rgba(0, 255, 136, 0.2) 50%, rgba(0, 229, 255, 0.1) 100%);
}

.sidebar-menu {
  border: none;
  background: transparent;
  padding-top: 12px;
}

.sidebar-menu :deep(.el-menu-item) {
  height: 44px;
  line-height: 44px;
  padding-left: 20px !important;
  border-left: 3px solid transparent;
  margin: 4px 0;
  font-family: 'Rajdhani', 'Noto Sans SC', sans-serif;
  font-size: 13px;
  font-weight: 500;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.15) 0%, transparent 100%);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(0, 229, 255, 0.2) 0%, rgba(0, 229, 255, 0.05) 100%);
  border-left-color: #00E5FF;
  color: #00E5FF;
  box-shadow: inset 0 0 20px rgba(0, 229, 255, 0.1);
}

.layout-content {
  flex: 1;
  overflow-y: auto;
  background: linear-gradient(135deg, rgba(0, 20, 50, 0.4) 0%, rgba(0, 10, 30, 0.6) 100%);
  min-width: 0;
  padding: 16px;
}
</style>
