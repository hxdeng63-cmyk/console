export const platformList = Object.freeze([
  { id: 1, name: 'GB28181', type: '国家标准', version: 'GB/T 28181-2016', deviceCount: 45, status: '启用', config: { sipServer: '192.168.1.200', sipPort: 5060 } },
  { id: 2, name: 'ONVIF', type: '国际标准', version: 'ONVIF 2.0', deviceCount: 30, status: '启用', config: { discovery: true, port: 80 } },
  { id: 3, name: 'RTSP', type: '通用协议', version: 'RTSP 1.0', deviceCount: 60, status: '启用', config: { defaultPort: 554 } },
  { id: 4, name: '私有SDK', type: '厂商私有', version: 'V3.2.1', deviceCount: 25, status: '停用', config: { manufacturer: 'HIKVISION' } },
  { id: 5, name: 'RTMP', type: '流媒体协议', version: 'RTMP 1.0', deviceCount: 10, status: '启用', config: { rtmpPort: 1935 } },
])
