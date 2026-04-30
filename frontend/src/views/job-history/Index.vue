<template>
  <div class="job-history-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>作业历史</span>
          <el-button type="primary" @click="fetchData">刷新</el-button>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="filterForm" style="margin-bottom: 20px">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" @change="fetchData">
            <el-option label="全部" value="all" />
            <el-option label="等待中" value="pending" />
            <el-option label="运行中" value="running" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="filteredJobs" stripe>
        <el-table-column prop="id" label="作业ID" width="100" />
        <el-table-column label="执行类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getExecuteTypeText(row.jobType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="命令检查" width="100">
          <template #default="{ row }">
            <el-tag :type="row.commandCheckPassed ? 'success' : 'danger'" size="small">
              {{ row.commandCheckPassed ? '通过' : '未通过' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">
            {{ row.startedAt ? formatDate(row.startedAt) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? formatDuration(row.duration) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="创建者ID" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewDetail(row)">
              <el-icon><Document /></el-icon>
              详情
            </el-button>
            <el-button link type="primary" size="small" @click="handleViewLogs(row)">
              <el-icon><List /></el-icon>
              日志
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 作业详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="作业详情"
      width="700px"
    >
      <el-descriptions :column="1" border v-if="currentJob">
        <el-descriptions-item label="作业ID">{{ currentJob.id }}</el-descriptions-item>
        <el-descriptions-item label="执行类型">{{ getExecuteTypeText(currentJob.jobType) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentJob.status)">{{ getStatusText(currentJob.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="命令检查">
          <el-tag :type="currentJob.commandCheckPassed ? 'success' : 'danger'">
            {{ currentJob.commandCheckPassed ? '通过' : '未通过' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="目标类型">{{ currentJob.targetType }}</el-descriptions-item>
        <el-descriptions-item label="目标主机ID">
          {{ currentJob.targetHostIds?.join(', ') || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ currentJob.startedAt ? formatDate(currentJob.startedAt) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间">
          {{ currentJob.completedAt ? formatDate(currentJob.completedAt) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ currentJob.duration ? formatDuration(currentJob.duration) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建者ID">{{ currentJob.createdBy }}</el-descriptions-item>

        <!-- 根据类型显示不同内容 -->
        <template v-if="currentJob.jobType === 'SHELL'">
          <el-descriptions-item label="Shell命令">
            <pre style="white-space: pre-wrap; word-break: break-all; margin: 0">{{ currentJob.shellCommand }}</pre>
          </el-descriptions-item>
        </template>
        <template v-else-if="currentJob.jobType === 'MODULE'">
          <el-descriptions-item label="模块名称">{{ currentJob.moduleName }}</el-descriptions-item>
          <el-descriptions-item label="模块参数">
            <pre style="white-space: pre-wrap; word-break: break-all; margin: 0">{{ currentJob.moduleArgs || '-' }}</pre>
          </el-descriptions-item>
        </template>
        <template v-else-if="currentJob.jobType === 'PLAYBOOK'">
          <el-descriptions-item label="剧本ID">{{ currentJob.playbookId }}</el-descriptions-item>
          <el-descriptions-item label="剧本版本">{{ currentJob.playbookVersion || '最新' }}</el-descriptions-item>
        </template>
        <template v-else-if="currentJob.jobType === 'SCRIPT'">
          <el-descriptions-item label="脚本ID">{{ currentJob.scriptId }}</el-descriptions-item>
          <el-descriptions-item label="脚本版本">{{ currentJob.scriptVersion || '最新' }}</el-descriptions-item>
        </template>

        <el-descriptions-item label="错误信息" v-if="currentJob.errorMessage">
          <pre style="white-space: pre-wrap; word-break: break-all; margin: 0; color: #f44747">{{ currentJob.errorMessage }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 日志查看对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      title="执行日志"
      width="900px"
    >
      <div class="log-container" v-if="jobTasks.length > 0">
        <div v-for="task in jobTasks" :key="task.id" style="margin-bottom: 16px; padding-bottom: 16px; border-bottom: 1px solid #333">
          <div style="margin-bottom: 8px; font-weight: bold">
            主机 {{ task.hostId }} - <el-tag :type="getStatusType(task.status)" size="small">{{ getStatusText(task.status) }}</el-tag>
          </div>
          <template v-if="task.stdout">
            <div style="margin-bottom: 4px; color: #6a9955">STDOUT:</div>
            <pre style="background: #252526; padding: 8px; border-radius: 4px; margin: 0; white-space: pre-wrap; word-break: break-all">{{ task.stdout }}</pre>
          </template>
          <template v-if="task.stderr">
            <div style="margin-bottom: 4px; color: #f44747; margin-top: 8px">STDERR:</div>
            <pre style="background: #252526; padding: 8px; border-radius: 4px; margin: 0; white-space: pre-wrap; word-break: break-all; color: #f44747">{{ task.stderr }}</pre>
          </template>
          <template v-if="task.exitCode !== null && task.exitCode !== undefined">
            <div style="margin-top: 8px; color: #dcdcaa">退出码: {{ task.exitCode }}</div>
          </template>
          <template v-if="task.errorMessage">
            <div style="margin-top: 8px; color: #f44747">错误: {{ task.errorMessage }}</div>
          </template>
        </div>
      </div>
      <div v-else style="text-align: center; color: #888; padding: 40px">暂无日志</div>
      <template #footer>
        <el-button @click="logsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, List } from '@element-plus/icons-vue'
import { getJobList, getJobDetail, getJobTasks } from '@/api/jobExecutions'
import { useAuthStore } from '@/stores/auth'

const loading = ref(false)
const jobs = ref([])
const jobTasks = ref([])

const filterForm = reactive({
  status: 'all'
})

const detailDialogVisible = ref(false)
const logsDialogVisible = ref(false)
const currentJob = ref(null)

const authStore = useAuthStore()

const filteredJobs = computed(() => {
  let result = jobs.value
  // 权限过滤暂时保留所有
  return result
})

const getExecuteTypeText = (type) => {
  const map = {
    SHELL: 'Shell',
    MODULE: 'Ansible模块',
    PLAYBOOK: 'Ansible剧本',
    SCRIPT: '脚本'
  }
  return map?.[type] || type || '-'
}

const getStatusType = (status) => {
  const map = {
    PENDING: 'info',
    RUNNING: 'primary',
    COMPLETED: 'success',
    SUCCESS: 'success',
    FAILED: 'danger',
    CANCELLED: 'warning'
  }
  return map?.[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    PENDING: '等待中',
    RUNNING: '运行中',
    COMPLETED: '已完成',
    SUCCESS: '成功',
    FAILED: '失败',
    CANCELLED: '已取消'
  }
  return map?.[status] || status || '-'
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDuration = (seconds) => {
  if (typeof seconds !== 'number') return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  if (mins > 0) {
    return `${mins}分${secs}秒`
  }
  return `${secs}秒`
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.status && filterForm.status !== 'all') {
      params.status = filterForm.status.toUpperCase()
    }
    const res = await getJobList(params)

    // 计算耗时
    const jobsWithDuration = res.data.map(job => {
      let duration = null
      if (job.startedAt && job.completedAt) {
        duration = (new Date(job.completedAt) - new Date(job.startedAt)) / 1000
      }
      return {
        ...job,
        duration
      }
    })

    jobs.value = jobsWithDuration
  } catch (error) {
    ElMessage.error('获取作业历史失败')
  } finally {
    loading.value = false
  }
}

const handleViewDetail = async (row) => {
  try {
    const res = await getJobDetail(row.id)
    const job = res.data

    // 计算耗时
    let duration = null
    if (job.startedAt && job.completedAt) {
      duration = (new Date(job.completedAt) - new Date(job.startedAt)) / 1000
    }

    currentJob.value = {
      ...job,
      duration
    }
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取作业详情失败')
  }
}

const handleViewLogs = async (row) => {
  try {
    const res = await getJobTasks(row.id)
    jobTasks.value = res.data
    logsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取执行日志失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.job-history-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-container {
  background: #1e1e1e;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  max-height: 500px;
  overflow-y: auto;
  color: #d4d4d4;
}
</style>
