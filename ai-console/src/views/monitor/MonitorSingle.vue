<template>
  <div class="monitor-single">
    <!-- 左侧：设备列表 -->
    <div class="left-panel">
      <div class="panel-header">
        <span class="panel-title">设备列表</span>
      </div>
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="请输入关键字进行过滤"
          size="small"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="device-tree-container">
        <DeviceTree
          :data="filteredDeviceTree"
          mode="radio"
          @node-click="handleDeviceClick"
        />
      </div>
    </div>

    <!-- 中间：视频区域 -->
    <div class="center-panel">
      <!-- 视频顶部控制栏 -->
      <div class="video-controls">
        <div class="protocol-toggle">
          <el-radio-group v-model="currentProtocol" size="small">
            <el-radio-button value="flv">flv</el-radio-button>
            <el-radio-button value="hls">vlc</el-radio-button>
          </el-radio-group>
        </div>
        <div class="video-settings">
          <el-button text size="small">
            <el-icon><Setting /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 视频播放器 -->
      <div class="video-container">
        <VideoPlayer
          v-if="currentDevice"
          ref="videoPlayerRef"
          :url="currentVideoUrl"
          :protocol="currentProtocol"
          :enable-dual-protocol="true"
          :initial-osd-location="currentDevice.name"
        />
        <div v-else class="video-placeholder">
          <span>等待选择设备...</span>
        </div>

        <!-- 视频叠加信息 -->
        <div class="video-overlay-info" v-if="currentDevice">
          <div class="bandwidth-info">
            <span>{{ currentBandwidth }}</span>
          </div>
          <div class="status-info">
            <span>当前画面：正常画面</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：报警动态 -->
    <div class="right-panel">
      <div class="panel-header">
        <span class="panel-title">报警动态</span>
      </div>
      <div class="alarm-filters">
        <el-select v-model="alarmTypeFilter" size="small" placeholder="全部">
          <el-option label="全部" value="all" />
          <el-option label="不合规" value="danger" />
        </el-select>
        <el-select v-model="alarmStatusFilter" size="small" placeholder="全部">
          <el-option label="全部" value="all" />
          <el-option label="合规" value="compliant" />
          <el-option label="不合规" value="non-compliant" />
        </el-select>
      </div>
      <div class="alarm-list-container">
        <div
          v-for="alarm in filteredAlarms"
          :key="alarm.id"
          class="alarm-card"
          @click="handleAlarmClick(alarm)"
        >
          <div class="alarm-thumbnail">
            <img :src="alarm.imageUrl" :alt="alarm.type" />
            <div class="alarm-detection-box"></div>
            <div class="alarm-time">{{ alarm.captureTime }}</div>
          </div>
          <div class="alarm-info">
            <div class="alarm-location">{{ alarm.location }}</div>
            <div class="alarm-tags">
              <span class="alarm-status" :class="alarm.isCompliant ? 'compliant' : 'non-compliant'">
                {{ alarm.isCompliant ? '合规' : '不合规' }}
              </span>
            </div>
            <div class="alarm-type">{{ alarm.type }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Setting } from '@element-plus/icons-vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import DeviceTree from '@/components/device-tree/DeviceTree.vue'
import { getDevices } from '@/api/devices'
import type { DeviceNode } from '@/components/device-tree/useDeviceTree'

const searchQuery = ref('')
const currentDevice = ref<DeviceNode | null>(null)
const currentProtocol = ref<'flv' | 'hls'>('flv')
const videoPlayerRef = ref<InstanceType<typeof VideoPlayer> | null>(null)
const alarmTypeFilter = ref('all')
const alarmStatusFilter = ref('all')
const deviceTreeData = ref<DeviceNode[]>([])

