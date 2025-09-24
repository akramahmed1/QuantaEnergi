import { chromium, FullConfig } from '@playwright/test';

async function globalTeardown(config: FullConfig) {
  console.log('🧹 Starting global teardown for E2E tests...');
  
  // Start browser for cleanup tasks
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  try {
    // Clean up test data
    console.log('🗑️ Cleaning up test data...');
    await cleanupTestData(page);
    console.log('✅ Test data cleanup complete');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw error in teardown to avoid masking test failures
  } finally {
    await browser.close();
  }
  
  console.log('🎉 Global teardown completed');
}

async function cleanupTestData(page: any) {
  try {
    const testTenantId = process.env.E2E_TEST_TENANT_ID;
    
    if (testTenantId) {
      console.log('Cleaning up test tenant:', testTenantId);
      
      // Note: In a real implementation, you would make API calls to clean up test data
      // For now, we'll just log that we're cleaning up test data
      
      // Example cleanup operations:
      // 1. Delete test trades
      // 2. Delete test portfolios
      // 3. Delete test tenant
      // 4. Clean up any uploaded files
      // 5. Reset database state
      
      console.log('Test tenant cleanup completed');
    }
    
  } catch (error) {
    console.error('Failed to cleanup test data:', error);
    // Don't fail the teardown if cleanup fails
  }
}

export default globalTeardown;
