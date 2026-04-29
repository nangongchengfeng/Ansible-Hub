import request from '@/utils/request'
import { mockGetPlaybooks, mockCreatePlaybook, mockUpdatePlaybook, mockDeletePlaybook, mockGetPlaybookVersions, mockGetPlaybookVersion, mockRollbackPlaybook } from '@/utils/mock'

const useMock = true

export const getPlaybooks = () => {
  if (useMock) return mockGetPlaybooks()
  return request.get('/playbooks')
}

export const createPlaybook = (data) => {
  if (useMock) return mockCreatePlaybook(data)
  return request.post('/playbooks', data)
}

export const updatePlaybook = (id, data) => {
  if (useMock) return mockUpdatePlaybook(id, data)
  return request.put(`/playbooks/${id}`, data)
}

export const deletePlaybook = (id) => {
  if (useMock) return mockDeletePlaybook(id)
  return request.delete(`/playbooks/${id}`)
}

export const getPlaybookVersions = (id) => {
  if (useMock) return mockGetPlaybookVersions(id)
  return request.get(`/playbooks/${id}/versions`)
}

export const getPlaybookVersion = (playbookId, versionId) => {
  if (useMock) return mockGetPlaybookVersion(playbookId, versionId)
  return request.get(`/playbooks/${playbookId}/versions/${versionId}`)
}

export const rollbackPlaybook = (playbookId, versionId) => {
  if (useMock) return mockRollbackPlaybook(playbookId, versionId)
  return request.post(`/playbooks/${playbookId}/rollback/${versionId}`)
}
