import request from '@/utils/request'
import { mockGetAuditLogs, mockGetAuditLogDetail } from '@/utils/mock'

const useMock = true

export const getAuditLogs = (params) => {
  if (useMock) return mockGetAuditLogs(params)
  return request.get('/audit-logs', { params })
}

export const getAuditLogDetail = (id) => {
  if (useMock) return mockGetAuditLogDetail(id)
  return request.get(`/audit-logs/${id}`)
}
