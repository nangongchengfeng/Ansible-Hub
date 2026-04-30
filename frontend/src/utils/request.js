import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const authStore = useAuthStore()
    if (error.response) {
      const { status, data } = error.response
      // 兼容后端返回的 detail 或 message 字段
      const errorMsg = data?.detail || data?.message || '请求失败'
      switch (status) {
        case 401:
          ElMessage.error(errorMsg || '登录已过期，请重新登录')
          authStore.clearAuth()
          router.push({ name: 'login' })
          break
        case 403:
          ElMessage.error(errorMsg || '没有权限执行此操作')
          break
        case 404:
          ElMessage.error(errorMsg || '请求的资源不存在')
          break
        case 500:
          ElMessage.error(errorMsg || '服务器错误')
          break
        default:
          ElMessage.error(errorMsg)
      }
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default request
