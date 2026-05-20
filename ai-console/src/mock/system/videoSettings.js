export const videoSettingList = Object.freeze([
  { id: 1, ruleName: '高速公路录像规则', streamType: '主码流', resolution: '1920x1080', fps: 25, quality: '高', retentionDays: 30, storagePath: '/video/highway', enabled: true },
  { id: 2, ruleName: '城市道路录像规则', streamType: '主码流', resolution: '2560x1440', fps: 30, quality: '高', retentionDays: 15, storagePath: '/video/cityroad', enabled: true },
  { id: 3, ruleName: '公共场所录像规则', streamType: '子码流', resolution: '1280x720', fps: 25, quality: '中', retentionDays: 7, storagePath: '/video/public', enabled: true },
  { id: 4, ruleName: '校园监控录像规则', streamType: '主码流', resolution: '1920x1080', fps: 25, quality: '高', retentionDays: 30, storagePath: '/video/campus', enabled: true },
  { id: 5, ruleName: '金融网点录像规则', streamType: '主码流', resolution: '1920x1080', fps: 25, quality: '高', retentionDays: 60, storagePath: '/video/bank', enabled: true },
  { id: 6, ruleName: '医疗机构录像规则', streamType: '子码流', resolution: '1280x720', fps: 25, quality: '中', retentionDays: 15, storagePath: '/video/hospital', enabled: true },
  { id: 7, ruleName: '住宅小区录像规则', streamType: '子码流', resolution: '1280x720', fps: 20, quality: '中', retentionDays: 7, storagePath: '/video/residential', enabled: true },
  { id: 8, ruleName: '交通枢纽录像规则', streamType: '主码流', resolution: '2560x1440', fps: 30, quality: '高', retentionDays: 30, storagePath: '/video/transport', enabled: true },
  { id: 9, ruleName: '事件触发录像规则', streamType: '主码流', resolution: '1920x1080', fps: 25, quality: '高', retentionDays: 90, storagePath: '/video/event', enabled: true },
  { id: 10, ruleName: '默认录像规则', streamType: '子码流', resolution: '1280x720', fps: 25, quality: '低', retentionDays: 3, storagePath: '/video/default', enabled: false },
])
