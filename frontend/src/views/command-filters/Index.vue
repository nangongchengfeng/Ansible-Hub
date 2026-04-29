<template>
  <div class="command-filters-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>命令过滤规则</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建规则
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="filters" stripe>
        <el-table-column prop="priority" label="优先级" width="100" sortable>
          <template #default="{ row }">
            #{{ row.priority }}
          </template>
        </el-table-column>
        <el-table-column prop="name" label="规则名称" width="180" />
        <el-table-column prop="pattern" label="匹配模式" min-width="200" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'regex' ? 'warning' : 'info'">
              {{ row.type === 'regex' ? '正则表达式' : '字符串' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleToggle(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="创建者" width="120" />
        <el-table-column label="操作" width="280" fixed="right">
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
        <el-form-item label="匹配类型" prop="type">
          <el-radio-group v-model="formData.type">
            <el-radio value="string">字符串匹配</el-radio>
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
import { Plus, Edit, Delete, Top, Bottom } from '@element-plus/icons-vue'
import { getCommandFilters, createCommandFilter, updateCommandFilter, deleteCommandFilter, toggleCommandFilter, moveCommandFilter } from '@/api/commandFilters'

const loading = ref(false)
const submitLoading = ref(false)
const filters = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('创建规则')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const formData = reactive({
  name: '',
  type: 'string',
  pattern: ''
})

const formRules = {
  name: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  pattern: [{ required: true, message: '请输入匹配模式', trigger: 'blur' }],
  type: [{ required: true, message: '请选择匹配类型', trigger: 'change' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getCommandFilters()
    filters.value = res.data.sort((a, b) => a.priority - b.priority)
  } catch (error) {
    ElMessage.error('获取规则列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.name = ''
  formData.type = 'string'
  formData.pattern = ''
  isEdit.value = false
  editingId.value = null
}

const handleCreate = () => {
  resetForm()
  dialogTitle.value = '创建规则'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑规则'
  formData.name = row.name
  formData.type = row.type
  formData.pattern = row.pattern
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
      ElMessage.error('删除失败')
    }
  }
}

const handleToggle = async (row) => {
  try {
    await toggleCommandFilter(row.id)
    ElMessage.success(row.enabled ? '已启用' : '已禁用')
  } catch (error) {
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
  }
}

const handleMove = async (row, direction) => {
  try {
    await moveCommandFilter(row.id, direction)
    ElMessage.success(direction === 'up' ? '已上移' : '已下移')
    await fetchData()
  } catch (error) {
    ElMessage.error('移动失败')
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
.command-filters-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
