export const serviceList = Object.freeze([
  {
    id: 1, serviceId: 'SVC001', serviceName: '人脸检测服务', serviceAddress: { ip: '192.168.2.101', port: 8080 }, annotationAddress: { ip: '192.168.2.102', port: 8081 }, status: '运行中'
  },
  {
    id: 2, serviceId: 'SVC002', serviceName: '车牌识别服务', serviceAddress: { ip: '192.168.2.103', port: 8080 }, annotationAddress: { ip: '192.168.2.104', port: 8081 }, status: '运行中'
  },
  {
    id: 3, serviceId: 'SVC003', serviceName: '行为分析服务', serviceAddress: { ip: '192.168.2.105', port: 8080 }, annotationAddress: { ip: '192.168.2.106', port: 8081 }, status: '运行中'
  },
  {
    id: 4, serviceId: 'SVC004', serviceName: '视频抽帧服务', serviceAddress: { ip: '192.168.2.107', port: 8080 }, annotationAddress: { ip: '192.168.2.108', port: 8081 }, status: '运行中'
  },
  {
    id: 5, serviceId: 'SVC005', serviceName: '周界防范服务', serviceAddress: { ip: '192.168.2.109', port: 8080 }, annotationAddress: { ip: '192.168.2.110', port: 8081 }, status: '停止'
  },
])
