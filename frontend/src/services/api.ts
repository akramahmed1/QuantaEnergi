/**
 * Enhanced API Service for QuantaEnergi Platform
 * Integrates with all backend ETRM/CTRM features with performance optimization
 */

import performanceOptimizer from './performanceOptimizer';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Performance monitoring wrapper
const withPerformanceMonitoring = async <T>(
  operation: string,
  apiCall: () => Promise<T>
): Promise<T> => {
  const startTime = performance.now();
  try {
    const result = await apiCall();
    const responseTime = performance.now() - startTime;
    performanceOptimizer.recordApiResponseTime(responseTime);
    return result;
  } catch (error) {
    const responseTime = performance.now() - startTime;
    performanceOptimizer.recordApiResponseTime(responseTime);
    throw error;
  }
};

// Generic API request function with caching and error handling
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {},
  useCache: boolean = true,
  cacheKey?: string
): Promise<T> {
  // Check cache first if enabled
  if (useCache && cacheKey) {
    const cached = performanceOptimizer.getCached<T>(cacheKey);
    if (cached) {
      return cached;
    }
  }

  try {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `API request failed: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    
    // Cache the result if caching is enabled
    if (useCache && cacheKey) {
      performanceOptimizer.setCached(cacheKey, data);
    }

    return data;
  } catch (error) {
    console.error(`API request to ${endpoint} failed:`, error);
    throw error;
  }
}

// ============================================================================
// TRADE LIFECYCLE API
// ============================================================================

export interface TradeCreate {
  trade_type: string;
  commodity: string;
  quantity: number;
  price: number;
  currency: string;
  counterparty: string;
  delivery_date: string;
  delivery_location: string;
  additional_terms?: Record<string, any>;
}

export interface TradeResponse {
  trade_id: string;
  status: string;
  message: string;
  timestamp: string;
}

export interface TradeStatusResponse {
  trade_id: string;
  status: string;
  valid: boolean;
  compliant: boolean;
  sharia_result: {
    compliant: boolean;
    restrictions: string[];
  };
}

export const tradeLifecycleAPI = {
  // Capture new trade
  captureTrade: async (tradeData: TradeCreate): Promise<TradeResponse> => {
    const cacheKey = performanceOptimizer.generateCacheKey('trade_capture', tradeData);
    return withPerformanceMonitoring('capture_trade', () =>
      apiRequest<TradeResponse>('/api/v1/trade-lifecycle/capture', {
        method: 'POST',
        body: JSON.stringify(tradeData)
      }, true, cacheKey)
    );
  },

  // Validate trade
  validateTrade: async (tradeId: string): Promise<TradeStatusResponse> => {
    const cacheKey = `trade_validation_${tradeId}`;
    return withPerformanceMonitoring('validate_trade', () =>
      apiRequest<TradeStatusResponse>(`/api/v1/trade-lifecycle/${tradeId}/validate`, {
        method: 'POST'
      }, true, cacheKey)
    );
  },

  // Generate confirmation
  generateConfirmation: async (tradeId: string): Promise<any> => {
    const cacheKey = `trade_confirmation_${tradeId}`;
    return withPerformanceMonitoring('generate_confirmation', () =>
      apiRequest(`/api/v1/trade-lifecycle/${tradeId}/confirm`, {
        method: 'POST'
      }, true, cacheKey)
    );
  },

  // Allocate trade
  allocateTrade: async (tradeId: string, allocationData: any): Promise<any> => {
    const cacheKey = `trade_allocation_${tradeId}`;
    return withPerformanceMonitoring('allocate_trade', () =>
      apiRequest(`/api/v1/trade-lifecycle/${tradeId}/allocate`, {
        method: 'POST',
        body: JSON.stringify(allocationData)
      }, true, cacheKey)
    );
  },

  // Process settlement
  processSettlement: async (tradeId: string, settlementData: any): Promise<any> => {
    const cacheKey = `trade_settlement_${tradeId}`;
    return withPerformanceMonitoring('process_settlement', () =>
      apiRequest(`/api/v1/trade-lifecycle/${tradeId}/settle`, {
        method: 'POST',
        body: JSON.stringify(settlementData)
      }, true, cacheKey)
    );
  },

  // Generate invoice
  generateInvoice: async (tradeId: string): Promise<any> => {
    const cacheKey = `trade_invoice_${tradeId}`;
    return withPerformanceMonitoring('generate_invoice', () =>
      apiRequest(`/api/v1/trade-lifecycle/${tradeId}/invoice`, {
        method: 'POST'
      }, true, cacheKey)
    );
  },

  // Process payment
  processPayment: async (tradeId: string, paymentData: any): Promise<any> => {
    const cacheKey = `trade_payment_${tradeId}`;
    return withPerformanceMonitoring('process_payment', () =>
      apiRequest(`/api/v1/trade-lifecycle/${tradeId}/payment`, {
        method: 'POST',
        body: JSON.stringify(paymentData)
      }, true, cacheKey)
    );
  },

  // Get trade status
  getTradeStatus: async (tradeId: string): Promise<TradeStatusResponse> => {
    const cacheKey = `trade_status_${tradeId}`;
    return withPerformanceMonitoring('get_trade_status', () =>
      apiRequest<TradeStatusResponse>(`/api/v1/trade-lifecycle/${tradeId}/status`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get user trades
  getUserTrades: async (userId: string): Promise<TradeResponse[]> => {
    const cacheKey = `user_trades_${userId}`;
    return withPerformanceMonitoring('get_user_trades', () =>
      apiRequest<TradeResponse[]>(`/api/v1/trade-lifecycle/user/${userId}/trades`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Cancel trade
  cancelTrade: async (tradeId: string, reason: string): Promise<any> => {
    return withPerformanceMonitoring('cancel_trade', () =>
      apiRequest(`/api/v1/trade-lifecycle/${tradeId}/cancel`, {
        method: 'POST',
        body: JSON.stringify({ reason })
      }, false)
    );
  }
};

// ============================================================================
// RISK ANALYTICS API
// ============================================================================

export interface PortfolioData {
  portfolio_id: string;
  total_value: number;
  volatility: number;
  positions: Array<{
    commodity: string;
    quantity: number;
    price: number;
  }>;
  historical_returns: number[];
}

export interface RiskMetrics {
  var_95: number;
  var_99: number;
  expected_shortfall: number;
  sharpe_ratio: number;
  max_drawdown: number;
}

export const riskAnalyticsAPI = {
  // Monte Carlo VaR
  calculateVaRMonteCarlo: async (portfolioData: PortfolioData, confidenceLevel: number = 0.95): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('var_monte_carlo', { portfolioData, confidenceLevel });
    return withPerformanceMonitoring('calculate_var_monte_carlo', () =>
      apiRequest('/api/v1/risk-analytics/var/monte-carlo', {
        method: 'POST',
        body: JSON.stringify({ portfolio_data: portfolioData, confidence_level: confidenceLevel })
      }, true, cacheKey)
    );
  },

  // Parametric VaR
  calculateVaRParametric: async (portfolioData: PortfolioData, confidenceLevel: number = 0.95): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('var_parametric', { portfolioData, confidenceLevel });
    return withPerformanceMonitoring('calculate_var_parametric', () =>
      apiRequest('/api/v1/risk-analytics/var/parametric', {
        method: 'POST',
        body: JSON.stringify({ portfolio_data: portfolioData, confidence_level: confidenceLevel })
      }, true, cacheKey)
    );
  },

  // Historical VaR
  calculateVaRHistorical: async (portfolioData: PortfolioData, confidenceLevel: number = 0.95): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('var_historical', { portfolioData, confidenceLevel });
    return withPerformanceMonitoring('calculate_var_historical', () =>
      apiRequest('/api/v1/risk-analytics/var/historical', {
        method: 'POST',
        body: JSON.stringify({ portfolio_data: portfolioData, confidence_level: confidenceLevel })
      }, true, cacheKey)
    );
  },

  // Stress testing
  stressTestPortfolio: async (portfolioData: PortfolioData, scenarios: string[]): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('stress_test', { portfolioData, scenarios });
    return withPerformanceMonitoring('stress_test_portfolio', () =>
      apiRequest('/api/v1/risk-analytics/stress-test', {
        method: 'POST',
        body: JSON.stringify({ portfolio_data: portfolioData, scenarios })
      }, true, cacheKey)
    );
  },

  // Expected shortfall
  calculateExpectedShortfall: async (portfolioData: PortfolioData, confidenceLevel: number = 0.95): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('expected_shortfall', { portfolioData, confidenceLevel });
    return withPerformanceMonitoring('calculate_expected_shortfall', () =>
      apiRequest('/api/v1/risk-analytics/expected-shortfall', {
        method: 'POST',
        body: JSON.stringify({ portfolio_data: portfolioData, confidence_level: confidenceLevel })
      }, true, cacheKey)
    );
  },

  // Scenario analysis
  performScenarioAnalysis: async (portfolioData: PortfolioData, scenarios: any[]): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('scenario_analysis', { portfolioData, scenarios });
    return withPerformanceMonitoring('perform_scenario_analysis', () =>
      apiRequest('/api/v1/risk-analytics/scenario-analysis', {
        method: 'POST',
        body: JSON.stringify({ portfolio_data: portfolioData, scenarios })
      }, true, cacheKey)
    );
  },

  // Generate risk report
  generateRiskReport: async (portfolioData: PortfolioData, reportType: string = 'comprehensive'): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('risk_report', { portfolioData, reportType });
    return withPerformanceMonitoring('generate_risk_report', () =>
      apiRequest('/api/v1/risk-analytics/risk-report', {
        method: 'POST',
        body: JSON.stringify({ portfolio_data: portfolioData, report_type: reportType })
      }, true, cacheKey)
    );
  },

  // Get risk metrics
  getRiskMetrics: async (portfolioId: string): Promise<RiskMetrics> => {
    const cacheKey = `risk_metrics_${portfolioId}`;
    return withPerformanceMonitoring('get_risk_metrics', () =>
      apiRequest<RiskMetrics>(`/api/v1/risk-analytics/metrics/${portfolioId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get risk dashboard
  getRiskDashboard: async (userId: string): Promise<any> => {
    const cacheKey = `risk_dashboard_${userId}`;
    return withPerformanceMonitoring('get_risk_dashboard', () =>
      apiRequest(`/api/v1/risk-analytics/dashboard/${userId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Monte Carlo simulation
  runMonteCarloSimulation: async (simulationParams: any): Promise<any> => {
    return withPerformanceMonitoring('run_monte_carlo_simulation', () =>
      apiRequest('/api/v1/risk-analytics/simulation/monte-carlo', {
        method: 'POST',
        body: JSON.stringify(simulationParams)
      }, false)
    );
  },

  // Get simulation status
  getSimulationStatus: async (simulationId: string): Promise<any> => {
    const cacheKey = `simulation_status_${simulationId}`;
    return withPerformanceMonitoring('get_simulation_status', () =>
      apiRequest(`/api/v1/risk-analytics/simulation/${simulationId}/status`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get simulation results
  getSimulationResults: async (simulationId: string): Promise<any> => {
    const cacheKey = `simulation_results_${simulationId}`;
    return withPerformanceMonitoring('get_simulation_results', () =>
      apiRequest(`/api/v1/risk-analytics/simulation/${simulationId}/results`, {
        method: 'GET'
      }, true, cacheKey)
    );
  }
};

// ============================================================================
// CREDIT MANAGEMENT API
// ============================================================================

export interface CreditLimit {
  counterparty_id: string;
  limit_amount: number;
  currency: string;
  risk_rating: string;
  expiry_date: string;
  terms: Record<string, any>;
}

export interface CreditExposure {
  counterparty_id: string;
  current_exposure: number;
  credit_limit: number;
  utilization_rate: number;
  risk_score: number;
}

export const creditManagementAPI = {
  // Set credit limit
  setCreditLimit: async (creditLimit: CreditLimit): Promise<any> => {
    return withPerformanceMonitoring('set_credit_limit', () =>
      apiRequest('/api/v1/credit-management/limit', {
        method: 'POST',
        body: JSON.stringify(creditLimit)
      }, false)
    );
  },

  // Get credit limit
  getCreditLimit: async (counterpartyId: string): Promise<any> => {
    const cacheKey = `credit_limit_${counterpartyId}`;
    return withPerformanceMonitoring('get_credit_limit', () =>
      apiRequest(`/api/v1/credit-management/limit/${counterpartyId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get all credit limits
  getAllCreditLimits: async (): Promise<any> => {
    const cacheKey = 'all_credit_limits';
    return withPerformanceMonitoring('get_all_credit_limits', () =>
      apiRequest('/api/v1/credit-management/limits', {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Calculate exposure
  calculateExposure: async (counterpartyId: string): Promise<any> => {
    const cacheKey = `exposure_${counterpartyId}`;
    return withPerformanceMonitoring('calculate_exposure', () =>
      apiRequest('/api/v1/credit-management/exposure', {
        method: 'POST',
        body: JSON.stringify({ counterparty_id: counterpartyId })
      }, true, cacheKey)
    );
  },

  // Get exposure
  getExposure: async (counterpartyId: string): Promise<CreditExposure> => {
    const cacheKey = `exposure_${counterpartyId}`;
    return withPerformanceMonitoring('get_exposure', () =>
      apiRequest<CreditExposure>(`/api/v1/credit-management/exposure/${counterpartyId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Check credit availability
  checkCreditAvailability: async (counterpartyId: string, amount: number): Promise<any> => {
    const cacheKey = `credit_availability_${counterpartyId}_${amount}`;
    return withPerformanceMonitoring('check_credit_availability', () =>
      apiRequest('/api/v1/credit-management/availability', {
        method: 'POST',
        body: JSON.stringify({ counterparty_id: counterpartyId, amount })
      }, true, cacheKey)
    );
  },

  // Get credit availability
  getCreditAvailability: async (counterpartyId: string): Promise<any> => {
    const cacheKey = `credit_availability_${counterpartyId}`;
    return withPerformanceMonitoring('get_credit_availability', () =>
      apiRequest(`/api/v1/credit-management/availability/${counterpartyId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Generate credit report
  generateCreditReport: async (counterpartyId: string): Promise<any> => {
    const cacheKey = `credit_report_${counterpartyId}`;
    return withPerformanceMonitoring('generate_credit_report', () =>
      apiRequest('/api/v1/credit-management/report', {
        method: 'POST',
        body: JSON.stringify({ counterparty_id: counterpartyId })
      }, true, cacheKey)
    );
  },

  // Get credit dashboard
  getCreditDashboard: async (userId: string): Promise<any> => {
    const cacheKey = `credit_dashboard_${userId}`;
    return withPerformanceMonitoring('get_credit_dashboard', () =>
      apiRequest(`/api/v1/credit-management/dashboard/${userId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  }
};

// ============================================================================
// ALGORITHMIC TRADING API
// ============================================================================

export interface AlgoStrategyCreate {
  strategy_name: string;
  strategy_type: string;
  parameters: Record<string, any>;
  risk_limits: Record<string, any>;
  islamic_compliant: boolean;
  execution_mode: string;
}

export const algorithmicTradingAPI = {
  // Execute algorithm
  executeAlgorithm: async (algoSpec: AlgoStrategyCreate): Promise<any> => {
    return withPerformanceMonitoring('execute_algorithm', () =>
      apiRequest('/api/v1/options/algo/execute', {
        method: 'POST',
        body: JSON.stringify(algoSpec)
      }, false)
    );
  },

  // Calculate VWAP
  calculateVWAP: async (orders: any[]): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('vwap_calculation', { orders });
    return withPerformanceMonitoring('calculate_vwap', () =>
      apiRequest('/api/v1/options/algo/vwap', {
        method: 'POST',
        body: JSON.stringify({ orders })
      }, true, cacheKey)
    );
  },

  // Execute TWAP strategy
  executeTWAPStrategy: async (twapParams: any): Promise<any> => {
    return withPerformanceMonitoring('execute_twap_strategy', () =>
      apiRequest('/api/v1/options/algo/twap', {
        method: 'POST',
        body: JSON.stringify(twapParams)
      }, false)
    );
  },

  // Optimize order sizing
  optimizeOrderSizing: async (marketData: any, targetVolume: number, riskParams: any): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('order_sizing_optimization', { marketData, targetVolume, riskParams });
    return withPerformanceMonitoring('optimize_order_sizing', () =>
      apiRequest('/api/v1/options/algo/optimize-sizing', {
        method: 'POST',
        body: JSON.stringify({ market_data: marketData, target_volume: targetVolume, risk_params: riskParams })
      }, true, cacheKey)
    );
  },

  // Monitor execution quality
  monitorExecutionQuality: async (strategyId: string): Promise<any> => {
    const cacheKey = `execution_quality_${strategyId}`;
    return withPerformanceMonitoring('monitor_execution_quality', () =>
      apiRequest(`/api/v1/options/algo/execution-quality/${strategyId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get strategy performance
  getStrategyPerformance: async (strategyId: string): Promise<any> => {
    const cacheKey = `strategy_performance_${strategyId}`;
    return withPerformanceMonitoring('get_strategy_performance', () =>
      apiRequest(`/api/v1/options/algo/performance/${strategyId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Validate algo strategy
  validateAlgoStrategy: async (strategy: AlgoStrategyCreate): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('algo_strategy_validation', strategy);
    return withPerformanceMonitoring('validate_algo_strategy', () =>
      apiRequest('/api/v1/options/algo/validate', {
        method: 'POST',
        body: JSON.stringify(strategy)
      }, true, cacheKey)
    );
  },

  // Check execution ethics
  checkExecutionEthics: async (strategyId: string): Promise<any> => {
    const cacheKey = `execution_ethics_${strategyId}`;
    return withPerformanceMonitoring('check_execution_ethics', () =>
      apiRequest(`/api/v1/options/algo/ethics/${strategyId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  }
};

// ============================================================================
// OPTIONS TRADING API
// ============================================================================

export interface OptionCreate {
  option_type: string;
  underlying: string;
  strike_price: number;
  expiry_date: string;
  quantity: number;
  premium?: number;
  volatility?: number;
  risk_free_rate?: number;
  islamic_compliant: boolean;
}

export const optionsTradingAPI = {
  // Price option
  priceOption: async (optionData: OptionCreate): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('option_pricing', optionData);
    return withPerformanceMonitoring('price_option', () =>
      apiRequest('/api/v1/options/price', {
        method: 'POST',
        body: JSON.stringify(optionData)
      }, true, cacheKey)
    );
  },

  // Execute option trade
  executeOptionTrade: async (optionId: string, executionParams: any): Promise<any> => {
    return withPerformanceMonitoring('execute_option_trade', () =>
      apiRequest('/api/v1/options/execute', {
        method: 'POST',
        body: JSON.stringify({ option_id: optionId, ...executionParams })
      }, false)
    );
  },

  // Get options portfolio
  getOptionsPortfolio: async (userId: string): Promise<any> => {
    const cacheKey = `options_portfolio_${userId}`;
    return withPerformanceMonitoring('get_options_portfolio', () =>
      apiRequest(`/api/v1/options/portfolio/${userId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Create structured product
  createStructuredProduct: async (productData: any): Promise<any> => {
    return withPerformanceMonitoring('create_structured_product', () =>
      apiRequest('/api/v1/options/structured-product', {
        method: 'POST',
        body: JSON.stringify(productData)
      }, false)
    );
  }
};

// ============================================================================
// REGULATORY COMPLIANCE API
// ============================================================================

export interface ComplianceReport {
  report_id: string;
  region: string;
  regulation_type: string;
  status: string;
  generated_at: string;
  data: any;
}

export const regulatoryComplianceAPI = {
  // Generate compliance report
  generateComplianceReport: async (region: string, regulationType: string): Promise<ComplianceReport> => {
    const cacheKey = `compliance_report_${region}_${regulationType}`;
    return withPerformanceMonitoring('generate_compliance_report', () =>
      apiRequest<ComplianceReport>('/api/v1/compliance/report', {
        method: 'POST',
        body: JSON.stringify({ region, regulation_type: regulationType })
      }, true, cacheKey)
    );
  },

  // Generate bulk compliance reports
  generateBulkComplianceReports: async (regions: string[], regulationTypes: string[]): Promise<any> => {
    return withPerformanceMonitoring('generate_bulk_compliance_reports', () =>
      apiRequest('/api/v1/compliance/bulk-reports', {
        method: 'POST',
        body: JSON.stringify({ regions, regulation_types: regulationTypes })
      }, false)
    );
  },

  // Anonymize compliance data
  anonymizeComplianceData: async (data: any, anonymizationRules: any): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('anonymized_data', { data, anonymizationRules });
    return withPerformanceMonitoring('anonymize_compliance_data', () =>
      apiRequest('/api/v1/compliance/anonymize', {
        method: 'POST',
        body: JSON.stringify({ data, anonymization_rules: anonymizationRules })
      }, true, cacheKey)
    );
  },

  // Get compliance regions
  getComplianceRegions: async (): Promise<string[]> => {
    const cacheKey = 'compliance_regions';
    return withPerformanceMonitoring('get_compliance_regions', () =>
      apiRequest<string[]>('/api/v1/compliance/regions', {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get compliance status
  getComplianceStatus: async (region: string): Promise<any> => {
    const cacheKey = `compliance_status_${region}`;
    return withPerformanceMonitoring('get_compliance_status', () =>
      apiRequest(`/api/v1/compliance/status/${region}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get compliance dashboard
  getComplianceDashboard: async (userId: string): Promise<any> => {
    const cacheKey = `compliance_dashboard_${userId}`;
    return withPerformanceMonitoring('get_compliance_dashboard', () =>
      apiRequest(`/api/v1/compliance/dashboard/${userId}`, {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Validate compliance requirements
  validateComplianceRequirements: async (requirements: any): Promise<any> => {
    const cacheKey = performanceOptimizer.generateCacheKey('compliance_validation', requirements);
    return withPerformanceMonitoring('validate_compliance_requirements', () =>
      apiRequest('/api/v1/compliance/validate', {
        method: 'POST',
        body: JSON.stringify(requirements)
      }, true, cacheKey)
    );
  },

  // Get compliance history
  getComplianceHistory: async (userId: string, region?: string): Promise<ComplianceReport[]> => {
    const cacheKey = `compliance_history_${userId}_${region || 'all'}`;
    return withPerformanceMonitoring('get_compliance_history', () =>
      apiRequest<ComplianceReport[]>(`/api/v1/compliance/history/${userId}`, {
        method: 'GET',
        headers: region ? { 'X-Region': region } : {}
      }, true, cacheKey)
    );
  }
};

// ============================================================================
// PERFORMANCE MONITORING API
// ============================================================================

export const performanceMonitoringAPI = {
  // Get system health
  getSystemHealth: async (): Promise<any> => {
    const cacheKey = 'system_health';
    return withPerformanceMonitoring('get_system_health', () =>
      apiRequest('/api/v1/health', {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get performance metrics
  getPerformanceMetrics: async (): Promise<any> => {
    const cacheKey = 'performance_metrics';
    return withPerformanceMonitoring('get_performance_metrics', () =>
      apiRequest('/api/v1/metrics', {
        method: 'GET'
      }, true, cacheKey)
    );
  },

  // Get cache statistics
  getCacheStats: () => performanceOptimizer.getCacheStats(),

  // Get performance summary
  getPerformanceSummary: () => performanceOptimizer.getPerformanceSummary(),

  // Clear cache
  clearCache: () => performanceOptimizer.clearCache(),

  // Start monitoring
  startMonitoring: () => performanceOptimizer.startMonitoring(),

  // Stop monitoring
  stopMonitoring: () => performanceOptimizer.stopMonitoring()
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

export const formatCurrency = (amount: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(2)}%`;
};

export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
};

export const calculatePnL = (currentPrice: number, entryPrice: number, quantity: number): number => {
  return (currentPrice - entryPrice) * quantity;
};

export const calculatePnLPercentage = (currentPrice: number, entryPrice: number): number => {
  return ((currentPrice - entryPrice) / entryPrice) * 100;
};

// ============================================================================
// EXPORT ALL APIs
// ============================================================================

export {
  tradeLifecycleAPI,
  riskAnalyticsAPI,
  creditManagementAPI,
  algorithmicTradingAPI,
  optionsTradingAPI,
  regulatoryComplianceAPI,
  performanceMonitoringAPI
};

export default {
  tradeLifecycle: tradeLifecycleAPI,
  riskAnalytics: riskAnalyticsAPI,
  creditManagement: creditManagementAPI,
  algorithmicTrading: algorithmicTradingAPI,
  optionsTrading: optionsTradingAPI,
  regulatoryCompliance: regulatoryComplianceAPI,
  performanceMonitoring: performanceMonitoringAPI
};
