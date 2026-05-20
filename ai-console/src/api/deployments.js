import request from './index'

export const getDeployments = (params) => request.get('/deployments', { params })
export const getDeployment = (id) => request.get(`/deployments/${id}`)
export const createDeployment = (data) => request.post('/deployments', data)
export const updateDeployment = (id, data) => request.put(`/deployments/${id}`, data)
export const deleteDeployment = (id) => request.delete(`/deployments/${id}`)
export const scaleDeployment = (id, data) => request.post(`/deployments/${id}/scale`, data)
export const restartDeployment = (id) => request.post(`/deployments/${id}/restart`)
export const getDeploymentPods = (id, params) => request.get(`/deployments/${id}/pods`, { params })
export const getDeploymentLogs = (id, params) => request.get(`/deployments/${id}/logs`, { params })
export const updateDeploymentAnnotations = (id, data) => request.patch(`/deployments/${id}/annotations`, data)