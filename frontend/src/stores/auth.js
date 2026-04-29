import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, getCurrentUser } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const refreshToken = ref(localStorage.getItem('refreshToken') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const loading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  const setToken = (newToken, newRefreshToken) => {
    token.value = newToken
    refreshToken.value = newRefreshToken
    localStorage.setItem('token', newToken)
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken)
    }
  }

  const setUser = (newUser) => {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
  }

  const clearAuth = () => {
    token.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  const login = async (credentials) => {
    loading.value = true
    try {
      const response = await loginApi(credentials)
      setToken(response.data.access_token, response.data.refresh_token)
      await fetchCurrentUser()
      return response
    } finally {
      loading.value = false
    }
  }

  const fetchCurrentUser = async () => {
    try {
      const response = await getCurrentUser()
      setUser(response.data)
    } catch (error) {
      clearAuth()
      throw error
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      await logoutApi()
    } finally {
      clearAuth()
      loading.value = false
    }
  }

  return {
    token,
    refreshToken,
    user,
    loading,
    isAuthenticated,
    setToken,
    setUser,
    clearAuth,
    login,
    fetchCurrentUser,
    logout
  }
})
