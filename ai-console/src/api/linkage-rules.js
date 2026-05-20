import request from './index'

export const getLinkageRules = (params) => request.get('/linkage-rules', { params })
export const getLinkageRule = (id) => request.get(`/linkage-rules/${id}`)
export const createLinkageRule = (data) => request.post('/linkage-rules', data)
export const updateLinkageRule = (id, data) => request.put(`/linkage-rules/${id}`, data)
export const deleteLinkageRule = (id) => request.delete(`/linkage-rules/${id}`)
export const enableLinkageRule = (id) => request.post(`/linkage-rules/${id}/enable`)
export const disableLinkageRule = (id) => request.post(`/linkage-rules/${id}/disable`)
export const testLinkageRule = (id, data) => request.post(`/linkage-rules/${id}/test`, data)
export const copyLinkageRule = (id) => request.post(`/linkage-rules/${id}/copy`)