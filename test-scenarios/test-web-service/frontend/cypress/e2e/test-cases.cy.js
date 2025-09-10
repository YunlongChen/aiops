/**
 * E2E测试 - 测试用例管理功能测试
 * 测试测试用例的创建、编辑、执行和结果查看功能
 */

describe('测试用例管理功能测试', () => {
  beforeEach(() => {
    // 设置API模拟响应
    cy.mockApiResponses()
    cy.login()
    cy.navigateTo('test-cases')
  })

  describe('测试用例列表', () => {
    it('应该显示测试用例列表', () => {
      cy.wait('@getTestCases')
      cy.get('[data-cy="test-cases-table"]').should('be.visible')
      cy.get('[data-cy="test-case-row"]').should('have.length.at.least', 1)
      cy.get('[data-cy="test-case-row"]').first().should('contain', 'API Test Case 1')
    })

    it('应该显示测试用例状态', () => {
      cy.wait('@getTestCases')
      cy.get('[data-cy="test-case-row"]').first().within(() => {
        cy.get('[data-cy="status-badge"]').should('contain', 'passed')
        cy.get('[data-cy="status-badge"]').should('have.class', 'status-passed')
      })
      
      cy.get('[data-cy="test-case-row"]').eq(1).within(() => {
        cy.get('[data-cy="status-badge"]').should('contain', 'failed')
        cy.get('[data-cy="status-badge"]').should('have.class', 'status-failed')
      })
    })

    it('应该能够按状态筛选测试用例', () => {
      cy.wait('@getTestCases')
      cy.get('[data-cy="status-filter"]').select('passed')
      cy.get('[data-cy="test-case-row"]').should('have.length', 1)
      cy.get('[data-cy="test-case-row"]').should('contain', 'API Test Case 1')
    })

    it('应该能够按运行时筛选测试用例', () => {
      cy.wait('@getTestCases')
      cy.get('[data-cy="runtime-filter"]').select('1') // Docker Runtime
      cy.get('[data-cy="test-case-row"]').should('have.length', 1)
      cy.get('[data-cy="test-case-row"]').should('contain', 'API Test Case 1')
    })
  })

  describe('测试用例创建', () => {
    it('应该能够创建新的API测试用例', () => {
      // 模拟创建测试用例API
      cy.intercept('POST', '/api/test-cases', {
        statusCode: 201,
        body: {
          id: 3,
          name: 'New API Test',
          description: 'Test new API endpoint',
          type: 'api',
          runtime_id: 1,
          config: {
            method: 'GET',
            url: '/api/health',
            expected_status: 200
          }
        }
      }).as('createTestCase')

      cy.get('[data-cy="add-test-case-button"]').click()
      cy.get('[data-cy="test-case-form"]').should('be.visible')
      
      cy.get('[data-cy="name-input"]').type('New API Test')
      cy.get('[data-cy="description-input"]').type('Test new API endpoint')
      cy.get('[data-cy="type-select"]').select('api')
      cy.get('[data-cy="runtime-select"]').select('1')
      
      // 配置API测试特定选项
      cy.get('[data-cy="method-select"]').select('GET')
      cy.get('[data-cy="url-input"]').type('/api/health')
      cy.get('[data-cy="expected-status-input"]').type('200')
      
      cy.get('[data-cy="submit-button"]').click()
      cy.wait('@createTestCase')
      
      cy.get('[data-cy="success-message"]').should('contain', '测试用例创建成功')
    })

    it('应该能够创建脚本测试用例', () => {
      // 模拟创建脚本测试用例API
      cy.intercept('POST', '/api/test-cases', {
        statusCode: 201,
        body: {
          id: 4,
          name: 'Script Test',
          description: 'Custom script test',
          type: 'script',
          runtime_id: 2,
          config: {
            language: 'python',
            script: 'print("Hello World")',
            expected_output: 'Hello World'
          }
        }
      }).as('createScriptTestCase')

      cy.get('[data-cy="add-test-case-button"]').click()
      cy.get('[data-cy="test-case-form"]').should('be.visible')
      
      cy.get('[data-cy="name-input"]').type('Script Test')
      cy.get('[data-cy="description-input"]').type('Custom script test')
      cy.get('[data-cy="type-select"]').select('script')
      cy.get('[data-cy="runtime-select"]').select('2')
      
      // 配置脚本测试特定选项
      cy.get('[data-cy="language-select"]').select('python')
      cy.get('[data-cy="script-editor"]').type('print("Hello World")')
      cy.get('[data-cy="expected-output-input"]').type('Hello World')
      
      cy.get('[data-cy="submit-button"]').click()
      cy.wait('@createScriptTestCase')
      
      cy.get('[data-cy="success-message"]').should('contain', '测试用例创建成功')
    })
  })

  describe('测试用例执行', () => {
    it('应该能够执行单个测试用例', () => {
      // 模拟执行测试用例API
      cy.intercept('POST', '/api/test-cases/1/execute', {
        statusCode: 200,
        body: {
          execution_id: 'exec-123',
          status: 'running'
        }
      }).as('executeTestCase')

      // 模拟获取执行结果API
      cy.intercept('GET', '/api/test-executions/exec-123', {
        statusCode: 200,
        body: {
          id: 'exec-123',
          status: 'completed',
          result: 'passed',
          output: 'Test completed successfully',
          execution_time: 1.5,
          started_at: '2025-01-11T10:00:00Z',
          completed_at: '2025-01-11T10:00:01Z'
        }
      }).as('getExecutionResult')

      cy.wait('@getTestCases')
      cy.get('[data-cy="test-case-row"]').first().within(() => {
        cy.get('[data-cy="execute-button"]').click()
      })
      
      cy.wait('@executeTestCase')
      cy.get('[data-cy="execution-dialog"]').should('be.visible')
      cy.get('[data-cy="execution-dialog"]').should('contain', '测试执行中...')
      
      // 等待执行完成
      cy.wait('@getExecutionResult')
      cy.get('[data-cy="execution-dialog"]').should('contain', '测试完成')
      cy.get('[data-cy="execution-dialog"]').should('contain', 'passed')
      cy.get('[data-cy="execution-dialog"]').should('contain', '执行时间: 1.5s')
    })

    it('应该能够批量执行测试用例', () => {
      // 模拟批量执行API
      cy.intercept('POST', '/api/test-cases/batch-execute', {
        statusCode: 200,
        body: {
          batch_id: 'batch-456',
          total_tests: 2,
          status: 'running'
        }
      }).as('batchExecute')

      cy.wait('@getTestCases')
      
      // 选择多个测试用例
      cy.get('[data-cy="test-case-row"]').first().within(() => {
        cy.get('[data-cy="select-checkbox"]').check()
      })
      cy.get('[data-cy="test-case-row"]').eq(1).within(() => {
        cy.get('[data-cy="select-checkbox"]').check()
      })
      
      cy.get('[data-cy="batch-execute-button"]').click()
      cy.wait('@batchExecute')
      
      cy.get('[data-cy="batch-execution-dialog"]').should('be.visible')
      cy.get('[data-cy="batch-execution-dialog"]').should('contain', '批量执行中...')
      cy.get('[data-cy="batch-execution-dialog"]').should('contain', '总计: 2 个测试')
    })
  })

  describe('测试用例管理', () => {
    it('应该能够编辑测试用例', () => {
      // 模拟更新测试用例API
      cy.intercept('PUT', '/api/test-cases/1', {
        statusCode: 200,
        body: {
          id: 1,
          name: 'Updated API Test Case',
          description: 'Updated description',
          status: 'passed',
          runtime_id: 1
        }
      }).as('updateTestCase')

      cy.wait('@getTestCases')
      cy.get('[data-cy="test-case-row"]').first().within(() => {
        cy.get('[data-cy="edit-button"]').click()
      })
      
      cy.get('[data-cy="name-input"]').clear().type('Updated API Test Case')
      cy.get('[data-cy="description-input"]').clear().type('Updated description')
      cy.get('[data-cy="submit-button"]').click()
      
      cy.wait('@updateTestCase')
      cy.get('[data-cy="success-message"]').should('contain', '测试用例更新成功')
    })

    it('应该能够复制测试用例', () => {
      // 模拟复制测试用例API
      cy.intercept('POST', '/api/test-cases/1/clone', {
        statusCode: 201,
        body: {
          id: 5,
          name: 'API Test Case 1 (Copy)',
          description: 'Test user authentication',
          status: 'pending',
          runtime_id: 1
        }
      }).as('cloneTestCase')

      cy.wait('@getTestCases')
      cy.get('[data-cy="test-case-row"]').first().within(() => {
        cy.get('[data-cy="clone-button"]').click()
      })
      
      cy.wait('@cloneTestCase')
      cy.get('[data-cy="success-message"]').should('contain', '测试用例复制成功')
    })

    it('应该能够删除测试用例', () => {
      // 模拟删除测试用例API
      cy.intercept('DELETE', '/api/test-cases/2', {
        statusCode: 200,
        body: { message: '测试用例删除成功' }
      }).as('deleteTestCase')

      cy.wait('@getTestCases')
      cy.get('[data-cy="test-case-row"]').eq(1).within(() => {
        cy.get('[data-cy="delete-button"]').click()
      })
      
      // 确认删除对话框
      cy.get('[data-cy="confirm-dialog"]').should('be.visible')
      cy.get('[data-cy="confirm-delete-button"]').click()
      
      cy.wait('@deleteTestCase')
      cy.get('[data-cy="success-message"]').should('contain', '测试用例删除成功')
    })
  })

  describe('测试历史和报告', () => {
    it('应该能够查看测试执行历史', () => {
      // 模拟获取执行历史API
      cy.intercept('GET', '/api/test-cases/1/executions', {
        statusCode: 200,
        body: [
          {
            id: 'exec-123',
            status: 'completed',
            result: 'passed',
            execution_time: 1.5,
            started_at: '2025-01-11T10:00:00Z'
          },
          {
            id: 'exec-124',
            status: 'completed',
            result: 'failed',
            execution_time: 2.1,
            started_at: '2025-01-11T09:00:00Z'
          }
        ]
      }).as('getExecutionHistory')

      cy.wait('@getTestCases')
      cy.get('[data-cy="test-case-row"]').first().within(() => {
        cy.get('[data-cy="view-history-button"]').click()
      })
      
      cy.wait('@getExecutionHistory')
      cy.get('[data-cy="history-dialog"]').should('be.visible')
      cy.get('[data-cy="execution-history-row"]').should('have.length', 2)
      cy.get('[data-cy="execution-history-row"]').first().should('contain', 'passed')
      cy.get('[data-cy="execution-history-row"]').eq(1).should('contain', 'failed')
    })

    it('应该能够查看详细的执行报告', () => {
      // 模拟获取详细报告API
      cy.intercept('GET', '/api/test-executions/exec-123/report', {
        statusCode: 200,
        body: {
          id: 'exec-123',
          test_case_name: 'API Test Case 1',
          result: 'passed',
          execution_time: 1.5,
          output: 'HTTP/1.1 200 OK\nContent-Type: application/json\n{"status": "ok"}',
          logs: [
            { timestamp: '2025-01-11T10:00:00Z', level: 'INFO', message: 'Starting test execution' },
            { timestamp: '2025-01-11T10:00:01Z', level: 'INFO', message: 'Test completed successfully' }
          ]
        }
      }).as('getExecutionReport')

      cy.wait('@getTestCases')
      cy.get('[data-cy="test-case-row"]').first().within(() => {
        cy.get('[data-cy="view-report-button"]').click()
      })
      
      cy.wait('@getExecutionReport')
      cy.get('[data-cy="report-dialog"]').should('be.visible')
      cy.get('[data-cy="report-dialog"]').should('contain', 'API Test Case 1')
      cy.get('[data-cy="report-dialog"]').should('contain', 'passed')
      cy.get('[data-cy="report-dialog"]').should('contain', '执行时间: 1.5s')
      cy.get('[data-cy="execution-output"]').should('contain', 'HTTP/1.1 200 OK')
      cy.get('[data-cy="execution-logs"]').should('contain', 'Starting test execution')
    })
  })
})