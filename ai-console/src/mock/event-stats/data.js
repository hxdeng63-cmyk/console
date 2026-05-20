// 公司选项
export const companies = [
  { label: '海东分公司', value: '海东分公司' },
  { label: '西宁分公司', value: '西宁分公司' }
]

// 区域选项
export const regions = [
  { label: 'S201', value: 'S201' },
  { label: 'G213', value: 'G213' }
]

// 事件类型列表（16种）
export const eventTypes = [
  '疑似事故',
  '作业人员',
  '交通阻塞',
  '异常停车',
  '烟雾',
  '作业车辆识别',
  '非机动车驶入',
  '占用应急车道',
  '逆向行驶',
  '通过卡车数量',
  '通过大客车数量',
  '通过摩托车数量',
  '通过小汽车数量',
  '下行车流量',
  '上行车流量',
  '行人闯入'
]

// 事件统计汇总
export const summary = {
  totalEvents: 3856,
  todayEvents: 127,
  eventTypes: [
    { name: '疑似事故', count: 256 },
    { name: '作业人员', count: 412 },
    { name: '交通阻塞', count: 521 },
    { name: '异常停车', count: 389 },
    { name: '烟雾', count: 178 },
    { name: '作业车辆识别', count: 445 },
    { name: '非机动车驶入', count: 312 },
    { name: '占用应急车道', count: 198 },
    { name: '逆向行驶', count: 156 },
    { name: '通过卡车数量', count: 892 },
    { name: '通过大客车数量', count: 734 },
    { name: '通过摩托车数量', count: 445 },
    { name: '通过小汽车数量', count: 1205 },
    { name: '下行车流量', count: 2156 },
    { name: '上行车流量', count: 1987 },
    { name: '行人闯入', count: 298 }
  ]
}

// 趋势数据
export const trendData = {
  hours: Array.from({length: 24}, (_, i) => ({ time: `${i}:00`, value: Math.floor(Math.random() * 100) })),
  days: Array.from({length: 7}, (_, i) => ({ time: `Day ${i+1}`, value: Math.floor(Math.random() * 500) })),
  months: Array.from({length: 30}, (_, i) => ({ time: `Day ${i+1}`, value: Math.floor(Math.random() * 300) }))
}

// 环形图数据
export const ringData = summary.eventTypes
