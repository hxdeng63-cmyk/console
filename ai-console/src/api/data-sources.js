import request from './index'

export const getDataSources = (params) => request.get('/data-sources', { params })
export const getDataSource = (id) => request.get(`/data-sources/${id}`)
export const createDataSource = (data) => request.post('/data-sources', data)
export const updateDataSource = (id, data) => request.put(`/data-sources/${id}`, data)
export const deleteDataSource = (id) => request.delete(`/data-sources/${id}`)
export const testConnection = (data) => request.post('/data-sources/test-connection', data)
export const syncDataSource = (id) => request.post(`/data-sources/${id}/sync`)
export const getDataSourceDevices = (id, params) => request.get(`/data-sources/${id}/devices`, { params })