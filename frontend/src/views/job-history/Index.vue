<template>
  <div class="job-history-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>作业历史</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="filterForm" style="margin-bottom: 20px">
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" @change="fetchData">
            <el-option label="全部" value="all" />
            <el-option label="运行中" value="running" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="filterForm.startTime"
            type="datetime"
            placeholder="开始时间"
            style="width: 220px"
            @change="fetchData"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="filterForm.endTime"
            type="datetime"
            placeholder="结束时间"
            style="width: 220px"
            @change="fetchData"
          />
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="filteredJobs" stripe>
        <el-table-column prop="name" label="作业名称" width="200" />
        <el-table-column label="执行类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getExecuteTypeText(row.executeType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="hostNames" label="目标主机" min-width="200">
          <template #default="{ row }">
            {{ row.hostNames?.join(', ') }}
          </template>
        </el-table-column>
        <el-table-column label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.startedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="耗时" width="100">
          <template #default="{ row }">
            {{ row.duration ? formatDuration(row.duration) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="执行用户" width="100" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewDetail(row)">
              <el-icon><Document /></el-icon>
              详情
            </el-button>
            <el-button link type="primary" size="small" @click="handleViewLogs(row)">
              <el-icon><List /></el-icon>
              日志
            </el-button>
            <el-button link type="warning" size="small" @click="handleRedo(row)" v-if="row.status !== 'running'">
              <el-icon><Refresh /></el-icon>
              重做
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
        <el-descriptions-item label="作业名称">{{ currentJob.name }}</el-descriptions-item>
        <el-descriptions-item label="执行类型">{{ getExecuteTypeText(currentJob.executeType) }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentJob.status)">{{ getStatusText(currentJob.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="目标主机">{{ currentJob.hostNames?.join(', ') }}</el-descriptions-item>
        <el-descriptions-item label="开始时间">{{ formatDate(currentJob.startedAt) }}</el-descriptions-item>
        <el-descriptions-item label="结束时间">{{ currentJob.completedAt ? formatDate(currentJob.completedAt) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="耗时">{{ currentJob.duration ? formatDuration(currentJob.duration) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="执行用户">{{ currentJob.createdBy }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleRedo(currentJob)" v-if="currentJob?.status !== 'running'">重做</el-button>
      </template>
    </el-dialog>

    <!-- 日志查看对话框 -->
    <el-dialog
      v-model="logsDialogVisible"
      title="作业日志"
      width="900px"
    >
      <div class="log-container">
        <div v-for="(log, index) in jobLogs" :key="index" class="log-line">
          <span class="log-time">[{{ formatDate(log.time) }}]</span>
          <span class="log-level" :class="`log-${log.level}`">[{{ log.level.toUpperCase() }}]</span>
          <span class="log-text">{{ log.message }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="logsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Document, List, Refresh } from '@element-plus/icons-vue'
import { getJobHistory, getJobDetail, getJobLogs, redoJob } from '@/api/jobHistory'
import { useAuthStore } from '@/stores/auth'

const loading = ref(false)
const jobs = ref([])
const jobLogs = ref([])

const filterForm = reactive({
  status: 'all',
  startTime: null,
  endTime: null
})

const detailDialogVisible = ref(false)
const logsDialogVisible = ref(false)
const currentJob = ref(null)

const authStore = useAuthStore()

const filteredJobs = computed(() => {
  if (authStore.user?.role === 'superadmin' || authStore.user?.role === 'auditor') {
    return jobs.value
  }
  return jobs.value.filter(j => j.createdBy === authStore.user?.username)
})

const getExecuteTypeText = (type) => {
  const map = {
    shell: 'Shell',
    module: 'Ansible模块',
    playbook: 'Ansible剧本',
    script: '脚本'
  }
  return map[type] || type
}

const getStatusType = (status) => {
  const map = {
    running: 'primary',
    success: 'success',
    failed: 'danger',
    cancelled: 'warning'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    running: '运行中',
    success: '成功',
    failed: '失败',
    cancelled: '已取消'
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (mins > 0) {
    return `${mins}分${secs}秒`
  }
  return `${secs}秒`
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      status: filterForm.status,
      startTime: filterForm.startTime,
      endTime: filterForm.endTime
    }
    const res = await getJobHistory(params)
    jobs.value = res.data
  } catch (error) {
    ElMessage.error('获取作业历史失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.status = 'all'
  filterForm.startTime = null
  filterForm.endTime = null
  fetchData()
}

const handleViewDetail = async (row) => {
  try {
    const res = await getJobDetail(row.id)
    currentJob.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取作业详情失败')
  }
}

const handleViewLogs = async (row) => {
  try {
    const res = await getJobLogs(row.id)
    jobLogs.value = res.data
    logsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取作业日志失败')
  }
}

const handleRedo = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要重做作业「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const res = await redoJob(row.id)
    ElMessage.success(`作业已重新执行！新作业ID：${res.data.jobId}`)
    detailDialogVisible.value = false
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重做失败')
    }
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
  max-height: 400px;
  overflow-y: auto;
}

.log-line {
  margin-bottom: 4px;
}

.log-time {
  color: #6a9955;
  margin-right: 8px;
}

.log-level {
  margin-right: 8px;
  font-weight: bold;
}

.log-info {
  color: #569cd6;
}

.log-success {
  color: #6a9955;
}

.log-warning {
  color: #dcdcaa;
}

.log-error {
  color: #f44747;
}
</style>
