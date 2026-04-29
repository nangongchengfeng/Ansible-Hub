<template>
  <div class="search-filter">
    <el-form :inline="true" :model="filterModel" class="filter-form">
      <slot />
      <el-form-item v-if="showReset || showSearch">
        <el-button v-if="showSearch" type="primary" @click="handleSearch">搜索</el-button>
        <el-button v-if="showReset" @click="handleReset">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  showReset: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'search', 'reset'])

const filterModel = reactive({ ...props.modelValue })

const handleSearch = () => {
  emit('update:modelValue', { ...filterModel })
  emit('search', { ...filterModel })
}

const handleReset = () => {
  Object.keys(filterModel).forEach(key => {
    filterModel[key] = ''
  })
  emit('update:modelValue', { ...filterModel })
  emit('reset', { ...filterModel })
}
</script>

<style scoped>
.search-filter {
  margin-bottom: 20px;
}

.filter-form {
  margin: 0;
}
</style>
