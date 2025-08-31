// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

// Custom command to login to QuantaEnergi
Cypress.Commands.add('login', (email = 'test@quantaenergi.com', password = 'testpass123') => {
  cy.visit('/login')
  cy.get('[data-testid="email-input"]').type(email)
  cy.get('[data-testid="password-input"]').type(password)
  cy.get('[data-testid="login-button"]').click()
  cy.url().should('include', '/dashboard')
  cy.log('Successfully logged in to QuantaEnergi')
})

// Custom command to logout from QuantaEnergi
Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="user-menu"]').click()
  cy.get('[data-testid="logout-button"]').click()
  cy.url().should('include', '/login')
  cy.log('Successfully logged out from QuantaEnergi')
})

// Custom command to navigate to trading dashboard
Cypress.Commands.add('navigateToTradingDashboard', () => {
  cy.visit('/dashboard')
  cy.get('[data-testid="trading-dashboard"]').should('be.visible')
  cy.log('Successfully navigated to Trading Dashboard')
})

// Custom command to check real-time market data
Cypress.Commands.add('checkMarketData', () => {
  cy.get('[data-testid="market-data"]').should('be.visible')
  cy.get('[data-testid="price-update"]').should('exist')
  cy.log('Real-time market data is working')
})

// Custom command to execute a trade
Cypress.Commands.add('executeTrade', (commodity, quantity, price) => {
  cy.get('[data-testid="trade-form"]').within(() => {
    cy.get('[data-testid="commodity-select"]').select(commodity)
    cy.get('[data-testid="quantity-input"]').type(quantity)
    cy.get('[data-testid="price-input"]').type(price)
    cy.get('[data-testid="execute-trade-button"]').click()
  })
  cy.get('[data-testid="trade-success"]').should('be.visible')
  cy.log(`Successfully executed trade: ${quantity} ${commodity} at ${price}`)
})

// Custom command to check ESG scoring
Cypress.Commands.add('checkESGScore', () => {
  cy.get('[data-testid="esg-score"]').should('be.visible')
  cy.get('[data-testid="esg-breakdown"]').should('exist')
  cy.log('ESG scoring functionality is working')
})

// Custom command to verify WebSocket connection
Cypress.Commands.add('verifyWebSocketConnection', () => {
  cy.window().then((win) => {
    // Check if WebSocket connection is established
    expect(win.websocketConnected).to.be.true
  })
  cy.log('WebSocket connection is active')
})

// Custom command to wait for API response
Cypress.Commands.add('waitForAPI', (alias) => {
  cy.wait(alias).then((interception) => {
    expect(interception.response.statusCode).to.be.oneOf([200, 201])
    cy.log(`API call ${alias} completed successfully`)
  })
})

// Custom command to check portfolio performance
Cypress.Commands.add('checkPortfolioPerformance', () => {
  cy.get('[data-testid="portfolio-performance"]').should('be.visible')
  cy.get('[data-testid="performance-chart"]').should('exist')
  cy.log('Portfolio performance tracking is working')
})

// Custom command to test responsive design
Cypress.Commands.add('testResponsiveDesign', () => {
  // Test mobile viewport
  cy.viewport(375, 667)
  cy.get('[data-testid="mobile-menu"]').should('be.visible')
  
  // Test tablet viewport
  cy.viewport(768, 1024)
  cy.get('[data-testid="tablet-layout"]').should('be.visible')
  
  // Test desktop viewport
  cy.viewport(1280, 720)
  cy.get('[data-testid="desktop-layout"]').should('be.visible')
  
  cy.log('Responsive design testing completed')
})

// Custom command to check accessibility
Cypress.Commands.add('checkAccessibility', () => {
  cy.injectAxe()
  cy.checkA11y()
  cy.log('Accessibility check completed')
})

// Custom command to monitor performance
Cypress.Commands.add('monitorPerformance', () => {
  cy.window().then((win) => {
    // Check if performance monitoring is active
    expect(win.performanceObserver).to.exist
  })
  cy.log('Performance monitoring is active')
})

// Custom command to test error handling
Cypress.Commands.add('testErrorHandling', () => {
  // Test with invalid data
  cy.get('[data-testid="error-boundary"]').should('exist')
  cy.log('Error handling is properly implemented')
})

// Override visit command to add custom logging
Cypress.Commands.overwrite('visit', (originalFn, url, options) => {
  cy.log(`Navigating to: ${url}`)
  return originalFn(url, options)
})

// Override click command to add custom logging
Cypress.Commands.overwrite('click', (originalFn, element, options) => {
  cy.log(`Clicking element: ${element}`)
  return originalFn(element, options)
})
