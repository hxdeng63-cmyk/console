<template>
  <div class="three-column-layout">
    <aside class="column-left" :style="{ width: leftWidth }">
      <slot name="left"></slot>
    </aside>
    <main class="column-middle">
      <slot name="middle"></slot>
    </main>
    <aside class="column-right" :style="{ width: rightWidth }">
      <slot name="right"></slot>
    </aside>
  </div>
</template>

<script setup lang="ts">
interface Props {
  leftWidth?: string
  rightWidth?: string
}

withDefaults(defineProps<Props>(), {
  leftWidth: '260px',
  rightWidth: '300px',
})
</script>

<style scoped>
.three-column-layout {
  display: flex;
  width: 100%;
  height: 100%;
  gap: 12px;
  padding: 12px;
}

.column-left,
.column-right {
  overflow: hidden;
  flex-shrink: 0;
  border-radius: 12px;
}

.column-left {
  background: linear-gradient(145deg, rgba(0, 40, 70, 0.6) 0%, rgba(0, 20, 40, 0.8) 100%);
  border: 1px solid rgba(0, 229, 255, 0.15);
  backdrop-filter: blur(16px) saturate(160%);
}

.column-right {
  background: linear-gradient(145deg, rgba(0, 50, 80, 0.5) 0%, rgba(0, 25, 50, 0.75) 100%);
  border: 1px solid rgba(0, 229, 255, 0.18);
  backdrop-filter: blur(18px) saturate(170%);
}

.column-middle {
  flex: 1;
  background: linear-gradient(145deg, rgba(0, 30, 60, 0.5) 0%, rgba(0, 15, 35, 0.7) 100%);
  border: 1px solid rgba(0, 229, 255, 0.12);
  backdrop-filter: blur(14px) saturate(150%);
  border-radius: 12px;
  overflow: hidden;
  min-width: 0;
}
</style>
