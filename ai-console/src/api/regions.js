import request from './index'

export const getRegions = (params) => request.get('/regions', { params })
export const getRegion = (id) => request.get(`/regions/${id}`)
export const createRegion = (data) => request.post('/regions', data)
export const updateRegion = (id, data) => request.put(`/regions/${id}`, data)
export const deleteRegion = (id) => request.delete(`/regions/${id}`)
export const getRegionTree = () => request.get('/regions/tree')
export const getRegionDevices = (id, params) => request.get(`/regions/${id}/devices`, { params })