// ***********************************************************
// This example support/e2e.js is processed and
// loaded automatically before your test files.
//
// This is a great place to put global configuration and
// behavior that modifies Cypress.
//
// You can change the location of this file or turn off
// automatically serving support files with the
// 'supportFile' configuration option.
//
// You can read more here:
// https://on.cypress.io/configuration
// ***********************************************************

// Import commands.js using ES2015 syntax:
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Mock API responses for testing
Cypress.Commands.add('mockApiResponses', () => {
  // Mock user login
  cy.intercept('POST', '/api/v1/auth/login', {
    statusCode: 200,
    body: {
      token: 'mock-jwt-token',
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com'
      }
    }
  }).as('login')

  // Mock user list
  cy.intercept('GET', '/api/v1/users', {
    statusCode: 200,
    body: [
      { id: 1, username: 'testuser', email: 'test@example.com', role: 'admin' },
      { id: 2, username: 'user2', email: 'user2@example.com', role: 'user' }
    ]
  }).as('getUsers')

  // Mock settings
  cy.intercept('GET', '/api/v1/settings', {
    statusCode: 200,
    body: {
      theme: 'light',
      language: 'zh-CN',
      notifications: true
    }
  }).as('getSettings')

  // Mock runtime managers
  cy.intercept('GET', '/api/v1/runtime-managers', {
    statusCode: 200,
    body: [
      {
        id: 1,
        name: 'Docker Runtime',
        type: 'docker',
        status: 'active',
        endpoint: 'unix:///var/run/docker.sock'
      },
      {
        id: 2,
        name: 'Kubernetes Runtime',
        type: 'kubernetes',
        status: 'active',
        endpoint: 'https://k8s-api.example.com'
      }
    ]
  }).as('getRuntimeManagers')

  // Mock test cases
  cy.intercept('GET', '/api/v1/test-cases', {
    statusCode: 200,
    body: [
      {
        id: 1,
        name: 'API Test Case 1',
        description: 'Test user authentication',
        status: 'passed',
        runtime_id: 1
      },
      {
        id: 2,
        name: 'API Test Case 2',
        description: 'Test data validation',
        status: 'failed',
        runtime_id: 2
      }
    ]
  }).as('getTestCases')
})