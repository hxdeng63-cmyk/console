import request from './index'

export const getHelpArticles = (params) => request.get('/help/articles', { params })
export const getHelpArticle = (id) => request.get(`/help/articles/${id}`)
export const createHelpArticle = (data) => request.post('/help/articles', data)
export const updateHelpArticle = (id, data) => request.put(`/help/articles/${id}`, data)
export const deleteHelpArticle = (id) => request.delete(`/help/articles/${id}`)
export const getHelpCategories = () => request.get('/help/categories')
export const searchHelp = (keyword) => request.get('/help/search', { params: { keyword } })