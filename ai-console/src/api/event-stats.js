import request from './index'

export const getTodayStats = (params) => request.get('/event-stats/today', { params })
export const getViolationStats = (params) => request.get('/event-stats/violations', { params })
export const getAlgorithmSummary = (params) => request.get('/event-stats/algorithm-summary', { params })
export const getSceneStats = (params) => request.get('/event-stats/scenes', { params })
export const getTrendStats = (params) => request.get('/event-stats/trend', { params })
export const getEventTrendStats = (params) => request.get('/event-stats/event-trend', { params })
