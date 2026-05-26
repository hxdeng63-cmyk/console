import request from './index'

export const getOrgs = (params) => request.get('/organizations', { params })
export const getOrg = (id) => request.get(`/organizations/${id}`)
export const createOrg = (data) => request.post('/organizations', data)
export const updateOrg = (id, data) => request.put(`/organizations/${id}`, data)
export const deleteOrg = (id) => request.delete(`/organizations/${id}`)
export const getOrgTree = () => request.get('/organizations/tree')
export const getOrgUsers = (id, params) => request.get(`/organizations/${id}/users`, { params })
export const addOrgUsers = (id, data) => request.post(`/organizations/${id}/users`, data)
export const removeOrgUsers = (id, data) => request.delete(`/organizations/${id}/users`, data)