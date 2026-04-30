import request from '@/utils/request'

export const getGateways = async () => {
  // TODO: 对接真实API
  return { data: [] }
}

export const createGateway = (data) => {
  return request.post('/gateways', data)
}

export const updateGateway = (id, data) => {
  return request.put(`/gateways/${id}`, data)
}

export const deleteGateway = (id) => {
  return request.delete(`/gateways/${id}`)
}
