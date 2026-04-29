<template>
  <div class="gateways-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>网关管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建网关
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="gateways" stripe>
        <el-table-column prop="name" label="名称" width="180" />
        <el-table-column prop="host" label="主机地址" width="180" />
        <el-table-column prop="port" label="端口" width="100" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
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
      width="500px"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入网关名称" />
        </el-form-item>
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="formData.host" placeholder="请输入网关IP或域名" />
        </el-form-item>
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="formData.port" :min="1" :max="65535" />
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
import { getGateways, createGateway, updateGateway, deleteGateway } from '@/api/gateways'

const loading = ref(false)
const submitLoading = ref(false)
const gateways = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('创建网关')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const formData = reactive({
  name: '',
  host: '',
  port: 22
})

const formRules = {
  name: [{ required: true, message: '请输入网关名称', trigger: 'blur' }],
  host: [{ required: true, message: '请输入主机地址', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getGateways()
    gateways.value = res.data
  } catch (error) {
    ElMessage.error('获取网关列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.name = ''
  formData.host = ''
  formData.port = 22
  isEdit.value = false
  editingId.value = null
}

const handleCreate = () => {
  resetForm()
  dialogTitle.value = '创建网关'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑网关'
  formData.name = row.name
  formData.host = row.host
  formData.port = row.port
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除网关「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteGateway(row.id)
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
        await updateGateway(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createGateway(formData)
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

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.gateways-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
