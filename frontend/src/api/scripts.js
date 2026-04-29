import request from '@/utils/request'
import { mockGetScripts, mockCreateScript, mockUpdateScript, mockDeleteScript, mockGetScriptVersions, mockGetScriptVersion, mockRollbackScript } from '@/utils/mock'

const useMock = true

export const getScripts = () => {
  if (useMock) return mockGetScripts()
  return request.get('/scripts')
}

export const createScript = (data) => {
  if (useMock) return mockCreateScript(data)
  return request.post('/scripts', data)
}

export const updateScript = (id, data) => {
  if (useMock) return mockUpdateScript(id, data)
  return request.put(`/scripts/${id}`, data)
}

export const deleteScript = (id) => {
  if (useMock) return mockDeleteScript(id)
  return request.delete(`/scripts/${id}`)
}

export const getScriptVersions = (id) => {
  if (useMock) return mockGetScriptVersions(id)
  return request.get(`/scripts/${id}/versions`)
}

export const getScriptVersion = (scriptId, versionId) => {
  if (useMock) return mockGetScriptVersion(scriptId, versionId)
  return request.get(`/scripts/${scriptId}/versions/${versionId}`)
}

export const rollbackScript = (scriptId, versionId) => {
  if (useMock) return mockRollbackScript(scriptId, versionId)
  return request.post(`/scripts/${scriptId}/rollback/${versionId}`)
}
