<template>
  <div class="layout-container">
    <Sidebar :collapsed="sidebarCollapsed" />
    <div class="layout-main" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <Header @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <Tabs />
      <div class="content-wrapper">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Sidebar from './Sidebar.vue'
import Header from './Header.vue'
import Tabs from './Tabs.vue'

const sidebarCollapsed = ref(false)
</script>

<style scoped>
.layout-container {
  display: flex;
  width: 100%;
  height: 100vh;
  background: var(--bg-primary);
}

.layout-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 200px;
  transition: margin-left 0.3s;
  overflow: hidden;
  min-width: 0;
}

.layout-main.sidebar-collapsed {
  margin-left: 64px;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  background: var(--bg-primary);
}
</style>
