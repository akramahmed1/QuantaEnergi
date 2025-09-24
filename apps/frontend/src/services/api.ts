import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/api/v1/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  
  getMe: async () => {
    const response = await api.get('/api/v1/me');
    return response.data;
  },
};

// Trade API
export const tradeAPI = {
  captureTrade: async (trade: any) => {
    const response = await api.post('/api/v1/capture', trade);
    return response.data;
  },
  
  validateTrade: async (tradeId: string) => {
    const response = await api.post(`/api/v1/validate/${tradeId}`);
    return response.data;
  },
  
  settleTrade: async (tradeId: string) => {
    const response = await api.post(`/api/v1/settle/${tradeId}`);
    return response.data;
  },
  
  getTrades: async () => {
    const response = await api.get('/api/v1/trades');
    return response.data;
  },
  
  getTrade: async (tradeId: string) => {
    const response = await api.get(`/api/v1/trades/${tradeId}`);
    return response.data;
  },
};

export default api;
