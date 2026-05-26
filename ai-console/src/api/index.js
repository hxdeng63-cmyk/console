import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000
})

// Request interceptor - add token
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor - handle errors
request.interceptors.response.use(
  response => {
    const res = response.data
    // Support both wrapped {code, data} format and raw REST responses
    if (res.code !== undefined && res.code !== 0) {
      ElMessage.error(res.message || 'Request failed')
      return Promise.reject(new Error(res.message))
    }
    // If wrapped format, return data; otherwise return raw response
    return res.data !== undefined ? res.data : res
  },
  error => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      // Organization permission denied
      ElMessage.error('权限不足，无法访问该资源')
    } else if (error.response?.status === 422) {
      // Validation error
      const detail = error.response?.data?.detail
      if (Array.isArray(detail)) {
        ElMessage.error(detail.map((d) => d.msg).join(', '))
      } else {
        ElMessage.error(detail || '请求参数错误')
      }
    }
    ElMessage.error(error.message || 'Network error')
    return Promise.reject(error)
  }
)

export default request