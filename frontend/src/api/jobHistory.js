import request from '@/utils/request'
import { getJobList, getJobDetail, getJobTasks } from '@/api/jobExecutions'

// 获取作业历史
export const getJobHistory = async (params = {}) => {
  const queryParams = {}
  if (params.status && params.status !== 'all') {
    queryParams.status = params.status.toUpperCase()
  }
  const res = await getJobList(queryParams)

  // 转换数据格式以适配前端视图
  const jobs = res.data.map(job => ({
    id: job.id,
    name: `作业 #${job.id}`,
    executeType: job.jobType?.toLowerCase() || 'shell',
    status: job.status?.toLowerCase() || 'pending',
    hostNames: [], // 后端暂未返回主机名称
    startedAt: job.startedAt,
    completedAt: job.completedAt,
    duration: job.startedAt && job.completedAt
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
export const getJobDetail_ = async (id) => {
  const res = await getJobDetail(id)
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
      duration: job.startedAt && job.completedAt
        ? Math.round((new Date(job.completedAt) - new Date(job.startedAt)) / 1000)
        : null,
      createdBy: job.createdBy,
      ...job
    }
  }
}

// 获取作业日志（从任务中提取）
export const getJobLogs = async (id) => {
  const [jobRes, tasksRes] = await Promise.all([
    getJobDetail(id),
    getJobTasks(id)
  ])

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
  tasksRes.data.forEach(task => {
    if (task.startedAt) {
      logs.push({
        time: task.startedAt,
        level: 'info',
        message: `主机 ${task.hostId} 开始执行`
      })
    }

    if (task.stdout) {
      logs.push({
        time: task.completedAt || task.updatedAt,
        level: 'info',
        message: `主机 ${task.hostId} 输出: ${task.stdout}`
      })
    }

    if (task.stderr) {
      logs.push({
        time: task.completedAt || task.updatedAt,
        level: 'error',
        message: `主机 ${task.hostId} 错误: ${task.stderr}`
      })
    }

    if (task.completedAt) {
      const level = task.status === 'COMPLETED' || task.status === 'SUCCESS' ? 'success' : 'error'
      logs.push({
        time: task.completedAt,
        level,
        message: `主机 ${task.hostId} 执行完成，状态: ${task.status}`
      })
    }
  })

  if (jobRes.data.completedAt) {
    const level = jobRes.data.status === 'COMPLETED' || jobRes.data.status === 'SUCCESS' ? 'success' : 'error'
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

export const redoJob = (id) => {
  // 重做功能暂未实现
  return request.post(`/job-history/${id}/redo`)
}

// 重新导出以保持兼容
export { getJobDetail_ as getJobDetail }
