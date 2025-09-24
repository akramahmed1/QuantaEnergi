import { test, expect } from '@playwright/test';

test.describe('Risk Analytics', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', process.env.E2E_TEST_USER_EMAIL || 'test@quantaenergi.com');
    await page.fill('input[type="password"]', process.env.E2E_TEST_USER_PASSWORD || 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should display risk analytics dashboard', async ({ page }) => {
    // Navigate to risk analytics page
    await page.click('[data-testid="risk-analytics-nav"]');
    await expect(page).toHaveURL('/risk-analytics');
    
    // Check if risk analytics elements are present
    await expect(page.locator('text=Risk Analytics')).toBeVisible();
    await expect(page.locator('text=Portfolio Risk')).toBeVisible();
    await expect(page.locator('text=Value at Risk (VaR)')).toBeVisible();
    await expect(page.locator('text=Stress Testing')).toBeVisible();
  });

  test('should calculate VaR for portfolio', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Select portfolio
    await page.selectOption('[data-testid="portfolio-select"]', 'main-portfolio');
    
    // Set VaR parameters
    await page.selectOption('[data-testid="confidence-level"]', '95');
    await page.selectOption('[data-testid="time-horizon"]', '1');
    await page.selectOption('[data-testid="calculation-method"]', 'monte_carlo');
    
    // Calculate VaR
    await page.click('[data-testid="calculate-var"]');
    
    // Wait for calculation to complete
    await expect(page.locator('[data-testid="var-result"]')).toBeVisible({ timeout: 30000 });
    
    // Check VaR result
    await expect(page.locator('[data-testid="var-value"]')).toBeVisible();
    await expect(page.locator('[data-testid="expected-shortfall"]')).toBeVisible();
    await expect(page.locator('[data-testid="max-loss"]')).toBeVisible();
    
    // Check if VaR value is numeric
    const varValue = await page.locator('[data-testid="var-value"]').textContent();
    expect(varValue).toMatch(/\$[\d,]+\.\d{2}/);
  });

  test('should display VaR calculation progress', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Start VaR calculation
    await page.click('[data-testid="calculate-var"]');
    
    // Check if progress indicator is shown
    await expect(page.locator('[data-testid="calculation-progress"]')).toBeVisible();
    await expect(page.locator('text=Calculating VaR...')).toBeVisible();
  });

  test('should run stress test scenario', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Go to stress testing tab
    await page.click('[data-testid="stress-testing-tab"]');
    
    // Select stress test scenario
    await page.selectOption('[data-testid="stress-scenario"]', 'market_crash');
    
    // Run stress test
    await page.click('[data-testid="run-stress-test"]');
    
    // Wait for stress test to complete
    await expect(page.locator('[data-testid="stress-test-result"]')).toBeVisible({ timeout: 30000 });
    
    // Check stress test results
    await expect(page.locator('[data-testid="portfolio-loss"]')).toBeVisible();
    await expect(page.locator('[data-testid="position-losses"]')).toBeVisible();
    await expect(page.locator('[data-testid="market-shocks"]')).toBeVisible();
    
    // Check if portfolio loss is numeric
    const portfolioLoss = await page.locator('[data-testid="portfolio-loss"]').textContent();
    expect(portfolioLoss).toMatch(/\$[\d,]+\.\d{2}/);
  });

  test('should create custom stress test scenario', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Go to stress testing tab
    await page.click('[data-testid="stress-testing-tab"]');
    
    // Click create custom scenario
    await page.click('[data-testid="create-custom-scenario"]');
    
    // Fill in custom scenario details
    await page.fill('[data-testid="scenario-name"]', 'Custom Market Shock');
    await page.fill('[data-testid="crude-oil-shock"]', '-0.25');
    await page.fill('[data-testid="natural-gas-shock"]', '-0.15');
    await page.fill('[data-testid="electricity-shock"]', '-0.30');
    
    // Save custom scenario
    await page.click('[data-testid="save-scenario"]');
    
    // Check for success message
    await expect(page.locator('text=Custom scenario created')).toBeVisible();
    
    // Verify scenario appears in dropdown
    await expect(page.locator('[data-testid="stress-scenario"]')).toContainText('Custom Market Shock');
  });

  test('should display risk metrics dashboard', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Check risk metrics
    await expect(page.locator('[data-testid="sharpe-ratio"]')).toBeVisible();
    await expect(page.locator('[data-testid="beta"]')).toBeVisible();
    await expect(page.locator('[data-testid="alpha"]')).toBeVisible();
    await expect(page.locator('[data-testid="portfolio-volatility"]')).toBeVisible();
    
    // Check if metrics are numeric
    const sharpeRatio = await page.locator('[data-testid="sharpe-ratio"]').textContent();
    expect(sharpeRatio).toMatch(/\d+\.\d{2}/);
  });

  test('should display risk concentration analysis', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Go to concentration tab
    await page.click('[data-testid="concentration-tab"]');
    
    // Check concentration analysis
    await expect(page.locator('[data-testid="concentration-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="commodity-concentration"]')).toBeVisible();
    await expect(page.locator('[data-testid="region-concentration"]')).toBeVisible();
    
    // Check if concentration percentages add up to 100%
    const concentrationItems = page.locator('[data-testid="concentration-item"]');
    const count = await concentrationItems.count();
    
    let totalConcentration = 0;
    for (let i = 0; i < count; i++) {
      const percentage = await concentrationItems.nth(i).locator('[data-testid="concentration-percentage"]').textContent();
      totalConcentration += parseFloat(percentage?.replace('%', '') || '0');
    }
    
    expect(totalConcentration).toBeCloseTo(100, 1);
  });

  test('should display correlation matrix', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Go to correlation tab
    await page.click('[data-testid="correlation-tab"]');
    
    // Check correlation matrix
    await expect(page.locator('[data-testid="correlation-matrix"]')).toBeVisible();
    await expect(page.locator('[data-testid="correlation-heatmap"]')).toBeVisible();
    
    // Check correlation values are between -1 and 1
    const correlationCells = page.locator('[data-testid="correlation-cell"]');
    const count = await correlationCells.count();
    
    for (let i = 0; i < count; i++) {
      const correlation = await correlationCells.nth(i).textContent();
      const value = parseFloat(correlation || '0');
      expect(value).toBeGreaterThanOrEqual(-1);
      expect(value).toBeLessThanOrEqual(1);
    }
  });

  test('should generate risk report', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Click generate report button
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="generate-risk-report"]');
    const download = await downloadPromise;
    
    // Check if report is downloaded
    expect(download.suggestedFilename()).toMatch(/risk_report_\d{4}-\d{2}-\d{2}\.pdf/);
  });

  test('should set risk limits', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Go to risk limits tab
    await page.click('[data-testid="risk-limits-tab"]');
    
    // Set VaR limit
    await page.fill('[data-testid="var-limit"]', '100000');
    
    // Set position limit
    await page.fill('[data-testid="position-limit"]', '500000');
    
    // Set concentration limit
    await page.fill('[data-testid="concentration-limit"]', '0.3');
    
    // Save limits
    await page.click('[data-testid="save-risk-limits"]');
    
    // Check for success message
    await expect(page.locator('text=Risk limits updated')).toBeVisible();
  });

  test('should display risk limit breaches', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Go to risk limits tab
    await page.click('[data-testid="risk-limits-tab"]');
    
    // Check if limit breaches are displayed
    await expect(page.locator('[data-testid="limit-breach"]')).toBeVisible();
    await expect(page.locator('text=Risk limit breached')).toBeVisible();
    
    // Check breach details
    await expect(page.locator('[data-testid="breach-type"]')).toBeVisible();
    await expect(page.locator('[data-testid="breach-value"]')).toBeVisible();
    await expect(page.locator('[data-testid="breach-limit"]')).toBeVisible();
  });

  test('should display historical VaR', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Go to historical tab
    await page.click('[data-testid="historical-tab"]');
    
    // Check historical VaR chart
    await expect(page.locator('[data-testid="historical-var-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="var-timeline"]')).toBeVisible();
    
    // Check date range selector
    await expect(page.locator('[data-testid="date-range-selector"]')).toBeVisible();
    
    // Select different date range
    await page.selectOption('[data-testid="date-range-selector"]', '3m');
    
    // Check if chart updates
    await expect(page.locator('[data-testid="historical-var-chart"]')).toBeVisible();
  });

  test('should handle calculation errors gracefully', async ({ page }) => {
    // Simulate calculation error
    await page.route('**/api/risk-analytics/var', route => route.abort());
    
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Try to calculate VaR
    await page.click('[data-testid="calculate-var"]');
    
    // Check for error message
    await expect(page.locator('text=Failed to calculate VaR')).toBeVisible();
    await expect(page.locator('[data-testid="retry-calculation"]')).toBeVisible();
  });

  test('should display real-time risk monitoring', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Check real-time monitoring
    await expect(page.locator('[data-testid="real-time-risk"]')).toBeVisible();
    await expect(page.locator('[data-testid="risk-alerts"]')).toBeVisible();
    
    // Check if risk level is displayed
    await expect(page.locator('[data-testid="current-risk-level"]')).toBeVisible();
    
    // Check risk level color coding
    const riskLevel = page.locator('[data-testid="current-risk-level"]');
    const className = await riskLevel.getAttribute('class');
    expect(className).toMatch(/risk-(low|medium|high)/);
  });

  test('should export risk data', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Click export button
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-risk-data"]');
    const download = await downloadPromise;
    
    // Check if data is exported
    expect(download.suggestedFilename()).toMatch(/risk_data_\d{4}-\d{2}-\d{2}\.xlsx/);
  });

  test('should display Monte Carlo simulation results', async ({ page }) => {
    // Navigate to risk analytics page
    await page.goto('/risk-analytics');
    
    // Run Monte Carlo simulation
    await page.click('[data-testid="run-monte-carlo"]');
    
    // Wait for simulation to complete
    await expect(page.locator('[data-testid="monte-carlo-results"]')).toBeVisible({ timeout: 60000 });
    
    // Check simulation results
    await expect(page.locator('[data-testid="simulation-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="simulation-stats"]')).toBeVisible();
    await expect(page.locator('[data-testid="confidence-intervals"]')).toBeVisible();
    
    // Check simulation parameters
    await expect(page.locator('[data-testid="simulation-count"]')).toBeVisible();
    await expect(page.locator('[data-testid="simulation-time"]')).toBeVisible();
  });
});
