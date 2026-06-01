import request from './index'

export const getVideoSettings = (params) => request.get('/video-settings', { params })
export const getVideoSetting = (id) => request.get(`/video-settings/${id}`)
export const createVideoSetting = (data) => request.post('/video-settings', data)
export const updateVideoSetting = (id, data) => request.put(`/video-settings/${id}`, data)
export const deleteVideoSetting = (id) => request.delete(`/video-settings/${id}`)
export const toggleVideoSettingStatus = (id) => request.put(`/video-settings/${id}/status`)
