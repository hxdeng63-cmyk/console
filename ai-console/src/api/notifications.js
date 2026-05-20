import request from './index'

export const getNotifications = (params) => request.get('/notifications', { params })
export const getNotification = (id) => request.get(`/notifications/${id}`)
export const createNotification = (data) => request.post('/notifications', data)
export const updateNotification = (id, data) => request.put(`/notifications/${id}`, data)
export const deleteNotification = (id) => request.delete(`/notifications/${id}`)
export const markAsRead = (id) => request.post(`/notifications/${id}/read`)
export const markAllAsRead = () => request.post('/notifications/read-all')
export const deleteAllNotifications = () => request.delete('/notifications')