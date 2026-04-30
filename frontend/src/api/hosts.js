import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformFromBackend = (item) => ({
  ...item,
  hostname: item.ip_external || item.ip_internal,
  port: item.ssh_port,
  businessNodeId: item.business_node_id,
  systemUserId: item.system_user_id,
  gatewayId: item.gateway_id,
  enabled: item.is_enabled,
  status: item.last_connection_status,
  createdAt: item.created_at,
  updatedAt: item.updated_at
})

// 字段转换：前端 -> 后端
const transformToBackend = (data) => ({
  name: data.name,
  business_node_id: data.businessNodeId,
  ip_external: data.hostname,
  ip_preference: data.hostname ? 'external' : 'internal',
  ssh_port: data.port,
  system_user_id: data.systemUserId,
  gateway_id: data.gatewayId
})

export const getHosts = async (params) => {
  const res = await request.get('/hosts', { params })
  return {
    ...res,
    data: res.data.map(transformFromBackend)
  }
}

export const createHost = (data) => {
  return request.post('/hosts', transformToBackend(data))
}

export const updateHost = (id, data) => {
  return request.put(`/hosts/${id}`, transformToBackend(data))
}

export const deleteHost = (id) => {
  return request.delete(`/hosts/${id}`)
}

export const toggleHost = async (id) => {
  const res = await request.get(`/hosts/${id}`)
  const current = res.data
  await request.put(`/hosts/${id}`, { is_enabled: !current.is_enabled })
  return { data: { enabled: !current.is_enabled } }
}
