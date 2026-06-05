<template>
  <div class="menu-panel">
    <GlobalHeader />
    <div class="panel-content">
      <router-view class="router-view-content" />
    </div>
  </div>
</template>

<script setup lang="ts">
import GlobalHeader from '@/components/layout/GlobalHeader.vue'
</script>

<style scoped>
.menu-panel {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  overflow: hidden;
}

.panel-content {
  flex: 1;
  overflow: hidden;
  position: relative;
  display: flex;
}

.router-view-content {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
}
</style>
