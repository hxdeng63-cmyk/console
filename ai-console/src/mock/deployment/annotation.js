// 标注管理 Mock 数据

export const annotations = [
  { id: 1, deploymentId: 1, deviceId: 'dev-1', type: 'monitoring', polygon: [[10,20],[30,20],[30,40],[10,40]], createTime: '2026-04-15 10:00:00' },
  { id: 2, deploymentId: 1, deviceId: 'dev-1', type: 'monitoring', polygon: [[50,30],[70,30],[70,50],[50,50]], createTime: '2026-04-15 11:30:00' },
  { id: 3, deploymentId: 2, deviceId: 'dev-2', type: 'forbidden', polygon: [[20,10],[40,10],[40,30],[20,30]], createTime: '2026-04-16 09:00:00' },
  { id: 4, deploymentId: 2, deviceId: 'dev-3', type: 'monitoring', polygon: [[15,25],[35,25],[35,45],[15,45]], createTime: '2026-04-16 14:20:00' },
  { id: 5, deploymentId: 3, deviceId: 'dev-4', type: 'forbidden', polygon: [[5,15],[25,15],[25,35],[5,35]], createTime: '2026-04-17 08:45:00' }
]

export const presets = [
  { id: 1, deviceId: 'dev-1', name: '预置点1', p: 120, t: 45, z: 8, timeRange: { start: '00:00:00', end: '23:59:59' } },
  { id: 2, deviceId: 'dev-1', name: '预置点2', p: 240, t: 30, z: 6, timeRange: { start: '00:00:00', end: '23:59:59' } },
  { id: 3, deviceId: 'dev-2', name: '预置点1', p: 180, t: 60, z: 10, timeRange: { start: '06:00:00', end: '18:00:00' } },
  { id: 4, deviceId: 'dev-3', name: '预置点1', p: 90, t: 35, z: 7, timeRange: { start: '00:00:00', end: '23:59:59' } },
  { id: 5, deviceId: 'dev-4', name: '隧道入口', p: 0, t: 20, z: 5, timeRange: { start: '00:00:00', end: '23:59:59' } }
]

export const tags = [
  { id: 1, name: '重点区域', type: 'number' },
  { id: 2, name: '禁行区域', type: 'number' },
  { id: 3, name: '施工区域', type: 'number' },
  { id: 4, name: '分流区域', type: 'number' }
]
