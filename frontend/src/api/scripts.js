import request from '@/utils/request'

export const getScripts = async () => {
  // TODO: 等后端API完成后对接
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
  return { data: [] }
}

export const getScriptVersion = async (scriptId, versionId) => {
  return { data: null }
}

export const rollbackScript = (scriptId, versionId) => {
  return request.post(`/scripts/${scriptId}/rollback/${versionId}`)
}
