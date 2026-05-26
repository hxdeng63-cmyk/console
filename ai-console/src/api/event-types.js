import request from './index'

export const getEventTypes = (params) => request.get('/event-types', { params })
export const getEventType = (id) => request.get(`/event-types/${id}`)
export const createEventType = (data) => request.post('/event-types', data)
export const updateEventType = (id, data) => request.put(`/event-types/${id}`, data)
export const deleteEventType = (id) => request.delete(`/event-types/${id}`)
