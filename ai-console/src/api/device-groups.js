import request from './index'

export const getDeviceGroups = (params) => request.get('/device-groups', { params })
export const getDeviceGroup = (id) => request.get(`/device-groups/${id}`)
export const createDeviceGroup = (data) => request.post('/device-groups', data)
export const updateDeviceGroup = (id, data) => request.put(`/device-groups/${id}`, data)
export const deleteDeviceGroup = (id) => request.delete(`/device-groups/${id}`)
export const getDeviceGroupTree = () => request.get('/device-groups/tree')
export const getDeviceGroupDevices = (id, params) => request.get(`/device-groups/${id}/devices`, { params })
export const addDeviceGroupDevices = (id, data) => request.post(`/device-groups/${id}/devices`, data)
export const removeDeviceGroupDevices = (id, data) => request.delete(`/device-groups/${id}/devices`, data)