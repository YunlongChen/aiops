// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Custom command for login
Cypress.Commands.add('login', (username = 'testuser', password = 'password') => {
  cy.visit('/login')
  cy.get('[data-cy="username-input"]').type(username)
  cy.get('[data-cy="password-input"]').type(password)
  cy.get('[data-cy="login-button"]').click()
  cy.wait('@login')
  cy.url().should('not.include', '/login')
})

// Custom command for logout
Cypress.Commands.add('logout', () => {
  cy.get('[data-cy="user-menu"]').click()
  cy.get('[data-cy="logout-button"]').click()
  cy.url().should('include', '/login')
})

// Custom command to navigate to a specific page
Cypress.Commands.add('navigateTo', (page) => {
  const routes = {
    dashboard: '/',
    users: '/users',
    settings: '/settings',
    'runtime-managers': '/runtime-managers',
    'test-cases': '/test-cases'
  }
  
  if (routes[page]) {
    cy.visit(routes[page])
  } else {
    throw new Error(`Unknown page: ${page}`)
  }
})

// Custom command to check if element is visible and contains text
Cypress.Commands.add('shouldBeVisibleAndContain', { prevSubject: 'element' }, (subject, text) => {
  cy.wrap(subject).should('be.visible').and('contain', text)
})

// Custom command to wait for page to load
Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('[data-cy="loading"]', { timeout: 10000 }).should('not.exist')
})

// Custom command to check API response
Cypress.Commands.add('checkApiResponse', (alias, expectedStatus = 200) => {
  cy.wait(alias).then((interception) => {
    expect(interception.response.statusCode).to.equal(expectedStatus)
  })
})