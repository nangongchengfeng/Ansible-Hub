import request from '@/utils/request'

// 字段转换：后端 -> 前端
const transformFromBackend = (item) => ({
  ...item,
  userId: item.user_id,
  resourceType: item.resource_type,
  resourceId: item.resource_id,
  resourceName: item.resource_name,
  oldValues: item.old_values,
  newValues: item.new_values,
  ipAddress: item.ip_address,
  userAgent: item.user_agent,
  createdAt: item.created_at
})

export const getAuditLogs = async (params) => {
  const backendParams = {}
  if (params?.userId) {
    backendParams.user_id = params.userId
  }
  if (params?.action) {
    backendParams.action = params.action
  }
  if (params?.resourceType) {
    backendParams.resource_type = params.resourceType
  }
  if (params?.startTime) {
    backendParams.start_time = params.startTime
  }
  if (params?.endTime) {
    backendParams.end_time = params.endTime
  }
  if (params?.search) {
    backendParams.search = params.search
  }
  if (params?.page) {
    backendParams.page = params.page
  }
  if (params?.pageSize) {
    backendParams.page_size = params.pageSize
  }

  const res = await request.get('/audit-logs', { params: backendParams })
  return {
    total: res.data.total,
    page: res.data.page,
    pageSize: res.data.page_size,
    totalPages: res.data.total_pages,
    data: (res.data.items || []).map(transformFromBackend)
  }
}

export const getAuditLogDetail = async (id) => {
  const res = await request.get(`/audit-logs/${id}`)
  return {
    data: transformFromBackend(res.data)
  }
}
