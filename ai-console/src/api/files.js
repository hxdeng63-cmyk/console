import request from './index'

export const getFiles = (params) => request.get('/file-records', { params })
export const getFile = (id) => request.get(`/file-records/${id}`)
export const uploadFile = (data) => request.post('/file-records', data)
export const deleteFile = (id) => request.delete(`/file-records/${id}`)
export const downloadFile = (id, filename) => {
  return request.get(`/file-records/${id}/download`, { responseType: 'blob' }).then(blob => {
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename || 'download'
    a.click()
    window.URL.revokeObjectURL(url)
  })
}
export const getFileUrl = (id) => request.get(`/file-records/${id}/url`)
export const batchDeleteFiles = (data) => request.post('/file-records/batch-delete', data)
export const getFileTree = (params) => request.get('/file-records/tree', { params })
