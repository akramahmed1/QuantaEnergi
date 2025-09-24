import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the login page before each test
    await page.goto('/login');
  });

  test('should display login form', async ({ page }) => {
    // Check if login form elements are present
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
    
    // Check for login form labels
    await expect(page.locator('text=Email')).toBeVisible();
    await expect(page.locator('text=Password')).toBeVisible();
    await expect(page.locator('text=Sign In')).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    // Submit empty form
    await page.click('button[type="submit"]');
    
    // Check for validation errors
    await expect(page.locator('text=Email is required')).toBeVisible();
    await expect(page.locator('text=Password is required')).toBeVisible();
  });

  test('should show validation error for invalid email', async ({ page }) => {
    // Fill in invalid email
    await page.fill('input[type="email"]', 'invalid-email');
    await page.fill('input[type="password"]', 'password123');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for email validation error
    await expect(page.locator('text=Please enter a valid email')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    // Fill in invalid credentials
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for error message
    await expect(page.locator('text=Invalid email or password')).toBeVisible();
  });

  test('should successfully login with valid credentials', async ({ page }) => {
    // Fill in valid credentials
    await page.fill('input[type="email"]', process.env.E2E_TEST_USER_EMAIL || 'test@quantaenergi.com');
    await page.fill('input[type="password"]', process.env.E2E_TEST_USER_PASSWORD || 'TestPassword123!');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');
    
    // Check if we're on the dashboard
    await expect(page.locator('text=Dashboard')).toBeVisible();
    await expect(page.locator('text=Welcome back')).toBeVisible();
  });

  test('should redirect to dashboard if already logged in', async ({ page }) => {
    // First, login
    await page.fill('input[type="email"]', process.env.E2E_TEST_USER_EMAIL || 'test@quantaenergi.com');
    await page.fill('input[type="password"]', process.env.E2E_TEST_USER_PASSWORD || 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    // Try to navigate to login page again
    await page.goto('/login');
    
    // Should be redirected back to dashboard
    await expect(page).toHaveURL('/dashboard');
  });

  test('should logout successfully', async ({ page }) => {
    // First, login
    await page.fill('input[type="email"]', process.env.E2E_TEST_USER_EMAIL || 'test@quantaenergi.com');
    await page.fill('input[type="password"]', process.env.E2E_TEST_USER_PASSWORD || 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    // Click logout button
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // Should be redirected to login page
    await expect(page).toHaveURL('/login');
    await expect(page.locator('text=Sign In')).toBeVisible();
  });

  test('should handle password reset flow', async ({ page }) => {
    // Click forgot password link
    await page.click('text=Forgot password?');
    
    // Should navigate to password reset page
    await expect(page).toHaveURL('/forgot-password');
    await expect(page.locator('text=Reset Password')).toBeVisible();
    
    // Fill in email
    await page.fill('input[type="email"]', 'test@quantaenergi.com');
    await page.click('button[type="submit"]');
    
    // Check for success message
    await expect(page.locator('text=Password reset email sent')).toBeVisible();
  });

  test('should handle registration flow', async ({ page }) => {
    // Click register link
    await page.click('text=Create account');
    
    // Should navigate to registration page
    await expect(page).toHaveURL('/register');
    await expect(page.locator('text=Create Account')).toBeVisible();
    
    // Fill in registration form
    await page.fill('input[name="firstName"]', 'Test');
    await page.fill('input[name="lastName"]', 'User');
    await page.fill('input[name="email"]', 'newuser@quantaenergi.com');
    await page.fill('input[name="password"]', 'NewPassword123!');
    await page.fill('input[name="confirmPassword"]', 'NewPassword123!');
    await page.check('input[name="terms"]');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Check for success message
    await expect(page.locator('text=Account created successfully')).toBeVisible();
  });

  test('should handle multi-factor authentication', async ({ page }) => {
    // Login with MFA-enabled account
    await page.fill('input[type="email"]', 'mfa@quantaenergi.com');
    await page.fill('input[type="password"]', 'MFAPassword123!');
    await page.click('button[type="submit"]');
    
    // Should be redirected to MFA page
    await expect(page).toHaveURL('/mfa');
    await expect(page.locator('text=Enter verification code')).toBeVisible();
    
    // Fill in MFA code
    await page.fill('input[name="mfaCode"]', '123456');
    await page.click('button[type="submit"]');
    
    // Should be redirected to dashboard
    await expect(page).toHaveURL('/dashboard');
  });

  test('should handle session timeout', async ({ page }) => {
    // Login
    await page.fill('input[type="email"]', process.env.E2E_TEST_USER_EMAIL || 'test@quantaenergi.com');
    await page.fill('input[type="password"]', process.env.E2E_TEST_USER_PASSWORD || 'TestPassword123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    // Simulate session timeout by clearing storage
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    
    // Try to navigate to a protected page
    await page.goto('/trades');
    
    // Should be redirected to login page
    await expect(page).toHaveURL('/login');
    await expect(page.locator('text=Session expired')).toBeVisible();
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Simulate network failure
    await page.route('**/api/auth/login', route => route.abort());
    
    // Try to login
    await page.fill('input[type="email"]', 'test@quantaenergi.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Check for network error message
    await expect(page.locator('text=Network error. Please try again.')).toBeVisible();
  });
});
