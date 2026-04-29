<template>
  <div class="playbooks-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>剧本管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建剧本
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="playbooks" stripe>
        <el-table-column prop="name" label="剧本名称" width="200" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="currentVersion" label="当前版本" width="100" />
        <el-table-column prop="createdBy" label="创建者" width="120" />
        <el-table-column prop="updatedAt" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updatedAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button link type="primary" size="small" @click="handleViewVersions(row)">
              <el-icon><Document /></el-icon>
              历史版本
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
      width="800px"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="剧本名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入剧本名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item v-if="isEdit" label="变更说明" prop="changeNote">
          <el-input v-model="formData.changeNote" type="textarea" :rows="2" placeholder="请输入本次变更的说明" />
        </el-form-item>
        <el-form-item label="剧本内容" prop="content">
          <el-input
            v-model="formData.content"
            type="textarea"
            :rows="15"
            placeholder="请输入剧本内容 (YAML)"
            class="code-editor"
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

    <!-- 历史版本对话框 -->
    <el-dialog
      v-model="versionsDialogVisible"
      title="历史版本"
      width="900px"
    >
      <el-table v-loading="versionsLoading" :data="versions" stripe max-height="400">
        <el-table-column prop="version" label="版本" width="100" />
        <el-table-column prop="changeNote" label="变更说明" min-width="200" />
        <el-table-column prop="createdBy" label="创建者" width="120" />
        <el-table-column prop="createdAt" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.createdAt) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleViewVersion(row)">
              查看详情
            </el-button>
            <el-button link type="primary" size="small" @click="handleViewDiff(row)">
              对比
            </el-button>
            <el-button link type="warning" size="small" @click="handleRollback(row)">
              回滚
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 版本详情对话框 -->
    <el-dialog
      v-model="versionDetailVisible"
      title="版本详情"
      width="800px"
    >
      <el-descriptions :column="1" border v-if="currentVersion">
        <el-descriptions-item label="版本">{{ currentVersion.version }}</el-descriptions-item>
        <el-descriptions-item label="变更说明">{{ currentVersion.changeNote }}</el-descriptions-item>
        <el-descriptions-item label="创建者">{{ currentVersion.createdBy }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentVersion.createdAt) }}</el-descriptions-item>
      </el-descriptions>
      <div class="code-display mt-4">
        <pre>{{ currentVersion?.content }}</pre>
      </div>
    </el-dialog>

    <!-- Diff 对比对话框 -->
    <el-dialog
      v-model="diffDialogVisible"
      title="版本对比"
      width="900px"
    >
      <div class="diff-container">
        <div class="diff-side">
          <h4>当前版本</h4>
          <pre>{{ currentPlaybook?.content }}</pre>
        </div>
        <div class="diff-divider"></div>
        <div class="diff-side">
          <h4>版本 {{ selectedVersion?.version }}</h4>
          <pre>{{ selectedVersion?.content }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Document } from '@element-plus/icons-vue'
import { getPlaybooks, createPlaybook, updatePlaybook, deletePlaybook, getPlaybookVersions, getPlaybookVersion, rollbackPlaybook } from '@/api/playbooks'

const loading = ref(false)
const submitLoading = ref(false)
const versionsLoading = ref(false)
const playbooks = ref([])
const versions = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('创建剧本')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const versionsDialogVisible = ref(false)
const currentPlaybook = ref(null)

const versionDetailVisible = ref(false)
const currentVersion = ref(null)

const diffDialogVisible = ref(false)
const selectedVersion = ref(null)

const formData = reactive({
  name: '',
  description: '',
  content: '',
  changeNote: ''
})

const formRules = {
  name: [{ required: true, message: '请输入剧本名称', trigger: 'blur' }],
  content: [{ required: true, message: '请输入剧本内容', trigger: 'blur' }]
}

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPlaybooks()
    playbooks.value = res.data
  } catch (error) {
    ElMessage.error('获取剧本列表失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.content = ''
  formData.changeNote = ''
  isEdit.value = false
  editingId.value = null
}

const handleCreate = () => {
  resetForm()
  dialogTitle.value = '创建剧本'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑剧本'
  formData.name = row.name
  formData.description = row.description
  formData.content = row.content
  formData.changeNote = ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除剧本「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deletePlaybook(row.id)
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
        await updatePlaybook(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createPlaybook(formData)
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

const handleViewVersions = async (row) => {
  currentPlaybook.value = row
  versionsDialogVisible.value = true
  versionsLoading.value = true
  try {
    const res = await getPlaybookVersions(row.id)
    versions.value = res.data.reverse()
  } catch (error) {
    ElMessage.error('获取历史版本失败')
  } finally {
    versionsLoading.value = false
  }
}

const handleViewVersion = async (row) => {
  try {
    const res = await getPlaybookVersion(currentPlaybook.value.id, row.id)
    currentVersion.value = res.data
    versionDetailVisible.value = true
  } catch (error) {
    ElMessage.error('获取版本详情失败')
  }
}

const handleViewDiff = async (row) => {
  selectedVersion.value = row
  diffDialogVisible.value = true
}

const handleRollback = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要回滚到版本 ${row.version} 吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await rollbackPlaybook(currentPlaybook.value.id, row.id)
    ElMessage.success('回滚成功')
    versionsDialogVisible.value = false
    await fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('回滚失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.playbooks-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.code-editor :deep(textarea) {
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
}

.code-display {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  max-height: 400px;
  overflow: auto;
}

.code-display pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.diff-container {
  display: flex;
  gap: 16px;
}

.diff-side {
  flex: 1;
  background: #f5f5f5;
  padding: 16px;
  border-radius: 4px;
  overflow: auto;
  max-height: 500px;
}

.diff-side h4 {
  margin-top: 0;
  margin-bottom: 12px;
}

.diff-side pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.diff-divider {
  width: 1px;
  background: #dcdfe6;
}

.mt-4 {
  margin-top: 16px;
}
</style>
