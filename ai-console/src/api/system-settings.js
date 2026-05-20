import request from './index'

export const getSystemSettings = () => request.get('/system-settings')
export const updateSystemSettings = (data) => request.put('/system-settings', data)
export const getSystemSetting = (key) => request.get(`/system-settings/${key}`)
export const updateSystemSetting = (key, data) => request.put(`/system-settings/${key}`, data)
export const resetSystemSettings = () => request.post('/system-settings/reset')