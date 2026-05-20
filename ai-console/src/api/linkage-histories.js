import request from './index'

export const getLinkageHistories = (params) => request.get('/linkage-histories', { params })
export const getLinkageHistory = (id) => request.get(`/linkage-histories/${id}`)
export const exportLinkageHistories = (params) => request.get('/linkage-histories/export', { params, responseType: 'blob' })