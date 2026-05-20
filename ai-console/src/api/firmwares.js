import request from './index'

export const getFirmwares = (params) => request.get('/firmwares', { params })
export const getFirmware = (id) => request.get(`/firmwares/${id}`)
export const uploadFirmware = (data) => request.post('/firmwares', data)
export const deleteFirmware = (id) => request.delete(`/firmwares/${id}`)
export const upgradeDevice = (id, data) => request.post(`/firmwares/upgrade`, { deviceId: id, ...data })
export const batchUpgradeDevices = (data) => request.post('/firmwares/batch-upgrade', data)
export const getFirmwareVersions = (deviceType) => request.get('/firmwares/versions', { params: { deviceType } })