import request from './index'

export const getFiles = (params) => request.get('/files', { params })
export const getFile = (id) => request.get(`/files/${id}`)
export const uploadFile = (data) => request.post('/files', data)
export const deleteFile = (id) => request.delete(`/files/${id}`)
export const downloadFile = (id, filename) => {
  return request.get(`/files/${id}/download`, { responseType: 'blob' }).then(blob => {
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'download'
    a.click()
    window.URL.revokeObjectURL(url)
  })
}
export const getFileUrl = (id) => request.get(`/files/${id}/url`)
export const batchDeleteFiles = (data) => request.post('/files/batch-delete', data)