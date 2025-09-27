/**
 * Vue Router 路由配置
 * 定义应用程序的页面路由和导航规则
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: {
      title: '仪表板',
      icon: 'Monitor',
      requiresAuth: false
    }
  },
  {
    path: '/server-status',
    name: 'ServerStatus',
    component: () => import('../views/ServerStatus.vue'),
    meta: {
      title: '服务器状态',
      icon: 'Server',
      requiresAuth: false
    }
  },
  {
    path: '/ipmi-control',
    name: 'IPMIControl',
    component: () => import('../views/IPMIControl.vue'),
    meta: {
      title: 'IPMI控制',
      icon: 'Setting',
      requiresAuth: true
    }
  },
  {
    path: '/monitoring',
    name: 'Monitoring',
    component: () => import('../views/Monitoring.vue'),
    meta: {
      title: '监控面板',
      icon: 'DataAnalysis',
      requiresAuth: false
    }
  },
  {
    path: '/logs',
    name: 'SystemLogs',
    component: () => import('../views/SystemLogs.vue'),
    meta: {
      title: '系统日志',
      icon: 'Document',
      requiresAuth: false
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/Settings.vue'),
    meta: {
      title: '系统设置',
      icon: 'Tools',
      requiresAuth: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: '页面未找到'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 服务器热控制系统` : '服务器热控制系统'
  
  // 权限检查（暂时跳过，后续可以添加认证逻辑）
  if (to.meta.requiresAuth) {
    // TODO: 添加认证检查逻辑
    // const isAuthenticated = checkAuth()
    // if (!isAuthenticated) {
    //   next('/login')
    //   return
    // }
  }
  
  next()
})

export default router