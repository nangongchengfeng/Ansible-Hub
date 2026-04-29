import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/layout/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '仪表盘' }
        },
        {
          path: 'business-nodes',
          name: 'business-nodes',
          component: () => import('@/views/business-nodes/Index.vue'),
          meta: { title: '业务节点' }
        },
        {
          path: 'hosts',
          name: 'hosts',
          component: () => import('@/views/hosts/Index.vue'),
          meta: { title: '主机管理' }
        },
        {
          path: 'system-users',
          name: 'system-users',
          component: () => import('@/views/system-users/Index.vue'),
          meta: { title: '系统用户' }
        },
        {
          path: 'gateways',
          name: 'gateways',
          component: () => import('@/views/gateways/Index.vue'),
          meta: { title: '网关管理' }
        },
        {
          path: 'scripts',
          name: 'scripts',
          component: () => import('@/views/scripts/Index.vue'),
          meta: { title: '脚本管理' }
        },
        {
          path: 'playbooks',
          name: 'playbooks',
          component: () => import('@/views/playbooks/Index.vue'),
          meta: { title: '剧本管理' }
        },
        {
          path: 'command-filters',
          name: 'command-filters',
          component: () => import('@/views/command-filters/Index.vue'),
          meta: { title: '命令过滤' }
        },
        {
          path: 'job-execute',
          name: 'job-execute',
          component: () => import('@/views/job-execute/Index.vue'),
          meta: { title: '作业执行' }
        },
        {
          path: 'job-templates',
          name: 'job-templates',
          component: () => import('@/views/job-templates/Index.vue'),
          meta: { title: '作业模板' }
        },
        {
          path: 'job-history',
          name: 'job-history',
          component: () => import('@/views/job-history/Index.vue'),
          meta: { title: '作业历史' }
        },
        {
          path: 'audit-logs',
          name: 'audit-logs',
          component: () => import('@/views/audit-logs/Index.vue'),
          meta: { title: '审计日志' }
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('@/views/users/Index.vue'),
          meta: { title: '用户管理' }
        }
      ]
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