onMounted(async () => {
  try {
    const data = await getDevices({ page: 1, page_size: 100 })
    const devices = data.items || []
    // Transform flat device list to tree: org -> region -> device
    const orgMap = new Map<number, Map<number, DeviceNode[]>>()
    for (const device of devices) {
      const orgId = device.org_id || 0
      const regionId = device.region_id || 0
      if (!orgMap.has(orgId)) {
        orgMap.set(orgId, new Map())
      }
      const regionMap = orgMap.get(orgId)!
      if (!regionMap.has(regionId)) {
        regionMap.set(regionId, [])
      }
      regionMap.get(regionId)!.push({
        id: String(device.id),
        name: device.name,
        type: 'camera',
        online: device.status === 'active',
        ip: device.device_code || ''
      })
    }
    const tree: DeviceNode[] = []
    for (const [orgId, regionMap] of orgMap) {
      const orgNode: DeviceNode = {
        id: `org-${orgId}`,
        name: `Organization ${orgId}`,
        type: 'org',
        online: true,
        children: []
      }
      for (const [regionId, children] of regionMap) {
        orgNode.children!.push({
          id: `group-${regionId}`,
          name: `Region ${regionId}`,
          type: 'group',
          online: true,
          children
        })
      }
      tree.push(orgNode)
    }
    deviceTreeData.value = tree
  } catch (error) {
    console.error('Failed to load devices:', error)
  }
})

const currentVideoUrl = computed(() => {
  if (!currentDevice.value) return ''
  return `ws://localhost:8080/stream/${currentDevice.value.id}`
})

const currentBandwidth = computed(() => {
  // 模拟带宽显示
  return '1560.27 kb/s'
})

const filteredDeviceTree = computed(() => {
  if (!searchQuery.value) return deviceTreeData.value
  const query = searchQuery.value.toLowerCase()

  function filterNodes(nodes: any[]): any[] {
    return nodes.reduce((acc: any[], node) => {
      const matches = node.name?.toLowerCase().includes(query)
      const children = node.children ? filterNodes(node.children) : []
      if (matches || children.length > 0) {
        acc.push({
          ...node,
          children: children.length > 0 ? children : node.children
        })
      }
      return acc
    }, [])
  }

  return filterNodes(deviceTreeData.value)
})

const filteredAlarms = computed<any[]>(() => {
  return []
})

function handleDeviceClick(node: DeviceNode) {
  if (node.type === 'camera' || node.type === 'device') {
    currentDevice.value = node
  }
}

function handleAlarmClick(alarm: any) {
  console.log('Alarm clicked:', alarm)
}
</script>

<style scoped>
.monitor-single {
  display: flex;
  height: 100%;
  background: var(--bg-primary);
}

/* 左侧面板 */
.left-panel {
  width: 280px;
  min-width: 280px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.panel-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.search-box {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.device-tree-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

/* 中间面板 */
.center-panel {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.video-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: rgba(0, 20, 40, 0.8);
  border-bottom: 1px solid var(--border-color);
}

.protocol-toggle :deep(.el-radio-button__inner) {
  background: rgba(0, 30, 60, 0.8);
  border-color: var(--border-color);
  color: var(--text-secondary);
}

.protocol-toggle :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: rgba(180, 210, 235, 0.85);
}

.video-settings {
  display: flex;
  gap: 8px;
}

.video-container {
  flex: 1;
  position: relative;
  background: #000;
  overflow: hidden;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(232, 244, 255, 0.3);
  font-size: 16px;
}

.video-overlay-info {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.6), transparent);
  pointer-events: none;
}

.bandwidth-info,
.status-info {
  font-size: 12px;
  font-family: 'Courier New', monospace;
  color: var(--tech-accent);
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.8);
}

/* 右侧面板 */
.right-panel {
  width: 300px;
  min-width: 300px;
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.alarm-filters {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color);
}

.alarm-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.alarm-card {
  background: rgba(0, 30, 60, 0.6);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  margin-bottom: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
}

.alarm-card:hover {
  border-color: var(--primary-color);
}

.alarm-thumbnail {
  position: relative;
  height: 100px;
  overflow: hidden;
}

.alarm-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.alarm-detection-box {
  position: absolute;
  top: 20%;
  left: 20%;
  width: 60%;
  height: 50%;
  border: 2px solid #FF006E;
  border-radius: 2px;
  pointer-events: none;
}

.alarm-time {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(0, 0, 0, 0.5);
  padding: 2px 6px;
  border-radius: 2px;
}

.alarm-info {
  padding: 10px;
}

.alarm-location {
  font-size: 12px;
  color: var(--text-primary);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.alarm-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 4px;
}

.alarm-status {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
}

.alarm-status.compliant {
  background: rgba(54, 214, 138, 0.2);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success);
}

.alarm-status.non-compliant {
  background: rgba(255, 77, 106, 0.2);
  color: var(--el-color-danger);
  border: 1px solid var(--el-color-danger);
}

.alarm-type {
  font-size: 11px;
  color: var(--text-secondary);
}
</style>
