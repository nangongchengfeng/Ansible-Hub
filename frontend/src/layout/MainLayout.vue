<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <h2 v-if="!isCollapse">Ansible</h2>
        <h2 v-else>A</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        :unique-opened="true"
        router
        class="layout-menu"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-sub-menu index="assets">
          <template #title>
            <el-icon><FolderOpened /></el-icon>
            <span>资产管理</span>
          </template>
          <el-menu-item index="/business-nodes">业务节点</el-menu-item>
          <el-menu-item index="/hosts">主机管理</el-menu-item>
          <el-menu-item index="/system-users">系统用户</el-menu-item>
          <el-menu-item index="/gateways">网关管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="automation">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>自动化配置</span>
          </template>
          <el-menu-item index="/scripts">脚本管理</el-menu-item>
          <el-menu-item index="/playbooks">剧本管理</el-menu-item>
          <el-menu-item index="/command-filters">命令过滤</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="jobs">
          <template #title>
            <el-icon><VideoPlay /></el-icon>
            <span>作业管理</span>
          </template>
          <el-menu-item index="/job-execute">执行作业</el-menu-item>
          <el-menu-item index="/job-templates">作业模板</el-menu-item>
          <el-menu-item index="/job-history">作业历史</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/audit-logs" v-if="isAdminOrAuditor">
          <el-icon><List /></el-icon>
          <template #title>审计日志</template>
        </el-menu-item>
        <el-menu-item index="/users" v-if="isAdmin">
          <el-icon><User /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container class="layout-main-container">
      <el-header class="layout-header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ name: 'dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRouteTitle">
              {{ currentRouteTitle }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">{{ authStore.user?.name || authStore.user?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view :key="$route.path" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  Odometer,
  FolderOpened,
  Document,
  VideoPlay,
  List,
  User,
  Fold,
  Expand,
  ArrowDown
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isCollapse = ref(false)

const activeMenu = computed(() => route.path)
const currentRouteTitle = computed(() => route.meta.title || '')

const isAdmin = computed(() => authStore.user?.role === 'superadmin')
const isAdminOrAuditor = computed(
  () => authStore.user?.role === 'superadmin' || authStore.user?.role === 'auditor'
)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      })
      await authStore.logout()
      ElMessage.success('退出成功')
      router.push({ name: 'login' })
    } catch (error) {
      if (error !== 'cancel') {
        await authStore.logout()
        router.push({ name: 'login' })
      }
    }
  } else if (command === 'profile') {
    ElMessage.info('个人信息功能开发中')
  }
}
</script>

<style scoped>
.layout-container {
  width: 100%;
  height: 100vh;
}

.layout-aside {
  background-color: #2b2f3a;
  transition: width 0.3s;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  background-color: #21252e;
  font-weight: bold;
}

.logo h2 {
  font-size: 18px;
  margin: 0;
}

.layout-menu {
  border: none;
  background-color: #2b2f3a;
}

.layout-menu:not(.el-menu--collapse) {
  width: 220px;
}

.layout-main-container {
  display: flex;
  flex-direction: column;
}

.layout-header {
  background-color: white;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.collapse-icon:hover {
  color: #409eff;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  color: #333;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow: auto;
}
</style>
