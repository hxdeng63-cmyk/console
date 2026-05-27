import request from './index'

export const getRoles = (params) => request.get('/roles', { params })
export const getRole = (id) => request.get(`/roles/${id}`)
export const createRole = (data) => request.post('/roles', data)
export const updateRole = (id, data) => request.put(`/roles/${id}`, data)
export const deleteRole = (id) => request.delete(`/roles/${id}`)
export const getRoleUsers = (id, params) => request.get(`/roles/${id}/users`, { params })
export const getRoleMenus = (id) => request.get(`/roles/${id}/menus`)
export const setRoleMenus = (id, data) => request.put(`/roles/${id}/menus`, data)
export const getRoleResources = (id) => request.get(`/roles/${id}/resources`)
export const setRoleResources = (id, data) => request.put(`/roles/${id}/resources`, data)