// 布控管理 Mock 数据

export const algorithms = [
  { id: 1, name: '交通检测', type: 'traffic' },
  { id: 2, name: '火灾检测', type: 'fire' },
  { id: 3, name: '违章检测', type: 'violation' }
]

export const services = [
  { id: 1, name: '算法服务-01', address: '192.168.1.101:8080', labelAddress: '192.168.1.101:8081' },
  { id: 2, name: '算法服务-02', address: '192.168.1.102:8080', labelAddress: '192.168.1.102:8081' }
]

export const deployments = [
  {
    id: 1,
    name: 'test',
    deviceIds: [101, 102],
    deviceNames: 'S201(川大高速)青海海东川官路段海东分公司K216+299下行(浪塘山3号隧道),G6海东分公司...',
    deviceNamesLink: true,
    algorithmId: 1,
    serviceId: 1,
    schedule: {
      1: [{ start: '00:00:00', end: '23:59:59' }],
      2: [{ start: '00:00:00', end: '23:59:59' }],
      3: [{ start: '00:00:00', end: '23:59:59' }],
      4: [{ start: '00:00:00', end: '23:59:59' }],
      5: [{ start: '00:00:00', end: '23:59:59' }],
      6: [{ start: '00:00:00', end: '23:59:59' }],
      7: [{ start: '00:00:00', end: '23:59:59' }]
    },
    status: 'inactive',
    algorithmStatus: 'stopped',
    createTime: '2023-10-12 16:03:25'
  },
  {
    id: 2,
    name: '火灾监控-01',
    deviceIds: [103, 104, 105],
    deviceNames: '摄像头-103, 摄像头-104, 摄像头-105',
    algorithmId: 2,
    serviceId: 2,
    schedule: {
      1: [{ start: '06:00:00', end: '18:00:00' }],
      2: [{ start: '06:00:00', end: '18:00:00' }],
      3: [{ start: '06:00:00', end: '18:00:00' }],
      4: [{ start: '06:00:00', end: '18:00:00' }],
      5: [{ start: '06:00:00', end: '18:00:00' }],
      6: [{ start: '06:00:00', end: '18:00:00' }],
      7: [{ start: '06:00:00', end: '18:00:00' }]
    },
    status: 'active',
    algorithmStatus: 'running',
    createTime: '2026-04-12 14:30:00'
  },
  {
    id: 3,
    name: '违章检测-隧道',
    deviceIds: [106, 107],
    deviceNames: '摄像头-106, 摄像头-107',
    algorithmId: 3,
    serviceId: 1,
    schedule: {
      1: [{ start: '00:00:00', end: '23:59:59' }],
      2: [{ start: '00:00:00', end: '23:59:59' }],
      3: [{ start: '00:00:00', end: '23:59:59' }],
      4: [{ start: '00:00:00', end: '23:59:59' }],
      5: [{ start: '00:00:00', end: '23:59:59' }],
      6: [{ start: '00:00:00', end: '23:59:59' }],
      7: [{ start: '00:00:00', end: '23:59:59' }]
    },
    status: 'inactive',
    algorithmStatus: 'stopped',
    createTime: '2026-04-15 09:00:00'
  },
  {
    id: 4,
    name: '夜间交通检测',
    deviceIds: [108, 109, 110, 111],
    deviceNames: '摄像头-108, 摄像头-109, 摄像头-110, 摄像头-111',
    algorithmId: 1,
    serviceId: 2,
    schedule: {
      1: [{ start: '22:00:00', end: '06:00:00' }],
      2: [{ start: '22:00:00', end: '06:00:00' }],
      3: [{ start: '22:00:00', end: '06:00:00' }],
      4: [{ start: '22:00:00', end: '06:00:00' }],
      5: [{ start: '22:00:00', end: '06:00:00' }],
      6: [{ start: '22:00:00', end: '06:00:00' }],
      7: [{ start: '22:00:00', end: '06:00:00' }]
    },
    status: 'active',
    algorithmStatus: 'running',
    createTime: '2026-04-18 08:00:00'
  },
  {
    id: 5,
    name: '施工区域监控',
    deviceIds: [112, 113],
    deviceNames: '摄像头-112, 摄像头-113',
    algorithmId: 3,
    serviceId: 1,
    schedule: {
      1: [{ start: '08:00:00', end: '18:00:00' }],
      2: [{ start: '08:00:00', end: '18:00:00' }],
      3: [{ start: '08:00:00', end: '18:00:00' }],
      4: [{ start: '08:00:00', end: '18:00:00' }],
      5: [{ start: '08:00:00', end: '18:00:00' }],
      6: [{ start: '08:00:00', end: '18:00:00' }],
      7: []
    },
    status: 'active',
    algorithmStatus: 'running',
    createTime: '2026-04-19 11:00:00'
  }
]
