import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE_URL = 'http://localhost:8080/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
        ElMessage.error('登录已过期，请重新登录')
      } else if (status === 403) {
        ElMessage.error('权限不足')
      } else if (status === 422) {
        const detail = data?.detail
        if (Array.isArray(detail)) {
          ElMessage.error(detail.map((d) => d.msg).join(', '))
        } else {
          ElMessage.error(detail || '请求参数错误')
        }
      } else {
        ElMessage.error(data?.message || data?.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查连接')
    }
    return Promise.reject(error)
  }
)

export default apiClient

// Device Group APIs
export const getDeviceList = (params) => apiClient.get('/devices/', { params })
export const getDeviceGroupTree = () => apiClient.get('/device-groups/tree')
export const createDeviceGroup = (data) => apiClient.post('/device-groups/', data)
export const updateDeviceGroup = (id, data) => apiClient.put(`/device-groups/${id}`, data)
export const deleteDeviceGroup = (id) => apiClient.delete(`/device-groups/${id}`)

// Access Platform APIs (Gb28181, Onvif)
export const getAccessPlatforms = (params) => apiClient.get('/access-platforms/', { params })
export const createAccessPlatform = (data) => apiClient.post('/access-platforms/', data)
export const updateAccessPlatform = (id, data) => apiClient.put(`/access-platforms/${id}`, data)
export const deleteAccessPlatform = (id) => apiClient.delete(`/access-platforms/${id}`)

// Linkage Rule APIs
export const getLinkageRules = (params) => apiClient.get('/linkage-rules/', { params })
export const createLinkageRule = (data) => apiClient.post('/linkage-rules/', data)
export const updateLinkageRule = (id, data) => apiClient.put(`/linkage-rules/${id}`, data)
export const deleteLinkageRule = (id) => apiClient.delete(`/linkage-rules/${id}`)

// Push History APIs
export const getPushHistories = (params) => apiClient.get('/push-histories/', { params })

// Algorithm Service APIs
export const getAlgorithmServices = (params) => apiClient.get('/algorithm-services/', { params })
export const createAlgorithmService = (data) => apiClient.post('/algorithm-services/', data)
export const updateAlgorithmService = (id, data) => apiClient.put(`/algorithm-services/${id}`, data)
export const deleteAlgorithmService = (id) => apiClient.delete(`/algorithm-services/${id}`)

// Video Setting (Record Rules) APIs
export const getRecordRules = (params) => apiClient.get('/record-rules/', { params })
export const createRecordRule = (data) => apiClient.post('/record-rules/', data)
export const updateRecordRule = (id, data) => apiClient.put(`/record-rules/${id}`, data)
export const deleteRecordRule = (id) => apiClient.delete(`/record-rules/${id}`)

// File Manager APIs
export const getFileRecords = (params) => apiClient.get('/file-records/', { params })
export const deleteFileRecord = (id) => apiClient.delete(`/file-records/${id}`)

// Dispose Tag APIs
export const getDisposeTags = (params) => apiClient.get('/dispose-tags/', { params })
export const createDisposeTag = (data) => apiClient.post('/dispose-tags/', data)
export const updateDisposeTag = (id, data) => apiClient.put(`/dispose-tags/${id}`, data)
export const deleteDisposeTag = (id) => apiClient.delete(`/dispose-tags/${id}`)