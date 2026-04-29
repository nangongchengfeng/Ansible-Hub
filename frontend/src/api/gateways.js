import request from '@/utils/request'
import { mockGetGateways, mockCreateGateway, mockUpdateGateway, mockDeleteGateway } from '@/utils/mock'

const useMock = true

export const getGateways = () => {
  if (useMock) return mockGetGateways()
  return request.get('/gateways')
}

export const createGateway = (data) => {
  if (useMock) return mockCreateGateway(data)
  return request.post('/gateways', data)
}

export const updateGateway = (id, data) => {
  if (useMock) return mockUpdateGateway(id, data)
  return request.put(`/gateways/${id}`, data)
}

export const deleteGateway = (id) => {
  if (useMock) return mockDeleteGateway(id)
  return request.delete(`/gateways/${id}`)
}
