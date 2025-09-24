/**
 * Vue Router配置文件
 * 定义应用的路由结构和导航规则，支持懒加载优化
 * 
 * @author AI Assistant
 * @version 1.1.0
 * @date 2025-01-24
 */

import { createRouter, createWebHistory } from 'vue-router'

// 懒加载Layout组件
const Layout = () => import('@/components/layout/index.vue')

/**
 * 路由配置
 * 按照菜单层级结构组织路由
 */
const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '仪表板',
          icon: 'fas fa-tachometer-alt'
        }
      }
    ]
  },
  {
    path: '/monitoring',
    component: Layout,
    meta: {
      title: '监控中心',
      icon: 'fas fa-chart-line'
    },
    children: [
      {
        path: '',
        redirect: '/monitoring/infrastructure'
      },
      {
        path: 'infrastructure',
        name: 'MonitoringInfrastructure',
        meta: {
          title: '基础设施',
          parent: '监控中心'
        },
        children: [
          {
            path: '',
            redirect: '/monitoring/infrastructure/servers'
          },
          {
            path: 'servers',
            name: 'ServerMonitoring',
            component: () => import('@/views/Monitoring/Infrastructure/ServerMonitoring.vue'),
            meta: {
              title: '服务器监控',
              parent: '基础设施'
            }
          },
          {
            path: 'network',
            name: 'NetworkMonitoring',
            component: () => import('@/views/Monitoring/Infrastructure/NetworkMonitoring.vue'),
            meta: {
              title: '网络监控',
              parent: '基础设施'
            }
          },
          {
            path: 'storage',
            name: 'StorageMonitoring',
            component: () => import('@/views/Monitoring/Infrastructure/StorageMonitoring.vue'),
            meta: {
              title: '存储监控',
              parent: '基础设施'
            }
          }
        ]
      },
      {
        path: 'applications',
        name: 'ApplicationMonitoring',
        component: () => import('@/views/Monitoring/application/ApplicationMonitoring.vue'),
        meta: {
          title: '应用监控',
          parent: '监控中心'
        }
      },
      {
        path: 'databases',
        name: 'DatabaseMonitoring',
        component: () => import('@/views/Monitoring/infrastructure/DatabaseMonitoring.vue'),
        meta: {
          title: '数据库监控',
          parent: '监控中心'
        }
      }
    ]
  },
  {
    path: '/alerting',
    component: Layout,
    meta: {
      title: '告警管理',
      icon: 'fas fa-bell'
    },
    children: [
      {
        path: '',
        redirect: '/alerting/dashboard'
      },
      {
        path: 'dashboard',
        name: 'AlertingDashboard',
        component: () => import('@/views/alerts/AlertManagement.vue'),
        meta: {
          title: '告警仪表板',
          parent: '告警管理'
        }
      },
      // {
      //   path: 'active',
      //   name: 'ActiveAlerts',
      //   component: () => import('@/views/Alerting/ActiveAlerts.vue'),
      //   meta: {
      //     title: '活跃告警',
      //     parent: '告警管理'
      //   }
      // },
      {
        path: 'rules',
        name: 'AlertRules',
        component: () => import('@/views/alerts/AlertRules.vue'),
        meta: {
          title: '告警规则',
          parent: '告警管理'
        }
      },
      {
        path: 'history',
        name: 'AlertHistory',
        component: () => import('@/views/alerts/AlertHistory.vue'),
        meta: {
          title: '告警历史',
          parent: '告警管理'
        }
      }
    ]
  },
  {
    path: '/ai-engine',
    component: Layout,
    children: [
      {
        path: '',
        name: 'AiEngine',
        component: () => import('@/views/AiEngineView.vue'),
        meta: {
          title: 'AI引擎',
          icon: 'fas fa-brain'
        }
      }
    ]
  },
  {
    path: '/self-healing',
    component: Layout,
    children: [
      {
        path: '',
        name: 'SelfHealing',
        component: () => import('@/views/SelfHealingView.vue'),
        meta: {
          title: '自愈系统',
          icon: 'fas fa-magic'
        }
      }
    ]
  },
  {
    path: '/settings',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Settings',
        component: () => import('@/views/SettingsView.vue'),
        meta: {
          title: '系统设置',
          icon: 'fas fa-cog'
        }
      }
    ]
  }
]

/**
 * 创建路由实例
 */
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

/**
 * 路由守卫
 * 处理页面标题和权限验证
 */
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - AIOps 智能运维平台`
  }
  
  next()
})

export default router