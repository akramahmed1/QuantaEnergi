import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Authentication
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', credentials),
  logout: () => api.post('/auth/logout'),
};

// Trading APIs
export const tradingAPI = {
  createTrade: (trade: any) => api.post('/api/v1/etrm/trades', trade),
  executeTrade: (tradeId: string, marketPrice: number) =>
    api.post(`/api/v1/etrm/trades/${tradeId}/execute`, { market_price: marketPrice }),
  getPortfolioSummary: () => api.get('/api/v1/etrm/trades/portfolio'),
  getRecentTrades: (limit: number = 10) => api.get(`/api/trades/recent?limit=${limit}`),
};

// Risk Management APIs
export const riskAPI = {
  addRiskLimit: (riskLimit: any) => api.post('/api/v1/etrm/risk/limits', riskLimit),
  getRiskLimitsStatus: () => api.get('/api/v1/etrm/risk/limits/status'),
  runStressTest: (scenarioId: string, positions: any) =>
    api.post('/api/v1/etrm/risk/stress-test', { scenario_id: scenarioId, positions }),
  calculateVar: (portfolioId: string, confidence: number = 0.95) =>
    api.get(`/api/v1/risk/var?portfolio_id=${portfolioId}&confidence=${confidence}`),
};

// Pricing APIs
export const pricingAPI = {
  calculatePricing: (pricingRequest: any) => api.post('/api/v1/etrm/pricing/calculate', pricingRequest),
};

// Portfolio Optimization APIs
export const portfolioAPI = {
  optimizePortfolio: (optimizationRequest: any) =>
    api.post('/api/v1/etrm/portfolio/optimize', optimizationRequest),
  getPortfolioSummary: () => api.get('/api/portfolio/summary'),
};

// Compliance APIs
export const complianceAPI = {
  checkCompliance: (complianceRequest: any) =>
    api.post('/api/v1/etrm/compliance/check', complianceRequest),
};

// Credit Risk APIs
export const creditRiskAPI = {
  calculateCreditRisk: (creditRequest: any) =>
    api.post('/api/v1/etrm/credit-risk/calculate', creditRequest),
};

// Analytics APIs
export const analyticsAPI = {
  calculatePerformanceAnalytics: (analyticsRequest: any) =>
    api.post('/api/v1/etrm/analytics/performance', analyticsRequest),
  getUserAnalytics: () => api.get('/api/analytics'),
};

// Market Data APIs
export const marketDataAPI = {
  getLatestPrice: (symbol: string) => api.get(`/api/v1/etrm/market-data/${symbol}/price`),
  getVolatility: (symbol: string, volType: string = 'historical') =>
    api.get(`/api/v1/etrm/market-data/${symbol}/volatility?vol_type=${volType}`),
  getCorrelation: (symbol1: string, symbol2: string) =>
    api.get(`/api/v1/etrm/market-data/${symbol1}/${symbol2}/correlation`),
  getMarketPrices: (region: string = 'global', ramadanMode: boolean = false) =>
    api.get(`/api/market/prices?region=${region}&ramadan_mode=${ramadanMode}`),
  getRenewableEnergy: () => api.get('/api/renewables'),
};

// ESG APIs
export const esgAPI = {
  getESGMetrics: () => api.get('/api/esg/metrics'),
  trackESG: (tradeId: number) => api.post('/esg/track', { trade_id: tradeId }),
};

// Weather APIs
export const weatherAPI = {
  getCurrentWeather: (lat: number, lon: number) =>
    api.get(`/api/weather/current?lat=${lat}&lon=${lon}`),
  getWeatherForecast: (lat: number, lon: number, days: number = 7) =>
    api.get(`/api/weather/forecast?lat=${lat}&lon=${lon}&days=${days}`),
};

// Trading Signals APIs
export const signalsAPI = {
  getTradingSignals: (commodity?: string, confidenceMin: number = 50.0) =>
    api.get(`/api/signals?commodity=${commodity}&confidence_min=${confidenceMin}`),
};

// Forecasting APIs
export const forecastingAPI = {
  getEnergyForecast: (commodity: string = 'crude_oil', days: number = 30) =>
    api.get(`/api/forecast/energy?commodity=${commodity}&days=${days}`),
};

