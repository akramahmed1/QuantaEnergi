const API_BASE_URL = 'http://localhost:8001';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Get auth headers with JWT token
  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    };
  }

  // Handle API responses
  async handleResponse(response) {
    if (response.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      throw new Error('Authentication required');
    }
    
    if (response.status === 403) {
      throw new Error('Insufficient permissions');
    }
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || 'Request failed');
    }
    
    return response.json();
  }

  // Generic API request method
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: this.getAuthHeaders(),
      ...options
    };

    try {
      const response = await fetch(url, config);
      return await this.handleResponse(response);
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication methods
  async login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  async signup(email, password, company_name, role = 'user') {
    return this.request('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ email, password, company_name, role })
    });
  }

  async getCurrentUser() {
    return this.request('/api/auth/me');
  }

  // Energy data methods
  async getMarketPrices(region = 'global', ramadan_mode = false) {
    const params = new URLSearchParams();
    if (region) params.append('region', region);
    if (ramadan_mode) params.append('ramadan_mode', 'true');
    
    return this.request(`/api/prices?${params.toString()}`);
  }

  async getRenewableEnergy() {
    return this.request('/api/renewables');
  }

  async getOilfieldData() {
    return this.request('/api/oilfield');
  }

  async getTariffImpact() {
    return this.request('/api/tariff_impact');
  }

  async getRetentionData() {
    return this.request('/api/retention');
  }

  async getOnboardingGuide(user_type = 'trader') {
    return this.request(`/api/onboarding?user_type=${user_type}`);
  }

  // New API methods for enhanced UI components
  async getUserAnalytics() {
    return this.request('/api/analytics');
  }

  async getTrades() {
    return this.request('/api/trades');
  }

  async getForecast() {
    return this.request('/api/forecast');
  }

  async getSecureData() {
    return this.request('/api/secure');
  }

  async getSecurityTransparency() {
    return this.request('/api/secure/transparency');
  }

  async getEnhancedPrices(region = 'global', ramadan_mode = false) {
    const params = new URLSearchParams();
    if (region) params.append('region', region);
    if (ramadan_mode) params.append('ramadan_mode', 'true');
    
    return this.request(`/api/models/v1/prices?${params.toString()}`);
  }

  // Health check
  async getHealthStatus() {
    return this.request('/api/health');
  }

  // Weather methods
  async getCurrentWeather(lat = 33.44, lon = -94.04) {
    return this.request(`/api/weather/current?lat=${lat}&lon=${lon}`);
  }

  async getWeatherForecast(lat = 33.44, lon = -94.04) {
    return this.request(`/api/weather/forecast?lat=${lat}&lon=${lon}`);
  }

  // Logout
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('token');
  }

  // Get current user data
  getCurrentUserData() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
