import request from './index'

export const getPopupSettings = () => request.get('/popup-settings')
export const createPopupSetting = (data) => request.post('/popup-settings', data)
export const updatePopupSetting = (id, data) => request.put(`/popup-settings/${id}`, data)
export const deletePopupSetting = (id) => request.delete(`/popup-settings/${id}`)
