import request from './index'

export const getAlgorithms = (params) => request.get('/algorithms', { params })
export const getAlgorithm = (id) => request.get(`/algorithms/${id}`)
export const createAlgorithm = (data) => request.post('/algorithms', data)
export const updateAlgorithm = (id, data) => request.put(`/algorithms/${id}`, data)
export const deleteAlgorithm = (id) => request.delete(`/algorithms/${id}`)
export const deployAlgorithm = (id, data) => request.post(`/algorithms/${id}/deploy`, data)
export const undeployAlgorithm = (id) => request.post(`/algorithms/${id}/undeploy`)
export const getAlgorithmVersions = (id, params) => request.get(`/algorithms/${id}/versions`, { params })