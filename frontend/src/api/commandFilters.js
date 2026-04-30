import request from '@/utils/request'

export const getCommandFilters = async () => {
  // TODO: 对接真实API
  return { data: [] }
}

export const createCommandFilter = (data) => {
  return request.post('/command-filters', data)
}

export const updateCommandFilter = (id, data) => {
  return request.put(`/command-filters/${id}`, data)
}

export const deleteCommandFilter = (id) => {
  return request.delete(`/command-filters/${id}`)
}

export const toggleCommandFilter = (id) => {
  return request.patch(`/command-filters/${id}/toggle`)
}

export const moveCommandFilter = (id, direction) => {
  return request.patch(`/command-filters/${id}/move`, { direction })
}
