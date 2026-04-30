import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformFromBackend = (item) => ({
  ...item,
  isEnabled: item.is_enabled,
  matchType: item.match_type,
  createdAt: item.created_at,
  updatedAt: item.updated_at,
  createdBy: item.created_by
})

// 字段转换：前端 -> 后端
const transformToBackend = (data) => ({
  name: data.name,
  description: data.description,
  match_type: data.matchType,
  pattern: data.pattern,
  action: data.action,
  priority: data.priority,
  is_enabled: data.isEnabled
})

export const getCommandFilters = async (params) => {
  const backendParams = {}
  if (params?.isEnabled !== undefined) {
    backendParams.is_enabled = params.isEnabled
  }
  if (params?.matchType) {
    backendParams.match_type = params.matchType
  }

  const res = await request.get('/command-filter-rules', { params: backendParams })
  return {
    total: res.data.total,
    data: (res.data.items || []).map(transformFromBackend)
  }
}

export const createCommandFilter = (data) => {
  return request.post('/command-filter-rules', transformToBackend(data))
}

export const getCommandFilter = async (id) => {
  const res = await request.get(`/command-filter-rules/${id}`)
  return {
    data: transformFromBackend(res.data)
  }
}

export const updateCommandFilter = (id, data) => {
  return request.put(`/command-filter-rules/${id}`, transformToBackend(data))
}

export const deleteCommandFilter = (id) => {
  return request.delete(`/command-filter-rules/${id}`)
}

export const toggleCommandFilter = (id) => {
  return request.patch(`/command-filter-rules/${id}/toggle`)
}

export const reorderCommandFilters = (order) => {
  return request.put('/command-filter-rules/reorder', { order })
}

export const checkCommand = (command) => {
  return request.post('/command-filter-rules/check', { command })
}
