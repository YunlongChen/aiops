/**
 * E2E测试 - 设置管理功能测试
 * 测试系统设置、用户偏好设置等功能
 */

describe('设置管理功能测试', () => {
  beforeEach(() => {
    // 设置API模拟响应
    cy.mockApiResponses()
    cy.login()
    cy.navigateTo('settings')
  })

  describe('系统设置', () => {
    it('应该显示系统设置页面', () => {
      cy.wait('@getSettings')
      cy.get('[data-cy="settings-container"]').should('be.visible')
      cy.get('[data-cy="system-settings-section"]').should('be.visible')
      cy.get('h2').should('contain', '系统设置')
    })

    it('应该能够切换主题', () => {
      // 模拟更新设置API
      cy.intercept('PUT', '/api/settings', {
        statusCode: 200,
        body: {
          theme: 'dark',
          language: 'zh-CN',
          notifications: true
        }
      }).as('updateSettings')

      cy.wait('@getSettings')
      cy.get('[data-cy="theme-select"]').select('dark')
      cy.get('[data-cy="save-settings-button"]').click()
      
      cy.wait('@updateSettings')
      cy.get('[data-cy="success-message"]').should('contain', '设置保存成功')
      
      // 验证主题是否应用
      cy.get('body').should('have.class', 'dark-theme')
    })

    it('应该能够切换语言', () => {
      // 模拟更新设置API
      cy.intercept('PUT', '/api/settings', {
        statusCode: 200,
        body: {
          theme: 'light',
          language: 'en-US',
          notifications: true
        }
      }).as('updateLanguage')

      cy.wait('@getSettings')
      cy.get('[data-cy="language-select"]').select('en-US')
      cy.get('[data-cy="save-settings-button"]').click()
      
      cy.wait('@updateLanguage')
      cy.get('[data-cy="success-message"]').should('contain', '设置保存成功')
    })

    it('应该能够配置通知设置', () => {
      // 模拟更新通知设置API
      cy.intercept('PUT', '/api/settings', {
        statusCode: 200,
        body: {
          theme: 'light',
          language: 'zh-CN',
          notifications: false,
          email_notifications: true,
          push_notifications: false
        }
      }).as('updateNotifications')

      cy.wait('@getSettings')
      cy.get('[data-cy="notifications-checkbox"]').uncheck()
      cy.get('[data-cy="email-notifications-checkbox"]').check()
      cy.get('[data-cy="push-notifications-checkbox"]').uncheck()
      cy.get('[data-cy="save-settings-button"]').click()
      
      cy.wait('@updateNotifications')
      cy.get('[data-cy="success-message"]').should('contain', '设置保存成功')
    })
  })

  describe('用户偏好设置', () => {
    it('应该显示用户偏好设置', () => {
      cy.get('[data-cy="user-preferences-tab"]').click()
      cy.get('[data-cy="user-preferences-section"]').should('be.visible')
    })

    it('应该能够配置默认运行时', () => {
      // 模拟更新用户偏好API
      cy.intercept('PUT', '/api/user-preferences', {
        statusCode: 200,
        body: {
          default_runtime_id: 2,
          auto_save: true,
          show_advanced_options: false
        }
      }).as('updateUserPreferences')

      cy.get('[data-cy="user-preferences-tab"]').click()
      cy.get('[data-cy="default-runtime-select"]').select('2')
      cy.get('[data-cy="save-preferences-button"]').click()
      
      cy.wait('@updateUserPreferences')
      cy.get('[data-cy="success-message"]').should('contain', '偏好设置保存成功')
    })

    it('应该能够配置自动保存选项', () => {
      // 模拟更新自动保存设置API
      cy.intercept('PUT', '/api/user-preferences', {
        statusCode: 200,
        body: {
          default_runtime_id: 1,
          auto_save: false,
          auto_save_interval: 30,
          show_advanced_options: true
        }
      }).as('updateAutoSave')

      cy.get('[data-cy="user-preferences-tab"]').click()
      cy.get('[data-cy="auto-save-checkbox"]').uncheck()
      cy.get('[data-cy="auto-save-interval-input"]').clear().type('30')
      cy.get('[data-cy="show-advanced-options-checkbox"]').check()
      cy.get('[data-cy="save-preferences-button"]').click()
      
      cy.wait('@updateAutoSave')
      cy.get('[data-cy="success-message"]').should('contain', '偏好设置保存成功')
    })
  })

  describe('系统配置', () => {
    beforeEach(() => {
      // 模拟系统配置API
      cy.intercept('GET', '/api/system-config', {
        statusCode: 200,
        body: {
          max_concurrent_tests: 10,
          test_timeout: 300,
          log_level: 'INFO',
          enable_metrics: true,
          metrics_retention_days: 30
        }
      }).as('getSystemConfig')
    })

    it('应该显示系统配置（管理员权限）', () => {
      cy.get('[data-cy="system-config-tab"]').click()
      cy.wait('@getSystemConfig')
      cy.get('[data-cy="system-config-section"]').should('be.visible')
      cy.get('[data-cy="max-concurrent-tests-input"]').should('have.value', '10')
      cy.get('[data-cy="test-timeout-input"]').should('have.value', '300')
    })

    it('应该能够更新系统配置', () => {
      // 模拟更新系统配置API
      cy.intercept('PUT', '/api/system-config', {
        statusCode: 200,
        body: {
          max_concurrent_tests: 15,
          test_timeout: 600,
          log_level: 'DEBUG',
          enable_metrics: true,
          metrics_retention_days: 60
        }
      }).as('updateSystemConfig')

      cy.get('[data-cy="system-config-tab"]').click()
      cy.wait('@getSystemConfig')
      
      cy.get('[data-cy="max-concurrent-tests-input"]').clear().type('15')
      cy.get('[data-cy="test-timeout-input"]').clear().type('600')
      cy.get('[data-cy="log-level-select"]').select('DEBUG')
      cy.get('[data-cy="metrics-retention-input"]').clear().type('60')
      
      cy.get('[data-cy="save-system-config-button"]').click()
      cy.wait('@updateSystemConfig')
      
      cy.get('[data-cy="success-message"]').should('contain', '系统配置更新成功')
    })

    it('应该能够重置系统配置', () => {
      // 模拟重置系统配置API
      cy.intercept('POST', '/api/system-config/reset', {
        statusCode: 200,
        body: {
          max_concurrent_tests: 5,
          test_timeout: 300,
          log_level: 'INFO',
          enable_metrics: false,
          metrics_retention_days: 7
        }
      }).as('resetSystemConfig')

      cy.get('[data-cy="system-config-tab"]').click()
      cy.wait('@getSystemConfig')
      
      cy.get('[data-cy="reset-config-button"]').click()
      
      // 确认重置对话框
      cy.get('[data-cy="confirm-dialog"]').should('be.visible')
      cy.get('[data-cy="confirm-reset-button"]').click()
      
      cy.wait('@resetSystemConfig')
      cy.get('[data-cy="success-message"]').should('contain', '系统配置已重置')
    })
  })

  describe('数据管理', () => {
    it('应该能够导出系统数据', () => {
      // 模拟导出数据API
      cy.intercept('POST', '/api/data/export', {
        statusCode: 200,
        body: {
          export_id: 'export-123',
          status: 'processing'
        }
      }).as('exportData')

      // 模拟获取导出状态API
      cy.intercept('GET', '/api/data/export/export-123', {
        statusCode: 200,
        body: {
          export_id: 'export-123',
          status: 'completed',
          download_url: '/api/data/download/export-123.zip'
        }
      }).as('getExportStatus')

      cy.get('[data-cy="data-management-tab"]').click()
      cy.get('[data-cy="export-data-button"]').click()
      
      cy.wait('@exportData')
      cy.get('[data-cy="export-dialog"]').should('be.visible')
      cy.get('[data-cy="export-dialog"]').should('contain', '数据导出中...')
      
      cy.wait('@getExportStatus')
      cy.get('[data-cy="export-dialog"]').should('contain', '导出完成')
      cy.get('[data-cy="download-button"]').should('be.visible')
    })

    it('应该能够导入系统数据', () => {
      // 模拟导入数据API
      cy.intercept('POST', '/api/data/import', {
        statusCode: 200,
        body: {
          import_id: 'import-456',
          status: 'processing'
        }
      }).as('importData')

      cy.get('[data-cy="data-management-tab"]').click()
      
      // 模拟文件上传
      cy.get('[data-cy="import-file-input"]').selectFile({
        contents: Cypress.Buffer.from('test data'),
        fileName: 'test-data.zip',
        mimeType: 'application/zip'
      })
      
      cy.get('[data-cy="import-data-button"]').click()
      cy.wait('@importData')
      
      cy.get('[data-cy="import-dialog"]').should('be.visible')
      cy.get('[data-cy="import-dialog"]').should('contain', '数据导入中...')
    })

    it('应该能够清理系统数据', () => {
      // 模拟清理数据API
      cy.intercept('POST', '/api/data/cleanup', {
        statusCode: 200,
        body: {
          deleted_executions: 150,
          deleted_logs: 500,
          freed_space: '2.5GB'
        }
      }).as('cleanupData')

      cy.get('[data-cy="data-management-tab"]').click()
      cy.get('[data-cy="cleanup-data-button"]').click()
      
      // 确认清理对话框
      cy.get('[data-cy="confirm-dialog"]').should('be.visible')
      cy.get('[data-cy="cleanup-options"]').within(() => {
        cy.get('[data-cy="cleanup-executions-checkbox"]').check()
        cy.get('[data-cy="cleanup-logs-checkbox"]').check()
      })
      cy.get('[data-cy="confirm-cleanup-button"]').click()
      
      cy.wait('@cleanupData')
      cy.get('[data-cy="cleanup-result-dialog"]').should('be.visible')
      cy.get('[data-cy="cleanup-result-dialog"]').should('contain', '删除了 150 个执行记录')
      cy.get('[data-cy="cleanup-result-dialog"]').should('contain', '释放了 2.5GB 空间')
    })
  })

  describe('设置验证', () => {
    it('应该验证输入值的有效性', () => {
      cy.get('[data-cy="system-config-tab"]').click()
      
      // 测试无效的并发测试数量
      cy.get('[data-cy="max-concurrent-tests-input"]').clear().type('-1')
      cy.get('[data-cy="save-system-config-button"]').click()
      cy.get('[data-cy="error-message"]').should('contain', '并发测试数量必须大于0')
      
      // 测试无效的超时时间
      cy.get('[data-cy="max-concurrent-tests-input"]').clear().type('5')
      cy.get('[data-cy="test-timeout-input"]').clear().type('0')
      cy.get('[data-cy="save-system-config-button"]').click()
      cy.get('[data-cy="error-message"]').should('contain', '超时时间必须大于0')
    })

    it('应该在设置更改前显示确认对话框', () => {
      cy.get('[data-cy="system-config-tab"]').click()
      
      // 更改关键设置
      cy.get('[data-cy="max-concurrent-tests-input"]').clear().type('1')
      cy.get('[data-cy="save-system-config-button"]').click()
      
      // 应该显示确认对话框
      cy.get('[data-cy="confirm-dialog"]').should('be.visible')
      cy.get('[data-cy="confirm-dialog"]').should('contain', '此更改可能影响系统性能')
    })
  })
})