// 设备树数据 — 与设备组管理数据完全对齐
export const deviceTreeData = [
  {
    id: 'org-1',
    name: '海东分公司',
    type: 'org',
    online: true,
    children: [
      {
        id: 'group-1',
        name: 'S201',
        type: 'group',
        online: true,
        children: [
          { id: 'device-1', name: 'S201海东分公司K228+300下行(道路沿线)', type: 'camera', online: true, ip: '192.168.10.1' },
          { id: 'device-2', name: 'S201海东分公司K199+650上行(道路沿线)', type: 'camera', online: true, ip: '192.168.10.2' },
          { id: 'device-3', name: 'S201海东分公司K195+700上行(道路沿线)', type: 'camera', online: true, ip: '192.168.10.3' }
        ]
      },
      {
        id: 'group-2',
        name: 'G213',
        type: 'group',
        online: true,
        children: [
          { id: 'device-4', name: 'G213策磨高速乐化路段K16+250上行', type: 'camera', online: true, ip: '192.168.10.4' },
          { id: 'device-5', name: 'G213策磨高速乐化路段K10+150上行', type: 'camera', online: true, ip: '192.168.10.5' },
          { id: 'device-6', name: 'G213策磨高速乐化路段K9+045下行', type: 'camera', online: false, ip: '192.168.10.6' },
          { id: 'device-7', name: 'G213策磨高速乐化路段K8+150下行', type: 'camera', online: true, ip: '192.168.10.7' }
        ]
      }
    ]
  },
  {
    id: 'org-2',
    name: '西宁分公司',
    type: 'org',
    online: true,
    children: [
      {
        id: 'group-3',
        name: 'S201',
        type: 'group',
        online: true,
        children: [
          { id: 'device-8', name: 'S201西宁分公司K45+200上行(道路沿线)', type: 'camera', online: true, ip: '192.168.10.8' },
          { id: 'device-9', name: 'S201西宁分公司K38+600下行(道路沿线)', type: 'camera', online: true, ip: '192.168.10.9' }
        ]
      },
      {
        id: 'group-4',
        name: 'G213',
        type: 'group',
        online: true,
        children: [
          { id: 'device-10', name: 'G213策磨高速西宁段K89+100下行', type: 'camera', online: false, ip: '192.168.10.10' },
          { id: 'device-11', name: '西宁分公司环城高速K120+500上行', type: 'camera', online: true, ip: '192.168.10.11' },
          { id: 'device-12', name: '西宁分公司环城高速K115+300下行', type: 'camera', online: true, ip: '192.168.10.12' }
        ]
      }
    ]
  }
]

// 报警事件数据 - 带合规性标签（设备名与 deviceTreeData 对齐）
export const alarmList = [
  {
    id: 1,
    time: '10:25:30',
    type: '行人闯入',
    device: 'S201海东分公司K228+300下行(道路沿线)',
    location: '海东分公司S201-S201海东分公司K228+300下行',
    level: 'danger',
    handled: false,
    isCompliant: false,
    imageUrl: 'https://picsum.photos/seed/alarm1/300/200',
    captureTime: '2024-04-17 17:55:37'
  },
  {
    id: 2,
    time: '10:20:15',
    type: '异常停车',
    device: 'S201海东分公司K199+650上行(道路沿线)',
    location: '海东分公司S201-S201海东分公司K199+650上行',
    level: 'warning',
    handled: false,
    isCompliant: false,
    imageUrl: 'https://picsum.photos/seed/alarm2/300/200',
    captureTime: '2024-04-17 17:50:22'
  },
  {
    id: 3,
    time: '10:15:00',
    type: '作业人员',
    device: 'G213策磨高速乐化路段K16+250上行',
    location: '海东分公司G213-G213策磨高速乐化路段K16+250上行',
    level: 'info',
    handled: true,
    isCompliant: true,
    imageUrl: 'https://picsum.photos/seed/alarm3/300/200',
    captureTime: '2024-04-17 17:45:10'
  },
  {
    id: 4,
    time: '10:10:45',
    type: '作业车辆',
    device: 'S201西宁分公司K45+200上行(道路沿线)',
    location: '西宁分公司S201-S201西宁分公司K45+200上行',
    level: 'info',
    handled: true,
    isCompliant: true,
    imageUrl: 'https://picsum.photos/seed/alarm4/300/200',
    captureTime: '2024-04-17 17:40:45'
  },
  {
    id: 5,
    time: '10:05:30',
    type: '疑似事故',
    device: 'S201西宁分公司K38+600下行(道路沿线)',
    location: '西宁分公司S201-S201西宁分公司K38+600下行',
    level: 'danger',
    handled: false,
    isCompliant: false,
    imageUrl: 'https://picsum.photos/seed/alarm5/300/200',
    captureTime: '2024-04-17 17:35:30'
  },
  {
    id: 6,
    time: '10:00:20',
    type: '路面施工',
    device: '西宁分公司环城高速K120+500上行',
    location: '西宁分公司G213-西宁分公司环城高速K120+500上行',
    level: 'warning',
    handled: false,
    isCompliant: true,
    imageUrl: 'https://picsum.photos/seed/alarm6/300/200',
    captureTime: '2024-04-17 17:30:20'
  },
  {
    id: 7,
    time: '09:55:10',
    type: '抛洒物',
    device: 'G213策磨高速乐化路段K10+150上行',
    location: '海东分公司G213-G213策磨高速乐化路段K10+150上行',
    level: 'info',
    handled: true,
    isCompliant: true,
    imageUrl: 'https://picsum.photos/seed/alarm7/300/200',
    captureTime: '2024-04-17 17:25:10'
  },
  {
    id: 8,
    time: '09:50:05',
    type: '交通拥堵',
    device: 'S201海东分公司K228+300下行(道路沿线)',
    location: '海东分公司S201-S201海东分公司K228+300下行',
    level: 'warning',
    handled: false,
    isCompliant: false,
    imageUrl: 'https://picsum.photos/seed/alarm8/300/200',
    captureTime: '2024-04-17 17:20:05'
  }
]

// 统计数据
export const statsData = {
  upFlow: '125.6',
  downFlow: '458.2',
  avgSpeed: '85.3',
  congestionLevel: '2.3'
}

// 报警类型选项
export const alarmTypeOptions = ['行人闯入', '异常停车', '作业人员', '作业车辆', '路面施工', '疑似事故', '抛洒物', '交通拥堵']
