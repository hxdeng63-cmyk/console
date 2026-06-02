import request from './index'

export const getCleanupPolicy = () => request.get('/cleanup-policy')
export const updateCleanupPolicy = (data) => request.put('/cleanup-policy', data)
