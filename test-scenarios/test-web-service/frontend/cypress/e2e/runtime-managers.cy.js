/**
 * E2E测试 - 运行时管理功能测试
 * 测试运行时管理器的创建、编辑、删除和连接测试功能
 */

describe('运行时管理功能测试', () => {
  beforeEach(() => {
    // 设置API模拟响应
    cy.mockApiResponses()
    cy.login()
    cy.navigateTo('runtime-managers')
  })

  describe('运行时管理器列表', () => {
    it('应该显示运行时管理器列表', () => {
      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="runtime-managers-table"]').should('be.visible')
      cy.get('[data-cy="runtime-row"]').should('have.length.at.least', 1)
      cy.get('[data-cy="runtime-row"]').first().should('contain', 'Docker Runtime')
    })

    it('应该显示运行时管理器状态', () => {
      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="runtime-row"]').first().within(() => {
        cy.get('[data-cy="status-badge"]').should('contain', 'active')
        cy.get('[data-cy="status-badge"]').should('have.class', 'status-active')
      })
    })

    it('应该能够按类型筛选运行时管理器', () => {
      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="type-filter"]').select('docker')
      cy.get('[data-cy="runtime-row"]').should('have.length', 1)
      cy.get('[data-cy="runtime-row"]').should('contain', 'Docker Runtime')
    })
  })

  describe('运行时管理器操作', () => {
    it('应该能够创建新的Docker运行时管理器', () => {
      // 模拟创建运行时管理器API
      cy.intercept('POST', '/api/runtime-managers', {
        statusCode: 201,
        body: {
          id: 3,
          name: 'New Docker Runtime',
          type: 'docker',
          status: 'active',
          endpoint: 'tcp://localhost:2376',
          config: {
            tls: true,
            cert_path: '/path/to/certs'
          }
        }
      }).as('createRuntimeManager')

      cy.get('[data-cy="add-runtime-button"]').click()
      cy.get('[data-cy="runtime-form"]').should('be.visible')
      
      cy.get('[data-cy="name-input"]').type('New Docker Runtime')
      cy.get('[data-cy="type-select"]').select('docker')
      cy.get('[data-cy="endpoint-input"]').type('tcp://localhost:2376')
      
      // 配置Docker特定选项
      cy.get('[data-cy="tls-checkbox"]').check()
      cy.get('[data-cy="cert-path-input"]').type('/path/to/certs')
      
      cy.get('[data-cy="submit-button"]').click()
      cy.wait('@createRuntimeManager')
      
      cy.get('[data-cy="success-message"]').should('contain', '运行时管理器创建成功')
    })

    it('应该能够创建新的Kubernetes运行时管理器', () => {
      // 模拟创建Kubernetes运行时管理器API
      cy.intercept('POST', '/api/runtime-managers', {
        statusCode: 201,
        body: {
          id: 4,
          name: 'New K8s Runtime',
          type: 'kubernetes',
          status: 'active',
          endpoint: 'https://k8s-new.example.com',
          config: {
            namespace: 'default',
            kubeconfig: '/path/to/kubeconfig'
          }
        }
      }).as('createK8sRuntimeManager')

      cy.get('[data-cy="add-runtime-button"]').click()
      cy.get('[data-cy="runtime-form"]').should('be.visible')
      
      cy.get('[data-cy="name-input"]').type('New K8s Runtime')
      cy.get('[data-cy="type-select"]').select('kubernetes')
      cy.get('[data-cy="endpoint-input"]').type('https://k8s-new.example.com')
      
      // 配置Kubernetes特定选项
      cy.get('[data-cy="namespace-input"]').type('default')
      cy.get('[data-cy="kubeconfig-input"]').type('/path/to/kubeconfig')
      
      cy.get('[data-cy="submit-button"]').click()
      cy.wait('@createK8sRuntimeManager')
      
      cy.get('[data-cy="success-message"]').should('contain', '运行时管理器创建成功')
    })

    it('应该能够测试运行时管理器连接', () => {
      // 模拟连接测试API
      cy.intercept('POST', '/api/runtime-managers/1/test', {
        statusCode: 200,
        body: {
          success: true,
          message: '连接测试成功',
          details: {
            version: 'Docker version 20.10.8',
            containers: 5,
            images: 12
          }
        }
      }).as('testConnection')

      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="runtime-row"]').first().within(() => {
        cy.get('[data-cy="test-connection-button"]').click()
      })
      
      cy.wait('@testConnection')
      cy.get('[data-cy="test-result-dialog"]').should('be.visible')
      cy.get('[data-cy="test-result-dialog"]').should('contain', '连接测试成功')
      cy.get('[data-cy="test-result-dialog"]').should('contain', 'Docker version 20.10.8')
    })

    it('应该能够编辑运行时管理器', () => {
      // 模拟更新运行时管理器API
      cy.intercept('PUT', '/api/runtime-managers/1', {
        statusCode: 200,
        body: {
          id: 1,
          name: 'Updated Docker Runtime',
          type: 'docker',
          status: 'active',
          endpoint: 'unix:///var/run/docker.sock'
        }
      }).as('updateRuntimeManager')

      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="runtime-row"]').first().within(() => {
        cy.get('[data-cy="edit-button"]').click()
      })
      
      cy.get('[data-cy="name-input"]').clear().type('Updated Docker Runtime')
      cy.get('[data-cy="submit-button"]').click()
      
      cy.wait('@updateRuntimeManager')
      cy.get('[data-cy="success-message"]').should('contain', '运行时管理器更新成功')
    })

    it('应该能够删除运行时管理器', () => {
      // 模拟删除运行时管理器API
      cy.intercept('DELETE', '/api/runtime-managers/2', {
        statusCode: 200,
        body: { message: '运行时管理器删除成功' }
      }).as('deleteRuntimeManager')

      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="runtime-row"]').eq(1).within(() => {
        cy.get('[data-cy="delete-button"]').click()
      })
      
      // 确认删除对话框
      cy.get('[data-cy="confirm-dialog"]').should('be.visible')
      cy.get('[data-cy="confirm-delete-button"]').click()
      
      cy.wait('@deleteRuntimeManager')
      cy.get('[data-cy="success-message"]').should('contain', '运行时管理器删除成功')
    })
  })

  describe('运行时管理器详情', () => {
    it('应该显示运行时管理器详细信息', () => {
      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="runtime-row"]').first().within(() => {
        cy.get('[data-cy="view-details-button"]').click()
      })
      
      cy.get('[data-cy="runtime-details-dialog"]').should('be.visible')
      cy.get('[data-cy="runtime-details-dialog"]').should('contain', 'Docker Runtime')
      cy.get('[data-cy="runtime-details-dialog"]').should('contain', 'unix:///var/run/docker.sock')
    })

    it('应该显示运行时管理器使用统计', () => {
      // 模拟统计数据API
      cy.intercept('GET', '/api/runtime-managers/1/stats', {
        statusCode: 200,
        body: {
          total_tests: 25,
          successful_tests: 20,
          failed_tests: 5,
          avg_execution_time: 45.2
        }
      }).as('getRuntimeStats')

      cy.wait('@getRuntimeManagers')
      cy.get('[data-cy="runtime-row"]').first().within(() => {
        cy.get('[data-cy="view-stats-button"]').click()
      })
      
      cy.wait('@getRuntimeStats')
      cy.get('[data-cy="stats-dialog"]').should('be.visible')
      cy.get('[data-cy="stats-dialog"]').should('contain', '总测试数: 25')
      cy.get('[data-cy="stats-dialog"]').should('contain', '成功: 20')
      cy.get('[data-cy="stats-dialog"]').should('contain', '失败: 5')
    })
  })
})