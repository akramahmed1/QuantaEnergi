/**
 * Authentication Middleware for QuantaEnergi Frontend
 * Production-Ready JWT Authentication with Role-Based Access Control
 */

import { jwtDecode } from 'jwt-decode';
import { User, AuthState, LoginCredentials, RegisterData } from '@/types/auth';

// JWT Token interface
interface JWTPayload {
  sub: string;
  username: string;
  email: string;
  roles: string[];
  exp: number;
  iat: number;
  company?: string;
  permissions?: string[];
}

// Authentication service class
class AuthService {
  private baseURL: string;
  private tokenKey: string = 'quantaenergi_token';
  private refreshTokenKey: string = 'quantaenergi_refresh_token';
  private userKey: string = 'quantaenergi_user';

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }

  /**
   * Login user with credentials
   */
  async login(credentials: LoginCredentials): Promise<AuthState> {
    try {
      const response = await fetch(`${this.baseURL}/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Store tokens
      localStorage.setItem(this.tokenKey, data.access_token);
      localStorage.setItem(this.refreshTokenKey, data.refresh_token);
      localStorage.setItem(this.userKey, JSON.stringify(data.user));

      return {
        user: data.user,
        token: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      };
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Register new user
   */
  async register(userData: RegisterData): Promise<User> {
    try {
      const response = await fetch(`${this.baseURL}/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      const token = this.getToken();
      if (token) {
        await fetch(`${this.baseURL}/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token }),
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API call success
      localStorage.removeItem(this.tokenKey);
      localStorage.removeItem(this.refreshTokenKey);
      localStorage.removeItem(this.userKey);
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string | null> {
    try {
      const refreshToken = localStorage.getItem(this.refreshTokenKey);
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch(`${this.baseURL}/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      localStorage.setItem(this.tokenKey, data.access_token);
      
      return data.access_token;
    } catch (error) {
      console.error('Token refresh error:', error);
      // If refresh fails, logout user
      await this.logout();
      return null;
    }
  }

  /**
   * Get current user from localStorage
   */
  getCurrentUser(): User | null {
    try {
      const userStr = localStorage.getItem(this.userKey);
      return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  }

  /**
   * Get access token from localStorage
   */
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      const decoded = jwtDecode<JWTPayload>(token);
      const now = Date.now() / 1000;
      
      // Check if token is expired
      if (decoded.exp < now) {
        // Try to refresh token
        this.refreshToken();
        return false;
      }
      
      return true;
    } catch (error) {
      console.error('Token validation error:', error);
      return false;
    }
  }

  /**
   * Check if user has specific role
   */
  hasRole(role: string): boolean {
    const user = this.getCurrentUser();
    return user ? user.roles.includes(role) : false;
  }

  /**
   * Check if user has any of the specified roles
   */
  hasAnyRole(roles: string[]): boolean {
    const user = this.getCurrentUser();
    if (!user) return false;
    
    return roles.some(role => user.roles.includes(role));
  }

  /**
   * Check if user has specific permission
   */
  hasPermission(permission: string): boolean {
    const user = this.getCurrentUser();
    return user ? (user.permissions || []).includes(permission) : false;
  }

  /**
   * Get user's JWT payload
   */
  getTokenPayload(): JWTPayload | null {
    const token = this.getToken();
    if (!token) return null;

    try {
      return jwtDecode<JWTPayload>(token);
    } catch (error) {
      console.error('Token decode error:', error);
      return null;
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData: Partial<User>): Promise<User> {
    try {
      const token = this.getToken();
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch(`${this.baseURL}/v1/auth/me`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Profile update failed');
      }

      const data = await response.json();
      
      // Update stored user data
      localStorage.setItem(this.userKey, JSON.stringify(data));
      
      return data;
    } catch (error) {
      console.error('Profile update error:', error);
      throw error;
    }
  }

  /**
   * Change user password
   */
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    try {
      const token = this.getToken();
      if (!token) {
        throw new Error('No authentication token');
      }

      const response = await fetch(`${this.baseURL}/v1/auth/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Password change failed');
      }
    } catch (error) {
      console.error('Password change error:', error);
      throw error;
    }
  }

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}/v1/auth/reset-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Password reset request failed');
      }
    } catch (error) {
      console.error('Password reset request error:', error);
      throw error;
    }
  }

  /**
   * Initialize authentication state from localStorage
   */
  initializeAuth(): AuthState {
    const user = this.getCurrentUser();
    const token = this.getToken();
    const isAuthenticated = this.isAuthenticated();

    return {
      user: isAuthenticated ? user : null,
      token: isAuthenticated ? token : null,
      refreshToken: isAuthenticated ? localStorage.getItem(this.refreshTokenKey) : null,
      isAuthenticated,
      isLoading: false,
    };
  }
}

// Create singleton instance
export const authService = new AuthService();

// Export types and service
export type { JWTPayload, AuthState, User, LoginCredentials, RegisterData };
export default authService;