// System Status APIs
export const systemAPI = {
  getSystemStatus: () => api.get('/api/v1/etrm/system/status'),
  getDashboard: () => api.get('/api/v1/etrm/system/dashboard'),
  getEngineHealth: (engineName: string) => api.get(`/api/v1/etrm/system/health/${engineName}`),
  getAPIStatus: () => api.get('/api/status'),
  healthCheck: () => api.get('/health'),
};

// Operational Risk APIs
export const operationalRiskAPI = {
  getOperationalRiskSummary: () => api.get('/api/v1/etrm/operational-risk/summary'),
  calculateOperationalRiskCapital: (businessLine: string, method: string = 'basic_indicator') =>
    api.post('/api/v1/etrm/operational-risk/calculate', { business_line: businessLine, method }),
};

// Clearing and Settlement APIs
export const clearingAPI = {
  getClearingSummary: () => api.get('/api/v1/etrm/clearing/summary'),
  processSettlement: (tradeId: string, settlementType: string = 'cash') =>
    api.post('/api/v1/etrm/clearing/settle', { trade_id: tradeId, settlement_type: settlementType }),
};

// AI/ML APIs
export const aiAPI = {
  getAIForecast: (commodity: string, model: string, periods: number) =>
    api.get(`/api/v1/ai/forecast?commodity=${commodity}&model=${model}&periods=${periods}`),
  optimizePortfolio: (commodities: string[], objective: string, useQuantum: boolean = true) =>
    api.post('/api/v1/ai/optimize', { commodities, objective, use_quantum: useQuantum }),
  getAIInsights: (commodities: string[], portfolio?: any) =>
    api.get(`/api/v1/ai/insights?commodities=${commodities.join(',')}`, { data: portfolio }),
  runScenarioAnalysis: (portfolio: any, scenarioType: string, scenarios?: string[], numSimulations: number = 10000) =>
    api.post('/api/v1/ai/scenarios', { portfolio, scenario_type: scenarioType, scenarios, num_simulations: numSimulations }),
};

// Quantum Computing APIs
export const quantumAPI = {
  quantumPortfolioOptimization: (assets: string[], constraints?: any, useRealHardware: boolean = false) =>
    api.post('/api/v1/quantum/optimize', { assets, constraints, use_real_hardware: useRealHardware }),
  quantumRiskAnalysis: (portfolio: any, marketData?: any, useRealHardware: boolean = false) =>
    api.post('/api/v1/quantum/risk', { portfolio, market_data: marketData, use_real_hardware: useRealHardware }),
  quantumMarketSimulation: (marketConditions: any, numScenarios: number = 1000, useRealHardware: boolean = false) =>
    api.post('/api/v1/quantum/simulate', { market_conditions: marketConditions, num_scenarios: numScenarios, use_real_hardware: useRealHardware }),
  getQuantumCapabilities: () => api.get('/api/v1/quantum/capabilities'),
};

// Billing APIs
export const billingAPI = {
  createSubscription: (userId: string, planType: string, billingCycle: string, paymentMethod: string) =>
    api.post('/api/v1/billing/subscribe', { user_id: userId, plan_type: planType, billing_cycle: billingCycle, payment_method: paymentMethod }),
  getSubscription: (userId: string) => api.get(`/api/v1/billing/subscription/${userId}`),
  getUsage: (userId: string, period: string = 'current_month') =>
    api.get(`/api/v1/billing/usage/${userId}?period=${period}`),
  getAvailablePlans: () => api.get('/api/v1/billing/plans'),
  getBillingHistory: (userId: string, limit: number = 10) =>
    api.get(`/api/v1/billing/history/${userId}?limit=${limit}`),
};

// Admin APIs
export const adminAPI = {
  getSystemOverview: () => api.get('/api/v1/admin/overview'),
  getPerformanceMetrics: () => api.get('/api/v1/admin/metrics'),
  getUserAnalytics: () => api.get('/api/v1/admin/users'),
  getRevenueMetrics: () => api.get('/api/v1/admin/revenue'),
  getSystemAlerts: () => api.get('/api/v1/admin/alerts'),
  getSecurityMetrics: () => api.get('/api/v1/admin/security'),
  getPerformanceHistory: (period: string = '24h') => api.get(`/api/v1/admin/performance?period=${period}`),
  getDatabaseMetrics: () => api.get('/api/v1/admin/database'),
  getAPIMetrics: () => api.get('/api/v1/admin/api'),
};

// Legacy APIs for backward compatibility
export const createTrade = (trade: any) => api.post('/trades', trade);
