import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformFromBackend = (item) => ({
  ...item,
  host: item.ip,
  systemUserId: item.system_user_id,
  createdAt: item.created_at,
  updatedAt: item.updated_at
})

// 字段转换：前端 -> 后端
const transformToBackend = (data) => ({
  name: data.name,
  ip: data.host,
  port: data.port,
  system_user_id: data.systemUserId
})

export const getGateways = async () => {
  const res = await request.get('/gateways')
  return {
    ...res,
    data: res.data.map(transformFromBackend)
  }
}

export const createGateway = (data) => {
  return request.post('/gateways', transformToBackend(data))
}

export const updateGateway = (id, data) => {
  return request.put(`/gateways/${id}`, transformToBackend(data))
}

export const deleteGateway = (id) => {
  return request.delete(`/gateways/${id}`)
}
