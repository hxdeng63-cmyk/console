export const taskList = Object.freeze([
  { id: 1, taskName: '视频抽帧任务', triggerType: '定时', triggerRule: '0 0 2 * * ?', algorithmName: '视频抽帧', targetDevices: 'D001,D002,D003', status: '运行中', createTime: '2024-01-15', lastRunTime: '2024-03-10 02:00:00' },
  { id: 2, taskName: '人脸检测任务', triggerType: '事件', triggerRule: '实时', algorithmName: '人脸检测', targetDevices: 'D007,D008', status: '运行中', createTime: '2024-01-20', lastRunTime: '2024-03-10 10:30:00' },
  { id: 3, taskName: '行为分析任务', triggerType: '事件', triggerRule: '实时', algorithmName: '行为分析', targetDevices: 'D013,D014', status: '运行中', createTime: '2024-02-01', lastRunTime: '2024-03-10 10:30:00' },
  { id: 4, taskName: '车牌识别任务', triggerType: '事件', triggerRule: '实时', algorithmName: '车牌识别', targetDevices: 'D002,D006', status: '停止', createTime: '2024-02-10', lastRunTime: '2024-03-05 18:00:00' },
  { id: 5, taskName: '夜间分析任务', triggerType: '定时', triggerRule: '0 0 23 * * ?', algorithmName: '夜间分析', targetDevices: 'D001,D005,D009', status: '运行中', createTime: '2024-02-15', lastRunTime: '2024-03-09 23:00:00' },
  { id: 6, taskName: '拥挤检测任务', triggerType: '事件', triggerRule: '实时', algorithmName: '拥挤检测', targetDevices: 'D003,D008', status: '运行中', createTime: '2024-02-20', lastRunTime: '2024-03-10 10:30:00' },
  { id: 7, taskName: '遗留物检测', triggerType: '事件', triggerRule: '实时', algorithmName: '遗留物检测', targetDevices: 'D005,D010', status: '运行中', createTime: '2024-03-01', lastRunTime: '2024-03-10 10:30:00' },
  { id: 8, taskName: '越界检测任务', triggerType: '事件', triggerRule: '实时', algorithmName: '越界检测', targetDevices: 'D013,D014', status: '运行中', createTime: '2024-03-05', lastRunTime: '2024-03-10 10:30:00' },
  { id: 9, taskName: '周界防范任务', triggerType: '定时', triggerRule: '0 0 0/6 * * ?', algorithmName: '周界防范', targetDevices: 'D007,D011', status: '停止', createTime: '2024-03-08', lastRunTime: '2024-03-09 18:00:00' },
  { id: 10, taskName: '人员聚集任务', triggerType: '事件', triggerRule: '实时', algorithmName: '人员聚集', targetDevices: 'D003,D008,D009', status: '运行中', createTime: '2024-03-10', lastRunTime: '2024-03-10 10:30:00' },
])
