export const ruleList = Object.freeze([
  { id: 1, ruleName: '人脸识别联动', eventType: '人脸识别', algorithmName: '人脸检测', actionType: '推送告警', isEnabled: true, createTime: '2024-01-10' },
  { id: 2, ruleName: '车牌识别联动', eventType: '车牌识别', algorithmName: '车牌识别', actionType: '推送数据', isEnabled: true, createTime: '2024-01-15' },
  { id: 3, ruleName: '行为异常联动', eventType: '行为异常', algorithmName: '行为分析', actionType: '推送告警', isEnabled: true, createTime: '2024-01-20' },
  { id: 4, ruleName: '拥挤检测联动', eventType: '区域拥挤', algorithmName: '拥挤检测', actionType: '声光提示', isEnabled: false, createTime: '2024-02-01' },
  { id: 5, ruleName: '越界检测联动', eventType: '越界', algorithmName: '越界检测', actionType: '推送告警', isEnabled: true, createTime: '2024-02-10' },
  { id: 6, ruleName: '遗留物联动', eventType: '遗留物', algorithmName: '遗留物检测', actionType: '推送告警', isEnabled: true, createTime: '2024-02-15' },
  { id: 7, ruleName: '夜间闯入联动', eventType: '人员闯入', algorithmName: '夜间分析', actionType: '推送告警', isEnabled: true, createTime: '2024-03-01' },
  { id: 8, ruleName: '聚集检测联动', eventType: '人员聚集', algorithmName: '人员聚集', actionType: '推送数据', isEnabled: false, createTime: '2024-03-05' },
])
