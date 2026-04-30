import request from '@/utils/request'

export const getPlaybooks = async () => {
  // TODO: 对接真实API
  return { data: [] }
}

export const createPlaybook = (data) => {
  return request.post('/playbooks', data)
}

export const updatePlaybook = (id, data) => {
  return request.put(`/playbooks/${id}`, data)
}

export const deletePlaybook = (id) => {
  return request.delete(`/playbooks/${id}`)
}

export const getPlaybookVersions = async (id) => {
  // TODO: 对接真实API
  return { data: [] }
}

export const getPlaybookVersion = async (playbookId, versionId) => {
  // TODO: 对接真实API
  return { data: null }
}

export const rollbackPlaybook = (playbookId, versionId) => {
  return request.post(`/playbooks/${playbookId}/rollback/${versionId}`)
}
