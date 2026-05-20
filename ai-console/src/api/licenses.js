import request from './index'

export const getLicenses = (params) => request.get('/licenses', { params })
export const getLicense = (id) => request.get(`/licenses/${id}`)
export const uploadLicense = (data) => request.post('/licenses', data)
export const deleteLicense = (id) => request.delete(`/licenses/${id}`)
export const getLicenseInfo = () => request.get('/licenses/info')
export const verifyLicense = (data) => request.post('/licenses/verify', data)