import request from './index'

export const getSessions = (params) => request.get('/sessions', { params })
export const getSession = (id) => request.get(`/sessions/${id}`)
export const deleteSession = (id) => request.delete(`/sessions/${id}`)
export const deleteAllSessions = () => request.delete('/sessions')
export const updateSession = (id, data) => request.put(`/sessions/${id}`, data)