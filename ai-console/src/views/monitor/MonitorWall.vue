<template>
  <div class="monitor-wall">
    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧视频区域 -->
      <div class="video-area">
        <div class="video-wrapper">
          <!-- 视频播放器 -->
          <div class="video-container">
            <VideoPlayer
              v-if="currentDevice"
              :url="currentVideoUrl"
              protocol="flv"
              :initial-osd-location="currentDevice.name"
            />
            <div v-else class="video-placeholder">
              <span>等待选择设备...</span>
            </div>

            <!-- 视频装饰角 -->
            <div class="video-corner top-left"></div>
            <div class="video-corner top-right"></div>
            <div class="video-corner bottom-left"></div>
            <div class="video-corner bottom-right"></div>
          </div>

          <!-- 视频底部装饰 -->
          <div class="video-footer">
            <div class="footer-line"></div>
          </div>
        </div>
      </div>

      <!-- 右侧数据面板 -->
      <div class="right-panel">
        <!-- 预览通道 -->
        <div class="panel-section channel-section">
          <div class="section-header">
            <span class="section-title">预览通道</span>
          </div>
          <div class="channel-content">
            <el-select v-model="selectedChannel" placeholder="选择通道" class="channel-select">
              <el-option
                v-for="ch in channels"
                :key="ch.id"
                :label="ch.name"
                :value="ch.id"
              />
            </el-select>
            <el-button class="draw-btn">
              <el-icon><Edit /></el-icon>
              绘制区域
            </el-button>
          </div>
        </div>

        <!-- 实时交通参数 -->
        <div class="panel-section traffic-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">实时交通参数</span>
            <span class="header-line"></span>
          </div>
          <div class="traffic-grid">
            <div class="traffic-item">
              <div class="traffic-value primary">{{ statsData.avgSpeed }}</div>
              <div class="traffic-label">平均速度 (km/h)</div>
            </div>
            <div class="traffic-item">
              <div class="traffic-value">{{ statsData.upTraffic }}</div>
              <div class="traffic-label">上行车流量</div>
            </div>
            <div class="traffic-item">
              <div class="traffic-value">{{ statsData.downTraffic }}</div>
              <div class="traffic-label">下行车流量</div>
            </div>
          </div>
        </div>

        <!-- 交通事件统计 -->
        <div class="panel-section events-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">交通事件统计</span>
            <span class="header-line"></span>
          </div>
          <div class="donut-chart-area">
            <div class="donut-chart">
              <div class="donut-circle" :style="donutStyle"></div>
              <div class="donut-center">
                <span class="donut-total">{{ eventStats.total }}</span>
                <span class="donut-label">交通事件</span>
              </div>
            </div>
            <div class="donut-legend">
              <div class="legend-item" v-for="item in eventStats.legend" :key="item.name">
                <span class="legend-dot" :style="{ background: item.color }"></span>
                <span class="legend-name">{{ item.name }}</span>
                <span class="legend-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 等级指标 -->
        <div class="panel-section level-section">
          <div class="level-item">
            <div class="level-header">
              <span class="level-label">道理通行等级</span>
            </div>
            <div class="level-bar">
              <div class="level-gradient"></div>
              <div class="level-marker" :style="{ left: roadLevelPosition }"></div>
            </div>
            <div class="level-scale">
              <span>1</span>
              <span>2</span>
              <span>3</span>
              <span>4</span>
              <span>5</span>
            </div>
            <div class="level-status" :class="'level-' + statsData.roadLevel">{{ statsData.roadLevelText }}</div>
          </div>
          <div class="level-item">
            <div class="level-header">
              <span class="level-label">能见度等级</span>
            </div>
            <div class="level-bar">
              <div class="level-gradient visibility"></div>
              <div class="level-marker" :style="{ left: visibilityPosition }"></div>
            </div>
            <div class="level-scale">
              <span>0</span>
              <span>2</span>
              <span>4</span>
              <span>6</span>
              <span>8</span>
              <span>10</span>
            </div>
          </div>
        </div>

        <!-- 布控信息 -->
        <div class="panel-section deployment-section">
          <div class="section-header">
            <span class="header-bar"></span>
            <span class="section-title">布控信息</span>
            <span class="header-line"></span>
          </div>
          <el-table :data="deploymentData" size="small" class="deployment-table" border>
            <el-table-column prop="name" label="布控方案名称" min-width="130" show-overflow-tooltip />
            <el-table-column prop="algorithm" label="算法名称" width="95" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="70" align="center">
              <template #default="{ row }">
                <span class="status-tag" :class="row.statusClass">{{ row.status }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 视频质量检测 -->
        <div class="panel-section quality-section">
          <span class="quality-label">视频质量检测</span>
          <span class="status-tag online">在线</span>
        </div>
      </div>
    </div>

    <!-- 底部实时事件抓拍 -->
    <div class="bottom-events">
      <div class="events-header">
        <span class="events-title">实时事件抓拍</span>
      </div>
      <div class="events-carousel">
        <div
          v-for="event in filteredEvents"
          :key="event.id"
          class="event-card"
        >
          <div class="event-thumb">
            <img :src="event.imageUrl" :alt="event.type" />
            <div class="event-detection-box"></div>
          </div>
          <div class="event-label">
            <span class="event-type">{{ event.type }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部信息栏 -->
    <div class="bottom-info">
      <div class="info-left">
        <div class="info-item">
          <span class="info-label">布控信息：</span>
          <span class="info-value">{{ deploymentInfo }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">视频质量检测：</span>
          <span class="info-value quality-ok">正常</span>
        </div>
      </div>
      <el-radio-group v-model="eventFilter" size="small">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="danger">不合规</el-radio-button>
      </el-radio-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Edit } from '@element-plus/icons-vue'
import VideoPlayer from '@/components/video/VideoPlayer.vue'
import { getDevices } from '@/api/devices'
import { getList as getWarningEvents } from '@/api/warning-events'
import type { DeviceNode } from '@/components/device-tree/useDeviceTree'

const selectedChannel = ref('device-4')
const eventFilter = ref('all')
const deploymentInfo = computed(() => {
  const totalDevices = deviceTreeData.value.reduce((sum, org) => {
    return sum + (org.children?.reduce((s, group) => s + (group.children?.length || 0), 0) || 0)
  }, 0)
  const firstOrg = deviceTreeData.value[0]
  return firstOrg ? `${firstOrg.name}(${totalDevices}路)` : '暂无设备'
})

const deviceTreeData = ref<DeviceNode[]>([])
const alarmList = ref<any[]>([])

const fetchDeviceTree = async () => {
  try {
    const res: any = await getDevices({ page: 1, page_size: 100 })
    const devices = res.items || []
    const grouped: Record<string, Record<string, any[]>> = {}
    devices.forEach((d: any) => {
      const org = d.org_name || d.org || '未知组织'
      const region = d.region_name || d.region || '未知区域'
      if (!grouped[org]) grouped[org] = {}
      if (!grouped[org][region]) grouped[org][region] = []
      grouped[org][region].push({
        id: `device-${d.id}`,
        name: d.name,
        type: 'camera' as const,
        online: d.status === 'active',
        ip: ''
      })
    })

    deviceTreeData.value = Object.entries(grouped).map(([orgName, regions]) => ({
      id: `org-${orgName}`,
      name: orgName,
      type: 'org' as const,
      online: true,
      children: Object.entries(regions).map(([regionName, cameras]) => ({
        id: `group-${regionName}`,
        name: regionName,
        type: 'group' as const,
        online: true,
        children: cameras
      }))
    }))
  } catch {
    console.error('获取设备列表失败')
  }
}

const fetchAlarms = async () => {
  try {
    const res: any = await getWarningEvents({ page: 1, page_size: 50 })
    const items = res.items || []
    alarmList.value = items.map((item: any) => ({
      id: item.id,
      time: item.time || item.captureTime?.split(' ')[1] || '00:00:00',
      type: item.type || '未知',
      device: item.device || '',
      location: item.location || '',
      level: item.level || 'info',
      handled: item.handled ?? false,
      isCompliant: item.isCompliant ?? true,
      imageUrl: item.imageUrl || '',
      captureTime: item.captureTime || ''
    }))
  } catch (error) {
    console.error('Failed to load alarms:', error)
    alarmList.value = []
  }
}

onMounted(() => {
  fetchDeviceTree()
  fetchAlarms()
})

// 通道列表
const channels = computed(() => {
  const result: any[] = []
  deviceTreeData.value.forEach(org => {
    if (org.children) {
      org.children.forEach(group => {
        if (group.children) {
          group.children.forEach(device => {
            result.push({
              id: device.id,
              name: `${org.name} ${device.name}`
            })
          })
        }
      })
    }
  })
  return result
})

// 当前选中的设备
const currentDevice = computed(() => {
  return channels.value.find(ch => ch.id === selectedChannel.value)
})

// 视频URL
const currentVideoUrl = computed(() => {
  if (!currentDevice.value) return ''
  return `ws://localhost:8080/stream/${currentDevice.value.id}`
})

// 统计数据
const statsData = ref({
  avgSpeed: '--',
  upTraffic: '--',
  downTraffic: '--',
  roadLevel: 1,
  roadLevelText: '畅通'
})

// 事件统计
const eventStats = computed(() => {
  const total = alarmList.value.length * 10 || 1
  const legend = [
    { name: '行人闯入', value: 64, color: '#00FFCC' },
    { name: '异常停车', value: 32, color: '#0099FF' },
    { name: '作业人员', value: 28, color: '#00EAFF' },
    { name: '非机动车驶入', value: 19, color: '#FF9900' }
  ]
  return { total, legend }
})

// 饼图样式
const donutStyle = computed(() => {
  const legend = eventStats.value.legend
  let gradient = ''
  let currentPercent = 0
  legend.forEach((item, index) => {
    const percent = (item.value / eventStats.value.total) * 100
    gradient += `${item.color} ${currentPercent}% ${currentPercent + percent}%`
    if (index < legend.length - 1) gradient += ', '
    currentPercent += percent
  })
  return {
    background: `conic-gradient(${gradient})`
  }
})

// 能见度
const visibilityPosition = computed(() => {
  return '65%'
})

// 道路等级位置
const roadLevelPosition = computed(() => {
  const level = statsData.value.roadLevel
  return `${(level - 1) * 25}%`
})

// 布控数据
const deploymentData = ref([])

// 过滤后的事件
const filteredEvents = computed(() => {
  const events = [
    ...alarmList.value,
    ...alarmList.value.map(a => ({ ...a, id: a.id + 100, type: '非机动车驶入' })),
    ...alarmList.value.map(a => ({ ...a, id: a.id + 200, type: '行人闯入' }))
  ].slice(0, 8)
  if (eventFilter.value === 'all') {
    return events
  }
  return events.filter(e => !e.isCompliant)
})
</script>

<style scoped>
.monitor-wall {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #000510;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  min-height: 0;
  padding: 15px;
  gap: 15px;
}

/* 左侧视频区域 */
.video-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.video-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #000;
  border: 1px solid #00E5FF;
  border-radius: 4px;
  overflow: hidden;
}

.video-container {
  flex: 1;
  position: relative;
  background: #000;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(0, 229, 255, 0.4);
  font-size: 18px;
}

/* 视频装饰角 */
.video-corner {
  position: absolute;
  width: 20px;
  height: 20px;
  border-color: #00E5FF;
  border-style: solid;
  pointer-events: none;
}

.video-corner.top-left {
  top: 0;
  left: 0;
  border-width: 3px 0 0 3px;
}

.video-corner.top-right {
  top: 0;
  right: 0;
  border-width: 3px 3px 0 0;
}

.video-corner.bottom-left {
  bottom: 0;
  left: 0;
  border-width: 0 0 3px 3px;
}

.video-corner.bottom-right {
  bottom: 0;
  right: 0;
  border-width: 0 3px 3px 0;
}

.video-footer {
  height: 6px;
  background: linear-gradient(90deg, #00E5FF, #0099FF, #00E5FF);
  padding: 0 20px;
}

.footer-line {
  height: 100%;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 10px,
    rgba(0, 0, 0, 0.5) 10px,
    rgba(0, 0, 0, 0.5) 20px
  );
}

/* 右侧面板 */
.right-panel {
  width: 400px;
  min-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-section {
  background: rgba(0, 20, 50, 0.6);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  padding: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.header-bar {
  width: 3px;
  height: 14px;
  background: #00E5FF;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
}

.header-line {
  flex: 1;
  height: 1px;
  background: repeating-linear-gradient(
    90deg,
    rgba(0, 229, 255, 0.3),
    rgba(0, 229, 255, 0.3) 4px,
    transparent 4px,
    transparent 8px
  );
}

/* 预览通道 */
.channel-content {
  display: flex;
  gap: 10px;
}

.channel-select {
  flex: 1;
}

.draw-btn {
  border-color: #00E5FF;
  color: #00E5FF;
}

.draw-btn:hover {
  background: rgba(0, 229, 255, 0.1);
}

/* 实时交通参数 */
.traffic-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.traffic-item {
  text-align: center;
}

.traffic-value {
  font-size: 28px;
  font-weight: bold;
  color: rgba(180, 210, 235, 0.85);
  margin-bottom: 4px;
}

.traffic-value.primary {
  color: #00E5FF;
  text-shadow: 0 0 10px rgba(0, 229, 255, 0.5);
}

.traffic-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

/* 事件统计 */
.donut-chart-area {
  display: flex;
  align-items: center;
  gap: 20px;
}

.donut-chart {
  position: relative;
  width: 100px;
  height: 100px;
  flex-shrink: 0;
}

.donut-circle {
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.donut-total {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #00E5FF;
}

.donut-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
}

.donut-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.legend-name {
  flex: 1;
  color: rgba(255, 255, 255, 0.8);
}

.legend-value {
  font-weight: bold;
  color: rgba(180, 210, 235, 0.85);
}

/* 等级指标 */
.level-item {
  margin-bottom: 12px;
}

.level-item:last-child {
  margin-bottom: 0;
}

.level-header {
  margin-bottom: 6px;
}

.level-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.level-bar {
  position: relative;
  height: 8px;
  background: linear-gradient(90deg, #00FF88, #FFB800, #FF006E);
  border-radius: 4px;
  margin-bottom: 4px;
}

.level-gradient {
  width: 100%;
  height: 100%;
  border-radius: 4px;
}

.level-marker {
  position: absolute;
  top: -4px;
  width: 4px;
  height: 16px;
  background: rgba(180, 210, 235, 0.85);
  border-radius: 2px;
  transform: translateX(-50%);
}

.level-scale {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
}

.level-status {
  text-align: center;
  font-size: 12px;
  margin-top: 4px;
  padding: 2px 8px;
  border-radius: 2px;
  display: inline-block;
}

.level-status.level-1 {
  background: rgba(82, 196, 26, 0.2);
  color: #00FF88;
}

.level-status.level-2 {
  background: rgba(255, 170, 0, 0.2);
  color: #FFB800;
}

/* 布控信息 */
.deployment-table {
  background: transparent;
}

.deployment-table :deep(.el-table__header th) {
  background: rgba(0, 229, 255, 0.1);
  color: rgba(180, 210, 235, 0.85);
  font-size: 11px;
  border-color: rgba(0, 229, 255, 0.15);
}

.deployment-table :deep(.el-table__body td) {
  background: transparent;
  color: rgba(255, 255, 255, 0.8);
  font-size: 11px;
  border-color: rgba(0, 229, 255, 0.1);
}

.deployment-table :deep(.el-table__row:hover td) {
  background: rgba(0, 229, 255, 0.06);
}

.status-tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 2px;
}

.status-tag.online {
  background: rgba(82, 196, 26, 0.2);
  color: #00FF88;
}

/* 视频质量检测 */
.quality-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.quality-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

/* 底部事件抓拍 */
.bottom-events {
  padding: 12px 20px;
  background: rgba(0, 20, 50, 0.6);
  border-top: 1px solid rgba(0, 229, 255, 0.2);
}

.events-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.events-title {
  font-size: 13px;
  font-weight: 500;
  color: rgba(180, 210, 235, 0.85);
}

/* radio-button 深色主题适配 */
.events-header :deep(.el-radio-button__inner) {
  background: rgba(0, 21, 41, 0.8);
  border-color: rgba(0, 229, 255, 0.3);
  color: rgba(200, 230, 255, 0.85);
  font-size: 12px;
  padding: 4px 12px;
}

.events-header :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: #00E5FF;
  border-color: #00E5FF;
  color: #001a2e;
  box-shadow: none;
}

.events-carousel {
  display: flex;
  gap: 12px;
  overflow-x: auto;
}

.events-carousel::-webkit-scrollbar {
  height: 4px;
}

.events-carousel::-webkit-scrollbar-thumb {
  background: rgba(0, 229, 255, 0.3);
  border-radius: 2px;
}

.event-card {
  flex-shrink: 0;
  width: 140px;
  background: rgba(0, 20, 50, 0.8);
  border: 1px solid rgba(0, 229, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.event-thumb {
  position: relative;
  height: 80px;
  overflow: hidden;
}

.event-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.event-detection-box {
  position: absolute;
  top: 20%;
  left: 15%;
  width: 70%;
  height: 50%;
  border: 2px solid #FF006E;
  border-radius: 2px;
}

.event-label {
  padding: 6px 8px;
  background: linear-gradient(135deg, rgba(0, 229, 255, 0.1), transparent);
  clip-path: polygon(0 0, 100% 0, 100% 70%, 80% 100%, 0 100%);
}

.event-type {
  font-size: 11px;
  color: rgba(180, 210, 235, 0.85);
}

/* 底部信息栏 */
.bottom-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 20px;
  background: rgba(0, 10, 30, 0.9);
  border-top: 1px solid rgba(0, 229, 255, 0.1);
}

.info-left {
  display: flex;
  gap: 40px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.info-value {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.info-value.quality-ok {
  color: #00FF88;
}
</style>
