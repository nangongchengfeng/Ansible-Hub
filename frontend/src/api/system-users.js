import request from '@/utils/request'
import { mockGetSystemUsers, mockCreateSystemUser, mockUpdateSystemUser, mockDeleteSystemUser } from '@/utils/mock'

const useMock = true

export const getSystemUsers = () => {
  if (useMock) return mockGetSystemUsers()
  return request.get('/system-users')
}

export const createSystemUser = (data) => {
  if (useMock) return mockCreateSystemUser(data)
  return request.post('/system-users', data)
}

export const updateSystemUser = (id, data) => {
  if (useMock) return mockUpdateSystemUser(id, data)
  return request.put(`/system-users/${id}`, data)
}

export const deleteSystemUser = (id) => {
  if (useMock) return mockDeleteSystemUser(id)
  return request.delete(`/system-users/${id}`)
}
