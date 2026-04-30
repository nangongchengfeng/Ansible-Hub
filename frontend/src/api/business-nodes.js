import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformNodeFromBackend = (node) => {
  const transformed = {
    ...node,
    parentId: node.parent_id,
    gatewayId: node.gateway_id,
    createdAt: node.created_at,
    updatedAt: node.updated_at,
    createdBy: node.created_by,
    permissions: {} // 权限暂时单独处理
  }
  // 递归转换子节点
  if (node.children && node.children.length > 0) {
    transformed.children = node.children.map(transformNodeFromBackend)
  }
  return transformed
}

export const getBusinessNodes = async () => {
  const res = await request.get('/business-nodes/tree')
  return {
    ...res,
    data: res.data.map(transformNodeFromBackend)
  }
}

export const getBusinessNodesList = async (params) => {
  const backendParams = {}
  if (params?.parentId !== undefined) {
    backendParams.parent_id = params.parentId
  }
  const res = await request.get('/business-nodes', { params: backendParams })
  return {
    ...res,
    total: res.data.total,
    data: res.data.items.map(transformNodeFromBackend)
  }
}

export const getGateways = () => {
  // TODO: 网关API对接
  return Promise.resolve({ data: [] })
}

export const createBusinessNode = (data) => {
  return request.post('/business-nodes', {
    name: data.name,
    description: data.description,
    parent_id: data.parentId,
    gateway_id: data.gatewayId
  })
}

export const updateBusinessNode = (id, data) => {
  return request.put(`/business-nodes/${id}`, {
    name: data.name,
    description: data.description,
    parent_id: data.parentId,
    gateway_id: data.gatewayId
  })
}

export const deleteBusinessNode = (id) => {
  return request.delete(`/business-nodes/${id}`)
}

export const updateNodePermissions = (id, permissions) => {
  // TODO: 权限API需要根据实际后端调整
  return request.put(`/business-nodes/${id}/permissions`, { permissions: [] })
}
