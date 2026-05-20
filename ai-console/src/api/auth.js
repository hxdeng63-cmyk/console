import request from './index'

export const login = (data) => request.post('/auth/login', data)
export const logout = () => request.post('/auth/logout')
export const refreshToken = (data) => request.post('/auth/refresh', data)
export const getMe = () => request.get('/auth/me')
export const updatePassword = (data) => request.put('/auth/password', data)
export const getSessions = () => request.get('/auth/sessions')
export const revokeSession = (id) => request.delete(`/auth/sessions/${id}`)
export const revokeAllSessions = () => request.delete('/auth/sessions')