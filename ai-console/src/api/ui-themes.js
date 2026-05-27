import request from './index'

export const getUIThemes = (params = {}) => {
  const { pageNo = 1, pageSize = 10 } = params
  return request.get('/ui-themes', {
    params: {
      page: pageNo,
      page_size: pageSize
    }
  })
}

export const getUITheme = (id) => request.get(`/ui-themes/${id}`)

export const createUITheme = (data) => request.post('/ui-themes', data)

export const updateUITheme = (id, data) => request.put(`/ui-themes/${id}`, data)

export const deleteUITheme = (id) => request.delete(`/ui-themes/${id}`)

export const activateUITheme = (id) => request.post(`/ui-themes/${id}/activate`)
