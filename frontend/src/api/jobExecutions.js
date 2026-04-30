import request from '@/utils/request'

// 字段转换：后端 snake_case -> 前端 camelCase
const transformJobToCamel = (job) => {
  if (!job) return job
  return {
    id: job.id,
    jobType: job.job_type,
    status: job.status,
    startedAt: job.started_at,
    completedAt: job.completed_at,
    commandCheckPassed: job.command_check_passed,
    errorMessage: job.error_message,
    createdBy: job.created_by,
    createdAt: job.created_at,
    updatedAt: job.updated_at,
    shellCommand: job.shell_command,
    moduleName: job.module_name,
    moduleArgs: job.module_args,
    playbookId: job.playbook_id,
    playbookVersion: job.playbook_version,
    scriptId: job.script_id,
    scriptVersion: job.script_version,
    targetType: job.target_type,
    targetHostIds: job.target_host_ids,
    targetBusinessNodeId: job.target_business_node_id,
    commandCheckResult: job.command_check_result,
    tasks: (job.tasks || []).map(transformTaskToCamel)
  }
}

const transformTaskToCamel = (task) => {
  if (!task) return task
  return {
    id: task.id,
    jobExecutionId: task.job_execution_id,
    hostId: task.host_id,
    status: task.status,
    startedAt: task.started_at,
    completedAt: task.completed_at,
    stdout: task.stdout,
    stderr: task.stderr,
    exitCode: task.exit_code,
    errorMessage: task.error_message,
    createdAt: task.created_at,
    updatedAt: task.updated_at,
    connectionConfig: task.connection_config,
    resultJson: task.result_json
  }
}

// 字段转换：前端 camelCase -> 后端 snake_case
const transformJobToSnake = (data) => {
  if (!data) return data
  return {
    job_type: data.jobType,
    shell_command: data.shellCommand,
    module_name: data.moduleName,
    module_args: data.moduleArgs,
    playbook_id: data.playbookId,
    playbook_version: data.playbookVersion,
    script_id: data.scriptId,
    script_version: data.scriptVersion,
    target_type: data.targetType,
    target_host_id: data.targetHostId,
    target_host_ids: data.targetHostIds,
    target_business_node_id: data.targetBusinessNodeId
  }
}

// 获取作业列表
export const getJobList = async (params = {}) => {
  const res = await request.get('/job-executions', { params })
  return {
    data: res.data.items.map(transformJobToCamel),
    total: res.data.total
  }
}

// 提交作业
export const submitJob = async (data) => {
  const res = await request.post('/job-executions', transformJobToSnake(data))
  return {
    data: {
      id: res.data.id,
      status: res.data.status,
      commandCheckPassed: res.data.command_check_passed,
      commandCheckResult: res.data.command_check_result,
      message: res.data.message
    }
  }
}

// 获取作业详情
export const getJobDetail = async (id) => {
  const res = await request.get(`/job-executions/${id}`)
  return {
    data: transformJobToCamel(res.data)
  }
}

// 获取作业的任务列表
export const getJobTasks = async (jobId, params = {}) => {
  const res = await request.get(`/job-executions/${jobId}/tasks`, { params })
  return {
    data: res.data.items.map(transformTaskToCamel),
    total: res.data.total
  }
}

// 获取任务详情
export const getTaskDetail = async (taskId) => {
  const res = await request.get(`/job-executions/tasks/${taskId}`)
  return {
    data: transformTaskToCamel(res.data)
  }
}

// 检查命令
export const checkCommand = async (command) => {
  const res = await request.post('/command-filter-rules/check', { command })
  return {
    data: {
      allowed: res.data.allowed,
      matchedRules: res.data.matched_rules,
      severity: res.data.severity,
      message: res.data.message,
      blocked: res.data.severity === 'block'
    }
  }
}
