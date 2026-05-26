import request from './index'

export const getList = (params) => request.get('/warning-events', { params })
