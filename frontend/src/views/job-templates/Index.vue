<template>
  <div class="job-templates-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>作业模板管理</span>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建模板
          </el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="filteredTemplates" stripe>
        <el-table-column prop="name" label="模板名称" width="200" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column label="执行类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getExecuteTypeText(row.executeType) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="cronExpression" label="调度计划" width="150" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleToggle(row)" />
          </template>
        </el-table-column>
        <el-table-column prop="createdBy" label="创建者" width="100" />
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" size="small" @click="handleTrigger(row)">
              <el-icon><VideoPlay /></el-icon>
              执行
            </el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button link type="primary" size="small" @click="handlePermission(row)">
              <el-icon><Key /></el-icon>
              权限
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
      width="700px"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入模板名称" />
        </el-form-item>

        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>

        <el-form-item label="执行类型" prop="executeType">
          <el-radio-group v-model="formData.executeType" @change="handleTypeChange">
            <el-radio value="shell">Shell 命令</el-radio>
            <el-radio value="module">Ansible 模块</el-radio>
            <el-radio value="playbook">Ansible 剧本</el-radio>
            <el-radio value="script">脚本</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="目标主机">
          <el-select
            v-model="formData.hostIds"
            multiple
            placeholder="请选择主机"
            style="width: 100%"
          >
            <el-option
              v-for="host in hosts"
              :key="host.id"
              :label="`${host.name} (${host.hostname})`"
              :value="host.id"
            />
          </el-select>
        </el-form-item>

        <!-- Shell 命令 -->
        <template v-if="formData.executeType === 'shell'">
          <el-form-item label="命令内容" prop="command">
            <el-input
              v-model="formData.command"
              type="textarea"
              :rows="4"
              placeholder="请输入 Shell 命令"
            />
          </el-form-item>
        </template>

        <!-- Ansible 模块 -->
        <template v-if="formData.executeType === 'module'">
          <el-form-item label="模块名称" prop="moduleName">
            <el-input v-model="formData.moduleName" placeholder="例如：shell, command, copy" />
          </el-form-item>
          <el-form-item label="模块参数" prop="moduleArgs">
            <el-input
              v-model="formData.moduleArgs"
              type="textarea"
              :rows="4"
              placeholder="请输入模块参数"
            />
          </el-form-item>
        </template>

        <!-- Ansible 剧本 -->
        <template v-if="formData.executeType === 'playbook'">
          <el-form-item label="选择剧本" prop="playbookId">
            <el-select v-model="formData.playbookId" placeholder="请选择剧本" style="width: 100%">
              <el-option
                v-for="playbook in playbooks"
                :key="playbook.id"
                :label="playbook.name"
                :value="playbook.id"
              />
            </el-select>
          </el-form-item>
        </template>

        <!-- 脚本 -->
        <template v-if="formData.executeType === 'script'">
          <el-form-item label="选择脚本" prop="scriptId">
            <el-select v-model="formData.scriptId" placeholder="请选择脚本" style="width: 100%">
              <el-option
                v-for="script in scripts"
                :key="script.id"
                :label="script.name"
                :value="script.id"
              />
            </el-select>
          </el-form-item>
        </template>

        <el-form-item label="调度计划" prop="cronExpression">
          <div class="cron-input">
            <el-input v-model="formData.cronExpression" placeholder="例如：0 2 * * *" style="flex: 1" />
            <el-button @click="showCronHelper = true" style="margin-left: 10px">Cron 助手</el-button>
          </div>
          <div style="margin-top: 8px; color: #909399; font-size: 12px">
            格式：分 时 日 月 周 (示例：0 2 * * * 表示每天凌晨2点执行)
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Cron 助手对话框 -->
    <el-dialog v-model="showCronHelper" title="Cron 表达式助手" width="600px">
      <el-form label-width="100px">
        <el-form-item label="分钟">
          <el-select v-model="cronHelper.minute" placeholder="选择分钟" style="width: 100%">
            <el-option label="每分钟" value="*" />
            <el-option v-for="i in 60" :key="i - 1" :label="String(i - 1)" :value="String(i - 1)" />
          </el-select>
        </el-form-item>
        <el-form-item label="小时">
          <el-select v-model="cronHelper.hour" placeholder="选择小时" style="width: 100%">
            <el-option label="每小时" value="*" />
            <el-option v-for="i in 24" :key="i - 1" :label="String(i - 1)" :value="String(i - 1)" />
          </el-select>
        </el-form-item>
        <el-form-item label="日期">
          <el-select v-model="cronHelper.day" placeholder="选择日期" style="width: 100%">
            <el-option label="每天" value="*" />
            <el-option v-for="i in 31" :key="i" :label="String(i)" :value="String(i)" />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-select v-model="cronHelper.month" placeholder="选择月份" style="width: 100%">
            <el-option label="每月" value="*" />
            <el-option v-for="i in 12" :key="i" :label="String(i)" :value="String(i)" />
          </el-select>
        </el-form-item>
        <el-form-item label="星期">
          <el-select v-model="cronHelper.week" placeholder="选择星期" style="width: 100%">
            <el-option label="每天" value="*" />
            <el-option v-for="i in 7" :key="i - 1" :label="String(i - 1)" :value="String(i - 1)" />
          </el-select>
        </el-form-item>
      </el-form>
      <div style="margin-top: 16px; padding: 12px; background: #f5f7fa; border-radius: 4px">
        <strong>生成的表达式：</strong> {{ `${cronHelper.minute} ${cronHelper.hour} ${cronHelper.day} ${cronHelper.month} ${cronHelper.week}` }}
      </div>
      <template #footer>
        <el-button @click="showCronHelper = false">取消</el-button>
        <el-button type="primary" @click="applyCronExpression">应用</el-button>
      </template>
    </el-dialog>

    <!-- 权限配置对话框 -->
    <el-dialog
      v-model="permissionDialogVisible"
      title="权限配置"
      width="500px"
    >
      <el-form label-width="100px">
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
        <el-button type="primary" :loading="submitLoading" @click="handlePermissionSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Key, VideoPlay } from '@element-plus/icons-vue'
