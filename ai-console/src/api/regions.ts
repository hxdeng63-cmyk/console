import request from '@/api/index'

export const getRegions = (params?: any) => request.get('/regions', { params })
export const getRegion = (id: number | string) => request.get(`/regions/${id}`)
export const createRegion = (data: any) => request.post('/regions', data)
export const updateRegion = (id: number | string, data: any) => request.put(`/regions/${id}`, data)
export const deleteRegion = (id: number | string) => request.delete(`/regions/${id}`)
export const getRegionTree = (params?: any): Promise<any> => request.get('/regions/tree', { params })
export const getFullRegionTree = () => request.get('/regions/full-tree')
export const getRegionDevices = (id: number | string, params?: any) => request.get(`/regions/${id}/devices`, { params })
