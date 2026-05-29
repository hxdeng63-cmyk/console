import request from './index'

export const getPTWeightFiles = (params) => request.get('/pt-weight-files', { params })
export const getPTWeightFile = (id) => request.get(`/pt-weight-files/${id}`)
export const createPTWeightFile = (data) => request.post('/pt-weight-files', data)
export const updatePTWeightFile = (id, data) => request.put(`/pt-weight-files/${id}`, data)
export const deletePTWeightFile = (id) => request.delete(`/pt-weight-files/${id}`)
