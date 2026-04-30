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
          <el-select v-model="filterForm.action" placeholder="全部" clearable @change="fetchData">
            <el-option label="创建" value="create" />
            <el-option label="更新" value="update" />
            <el-option label="删除" value="delete" />
            <el-option label="登录" value="login" />
            <el-option label="登出" value="logout" />
          </el-select>
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="filterForm.resourceType" placeholder="全部" clearable @change="fetchData">
            <el-option label="用户" value="user" />
            <el-option label="业务节点" value="business_node" />
            <el-option label="网关" value="gateway" />
            <el-option label="主机" value="host" />
            <el-option label="脚本" value="script" />
            <el-option label="剧本" value="playbook" />
            <el-option label="命令过滤规则" value="command_filter_rule" />
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
        <el-form-item label="搜索">
          <el-input v-model="filterForm.search" placeholder="搜索用户名或资源名" clearable style="width: 200px" @keyup.enter="fetchData" />
        </el-form-item>
        <el-form-item>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="auditLogs" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getActionType(row.action)">{{ getActionText(row.action) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="username" label="操作用户" width="120" />
        <el-table-column prop="resourceType" label="资源类型" width="120">
          <template #default="{ row }">
            {{ getResourceTypeText(row.resourceType) }}
          </template>
        </el-table-column>
        <el-table-column prop="resourceName" label="资源名称" min-width="150" show-overflow-tooltip />
        <el-table-column prop="ipAddress" label="IP地址" width="140" />
        <el-table-column label="操作时间" width="180">
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

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 日志详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="审计日志详情"
      width="700px"
    >
      <el-descriptions :column="1" border v-if="currentLog">
        <el-descriptions-item label="日志ID">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionType(currentLog.action)">{{ getActionText(currentLog.action) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作用户">{{ currentLog.username }}</el-descriptions-item>
        <el-descriptions-item label="资源类型">{{ getResourceTypeText(currentLog.resourceType) }}</el-descriptions-item>
        <el-descriptions-item label="资源ID">{{ currentLog.resourceId || '-' }}</el-descriptions-item>
        <el-descriptions-item label="资源名称">{{ currentLog.resourceName || '-' }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ipAddress || '-' }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ formatDate(currentLog.createdAt) }}</el-descriptions-item>
        <el-descriptions-item v-if="currentLog.oldValues" label="旧值">
          <pre class="json-display">{{ JSON.stringify(currentLog.oldValues, null, 2) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentLog.newValues" label="新值">
          <pre class="json-display">{{ JSON.stringify(currentLog.newValues, null, 2) }}</pre>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentLog.changes && Object.keys(currentLog.changes).length > 0" label="变更对比">
          <div class="changes-display">
            <div v-for="(change, key) in currentLog.changes" :key="key" class="change-item">
              <span class="change-key">{{ key }}:</span>
              <span class="change-old">旧: {{ JSON.stringify(change.old) }}</span>
              <span class="change-arrow">→</span>
              <span class="change-new">新: {{ JSON.stringify(change.new) }}</span>
            </div>
          </div>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getAuditLogs, getAuditLogDetail } from '@/api/auditLogs'

const loading = ref(false)
const auditLogs = ref([])
const currentLog = ref(null)
const detailDialogVisible = ref(false)

const filterForm = reactive({
  action: null,
  resourceType: null,
  startTime: null,
  endTime: null,
  search: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
  totalPages: 0
})

const formatValidationError = (error) => {
  if (error?.response?.data?.detail) {
    if (Array.isArray(error.response.data.detail)) {
      return error.response.data.detail.map(err => err.msg).join('\n')
    }
    return error.response.data.detail
  }
  if (error?.message) {
    return error.message
  }
  return '操作失败，请重试'
}

const getActionType = (action) => {
  const map = {
    login: 'success',
    logout: 'info',
    create: 'primary',
    update: 'warning',
    delete: 'danger'
  }
  const lowerAction = action?.toLowerCase() || ''
  return map[lowerAction] || ''
}

const getActionText = (action) => {
  const map = {
    login: '登录',
    logout: '登出',
    create: '创建',
    update: '更新',
    delete: '删除'
  }
  const lowerAction = action?.toLowerCase() || ''
  return map[lowerAction] || action
}

const getResourceTypeText = (resourceType) => {
  const map = {
    user: '用户',
    business_node: '业务节点',
    gateway: '网关',
    host: '主机',
    script: '脚本',
    playbook: '剧本',
    command_filter_rule: '命令过滤规则',
    audit_log: '审计日志'
  }
  return map[resourceType] || resourceType || '-'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      action: filterForm.action,
      resourceType: filterForm.resourceType,
      startTime: filterForm.startTime,
      endTime: filterForm.endTime,
      search: filterForm.search,
      page: pagination.page,
      pageSize: pagination.pageSize
    }
    const res = await getAuditLogs(params)
    auditLogs.value = res.data
    pagination.total = res.total
    pagination.totalPages = res.totalPages
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  } finally {
    loading.value = false
  }
}

const resetFilter = () => {
  filterForm.action = null
  filterForm.resourceType = null
  filterForm.startTime = null
  filterForm.endTime = null
  filterForm.search = null
  pagination.page = 1
  fetchData()
}

const handleViewDetail = async (row) => {
  try {
    const res = await getAuditLogDetail(row.id)
    currentLog.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  }
}

const handlePageChange = (page) => {
  pagination.page = page
  fetchData()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.page = 1
  fetchData()
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

.json-display {
  margin: 0;
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 12px;
}

.changes-display {
  width: 100%;
}

.change-item {
  padding: 8px;
  margin-bottom: 8px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 12px;
}

.change-key {
  font-weight: bold;
  margin-right: 8px;
}

.change-old {
  color: #f56c6c;
  margin-right: 8px;
}

.change-arrow {
  color: #909399;
  margin: 0 8px;
}

.change-new {
  color: #67c23a;
}
</style>
