import request from './index'

export const getOrgs = (params) => request.get('/orgs', { params })
export const getOrg = (id) => request.get(`/orgs/${id}`)
export const createOrg = (data) => request.post('/orgs', data)
export const updateOrg = (id, data) => request.put(`/orgs/${id}`, data)
export const deleteOrg = (id) => request.delete(`/orgs/${id}`)
export const getOrgTree = () => request.get('/orgs/tree')
export const getOrgUsers = (id, params) => request.get(`/orgs/${id}/users`, { params })
export const addOrgUsers = (id, data) => request.post(`/orgs/${id}/users`, data)
export const removeOrgUsers = (id, data) => request.delete(`/orgs/${id}/users`, data)