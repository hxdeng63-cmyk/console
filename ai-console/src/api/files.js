import request from './index'

export const getFiles = (params) => request.get('/file-records', { params })
export const getFile = (id) => request.get(`/file-records/${id}`)
export const uploadFile = (data) => request.post('/file-records', data)
export const deleteFile = (id) => request.delete(`/file-records/${id}`)
export const downloadFile = (id, filename) => {
  return request.post(`/file-records/${id}/download`).then(data => {
    const url = data?.url
    const name = filename || data?.file_name || 'download'
    if (!url) {
      throw new Error('下载链接为空')
    }
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  })
}
export const getFileUrl = (id) => request.get(`/file-records/${id}/url`)
export const batchDeleteFiles = (data) => request.post('/file-records/batch-delete', data)
export const getFileTree = (params) => request.get('/file-records/tree', { params })
