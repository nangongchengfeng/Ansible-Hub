<template>
  <div class="job-execute-page">
    <el-card>
      <template #header>
        <span>临时作业执行</span>
      </template>

      <el-form :model="formData" label-width="120px">
        <el-form-item label="执行类型">
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
            <el-option-group v-for="node in nodeHostMap" :key="node.id" :label="node.name">
              <el-option
                v-for="host in node.hosts"
                :key="host.id"
                :label="`${host.name} (${host.hostname})`"
                :value="host.id"
              />
            </el-option-group>
          </el-select>
        </el-form-item>

        <!-- Shell 命令 -->
        <template v-if="formData.executeType === 'shell'">
          <el-form-item label="命令内容">
            <el-input
              v-model="formData.command"
              type="textarea"
              :rows="4"
              placeholder="请输入 Shell 命令"
              @input="handleCommandCheck"
            />
            <el-alert
              v-if="checkResult"
              :type="checkResult.blocked ? 'error' : 'success'"
              :closable="false"
              style="margin-top: 10px"
            >
              {{ checkResult.message }}
            </el-alert>
          </el-form-item>
        </template>

        <!-- Ansible 模块 -->
        <template v-if="formData.executeType === 'module'">
          <el-form-item label="模块名称">
            <el-input v-model="formData.moduleName" placeholder="例如：shell, command, copy" />
          </el-form-item>
          <el-form-item label="模块参数">
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
          <el-form-item label="选择剧本">
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
          <el-form-item label="选择脚本">
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
      </el-form>

      <div class="action-buttons" style="margin-top: 20px">
        <el-button type="primary" @click="handleExecute" :disabled="!canExecute || isRunning">
          <el-icon><VideoPlay /></el-icon>
          执行作业
        </el-button>
        <el-button type="danger" @click="handleCancel" v-if="isRunning">
          <el-icon><Close /></el-icon>
          取消作业
        </el-button>
        <el-button @click="handleSaveTemplate" v-if="jobStatus === 'success'">
          <el-icon><Document /></el-icon>
          保存为模板
        </el-button>
      </div>
    </el-card>

    <!-- 执行结果 -->
    <el-card style="margin-top: 20px" v-if="isRunning || jobStatus">
      <template #header>
        <div class="card-header">
          <span>执行结果</span>
          <el-tag :type="statusType">{{ statusText }}</el-tag>
        </div>
      </template>

      <div class="log-output" ref="logOutput">
        <div v-for="(log, index) in logs" :key="index" class="log-line">
          <span class="log-time">[{{ log.time }}]</span>
          <span class="log-text">{{ log.text }}</span>
        </div>
        <div v-if="isRunning" class="log-line">
          <span class="log-time">[{{ currentTime }}]</span>
          <span class="log-text">执行中...</span>
          <span class="log-dots"></span>
        </div>
      </div>
    </el-card>

    <!-- 保存模板对话框 -->
    <el-dialog v-model="saveDialogVisible" title="保存为模板" width="500px">
      <el-form :model="templateForm" label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="templateForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="saveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmSaveTemplate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VideoPlay, Close, Document } from '@element-plus/icons-vue'
import { getHostList, getScriptList, getPlaybookList, executeJob, cancelJob, checkCommand, saveAsTemplate } from '@/api/jobExecute'
import { getBusinessNodes } from '@/api/business-nodes'

const loading = ref(false)
const isRunning = ref(false)
const jobStatus = ref('')
const jobId = ref('')
const logs = ref([])
const checkResult = ref(null)
const saveDialogVisible = ref(false)

const formData = reactive({
  executeType: 'shell',
  hostIds: [],
  command: '',
  moduleName: '',
  moduleArgs: '',
  playbookId: null,
  scriptId: null
})

const templateForm = reactive({
  name: '',
  description: ''
})

const hosts = ref([])
const scripts = ref([])
const playbooks = ref([])
const businessNodes = ref([])
const nodeHostMap = computed(() => {
  const map = {}
  const hostMap = {}
  hosts.value.forEach(host => {
    hostMap[host.businessNodeId] = hostMap[host.businessNodeId] || []
    hostMap[host.businessNodeId].push(host)
  })

  const result = []
  const flattenNodes = (nodes) => {
    for (const node of nodes) {
      result.push({
        id: node.id,
        name: node.name,
        hosts: hostMap[node.id] || []
      })
      if (node.children) {
        flattenNodes(node.children)
      }
    }
  }
  flattenNodes(businessNodes.value)
  return result
})

