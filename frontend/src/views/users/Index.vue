<template>
  <div class="users-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>用户管理</span>
          <el-button type="primary" @click="handleCreate" v-if="canManageUsers">
            添加用户
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="users" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" width="150" />
        <el-table-column prop="name" label="姓名" width="150" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)" v-if="canManageUsers">
              编辑
            </el-button>
            <el-button link type="warning" size="small" @click="handleResetPassword(row)" v-if="canManageUsers">
              重置密码
            </el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)" v-if="canManageUsers">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 创建/编辑用户对话框 -->
    <el-dialog
      v-model="userDialogVisible"
      :title="editingUser ? '编辑用户' : '添加用户'"
      width="500px"
    >
      <el-form :model="userForm" :rules="userRules" ref="userFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="!!editingUser" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="userForm.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="userForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="userForm.role" placeholder="请选择角色">
            <el-option label="超级管理员" value="superadmin" />
            <el-option label="审计员" value="auditor" />
            <el-option label="操作员" value="operator" />
          </el-select>
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!editingUser">
          <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="passwordDialogVisible"
      title="重置密码"
      width="400px"
    >
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="80px">
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmResetPassword">确认</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="400px"
    >
      <p>确定要删除用户「{{ deletingUser?.name || deletingUser?.username }}」吗？</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="handleConfirmDelete">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUsers, createUser, updateUser, deleteUser, resetUserPassword } from '@/api/users'
import { useAuthStore } from '@/stores/auth'

const loading = ref(false)
const users = ref([])
const userDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const deleteDialogVisible = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)
const userFormRef = ref(null)
const passwordFormRef = ref(null)

const userForm = reactive({
  username: '',
  name: '',
  email: '',
  role: '',
  password: ''
})

const passwordForm = reactive({
  newPassword: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.newPassword) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const userRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名至少3个字符', trigger: 'blur' }
  ],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱', trigger: 'blur' }
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ]
}

const passwordRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const authStore = useAuthStore()

const canManageUsers = computed(() => {
  return authStore.user?.role === 'superadmin'
})

const getRoleType = (role) => {
  const map = {
    superadmin: 'danger',
    auditor: 'warning',
    operator: 'primary'
  }
  return map[role] || ''
}

const getRoleText = (role) => {
  const map = {
    superadmin: '超级管理员',
    auditor: '审计员',
    operator: '操作员'
  }
  return map[role] || role
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 格式化后端验证错误
const formatValidationError = (error) => {
  if (error?.response?.data?.detail) {
    const details = error.response.data.detail
    if (Array.isArray(details)) {
      return details.map(err => {
        const field = err.loc?.slice(-1)[0] || ''
        const fieldName = {
          username: '用户名',
          name: '姓名',
          real_name: '姓名',
          email: '邮箱',
          role: '角色',
          password: '密码',
          newPassword: '新密码',
          new_password: '新密码'
        }[field] || field
        return `${fieldName}: ${err.msg}`
      }).join('\n')
    }
    return details
  }
  if (error?.message) {
    return error.message
  }
  return '操作失败，请重试'
}

const fetchData = async () => {
  if (!canManageUsers.value) {
    ElMessage.error('您没有权限管理用户')
    return
  }

  loading.value = true
  try {
    const res = await getUsers()
    users.value = res.data
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  } finally {
    loading.value = false
  }
}

const resetUserForm = () => {
  userForm.username = ''
  userForm.name = ''
  userForm.email = ''
  userForm.role = ''
  userForm.password = ''
  if (userFormRef.value) {
    userFormRef.value.clearValidate()
  }
}

const resetPasswordForm = () => {
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  if (passwordFormRef.value) {
    passwordFormRef.value.clearValidate()
  }
}

const handleCreate = () => {
  editingUser.value = null
  resetUserForm()
  userDialogVisible.value = true
}

const handleEdit = (row) => {
  editingUser.value = row
  userForm.username = row.username
  userForm.name = row.name
  userForm.email = row.email
  userForm.role = row.role
  userDialogVisible.value = true
}

const handleSaveUser = async () => {
  if (!userFormRef.value) return

  try {
    await userFormRef.value.validate()

    if (editingUser.value) {
      await updateUser(editingUser.value.id, {
        name: userForm.name,
        email: userForm.email,
        role: userForm.role
      })
      ElMessage.success('用户更新成功')
    } else {
      await createUser(userForm)
      ElMessage.success('用户创建成功')
    }

    userDialogVisible.value = false
    fetchData()
  } catch (error) {
    if (error !== false) {
      ElMessage.error(formatValidationError(error))
    }
  }
}

const handleResetPassword = (row) => {
  deletingUser.value = row
  resetPasswordForm()
  passwordDialogVisible.value = true
}

const handleConfirmResetPassword = async () => {
  if (!passwordFormRef.value) return

  try {
    await passwordFormRef.value.validate()
    await resetUserPassword(deletingUser.value.id, passwordForm.newPassword)
    ElMessage.success('密码重置成功')
    passwordDialogVisible.value = false
  } catch (error) {
    if (error !== false) {
      ElMessage.error(formatValidationError(error))
    }
  }
}

const handleDelete = (row) => {
  deletingUser.value = row
  deleteDialogVisible.value = true
}

const handleConfirmDelete = async () => {
  try {
    await deleteUser(deletingUser.value.id)
    ElMessage.success('用户删除成功')
    deleteDialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.users-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
