/**
 * AIOps测试管理平台 - 路由配置
 * 定义应用的所有路由和页面组件映射
 */

import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import TestCases from '../views/TestCases.vue'
import TestScripts from '../views/TestScripts.vue'
import TestRuns from '../views/TestRuns.vue'
import RuntimeManagers from '../views/RuntimeManagers.vue'
import Settings from '../views/Settings.vue'

/**
 * 路由配置数组
 * 定义每个路由的路径、名称和对应的组件
 */
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '仪表板',
      description: '系统概览和统计信息'
    }
  },
  {
    path: '/test-cases',
    name: 'TestCases',
    component: TestCases,
    meta: {
      title: '测试用例',
      description: '管理和查看测试用例'
    }
  },
  {
    path: '/test-scripts',
    name: 'TestScripts',
    component: TestScripts,
    meta: {
      title: '测试脚本',
      description: '管理多语言测试脚本'
    }
  },
  {
    path: '/test-runs',
    name: 'TestRuns',
    component: TestRuns,
    meta: {
      title: '测试运行',
      description: '查看测试运行历史和结果'
    }
  },
  {
    path: '/runtime-managers',
    name: 'RuntimeManagers',
    component: RuntimeManagers,
    meta: {
      title: '运行时管理',
      description: '管理Docker、Kubernetes等运行时环境'
    }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: {
      title: '系统设置',
      description: '系统配置和参数设置'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: '页面未找到',
      description: '请求的页面不存在'
    }
  }
]

/**
 * 创建路由实例
 * 使用HTML5 History模式
 */
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 路由切换时的滚动行为
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

/**
 * 全局前置守卫
 * 在每次路由跳转前执行，用于设置页面标题等
 */
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AIOps 测试管理平台`
  } else {
    document.title = 'AIOps 测试管理平台'
  }
  
  next()
})

export default router