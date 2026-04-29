<template>
  <el-card shadow="hover">
    <template #header>
      <span>{{ title }}</span>
    </template>
    <el-empty description="This feature is coming soon" />
  </el-card>
</template>

<script setup>
const props = defineProps({
  title: {
    type: String,
    default: 'Feature'
  }
})
</script>
