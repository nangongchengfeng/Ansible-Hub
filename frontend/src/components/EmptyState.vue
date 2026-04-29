<template>
  <div class="empty-state">
    <el-empty :description="description">
      <template v-if="$slots.default">
        <slot />
      </template>
      <el-button v-else-if="actionText" type="primary" @click="$emit('action')">
        {{ actionText }}
      </el-button>
    </el-empty>
  </div>
</template>

<script setup>
defineProps({
  description: {
    type: String,
    default: '暂无数据'
  },
  actionText: {
    type: String,
    default: ''
  }
})

defineEmits(['action'])
</script>

<style scoped>
.empty-state {
  padding: 40px 0;
}
</style>
