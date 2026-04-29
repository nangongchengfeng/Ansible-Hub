import request from '@/utils/request'
import { mockGetBusinessNodes, mockGetGateways, mockCreateBusinessNode } from '@/utils/mock'

const useMock = true

export const getBusinessNodes = () => {
  if (useMock) return mockGetBusinessNodes()
  return request.get('/business-nodes')
}

export const getGateways = () => {
  if (useMock) return mockGetGateways()
  return request.get('/gateways')
}

export const createBusinessNode = (data) => {
  if (useMock) return mockCreateBusinessNode(data)
  return request.post('/business-nodes', data)
}

export const updateBusinessNode = (id, data) => {
  return request.put(`/business-nodes/${id}`, data)
}

export const deleteBusinessNode = (id) => {
  return request.delete(`/business-nodes/${id}`)
}

export const updateNodePermissions = (id, permissions) => {
  return request.put(`/business-nodes/${id}/permissions`, { permissions })
}
