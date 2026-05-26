import request from './index'

export const getEventStats = (params) => request.get('/event-stats', { params })
export const getEventTrend = (params) => request.get('/event-stats/trend', { params })
export const getSceneStats = () => request.get('/event-stats/scenes')