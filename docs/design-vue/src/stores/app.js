/**
 * 应用状态管理Store
 * 管理全局应用状态和配置
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @date 2025-01-23
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 应用状态管理
 */
export const useAppStore = defineStore('app', () => {
  // 状态定义
  const sidebarCollapsed = ref(false)
  const currentUser = ref({
    name: '管理员',
    avatar: '/src/assets/images/user-avatar.svg',
    role: 'admin'
  })
  const theme = ref('light')
  const loading = ref(false)
  
  // 计算属性
  const isAdmin = computed(() => currentUser.value.role === 'admin')
  
  // 操作方法
  
  /**
   * 初始化应用
   */
  const initializeApp = () => {
    // 从localStorage恢复设置
    const savedTheme = localStorage.getItem('aiops-theme')
    if (savedTheme) {
      theme.value = savedTheme
    }
    
    const savedSidebarState = localStorage.getItem('aiops-sidebar-collapsed')
    if (savedSidebarState) {
      sidebarCollapsed.value = JSON.parse(savedSidebarState)
    }
  }
  
  /**
   * 切换侧边栏折叠状态
   */
  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem('aiops-sidebar-collapsed', JSON.stringify(sidebarCollapsed.value))
  }
  
  /**
   * 设置主题
   * @param {string} newTheme - 主题名称
   */
  const setTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('aiops-theme', newTheme)
    document.documentElement.setAttribute('data-theme', newTheme)
  }
  
  /**
   * 设置加载状态
   * @param {boolean} state - 加载状态
   */
  const setLoading = (state) => {
    loading.value = state
  }
  
  /**
   * 更新用户信息
   * @param {Object} userInfo - 用户信息
   */
  const updateUser = (userInfo) => {
    currentUser.value = { ...currentUser.value, ...userInfo }
  }
  
  return {
    // 状态
    sidebarCollapsed,
    currentUser,
    theme,
    loading,
    
    // 计算属性
    isAdmin,
    
    // 方法
    initializeApp,
    toggleSidebar,
    setTheme,
    setLoading,
    updateUser
  }
})