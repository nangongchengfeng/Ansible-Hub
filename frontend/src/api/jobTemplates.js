import request from '@/utils/request'

export const getJobTemplates = async () => {
  // TODO: 对接真实API
  return { data: [] }
}

export const createJobTemplate = (data) => {
  return request.post('/job-templates', data)
}

export const updateJobTemplate = (id, data) => {
  return request.put(`/job-templates/${id}`, data)
}

export const deleteJobTemplate = (id) => {
  return request.delete(`/job-templates/${id}`)
}

export const toggleJobTemplate = (id) => {
  return request.patch(`/job-templates/${id}/toggle`)
}

export const triggerJobTemplate = (id) => {
  return request.post(`/job-templates/${id}/trigger`)
}

export const updateTemplatePermissions = (id, permissions) => {
  return request.put(`/job-templates/${id}/permissions`, { permissions })
}
