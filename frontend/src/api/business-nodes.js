import request from '@/utils/request'
import { mockGetBusinessNodes, mockGetGateways, mockCreateBusinessNode, mockUpdateBusinessNode, mockDeleteBusinessNode, mockUpdateNodePermissions, mockCreateGateway, mockUpdateGateway, mockDeleteGateway } from '@/utils/mock'

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
  if (useMock) return mockUpdateBusinessNode(id, data)
  return request.put(`/business-nodes/${id}`, data)
}

export const deleteBusinessNode = (id) => {
  if (useMock) return mockDeleteBusinessNode(id)
  return request.delete(`/business-nodes/${id}`)
}

export const updateNodePermissions = (id, permissions) => {
  if (useMock) return mockUpdateNodePermissions(id, permissions)
  return request.put(`/business-nodes/${id}/permissions`, { permissions })
}
