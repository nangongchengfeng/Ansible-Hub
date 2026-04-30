import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformScriptFromBackend = (item) => ({
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
const transformScriptToBackend = (data) => ({
  name: data.name,
  description: data.description,
  content: data.content,
  change_description: data.changeNote
})

export const getScripts = async (params) => {
  const res = await request.get('/scripts', { params })
  return {
    total: res.data.total,
    data: (res.data.items || []).map(transformScriptFromBackend)
  }
}

export const createScript = (data) => {
  return request.post('/scripts', transformScriptToBackend(data))
}

export const getScript = async (id) => {
  const res = await request.get(`/scripts/${id}`)
  return {
    data: transformScriptFromBackend(res.data)
  }
}

export const updateScript = (id, data) => {
  return request.put(`/scripts/${id}`, transformScriptToBackend(data))
}

export const deleteScript = (id) => {
  return request.delete(`/scripts/${id}`)
}

export const getScriptVersions = async (id, params) => {
  const res = await request.get(`/scripts/${id}/versions`, { params })
  return {
    total: res.data.total,
    data: (res.data.items || []).map(transformVersionFromBackend)
  }
}

export const getScriptVersion = async (scriptId, version) => {
  const res = await request.get(`/scripts/${scriptId}/versions/${version}`)
  return {
    data: transformVersionFromBackend(res.data)
  }
}

export const compareScriptVersions = async (scriptId, version1, version2) => {
  const res = await request.get(`/scripts/${scriptId}/versions/${version1}/diff/${version2}`)
  return { data: res.data }
}

export const rollbackScript = (scriptId, data) => {
  return request.post(`/scripts/${scriptId}/rollback`, data)
}