const canExecute = computed(() => {
  if (formData.hostIds.length === 0) return false
  if (formData.executeType === 'shell' && !formData.command) return false
  if (formData.executeType === 'module' && !formData.moduleName) return false
  if (formData.executeType === 'playbook' && !formData.playbookId) return false
  if (formData.executeType === 'script' && !formData.scriptId) return false
  if (checkResult.value?.blocked) return false
  return true
})

const statusType = computed(() => {
  if (jobStatus.value === 'success') return 'success'
  if (jobStatus.value === 'failed') return 'danger'
  if (jobStatus.value === 'cancelled') return 'warning'
  return 'info'
})

const statusText = computed(() => {
  const map = {
    success: '执行成功',
    failed: '执行失败',
    cancelled: '已取消',
    running: '执行中'
  }
  return map[jobStatus.value] || ''
})

const currentTime = computed(() => {
  return new Date().toLocaleTimeString('zh-CN')
})

const addLog = (text) => {
  logs.value.push({
    time: new Date().toLocaleTimeString('zh-CN'),
    text
  })
  nextTick(() => {
    const logOutput = document.querySelector('.log-output')
    if (logOutput) {
      logOutput.scrollTop = logOutput.scrollHeight
    }
  })
}

const fetchData = async () => {
  loading.value = true
  try {
    const [hostRes, scriptRes, playbookRes, nodeRes] = await Promise.all([
      getHostList(),
      getScriptList(),
      getPlaybookList(),
      getBusinessNodes()
    ])
    hosts.value = hostRes.data
    scripts.value = scriptRes.data
    playbooks.value = playbookRes.data
    businessNodes.value = nodeRes.data
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const handleTypeChange = () => {
  checkResult.value = null
}

const handleCommandCheck = async () => {
  if (!formData.command) {
    checkResult.value = null
    return
  }
  try {
    const res = await checkCommand(formData.command)
    checkResult.value = res.data
  } catch (error) {
    checkResult.value = null
  }
}

const handleExecute = async () => {
  logs.value = []
  isRunning.value = true
  jobStatus.value = ''

  addLog('开始执行作业...')

  try {
    const res = await executeJob(formData)
    jobId.value = res.data.jobId
    addLog(`作业已启动，作业ID: ${jobId.value}`)

    await simulateExecution()
  } catch (error) {
    jobStatus.value = 'failed'
    addLog('执行失败: ' + error.message)
  } finally {
    isRunning.value = false
  }
}

const simulateExecution = async () => {
  const fakeLogs = [
    '连接主机...',
    '主机连接成功',
    '上传执行文件...',
    '开始执行...',
    '执行进度: 25%',
    '执行进度: 50%',
    '执行进度: 75%',
    '执行进度: 100%',
    '收集执行结果...'
  ]

  for (let i = 0; i < fakeLogs.length; i++) {
    if (!isRunning.value) break
    await new Promise(resolve => setTimeout(resolve, 500))
    addLog(fakeLogs[i])
  }

  if (isRunning.value) {
    jobStatus.value = 'success'
    addLog('作业执行完成！')
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消当前作业吗？', '确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await cancelJob(jobId.value)
    isRunning.value = false
    jobStatus.value = 'cancelled'
    addLog('作业已取消')
    ElMessage.success('作业已取消')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const handleSaveTemplate = () => {
  saveDialogVisible.value = true
}

const handleConfirmSaveTemplate = async () => {
  if (!templateForm.name) {
    ElMessage.warning('请输入模板名称')
    return
  }

  try {
    await saveAsTemplate({
      ...templateForm,
      ...formData
    })
    ElMessage.success('保存成功')
    saveDialogVisible.value = false
    templateForm.name = ''
    templateForm.description = ''
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.job-execute-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.log-output {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow-y: auto;
}

.log-line {
  margin-bottom: 4px;
}

.log-time {
  color: #6a9955;
  margin-right: 8px;
}

.log-dots::after {
  content: '';
  animation: dots 1.5s steps(5, end) infinite;
}

@keyframes dots {
  0%, 20% { content: ''; }
  40% { content: '.'; }
  60% { content: '..'; }
  80%, 100% { content: '...'; }
}
</style>
