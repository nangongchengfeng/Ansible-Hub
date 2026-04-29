import request from '@/utils/request'
import {
  mockGetUsers,
  mockCreateUser,
  mockUpdateUser,
  mockDeleteUser,
  mockResetUserPassword
} from '@/utils/mock'

const useMock = true

export const getUsers = () => {
  if (useMock) return mockGetUsers()
  return request.get('/users')
}

export const createUser = (data) => {
  if (useMock) return mockCreateUser(data)
  return request.post('/users', data)
}

export const updateUser = (id, data) => {
  if (useMock) return mockUpdateUser(id, data)
  return request.put(`/users/${id}`, data)
}

export const deleteUser = (id) => {
  if (useMock) return mockDeleteUser(id)
  return request.delete(`/users/${id}`)
}

export const resetUserPassword = (id, newPassword) => {
  if (useMock) return mockResetUserPassword(id, newPassword)
  return request.post(`/users/${id}/reset-password`, { newPassword })
}
