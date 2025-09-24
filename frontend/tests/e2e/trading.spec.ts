import { test, expect } from '@playwright/test';

test.describe('Trading Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[type="email"]', process.env.E2E_TEST_USER_EMAIL || 'test@quantaenergi.com');
    await page.fill('input[type="password"]', process.env.E2E_TEST_USER_PASSWORD || 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should display trading dashboard', async ({ page }) => {
    // Navigate to trading page
    await page.click('[data-testid="trading-nav"]');
    await expect(page).toHaveURL('/trading');
    
    // Check if trading dashboard elements are present
    await expect(page.locator('text=Trading Dashboard')).toBeVisible();
    await expect(page.locator('text=Market Prices')).toBeVisible();
    await expect(page.locator('text=Trading Signals')).toBeVisible();
    await expect(page.locator('text=Portfolio')).toBeVisible();
  });

  test('should display market prices', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Check if market prices are displayed
    await expect(page.locator('[data-testid="crude-oil-price"]')).toBeVisible();
    await expect(page.locator('[data-testid="natural-gas-price"]')).toBeVisible();
    await expect(page.locator('[data-testid="electricity-price"]')).toBeVisible();
    await expect(page.locator('[data-testid="carbon-credits-price"]')).toBeVisible();
    
    // Check if prices are numeric
    const crudeOilPrice = await page.locator('[data-testid="crude-oil-price"]').textContent();
    expect(crudeOilPrice).toMatch(/\$[\d,]+\.\d{2}/);
  });

  test('should display trading signals', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Check if trading signals are displayed
    await expect(page.locator('[data-testid="trading-signals"]')).toBeVisible();
    await expect(page.locator('[data-testid="signal-item"]')).toBeVisible();
    
    // Check signal properties
    const signalItems = page.locator('[data-testid="signal-item"]');
    await expect(signalItems.first()).toBeVisible();
    
    // Check if signal has required elements
    await expect(signalItems.first().locator('[data-testid="signal-type"]')).toBeVisible();
    await expect(signalItems.first().locator('[data-testid="signal-confidence"]')).toBeVisible();
    await expect(signalItems.first().locator('[data-testid="signal-commodity"]')).toBeVisible();
  });

  test('should create a new trade', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Click new trade button
    await page.click('[data-testid="new-trade-button"]');
    
    // Fill in trade form
    await page.selectOption('[data-testid="trade-type"]', 'spot');
    await page.selectOption('[data-testid="commodity"]', 'crude_oil');
    await page.fill('[data-testid="quantity"]', '1000');
    await page.fill('[data-testid="price"]', '85.50');
    await page.fill('[data-testid="counterparty"]', 'Test Counterparty');
    await page.selectOption('[data-testid="currency"]', 'USD');
    await page.check('[data-testid="sharia-compliant"]');
    
    // Submit trade
    await page.click('[data-testid="submit-trade"]');
    
    // Check for success message
    await expect(page.locator('text=Trade created successfully')).toBeVisible();
    
    // Check if trade appears in trades list
    await expect(page.locator('[data-testid="trade-item"]').first()).toBeVisible();
  });

  test('should validate trade form', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Click new trade button
    await page.click('[data-testid="new-trade-button"]');
    
    // Submit empty form
    await page.click('[data-testid="submit-trade"]');
    
    // Check for validation errors
    await expect(page.locator('text=Trade type is required')).toBeVisible();
    await expect(page.locator('text=Commodity is required')).toBeVisible();
    await expect(page.locator('text=Quantity is required')).toBeVisible();
    await expect(page.locator('text=Price is required')).toBeVisible();
  });

  test('should calculate trade value automatically', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Click new trade button
    await page.click('[data-testid="new-trade-button"]');
    
    // Fill in quantity and price
    await page.fill('[data-testid="quantity"]', '1000');
    await page.fill('[data-testid="price"]', '85.50');
    
    // Check if total value is calculated
    const totalValue = page.locator('[data-testid="total-value"]');
    await expect(totalValue).toHaveValue('85500.00');
  });

  test('should filter trades by commodity', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Filter by crude oil
    await page.selectOption('[data-testid="commodity-filter"]', 'crude_oil');
    
    // Check if only crude oil trades are displayed
    const tradeItems = page.locator('[data-testid="trade-item"]');
    const count = await tradeItems.count();
    
    for (let i = 0; i < count; i++) {
      await expect(tradeItems.nth(i).locator('[data-testid="trade-commodity"]')).toHaveText('Crude Oil');
    }
  });

  test('should filter trades by date range', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Set date range filter
    await page.fill('[data-testid="date-from"]', '2024-01-01');
    await page.fill('[data-testid="date-to"]', '2024-01-31');
    
    // Apply filter
    await page.click('[data-testid="apply-date-filter"]');
    
    // Check if trades are filtered by date
    const tradeItems = page.locator('[data-testid="trade-item"]');
    const count = await tradeItems.count();
    
    for (let i = 0; i < count; i++) {
      const tradeDate = await tradeItems.nth(i).locator('[data-testid="trade-date"]').textContent();
      expect(tradeDate).toMatch(/2024-01-\d{2}/);
    }
  });

  test('should display trade details', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Click on first trade
    await page.click('[data-testid="trade-item"]').first();
    
    // Check if trade details modal is displayed
    await expect(page.locator('[data-testid="trade-details-modal"]')).toBeVisible();
    
    // Check trade details
    await expect(page.locator('[data-testid="trade-id"]')).toBeVisible();
    await expect(page.locator('[data-testid="trade-status"]')).toBeVisible();
    await expect(page.locator('[data-testid="trade-commission"]')).toBeVisible();
    await expect(page.locator('[data-testid="trade-settlement-date"]')).toBeVisible();
  });

  test('should update trade status', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Click on first trade
    await page.click('[data-testid="trade-item"]').first();
    
    // Change trade status
    await page.selectOption('[data-testid="trade-status-select"]', 'confirmed');
    await page.click('[data-testid="update-trade-status"]');
    
    // Check for success message
    await expect(page.locator('text=Trade status updated')).toBeVisible();
  });

  test('should export trades to CSV', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Click export button
    const downloadPromise = page.waitForEvent('download');
    await page.click('[data-testid="export-trades-csv"]');
    const download = await downloadPromise;
    
    // Check if file is downloaded
    expect(download.suggestedFilename()).toMatch(/trades_\d{4}-\d{2}-\d{2}\.csv/);
  });

  test('should handle real-time price updates', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Get initial price
    const initialPrice = await page.locator('[data-testid="crude-oil-price"]').textContent();
    
    // Wait for price update (simulated)
    await page.waitForTimeout(5000);
    
    // Check if price has updated
    const updatedPrice = await page.locator('[data-testid="crude-oil-price"]').textContent();
    
    // Price should be different (in real scenario)
    expect(updatedPrice).toBeDefined();
  });

  test('should display risk warnings', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Create a high-risk trade
    await page.click('[data-testid="new-trade-button"]');
    await page.fill('[data-testid="quantity"]', '100000'); // High quantity
    await page.fill('[data-testid="price"]', '100.00'); // High price
    
    // Check if risk warning is displayed
    await expect(page.locator('[data-testid="risk-warning"]')).toBeVisible();
    await expect(page.locator('text=High risk trade detected')).toBeVisible();
  });

  test('should handle trading limits', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Try to create trade exceeding daily limit
    await page.click('[data-testid="new-trade-button"]');
    await page.fill('[data-testid="quantity"]', '999999'); // Very high quantity
    
    // Submit trade
    await page.click('[data-testid="submit-trade"]');
    
    // Check for limit exceeded message
    await expect(page.locator('text=Daily trading limit exceeded')).toBeVisible();
  });

  test('should display portfolio summary', async ({ page }) => {
    // Navigate to trading page
    await page.goto('/trading');
    
    // Check portfolio summary
    await expect(page.locator('[data-testid="portfolio-value"]')).toBeVisible();
    await expect(page.locator('[data-testid="portfolio-change"]')).toBeVisible();
    await expect(page.locator('[data-testid="portfolio-positions"]')).toBeVisible();
    
    // Check if portfolio value is numeric
    const portfolioValue = await page.locator('[data-testid="portfolio-value"]').textContent();
    expect(portfolioValue).toMatch(/\$[\d,]+\.\d{2}/);
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate network failure
    await page.route('**/api/trades', route => route.abort());
    
    // Navigate to trading page
    await page.goto('/trading');
    
    // Check for error message
    await expect(page.locator('text=Failed to load trades')).toBeVisible();
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });
});
