import request from '@/utils/request'
import { mockGetDashboardData } from '@/utils/mock'

const useMock = true

export const getDashboardData = (params) => {
  if (useMock) return mockGetDashboardData(params)
  return request.get('/dashboard', { params })
}
