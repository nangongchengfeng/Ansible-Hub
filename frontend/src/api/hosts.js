import request from '@/utils/request'

// 字段转换
const transformFromBackend = (item) => ({
  ...item,
  businessNodeId: item.business_node_id,
  createdAt: item.created_at,
  updatedAt: item.updated_at
})

export const getHosts = async (params) => {
  // TODO: 对接真实API
  return { data: [], total: 0 }
}

export const createHost = (data) => {
  return request.post('/hosts', {
    ...data,
    business_node_id: data.businessNodeId
  })
}

export const updateHost = (id, data) => {
  return request.put(`/hosts/${id}`, {
    ...data,
    business_node_id: data.businessNodeId
  })
}

export const deleteHost = (id) => {
  return request.delete(`/hosts/${id}`)
}

export const toggleHost = (id) => {
  return request.patch(`/hosts/${id}/toggle`)
}
