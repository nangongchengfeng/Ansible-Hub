import request from '@/utils/request'
import { mockExecuteJob, mockCancelJob, mockCheckCommand, mockSaveTemplate } from '@/utils/mock'
import { getHosts } from '@/api/hosts'
import { getScripts } from '@/api/scripts'
import { getPlaybooks } from '@/api/playbooks'

const useMock = true

export const getHostList = () => {
  return getHosts()
}

export const getScriptList = () => {
  return getScripts()
}

export const getPlaybookList = () => {
  return getPlaybooks()
}

export const executeJob = (data) => {
  if (useMock) return mockExecuteJob(data)
  return request.post('/jobs/execute', data)
}

export const cancelJob = (jobId) => {
  if (useMock) return mockCancelJob(jobId)
  return request.post(`/jobs/${jobId}/cancel`)
}

export const checkCommand = (command) => {
  if (useMock) return mockCheckCommand(command)
  return request.post('/command-filters/check', { command })
}

export const saveAsTemplate = (data) => {
  if (useMock) return mockSaveTemplate(data)
  return request.post('/job-templates', data)
}
