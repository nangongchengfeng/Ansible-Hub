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
        :data="treeData"
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
            :data="treeData"
            :props="treeProps"
            placeholder="选择父节点（不选则为根节点）"
            clearable
            check-strictly
            :disabled="isEdit"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { getBusinessNodes, createBusinessNode, updateBusinessNode, deleteBusinessNode } from '@/api/business-nodes'

const loading = ref(false)
const submitLoading = ref(false)
const treeData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('创建业务节点')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

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

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getBusinessNodes()
    treeData.value = res.data
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.parentId = null
  formData.gatewayId = null
  isEdit.value = false
  editingId.value = null
  if (formRef.value) {
    formRef.value.clearValidate()
  }
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
    await ElMessageBox.confirm(`确定要删除节点「${node.name}」吗？子节点也会一并删除！`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteBusinessNode(node.id)
    ElMessage.success('删除成功')
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(formatValidationError(error))
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitLoading.value = true
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
    if (error !== false) {
      ElMessage.error(formatValidationError(error))
    }
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchData()
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
