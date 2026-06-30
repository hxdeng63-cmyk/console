import request from '@/api/index'

export const registerDevicesAsync = (deviceIds) => {
  return request.post('/stream/devices/register', { device_ids: deviceIds })
}

export const getRegisterDevicesStatus = (taskId) => {
  return request.get(`/stream/devices/register/status/${taskId}`)
}

export const getDeviceFlvUrl = (deviceId) => {
  return request.get(`/stream/device/${deviceId}/flv`)
}
