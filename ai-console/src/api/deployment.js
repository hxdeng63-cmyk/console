import request from './index'

export const deploymentApi = {
  // Deployments
  list: (params) => request.get('/deployments', { params }),
  get: (id) => request.get(`/deployments/${id}`),
  create: (data) => request.post('/deployments', data),
  update: (id, data) => request.put(`/deployments/${id}`, data),
  delete: (id) => request.delete(`/deployments/${id}`),

  // Deployment lifecycle
  restartAll: () => request.post('/deployments/restart-all'),
  getRestartAllStatus: (taskId) => request.get(`/deployments/restart-all/status/${taskId}`),
  start: (id, data) => request.post(`/deployments/${id}/start`, data),
  startStatus: (id, taskId) => request.get(`/deployments/${id}/start/status/${taskId}`),

  // Algorithms
  listAlgorithms: (params) => request.get('/algorithms', { params }),

  // Algorithm Services
  listServices: (params) => request.get('/algorithm-services', { params }),

  // Devices
  listDevices: (params) => request.get('/devices', { params }),
}