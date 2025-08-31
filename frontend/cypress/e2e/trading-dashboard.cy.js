describe('QuantaEnergi Trading Dashboard', () => {
  beforeEach(() => {
    // Login before each test
    cy.login('test@quantaenergi.com', 'testpass123')
    cy.navigateToTradingDashboard()
  })

  it('should display trading dashboard with all components', () => {
    // Check main dashboard elements
    cy.get('[data-testid="trading-dashboard"]').should('be.visible')
    cy.get('[data-testid="portfolio-summary"]').should('be.visible')
    cy.get('[data-testid="market-overview"]').should('be.visible')
    cy.get('[data-testid="trade-form"]').should('be.visible')
    cy.get('[data-testid="recent-trades"]').should('be.visible')
    
    // Check QuantaEnergi branding
    cy.get('[data-testid="dashboard-title"]').should('contain', 'QuantaEnergi Trading Dashboard')
  })

  it('should display real-time market data', () => {
    // Check market data section
    cy.get('[data-testid="market-data"]').should('be.visible')
    cy.get('[data-testid="price-update"]').should('exist')
    
    // Check for different commodities
    cy.get('[data-testid="commodity-price"]').should('have.length.at.least', 3)
    
    // Verify WebSocket connection
    cy.verifyWebSocketConnection()
  })

  it('should show portfolio performance metrics', () => {
    // Check portfolio section
    cy.get('[data-testid="portfolio-performance"]').should('be.visible')
    cy.get('[data-testid="performance-chart"]').should('exist')
    
    // Check key metrics
    cy.get('[data-testid="total-value"]').should('be.visible')
    cy.get('[data-testid="daily-change"]').should('be.visible')
    cy.get('[data-testid="esg-score"]').should('be.visible')
  })

  it('should execute trades successfully', () => {
    // Test trade execution
    cy.executeTrade('crude_oil', '100', '85.50')
    
    // Verify trade confirmation
    cy.get('[data-testid="trade-confirmation"]').should('be.visible')
    cy.get('[data-testid="trade-id"]').should('exist')
    
    // Check portfolio update
    cy.get('[data-testid="portfolio-update"]').should('be.visible')
  })

  it('should validate trade form inputs', () => {
    // Test invalid inputs
    cy.get('[data-testid="trade-form"]').within(() => {
      // Try negative quantity
      cy.get('[data-testid="quantity-input"]').type('-100')
      cy.get('[data-testid="execute-trade-button"]').click()
      cy.get('[data-testid="quantity-error"]').should('be.visible')
      
      // Try zero price
      cy.get('[data-testid="quantity-input"]').clear().type('100')
      cy.get('[data-testid="price-input"]').type('0')
      cy.get('[data-testid="execute-trade-button"]').click()
      cy.get('[data-testid="price-error"]').should('be.visible')
    })
  })

  it('should display ESG scoring and sustainability metrics', () => {
    // Check ESG section
    cy.checkESGScore()
    
    // Check sustainability metrics
    cy.get('[data-testid="carbon-footprint"]').should('be.visible')
    cy.get('[data-testid="renewable-ratio"]').should('be.visible')
    cy.get('[data-testid="sustainability-score"]').should('be.visible')
  })

  it('should show recent trades and history', () => {
    // Check recent trades section
    cy.get('[data-testid="recent-trades"]').should('be.visible')
    cy.get('[data-testid="trade-history"]').should('exist')
    
    // Check trade details
    cy.get('[data-testid="trade-item"]').should('have.length.at.least', 1)
    
    // Check trade information
    cy.get('[data-testid="trade-commodity"]').should('be.visible')
    cy.get('[data-testid="trade-quantity"]').should('be.visible')
    cy.get('[data-testid="trade-price"]').should('be.visible')
    cy.get('[data-testid="trade-timestamp"]').should('be.visible')
  })

  it('should handle real-time updates via WebSocket', () => {
    // Verify WebSocket connection
    cy.verifyWebSocketConnection()
    
    // Check for real-time price updates
    cy.get('[data-testid="price-update"]').should('exist')
    
    // Monitor for changes
    cy.get('[data-testid="last-updated"]').should('be.visible')
  })

  it('should display market overview with charts', () => {
    // Check market overview section
    cy.get('[data-testid="market-overview"]').should('be.visible')
    
    // Check for charts
    cy.get('[data-testid="price-chart"]').should('exist')
    cy.get('[data-testid="volume-chart"]').should('exist')
    
    // Check market indicators
    cy.get('[data-testid="market-indicators"]').should('be.visible')
  })

  it('should support different timeframes for charts', () => {
    // Check timeframe selector
    cy.get('[data-testid="timeframe-selector"]').should('be.visible')
    
    // Test different timeframes
    cy.get('[data-testid="timeframe-selector"]').select('1D')
    cy.get('[data-testid="price-chart"]').should('exist')
    
    cy.get('[data-testid="timeframe-selector"]').select('1W')
    cy.get('[data-testid="price-chart"]').should('exist')
    
    cy.get('[data-testid="timeframe-selector"]').select('1M')
    cy.get('[data-testid="price-chart"]').should('exist')
  })

  it('should handle error scenarios gracefully', () => {
    // Test error handling
    cy.testErrorHandling()
    
    // Check for error boundaries
    cy.get('[data-testid="error-boundary"]').should('exist')
    
    // Test network error handling
    cy.intercept('GET', '/api/market-data', { forceNetworkError: true })
    cy.reload()
    cy.get('[data-testid="network-error"]').should('be.visible')
  })

  it('should be responsive across different screen sizes', () => {
    // Test responsive design
    cy.testResponsiveDesign()
    
    // Check mobile layout
    cy.viewport(375, 667)
    cy.get('[data-testid="mobile-menu"]').should('be.visible')
    
    // Check tablet layout
    cy.viewport(768, 1024)
    cy.get('[data-testid="tablet-layout"]').should('be.visible')
    
    // Check desktop layout
    cy.viewport(1280, 720)
    cy.get('[data-testid="desktop-layout"]').should('be.visible')
  })

  it('should support keyboard navigation', () => {
    // Test keyboard navigation
    cy.get('body').tab()
    cy.focused().should('have.attr', 'data-testid', 'navigation-menu')
    
    // Test tab order
    cy.get('[data-testid="trade-form"]').within(() => {
      cy.get('[data-testid="commodity-select"]').focus()
      cy.tab()
      cy.focused().should('have.attr', 'data-testid', 'quantity-input')
    })
  })

  it('should meet accessibility standards', () => {
    // Check accessibility
    cy.checkAccessibility()
    
    // Check ARIA labels
    cy.get('[data-testid="price-chart"]').should('have.attr', 'aria-label')
    cy.get('[data-testid="trade-form"]').should('have.attr', 'aria-labelledby')
  })

  it('should monitor performance metrics', () => {
    // Check performance monitoring
    cy.monitorPerformance()
    
    // Check for performance indicators
    cy.get('[data-testid="performance-metrics"]').should('be.visible')
  })
})
