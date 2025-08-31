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

// Global configuration for QuantaEnergi E2E tests
Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from failing the test
  // for uncaught exceptions in the application
  if (err.message.includes('ResizeObserver loop limit exceeded')) {
    return false
  }
  if (err.message.includes('Non-Error promise rejection')) {
    return false
  }
  return true
})

// Custom error handling for WebSocket connections
Cypress.on('fail', (error, runnable) => {
  // Log custom error information for debugging
  console.log('Cypress test failed:', {
    test: runnable.title,
    error: error.message,
    stack: error.stack
  })
  throw error
})

// Global test data setup
beforeEach(() => {
  // Clear any stored data before each test
  cy.clearLocalStorage()
  cy.clearCookies()
  
  // Set up test environment
  cy.log('Setting up test environment for QuantaEnergi')
})

// Global test cleanup
afterEach(() => {
  // Clean up after each test
  cy.log('Cleaning up test environment')
})
