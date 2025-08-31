describe('QuantaEnergi Authentication Flow', () => {
  beforeEach(() => {
    // Clear any existing data before each test
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  it('should display login page with QuantaEnergi branding', () => {
    cy.visit('/login')
    
    // Check QuantaEnergi branding
    cy.get('[data-testid="logo"]').should('contain', 'QuantaEnergi')
    cy.get('[data-testid="page-title"]').should('contain', 'Welcome to QuantaEnergi')
    
    // Check login form elements
    cy.get('[data-testid="email-input"]').should('be.visible')
    cy.get('[data-testid="password-input"]').should('be.visible')
    cy.get('[data-testid="login-button"]').should('be.visible')
    
    // Check for additional elements
    cy.get('[data-testid="forgot-password-link"]').should('be.visible')
    cy.get('[data-testid="register-link"]').should('be.visible')
  })

  it('should successfully login with valid credentials', () => {
    cy.login('test@quantaenergi.com', 'testpass123')
    
    // Verify successful login
    cy.url().should('include', '/dashboard')
    cy.get('[data-testid="welcome-message"]').should('contain', 'Welcome to QuantaEnergi')
    cy.get('[data-testid="user-menu"]').should('be.visible')
  })

  it('should show error message with invalid credentials', () => {
    cy.visit('/login')
    
    // Enter invalid credentials
    cy.get('[data-testid="email-input"]').type('invalid@email.com')
    cy.get('[data-testid="password-input"]').type('wrongpassword')
    cy.get('[data-testid="login-button"]').click()
    
    // Check error message
    cy.get('[data-testid="error-message"]').should('be.visible')
    cy.get('[data-testid="error-message"]').should('contain', 'Invalid credentials')
  })

  it('should validate required fields', () => {
    cy.visit('/login')
    
    // Try to submit without entering data
    cy.get('[data-testid="login-button"]').click()
    
    // Check validation messages
    cy.get('[data-testid="email-error"]').should('be.visible')
    cy.get('[data-testid="password-error"]').should('be.visible')
  })

  it('should successfully logout', () => {
    // Login first
    cy.login('test@quantaenergi.com', 'testpass123')
    
    // Then logout
    cy.logout()
    
    // Verify logout
    cy.url().should('include', '/login')
    cy.get('[data-testid="login-form"]').should('be.visible')
  })

  it('should redirect to dashboard after successful login', () => {
    cy.login('test@quantaenergi.com', 'testpass123')
    
    // Check dashboard elements
    cy.get('[data-testid="trading-dashboard"]').should('be.visible')
    cy.get('[data-testid="portfolio-summary"]').should('be.visible')
    cy.get('[data-testid="market-overview"]').should('be.visible')
  })

  it('should maintain session across page refreshes', () => {
    cy.login('test@quantaenergi.com', 'testpass123')
    
    // Refresh the page
    cy.reload()
    
    // Should still be logged in
    cy.url().should('include', '/dashboard')
    cy.get('[data-testid="user-menu"]').should('be.visible')
  })

  it('should handle session expiration gracefully', () => {
    // This test would require backend session management
    // For now, we'll test the UI behavior
    cy.visit('/dashboard')
    
    // Should redirect to login if not authenticated
    cy.url().should('include', '/login')
  })

  it('should show loading state during authentication', () => {
    cy.visit('/login')
    
    // Enter credentials
    cy.get('[data-testid="email-input"]').type('test@quantaenergi.com')
    cy.get('[data-testid="password-input"]').type('testpass123')
    
    // Click login and check loading state
    cy.get('[data-testid="login-button"]').click()
    cy.get('[data-testid="loading-spinner"]').should('be.visible')
    
    // Wait for login to complete
    cy.url().should('include', '/dashboard')
  })

  it('should handle network errors gracefully', () => {
    // Intercept API call and simulate network error
    cy.intercept('POST', '/api/auth/login', { forceNetworkError: true })
    
    cy.visit('/login')
    cy.get('[data-testid="email-input"]').type('test@quantaenergi.com')
    cy.get('[data-testid="password-input"]').type('testpass123')
    cy.get('[data-testid="login-button"]').click()
    
    // Check error handling
    cy.get('[data-testid="network-error"]').should('be.visible')
  })

  it('should support password reset flow', () => {
    cy.visit('/login')
    
    // Click forgot password link
    cy.get('[data-testid="forgot-password-link"]').click()
    
    // Should navigate to password reset page
    cy.url().should('include', '/reset-password')
    cy.get('[data-testid="reset-password-form"]').should('be.visible')
  })

  it('should support user registration', () => {
    cy.visit('/login')
    
    // Click register link
    cy.get('[data-testid="register-link"]').click()
    
    // Should navigate to registration page
    cy.url().should('include', '/register')
    cy.get('[data-testid="registration-form"]').should('be.visible')
  })
})
