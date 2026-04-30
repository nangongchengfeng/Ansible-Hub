import {
  getJobList,
  getJobDetail as getJobDetailApi,
  getJobTasks,
  getJobLogs as getJobLogsApi,
  retryJob
} from '@/api/jobExecutions'

// 获取作业历史
export const getJobHistory = async (params = {}) => {
  const queryParams = {}
  if (params.status && params.status !== 'all') {
    queryParams.status = params.status.toUpperCase()
  }
  const res = await getJobList(queryParams)

  // 转换数据格式以适配前端视图
  const jobs = res.data.map((job) => ({
    id: job.id,
    name: `作业 #${job.id}`,
    executeType: job.jobType?.toLowerCase() || 'shell',
    status: job.status?.toLowerCase() || 'pending',
    hostNames: [], // 后端暂未返回主机名称
    startedAt: job.startedAt,
    completedAt: job.completedAt,
    duration:
      job.startedAt && job.completedAt
        ? Math.round((new Date(job.completedAt) - new Date(job.startedAt)) / 1000)
        : null,
    createdBy: job.createdBy, // 后端返回的是用户ID，需要显示用户名
    ...job
  }))

  return {
    data: jobs,
    total: res.total
  }
}

// 获取作业详情
export const getJobDetail = async (id) => {
  const res = await getJobDetailApi(id)
  const job = res.data
  return {
    data: {
      id: job.id,
      name: `作业 #${job.id}`,
      executeType: job.jobType?.toLowerCase() || 'shell',
      status: job.status?.toLowerCase() || 'pending',
      hostNames: [],
      startedAt: job.startedAt,
      completedAt: job.completedAt,
      duration:
        job.startedAt && job.completedAt
          ? Math.round((new Date(job.completedAt) - new Date(job.startedAt)) / 1000)
          : null,
      createdBy: job.createdBy,
      ...job
    }
  }
}

// 获取作业日志
export const getJobLogs = async (id) => {
  try {
    const res = await getJobLogsApi(id)
    // 转换后端日志格式为前端期望格式
    const logs = []
    const jobData = res.data

    if (jobData.created_at) {
      logs.push({
        time: jobData.created_at,
        level: 'info',
        message: '作业已创建'
      })
    }

    if (jobData.started_at) {
      logs.push({
        time: jobData.started_at,
        level: 'info',
        message: '作业开始执行'
      })
    }

    // 处理任务日志
    if (jobData.tasks) {
      jobData.tasks.forEach((task) => {
        if (task.started_at) {
          logs.push({
            time: task.started_at,
            level: 'info',
            message: `主机 ${task.host_name || task.host_id} 开始执行`
          })
        }

        if (task.stdout) {
          logs.push({
            time: task.completed_at || task.updated_at,
            level: 'info',
            message: `主机 ${task.host_name || task.host_id} 输出: ${task.stdout}`
          })
        }

        if (task.stderr) {
          logs.push({
            time: task.completed_at || task.updated_at,
            level: 'error',
            message: `主机 ${task.host_name || task.host_id} 错误: ${task.stderr}`
          })
        }

        if (task.completed_at) {
          const level =
            task.status === 'COMPLETED' || task.status === 'SUCCESS' ? 'success' : 'error'
          logs.push({
            time: task.completed_at,
            level,
            message: `主机 ${task.host_name || task.host_id} 执行完成，状态: ${task.status}`
          })
        }
      })
    }

    if (jobData.completed_at) {
      const level =
        jobData.status === 'COMPLETED' || jobData.status === 'SUCCESS' ? 'success' : 'error'
      logs.push({
        time: jobData.completed_at,
        level,
        message: `作业执行完成，状态: ${jobData.status}`
      })
    }

    // 按时间排序
    logs.sort((a, b) => new Date(a.time) - new Date(b.time))

    return {
      data: logs
    }
  } catch (error) {
    // 如果专用端点失败，回退到从任务获取
    return getJobLogsFallback(id)
  }
}

// 回退方法：从任务中提取日志
const getJobLogsFallback = async (id) => {
  const [jobRes, tasksRes] = await Promise.all([getJobDetailApi(id), getJobTasks(id)])

  const logs = []

  // 添加作业级别日志
  logs.push({
    time: jobRes.data.createdAt,
    level: 'info',
    message: '作业已创建'
  })

  if (jobRes.data.startedAt) {
    logs.push({
      time: jobRes.data.startedAt,
      level: 'info',
      message: '作业开始执行'
    })
  }

  // 添加任务日志
  tasksRes.data.forEach((task) => {
    const hostName = task.host?.name || task.host?.hostname || task.hostId
    if (task.startedAt) {
      logs.push({
        time: task.startedAt,
        level: 'info',
        message: `主机 ${hostName} 开始执行`
      })
    }

    if (task.stdout) {
      logs.push({
        time: task.completedAt || task.updatedAt,
        level: 'info',
        message: `主机 ${hostName} 输出: ${task.stdout}`
      })
    }

    if (task.stderr) {
      logs.push({
        time: task.completedAt || task.updatedAt,
        level: 'error',
        message: `主机 ${hostName} 错误: ${task.stderr}`
      })
    }

    if (task.completedAt) {
      const level = task.status === 'COMPLETED' || task.status === 'SUCCESS' ? 'success' : 'error'
      logs.push({
        time: task.completedAt,
        level,
        message: `主机 ${hostName} 执行完成，状态: ${task.status}`
      })
    }
  })

  if (jobRes.data.completedAt) {
    const level =
      jobRes.data.status === 'COMPLETED' || jobRes.data.status === 'SUCCESS' ? 'success' : 'error'
    logs.push({
      time: jobRes.data.completedAt,
      level,
      message: `作业执行完成，状态: ${jobRes.data.status}`
    })
  }

  // 按时间排序
  logs.sort((a, b) => new Date(a.time) - new Date(b.time))

  return {
    data: logs
  }
}

export const redoJob = async (id) => {
  return retryJob(id)
}
