<template>
  <div class="command-filters-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>命令过滤规则</span>
          <div>
            <el-button type="success" @click="handleCheckCommand">
              <el-icon><Warning /></el-icon>
              测试命令
            </el-button>
            <el-button type="primary" @click="handleCreate">
              <el-icon><Plus /></el-icon>
              创建规则
            </el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="filters" stripe row-key="id">
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            #{{ row.priority }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="规则名称" width="180" />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column prop="pattern" label="匹配模式" min-width="200" show-overflow-tooltip />
        <el-table-column prop="matchType" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.matchType === 'regex' ? 'warning' : 'info'">
              {{ row.matchType === 'regex' ? '正则表达式' : '字符串' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="动作" width="100">
          <template #default="{ row }">
            <el-tag :type="row.action === 'block' ? 'danger' : 'warning'">
              {{ row.action === 'block' ? '禁止' : '警告' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch
              :model-value="row.isEnabled"
              @change="handleToggle(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="创建者" width="120" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row, $index }">
            <el-button link type="primary" size="small" @click="handleMove(row, 'up')" :disabled="$index === 0">
              <el-icon><Top /></el-icon>
              上移
            </el-button>
            <el-button link type="primary" size="small" @click="handleMove(row, 'down')" :disabled="$index === filters.length - 1">
              <el-icon><Bottom /></el-icon>
              下移
            </el-button>
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
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="匹配类型" prop="matchType">
          <el-radio-group v-model="formData.matchType">
            <el-radio value="contains">字符串匹配</el-radio>
            <el-radio value="regex">正则表达式</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="匹配模式" prop="pattern">
          <el-input
            v-model="formData.pattern"
            type="textarea"
            :rows="3"
            placeholder="请输入匹配模式"
          />
        </el-form-item>
        <el-form-item label="动作" prop="action">
          <el-radio-group v-model="formData.action">
            <el-radio value="warn">警告</el-radio>
            <el-radio value="block">禁止</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="启用" prop="isEnabled">
          <el-switch v-model="formData.isEnabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 测试命令对话框 -->
    <el-dialog
      v-model="checkDialogVisible"
      title="测试命令过滤"
      width="600px"
    >
      <el-form label-width="100px">
        <el-form-item label="测试命令">
          <el-input
            v-model="testCommand"
            type="textarea"
            :rows="3"
            placeholder="请输入要测试的命令"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="doCheckCommand" :loading="checkLoading">
            检查
          </el-button>
        </el-form-item>
      </el-form>

      <div v-if="checkResult" class="check-result">
        <el-alert
          :title="checkResult.message"
          :type="checkResult.allowed ? 'success' : 'error'"
          show-icon
          style="margin-bottom: 16px"
        />
        <div v-if="checkResult.matched_rules.length > 0">
          <h4>匹配的规则:</h4>
          <ul>
            <li v-for="rule in checkResult.matched_rules" :key="rule.id">
              {{ rule.name }} ({{ rule.action }})
            </li>
          </ul>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Top, Bottom, Warning } from '@element-plus/icons-vue'
import {
  getCommandFilters,
  createCommandFilter,
  getCommandFilter,
  updateCommandFilter,
  deleteCommandFilter,
  toggleCommandFilter,
  reorderCommandFilters,
  checkCommand
} from '@/api/commandFilters'

const loading = ref(false)
const submitLoading = ref(false)
const checkLoading = ref(false)
const filters = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('创建规则')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const checkDialogVisible = ref(false)
const testCommand = ref('')
const checkResult = ref(null)

const formData = reactive({
  name: '',
  description: '',
  matchType: 'contains',
  pattern: '',
  action: 'block',
  isEnabled: true,
  priority: 0
})

const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  pattern: [{ required: true, message: '请输入匹配模式', trigger: 'blur' }],
  matchType: [{ required: true, message: '请选择匹配类型', trigger: 'change' }],
  action: [{ required: true, message: '请选择动作', trigger: 'change' }]
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
    const res = await getCommandFilters()
    filters.value = res.data.sort((a, b) => a.priority - b.priority)
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.matchType = 'contains'
  formData.pattern = ''
  formData.action = 'block'
  formData.isEnabled = true
  formData.priority = 0
  isEdit.value = false
  editingId.value = null
}

const handleCreate = () => {
  resetForm()
  formData.priority = filters.value.length
  dialogTitle.value = '创建规则'
  dialogVisible.value = true
}

const handleEdit = async (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑规则'
  try {
    const res = await getCommandFilter(row.id)
    const data = res.data
    formData.name = data.name
    formData.description = data.description
    formData.matchType = data.matchType
    formData.pattern = data.pattern
    formData.action = data.action
    formData.isEnabled = data.isEnabled
    formData.priority = data.priority
  } catch (error) {
    formData.name = row.name
    formData.description = row.description
    formData.matchType = row.matchType
    formData.pattern = row.pattern
    formData.action = row.action
    formData.isEnabled = row.isEnabled
    formData.priority = row.priority
  }
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除规则「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteCommandFilter(row.id)
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
    await toggleCommandFilter(row.id)
    ElMessage.success(row.isEnabled ? '已禁用' : '已启用')
    row.isEnabled = !row.isEnabled
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  }
}

const handleMove = async (row, direction) => {
  const currentIndex = filters.value.findIndex(f => f.id === row.id)
  if (currentIndex === -1) return

  const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1
  if (newIndex < 0 || newIndex >= filters.value.length) return

  // 交换位置
  const newOrder = [...filters.value.map(f => f.id)]
  const temp = newOrder[currentIndex]
  newOrder[currentIndex] = newOrder[newIndex]
  newOrder[newIndex] = temp

  try {
    await reorderCommandFilters(newOrder)
    ElMessage.success('排序成功')
    await fetchData()
  } catch (error) {
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
        await updateCommandFilter(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createCommandFilter(formData)
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

const handleCheckCommand = () => {
  testCommand.value = ''
  checkResult.value = null
  checkDialogVisible.value = true
}

const doCheckCommand = async () => {
  if (!testCommand.value.trim()) {
    ElMessage.warning('请输入要测试的命令')
    return
  }

  checkLoading.value = true
  try {
    const res = await checkCommand(testCommand.value)
    checkResult.value = res.data
  } catch (error) {
    ElMessage.error(formatValidationError(error))
  } finally {
    checkLoading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.command-filters-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.check-result {
  margin-top: 16px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.check-result ul {
  margin: 0;
  padding-left: 20px;
}

.check-result li {
  margin: 8px 0;
}
</style>
