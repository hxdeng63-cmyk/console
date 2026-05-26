import request from './index'

export const getLinkageHistories = (params) => request.get('/push-histories', { params })
export const getLinkageHistory = (id) => request.get(`/push-histories/${id}`)
export const exportLinkageHistories = (params) => request.get('/push-histories/export', { params, responseType: 'blob' })
