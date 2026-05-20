import request from './index'

export const getAlgorithmServices = (params) => request.get('/algorithm-services', { params })
export const getAlgorithmService = (id) => request.get(`/algorithm-services/${id}`)
export const createAlgorithmService = (data) => request.post('/algorithm-services', data)
export const updateAlgorithmService = (id, data) => request.put(`/algorithm-services/${id}`, data)
export const deleteAlgorithmService = (id) => request.delete(`/algorithm-services/${id}`)
export const startAlgorithmService = (id) => request.post(`/algorithm-services/${id}/start`)
export const stopAlgorithmService = (id) => request.post(`/algorithm-services/${id}/stop`)
export const restartAlgorithmService = (id) => request.post(`/algorithm-services/${id}/restart`)
export const getAlgorithmServiceStats = (id) => request.get(`/algorithm-services/${id}/stats`)
export const getAlgorithmServiceLogs = (id, params) => request.get(`/algorithm-services/${id}/logs`, { params })