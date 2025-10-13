import axios from 'axios'
import { ElMessage } from 'element-plus'

// Create axios instance
let API_BASE = import.meta?.env?.VITE_API_BASE
if (import.meta?.env?.DEV) {
  // In dev, backend runs on 8000 by default
  API_BASE = API_BASE || 'http://localhost:8000'
} else {
  // In prod, default to same-origin if not explicitly set
  if (!API_BASE) {
    if (typeof window !== 'undefined' && window.location && window.location.origin) {
      API_BASE = window.location.origin
    } else {
      API_BASE = 'http://localhost:8000'
    }
  }
}
const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 增加到120秒，处理大型请求
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('Response error:', error)
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          ElMessage.error(data.detail || '请求参数错误')
          break
        case 401:
          ElMessage.error('未授权访问')
          break
        case 403:
          ElMessage.error('访问被拒绝')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error(data.detail || '服务器内部错误')
          break
        default:
          ElMessage.error(data.detail || `请求失败 (${status})`)
      }
    } else if (error.request) {
      // Network error
      ElMessage.error('网络连接失败，请检查网络设置')
    } else {
      // Other error
      ElMessage.error('请求失败，请重试')
    }
    
    return Promise.reject(error)
  }
)

export default api
