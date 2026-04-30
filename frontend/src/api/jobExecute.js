import { getHosts } from '@/api/hosts'
import { getScripts } from '@/api/scripts'
import { getPlaybooks } from '@/api/playbooks'
import {
  submitJob,
  checkCommand,
  cancelJob,
  saveAsTemplate as saveAsTemplateApi
} from '@/api/jobExecutions'

export const getHostList = () => {
  return getHosts()
}

export const getScriptList = () => {
  return getScripts()
}

export const getPlaybookList = () => {
  return getPlaybooks()
}

// 执行作业
export const executeJob = async (formData) => {
  // 将前端表单数据转换为后端API格式
  const jobData = {
    jobType: formData.executeType.toUpperCase(),
    targetType: 'hosts',
    targetHostIds: formData.hostIds
  }

  if (formData.executeType === 'shell') {
    jobData.shellCommand = formData.command
  } else if (formData.executeType === 'module') {
    jobData.moduleName = formData.moduleName
    jobData.moduleArgs = formData.moduleArgs
  } else if (formData.executeType === 'playbook') {
    jobData.playbookId = formData.playbookId
  } else if (formData.executeType === 'script') {
    jobData.scriptId = formData.scriptId
  }

  const res = await submitJob(jobData)
  // 保持原有的返回格式兼容
  return {
    data: {
      jobId: res.data.id,
      ...res.data
    }
  }
}

export { cancelJob, checkCommand, saveAsTemplateApi as saveAsTemplate }
