<template>
  <el-breadcrumb separator="/">
    <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path">
      <span>{{ item.label }}</span>
    </el-breadcrumb-item>
  </el-breadcrumb>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const moduleLabelMap: Record<string, string> = {
  'super-admin': '超级管理员',
  'user-center': '用户中心',
  'device': '设备管理',
  'linkage': '智能联动',
  'system': '系统设置',
  'data-clean': '数据清理',
  'algorithm': '算法管理',
  'firmware': '固件中心',
  'events': '预警事件'
}

const intermediateMap: Record<string, string> = {
  'device-access': '设备接入管理'
}

const breadcrumbs = computed(() => {
  const pathParts = route.path.split('/').filter(Boolean)
  // pathParts[0] = 'console'
  // pathParts[1] = module key (e.g. 'super-admin')
  // pathParts[2] = sub-group or leaf (e.g. 'device-access' or 'menu-manage')
  // pathParts[3] = leaf (e.g. 'platform-list') — only for 3-level menus

  const items: Array<{ path: string; label: string; isLast: boolean }> = []

  // Level 1: parent module
  const parentKey = pathParts.length >= 2 ? pathParts[1] : ''
  const parentLabel = moduleLabelMap[parentKey] || ''
  if (parentLabel) {
    items.push({ path: '/console/' + parentKey, label: parentLabel, isLast: false })
  }

  // Level 2 (intermediate): only when there are 4 segments and a known intermediate key
  if (pathParts.length >= 4) {
    const intermediateKey = pathParts[2]
    const intermediateLabel = intermediateMap[intermediateKey]
    if (intermediateLabel) {
      items.push({
        path: '/console/' + parentKey + '/' + intermediateKey,
        label: intermediateLabel,
        isLast: false
      })
    }
  }

  // Last: current page
  const lastRecord = route.matched[route.matched.length - 1]
  const currentLabel = (lastRecord?.meta?.title as string) || pathParts[pathParts.length - 1]
  const currentPath = route.path
  // Avoid duplicate breadcrumb when parent path equals current path (e.g. /console/firmware)
  const parentPath = items.length > 0 ? items[items.length - 1].path : ''
  if (currentPath !== parentPath) {
    items.push({ path: currentPath, label: currentLabel, isLast: true })
  } else if (items.length > 0) {
    items[items.length - 1].isLast = true
  }

  return items
})
</script>

<style scoped>
:deep(.el-breadcrumb__inner) {
  color: var(--text-secondary);
  cursor: default;
}

:deep(.el-breadcrumb__separator) {
  color: var(--text-secondary);
}
</style>
