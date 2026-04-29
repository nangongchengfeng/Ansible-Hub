import request from '@/utils/request'
import { mockGetHosts, mockCreateHost, mockUpdateHost, mockDeleteHost, mockToggleHost } from '@/utils/mock'

const useMock = true

export const getHosts = (params) => {
  if (useMock) return mockGetHosts(params)
  return request.get('/hosts', { params })
}

export const createHost = (data) => {
  if (useMock) return mockCreateHost(data)
  return request.post('/hosts', data)
}

export const updateHost = (id, data) => {
  if (useMock) return mockUpdateHost(id, data)
  return request.put(`/hosts/${id}`, data)
}

export const deleteHost = (id) => {
  if (useMock) return mockDeleteHost(id)
  return request.delete(`/hosts/${id}`)
}

export const toggleHost = (id) => {
  if (useMock) return mockToggleHost(id)
  return request.patch(`/hosts/${id}/toggle`)
}
