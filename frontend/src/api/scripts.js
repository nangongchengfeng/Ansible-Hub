import request from '@/utils/request'

export const getScripts = async () => {
  // TODO: 对接真实API
  return { data: [] }
}

export const createScript = (data) => {
  return request.post('/scripts', data)
}

export const updateScript = (id, data) => {
  return request.put(`/scripts/${id}`, data)
}

export const deleteScript = (id) => {
  return request.delete(`/scripts/${id}`)
}

export const getScriptVersions = async (id) => {
  // TODO: 对接真实API
  return { data: [] }
}

export const getScriptVersion = async (scriptId, versionId) => {
  // TODO: 对接真实API
  return { data: null }
}

export const rollbackScript = (scriptId, versionId) => {
  return request.post(`/scripts/${scriptId}/rollback/${versionId}`)
}
