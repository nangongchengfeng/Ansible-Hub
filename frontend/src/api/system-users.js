import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformFromBackend = (item) => ({
  ...item,
  authType: item.auth_type === 'private_key' ? 'key' : 'password',
  privateKey: item.private_key || '',
  createdBy: item.created_by,
  createdAt: item.created_at,
  updatedAt: item.updated_at
})

// 字段转换：前端 -> 后端
const transformToBackend = (data) => ({
  name: data.name,
  username: data.username,
  auth_type: data.authType === 'key' ? 'private_key' : 'password',
  password: data.password,
  private_key: data.privateKey
})

export const getSystemUsers = async () => {
  const res = await request.get('/system-users')
  return {
    ...res,
    data: res.data.map(transformFromBackend)
  }
}

export const createSystemUser = (data) => {
  return request.post('/system-users', transformToBackend(data))
}

export const updateSystemUser = (id, data) => {
  return request.put(`/system-users/${id}`, transformToBackend(data))
}

export const deleteSystemUser = (id) => {
  return request.delete(`/system-users/${id}`)
}
