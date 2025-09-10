/**
 * E2E测试 - 用户管理功能测试
 * 测试用户登录、用户列表、用户创建等功能
 */

describe('用户管理功能测试', () => {
  beforeEach(() => {
    // 设置API模拟响应
    cy.mockApiResponses()
  })

  describe('用户认证', () => {
    it('应该能够成功登录', () => {
      cy.visit('/login')
      cy.get('[data-cy="username-input"]').type('testuser')
      cy.get('[data-cy="password-input"]').type('password')
      cy.get('[data-cy="login-button"]').click()
      
      cy.wait('@login')
      cy.url().should('not.include', '/login')
      cy.get('[data-cy="user-info"]').should('contain', 'testuser')
    })

    it('应该显示登录错误信息', () => {
      // 模拟登录失败
      cy.intercept('POST', '/api/auth/login', {
        statusCode: 401,
        body: { error: '用户名或密码错误' }
      }).as('loginFailed')

      cy.visit('/login')
      cy.get('[data-cy="username-input"]').type('wronguser')
      cy.get('[data-cy="password-input"]').type('wrongpassword')
      cy.get('[data-cy="login-button"]').click()
      
      cy.wait('@loginFailed')
      cy.get('[data-cy="error-message"]').should('contain', '用户名或密码错误')
    })

    it('应该能够成功登出', () => {
      cy.login()
      cy.logout()
      cy.url().should('include', '/login')
    })
  })

  describe('用户列表管理', () => {
    beforeEach(() => {
      cy.login()
      cy.navigateTo('users')
    })

    it('应该显示用户列表', () => {
      cy.wait('@getUsers')
      cy.get('[data-cy="users-table"]').should('be.visible')
      cy.get('[data-cy="user-row"]').should('have.length.at.least', 1)
      cy.get('[data-cy="user-row"]').first().should('contain', 'testuser')
    })

    it('应该能够搜索用户', () => {
      cy.wait('@getUsers')
      cy.get('[data-cy="search-input"]').type('testuser')
      cy.get('[data-cy="user-row"]').should('have.length', 1)
      cy.get('[data-cy="user-row"]').should('contain', 'testuser')
    })

    it('应该能够创建新用户', () => {
      // 模拟创建用户API
      cy.intercept('POST', '/api/users', {
        statusCode: 201,
        body: {
          id: 3,
          username: 'newuser',
          email: 'newuser@example.com',
          role: 'user'
        }
      }).as('createUser')

      cy.get('[data-cy="add-user-button"]').click()
      cy.get('[data-cy="user-form"]').should('be.visible')
      
      cy.get('[data-cy="username-input"]').type('newuser')
      cy.get('[data-cy="email-input"]').type('newuser@example.com')
      cy.get('[data-cy="password-input"]').type('password123')
      cy.get('[data-cy="role-select"]').select('user')
      
      cy.get('[data-cy="submit-button"]').click()
      cy.wait('@createUser')
      
      cy.get('[data-cy="success-message"]').should('contain', '用户创建成功')
    })

    it('应该能够编辑用户信息', () => {
      // 模拟更新用户API
      cy.intercept('PUT', '/api/users/1', {
        statusCode: 200,
        body: {
          id: 1,
          username: 'testuser',
          email: 'updated@example.com',
          role: 'admin'
        }
      }).as('updateUser')

      cy.wait('@getUsers')
      cy.get('[data-cy="user-row"]').first().find('[data-cy="edit-button"]').click()
      
      cy.get('[data-cy="email-input"]').clear().type('updated@example.com')
      cy.get('[data-cy="submit-button"]').click()
      
      cy.wait('@updateUser')
      cy.get('[data-cy="success-message"]').should('contain', '用户更新成功')
    })

    it('应该能够删除用户', () => {
      // 模拟删除用户API
      cy.intercept('DELETE', '/api/users/2', {
        statusCode: 200,
        body: { message: '用户删除成功' }
      }).as('deleteUser')

      cy.wait('@getUsers')
      cy.get('[data-cy="user-row"]').eq(1).find('[data-cy="delete-button"]').click()
      
      // 确认删除对话框
      cy.get('[data-cy="confirm-dialog"]').should('be.visible')
      cy.get('[data-cy="confirm-delete-button"]').click()
      
      cy.wait('@deleteUser')
      cy.get('[data-cy="success-message"]').should('contain', '用户删除成功')
    })
  })
})