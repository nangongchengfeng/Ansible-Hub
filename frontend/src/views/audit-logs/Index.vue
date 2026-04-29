<template>
  <div class="audit-logs-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>审计日志</span>
        </div>
      </template>

      <!-- 筛选条件 -->
      <el-form :inline="true" :model="filterForm" style="margin-bottom: 20px">
        <el-form-item label="操作类型">
          <el-select v-model="filterForm.action" placeholder="全部" @change="fetchData">
            <el-option label="全部" value="all" />
            <el-option label="登录" value="LOGIN" />
            <el-option label="登出" value="LOGOUT" />
            <el-option label="创建" value="CREATE" />
            <el-option label="更新" value="UPDATE" />
            <el-option label="删除" value="DELETE" />
            <el-option label="执行" value="EXECUTE" />
            <el-option label="权限" value="PERMISSION" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作用户">
          <el-select v-model="filterForm.user" placeholder="全部" @change="fetchData">
            <el-option label="全部" value="all" />
            <el-option label="admin" value="admin" />
            <el-option label="auditor" value="auditor" />
            <el-option label="operator" value="operator" />
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

      <el-table v-loading="loading" :data="auditLogs" stripe>
        <el-table-column prop="id" label="ID" width="80" sortable />
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">{{ getActionText(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="user" label="操作用户" width="120" />
        <el-table-column prop="detail" label="操作详情" min-width="300" />
        <el-table-column prop="ip" label="IP地址" width="140" />
        <el-table-column label="操作时间" width="180" sortable>
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="审计日志详情"
      width="600px"
    >
      <el-descriptions :column="1" border v-if="currentLog">
        <el-descriptions-item label="日志ID">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionType(currentLog.action)">{{ getActionText(currentLog.action) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作用户">{{ currentLog.user }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ formatDate(currentLog.createdAt) }}</el-descriptions-item>
        <el-descriptions-item label="操作详情">
          <div class="detail-content">{{ currentLog.detail }}</div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAuditLogs, getAuditLogDetail } from '@/api/auditLogs'
import { useAuthStore } from '@/stores/auth'

const loading = ref(false)
const auditLogs = ref([])
const currentLog = ref(null)
const detailDialogVisible = ref(false)

const filterForm = reactive({
  action: 'all',
  user: 'all',
  startTime: null,
  endTime: null
})

const authStore = useAuthStore()

const canViewAuditLogs = computed(() => {
  return authStore.user?.role === 'superadmin' || authStore.user?.role === 'auditor'
})

const getActionType = (action) => {
  const map = {
    LOGIN: 'success',
    LOGOUT: 'info',
    CREATE: 'primary',
    UPDATE: 'warning',
    DELETE: 'danger',
    EXECUTE: '',
    PERMISSION: 'warning'
  }
  return map[action] || ''
}

const getActionText = (action) => {
  const map = {
    LOGIN: '登录',
    LOGOUT: '登出',
    CREATE: '创建',
    UPDATE: '更新',
    DELETE: '删除',
    EXECUTE: '执行',
    PERMISSION: '权限'
  }
  return map[action] || action
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchData = async () => {
  if (!canViewAuditLogs.value) {
    ElMessage.error('您没有权限查看审计日志')
    return
  }

  loading.value = true
  try {
    const params = {
      action: filterForm.action,
      user: filterForm.user,
      startTime: filterForm.startTime,
      endTime: filterForm.endTime
    }
    const res = await getAuditLogs(params)
    auditLogs.value = res.data
  } catch (error) {
    ElMessage.error('获取审计日志失败')
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.action = 'all'
  filterForm.user = 'all'
  filterForm.startTime = null
  filterForm.endTime = null
  fetchData()
}

const handleViewDetail = async (row) => {
  try {
    const res = await getAuditLogDetail(row.id)
    currentLog.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取日志详情失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.audit-logs-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-content {
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
