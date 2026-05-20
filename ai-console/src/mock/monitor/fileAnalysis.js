// 文件分析 Mock 数据

export const videoFiles = [
  { id: 1, deviceId: 'dev-1', deviceName: 'K16+250 下行', fileName: '202604201000_001.flv', startTime: '2026-04-20 10:00:00', endTime: '2026-04-20 11:00:00', duration: 3600 },
  { id: 2, deviceId: 'dev-1', deviceName: 'K16+250 下行', fileName: '202604201100_001.flv', startTime: '2026-04-20 11:00:00', endTime: '2026-04-20 12:00:00', duration: 3600 },
  { id: 3, deviceId: 'dev-2', deviceName: 'K7+050 上行', fileName: '202604201200_001.flv', startTime: '2026-04-20 12:00:00', endTime: '2026-04-20 13:00:00', duration: 3600 },
  { id: 4, deviceId: 'dev-2', deviceName: 'K7+050 上行', fileName: '202604201300_001.flv', startTime: '2026-04-20 13:00:00', endTime: '2026-04-20 14:00:00', duration: 3600 },
  { id: 5, deviceId: 'dev-3', deviceName: 'K8+100 下行', fileName: '202604201400_001.flv', startTime: '2026-04-20 14:00:00', endTime: '2026-04-20 15:00:00', duration: 3600 },
  { id: 6, deviceId: 'dev-4', deviceName: 'K228+300 上行', fileName: '202604201500_001.flv', startTime: '2026-04-20 15:00:00', endTime: '2026-04-20 16:00:00', duration: 3600 }
]

export const videoUrl = {
  fileId: 1,
  hlsUrl: 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8',
  duration: 3600
}
