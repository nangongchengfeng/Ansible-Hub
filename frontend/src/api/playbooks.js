import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformPlaybookFromBackend = (item) => ({
  ...item,
  currentVersion: item.latest_version,
  createdAt: item.created_at,
  updatedAt: item.updated_at,
  createdBy: item.created_by,
  content: item.current_content || item.content
})

const transformVersionFromBackend = (item) => ({
  ...item,
  changeNote: item.change_description,
  createdAt: item.created_at,
  createdBy: item.created_by
})

// 字段转换：前端 -> 后端
const transformPlaybookToBackend = (data) => ({
  name: data.name,
  description: data.description,
  content: data.content,
  change_description: data.changeNote
})

export const getPlaybooks = async (params) => {
  const res = await request.get('/playbooks', { params })
  return {
    total: res.data.total,
    data: (res.data.items || []).map(transformPlaybookFromBackend)
  }
}

export const createPlaybook = (data) => {
  return request.post('/playbooks', transformPlaybookToBackend(data))
}

export const getPlaybook = async (id) => {
  const res = await request.get(`/playbooks/${id}`)
  return {
    data: transformPlaybookFromBackend(res.data)
  }
}

export const updatePlaybook = (id, data) => {
  return request.put(`/playbooks/${id}`, transformPlaybookToBackend(data))
}

export const deletePlaybook = (id) => {
  return request.delete(`/playbooks/${id}`)
}

export const getPlaybookVersions = async (id, params) => {
  const res = await request.get(`/playbooks/${id}/versions`, { params })
  return {
    total: res.data.total,
    data: (res.data.items || []).map(transformVersionFromBackend)
  }
}

export const getPlaybookVersion = async (playbookId, version) => {
  const res = await request.get(`/playbooks/${playbookId}/versions/${version}`)
  return {
    data: transformVersionFromBackend(res.data)
  }
}

export const comparePlaybookVersions = async (playbookId, version1, version2) => {
  const res = await request.get(`/playbooks/${playbookId}/versions/${version1}/diff/${version2}`)
  return { data: res.data }
}

export const rollbackPlaybook = (playbookId, data) => {
  return request.post(`/playbooks/${playbookId}/rollback`, data)
}
