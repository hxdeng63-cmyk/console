import request from './index'

export const getCleanRecords = (params) => request.get('/clean-records', { params })
export const getCleanRecord = (id) => request.get(`/clean-records/${id}`)
export const createCleanRecord = (data) => request.post('/clean-records', data)
export const updateCleanRecord = (id, data) => request.put(`/clean-records/${id}`, data)
export const deleteCleanRecord = (id) => request.delete(`/clean-records/${id}`)
