/**
 * E2E测试 - 应用基本功能测试
 * 测试应用的核心功能，包括导航、用户认证等
 */

describe('应用基本功能测试', () => {
  beforeEach(() => {
    // 设置API模拟响应
    cy.mockApiResponses()
  })

  it('应该正确加载首页', () => {
    cy.visit('/')
    cy.get('h1').should('contain', 'AIOps测试平台')
    cy.get('[data-cy="navigation"]').should('be.visible')
  })

  it('应该能够导航到不同页面', () => {
    cy.visit('/')
    
    // 测试导航到用户管理页面
    cy.get('[data-cy="nav-users"]').click()
    cy.url().should('include', '/users')
    cy.get('h2').should('contain', '用户管理')
    
    // 测试导航到设置页面
    cy.get('[data-cy="nav-settings"]').click()
    cy.url().should('include', '/settings')
    cy.get('h2').should('contain', '系统设置')
    
    // 测试导航到运行时管理页面
    cy.get('[data-cy="nav-runtime-managers"]').click()
    cy.url().should('include', '/runtime-managers')
    cy.get('h2').should('contain', '运行时管理')
    
    // 测试导航到测试用例页面
    cy.get('[data-cy="nav-test-cases"]').click()
    cy.url().should('include', '/test-cases')
    cy.get('h2').should('contain', '测试用例')
  })

  it('应该正确处理响应式布局', () => {
    // 测试桌面视图
    cy.viewport(1280, 720)
    cy.visit('/')
    cy.get('[data-cy="sidebar"]').should('be.visible')
    
    // 测试移动视图
    cy.viewport(375, 667)
    cy.get('[data-cy="mobile-menu-button"]').should('be.visible')
  })

  it('应该显示加载状态', () => {
    cy.visit('/')
    // 检查是否有加载指示器（如果有的话）
    cy.get('body').should('not.contain', 'Loading...')
  })
})