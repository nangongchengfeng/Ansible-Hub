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
  // 转换前端参数名到后端
  const backendParams = {}
  if (params?.businessNodeId) {
    backendParams.business_node_id = params.businessNodeId
  }
  if (params?.isEnabled !== undefined) {
    backendParams.is_enabled = params.isEnabled
  }
  if (params?.search) {
    backendParams.search = params.search
  }

  const res = await request.get('/hosts', { params: backendParams })
  return {
    ...res,
    data: res.data.map(transformFromBackend)
  }
}

export const createHost = (data) => {
  return request.post('/hosts', transformToBackend(data))
}

export const getHost = async (id) => {
  const res = await request.get(`/hosts/${id}`)
  return {
    ...res,
    data: transformFromBackend(res.data)
  }
}

export const updateHost = (id, data) => {
  return request.put(`/hosts/${id}`, transformToBackend(data))
}

export const toggleHost = (id) => {
  return request.patch(`/hosts/${id}/toggle`)
}

export const moveHost = (id, targetBusinessNodeId) => {
  return request.post(`/hosts/${id}/move`, {
    target_business_node_id: targetBusinessNodeId
  })
}

export const deleteHost = (id) => {
  return request.delete(`/hosts/${id}`)
}
