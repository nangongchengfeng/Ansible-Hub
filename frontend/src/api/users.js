import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformUserFromBackend = (user) => ({
  ...user,
  name: user.real_name,
  createdAt: user.created_at
})

export const getUsers = async () => {
  const res = await request.get('/users')
  return {
    ...res,
    data: res.data.items.map(transformUserFromBackend)
  }
}

export const createUser = (data) => {
  return request.post('/users', {
    username: data.username,
    email: data.email,
    name: data.name,
    role: data.role,
    password: data.password
  })
}

export const updateUser = (id, data) => {
  return request.put(`/users/${id}`, {
    name: data.name,
    email: data.email,
    role: data.role
  })
}

export const deleteUser = (id) => {
  return request.delete(`/users/${id}`)
}

export const resetUserPassword = (id, newPassword) => {
  return request.post(`/users/${id}/reset-password`, { newPassword })
}
