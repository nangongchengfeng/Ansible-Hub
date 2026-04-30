<template>
  <div class="hosts-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>主机管理</span>
          <div class="header-actions">
            <el-select v-model="filterNodeId" placeholder="按业务节点筛选" clearable style="width: 200px; margin-right: 10px" @change="fetchData">
              <el-option v-for="node in allNodes" :key="node.id" :label="node.name" :value="node.id" />
            </el-select>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              创建主机
            </el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="hosts" stripe>
        <el-table-column prop="name" label="主机名称" width="180" />
        <el-table-column prop="hostname" label="主机地址" width="150" />
        <el-table-column prop="port" label="端口" width="80" />
        <el-table-column label="业务节点" width="150">
          <template #default="{ row }">
            {{ getNodeName(row.businessNodeId) }}
          </template>
        </el-table-column>
        <el-table-column label="系统用户" width="120">
          <template #default="{ row }">
            {{ getSystemUserName(row.systemUserId) }}
          </template>
        </el-table-column>
        <el-table-column label="网关" width="120">
          <template #default="{ row }">
            {{ row.gatewayId ? getGatewayName(row.gatewayId) : '直连' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="启用状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleToggle(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button link type="primary" size="small" @click="handleMove(row)">
              <el-icon><FolderOpened /></el-icon>
              移动
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="主机名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入主机名称" />
        </el-form-item>
        <el-form-item label="主机地址" prop="hostname">
          <el-input v-model="formData.hostname" placeholder="请输入主机IP或域名" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="formData.port" :min="1" :max="65535" />
        </el-form-item>
        <el-form-item label="业务节点" prop="businessNodeId">
          <el-tree-select
            v-model="formData.businessNodeId"
            :data="treeData"
            :props="treeProps"
            placeholder="请选择业务节点"
            check-strictly
          />
        </el-form-item>
        <el-form-item label="系统用户" prop="systemUserId">
          <el-select v-model="formData.systemUserId" placeholder="请选择系统用户">
            <el-option v-for="user in systemUsers" :key="user.id" :label="user.name" :value="user.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="网关" prop="gatewayId">
          <el-select v-model="formData.gatewayId" placeholder="请选择网关（可选）" clearable>
            <el-option v-for="gw in gateways" :key="gw.id" :label="gw.name" :value="gw.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 移动对话框 -->
    <el-dialog
      v-model="moveDialogVisible"
      title="移动主机"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="当前主机">
          <span>{{ movingHost?.name }}</span>
        </el-form-item>
        <el-form-item label="目标节点" prop="targetNodeId">
          <el-tree-select
            v-model="moveTargetNodeId"
            :data="treeData"
            :props="treeProps"
            placeholder="请选择目标业务节点"
            check-strictly
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="moveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleMoveSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, FolderOpened } from '@element-plus/icons-vue'
import { getHosts, createHost, updateHost, deleteHost, toggleHost, moveHost } from '@/api/hosts'
import { getBusinessNodes } from '@/api/business-nodes'
import { getGateways } from '@/api/gateways'
import { getSystemUsers } from '@/api/system-users'

const loading = ref(false)
const submitLoading = ref(false)
const hosts = ref([])
const treeData = ref([])
const gateways = ref([])
const systemUsers = ref([])
const filterNodeId = ref(null)

const dialogVisible = ref(false)
const dialogTitle = ref('创建主机')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const moveDialogVisible = ref(false)
const movingHost = ref(null)
const moveTargetNodeId = ref(null)

const formData = reactive({
  name: '',
  hostname: '',
  port: 22,
  businessNodeId: null,
  systemUserId: null,
  gatewayId: null
})

const formRules = {
  name: [{ required: true, message: '请输入主机名称', trigger: 'blur' }],
  hostname: [{ required: true, message: '请输入主机地址', trigger: 'blur' }],
  businessNodeId: [{ required: true, message: '请选择业务节点', trigger: 'change' }],
  systemUserId: [{ required: true, message: '请选择系统用户', trigger: 'change' }]
}

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

const treeProps = {
  children: 'children',
  label: 'name'
}

// 扁平化节点列表用于筛选
const allNodes = computed(() => {
  const flatten = (nodes) => {
    let result = []
    for (const node of nodes) {
      result.push(node)
      if (node.children) {
        result = result.concat(flatten(node.children))
      }
    }
    return result
  }
  return flatten(treeData.value)
})

const getNodeName = (nodeId) => {
  const node = allNodes.value.find(n => n.id === nodeId)
  return node?.name || '-'
}

const getSystemUserName = (userId) => {
  const user = systemUsers.value.find(u => u.id === userId)
  return user?.name || '-'
}

const getGatewayName = (gatewayId) => {
  const gw = gateways.value.find(g => g.id === gatewayId)
  return gw?.name || '-'
}

const getStatusType = (status) => {
  const map = {
    online: 'success',
    offline: 'danger',
    unknown: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    online: '在线',
    offline: '离线',
    unknown: '未知'
  }
  return map[status] || '未知'
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = filterNodeId.value ? { businessNodeId: filterNodeId.value } : {}
    const res = await getHosts(params)
    hosts.value = res.data
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  } finally {
    loading.value = false
  }
}

const fetchTreeData = async () => {
  try {
    const res = await getBusinessNodes()
    treeData.value = res.data
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  }
}

const fetchGateways = async () => {
  try {
    const res = await getGateways()
    gateways.value = res.data
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  }
}

const fetchSystemUsers = async () => {
  try {
    const res = await getSystemUsers()
    systemUsers.value = res.data
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  }
}

const resetForm = () => {
  formData.name = ''
  formData.hostname = ''
  formData.port = 22
  formData.businessNodeId = null
  formData.systemUserId = null
  formData.gatewayId = null
  isEdit.value = false
  editingId.value = null
}

const handleCreate = () => {
  resetForm()
  dialogTitle.value = '创建主机'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑主机'
  formData.name = row.name
  formData.hostname = row.hostname
  formData.port = row.port
  formData.businessNodeId = row.businessNodeId
  formData.systemUserId = row.systemUserId
  formData.gatewayId = row.gatewayId
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除主机「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteHost(row.id)
    ElMessage.success('删除成功')
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(formatValidationError(error))
    }
  }
}

const handleToggle = async (row) => {
  try {
    const res = await toggleHost(row.id)
    // 更新本地状态
    row.enabled = res.data.is_enabled
    ElMessage.success(row.enabled ? '已启用' : '已禁用')
  } catch (error) {
    // 回滚状态
    row.enabled = !row.enabled
    ElMessage.error(formatValidationError(error))
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateHost(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createHost(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchData()
    } catch (error) {
      ElMessage.error(formatValidationError(error))
    } finally {
      submitLoading.value = false
    }
  })
}

const handleMove = (row) => {
  movingHost.value = row
  moveTargetNodeId.value = row.businessNodeId
  moveDialogVisible.value = true
}

const handleMoveSubmit = async () => {
  if (!moveTargetNodeId.value) {
    ElMessage.warning('请选择目标节点')
    return
  }

  submitLoading.value = true
  try {
    await moveHost(movingHost.value.id, moveTargetNodeId.value)
    ElMessage.success('移动成功')
    moveDialogVisible.value = false
    await fetchData()
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchTreeData()
  fetchGateways()
  fetchSystemUsers()
})
</script>

<style scoped>
.hosts-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}
</style>
