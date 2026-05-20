import request from './index'

export const getAlgorithmEvents = (params) => request.get('/algorithm-events', { params })
export const getAlgorithmEvent = (id) => request.get(`/algorithm-events/${id}`)
export const handleAlgorithmEvent = (id, data) => request.post(`/algorithm-events/${id}/handle`, data)
export const batchHandleAlgorithmEvents = (data) => request.post('/algorithm-events/batch-handle', data)
export const getAlgorithmEventStats = () => request.get('/algorithm-events/stats')
export const exportAlgorithmEvents = (params) => request.get('/algorithm-events/export', { params, responseType: 'blob' })