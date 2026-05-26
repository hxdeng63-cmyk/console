import request from './index'

export const getStats = () => request.get('/dashboard/stats')
export const getEventStats = () => request.get('/dashboard/event-stats')
export const getDeployments = () => request.get('/dashboard/deployments')
