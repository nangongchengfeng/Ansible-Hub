import request from '@/utils/request'

export const getSystemUsers = async () => {
  // TODO: 对接真实API
  return { data: [] }
}

export const createSystemUser = (data) => {
  return request.post('/system-users', data)
}

export const updateSystemUser = (id, data) => {
  return request.put(`/system-users/${id}`, data)
}

export const deleteSystemUser = (id) => {
  return request.delete(`/system-users/${id}`)
}