import { getJobTemplates, createJobTemplate, updateJobTemplate, deleteJobTemplate, toggleJobTemplate, triggerJobTemplate, updateTemplatePermissions } from '@/api/jobTemplates'
import { getHosts } from '@/api/hosts'
import { getScripts } from '@/api/scripts'
import { getPlaybooks } from '@/api/playbooks'
import { useAuthStore } from '@/stores/auth'

const loading = ref(false)
const submitLoading = ref(false)
const templates = ref([])
const hosts = ref([])
const scripts = ref([])
const playbooks = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('创建模板')
const formRef = ref(null)
const isEdit = ref(false)
const editingId = ref(null)

const permissionDialogVisible = ref(false)
const permissionTemplateId = ref(null)

const showCronHelper = ref(false)

const formData = reactive({
  name: '',
  description: '',
  executeType: 'shell',
  hostIds: [],
  command: '',
  moduleName: '',
  moduleArgs: '',
  playbookId: null,
  scriptId: null,
  cronExpression: ''
})

const permissionData = reactive({
  view: true,
  execute: false,
  manage: false
})

const cronHelper = reactive({
  minute: '0',
  hour: '2',
  day: '*',
  month: '*',
  week: '*'
})

const formRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  executeType: [{ required: true, message: '请选择执行类型', trigger: 'change' }],
  cronExpression: [{ required: true, message: '请输入调度计划', trigger: 'blur' }]
}

const authStore = useAuthStore()

const filteredTemplates = computed(() => {
  if (authStore.user?.role === 'superadmin') {
    return templates.value
  }
  return templates.value.filter(t => t.permissions?.view)
})

const getExecuteTypeText = (type) => {
  const map = {
    shell: 'Shell',
    module: 'Ansible模块',
    playbook: 'Ansible剧本',
    script: '脚本'
  }
  return map[type] || type
}

const fetchData = async () => {
  loading.value = true
  try {
    const [templateRes, hostRes, scriptRes, playbookRes] = await Promise.all([
      getJobTemplates(),
      getHosts(),
      getScripts(),
      getPlaybooks()
    ])
    templates.value = templateRes.data
    hosts.value = hostRes.data
    scripts.value = scriptRes.data
    playbooks.value = playbookRes.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.name = ''
  formData.description = ''
  formData.executeType = 'shell'
  formData.hostIds = []
  formData.command = ''
  formData.moduleName = ''
  formData.moduleArgs = ''
  formData.playbookId = null
  formData.scriptId = null
  formData.cronExpression = ''
  isEdit.value = false
  editingId.value = null
}

const handleCreate = () => {
  resetForm()
  dialogTitle.value = '创建模板'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑模板'
  formData.name = row.name
  formData.description = row.description
  formData.executeType = row.executeType
  formData.hostIds = [...row.hostIds]
  formData.command = row.command || ''
  formData.moduleName = row.moduleName || ''
  formData.moduleArgs = row.moduleArgs || ''
  formData.playbookId = row.playbookId || null
  formData.scriptId = row.scriptId || null
  formData.cronExpression = row.cronExpression || ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除模板「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteJobTemplate(row.id)
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
    await toggleJobTemplate(row.id)
    ElMessage.success(row.enabled ? '已启用' : '已禁用')
  } catch (error) {
    row.enabled = !row.enabled
    ElMessage.error('操作失败')
  }
}

const handleTrigger = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要立即执行模板「${row.name}」吗？`, '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    const res = await triggerJobTemplate(row.id)
    ElMessage.success(`执行成功！作业ID：${res.data.jobId}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('执行失败')
    }
  }
}

const handlePermission = (row) => {
  permissionTemplateId.value = row.id
  permissionData.view = row.permissions?.view ?? true
  permissionData.execute = row.permissions?.execute ?? false
  permissionData.manage = row.permissions?.manage ?? false
  permissionDialogVisible.value = true
}

const handlePermissionSubmit = async () => {
  submitLoading.value = true
  try {
    await updateTemplatePermissions(permissionTemplateId.value, { ...permissionData })
    ElMessage.success('权限更新成功')
    permissionDialogVisible.value = false
    await fetchData()
  } catch (error) {
    ElMessage.error('权限更新失败')
  } finally {
    submitLoading.value = false
  }
}

const handleTypeChange = () => {
  // 清空其他类型的参数
  formData.command = ''
  formData.moduleName = ''
  formData.moduleArgs = ''
  formData.playbookId = null
  formData.scriptId = null
}

const applyCronExpression = () => {
  formData.cronExpression = `${cronHelper.minute} ${cronHelper.hour} ${cronHelper.day} ${cronHelper.month} ${cronHelper.week}`
  showCronHelper.value = false
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      if (isEdit.value) {
        await updateJobTemplate(editingId.value, formData)
        ElMessage.success('更新成功')
      } else {
        await createJobTemplate(formData)
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
.job-templates-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cron-input {
  display: flex;
  align-items: center;
}
</style>
