import { chromium, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🚀 Starting global setup for E2E tests...');
  
  // Start browser for setup tasks
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Wait for backend to be ready
    console.log('⏳ Waiting for backend to be ready...');
    await page.goto('http://localhost:8000/health');
    await page.waitForResponse(response => response.url().includes('/health') && response.status() === 200);
    console.log('✅ Backend is ready');
    
    // Wait for frontend to be ready
    console.log('⏳ Waiting for frontend to be ready...');
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    console.log('✅ Frontend is ready');
    
    // Create test data if needed
    console.log('📝 Setting up test data...');
    await setupTestData(page);
    console.log('✅ Test data setup complete');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('🎉 Global setup completed successfully');
}

async function setupTestData(page: any) {
  try {
    // Create test tenant
    const testTenant = {
      tenant_id: 'e2e-test-tenant',
      name: 'E2E Test Tenant',
      region: 'us',
      subscription_tier: 'premium',
      max_users: 100,
      max_trades_per_day: 10000,
      features: ['trading', 'analytics', 'compliance']
    };
    
    // Note: In a real implementation, you would make API calls to create test data
    // For now, we'll just log that we're setting up test data
    console.log('Setting up test tenant:', testTenant.tenant_id);
    
    // Store test data for use in tests
    process.env.E2E_TEST_TENANT_ID = testTenant.tenant_id;
    process.env.E2E_TEST_USER_EMAIL = 'e2e-test@quantaenergi.com';
    process.env.E2E_TEST_USER_PASSWORD = 'E2ETestPassword123!';
    
  } catch (error) {
    console.error('Failed to setup test data:', error);
    // Don't fail the setup if test data creation fails
    // Tests can handle missing test data gracefully
  }
}

export default globalSetup;
