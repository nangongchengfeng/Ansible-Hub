import request from '@/utils/request'
import { mockGetJobHistory, mockGetJobDetail, mockGetJobLogs, mockRedoJob } from '@/utils/mock'

const useMock = true

export const getJobHistory = (params) => {
  if (useMock) return mockGetJobHistory(params)
  return request.get('/job-history', { params })
}

export const getJobDetail = (id) => {
  if (useMock) return mockGetJobDetail(id)
  return request.get(`/job-history/${id}`)
}

export const getJobLogs = (id) => {
  if (useMock) return mockGetJobLogs(id)
  return request.get(`/job-history/${id}/logs`)
}

export const redoJob = (id) => {
  if (useMock) return mockRedoJob(id)
  return request.post(`/job-history/${id}/redo`)
}
