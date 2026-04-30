import request from '@/utils/request'
import { getHosts } from '@/api/hosts'
import { getScripts } from '@/api/scripts'
import { getPlaybooks } from '@/api/playbooks'

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
  return request.post('/jobs/execute', data)
}

export const cancelJob = (jobId) => {
  return request.post(`/jobs/${jobId}/cancel`)
}

export const checkCommand = (command) => {
  return request.post('/command-filters/check', { command })
}

export const saveAsTemplate = (data) => {
  return request.post('/job-templates', data)
}
