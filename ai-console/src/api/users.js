import request from './index'

export const getUsers = (params) => request.get('/users', { params })
export const getUser = (id) => request.get(`/users/${id}`)
export const createUser = (data) => request.post('/users', data)
export const updateUser = (id, data) => request.put(`/users/${id}`, data)
export const deleteUser = (id) => request.delete(`/users/${id}`)
export const getUserRoles = (id) => request.get(`/users/${id}/roles`)
export const setUserRoles = (id, data) => request.put(`/users/${id}/roles`, data)
export const getUserPermissions = (id) => request.get(`/users/${id}/permissions`)
export const resetUserPassword = (id) => request.post(`/users/${id}/reset-password`)
export const batchDeleteUsers = (data) => request.post('/users/batch-delete', data)
export const batchUpdateUsers = (data) => request.put('/users/batch-update', data)