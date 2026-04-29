<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="400px"
    :before-close="handleCancel"
  >
    <div class="confirm-content">
      <el-icon v-if="type === 'warning'" class="icon warning-icon">
        <WarningFilled />
      </el-icon>
      <el-icon v-else-if="type === 'danger'" class="icon danger-icon">
        <CircleCloseFilled />
      </el-icon>
      <el-icon v-else class="icon info-icon">
        <InfoFilled />
      </el-icon>
      <span class="message">{{ message }}</span>
    </div>
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button :type="confirmButtonType" @click="handleConfirm" :loading="loading">
        {{ confirmButtonText }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import { WarningFilled, CircleCloseFilled, InfoFilled } from '@element-plus/icons-vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '确认'
  },
  message: {
    type: String,
    default: '确定要执行此操作吗？'
  },
  type: {
    type: String,
    default: 'warning',
    validator: (val) => ['warning', 'danger', 'info'].includes(val)
  },
  confirmButtonText: {
    type: String,
    default: '确定'
  },
  confirmButtonType: {
    type: String,
    default: 'primary'
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
  visible.value = false
}
</script>

<style scoped>
.confirm-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.icon {
  font-size: 24px;
}

.warning-icon {
  color: #e6a23c;
}

.danger-icon {
  color: #f56c6c;
}

.info-icon {
  color: #409eff;
}

.message {
  font-size: 14px;
  color: #606266;
}
</style>
