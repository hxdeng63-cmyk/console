export const microserviceList = Object.freeze([
  { id: 1, name: '视频分析服务', serviceName: 'video-analysis', ip: '192.168.1.101', port: 8080, status: '运行中', cpuUsage: 45, memoryUsage: 60 },
  { id: 2, name: '算法推理服务', serviceName: 'algorithm-inference', ip: '192.168.1.102', port: 8081, status: '运行中', cpuUsage: 72, memoryUsage: 85 },
  { id: 3, name: '事件上报服务', serviceName: 'event-report', ip: '192.168.1.103', port: 8082, status: '运行中', cpuUsage: 30, memoryUsage: 40 },
  { id: 4, name: '设备接入服务', serviceName: 'device-access', ip: '192.168.1.104', port: 8083, status: '停止', cpuUsage: 0, memoryUsage: 0 },
  { id: 5, name: '数据存储服务', serviceName: 'data-storage', ip: '192.168.1.105', port: 8084, status: '运行中', cpuUsage: 55, memoryUsage: 70 },
])
