import request from './index'

export const getAnnotations = (params) => request.get('/annotations', { params })
export const getAnnotation = (id) => request.get(`/annotations/${id}`)
export const createAnnotation = (data) => request.post('/annotations', data)
export const updateAnnotation = (id, data) => request.put(`/annotations/${id}`, data)
export const deleteAnnotation = (id) => request.delete(`/annotations/${id}`)

export const getPresets = (params) => request.get('/presets', { params })
export const createPreset = (data) => request.post('/presets', data)
export const updatePreset = (id, data) => request.put(`/presets/${id}`, data)
export const deletePreset = (id) => request.delete(`/presets/${id}`)
