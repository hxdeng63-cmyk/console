import request from './index'

export const getMenus = () => request.get('/menus/tree')

export const getMenu = (id) => request.get(`/menus/${id}`)

export const createMenu = (data) => request.post('/menus', data)

export const updateMenu = (id, data) => request.put(`/menus/${id}`, data)

export const deleteMenu = (id) => request.delete(`/menus/${id}`)

export const getMenuTree = () => request.get('/menus/tree')

export const getMenuButtons = (id) => request.get(`/menus/${id}/buttons`)

export const updateMenuButtons = (id, data) => request.put(`/menus/${id}/buttons`, data)