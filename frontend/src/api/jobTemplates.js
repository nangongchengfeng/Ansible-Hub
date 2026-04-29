import request from '@/utils/request'
import { mockGetJobTemplates, mockCreateJobTemplate, mockUpdateJobTemplate, mockDeleteJobTemplate, mockToggleJobTemplate, mockTriggerJobTemplate, mockUpdateTemplatePermissions } from '@/utils/mock'

const useMock = true

export const getJobTemplates = () => {
  if (useMock) return mockGetJobTemplates()
  return request.get('/job-templates')
}

export const createJobTemplate = (data) => {
  if (useMock) return mockCreateJobTemplate(data)
  return request.post('/job-templates', data)
}

export const updateJobTemplate = (id, data) => {
  if (useMock) return mockUpdateJobTemplate(id, data)
  return request.put(`/job-templates/${id}`, data)
}

export const deleteJobTemplate = (id) => {
  if (useMock) return mockDeleteJobTemplate(id)
  return request.delete(`/job-templates/${id}`)
}

export const toggleJobTemplate = (id) => {
  if (useMock) return mockToggleJobTemplate(id)
  return request.patch(`/job-templates/${id}/toggle`)
}

export const triggerJobTemplate = (id) => {
  if (useMock) return mockTriggerJobTemplate(id)
  return request.post(`/job-templates/${id}/trigger`)
}

export const updateTemplatePermissions = (id, permissions) => {
  if (useMock) return mockUpdateTemplatePermissions(id, permissions)
  return request.put(`/job-templates/${id}/permissions`, { permissions })
}
