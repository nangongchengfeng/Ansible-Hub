<template>
  <div class="system-users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>系统用户管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建用户
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column label="认证类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ row.authType === 'password' ? '密码' : '密钥' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="密码/密钥" min-width="200">
          <template #default="{ row }">
            <template v-if="canViewSensitive(row)">
              <el-input
                v-if="row.authType === 'password'"
                v-model="row.password"
                type="password"
                readonly
                show-password
                size="small"
                style="width: 200px"
              />
              <el-input
                v-else
                v-model="showPrivateKeys[row.id]"
                type="textarea"
                :rows="3"
                readonly
                size="small"
              />
            </template>
            <span v-else>******</span>
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="创建者" width="120" />
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
      width="600px"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="认证类型" prop="authType">
          <el-radio-group v-model="formData.authType">
            <el-radio value="password">密码</el-radio>
            <el-radio value="key">密钥</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="formData.authType === 'password'" label="密码" prop="password">
          <el-input v-model="formData.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
        <el-form-item v-if="formData.authType === 'key'" label="私钥" prop="privateKey">
          <el-input v-model="formData.privateKey" type="textarea" :rows="6" placeholder="请输入私钥内容" />
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
import { getSystemUsers, createSystemUser, updateSystemUser, deleteSystemUser } from '@/api/system-users'
import { useAuthStore } from '@/stores/auth'

const loading = ref(false)
const submitLoading = ref(false)
const users = ref([])
const showPrivateKeys = reactive({})

const dialogVisible = ref(false)
const dialogTitle = ref('创建系统用户')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const formData = reactive({
  name: '',
  username: '',
  authType: 'password',
  password: '',
  privateKey: ''
})

const formRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  authType: [{ required: true, message: '请选择认证类型', trigger: 'change' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  privateKey: [{ required: true, message: '请输入私钥', trigger: 'blur' }]
}

const authStore = useAuthStore()

const canViewSensitive = (row) => {
  // 超级管理员或创建者可以查看
  return authStore.user?.role === 'superadmin' || row.createdBy === authStore.user?.username
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getSystemUsers()
    users.value = res.data
    // 初始化私钥显示
    users.value.forEach(user => {
      if (user.authType === 'key') {
        showPrivateKeys[user.id] = user.privateKey
      }
    })
  } catch (error) {
    ElMessage.error('获取系统用户失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.name = ''
  formData.username = ''
  formData.authType = 'password'
  formData.password = ''
  formData.privateKey = ''
  isEdit.value = false
  editingId.value = null
}

const handleCreate = () => {
  resetForm()
  dialogTitle.value = '创建系统用户'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑系统用户'
  formData.name = row.name
  formData.username = row.username
  formData.authType = row.authType
  formData.password = row.password || ''
  formData.privateKey = row.privateKey || ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除系统用户「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteSystemUser(row.id)
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

  // 根据认证类型动态验证
  const rules = { ...formRules }
  if (formData.authType === 'password') {
    delete rules.privateKey
  } else {
    delete rules.password
  }

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (isEdit.value) {
        // 只发送修改的字段
        const updateData = { name: formData.name }
        if (formData.authType === 'password' && formData.password) {
          updateData.password = formData.password
        }
        if (formData.authType === 'key' && formData.privateKey) {
          updateData.privateKey = formData.privateKey
        }
        await updateSystemUser(editingId.value, updateData)
        ElMessage.success('更新成功')
      } else {
        await createSystemUser(formData)
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
.system-users-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
