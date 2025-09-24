/**
 * 懒加载工具函数
 * 提供组件懒加载和错误处理功能
 * 
 * @author AI Assistant
 * @version 1.0.0
 * @date 2025-01-24
 */

/**
 * 创建懒加载组件
 * @param {Function} importFunc - 动态导入函数
 * @param {Object} options - 配置选项
 * @returns {Object} 懒加载组件配置
 */
export function createLazyComponent(importFunc, options = {}) {
  const {
    loading = null,
    error = null,
    delay = 200,
    timeout = 10000
  } = options

  return {
    component: importFunc,
    loading,
    error,
    delay,
    timeout
  }
}

/**
 * 批量创建懒加载路由
 * @param {Object} routes - 路由配置对象
 * @returns {Array} 懒加载路由数组
 */
export function createLazyRoutes(routes) {
  return Object.entries(routes).map(([path, component]) => ({
    path,
    component: () => import(component),
    meta: {
      lazy: true
    }
  }))
}

/**
 * 预加载组件
 * @param {Array} components - 组件路径数组
 * @returns {Promise} 预加载Promise
 */
export async function preloadComponents(components) {
  const promises = components.map(component => {
    if (typeof component === 'string') {
      return import(component)
    }
    return component()
  })
  
  try {
    await Promise.all(promises)
    console.log('Components preloaded successfully')
  } catch (error) {
    console.warn('Some components failed to preload:', error)
  }
}

/**
 * 路由级别的代码分割
 * @param {String} chunkName - chunk名称
 * @param {Function} importFunc - 导入函数
 * @returns {Function} 懒加载函数
 */
export function lazyLoadRoute(chunkName, importFunc) {
  return () => import(
    /* webpackChunkName: "[request]" */
    /* webpackMode: "lazy" */
    importFunc
  )
}