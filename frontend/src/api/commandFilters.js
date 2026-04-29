import request from '@/utils/request'
import { mockGetCommandFilters, mockCreateCommandFilter, mockUpdateCommandFilter, mockDeleteCommandFilter, mockToggleCommandFilter, mockMoveCommandFilter } from '@/utils/mock'

const useMock = true

export const getCommandFilters = () => {
  if (useMock) return mockGetCommandFilters()
  return request.get('/command-filters')
}

export const createCommandFilter = (data) => {
  if (useMock) return mockCreateCommandFilter(data)
  return request.post('/command-filters', data)
}

export const updateCommandFilter = (id, data) => {
  if (useMock) return mockUpdateCommandFilter(id, data)
  return request.put(`/command-filters/${id}`, data)
}

export const deleteCommandFilter = (id) => {
  if (useMock) return mockDeleteCommandFilter(id)
  return request.delete(`/command-filters/${id}`)
}

export const toggleCommandFilter = (id) => {
  if (useMock) return mockToggleCommandFilter(id)
  return request.patch(`/command-filters/${id}/toggle`)
}

export const moveCommandFilter = (id, direction) => {
  if (useMock) return mockMoveCommandFilter(id, direction)
  return request.patch(`/command-filters/${id}/move`, { direction })
}
