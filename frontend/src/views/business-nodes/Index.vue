<template>
  <div class="business-nodes-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>业务节点管理</span>
          <el-button type="primary" @click="handleCreate()">
            <el-icon><Plus /></el-icon>
            创建节点
          </el-button>
        </div>
      </template>

      <el-tree
        v-loading="loading"
        :data="filteredTreeData"
        :props="treeProps"
        node-key="id"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <span class="node-label">{{ data.name }}</span>
            <span v-if="data.description" class="node-desc">({{ data.description }})</span>
            <div class="node-actions">
              <el-button link type="primary" size="small" @click="handleEdit(data)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button link type="primary" size="small" @click="handleCreate(data)">
                <el-icon><Plus /></el-icon>
                添加子节点
              </el-button>
              <el-button link type="primary" size="small" @click="handlePermission(data)">
                <el-icon><Key /></el-icon>
                权限
              </el-button>
              <el-button link type="danger" size="small" @click="handleDelete(data)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </div>
          </div>
        </template>
      </el-tree>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="父节点" prop="parentId">
          <el-tree-select
            v-model="formData.parentId"
            :data="filteredTreeData"
            :props="treeProps"
            placeholder="选择父节点（不选则为根节点）"
            clearable
            check-strictly
            :disabled="isEdit"
          />
        </el-form-item>
        <el-form-item label="绑定网关" prop="gatewayId">
          <el-select v-model="formData.gatewayId" placeholder="选择网关" clearable>
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

    <!-- 权限配置对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="配置节点权限"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="节点名称">
          <span>{{ permissionNode?.name }}</span>
        </el-form-item>
        <el-form-item label="查看权限">
          <el-switch v-model="permissionData.view" />
        </el-form-item>
        <el-form-item label="执行权限">
          <el-switch v-model="permissionData.execute" />
        </el-form-item>
        <el-form-item label="管理权限">
          <el-switch v-model="permissionData.manage" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="permissionDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handlePermissionSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Key } from '@element-plus/icons-vue'
import { getBusinessNodes, getGateways, createBusinessNode, updateBusinessNode, deleteBusinessNode, updateNodePermissions } from '@/api/business-nodes'
import { useAuthStore } from '@/stores/auth'

const loading = ref(false)
const submitLoading = ref(false)
const treeData = ref([])
const gateways = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('创建业务节点')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const permissionDialogVisible = ref(false)
const permissionNode = ref(null)
const permissionData = reactive({
  view: true,
  execute: false,
  manage: false
})

const formData = reactive({
  name: '',
  description: '',
  parentId: null,
  gatewayId: null
})

const formRules = {
  name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }]
}

const treeProps = {
  children: 'children',
  label: 'name'
}

const authStore = useAuthStore()

const filterTreeByPermission = (nodes, permission = 'view') => {
  // 超级管理员可以看到所有节点
  if (authStore.user?.role === 'superadmin') {
    return nodes
  }

  return nodes.filter(node => {
    // 检查当前节点权限
    const hasPermission = node.permissions?.[permission] ?? true

    // 递归过滤子节点
    let filteredChildren = []
    if (node.children && node.children.length > 0) {
      filteredChildren = filterTreeByPermission(node.children, permission)
    }

    // 如果当前节点有权限，或者有子节点有权限，则保留
    if (hasPermission || filteredChildren.length > 0) {
      return {
        ...node,
        children: filteredChildren.length > 0 ? filteredChildren : undefined
      }
    }
    return false
  }).filter(Boolean)
}

const filteredTreeData = computed(() => {
  return filterTreeByPermission(treeData.value)
})

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getBusinessNodes()
    treeData.value = res.data
  } catch (error) {
    ElMessage.error('获取业务节点失败')
  } finally {
    loading.value = false
  }
}

const fetchGateways = async () => {
  try {
    const res = await getGateways()
    gateways.value = res.data
  } catch (error) {
    ElMessage.error('获取网关列表失败')
  }
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.parentId = null
  formData.gatewayId = null
  isEdit.value = false
  editingId.value = null
}

const handleCreate = (parentNode) => {
  resetForm()
  if (parentNode) {
    formData.parentId = parentNode.id
    dialogTitle.value = `在「${parentNode.name}」下添加子节点`
  } else {
    dialogTitle.value = '创建业务节点'
  }
  dialogVisible.value = true
}

const handleEdit = (node) => {
  isEdit.value = true
  editingId.value = node.id
  dialogTitle.value = '编辑业务节点'
  formData.name = node.name
  formData.description = node.description || ''
  formData.parentId = node.parentId
  formData.gatewayId = node.gatewayId || null
  dialogVisible.value = true
}

const handleDelete = async (node) => {
  try {
    await ElMessageBox.confirm(`确定要删除节点「${node.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteBusinessNode(node.id)
    ElMessage.success('删除成功')
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateBusinessNode(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createBusinessNode(formData)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      await fetchData()
    } catch (error) {
      ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const handlePermission = (node) => {
  permissionNode.value = node
  permissionData.view = node.permissions?.view ?? true
  permissionData.execute = node.permissions?.execute ?? false
  permissionData.manage = node.permissions?.manage ?? false
  permissionDialogVisible.value = true
}

const handlePermissionSubmit = async () => {
  submitLoading.value = true
  try {
    await updateNodePermissions(permissionNode.value.id, { ...permissionData })
    ElMessage.success('权限配置成功')
    permissionDialogVisible.value = false
    await fetchData()
  } catch (error) {
    ElMessage.error('权限配置失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
  fetchGateways()
})
</script>

<style scoped>
.business-nodes-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 8px;
}

.node-label {
  font-weight: 500;
}

.node-desc {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}

.node-actions {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}

.tree-node:hover .node-actions {
  opacity: 1;
}
</style>
