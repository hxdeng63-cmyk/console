import request from './index'

export const getOperationLogs = (params) => request.get('/operation-logs', { params })
export const getOperationLog = (id) => request.get(`/operation-logs/${id}`)
export const exportOperationLogs = (params) => request.get('/operation-logs/export', { params, responseType: 'blob' })
export const deleteOperationLog = (id) => request.delete(`/operation-logs/${id}`)
export const deleteOperationLogs = (data) => request.post('/operation-logs/batch-delete', data)