import request from './index'

export const getPlatforms = (params) => request.get('/platforms', { params })
export const getPlatform = (id) => request.get(`/platforms/${id}`)
export const createPlatform = (data) => request.post('/platforms', data)
export const updatePlatform = (id, data) => request.put(`/platforms/${id}`, data)
export const deletePlatform = (id) => request.delete(`/platforms/${id}`)
export const syncPlatform = (id) => request.post(`/platforms/${id}/sync`)
export const getPlatformDevices = (id, params) => request.get(`/platforms/${id}/devices`, { params })