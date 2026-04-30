import request from '@/utils/request'

export const getJobHistory = async (params) => {
  // TODO: 对接真实API
  return { data: [], total: 0 }
}

export const getJobDetail = async (id) => {
  // TODO: 对接真实API
  return { data: null }
}

export const getJobLogs = async (id) => {
  // TODO: 对接真实API
  return { data: '' }
}

export const redoJob = (id) => {
  return request.post(`/job-history/${id}/redo`)
}
