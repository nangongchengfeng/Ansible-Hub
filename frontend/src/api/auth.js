import request from '@/utils/request'
import { mockLogin, mockLogout, mockGetCurrentUser } from '@/utils/mock'

// 使用 Mock API（后端完成前）
const useMock = true

export const login = (data) => {
  if (useMock) return mockLogin(data)
  return request.post('/auth/login', data)
}

export const logout = () => {
  if (useMock) return mockLogout()
  return request.post('/auth/logout')
}

export const getCurrentUser = () => {
  if (useMock) return mockGetCurrentUser()
  return request.get('/auth/me')
}

export const refreshToken = (data) => {
  return request.post('/auth/refresh', data)
}
